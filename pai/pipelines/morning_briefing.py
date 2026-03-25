#!/usr/bin/env python3
"""PAI V3: Morning Briefing Pipeline

Collects email summaries + calendar events, produces a structured morning brief.
Designed to be called by Jake or scheduled via cron/LaunchAgent.

Data sources:
  - mail-app-cli (Go CLI → JSON) for iCloud + Exchange email
  - osascript for Calendar events (fallback)
  - Orchard MCP for Calendar when available

Output: structured text brief (stdout) or JSON (--json flag)
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MAIL_CLI = Path.home() / "go" / "bin" / "mail-app-cli"

# VIP senders — messages from these get flagged
VIP_SENDERS = {
    # Oracle / Work
    "oracle.com": "Oracle",
    # Personal VIPs
    "icloud.com": None,  # Not all iCloud is VIP — filtered by name below
}

VIP_NAMES = [
    "jordan", "voss",
]

NOISE_SENDERS = [
    "noreply", "no-reply", "donotreply", "mailer-daemon",
    "notifications@", "updates@", "marketing@", "news@",
    "promotions@", "newsletter@", "info@",
]


def run_cmd(cmd: list[str], timeout: int = 30) -> str:
    """Run a command and return stdout."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return json.dumps({"error": str(e)})


def get_emails(account: str, mailbox: str = "INBOX") -> list[dict]:
    """Get unread emails from a mail account."""
    raw = run_cmd([
        str(MAIL_CLI), "messages", "list",
        "--account", account,
        "--mailbox", mailbox,
        "--unread",
    ])
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def classify_email(msg: dict) -> dict:
    """Classify an email by urgency and VIP status."""
    sender = msg.get("Sender", "").lower()
    subject = msg.get("Subject", "").lower()

    # VIP detection
    is_vip = False
    vip_reason = None
    for domain, label in VIP_SENDERS.items():
        if domain in sender and label:
            is_vip = True
            vip_reason = label
            break
    for name in VIP_NAMES:
        if name in sender:
            is_vip = True
            vip_reason = f"VIP: {name}"
            break

    # Noise detection
    is_noise = any(n in sender for n in NOISE_SENDERS)

    # Urgency scoring (1-5)
    urgency = 2  # default
    if is_vip:
        urgency = 4
    if is_noise:
        urgency = 1
    if any(w in subject for w in ["urgent", "asap", "critical", "action required", "deadline"]):
        urgency = 5
    if any(w in subject for w in ["meeting", "calendar", "invite"]):
        urgency = max(urgency, 3)
    if msg.get("Flagged", False):
        urgency = max(urgency, 4)

    return {
        "id": msg.get("ID", ""),
        "sender": msg.get("Sender", ""),
        "subject": msg.get("Subject", "(no subject)"),
        "date": msg.get("DateReceived", ""),
        "is_vip": is_vip,
        "vip_reason": vip_reason,
        "is_noise": is_noise,
        "urgency": urgency,
    }


def get_calendar_events() -> list[dict]:
    """Get today's calendar events via osascript."""
    script = '''
    tell application "Calendar"
        set today to current date
        set time of today to 0
        set endDay to today + (1 * days)
        set output to ""
        repeat with calName in {"Work", "Home", "Calendar"}
            try
                set evts to every event of calendar calName whose start date >= today and start date < endDay
                repeat with e in evts
                    set h to hours of (start date of e)
                    set m to minutes of (start date of e)
                    if m < 10 then
                        set timeStr to (h as string) & ":0" & (m as string)
                    else
                        set timeStr to (h as string) & ":" & (m as string)
                    end if
                    set output to output & calName & "|" & timeStr & "|" & (summary of e) & linefeed
                end repeat
            end try
        end repeat
        return output
    end tell'''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=15
        )
        events = []
        for line in result.stdout.strip().split("\n"):
            if "|" in line:
                parts = line.split("|", 2)
                if len(parts) == 3:
                    events.append({
                        "calendar": parts[0].strip(),
                        "time": parts[1].strip(),
                        "title": parts[2].strip(),
                    })
        return sorted(events, key=lambda e: e["time"])
    except subprocess.TimeoutExpired:
        return [{"calendar": "?", "time": "?", "title": "Calendar query timed out"}]


def build_briefing() -> dict:
    """Build the complete morning briefing."""
    now = datetime.now()

    # Email
    icloud_raw = get_emails("iCloud")
    exchange_raw = get_emails("Exchange")

    icloud = [classify_email(m) for m in icloud_raw]
    exchange = [classify_email(m) for m in exchange_raw]

    # Sort by urgency descending
    icloud.sort(key=lambda x: x["urgency"], reverse=True)
    exchange.sort(key=lambda x: x["urgency"], reverse=True)

    # Calendar
    events = get_calendar_events()

    # Stats
    all_emails = icloud + exchange
    vip_count = sum(1 for e in all_emails if e["is_vip"])
    urgent_count = sum(1 for e in all_emails if e["urgency"] >= 4)
    noise_count = sum(1 for e in all_emails if e["is_noise"])

    return {
        "generated": now.isoformat(),
        "date": now.strftime("%A, %B %d %Y"),
        "summary": {
            "total_unread": len(all_emails),
            "icloud_unread": len(icloud),
            "exchange_unread": len(exchange),
            "vip_messages": vip_count,
            "urgent_messages": urgent_count,
            "noise_messages": noise_count,
        },
        "email": {
            "icloud": icloud[:10],
            "exchange": exchange[:10],
        },
        "calendar": events,
    }


def print_text_brief(brief: dict):
    """Print human-readable morning briefing."""
    print(f"=== JAKE MORNING BRIEFING ===")
    print(f"Date: {brief['date']}")
    print(f"Generated: {brief['generated']}")
    print()

    s = brief["summary"]
    print(f"## Overview")
    print(f"  Unread: {s['total_unread']} ({s['icloud_unread']} iCloud, {s['exchange_unread']} Exchange)")
    if s["vip_messages"]:
        print(f"  VIP: {s['vip_messages']} messages need attention")
    if s["urgent_messages"]:
        print(f"  URGENT: {s['urgent_messages']} high-priority messages")
    print()

    for acct, label in [("icloud", "iCloud"), ("exchange", "Oracle/Exchange")]:
        msgs = brief["email"][acct]
        if not msgs:
            print(f"## {label}: No unread messages")
            continue
        print(f"## {label} ({len(msgs)} shown)")
        for m in msgs[:7]:
            flag = ""
            if m["urgency"] >= 4:
                flag = " [!!!]"
            elif m["is_vip"]:
                flag = f" [VIP:{m['vip_reason']}]"
            elif m["is_noise"]:
                flag = " [noise]"
            sender = m["sender"][:35]
            subj = m["subject"][:50]
            print(f"  U{m['urgency']} {sender}: {subj}{flag}")
        print()

    print("## Calendar")
    if brief["calendar"]:
        for e in brief["calendar"]:
            print(f"  {e['time']} [{e['calendar']}] {e['title']}")
    else:
        print("  No events today")
    print()
    print("=== END BRIEFING ===")


if __name__ == "__main__":
    brief = build_briefing()
    if "--json" in sys.argv:
        print(json.dumps(brief, indent=2))
    else:
        print_text_brief(brief)
