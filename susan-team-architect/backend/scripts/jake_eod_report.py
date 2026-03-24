#!/usr/bin/env python3
"""jake_eod_report.py — Jake's 6 PM end-of-day report.

What shipped, what got stuck, goals movement, tomorrow's top priority.

Usage:
    python3 jake_eod_report.py --telegram
    python3 jake_eod_report.py              # stdout only
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

SUSAN_BACKEND = os.path.expanduser(
    "~/Startup-Intelligence-OS/susan-team-architect/backend"
)
if SUSAN_BACKEND not in sys.path:
    sys.path.insert(0, SUSAN_BACKEND)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s — %(message)s")
logger = logging.getLogger("jake_eod_report")


def load_env():
    hermes_env = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(hermes_env):
        with open(hermes_env) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())


def get_supabase():
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")
        if not url or not key:
            return None
        return create_client(url, key)
    except Exception as e:
        logger.warning("Supabase unavailable: %s", e)
        return None


def fetch_tasks_eod(sb) -> dict:
    """Fetch all tasks, categorized by completion status."""
    if not sb:
        return {}
    try:
        r = sb.table("jake_tasks").select(
            "task_text,status,priority,completed_at,due_date"
        ).execute()
        tasks = r.data or []
        completed = []
        still_pending = []
        blocked = []
        for t in tasks:
            s = t.get("status", "pending")
            if s == "completed":
                completed.append(t)
            elif s == "blocked":
                blocked.append(t)
            elif s in ("pending", "in_progress"):
                still_pending.append(t)
        # Sort completed by completed_at desc
        completed.sort(key=lambda t: t.get("completed_at") or "", reverse=True)
        return {
            "completed": completed[:8],
            "pending": still_pending[:5],
            "blocked": blocked[:3],
        }
    except Exception as e:
        logger.warning("EOD tasks fetch failed: %s", e)
        return {}


def fetch_goals_eod(sb) -> list[dict]:
    if not sb:
        return []
    try:
        r = sb.table("jake_goals").select(
            "title,status,current_value,target_value,description"
        ).in_("status", ["active", "completed"]).order("created_at").limit(6).execute()
        return r.data or []
    except Exception as e:
        logger.warning("Goals fetch failed: %s", e)
        return []


def fetch_todays_learnings(sb) -> list[str]:
    """Pull today's procedural memories for learning signals."""
    if not sb:
        return []
    try:
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        ).isoformat()
        r = sb.table("jake_procedural").select("content,pattern_type,confidence").gte(
            "created_at", today_start
        ).order("confidence", desc=True).limit(5).execute()
        return [
            f"[{row.get('pattern_type','?')}] {row.get('content','')[:100]}"
            for row in (r.data or [])
        ]
    except Exception as e:
        logger.warning("Learnings fetch failed: %s", e)
        return []


def pick_tomorrow_priority(pending: list[dict], goals: list[dict]) -> str:
    """Identify the #1 thing for tomorrow."""
    # Overdue tasks (past due_date)
    now = datetime.now(timezone.utc)
    for t in pending:
        due = t.get("due_date")
        if due:
            try:
                dt = datetime.fromisoformat(str(due).replace("Z", "+00:00"))
                if dt < now:
                    return t.get("task_text", "")[:200] + " (OVERDUE)"
            except Exception:
                pass
    # High priority pending
    for t in pending:
        if t.get("priority") in ("high", "critical"):
            return t.get("task_text", "")[:200]
    # First pending goal with no progress
    for g in goals:
        if g.get("status") == "active" and (g.get("current_value", 0) or 0) == 0:
            return g.get("title", "")[:200]
    # First pending task
    if pending:
        return pending[0].get("task_text", "")[:200]
    # First active goal
    active_goals = [g for g in goals if g.get("status") == "active"]
    if active_goals:
        return active_goals[0].get("title", "")[:200]
    return "Plan tomorrow's priorities."


def assess_day(completed: list, pending: list, blocked: list) -> tuple[str, str]:
    """Grade the day."""
    done_count = len(completed)
    pending_count = len(pending)
    blocked_count = len(blocked)
    total = done_count + pending_count + blocked_count

    if total == 0:
        return "⚪", "No tasks tracked today."
    rate = done_count / total
    if rate >= 0.8:
        return "🟢", f"STRONG day — {done_count}/{total} tasks done"
    if rate >= 0.5:
        return "🟡", f"SOLID day — {done_count}/{total} tasks done"
    if rate >= 0.25:
        return "🟠", f"PARTIAL day — {done_count}/{total} tasks done"
    return "🔴", f"TOUGH day — only {done_count}/{total} tasks done"


