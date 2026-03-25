"""Rating Capture System — V5 Learning Engine

Captures satisfaction signals from Mike — both explicit and implicit.

Explicit signals:
  "good", "great", "perfect", "that's fire" → auto-rate 4-5
  "no", "wrong", "try again", "mid" → auto-rate 1-2
  Explicit 1-5 rating at session end

Implicit signals:
  Re-asking same question → previous answer unsatisfactory (rate 2)
  Mike corrects output → capture correction pair
  Long silence → possible dissatisfaction (flag)
  "skip" / topic change → response wasn't useful (rate 2)
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class SatisfactionSignal:
    """A single satisfaction signal from Mike."""
    rating: int  # 1-5
    signal_type: str  # "explicit", "implicit_positive", "implicit_negative", "correction"
    trigger: str  # What triggered the signal
    context: str = ""  # Recent conversation context
    jake_response: str = ""  # What Jake said
    mike_message: str = ""  # What Mike said
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "rating": self.rating,
            "signal_type": self.signal_type,
            "trigger": self.trigger,
            "context": self.context[:200],
            "jake_response": self.jake_response[:200],
            "mike_message": self.mike_message[:200],
            "timestamp": self.timestamp.isoformat(),
        }


# Pattern matching for explicit satisfaction signals
POSITIVE_PATTERNS = [
    (5, [r"\bperfect\b", r"\bexactly\b", r"\bthat'?s fire\b", r"\bnailed it\b", r"\bspot on\b"]),
    (4, [r"\bgood\b", r"\bgreat\b", r"\bnice\b", r"\bthanks\b", r"\byes\b", r"\byep\b", r"\bcorrect\b"]),
]

NEGATIVE_PATTERNS = [
    (1, [r"\bwrong\b", r"\bterrible\b", r"\bawful\b", r"\buseless\b", r"\bgarbage\b"]),
    (2, [r"\bno\b", r"\bnope\b", r"\btry again\b", r"\bmid\b", r"\bnot (what|that)\b", r"\bskip\b"]),
]

COMPILED_POSITIVE = [(score, [re.compile(p, re.I) for p in pats]) for score, pats in POSITIVE_PATTERNS]
COMPILED_NEGATIVE = [(score, [re.compile(p, re.I) for p in pats]) for score, pats in NEGATIVE_PATTERNS]


class RatingSystem:
    """Capture and analyze satisfaction signals."""

    LOG_DIR = Path(__file__).parent.parent / "MEMORY" / "STATE"

    def __init__(self):
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self._session_signals: list[SatisfactionSignal] = []
        self._recent_messages: list[str] = []  # Rolling window for re-ask detection

    def capture_explicit(self, mike_message: str, jake_response: str = "") -> SatisfactionSignal | None:
        """Detect explicit satisfaction/dissatisfaction from Mike's message."""
        msg = mike_message.strip()

        # Check positive patterns
        for score, patterns in COMPILED_POSITIVE:
            for pat in patterns:
                if pat.search(msg):
                    signal = SatisfactionSignal(
                        rating=score,
                        signal_type="explicit",
                        trigger=f"pattern:{pat.pattern}",
                        jake_response=jake_response,
                        mike_message=msg,
                    )
                    self._record(signal)
                    return signal

        # Check negative patterns
        for score, patterns in COMPILED_NEGATIVE:
            for pat in patterns:
                if pat.search(msg):
                    signal = SatisfactionSignal(
                        rating=score,
                        signal_type="explicit",
                        trigger=f"pattern:{pat.pattern}",
                        jake_response=jake_response,
                        mike_message=msg,
                    )
                    self._record(signal)
                    return signal

        return None

    def capture_implicit_reask(self, mike_message: str, jake_response: str = "") -> SatisfactionSignal | None:
        """Detect when Mike re-asks a similar question (previous answer unsatisfactory)."""
        msg_lower = mike_message.lower().strip()

        # Simple overlap check: if >50% of words match a recent message, it's a re-ask
        msg_words = set(msg_lower.split())
        for prev in self._recent_messages[-5:]:
            prev_words = set(prev.lower().split())
            if len(msg_words) < 3:
                continue
            overlap = len(msg_words & prev_words) / len(msg_words)
            if overlap > 0.5:
                signal = SatisfactionSignal(
                    rating=2,
                    signal_type="implicit_negative",
                    trigger="re-ask",
                    context=f"Re-asked: '{msg_lower[:80]}' (similar to previous)",
                    jake_response=jake_response,
                    mike_message=mike_message,
                )
                self._record(signal)
                self._recent_messages.append(msg_lower)
                return signal

        self._recent_messages.append(msg_lower)
        return None

    def capture_topic_change(self, mike_message: str, jake_response: str = "") -> SatisfactionSignal | None:
        """Detect abrupt topic change (skip signal)."""
        skip_signals = ["skip", "anyway", "never mind", "nevermind", "forget it", "moving on"]
        msg_lower = mike_message.lower().strip()
        if any(s in msg_lower for s in skip_signals):
            signal = SatisfactionSignal(
                rating=2,
                signal_type="implicit_negative",
                trigger="topic_change",
                jake_response=jake_response,
                mike_message=mike_message,
            )
            self._record(signal)
            return signal
        return None

    def process_message(self, mike_message: str, jake_response: str = "") -> SatisfactionSignal | None:
        """Run all signal detection on a message. Returns the strongest signal found."""
        # Priority order: explicit > re-ask > topic change
        signal = self.capture_explicit(mike_message, jake_response)
        if signal:
            return signal

        signal = self.capture_implicit_reask(mike_message, jake_response)
        if signal:
            return signal

        signal = self.capture_topic_change(mike_message, jake_response)
        if signal:
            return signal

        return None

    def analyze_session(self) -> dict:
        """Analyze satisfaction signals from the current session."""
        if not self._session_signals:
            return {"count": 0, "average": 0, "trend": "no_data"}

        ratings = [s.rating for s in self._session_signals]
        avg = sum(ratings) / len(ratings)

        # Trend: compare first half vs second half
        mid = len(ratings) // 2
        if mid > 0:
            first_half = sum(ratings[:mid]) / mid
            second_half = sum(ratings[mid:]) / (len(ratings) - mid)
            if second_half > first_half + 0.3:
                trend = "improving"
            elif second_half < first_half - 0.3:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "count": len(ratings),
            "average": round(avg, 2),
            "trend": trend,
            "positive": sum(1 for r in ratings if r >= 4),
            "negative": sum(1 for r in ratings if r <= 2),
            "neutral": sum(1 for r in ratings if r == 3),
        }

    def weekly_stats(self) -> dict:
        """Read ratings log and compute weekly statistics."""
        log_file = self.LOG_DIR / "ratings.jsonl"
        if not log_file.exists():
            return {"count": 0, "average": 0, "trend": "no_data"}

        cutoff = datetime.now(timezone.utc).timestamp() - (7 * 86400)
        ratings = []
        with open(log_file) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    ts = datetime.fromisoformat(entry["timestamp"])
                    if ts.timestamp() > cutoff:
                        ratings.append(entry["rating"])
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue

        if not ratings:
            return {"count": 0, "average": 0, "trend": "no_data"}

        return {
            "count": len(ratings),
            "average": round(sum(ratings) / len(ratings), 2),
            "positive": sum(1 for r in ratings if r >= 4),
            "negative": sum(1 for r in ratings if r <= 2),
        }

    def _record(self, signal: SatisfactionSignal):
        """Record a signal to session and persistent log."""
        self._session_signals.append(signal)

        log_file = self.LOG_DIR / "ratings.jsonl"
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(signal.to_dict()) + "\n")
        except OSError:
            pass
