"""Meeting Prep Scanner — detect meetings starting in ~15 min and launch full autonomous prep.

Sources:
  - Google Calendar (OAuth API via brain_calendar_ingest patterns)
  - Apple Calendar (osascript, non-Exchange accounts)

Alert window: 13–17 min before meeting start (fires when daemon runs in that range)

Flow:
  1. Detect meeting in alert window
  2. Emit NervousEvent (for dedup + Telegram "prep starting" message)
  3. Launch MeetingOrchestrator in background thread
  4. Orchestrator runs 4 research phases via Claude Code MCP tools
  5. Saves docs/meeting-prep/{date}-{slug}/BRIEF.md + sends detailed Telegram
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from typing import Any

from .event_bus import EventBus, NervousEvent, EventType

logger = logging.getLogger(__name__)

PREP_WINDOW_MIN = 13   # minutes before meeting
PREP_WINDOW_MAX = 17   # minutes before meeting


def _fetch_google_events_soon(minutes_ahead: int = 20) -> list[dict[str, Any]]:
    """Fetch upcoming Google Calendar events in the next N minutes."""
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        import pickle

        token_file = os.path.expanduser("~/.hermes/google_token.pickle")
        if not os.path.exists(token_file):
            return []

        with open(token_file, "rb") as f:
            creds = pickle.load(f)

        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        now = datetime.now(timezone.utc)
        time_max = now + timedelta(minutes=minutes_ahead)

        events_result = service.events().list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=time_max.isoformat(),
            singleEvents=True,
            orderBy="startTime",
            maxResults=10,
        ).execute()

        items = events_result.get("items", [])
        results = []
        for item in items:
            start = item.get("start", {})
            start_str = start.get("dateTime") or start.get("date")
            results.append({
                "id": item.get("id", ""),
                "summary": item.get("summary", "Untitled"),
                "start": start_str,
                "location": item.get("location", ""),
                "description": item.get("description", "")[:200],
                "attendees": [a.get("email", "") for a in item.get("attendees", [])],
                "hangout": item.get("hangoutLink", ""),
                "source": "google",
            })
        return results

    except Exception as exc:
        logger.debug("Google Calendar fetch failed: %s", exc)
        return []


def _fetch_apple_events_soon(minutes_ahead: int = 20) -> list[dict[str, Any]]:
    """Fetch upcoming Apple Calendar events via osascript (non-Exchange calendars)."""
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
        // Skip Exchange/Oracle (handled separately or slow)
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
}}
"""
    try:
        result = subprocess.run(
            ["osascript", "-l", "JavaScript", "-e", script],
            capture_output=True, text=True, timeout=20
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout.strip())
    except Exception as exc:
        logger.debug("Apple Calendar fetch failed: %s", exc)
    return []


def _minutes_until(start_str: str) -> float | None:
    """Return minutes until the event starts. None if unparseable."""
    if not start_str:
        return None
    try:
        # Handle date-only events
        if "T" not in start_str and len(start_str) == 10:
            return None  # All-day event, skip
        # Parse ISO or JS Date strings
        from dateutil import parser as dtparser
        start_dt = dtparser.parse(start_str)
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = (start_dt - now).total_seconds() / 60
        return delta
    except Exception:
        return None


def _format_prep_starting_message(event: dict[str, Any], minutes_left: float) -> str:
    """Format an immediate 'prep starting' Telegram message while orchestrator runs."""
    summary = event.get("summary", "Meeting")
    location = event.get("location", "")
    hangout = event.get("hangout", "")
    attendees = event.get("attendees", [])

    lines = [f"📅 *{summary}* in ~{int(minutes_left)} min"]
    lines.append("🔍 _Running full prep: attendee intel, topic research, strategic analysis..._")

    if hangout:
        lines.append(f"🔗 [Join]({hangout})")
    elif location:
        lines.append(f"📍 {location}")
    if attendees:
        att_str = ", ".join(attendees[:4])
        if len(attendees) > 4:
            att_str += f" +{len(attendees)-4} more"
        lines.append(f"👥 {att_str}")

    lines.append("\n_Full prep brief incoming in ~3 min._")
    return "\n".join(lines)


def _launch_orchestrator(event: dict[str, Any], minutes_left: float) -> None:
    """Launch the MeetingOrchestrator in a background thread."""
    try:
        import sys
        backend_dir = str(Path(__file__).resolve().parent.parent.parent)
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)

        from jake_brain.meeting_orchestrator import MeetingOrchestrator
        orch = MeetingOrchestrator()
        thread = orch.orchestrate_background(event, minutes_left)
        logger.info("Meeting orchestrator launched in thread: %s", thread.name)
    except Exception as exc:
        logger.error("Failed to launch meeting orchestrator: %s", exc)


class MeetingPrepScanner:
    """Scan for upcoming meetings and emit prep brief events."""

    def __init__(self, bus: EventBus):
        self.bus = bus

    def scan(self) -> list[NervousEvent]:
        """Scan for meetings 13–17 min away and emit prep events."""
        new_events: list[NervousEvent] = []

        # Fetch from both sources
        all_events = _fetch_google_events_soon(minutes_ahead=20)
        all_events += _fetch_apple_events_soon(minutes_ahead=20)

        for cal_event in all_events:
            start_str = cal_event.get("start", "")
            minutes_left = _minutes_until(start_str)
            if minutes_left is None:
                continue
            if not (PREP_WINDOW_MIN <= minutes_left <= PREP_WINDOW_MAX):
                continue

            event_id = f"meeting_prep:{cal_event.get('id') or cal_event.get('summary')}:{int(minutes_left)}"
            # Round to 2 min buckets to handle repeated daemon runs
            bucket = int(minutes_left / 2) * 2
            event_id = f"meeting_prep:{cal_event.get('id') or cal_event.get('summary')}:b{bucket}"

            summary = cal_event.get("summary", "Meeting")
            # Immediate "prep starting" message — full brief arrives from orchestrator in ~3 min
            starting_text = _format_prep_starting_message(cal_event, minutes_left)

            nervous_event = NervousEvent(
                event_id=event_id,
                event_type=EventType.MEETING_PREP,
                title=f"Meeting prep: {summary}",
                body=starting_text,
                urgency=0.85,  # Meeting preps are always high priority
                source=cal_event.get("source", "calendar"),
                metadata={
                    "summary": summary,
                    "start": start_str,
                    "minutes_left": minutes_left,
                    "hangout": cal_event.get("hangout", ""),
                },
            )

            if self.bus.emit(nervous_event):
                new_events.append(nervous_event)
                logger.info("Meeting prep triggered: %s in ~%.0f min", summary, minutes_left)
                # Launch full autonomous prep in background (sends its own detailed Telegram when done)
                _launch_orchestrator(cal_event, minutes_left)

        self.bus.update_calendar_check()
        return new_events
