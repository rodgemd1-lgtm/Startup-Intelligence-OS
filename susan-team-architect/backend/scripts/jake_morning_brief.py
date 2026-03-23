#!/usr/bin/env python3
"""jake_morning_brief.py — Jake's 7 AM daily briefing to Mike.

Distinct from brain_morning_brief.py (6 AM, data-first).
This is Jake's perspective: goals progress, today's top tasks,
one direct priority call, and a brief system status.

Usage:
    python3 jake_morning_brief.py --telegram
    python3 jake_morning_brief.py              # stdout only
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import urllib.request
from datetime import datetime, timezone

SUSAN_BACKEND = os.path.expanduser(
    "~/Startup-Intelligence-OS/susan-team-architect/backend"
)
if SUSAN_BACKEND not in sys.path:
    sys.path.insert(0, SUSAN_BACKEND)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s — %(message)s")
logger = logging.getLogger("jake_morning_brief")


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


def fetch_active_goals(sb) -> list[dict]:
    if not sb:
        return []
    try:
        r = sb.table("jake_goals").select(
            "title,status,current_value,target_value,description"
        ).eq("status", "active").order("created_at").limit(8).execute()
        return r.data or []
    except Exception as e:
        logger.warning("Goals fetch failed: %s", e)
        return []


def fetch_todays_tasks(sb) -> list[dict]:
    if not sb:
        return []
    try:
        r = sb.table("jake_tasks").select(
            "task_text,status,priority,due_date"
        ).in_("status", ["pending", "in_progress"]).order("priority", desc=True).limit(8).execute()
        return r.data or []
    except Exception as e:
        logger.warning("Tasks fetch failed: %s", e)
        return []


def pick_one_thing(goals: list[dict], tasks: list[dict]) -> str:
    """Pick the single most important thing for today."""
    # Prefer in_progress tasks first
    for t in tasks:
        if t.get("status") == "in_progress":
            return t.get("task_text", "")[:200]
    # Then high-priority pending tasks
    for t in tasks:
        if t.get("priority") in ("high", "critical"):
            return t.get("task_text", "")[:200]
    # Then first active goal with no progress
    for g in goals:
        if g.get("current_value", 0) == 0:
            return g.get("title", "")[:200]
    # Fall back to first task
    if tasks:
        return tasks[0].get("task_text", "")[:200]
    if goals:
        return goals[0].get("title", "")[:200]
    return "Set your top priority for today."


def format_brief(goals: list[dict], tasks: list[dict], now: datetime) -> str:
    day_str = now.strftime("%A, %B %-d")
    time_str = now.strftime("%-I:%M %p")

    one_thing = pick_one_thing(goals, tasks)

    lines = [
        f"⚡ *JAKE MORNING BRIEF — {day_str}*",
        f"_{time_str}_\n",
        f"🎯 *THE ONE THING TODAY*",
        f"{one_thing}\n",
    ]

    # Goals progress
    if goals:
        lines.append("📊 *ACTIVE GOALS*")
        for g in goals[:5]:
            title = g.get("title", "?")[:80]
            cur = g.get("current_value", 0) or 0
            tgt = g.get("target_value")
            if tgt and float(tgt) > 0:
                pct = int((float(cur) / float(tgt)) * 100)
                bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
                lines.append(f"  {bar} {pct}% — {title}")
            else:
                status_icon = "🟢" if cur > 0 else "⚪"
                lines.append(f"  {status_icon} {title}")
        lines.append("")

    # Top tasks
    if tasks:
        lines.append("✅ *TODAY'S TASKS*")
        for t in tasks[:5]:
            task = t.get("task_text", "?")[:100]
            status = t.get("status", "pending")
            icon = {"in_progress": "🔄", "pending": "⬜", "blocked": "🚫"}.get(status, "⬜")
            lines.append(f"  {icon} {task}")
        lines.append("")

    lines.append("_Reply to Jake with updates, corrections, or new priorities._")

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
    parser = argparse.ArgumentParser(description="Jake's 7 AM Morning Brief")
    parser.add_argument("--telegram", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    load_env()
    now = datetime.now(timezone.utc).astimezone()
    sb = get_supabase()

    logger.info("Fetching goals and tasks...")
    goals = fetch_active_goals(sb)
    tasks = fetch_todays_tasks(sb)
    logger.info("Goals: %d, Tasks: %d", len(goals), len(tasks))

    brief = format_brief(goals, tasks, now)

    print("\n" + "=" * 60)
    print(brief)
    print("=" * 60 + "\n")

    if args.telegram:
        logger.info("Sending to Telegram...")
        ok = send_telegram(brief)
        if ok:
            logger.info("Morning brief delivered.")
        else:
            logger.error("Telegram delivery failed.")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
