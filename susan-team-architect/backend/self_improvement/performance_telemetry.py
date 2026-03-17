"""Agent performance tracking and dashboard generation.

Collects performance records from run YAML files, aggregates by agent
and domain, computes trends, ranks agents, and produces formatted dashboards.
"""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from self_improvement.schemas import AgentPerformanceRecord, PerformanceDashboard


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_load_yaml(path: Path) -> dict | None:
    """Load a YAML file, returning None on any failure."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return None


def _parse_timestamp(ts: str) -> datetime | None:
    """Parse an ISO timestamp string to datetime."""
    fmt_patterns = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S.%f%z",
    ]
    for fmt in fmt_patterns:
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            continue
    return None


def _timestamp_delta_ms(ts_a: str, ts_b: str) -> int:
    """Compute millisecond delta between two ISO timestamps."""
    dt_a = _parse_timestamp(ts_a)
    dt_b = _parse_timestamp(ts_b)
    if dt_a and dt_b:
        delta = (dt_b - dt_a).total_seconds() * 1000
        return max(0, int(delta))
    return 0


def _estimate_tokens_from_data(data: Any) -> int:
    """Rough token estimate based on data payload size (~4 chars per token)."""
    try:
        text_len = len(str(data))
        return max(1, text_len // 4)
    except Exception:
        return 100


def _infer_agent_name(run_data: dict) -> str:
    """Infer the agent name from the run's trigger and mode."""
    trigger = run_data.get("trigger", "")
    mode = run_data.get("mode", "")

    # Try to extract from trigger prefix
    if ":" in trigger:
        prefix = trigger.split(":")[0]
        return prefix.replace("-", "_")

    return mode if mode else "unknown"


def _infer_task_type(run_data: dict) -> str:
    """Infer the task type from the run's mode and trigger."""
    mode = run_data.get("mode", "unknown")
    trigger = run_data.get("trigger", "")

    # Use trigger for more specific task types
    if "simulated-maturity" in trigger:
        return "simulated_maturity"
    if "debate" in trigger or "debate" in mode:
        return "debate"
    if "decision" in trigger or "decision" in mode:
        return "decision"
    if "simulation" in mode:
        return "simulation"
    if "foundry" in mode:
        return "foundry"

    return mode


def _compute_quality_score(run_data: dict) -> float | None:
    """Compute a quality score for the run based on available signals."""
    events = run_data.get("events", [])
    output = run_data.get("output", {})

    if not events:
        return None

    # Average confidence across events
    confidences = [e.get("confidence", 0.5) for e in events]
    avg_conf = sum(confidences) / len(confidences)

    # Output completeness
    output_score = 0.0
    if isinstance(output, dict):
        if output.get("recommendation"):
            output_score += 0.25
        if output.get("counter_recommendation"):
            output_score += 0.15
        if output.get("failure_modes"):
            output_score += 0.1
        if output.get("next_experiment"):
            output_score += 0.1

    # Evidence density
    unique_evidence: set[str] = set()
    for event in events:
        unique_evidence.update(event.get("evidence_ids", []))
    evidence_score = min(0.2, len(unique_evidence) * 0.04)

    quality = avg_conf * 0.5 + output_score + evidence_score
    return max(0.0, min(1.0, quality))


# ---------------------------------------------------------------------------
# PerformanceTelemetry
# ---------------------------------------------------------------------------

