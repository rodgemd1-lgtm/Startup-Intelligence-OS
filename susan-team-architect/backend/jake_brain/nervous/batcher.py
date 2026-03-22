"""Notification Batcher — debounce and batch alerts into one Telegram message.

Rules:
  - P0 events (urgency ≥ 0.75) → send immediately, one message per event
  - P1 events (urgency 0.50–0.74) → batch together in one Telegram message
  - Meeting prep events → always send immediately (time-sensitive)
  - DND active → suppress all alerts (except P0 if DND was set manually)
  - Max 3 messages per 5-minute window (anti-spam)

State tracked in EventBus.
"""
from __future__ import annotations

import json
import logging
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .event_bus import EventBus, NervousEvent, EventType

logger = logging.getLogger(__name__)

P0_URGENCY_THRESHOLD = 0.75
BATCH_MIN_URGENCY = 0.50


def _send_telegram(token: str, chat_id: str, text: str) -> bool:
    """Send a Telegram message. Returns True on success."""
    try:
        payload = json.dumps({
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as exc:
        logger.error("Telegram send failed: %s", exc)
        return False


class NotificationBatcher:
    """Dispatch events as Telegram notifications with debounce logic."""

    def __init__(self, bus: EventBus):
        self.bus = bus
        self._token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self._chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
        self._rate_window_file = Path.home() / ".hermes" / "state" / "nervous_rate.json"

    def _can_send(self) -> bool:
        """Check rate limit: max 3 messages per 5 minutes."""
        try:
            now = datetime.now(timezone.utc).timestamp()
            data: dict[str, Any] = {}
            if self._rate_window_file.exists():
                with open(self._rate_window_file) as f:
                    data = json.load(f)

            window_start = data.get("window_start", 0)
            count = data.get("count", 0)

            # Reset window if >5 min has passed
            if now - window_start > 300:
                data = {"window_start": now, "count": 0}
                count = 0

            if count >= 3:
                return False

            data["count"] = count + 1
            self._rate_window_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._rate_window_file, "w") as f:
                json.dump(data, f)
            return True

        except Exception:
            return True  # Fail open

    def dispatch(self, events: list[NervousEvent]) -> int:
        """Send notifications for events. Returns count of messages sent."""
        if not events:
            return 0

        if not self._token or not self._chat_id:
            logger.warning("Telegram not configured — skipping notifications")
            return 0

        sent = 0
        immediate: list[NervousEvent] = []  # P0 + meeting prep
        batched: list[NervousEvent] = []    # P1

        for event in events:
            if event.event_type == EventType.MEETING_PREP:
                immediate.append(event)
            elif event.urgency >= P0_URGENCY_THRESHOLD:
                immediate.append(event)
            elif event.urgency >= BATCH_MIN_URGENCY:
                batched.append(event)
            # Below threshold: skip (daily brief handles P2/P3)

        # Send immediate events one by one
        for event in immediate:
            if self.bus.is_dnd() and event.urgency < P0_URGENCY_THRESHOLD:
                logger.info("DND active — skipping non-P0 event: %s", event.event_id)
                continue
            if not self._can_send():
                logger.warning("Rate limit hit — deferring %s", event.event_id)
                break
            if _send_telegram(self._token, self._chat_id, event.to_telegram()):
                self.bus.mark_seen(event.event_id)
                self.bus.increment_alerts_sent()
                sent += 1
                logger.info("Sent immediate alert: %s", event.title)

        # Batch P1 events into one message
        if batched and not self.bus.is_dnd():
            if self._can_send():
                lines = ["⚡ *Jake Intel Update*\n"]
                for event in batched:
                    lines.append(event.to_telegram())
                    lines.append("")
                batch_msg = "\n".join(lines).strip()
                if _send_telegram(self._token, self._chat_id, batch_msg):
                    for event in batched:
                        self.bus.mark_seen(event.event_id)
                    self.bus.increment_alerts_sent()
                    sent += 1
                    logger.info("Sent batched alert: %d events", len(batched))

        return sent
