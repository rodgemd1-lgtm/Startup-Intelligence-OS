#!/usr/bin/env python3
"""PAI V3: Meeting Prep Pipeline

Generates pre-meeting context briefs by:
1. Pulling upcoming meetings from Calendar
2. Searching email for related threads
3. Checking Susan RAG for company/contact context
4. Producing a structured prep brief

Designed to run 15-30 min before each meeting.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MAIL_CLI = Path.home() / "go" / "bin" / "mail-app-cli"
SUSAN_DATA = Path.home() / "Desktop" / "Startup-Intelligence-OS" / "susan-team-architect" / "backend" / "data"


def run_cmd(cmd: list[str], timeout: int = 30) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def search_emails(query: str, account: str = "iCloud") -> list[dict]:
    """Search emails for a query string."""
    raw = run_cmd([str(MAIL_CLI), "search", query, "--account", account])
    try:
        return json.loads(raw)[:5]  # Top 5 results
    except (json.JSONDecodeError, TypeError):
        return []


def search_susan_rag(query: str) -> list[dict]:
    """Search Susan's RAG data for relevant context."""
    results = []
    if not SUSAN_DATA.exists():
        return results

    # Search through company directories for matching content
    for company_dir in SUSAN_DATA.iterdir():
        if not company_dir.is_dir():
            continue
        for json_file in company_dir.glob("**/*.json"):
            try:
                data = json.loads(json_file.read_text())
                content = json.dumps(data).lower()
                if query.lower() in content:
                    results.append({
                        "source": str(json_file.relative_to(SUSAN_DATA)),
                        "company": company_dir.name,
                        "snippet": content[:200],
                    })
            except (json.JSONDecodeError, OSError):
                continue
    return results[:3]


def extract_attendees(event_title: str) -> list[str]:
    """Extract likely attendee names from meeting title."""
    # Common patterns: "1:1 with John", "Sync with Team", "Review with Sarah"
    words = event_title.split()
    attendees = []
    skip_words = {
        "meeting", "sync", "standup", "review", "with", "and",
        "the", "a", "an", "for", "on", "re:", "fwd:",
        "1:1", "1-1", "weekly", "daily", "monthly", "bi-weekly",
    }
    for i, word in enumerate(words):
        if word.lower() == "with" and i + 1 < len(words):
            # Grab everything after "with"
            rest = " ".join(words[i + 1:])
            for name in rest.split(" and "):
                name = name.strip().rstrip(".,;:")
                if name and name.lower() not in skip_words:
                    attendees.append(name)
            break
    return attendees


def prep_meeting(title: str, time: str = "", calendar: str = "") -> dict:
    """Build a meeting prep brief for a single meeting."""
    attendees = extract_attendees(title)

    # Search email for related threads
    email_context = []
    search_terms = [title]
    for a in attendees:
        search_terms.append(a)

    for term in search_terms[:3]:  # Limit searches
        for acct in ["iCloud", "Exchange"]:
            results = search_emails(term, acct)
            for r in results:
                email_context.append({
                    "account": acct,
                    "sender": r.get("Sender", ""),
                    "subject": r.get("Subject", ""),
                    "date": r.get("DateReceived", ""),
                })

    # Deduplicate by subject
    seen = set()
    unique_emails = []
    for e in email_context:
        if e["subject"] not in seen:
            seen.add(e["subject"])
            unique_emails.append(e)

    # Search Susan RAG for company context
    rag_context = []
    for term in search_terms[:2]:
        rag_context.extend(search_susan_rag(term))

    return {
        "meeting": title,
        "time": time,
        "calendar": calendar,
        "attendees_detected": attendees,
        "related_emails": unique_emails[:5],
        "rag_context": rag_context[:3],
        "prep_notes": generate_prep_notes(title, attendees, unique_emails, rag_context),
    }


def generate_prep_notes(title: str, attendees: list, emails: list, rag: list) -> list[str]:
    """Generate actionable prep notes."""
    notes = []
    if attendees:
        notes.append(f"Attendees: {', '.join(attendees)}")
    if emails:
        notes.append(f"Found {len(emails)} related email thread(s) — review before meeting")
    if rag:
        notes.append(f"Susan has context on: {', '.join(r['company'] for r in rag)}")
    if not emails and not rag:
        notes.append("No prior context found — this may be a new conversation")
    if any(kw in title.lower() for kw in ["1:1", "1-1", "one-on-one"]):
        notes.append("1:1 format — prepare personal updates and blockers")
    if any(kw in title.lower() for kw in ["review", "demo"]):
        notes.append("Review/demo format — prepare walkthrough materials")
    if any(kw in title.lower() for kw in ["standup", "sync"]):
        notes.append("Status sync — prepare 3-bullet update (done, doing, blocked)")
    return notes


def print_prep(result: dict):
    """Print human-readable meeting prep brief."""
    print(f"=== MEETING PREP: {result['meeting']} ===")
    if result["time"]:
        print(f"Time: {result['time']} [{result['calendar']}]")
    print()

    if result["prep_notes"]:
        print("## Prep Notes")
        for note in result["prep_notes"]:
            print(f"  - {note}")
        print()

    if result["related_emails"]:
        print("## Related Email Threads")
        for e in result["related_emails"]:
            sender = e["sender"][:30]
            subj = e["subject"][:50]
            print(f"  {sender}: {subj}")
        print()

    if result["rag_context"]:
        print("## Susan RAG Context")
        for r in result["rag_context"]:
            print(f"  [{r['company']}] {r['source']}")
        print()

    print("=== END PREP ===")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "--json":
        # Prep a specific meeting by title
        title = " ".join(a for a in sys.argv[1:] if a != "--json")
        result = prep_meeting(title)
    else:
        # Default: prep the next meeting (placeholder — needs calendar integration)
        result = prep_meeting("Next Meeting", "TBD", "TBD")

    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        print_prep(result)
