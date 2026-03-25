"""Base Channel Adapter — V6 Multi-Channel

Abstract base for all channel adapters. Each channel implements:
  - send_message(text, recipient)
  - receive_messages() → iterator
  - format_response(text) → channel-native format
  - get_channel_id() → unique channel identifier for LosslessClaw tagging
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, AsyncIterator


class ChannelType(str, Enum):
    TELEGRAM = "telegram"
    IMESSAGE = "imessage"
    SLACK = "slack"
    DISCORD = "discord"
    VOICE = "voice"
    CLAUDE_CODE = "claude_code"


@dataclass
class IncomingMessage:
    """A message received on any channel."""
    text: str
    sender: str
    channel: ChannelType
    channel_id: str  # Unique conversation/thread ID
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)
    # Attachments, reply-to, thread context, etc.
    attachments: list[dict] = field(default_factory=list)
    reply_to: str | None = None  # Message ID this is replying to


@dataclass
class OutgoingMessage:
    """A message to send on any channel."""
    text: str
    channel: ChannelType
    recipient: str = ""
    channel_id: str = ""
    format: str = "markdown"  # "markdown", "plain", "mrkdwn", "spoken"
    metadata: dict[str, Any] = field(default_factory=dict)


class ChannelAdapter(ABC):
    """Abstract base class for channel adapters."""

    channel_type: ChannelType

    @abstractmethod
    async def send(self, message: OutgoingMessage) -> bool:
        """Send a message through this channel. Returns True on success."""
        ...

    @abstractmethod
    async def receive(self) -> AsyncIterator[IncomingMessage]:
        """Receive messages from this channel."""
        ...

    @abstractmethod
    def format_response(self, text: str) -> str:
        """Format a response for this channel's native format."""
        ...

    def get_channel_tag(self) -> str:
        """Tag for LosslessClaw context persistence."""
        return self.channel_type.value

    def max_message_length(self) -> int:
        """Maximum message length for this channel."""
        limits = {
            ChannelType.TELEGRAM: 4096,
            ChannelType.IMESSAGE: 20000,
            ChannelType.SLACK: 40000,
            ChannelType.DISCORD: 2000,
            ChannelType.VOICE: 200,  # Words, not chars — keep spoken responses short
            ChannelType.CLAUDE_CODE: 100000,
        }
        return limits.get(self.channel_type, 4096)

    def split_message(self, text: str) -> list[str]:
        """Split a long message into channel-compatible chunks."""
        max_len = self.max_message_length()
        if len(text) <= max_len:
            return [text]

        chunks = []
        while text:
            if len(text) <= max_len:
                chunks.append(text)
                break
            # Find a good split point (newline or space)
            split_at = text.rfind("\n", 0, max_len)
            if split_at < max_len // 2:
                split_at = text.rfind(" ", 0, max_len)
            if split_at < max_len // 2:
                split_at = max_len
            chunks.append(text[:split_at])
            text = text[split_at:].lstrip()

        return chunks
