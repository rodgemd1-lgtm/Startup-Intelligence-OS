"""Intent Router — classify user request intent and route to the right handler.

This is Jake's lightweight KIRA-equivalent for Hermes. It classifies an
incoming message and returns:
  - intent_class: what kind of request is this?
  - confidence: 0.0–1.0
  - suggested_skill: which Hermes skill to invoke
  - context_hints: what brain context to assemble first
  - agent_suggestion: which Susan agent to use (if applicable)

Design: keyword + pattern matching (fast, no LLM call needed).
Upgrade path: swap classify() with a local embedding similarity model.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class IntentClass(str, Enum):
    # Calendar & schedule
    CALENDAR = "calendar"           # "what's on my calendar", "today's schedule"
    # Email
    EMAIL = "email"                 # "check email", "any emails from Matt"
    # Reminders & tasks
    REMINDER = "reminder"           # "add a reminder", "what do I have to do"
    # Morning/daily brief
    BRIEF = "brief"                 # "morning brief", "daily summary", "what's today"
    # Oracle Health
    ORACLE = "oracle"               # "Oracle meeting", "SharePoint", "Ellen"
    # Family & personal
    FAMILY = "family"               # "Jacob's game", "James", "kids"
    # Recruiting (Jacob)
    RECRUITING = "recruiting"       # "coach outreach", "Jacob's highlights"
    # Research
    RESEARCH = "research"           # "research X", "what do we know about"
    # Memory & recall
    MEMORY = "memory"               # "what did we decide", "remember", "recall"
    # System & ops
    SYSTEM = "system"               # "cron status", "health check", "brain stats"
    # Coding & dev
    CODING = "coding"               # "fix the bug", "deploy", "PR"
    # General / fallback
    GENERAL = "general"


@dataclass
class RoutingDecision:
    """Result of routing a user message."""

    original_message: str
    intent_class: str
    confidence: float
    suggested_skill: str | None = None        # Hermes skill name
    agent_suggestion: str | None = None        # Susan agent name
    context_hints: dict = field(default_factory=dict)  # hints for ContextAssembler
    reasoning: str = ""


# Rule table: (intent_class, skill, agent, keywords, patterns)
ROUTING_RULES: list[tuple[str, str | None, str | None, list[str], list[str]]] = [
    # intent_class, skill, agent, keywords, regex_patterns
    (
        IntentClass.BRIEF,
        "jake-daily-intel",
        None,
        ["brief", "morning brief", "daily brief", "what's today", "today look like",
         "what do i have today", "morning summary", "daily summary", "what's on today",
         "whats today", "daily intel"],
        [r"\bbrief\b", r"\bmorning\b.*\bsummary\b"],
    ),
    (
        IntentClass.CALENDAR,
        "jake-daily-intel",
        None,
        ["calendar", "schedule", "meeting", "event", "appointment", "what time",
         "when is", "do i have anything", "what's on my", "whats on my"],
        [r"\bschedule\b", r"\bmeeting\b", r"\bcalendar\b"],
    ),
    (
        IntentClass.EMAIL,
        "email-triage",
        None,
        ["email", "inbox", "unread", "mail", "message from", "did.*email",
         "any emails", "oracle email", "exchange"],
        [r"\bemail(s)?\b", r"\binbox\b", r"\bunread\b"],
    ),
    (
        IntentClass.REMINDER,
        None,
        None,
        ["reminder", "remind me", "to-do", "todo", "task", "add a task",
         "what do i need to do", "what's due", "overdue"],
        [r"\breminder\b", r"\btask(s)?\b"],
    ),
    (
        IntentClass.ORACLE,
        "ellen-oracle-health",
        "oracle-jake",
        ["oracle", "sharepoint", "ellen", "cohlmia", "oracle health",
         "myhelp", "oracle meeting", "work meeting"],
        [r"\boracle\b", r"\bsharepoint\b"],
    ),
    (
        IntentClass.FAMILY,
        None,
        "family-jake",
        ["jacob", "james", "alex", "jen", "kids", "son", "husband",
         "family", "school", "game", "practice", "sport"],
        [r"\bjacob\b", r"\bjames\b", r"\bkids\b"],
    ),
    (
        IntentClass.RECRUITING,
        None,
        "recruiting-jake",
        ["coach", "recruit", "recruiting", "highlight", "film", "offer",
         "scholarship", "visit", "campus", "ncaa"],
        [r"\bcoach\b", r"\brecruit\b", r"\bhighlight(s)?\b"],
    ),
    (
        IntentClass.RESEARCH,
        None,
        "research-jake",
        ["research", "what do we know about", "look up", "find out",
         "investigate", "analyze", "competitive intel", "market"],
        [r"\bresearch\b", r"\bcompetitive\b"],
    ),
    (
        IntentClass.MEMORY,
        None,
        None,
        ["remember", "recall", "what did we", "what did you", "last time",
         "last session", "we decided", "brain", "memory"],
        [r"\bremember\b", r"\brecall\b", r"\bbrain\b"],
    ),
    (
        IntentClass.SYSTEM,
        None,
        None,
        ["cron", "health check", "system status", "brain stats", "plugin",
         "hermes status", "what's running", "launchd", "error rate"],
        [r"\bcron\b", r"\bhealth\b.*\bcheck\b", r"\bstatus\b"],
    ),
    (
        IntentClass.CODING,
        None,
        "atlas-engineering",
        ["bug", "deploy", "pull request", "pr", "commit", "branch", "test",
         "build", "error in code", "fix the", "implement", "refactor"],
        [r"\bbug\b", r"\bdeploy\b", r"\bpr\b", r"\bcommit\b"],
    ),
]

# Context hint templates per intent
CONTEXT_HINTS: dict[str, dict] = {
    IntentClass.BRIEF: {
        "mode": "morning_brief",
        "time_range_hours": 48,
        "include_entities": True,
    },
    IntentClass.CALENDAR: {
        "mode": "standard",
        "filter_source": "calendar",
        "time_range_hours": 24,
    },
    IntentClass.EMAIL: {
        "mode": "standard",
        "filter_source": "email",
        "time_range_hours": 24,
    },
    IntentClass.ORACLE: {
        "mode": "standard",
        "project": "oracle-health",
        "people": ["matt cohlmia", "ellen"],
    },
    IntentClass.FAMILY: {
        "mode": "person",
        "people": ["jacob", "james", "alex", "jen"],
    },
    IntentClass.RECRUITING: {
        "mode": "standard",
        "project": "alex-recruiting",
        "people": ["jacob"],
    },
    IntentClass.MEMORY: {
        "mode": "recall",
        "include_entities": True,
        "time_range_hours": 168,  # 7 days
    },
    IntentClass.CODING: {
        "mode": "standard",
        "project": "startup-os",
    },
    IntentClass.GENERAL: {
        "mode": "standard",
    },
}


class IntentRouter:
    """Route user messages to the right skill/agent based on intent."""

    def route(self, message: str) -> RoutingDecision:
        """Classify message and return routing decision."""
        message_lower = message.lower().strip()

        best_intent = IntentClass.GENERAL
        best_confidence = 0.0
        best_skill = None
        best_agent = None
        best_reasoning = "No strong pattern matched — routing to general"

        for (intent, skill, agent, keywords, patterns) in ROUTING_RULES:
            score = 0.0
            matched_on = []

            # Keyword matching
            for kw in keywords:
                if kw in message_lower:
                    score += 0.15
                    matched_on.append(f"kw:{kw}")

            # Regex pattern matching (higher weight)
            for pat in patterns:
                if re.search(pat, message_lower):
                    score += 0.25
                    matched_on.append(f"re:{pat}")

            # Normalize: cap at 1.0
            confidence = min(1.0, score)

            if confidence > best_confidence:
                best_confidence = confidence
                best_intent = intent
                best_skill = skill
                best_agent = agent
                best_reasoning = f"Matched: {', '.join(matched_on[:3])}"

        # Fallback to GENERAL with low confidence
        if best_confidence < 0.10:
            best_intent = IntentClass.GENERAL
            best_confidence = 0.30
            best_reasoning = "No pattern matched — general routing"

        hints = CONTEXT_HINTS.get(best_intent, CONTEXT_HINTS[IntentClass.GENERAL]).copy()

        return RoutingDecision(
            original_message=message,
            intent_class=best_intent,
            confidence=round(best_confidence, 3),
            suggested_skill=best_skill,
            agent_suggestion=best_agent,
            context_hints=hints,
            reasoning=best_reasoning,
        )

    def route_and_format(self, message: str) -> str:
        """Route and return a formatted summary string."""
        decision = self.route(message)
        lines = [
            f"Intent: {decision.intent_class} (confidence={decision.confidence:.2f})",
            f"Reasoning: {decision.reasoning}",
        ]
        if decision.suggested_skill:
            lines.append(f"Skill: /{decision.suggested_skill}")
        if decision.agent_suggestion:
            lines.append(f"Agent: {decision.agent_suggestion}")
        lines.append(f"Context mode: {decision.context_hints.get('mode', 'standard')}")
        return "\n".join(lines)

    def should_notify(self, message: str, threshold: float = 0.60) -> bool:
        """Quick check: is this message worth a push notification?"""
        decision = self.route(message)
        high_priority_intents = {
            IntentClass.BRIEF,
            IntentClass.ORACLE,
            IntentClass.SYSTEM,
        }
        return (
            decision.intent_class in high_priority_intents
            and decision.confidence >= threshold
        )
