#!/usr/bin/env python3
"""Email-to-Task Pipeline — convert actionable Oracle emails to jake_tasks.

Reads recent Oracle Health emails from Supabase (already ingested by
brain_oracle_email_ingest.py), extracts action items and deadlines,
and creates jake_tasks entries.

Priority assignment:
  Matt Cohlmia     → P0 (exec sponsor)
  Other leadership → P1 (VPs, directors)
  Team             → P2 (default)
  FYI / low signal → P3 or skipped

Usage:
    python scripts/jake_email_task_extractor.py              # process last 24h
    python scripts/jake_email_task_extractor.py --hours 48   # process last 48h
    python scripts/jake_email_task_extractor.py --dry-run    # print without creating tasks
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

env_file = Path.home() / ".hermes" / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("jake-email-task")

# ---------------------------------------------------------------------------
# Priority tiers — who sends email that needs attention
# ---------------------------------------------------------------------------

PRIORITY_SENDERS: dict[str, str] = {
    # P0 — exec sponsor, immediate action
    "matt.cohlmia": "P0",
    "matthew.cohlmia": "P0",
    # P1 — leadership, requires response
    "ellen": "P1",        # Ellen Doering (adjust if name differs)
    "oracle.cto": "P1",
    "oracle.cpo": "P1",
    "vp.": "P1",
    "director.": "P1",
}

# Email subjects/bodies that signal action required
ACTION_SIGNALS = [
    r"\bplease\s+(review|confirm|approve|respond|send|prepare|update)\b",
    r"\baction\s+required\b",
    r"\bdeadline\b",
    r"\bby\s+(monday|tuesday|wednesday|thursday|friday|today|tomorrow|eod|cob)\b",
    r"\bneed\s+(your|the)\b",
    r"\bfollowing\s+up\b",
    r"\bcan\s+you\b",
    r"\bwould\s+you\b",
    r"\bplease\s+let\s+me\s+know\b",
    r"\bpending\s+your\b",
    r"\bawaiting\s+your\b",
    r"\byour\s+input\b",
    r"\byour\s+thoughts\b",
    r"\bscheduled\s+for\b",
    r"\bmeeting\s+on\b",
]

# FYI / no-action signals (skip these)
SKIP_SIGNALS = [
    r"\bfyi\b",
    r"\bfor\s+your\s+information\b",
    r"\bno\s+action\s+required\b",
    r"\bjust\s+sharing\b",
    r"\bnewsletter\b",
    r"\bunsubscribe\b",
    r"\bnotification\s+only\b",
]


def _is_actionable(email: dict) -> bool:
    """Return True if the email contains action signals."""
    text = (
        (email.get("subject") or "") + " " +
        (email.get("body_preview") or "") + " " +
        (email.get("content") or "")
    ).lower()

    # Skip no-action emails
    if any(re.search(p, text) for p in SKIP_SIGNALS):
        return False

    # Must have at least one action signal
    return any(re.search(p, text) for p in ACTION_SIGNALS)


def _get_sender_priority(email: dict) -> str:
    """Determine task priority based on sender."""
    sender = (
        (email.get("from_address") or "") + " " +
        (email.get("from_name") or "") + " " +
        (email.get("sender") or "")
    ).lower()

    for pattern, priority in PRIORITY_SENDERS.items():
        if pattern in sender:
            return priority

    return "P2"  # default for Oracle team emails


def _extract_action_text(email: dict) -> str:
    """Build the task_text from the email."""
    subject = email.get("subject") or "Oracle email action item"
    sender = email.get("from_name") or email.get("from_address") or "unknown sender"
    body_preview = (email.get("body_preview") or email.get("content") or "")[:200]

    # Try to extract the specific action phrase
    text = body_preview.lower()
    for pattern in ACTION_SIGNALS:
        match = re.search(pattern, text)
        if match:
            # Get surrounding context
            start = max(0, match.start() - 20)
            end = min(len(body_preview), match.end() + 60)
            action_context = body_preview[start:end].strip()
            return f"[{sender}] {subject}: {action_context}"

    return f"[{sender}] Respond to: {subject}"


def _extract_deadline(email: dict) -> str | None:
    """Try to extract a deadline from the email body."""
    text = (email.get("body_preview") or email.get("content") or "").lower()
    today = datetime.now(timezone.utc)

    # "by EOD / COB" → today
    if re.search(r"\b(eod|cob|end of day)\b", text):
        return today.strftime("%Y-%m-%d")

    # "by tomorrow"
    if re.search(r"\btomorrow\b", text):
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    # "by Monday/Tuesday/..."
    days = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6}
    for day_name, day_num in days.items():
        if re.search(rf"\b{day_name}\b", text):
            current_weekday = today.weekday()
            days_ahead = (day_num - current_weekday) % 7
            if days_ahead == 0:
                days_ahead = 7  # "next Monday" if today is Monday
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    return None


def fetch_recent_emails(hours: int = 24) -> list[dict]:
    """Fetch recent Oracle emails from Supabase."""
    from supabase import create_client
    from susan_core.config import config

    supabase = create_client(config.supabase_url, config.supabase_key)
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()

    result = (
        supabase.table("jake_episodic")
        .select("*")
        .contains("tags", ["oracle", "email"])
        .gte("created_at", since)
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    )
    return result.data or []


def get_already_processed_ids() -> set[str]:
    """Return source IDs of emails already converted to tasks."""
    from supabase import create_client
    from susan_core.config import config

    supabase = create_client(config.supabase_url, config.supabase_key)
    result = (
        supabase.table("jake_tasks")
        .select("executor_hint")
        .like("executor_hint", "email:%")
        .limit(200)
        .execute()
    )
    ids = set()
    for row in (result.data or []):
        hint = row.get("executor_hint", "")
        if hint.startswith("email:"):
            ids.add(hint[6:])
    return ids


def process_emails(hours: int = 24, dry_run: bool = False) -> list[dict]:
    """Main pipeline — fetch emails, filter, create tasks."""
    from jake_brain.goals.tasks import TaskStore

    logger.info(f"Fetching emails from last {hours}h...")
    emails = fetch_recent_emails(hours)
    logger.info(f"Found {len(emails)} Oracle email memories")

    already_done = get_already_processed_ids() if not dry_run else set()
    task_store = TaskStore()
    created = []

    for email in emails:
        email_id = email.get("id") or email.get("source_id", "")

        # Skip if already processed
        if email_id in already_done:
            continue

        # Skip non-actionable
        if not _is_actionable(email):
            logger.debug(f"Skipping non-actionable: {email.get('content', '')[:60]}")
            continue

        priority = _get_sender_priority(email)
        task_text = _extract_action_text(email)
        deadline = _extract_deadline(email)

        logger.info(f"[{priority}] Creating task: {task_text[:60]}")

        if not dry_run:
            task = task_store.create_task(
                task_text=task_text,
                assigned_to="hermes",  # Hermes handles email response coordination
                executor_hint=f"email:{email_id}",
                priority=priority,
                due_date=deadline,
                description=f"Auto-created from Oracle email. Original ID: {email_id}",
            )
            created.append(task)
        else:
            created.append({
                "task_text": task_text,
                "priority": priority,
                "deadline": deadline,
                "dry_run": True,
            })

    logger.info(f"Created {len(created)} tasks from emails")
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert Oracle emails to Jake tasks")
    parser.add_argument("--hours", type=int, default=24, help="Look back N hours")
    parser.add_argument("--dry-run", action="store_true", help="Print without creating")
    args = parser.parse_args()

    tasks = process_emails(hours=args.hours, dry_run=args.dry_run)

    if args.dry_run:
        print(f"\n[DRY RUN] Would create {len(tasks)} tasks:")
        for t in tasks:
            print(f"  [{t.get('priority')}] {t.get('task_text', '')[:70]}")
            if t.get("deadline"):
                print(f"         Due: {t['deadline']}")
    else:
        print(f"Created {len(tasks)} tasks from emails.")
        for t in tasks:
            print(f"  [{t.get('priority','?')}] {t.get('task_text','')[:60]}")


if __name__ == "__main__":
    main()
