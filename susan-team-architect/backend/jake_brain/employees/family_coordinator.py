"""Family Coordinator — weekly family event and coordination summary.

Runs every Sunday at 7 AM. Reads upcoming Apple Calendar events via osascript,
loads family entities from the brain, and generates a family coordination summary.

HARDCODED RULE: Apple Calendar ONLY via osascript — never Google Calendar API or MS Graph.
"""
from __future__ import annotations

import logging
import subprocess
from datetime import datetime, timezone
from typing import Any

from jake_brain.autonomous_pipeline import AutonomousPipeline, PipelineTask

logger = logging.getLogger(__name__)

# How many days ahead to scan for events
LOOKAHEAD_DAYS = 14

# Known family members — seed for entity lookup
FAMILY_MEMBERS = ["jacob", "alex", "james", "jen", "mike"]

# Calendar names that are family-relevant (Apple Calendar account names)
FAMILY_CALENDAR_KEYWORDS = ["home", "family", "personal", "kids", "jacob", "alex", "james"]


def get_upcoming_family_events(days: int = LOOKAHEAD_DAYS) -> list[dict]:
    """Load upcoming calendar events via Apple Calendar osascript.

    Returns a list of event dicts with keys: summary, start_date, calendar.
    Falls back to empty list on any error.

    HARDCODED: Uses osascript only. Never Google Calendar API. Never MS Graph.
    """
    script = f'''
    tell application "Calendar"
        set today to current date
        set future_date to today + {days} * days
        set output to ""
        repeat with cal in calendars
            try
                set evts to (every event of cal whose start date >= today and start date < future_date)
                repeat with e in evts
                    try
                        set output to output & (summary of e) & "|" & (start date of e as string) & "|" & (name of cal) & linefeed
                    end try
                end repeat
            end try
        end repeat
        return output
    end tell
    '''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            logger.warning("FamilyCoordinator: osascript error: %s", result.stderr.strip()[:200])
            return []

        raw_output = result.stdout.strip()
        if not raw_output:
            return []

        events = []
        for line in raw_output.split("\n"):
            line = line.strip()
            if not line:
                continue
            parts = line.split("|")
            if len(parts) >= 3:
                events.append({
                    "summary": parts[0].strip(),
                    "start_date": parts[1].strip(),
                    "calendar": parts[2].strip(),
                })
            elif len(parts) == 2:
                events.append({
                    "summary": parts[0].strip(),
                    "start_date": parts[1].strip(),
                    "calendar": "unknown",
                })

        return events

    except subprocess.TimeoutExpired:
        logger.warning("FamilyCoordinator: osascript timed out after 30s")
        return []
    except FileNotFoundError:
        logger.warning("FamilyCoordinator: osascript not available (not on macOS?)")
        return []
    except Exception as exc:
        logger.warning("FamilyCoordinator: calendar read failed: %s", exc)
        return []


def _is_family_event(event: dict) -> bool:
    """Check if a calendar event is family-relevant."""
    summary_lower = event.get("summary", "").lower()
    calendar_lower = event.get("calendar", "").lower()

    # Check calendar name
    if any(kw in calendar_lower for kw in FAMILY_CALENDAR_KEYWORDS):
        return True

    # Check event title for family member names
    if any(name in summary_lower for name in FAMILY_MEMBERS):
        return True

    return False


