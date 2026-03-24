#!/usr/bin/env python3
"""Rich Meeting Prep — auto-generate prep briefs for upcoming calendar meetings.

This enhances the existing MeetingPrepScanner with brain context:
  - Who are the attendees (from jake_entities + jake_episodic)
  - Last interactions with them
  - Recent relevant emails on the meeting topic
  - Open tasks/goals related to attendees or topic
  - Quick Jake's Take for each meeting

Triggered by:
  - The nervous system daemon (runs every 2 min)
  - Directly 15-30 min before each meeting
  - Can be run manually for any upcoming meeting

Usage:
    python scripts/jake_meeting_prep_rich.py              # check next 30 min
    python scripts/jake_meeting_prep_rich.py --minutes 60 # check next hour
    python scripts/jake_meeting_prep_rich.py --dry-run    # print without sending
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("jake-meeting-prep")

# Deduplicate — don't send the same meeting prep twice
_SENT_CACHE_FILE = Path.home() / ".hermes" / "logs" / "meeting_prep_sent.json"
PREP_WINDOW_MIN = 15   # start prepping at 15 minutes before
PREP_WINDOW_MAX = 35   # don't prep if <35 min ahead (too much notice)


def _load_sent_cache() -> set[str]:
    if _SENT_CACHE_FILE.exists():
        try:
            data = json.loads(_SENT_CACHE_FILE.read_text())
            return set(data.get("sent_ids", []))
        except Exception:
            pass
    return set()


def _save_sent_cache(sent_ids: set[str]) -> None:
    _SENT_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    _SENT_CACHE_FILE.write_text(json.dumps({"sent_ids": list(sent_ids)}, indent=2))


# ---------------------------------------------------------------------------
# Fetch upcoming meetings
# ---------------------------------------------------------------------------

def fetch_upcoming_meetings(minutes_ahead: int = 40) -> list[dict[str, Any]]:
    """Fetch meetings from Google Calendar and Apple Calendar."""
    meetings = []

    # --- Google Calendar ---
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        import pickle

        token_file = Path.home() / ".hermes" / "google_token.pickle"
        if token_file.exists():
            with open(token_file, "rb") as f:
                creds = pickle.load(f)

            service = build("calendar", "v3", credentials=creds, cache_discovery=False)
            now = datetime.now(timezone.utc)
            time_max = now + timedelta(minutes=minutes_ahead)

            result = service.events().list(
                calendarId="primary",
                timeMin=now.isoformat(),
                timeMax=time_max.isoformat(),
                singleEvents=True,
                orderBy="startTime",
                maxResults=10,
            ).execute()

            for item in result.get("items", []):
                start = item.get("start", {})
                start_str = start.get("dateTime") or start.get("date")
                if not start_str or "T" not in start_str:
                    continue  # skip all-day events
                attendees = [a.get("email", "") for a in item.get("attendees", [])]
                meetings.append({
                    "id": item.get("id", ""),
                    "summary": item.get("summary", "Untitled Meeting"),
                    "start": start_str,
                    "location": item.get("location", ""),
                    "description": (item.get("description") or "")[:300],
                    "attendees": attendees,
                    "hangout": item.get("hangoutLink", ""),
                    "source": "google",
                })
    except Exception as e:
        logger.debug(f"Google Calendar fetch error: {e}")

    # --- Apple Calendar (non-Exchange) ---
    try:
        now = datetime.now()
        time_max = now + timedelta(minutes=minutes_ahead)
        script = f"""
