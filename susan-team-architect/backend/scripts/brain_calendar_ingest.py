#!/usr/bin/env python3
"""Ingest Apple Calendar events into Jake's Brain as episodic memories.

Reads events from Calendar.app via osascript (JXA) and:
1. Creates episodic memories for each calendar event
2. Stores a semantic memory summarizing today's + tomorrow's schedule
3. Creates entities for recurring meeting names
4. Deduplicates on re-runs using content hash stored in metadata.event_id

Usage:
    cd susan-team-architect/backend && source .venv/bin/activate
    python scripts/brain_calendar_ingest.py [--dry-run] [--days-back 7] [--days-forward 30]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from jake_brain.store import BrainStore
from jake_brain.config import brain_config

# Calendar name → topic mapping
CALENDAR_TOPIC_MAP = {
    "exchange": "oracle-health",
    "oracle": "oracle-health",
    "work": "work",
    "family": "family",
    "kids": "family",
    "jacob": "family",
    "alex": "family",
    "birthdays": "family",
    "personal": "personal",
    "home": "personal",
    "us holidays": "holidays",
    "holidays": "holidays",
}

# Calendar name → project mapping
CALENDAR_PROJECT_MAP = {
    "exchange": "oracle-health",
}


def _get_calendar_names() -> list[str]:
    """Get list of calendar names from Calendar.app (fast — no event queries)."""
    script = "var app = Application('Calendar'); JSON.stringify(app.calendars().map(c => c.name()));"
    try:
        result = subprocess.run(
            ["osascript", "-l", "JavaScript", "-e", script],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout.strip())
    except Exception:
        pass
    return []


def _build_jxa_script_single(cal_name: str, days_back: int, days_forward: int) -> str:
    """Build a JXA script that queries ONE calendar by name."""
    escaped = cal_name.replace("'", "\\'")
    return f"""
