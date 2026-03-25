"""PAI V4: Proactive Intelligence Module

KIRA intent routing, smart notifications, SCOUT competitive intelligence,
decision support, priority engine, and structured brief formatting.
"""

from pai.intelligence.intent_router import IntentRouter, IntentCategory, RoutingDecision
from pai.intelligence.notifications import NotificationManager
from pai.intelligence.priority_engine import PriorityEngine
from pai.intelligence.brief_formatter import BriefFormatter

__all__ = [
    "IntentRouter",
    "IntentCategory",
    "RoutingDecision",
    "NotificationManager",
    "PriorityEngine",
    "BriefFormatter",
]
