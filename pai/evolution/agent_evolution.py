"""Agent Evolution Engine — V10 Full Autonomy

Automatically proposes new agents, retires unused agents, and optimizes
agent configurations based on usage patterns.

Evolution triggers:
  New agent proposed     — recurring task type with no dedicated agent
  Agent retirement       — not invoked in 60+ days with viable alternative
  Agent optimization     — success rate <70% → analyze failures → propose changes
  Agent specialization   — general agent handling too many task types → split

All proposals require Mike's APPROVE before activation.
Retired agents are archived, not deleted (reversible).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any


@dataclass
class EvolutionProposal:
    """A proposed change to the agent roster."""
    proposal_type: str  # "new_agent", "retire", "optimize", "specialize"
    agent_name: str
    reason: str
    evidence: list[str] = field(default_factory=list)
    impact: str = "medium"
    reversible: bool = True
    status: str = "proposed"  # "proposed", "approved", "rejected", "implemented"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "proposal_type": self.proposal_type,
            "agent_name": self.agent_name,
            "reason": self.reason,
            "evidence": self.evidence[:5],
            "impact": self.impact,
            "reversible": self.reversible,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class AgentUsageStats:
    """Usage statistics for a single agent."""
    name: str
    invocation_count_30d: int = 0
    invocation_count_90d: int = 0
    success_rate: float = 0
    avg_rating: float = 0
    last_invoked: datetime | None = None
    task_types: list[str] = field(default_factory=list)


class AgentEvolution:
    """Self-evolving agent roster management."""

    INTELLIGENCE_LOGS = Path(__file__).parent.parent / "intelligence" / "logs"
    STATE_DIR = Path(__file__).parent.parent / "MEMORY" / "STATE"
    ARCHIVE_DIR = Path(__file__).parent / "archive"

    RETIREMENT_THRESHOLD_DAYS = 60
    LOW_SUCCESS_THRESHOLD = 0.7
    SPECIALIZATION_TASK_THRESHOLD = 5  # Agent handling 5+ task types → specialize

    def __init__(self):
        self.ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    def analyze(self) -> list[EvolutionProposal]:
        """Run full evolution analysis. Returns proposals."""
        proposals = []

        usage = self._get_usage_stats()

        # Check for retirement candidates
        proposals.extend(self._detect_retirements(usage))

        # Check for optimization candidates
        proposals.extend(self._detect_optimizations(usage))

        # Check for new agent opportunities
        proposals.extend(self._detect_new_agents())

        # Check for specialization candidates
        proposals.extend(self._detect_specializations(usage))

        self._persist_proposals(proposals)
        return proposals

    def approve(self, agent_name: str) -> bool:
        """Approve a proposal for an agent."""
        log_file = self.STATE_DIR / "evolution-proposals.jsonl"
        if not log_file.exists():
            return False

        # Read all proposals, update the matching one
        entries = []
        found = False
        with open(log_file) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("agent_name") == agent_name and entry.get("status") == "proposed":
                        entry["status"] = "approved"
                        found = True
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue

        if found:
            with open(log_file, "w") as f:
                for entry in entries:
                    f.write(json.dumps(entry) + "\n")
        return found

    def evolution_report(self) -> str:
        """Generate a formatted evolution report."""
        proposals = self.analyze()
        if not proposals:
            return "No agent evolution proposals at this time."

        lines = ["# Agent Evolution Report", ""]

        for p in proposals:
            lines.append(f"## [{p.proposal_type}] {p.agent_name}")
            lines.append(f"**Reason:** {p.reason}")
            lines.append(f"**Impact:** {p.impact} | **Reversible:** {p.reversible}")
            if p.evidence:
                lines.append("**Evidence:**")
                for ev in p.evidence:
                    lines.append(f"  - {ev}")
            lines.append("")

        return "\n".join(lines)

    def _get_usage_stats(self) -> dict[str, AgentUsageStats]:
        """Compute usage stats per agent from intent router logs."""
        stats: dict[str, AgentUsageStats] = {}

        log_file = self.INTELLIGENCE_LOGS / "intent-classifications.jsonl"
        if not log_file.exists():
            return stats

        now = datetime.now(timezone.utc)
        cutoff_30d = now.timestamp() - (30 * 86400)
        cutoff_90d = now.timestamp() - (90 * 86400)

        with open(log_file) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    agent = entry.get("agent")
                    if not agent:
                        continue

                    if agent not in stats:
                        stats[agent] = AgentUsageStats(name=agent)

                    ts = datetime.fromisoformat(entry.get("ts", "2000-01-01"))

                    if ts.timestamp() > cutoff_30d:
                        stats[agent].invocation_count_30d += 1
                    if ts.timestamp() > cutoff_90d:
                        stats[agent].invocation_count_90d += 1

                    stats[agent].last_invoked = ts
                    intent = entry.get("intent", "")
                    if intent and intent not in stats[agent].task_types:
                        stats[agent].task_types.append(intent)

                except (json.JSONDecodeError, ValueError):
                    continue

        return stats

    def _detect_retirements(self, usage: dict[str, AgentUsageStats]) -> list[EvolutionProposal]:
        """Find agents that should be retired (unused for 60+ days)."""
        proposals = []
        now = datetime.now(timezone.utc)

        for name, stats in usage.items():
            if stats.last_invoked:
                days_since = (now - stats.last_invoked).days
                if days_since >= self.RETIREMENT_THRESHOLD_DAYS:
                    proposals.append(EvolutionProposal(
                        proposal_type="retire",
                        agent_name=name,
                        reason=f"Not invoked in {days_since} days",
                        evidence=[
                            f"Last invoked: {stats.last_invoked.isoformat()}",
                            f"30-day count: {stats.invocation_count_30d}",
                            f"90-day count: {stats.invocation_count_90d}",
                        ],
                        impact="low",
                    ))

        return proposals

    def _detect_optimizations(self, usage: dict[str, AgentUsageStats]) -> list[EvolutionProposal]:
        """Find agents with low success rate that need optimization."""
        proposals = []

        for name, stats in usage.items():
            if stats.success_rate > 0 and stats.success_rate < self.LOW_SUCCESS_THRESHOLD:
                proposals.append(EvolutionProposal(
                    proposal_type="optimize",
                    agent_name=name,
                    reason=f"Success rate {stats.success_rate:.0%} below threshold ({self.LOW_SUCCESS_THRESHOLD:.0%})",
                    evidence=[
                        f"Success rate: {stats.success_rate:.0%}",
                        f"Avg rating: {stats.avg_rating:.1f}",
                        f"Invocations (30d): {stats.invocation_count_30d}",
                    ],
                    impact="medium",
                ))

        return proposals

    def _detect_new_agents(self) -> list[EvolutionProposal]:
        """Find task types that don't have dedicated agents."""
        # Read detected patterns from learning engine
        patterns_file = self.STATE_DIR / "detected-patterns.jsonl"
        if not patterns_file.exists():
            return []

        proposals = []
        with open(patterns_file) as f:
            for line in f:
                try:
                    pattern = json.loads(line)
                    if pattern.get("frequency", 0) >= 5 and pattern.get("avg_rating", 0) >= 4.0:
                        proposals.append(EvolutionProposal(
                            proposal_type="new_agent",
                            agent_name=pattern.get("name", "unknown"),
                            reason=f"Recurring pattern '{pattern['name']}' has no dedicated agent "
                                   f"({pattern['frequency']} occurrences, {pattern.get('avg_rating', 0):.1f} rating)",
                            evidence=[
                                f"Frequency: {pattern['frequency']}/month",
                                f"Avg rating: {pattern.get('avg_rating', 0):.1f}",
                            ],
                            impact="medium",
                        ))
                except (json.JSONDecodeError, KeyError):
                    continue

        return proposals

    def _detect_specializations(self, usage: dict[str, AgentUsageStats]) -> list[EvolutionProposal]:
        """Find agents handling too many task types."""
        proposals = []

        for name, stats in usage.items():
            if len(stats.task_types) >= self.SPECIALIZATION_TASK_THRESHOLD:
                proposals.append(EvolutionProposal(
                    proposal_type="specialize",
                    agent_name=name,
                    reason=f"Handling {len(stats.task_types)} task types — consider splitting into specialists",
                    evidence=[
                        f"Task types: {', '.join(stats.task_types[:5])}",
                        f"Total invocations (30d): {stats.invocation_count_30d}",
                    ],
                    impact="medium",
                ))

        return proposals

    def _persist_proposals(self, proposals: list[EvolutionProposal]):
        log_file = self.STATE_DIR / "evolution-proposals.jsonl"
        self.STATE_DIR.mkdir(parents=True, exist_ok=True)
        try:
            with open(log_file, "a") as f:
                for p in proposals:
                    f.write(json.dumps(p.to_dict()) + "\n")
        except OSError:
            pass
