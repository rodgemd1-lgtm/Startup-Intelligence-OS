"""Trajectory-Informed Memory Generation (TIMG) pipeline.

Analyzes agent run YAML files to extract reusable strategy, recovery, and
optimization tips that feed back into the memory system.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Import memory schemas -- fall back to compatible local definitions when
# the memory package is not on sys.path (avoids circular-import issues).
# ---------------------------------------------------------------------------

try:
    from memory.schemas import MemoryTip, Trajectory, TrajectoryStep  # noqa: F401
    _HAS_MEMORY = True
except ImportError:
    _HAS_MEMORY = False

    # Minimal compatible stand-ins so the pipeline works standalone.
    class TrajectoryStep:  # type: ignore[no-redef]
        """Lightweight stand-in for memory.schemas.TrajectoryStep."""

        def __init__(self, **kwargs: Any) -> None:
            for k, v in kwargs.items():
                setattr(self, k, v)

    class Trajectory:  # type: ignore[no-redef]
        """Lightweight stand-in for memory.schemas.Trajectory."""

        def __init__(self, **kwargs: Any) -> None:
            for k, v in kwargs.items():
                setattr(self, k, v)

    class MemoryTip:  # type: ignore[no-redef]
        """Lightweight stand-in for memory.schemas.MemoryTip."""

        def __init__(self, **kwargs: Any) -> None:
            for k, v in kwargs.items():
                setattr(self, k, v)


def _tip_id(content: str, run_id: str) -> str:
    """Deterministic tip ID from content + run."""
    raw = f"{content}:{run_id}"
    return f"tip-{hashlib.sha256(raw.encode()).hexdigest()[:12]}"


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


# ---------------------------------------------------------------------------
# Step contribution scoring
# ---------------------------------------------------------------------------

# Steps that represent decision points or high-value events
_DECISION_STEP_KEYWORDS = {
    "debate", "scored", "option", "monte_carlo", "recommendation",
    "synthesized", "decision", "review",
}

_HIGH_VALUE_STEPS = {
    "output_synthesized", "debate_completed", "options_scored",
    "run_monte_carlo",
}


def _step_has_alternatives(step: dict) -> bool:
    """Heuristic: a step represents a decision point if data suggests options."""
    data = step.get("data", {})
    if isinstance(data, dict):
        if "option_count" in data or "ranked" in data:
            return True
        if "modes" in data or "entry_count" in data:
            return True
    step_name = step.get("step", "")
    return any(kw in step_name for kw in _DECISION_STEP_KEYWORDS)


def _score_step_contribution(step: dict, outcome_success: bool) -> float:
    """Score how much a step contributed to the run outcome (0-1)."""
    base = 0.5
    confidence = step.get("confidence", 0.5)
    # Higher confidence steps contributed more to outcome
    base += (confidence - 0.5) * 0.4

    # Decision-point steps are more impactful
    if _step_has_alternatives(step):
        base += 0.15

    # High-value named steps
    step_name = step.get("step", "")
    if step_name in _HIGH_VALUE_STEPS:
        base += 0.1

    # If the run failed, steps with low confidence were likely culprits
    if not outcome_success and confidence < 0.6:
        base -= 0.2

    return max(0.0, min(1.0, base))


# ---------------------------------------------------------------------------
# TIMG Pipeline
# ---------------------------------------------------------------------------

class TIMGPipeline:
    """Trajectory-Informed Memory Generation pipeline.

    Analyzes completed run YAML files to extract strategy, recovery, and
    optimization tips that can be stored back into the memory system.
    """

    def __init__(self, memory_module_path: Path | None = None) -> None:
        self._memory_path = memory_module_path or Path(__file__).resolve().parent.parent / "memory"

    # ------------------------------------------------------------------
    # Core analysis
    # ------------------------------------------------------------------

    def analyze_trajectory(self, run_data: dict) -> list[dict]:
        """Analyze a single run YAML dict and return raw tip candidates.

        Returns a list of dicts with keys:
            tip_type, content, source_run_id, source_agent, task_domain,
            confidence, step_name, contribution_score
        """
        run_id = run_data.get("id", "unknown")
        events = run_data.get("events", [])
        status = run_data.get("status", "unknown")
        mode = run_data.get("mode", "unknown")
        company = run_data.get("company", "")
        outcome_success = status == "completed"

        tips: list[dict] = []

        # Build causal chain
        causal_chain: list[dict] = []
        for i, event in enumerate(events):
            step_name = event.get("step", f"step_{i}")
            contribution = _score_step_contribution(event, outcome_success)
            has_alternatives = _step_has_alternatives(event)
            causal_chain.append({
                "index": i,
                "step": step_name,
                "confidence": event.get("confidence", 0.5),
                "uncertainty": event.get("uncertainty", 0.5),
                "contribution": contribution,
                "has_alternatives": has_alternatives,
                "data": event.get("data", {}),
                "evidence_ids": event.get("evidence_ids", []),
            })

        # Extract tips from decision points (where alternatives existed)
        for node in causal_chain:
            if node["has_alternatives"]:
                data = node["data"]
                data_summary = _summarize_step_data(data)
                tips.append({
                    "tip_type": "strategy",
                    "content": (
                        f"At step '{node['step']}' in mode '{mode}', "
                        f"a decision point was reached. {data_summary} "
                        f"Confidence at this point was {node['confidence']:.2f}."
                    ),
                    "source_run_id": run_id,
                    "source_agent": run_data.get("trigger", "").split(":")[0] if ":" in run_data.get("trigger", "") else mode,
                    "task_domain": mode,
                    "confidence": node["contribution"],
                    "step_name": node["step"],
                    "contribution_score": node["contribution"],
                })

        # Extract from output section
        output = run_data.get("output", {})
        if isinstance(output, dict) and output.get("recommendation"):
            recommendation = output["recommendation"]
            failure_modes = output.get("failure_modes", [])
            tips.append({
                "tip_type": "strategy",
                "content": (
                    f"Run '{run_id}' ({mode} mode, company '{company}') "
                    f"produced recommendation: {recommendation[:200]}..."
                    if len(recommendation) > 200 else
                    f"Run '{run_id}' ({mode} mode, company '{company}') "
                    f"produced recommendation: {recommendation}"
                ),
                "source_run_id": run_id,
                "source_agent": mode,
                "task_domain": mode,
                "confidence": 0.7 if outcome_success else 0.3,
                "step_name": "output",
                "contribution_score": 0.8 if outcome_success else 0.4,
            })
            if failure_modes:
                tips.append({
                    "tip_type": "recovery",
                    "content": (
                        f"Known failure modes for '{mode}' run '{run_id}': "
                        + "; ".join(str(f)[:100] for f in failure_modes[:5])
                    ),
                    "source_run_id": run_id,
                    "source_agent": mode,
                    "task_domain": mode,
                    "confidence": 0.6,
                    "step_name": "failure_modes",
                    "contribution_score": 0.6,
                })

        return tips

    # ------------------------------------------------------------------
    # Strategy tips (from successful runs)
    # ------------------------------------------------------------------

    def extract_strategy_tips(self, run_data: dict) -> list[dict]:
        """Extract strategy tips from successful runs.

        Identifies: what sequence of actions led to success, what tools
        were most effective, and what order of operations worked.
        """
        status = run_data.get("status", "")
        if status != "completed":
            return []

        run_id = run_data.get("id", "unknown")
        mode = run_data.get("mode", "unknown")
        events = run_data.get("events", [])
        output = run_data.get("output", {})
        company = run_data.get("company", "")
        tips: list[dict] = []

        # Tip 1: Successful action sequence
        step_names = [e.get("step", "unknown") for e in events]
        if step_names:
            tips.append({
                "tip_type": "strategy",
                "content": (
                    f"Successful {mode} run for '{company}': "
                    f"action sequence was {' -> '.join(step_names)}. "
                    f"This sequence completed without errors."
                ),
                "source_run_id": run_id,
                "source_agent": mode,
                "task_domain": mode,
                "confidence": 0.75,
                "step_name": "sequence_analysis",
                "contribution_score": 0.7,
            })

        # Tip 2: High-confidence steps that drove outcome
        high_conf_steps = [
            e for e in events
            if e.get("confidence", 0) >= 0.9
        ]
        for step in high_conf_steps:
            step_name = step.get("step", "unknown")
            data = step.get("data", {})
            evidence_ids = step.get("evidence_ids", [])
            tips.append({
                "tip_type": "strategy",
                "content": (
                    f"Step '{step_name}' in {mode} mode had high confidence "
                    f"({step.get('confidence', 0):.2f}) and "
                    f"used {len(evidence_ids)} evidence sources. "
                    f"Data: {_summarize_step_data(data)}"
                ),
                "source_run_id": run_id,
                "source_agent": mode,
                "task_domain": mode,
                "confidence": step.get("confidence", 0.5),
                "step_name": step_name,
                "contribution_score": 0.8,
            })

        # Tip 3: Effective evidence usage patterns
        all_evidence: list[str] = []
        for e in events:
            all_evidence.extend(e.get("evidence_ids", []))
        unique_evidence = list(dict.fromkeys(all_evidence))
        if unique_evidence:
            tips.append({
                "tip_type": "strategy",
                "content": (
                    f"Run '{run_id}' ({mode}) used {len(unique_evidence)} "
                    f"unique evidence sources: {', '.join(unique_evidence[:10])}. "
                    f"Evidence-backed runs in this domain tend to produce "
                    f"higher-confidence outputs."
                ),
                "source_run_id": run_id,
                "source_agent": mode,
                "task_domain": mode,
                "confidence": 0.7,
                "step_name": "evidence_usage",
                "contribution_score": 0.65,
            })

        # Tip 4: Output quality indicators
        if isinstance(output, dict):
            rec = output.get("recommendation", "")
            counter = output.get("counter_recommendation", "")
            if rec and counter:
                tips.append({
                    "tip_type": "strategy",
                    "content": (
                        f"Successful {mode} run produced both a primary "
                        f"recommendation and counter-recommendation, "
                        f"indicating balanced analysis. "
                        f"Recommendation length: {len(rec)} chars, "
                        f"counter length: {len(counter)} chars."
                    ),
                    "source_run_id": run_id,
                    "source_agent": mode,
                    "task_domain": mode,
                    "confidence": 0.65,
                    "step_name": "output_quality",
                    "contribution_score": 0.6,
                })

        return tips

    # ------------------------------------------------------------------
    # Recovery tips (from runs with errors or low confidence)
    # ------------------------------------------------------------------

    def extract_recovery_tips(self, run_data: dict) -> list[dict]:
        """Extract recovery tips from runs with errors or issues.

        Identifies: what error occurred, what recovery action fixed it,
        and what should have been done differently.
        """
        run_id = run_data.get("id", "unknown")
        mode = run_data.get("mode", "unknown")
        status = run_data.get("status", "unknown")
        events = run_data.get("events", [])
        output = run_data.get("output", {})
        tips: list[dict] = []

        # Check for failed status
        if status == "failed" or status == "error":
            tips.append({
                "tip_type": "recovery",
                "content": (
                    f"Run '{run_id}' ({mode}) ended with status '{status}'. "
                    f"Review the event chain to identify the failure point. "
                    f"Steps executed: {len(events)}."
                ),
                "source_run_id": run_id,
                "source_agent": mode,
                "task_domain": mode,
                "confidence": 0.8,
                "step_name": "run_failure",
                "contribution_score": 0.9,
            })

        # Check for high-uncertainty steps (uncertainty > 0.3)
        for event in events:
            uncertainty = event.get("uncertainty", 0.0)
            step_name = event.get("step", "unknown")
            if uncertainty > 0.3:
                tips.append({
                    "tip_type": "recovery",
                    "content": (
                        f"Step '{step_name}' in run '{run_id}' had high "
                        f"uncertainty ({uncertainty:.2f}). Consider: "
                        f"(1) providing more evidence inputs, "
                        f"(2) breaking the step into smaller sub-tasks, "
                        f"(3) using a different tool or approach."
                    ),
                    "source_run_id": run_id,
                    "source_agent": mode,
                    "task_domain": mode,
                    "confidence": 0.6,
                    "step_name": step_name,
                    "contribution_score": 0.7,
                })

        # Check for steps with declining confidence
        prev_confidence = 1.0
        for event in events:
            conf = event.get("confidence", 0.5)
            step_name = event.get("step", "unknown")
            if conf < prev_confidence - 0.15:
                tips.append({
                    "tip_type": "recovery",
                    "content": (
                        f"Confidence dropped from {prev_confidence:.2f} to "
                        f"{conf:.2f} at step '{step_name}' in run '{run_id}'. "
                        f"This may indicate the step lacked sufficient context "
                        f"or evidence to proceed confidently."
                    ),
                    "source_run_id": run_id,
                    "source_agent": mode,
                    "task_domain": mode,
                    "confidence": 0.55,
                    "step_name": step_name,
                    "contribution_score": 0.65,
                })
            prev_confidence = conf

        # Check failure modes from output
        if isinstance(output, dict):
            failure_modes = output.get("failure_modes", [])
            for fm in failure_modes:
                fm_str = str(fm)[:200]
                tips.append({
                    "tip_type": "recovery",
                    "content": (
                        f"Documented failure mode from run '{run_id}' ({mode}): "
                        f"{fm_str}. Future runs should include a mitigation "
                        f"strategy or early-exit check for this scenario."
                    ),
                    "source_run_id": run_id,
                    "source_agent": mode,
                    "task_domain": mode,
                    "confidence": 0.6,
                    "step_name": "failure_mode_documentation",
                    "contribution_score": 0.6,
                })

        return tips

    # ------------------------------------------------------------------
    # Optimization tips (from slow or expensive runs)
    # ------------------------------------------------------------------

    def extract_optimization_tips(self, run_data: dict) -> list[dict]:
        """Extract optimization tips from slow or expensive runs.

        Identifies: which steps used disproportionate resources, what
        could be parallelized, and where context was wasted.
        """
        run_id = run_data.get("id", "unknown")
        mode = run_data.get("mode", "unknown")
        events = run_data.get("events", [])
        tips: list[dict] = []

        if len(events) < 2:
            return tips

        # Compute per-step time deltas from timestamps
        step_durations: list[dict] = []
        for i, event in enumerate(events):
            ts = event.get("timestamp", "")
            next_ts = events[i + 1].get("timestamp", "") if i + 1 < len(events) else ""
            duration_ms = _timestamp_delta_ms(ts, next_ts) if next_ts else 0
            step_durations.append({
                "step": event.get("step", f"step_{i}"),
                "duration_ms": duration_ms,
                "data_size": _estimate_data_size(event.get("data", {})),
                "evidence_count": len(event.get("evidence_ids", [])),
            })

        # Find disproportionately expensive steps
        total_duration = sum(s["duration_ms"] for s in step_durations)
        if total_duration > 0:
            for sd in step_durations:
                if sd["duration_ms"] > 0:
                    fraction = sd["duration_ms"] / total_duration
                    if fraction > 0.5 and len(step_durations) > 2:
                        tips.append({
                            "tip_type": "optimization",
                            "content": (
                                f"Step '{sd['step']}' consumed {fraction:.0%} of "
                                f"total run time in '{run_id}' ({mode}). "
                                f"Consider: caching inputs, reducing context window, "
                                f"or splitting into parallel sub-steps."
                            ),
                            "source_run_id": run_id,
                            "source_agent": mode,
                            "task_domain": mode,
                            "confidence": 0.65,
                            "step_name": sd["step"],
                            "contribution_score": 0.7,
                        })

        # Detect duplicate evidence loading
        all_evidence_per_step: list[set[str]] = []
        for event in events:
            ids = set(event.get("evidence_ids", []))
            all_evidence_per_step.append(ids)

        for i in range(1, len(all_evidence_per_step)):
            overlap = all_evidence_per_step[i] & all_evidence_per_step[i - 1]
            if overlap and len(overlap) >= 2:
                step_name = events[i].get("step", f"step_{i}")
                prev_step = events[i - 1].get("step", f"step_{i-1}")
                tips.append({
                    "tip_type": "optimization",
                    "content": (
                        f"Steps '{prev_step}' and '{step_name}' in run '{run_id}' "
                        f"both loaded {len(overlap)} identical evidence IDs "
                        f"({', '.join(sorted(overlap)[:5])}). "
                        f"Consider passing evidence forward to avoid redundant loads."
                    ),
                    "source_run_id": run_id,
                    "source_agent": mode,
                    "task_domain": mode,
                    "confidence": 0.7,
                    "step_name": step_name,
                    "contribution_score": 0.65,
                })

        # Detect potential parallelism (independent steps)
        independent_candidates: list[str] = []
        for i in range(1, len(events)):
            prev_evidence = set(events[i - 1].get("evidence_ids", []))
            curr_evidence = set(events[i].get("evidence_ids", []))
            # If step does not depend on prior step's evidence, it might be parallelizable
            if not curr_evidence.issubset(prev_evidence) and prev_evidence and curr_evidence:
                if not (curr_evidence & prev_evidence):
                    independent_candidates.append(events[i].get("step", f"step_{i}"))

        if independent_candidates:
            tips.append({
                "tip_type": "optimization",
                "content": (
                    f"In run '{run_id}' ({mode}), steps "
                    f"{', '.join(independent_candidates[:5])} appear to use "
                    f"independent evidence sets and may be parallelizable."
                ),
                "source_run_id": run_id,
                "source_agent": mode,
                "task_domain": mode,
                "confidence": 0.5,
                "step_name": "parallelism_opportunity",
                "contribution_score": 0.5,
            })

        # Large data payloads
        for sd in step_durations:
            if sd["data_size"] > 500:
                tips.append({
                    "tip_type": "optimization",
                    "content": (
                        f"Step '{sd['step']}' in run '{run_id}' carried a "
                        f"large data payload (~{sd['data_size']} chars). "
                        f"Consider summarizing or compressing context before "
                        f"passing to downstream steps."
                    ),
                    "source_run_id": run_id,
                    "source_agent": mode,
                    "task_domain": mode,
                    "confidence": 0.55,
                    "step_name": sd["step"],
                    "contribution_score": 0.55,
                })

        return tips

    # ------------------------------------------------------------------
    # Batch processing
    # ------------------------------------------------------------------

    def process_all_runs(self, runs_dir: Path) -> list[dict]:
        """Batch process all run YAML files in the given directory.

        Returns the combined list of tips from all three extraction methods.
        """
        all_tips: list[dict] = []

        if not runs_dir.exists():
            return all_tips

        yaml_files = sorted(runs_dir.glob("run-*.yaml"))
        for yaml_file in yaml_files:
            run_data = _safe_load_yaml(yaml_file)
            if run_data is None:
                continue

            # General trajectory analysis
            all_tips.extend(self.analyze_trajectory(run_data))

            # Strategy tips from successful runs
            all_tips.extend(self.extract_strategy_tips(run_data))

            # Recovery tips from any run (looks for errors and low confidence)
            all_tips.extend(self.extract_recovery_tips(run_data))

            # Optimization tips from runs with multiple steps
            all_tips.extend(self.extract_optimization_tips(run_data))

        return all_tips

    # ------------------------------------------------------------------
    # Format for storage
    # ------------------------------------------------------------------

    def format_tips_for_storage(self, raw_tips: list[dict]) -> list[dict]:
        """Normalize raw tips into MemoryTip-compatible format.

        Each returned dict is ready to be serialized to YAML or constructed
        into a MemoryTip instance.
        """
        formatted: list[dict] = []
        seen_ids: set[str] = set()
        now = _now_iso()

        for tip in raw_tips:
            content = tip.get("content", "")
            run_id = tip.get("source_run_id", "unknown")
            tip_id = _tip_id(content, run_id)

            # Deduplicate
            if tip_id in seen_ids:
                continue
            seen_ids.add(tip_id)

            tip_type = tip.get("tip_type", "strategy")
            if tip_type not in ("strategy", "recovery", "optimization"):
                tip_type = "strategy"

            formatted.append({
                "id": tip_id,
                "tip_type": tip_type,
                "content": content,
                "source_run_id": run_id,
                "source_agent": tip.get("source_agent", "unknown"),
                "task_domain": tip.get("task_domain", "general"),
                "confidence": max(0.0, min(1.0, tip.get("confidence", 0.5))),
                "created_at": now,
                "access_count": 0,
                "last_accessed": None,
                "embedding": None,
                "tags": [
                    tip_type,
                    tip.get("task_domain", "general"),
                    tip.get("step_name", ""),
                ],
            })

        return formatted


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _summarize_step_data(data: Any) -> str:
    """Create a short text summary of a step's data payload."""
    if not isinstance(data, dict):
        return str(data)[:100]

    parts: list[str] = []
    for key, value in list(data.items())[:6]:
        if isinstance(value, list):
            parts.append(f"{key}: {len(value)} items")
        elif isinstance(value, dict):
            parts.append(f"{key}: {len(value)} fields")
        else:
            val_str = str(value)[:60]
            parts.append(f"{key}={val_str}")

    return "; ".join(parts) if parts else "no data"


def _timestamp_delta_ms(ts_a: str, ts_b: str) -> int:
    """Compute millisecond delta between two ISO timestamps."""
    try:
        fmt_patterns = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%S.%f%z",
        ]
        dt_a = dt_b = None
        for fmt in fmt_patterns:
            try:
                dt_a = datetime.strptime(ts_a, fmt)
                break
            except ValueError:
                continue
        for fmt in fmt_patterns:
            try:
                dt_b = datetime.strptime(ts_b, fmt)
                break
            except ValueError:
                continue
        if dt_a and dt_b:
            delta = (dt_b - dt_a).total_seconds() * 1000
            return max(0, int(delta))
    except Exception:
        pass
    return 0


def _estimate_data_size(data: Any) -> int:
    """Rough character count of a data payload."""
    try:
        return len(str(data))
    except Exception:
        return 0
