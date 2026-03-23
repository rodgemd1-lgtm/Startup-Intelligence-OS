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
