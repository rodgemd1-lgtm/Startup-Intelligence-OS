#!/usr/bin/env python3
"""Ingest Google Calendar events into Jake's Brain as episodic memories.

Reads events from Google Calendar via OAuth and:
1. Creates episodic memories for each event (title, time, location, attendees)
2. Extracts attendee names as people references
3. Stores a semantic memory summarizing the upcoming schedule
4. Deduplicates by event_id in metadata

Usage:
    cd susan-team-architect/backend && source .venv/bin/activate
    python scripts/brain_gcal_ingest.py [--dry-run] [--days-back 7] [--days-forward 30]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from jake_brain.store import BrainStore
from jake_brain.config import brain_config

# Google API imports
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("ERROR: Google API libraries not installed.")
    print("  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

# OAuth token file — vault is canonical, hermes is fallback
_vault_tokens = Path.home() / ".jake-vault" / "google_oauth_tokens.json"
_hermes_tokens = Path.home() / ".hermes" / "google_oauth_tokens.json"
GOOGLE_TOKENS_FILE = _vault_tokens if _vault_tokens.exists() else _hermes_tokens

# Scopes needed for read-only calendar access
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# Calendar-to-topic mapping
CALENDAR_TOPIC_MAP = {
    "primary": "personal",
    "family": "family",
    "kids": "family",
    "jacob": "family",
    "alex": "family",
    "work": "work",
    "oracle": "oracle_health",
}


def get_calendar_service():
    """Build a Google Calendar API service from saved OAuth tokens."""
    if not GOOGLE_TOKENS_FILE.exists():
        print(f"ERROR: Google OAuth tokens not found at {GOOGLE_TOKENS_FILE}")
        print()
        print("To set up Google Calendar OAuth:")
        print("  1. Go to https://console.cloud.google.com/apis/credentials")
        print("  2. Create an OAuth 2.0 Client ID (Desktop app)")
        print("  3. Download the credentials JSON")
        print("  4. Run the OAuth flow to get a refresh token")
        print(f"  5. Save tokens to {GOOGLE_TOKENS_FILE} with format:")
        print('     {"client_id": "...", "client_secret": "...", "refresh_token": "..."}')
        sys.exit(1)

    with open(GOOGLE_TOKENS_FILE) as f:
        tokens = json.load(f)

    creds = Credentials(
        token=None,
        refresh_token=tokens["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=tokens["client_id"],
        client_secret=tokens["client_secret"],
        scopes=tokens.get("scopes", SCOPES),
    )

    service = build("calendar", "v3", credentials=creds)
    return service


def get_calendar_topics(calendar_summary: str, calendar_id: str) -> list[str]:
    """Derive topic tags from calendar name/ID."""
    topics = ["calendar"]
    summary_lower = (calendar_summary or "").lower()
    cal_lower = (calendar_id or "").lower()

    for keyword, topic in CALENDAR_TOPIC_MAP.items():
        if keyword in summary_lower or keyword in cal_lower:
            topics.append(topic)
            break
    else:
        # Default topic if no match
        if calendar_id == "primary":
            topics.append("personal")
        else:
            topics.append("shared")

    return topics


def extract_attendee_names(event: dict) -> list[str]:
    """Extract attendee display names from a calendar event."""
    people = []
    attendees = event.get("attendees", [])
    for att in attendees:
        # Skip the organizer's own entry if self
        if att.get("self", False):
            continue
        name = att.get("displayName", "")
        if not name:
            # Fall back to email prefix
            email = att.get("email", "")
            if email:
                name = email.split("@")[0].replace(".", " ").title()
        if name:
            people.append(name)
    return people


def format_event_content(event: dict, calendar_name: str) -> str:
    """Format a calendar event into a readable content string for brain storage."""
    title = event.get("summary", "(No title)")

    # Parse start/end times
    start = event.get("start", {})
    end = event.get("end", {})
    is_all_day = "date" in start

    if is_all_day:
        start_str = start.get("date", "")
        end_str = end.get("date", "")
        time_str = f"{start_str} (all day)"
        if end_str and end_str != start_str:
            time_str = f"{start_str} to {end_str} (all day)"
    else:
        start_dt = start.get("dateTime", "")
        end_dt = end.get("dateTime", "")
        if start_dt:
            st = datetime.fromisoformat(start_dt)
            time_str = st.strftime("%Y-%m-%d %I:%M %p")
            if end_dt:
                et = datetime.fromisoformat(end_dt)
                if st.date() == et.date():
                    time_str += f" - {et.strftime('%I:%M %p')}"
                else:
                    time_str += f" to {et.strftime('%Y-%m-%d %I:%M %p')}"
        else:
            time_str = "unknown time"

    parts = [f"Calendar event: {title}", f"When: {time_str}"]

    location = event.get("location", "")
    if location:
        parts.append(f"Where: {location}")

    attendees = extract_attendee_names(event)
    if attendees:
        parts.append(f"Attendees: {', '.join(attendees)}")

    description = event.get("description", "")
    if description:
        # Truncate long descriptions
        desc = description[:300].strip()
        if len(description) > 300:
            desc += "..."
        parts.append(f"Notes: {desc}")

    if calendar_name and calendar_name != "primary":
        parts.append(f"Calendar: {calendar_name}")

    return "\n".join(parts)


def get_event_start_dt(event: dict) -> datetime:
    """Parse event start into a datetime object."""
    start = event.get("start", {})
    if "dateTime" in start:
        return datetime.fromisoformat(start["dateTime"])
    elif "date" in start:
        return datetime.fromisoformat(start["date"]).replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def compute_importance(event: dict) -> float:
    """Score event importance for brain storage."""
    start = event.get("start", {})
    is_all_day = "date" in start
    attendees = event.get("attendees", [])
    has_attendees = len([a for a in attendees if not a.get("self", False)]) > 0

    if is_all_day:
        return 0.8  # All-day events (birthdays, holidays, trips)
    elif has_attendees:
        return 0.7  # Meetings with other people
    else:
        return 0.5  # Personal calendar blocks


def ingest_gcal(days_back: int = 7, days_forward: int = 30, dry_run: bool = False):
    """Fetch Google Calendar events and ingest into Jake's Brain."""
    service = get_calendar_service()

    # Time window
    now = datetime.now(timezone.utc)
    time_min = (now - timedelta(days=days_back)).isoformat()
    time_max = (now + timedelta(days=days_forward)).isoformat()

    print(f"Fetching events from {days_back} days ago to {days_forward} days ahead")
    print(f"  Window: {time_min[:10]} → {time_max[:10]}")
    print()

    # Get all calendars
    try:
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get("items", [])
    except HttpError as e:
        print(f"ERROR: Failed to list calendars: {e}")
        sys.exit(1)

    print(f"Found {len(calendars)} calendar(s):")
    for cal in calendars:
        print(f"  - {cal.get('summary', '(unnamed)')} [{cal['id'][:40]}...]")
    print()

    all_events = []

    for cal in calendars:
        cal_id = cal["id"]
        cal_name = cal.get("summary", "")

        try:
            events_result = (
                service.events()
                .list(
                    calendarId=cal_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy="startTime",
                    maxResults=500,
                )
                .execute()
            )
            events = events_result.get("items", [])
            if events:
                print(f"  {cal_name}: {len(events)} events")
            for ev in events:
                ev["_calendar_name"] = cal_name
                ev["_calendar_id"] = cal_id
                all_events.append(ev)
        except HttpError as e:
            print(f"  {cal_name}: ERROR — {e}")
            continue

    print(f"\nTotal events: {len(all_events)}")

    if not all_events:
        print("No events to ingest.")
        return

    if dry_run:
        print("\n[DRY RUN] Events that would be ingested:\n")
        for ev in sorted(all_events, key=get_event_start_dt):
            title = ev.get("summary", "(No title)")
            start_dt = get_event_start_dt(ev)
            attendees = extract_attendee_names(ev)
            importance = compute_importance(ev)
            cal_name = ev["_calendar_name"]
            att_str = f" | with: {', '.join(attendees)}" if attendees else ""
            print(f"  {start_dt.strftime('%Y-%m-%d %H:%M'):16s} | {title:40s} | imp={importance}{att_str} | cal={cal_name}")
        print(f"\n[DRY RUN] Would ingest {len(all_events)} events. Exiting.")
        return

    # --- Live ingestion ---
    store = BrainStore()
    stats = {"created": 0, "skipped_dup": 0, "failed": 0, "semantic": 0}

    # Check existing event_ids for deduplication
    try:
        existing = (
            store.supabase.table("jake_episodic")
            .select("metadata")
            .eq("source", "google_calendar")
            .execute()
        )
        existing_event_ids = set()
        for row in (existing.data or []):
            meta = row.get("metadata", {})
            if isinstance(meta, dict) and "event_id" in meta:
                existing_event_ids.add(meta["event_id"])
        print(f"\nExisting calendar memories: {len(existing_event_ids)}")
    except Exception as exc:
        print(f"Warning: could not check for duplicates: {exc}")
        existing_event_ids = set()

    # Prepare batch
    memories_to_store = []
    for ev in sorted(all_events, key=get_event_start_dt):
        event_id = ev.get("id", "")

        # Deduplication
        if event_id in existing_event_ids:
            stats["skipped_dup"] += 1
            continue

        cal_name = ev["_calendar_name"]
        cal_id = ev["_calendar_id"]
        content = format_event_content(ev, cal_name)
        start_dt = get_event_start_dt(ev)
        attendees = extract_attendee_names(ev)
        importance = compute_importance(ev)
        topics = get_calendar_topics(cal_name, cal_id)

        memories_to_store.append({
            "content": content,
            "occurred_at": start_dt,
            "memory_type": "calendar_event",
            "source": "google_calendar",
            "source_type": "calendar",
            "importance": importance,
            "people": attendees,
            "topics": topics,
            "metadata": {"event_id": event_id, "calendar_id": cal_id},
        })

    # Batch store
    if memories_to_store:
        try:
            stored = store.store_episodic_batch(memories_to_store)
            stats["created"] = stored
            print(f"  Stored {stored} episodic memories")
        except Exception as exc:
            print(f"  Batch store failed, falling back to individual inserts: {exc}")
            for mem in memories_to_store:
                try:
                    store.store_episodic(**mem)
                    stats["created"] += 1
                except Exception as inner_exc:
                    print(f"  Failed: {mem['content'][:60]}... — {inner_exc}")
                    stats["failed"] += 1

    # Store semantic summary of upcoming schedule
    upcoming = [
        ev for ev in sorted(all_events, key=get_event_start_dt)
        if get_event_start_dt(ev) >= now
    ]

    if upcoming:
        try:
            summary_lines = [f"Mike's upcoming schedule ({len(upcoming)} events, next {days_forward} days):\n"]
            for ev in upcoming[:50]:  # Cap at 50 for summary
                title = ev.get("summary", "(No title)")
                start_dt = get_event_start_dt(ev)
                attendees = extract_attendee_names(ev)
                line = f"- {start_dt.strftime('%Y-%m-%d %I:%M %p')}: {title}"
                if attendees:
                    line += f" (with {', '.join(attendees)})"
                summary_lines.append(line)

            if len(upcoming) > 50:
                summary_lines.append(f"... and {len(upcoming) - 50} more events")

            store.store_semantic(
                content="\n".join(summary_lines),
                category="fact",
                confidence=0.9,
                source_episodes=[],
                project=None,
                topics=["calendar", "schedule", "upcoming"],
            )
            stats["semantic"] += 1
            print(f"  Stored upcoming schedule as semantic memory")
        except Exception as exc:
            print(f"  Failed to store schedule summary: {exc}")

    print(f"\n{'=' * 60}")
    print(f"Google Calendar Ingestion Complete")
    print(f"  Events created:    {stats['created']}")
    print(f"  Duplicates skipped:{stats['skipped_dup']}")
    print(f"  Failed:            {stats['failed']}")
    print(f"  Semantic memories: {stats['semantic']}")
    print(f"{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(description="Ingest Google Calendar events into Jake's Brain")
    parser.add_argument("--dry-run", action="store_true", help="Preview events without storing")
    parser.add_argument("--days-back", type=int, default=7, help="Days of past events to ingest (default: 7)")
    parser.add_argument("--days-forward", type=int, default=30, help="Days of future events to ingest (default: 30)")
    args = parser.parse_args()
    ingest_gcal(days_back=args.days_back, days_forward=args.days_forward, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
