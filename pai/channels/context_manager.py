"""Cross-Channel Context Manager — V6 Multi-Channel

Ensures context persists across all channels via a shared context store.
When Mike starts a conversation in Telegram and continues in Slack,
Jake remembers the full thread.

Design:
  - All channels tag messages with channel source
  - Single shared context store (JSONL on disk, Supabase in production)
  - Cross-channel search works across all channels
  - Context header: "Last interaction was 2 hours ago via Slack about X"
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from pai.channels.base import ChannelType


@dataclass
class ContextEntry:
    """A single context entry from any channel."""
    message: str
    response: str
    channel: ChannelType
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    topic: str = ""  # Auto-detected or user-tagged
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "message": self.message[:500],
            "response": self.response[:500],
            "channel": self.channel.value,
            "timestamp": self.timestamp.isoformat(),
            "topic": self.topic,
        }


class CrossChannelContext:
    """Manage context across all channels."""

    CONTEXT_DIR = Path(__file__).parent.parent / "MEMORY" / "STATE"
    CONTEXT_FILE = CONTEXT_DIR / "cross-channel-context.jsonl"

    def __init__(self, max_context_entries: int = 100):
        self.CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
        self.max_entries = max_context_entries

    def record(
        self,
        message: str,
        response: str,
        channel: ChannelType | str,
        topic: str = "",
    ):
        """Record a message/response pair with channel tag."""
        if isinstance(channel, str):
            channel = ChannelType(channel)

        entry = ContextEntry(
            message=message,
            response=response,
            channel=channel,
            topic=topic or self._detect_topic(message),
        )

        try:
            with open(self.CONTEXT_FILE, "a") as f:
                f.write(json.dumps(entry.to_dict()) + "\n")
        except OSError:
            pass

    def get_context_header(self) -> str:
        """Generate a context header showing the last interaction.

        Example: "Last interaction was 2 hours ago via Slack about Oracle Health pricing."
        """
        last = self.get_last_interaction()
        if not last:
            return "No prior interactions recorded."

        # Calculate time ago
        now = datetime.now(timezone.utc)
        try:
            ts = datetime.fromisoformat(last.get("timestamp", ""))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            delta = now - ts
            time_ago = self._format_timedelta(delta)
        except (ValueError, TypeError):
            time_ago = "recently"

        channel = last.get("channel", "unknown")
        topic = last.get("topic", "")

        if topic:
            return f"Last interaction was {time_ago} via {channel} about {topic}."
        return f"Last interaction was {time_ago} via {channel}."

    def get_last_interaction(self, channel: str | None = None) -> dict | None:
        """Get the most recent interaction, optionally filtered by channel."""
        entries = self._read_recent(count=10)
        if channel:
            entries = [e for e in entries if e.get("channel") == channel]
        return entries[-1] if entries else None

    def search(self, query: str, limit: int = 5) -> list[dict]:
        """Search context across all channels."""
        query_lower = query.lower()
        entries = self._read_recent(count=200)

        matches = []
        for entry in entries:
            text = f"{entry.get('message', '')} {entry.get('response', '')} {entry.get('topic', '')}".lower()
            if query_lower in text:
                matches.append(entry)

        return matches[-limit:]

    def get_channel_summary(self) -> dict[str, int]:
        """Get interaction counts per channel."""
        entries = self._read_recent(count=500)
        counts: dict[str, int] = {}
        for e in entries:
            ch = e.get("channel", "unknown")
            counts[ch] = counts.get(ch, 0) + 1
        return counts

    def _detect_topic(self, message: str) -> str:
        """Simple topic detection from message content."""
        msg = message.lower()

        topics = {
            "oracle health": ["oracle", "health", "clinical", "ehr", "ellen"],
            "alex recruiting": ["recruiting", "coach", "jacob", "highlights", "ncsa"],
            "startup os": ["susan", "jake", "pai", "agent", "capability"],
            "email": ["email", "inbox", "unread", "mail"],
            "calendar": ["meeting", "calendar", "schedule", "event"],
            "goals": ["goal", "milestone", "okr", "target"],
        }

        for topic, keywords in topics.items():
            if any(kw in msg for kw in keywords):
                return topic
        return ""

    def _format_timedelta(self, delta: timedelta) -> str:
        """Format a timedelta as human-readable string."""
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return "just now"
        if seconds < 3600:
            mins = seconds // 60
            return f"{mins} minute{'s' if mins > 1 else ''} ago"
        if seconds < 86400:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        days = seconds // 86400
        return f"{days} day{'s' if days > 1 else ''} ago"

    def _read_recent(self, count: int = 100) -> list[dict]:
        """Read the most recent context entries."""
        if not self.CONTEXT_FILE.exists():
            return []

        entries = []
        try:
            with open(self.CONTEXT_FILE) as f:
                for line in f:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except OSError:
            return []

        return entries[-count:]
