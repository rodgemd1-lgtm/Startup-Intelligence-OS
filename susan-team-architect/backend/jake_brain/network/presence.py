"""
PresenceManager — knows which device/interface Mike is currently on.

Presence is stored in Supabase jake_working table (source_type='presence').
Any interface that communicates with Jake updates presence on interaction.
Notifications route to the most recently active interface.

Interfaces (in priority order when tie):
  telegram   — iPhone/iPad, most portable
  mac        — Hammerspoon or Claude Code on desktop
  email      — fallback if no active session
"""

from __future__ import annotations

import os
import json
import logging
from enum import Enum
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from typing import Optional

logger = logging.getLogger(__name__)


class Interface(str, Enum):
    TELEGRAM = "telegram"
    MAC = "mac"
    EMAIL = "email"
    CLAUDE_CODE = "claude_code"
    UNKNOWN = "unknown"


@dataclass
class PresenceState:
    interface: Interface
    last_seen: datetime
    device_hint: Optional[str] = None   # e.g. "iPhone", "MacBook Pro"
    session_id: Optional[str] = None

    def is_active(self, timeout_minutes: int = 30) -> bool:
        """True if last seen within timeout_minutes."""
        age = datetime.now(timezone.utc) - self.last_seen
        return age < timedelta(minutes=timeout_minutes)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["interface"] = self.interface.value
        d["last_seen"] = self.last_seen.isoformat()
        return d


class PresenceManager:
    """
    Tracks active interface and routes notifications accordingly.

    Usage:
        pm = PresenceManager()
        pm.update(Interface.TELEGRAM, device_hint="iPhone")
        active = pm.get_active()
        best = pm.best_interface()
    """

    SOURCE_TYPE = "presence"
    PRESENCE_KEY = "jake_presence_state"

    def __init__(self):
        self._supabase = None
        self._local_cache: Optional[PresenceState] = None

    def _get_supabase(self):
        if self._supabase is None:
            try:
                from supabase import create_client
                url = os.environ.get("SUPABASE_URL")
                key = os.environ.get("SUPABASE_SERVICE_KEY")
                if url and key:
                    self._supabase = create_client(url, key)
            except Exception as e:
                logger.warning(f"Supabase unavailable: {e}")
        return self._supabase

    def update(
        self,
        interface: Interface,
        device_hint: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> PresenceState:
        """Record that Mike is active on this interface right now."""
        state = PresenceState(
            interface=interface,
            last_seen=datetime.now(timezone.utc),
            device_hint=device_hint,
            session_id=session_id,
        )
        self._local_cache = state
        self._persist(state)
        return state

    def get_active(self, timeout_minutes: int = 30) -> Optional[PresenceState]:
        """Return current presence if still active, else None."""
        state = self._load()
        if state and state.is_active(timeout_minutes):
            return state
        return None

    def best_interface(self) -> Interface:
        """
        Return the best interface to send a notification to.

        Priority:
          1. Most recently active interface (if within 30 min)
          2. Telegram (most portable fallback)
        """
        state = self.get_active()
        if state:
            return state.interface
        return Interface.TELEGRAM

    def status_dict(self) -> dict:
        state = self._load()
        if not state:
            return {"status": "no_presence_recorded", "best_interface": Interface.TELEGRAM.value}
        return {
            "status": "active" if state.is_active() else "stale",
            "interface": state.interface.value,
            "last_seen": state.last_seen.isoformat(),
            "device_hint": state.device_hint,
            "active": state.is_active(),
            "best_interface": self.best_interface().value,
        }

    # ── persistence ──────────────────────────────────────────────────────────

    def _persist(self, state: PresenceState) -> None:
        sb = self._get_supabase()
        if not sb:
            return
        try:
            payload = {
                "content": json.dumps(state.to_dict()),
                "source_type": self.SOURCE_TYPE,
                "metadata": {"key": self.PRESENCE_KEY},
                "created_at": state.last_seen.isoformat(),
            }
            # Upsert by key — we only ever want ONE presence record
            sb.table("jake_working").upsert(
                {"id": self.PRESENCE_KEY, **payload},
                on_conflict="id",
            ).execute()
        except Exception as e:
            logger.debug(f"Presence persist failed (non-critical): {e}")

    def _load(self) -> Optional[PresenceState]:
        if self._local_cache:
            return self._local_cache
        sb = self._get_supabase()
        if not sb:
            return None
        try:
            result = (
                sb.table("jake_working")
                .select("content, created_at")
                .eq("source_type", self.SOURCE_TYPE)
                .limit(1)
                .execute()
            )
            if result.data:
                raw = json.loads(result.data[0]["content"])
                state = PresenceState(
                    interface=Interface(raw.get("interface", "unknown")),
                    last_seen=datetime.fromisoformat(raw["last_seen"]),
                    device_hint=raw.get("device_hint"),
                    session_id=raw.get("session_id"),
                )
                self._local_cache = state
                return state
        except Exception as e:
            logger.debug(f"Presence load failed (non-critical): {e}")
        return None
