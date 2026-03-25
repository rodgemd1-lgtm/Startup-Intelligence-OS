"""Weekly Learning Synthesis — V5 Learning Engine

Every Sunday, synthesize all learning from the past week into actionable patterns.

Pipeline:
  1. Read all LEARNING files from past 7 days
  2. Read all corrections
  3. Read all failures
  4. Read ratings distribution
  5. Generate synthesis report with patterns, rules, and proposed updates
  6. Write to WISDOM/synthesis-YYYY-WNN.md
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class WeeklySynthesis:
    """Synthesize learning from the past week."""

    MEMORY_DIR = Path(__file__).parent.parent / "MEMORY"
    STATE_DIR = MEMORY_DIR / "STATE"
    WISDOM_DIR = MEMORY_DIR / "WISDOM"
    LEARNING_DIR = MEMORY_DIR / "LEARNING"

    def __init__(self):
        self.WISDOM_DIR.mkdir(parents=True, exist_ok=True)

    def run(self) -> str:
        """Run the full weekly synthesis. Returns the report as markdown."""
        now = datetime.now(timezone.utc)
        week = now.strftime("%Y-W%V")

        # Collect data
        ratings = self._read_ratings(days=7)
        corrections = self._read_corrections(days=7)
        failures = self._read_failures(days=7)

        # Analyze
        rating_stats = self._analyze_ratings(ratings)
        correction_rules = self._extract_rules(corrections)
        failure_patterns = self._analyze_failures(failures)

        # Generate report
        report = self._generate_report(
            week=week,
            rating_stats=rating_stats,
            correction_rules=correction_rules,
            failure_patterns=failure_patterns,
            corrections=corrections,
            failures=failures,
        )

        # Persist
        output_file = self.WISDOM_DIR / f"synthesis-{week}.md"
        try:
            output_file.write_text(report)
        except OSError:
            pass

        return report

    def _analyze_ratings(self, ratings: list[dict]) -> dict:
        """Compute rating statistics."""
        if not ratings:
            return {"count": 0, "average": 0, "trend": "no_data"}

        scores = [r.get("rating", 3) for r in ratings]
        avg = sum(scores) / len(scores)

        # Week-over-week trend
        prev_ratings = self._read_ratings(days=14)
        prev_only = [r for r in prev_ratings if r not in ratings]
        if prev_only:
            prev_avg = sum(r.get("rating", 3) for r in prev_only) / len(prev_only)
            if avg > prev_avg + 0.2:
                trend = "improving"
            elif avg < prev_avg - 0.2:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "first_week"

        return {
            "count": len(scores),
            "average": round(avg, 2),
            "trend": trend,
            "positive": sum(1 for s in scores if s >= 4),
            "negative": sum(1 for s in scores if s <= 2),
        }

    def _extract_rules(self, corrections: list[dict]) -> list[str]:
        """Extract unique rules from corrections."""
        rules = set()
        for c in corrections:
            rule = c.get("rule_extracted", "")
            if rule and rule != "(see context)":
                rules.add(rule)
        return sorted(rules)

    def _analyze_failures(self, failures: list[dict]) -> dict[str, int]:
        """Count failures by type."""
        counts: dict[str, int] = {}
        for f in failures:
            ft = f.get("failure_type", "unknown")
            counts[ft] = counts.get(ft, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    def _generate_report(
        self,
        week: str,
        rating_stats: dict,
        correction_rules: list[str],
        failure_patterns: dict[str, int],
        corrections: list[dict],
        failures: list[dict],
    ) -> str:
        """Generate the weekly synthesis markdown report."""
        sections = [
            f"# Weekly Learning Synthesis — {week}",
            f"*Generated: {datetime.now(timezone.utc).isoformat()}*",
            "",
        ]

        # Satisfaction
        sections.append("## Satisfaction")
        sections.append(f"- Signals: {rating_stats.get('count', 0)}")
        sections.append(f"- Average: {rating_stats.get('average', 0)}/5")
        sections.append(f"- Trend: {rating_stats.get('trend', 'unknown')}")
        sections.append(f"- Positive (4-5): {rating_stats.get('positive', 0)}")
        sections.append(f"- Negative (1-2): {rating_stats.get('negative', 0)}")
        sections.append("")

        # Corrections → Rules
        sections.append(f"## Corrections ({len(corrections)} this week)")
        if correction_rules:
            sections.append("### Rules to add/update:")
            for rule in correction_rules:
                sections.append(f"  - {rule}")
        else:
            sections.append("  No new correction rules this week.")
        sections.append("")

        # Failures
        sections.append(f"## Failures ({len(failures)} this week)")
        if failure_patterns:
            for ftype, count in failure_patterns.items():
                sections.append(f"  - {ftype}: {count}")
        else:
            sections.append("  No failures this week.")
        sections.append("")

        # Patterns detected
        sections.append("## Patterns Detected")
        if rating_stats.get("trend") == "declining":
            sections.append("  - WARNING: Satisfaction trend is declining. Review recent interactions.")
        if failure_patterns.get("tool_error", 0) >= 3:
            sections.append("  - PATTERN: Repeated tool errors — check MCP tool availability.")
        if failure_patterns.get("hallucination", 0) >= 2:
            sections.append("  - PATTERN: Hallucination detected — increase RAG retrieval before answering.")
        if len(correction_rules) >= 3:
            sections.append(f"  - PATTERN: {len(correction_rules)} new rules — consider updating TELOS.")
        if not any([
            rating_stats.get("trend") == "declining",
            failure_patterns.get("tool_error", 0) >= 3,
            len(correction_rules) >= 3,
        ]):
            sections.append("  No significant patterns detected.")
        sections.append("")

        # Proposed actions
        sections.append("## Proposed Actions")
        actions = []
        if correction_rules:
            actions.append("- [ ] Review and approve new LEARNED.md rules")
        if failure_patterns:
            actions.append("- [ ] Investigate top failure type and add prevention")
        if rating_stats.get("trend") == "declining":
            actions.append("- [ ] Review declining satisfaction — identify root cause")
        if not actions:
            actions.append("- No actions needed — system performing well")
        sections.extend(actions)
        sections.append("")

        return "\n".join(sections)

    def _read_ratings(self, days: int = 7) -> list[dict]:
        return self._read_jsonl(self.STATE_DIR / "ratings.jsonl", days)

    def _read_corrections(self, days: int = 7) -> list[dict]:
        return self._read_jsonl(self.STATE_DIR / "corrections.jsonl", days)

    def _read_failures(self, days: int = 7) -> list[dict]:
        return self._read_jsonl(self.STATE_DIR / "failures.jsonl", days)

    def _read_jsonl(self, path: Path, days: int) -> list[dict]:
        if not path.exists():
            return []
        cutoff = datetime.now(timezone.utc).timestamp() - (days * 86400)
        entries = []
        with open(path) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    ts = datetime.fromisoformat(entry.get("timestamp", "2000-01-01"))
                    if ts.timestamp() > cutoff:
                        entries.append(entry)
                except (json.JSONDecodeError, ValueError):
                    continue
        return entries
