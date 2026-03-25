"""iMessage Channel Adapter — V6 Multi-Channel

Uses BlueBubbles REST API on Mac Studio for iMessage send/receive.
BlueBubbles provides a REST API over the native Messages.app.

Setup:
  1. brew install --cask bluebubbles
  2. Configure REST API on port 1234
  3. Set API password in pai/config/bluebubbles.json

Only responds to whitelisted contacts (Mike's phone number).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, AsyncIterator

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

from pai.channels.base import (
    ChannelAdapter, ChannelType, IncomingMessage, OutgoingMessage,
)


class IMessageAdapter(ChannelAdapter):
    """iMessage channel via BlueBubbles REST API."""

    channel_type = ChannelType.IMESSAGE

    def __init__(self, config_path: Path | None = None):
        self.config = self._load_config(config_path)
        self.base_url = self.config.get("api_url", "http://localhost:1234")
        self.password = self.config.get("password", "")
        self.allowed_contacts = self.config.get("allowed_contacts", [])

    async def send(self, message: OutgoingMessage) -> bool:
        """Send an iMessage via BlueBubbles API."""
        if not HAS_HTTPX:
            return False

        formatted = self.format_response(message.text)

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/api/v1/message/text",
                    json={
                        "chatGuid": message.channel_id or f"iMessage;-;{message.recipient}",
                        "message": formatted,
                    },
                    params={"password": self.password},
                    timeout=15,
                )
                return resp.status_code == 200
            except httpx.HTTPError:
                return False

    async def receive(self) -> AsyncIterator[IncomingMessage]:
        """Poll BlueBubbles for new messages."""
        if not HAS_HTTPX:
            return

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.base_url}/api/v1/message",
                    params={
                        "password": self.password,
                        "limit": 10,
                        "sort": "DESC",
                        "with": "chat",
                    },
                    timeout=15,
                )
                if resp.status_code != 200:
                    return

                data = resp.json()
                for msg in data.get("data", []):
                    # Only process messages from allowed contacts
                    sender = msg.get("handle", {}).get("address", "")
                    if sender not in self.allowed_contacts:
                        continue
                    # Only process incoming (not sent by us)
                    if msg.get("isFromMe", True):
                        continue

                    yield IncomingMessage(
                        text=msg.get("text", ""),
                        sender=sender,
                        channel=ChannelType.IMESSAGE,
                        channel_id=msg.get("chats", [{}])[0].get("guid", ""),
                        metadata={"message_id": msg.get("guid", "")},
                    )
            except httpx.HTTPError:
                return

    def format_response(self, text: str) -> str:
        """Format for iMessage: plain text, brief, personal."""
        # Strip markdown formatting for iMessage
        result = text
        # Remove headers
        import re
        result = re.sub(r"^#{1,6}\s+", "", result, flags=re.MULTILINE)
        # Remove bold/italic markers
        result = re.sub(r"\*\*(.+?)\*\*", r"\1", result)
        result = re.sub(r"\*(.+?)\*", r"\1", result)
        # Remove code blocks
        result = re.sub(r"```[\s\S]*?```", "", result)
        result = re.sub(r"`(.+?)`", r"\1", result)

        # Truncate for iMessage brevity
        if len(result) > 500:
            result = result[:497] + "..."

        return result.strip()

    def _load_config(self, config_path: Path | None = None) -> dict:
        path = config_path or Path(__file__).parent.parent.parent / "config" / "bluebubbles.json"
        if path.exists():
            try:
                return json.loads(path.read_text())
            except (json.JSONDecodeError, OSError):
                pass
        return {}
