"""Auto-Pattern Generator — V5 Learning Engine

Detects recurring interaction patterns and auto-generates Fabric custom patterns.

Detection method:
  1. Analyze last 30 days of work sessions
  2. Find repeated task types (e.g., "competitive analysis" happens 5x/month)
  3. Extract the common structure from successful completions (rating >= 4)
  4. Generate a custom Fabric pattern with the distilled approach
  5. Save to pai/patterns/custom/ (Mike reviews before Fabric install)

Examples:
  jake_competitive_brief — Mike's preferred competitive analysis format
  jake_decision_frame — How Mike likes decisions structured
  jake_meeting_summary — Meeting summary in Mike's preferred format
"""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class DetectedPattern:
    """A recurring interaction pattern detected from session data."""
    name: str                  # Pattern name (e.g., "jake_competitive_brief")
    description: str           # What this pattern does
    frequency: int             # How many times in the analysis window
    avg_rating: float          # Average satisfaction rating for this pattern
    trigger_phrases: list[str] = field(default_factory=list)
    common_structure: str = ""  # The distilled approach
    example_output: str = ""   # A good example of the pattern output
    status: str = "proposed"   # "proposed", "approved", "installed"
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "frequency": self.frequency,
            "avg_rating": self.avg_rating,
            "trigger_phrases": self.trigger_phrases,
            "status": self.status,
            "detected_at": self.detected_at.isoformat(),
        }


@dataclass
class FabricPattern:
    """A generated Fabric pattern ready for review."""
    name: str
    system_prompt: str
    user_prompt_template: str
    output_format: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_pattern_dir(self, base_dir: Path) -> Path:
        """Write the pattern to a Fabric-compatible directory structure."""
        pattern_dir = base_dir / self.name
        pattern_dir.mkdir(parents=True, exist_ok=True)

        (pattern_dir / "system.md").write_text(self.system_prompt)
        (pattern_dir / "user.md").write_text(self.user_prompt_template)

        meta = {
            "name": self.name,
            "output_format": self.output_format,
            **self.metadata,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "proposed",
        }
        (pattern_dir / "metadata.json").write_text(json.dumps(meta, indent=2))

        return pattern_dir


# Task type detection keywords
TASK_CATEGORIES = {
    "competitive_analysis": [
        "competitor", "competitive", "market analysis", "landscape",
        "vs", "versus", "compare", "benchmark",
    ],
    "decision_framing": [
        "should i", "should we", "decide", "decision", "pros and cons",
        "trade-off", "options", "worth it",
    ],
    "meeting_prep": [
        "meeting prep", "prepare for", "before the meeting",
        "attendees", "agenda",
    ],
    "code_review": [
        "review this", "code review", "pr review", "check this code",
    ],
    "email_draft": [
        "draft email", "write email", "reply to", "email to",
    ],
    "research_brief": [
        "research", "what do we know", "deep dive", "investigate",
        "find out about",
    ],
    "status_report": [
        "status", "progress", "update on", "how's",
    ],
}