var app = Application('Calendar');
var now = new Date();
var startDate = new Date(now.getTime() - {days_back} * 24 * 60 * 60 * 1000);
var endDate = new Date(now.getTime() + {days_forward} * 24 * 60 * 60 * 1000);
var results = [];
var cals = app.calendars.whose({{name: '{escaped}'}})();
if (cals.length === 0) {{ JSON.stringify(results); }}
var cal = cals[0];
var events;
try {{
    events = cal.events.whose({{
        _and: [
            {{ startDate: {{ _greaterThan: startDate }} }},
            {{ startDate: {{ _lessThan: endDate }} }}
        ]
    }})();
}} catch(e) {{
    JSON.stringify(results);
}}
for (var j = 0; j < events.length; j++) {{
    var ev = events[j];
    try {{
        var attendeeNames = [];
        try {{
            var attendees = ev.attendees();
            for (var k = 0; k < attendees.length; k++) {{
                try {{ attendeeNames.push(attendees[k].displayName()); }} catch(e2) {{}}
            }}
        }} catch(e3) {{}}
        var obj = {{
            uid: ev.uid(),
            title: ev.summary() || '(No Title)',
            startDate: ev.startDate().toISOString(),
            endDate: ev.endDate().toISOString(),
            location: '',
            notes: '',
            calendarName: '{escaped}',
            allDay: ev.alldayEvent(),
            attendees: attendeeNames
        }};
        try {{ obj.location = ev.location() || ''; }} catch(e4) {{}}
        try {{ obj.notes = ev.description() || ''; }} catch(e5) {{}}
        results.push(obj);
    }} catch(e6) {{}}
}}
JSON.stringify(results);
"""


# Timeout per individual calendar (seconds). Exchange is slow; 25s is generous but bounded.
_PER_CALENDAR_TIMEOUT = 25

# Skip these system/read-only calendar types that never have useful events.
_SKIP_CALENDARS = {"scheduled reminders", "siri suggestions"}


def extract_calendar_events(days_back: int = 7, days_forward: int = 30) -> list[dict]:
    """Extract calendar events from Apple Calendar via osascript JXA.

    Queries one calendar at a time with a 25-second timeout each, so a slow
    Exchange calendar never blocks the entire ingestion run.
    """
    cal_names = _get_calendar_names()
    if not cal_names:
        print("WARNING: Could not list calendars from Calendar.app.")
        return []

    all_events: list[dict] = []
    for cal_name in cal_names:
        if cal_name.lower() in _SKIP_CALENDARS:
            continue
        script = _build_jxa_script_single(cal_name, days_back, days_forward)
        try:
            result = subprocess.run(
                ["osascript", "-l", "JavaScript", "-e", script],
                capture_output=True, text=True,
                timeout=_PER_CALENDAR_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            print(f"  WARNING: '{cal_name}' timed out after {_PER_CALENDAR_TIMEOUT}s — skipping")
            continue

        if result.returncode != 0:
            print(f"  WARNING: '{cal_name}' failed (rc={result.returncode}) — skipping")
            continue

        raw = result.stdout.strip()
        if not raw:
            continue

        try:
            events = json.loads(raw)
            if events:
                print(f"  {cal_name}: {len(events)} events")
            all_events.extend(events)
        except json.JSONDecodeError:
            print(f"  WARNING: '{cal_name}' returned invalid JSON — skipping")

    return all_events


def _event_id(event: dict) -> str:
    """Generate a stable dedup key for an event based on uid + start time."""
    uid = event.get("uid", "")
    start = event.get("startDate", "")
    raw = f"{uid}|{start}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _parse_iso(s: str) -> datetime:
    """Parse an ISO datetime string, handling timezone offsets."""
    if not s:
        return datetime.now(timezone.utc)
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)


def _topics_for_calendar(cal_name: str) -> list[str]:
    """Derive topic tags from calendar name."""
    lower = cal_name.lower().strip()
    topics = ["calendar"]
    for key, topic in CALENDAR_TOPIC_MAP.items():
        if key in lower:
            topics.append(topic)
            break
    else:
        topics.append("personal")
    return topics


def _project_for_calendar(cal_name: str) -> str | None:
    """Derive project from calendar name."""
    lower = cal_name.lower().strip()
    for key, project in CALENDAR_PROJECT_MAP.items():
        if key in lower:
            return project
    return None


def _importance_for_event(event: dict) -> float:
    """Determine importance: 0.8 all-day, 0.7 meetings (has attendees), 0.5 regular."""
    if event.get("allDay"):
        return 0.8
    if event.get("attendees"):
        return 0.7
    return 0.5


def _extract_people(event: dict) -> list[str]:
    """Extract person names from attendees and notes."""
    people = []
    for name in event.get("attendees", []):
        if name and isinstance(name, str):
            cleaned = name.strip()
            # Skip email-only entries
            if "@" not in cleaned and cleaned:
                people.append(cleaned)
    return people


def _format_event_content(event: dict) -> str:
    """Format an event into a human-readable description for brain storage."""
    title = event.get("title", "(No Title)")
    cal = event.get("calendarName", "Unknown")
    start = _parse_iso(event.get("startDate", ""))
    end = _parse_iso(event.get("endDate", ""))
    location = event.get("location", "")
    attendees = event.get("attendees", [])
    all_day = event.get("allDay", False)

    if all_day:
        time_str = start.strftime("%A, %B %d, %Y") + " (all day)"
    else:
        if start.date() == end.date():
            time_str = start.strftime("%A, %B %d, %Y %I:%M %p") + " – " + end.strftime("%I:%M %p")
        else:
            time_str = start.strftime("%A, %B %d %I:%M %p") + " – " + end.strftime("%A, %B %d %I:%M %p")

    parts = [f"Calendar Event: {title}", f"  Time: {time_str}", f"  Calendar: {cal}"]
    if location:
        parts.append(f"  Location: {location}")
    if attendees:
        parts.append(f"  Attendees: {', '.join(attendees[:20])}")

    return "\n".join(parts)


def _get_existing_event_ids(store: BrainStore) -> set[str]:
    """Fetch all event_ids already stored to avoid duplicates."""
    try:
        result = (
            store.supabase.table("jake_episodic")
            .select("metadata")
            .eq("source", "apple_calendar")
            .execute()
        )
        ids = set()
        for row in result.data or []:
            meta = row.get("metadata", {})
            if isinstance(meta, dict) and "event_id" in meta:
                ids.add(meta["event_id"])
        return ids
    except Exception as exc:
        print(f"  WARNING: Could not fetch existing event IDs: {exc}")
        return set()


def ingest_events(days_back: int = 7, days_forward: int = 30, dry_run: bool = False):
    """Main ingestion logic."""
    print(f"Extracting Apple Calendar events ({days_back} days back, {days_forward} days forward)...")
    events = extract_calendar_events(days_back, days_forward)

    if not events:
        print("No events found. Exiting.")
        return

    print(f"Found {len(events)} events across calendars.\n")

    # Group by calendar for summary
    by_cal = Counter(e.get("calendarName", "?") for e in events)
    for cal, count in sorted(by_cal.items()):
        print(f"  {cal}: {count} events")
    print()

    if dry_run:
        for e in sorted(events, key=lambda x: x.get("startDate", "")):
            title = e.get("title", "(No Title)")
            cal = e.get("calendarName", "?")
            start = e.get("startDate", "?")[:16]
            all_day = " [ALL DAY]" if e.get("allDay") else ""
            attendees = e.get("attendees", [])
            att_str = f" ({len(attendees)} attendees)" if attendees else ""
            eid = _event_id(e)
            print(f"  Would ingest: {start} | {title:40s} | {cal}{all_day}{att_str} | id={eid}")
        print(f"\n[DRY RUN] Would process {len(events)} events. Exiting.")
        return

    store = BrainStore()
    stats = {"episodic_created": 0, "episodic_skipped": 0, "semantic": 0, "entities": 0}

    # Get existing event IDs for dedup
    existing_ids = _get_existing_event_ids(store)
    print(f"Found {len(existing_ids)} existing calendar events in brain.\n")

    # --- Episodic memories for each event ---
    batch = []
    for event in events:
        eid = _event_id(event)
        if eid in existing_ids:
            stats["episodic_skipped"] += 1
            continue

        content = _format_event_content(event)
        start_dt = _parse_iso(event.get("startDate", ""))
        topics = _topics_for_calendar(event.get("calendarName", ""))
        project = _project_for_calendar(event.get("calendarName", ""))
        people = _extract_people(event)
        importance = _importance_for_event(event)

        batch.append({
            "content": content,
            "occurred_at": start_dt,
            "memory_type": "calendar_event",
            "project": project,
            "importance": importance,
            "people": people,
            "topics": topics,
            "session_id": None,
            "source": "apple_calendar",
            "source_type": "calendar",
            "metadata": {
                "event_id": eid,
                "uid": event.get("uid", ""),
                "calendar_name": event.get("calendarName", ""),
                "all_day": event.get("allDay", False),
                "location": event.get("location", ""),
            },
        })

    if batch:
        # Insert in batches of 25 to avoid payload limits
        BATCH_SIZE = 25
        for i in range(0, len(batch), BATCH_SIZE):
            chunk = batch[i : i + BATCH_SIZE]
            try:
                count = store.store_episodic_batch(chunk)
                stats["episodic_created"] += count
                print(f"  Stored batch {i // BATCH_SIZE + 1}: {count} events")
            except Exception as exc:
                print(f"  ERROR storing batch {i // BATCH_SIZE + 1}: {exc}")
                # Fall back to individual inserts
                for mem in chunk:
                    try:
                        store.store_episodic(**mem)
                        stats["episodic_created"] += 1
                    except Exception as exc2:
                        print(f"    Failed: {mem['content'][:60]}... — {exc2}")
    else:
        print("  No new events to store (all deduplicated).")

    print(f"\n  Skipped {stats['episodic_skipped']} duplicate events.")

    # --- Semantic memory: today's + tomorrow's schedule ---
    now = datetime.now(timezone.utc)
    today = now.date()
    tomorrow = today + timedelta(days=1)

    today_events = []
    tomorrow_events = []
    for e in sorted(events, key=lambda x: x.get("startDate", "")):
        start_dt = _parse_iso(e.get("startDate", "")).date()
        if start_dt == today:
            today_events.append(e)
        elif start_dt == tomorrow:
            tomorrow_events.append(e)

    schedule_parts = [f"Schedule summary as of {now.strftime('%A, %B %d, %Y')}:\n"]

    schedule_parts.append(f"TODAY ({today.strftime('%A, %B %d')}):")
    if today_events:
        for e in today_events:
            t = e.get("title", "?")
            s = _parse_iso(e.get("startDate", ""))
            time_str = "All Day" if e.get("allDay") else s.strftime("%I:%M %p")
            cal = e.get("calendarName", "")
            schedule_parts.append(f"  - {time_str}: {t} [{cal}]")
    else:
        schedule_parts.append("  (no events)")

    schedule_parts.append(f"\nTOMORROW ({tomorrow.strftime('%A, %B %d')}):")
    if tomorrow_events:
        for e in tomorrow_events:
            t = e.get("title", "?")
            s = _parse_iso(e.get("startDate", ""))
            time_str = "All Day" if e.get("allDay") else s.strftime("%I:%M %p")
            cal = e.get("calendarName", "")
            schedule_parts.append(f"  - {time_str}: {t} [{cal}]")
    else:
        schedule_parts.append("  (no events)")

    schedule_summary = "\n".join(schedule_parts)

    try:
        store.store_semantic(
            content=schedule_summary,
            category="fact",
            confidence=0.9,
            source_episodes=[],
            project=None,
            topics=["calendar", "schedule", "daily"],
        )
        stats["semantic"] += 1
        print(f"\n  Stored schedule summary as semantic memory.")
    except Exception as exc:
        print(f"\n  Failed to store schedule summary: {exc}")

    # --- Entities for recurring meetings ---
    title_counts = Counter(e.get("title", "") for e in events)
    recurring = {title: count for title, count in title_counts.items() if count >= 2 and title}

    if recurring:
        for title, count in sorted(recurring.items(), key=lambda x: -x[1]):
            try:
                # Check if entity already exists
                existing = (
                    store.supabase.table("jake_entities")
                    .select("id")
                    .eq("name", title)
                    .eq("entity_type", "recurring_event")
                    .execute()
                )
                if existing.data:
                    continue

                embedding = store.embedder.embed_query(f"Recurring calendar event: {title}")
                # Determine which calendars this appears on
                cals = set(
                    e.get("calendarName", "")
                    for e in events
                    if e.get("title") == title
                )
                store.supabase.table("jake_entities").insert({
                    "name": title,
                    "entity_type": "recurring_event",
                    "properties": {
                        "occurrence_count": count,
                        "calendars": list(cals),
                        "source": "apple_calendar",
                    },
                    "importance": 0.5,
                    "embedding": embedding,
                }).execute()
                stats["entities"] += 1
                print(f"  Created recurring entity: {title} ({count} occurrences)")
            except Exception as exc:
                print(f"  Failed to create entity for '{title}': {exc}")

    print(f"\n{'=' * 60}")
    print(f"Calendar Ingestion Complete")
    print(f"  Episodic created:  {stats['episodic_created']}")
    print(f"  Episodic skipped:  {stats['episodic_skipped']} (duplicates)")
    print(f"  Semantic memories: {stats['semantic']}")
    print(f"  Recurring entities:{stats['entities']}")
    print(f"{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(description="Ingest Apple Calendar events into Jake's Brain")
    parser.add_argument("--dry-run", action="store_true", help="Preview without storing")
    parser.add_argument("--days-back", type=int, default=7, help="Days in the past to fetch (default: 7)")
    parser.add_argument("--days-forward", type=int, default=30, help="Days in the future to fetch (default: 30)")
    args = parser.parse_args()
    ingest_events(days_back=args.days_back, days_forward=args.days_forward, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
