#!/usr/bin/env python3
"""Weekly goal progress report — sent to Mike via Telegram.

Usage:
  python jake_goal_weekly.py          # send report
  python jake_goal_weekly.py --dry-run  # print without sending
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
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


def format_report(dashboard: dict) -> str:
    now = datetime.now(timezone.utc)
    lines = [
        f"📊 *Weekly Goal Check-in* — {now.strftime('%B %d, %Y')}",
        "",
        f"Active: {dashboard['active']}  |  Completed: {dashboard['completed']}  |  Overdue: {dashboard['overdue']}",
        "",
    ]

    if dashboard["overdue_goals"]:
        lines.append("⚠️ *OVERDUE*:")
        for g in dashboard["overdue_goals"]:
            lines.append(f"  • {g['title']} (due {g['deadline'][:10]})")
        lines.append("")

    if dashboard["behind_goals"]:
        lines.append("🔴 *BEHIND SCHEDULE*:")
        for g in dashboard["behind_goals"]:
            pct = (g.get("current_value", 0) / g["target_value"]) * 100 if g.get("target_value") else 0
            lines.append(f"  • {g['title']} ({pct:.0f}%)")
        lines.append("")

    if dashboard["active_goals"]:
        lines.append("📋 *Active Goals*:")
        for g in dashboard["active_goals"][:10]:
            progress = ""
            if g.get("target_value") and g["target_value"] > 0:
                pct = (g.get("current_value", 0) / g["target_value"]) * 100
                progress = f" — {pct:.0f}%"
            deadline = f" (due {g['deadline'][:10]})" if g.get("deadline") else ""
            lines.append(f"  • [{g['priority']}] {g['title']}{progress}{deadline}")

    if not dashboard["active_goals"]:
        lines.append("_No active goals. Set some with: goal for [project]_")

    return "\n".join(lines)


def send_telegram(text: str) -> bool:
    import requests
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return False
    resp = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
        timeout=10,
    )
    return resp.ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    from jake_brain.goals import GoalStore
    store = GoalStore()
    dashboard = store.dashboard()
    report = format_report(dashboard)

    if args.dry_run:
        print(report)
        return

    if dashboard["active"] == 0:
        print("No active goals — skipping report.")
        return

    if send_telegram(report):
        print(f"✅ Weekly goal report sent ({dashboard['active']} active goals)")
    else:
        print("❌ Failed to send weekly goal report")


if __name__ == "__main__":
    main()