class PerformanceTelemetry:
    """Agent performance tracking and dashboard generation.

    Collects records from run YAML files, aggregates metrics, computes
    trends, and produces formatted performance dashboards.
    """

    def __init__(self, data_dir: Path) -> None:
        """Initialize with path to runs directory."""
        self._data_dir = data_dir
        # Support both direct runs dir and parent data dir
        if (data_dir / "runs").is_dir():
            self._runs_dir = data_dir / "runs"
        else:
            self._runs_dir = data_dir

    # ------------------------------------------------------------------
    # Collect records
    # ------------------------------------------------------------------

    def collect_records(self) -> list[AgentPerformanceRecord]:
        """Scan all run YAML files for agent performance data.

        Each run file produces one AgentPerformanceRecord with metrics
        derived from the run's events, output, and metadata.
        """
        records: list[AgentPerformanceRecord] = []

        if not self._runs_dir.exists():
            return records

        for yaml_file in sorted(self._runs_dir.glob("run-*.yaml")):
            run_data = _safe_load_yaml(yaml_file)
            if run_data is None:
                continue

            run_id = run_data.get("id", yaml_file.stem)
            agent_name = _infer_agent_name(run_data)
            task_type = _infer_task_type(run_data)

            # Compute duration from timestamps
            started = run_data.get("started_at", "")
            completed = run_data.get("completed_at", "")
            duration_ms = _timestamp_delta_ms(started, completed) if started and completed else 0

            # Estimate tokens from event data payloads
            events = run_data.get("events", [])
            total_tokens = sum(
                _estimate_tokens_from_data(e.get("data", {}))
                for e in events
            )
            # Also count output tokens
            output = run_data.get("output", {})
            if isinstance(output, dict):
                total_tokens += _estimate_tokens_from_data(output)

            success = run_data.get("status") == "completed"
            quality = _compute_quality_score(run_data)

            # Output reuse: whether artifacts were produced
            artifacts = run_data.get("artifacts_produced", [])
            output_reuse = bool(artifacts)

            timestamp = completed or started or _now_iso()

            records.append(AgentPerformanceRecord(
                agent_name=agent_name,
                run_id=run_id,
                task_type=task_type,
                tokens_used=total_tokens,
                duration_ms=duration_ms,
                success=success,
                quality_score=quality,
                user_satisfaction=None,
                output_reuse=output_reuse,
                timestamp=timestamp,
            ))

        return records

    # ------------------------------------------------------------------
    # Aggregate by agent
    # ------------------------------------------------------------------

    def aggregate_by_agent(
        self, records: list[AgentPerformanceRecord]
    ) -> dict[str, dict]:
        """Per-agent stats: avg quality, avg tokens, success rate, total runs."""
        agents: dict[str, dict[str, Any]] = defaultdict(lambda: {
            "total_runs": 0,
            "successes": 0,
            "total_tokens": 0,
            "total_duration_ms": 0,
            "quality_scores": [],
            "output_reuse_count": 0,
        })

        for r in records:
            a = agents[r.agent_name]
            a["total_runs"] += 1
            if r.success:
                a["successes"] += 1
            a["total_tokens"] += r.tokens_used
            a["total_duration_ms"] += r.duration_ms
            if r.quality_score is not None:
                a["quality_scores"].append(r.quality_score)
            if r.output_reuse:
                a["output_reuse_count"] += 1

        result: dict[str, dict] = {}
        for agent_name, a in agents.items():
            total = a["total_runs"]
            qs = a["quality_scores"]
            result[agent_name] = {
                "total_runs": total,
                "success_rate": a["successes"] / total if total > 0 else 0.0,
                "avg_tokens": a["total_tokens"] // total if total > 0 else 0,
                "avg_duration_ms": a["total_duration_ms"] // total if total > 0 else 0,
                "avg_quality": sum(qs) / len(qs) if qs else 0.0,
                "output_reuse_rate": a["output_reuse_count"] / total if total > 0 else 0.0,
            }

        return result

    # ------------------------------------------------------------------
    # Aggregate by domain
    # ------------------------------------------------------------------

    def aggregate_by_domain(
        self, records: list[AgentPerformanceRecord]
    ) -> dict[str, dict]:
        """Per-domain (task_type) stats: avg quality, avg tokens, success rate."""
        domains: dict[str, dict[str, Any]] = defaultdict(lambda: {
            "total_runs": 0,
            "successes": 0,
            "total_tokens": 0,
            "quality_scores": [],
            "agents_involved": set(),
        })

        for r in records:
            d = domains[r.task_type]
            d["total_runs"] += 1
            if r.success:
                d["successes"] += 1
            d["total_tokens"] += r.tokens_used
            if r.quality_score is not None:
                d["quality_scores"].append(r.quality_score)
            d["agents_involved"].add(r.agent_name)

        result: dict[str, dict] = {}
        for domain, d in domains.items():
            total = d["total_runs"]
            qs = d["quality_scores"]
            result[domain] = {
                "total_runs": total,
                "success_rate": d["successes"] / total if total > 0 else 0.0,
                "avg_tokens": d["total_tokens"] // total if total > 0 else 0,
                "avg_quality": sum(qs) / len(qs) if qs else 0.0,
                "agents_involved": sorted(d["agents_involved"]),
            }

        return result

    # ------------------------------------------------------------------
    # Compute trends
    # ------------------------------------------------------------------

    def compute_trends(
        self,
        records: list[AgentPerformanceRecord],
        window_days: int = 30,
    ) -> dict:
        """Compute whether performance is improving over a time window.

        Compares the most recent half of the window against the older half.
        Returns trend data including directional improvement indicator.
        """
        if not records:
            return {
                "window_days": window_days,
                "total_records": 0,
                "trend_direction": "insufficient_data",
                "quality_delta": 0.0,
                "token_delta": 0,
                "success_rate_delta": 0.0,
            }

        # Parse timestamps and sort
        timed_records: list[tuple[datetime, AgentPerformanceRecord]] = []
        for r in records:
            dt = _parse_timestamp(r.timestamp)
            if dt:
                timed_records.append((dt, r))

        if not timed_records:
            return {
                "window_days": window_days,
                "total_records": len(records),
                "trend_direction": "insufficient_data",
                "quality_delta": 0.0,
                "token_delta": 0,
                "success_rate_delta": 0.0,
            }

        timed_records.sort(key=lambda x: x[0])

        # Split into halves
        mid = len(timed_records) // 2
        if mid == 0:
            return {
                "window_days": window_days,
                "total_records": len(timed_records),
                "trend_direction": "insufficient_data",
                "quality_delta": 0.0,
                "token_delta": 0,
                "success_rate_delta": 0.0,
            }

        older_half = [r for _, r in timed_records[:mid]]
        newer_half = [r for _, r in timed_records[mid:]]

        def _avg_quality(recs: list[AgentPerformanceRecord]) -> float:
            scores = [r.quality_score for r in recs if r.quality_score is not None]
            return sum(scores) / len(scores) if scores else 0.0

        def _avg_tokens(recs: list[AgentPerformanceRecord]) -> int:
            if not recs:
                return 0
            return sum(r.tokens_used for r in recs) // len(recs)

        def _success_rate(recs: list[AgentPerformanceRecord]) -> float:
            if not recs:
                return 0.0
            return sum(1 for r in recs if r.success) / len(recs)

        old_quality = _avg_quality(older_half)
        new_quality = _avg_quality(newer_half)
        quality_delta = new_quality - old_quality

        old_tokens = _avg_tokens(older_half)
        new_tokens = _avg_tokens(newer_half)
        token_delta = new_tokens - old_tokens

        old_success = _success_rate(older_half)
        new_success = _success_rate(newer_half)
        success_delta = new_success - old_success

        # Determine overall trend direction
        improving_signals = 0
        if quality_delta > 0.02:
            improving_signals += 1
        if token_delta < 0:
            improving_signals += 1  # Lower tokens = more efficient
        if success_delta > 0.02:
            improving_signals += 1

        if improving_signals >= 2:
            direction = "improving"
        elif improving_signals == 0 and (quality_delta < -0.02 or success_delta < -0.02):
            direction = "declining"
        else:
            direction = "stable"

        return {
            "window_days": window_days,
            "total_records": len(timed_records),
            "older_half_count": len(older_half),
            "newer_half_count": len(newer_half),
            "trend_direction": direction,
            "quality_delta": round(quality_delta, 4),
            "token_delta": token_delta,
            "success_rate_delta": round(success_delta, 4),
            "older_avg_quality": round(old_quality, 4),
            "newer_avg_quality": round(new_quality, 4),
            "older_avg_tokens": old_tokens,
            "newer_avg_tokens": new_tokens,
            "older_success_rate": round(old_success, 4),
            "newer_success_rate": round(new_success, 4),
        }

    # ------------------------------------------------------------------
    # Rank agents
    # ------------------------------------------------------------------

    def rank_agents(
        self, records: list[AgentPerformanceRecord]
    ) -> list[dict]:
        """Rank agents by composite score: quality * success_rate / log(tokens).

        Uses log(tokens) to penalize excessive token usage while still
        rewarding quality and reliability.
        """
        agent_stats = self.aggregate_by_agent(records)

        ranked: list[dict] = []
        for agent_name, stats in agent_stats.items():
            quality = stats["avg_quality"]
            success_rate = stats["success_rate"]
            avg_tokens = stats["avg_tokens"]

            # Composite: quality * success_rate / log2(tokens + 1)
            # +1 to avoid log(0), log2 for reasonable scaling
            token_penalty = math.log2(avg_tokens + 1) if avg_tokens > 0 else 1.0
            composite = (quality * success_rate) / max(token_penalty, 0.1)

            ranked.append({
                "agent_name": agent_name,
                "composite_score": round(composite, 4),
                "avg_quality": round(quality, 4),
                "success_rate": round(success_rate, 4),
                "avg_tokens": avg_tokens,
                "total_runs": stats["total_runs"],
                "output_reuse_rate": round(stats["output_reuse_rate"], 4),
            })

        ranked.sort(key=lambda x: x["composite_score"], reverse=True)

        # Add rank position
        for i, entry in enumerate(ranked):
            entry["rank"] = i + 1

        return ranked

    # ------------------------------------------------------------------
    # Generate dashboard
    # ------------------------------------------------------------------

    def generate_dashboard(
        self, records: list[AgentPerformanceRecord]
    ) -> PerformanceDashboard:
        """Generate a full performance dashboard from records."""
        agents_ranked = self.rank_agents(records)
        trends = self.compute_trends(records)
        agent_stats = self.aggregate_by_agent(records)
        domain_stats = self.aggregate_by_domain(records)

        # Average quality across all records
        quality_scores = [r.quality_score for r in records if r.quality_score is not None]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

        # Average tokens
        avg_tokens = (
            sum(r.tokens_used for r in records) // len(records)
            if records else 0
        )

        improvement_trend = trends.get("quality_delta", 0.0)

        # Generate top learnings
        top_learnings: list[str] = []

        # Learning 1: Best performing agent
        if agents_ranked:
            best = agents_ranked[0]
            top_learnings.append(
                f"Top agent: '{best['agent_name']}' with composite score "
                f"{best['composite_score']:.3f} across {best['total_runs']} runs."
            )

        # Learning 2: Trend direction
        direction = trends.get("trend_direction", "unknown")
        if direction == "improving":
            top_learnings.append(
                f"Performance is improving: quality delta +{trends.get('quality_delta', 0):.3f}, "
                f"success rate delta +{trends.get('success_rate_delta', 0):.3f}."
            )
        elif direction == "declining":
            top_learnings.append(
                f"Performance is declining: quality delta {trends.get('quality_delta', 0):.3f}. "
                f"Investigate recent runs for regressions."
            )
        else:
            top_learnings.append(f"Performance trend is {direction}.")

        # Learning 3: Most active domain
        if domain_stats:
            most_active_domain = max(domain_stats.items(), key=lambda x: x[1]["total_runs"])
            top_learnings.append(
                f"Most active domain: '{most_active_domain[0]}' with "
                f"{most_active_domain[1]['total_runs']} runs and "
                f"{most_active_domain[1]['success_rate']:.0%} success rate."
            )

        # Learning 4: Token efficiency observation
        if agent_stats:
            token_efficient = min(
                agent_stats.items(),
                key=lambda x: x[1]["avg_tokens"] if x[1]["avg_tokens"] > 0 else float("inf"),
            )
            top_learnings.append(
                f"Most token-efficient agent: '{token_efficient[0]}' "
                f"averaging {token_efficient[1]['avg_tokens']} tokens/run."
            )

        # Learning 5: Reuse patterns
        reuse_agents = [
            name for name, stats in agent_stats.items()
            if stats["output_reuse_rate"] > 0.5
        ]
        if reuse_agents:
            top_learnings.append(
                f"High output-reuse agents (>50%): {', '.join(reuse_agents)}."
            )

        # Determine period from record timestamps
        timestamps = [r.timestamp for r in records]
        earliest = min(timestamps) if timestamps else "N/A"
        latest = max(timestamps) if timestamps else "N/A"
        period = f"{earliest[:10]} to {latest[:10]}" if timestamps else "N/A"

        return PerformanceDashboard(
            period=period,
            agents_ranked=agents_ranked,
            avg_quality=round(avg_quality, 4),
            avg_tokens=avg_tokens,
            improvement_trend=round(improvement_trend, 4),
            top_learnings=top_learnings,
        )

    # ------------------------------------------------------------------
    # Format dashboard
    # ------------------------------------------------------------------

    def format_dashboard(self, dashboard: PerformanceDashboard) -> str:
        """Format a PerformanceDashboard as readable markdown."""
        lines: list[str] = [
            "# Agent Performance Dashboard",
            "",
            f"**Period:** {dashboard.period}",
            f"**Average Quality:** {dashboard.avg_quality:.3f}",
            f"**Average Tokens:** {dashboard.avg_tokens:,}",
            f"**Improvement Trend:** {dashboard.improvement_trend:+.4f}",
            "",
            "## Agent Rankings",
            "",
            "| Rank | Agent | Composite | Quality | Success Rate | Avg Tokens | Runs | Reuse Rate |",
            "|---|---|---|---|---|---|---|---|",
        ]

        for agent in dashboard.agents_ranked:
            lines.append(
                f"| {agent.get('rank', '-')} "
                f"| {agent['agent_name']} "
                f"| {agent['composite_score']:.4f} "
                f"| {agent['avg_quality']:.3f} "
                f"| {agent['success_rate']:.0%} "
                f"| {agent['avg_tokens']:,} "
                f"| {agent['total_runs']} "
                f"| {agent['output_reuse_rate']:.0%} |"
            )

        lines.extend([
            "",
            "## Top Learnings",
            "",
        ])

        for i, learning in enumerate(dashboard.top_learnings, 1):
            lines.append(f"{i}. {learning}")

        lines.extend([
            "",
            f"*Generated at {_now_iso()}*",
            "",
        ])

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Save telemetry snapshot
    # ------------------------------------------------------------------

    def save_snapshot(self, records: list[AgentPerformanceRecord]) -> Path:
        """Save a performance snapshot to the data directory."""
        output_dir = (
            Path(__file__).resolve().parent.parent
            / "data" / "memory" / "performance"
        )
        output_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc)
        filename = f"performance-{now.strftime('%Y%m%d-%H%M%S')}.yaml"
        output_path = output_dir / filename

        dashboard = self.generate_dashboard(records)

        payload = {
            "generated_at": _now_iso(),
            "period": dashboard.period,
            "avg_quality": dashboard.avg_quality,
            "avg_tokens": dashboard.avg_tokens,
            "improvement_trend": dashboard.improvement_trend,
            "agents_ranked": dashboard.agents_ranked,
            "top_learnings": dashboard.top_learnings,
            "record_count": len(records),
        }

        with open(output_path, "w", encoding="utf-8") as fh:
            yaml.dump(payload, fh, default_flow_style=False, allow_unicode=True, sort_keys=False)

        return output_path