class PatternGenerator:
    """Detect recurring patterns and generate Fabric custom patterns."""

    PATTERNS_DIR = Path(__file__).parent.parent / "patterns" / "custom"
    STATE_DIR = Path(__file__).parent.parent / "MEMORY" / "STATE"

    def __init__(self):
        self.PATTERNS_DIR.mkdir(parents=True, exist_ok=True)
        self.STATE_DIR.mkdir(parents=True, exist_ok=True)

    def detect_patterns(self, min_frequency: int = 3, min_rating: float = 3.5) -> list[DetectedPattern]:
        """Analyze recent interactions to find recurring high-quality patterns.

        Reads from ratings.jsonl and corrections.jsonl to find task types
        that Mike rates highly and requests frequently.
        """
        ratings_file = self.STATE_DIR / "ratings.jsonl"
        if not ratings_file.exists():
            return []

        # Read all rated interactions from last 30 days
        cutoff = datetime.now(timezone.utc).timestamp() - (30 * 86400)
        interactions = []
        with open(ratings_file) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    ts = datetime.fromisoformat(entry["timestamp"])
                    if ts.timestamp() > cutoff:
                        interactions.append(entry)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue

        if not interactions:
            return []

        # Classify each interaction
        classified: dict[str, list] = {}
        for interaction in interactions:
            msg = interaction.get("mike_message", "").lower()
            context = interaction.get("context", "").lower()
            text = f"{msg} {context}"

            for category, keywords in TASK_CATEGORIES.items():
                if any(kw in text for kw in keywords):
                    classified.setdefault(category, []).append(interaction)
                    break

        # Find patterns that meet thresholds
        patterns = []
        for category, items in classified.items():
            if len(items) < min_frequency:
                continue

            ratings = [i.get("rating", 3) for i in items]
            avg = sum(ratings) / len(ratings)
            if avg < min_rating:
                continue

            # Extract trigger phrases
            triggers = []
            for item in items:
                msg = item.get("mike_message", "")
                if msg:
                    triggers.append(msg[:80])

            patterns.append(DetectedPattern(
                name=f"jake_{category}",
                description=f"Auto-detected pattern: {category.replace('_', ' ')} "
                            f"({len(items)} occurrences, avg rating {avg:.1f})",
                frequency=len(items),
                avg_rating=round(avg, 2),
                trigger_phrases=triggers[:5],
            ))

        # Persist detected patterns
        self._persist_detections(patterns)
        return patterns

    def generate_pattern(self, detected: DetectedPattern) -> FabricPattern:
        """Generate a Fabric pattern from a detected pattern.

        This produces a skeleton pattern. The real power comes when
        augmented with LLM analysis of successful examples in V6+.
        """
        category = detected.name.replace("jake_", "")

        system_prompt = self._generate_system_prompt(category, detected)
        user_prompt = self._generate_user_prompt(category, detected)
        output_format = self._generate_output_format(category)

        pattern = FabricPattern(
            name=detected.name,
            system_prompt=system_prompt,
            user_prompt_template=user_prompt,
            output_format=output_format,
            metadata={
                "frequency": detected.frequency,
                "avg_rating": detected.avg_rating,
                "auto_generated": True,
            },
        )

        # Write to patterns directory for review
        pattern.to_pattern_dir(self.PATTERNS_DIR)
        return pattern

    def list_proposed(self) -> list[dict]:
        """List all proposed (not yet approved) patterns."""
        proposed = []
        for pattern_dir in self.PATTERNS_DIR.iterdir():
            if not pattern_dir.is_dir():
                continue
            meta_file = pattern_dir / "metadata.json"
            if meta_file.exists():
                try:
                    meta = json.loads(meta_file.read_text())
                    if meta.get("status") == "proposed":
                        proposed.append(meta)
                except (json.JSONDecodeError, OSError):
                    continue
        return proposed

    def approve_pattern(self, pattern_name: str) -> bool:
        """Mark a pattern as approved (ready for Fabric install)."""
        meta_file = self.PATTERNS_DIR / pattern_name / "metadata.json"
        if not meta_file.exists():
            return False

        meta = json.loads(meta_file.read_text())
        meta["status"] = "approved"
        meta["approved_at"] = datetime.now(timezone.utc).isoformat()
        meta_file.write_text(json.dumps(meta, indent=2))
        return True

    def _generate_system_prompt(self, category: str, detected: DetectedPattern) -> str:
        """Generate a system prompt for a Fabric pattern."""
        prompts = {
            "competitive_analysis": (
                "You are a competitive intelligence analyst for a startup founder. "
                "Analyze the competitive landscape with precision. Lead with the "
                "single most important insight, then provide structured comparison. "
                "Include: market position, strengths/weaknesses, recent moves, "
                "and recommended response. Be direct, not diplomatic."
            ),
            "decision_framing": (
                "You are a decision architect. Frame every decision with: "
                "the real question (often different from the stated one), "
                "3-5 options (always including 'do nothing'), risk analysis, "
                "evidence from precedent, and a clear recommendation with "
                "confidence level and reversibility assessment."
            ),
            "meeting_prep": (
                "You are a meeting preparation specialist. For any upcoming meeting, "
                "provide: attendee context (roles, recent interactions), key topics "
                "to raise, questions to ask, desired outcomes, and potential risks. "
                "Keep it actionable and under 1 page."
            ),
            "research_brief": (
                "You are a research analyst producing concise intelligence briefs. "
                "Lead with the bottom line. Structure findings as: key insight, "
                "supporting evidence (3-5 points), implications for our work, "
                "and recommended next steps. Cite sources."
            ),
        }
        return prompts.get(category, (
            f"You are an AI assistant specialized in {category.replace('_', ' ')}. "
            f"This pattern was auto-generated from {detected.frequency} successful "
            f"interactions with an average satisfaction rating of {detected.avg_rating}/5."
        ))

    def _generate_user_prompt(self, category: str, detected: DetectedPattern) -> str:
        """Generate a user prompt template."""
        return f"Analyze the following and produce a structured {category.replace('_', ' ')} output:\n\n{{input}}"

    def _generate_output_format(self, category: str) -> str:
        """Define the expected output format."""
        formats = {
            "competitive_analysis": "markdown_structured",
            "decision_framing": "decision_brief",
            "meeting_prep": "meeting_brief",
            "research_brief": "intelligence_brief",
        }
        return formats.get(category, "markdown")

    def _persist_detections(self, patterns: list[DetectedPattern]):
        """Save detected patterns to state log."""
        log_file = self.STATE_DIR / "detected-patterns.jsonl"
        try:
            with open(log_file, "a") as f:
                for p in patterns:
                    f.write(json.dumps(p.to_dict()) + "\n")
        except OSError:
            pass
