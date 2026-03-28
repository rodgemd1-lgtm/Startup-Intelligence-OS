"""Firehose.com SSE consumer — real-time web monitoring by Ahrefs."""
from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field

import aiohttp

from birch.schemas import RawSignal

logger = logging.getLogger("birch.firehose")


@dataclass
class FirehoseConfig:
    api_key: str
    base_url: str = "https://api.firehose.com"

    @property
    def stream_url(self) -> str:
        return f"{self.base_url}/stream"

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "text/event-stream",
        }

    @classmethod
    def from_env(cls) -> FirehoseConfig:
        api_key = os.environ.get("FIREHOSE_API_KEY", "")
        if not api_key:
            raise RuntimeError("FIREHOSE_API_KEY not set in environment")
        return cls(api_key=api_key)


def _parse_sse_event(event_text: str) -> RawSignal | None:
    """Parse an SSE event into a RawSignal. Returns None for control events."""
    data_lines = []
    for line in event_text.strip().split("\n"):
        if line.startswith("data:"):
            data_lines.append(line[5:].strip())

    if not data_lines:
        return None

    try:
        payload = json.loads("".join(data_lines))
    except json.JSONDecodeError:
        logger.warning("Could not parse SSE data: %s", "".join(data_lines)[:200])
        return None

    return RawSignal(
        source="firehose",
        title=payload.get("title", payload.get("headline", "")),
        content=payload.get("content", payload.get("text", payload.get("snippet", ""))),
        url=payload.get("url", payload.get("link", "")),
        published_at=payload.get("published_at", payload.get("date", "")),
        metadata=payload,
    )


async def listen(config: FirehoseConfig, on_signal) -> None:
    """Connect to Firehose SSE stream, yield RawSignal via callback.

    Args:
        config: FirehoseConfig with API key
        on_signal: async callable(RawSignal) invoked for each parsed signal
    """
    logger.info("Connecting to Firehose SSE at %s", config.stream_url)

    async with aiohttp.ClientSession() as session:
        async with session.get(config.stream_url, headers=config.headers) as resp:
            if resp.status != 200:
                body = await resp.text()
                logger.error("Firehose returned %d: %s", resp.status, body[:200])
                return

            logger.info("Connected — streaming signals")
            buffer = ""
            async for chunk in resp.content:
                buffer += chunk.decode("utf-8", errors="replace")
                while "\n\n" in buffer:
                    event_text, buffer = buffer.split("\n\n", 1)
                    raw_signal = _parse_sse_event(event_text)
                    if raw_signal is not None:
                        await on_signal(raw_signal)
