"""Event Bus — event queue, state persistence, dedup tracking.

State file: ~/.hermes/state/nervous_state.json
  - seen_events: set of event_id strings (prevents re-alerting)
  - dnd_until: ISO timestamp for DND mode
  - last_email_check: ISO timestamp
  - last_calendar_check: ISO timestamp
  - stats: total events, alerts sent
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

STATE_FILE = Path.home() / ".hermes" / "state" / "nervous_state.json"


class EventType(str, Enum):
    URGENT_EMAIL = "urgent_email"
    MEETING_PREP = "meeting_prep"
    CRON_FAILURE = "cron_failure"
    GITHUB_PR = "github_pr"
    TREND_ALERT = "trend_alert"


@dataclass
class NervousEvent:
    event_id: str           # stable ID for dedup (e.g. "email:msg_id" or "cal:event_id:15min")
    event_type: EventType
    title: str
    body: str
    urgency: float          # 0.0 – 1.0
    source: str             # "email", "calendar", etc.
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_telegram(self) -> str:
        """Format for Telegram message."""
        icon = {
            EventType.URGENT_EMAIL: "📧",
            EventType.MEETING_PREP: "📅",
            EventType.CRON_FAILURE: "🚨",
            EventType.GITHUB_PR: "🔀",
            EventType.TREND_ALERT: "📡",
        }.get(self.event_type, "⚡")
        return f"{icon} *{self.title}*\n{self.body}"


class EventBus:
    """Lightweight event queue + state manager for the nervous system."""

    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = state_file
        self._state: dict[str, Any] = {}
        self._pending: list[NervousEvent] = []
        self._load_state()

    # ── State persistence ──────────────────────────────────────────────────

    def _load_state(self) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    self._state = json.load(f)
            except Exception as exc:
                logger.warning("Could not load nervous state: %s", exc)
                self._state = {}
        # Defaults
        self._state.setdefault("seen_events", [])
        self._state.setdefault("dnd_until", None)
        self._state.setdefault("last_email_check", None)
        self._state.setdefault("last_calendar_check", None)
        self._state.setdefault("stats", {"total_events": 0, "alerts_sent": 0})

    def _save_state(self) -> None:
        try:
            with open(self.state_file, "w") as f:
                json.dump(self._state, f, indent=2, default=str)
        except Exception as exc:
            logger.warning("Could not save nervous state: %s", exc)

    # ── DND ────────────────────────────────────────────────────────────────

    def is_dnd(self) -> bool:
        """Return True if DND mode is active."""
        dnd = self._state.get("dnd_until")
        if not dnd:
            return False
        try:
            dnd_dt = datetime.fromisoformat(dnd)
            return datetime.now(timezone.utc) < dnd_dt
        except Exception:
            return False

    def set_dnd(self, minutes: int) -> str:
        """Enable DND for N minutes."""
        from datetime import timedelta
        until = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        self._state["dnd_until"] = until.isoformat()
        self._save_state()
        return f"DND active until {until.strftime('%I:%M %p')} ({minutes} min)"

    def clear_dnd(self) -> None:
        self._state["dnd_until"] = None
        self._save_state()

    # ── Event dedup ────────────────────────────────────────────────────────

    def is_seen(self, event_id: str) -> bool:
        return event_id in self._state["seen_events"]

    def mark_seen(self, event_id: str) -> None:
        seen = self._state["seen_events"]
        if event_id not in seen:
            seen.append(event_id)
        # Keep last 500 to avoid unbounded growth
        self._state["seen_events"] = seen[-500:]
        self._save_state()

    # ── Event queue ────────────────────────────────────────────────────────

    def emit(self, event: NervousEvent) -> bool:
        """Add event to pending queue if not already seen or pending. Returns True if new."""
        if self.is_seen(event.event_id):
            return False
        # Also dedup within pending queue (same event_id)
        if any(e.event_id == event.event_id for e in self._pending):
            return False
        self._pending.append(event)
        self._state["stats"]["total_events"] += 1
        self._save_state()
        return True

    def drain(self) -> list[NervousEvent]:
        """Return all pending events and clear the queue."""
        events = list(self._pending)
        self._pending.clear()
        return events

    # ── Timestamps ────────────────────────────────────────────────────────

    def update_email_check(self) -> None:
        self._state["last_email_check"] = datetime.now(timezone.utc).isoformat()
        self._save_state()

    def update_calendar_check(self) -> None:
        self._state["last_calendar_check"] = datetime.now(timezone.utc).isoformat()
        self._save_state()

    def increment_alerts_sent(self, n: int = 1) -> None:
        self._state["stats"]["alerts_sent"] += n
        self._save_state()

    # ── Status ────────────────────────────────────────────────────────────

    def status(self) -> dict[str, Any]:
        return {
            "dnd_active": self.is_dnd(),
            "dnd_until": self._state.get("dnd_until"),
            "last_email_check": self._state.get("last_email_check"),
            "last_calendar_check": self._state.get("last_calendar_check"),
            "seen_event_count": len(self._state["seen_events"]),
            "stats": self._state["stats"],
            "pending": len(self._pending),
        }
