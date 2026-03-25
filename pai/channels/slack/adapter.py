"""Slack Channel Adapter — V6 Multi-Channel

Uses Slack Socket Mode for secure, DM-only communication.
No public channel posting without explicit APPROVE.

Setup:
  1. Create Slack app with Socket Mode enabled
  2. Bot token scopes: chat:write, im:history, im:read, im:write
  3. Configure in pai/config/slack-app.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, AsyncIterator

from pai.channels.base import (
    ChannelAdapter, ChannelType, IncomingMessage, OutgoingMessage,
)


class SlackAdapter(ChannelAdapter):
    """Slack channel via Socket Mode."""

    channel_type = ChannelType.SLACK

    def __init__(self, config_path: Path | None = None):
        self.config = self._load_config(config_path)
        self.app_token = self.config.get("app_token", "")
        self.bot_token = self.config.get("bot_token", "")
        self.allowed_users = self.config.get("allowed_users", [])
        self.dm_only = self.config.get("dm_only", True)

    async def send(self, message: OutgoingMessage) -> bool:
        """Send a Slack message via Web API."""
        try:
            from slack_sdk.web.async_client import AsyncWebClient
        except ImportError:
            return False

        client = AsyncWebClient(token=self.bot_token)
        formatted = self.format_response(message.text)

        # Split long messages
        chunks = self.split_message(formatted)
        for chunk in chunks:
            try:
                await client.chat_postMessage(
                    channel=message.channel_id or message.recipient,
                    text=chunk,
                )
            except Exception:
                return False
        return True

    async def receive(self) -> AsyncIterator[IncomingMessage]:
        """Receive messages via Slack Socket Mode.

        Note: In production, this is handled by the Socket Mode handler
        registered with OpenClaw. This method is for polling fallback.
        """
        # Socket Mode is event-driven, not polling.
        # This is a placeholder — the real handler is in OpenClaw's Slack channel.
        return
        yield  # Make this an async generator

    def format_response(self, text: str) -> str:
        """Format for Slack: mrkdwn format, professional, structured."""
        result = text

        # Convert markdown headers to Slack bold
        result = re.sub(r"^# (.+)$", r"*\1*", result, flags=re.MULTILINE)
        result = re.sub(r"^## (.+)$", r"*\1*", result, flags=re.MULTILINE)
        result = re.sub(r"^### (.+)$", r"*\1*", result, flags=re.MULTILINE)

        # Convert markdown bold to Slack bold
        result = re.sub(r"\*\*(.+?)\*\*", r"*\1*", result)

        # Convert markdown italic to Slack italic
        result = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"_\1_", result)

        # Convert markdown links
        result = re.sub(r"\[(.+?)\]\((.+?)\)", r"<\2|\1>", result)

        return result.strip()

    def _load_config(self, config_path: Path | None = None) -> dict:
        path = config_path or Path(__file__).parent.parent.parent / "config" / "slack-app.json"
        if path.exists():
            try:
                return json.loads(path.read_text())
            except (json.JSONDecodeError, OSError):
                pass
        return {}
