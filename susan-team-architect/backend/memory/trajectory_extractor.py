"""TIMG Phase 1 -- Trajectory Extraction.

Reads completed run YAML files from the Decision OS runs directory, converts
them into Trajectory objects, and extracts reusable MemoryTip insights.

Extraction heuristics:
  - **Strategy tips** are derived from runs that completed successfully with
    high-confidence steps.  The recommendation and key step decisions are
    captured as transferable strategy knowledge.
  - **Recovery tips** are derived from runs that contain a failure or
    low-confidence step followed by a later step that recovered (confidence
    increased or outcome improved).
  - **Optimization tips** are derived from runs that succeeded but took many
    steps relative to their peers, or produced redundant evidence -- signaling
    that a shorter path likely exists.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .schemas import MemoryTip, Trajectory, TrajectoryStep


def _deterministic_id(prefix: str, *parts: str) -> str:
    """Generate a deterministic short hash ID from string parts."""
    raw = ":".join(parts)
    digest = hashlib.sha256(raw.encode()).hexdigest()[:12]
    return f"{prefix}-{digest}"


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_timestamp_pair(start: str, end: str) -> int:
    """Return duration in milliseconds between two ISO timestamp strings."""
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    try:
        t_start = datetime.strptime(start, fmt)
        t_end = datetime.strptime(end, fmt)
        delta = t_end - t_start
        return max(int(delta.total_seconds() * 1000), 0)
    except (ValueError, TypeError):
        return 0


class TrajectoryExtractor:
    """Loads run YAML files and converts them into Trajectory + MemoryTip objects."""

    def __init__(self, runs_dir: Path) -> None:
        self.runs_dir = runs_dir

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load_trajectories(self) -> list[Trajectory]:
        """Read all run-*.yaml files and convert to Trajectory objects."""
        trajectories: list[Trajectory] = []
        if not self.runs_dir.exists():
            return trajectories

        for yaml_path in sorted(self.runs_dir.glob("run-*.yaml")):
            try:
                data = yaml.safe_load(yaml_path.read_text())
                if data is None:
                    continue
                trajectory = self._run_to_trajectory(data)
                trajectories.append(trajectory)
            except Exception:
                # Skip malformed files rather than crashing the batch
                continue
        return trajectories

    def _run_to_trajectory(self, run: dict[str, Any]) -> Trajectory:
        """Convert a raw run YAML dict into a Trajectory model."""
        events: list[dict[str, Any]] = run.get("events") or []
        steps: list[TrajectoryStep] = []

        for idx, event in enumerate(events):
            step_name = event.get("step", "unknown")
            data = event.get("data") or {}
            confidence = event.get("confidence", 0.0)
            ts = event.get("timestamp", "")

            # Compute duration relative to previous step
            if idx > 0:
                prev_ts = events[idx - 1].get("timestamp", "")
                dur = _parse_timestamp_pair(prev_ts, ts)
            else:
                dur = 0

            # Estimate token count from data payload size (proxy)
            data_str = str(data)
            token_estimate = max(len(data_str) // 4, 1)

            steps.append(TrajectoryStep(
                step_index=idx,
                tool_name=step_name,
                input_summary=f"step={step_name}",
                output_summary=self._summarise_data(data),
                success=confidence >= 0.5,
                duration_ms=dur,
                token_count=token_estimate,
                reasoning=None,
            ))

        # Determine outcome
        status = run.get("status", "completed")
        if status == "completed":
            # Check if all steps succeeded
            if steps and all(s.success for s in steps):
                outcome = "success"
            elif steps and any(s.success for s in steps):
                outcome = "partial"
            else:
                outcome = "failure"
        elif status == "failed":
            outcome = "failure"
        else:
            outcome = "partial"

        total_tokens = sum(s.token_count for s in steps)
        total_dur = sum(s.duration_ms for s in steps)

        # Derive agent name from trigger
        trigger = run.get("trigger", "")
        agent_name = trigger.split(":")[0] if ":" in trigger else trigger

        # Derive task description from output recommendation or trigger
        output = run.get("output") or {}
        task_desc = output.get("recommendation", trigger)[:200]

        # Quality score: average confidence of all events
        confidences = [e.get("confidence", 0.0) for e in events if "confidence" in e]
        quality = sum(confidences) / len(confidences) if confidences else None

        return Trajectory(
            run_id=run.get("id", "unknown"),
            agent_name=agent_name,
            task_description=task_desc,
            steps=steps,
            outcome=outcome,  # type: ignore[arg-type]
            total_tokens=total_tokens,
            total_duration_ms=total_dur,
            created_at=run.get("started_at", _iso_now()),
            quality_score=quality,
        )

    @staticmethod
    def _summarise_data(data: dict[str, Any]) -> str:
        """Produce a short human-readable summary from a step data dict."""
        if not data:
            return "no data"
        keys = list(data.keys())[:5]
        parts = []
        for k in keys:
            v = data[k]
            if isinstance(v, (int, float)):
                parts.append(f"{k}={v}")
            elif isinstance(v, str):
                parts.append(f"{k}={v[:60]}")
            elif isinstance(v, list):
                parts.append(f"{k}=[{len(v)} items]")
            else:
                parts.append(f"{k}=...")
        return "; ".join(parts)

    # ------------------------------------------------------------------
    # Tip extraction
    # ------------------------------------------------------------------

    def extract_tips(self, trajectory: Trajectory) -> list[MemoryTip]:
        """Analyse a single trajectory and extract strategy/recovery/optimization tips."""
        tips: list[MemoryTip] = []

        # --- Strategy tips: successful runs with high quality ---
        if trajectory.outcome == "success":
            tip = self._extract_strategy_tip(trajectory)
            if tip is not None:
                tips.append(tip)

        # --- Recovery tips: runs containing failure->success transitions ---
        recovery_tip = self._extract_recovery_tip(trajectory)
        if recovery_tip is not None:
            tips.append(recovery_tip)

        # --- Optimization tips: successful but potentially inefficient ---
        opt_tip = self._extract_optimization_tip(trajectory)
        if opt_tip is not None:
            tips.append(opt_tip)

        return tips

    def _extract_strategy_tip(self, trajectory: Trajectory) -> MemoryTip | None:
        """Extract the core strategy that led to success."""
        if trajectory.outcome != "success":
            return None

        # Identify the highest-value steps (ones with meaningful output)
        key_steps = [s for s in trajectory.steps if s.success and s.output_summary != "no data"]
        if not key_steps:
            return None

        step_names = [s.tool_name for s in key_steps]
        content = (
            f"Successful {trajectory.agent_name} run used steps: "
            f"{' -> '.join(step_names)}. "
            f"Task: {trajectory.task_description[:150]}"
        )

        confidence = trajectory.quality_score if trajectory.quality_score else 0.7

        # Derive domain from agent name
        domain = self._infer_domain(trajectory)

        return MemoryTip(
            id=_deterministic_id("tip", trajectory.run_id, "strategy"),
            tip_type="strategy",
            content=content,
            source_run_id=trajectory.run_id,
            source_agent=trajectory.agent_name,
            task_domain=domain,
            confidence=min(confidence, 1.0),
            created_at=trajectory.created_at,
            tags=["auto-extracted", "strategy"] + step_names[:3],
        )

    def _extract_recovery_tip(self, trajectory: Trajectory) -> MemoryTip | None:
        """Extract recovery pattern from failure->success transitions."""
        steps = trajectory.steps
        if len(steps) < 2:
            return None

        # Look for a failed step followed eventually by a successful step
        recovery_pairs: list[tuple[TrajectoryStep, TrajectoryStep]] = []
        for i, step in enumerate(steps):
            if not step.success:
                # Find next successful step
                for j in range(i + 1, len(steps)):
                    if steps[j].success:
                        recovery_pairs.append((step, steps[j]))
                        break

        if not recovery_pairs:
            return None

        failed_step, recovery_step = recovery_pairs[0]
        content = (
            f"Recovery pattern: after '{failed_step.tool_name}' failed, "
            f"'{recovery_step.tool_name}' recovered the run. "
            f"Failed step output: {failed_step.output_summary[:100]}. "
            f"Recovery output: {recovery_step.output_summary[:100]}."
        )

        domain = self._infer_domain(trajectory)

        return MemoryTip(
            id=_deterministic_id("tip", trajectory.run_id, "recovery"),
            tip_type="recovery",
            content=content,
            source_run_id=trajectory.run_id,
            source_agent=trajectory.agent_name,
            task_domain=domain,
            confidence=0.6,
            created_at=trajectory.created_at,
            tags=["auto-extracted", "recovery", failed_step.tool_name, recovery_step.tool_name],
        )

    def _extract_optimization_tip(self, trajectory: Trajectory) -> MemoryTip | None:
        """Extract optimization insight from successful but costly runs."""
        if trajectory.outcome != "success":
            return None

        # Flag runs with many steps (>= 4) or high token count as optimization candidates
        if len(trajectory.steps) < 4 and trajectory.total_tokens < 500:
            return None

        # Find the most expensive step
        if not trajectory.steps:
            return None

        most_expensive = max(trajectory.steps, key=lambda s: s.token_count)

        content = (
            f"Optimization opportunity in {trajectory.agent_name}: "
            f"run used {len(trajectory.steps)} steps and {trajectory.total_tokens} tokens. "
            f"Most expensive step: '{most_expensive.tool_name}' "
            f"({most_expensive.token_count} tokens). "
            f"Consider caching or pre-computing this step."
        )

        domain = self._infer_domain(trajectory)

        return MemoryTip(
            id=_deterministic_id("tip", trajectory.run_id, "optimization"),
            tip_type="optimization",
            content=content,
            source_run_id=trajectory.run_id,
            source_agent=trajectory.agent_name,
            task_domain=domain,
            confidence=0.5,
            created_at=trajectory.created_at,
            tags=["auto-extracted", "optimization", most_expensive.tool_name],
        )

    def classify_tip_type(self, trajectory: Trajectory, step_index: int) -> str:
        """Determine if a specific step represents strategy, recovery, or optimization."""
        steps = trajectory.steps
        if step_index < 0 or step_index >= len(steps):
            return "strategy"

        step = steps[step_index]

        # Recovery: step that follows a failed step
        if step_index > 0 and not steps[step_index - 1].success and step.success:
            return "recovery"

        # Optimization: step that is disproportionately expensive
        if len(steps) > 1:
            avg_tokens = trajectory.total_tokens / len(steps)
            if step.token_count > avg_tokens * 2:
                return "optimization"

        # Default: strategy
        return "strategy"

    @staticmethod
    def _infer_domain(trajectory: Trajectory) -> str:
        """Infer the task domain from agent name and task description."""
        agent = trajectory.agent_name.lower()
        desc = trajectory.task_description.lower()

        domain_keywords = {
            "simulation": ["simulated", "monte carlo", "simulation"],
            "decision": ["debate", "decision", "option", "recommend"],
            "finance": ["finance", "revenue", "burn", "runway"],
            "maturity": ["maturity", "benchmark", "eval"],
            "training": ["training", "job studio", "corpus"],
            "research": ["research", "analysis", "study"],
        }

        combined = f"{agent} {desc}"
        for domain, keywords in domain_keywords.items():
            if any(kw in combined for kw in keywords):
                return domain

        return "general"

    # ------------------------------------------------------------------
    # Batch extraction
    # ------------------------------------------------------------------

    def extract_all(self) -> list[MemoryTip]:
        """Process all trajectories and return extracted tips."""
        trajectories = self.load_trajectories()
        all_tips: list[MemoryTip] = []
        for traj in trajectories:
            tips = self.extract_tips(traj)
            all_tips.extend(tips)
        return all_tips
