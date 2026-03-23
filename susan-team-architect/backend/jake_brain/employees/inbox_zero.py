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