ObjC.import('Foundation');
function run() {{
    var app = Application('Calendar');
    var results = [];
    var now = new Date("{now.isoformat()}");
    var maxTime = new Date("{time_max.isoformat()}");
    var cals = app.calendars();
    for (var i = 0; i < cals.length; i++) {{
        var cal = cals[i];
        var calName = cal.name();
        if (calName.toLowerCase().includes('oracle') || calName.toLowerCase().includes('exchange')) continue;
        var events = cal.events();
        for (var j = 0; j < Math.min(20, events.length); j++) {{
            try {{
                var ev = events[j];
                var start = ev.startDate();
                if (start >= now && start <= maxTime) {{
                    results.push({{
                        id: ev.uid ? ev.uid() : '',
                        summary: ev.summary ? ev.summary() : '',
                        start: start.toString(),
                        location: ev.location ? ev.location() : '',
                        source: 'apple'
                    }});
                }}
            }} catch(e) {{}}
        }}
    }}
    return JSON.stringify(results);
}}"""
        result = subprocess.run(
            ["osascript", "-l", "JavaScript", "-e", script],
            capture_output=True, text=True, timeout=20
        )
        if result.returncode == 0 and result.stdout.strip():
            apple_events = json.loads(result.stdout.strip())
            meetings.extend(apple_events)
    except Exception as e:
        logger.debug(f"Apple Calendar fetch error: {e}")

    return meetings


def _minutes_until(start_str: str) -> float | None:
    if not start_str or "T" not in start_str:
        return None
    try:
        from dateutil import parser as dtparser
        start_dt = dtparser.parse(start_str)
        if start_dt.tzinfo is None:
            from dateutil.tz import tzlocal
            start_dt = start_dt.replace(tzinfo=tzlocal())
        now = datetime.now(timezone.utc)
        start_dt_utc = start_dt.astimezone(timezone.utc)
        return (start_dt_utc - now).total_seconds() / 60
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Brain context retrieval
# ---------------------------------------------------------------------------

def _brain_search(query: str, limit: int = 5) -> list[dict]:
    """Search all brain layers for relevant context."""
    try:
        from jake_brain.retriever import BrainRetriever
        retriever = BrainRetriever()
        return retriever.search(query, limit=limit)
    except Exception as e:
        logger.debug(f"Brain search failed: {e}")
        return []


def _get_entity_context(name: str) -> dict | None:
    """Fetch entity record for a person (attendee)."""
    try:
        from supabase import create_client
        from susan_core.config import config

        supabase = create_client(config.supabase_url, config.supabase_key)
        result = (
            supabase.table("jake_entities")
            .select("*")
            .ilike("name", f"%{name}%")
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception as e:
        logger.debug(f"Entity fetch failed: {e}")
        return None


def _get_open_tasks_for_topic(topic: str) -> list[dict]:
    """Find open tasks related to a meeting topic."""
    try:
        from jake_brain.goals.tasks import TaskStore
        store = TaskStore()
        return store.search_tasks(topic, limit=3)
    except Exception as e:
        logger.debug(f"Task search failed: {e}")
        return []


def _get_open_goals_for_topic(topic: str) -> list[dict]:
    """Find active goals related to a meeting topic."""
    try:
        from jake_brain.goals.store import GoalStore
        store = GoalStore()
        return store.search_goals(topic, status="active", limit=3)
    except Exception as e:
        logger.debug(f"Goal search failed: {e}")
        return []


# ---------------------------------------------------------------------------
# Brief formatter
# ---------------------------------------------------------------------------

def build_meeting_brief(meeting: dict) -> str:
    """Build a rich prep brief for a single meeting."""
    summary = meeting.get("summary", "Untitled Meeting")
    start_str = meeting.get("start", "")
    location = meeting.get("location", "")
    attendees = meeting.get("attendees", [])
    description = meeting.get("description", "")
    hangout = meeting.get("hangout", "")

    mins = _minutes_until(start_str)
    time_label = f"{int(mins)} min" if mins is not None else "soon"

    lines = [
        f"📅 *Meeting in {time_label}:* {summary}",
        "",
    ]

    if location:
        lines.append(f"📍 {location}")
    if hangout:
        lines.append(f"🔗 {hangout}")
    lines.append("")

    # Attendee context
    if attendees:
        lines.append("👥 *Attendees:*")
        for email in attendees[:5]:
            name = email.split("@")[0].replace(".", " ").title()
            entity = _get_entity_context(name)
            if entity:
                role = entity.get("metadata", {}).get("role", "") if isinstance(entity.get("metadata"), dict) else ""
                context = entity.get("context") or ""
                line = f"  • {name}"
                if role:
                    line += f" ({role})"
                if context:
                    line += f": {context[:60]}"
                lines.append(line)
            else:
                lines.append(f"  • {email}")
        lines.append("")

    # Topic-based brain context
    brain_context = _brain_search(summary, limit=4)
    if brain_context:
        lines.append("🧠 *Relevant Context:*")
        for item in brain_context[:3]:
            content = item.get("content") or item.get("fact") or ""
            if content:
                lines.append(f"  • {content[:80]}")
        lines.append("")

    # Open tasks related to this meeting
    tasks = _get_open_tasks_for_topic(summary)
    if tasks:
        lines.append("📋 *Open Tasks (related):*")
        for t in tasks[:3]:
            lines.append(f"  • [{t.get('priority','?')}] {t.get('task_text','')[:60]}")
        lines.append("")

    # Open goals related to this meeting
    goals = _get_open_goals_for_topic(summary)
    if goals:
        lines.append("🎯 *Active Goals (related):*")
        for g in goals[:2]:
            lines.append(f"  • {g.get('title','')[:60]}")
        lines.append("")

    # Jake's Take
    lines.append("💡 *Jake's Take:*")
    take_parts = []
    if "battlecard" in summary.lower() or "competitive" in summary.lower():
        take_parts.append("Bring the latest competitive signals — run SOP-08 if you have time.")
    if "1:1" in summary.lower() or "one on one" in summary.lower():
        take_parts.append("Good time to surface blocked items and ask about priorities.")
    if any("cohlmia" in a or "matt" in a.lower() for a in attendees):
        take_parts.append("Matt meeting — prepare your top 3 highlights and 1 ask.")
    if not take_parts:
        take_parts.append("Come prepared with context. First 2 min sets the tone.")
    lines.append(f"  {take_parts[0]}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Telegram send
# ---------------------------------------------------------------------------

def _send_telegram(message: str) -> bool:
    """Send message to Mike via Telegram (calls Hermes API)."""
    import urllib.request
    import urllib.error

    payload = json.dumps({"message": message, "source": "meeting_prep"}).encode()
    try:
        req = urllib.request.Request(
            "http://localhost:4242/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(minutes_ahead: int = 40, dry_run: bool = False) -> list[dict]:
    """Check for upcoming meetings and send prep briefs for any in the window."""
    sent_cache = _load_sent_cache()
    meetings = fetch_upcoming_meetings(minutes_ahead=minutes_ahead)
    processed = []

    for meeting in meetings:
        meeting_id = meeting.get("id", "")
        if not meeting_id:
            continue

        mins = _minutes_until(meeting.get("start", ""))
        if mins is None:
            continue

        # Only send for meetings in the prep window
        if not (PREP_WINDOW_MIN <= mins <= PREP_WINDOW_MAX):
            continue

        # Dedup — don't send twice
        cache_key = f"{meeting_id}:{meeting.get('start','')}"
        if cache_key in sent_cache:
            continue

        brief = build_meeting_brief(meeting)
        logger.info(f"Sending prep brief for: {meeting.get('summary','?')} (in {int(mins)} min)")

        if dry_run:
            print(f"\n{'='*60}")
            print(brief)
        else:
            success = _send_telegram(brief)
            if success:
                sent_cache.add(cache_key)
                _save_sent_cache(sent_cache)

        processed.append(meeting)

    if not processed:
        logger.debug("No meetings in prep window.")

    return processed


def main() -> None:
    parser = argparse.ArgumentParser(description="Rich meeting prep briefer")
    parser.add_argument("--minutes", type=int, default=40, help="Look ahead N minutes")
    parser.add_argument("--dry-run", action="store_true", help="Print without sending")
    args = parser.parse_args()

    meetings = run(minutes_ahead=args.minutes, dry_run=args.dry_run)
    print(f"Processed {len(meetings)} meeting(s).")


if __name__ == "__main__":
    main()
