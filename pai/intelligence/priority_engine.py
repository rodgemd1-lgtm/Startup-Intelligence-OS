"""Priority Engine — V4 Proactive Intelligence (Jordan Voss Test)

Every morning, answers: "What is the ONE move today?" in <30 seconds.

Scoring factors:
  1. Deadline proximity (exponential weight as deadline approaches)
  2. Goal alignment (TELOS/GOALS.md connection)
  3. Blocking dependencies (is this blocking other work?)
  4. Effort/impact ratio (quick wins score higher early in day)
  5. Competitive urgency (SCOUT P0 signals)
  6. Calendar constraints (meetings limit available deep work time)

Output format:
  THE ONE THING TODAY:
  > [Action in imperative form]
  WHY: [One sentence]
  IMPACT: [What changes]
  TIME: [Estimated time]
  BLOCKED BY: [Nothing / specific blocker]

Evolved from jake_brain/priority.py — adds goal alignment, blocking detection,
calendar awareness, and the structured ONE THING output.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Any


class ActionSource(str, Enum):
    GOAL = "goal"
    EMAIL = "email"
    CALENDAR = "calendar"
    SCOUT = "scout"
    PIPELINE = "pipeline"
    MANUAL = "manual"
    DECISION = "decision"
    BLOCKED_ITEM = "blocked_item"


@dataclass
class CandidateAction:
    """A candidate for THE ONE THING."""
    action: str               # Imperative form: "Ship the V4 intent router"
    why: str                  # One sentence reason
    impact: str               # What changes if you do this
    estimated_minutes: int = 60
    source: ActionSource = ActionSource.MANUAL
    goal_id: str | None = None    # Link to TELOS goal if applicable
    blocked_by: str | None = None  # What's blocking this, if anything
    blocks_others: bool = False    # Does this unblock downstream work?
    deadline: datetime | None = None
    people: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Computed
    score: float = 0.0
    score_breakdown: dict[str, float] = field(default_factory=dict)


@dataclass
class OneThing:
    """THE ONE THING output — the Jordan Voss test answer."""
    action: str
    why: str
    impact: str
    estimated_minutes: int
    blocked_by: str
    score: float
    runner_up: str | None = None
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_text(self) -> str:
        """Render as the structured ONE THING format."""
        time_str = f"{self.estimated_minutes} min" if self.estimated_minutes < 120 else f"{self.estimated_minutes // 60}h"
        lines = [
            "THE ONE THING TODAY:",
            f"> {self.action}",
            "",
            f"WHY: {self.why}",
            f"IMPACT: {self.impact}",
            f"TIME: {time_str}",
            f"BLOCKED BY: {self.blocked_by or 'Nothing'}",
        ]
        if self.runner_up:
            lines.append(f"RUNNER-UP: {self.runner_up}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "why": self.why,
            "impact": self.impact,
            "estimated_minutes": self.estimated_minutes,
            "blocked_by": self.blocked_by,
            "score": self.score,
            "runner_up": self.runner_up,
            "generated_at": self.generated_at.isoformat(),
        }


class PriorityEngine:
    """Calculate THE ONE THING from a list of candidate actions."""

    # Scoring weights
    W_DEADLINE = 0.25
    W_GOAL_ALIGNMENT = 0.20
    W_BLOCKING = 0.20
    W_EFFORT_IMPACT = 0.15
    W_COMPETITIVE = 0.10
    W_CALENDAR = 0.10

    LOG_DIR = Path(__file__).parent / "logs"

    def __init__(self, available_deep_work_hours: float = 4.0):
        """
        Args:
            available_deep_work_hours: Hours of unscheduled time today.
                Calculate from calendar — total hours minus meetings.
        """
        self.available_hours = available_deep_work_hours
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)

    def calculate_one_thing(self, candidates: list[CandidateAction]) -> OneThing:
        """Score all candidates and return THE ONE THING."""
        if not candidates:
            return OneThing(
                action="Define your top priority for today",
                why="No candidate actions found — start by reviewing goals and inbox",
                impact="Clarity on what matters most",
                estimated_minutes=15,
                blocked_by="",
                score=0.0,
            )

        scored = [self._score(c) for c in candidates]
        scored.sort(key=lambda c: c.score, reverse=True)

        best = scored[0]
        runner_up = scored[1].action if len(scored) > 1 else None

        result = OneThing(
            action=best.action,
            why=best.why,
            impact=best.impact,
            estimated_minutes=best.estimated_minutes,
            blocked_by=best.blocked_by or "",
            score=best.score,
            runner_up=runner_up,
        )

        self._log(result)
        return result

    def _score(self, candidate: CandidateAction) -> CandidateAction:
        """Score a single candidate action across 6 factors."""
        scores = {}

        # 1. Deadline proximity (exponential as deadline approaches)
        scores["deadline"] = self._deadline_score(candidate)

        # 2. Goal alignment
        scores["goal_alignment"] = self._goal_alignment_score(candidate)

        # 3. Blocking power (does this unblock others?)
        scores["blocking"] = self._blocking_score(candidate)

        # 4. Effort/impact ratio
        scores["effort_impact"] = self._effort_impact_score(candidate)

        # 5. Competitive urgency
        scores["competitive"] = self._competitive_score(candidate)

        # 6. Calendar fit
        scores["calendar_fit"] = self._calendar_fit_score(candidate)

        # Weighted composite
        composite = (
            scores["deadline"] * self.W_DEADLINE +
            scores["goal_alignment"] * self.W_GOAL_ALIGNMENT +
            scores["blocking"] * self.W_BLOCKING +
            scores["effort_impact"] * self.W_EFFORT_IMPACT +
            scores["competitive"] * self.W_COMPETITIVE +
            scores["calendar_fit"] * self.W_CALENDAR
        )

        # Penalty: if blocked, reduce score significantly
        if candidate.blocked_by:
            composite *= 0.3

        candidate.score = round(composite, 4)
        candidate.score_breakdown = {k: round(v, 4) for k, v in scores.items()}
        return candidate

    def _deadline_score(self, c: CandidateAction) -> float:
        """Exponential urgency as deadline approaches."""
        if not c.deadline:
            return 0.3  # No deadline — moderate base

        now = datetime.now(timezone.utc)
        deadline = c.deadline
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)

        hours_left = (deadline - now).total_seconds() / 3600

        if hours_left < 0:
            return 1.0  # Overdue — maximum urgency
        if hours_left < 2:
            return 0.95
        if hours_left < 8:
            return 0.85
        if hours_left < 24:
            return 0.7
        if hours_left < 72:
            return 0.5
        return 0.2

    def _goal_alignment_score(self, c: CandidateAction) -> float:
        """Score based on connection to TELOS goals."""
        if c.goal_id:
            return 0.9  # Explicitly linked to a goal
        if c.source == ActionSource.GOAL:
            return 0.8
        # Keyword heuristics for goal-adjacent work
        goal_keywords = ["ship", "launch", "milestone", "okr", "kpi", "target"]
        if any(kw in c.action.lower() for kw in goal_keywords):
            return 0.6
        return 0.3

    def _blocking_score(self, c: CandidateAction) -> float:
        """High score if this action unblocks downstream work."""
        if c.blocks_others:
            return 0.95  # Unblocking is always high priority
        if c.source == ActionSource.BLOCKED_ITEM:
            return 0.1  # This is itself blocked — low
        return 0.4

    def _effort_impact_score(self, c: CandidateAction) -> float:
        """Quick wins (low effort, high impact) score highest early in day."""
        minutes = c.estimated_minutes

        # Effort score (lower time = higher score)
        if minutes <= 15:
            effort = 1.0
        elif minutes <= 30:
            effort = 0.8
        elif minutes <= 60:
            effort = 0.6
        elif minutes <= 120:
            effort = 0.4
        else:
            effort = 0.2

        # Impact from source type heuristic
        impact_by_source = {
            ActionSource.DECISION: 0.9,
            ActionSource.SCOUT: 0.8,
            ActionSource.GOAL: 0.8,
            ActionSource.EMAIL: 0.5,
            ActionSource.CALENDAR: 0.6,
            ActionSource.PIPELINE: 0.4,
            ActionSource.MANUAL: 0.7,
            ActionSource.BLOCKED_ITEM: 0.3,
        }
        impact = impact_by_source.get(c.source, 0.5)

        return (effort * 0.4 + impact * 0.6)

    def _competitive_score(self, c: CandidateAction) -> float:
        """High score if driven by competitive urgency."""
        if c.source == ActionSource.SCOUT:
            return 0.9
        competitive_keywords = ["competitor", "competitive", "market", "threat", "launch"]
        if any(kw in c.action.lower() for kw in competitive_keywords):
            return 0.7
        return 0.2

    def _calendar_fit_score(self, c: CandidateAction) -> float:
        """Score based on whether this fits in available deep work time."""
        hours_needed = c.estimated_minutes / 60

        if hours_needed <= self.available_hours:
            # Fits in available time — good
            return 0.8
        if hours_needed <= self.available_hours * 1.5:
            # Tight but possible with some stretch
            return 0.5
        # Doesn't fit today
        return 0.2

    def _log(self, result: OneThing):
        """Log THE ONE THING to JSONL."""
        log_file = self.LOG_DIR / "priority-engine.jsonl"
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(result.to_dict()) + "\n")
        except OSError:
            pass
