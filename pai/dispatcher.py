#!/usr/bin/env python3
"""Jake Message Dispatcher — V4 Intelligence Router

The central message handler. Takes any incoming message, classifies intent,
routes to the right V4 module, and returns a structured response.

This is what connects:
  IntentRouter → DecisionSupport / PriorityEngine / BriefFormatter / Susan

Called by OpenClaw via jake-intelligence skill, or by channel adapters.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pai.intelligence.intent_router import IntentRouter, IntentCategory, RoutingDecision


class Dispatcher:
    """Route incoming messages through the V4 intelligence pipeline."""

    def __init__(self):
        self.router = IntentRouter(log_classifications=True)

    def dispatch(self, message: str, channel: str = "telegram") -> str:
        """Classify and route a message, returning a formatted response."""
        decision = self.router.classify(message)

        # Route based on intent
        if decision.intent == IntentCategory.DECISION:
            return self._handle_decision(message, decision)
        elif decision.intent == IntentCategory.STATUS_CHECK:
            return self._handle_status(message, decision)
        elif decision.intent == IntentCategory.RESEARCH:
            return self._handle_research(message, decision)
        elif decision.intent == IntentCategory.STRATEGY:
            return self._handle_strategy(message, decision)
        elif decision.intent == IntentCategory.BUILD:
            return self._handle_build(message, decision)
        elif decision.intent == IntentCategory.QUICK_ANSWER:
            return self._handle_quick(message, decision)
        elif decision.intent == IntentCategory.CASUAL:
            return self._handle_casual(message, decision)
        else:
            return f"Classified as {decision.intent.value} (confidence: {decision.confidence:.0%}). Routing to general handler."

    def _handle_decision(self, message: str, decision: RoutingDecision) -> str:
        """Route to decision support engine."""
        from pai.intelligence.decision_support import DecisionSupport
        engine = DecisionSupport()
        brief = engine.full_analysis(message)
        return brief.to_markdown()

    def _handle_status(self, message: str, decision: RoutingDecision) -> str:
        """Handle status checks — brief, calendar, email, goals."""
        msg_lower = message.lower()

        # "brief" or "morning brief" → full V4 brief
        if "brief" in msg_lower or "morning" in msg_lower:
            from pai.pipelines.morning_briefing import build_v4_briefing
            return build_v4_briefing()

        # "what should I do" → THE ONE THING
        if any(p in msg_lower for p in ["what should i do", "one thing", "priority", "focus"]):
            return self._get_one_thing()

        # "calendar" or "schedule"
        if "calendar" in msg_lower or "schedule" in msg_lower:
            return self._get_calendar_summary()

        # "email" or "inbox"
        if "email" in msg_lower or "inbox" in msg_lower:
            return self._get_email_summary()

        # Generic status → THE ONE THING + quick status
        return self._get_one_thing()

    def _handle_research(self, message: str, decision: RoutingDecision) -> str:
        """Route to research — delegate to Susan bridge."""
        return (
            f"**Research request classified** (confidence: {decision.confidence:.0%})\n"
            f"Agent: {decision.agent or 'research-director'}\n\n"
            f"Routing to Susan research pipeline...\n"
            f"Run: `susan route founder-intelligence-os \"{message}\"`"
        )

    def _handle_strategy(self, message: str, decision: RoutingDecision) -> str:
        """Route to strategy — delegate to Steve via Susan."""
        return (
            f"**Strategy request classified** (confidence: {decision.confidence:.0%})\n"
            f"Agent: {decision.agent or 'steve-strategy'}\n\n"
            f"Routing to Steve Strategy...\n"
            f"Run: `susan route founder-intelligence-os \"{message}\" --agent steve-strategy`"
        )

    def _handle_build(self, message: str, decision: RoutingDecision) -> str:
        """Route to engineering — delegate to Atlas."""
        return (
            f"**Build request classified** (confidence: {decision.confidence:.0%})\n"
            f"Agent: {decision.agent or 'atlas-engineering'}\n\n"
            f"This is a build task. Route to Claude Code or Atlas Engineering.\n"
            f"Run: `susan route founder-intelligence-os \"{message}\" --agent atlas-engineering`"
        )

    def _handle_quick(self, message: str, decision: RoutingDecision) -> str:
        """Quick factual answers — pass through to default LLM."""
        return f"QUICK_ANSWER|{decision.confidence:.2f}|{message}"

    def _handle_casual(self, message: str, decision: RoutingDecision) -> str:
        """Casual conversation — pass through to default LLM."""
        return f"CASUAL|{decision.confidence:.2f}|{message}"

    def _get_one_thing(self) -> str:
        """Calculate and format THE ONE THING."""
        from pai.intelligence.priority_engine import PriorityEngine, CandidateAction, ActionSource

        try:
            from pai.pipelines.morning_briefing import build_briefing
            raw = build_briefing()
            all_emails = raw["email"].get("icloud", []) + raw["email"].get("exchange", [])

            candidates = []
            for e in all_emails:
                if e.get("urgency", 0) >= 4:
                    candidates.append(CandidateAction(
                        action=f"Reply to {e.get('sender', '?')}: {e.get('subject', '?')}",
                        why=f"Urgency {e['urgency']}",
                        impact="Unblock communication",
                        estimated_minutes=15,
                        source=ActionSource.EMAIL,
                        people=[e.get("sender", "")],
                    ))
            for event in raw.get("calendar", []):
                candidates.append(CandidateAction(
                    action=f"Prepare for: {event.get('title', '?')}",
                    why=f"Meeting at {event.get('time', '?')}",
                    impact="Show up prepared",
                    estimated_minutes=20,
                    source=ActionSource.CALENDAR,
                ))
            meeting_count = len(raw.get("calendar", []))
            free_hours = max(0, 10.0 - meeting_count * 0.75)
        except Exception:
            candidates = []
            free_hours = 8.0

        if not candidates:
            candidates.append(CandidateAction(
                action="Review priorities and set today's focus",
                why="No urgent items — perfect for strategic work",
                impact="Clear direction for the day",
                estimated_minutes=30,
                source=ActionSource.GOAL,
            ))

        engine = PriorityEngine(available_deep_work_hours=free_hours)
        result = engine.calculate_one_thing(candidates)
        return result.to_text()

    def _get_calendar_summary(self) -> str:
        """Quick calendar summary."""
        try:
            from pai.pipelines.morning_briefing import build_briefing
            raw = build_briefing()
            events = raw.get("calendar", [])
            if not events:
                return "No events today. Full day for deep work."
            lines = [f"**{len(events)} events today:**"]
            for e in events:
                lines.append(f"  {e.get('time', '?')} [{e.get('calendar', '')}] {e.get('title', '?')}")
            return "\n".join(lines)
        except Exception as ex:
            return f"Calendar unavailable: {ex}"

    def _get_email_summary(self) -> str:
        """Quick email summary."""
        try:
            from pai.pipelines.morning_briefing import build_briefing
            raw = build_briefing()
            summary = raw.get("summary", {})
            return (
                f"**Email: {summary.get('total_unread', '?')} unread**\n"
                f"  VIP: {summary.get('vip_messages', 0)}\n"
                f"  Urgent: {summary.get('urgent_count', 0)}\n"
                f"  Noise: {summary.get('noise_count', 0)}"
            )
        except Exception as ex:
            return f"Email unavailable: {ex}"


def main():
    """CLI entrypoint: jake-dispatch dispatch <message>"""
    if len(sys.argv) < 2:
        print("Usage: python -m pai.dispatcher <message>", file=sys.stderr)
        sys.exit(1)

    message = " ".join(sys.argv[1:])
    dispatcher = Dispatcher()
    result = dispatcher.dispatch(message)
    print(result)


if __name__ == "__main__":
    main()
