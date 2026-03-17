"""ActionPacket score to routing weight adjustment processor.

Scans run YAML files for quality scores by department, computes learned
routing weight adjustments, and writes them to a persistent YAML store.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from self_improvement.schemas import RoutingFeedback, RoutingWeight


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


def _safe_write_yaml(path: Path, data: Any) -> None:
    """Write data to a YAML file, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        yaml.dump(data, fh, default_flow_style=False, allow_unicode=True, sort_keys=False)


# ---------------------------------------------------------------------------
# Department keyword registry (mirrors .startup-os/departments/*.yaml)
# ---------------------------------------------------------------------------

_DEFAULT_DEPARTMENT_KEYWORDS: dict[str, list[str]] = {
    "founder-decision-room": [
        "strategy", "decision", "priority", "future-back", "project",
        "company", "roadmap",
    ],
    "consumer-user-studio": [
        "user", "customer", "consumer", "persona", "interview",
        "research", "discovery",
    ],
    "engineering-agent-systems-studio": [
        "build", "engineering", "architecture", "system",
        "implementation", "backend", "agent",
    ],
    "revenue-growth-studio": [
        "revenue", "pipeline", "funnel", "growth", "conversion",
        "acquisition", "expansion", "pricing",
    ],
    "product-experience-studio": [
        "product", "experience", "workflow", "ux", "design",
        "interface", "interaction",
    ],
    "marketing-narrative-studio": [
        "marketing", "narrative", "story", "brand", "messaging",
        "content", "campaign",
    ],
    "data-decision-science-studio": [
        "data", "analytics", "metrics", "experiment", "forecast",
        "model", "ml",
    ],
    "finance-operating-cadence-studio": [
        "finance", "budget", "runway", "burn", "operating",
        "cadence", "accounting",
    ],
    "talent-org-design-studio": [
        "talent", "hiring", "team", "org", "culture",
        "people", "onboarding",
    ],
    "trust-governance-studio": [
        "trust", "governance", "compliance", "risk", "security",
        "privacy", "legal",
    ],
    "job-studio": [
        "training", "session", "learner", "facilitator", "curriculum",
        "workshop", "enablement",
    ],
}


def _load_department_keywords(departments_dir: Path) -> dict[str, list[str]]:
    """Load routing keywords from department YAML files if available."""
    keywords: dict[str, list[str]] = {}
    if not departments_dir.exists():
        return _DEFAULT_DEPARTMENT_KEYWORDS.copy()

    for yaml_file in departments_dir.glob("*.yaml"):
        data = _safe_load_yaml(yaml_file)
        if data and "id" in data and "routing_keywords" in data:
            keywords[data["id"]] = data["routing_keywords"]

    return keywords if keywords else _DEFAULT_DEPARTMENT_KEYWORDS.copy()


# ---------------------------------------------------------------------------
# Extract department from run trigger
# ---------------------------------------------------------------------------

_TRIGGER_DEPARTMENT_MAP: dict[str, str] = {
    "decision": "founder-decision-room",
    "debate": "founder-decision-room",
    "simulation": "data-decision-science-studio",
    "simulated-maturity": "data-decision-science-studio",
    "foundry": "engineering-agent-systems-studio",
    "research": "consumer-user-studio",
}


def _infer_department_from_run(run_data: dict) -> str:
    """Infer the routed department from a run's trigger and mode."""
    trigger = run_data.get("trigger", "")
    mode = run_data.get("mode", "")

    # Check trigger prefix
    trigger_prefix = trigger.split(":")[0] if ":" in trigger else trigger
    if trigger_prefix in _TRIGGER_DEPARTMENT_MAP:
        return _TRIGGER_DEPARTMENT_MAP[trigger_prefix]

    # Check trigger body for department name keywords
    trigger_lower = trigger.lower()
    for dept_id in _DEFAULT_DEPARTMENT_KEYWORDS:
        dept_short = dept_id.replace("-studio", "").replace("-", " ")
        if dept_short in trigger_lower:
            return dept_id

    # Fall back to mode mapping
    if mode in _TRIGGER_DEPARTMENT_MAP:
        return _TRIGGER_DEPARTMENT_MAP[mode]

    return "unknown"


def _compute_run_quality_score(run_data: dict) -> float:
    """Compute an aggregate quality score for a run (0-1)."""
    events = run_data.get("events", [])
    if not events:
        return 0.5

    confidences = [e.get("confidence", 0.5) for e in events]
    avg_confidence = sum(confidences) / len(confidences)

    # Bonus for completed status
    status_bonus = 0.1 if run_data.get("status") == "completed" else -0.1

    # Bonus for having output
    output = run_data.get("output", {})
    output_bonus = 0.05 if isinstance(output, dict) and output.get("recommendation") else 0.0

    # Bonus for evidence usage
    total_evidence = sum(
        len(e.get("evidence_ids", []))
        for e in events
    )
    evidence_bonus = min(0.1, total_evidence * 0.01)

    score = avg_confidence + status_bonus + output_bonus + evidence_bonus
    return max(0.0, min(1.0, score))


