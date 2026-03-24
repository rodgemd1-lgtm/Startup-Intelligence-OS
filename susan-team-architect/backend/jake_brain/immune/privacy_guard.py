"""Privacy Guard — classify data sensitivity and enforce context boundaries.

Rules:
  - Personal data (health, family, finances, relationships) NEVER appears in work contexts.
  - Work data (Oracle Health, Salesforce, SharePoint) doesn't leak to family/recruiting contexts.
  - Sensitivity levels: PUBLIC < INTERNAL < PERSONAL < SENSITIVE

Context types and their allowed sensitivity levels:
  - "work"       → PUBLIC, INTERNAL only
  - "personal"   → all levels allowed
  - "family"     → PUBLIC, PERSONAL (not INTERNAL/SENSITIVE work data)
  - "recruiting" → PUBLIC only (Jacob's data, coach contacts — minimal sensitivity)
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import IntEnum
from typing import Sequence


class SensitivityLevel(IntEnum):
    PUBLIC = 0       # Anyone can see this
    INTERNAL = 1     # Mike only, work-related
    PERSONAL = 2     # Personal life, family — not for work
    SENSITIVE = 3    # Medical, financial, relationship details


# Which sensitivity levels are allowed per context
_CONTEXT_ALLOWED: dict[str, set[int]] = {
    "work":       {SensitivityLevel.PUBLIC, SensitivityLevel.INTERNAL},
    "personal":   {SensitivityLevel.PUBLIC, SensitivityLevel.INTERNAL,
                   SensitivityLevel.PERSONAL, SensitivityLevel.SENSITIVE},
    "family":     {SensitivityLevel.PUBLIC, SensitivityLevel.PERSONAL},
    "recruiting": {SensitivityLevel.PUBLIC},
}


@dataclass
class ClassificationResult:
    level: SensitivityLevel
    reason: str
    blocked_in: list[str]  # context types where this content is blocked


# ---------------------------------------------------------------------------
# Pattern-based classifier
# ---------------------------------------------------------------------------

# SENSITIVE patterns — medical, financial, relationship details
_SENSITIVE_PATTERNS = [
    r"\b(ssn|social security|passport)\b",
    r"\b(bank account|routing number|credit card|account number)\b",
    r"\b(diagnosis|prescribed|medication|therapy|mental health|depression|anxiety)\b",
    r"\b(salary|compensation|bonus|equity|stock options)\b",
    r"\b(divorce|custody|legal dispute|settlement)\b",
    r"\b(password|api.key|secret.key|private.key|token)\b",
]

# PERSONAL patterns — family life, personal relationships, not medical/financial
_PERSONAL_PATTERNS = [
    r"\b(jacob|alex|jen|jennifer|james loehr)\b",  # family members (except Mike)
    r"\b(football|recruiting|coach|scholarship)\b",
    r"\b(school|homework|practice|game|athlete)\b",
    r"\b(birthday|anniversary|wedding|graduation)\b",
    r"\b(personal calendar|family calendar|home calendar)\b",
    r"\b(workout|fitness|sleep|diet|nutrition)\b",
]

# INTERNAL patterns — work-specific, Oracle Health, business
_INTERNAL_PATTERNS = [
    r"\b(oracle health|oracle|cohlmia|matt cohlmia)\b",
    r"\b(sharepoint|myhelp|salesforce|jira|confluence)\b",
    r"\b(quarterly|q[1-4] |roadmap|budget|revenue|forecast)\b",
    r"\b(compliance|hipaa|phi|patient|clinical|ehr)\b",
    r"\b(stakeholder|executive|c-suite|vp |director)\b",
    r"\b(contract|nda|confidential|proprietary)\b",
]


def _matches_any(text: str, patterns: list[str]) -> bool:
    lower = text.lower()
    return any(re.search(p, lower) for p in patterns)


class PrivacyGuard:
    """Classifies content sensitivity and filters memories for context safety."""

    def classify(self, text: str) -> ClassificationResult:
        """Classify the sensitivity level of a piece of text."""
        if _matches_any(text, _SENSITIVE_PATTERNS):
            level = SensitivityLevel.SENSITIVE
            reason = "Contains sensitive personal data (medical/financial/credentials)"
        elif _matches_any(text, _PERSONAL_PATTERNS):
            level = SensitivityLevel.PERSONAL
            reason = "Contains personal/family information"
        elif _matches_any(text, _INTERNAL_PATTERNS):
            level = SensitivityLevel.INTERNAL
            reason = "Contains internal work/business information"
        else:
            level = SensitivityLevel.PUBLIC
            reason = "No sensitive patterns detected"

        blocked_in = [
            ctx for ctx, allowed in _CONTEXT_ALLOWED.items()
            if level not in allowed
        ]

        return ClassificationResult(level=level, reason=reason, blocked_in=blocked_in)

    def is_safe_for_context(self, text: str, context_type: str) -> bool:
        """Return True if text can appear in the given context type."""
        result = self.classify(text)
        allowed = _CONTEXT_ALLOWED.get(context_type, {SensitivityLevel.PUBLIC})
        return result.level in allowed

    def filter_memories(
        self, memories: list[dict], context_type: str
    ) -> tuple[list[dict], list[dict]]:
        """Split memories into (safe, blocked) for the given context.

        Returns:
            safe: memories allowed in this context
            blocked: memories filtered out
        """
        safe, blocked = [], []
        for mem in memories:
            content = mem.get("content", "")
            if self.is_safe_for_context(content, context_type):
                safe.append(mem)
            else:
                blocked.append(mem)
        return safe, blocked

    def redact(self, text: str) -> str:
        """Redact sensitive patterns from text (for logging/preview only)."""
        for pattern in _SENSITIVE_PATTERNS:
            text = re.sub(pattern, "[REDACTED]", text, flags=re.IGNORECASE)
        return text

    def audit_memories(
        self, memories: Sequence[dict]
    ) -> list[dict]:
        """Classify each memory and return audit records.

        Returns list of { content_preview, level, reason, blocked_in }
        """
        results = []
        for mem in memories:
            content = mem.get("content", "")
            r = self.classify(content)
            results.append({
                "id": mem.get("id"),
                "layer": mem.get("layer", "unknown"),
                "content_preview": content[:100],
                "sensitivity": r.level.name,
                "reason": r.reason,
                "blocked_in": r.blocked_in,
            })
        return results
