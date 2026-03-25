"""Smart Notification System — V4 Proactive Intelligence

Urgency scoring with DND awareness. Not every alert deserves a ping.

Priority tiers:
  P0 (interrupt)  → Family emergency, service outage, deadline <2h → Always deliver
  P1 (soon)       → Important email, meeting in 30 min → Deliver unless DND
  P2 (batch)      → Status update, research complete → Batch to next brief
  P3 (archive)    → Newsletter, notification → Don't notify, log only

DND rules:
  - Quiet hours (22:00-06:00 default)
  - P0 always breaks through
  - Weekend mode (relaxed — P1 batched too)
  - Family time windows (17:00-20:00 — only P0)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, time, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class UrgencyTier(str, Enum):
    P0 = "P0"  # Interrupt — always deliver
    P1 = "P1"  # Soon — deliver unless DND
    P2 = "P2"  # Batch — include in next brief
    P3 = "P3"  # Archive — log only


class DeliveryChannel(str, Enum):
    TELEGRAM = "telegram"
    IMESSAGE = "imessage"
    MORNING_BRIEF = "morning_brief"
    EVENING_BRIEF = "evening_brief"
    LOG_ONLY = "log_only"


@dataclass
class Notification:
    """A single notification to be triaged and delivered."""
    content: str
    source: str  # "email", "calendar", "scout", "pipeline", etc.
    urgency: UrgencyTier = UrgencyTier.P2
    people: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Set after triage
    delivery_channels: list[DeliveryChannel] = field(default_factory=list)
    batched: bool = False
    suppressed: bool = False
    suppression_reason: str = ""


@dataclass
class DNDConfig:
    """Do Not Disturb configuration."""
    enabled: bool = True
    quiet_start: time = field(default_factory=lambda: time(22, 0))
    quiet_end: time = field(default_factory=lambda: time(6, 0))
    override_for: list[str] = field(default_factory=lambda: ["P0"])
    weekend_mode: str = "relaxed"  # "relaxed" or "off" or "strict"
    family_time_enabled: bool = True
    family_time_start: time = field(default_factory=lambda: time(17, 0))
    family_time_end: time = field(default_factory=lambda: time(20, 0))


@dataclass
class BatchConfig:
    """Batching rules per urgency tier."""
    interval_minutes: int = 120
    max_items: int = 10


DEFAULT_CHANNEL_MAP: dict[str, list[DeliveryChannel]] = {
    "P0": [DeliveryChannel.TELEGRAM, DeliveryChannel.IMESSAGE],
    "P1": [DeliveryChannel.TELEGRAM],
    "P2": [DeliveryChannel.MORNING_BRIEF],
    "P3": [DeliveryChannel.LOG_ONLY],
}

DEFAULT_BATCH_CONFIG: dict[str, BatchConfig] = {
    "P2": BatchConfig(interval_minutes=120, max_items=10),
    "P3": BatchConfig(interval_minutes=1440, max_items=50),
}


class NotificationManager:
    """Triage notifications with DND awareness and batching."""

    def __init__(
        self,
        dnd: DNDConfig | None = None,
        channel_map: dict[str, list[DeliveryChannel]] | None = None,
        batch_config: dict[str, BatchConfig] | None = None,
        config_path: Path | None = None,
    ):
        # Load from JSON config file if provided
        if config_path and config_path.exists():
            self._load_config(config_path)
        else:
            self.dnd = dnd or DNDConfig()
            self.channel_map = channel_map or DEFAULT_CHANNEL_MAP
            self.batch_config = batch_config or DEFAULT_BATCH_CONFIG

        # Batch queues
        self._batch_queues: dict[str, list[Notification]] = {"P2": [], "P3": []}
        self._last_flush: dict[str, datetime] = {}

        # Log
        self._log_dir = Path(__file__).parent / "logs"
        self._log_dir.mkdir(parents=True, exist_ok=True)

    def triage(self, notification: Notification) -> Notification:
        """Decide delivery channels, batching, and suppression for a notification."""
        now = datetime.now(timezone.utc)
        tier = notification.urgency.value

        # Check DND
        in_dnd = self._is_dnd(now)
        in_family_time = self._is_family_time(now)

        if tier == "P0":
            # P0 always delivers
            notification.delivery_channels = list(self.channel_map.get("P0", []))
            notification.batched = False

        elif tier == "P1":
            if in_family_time and self.dnd.family_time_enabled:
                # Family time — batch P1
                notification.delivery_channels = [DeliveryChannel.MORNING_BRIEF]
                notification.batched = True
                notification.suppression_reason = "family_time"
            elif in_dnd:
                # Quiet hours — batch P1
                notification.delivery_channels = [DeliveryChannel.MORNING_BRIEF]
                notification.batched = True
                notification.suppression_reason = "quiet_hours"
            else:
                notification.delivery_channels = list(self.channel_map.get("P1", []))

        elif tier == "P2":
            notification.delivery_channels = list(self.channel_map.get("P2", []))
            notification.batched = True
            self._batch_queues["P2"].append(notification)

        elif tier == "P3":
            notification.delivery_channels = list(self.channel_map.get("P3", []))
            notification.batched = True
            notification.suppressed = True
            notification.suppression_reason = "low_priority"
            self._batch_queues["P3"].append(notification)

        self._log_notification(notification)
        return notification

    def flush_batch(self, tier: str) -> list[Notification]:
        """Flush the batch queue for a given tier. Returns queued notifications."""
        queue = self._batch_queues.get(tier, [])
        config = self.batch_config.get(tier)
        if not queue:
            return []

        items = queue[:config.max_items] if config else queue[:]
        self._batch_queues[tier] = queue[len(items):]
        self._last_flush[tier] = datetime.now(timezone.utc)
        return items

    def should_flush(self, tier: str) -> bool:
        """Check if enough time has passed to flush a batch tier."""
        config = self.batch_config.get(tier)
        if not config:
            return False
        last = self._last_flush.get(tier)
        if not last:
            return len(self._batch_queues.get(tier, [])) > 0
        now = datetime.now(timezone.utc)
        elapsed = (now - last).total_seconds() / 60
        return elapsed >= config.interval_minutes and len(self._batch_queues.get(tier, [])) > 0

    def classify_urgency(
        self,
        content: str,
        source: str = "unknown",
        people: list[str] | None = None,
    ) -> UrgencyTier:
        """Auto-classify urgency from content and metadata."""
        text = content.lower()
        people_lower = [p.lower() for p in (people or [])]

        # P0 signals
        p0_keywords = [
            "emergency", "urgent", "critical", "outage", "down",
            "deadline today", "deadline in", "action required immediately",
            "flight", "hospital", "accident",
        ]
        if any(kw in text for kw in p0_keywords):
            return UrgencyTier.P0

        # VIP people always P1+
        vip_names = ["matt cohlmia", "cohlmia", "jordan", "voss", "ellen"]
        if any(v in " ".join(people_lower) for v in vip_names):
            return UrgencyTier.P1
        if any(v in text for v in vip_names):
            return UrgencyTier.P1

        # P1 signals
        p1_keywords = [
            "meeting in", "starts in", "asap", "important",
            "blocked", "waiting on you", "need your input",
        ]
        if any(kw in text for kw in p1_keywords):
            return UrgencyTier.P1

        # P3 signals (noise)
        p3_keywords = [
            "newsletter", "unsubscribe", "promotion", "marketing",
            "no-reply", "noreply", "donotreply", "notification",
        ]
        if any(kw in text for kw in p3_keywords):
            return UrgencyTier.P3

        # Default to P2
        return UrgencyTier.P2

    def _is_dnd(self, now: datetime) -> bool:
        """Check if current time is in DND quiet hours."""
        if not self.dnd.enabled:
            return False
        current_time = now.astimezone().time()
        start = self.dnd.quiet_start
        end = self.dnd.quiet_end
        # Handle overnight span (22:00 -> 06:00)
        if start > end:
            return current_time >= start or current_time < end
        return start <= current_time < end

    def _is_family_time(self, now: datetime) -> bool:
        """Check if current time is in family time window."""
        if not self.dnd.family_time_enabled:
            return False
        current_time = now.astimezone().time()
        return self.dnd.family_time_start <= current_time < self.dnd.family_time_end

    def _is_weekend(self, now: datetime) -> bool:
        """Check if today is a weekend."""
        return now.astimezone().weekday() >= 5

    def _load_config(self, path: Path):
        """Load notification config from JSON file."""
        with open(path) as f:
            data = json.load(f)

        dnd_data = data.get("dnd", {})
        self.dnd = DNDConfig(
            enabled=dnd_data.get("enabled", True),
            quiet_start=time(*map(int, dnd_data.get("quiet_hours", {}).get("start", "22:00").split(":"))),
            quiet_end=time(*map(int, dnd_data.get("quiet_hours", {}).get("end", "06:00").split(":"))),
            override_for=dnd_data.get("override_for", ["P0"]),
            weekend_mode=dnd_data.get("weekend_mode", "relaxed"),
            family_time_enabled=dnd_data.get("family_time", {}).get("enabled", True),
        )

        # Parse channel map
        channels_data = data.get("channels", {})
        self.channel_map = {}
        for tier, ch_list in channels_data.items():
            self.channel_map[tier] = [DeliveryChannel(c) for c in ch_list]

        # Parse batch config
        batch_data = data.get("batching", {})
        self.batch_config = {}
        for tier, cfg in batch_data.items():
            self.batch_config[tier] = BatchConfig(
                interval_minutes=cfg.get("interval_minutes", 120),
                max_items=cfg.get("max_items", 10),
            )

    def _log_notification(self, n: Notification):
        """Log notification decision to JSONL."""
        log_file = self._log_dir / "notifications.jsonl"
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "content": n.content[:200],
            "source": n.source,
            "urgency": n.urgency.value,
            "channels": [c.value for c in n.delivery_channels],
            "batched": n.batched,
            "suppressed": n.suppressed,
            "suppression_reason": n.suppression_reason,
        }
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except OSError:
            pass
