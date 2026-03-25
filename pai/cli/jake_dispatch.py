#!/usr/bin/env python3
"""Jake Dispatch CLI — V4 Intelligence Entrypoints

Called by OpenClaw skills or directly from shell.
Each subcommand wraps a V4 intelligence module.

Usage:
  jake-dispatch classify "Should I take this meeting?"
  jake-dispatch decide "Should I take this meeting?"
  jake-dispatch one-thing
  jake-dispatch brief
  jake-dispatch notify --priority P1 --message "Meeting in 30min"
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Add pai to path
PAI_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PAI_ROOT) not in sys.path:
    sys.path.insert(0, str(PAI_ROOT))


def cmd_classify(message: str) -> None:
    """Classify intent and print routing decision as JSON."""
    from pai.intelligence.intent_router import IntentRouter

    router = IntentRouter(log_classifications=True)
    decision = router.classify(message)

    output = {
        "intent": decision.intent.value,
        "confidence": decision.confidence,
        "model_tier": decision.model_tier.value,
        "agent": decision.agent,
        "agents": decision.agents,
        "escalate": decision.escalate,
        "reasoning": decision.reasoning,
        "context_hints": decision.context_hints,
    }
    print(json.dumps(output, indent=2))


def cmd_decide(question: str) -> None:
    """Run decision support on a question and print structured analysis."""
    from pai.intelligence.decision_support import DecisionSupport

    engine = DecisionSupport()
    brief = engine.full_analysis(question)
    print(brief.to_markdown())


def cmd_one_thing() -> None:
    """Calculate THE ONE THING and print it."""
    from pai.intelligence.priority_engine import PriorityEngine, CandidateAction, ActionSource

    # Pull candidates from morning brief data
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
            why="No urgent items detected — perfect time for strategic work",
            impact="Clear direction for the day",
            estimated_minutes=30,
            source=ActionSource.GOAL,
        ))

    engine = PriorityEngine(available_deep_work_hours=free_hours)
    result = engine.calculate_one_thing(candidates)
    print(result.to_text())


def cmd_brief() -> None:
    """Generate V4 morning brief."""
    from pai.pipelines.morning_briefing import build_v4_briefing
    print(build_v4_briefing())


def main():
    if len(sys.argv) < 2:
        print("Usage: jake-dispatch <classify|decide|one-thing|brief> [args]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]
    args = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""

    if command == "classify":
        if not args:
            print("Usage: jake-dispatch classify <message>", file=sys.stderr)
            sys.exit(1)
        cmd_classify(args)
    elif command == "decide":
        if not args:
            print("Usage: jake-dispatch decide <question>", file=sys.stderr)
            sys.exit(1)
        cmd_decide(args)
    elif command in ("one-thing", "onething", "priority"):
        cmd_one_thing()
    elif command == "brief":
        cmd_brief()
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print("Commands: classify, decide, one-thing, brief", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