class FamilyCoordinator:
    """Sunday morning family coordination and weekly planning employee.

    Uses Apple Calendar (osascript only) to gather upcoming family events,
    enriches with brain entity data, and produces a coordination summary.
    """

    EMPLOYEE_NAME = "family_coordinator"
    TASK_TYPE = "family_coordination"
    CONTEXT_HINTS = ["family", "jacob", "alex", "james", "events", "birthdays"]
    SUCCESS_CRITERIA = [
        "upcoming_events list produced",
        "people_mentioned list produced",
        "summary produced",
    ]

    def __init__(self, store=None):
        """
        Args:
            store: BrainStore instance. If None, pipeline runs without memory persistence.
        """
        self._store = store
        self._pipeline = AutonomousPipeline(store=store)

    def run(self) -> dict[str, Any]:
        """Run the Family Coordinator employee.

        Returns:
            dict with upcoming_events, people_mentioned, summary.
        """
        task = PipelineTask(
            task_type=self.TASK_TYPE,
            description=(
                f"Scan Apple Calendar for next {LOOKAHEAD_DAYS} days of family events. "
                "Load family entities from brain. Produce weekly coordination summary."
            ),
            success_criteria=self.SUCCESS_CRITERIA,
            context_hints=self.CONTEXT_HINTS,
            employee_name=self.EMPLOYEE_NAME,
        )

        result = self._pipeline.run(task, build_fn=self._build)
        return result.outputs

    def _build(self, task: PipelineTask, context_data: dict) -> dict[str, Any]:
        """BUILD phase: read calendar, load entities, generate family summary."""
        now = datetime.now(timezone.utc)

        # ── Read Apple Calendar events ────────────────────────────────────
        all_events = get_upcoming_family_events(days=LOOKAHEAD_DAYS)
        family_events = [e for e in all_events if _is_family_event(e)]
        other_events = [e for e in all_events if not _is_family_event(e)]

        logger.info(
            "FamilyCoordinator: found %d total events (%d family, %d other)",
            len(all_events), len(family_events), len(other_events)
        )

        # ── Load family entities from brain ───────────────────────────────
        family_entities: list[dict] = []
        if self._store is not None:
            try:
                result = (
                    self._store.supabase.table("jake_entities")
                    .select("id, name, entity_type, properties, importance")
                    .eq("entity_type", "person")
                    .eq("is_active", True)
                    .order("importance", desc=True)
                    .limit(20)
                    .execute()
                )
                all_entities = result.data or []
                # Filter to family members
                family_entities = [
                    e for e in all_entities
                    if any(name in (e.get("name") or "").lower() for name in FAMILY_MEMBERS)
                ]
            except Exception as exc:
                logger.warning("FamilyCoordinator: failed to load family entities: %s", exc)

        # ── Check for upcoming birthdays (from entity properties) ─────────
        upcoming_birthdays: list[str] = []
        for entity in family_entities:
            props = entity.get("properties") or {}
            birthday = props.get("birthday") or props.get("birth_date") or ""
            if birthday:
                upcoming_birthdays.append(f"{entity.get('name', '?')} — {birthday}")

        # ── Extract people mentioned in calendar events ────────────────────
        people_mentioned: list[str] = []
        for event in family_events:
            summary = event.get("summary", "").lower()
            for name in FAMILY_MEMBERS:
                if name in summary and name not in people_mentioned:
                    people_mentioned.append(name)

        # Also add all known family entities
        for entity in family_entities:
            name = entity.get("name", "").lower()
            if name and name not in people_mentioned:
                people_mentioned.append(name)

        # ── Build coordination summary ─────────────────────────────────────
        week_str = now.strftime("%Y-%m-%d")
        lines = [
            f"# Family Coordination — Week of {week_str}",
            f"*Generated by {self.EMPLOYEE_NAME} | {now.strftime('%A, %B %d %Y')}*",
            "",
        ]

        # Upcoming family events
        lines.append(f"## Upcoming Events (next {LOOKAHEAD_DAYS} days)")
        if family_events:
            for event in family_events[:15]:
                lines.append(f"- **{event['summary']}** — {event['start_date']} [{event['calendar']}]")
        else:
            lines.append("- No family events found in Apple Calendar.")
            if all_events:
                lines.append(f"  (Note: {len(all_events)} non-family events exist on calendar)")
        lines.append("")

        # Birthdays
        if upcoming_birthdays:
            lines.append("## Upcoming Birthdays (from brain)")
            for bd in upcoming_birthdays:
                lines.append(f"- {bd}")
            lines.append("")

        # Family members tracked
        if family_entities:
            lines.append("## Family Members Tracked")
            for entity in family_entities:
                props = entity.get("properties") or {}
                role = props.get("role") or props.get("relationship") or entity.get("entity_type", "person")
                lines.append(f"- **{entity.get('name', '?')}** ({role})")
            lines.append("")

        # All events preview
        if other_events:
            lines.append(f"## Other Calendar Events ({len(other_events)} total)")
            for event in other_events[:5]:
                lines.append(f"- {event['summary']} — {event['start_date']}")
            if len(other_events) > 5:
                lines.append(f"  *(+{len(other_events) - 5} more)*")
            lines.append("")

        summary = "\n".join(lines)

        # ── Store family summary to episodic ──────────────────────────────
        if self._store is not None:
            try:
                self._store.store_episodic(
                    content=summary,
                    occurred_at=now,
                    memory_type="family_summary",
                    project="startup-os",
                    importance=0.75,
                    people=people_mentioned,
                    topics=["family", "events", "coordination"] + people_mentioned[:3],
                    source=self.EMPLOYEE_NAME,
                    source_type="autonomous_employee",
                    metadata={
                        "calendar_events_found": len(all_events),
                        "family_events_found": len(family_events),
                        "people_mentioned": people_mentioned,
                        "upcoming_birthdays": upcoming_birthdays,
                        "lookahead_days": LOOKAHEAD_DAYS,
                    },
                )
            except Exception as exc:
                logger.warning("FamilyCoordinator: failed to store family summary: %s", exc)

        return {
            "upcoming_events": family_events,
            "all_events_count": len(all_events),
            "people_mentioned": people_mentioned,
            "upcoming_birthdays": upcoming_birthdays,
            "family_entities_tracked": len(family_entities),
            "summary": summary,
            "generated_at": now.isoformat(),
        }
