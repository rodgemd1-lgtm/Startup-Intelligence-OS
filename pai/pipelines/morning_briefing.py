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
    """Get today's calendar events. Tries Orchard MCP first, falls back to osascript."""
    # Try Orchard MCP (fast, rich data)
    try:
        from orchard_client import OrchardClient
        client = OrchardClient()
        now = datetime.now()
        result = client.call("calendar_info", {
            "type": "events",
            "start_date": now.strftime("%Y-%m-%d") + " 00:00",
            "end_date": now.strftime("%Y-%m-%d") + " 23:59",
        })
        if isinstance(result, str) and "error" not in result.lower():
            # Orchard prefixes JSON with text like "Found 2 events:\n"
            # Extract the JSON portion
            data = None
            json_start = result.find("{")
            if json_start >= 0:
                try:
                    data = json.loads(result[json_start:])
                except (json.JSONDecodeError, TypeError):
                    data = None
        elif isinstance(result, dict) and "events" in result:
            data = result
        else:
            data = None

        if data and "events" in data:
            events = []
            for e in data["events"]:
                start = e.get("start_date", "")
                # Extract HH:MM from ISO format
                time_str = ""
                if "T" in start:
                    time_part = start.split("T")[1][:5]
                    h, m = int(time_part[:2]), int(time_part[3:5])
                    ampm = "AM" if h < 12 else "PM"
                    h12 = h if h <= 12 else h - 12
                    if h12 == 0:
                        h12 = 12
                    time_str = f"{h12}:{m:02d} {ampm}"
                events.append({
                    "calendar": e.get("calendar", ""),
                    "time": time_str,
                    "title": e.get("title", "(no title)"),
                    "location": e.get("location", ""),
                    "all_day": e.get("all_day", False),
                })
            return sorted(events, key=lambda ev: ev["time"])
    except Exception:
        pass  # Fall through to osascript

    # Fallback: osascript (slow but works without Orchard)
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


def build_v4_briefing() -> str:
    """Build V4 morning brief using the new intelligence modules.

    Integrates: BriefFormatter + PriorityEngine + SCOUT + email + calendar.
    Returns formatted markdown string.
    """
    # Import V4 modules (late import to avoid circular deps)
    from pai.intelligence.brief_formatter import BriefFormatter, BriefData
    from pai.intelligence.priority_engine import PriorityEngine, CandidateAction, ActionSource
    from pai.intelligence.scout import Scout

    # Collect raw data from V3 pipeline
    raw = build_briefing()

    # Calculate available deep work hours from calendar
    meeting_count = len(raw.get("calendar", []))
    # Assume 10h day, 0.75h per meeting average
    free_hours = max(0, 10.0 - meeting_count * 0.75)

    # Build candidate actions for priority engine
    candidates = []

    # Urgent emails become candidates
    all_emails = raw["email"].get("icloud", []) + raw["email"].get("exchange", [])
    for e in all_emails:
        if e.get("urgency", 0) >= 4:
            candidates.append(CandidateAction(
                action=f"Reply to {e.get('sender', '?')}: {e.get('subject', '?')}",
                why=f"Urgency {e['urgency']} — {'VIP' if e.get('is_vip') else 'flagged urgent'}",
                impact="Unblock communication / meet expectation",
                estimated_minutes=15,
                source=ActionSource.EMAIL,
                people=[e.get("sender", "")],
            ))

    # Imminent meetings become candidates
    for event in raw.get("calendar", []):
        candidates.append(CandidateAction(
            action=f"Prepare for: {event.get('title', '?')}",
            why=f"Meeting at {event.get('time', '?')}",
            impact="Show up prepared",
            estimated_minutes=20,
            source=ActionSource.CALENDAR,
        ))

    # Calculate THE ONE THING
    engine = PriorityEngine(available_deep_work_hours=free_hours)
    one_thing = engine.calculate_one_thing(candidates)

    # Run SCOUT for competitive signals
    scout = Scout()
    # Don't run full scan in brief (slow) — just read existing signals
    scout_signals = []
    try:
        signals_file = scout.SIGNALS_DIR / "competitive-signals.jsonl"
        if signals_file.exists():
            with open(signals_file) as f:
                for line in f:
                    try:
                        s = json.loads(line)
                        if s.get("priority") in ("P0", "P1"):
                            scout_signals.append(s)
                    except json.JSONDecodeError:
                        continue
    except OSError:
        pass

    # Assemble brief data
    data = BriefData(
        one_thing_action=one_thing.action,
        one_thing_why=one_thing.why,
        one_thing_impact=one_thing.impact,
        one_thing_time=f"{one_thing.estimated_minutes} min",
        one_thing_blocked=one_thing.blocked_by or "Nothing",
        meetings=raw.get("calendar", []),
        free_hours=free_hours,
        urgent_emails=[e for e in all_emails if e.get("urgency", 0) >= 4],
        total_unread=raw["summary"]["total_unread"],
        vip_count=raw["summary"]["vip_messages"],
        signals=scout_signals[:5],
    )

    # Render
    formatter = BriefFormatter()
    return formatter.morning_brief(data)


if __name__ == "__main__":
    brief = build_briefing()
    if "--v4" in sys.argv:
        print(build_v4_briefing())
    elif "--json" in sys.argv:
        print(json.dumps(brief, indent=2))
    else:
        print_text_brief(brief)
