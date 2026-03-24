#!/usr/bin/env python3
"""jake_midday_pulse.py — Jake's 12 PM midday check-in.

Checks progress vs morning's plan. Flags if anything is off-track.
Surfaces what's blocking and recommends afternoon focus.

Usage:
    python3 jake_midday_pulse.py --telegram
    python3 jake_midday_pulse.py              # stdout only
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
logger = logging.getLogger("jake_midday_pulse")


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


def fetch_tasks_status(sb) -> dict:
    """Fetch task counts by status for today."""
    if not sb:
        return {}
    try:
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        ).isoformat()
        r = sb.table("jake_tasks").select("task_text,status,priority,due_date").execute()
        tasks = r.data or []
        counts = {"done": 0, "in_progress": 0, "pending": 0, "blocked": 0}
        blocked_tasks = []
        in_progress_tasks = []
        pending_tasks = []
        for t in tasks:
            s = t.get("status", "pending")
            if s == "completed":
                counts["done"] += 1
            elif s == "in_progress":
                counts["in_progress"] += 1
                in_progress_tasks.append(t)
            elif s == "blocked":
                counts["blocked"] += 1
                blocked_tasks.append(t)
            else:
                counts["pending"] += 1
                pending_tasks.append(t)
        return {
            "counts": counts,
            "blocked": blocked_tasks[:3],
            "in_progress": in_progress_tasks[:3],
            "pending": pending_tasks[:3],
        }
    except Exception as e:
        logger.warning("Task status fetch failed: %s", e)
        return {}


def fetch_active_goals(sb) -> list[dict]:
    if not sb:
        return []
    try:
        r = sb.table("jake_goals").select(
            "title,current_value,target_value"
        ).eq("status", "active").limit(5).execute()
        return r.data or []
    except Exception as e:
        logger.warning("Goals fetch failed: %s", e)
        return []


def fetch_recent_brain_signals(sb) -> list[str]:
    """Get last 3h of episodic memories for context."""
    if not sb:
        return []
    try:
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
        r = sb.table("jake_episodic").select("content,source").gte(
            "created_at", cutoff
        ).order("created_at", desc=True).limit(5).execute()
        return [row.get("content", "")[:100] for row in (r.data or [])]
    except Exception as e:
        logger.warning("Brain signals fetch failed: %s", e)
        return []


def assess_velocity(counts: dict) -> tuple[str, str]:
    """Assess whether the day is on track."""
    done = counts.get("done", 0)
    in_prog = counts.get("in_progress", 0)
    blocked = counts.get("blocked", 0)
    pending = counts.get("pending", 0)
    total = done + in_prog + blocked + pending

    if total == 0:
        return "⚪", "No tasks loaded — is the day planned?"

    completion_rate = done / total
    if blocked > 2:
        return "🔴", f"{blocked} tasks blocked — find the bottleneck"
    if completion_rate > 0.5:
        return "🟢", f"Solid velocity — {done}/{total} done"
    if completion_rate > 0.25 or in_prog > 0:
        return "🟡", f"Progressing — {done} done, {in_prog} in flight"
    return "🔴", f"Low output — {done}/{total} done. Pivot?"


def format_pulse(task_data: dict, goals: list[dict], signals: list[str], now: datetime) -> str:
    time_str = now.strftime("%-I:%M %p")
    counts = task_data.get("counts", {})
    blocked = task_data.get("blocked", [])
    in_progress = task_data.get("in_progress", [])
    pending = task_data.get("pending", [])

    velocity_icon, velocity_msg = assess_velocity(counts)

    lines = [
        f"⚡ *MIDDAY PULSE — {time_str}*\n",
        f"{velocity_icon} *STATUS: {velocity_msg}*\n",
    ]

    # Task scoreboard
    c = counts
    lines.append(
        f"📊 Tasks: ✅ {c.get('done',0)} done | "
        f"🔄 {c.get('in_progress',0)} active | "
        f"🚫 {c.get('blocked',0)} blocked | "
        f"⬜ {c.get('pending',0)} queued\n"
    )

    # Blocked items (most urgent)
    if blocked:
        lines.append("🚫 *BLOCKED — NEEDS ATTENTION*")
        for t in blocked:
            lines.append(f"  • {t.get('task_text','?')[:100]}")
        lines.append("")

    # Currently in progress
    if in_progress:
        lines.append("🔄 *IN FLIGHT*")
        for t in in_progress:
            lines.append(f"  • {t.get('task_text','?')[:100]}")
        lines.append("")

    # Afternoon focus recommendation
    if pending:
        lines.append("🎯 *AFTERNOON FOCUS*")
        # Pick highest priority pending task
        high_priority = [t for t in pending if t.get("priority") in ("high", "critical")]
        focus_tasks = high_priority if high_priority else pending
        for t in focus_tasks[:2]:
            lines.append(f"  → {t.get('task_text','?')[:100]}")
        lines.append("")

    # Goals snapshot
    if goals:
        lines.append("📈 *GOALS PULSE*")
        for g in goals[:3]:
            title = g.get("title", "?")[:60]
            cur = g.get("current_value", 0) or 0
            tgt = g.get("target_value")
            if tgt and float(tgt) > 0:
                pct = int((float(cur) / float(tgt)) * 100)
                lines.append(f"  {pct}% — {title}")
            else:
                lines.append(f"  {'🟢' if cur > 0 else '⚪'} {title}")
        lines.append("")

    lines.append("_Reply to Jake with updates or pivots._")
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
    parser = argparse.ArgumentParser(description="Jake's 12 PM Midday Pulse")
    parser.add_argument("--telegram", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    load_env()
    now = datetime.now(timezone.utc).astimezone()
    sb = get_supabase()

    logger.info("Running midday pulse check...")
    task_data = fetch_tasks_status(sb)
    goals = fetch_active_goals(sb)
    signals = fetch_recent_brain_signals(sb)

    pulse = format_pulse(task_data, goals, signals, now)

    print("\n" + "=" * 60)
    print(pulse)
    print("=" * 60 + "\n")

    if args.telegram:
        logger.info("Sending to Telegram...")
        ok = send_telegram(pulse)
        if not ok:
            logger.warning("Telegram delivery failed — pulse was still generated.")

    # Write run-status file for pulse monitor freshness checks
    _write_run_status("jake_midday_pulse", success=True)


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
