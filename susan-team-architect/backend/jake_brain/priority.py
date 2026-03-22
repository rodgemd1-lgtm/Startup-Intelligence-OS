"""Priority Engine — rank signals by urgency × importance × recency decay.

Scoring formula: composite = urgency × importance × recency_factor × source_weight

Priority tiers:
  P0 (≥0.75): Act immediately — interrupt Mike
  P1 (≥0.50): Surface in next brief
  P2 (≥0.25): Include in daily summary
  P3 (<0.25): Background, log only
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class PriorityTier(str, Enum):
    P0 = "P0"  # Interrupt-level
    P1 = "P1"  # Brief-level
    P2 = "P2"  # Summary-level
    P3 = "P3"  # Background


class SourceType(str, Enum):
    EMAIL = "email"
    CALENDAR = "calendar"
    REMINDER = "reminder"
    BRAIN = "brain"
    GITHUB = "github"
    TELEGRAM = "telegram"
    SYSTEM = "system"
    MANUAL = "manual"
    PHONE = "phone"
    TEXT = "text"


# Source-level base importance weights
SOURCE_WEIGHTS: dict[str, float] = {
    SourceType.MANUAL: 1.0,
    SourceType.PHONE: 0.95,
    SourceType.TEXT: 0.90,
    SourceType.CALENDAR: 0.90,
    SourceType.EMAIL: 0.85,
    SourceType.REMINDER: 0.80,
    SourceType.TELEGRAM: 0.75,
    SourceType.BRAIN: 0.70,
    SourceType.GITHUB: 0.60,
    SourceType.SYSTEM: 0.50,
}

# VIP senders/people — always elevated
VIP_PATTERNS: list[str] = [
    "matt cohlmia", "cohlmia",
    "seema verma", "seema",
    "bharat sutariya", "bharat",
    "elizabeth krulish", "krulish",
    "james loehr", "james",
    "jacob", "jen", "alex",
    "oracle health", "oracle",
]

# Urgency signals in content (regex-free, simple substring)
HIGH_URGENCY_KEYWORDS: list[str] = [
    "urgent", "asap", "today", "due today", "overdue", "flight", "deadline",
    "critical", "p0", "immediate", "alert", "failure", "error", "down",
    "birthday today", "meeting in",
]

MEDIUM_URGENCY_KEYWORDS: list[str] = [
    "tomorrow", "this week", "follow up", "follow-up", "reminder",
    "review", "draft", "prepare", "prep", "schedule",
]


@dataclass
class PrioritySignal:
    """A single prioritizable signal — email, event, reminder, memory, etc."""

    content: str
    source_type: str = SourceType.MANUAL
    urgency: float = 0.5       # 0.0–1.0, caller can override
    importance: float = 0.5   # 0.0–1.0, caller can override
    event_time: datetime | None = None   # when does this thing happen?
    created_at: datetime | None = None   # when was the signal created?
    people: list[str] = field(default_factory=list)
    project: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    # Computed after scoring
    composite_score: float = 0.0
    tier: str = PriorityTier.P3
    score_breakdown: dict[str, float] = field(default_factory=dict)


class PriorityEngine:
    """Rank and triage a list of PrioritySignals."""

    HALF_LIFE_HOURS: float = 48.0  # signals decay to 50% after 2 days

    def score(self, signal: PrioritySignal) -> PrioritySignal:
        """Compute composite priority score. Mutates and returns the signal."""
        urgency = self._resolve_urgency(signal)
        importance = self._resolve_importance(signal)
        recency = self._recency_factor(signal)
        src_weight = SOURCE_WEIGHTS.get(signal.source_type, 0.7)

        composite = urgency * importance * recency * src_weight

        # VIP boost — multiply by 1.3 if any VIP appears in content or people
        if self._is_vip(signal):
            composite = min(1.0, composite * 1.3)

        # Event imminence boost — meeting in < 2 hours → big boost
        imminence = self._imminence_factor(signal)
        composite = min(1.0, composite * imminence)

        signal.composite_score = round(composite, 4)
        signal.urgency = round(urgency, 4)
        signal.importance = round(importance, 4)
        signal.tier = self._assign_tier(composite)
        signal.score_breakdown = {
            "urgency": urgency,
            "importance": importance,
            "recency": recency,
            "source_weight": src_weight,
            "vip": self._is_vip(signal),
            "imminence": imminence,
            "composite": composite,
        }
        return signal

    def rank(self, signals: list[PrioritySignal]) -> list[PrioritySignal]:
        """Score and sort signals highest→lowest."""
        scored = [self.score(s) for s in signals]
        return sorted(scored, key=lambda s: s.composite_score, reverse=True)

    def triage(self, signals: list[PrioritySignal]) -> dict[str, list[PrioritySignal]]:
        """Group signals into P0/P1/P2/P3 tiers after scoring."""
        ranked = self.rank(signals)
        buckets: dict[str, list[PrioritySignal]] = {
            PriorityTier.P0: [],
            PriorityTier.P1: [],
            PriorityTier.P2: [],
            PriorityTier.P3: [],
        }
        for s in ranked:
            buckets[s.tier].append(s)
        return buckets

    def top_n(self, signals: list[PrioritySignal], n: int = 5) -> list[PrioritySignal]:
        """Return the top N highest-priority signals."""
        return self.rank(signals)[:n]

    def format_triage(self, signals: list[PrioritySignal]) -> str:
        """Return a formatted triage summary string."""
        triage = self.triage(signals)
        lines = []
        emoji = {
            PriorityTier.P0: "🔴",
            PriorityTier.P1: "🟡",
            PriorityTier.P2: "🟢",
            PriorityTier.P3: "⚪",
        }
        for tier in [PriorityTier.P0, PriorityTier.P1, PriorityTier.P2, PriorityTier.P3]:
            items = triage[tier]
            if not items:
                continue
            lines.append(f"\n{emoji[tier]} {tier} ({len(items)} signals)")
            for item in items[:5]:  # cap at 5 per tier in display
                lines.append(f"  [{item.source_type}] {item.content[:120]} (score={item.composite_score:.3f})")
        return "\n".join(lines) if lines else "No signals to triage."

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _resolve_urgency(self, signal: PrioritySignal) -> float:
        """Auto-detect urgency from content if not explicitly set high/low."""
        base = signal.urgency  # caller's hint

        content_lower = signal.content.lower()
        for kw in HIGH_URGENCY_KEYWORDS:
            if kw in content_lower:
                base = max(base, 0.85)
                break

        for kw in MEDIUM_URGENCY_KEYWORDS:
            if kw in content_lower:
                base = max(base, 0.55)
                break

        return min(1.0, base)

    def _resolve_importance(self, signal: PrioritySignal) -> float:
        """Importance can be caller-set; VIPs boost it."""
        return min(1.0, signal.importance)

    def _recency_factor(self, signal: PrioritySignal) -> float:
        """Exponential decay from creation time. Defaults to 1.0 if no timestamp."""
        if not signal.created_at:
            return 1.0
        now = datetime.now(timezone.utc)
        created = signal.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        hours_ago = (now - created).total_seconds() / 3600
        # half-life decay: factor = 0.5^(hours/half_life)
        return 0.5 ** (hours_ago / self.HALF_LIFE_HOURS)

    def _imminence_factor(self, signal: PrioritySignal) -> float:
        """Boost signals whose event_time is soon."""
        if not signal.event_time:
            return 1.0
        now = datetime.now(timezone.utc)
        event = signal.event_time
        if event.tzinfo is None:
            event = event.replace(tzinfo=timezone.utc)
        hours_until = (event - now).total_seconds() / 3600
        if hours_until < 0:
            return 0.9  # already past, slightly deprioritize
        if hours_until < 1:
            return 1.8  # < 1 hour: major boost
        if hours_until < 2:
            return 1.4  # < 2 hours: prep time
        if hours_until < 24:
            return 1.1  # today: mild boost
        return 1.0

    def _is_vip(self, signal: PrioritySignal) -> bool:
        content_lower = signal.content.lower()
        people_lower = [p.lower() for p in signal.people]
        all_text = content_lower + " " + " ".join(people_lower)
        return any(vip in all_text for vip in VIP_PATTERNS)

    def _assign_tier(self, score: float) -> str:
        if score >= 0.75:
            return PriorityTier.P0
        if score >= 0.50:
            return PriorityTier.P1
        if score >= 0.25:
            return PriorityTier.P2
        return PriorityTier.P3


# Convenience factory functions for common signal types

def email_signal(
    subject: str,
    sender: str,
    body_preview: str = "",
    received_at: datetime | None = None,
) -> PrioritySignal:
    content = f"EMAIL from {sender}: {subject}"
    if body_preview:
        content += f"\n{body_preview[:200]}"
    return PrioritySignal(
        content=content,
        source_type=SourceType.EMAIL,
        urgency=0.5,
        importance=0.6,
        created_at=received_at,
        people=[sender],
    )


def calendar_signal(
    title: str,
    start_time: datetime,
    location: str = "",
    calendar_name: str = "",
) -> PrioritySignal:
    content = f"EVENT: {title}"
    if location:
        content += f" @ {location}"
    if calendar_name:
        content += f" [{calendar_name}]"
    return PrioritySignal(
        content=content,
        source_type=SourceType.CALENDAR,
        urgency=0.6,
        importance=0.7,
        event_time=start_time,
        created_at=datetime.now(timezone.utc),
    )


def reminder_signal(
    text: str,
    due_date: datetime | None = None,
    list_name: str = "",
) -> PrioritySignal:
    content = f"REMINDER: {text}"
    if list_name:
        content += f" [{list_name}]"
    now = datetime.now(timezone.utc)
    urgency = 0.5
    if due_date:
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)
        if due_date < now:
            urgency = 0.95  # overdue
        elif (due_date - now).total_seconds() < 86400:
            urgency = 0.80  # due today
    return PrioritySignal(
        content=content,
        source_type=SourceType.REMINDER,
        urgency=urgency,
        importance=0.65,
        event_time=due_date,
        created_at=now,
    )


def brain_signal(
    content: str,
    layer: str = "semantic",
    composite_score: float = 0.5,
) -> PrioritySignal:
    return PrioritySignal(
        content=content,
        source_type=SourceType.BRAIN,
        urgency=0.4,
        importance=composite_score,
        created_at=datetime.now(timezone.utc),
        metadata={"layer": layer},
    )
