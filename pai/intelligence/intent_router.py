"""KIRA Intent Router — V4 Proactive Intelligence

Classifies every incoming message into 7 intent categories with confidence scoring,
then routes to the right model tier, agent, and response style.

Evolved from jake_brain/intent_router.py (12 keyword categories) into a 7-category
system with model tier routing and confidence-based escalation.

Categories:
  quick_answer  → nano model, no agent          "What time is Jacob's game?"
  status_check  → cheap model, no agent         "How are the goals looking?"
  research      → mid model, research-director   "What's the latest on competitors?"
  strategy      → expensive model, steve         "Should we pivot pricing?"
  build         → expensive model, atlas          "Add dark mode to dashboard"
  decision      → expensive model, multiple       "Should I take this meeting?"
  casual        → cheap model, no agent           "Hey Jake"

If confidence < 0.6, escalates to Opus for disambiguation.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class IntentCategory(str, Enum):
    QUICK_ANSWER = "quick_answer"
    STATUS_CHECK = "status_check"
    RESEARCH = "research"
    STRATEGY = "strategy"
    BUILD = "build"
    DECISION = "decision"
    CASUAL = "casual"


class ModelTier(str, Enum):
    NANO = "nano"           # GPT-4o-mini, Haiku — fast, cheap
    CHEAP = "cheap"         # GPT-4o, Sonnet — good enough
    MID = "mid"             # GPT-4o, Sonnet — with agent routing
    EXPENSIVE = "expensive"  # Opus, GPT-5 — full power


@dataclass
class RoutingDecision:
    """Result of KIRA intent classification."""
    original_message: str
    intent: IntentCategory
    confidence: float
    model_tier: ModelTier
    agent: str | None = None
    agents: list[str] = field(default_factory=list)  # for multi-agent decisions
    context_hints: dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""
    escalate: bool = False  # True if confidence < 0.6

    def to_dict(self) -> dict:
        return {
            "intent": self.intent.value,
            "confidence": self.confidence,
            "model_tier": self.model_tier.value,
            "agent": self.agent,
            "agents": self.agents,
            "escalate": self.escalate,
            "reasoning": self.reasoning,
        }


# --- Routing rules ---
# (intent, model_tier, agent, agents_list, keywords, patterns, context_hints)

RULES: list[dict] = [
    {
        "intent": IntentCategory.CASUAL,
        "model": ModelTier.CHEAP,
        "agent": None,
        "keywords": [
            "hey", "hi", "hello", "yo", "sup", "good morning", "good evening",
            "thanks", "thank you", "cool", "nice", "ok", "okay", "got it",
            "how are you", "what's up", "how's it going",
        ],
        "patterns": [
            r"^(hey|hi|hello|yo|sup)\b",
            r"^(thanks|thank you|cool|ok|okay|got it)\s*$",
        ],
        "hints": {"mode": "casual", "max_tokens": 150},
    },
    {
        "intent": IntentCategory.QUICK_ANSWER,
        "model": ModelTier.NANO,
        "agent": None,
        "keywords": [
            "what time", "when is", "where is", "how many", "what day",
            "what date", "who is", "phone number", "address", "zip code",
            "weather", "score", "game time", "practice", "pickup",
            "jacob's game", "james", "dentist", "doctor",
        ],
        "patterns": [
            r"^(what|when|where|who|how many)\b.*\?",
            r"\b(time|date|address|number)\b.*\?",
        ],
        "hints": {"mode": "lookup", "max_tokens": 200},
    },
    {
        "intent": IntentCategory.STATUS_CHECK,
        "model": ModelTier.CHEAP,
        "agent": None,
        "keywords": [
            "status", "how are", "how's", "progress", "update", "check on",
            "goals", "goal progress", "pipeline", "funnel", "metrics",
            "brief", "morning brief", "daily brief", "what's today",
            "today look like", "what do i have", "schedule", "calendar",
            "email", "inbox", "unread", "any emails",
        ],
        "patterns": [
            r"\b(status|progress|update|check)\b",
            r"\bhow('s| are| is)\b.*\b(goal|project|company|pipeline)\b",
            r"\bbrief\b",
            r"\bcalendar\b",
            r"\bemail\b",
        ],
        "hints": {"mode": "status", "time_range_hours": 48},
    },
    {
        "intent": IntentCategory.RESEARCH,
        "model": ModelTier.MID,
        "agent": "research-director",
        "keywords": [
            "research", "look up", "find out", "investigate", "analyze",
            "competitive", "market", "benchmark", "what do we know",
            "competitor", "industry", "trend", "landscape", "deep dive",
            "white space", "opportunity", "threat",
        ],
        "patterns": [
            r"\bresearch\b",
            r"\bcompetit(ive|or)\b",
            r"\bmarket\b.*(analysis|research|landscape)",
            r"\bwhat do we know\b",
            r"\bdeep dive\b",
        ],
        "hints": {"mode": "research", "include_rag": True},
    },
    {
        "intent": IntentCategory.STRATEGY,
        "model": ModelTier.EXPENSIVE,
        "agent": "steve-strategy",
        "keywords": [
            "strategy", "strategic", "pivot", "pricing", "positioning",
            "roadmap", "vision", "mission", "moat", "differentiation",
            "business model", "go-to-market", "gtm", "fundraise",
            "should we", "what if we", "long term", "big picture",
        ],
        "patterns": [
            r"\bstrateg(y|ic)\b",
            r"\bpivot\b",
            r"\bpricing\b",
            r"\bshould we\b.*\b(pivot|change|stop|start|focus)\b",
            r"\bgo.to.market\b",
        ],
        "hints": {"mode": "strategy", "include_rag": True, "include_decisions": True},
    },
    {
        "intent": IntentCategory.BUILD,
        "model": ModelTier.EXPENSIVE,
        "agent": "atlas-engineering",
        "keywords": [
            "build", "implement", "code", "deploy", "fix", "bug", "feature",
            "refactor", "test", "pr", "pull request", "commit", "branch",
            "api", "endpoint", "database", "schema", "migration",
            "add", "create", "wire", "integrate", "install",
        ],
        "patterns": [
            r"\b(build|implement|deploy|fix|refactor)\b",
            r"\b(add|create|wire|install)\b.*\b(feature|component|module|page)\b",
            r"\bbug\b",
            r"\bpr\b",
        ],
        "hints": {"mode": "build", "include_codebase": True},
    },
    {
        "intent": IntentCategory.DECISION,
        "model": ModelTier.EXPENSIVE,
        "agent": "steve-strategy",
        "agents": ["steve-strategy", "shield-legal-compliance", "ledger-finance"],
        "keywords": [
            "decide", "decision", "should i", "should we", "worth it",
            "trade-off", "tradeoff", "pros and cons", "options",
            "take this meeting", "accept", "reject", "hire", "fire",
            "invest", "spend", "buy", "sell", "partner", "quit",
        ],
        "patterns": [
            r"\bshould (i|we)\b",
            r"\bdecide\b",
            r"\bdecision\b",
            r"\b(pros|cons)\b",
            r"\b(worth|worthwhile)\b.*\?",
            r"\b(accept|reject|hire|fire|invest|buy|sell)\b.*\?",
        ],
        "hints": {"mode": "decision", "include_rag": True, "include_decisions": True},
    },
]


class IntentRouter:
    """KIRA-style intent classifier with model tier routing."""

    ESCALATION_THRESHOLD = 0.6
    LOG_DIR = Path(__file__).parent / "logs"

    def __init__(self, log_classifications: bool = True):
        self.log_classifications = log_classifications
        if self.log_classifications:
            self.LOG_DIR.mkdir(parents=True, exist_ok=True)

    def classify(self, message: str) -> RoutingDecision:
        """Classify a message and return a routing decision."""
        msg_lower = message.lower().strip()

        best_score = 0.0
        best_rule = None

        for rule in RULES:
            score = 0.0
            matched = []

            # Keyword matching (0.12 each, diminishing returns)
            kw_hits = 0
            for kw in rule["keywords"]:
                if kw in msg_lower:
                    kw_hits += 1
                    matched.append(f"kw:{kw}")
            if kw_hits > 0:
                score += min(0.5, kw_hits * 0.12)

            # Regex patterns (0.2 each)
            for pat in rule["patterns"]:
                if re.search(pat, msg_lower):
                    score += 0.2
                    matched.append(f"re:{pat[:30]}")

            # Length heuristic: very short messages more likely casual/quick
            if len(msg_lower.split()) <= 3 and rule["intent"] == IntentCategory.CASUAL:
                score += 0.1

            # Question mark boost for quick_answer
            if "?" in message and rule["intent"] == IntentCategory.QUICK_ANSWER:
                score += 0.1

            score = min(1.0, score)

            if score > best_score:
                best_score = score
                best_rule = rule

        # Default to casual with low confidence if nothing matched
        if best_rule is None or best_score < 0.08:
            return RoutingDecision(
                original_message=message,
                intent=IntentCategory.CASUAL,
                confidence=0.3,
                model_tier=ModelTier.CHEAP,
                reasoning="No strong match — defaulting to casual",
                escalate=True,
            )

        decision = RoutingDecision(
            original_message=message,
            intent=best_rule["intent"],
            confidence=round(best_score, 3),
            model_tier=best_rule["model"],
            agent=best_rule.get("agent"),
            agents=best_rule.get("agents", []),
            context_hints=best_rule.get("hints", {}),
            reasoning=f"Matched {best_rule['intent'].value} (score={best_score:.3f})",
            escalate=best_score < self.ESCALATION_THRESHOLD,
        )

        if self.log_classifications:
            self._log(decision)

        return decision

    def classify_and_format(self, message: str) -> str:
        """Classify and return a human-readable summary."""
        d = self.classify(message)
        lines = [
            f"Intent: {d.intent.value} (confidence={d.confidence:.2f})",
            f"Model: {d.model_tier.value}",
        ]
        if d.agent:
            lines.append(f"Agent: {d.agent}")
        if d.agents:
            lines.append(f"Agents: {', '.join(d.agents)}")
        if d.escalate:
            lines.append("ESCALATE: Low confidence — needs Opus disambiguation")
        lines.append(f"Reasoning: {d.reasoning}")
        return "\n".join(lines)

    def _log(self, decision: RoutingDecision):
        """Append classification to JSONL log."""
        log_file = self.LOG_DIR / "intent-classifications.jsonl"
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "message": decision.original_message[:200],
            **decision.to_dict(),
        }
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except OSError:
            pass  # Non-critical — don't crash on log failure
