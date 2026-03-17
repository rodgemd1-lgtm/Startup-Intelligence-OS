"""Predictive maturity modeling for the Collective Intelligence Framework.

Loads capability history from runs and capability records, estimates maturity
velocity, identifies blockers, predicts time-to-target, and produces optimal
build sequences using topological dependency analysis.
"""

from __future__ import annotations

import hashlib
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .schemas import CapabilityPrediction


def _deterministic_id(prefix: str, *parts: str) -> str:
    raw = ":".join(parts)
    digest = hashlib.sha256(raw.encode()).hexdigest()[:12]
    return f"{prefix}-{digest}"


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(ts: str) -> datetime | None:
    """Parse an ISO timestamp string. Returns None if unparseable."""
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d"):
        try:
            return datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue
    return None


class CapabilityPredictor:
    """Predicts maturity timelines and optimal build sequences for capabilities.

    Uses historical run data and capability records to estimate velocity,
    identify blockers, compute time-to-target, and produce a topologically
    sorted build sequence.
    """

    def __init__(self, workspace_root: Path, runs_dir: Path) -> None:
        self.workspace_root = workspace_root
        self.capabilities_dir = workspace_root / ".startup-os" / "capabilities"
        self.runs_dir = runs_dir
        self._capability_cache: dict[str, dict[str, Any]] | None = None
        self._dep_graph: dict[str, list[str]] | None = None

    # ------------------------------------------------------------------
    # Capability loading
    # ------------------------------------------------------------------

    def _load_capabilities(self) -> dict[str, dict[str, Any]]:
        """Load all capability YAML records indexed by id."""
        if self._capability_cache is not None:
            return self._capability_cache

        caps: dict[str, dict[str, Any]] = {}
        if not self.capabilities_dir.exists():
            self._capability_cache = caps
            return caps

        for yaml_path in sorted(self.capabilities_dir.glob("*.yaml")):
            if yaml_path.stem.endswith(".profile") or yaml_path.stem == "README":
                continue
            try:
                data = yaml.safe_load(yaml_path.read_text())
                if data and isinstance(data, dict) and "id" in data:
                    caps[data["id"]] = data
            except Exception:
                continue

        self._capability_cache = caps
        return caps

    # ------------------------------------------------------------------
    # History tracking
    # ------------------------------------------------------------------

    def load_capability_history(self, capability_id: str) -> list[dict[str, Any]]:
        """Read historical maturity data from runs and capability records.

        Scans run files for events referencing the capability and tracks
        maturity snapshots over time. Returns a list of dicts with keys:
        timestamp (str), maturity (float), run_id (str), event (str).
        """
        history: list[dict[str, Any]] = []

        # 1. Check the capability record itself for the current snapshot
        caps = self._load_capabilities()
        cap_data = caps.get(capability_id)
        if cap_data:
            history.append({
                "timestamp": _iso_now(),
                "maturity": float(cap_data.get("maturity_current", 0)),
                "run_id": "capability-record",
                "event": "current_state",
            })

        # 2. Scan run files for references to this capability
        if self.runs_dir.exists():
            for yaml_path in sorted(self.runs_dir.glob("run-*.yaml")):
                try:
                    data = yaml.safe_load(yaml_path.read_text())
                    if data is None or not isinstance(data, dict):
                        continue
                except Exception:
                    continue

                run_id = data.get("id", yaml_path.stem)
                run_cap = data.get("capability", "")
                trigger = data.get("trigger", "")
                started_at = data.get("started_at", "")

                # Check if this run relates to the capability
                if (
                    run_cap == capability_id
                    or capability_id in trigger
                    or capability_id in str(data.get("output", {}))
                ):
                    # Extract any maturity data from the run events
                    events = data.get("events") or []
                    for event in events:
                        event_data = event.get("data") or {}
                        timestamp = event.get("timestamp", started_at)

                        # Look for maturity references in event data
                        for key in ("maturity", "maturity_score", "current_maturity"):
                            if key in event_data:
                                history.append({
                                    "timestamp": timestamp,
                                    "maturity": float(event_data[key]),
                                    "run_id": run_id,
                                    "event": event.get("step", "unknown"),
                                })

        # Sort by timestamp
        history.sort(key=lambda h: h.get("timestamp", ""))
        return history

    # ------------------------------------------------------------------
    # Velocity estimation
    # ------------------------------------------------------------------

    def estimate_velocity(self, history: list[dict[str, Any]]) -> float:
        """Estimate maturity points gained per week from historical data.

        If fewer than 2 data points exist, uses a default velocity of 0.1
        points per week (conservative estimate).
        """
        if len(history) < 2:
            return 0.1  # Conservative default

        # Get earliest and latest data points
        earliest = history[0]
        latest = history[-1]

        ts_early = _parse_iso(earliest.get("timestamp", ""))
        ts_late = _parse_iso(latest.get("timestamp", ""))

        if ts_early is None or ts_late is None:
            return 0.1

        delta_weeks = (ts_late - ts_early).total_seconds() / (7 * 24 * 3600)
        if delta_weeks < 0.1:
            return 0.1  # Avoid division by near-zero

        maturity_gained = latest["maturity"] - earliest["maturity"]
        velocity = maturity_gained / delta_weeks

        # Clamp to reasonable range
        return max(0.01, min(velocity, 2.0))

    # ------------------------------------------------------------------
    # Blocker identification
    # ------------------------------------------------------------------

    def _build_dependency_graph(self) -> dict[str, list[str]]:
        """Build capability dependency graph from capability records.

        Looks for 'dependencies', 'linked_capabilities', or 'requires'
        fields in capability YAML.
        """
        if self._dep_graph is not None:
            return self._dep_graph

        caps = self._load_capabilities()
        graph: dict[str, list[str]] = {}

        for cap_id, data in caps.items():
            deps: list[str] = []

            # Check multiple possible dependency fields
            for field in ("dependencies", "linked_capabilities", "requires"):
                field_val = data.get(field, [])
                if isinstance(field_val, list):
                    deps.extend(field_val)

            graph[cap_id] = deps

        self._dep_graph = graph
        return graph

    def identify_blockers(self, capability_id: str) -> list[str]:
        """Find blockers for a capability: dependencies behind target, missing evidence, resource gaps."""
        blockers: list[str] = []
        caps = self._load_capabilities()
        cap_data = caps.get(capability_id)

        if not cap_data:
            blockers.append(f"Capability record not found for '{capability_id}'.")
            return blockers

        dep_graph = self._build_dependency_graph()
        current = float(cap_data.get("maturity_current", 0))
        target = float(cap_data.get("maturity_target", 0))

        # 1. Check dependencies that are behind
        deps = dep_graph.get(capability_id, [])
        for dep_id in deps:
            dep_data = caps.get(dep_id)
            if dep_data:
                dep_current = float(dep_data.get("maturity_current", 0))
                dep_target = float(dep_data.get("maturity_target", 0))
                if dep_current < dep_target:
                    blockers.append(
                        f"Dependency '{dep_data.get('name', dep_id)}' is at "
                        f"{dep_current:.1f}/{dep_target:.1f} maturity."
                    )

        # 2. Check for explicit gaps in the capability record
        gap_list = cap_data.get("gaps", [])
        if gap_list:
            for gap in gap_list:
                blockers.append(f"Knowledge gap: {gap}")

        # 3. Check for incomplete checklist items at the current level
        levels = cap_data.get("levels", {})
        current_level = int(math.ceil(current))
        level_data = levels.get(current_level, levels.get(str(current_level)))
        if level_data and isinstance(level_data, dict):
            items = level_data.get("items", [])
            incomplete = [
                item.get("text", "unknown")
                for item in items
                if isinstance(item, dict) and not item.get("done", False)
            ]
            if incomplete:
                blockers.append(
                    f"Level {current_level} has {len(incomplete)} incomplete items: "
                    + "; ".join(incomplete[:3])
                )

        # 4. Resource gaps based on maturity band
        if current < 1:
            blockers.append("Resource gap: needs initial scoping and definition work.")
        if target >= 4 and current < 3:
            blockers.append(
                "Resource gap: significant investment needed to reach optimizing maturity."
            )

        return blockers

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict(self, capability_id: str) -> CapabilityPrediction:
        """Generate a full maturity prediction for a capability.

        Computes current/target maturity, velocity from history, blockers from
        dependency analysis, weeks to target (with blocker adjustments), and
        confidence based on data quality and history length.
        """
        caps = self._load_capabilities()
        cap_data = caps.get(capability_id, {})

        name = cap_data.get("name", capability_id)
        current = float(cap_data.get("maturity_current", 0))
        target = float(cap_data.get("maturity_target", 0))
        gap = max(target - current, 0)

        # Load history and compute velocity
        history = self.load_capability_history(capability_id)
        velocity = self.estimate_velocity(history)

        # Identify blockers
        blockers = self.identify_blockers(capability_id)

        # Compute weeks to target with blocker adjustments
        if velocity > 0 and gap > 0:
            base_weeks = gap / velocity
            # Add penalty for blockers: each blocker adds 10-20% delay
            blocker_multiplier = 1.0 + (len(blockers) * 0.15)
            predicted_weeks = int(math.ceil(base_weeks * blocker_multiplier))
        elif gap <= 0:
            predicted_weeks = 0
        else:
            predicted_weeks = 52  # 1 year fallback for zero velocity

        # Compute confidence
        confidence = self._compute_confidence(history, blockers, gap)

        # Required resources based on gap and blockers
        required_resources = self._determine_resources(cap_data, gap, blockers)

        # Recommended sequence of actions
        recommended_sequence = self._recommend_sequence(cap_data, current, target, blockers)

        return CapabilityPrediction(
            capability_id=capability_id,
            capability_name=name,
            current_maturity=current,
            target_maturity=target,
            predicted_weeks_to_target=predicted_weeks,
            confidence=confidence,
            blockers=blockers,
            required_resources=required_resources,
            recommended_sequence=recommended_sequence,
            predicted_at=_iso_now(),
        )

    @staticmethod
    def _compute_confidence(
        history: list[dict[str, Any]],
        blockers: list[str],
        gap: float,
    ) -> float:
        """Compute prediction confidence from data quality and context.

        Factors:
        - More history data points -> higher confidence
        - Fewer blockers -> higher confidence
        - Smaller gap -> higher confidence
        """
        # Base confidence from history length
        data_confidence = min(len(history) / 10.0, 0.5)

        # Blocker penalty: each blocker reduces confidence by 0.05
        blocker_penalty = min(len(blockers) * 0.05, 0.3)

        # Gap penalty: larger gaps are harder to predict
        gap_penalty = min(gap * 0.05, 0.2)

        confidence = 0.5 + data_confidence - blocker_penalty - gap_penalty
        return round(max(0.05, min(confidence, 0.95)), 2)

    @staticmethod
    def _determine_resources(
        cap_data: dict[str, Any], gap: float, blockers: list[str]
    ) -> list[str]:
        """Determine required resources based on gap size and blockers."""
        resources: list[str] = []
        owner = cap_data.get("owner_agent", "")

        if owner:
            resources.append(f"Primary agent: {owner}")

        if gap >= 3:
            resources.append("Dedicated research program for knowledge gaps")
            resources.append("Cross-functional agent collaboration")
        elif gap >= 2:
            resources.append("Targeted research on specific gaps")
            resources.append("Regular progress reviews")
        elif gap >= 1:
            resources.append("Focused execution on checklist items")

        # Check for dependency-related blockers
        dep_blockers = [b for b in blockers if b.startswith("Dependency")]
        if dep_blockers:
            resources.append("Resolve dependency bottlenecks first")

        knowledge_blockers = [b for b in blockers if "Knowledge gap" in b]
        if knowledge_blockers:
            resources.append("Research program to close knowledge gaps")

        return resources

    @staticmethod
    def _recommend_sequence(
        cap_data: dict[str, Any],
        current: float,
        target: float,
        blockers: list[str],
    ) -> list[str]:
        """Generate a recommended sequence of actions."""
        sequence: list[str] = []

        # Always start with resolving blockers
        dep_blockers = [b for b in blockers if b.startswith("Dependency")]
        if dep_blockers:
            sequence.append("Resolve dependency blockers")

        # Walk through maturity bands
        current_band = int(math.floor(current))
        target_band = int(math.ceil(target))

        band_actions = {
            0: "Define scope and foundational vocabulary",
            1: "Document processes and gather examples",
            2: "Establish metrics and measurement frameworks",
            3: "Implement optimization and automation",
            4: "Pursue industry-leading practices and innovation",
        }

        for band in range(current_band, min(target_band, 5)):
            action = band_actions.get(band)
            if action:
                sequence.append(action)

        # Check for incomplete items at current level
        levels = cap_data.get("levels", {})
        current_level = int(math.ceil(current))
        level_data = levels.get(current_level, levels.get(str(current_level)))
        if level_data and isinstance(level_data, dict):
            items = level_data.get("items", [])
            incomplete = [
                item.get("text", "")
                for item in items
                if isinstance(item, dict) and not item.get("done", False)
            ]
            for item_text in incomplete[:3]:
                if item_text:
                    sequence.append(f"Complete: {item_text[:100]}")

        return sequence

    # ------------------------------------------------------------------
    # Batch predictions
    # ------------------------------------------------------------------

    def predict_all(self) -> list[CapabilityPrediction]:
        """Generate predictions for all capabilities with a maturity gap."""
        caps = self._load_capabilities()
        predictions: list[CapabilityPrediction] = []

        for cap_id, data in caps.items():
            current = float(data.get("maturity_current", 0))
            target = float(data.get("maturity_target", 0))
            if target > current:
                prediction = self.predict(cap_id)
                predictions.append(prediction)

        # Sort by predicted weeks ascending (closest to completion first)
        predictions.sort(key=lambda p: p.predicted_weeks_to_target)
        return predictions

    # ------------------------------------------------------------------
    # Optimal build sequence
    # ------------------------------------------------------------------

    def optimal_build_sequence(
        self, predictions: list[CapabilityPrediction]
    ) -> list[str]:
        """Topological sort of capabilities considering dependencies and impact.

        Capabilities that unblock others come first.
        Higher impact per effort comes first within tiers.
        """
        dep_graph = self._build_dependency_graph()
        caps = self._load_capabilities()

        # Build reverse dependency map: which capabilities are blocked by each
        blocked_by: dict[str, list[str]] = defaultdict(list)
        for cap_id, deps in dep_graph.items():
            for dep in deps:
                blocked_by[dep].append(cap_id)

        # Create a map from capability ID to prediction
        pred_map: dict[str, CapabilityPrediction] = {
            p.capability_id: p for p in predictions
        }

        # Score each capability:
        # - Number of capabilities it unblocks (higher = earlier)
        # - Gap size / predicted weeks = impact per effort (higher = earlier)
        scored: list[tuple[str, float]] = []
        for pred in predictions:
            unblocks_count = len(blocked_by.get(pred.capability_id, []))
            gap = pred.target_maturity - pred.current_maturity
            effort = max(pred.predicted_weeks_to_target, 1)
            impact_per_effort = gap / effort

            # Combined score: unblock bonus + impact per effort
            score = (unblocks_count * 10.0) + impact_per_effort
            scored.append((pred.capability_id, score))

        # Sort by score descending (highest priority first)
        scored.sort(key=lambda x: x[1], reverse=True)

        # Topological adjustment: ensure dependencies come before dependents
        ordered: list[str] = []
        visited: set[str] = set()

        def visit(cap_id: str) -> None:
            if cap_id in visited:
                return
            visited.add(cap_id)
            # Visit dependencies first
            for dep in dep_graph.get(cap_id, []):
                if dep in pred_map:
                    visit(dep)
            ordered.append(cap_id)

        for cap_id, _ in scored:
            visit(cap_id)

        return ordered

    # ------------------------------------------------------------------
    # Forecast reporting
    # ------------------------------------------------------------------

    def format_forecast(self, predictions: list[CapabilityPrediction]) -> str:
        """Generate a markdown forecast report."""
        lines: list[str] = [
            "# Capability Maturity Forecast",
            "",
            f"**Generated:** {_iso_now()}",
            f"**Capabilities tracked:** {len(predictions)}",
            "",
            "## Predictions",
            "",
            "| Capability | Current | Target | Gap | Weeks | Confidence | Blockers |",
            "|------------|---------|--------|-----|-------|------------|----------|",
        ]

        for pred in predictions:
            gap = pred.target_maturity - pred.current_maturity
            blocker_count = len(pred.blockers)
            lines.append(
                f"| {pred.capability_name} "
                f"| {pred.current_maturity:.1f} "
                f"| {pred.target_maturity:.1f} "
                f"| {gap:.1f} "
                f"| {pred.predicted_weeks_to_target} "
                f"| {pred.confidence:.0%} "
                f"| {blocker_count} |"
            )

        # Optimal build sequence
        sequence = self.optimal_build_sequence(predictions)
        if sequence:
            lines.extend([
                "",
                "## Recommended Build Sequence",
                "",
            ])
            for idx, cap_id in enumerate(sequence, 1):
                pred = next(
                    (p for p in predictions if p.capability_id == cap_id), None
                )
                name = pred.capability_name if pred else cap_id
                weeks = pred.predicted_weeks_to_target if pred else "?"
                lines.append(f"{idx}. **{name}** -- estimated {weeks} weeks")

        # Blocker summary
        all_blockers: list[str] = []
        for pred in predictions:
            for blocker in pred.blockers:
                if blocker not in all_blockers:
                    all_blockers.append(blocker)

        if all_blockers:
            lines.extend([
                "",
                "## Active Blockers",
                "",
            ])
            for blocker in all_blockers:
                lines.append(f"- {blocker}")

        return "\n".join(lines)
