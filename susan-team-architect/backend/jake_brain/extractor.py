"""Extract entities, decisions, patterns, and topics from text."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from jake_brain.config import brain_config


@dataclass
class Extraction:
    """Structured extraction from a piece of text."""
    people: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    preferences: list[str] = field(default_factory=list)
    project: str | None = None
    importance: float = 0.5


class Extractor:
    """Extract structured information from conversation text.

    This is a rule-based extractor. For v2, we can add LLM-based extraction
    for higher quality at the cost of API calls.
    """

    def extract(self, text: str) -> Extraction:
        """Run all extraction passes on text."""
        result = Extraction()
        result.people = self._extract_people(text)
        result.topics = self._extract_topics(text)
        result.decisions = self._extract_decisions(text)
        result.action_items = self._extract_action_items(text)
        result.patterns = self._extract_patterns(text)
        result.preferences = self._extract_preferences(text)
        result.project = self._detect_project(text)
        result.importance = self._estimate_importance(result)
        return result

    def _extract_people(self, text: str) -> list[str]:
        """Find known people mentioned in text."""
        lower = text.lower()
        found = []
        for person in brain_config.known_people:
            if person in lower:
                # Prefer full names over first names
                if person in ("matt",) and "matt cohlmia" in lower:
                    continue  # skip "matt" if "matt cohlmia" is present
                if person in ("jordan",) and "jordan voss" in lower:
                    continue
                found.append(person)
        return list(set(found))

    def _extract_topics(self, text: str) -> list[str]:
        """Extract topic keywords from text."""
        lower = text.lower()
        topic_keywords = {
            "recruiting": ["recruit", "outreach", "coach", "pipeline", "prospect"],
            "oracle-health": ["oracle health", "oracle", "myhelp", "cohlmia"],
            "ai-agents": ["agent", "susan", "hermes", "mcp", "rag"],
            "memory": ["memory", "brain", "cognitive", "episodic", "semantic"],
            "meetings": ["meeting", "calendar", "agenda", "prep"],
            "email": ["email", "inbox", "triage", "compose"],
            "family": ["jacob", "alex", "james", "jen", "birthday", "family"],
            "football": ["football", "recruiting", "ol", "dl", "offensive line"],
            "strategy": ["strategy", "roadmap", "plan", "architecture"],
            "finance": ["budget", "cost", "revenue", "pricing", "runway"],
        }
        found = []
        for topic, keywords in topic_keywords.items():
            if any(kw in lower for kw in keywords):
                found.append(topic)
        return found

    def _extract_decisions(self, text: str) -> list[str]:
        """Extract decision statements."""
        decisions = []
        patterns = [
            r"(?:decided|decision|chose|going with|we'll use|settled on|agreed on)\s*:?\s*(.{10,200})",
            r"(?:##\s*Decisions?\s*Made?)\s*\n([\s\S]*?)(?:\n##|\Z)",
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                dec = match.group(1).strip()[:200]
                if dec and len(dec) > 10:
                    decisions.append(dec)
        return decisions[:10]

    def _extract_action_items(self, text: str) -> list[str]:
        """Extract action items and TODOs."""
        items = []
        patterns = [
            r"- \[ \]\s+(.{5,150})",
            r"(?:TODO|FIXME|ACTION)[\s:]+(.{5,150})",
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                items.append(match.group(1).strip())
        return items[:10]

    def _extract_patterns(self, text: str) -> list[str]:
        """Extract observed patterns and rules."""
        patterns_found = []
        pattern_signals = [
            r"(?:pattern|always|never|every time|consistently|tends to)\s+(.{10,150})",
            r"(?:works? best|most effective|optimal)\s+(?:when|if|for)\s+(.{10,150})",
            r"(?:rule|principle|guideline)\s*:?\s+(.{10,150})",
        ]
        for pattern in pattern_signals:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                patterns_found.append(match.group(1).strip()[:150])
        return patterns_found[:5]

    def _extract_preferences(self, text: str) -> list[str]:
        """Extract stated preferences."""
        prefs = []
        pref_patterns = [
            r"(?:i prefer|i like|i want|i hate|i don't like|don't want)\s+(.{5,150})",
            r"(?:mike (?:prefers|likes|wants|hates))\s+(.{5,150})",
        ]
        for pattern in pref_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                prefs.append(match.group(1).strip()[:150])
        return prefs[:5]

    def _detect_project(self, text: str) -> str | None:
        """Auto-detect project context from content."""
        lower = text.lower()
        for project, keywords in brain_config.known_projects.items():
            for kw in keywords:
                if re.search(kw, lower):
                    return project
        return None

    def _estimate_importance(self, extraction: Extraction) -> float:
        """Estimate importance based on what was extracted."""
        score = 0.3  # base

        if extraction.decisions:
            score += 0.3
        if extraction.action_items:
            score += 0.1
        if extraction.patterns:
            score += 0.2
        if extraction.preferences:
            score += 0.2
        if len(extraction.people) >= 2:
            score += 0.1
        if extraction.project:
            score += 0.05

        return min(1.0, score)
