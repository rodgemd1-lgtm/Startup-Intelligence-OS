"""Capability Self-Upgrade — V10 Full Autonomy

Jake proposes his own capability improvements based on:
  - Self-evaluation gaps (domains scoring below target)
  - Failure patterns (recurring failure types)
  - User feedback trends (declining satisfaction in specific areas)
  - Cross-domain synergies (capabilities proven in other companies)

All proposals require Mike's APPROVE.
Target: Mike's daily interaction <15 min, 90%+ automation.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class UpgradeProposal:
    """A self-proposed capability upgrade."""
    title: str
    domain: str  # Which PAI maturity domain this improves
    current_state: str
    proposed_change: str
    expected_impact: str
    effort: str = "medium"  # low, medium, high
    priority: int = 2  # 1-5, 1 being highest
    evidence: list[str] = field(default_factory=list)
    implementation_steps: list[str] = field(default_factory=list)
    status: str = "proposed"  # "proposed", "approved", "in_progress", "completed"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "domain": self.domain,
            "current_state": self.current_state,
            "proposed_change": self.proposed_change,
            "expected_impact": self.expected_impact,
            "effort": self.effort,
            "priority": self.priority,
            "evidence": self.evidence[:5],
            "implementation_steps": self.implementation_steps,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }

    def to_markdown(self) -> str:
        lines = [
            f"## {self.title}",
            f"**Domain:** {self.domain}",
            f"**Priority:** {self.priority}/5 | **Effort:** {self.effort}",
            f"**Status:** {self.status}",
            "",
            f"**Current state:** {self.current_state}",
            f"**Proposed change:** {self.proposed_change}",
            f"**Expected impact:** {self.expected_impact}",
            "",
        ]
        if self.evidence:
            lines.append("**Evidence:**")
            for ev in self.evidence:
                lines.append(f"  - {ev}")
            lines.append("")
        if self.implementation_steps:
            lines.append("**Steps:**")
            for i, step in enumerate(self.implementation_steps, 1):
                lines.append(f"  {i}. {step}")
        return "\n".join(lines)


@dataclass
class AutomationMetrics:
    """Track automation level — target: 90%+ of routine ops automated."""
    total_routine_ops: int = 0
    automated_ops: int = 0
    daily_mike_minutes: float = 0  # Target: <15 min

    @property
    def automation_rate(self) -> float:
        if self.total_routine_ops == 0:
            return 0
        return self.automated_ops / self.total_routine_ops

    def to_dict(self) -> dict:
        return {
            "total_routine_ops": self.total_routine_ops,
            "automated_ops": self.automated_ops,
            "automation_rate": round(self.automation_rate, 3),
            "daily_mike_minutes": self.daily_mike_minutes,
        }


class CapabilityUpgrade:
    """Jake proposes his own capability improvements."""

    WISDOM_DIR = Path(__file__).parent.parent / "MEMORY" / "WISDOM"
    STATE_DIR = Path(__file__).parent.parent / "MEMORY" / "STATE"

    def __init__(self):
        self.STATE_DIR.mkdir(parents=True, exist_ok=True)

    def generate_proposals(self) -> list[UpgradeProposal]:
        """Analyze system state and generate upgrade proposals."""
        proposals = []

        # From self-evaluation gaps
        proposals.extend(self._proposals_from_evaluation())

        # From failure patterns
        proposals.extend(self._proposals_from_failures())

        # From rating trends
        proposals.extend(self._proposals_from_ratings())

        # Prioritize
        proposals.sort(key=lambda p: p.priority)

        self._persist_proposals(proposals)
        return proposals

    def measure_automation(self) -> AutomationMetrics:
        """Measure current automation level."""
        # Count routine ops from pipeline logs
        pipelines = ["morning_brief", "email_triage", "scout_scan",
                      "consolidation", "weekly_synthesis"]

        automated = 0
        for p in pipelines:
            # Check if pipeline has run in last 7 days
            # (simplified — real implementation checks cron logs)
            automated += 1

        total = len(pipelines) + 5  # +5 for manual tasks still remaining

        return AutomationMetrics(
            total_routine_ops=total,
            automated_ops=automated,
            daily_mike_minutes=30,  # Will be measured from interaction logs
        )

    def upgrade_report(self) -> str:
        """Generate a formatted upgrade report."""
        proposals = self.generate_proposals()
        metrics = self.measure_automation()

        lines = [
            "# Capability Self-Upgrade Report",
            "",
            f"**Automation rate:** {metrics.automation_rate:.0%} "
            f"(target: 90%)",
            f"**Daily Mike time:** {metrics.daily_mike_minutes:.0f} min "
            f"(target: <15 min)",
            "",
            f"## Proposals ({len(proposals)})",
            "",
        ]

        for p in proposals[:10]:
            lines.append(p.to_markdown())
            lines.append("")

        return "\n".join(lines)

    def _proposals_from_evaluation(self) -> list[UpgradeProposal]:
        """Generate proposals from self-evaluation gaps."""
        proposals = []

        # Load latest evaluation
        eval_files = sorted(self.WISDOM_DIR.glob("evaluation-*.json"))
        if not eval_files:
            return proposals

        try:
            latest = json.loads(eval_files[-1].read_text())
        except (json.JSONDecodeError, OSError):
            return proposals

        for domain_data in latest.get("domains", []):
            score = domain_data.get("score", 0)
            target = domain_data.get("target", 0)
            gap = domain_data.get("gap", "")

            if score < target and gap:
                proposals.append(UpgradeProposal(
                    title=f"Close gap in {domain_data['domain']}",
                    domain=domain_data["domain"],
                    current_state=f"Score: {score}/10 (target: {target})",
                    proposed_change=gap,
                    expected_impact=f"+{target - score} points in {domain_data['domain']}",
                    priority=max(1, 5 - (target - score)),
                    evidence=[f"Self-evaluation: {score}/{target}"],
                ))

        return proposals

    def _proposals_from_failures(self) -> list[UpgradeProposal]:
        """Generate proposals from recurring failure patterns."""
        failures_file = self.STATE_DIR / "failures.jsonl"
        if not failures_file.exists():
            return []

        # Count failure types in last 30 days
        cutoff = datetime.now(timezone.utc).timestamp() - (30 * 86400)
        counts: dict[str, int] = {}
        with open(failures_file) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    ts = datetime.fromisoformat(entry.get("timestamp", "2000-01-01"))
                    if ts.timestamp() > cutoff:
                        ft = entry.get("failure_type", "unknown")
                        counts[ft] = counts.get(ft, 0) + 1
                except (json.JSONDecodeError, ValueError):
                    continue

        proposals = []
        for ftype, count in counts.items():
            if count >= 3:
                proposals.append(UpgradeProposal(
                    title=f"Fix recurring {ftype} failures",
                    domain="Reliability & Error Recovery",
                    current_state=f"{count} {ftype} failures in last 30 days",
                    proposed_change=f"Add prevention/recovery for {ftype}",
                    expected_impact=f"Eliminate {count} monthly failures",
                    priority=2 if count >= 5 else 3,
                    evidence=[f"{count} occurrences in 30 days"],
                ))

        return proposals

    def _proposals_from_ratings(self) -> list[UpgradeProposal]:
        """Generate proposals from declining satisfaction."""
        ratings_file = self.STATE_DIR / "ratings.jsonl"
        if not ratings_file.exists():
            return []

        cutoff = datetime.now(timezone.utc).timestamp() - (7 * 86400)
        recent = []
        with open(ratings_file) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    ts = datetime.fromisoformat(entry.get("timestamp", "2000-01-01"))
                    if ts.timestamp() > cutoff:
                        recent.append(entry)
                except (json.JSONDecodeError, ValueError):
                    continue

        if len(recent) < 5:
            return []

        avg = sum(r.get("rating", 3) for r in recent) / len(recent)
        if avg < 3.5:
            return [UpgradeProposal(
                title="Improve response quality — declining satisfaction",
                domain="Communication Quality",
                current_state=f"Average rating: {avg:.1f}/5 (last 7 days)",
                proposed_change="Review recent low-rated interactions and extract improvement patterns",
                expected_impact="Raise satisfaction above 4.0/5",
                priority=1,
                evidence=[f"{len(recent)} ratings, avg {avg:.1f}"],
            )]

        return []

    def _persist_proposals(self, proposals: list[UpgradeProposal]):
        log_file = self.STATE_DIR / "upgrade-proposals.jsonl"
        try:
            with open(log_file, "a") as f:
                for p in proposals:
                    f.write(json.dumps(p.to_dict()) + "\n")
        except OSError:
            pass
