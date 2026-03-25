"""Self-Evaluation Cycle — V5 Learning Engine

Monthly self-evaluation against the PAI maturity scorecard.

Domains (1-10 scale):
  1. Memory & Context — Search accuracy, recall quality
  2. Autonomous Execution — Pipeline success rate, task completion
  3. Multi-System Integration — MCP availability, agent success rate
  4. Proactive Intelligence — Jordan Voss test pass rate
  5. Personal Context Depth — TELOS completeness, entity accuracy
  6. Communication Quality — Rating average, correction frequency
  7. Multi-Agent Orchestration — Agent invocation success, routing accuracy
  8. Learning & Self-Improvement — Patterns generated, consolidation runs
  9. Reliability & Error Recovery — Uptime, self-repair success rate
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class DomainScore:
    """Score for a single evaluation domain."""
    domain: str
    score: int  # 1-10
    target: int  # Target score for current version
    evidence: list[str] = field(default_factory=list)
    gap: str = ""  # What needs improvement
    previous_score: int | None = None  # Last month's score

    @property
    def delta(self) -> int | None:
        if self.previous_score is not None:
            return self.score - self.previous_score
        return None

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "score": self.score,
            "target": self.target,
            "delta": self.delta,
            "evidence": self.evidence[:5],
            "gap": self.gap,
        }


@dataclass
class EvaluationReport:
    """Monthly self-evaluation report."""
    month: str  # YYYY-MM
    domains: list[DomainScore] = field(default_factory=list)
    overall_score: float = 0.0
    overall_target: float = 0.0
    action_items: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_markdown(self) -> str:
        lines = [
            f"# PAI Self-Evaluation — {self.month}",
            f"*Generated: {self.timestamp.isoformat()}*",
            "",
            f"**Overall Score: {self.overall_score:.1f}/10** (target: {self.overall_target:.1f})",
            "",
            "## Domain Scores",
            "",
            "| Domain | Score | Target | Delta | Gap |",
            "|--------|-------|--------|-------|-----|",
        ]

        for d in self.domains:
            delta_str = f"+{d.delta}" if d.delta and d.delta > 0 else str(d.delta or "—")
            lines.append(
                f"| {d.domain} | {d.score}/10 | {d.target}/10 | {delta_str} | {d.gap[:50]} |"
            )

        lines.append("")

        # Evidence details
        lines.append("## Evidence")
        for d in self.domains:
            if d.evidence:
                lines.append(f"\n### {d.domain} ({d.score}/10)")
                for ev in d.evidence[:3]:
                    lines.append(f"  - {ev}")

        # Action items
        if self.action_items:
            lines.append("\n## Action Items")
            for item in self.action_items:
                lines.append(f"  - [ ] {item}")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "month": self.month,
            "overall_score": self.overall_score,
            "overall_target": self.overall_target,
            "domains": [d.to_dict() for d in self.domains],
            "action_items": self.action_items,
            "timestamp": self.timestamp.isoformat(),
        }


# V5 target scores
V5_TARGETS = {
    "Memory & Context": 8,
    "Autonomous Execution": 7,
    "Multi-System Integration": 7,
    "Proactive Intelligence": 8,
    "Personal Context Depth": 8,
    "Communication Quality": 8,
    "Multi-Agent Orchestration": 6,
    "Learning & Self-Improvement": 7,
    "Reliability & Error Recovery": 7,
}


class SelfEvaluation:
    """Monthly self-evaluation against the PAI maturity scorecard."""

    MEMORY_DIR = Path(__file__).parent.parent / "MEMORY"
    STATE_DIR = MEMORY_DIR / "STATE"
    WISDOM_DIR = MEMORY_DIR / "WISDOM"

    def __init__(self):
        self.WISDOM_DIR.mkdir(parents=True, exist_ok=True)

    def evaluate(self) -> EvaluationReport:
        """Run the full self-evaluation."""
        month = datetime.now(timezone.utc).strftime("%Y-%m")

        # Load previous evaluation for delta tracking
        previous = self._load_previous()

        # Score each domain
        domains = [
            self._score_memory_context(previous),
            self._score_autonomous_execution(previous),
            self._score_multi_system(previous),
            self._score_proactive_intelligence(previous),
            self._score_personal_context(previous),
            self._score_communication_quality(previous),
            self._score_multi_agent(previous),
            self._score_learning(previous),
            self._score_reliability(previous),
        ]

        overall = sum(d.score for d in domains) / len(domains)
        overall_target = sum(d.target for d in domains) / len(domains)

        # Generate action items for lowest-scoring domains
        sorted_domains = sorted(domains, key=lambda d: d.score)
        actions = []
        for d in sorted_domains[:3]:
            if d.score < d.target:
                actions.append(f"Improve {d.domain}: {d.gap}")

        report = EvaluationReport(
            month=month,
            domains=domains,
            overall_score=round(overall, 1),
            overall_target=round(overall_target, 1),
            action_items=actions,
        )

        self._persist(report)
        return report

    def _score_memory_context(self, previous: dict | None) -> DomainScore:
        """Score Memory & Context domain."""
        evidence = []

        # Check if consolidation is running
        consolidation_log = self.STATE_DIR / "consolidation.jsonl"
        if consolidation_log.exists():
            entries = self._read_jsonl(consolidation_log, days=30)
            evidence.append(f"{len(entries)} consolidation runs in last 30 days")
            score = min(10, 5 + len(entries) // 3)
        else:
            evidence.append("No consolidation runs found")
            score = 4

        return DomainScore(
            domain="Memory & Context",
            score=score,
            target=V5_TARGETS["Memory & Context"],
            evidence=evidence,
            gap="Need consistent nightly consolidation" if score < 8 else "",
            previous_score=self._get_prev_score(previous, "Memory & Context"),
        )

    def _score_autonomous_execution(self, previous: dict | None) -> DomainScore:
        """Score Autonomous Execution domain."""
        evidence = []
        failures = self._read_jsonl(self.STATE_DIR / "failures.jsonl", days=30)
        pipeline_failures = [f for f in failures if f.get("failure_type") == "pipeline"]

        evidence.append(f"{len(pipeline_failures)} pipeline failures in last 30 days")

        if len(pipeline_failures) == 0:
            score = 9
        elif len(pipeline_failures) <= 3:
            score = 7
        elif len(pipeline_failures) <= 10:
            score = 5
        else:
            score = 3

        return DomainScore(
            domain="Autonomous Execution",
            score=score,
            target=V5_TARGETS["Autonomous Execution"],
            evidence=evidence,
            gap=f"Reduce pipeline failures (currently {len(pipeline_failures)}/month)" if score < 7 else "",
            previous_score=self._get_prev_score(previous, "Autonomous Execution"),
        )

    def _score_multi_system(self, previous: dict | None) -> DomainScore:
        """Score Multi-System Integration."""
        evidence = []
        tool_errors = self._read_jsonl(self.STATE_DIR / "failures.jsonl", days=30)
        tool_failures = [f for f in tool_errors if f.get("failure_type") == "tool_error"]

        evidence.append(f"{len(tool_failures)} tool errors in last 30 days")
        score = max(3, min(10, 9 - len(tool_failures)))

        return DomainScore(
            domain="Multi-System Integration",
            score=score,
            target=V5_TARGETS["Multi-System Integration"],
            evidence=evidence,
            gap="Check MCP tool availability" if score < 7 else "",
            previous_score=self._get_prev_score(previous, "Multi-System Integration"),
        )

    def _score_proactive_intelligence(self, previous: dict | None) -> DomainScore:
        """Score Proactive Intelligence (V4)."""
        evidence = []
        priority_log = Path(__file__).parent.parent / "intelligence" / "logs" / "priority-engine.jsonl"

        if priority_log.exists():
            entries = self._read_jsonl(priority_log, days=30)
            evidence.append(f"{len(entries)} priority calculations in last 30 days")
            score = min(10, 5 + len(entries) // 5)
        else:
            evidence.append("Priority engine not yet running")
            score = 4

        return DomainScore(
            domain="Proactive Intelligence",
            score=score,
            target=V5_TARGETS["Proactive Intelligence"],
            evidence=evidence,
            gap="Need daily priority engine runs" if score < 8 else "",
            previous_score=self._get_prev_score(previous, "Proactive Intelligence"),
        )

    def _score_personal_context(self, previous: dict | None) -> DomainScore:
        """Score Personal Context Depth."""
        evidence = []
        telos_dir = Path(__file__).parent.parent / "TELOS"

        if telos_dir.exists():
            files = list(telos_dir.glob("*.md"))
            evidence.append(f"{len(files)} TELOS files")
            score = min(10, 5 + len(files))
        else:
            evidence.append("TELOS directory not found")
            score = 3

        return DomainScore(
            domain="Personal Context Depth",
            score=score,
            target=V5_TARGETS["Personal Context Depth"],
            evidence=evidence,
            gap="Expand TELOS knowledge" if score < 8 else "",
            previous_score=self._get_prev_score(previous, "Personal Context Depth"),
        )

    def _score_communication_quality(self, previous: dict | None) -> DomainScore:
        """Score Communication Quality."""
        ratings = self._read_jsonl(self.STATE_DIR / "ratings.jsonl", days=30)
        evidence = []

        if ratings:
            scores = [r.get("rating", 3) for r in ratings]
            avg = sum(scores) / len(scores)
            evidence.append(f"Average rating: {avg:.1f}/5 ({len(scores)} signals)")
            score = min(10, int(avg * 2))
        else:
            evidence.append("No ratings data yet")
            score = 5

        corrections = self._read_jsonl(self.STATE_DIR / "corrections.jsonl", days=30)
        evidence.append(f"{len(corrections)} corrections in last 30 days")
        if len(corrections) > 10:
            score = max(3, score - 2)

        return DomainScore(
            domain="Communication Quality",
            score=score,
            target=V5_TARGETS["Communication Quality"],
            evidence=evidence,
            gap="Reduce corrections and improve first-response quality" if score < 8 else "",
            previous_score=self._get_prev_score(previous, "Communication Quality"),
        )

    def _score_multi_agent(self, previous: dict | None) -> DomainScore:
        """Score Multi-Agent Orchestration."""
        evidence = []
        intent_log = Path(__file__).parent.parent / "intelligence" / "logs" / "intent-classifications.jsonl"

        if intent_log.exists():
            entries = self._read_jsonl(intent_log, days=30)
            routed = [e for e in entries if e.get("agent")]
            evidence.append(f"{len(routed)} agent-routed requests in last 30 days")
            score = min(10, 4 + len(routed) // 5)
        else:
            evidence.append("Intent router not yet logging")
            score = 4

        return DomainScore(
            domain="Multi-Agent Orchestration",
            score=score,
            target=V5_TARGETS["Multi-Agent Orchestration"],
            evidence=evidence,
            gap="Increase agent routing coverage" if score < 6 else "",
            previous_score=self._get_prev_score(previous, "Multi-Agent Orchestration"),
        )

    def _score_learning(self, previous: dict | None) -> DomainScore:
        """Score Learning & Self-Improvement."""
        evidence = []

        # Check for synthesis reports
        synthesis_files = list(self.WISDOM_DIR.glob("synthesis-*.md"))
        evidence.append(f"{len(synthesis_files)} weekly synthesis reports")

        # Check for detected patterns
        patterns_log = self.STATE_DIR / "detected-patterns.jsonl"
        if patterns_log.exists():
            patterns = self._read_jsonl(patterns_log, days=30)
            evidence.append(f"{len(patterns)} patterns detected in last 30 days")
        else:
            patterns = []

        score = min(10, 3 + len(synthesis_files) + len(patterns))

        return DomainScore(
            domain="Learning & Self-Improvement",
            score=score,
            target=V5_TARGETS["Learning & Self-Improvement"],
            evidence=evidence,
            gap="Need consistent weekly synthesis and pattern detection" if score < 7 else "",
            previous_score=self._get_prev_score(previous, "Learning & Self-Improvement"),
        )

    def _score_reliability(self, previous: dict | None) -> DomainScore:
        """Score Reliability & Error Recovery."""
        failures = self._read_jsonl(self.STATE_DIR / "failures.jsonl", days=30)
        evidence = [f"{len(failures)} total failures in last 30 days"]

        if len(failures) == 0:
            score = 9
        elif len(failures) <= 5:
            score = 7
        elif len(failures) <= 15:
            score = 5
        else:
            score = 3

        return DomainScore(
            domain="Reliability & Error Recovery",
            score=score,
            target=V5_TARGETS["Reliability & Error Recovery"],
            evidence=evidence,
            gap=f"Reduce overall failure count (currently {len(failures)}/month)" if score < 7 else "",
            previous_score=self._get_prev_score(previous, "Reliability & Error Recovery"),
        )

    def _load_previous(self) -> dict | None:
        """Load the most recent evaluation report."""
        eval_files = sorted(self.WISDOM_DIR.glob("evaluation-*.json"))
        if not eval_files:
            return None
        try:
            return json.loads(eval_files[-1].read_text())
        except (json.JSONDecodeError, OSError):
            return None

    def _get_prev_score(self, previous: dict | None, domain: str) -> int | None:
        if not previous:
            return None
        for d in previous.get("domains", []):
            if d.get("domain") == domain:
                return d.get("score")
        return None

    def _persist(self, report: EvaluationReport):
        """Save evaluation to markdown and JSON."""
        md_file = self.WISDOM_DIR / f"evaluation-{report.month}.md"
        json_file = self.WISDOM_DIR / f"evaluation-{report.month}.json"
        try:
            md_file.write_text(report.to_markdown())
            json_file.write_text(json.dumps(report.to_dict(), indent=2))
        except OSError:
            pass

    def _read_jsonl(self, path: Path, days: int) -> list[dict]:
        if not path.exists():
            return []
        cutoff = datetime.now(timezone.utc).timestamp() - (days * 86400)
        entries = []
        with open(path) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    ts_str = entry.get("timestamp", entry.get("ts", "2000-01-01"))
                    ts = datetime.fromisoformat(ts_str)
                    if ts.timestamp() > cutoff:
                        entries.append(entry)
                except (json.JSONDecodeError, ValueError):
                    continue
        return entries
