"""Discord Channel Adapter — V6 Multi-Channel

Discord bot that responds in DMs and whitelisted channels.

Setup:
  1. Create Discord application + bot
  2. Configure in pai/config/discord.json
  3. Add to OpenClaw channel registry
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, AsyncIterator

from pai.channels.base import (
    ChannelAdapter, ChannelType, IncomingMessage, OutgoingMessage,
)


class DiscordAdapter(ChannelAdapter):
    """Discord channel via bot API."""

    channel_type = ChannelType.DISCORD

    def __init__(self, config_path: Path | None = None):
        self.config = self._load_config(config_path)
        self.token = self.config.get("token", "")
        self.allowed_guilds = self.config.get("allowed_guilds", [])
        self.allowed_channels = self.config.get("allowed_channels", [])
        self.dm_enabled = self.config.get("dm_enabled", True)

    async def send(self, message: OutgoingMessage) -> bool:
        """Send a Discord message."""
        try:
            import discord
        except ImportError:
            return False

        # Discord sending is typically done through the bot's event loop.
        # This is a placeholder — the real handler is in OpenClaw's Discord channel.
        return False

    async def receive(self) -> AsyncIterator[IncomingMessage]:
        """Receive Discord messages.

        Note: In production, this is handled by discord.py's on_message event
        registered with OpenClaw. This is a placeholder.
        """
        return
        yield

    def format_response(self, text: str) -> str:
        """Format for Discord: markdown, casual, emoji-friendly.

        Discord supports standard markdown. Keep messages under 2000 chars.
        """
        result = text

        # Discord supports markdown natively, so minimal conversion needed
        # Just ensure we don't exceed 2000 chars
        if len(result) > 1950:
            result = result[:1947] + "..."

        return result.strip()

    def _load_config(self, config_path: Path | None = None) -> dict:
        path = config_path or Path(__file__).parent.parent.parent / "config" / "discord.json"
        if path.exists():
            try:
                return json.loads(path.read_text())
            except (json.JSONDecodeError, OSError):
                pass
        return {}
