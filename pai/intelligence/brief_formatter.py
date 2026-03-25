"""Brief Formatter — V4 Proactive Intelligence

All briefs follow a consistent Miessler-inspired structure.
Templates: morning, decision, meeting, competitive.

Morning brief template:
  # {date} — Morning Brief
  ## THE ONE THING
  ## Calendar ({count} meetings, {free_hours}h deep work)
  ## Email ({p0_count} urgent, {total_count} unread)
  ## Goals ({active} active, {blocked} blocked)
  ## Signals ({count})
  ## Learning (yesterday)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class BriefData:
    """Input data for brief rendering."""
    # THE ONE THING
    one_thing_action: str = ""
    one_thing_why: str = ""
    one_thing_impact: str = ""
    one_thing_time: str = ""
    one_thing_blocked: str = ""

    # Calendar
    meetings: list[dict] = field(default_factory=list)
    free_hours: float = 0.0

    # Email
    urgent_emails: list[dict] = field(default_factory=list)
    total_unread: int = 0
    vip_count: int = 0

    # Goals
    active_goals: list[dict] = field(default_factory=list)
    blocked_goals: list[dict] = field(default_factory=list)

    # Competitive signals
    signals: list[dict] = field(default_factory=list)

    # Learning / yesterday summary
    learning_summary: str = ""

    # Decision briefs pending
    pending_decisions: list[dict] = field(default_factory=list)

    # Extra sections
    extra_sections: dict[str, str] = field(default_factory=dict)


class BriefFormatter:
    """Render structured briefs from data."""

    def morning_brief(self, data: BriefData) -> str:
        """Render the full morning brief."""
        now = datetime.now(timezone.utc)
        date_str = now.astimezone().strftime("%A, %B %d %Y")
        time_str = now.astimezone().strftime("%I:%M %p")

        sections = []

        # Header
        sections.append(f"# {date_str} — Morning Brief")
        sections.append("")

        # THE ONE THING
        if data.one_thing_action:
            sections.append("## THE ONE THING")
            sections.append(f"> {data.one_thing_action}")
            sections.append("")
            if data.one_thing_why:
                sections.append(f"WHY: {data.one_thing_why}")
            if data.one_thing_impact:
                sections.append(f"IMPACT: {data.one_thing_impact}")
            if data.one_thing_time:
                sections.append(f"TIME: {data.one_thing_time}")
            if data.one_thing_blocked:
                sections.append(f"BLOCKED BY: {data.one_thing_blocked}")
            sections.append("")

        # Calendar
        meeting_count = len(data.meetings)
        sections.append(f"## Calendar ({meeting_count} meetings, {data.free_hours:.1f}h deep work)")
        if data.meetings:
            for m in data.meetings:
                time = m.get("time", "?")
                title = m.get("title", "(no title)")
                cal = m.get("calendar", "")
                loc = m.get("location", "")
                line = f"  {time} [{cal}] {title}"
                if loc:
                    line += f" @ {loc}"
                sections.append(line)
        else:
            sections.append("  No meetings — full deep work day")
        sections.append("")

        # Email
        p0_count = len(data.urgent_emails)
        sections.append(f"## Email ({p0_count} urgent, {data.total_unread} unread)")
        if data.urgent_emails:
            for e in data.urgent_emails[:7]:
                sender = str(e.get("sender", ""))[:35]
                subject = str(e.get("subject", "(no subject)"))[:50]
                urgency = e.get("urgency", 2)
                flag = ""
                if e.get("is_vip"):
                    flag = f" [VIP:{e.get('vip_reason', '')}]"
                sections.append(f"  U{urgency} {sender}: {subject}{flag}")
        else:
            sections.append("  No urgent emails")
        sections.append("")

        # Goals
        active = len(data.active_goals)
        blocked = len(data.blocked_goals)
        sections.append(f"## Goals ({active} active, {blocked} blocked)")
        for g in data.active_goals[:5]:
            name = g.get("name", "?")
            progress = g.get("progress", "?")
            sections.append(f"  [{progress}] {name}")
        for g in data.blocked_goals[:3]:
            name = g.get("name", "?")
            blocker = g.get("blocker", "?")
            sections.append(f"  [BLOCKED] {name} — {blocker}")
        if not data.active_goals and not data.blocked_goals:
            sections.append("  No active goals tracked")
        sections.append("")

        # Competitive signals
        signal_count = len(data.signals)
        sections.append(f"## Signals ({signal_count})")
        if data.signals:
            for s in data.signals[:5]:
                priority = s.get("priority", "P2")
                title = s.get("title", "?")
                competitor = s.get("competitor", "?")
                prefix = "!!!" if priority == "P0" else "!" if priority == "P1" else ""
                sections.append(f"  [{prefix}] {competitor}: {title}")
        else:
            sections.append("  No competitive signals detected")
        sections.append("")

        # Pending decisions
        if data.pending_decisions:
            sections.append(f"## Decisions Pending ({len(data.pending_decisions)})")
            for d in data.pending_decisions[:3]:
                q = d.get("question", "?")[:80]
                sections.append(f"  ? {q}")
            sections.append("")

        # Learning
        if data.learning_summary:
            sections.append("## Learning (yesterday)")
            sections.append(f"  {data.learning_summary}")
            sections.append("")

        # Extra sections
        for title, content in data.extra_sections.items():
            sections.append(f"## {title}")
            sections.append(content)
            sections.append("")

        # Footer
        sections.append("---")
        sections.append(f"*Generated by Jake PAI at {time_str}*")

        return "\n".join(sections)

    def decision_brief(self, decision_markdown: str) -> str:
        """Wrap a DecisionBrief markdown in consistent formatting."""
        return decision_markdown  # Already formatted by DecisionSupport

    def meeting_brief(
        self,
        meeting_title: str,
        attendees: list[str],
        context: str = "",
        prep_notes: list[str] | None = None,
    ) -> str:
        """Render a pre-meeting brief."""
        now = datetime.now(timezone.utc)
        sections = [
            f"# Meeting Brief: {meeting_title}",
            f"*Prepared at {now.astimezone().strftime('%I:%M %p')}*",
            "",
            "## Attendees",
        ]
        for a in attendees:
            sections.append(f"  - {a}")
        sections.append("")

        if context:
            sections.append("## Context")
            sections.append(context)
            sections.append("")

        if prep_notes:
            sections.append("## Prep Notes")
            for note in prep_notes:
                sections.append(f"  - {note}")
            sections.append("")

        sections.append("## Questions to Ask")
        sections.append("  1. ")
        sections.append("")
        sections.append("## Key Outcome")
        sections.append("  > What does success look like for this meeting?")

        return "\n".join(sections)

    def competitive_digest(self, signals: list[dict]) -> str:
        """Render a competitive intelligence digest."""
        if not signals:
            return "No competitive signals to report."

        sections = ["# SCOUT Competitive Digest", ""]

        # Group by company
        by_company: dict[str, list] = {}
        for s in signals:
            co = s.get("company", "unknown")
            by_company.setdefault(co, []).append(s)

        for co, sigs in by_company.items():
            p0_count = sum(1 for s in sigs if s.get("priority") == "P0")
            p1_count = sum(1 for s in sigs if s.get("priority") == "P1")
            sections.append(f"## {co} ({len(sigs)} signals: {p0_count} P0, {p1_count} P1)")
            for s in sorted(sigs, key=lambda x: x.get("priority", "P2")):
                sections.append(
                    f"  [{s.get('priority')}] {s.get('competitor', '?')}: "
                    f"{s.get('title', '?')}"
                )
            sections.append("")

        return "\n".join(sections)
