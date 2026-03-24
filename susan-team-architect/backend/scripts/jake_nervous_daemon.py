#!/usr/bin/env python3
"""Phase 8: THE NERVOUS SYSTEM — Event daemon.

Runs every 2 minutes via launchd (StartInterval: 120).
Checks for:
  1. Urgent emails → Telegram alert (P0: <5 min, P1: batched)
  2. Upcoming meetings (13–17 min window) → prep brief

Usage:
  python3 jake_nervous_daemon.py          # normal run
  python3 jake_nervous_daemon.py --test   # dry-run (no Telegram)
  python3 jake_nervous_daemon.py --status # print current state and exit
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Load env
env_file = Path.home() / ".hermes" / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

# ── Logging ───────────────────────────────────────────────────────────────
log_dir = Path.home() / ".hermes" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "nervous_daemon.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("jake.nervous")


def run_daemon(dry_run: bool = False) -> dict:
    """Run one detection cycle. Returns summary dict."""
    from jake_brain.nervous import EventBus, EmailAlertScanner, MeetingPrepScanner, NotificationBatcher

    bus = EventBus()
    summary = {"email_events": 0, "meeting_events": 0, "alerts_sent": 0, "dnd": False}

    if bus.is_dnd():
        logger.info("DND active — skipping non-P0 checks")
        summary["dnd"] = True

    # ── Email scan ────────────────────────────────────────────────────────
    try:
        email_scanner = EmailAlertScanner(bus)
        email_events = email_scanner.scan()
        summary["email_events"] = len(email_events)
        if email_events:
            logger.info("Email scan: %d urgent events found", len(email_events))
    except Exception as exc:
        logger.error("Email scan failed: %s", exc)

    # ── Meeting prep scan ─────────────────────────────────────────────────
    try:
        meeting_scanner = MeetingPrepScanner(bus)
        meeting_events = meeting_scanner.scan()
        summary["meeting_events"] = len(meeting_events)
        if meeting_events:
            logger.info("Meeting scan: %d prep events found", len(meeting_events))
    except Exception as exc:
        logger.error("Meeting scan failed: %s", exc)

    # ── Dispatch notifications ────────────────────────────────────────────
    pending = bus.drain()
    if pending and not dry_run:
        batcher = NotificationBatcher(bus)
        sent = batcher.dispatch(pending)
        summary["alerts_sent"] = sent
        logger.info("Dispatched %d notifications (%d events)", sent, len(pending))
    elif pending and dry_run:
        logger.info("[DRY RUN] Would dispatch %d events:", len(pending))
        for event in pending:
            logger.info("  - [%s] %s (urgency=%.2f)", event.event_type.value, event.title, event.urgency)
        # Still mark seen in dry-run to avoid duplicate prints
        for event in pending:
            bus.mark_seen(event.event_id)

    return summary


def print_status() -> None:
    """Print current nervous system state."""
    from jake_brain.nervous import EventBus
    bus = EventBus()
    status = bus.status()

    print("\n⚡ NERVOUS SYSTEM STATUS")
    print("=" * 40)
    print(f"DND active:          {status['dnd_active']}")
    if status.get("dnd_until"):
        print(f"DND until:           {status['dnd_until']}")
    print(f"Last email check:    {status['last_email_check'] or 'never'}")
    print(f"Last calendar check: {status['last_calendar_check'] or 'never'}")
    print(f"Seen events (total): {status['seen_event_count']}")
    print(f"Pending events:      {status['pending']}")
    stats = status.get("stats", {})
    print(f"Total events ever:   {stats.get('total_events', 0)}")
    print(f"Alerts sent:         {stats.get('alerts_sent', 0)}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Jake Nervous System Daemon")
    parser.add_argument("--test", action="store_true", help="Dry run — detect but don't send Telegram")
    parser.add_argument("--status", action="store_true", help="Print status and exit")
    parser.add_argument("--email-only", action="store_true", help="Only run email scan")
    parser.add_argument("--calendar-only", action="store_true", help="Only run calendar scan")
    args = parser.parse_args()

    if args.status:
        print_status()
        return

    logger.info("Nervous daemon starting (dry_run=%s)", args.test)

    try:
        summary = run_daemon(dry_run=args.test)
        logger.info(
            "Cycle complete — email_events=%d meeting_events=%d alerts_sent=%d",
            summary["email_events"],
            summary["meeting_events"],
            summary["alerts_sent"],
        )
        _write_run_status("jake_nervous_daemon", success=True)
    except Exception as exc:
        logger.exception("Nervous daemon cycle failed: %s", exc)
        _write_run_status("jake_nervous_daemon", success=False)
        sys.exit(1)


def _write_run_status(job_name: str, success: bool) -> None:
    """Write a small JSON status file for pulse monitor freshness checks."""
    import json
    log_dir = str(Path.home() / ".hermes" / "logs")
    os.makedirs(log_dir, exist_ok=True)
    status_file = os.path.join(log_dir, f"{job_name}.status.json")
    try:
        with open(status_file, "w") as f:
            json.dump({
                "job": job_name,
                "status": "ok" if success else "error",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }, f)
    except Exception as e:
        logger.warning("Could not write status file: %s", e)


if __name__ == "__main__":
    main()
