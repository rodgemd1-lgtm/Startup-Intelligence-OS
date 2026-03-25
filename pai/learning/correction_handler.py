"""Correction Handler — V5 Learning Engine

When Mike corrects Jake, captures the correction pair and updates rules.

Evolved from jake_brain/correction_handler.py — adds rule extraction,
LEARNED.md auto-update, and 3-strike auto-apply logic.

Correction capture format:
  {
    "timestamp": "...",
    "context": "...",
    "jake_said": "...",
    "mike_corrected": "...",
    "rule_extracted": "...",
    "applied_to": ["LEARNED.md"]
  }
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Correction signal patterns — these phrases from Mike = a correction
CORRECTION_PATTERNS = [
    r"\bno[,.]?\s+(it'?s|that'?s|its)\b",
    r"\bactually[,.]?\s+",
    r"\bthat'?s wrong\b",
    r"\byou'?re wrong\b",
    r"\bwrong[,.]?\s+",
    r"\bnot\s+(that|this|it)\b",
    r"\byou said\b.{0,60}\bbut\b",
    r"\bthe correct\b",
    r"\bcorrect(ion)?\s+",
    r"\bshould be\b",
    r"\bis actually\b",
    r"\bI told you\b",
    r"\bstop saying\b",
    r"\bstop calling\b",
    r"\bdon'?t call\b",
    r"\bremember[,:]?\s+it'?s\b",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in CORRECTION_PATTERNS]


@dataclass
class Correction:
    """A captured correction from Mike."""
    jake_said: str
    mike_corrected: str
    rule_extracted: str
    context: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    applied_to: list[str] = field(default_factory=list)
    occurrence_count: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "jake_said": self.jake_said[:300],
            "mike_corrected": self.mike_corrected[:300],
            "rule_extracted": self.rule_extracted,
            "context": self.context[:200],
            "timestamp": self.timestamp.isoformat(),
            "applied_to": self.applied_to,
            "occurrence_count": self.occurrence_count,
        }


class CorrectionHandler:
    """Detect, extract, and persist corrections from Mike."""

    CORRECTIONS_DIR = Path(__file__).parent.parent / "MEMORY" / "LEARNING" / "corrections"
    LOG_DIR = Path(__file__).parent.parent / "MEMORY" / "STATE"
    AUTO_APPLY_THRESHOLD = 3  # Auto-update LEARNED.md after 3 identical corrections

    def __init__(self):
        self.CORRECTIONS_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)

    def is_correction(self, message: str) -> bool:
        """Check if a message from Mike looks like a correction."""
        if not message or len(message.strip()) < 5:
            return False
        return any(p.search(message) for p in COMPILED_PATTERNS)

    def extract(self, mike_message: str, jake_response: str = "", context: str = "") -> Correction:
        """Extract correction details from Mike's message."""
        msg = mike_message.strip()

        # Try "it's X, not Y" pattern
        m = re.search(r"it'?s\s+(.{3,60}?)[,.]?\s+not\s+(.{3,60})", msg, re.I)
        if m:
            correct = m.group(1).strip().rstrip(".,!?")
            wrong = m.group(2).strip().rstrip(".,!?")
            return Correction(
                jake_said=wrong,
                mike_corrected=correct,
                rule_extracted=f"{correct} (NOT: {wrong})",
                context=context or jake_response[:200],
            )

        # Try "not X, it's Y" pattern
        m = re.search(r"\bnot\s+(.{3,60}?)[,.]?\s+it'?s\s+(.{3,60})", msg, re.I)
        if m:
            wrong = m.group(1).strip().rstrip(".,!?")
            correct = m.group(2).strip().rstrip(".,!?")
            return Correction(
                jake_said=wrong,
                mike_corrected=correct,
                rule_extracted=f"{correct} (NOT: {wrong})",
                context=context or jake_response[:200],
            )

        # Try "should be X" pattern
        m = re.search(r"should be\s+(.{3,80})", msg, re.I)
        if m:
            correct = m.group(1).strip().rstrip(".,!?")
            return Correction(
                jake_said=jake_response[:200] if jake_response else "(see context)",
                mike_corrected=correct,
                rule_extracted=correct,
                context=context or jake_response[:200],
            )

        # Fallback: the whole message is the correction
        return Correction(
            jake_said=jake_response[:200] if jake_response else "(see context)",
            mike_corrected=msg,
            rule_extracted=msg,
            context=context or jake_response[:200],
        )

    def process(self, mike_message: str, jake_response: str = "", context: str = "") -> Correction | None:
        """Full pipeline: detect → extract → persist → check auto-apply."""
        if not self.is_correction(mike_message):
            return None

        correction = self.extract(mike_message, jake_response, context)

        # Check for repeat corrections
        count = self._count_similar(correction.rule_extracted)
        correction.occurrence_count = count + 1

        # Persist
        self._persist(correction)

        # Auto-apply if threshold reached
        if correction.occurrence_count >= self.AUTO_APPLY_THRESHOLD:
            self._auto_apply_to_learned(correction)
            correction.applied_to.append("LEARNED.md (auto-applied, 3+ occurrences)")

        return correction

    def get_recent_corrections(self, days: int = 7) -> list[dict]:
        """Get corrections from the last N days."""
        log_file = self.LOG_DIR / "corrections.jsonl"
        if not log_file.exists():
            return []

        cutoff = datetime.now(timezone.utc).timestamp() - (days * 86400)
        recent = []
        with open(log_file) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    ts = datetime.fromisoformat(entry["timestamp"])
                    if ts.timestamp() > cutoff:
                        recent.append(entry)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
        return recent

    def format_confirmation(self, correction: Correction) -> str:
        """Format a confirmation message for Mike."""
        if correction.jake_said and correction.jake_said != "(see context)":
            return (
                f"Got it — updated my memory.\n"
                f"Old: {correction.jake_said[:100]}\n"
                f"New: {correction.mike_corrected[:100]}\n"
                f"Stored permanently. Won't happen again."
            )
        return f"Got it — stored permanently: {correction.mike_corrected[:150]}"

    def _count_similar(self, rule: str) -> int:
        """Count how many times a similar correction has been logged."""
        log_file = self.LOG_DIR / "corrections.jsonl"
        if not log_file.exists():
            return 0

        rule_lower = rule.lower()
        count = 0
        with open(log_file) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    existing = entry.get("rule_extracted", "").lower()
                    # Simple similarity: >50% word overlap
                    rule_words = set(rule_lower.split())
                    existing_words = set(existing.split())
                    if rule_words and existing_words:
                        overlap = len(rule_words & existing_words) / max(len(rule_words), 1)
                        if overlap > 0.5:
                            count += 1
                except (json.JSONDecodeError, KeyError):
                    continue
        return count

    def _persist(self, correction: Correction):
        """Save correction to JSONL log and individual file."""
        # JSONL log
        log_file = self.LOG_DIR / "corrections.jsonl"
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(correction.to_dict()) + "\n")
        except OSError:
            pass

        # Individual correction file
        ts = correction.timestamp.strftime("%Y-%m-%d-%H%M%S")
        file_path = self.CORRECTIONS_DIR / f"{ts}.json"
        try:
            with open(file_path, "w") as f:
                json.dump(correction.to_dict(), f, indent=2)
        except OSError:
            pass

    def _auto_apply_to_learned(self, correction: Correction):
        """Auto-append a correction rule to LEARNED.md after 3+ occurrences."""
        learned_path = Path(__file__).parent.parent / "TELOS" / "LEARNED.md"
        if not learned_path.exists():
            return

        entry = (
            f"\n## [{correction.timestamp.strftime('%Y-%m-%d')}] "
            f"Auto-applied correction ({correction.occurrence_count}x)\n"
            f"**Rule:** {correction.rule_extracted}\n"
            f"**Context:** {correction.context[:100]}\n"
        )

        try:
            with open(learned_path, "a") as f:
                f.write(entry)
        except OSError:
            pass