def format_eod(task_data: dict, goals: list[dict], learnings: list[str], now: datetime) -> str:
    day_str = now.strftime("%A, %B %-d")
    time_str = now.strftime("%-I:%M %p")

    completed = task_data.get("completed", [])
    pending = task_data.get("pending", [])
    blocked = task_data.get("blocked", [])

    grade_icon, grade_msg = assess_day(completed, pending, blocked)
    tomorrow_priority = pick_tomorrow_priority(pending, goals)

    lines = [
        f"🌙 *EOD REPORT — {day_str}*",
        f"_{time_str}_\n",
        f"{grade_icon} *{grade_msg}*\n",
    ]

    # What shipped
    if completed:
        lines.append(f"✅ *SHIPPED TODAY ({len(completed)})*")
        for t in completed[:5]:
            lines.append(f"  ✓ {t.get('task_text','?')[:100]}")
        lines.append("")

    # What got stuck
    if pending:
        lines.append(f"⬜ *DIDN'T FINISH ({len(pending)})*")
        for t in pending[:3]:
            lines.append(f"  • {t.get('task_text','?')[:100]}")
        lines.append("")

    if blocked:
        lines.append(f"🚫 *STILL BLOCKED ({len(blocked)})*")
        for t in blocked[:3]:
            lines.append(f"  ✗ {t.get('task_text','?')[:100]}")
        lines.append("")

    # Goals movement
    if goals:
        lines.append("📊 *GOALS MOVEMENT*")
        for g in goals[:4]:
            title = g.get("title", "?")[:60]
            cur = g.get("current_value", 0) or 0
            tgt = g.get("target_value")
            status = g.get("status", "active")
            if status == "completed":
                lines.append(f"  🏁 DONE — {title}")
            elif tgt and float(tgt) > 0:
                pct = int((float(cur) / float(tgt)) * 100)
                lines.append(f"  {pct}% — {title}")
            else:
                lines.append(f"  {'🟢' if cur > 0 else '⚪'} {title}")
        lines.append("")

    # Learnings captured today
    if learnings:
        lines.append("🧠 *JAKE LEARNED TODAY*")
        for l in learnings[:3]:
            lines.append(f"  • {l}")
        lines.append("")

    # Tomorrow's #1 priority
    lines.append("🎯 *TOMORROW'S #1 PRIORITY*")
    lines.append(tomorrow_priority)
    lines.append("")

    lines.append("_Reply to Jake with corrections or pivots. See you at 7 AM._")
    return "\n".join(lines)


def send_telegram(text: str) -> bool:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("HERMES_TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        logger.error("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return False
    try:
        payload = json.dumps({
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
        }).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            if data.get("ok"):
                logger.info("Telegram: delivered")
                return True
            logger.error("Telegram API error: %s", data)
            return False
    except Exception as e:
        logger.error("Telegram send failed: %s", e)
        return False


def main():
    parser = argparse.ArgumentParser(description="Jake's 6 PM EOD Report")
    parser.add_argument("--telegram", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    load_env()
    now = datetime.now(timezone.utc).astimezone()
    sb = get_supabase()

    logger.info("Assembling EOD report...")
    task_data = fetch_tasks_eod(sb)
    goals = fetch_goals_eod(sb)
    learnings = fetch_todays_learnings(sb)

    report = format_eod(task_data, goals, learnings, now)

    print("\n" + "=" * 60)
    print(report)
    print("=" * 60 + "\n")

    if args.telegram:
        logger.info("Sending to Telegram...")
        ok = send_telegram(report)
        if not ok:
            logger.warning("Telegram delivery failed — report was still generated.")

    # Write run-status file for pulse monitor freshness checks
    _write_run_status("jake_eod_report", success=True)


def _write_run_status(job_name: str, success: bool) -> None:
    """Write a small JSON status file for pulse monitor freshness checks."""
    import json as _json
    log_dir = os.path.expanduser("~/.hermes/logs")
    os.makedirs(log_dir, exist_ok=True)
    status_file = os.path.join(log_dir, f"{job_name}.status.json")
    try:
        with open(status_file, "w") as f:
            _json.dump({
                "job": job_name,
                "status": "ok" if success else "error",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }, f)
    except Exception as e:
        logger.warning("Could not write status file: %s", e)


if __name__ == "__main__":
    main()
