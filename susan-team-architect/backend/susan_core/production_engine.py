"""Production engine — manages the lifecycle of film and image productions."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProductionStatus(str, Enum):
    DESIGN = "design"
    STORYBOARD = "storyboard"
    GENERATION = "generation"
    REFINEMENT = "refinement"
    DELIVERED = "delivered"


_PHASE_ORDER = [
    ProductionStatus.DESIGN,
    ProductionStatus.STORYBOARD,
    ProductionStatus.GENERATION,
    ProductionStatus.REFINEMENT,
    ProductionStatus.DELIVERED,
]


class QualityGateError(Exception):
    """Raised when a phase transition is blocked by quality gates."""

    def __init__(self, production_id: str, reason: str) -> None:
        self.production_id = production_id
        self.reason = reason
        super().__init__(f"Quality gate blocked for {production_id}: {reason}")


@dataclass
class QualityGateConfig:
    """Definition of a single quality gate."""

    gate_name: str
    engine_type: str
    threshold: float
    description: str


@dataclass
class QualityGateResult:
    """Result of running a quality gate check."""

    gate_name: str
    passed: bool
    score: float
    details: str = ""


@dataclass
class Production:
    production_id: str
    brief: str
    company_id: str
    format: str
    status: ProductionStatus = ProductionStatus.DESIGN
    agents_assigned: list[str] = field(default_factory=list)
    outputs: list[dict[str, Any]] = field(default_factory=list)
    quality_results: list[QualityGateResult] = field(default_factory=list)


# ── Default quality gates per format ──────────────────────────

_DEFAULT_QUALITY_GATES: dict[str, list[QualityGateConfig]] = {
    "film": [
        QualityGateConfig("physics_plausibility", "film", 0.7, "Physically plausible motion"),
        QualityGateConfig("character_consistency", "film", 0.7, "Character consistency across shots"),
        QualityGateConfig("motion_quality", "film", 0.8, "Smooth, natural motion"),
        QualityGateConfig("audio_sync", "film", 0.9, "Audio/video sync within tolerance"),
        QualityGateConfig("resolution", "film", 0.8, "Meets delivery resolution specs"),
        QualityGateConfig("continuity", "film", 0.7, "Visual continuity between shots"),
    ],
    "reel": [
        QualityGateConfig("hook_impact", "reel", 0.8, "First 1.7s hooks viewer"),
        QualityGateConfig("aspect_ratio", "reel", 1.0, "9:16 vertical format"),
        QualityGateConfig("duration", "reel", 0.9, "30-90 second range"),
        QualityGateConfig("caption_safe", "reel", 0.8, "Key elements in caption-safe zone"),
        QualityGateConfig("audio_sync", "reel", 0.9, "Audio/visual beat-matched"),
    ],
    "photo": [
        QualityGateConfig("resolution", "photo", 0.9, "Meets minimum resolution"),
        QualityGateConfig("composition", "photo", 0.7, "Rule of thirds / visual balance"),
        QualityGateConfig("color_accuracy", "photo", 0.8, "Color within brand tolerance"),
        QualityGateConfig("artifact_check", "photo", 0.9, "No visible AI artifacts"),
    ],
    "carousel": [
        QualityGateConfig("slide_consistency", "carousel", 0.8, "Visual consistency across slides"),
        QualityGateConfig("text_legibility", "carousel", 0.9, "Text readable at mobile size"),
        QualityGateConfig("aspect_ratio", "carousel", 1.0, "1:1 or 4:5 format"),
        QualityGateConfig("brand_compliance", "carousel", 0.7, "Matches brand visual language"),
    ],
    "image": [
        QualityGateConfig("resolution", "image", 0.8, "Minimum resolution check"),
        QualityGateConfig("character_consistency", "image", 0.7, "Character consistency across outputs"),
        QualityGateConfig("text_legibility", "image", 0.9, "Text readable at target size"),
        QualityGateConfig("artifact_check", "image", 0.8, "No visible AI artifacts"),
        QualityGateConfig("brand_compliance", "image", 0.7, "Matches brand visual language"),
        QualityGateConfig("style_consistency", "image", 0.8, "Consistent style across outputs"),
    ],
    "documentary": [
        QualityGateConfig("narrative_clarity", "documentary", 0.8, "Clear narrative arc"),
        QualityGateConfig("audio_quality", "documentary", 0.9, "Clean dialogue audio"),
        QualityGateConfig("resolution", "documentary", 0.8, "Meets delivery resolution"),
        QualityGateConfig("fact_check", "documentary", 0.9, "Claims and data verified"),
    ],
}


class ProductionEngine:
    """In-memory production lifecycle manager with quality gate automation."""

    def __init__(self) -> None:
        self._productions: dict[str, Production] = {}
        self._quality_gates: dict[str, list[QualityGateConfig]] = dict(_DEFAULT_QUALITY_GATES)

    # ── Production lifecycle ──────────────────────────────────

    def start(
        self,
        brief: str,
        company_id: str,
        format: str,
        title: str | None = None,
    ) -> Production:
        prod_id = f"prod-{uuid.uuid4().hex[:12]}"
        prod = Production(
            production_id=prod_id,
            brief=brief,
            company_id=company_id,
            format=format,
        )
        self._productions[prod_id] = prod
        return prod

    def list_productions(self, company_id: str) -> list[Production]:
        return [p for p in self._productions.values() if p.company_id == company_id]

    def get_status(self, production_id: str) -> dict[str, Any]:
        prod = self._productions[production_id]
        return {
            "production_id": prod.production_id,
            "brief": prod.brief,
            "company_id": prod.company_id,
            "format": prod.format,
            "phase": prod.status.value,
            "agents_assigned": prod.agents_assigned,
            "outputs": prod.outputs,
            "quality_gates": self.quality_gate_summary(production_id),
        }

    def advance_phase(
        self, production_id: str, force: bool = False
    ) -> ProductionStatus:
        """Advance production to the next phase.

        Quality gates are enforced on the refinement → delivered transition
        unless *force* is True.
        """
        prod = self._productions[production_id]
        if not force:
            can, reason = self.can_advance(production_id)
            if not can:
                raise QualityGateError(production_id, reason)
        idx = _PHASE_ORDER.index(prod.status)
        if idx < len(_PHASE_ORDER) - 1:
            prod.status = _PHASE_ORDER[idx + 1]
        return prod.status

    def assign_agents(self, production_id: str, agent_ids: list[str]) -> None:
        self._productions[production_id].agents_assigned.extend(agent_ids)

    def add_output(self, production_id: str, output: dict[str, Any]) -> None:
        self._productions[production_id].outputs.append(output)

    # ── Quality gate automation ───────────────────────────────

    def get_quality_gates(self, production_id: str) -> list[QualityGateConfig]:
        """Return quality gates applicable to this production's format."""
        prod = self._productions[production_id]
        return list(self._quality_gates.get(prod.format, []))

    def run_quality_gate(
        self,
        production_id: str,
        gate_name: str,
        score: float,
        details: str = "",
    ) -> QualityGateResult:
        """Record a quality gate result for a production.

        The *score* (0.0–1.0) is compared against the gate's threshold.
        """
        prod = self._productions[production_id]
        gates = {g.gate_name: g for g in self._quality_gates.get(prod.format, [])}
        gate_config = gates.get(gate_name)
        if gate_config is None:
            raise ValueError(
                f"Unknown quality gate '{gate_name}' for format '{prod.format}'"
            )
        passed = score >= gate_config.threshold
        result = QualityGateResult(
            gate_name=gate_name,
            passed=passed,
            score=score,
            details=details,
        )
        # Replace any prior result for the same gate
        prod.quality_results = [
            r for r in prod.quality_results if r.gate_name != gate_name
        ]
        prod.quality_results.append(result)
        return result

    def quality_gate_summary(self, production_id: str) -> dict[str, Any]:
        """Return a summary of quality gate status for a production."""
        prod = self._productions[production_id]
        gates = self._quality_gates.get(prod.format, [])
        results = {r.gate_name: r for r in prod.quality_results}

        gate_details = []
        for g in gates:
            r = results.get(g.gate_name)
            gate_details.append(
                {
                    "gate": g.gate_name,
                    "threshold": g.threshold,
                    "description": g.description,
                    "result": {
                        "score": r.score,
                        "passed": r.passed,
                        "details": r.details,
                    }
                    if r
                    else None,
                }
            )

        return {
            "production_id": production_id,
            "format": prod.format,
            "gates": gate_details,
            "all_passed": all(
                g.gate_name in results and results[g.gate_name].passed
                for g in gates
            ),
            "gates_run": len(results),
            "gates_total": len(gates),
        }

    def can_advance(self, production_id: str) -> tuple[bool, str]:
        """Check if the production may advance to the next phase.

        Quality gates are only enforced on the refinement → delivered
        transition.  All other transitions pass unconditionally.
        """
        prod = self._productions[production_id]
        if prod.status != ProductionStatus.REFINEMENT:
            return True, "Quality gates not required for this phase transition"

        summary = self.quality_gate_summary(production_id)
        if summary["all_passed"]:
            return True, "All quality gates passed"

        failing = [
            g["gate"]
            for g in summary["gates"]
            if g["result"] is not None and not g["result"]["passed"]
        ]
        pending = [g["gate"] for g in summary["gates"] if g["result"] is None]

        parts: list[str] = []
        if failing:
            parts.append(f"Failing: {', '.join(failing)}")
        if pending:
            parts.append(f"Pending: {', '.join(pending)}")
        return False, "; ".join(parts)
