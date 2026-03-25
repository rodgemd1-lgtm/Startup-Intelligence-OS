#!/usr/bin/env python3
"""PAI V3: Email Triage Pipeline

Scans all unread email, applies urgency scoring + VIP detection,
and produces a prioritized action list.

Scoring model:
  U5 = CRITICAL (urgent keywords, flagged VIP)
  U4 = HIGH (VIP sender, flagged, action required)
  U3 = MEDIUM (meeting-related, known domains, direct reply)
  U2 = LOW (general unread)
  U1 = NOISE (newsletters, marketing, no-reply senders)

Actions:
  - Reply needed
  - Review needed
  - Archive (noise)
  - Flag for later
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MAIL_CLI = Path.home() / "go" / "bin" / "mail-app-cli"

# --- VIP CONFIGURATION ---
VIP_DOMAINS = {
    "oracle.com": "Oracle (Work)",
}

VIP_NAMES = [
    "jordan voss", "jordan", "voss",
]

# Domains that indicate a real person (not marketing)
REAL_DOMAINS = [
    "oracle.com", "gmail.com", "outlook.com", "hotmail.com",
    "icloud.com", "me.com", "mac.com", "yahoo.com",
]

NOISE_PATTERNS = [
    "noreply", "no-reply", "donotreply", "mailer-daemon",
    "notifications@", "updates@", "marketing@", "news@",
    "promotions@", "newsletter@", "info@", "hello@",
    "support@", "team@", "announce", "digest@",
]

URGENT_KEYWORDS = [
    "urgent", "asap", "critical", "action required", "deadline",
    "immediately", "time sensitive", "expiring", "final notice",
    "p0", "p1", "sev1", "sev2", "incident", "outage",
]

MEETING_KEYWORDS = [
    "meeting", "calendar", "invite", "rsvp", "agenda",
    "sync", "standup", "1:1", "one-on-one", "review",
]


def run_cmd(cmd: list[str], timeout: int = 30) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return json.dumps({"error": str(e)})


def get_emails(account: str, mailbox: str = "INBOX") -> list[dict]:
    raw = run_cmd([str(MAIL_CLI), "messages", "list",
                   "--account", account, "--mailbox", mailbox, "--unread"])
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def triage_email(msg: dict) -> dict:
    """Full triage of a single email."""
    sender = msg.get("Sender", "").lower()
    subject = msg.get("Subject", "").lower()
    content = msg.get("Content", "").lower()[:500]  # First 500 chars only
    flagged = msg.get("Flagged", False)
    to_list = msg.get("ToRecipients", [])
    cc_list = msg.get("CcRecipients", [])

    # --- Is this a VIP? ---
    is_vip = False
    vip_label = None
    for domain, label in VIP_DOMAINS.items():
        if domain in sender:
            is_vip = True
            vip_label = label
            break
    for name in VIP_NAMES:
        if name in sender:
            is_vip = True
            vip_label = f"VIP: {name}"
            break

    # --- Is this noise? ---
    is_noise = any(p in sender for p in NOISE_PATTERNS)

    # --- Is this from a real person? ---
    is_real_person = any(d in sender for d in REAL_DOMAINS) and not is_noise

    # --- Am I in To vs CC? ---
    my_emails = ["michael.rodgers1976@icloud.com", "mike.r.rodgers@oracle.com", "mike@mketech.org"]
    am_direct = any(any(me in str(r).lower() for me in my_emails) for r in to_list) if to_list else True
    am_cc = any(any(me in str(r).lower() for me in my_emails) for r in cc_list) if cc_list else False

    # --- Urgency scoring ---
    urgency = 2
    reasons = []

    if is_noise:
        urgency = 1
        reasons.append("noise sender")

    if is_real_person and not is_noise:
        urgency = max(urgency, 2)

    if any(k in subject for k in MEETING_KEYWORDS):
        urgency = max(urgency, 3)
        reasons.append("meeting-related")

    if is_vip:
        urgency = max(urgency, 4)
        reasons.append(f"VIP: {vip_label}")

    if flagged:
        urgency = max(urgency, 4)
        reasons.append("flagged")

    if any(k in subject or k in content[:200] for k in URGENT_KEYWORDS):
        urgency = 5
        reasons.append("urgent keywords")

    # --- Recommended action ---
    if urgency >= 4:
        action = "Reply needed" if am_direct else "Review needed"
    elif urgency == 3:
        action = "Review needed"
    elif urgency <= 1:
        action = "Archive"
    else:
        action = "Flag for later"

    if am_cc and urgency < 4:
        action = "FYI only (CC'd)"

    return {
        "id": msg.get("ID", ""),
        "account": msg.get("Account", ""),
        "sender": msg.get("Sender", ""),
        "subject": msg.get("Subject", "(no subject)"),
        "date": msg.get("DateReceived", ""),
        "urgency": urgency,
        "is_vip": is_vip,
        "vip_label": vip_label,
        "is_noise": is_noise,
        "is_real_person": is_real_person,
        "am_direct": am_direct,
        "am_cc": am_cc,
        "reasons": reasons,
        "action": action,
    }


def run_triage() -> dict:
    """Run full email triage across all accounts."""
    now = datetime.now()

    icloud_raw = get_emails("iCloud")
    exchange_raw = get_emails("Exchange")

    icloud = [triage_email(m) for m in icloud_raw]
    exchange = [triage_email(m) for m in exchange_raw]

    all_triaged = sorted(icloud + exchange, key=lambda x: x["urgency"], reverse=True)

    return {
        "generated": now.isoformat(),
        "total": len(all_triaged),
        "by_urgency": {
            "U5_critical": [e for e in all_triaged if e["urgency"] == 5],
            "U4_high": [e for e in all_triaged if e["urgency"] == 4],
            "U3_medium": [e for e in all_triaged if e["urgency"] == 3],
            "U2_low": [e for e in all_triaged if e["urgency"] == 2],
            "U1_noise": [e for e in all_triaged if e["urgency"] == 1],
        },
        "stats": {
            "critical": sum(1 for e in all_triaged if e["urgency"] == 5),
            "high": sum(1 for e in all_triaged if e["urgency"] == 4),
            "medium": sum(1 for e in all_triaged if e["urgency"] == 3),
            "low": sum(1 for e in all_triaged if e["urgency"] == 2),
            "noise": sum(1 for e in all_triaged if e["urgency"] == 1),
            "vip_total": sum(1 for e in all_triaged if e["is_vip"]),
            "reply_needed": sum(1 for e in all_triaged if e["action"] == "Reply needed"),
            "archive_candidates": sum(1 for e in all_triaged if e["action"] == "Archive"),
        },
    }


def print_triage(result: dict):
    """Print human-readable triage report."""
    print("=== EMAIL TRIAGE REPORT ===")
    print(f"Generated: {result['generated']}")
    print(f"Total unread: {result['total']}")
    print()

    s = result["stats"]
    print("## Summary")
    print(f"  Critical (U5): {s['critical']}")
    print(f"  High (U4):     {s['high']}")
    print(f"  Medium (U3):   {s['medium']}")
    print(f"  Low (U2):      {s['low']}")
    print(f"  Noise (U1):    {s['noise']}")
    print(f"  ---")
    print(f"  VIP messages:      {s['vip_total']}")
    print(f"  Reply needed:      {s['reply_needed']}")
    print(f"  Archive candidates: {s['archive_candidates']}")
    print()

    for level, label in [
        ("U5_critical", "CRITICAL"),
        ("U4_high", "HIGH PRIORITY"),
        ("U3_medium", "MEDIUM"),
    ]:
        msgs = result["by_urgency"][level]
        if msgs:
            print(f"## {label}")
            for m in msgs[:10]:
                sender = m["sender"][:30]
                subj = m["subject"][:45]
                act = m["action"]
                reasons = ", ".join(m["reasons"]) if m["reasons"] else ""
                print(f"  [{act}] {sender}: {subj}")
                if reasons:
                    print(f"         ({reasons})")
            print()

    noise = result["by_urgency"]["U1_noise"]
    if noise:
        print(f"## NOISE ({len(noise)} messages — safe to archive)")
        for m in noise[:5]:
            print(f"  {m['sender'][:30]}: {m['subject'][:45]}")
        if len(noise) > 5:
            print(f"  ... and {len(noise) - 5} more")

    print()
    print("=== END TRIAGE ===")


if __name__ == "__main__":
    result = run_triage()
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        print_triage(result)
