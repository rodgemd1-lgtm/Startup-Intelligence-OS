<<<<<<< HEAD
"""Inbox Zero Employee — email triage and action extraction (3x daily weekdays).

Runs at 8 AM, 12 PM, 5 PM on weekdays. Uses Apple Mail via osascript to:
- Read recent unread emails from key accounts
- Extract action items and deadlines
- Store in jake_brain as episodic memories
- Send triage summary to Telegram
"""
from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[3]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def load_env() -> None:
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        with open(env_path) as fh:
            for line in fh:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())


_FETCH_SCRIPT = """\
tell application "Mail"
    set unreadCount to 0
    set summaries to {}
    set targetAccounts to {"Exchange", "iCloud"}
    repeat with acct in every account
        if name of acct is in targetAccounts then
            repeat with mb in every mailbox of acct
                if name of mb is "INBOX" then
                    set msgs to (messages of mb whose read status is false)
                    set unreadCount to unreadCount + (count of msgs)
                    repeat with m in items 1 thru (count of msgs) of msgs
                        if (count of summaries) < 10 then
                            set end of summaries to (sender of m & " | " & subject of m)
                        end if
                    end repeat
                end if
            end repeat
        end if
    end repeat
    return {unreadCount as string, summaries as string}
end tell
"""


def fetch_unread_emails() -> tuple[int, list[str]]:
    """Fetch unread email count and summaries via Apple Mail osascript."""
    try:
        result = subprocess.run(
            ["osascript", "-e", _FETCH_SCRIPT],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return 0, []
        output = result.stdout.strip()
        # Parse: first element is count, rest are summaries
        parts = output.split(", ", 1)
        count = int(parts[0]) if parts and parts[0].isdigit() else 0
        summaries = [s.strip() for s in parts[1].split(",")] if len(parts) > 1 else []
        return count, [s for s in summaries if s]
    except Exception:
        return 0, []


def extract_action_items(email_summaries: list[str]) -> list[str]:
    """Simple keyword-based action item extraction."""
    action_keywords = [
        "action required", "please review", "approval needed", "response needed",
        "deadline", "urgent", "follow up", "next steps", "asap", "by end of day",
        "meeting request", "invite", "rsvp"
    ]
    actions = []
    for summary in email_summaries:
        lower = summary.lower()
        for kw in action_keywords:
            if kw in lower:
                actions.append(summary)
                break
    return actions


def store_triage_to_brain(count: int, actions: list[str]) -> bool:
    """Store email triage results as episodic memory."""
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        if not url or not key:
            return False
        client = create_client(url, key)
        now = datetime.utcnow().isoformat()
        content = f"Email triage: {count} unread. Actions: {'; '.join(actions[:5]) if actions else 'none'}"
        client.table("jake_episodic").insert({
            "content": content,
            "source": "inbox_zero",
            "source_type": "manual",
            "metadata": {"unread_count": count, "action_count": len(actions), "source_label": "email_triage"},
            "importance": min(1.0, 0.4 + len(actions) * 0.1),
            "occurred_at": now,
        }).execute()
        return True
    except Exception:
        return False


def send_telegram(message: str) -> bool:
    """Send triage summary to Telegram."""
    try:
        import urllib.request
        import json as json_mod
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
        if not token or not chat_id:
            return False
        payload = json_mod.dumps({"chat_id": chat_id, "text": message[:4000]}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception:
        return False


def run() -> dict:
    """Run inbox_zero employee — triage email and extract actions."""
    load_env()

    count, summaries = fetch_unread_emails()
    actions = extract_action_items(summaries)
    stored = store_triage_to_brain(count, actions)

    # Build Telegram message
    ts = datetime.now().strftime("%H:%M")
    lines = [f"📬 Inbox Triage ({ts})"]
    lines.append(f"  Unread: {count} emails")
    if actions:
        lines.append(f"  ⚡ {len(actions)} action items:")
        for a in actions[:3]:
            lines.append(f"    • {a[:80]}")
    else:
        lines.append("  ✓ No urgent items")

    sent = send_telegram("\n".join(lines))

    return {
        "status": "complete",
        "unread_count": count,
        "action_items": len(actions),
        "brain_stored": stored,
        "telegram_sent": sent,
    }


if __name__ == "__main__":
    result = run()
    print(result)
=======
"""Inbox Zero — Apple Mail triage autonomous employee.

Runs 3x daily: 8 AM, 12 PM, 5 PM weekdays (via cron) or on-demand.

Pipeline:
  1. CONTEXT  — Load recent email subjects via osascript, load Mike's priorities from jake_goals
  2. PLAN     — Categorize emails: URGENT, IMPORTANT, FYI, NOISE
  3. BUILD    — For URGENT: draft response bullets. For IMPORTANT: create jake_tasks. For NOISE: flag archive.
  4. VALIDATE — Check categorization against sender importance (jake_entities priority boost)
  5. HEAL     — If osascript times out, kill+relaunch Mail.app and retry once
  6. REPORT   — Generate email triage summary with action items
  7. CLOSE    — Write triage results to jake_episodic, create jake_tasks for follow-ups
  8. LEARN    — Track overridden categorizations to improve future accuracy

HARDCODED: Apple Mail via osascript only. Exchange account is named "Exchange".
"""
from __future__ import annotations

import logging
import subprocess
import time
from datetime import datetime, timezone
from typing import NamedTuple

logger = logging.getLogger(__name__)

# Email categories
URGENT = "URGENT"       # needs response today
IMPORTANT = "IMPORTANT" # needs response this week
FYI = "FYI"             # read later
NOISE = "NOISE"         # archive/delete

# Senders that auto-boost to URGENT (known important contacts)
HIGH_PRIORITY_DOMAINS = [
    "oracle.com", "cohlmia",
]
HIGH_PRIORITY_SENDERS = [
    "matt cohlmia", "ellen", "james", "jacob",
]

# Subject keywords that indicate URGENT
URGENT_KEYWORDS = [
    "urgent", "asap", "action required", "deadline", "today",
    "critical", "immediately", "response needed", "follow up",
]

# Subject keywords that indicate NOISE
NOISE_KEYWORDS = [
    "unsubscribe", "newsletter", "noreply", "no-reply",
    "promo", "offer", "deal", "sale", "marketing",
    "linkedin", "twitter", "facebook", "notification",
]


class EmailRecord(NamedTuple):
    subject: str
    sender: str
    date_received: str
    category: str = FYI
    priority_boost: bool = False


# ------------------------------------------------------------------
# Apple Mail osascript helpers (HARDCODED — do NOT change to other APIs)
# ------------------------------------------------------------------

def get_inbox_messages(limit: int = 20) -> list[dict]:
    """Fetch inbox messages via osascript. Handles Mail.app timeout."""
    script = f"""
    tell application "Mail"
        set msgs to messages 1 through {limit} of inbox
        set output to ""
        repeat with m in msgs
            set output to output & subject of m & "|" & sender of m & "|" & (date received of m as string) & linefeed
        end repeat
        return output
    end tell
    """
    result = _run_osascript(script, retry_on_fail=True)
    if not result:
        return []

    records = []
    for line in result.strip().split("\n"):
        parts = line.split("|")
        if len(parts) >= 2:
            records.append({
                "subject": parts[0].strip(),
                "sender": parts[1].strip() if len(parts) > 1 else "",
                "date_received": parts[2].strip() if len(parts) > 2 else "",
            })
    return records


def get_today_events() -> list[dict]:
    """Fetch today's calendar events via osascript."""
    script = """
    tell application "Calendar"
        set today to current date
        set tomorrow to today + 1 * days
        set output to ""
        repeat with cal in calendars
            set evts to (every event of cal whose start date >= today and start date < tomorrow)
            repeat with e in evts
                set output to output & summary of e & "|" & start date of e & "|" & end date of e & linefeed
            end repeat
        end repeat
        return output
    end tell
    """
    result = _run_osascript(script, retry_on_fail=False)
    if not result:
        return []

    events = []
    for line in result.strip().split("\n"):
        parts = line.split("|")
        if parts and parts[0].strip():
            events.append({
                "summary": parts[0].strip(),
                "start": parts[1].strip() if len(parts) > 1 else "",
                "end": parts[2].strip() if len(parts) > 2 else "",
            })
    return events


def _run_osascript(script: str, retry_on_fail: bool = True, timeout: int = 30) -> str:
    """Run osascript with automatic Mail.app restart on timeout (known fix)."""
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    if result.returncode != 0 and retry_on_fail:
        logger.warning(f"osascript failed (rc={result.returncode}), relaunching Mail.app...")
        subprocess.run(["killall", "Mail"], capture_output=True)
        time.sleep(3)
        subprocess.run(["open", "-a", "Mail"], capture_output=True)
        time.sleep(5)
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    if result.returncode != 0:
        logger.error(f"osascript error: {result.stderr}")
        return ""

    return result.stdout.strip()


# ------------------------------------------------------------------
# Categorization logic
# ------------------------------------------------------------------

def categorize_email(email: dict, known_entities: list[str] | None = None) -> str:
    """Categorize a single email into URGENT/IMPORTANT/FYI/NOISE."""
    subject = (email.get("subject") or "").lower()
    sender = (email.get("sender") or "").lower()
    known = [e.lower() for e in (known_entities or [])]

    # NOISE check first (fast exit)
    if any(kw in subject for kw in NOISE_KEYWORDS):
        return NOISE
    if any(kw in sender for kw in ["noreply", "no-reply", "newsletter", "promo"]):
        return NOISE

    # Priority boost from known important senders/domains
    is_priority_sender = (
        any(ps in sender for ps in HIGH_PRIORITY_SENDERS)
        or any(d in sender for d in HIGH_PRIORITY_DOMAINS)
        or any(e in sender for e in known)
    )

    # URGENT checks
    if any(kw in subject for kw in URGENT_KEYWORDS) or is_priority_sender:
        return URGENT

    # Default to IMPORTANT for everything non-noise
    return IMPORTANT


# ------------------------------------------------------------------
# Main Employee class
# ------------------------------------------------------------------

class InboxZero:
    """Autonomous email triage employee using Apple Mail via osascript."""

    PIPELINE_NAME = "inbox_zero"
    TASK_TYPE = "maintenance"
    CRON_JOBS = [
        "inbox_zero_morning",
        "inbox_zero_midday",
        "inbox_zero_evening",
    ]

    def run(self, cron_slot: str = "morning") -> dict:
        """Execute one inbox triage cycle."""
        now = datetime.now(timezone.utc)
        pipeline = InboxZeroPipeline(
            pipeline_name=f"inbox_zero_{cron_slot}_{now.strftime('%Y%m%d_%H%M')}",
            task_description=f"Apple Mail inbox triage — {cron_slot} run",
            task_type=self.TASK_TYPE,
        )
        return pipeline.run()


class InboxZeroPipeline:
    """Inbox Zero pipeline with overridden Apple Mail build logic."""

    MAX_HEAL_RETRIES = 2

    def __init__(self, pipeline_name: str, task_description: str, task_type: str):
        from jake_brain.autonomous_pipeline import AutonomousPipeline
        self._base = AutonomousPipeline(pipeline_name, task_description, task_type)

        # Override phases
        self._base._phase_build = self._phase_build
        self._base._phase_validate = self._phase_validate
        self._base._phase_close = self._phase_close

    def run(self) -> dict:
        return self._base.run()

    # ------------------------------------------------------------------
    # Inbox Zero BUILD
    # ------------------------------------------------------------------

    def _phase_build(self, plan: dict, context: dict, attempt: int = 0) -> dict:
        """Fetch inbox, categorize, build action items."""
        # Load messages from Apple Mail
        try:
            messages = get_inbox_messages(limit=25)
        except subprocess.TimeoutExpired:
            return {
                "results": [],
                "errors": ["osascript timeout — Mail.app unresponsive"],
                "steps_completed": 0,
                "steps_total": 3,
                "attempt": attempt,
            }
        except Exception as e:
            return {
                "results": [],
                "errors": [f"Mail fetch error: {e}"],
                "steps_completed": 0,
                "steps_total": 3,
                "attempt": attempt,
            }

        if not messages:
            return {
                "results": [{"step": "fetch_mail", "status": "ok", "note": "Inbox empty"}],
                "errors": [],
                "steps_completed": 3,
                "steps_total": 3,
                "categorized": [],
                "attempt": attempt,
            }

        # Get known entities for priority boost
        known_entities = self._get_known_entities()

        # Categorize
        categorized = []
        for msg in messages:
            cat = categorize_email(msg, known_entities)
            categorized.append({**msg, "category": cat})

        # Build action items
        urgent = [m for m in categorized if m["category"] == URGENT]
        important = [m for m in categorized if m["category"] == IMPORTANT]
        noise = [m for m in categorized if m["category"] == NOISE]

        return {
            "results": [
                {"step": "fetch_mail", "status": "ok", "count": len(messages)},
                {"step": "categorize", "status": "ok", "urgent": len(urgent), "important": len(important), "noise": len(noise)},
                {"step": "action_items", "status": "ok", "urgent_items": [m["subject"] for m in urgent[:5]]},
            ],
            "errors": [],
            "steps_completed": 3,
            "steps_total": 3,
            "categorized": categorized,
            "urgent": urgent,
            "important": important,
            "noise": noise,
            "attempt": attempt,
        }

    def _get_known_entities(self) -> list[str]:
        """Load known high-priority entity names from jake_entities."""
        try:
            from jake_brain.store import BrainStore
            store = BrainStore()
            result = store.supabase.table("jake_entities").select(
                "name, entity_type"
            ).in_("entity_type", ["person", "contact"]).limit(50).execute()
            return [e["name"].lower() for e in (result.data or [])]
        except Exception as e:
            logger.warning(f"Failed to load entities: {e}")
            return []

    # ------------------------------------------------------------------
    # Inbox Zero VALIDATE
    # ------------------------------------------------------------------

    def _phase_validate(self, build_results: dict, plan: dict) -> dict:
        """Validate triage completed without critical errors."""
        from jake_brain.autonomous_pipeline import ErrorClass

        errors = build_results.get("errors", [])
        steps_completed = build_results.get("steps_completed", 0)

        if errors:
            error_msg = errors[0]
            is_timeout = "timeout" in error_msg.lower() or "mail.app" in error_msg.lower()
            return {
                "passed": False,
                "reason": error_msg,
                "error_class": ErrorClass.API_ERROR if is_timeout else ErrorClass.LOGIC_ERROR,
                "completion_rate": 0,
            }

        if steps_completed < 3:
            return {
                "passed": False,
                "reason": f"Only {steps_completed}/3 steps completed",
                "error_class": ErrorClass.DATA_ERROR,
                "completion_rate": steps_completed / 3,
            }

        return {
            "passed": True,
            "reason": f"Inbox triaged: {len(build_results.get('urgent', []))} urgent, "
                      f"{len(build_results.get('important', []))} important, "
                      f"{len(build_results.get('noise', []))} noise",
            "completion_rate": 1.0,
        }

    # ------------------------------------------------------------------
    # Inbox Zero CLOSE
    # ------------------------------------------------------------------

    def _phase_close(self, report: dict, context: dict, plan: dict) -> dict:
        """Write triage to jake_episodic and create jake_tasks for urgent items."""
        from jake_brain.store import BrainStore
        store = BrainStore()
        closed = {}

        # Write episodic memory
        try:
            summary = (
                f"Inbox Zero triage {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}: "
                f"{report.get('steps_completed', 0)} steps completed. "
                + report.get("validation_passed_reason", "")
            )
            episodic = store.store_episodic(
                content=summary,
                occurred_at=datetime.now(timezone.utc),
                memory_type="inbox_triage",
                project="hermes",
                importance=0.5,
                topics=["email", "inbox-zero"],
                metadata={"run_id": report.get("run_id")},
            )
            closed["episodic_id"] = episodic.get("id")
        except Exception as e:
            logger.warning(f"Episodic write failed: {e}")

        # Create jake_tasks for urgent emails (top 3)
        results = report.get("results_summary", [])
        urgent_tasks_created = 0
        for result in results:
            if result.get("step") == "action_items" and result.get("status") == "ok":
                urgent_items = result.get("output", {}).get("urgent_items", [])
                for subj in urgent_items[:3]:
                    try:
                        store.supabase.table("jake_tasks").insert({
                            "title": f"Email: {subj[:80]}",
                            "description": f"Urgent email requiring response: {subj}",
                            "status": "pending",
                            "priority": "P1",
                            "project": "hermes",
                            "source": "inbox_zero_employee",
                        }).execute()
                        urgent_tasks_created += 1
                    except Exception as e:
                        logger.warning(f"Failed to create task for '{subj}': {e}")
                break

        closed["urgent_tasks_created"] = urgent_tasks_created
        return closed
>>>>>>> claude/nifty-ptolemy