# ---------------------------------------------------------------------------
# RoutingFeedbackProcessor
# ---------------------------------------------------------------------------

class RoutingFeedbackProcessor:
    """Processes run results into routing weight adjustments.

    Scans run YAML files, computes per-department quality scores, and
    adjusts routing keyword weights based on empirical performance.
    """

    def __init__(self, data_dir: Path) -> None:
        """Initialize with path to apps/decision_os/data/."""
        self._data_dir = data_dir
        self._runs_dir = data_dir / "runs"

    # ------------------------------------------------------------------
    # Collect feedback
    # ------------------------------------------------------------------

    def collect_feedback(self) -> list[RoutingFeedback]:
        """Scan run YAML files and extract routing feedback records.

        Each completed run produces one RoutingFeedback entry with quality
        scores derived from confidence, evidence usage, and output quality.
        """
        feedback: list[RoutingFeedback] = []

        if not self._runs_dir.exists():
            return feedback

        for yaml_file in sorted(self._runs_dir.glob("run-*.yaml")):
            run_data = _safe_load_yaml(yaml_file)
            if run_data is None:
                continue

            run_id = run_data.get("id", yaml_file.stem)
            department = _infer_department_from_run(run_data)
            if department == "unknown":
                continue

            quality = _compute_run_quality_score(run_data)

            # Output usefulness: does the output have a recommendation?
            output = run_data.get("output", {})
            has_rec = isinstance(output, dict) and bool(output.get("recommendation"))
            has_counter = isinstance(output, dict) and bool(output.get("counter_recommendation"))
            has_next = isinstance(output, dict) and bool(output.get("next_experiment"))
            usefulness_score = 0.3
            if has_rec:
                usefulness_score += 0.3
            if has_counter:
                usefulness_score += 0.2
            if has_next:
                usefulness_score += 0.2

            # Follow-through: were artifacts produced?
            artifacts = run_data.get("artifacts_produced", [])
            follow_through = min(1.0, 0.3 + len(artifacts) * 0.2)

            # Reuse value: based on evidence density
            events = run_data.get("events", [])
            unique_evidence: set[str] = set()
            for event in events:
                unique_evidence.update(event.get("evidence_ids", []))
            reuse_value = min(1.0, 0.2 + len(unique_evidence) * 0.1)

            timestamp = run_data.get("completed_at", run_data.get("started_at", _now_iso()))

            feedback.append(RoutingFeedback(
                action_packet_id=run_id,
                routed_department=department,
                routing_quality=quality,
                output_usefulness=usefulness_score,
                follow_through=follow_through,
                reuse_value=reuse_value,
                timestamp=timestamp,
            ))

        return feedback

    # ------------------------------------------------------------------
    # Compute adjustments
    # ------------------------------------------------------------------

    def compute_adjustments(
        self,
        feedback: list[RoutingFeedback],
        departments_dir: Path | None = None,
    ) -> list[RoutingWeight]:
        """Compute routing weight adjustments from collected feedback.

        For each department and its keywords:
        1. Average all quality scores from feedback for that department
        2. If avg > 0.7: boost weight by +0.1
        3. If avg < 0.4: reduce weight by -0.1
        4. Clamp adjustments to [-0.3, +0.3]
        """
        # Group feedback by department
        dept_scores: dict[str, list[float]] = {}
        for fb in feedback:
            avg_score = (
                fb.routing_quality
                + fb.output_usefulness
                + fb.follow_through
                + fb.reuse_value
            ) / 4.0
            dept_scores.setdefault(fb.routed_department, []).append(avg_score)

        # Load department keywords
        if departments_dir:
            dept_keywords = _load_department_keywords(departments_dir)
        else:
            dept_keywords = _DEFAULT_DEPARTMENT_KEYWORDS.copy()

        # Load existing weights to carry forward adjustments
        existing_weights = self._load_existing_weights()
        now = _now_iso()

        weights: list[RoutingWeight] = []

        for dept_id, keywords in dept_keywords.items():
            scores = dept_scores.get(dept_id, [])
            sample_count = len(scores)
            avg_quality = sum(scores) / len(scores) if scores else 0.5

            # Determine adjustment direction
            if avg_quality > 0.7:
                adjustment_delta = 0.1
            elif avg_quality < 0.4:
                adjustment_delta = -0.1
            else:
                adjustment_delta = 0.0

            for keyword in keywords:
                key = f"{dept_id}:{keyword}"
                existing = existing_weights.get(key)
                base_weight = 1.0
                prior_adjustment = 0.0

                if existing:
                    base_weight = existing.get("base_weight", 1.0)
                    prior_adjustment = existing.get("learned_adjustment", 0.0)

                # Accumulate adjustments but clamp
                new_adjustment = prior_adjustment + adjustment_delta
                new_adjustment = max(-0.3, min(0.3, new_adjustment))

                effective = base_weight + new_adjustment

                weights.append(RoutingWeight(
                    department=dept_id,
                    keyword=keyword,
                    base_weight=base_weight,
                    learned_adjustment=round(new_adjustment, 3),
                    effective_weight=round(effective, 3),
                    sample_count=sample_count,
                    last_updated=now,
                ))

        return weights

    # ------------------------------------------------------------------
    # Apply adjustments
    # ------------------------------------------------------------------

    def apply_adjustments(
        self,
        weights: list[RoutingWeight],
        departments_dir: Path,
    ) -> Path:
        """Write updated weights to routing_weights.yaml.

        Saves to backend/data/memory/routing_weights/ rather than
        modifying department YAML files directly.
        """
        output_dir = departments_dir.parent / "data" / "memory" / "routing_weights"
        if not output_dir.exists():
            # Try a relative fallback from the departments dir
            output_dir = Path(__file__).resolve().parent.parent / "data" / "memory" / "routing_weights"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / "routing_weights.yaml"

        records: list[dict] = []
        for w in weights:
            records.append({
                "department": w.department,
                "keyword": w.keyword,
                "base_weight": w.base_weight,
                "learned_adjustment": w.learned_adjustment,
                "effective_weight": w.effective_weight,
                "sample_count": w.sample_count,
                "last_updated": w.last_updated,
            })

        payload = {
            "version": "1.0",
            "generated_at": _now_iso(),
            "total_weights": len(records),
            "weights": records,
        }

        _safe_write_yaml(output_path, payload)
        return output_path

    # ------------------------------------------------------------------
    # Generate report
    # ------------------------------------------------------------------

    def generate_report(self) -> str:
        """Generate a markdown report of routing performance by department."""
        feedback = self.collect_feedback()

        # Group by department
        dept_data: dict[str, dict[str, Any]] = {}
        for fb in feedback:
            if fb.routed_department not in dept_data:
                dept_data[fb.routed_department] = {
                    "count": 0,
                    "routing_quality": [],
                    "output_usefulness": [],
                    "follow_through": [],
                    "reuse_value": [],
                }
            d = dept_data[fb.routed_department]
            d["count"] += 1
            d["routing_quality"].append(fb.routing_quality)
            d["output_usefulness"].append(fb.output_usefulness)
            d["follow_through"].append(fb.follow_through)
            d["reuse_value"].append(fb.reuse_value)

        lines: list[str] = [
            "# Routing Performance Report",
            "",
            f"**Generated:** {_now_iso()}",
            f"**Total feedback records:** {len(feedback)}",
            f"**Departments tracked:** {len(dept_data)}",
            "",
            "## Department Summary",
            "",
            "| Department | Runs | Avg Quality | Avg Usefulness | Avg Follow-Through | Avg Reuse | Verdict |",
            "|---|---|---|---|---|---|---|",
        ]

        for dept_id in sorted(dept_data.keys()):
            d = dept_data[dept_id]
            count = d["count"]
            avg_q = sum(d["routing_quality"]) / count
            avg_u = sum(d["output_usefulness"]) / count
            avg_f = sum(d["follow_through"]) / count
            avg_r = sum(d["reuse_value"]) / count
            composite = (avg_q + avg_u + avg_f + avg_r) / 4.0

            if composite > 0.7:
                verdict = "BOOST"
            elif composite < 0.4:
                verdict = "REDUCE"
            else:
                verdict = "HOLD"

            lines.append(
                f"| {dept_id} | {count} | {avg_q:.2f} | {avg_u:.2f} | "
                f"{avg_f:.2f} | {avg_r:.2f} | {verdict} |"
            )

        lines.extend([
            "",
            "## Interpretation",
            "",
            "- **BOOST**: Department consistently delivers high-quality, useful outputs. Routing weight increased.",
            "- **HOLD**: Department performance is within normal range. No weight change.",
            "- **REDUCE**: Department outputs have low quality or usefulness. Routing weight decreased.",
            "",
            "## Methodology",
            "",
            "Quality scores are derived from:",
            "- **Routing quality**: Average event confidence and completion status.",
            "- **Output usefulness**: Presence and completeness of recommendations.",
            "- **Follow-through**: Number of artifacts produced.",
            "- **Reuse value**: Density of evidence references.",
            "",
        ])

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_existing_weights(self) -> dict[str, dict]:
        """Load existing routing weights from the YAML store."""
        weights_path = (
            Path(__file__).resolve().parent.parent
            / "data" / "memory" / "routing_weights" / "routing_weights.yaml"
        )
        if not weights_path.exists():
            return {}

        data = _safe_load_yaml(weights_path)
        if not data or "weights" not in data:
            return {}

        result: dict[str, dict] = {}
        for w in data["weights"]:
            key = f"{w['department']}:{w['keyword']}"
            result[key] = w

        return result
