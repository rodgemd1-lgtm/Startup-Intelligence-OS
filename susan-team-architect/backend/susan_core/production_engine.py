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

    # ── V5: AI-directed multi-agent orchestration ─────────────

    # Agent assignments per format and phase
    _AGENT_ROSTER: dict[str, dict[str, list[str]]] = {
        "film": {
            "design": ["film-studio-director", "screenwriter-studio", "cinematography-studio", "production-designer-studio"],
            "storyboard": ["screenwriter-studio", "cinematography-studio", "image-gen-engine", "production-manager-studio"],
            "generation": ["film-gen-engine", "audio-gen-engine", "vfx-studio"],
            "refinement": ["editing-studio", "color-grade-studio", "sound-design-studio", "music-score-studio"],
        },
        "reel": {
            "design": ["film-studio-director", "instagram-studio", "cinematography-studio"],
            "storyboard": ["screenwriter-studio", "cinematography-studio", "image-gen-engine"],
            "generation": ["film-gen-engine", "audio-gen-engine"],
            "refinement": ["editing-studio", "color-grade-studio", "sound-design-studio"],
        },
        "photo": {
            "design": ["film-studio-director", "photography-studio", "production-designer-studio"],
            "storyboard": ["photography-studio", "image-gen-engine"],
            "generation": ["image-gen-engine"],
            "refinement": ["photography-studio", "color-grade-studio"],
        },
        "carousel": {
            "design": ["film-studio-director", "instagram-studio", "production-designer-studio"],
            "storyboard": ["screenwriter-studio", "image-gen-engine"],
            "generation": ["image-gen-engine"],
            "refinement": ["editing-studio", "color-grade-studio"],
        },
        "image": {
            "design": ["film-studio-director", "cinematography-studio", "production-designer-studio"],
            "storyboard": ["cinematography-studio", "image-gen-engine"],
            "generation": ["image-gen-engine"],
            "refinement": ["color-grade-studio"],
        },
        "documentary": {
            "design": ["film-studio-director", "screenwriter-studio", "cinematography-studio"],
            "storyboard": ["screenwriter-studio", "cinematography-studio", "production-manager-studio"],
            "generation": ["film-gen-engine", "audio-gen-engine"],
            "refinement": ["editing-studio", "color-grade-studio", "sound-design-studio"],
        },
    }

    def orchestrate(self, production_id: str) -> dict[str, Any]:
        """AI-directed orchestration: auto-assign agents for the current phase.

        Returns the orchestration plan with agent assignments and instructions
        for the current phase.
        """
        prod = self._productions[production_id]
        roster = self._AGENT_ROSTER.get(prod.format, self._AGENT_ROSTER.get("image", {}))
        phase_agents = roster.get(prod.status.value, [])

        # Auto-assign agents for this phase (avoid duplicates)
        new_agents = [a for a in phase_agents if a not in prod.agents_assigned]
        if new_agents:
            prod.agents_assigned.extend(new_agents)

        # Build phase-specific instructions
        phase_instructions = {
            "design": (
                "Run design session: brief intake, reference gathering, "
                "look & feel lock, brand system generation."
            ),
            "storyboard": (
                "Generate storyboard: script/beat sheet, shot list with "
                "tool assignments, visual storyboard frames."
            ),
            "generation": (
                "Execute generation: route each shot to optimal AI tool "
                "via engine routing logic, generate all assets."
            ),
            "refinement": (
                "Post-production: editing, color grading, sound design, "
                "VFX. Then run all quality gates before delivery."
            ),
            "delivered": "Production complete. Run final review.",
        }

        return {
            "production_id": prod.production_id,
            "phase": prod.status.value,
            "format": prod.format,
            "agents_assigned_this_phase": new_agents,
            "all_agents": prod.agents_assigned,
            "instruction": phase_instructions.get(prod.status.value, ""),
            "next_phase": (
                _PHASE_ORDER[_PHASE_ORDER.index(prod.status) + 1].value
                if _PHASE_ORDER.index(prod.status) < len(_PHASE_ORDER) - 1
                else None
            ),
        }

    def auto_run(self, production_id: str) -> list[dict[str, Any]]:
        """Fully autonomous production run: orchestrate all phases.

        Advances through design → storyboard → generation → refinement,
        assigning agents at each phase. Does NOT advance to delivered
        (quality gates must be satisfied first).
        """
        steps: list[dict[str, Any]] = []
        prod = self._productions[production_id]

        while prod.status != ProductionStatus.REFINEMENT:
            plan = self.orchestrate(production_id)
            steps.append(plan)
            if prod.status == ProductionStatus.DELIVERED:
                break
            self.advance_phase(production_id)

        # Orchestrate refinement phase (but don't auto-advance past it)
        if prod.status == ProductionStatus.REFINEMENT:
            plan = self.orchestrate(production_id)
            steps.append(plan)

        return steps

    # ── V5: Tool routing logic ────────────────────────────────

    _TOOL_ROUTING: dict[str, dict[str, str]] = {
        # Image generation routing
        "photorealistic": "Flux Pro 1.1 Ultra",
        "concept_art": "Midjourney v7",
        "text_heavy": "Ideogram 3.0",
        "brand_consistent": "Recraft V3",
        "product_photography": "Flux Pro 1.1 Ultra",
        "rapid_iteration": "DALL-E 3",
        "commercial_safe": "Adobe Firefly Image 3",
        "enhancement": "Topaz Photo AI",
        "inpainting": "Stable Diffusion 3.5 Large",
        # Video generation routing
        "dialogue_scene": "Sora 2",
        "long_establishing": "Veo 3.1",
        "character_lock": "Runway Gen-4.5",
        "simultaneous_audio_video": "Veo 3.1",
        "4k_delivery": "Sora 2",
        "budget_batch": "Kling 3.0",
        "camera_movement": "Runway Gen-4.5",
        "talking_head": "Synthesia",
        "social_reels": "Runway Gen-4.5",
        "upscaling": "Topaz Video AI",
        # Audio routing
        "voice_dialogue": "ElevenLabs",
        "voice_multilingual": "ElevenLabs",
        "voice_low_latency": "Cartesia",
        "music_orchestral": "AIVA",
        "music_pop": "Suno",
        "music_commercial_safe": "AIVA",
        "sfx_foley": "ElevenLabs SFX",
        "audio_repair": "iZotope RX 11",
        "stem_separation": "LALAL.AI",
    }

    def route_to_tool(self, task_type: str) -> dict[str, Any]:
        """Route a generation task to the optimal AI tool.

        Args:
            task_type: Key from the routing table (e.g., 'photorealistic',
                       'dialogue_scene', 'music_orchestral')

        Returns:
            dict with recommended_tool, task_type, and available alternatives.
        """
        tool = self._TOOL_ROUTING.get(task_type)
        if tool is None:
            # Find closest match category
            categories = {
                "image": [k for k in self._TOOL_ROUTING if k in (
                    "photorealistic", "concept_art", "text_heavy", "brand_consistent",
                    "product_photography", "rapid_iteration", "commercial_safe",
                    "enhancement", "inpainting",
                )],
                "video": [k for k in self._TOOL_ROUTING if k in (
                    "dialogue_scene", "long_establishing", "character_lock",
                    "simultaneous_audio_video", "4k_delivery", "budget_batch",
                    "camera_movement", "talking_head", "social_reels", "upscaling",
                )],
                "audio": [k for k in self._TOOL_ROUTING if k in (
                    "voice_dialogue", "voice_multilingual", "voice_low_latency",
                    "music_orchestral", "music_pop", "music_commercial_safe",
                    "sfx_foley", "audio_repair", "stem_separation",
                )],
            }
            return {
                "task_type": task_type,
                "recommended_tool": None,
                "error": f"Unknown task type '{task_type}'",
                "available_types": categories,
            }

        return {
            "task_type": task_type,
            "recommended_tool": tool,
            "engine": (
                "image-gen-engine" if task_type in (
                    "photorealistic", "concept_art", "text_heavy", "brand_consistent",
                    "product_photography", "rapid_iteration", "commercial_safe",
                    "enhancement", "inpainting",
                )
                else "film-gen-engine" if task_type in (
                    "dialogue_scene", "long_establishing", "character_lock",
                    "simultaneous_audio_video", "4k_delivery", "budget_batch",
                    "camera_movement", "talking_head", "social_reels", "upscaling",
                )
                else "audio-gen-engine"
            ),
        }

    # ── V5: Legal clearance workflow ──────────────────────────

    def add_legal_clearance(
        self,
        production_id: str,
        asset_name: str,
        clearance_type: str,
        status: str = "pending",
        notes: str = "",
    ) -> dict[str, Any]:
        """Add a legal clearance record for a production asset.

        Args:
            production_id: The production to add clearance to
            asset_name: Name/description of the asset
            clearance_type: Type — copyright, trademark, likeness, music_sync,
                            music_master, talent_consent, ai_disclosure
            status: pending, cleared, blocked, or waived
            notes: Additional context
        """
        prod = self._productions[production_id]
        valid_types = {
            "copyright", "trademark", "likeness", "music_sync",
            "music_master", "talent_consent", "ai_disclosure",
        }
        if clearance_type not in valid_types:
            raise ValueError(
                f"Invalid clearance type '{clearance_type}'. "
                f"Valid: {', '.join(sorted(valid_types))}"
            )
        valid_statuses = {"pending", "cleared", "blocked", "waived"}
        if status not in valid_statuses:
            raise ValueError(
                f"Invalid status '{status}'. Valid: {', '.join(sorted(valid_statuses))}"
            )
        record = {
            "asset_name": asset_name,
            "clearance_type": clearance_type,
            "status": status,
            "notes": notes,
        }
        # Store clearances as a special output type
        prod.outputs.append({"type": "legal_clearance", **record})
        return record

    def legal_clearance_summary(self, production_id: str) -> dict[str, Any]:
        """Return summary of all legal clearances for a production."""
        prod = self._productions[production_id]
        clearances = [o for o in prod.outputs if o.get("type") == "legal_clearance"]

        by_status: dict[str, list[str]] = {
            "pending": [],
            "cleared": [],
            "blocked": [],
            "waived": [],
        }
        for c in clearances:
            by_status[c["status"]].append(f"{c['asset_name']} ({c['clearance_type']})")

        all_resolved = (
            len(by_status["pending"]) == 0
            and len(by_status["blocked"]) == 0
        )

        return {
            "production_id": production_id,
            "total_clearances": len(clearances),
            "all_resolved": all_resolved,
            "by_status": by_status,
            "can_deliver": all_resolved and len(clearances) > 0,
        }
