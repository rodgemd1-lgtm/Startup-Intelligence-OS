"""Cross-Portfolio Synergy Detector — V8 Cross-Domain Intelligence

Detects patterns, techniques, and capabilities that transfer between companies.

Synergy types:
  Pattern transfer   — multi-agent orchestration from SIO → Oracle Health
  Capability reuse   — Susan RAG architecture → Alex Recruiting knowledge base
  Resource sharing   — ElevenLabs voice → all 3 companies
  Market insight     — Oracle Health enterprise sales → Alex Recruiting B2B
  Technical debt     — Bug fix in one → prevent same bug in others
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SynergyType:
    PATTERN_TRANSFER = "pattern_transfer"
    CAPABILITY_REUSE = "capability_reuse"
    RESOURCE_SHARING = "resource_sharing"
    MARKET_INSIGHT = "market_insight"
    TECHNICAL_DEBT = "technical_debt"


@dataclass
class Synergy:
    """A detected cross-company synergy."""
    title: str
    synergy_type: str
    source_company: str
    target_company: str
    description: str
    confidence: float = 0.5  # 0-1
    effort: str = "medium"
    impact: str = "medium"
    status: str = "detected"  # "detected", "proposed", "approved", "implemented"
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "synergy_type": self.synergy_type,
            "source_company": self.source_company,
            "target_company": self.target_company,
            "description": self.description,
            "confidence": self.confidence,
            "effort": self.effort,
            "impact": self.impact,
            "status": self.status,
            "detected_at": self.detected_at.isoformat(),
        }


# Known cross-company capability domains
CAPABILITY_DOMAINS = {
    "startup-intelligence-os": [
        "multi-agent orchestration", "rag architecture", "fabric patterns",
        "memory consolidation", "intent routing", "priority scoring",
        "competitive intelligence", "decision support", "voice interface",
    ],
    "oracle-health": [
        "clinical ai", "ehr integration", "enterprise sales", "compliance",
        "training systems", "healthcare workflows", "ambient documentation",
    ],
    "alex-recruiting": [
        "coach outreach", "highlight analysis", "recruiting pipeline",
        "nil deals", "transfer portal", "athlete profiles",
    ],
}


class SynergyDetector:
    """Detect cross-portfolio synergies between companies."""

    LOG_DIR = Path(__file__).parent / "logs"

    def __init__(self):
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self._synergies: list[Synergy] = []

    def detect_all(self) -> list[Synergy]:
        """Run full synergy detection across all company pairs."""
        synergies = []
        companies = list(CAPABILITY_DOMAINS.keys())

        for i, source in enumerate(companies):
            for target in companies[i + 1:]:
                synergies.extend(self._detect_pair(source, target))

        self._synergies = synergies
        self._persist(synergies)
        return synergies

    def detect_from_signals(self, signals: list[dict]) -> list[Synergy]:
        """Detect synergies from SCOUT competitive signals."""
        synergies = []
        for signal in signals:
            company = signal.get("company", "")
            category = signal.get("category", "")

            # If a competitor launches something in one domain, check if
            # our other companies could benefit from a similar capability
            for other_company in CAPABILITY_DOMAINS:
                if other_company == company:
                    continue
                if self._could_benefit(other_company, category):
                    synergies.append(Synergy(
                        title=f"Apply {category} insight from {company} to {other_company}",
                        synergy_type=SynergyType.MARKET_INSIGHT,
                        source_company=company,
                        target_company=other_company,
                        description=f"Competitive signal in {company}: {signal.get('title', '')}. "
                                    f"Consider applying similar strategy to {other_company}.",
                        confidence=0.4,
                    ))

        return synergies

    def weekly_report(self) -> str:
        """Generate a weekly cross-domain synergy report."""
        synergies = self._synergies or self.detect_all()

        if not synergies:
            return "No cross-domain synergies detected this week."

        lines = ["# Cross-Domain Synergy Report", ""]

        by_type: dict[str, list[Synergy]] = {}
        for s in synergies:
            by_type.setdefault(s.synergy_type, []).append(s)

        for stype, items in by_type.items():
            lines.append(f"## {stype.replace('_', ' ').title()} ({len(items)})")
            for s in items:
                lines.append(f"  - [{s.confidence:.0%}] {s.source_company} → {s.target_company}: {s.title}")
            lines.append("")

        return "\n".join(lines)

    def _detect_pair(self, source: str, target: str) -> list[Synergy]:
        """Detect synergies between two specific companies."""
        synergies = []
        source_caps = CAPABILITY_DOMAINS.get(source, [])
        target_caps = CAPABILITY_DOMAINS.get(target, [])

        # Find capabilities in source that could transfer to target
        transferable = [
            "multi-agent orchestration", "rag architecture", "memory consolidation",
            "intent routing", "priority scoring", "competitive intelligence",
            "decision support", "fabric patterns",
        ]

        for cap in source_caps:
            if cap in transferable and cap not in target_caps:
                synergies.append(Synergy(
                    title=f"Transfer '{cap}' from {source} to {target}",
                    synergy_type=SynergyType.CAPABILITY_REUSE,
                    source_company=source,
                    target_company=target,
                    description=f"'{cap}' is proven in {source} and could be adapted for {target}.",
                    confidence=0.6,
                    effort="medium",
                    impact="high",
                ))

        return synergies

    def _could_benefit(self, company: str, category: str) -> bool:
        """Check if a company could benefit from a capability category."""
        caps = CAPABILITY_DOMAINS.get(company, [])
        return not any(category.lower() in cap.lower() for cap in caps)

    def _persist(self, synergies: list[Synergy]):
        log_file = self.LOG_DIR / "synergies.jsonl"
        try:
            with open(log_file, "a") as f:
                for s in synergies:
                    f.write(json.dumps(s.to_dict()) + "\n")
        except OSError:
            pass
