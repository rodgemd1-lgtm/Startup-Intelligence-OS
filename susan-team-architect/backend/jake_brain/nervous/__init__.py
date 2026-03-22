"""Phase 8 — THE NERVOUS SYSTEM ⚡

Real-time event processing + push notifications.
Jake reacts to events as they happen, not just at cron time.

Modules:
  event_bus     — event queue, state file, dedup tracking
  email_alert   — urgent email detection → P0/P1 events
  meeting_prep  — upcoming meeting detection → prep briefs
  batcher       — debounce + batch pending alerts into one Telegram message
"""

from .event_bus import EventBus, NervousEvent, EventType
from .email_alert import EmailAlertScanner
from .meeting_prep import MeetingPrepScanner
from .batcher import NotificationBatcher

__all__ = [
    "EventBus",
    "NervousEvent",
    "EventType",
    "EmailAlertScanner",
    "MeetingPrepScanner",
    "NotificationBatcher",
]
