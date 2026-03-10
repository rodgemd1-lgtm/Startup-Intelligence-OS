"""Tests for the production engine lifecycle manager, quality gates, V5 orchestration, and persistence."""
from __future__ import annotations

from unittest.mock import MagicMock, patch, call

import pytest
from susan_core.production_engine import (
    ProductionEngine,
    Production,
    ProductionStatus,
    QualityGateConfig,
    QualityGateError,
    QualityGateResult,
)
from susan_core.production_store import ProductionStore


# ── V3 Core lifecycle tests ──────────────────────────────────


def test_start_production():
    engine = ProductionEngine()
    prod = engine.start("Hero video for TransformFit website", company_id="transformfit", format="film")
    assert prod.production_id is not None
    assert prod.status == ProductionStatus.DESIGN
    assert prod.company_id == "transformfit"
    assert prod.format == "film"


def test_list_productions():
    engine = ProductionEngine()
    engine.start("Reel 1", company_id="transformfit", format="reel")
    engine.start("Reel 2", company_id="transformfit", format="reel")
    engine.start("Photo set", company_id="founder-intelligence-os", format="photo")
    assert len(engine.list_productions("transformfit")) == 2
    assert len(engine.list_productions("founder-intelligence-os")) == 1


def test_production_status():
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="reel")
    status = engine.get_status(prod.production_id)
    assert status["phase"] == "design"
    assert status["agents_assigned"] == []


def test_advance_phase():
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    engine.advance_phase(prod.production_id)
    assert engine.get_status(prod.production_id)["phase"] == "storyboard"
    engine.advance_phase(prod.production_id)
    assert engine.get_status(prod.production_id)["phase"] == "generation"
    engine.advance_phase(prod.production_id)
    assert engine.get_status(prod.production_id)["phase"] == "refinement"
    # Must pass quality gates before delivered — pass them all
    for gate in engine.get_quality_gates(prod.production_id):
        engine.run_quality_gate(prod.production_id, gate.gate_name, 1.0)
    engine.advance_phase(prod.production_id)
    assert engine.get_status(prod.production_id)["phase"] == "delivered"


def test_advance_phase_at_delivered_stays():
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    for _ in range(3):
        engine.advance_phase(prod.production_id)
    # Pass quality gates for refinement → delivered
    for gate in engine.get_quality_gates(prod.production_id):
        engine.run_quality_gate(prod.production_id, gate.gate_name, 1.0)
    engine.advance_phase(prod.production_id)
    # Advancing past delivered should stay at delivered
    result = engine.advance_phase(prod.production_id)
    assert result == ProductionStatus.DELIVERED


def test_assign_agents():
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    engine.assign_agents(prod.production_id, ["film-studio-director", "screenwriter-studio", "cinematography-studio"])
    status = engine.get_status(prod.production_id)
    assert len(status["agents_assigned"]) == 3
    assert "film-studio-director" in status["agents_assigned"]


def test_add_output():
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="reel")
    engine.add_output(prod.production_id, {"type": "shot_list", "shots": 12})
    status = engine.get_status(prod.production_id)
    assert len(status["outputs"]) == 1
    assert status["outputs"][0]["type"] == "shot_list"


def test_get_status_missing_raises():
    engine = ProductionEngine()
    with pytest.raises(KeyError):
        engine.get_status("nonexistent-id")


def test_multi_tenant_isolation():
    engine = ProductionEngine()
    engine.start("TF Reel", company_id="transformfit", format="reel")
    engine.start("FIO Doc", company_id="founder-intelligence-os", format="documentary")
    engine.start("OHA Photo", company_id="oracle-health-ai", format="photo")
    assert len(engine.list_productions("transformfit")) == 1
    assert len(engine.list_productions("founder-intelligence-os")) == 1
    assert len(engine.list_productions("oracle-health-ai")) == 1
    assert len(engine.list_productions("nonexistent")) == 0


# ── V4 Quality gate definition tests ─────────────────────────


def test_quality_gates_defined_for_all_formats():
    """Every supported format has quality gates defined."""
    engine = ProductionEngine()
    formats = ["film", "reel", "photo", "carousel", "image", "documentary"]
    for fmt in formats:
        prod = engine.start(f"Test {fmt}", company_id="test", format=fmt)
        gates = engine.get_quality_gates(prod.production_id)
        assert len(gates) >= 3, f"Format '{fmt}' should have at least 3 quality gates"


def test_quality_gate_configs_valid():
    """All quality gate configs have valid thresholds and names."""
    engine = ProductionEngine()
    for fmt in ["film", "reel", "photo", "carousel", "image", "documentary"]:
        prod = engine.start(f"Test {fmt}", company_id="test", format=fmt)
        for gate in engine.get_quality_gates(prod.production_id):
            assert 0.0 < gate.threshold <= 1.0, f"{gate.gate_name} threshold out of range"
            assert gate.gate_name, "Gate name must not be empty"
            assert gate.description, "Gate description must not be empty"


# ── V4 Quality gate execution tests ──────────────────────────


def test_run_quality_gate_pass():
    """A score at or above threshold passes the gate."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    result = engine.run_quality_gate(prod.production_id, "resolution", 0.95)
    assert result.passed is True
    assert result.score == 0.95
    assert result.gate_name == "resolution"


def test_run_quality_gate_exact_threshold():
    """A score exactly at threshold passes."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    # Film resolution threshold is 0.8
    result = engine.run_quality_gate(prod.production_id, "resolution", 0.8)
    assert result.passed is True


def test_run_quality_gate_fail():
    """A score below threshold fails the gate."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    result = engine.run_quality_gate(prod.production_id, "resolution", 0.5, "Low resolution output")
    assert result.passed is False
    assert result.score == 0.5
    assert result.details == "Low resolution output"


def test_run_quality_gate_unknown_raises():
    """Running an undefined gate for a format raises ValueError."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    with pytest.raises(ValueError, match="Unknown quality gate"):
        engine.run_quality_gate(prod.production_id, "nonexistent_gate", 0.9)


def test_run_quality_gate_replaces_prior():
    """Re-running the same gate replaces the prior result."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    engine.run_quality_gate(prod.production_id, "resolution", 0.5)
    engine.run_quality_gate(prod.production_id, "resolution", 0.95, "Fixed")
    summary = engine.quality_gate_summary(prod.production_id)
    resolution_results = [g for g in summary["gates"] if g["gate"] == "resolution"]
    assert len(resolution_results) == 1
    assert resolution_results[0]["result"]["score"] == 0.95
    assert resolution_results[0]["result"]["passed"] is True


# ── V4 Quality gate summary tests ────────────────────────────


def test_quality_gate_summary_empty():
    """Summary with no results shows all gates as pending."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="photo")
    summary = engine.quality_gate_summary(prod.production_id)
    assert summary["gates_run"] == 0
    assert summary["gates_total"] == 4  # photo has 4 gates
    assert summary["all_passed"] is False
    for gate in summary["gates"]:
        assert gate["result"] is None


def test_quality_gate_summary_partial():
    """Summary with some results shows mix of completed and pending."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="photo")
    engine.run_quality_gate(prod.production_id, "resolution", 0.95)
    engine.run_quality_gate(prod.production_id, "composition", 0.8)
    summary = engine.quality_gate_summary(prod.production_id)
    assert summary["gates_run"] == 2
    assert summary["gates_total"] == 4
    assert summary["all_passed"] is False  # 2 pending


def test_quality_gate_summary_all_passed():
    """Summary with all gates passed."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="photo")
    for gate in engine.get_quality_gates(prod.production_id):
        engine.run_quality_gate(prod.production_id, gate.gate_name, 1.0)
    summary = engine.quality_gate_summary(prod.production_id)
    assert summary["all_passed"] is True
    assert summary["gates_run"] == summary["gates_total"]


# ── V4 Phase advancement + quality gate integration ──────────


def test_can_advance_non_refinement_always_true():
    """Quality gates only block refinement → delivered."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    # Design → storyboard: no gates needed
    can, reason = engine.can_advance(prod.production_id)
    assert can is True


def test_can_advance_refinement_blocked_no_gates_run():
    """Refinement → delivered blocked when no gates have been run."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    # Advance to refinement
    for _ in range(3):
        engine.advance_phase(prod.production_id)
    assert prod.status == ProductionStatus.REFINEMENT
    can, reason = engine.can_advance(prod.production_id)
    assert can is False
    assert "Pending" in reason


def test_can_advance_refinement_blocked_failing_gates():
    """Refinement → delivered blocked when gates are failing."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    for _ in range(3):
        engine.advance_phase(prod.production_id)
    # Fail one gate, pass the rest
    gates = engine.get_quality_gates(prod.production_id)
    engine.run_quality_gate(prod.production_id, gates[0].gate_name, 0.1)
    for gate in gates[1:]:
        engine.run_quality_gate(prod.production_id, gate.gate_name, 1.0)
    can, reason = engine.can_advance(prod.production_id)
    assert can is False
    assert "Failing" in reason


def test_can_advance_refinement_passes_all_gates():
    """Refinement → delivered succeeds when all gates pass."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="reel")
    for _ in range(3):
        engine.advance_phase(prod.production_id)
    for gate in engine.get_quality_gates(prod.production_id):
        engine.run_quality_gate(prod.production_id, gate.gate_name, 1.0)
    can, reason = engine.can_advance(prod.production_id)
    assert can is True


def test_advance_phase_raises_quality_gate_error():
    """advance_phase raises QualityGateError when gates block."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    for _ in range(3):
        engine.advance_phase(prod.production_id)
    with pytest.raises(QualityGateError):
        engine.advance_phase(prod.production_id)


def test_advance_phase_force_bypasses_gates():
    """advance_phase with force=True bypasses quality gates."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    for _ in range(3):
        engine.advance_phase(prod.production_id)
    # Force advancement without passing gates
    result = engine.advance_phase(prod.production_id, force=True)
    assert result == ProductionStatus.DELIVERED


# ── V4 End-to-end film production workflow ────────────────────


def test_e2e_film_production_workflow():
    """Full film production lifecycle: design → storyboard → generation → refinement → delivered."""
    engine = ProductionEngine()

    # Phase 1: DESIGN — start production, assign creative direction agents
    prod = engine.start(
        "TransformFit hero brand video — 60s cinematic fitness journey",
        company_id="transformfit",
        format="film",
    )
    assert prod.status == ProductionStatus.DESIGN

    engine.assign_agents(prod.production_id, [
        "film-studio-director",
        "screenwriter-studio",
        "cinematography-studio",
        "production-designer-studio",
    ])
    engine.add_output(prod.production_id, {
        "type": "design_brief",
        "visual_language": "cinematic dark, high-contrast, slow-motion fitness",
        "color_palette": ["#1a1a2e", "#16213e", "#0f3460", "#e94560"],
    })

    # Phase 2: STORYBOARD — advance and add storyboard outputs
    engine.advance_phase(prod.production_id)
    assert prod.status == ProductionStatus.STORYBOARD

    engine.assign_agents(prod.production_id, [
        "image-gen-engine",
        "production-manager-studio",
    ])
    engine.add_output(prod.production_id, {
        "type": "shot_list",
        "shots": 18,
        "duration_seconds": 60,
    })
    engine.add_output(prod.production_id, {
        "type": "storyboard",
        "frames": 18,
        "tool_assignments": {
            "establishing_shot": "Sora 2",
            "close_up_action": "Runway Gen-4.5",
            "slow_motion": "Veo 3.1",
        },
    })

    # Phase 3: GENERATION — advance and generate assets
    engine.advance_phase(prod.production_id)
    assert prod.status == ProductionStatus.GENERATION

    engine.assign_agents(prod.production_id, [
        "film-gen-engine",
        "audio-gen-engine",
    ])
    engine.add_output(prod.production_id, {
        "type": "generated_clips",
        "clips": 18,
        "tools_used": ["Sora 2", "Runway Gen-4.5", "Veo 3.1"],
    })
    engine.add_output(prod.production_id, {
        "type": "audio_assets",
        "voiceover": "ElevenLabs",
        "music": "AIVA",
        "sfx": "ElevenLabs SFX",
    })

    # Phase 4: REFINEMENT — advance, run post-production, run quality gates
    engine.advance_phase(prod.production_id)
    assert prod.status == ProductionStatus.REFINEMENT

    engine.assign_agents(prod.production_id, [
        "editing-studio",
        "color-grade-studio",
        "sound-design-studio",
        "vfx-studio",
    ])
    engine.add_output(prod.production_id, {
        "type": "final_edit",
        "duration_seconds": 62,
        "resolution": "4K",
        "color_space": "Rec.709",
    })

    # Run all quality gates
    gate_scores = {
        "physics_plausibility": 0.85,
        "character_consistency": 0.78,
        "motion_quality": 0.92,
        "audio_sync": 0.96,
        "resolution": 0.95,
        "continuity": 0.82,
    }
    for gate_name, score in gate_scores.items():
        result = engine.run_quality_gate(prod.production_id, gate_name, score)
        assert result.passed is True, f"Gate {gate_name} should pass with score {score}"

    # Verify quality summary
    summary = engine.quality_gate_summary(prod.production_id)
    assert summary["all_passed"] is True
    assert summary["gates_run"] == 6
    assert summary["gates_total"] == 6

    # Phase 5: DELIVERED — advance to final state
    engine.advance_phase(prod.production_id)
    assert prod.status == ProductionStatus.DELIVERED

    # Final verification
    status = engine.get_status(prod.production_id)
    assert status["phase"] == "delivered"
    assert len(status["agents_assigned"]) == 12  # 4 design + 2 storyboard + 2 generation + 4 refinement
    assert len(status["outputs"]) == 6  # All outputs recorded
    assert status["quality_gates"]["all_passed"] is True


# ── V4 End-to-end Instagram batch production workflow ─────────


def test_e2e_instagram_batch_workflow():
    """Instagram batch production: calendar → batch create → quality check → deliver."""
    engine = ProductionEngine()

    # Start 4 reel productions (1 week batch)
    productions = []
    briefs = [
        "Educational: 5 exercises for desk workers — hook with shocking posture stat",
        "Behind-the-scenes: AI workout generation demo — hook with transformation",
        "Social proof: User transformation story — hook with before/after",
        "Promotional: Free trial CTA — hook with time-limited offer urgency",
    ]
    for brief in briefs:
        prod = engine.start(brief, company_id="transformfit", format="reel")
        productions.append(prod)

    assert len(engine.list_productions("transformfit")) == 4

    # Assign instagram-studio to all
    for prod in productions:
        engine.assign_agents(prod.production_id, [
            "instagram-studio",
            "film-studio-director",
        ])

    # Move all through design and storyboard
    for prod in productions:
        engine.advance_phase(prod.production_id)  # → storyboard
        engine.add_output(prod.production_id, {
            "type": "reel_script",
            "hook_type": "pattern_interrupt",
            "duration_target": 45,
        })
        engine.advance_phase(prod.production_id)  # → generation
        engine.assign_agents(prod.production_id, [
            "film-gen-engine",
            "audio-gen-engine",
        ])
        engine.add_output(prod.production_id, {
            "type": "generated_reel",
            "tool": "Runway Gen-4.5",
            "resolution": "1080x1920",
        })
        engine.advance_phase(prod.production_id)  # → refinement
        engine.assign_agents(prod.production_id, ["editing-studio"])

    # Run quality gates on all productions
    reel_gates = {
        "hook_impact": 0.88,
        "aspect_ratio": 1.0,
        "duration": 0.95,
        "caption_safe": 0.85,
        "audio_sync": 0.92,
    }
    for prod in productions:
        for gate_name, score in reel_gates.items():
            engine.run_quality_gate(prod.production_id, gate_name, score)

    # All should pass quality gates
    for prod in productions:
        can, reason = engine.can_advance(prod.production_id)
        assert can is True, f"Production {prod.production_id} should pass: {reason}"

    # Deliver all
    for prod in productions:
        engine.advance_phase(prod.production_id)
        assert prod.status == ProductionStatus.DELIVERED

    # Verify batch delivery
    delivered = [
        p for p in engine.list_productions("transformfit")
        if p.status == ProductionStatus.DELIVERED
    ]
    assert len(delivered) == 4


# ── V4 Multi-tenant concurrent production tests ──────────────


def test_multi_tenant_concurrent_productions():
    """3+ companies running productions simultaneously with complete isolation."""
    engine = ProductionEngine()

    # Company 1: TransformFit — film + reel batch
    tf_film = engine.start(
        "TransformFit hero video", company_id="transformfit", format="film"
    )
    tf_reel = engine.start(
        "TransformFit weekly reel", company_id="transformfit", format="reel"
    )

    # Company 2: Founder Intelligence OS — documentary
    fio_doc = engine.start(
        "Founder Intelligence OS product demo", company_id="founder-intelligence-os", format="documentary"
    )

    # Company 3: Oracle Health AI — photo set + carousel
    oha_photo = engine.start(
        "Oracle Health AI product photography", company_id="oracle-health-ai", format="photo"
    )
    oha_carousel = engine.start(
        "Oracle Health AI feature carousel", company_id="oracle-health-ai", format="carousel"
    )

    # Verify isolation
    assert len(engine.list_productions("transformfit")) == 2
    assert len(engine.list_productions("founder-intelligence-os")) == 1
    assert len(engine.list_productions("oracle-health-ai")) == 2

    # Advance each at different rates
    engine.assign_agents(tf_film.production_id, ["film-studio-director", "cinematography-studio"])
    engine.advance_phase(tf_film.production_id)  # → storyboard
    engine.advance_phase(tf_film.production_id)  # → generation

    engine.assign_agents(fio_doc.production_id, ["film-studio-director", "screenwriter-studio"])
    engine.advance_phase(fio_doc.production_id)  # → storyboard

    engine.assign_agents(oha_photo.production_id, ["photography-studio", "image-gen-engine"])
    engine.advance_phase(oha_photo.production_id)  # → storyboard
    engine.advance_phase(oha_photo.production_id)  # → generation
    engine.advance_phase(oha_photo.production_id)  # → refinement

    # TF reel stays in design
    assert tf_reel.status == ProductionStatus.DESIGN
    # TF film in generation
    assert tf_film.status == ProductionStatus.GENERATION
    # FIO doc in storyboard
    assert fio_doc.status == ProductionStatus.STORYBOARD
    # OHA photo in refinement
    assert oha_photo.status == ProductionStatus.REFINEMENT
    # OHA carousel in design
    assert oha_carousel.status == ProductionStatus.DESIGN

    # Quality gates on OHA photo — pass all
    for gate in engine.get_quality_gates(oha_photo.production_id):
        engine.run_quality_gate(oha_photo.production_id, gate.gate_name, 0.95)
    engine.advance_phase(oha_photo.production_id)  # → delivered
    assert oha_photo.status == ProductionStatus.DELIVERED

    # Other productions unaffected
    assert tf_film.status == ProductionStatus.GENERATION
    assert fio_doc.status == ProductionStatus.STORYBOARD
    assert tf_reel.status == ProductionStatus.DESIGN

    # Quality gates on one company don't leak to another
    oha_summary = engine.quality_gate_summary(oha_photo.production_id)
    assert oha_summary["all_passed"] is True
    tf_summary = engine.quality_gate_summary(tf_film.production_id)
    assert tf_summary["gates_run"] == 0  # TF film has no gate results yet


def test_multi_tenant_different_quality_gates():
    """Different formats across tenants have their own quality gate definitions."""
    engine = ProductionEngine()

    tf_reel = engine.start("TF reel", company_id="transformfit", format="reel")
    fio_film = engine.start("FIO film", company_id="founder-intelligence-os", format="film")
    oha_photo = engine.start("OHA photo", company_id="oracle-health-ai", format="photo")

    reel_gates = {g.gate_name for g in engine.get_quality_gates(tf_reel.production_id)}
    film_gates = {g.gate_name for g in engine.get_quality_gates(fio_film.production_id)}
    photo_gates = {g.gate_name for g in engine.get_quality_gates(oha_photo.production_id)}

    # Each format has different gates
    assert "hook_impact" in reel_gates
    assert "hook_impact" not in film_gates
    assert "hook_impact" not in photo_gates

    assert "physics_plausibility" in film_gates
    assert "physics_plausibility" not in reel_gates

    assert "composition" in photo_gates
    assert "composition" not in film_gates


# ── V4 Status includes quality gates ─────────────────────────


def test_get_status_includes_quality_gates():
    """get_status returns quality gate summary in response."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="image")
    status = engine.get_status(prod.production_id)
    assert "quality_gates" in status
    assert status["quality_gates"]["gates_total"] == 6  # image has 6 gates
    assert status["quality_gates"]["gates_run"] == 0


def test_unknown_format_has_no_gates():
    """A format with no defined gates has empty gate list."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="custom_format")
    gates = engine.get_quality_gates(prod.production_id)
    assert gates == []
    # Can advance through refinement freely (no gates to check)
    for _ in range(3):
        engine.advance_phase(prod.production_id)
    assert prod.status == ProductionStatus.REFINEMENT
    can, _ = engine.can_advance(prod.production_id)
    assert can is True


# ═══════════════════════════════════════════════════════════════
# V5 — Hollywood-Grade Autonomous tests
# ═══════════════════════════════════════════════════════════════


# ── V5: AI-directed multi-agent orchestration ─────────────────


def test_orchestrate_assigns_correct_agents_for_film():
    """orchestrate() assigns format- and phase-specific agents."""
    engine = ProductionEngine()
    prod = engine.start("Test film", company_id="test", format="film")
    plan = engine.orchestrate(prod.production_id)
    assert plan["phase"] == "design"
    assert "film-studio-director" in plan["agents_assigned_this_phase"]
    assert "screenwriter-studio" in plan["agents_assigned_this_phase"]
    assert "cinematography-studio" in plan["agents_assigned_this_phase"]
    assert "production-designer-studio" in plan["agents_assigned_this_phase"]
    assert plan["next_phase"] == "storyboard"


def test_orchestrate_assigns_correct_agents_for_reel():
    """Reel format gets instagram-studio in design phase."""
    engine = ProductionEngine()
    prod = engine.start("Test reel", company_id="test", format="reel")
    plan = engine.orchestrate(prod.production_id)
    assert "instagram-studio" in plan["agents_assigned_this_phase"]
    assert "film-studio-director" in plan["agents_assigned_this_phase"]


def test_orchestrate_no_duplicate_agents():
    """Calling orchestrate twice doesn't duplicate agent assignments."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    engine.orchestrate(prod.production_id)
    plan2 = engine.orchestrate(prod.production_id)
    assert plan2["agents_assigned_this_phase"] == []
    # But all_agents still has them
    assert len(plan2["all_agents"]) == 4


def test_orchestrate_different_agents_per_phase():
    """Each phase gets its own set of agents."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")

    design_plan = engine.orchestrate(prod.production_id)
    engine.advance_phase(prod.production_id)

    storyboard_plan = engine.orchestrate(prod.production_id)
    assert storyboard_plan["phase"] == "storyboard"
    assert "image-gen-engine" in storyboard_plan["agents_assigned_this_phase"]
    assert "production-manager-studio" in storyboard_plan["agents_assigned_this_phase"]


def test_auto_run_film_production():
    """auto_run advances through all phases to refinement."""
    engine = ProductionEngine()
    prod = engine.start("Full auto film", company_id="test", format="film")
    steps = engine.auto_run(prod.production_id)

    # Should have 4 steps: design, storyboard, generation, refinement
    assert len(steps) == 4
    assert steps[0]["phase"] == "design"
    assert steps[1]["phase"] == "storyboard"
    assert steps[2]["phase"] == "generation"
    assert steps[3]["phase"] == "refinement"

    # Production should be in refinement (not delivered — gates needed)
    assert prod.status == ProductionStatus.REFINEMENT

    # All phase agents should be assigned
    assert "film-studio-director" in prod.agents_assigned
    assert "film-gen-engine" in prod.agents_assigned
    assert "editing-studio" in prod.agents_assigned


def test_auto_run_photo_production():
    """auto_run works for photo format with fewer agents."""
    engine = ProductionEngine()
    prod = engine.start("Product photos", company_id="test", format="photo")
    steps = engine.auto_run(prod.production_id)
    assert len(steps) == 4
    assert prod.status == ProductionStatus.REFINEMENT
    assert "photography-studio" in prod.agents_assigned
    assert "image-gen-engine" in prod.agents_assigned


def test_orchestrate_all_formats_have_agents():
    """Every defined format has agent assignments for all phases."""
    engine = ProductionEngine()
    formats = ["film", "reel", "photo", "carousel", "image", "documentary"]
    for fmt in formats:
        prod = engine.start(f"Test {fmt}", company_id="test", format=fmt)
        for phase in ["design", "storyboard", "generation", "refinement"]:
            agents = engine._AGENT_ROSTER.get(fmt, {}).get(phase, [])
            assert len(agents) >= 1, f"Format '{fmt}' phase '{phase}' has no agents"


# ── V5: Tool routing logic validation ─────────────────────────


def test_route_image_tools():
    """Image generation routing returns correct tools."""
    engine = ProductionEngine()
    assert engine.route_to_tool("photorealistic")["recommended_tool"] == "Flux Pro 1.1 Ultra"
    assert engine.route_to_tool("concept_art")["recommended_tool"] == "Midjourney v7"
    assert engine.route_to_tool("text_heavy")["recommended_tool"] == "Ideogram 3.0"
    assert engine.route_to_tool("brand_consistent")["recommended_tool"] == "Recraft V3"
    assert engine.route_to_tool("commercial_safe")["recommended_tool"] == "Adobe Firefly Image 3"


def test_route_video_tools():
    """Video generation routing returns correct tools."""
    engine = ProductionEngine()
    assert engine.route_to_tool("dialogue_scene")["recommended_tool"] == "Sora 2"
    assert engine.route_to_tool("long_establishing")["recommended_tool"] == "Veo 3.1"
    assert engine.route_to_tool("character_lock")["recommended_tool"] == "Runway Gen-4.5"
    assert engine.route_to_tool("budget_batch")["recommended_tool"] == "Kling 3.0"
    assert engine.route_to_tool("talking_head")["recommended_tool"] == "Synthesia"


def test_route_audio_tools():
    """Audio generation routing returns correct tools."""
    engine = ProductionEngine()
    assert engine.route_to_tool("voice_dialogue")["recommended_tool"] == "ElevenLabs"
    assert engine.route_to_tool("music_orchestral")["recommended_tool"] == "AIVA"
    assert engine.route_to_tool("music_pop")["recommended_tool"] == "Suno"
    assert engine.route_to_tool("sfx_foley")["recommended_tool"] == "ElevenLabs SFX"
    assert engine.route_to_tool("audio_repair")["recommended_tool"] == "iZotope RX 11"


def test_route_returns_correct_engine():
    """Routing returns the correct engine for each domain."""
    engine = ProductionEngine()
    assert engine.route_to_tool("photorealistic")["engine"] == "image-gen-engine"
    assert engine.route_to_tool("dialogue_scene")["engine"] == "film-gen-engine"
    assert engine.route_to_tool("voice_dialogue")["engine"] == "audio-gen-engine"


def test_route_unknown_returns_error():
    """Unknown task type returns error with available types."""
    engine = ProductionEngine()
    result = engine.route_to_tool("nonexistent_task")
    assert result["recommended_tool"] is None
    assert "error" in result
    assert "available_types" in result
    assert "image" in result["available_types"]
    assert "video" in result["available_types"]
    assert "audio" in result["available_types"]


def test_all_routing_entries_resolve():
    """Every entry in the routing table resolves to a tool and engine."""
    engine = ProductionEngine()
    for task_type in engine._TOOL_ROUTING:
        result = engine.route_to_tool(task_type)
        assert result["recommended_tool"] is not None, f"Task '{task_type}' has no tool"
        assert result["engine"] in ("image-gen-engine", "film-gen-engine", "audio-gen-engine")


# ── V5: Legal clearance workflow ──────────────────────────────


def test_add_legal_clearance():
    """Add a legal clearance record to a production."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    record = engine.add_legal_clearance(
        prod.production_id,
        "hero_music_track",
        "music_sync",
        "cleared",
        "Licensed via AIVA Pro — full ownership",
    )
    assert record["asset_name"] == "hero_music_track"
    assert record["clearance_type"] == "music_sync"
    assert record["status"] == "cleared"


def test_legal_clearance_invalid_type_raises():
    """Invalid clearance type raises ValueError."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    with pytest.raises(ValueError, match="Invalid clearance type"):
        engine.add_legal_clearance(prod.production_id, "asset", "invalid_type")


def test_legal_clearance_invalid_status_raises():
    """Invalid clearance status raises ValueError."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    with pytest.raises(ValueError, match="Invalid status"):
        engine.add_legal_clearance(
            prod.production_id, "asset", "copyright", "invalid_status"
        )


def test_legal_clearance_summary_all_cleared():
    """Summary shows all resolved when every clearance is cleared/waived."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    engine.add_legal_clearance(prod.production_id, "music_track", "music_sync", "cleared")
    engine.add_legal_clearance(prod.production_id, "music_master", "music_master", "cleared")
    engine.add_legal_clearance(prod.production_id, "voice_clone", "talent_consent", "cleared")
    engine.add_legal_clearance(prod.production_id, "ai_generated", "ai_disclosure", "waived")

    summary = engine.legal_clearance_summary(prod.production_id)
    assert summary["all_resolved"] is True
    assert summary["can_deliver"] is True
    assert summary["total_clearances"] == 4
    assert len(summary["by_status"]["cleared"]) == 3
    assert len(summary["by_status"]["waived"]) == 1


def test_legal_clearance_summary_has_pending():
    """Summary shows not resolved when pending clearances exist."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    engine.add_legal_clearance(prod.production_id, "music", "music_sync", "cleared")
    engine.add_legal_clearance(prod.production_id, "likeness", "likeness", "pending")

    summary = engine.legal_clearance_summary(prod.production_id)
    assert summary["all_resolved"] is False
    assert summary["can_deliver"] is False


def test_legal_clearance_summary_has_blocked():
    """Summary shows not resolved when blocked clearances exist."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    engine.add_legal_clearance(prod.production_id, "stock_footage", "copyright", "blocked", "Licensing dispute")

    summary = engine.legal_clearance_summary(prod.production_id)
    assert summary["all_resolved"] is False
    assert summary["can_deliver"] is False
    assert len(summary["by_status"]["blocked"]) == 1


def test_legal_clearance_summary_empty():
    """Summary with no clearances returns can_deliver=False."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    summary = engine.legal_clearance_summary(prod.production_id)
    assert summary["total_clearances"] == 0
    assert summary["can_deliver"] is False  # No clearances means not deliverable


# ── V5: Full autonomous production with legal clearance ───────


def test_e2e_v5_autonomous_film_with_legal():
    """V5 full autonomous: auto_run + tool routing + legal clearance + quality gates."""
    engine = ProductionEngine()

    # Start production
    prod = engine.start(
        "TransformFit brand anthem — 90s cinematic fitness journey",
        company_id="transformfit",
        format="film",
    )

    # Auto-run through all phases to refinement
    steps = engine.auto_run(prod.production_id)
    assert len(steps) == 4
    assert prod.status == ProductionStatus.REFINEMENT

    # Route specific generation tasks to optimal tools
    hero_shot = engine.route_to_tool("dialogue_scene")
    assert hero_shot["recommended_tool"] == "Sora 2"

    slow_mo = engine.route_to_tool("long_establishing")
    assert slow_mo["recommended_tool"] == "Veo 3.1"

    music = engine.route_to_tool("music_orchestral")
    assert music["recommended_tool"] == "AIVA"

    # Add legal clearances
    engine.add_legal_clearance(prod.production_id, "hero_music", "music_sync", "cleared", "AIVA Pro full ownership")
    engine.add_legal_clearance(prod.production_id, "hero_music_master", "music_master", "cleared", "AIVA Pro full ownership")
    engine.add_legal_clearance(prod.production_id, "voiceover", "talent_consent", "cleared", "ElevenLabs PVC consent signed")
    engine.add_legal_clearance(prod.production_id, "ai_generated_footage", "ai_disclosure", "cleared", "Disclosed in credits")
    engine.add_legal_clearance(prod.production_id, "brand_assets", "trademark", "cleared", "TransformFit owns all marks")
    engine.add_legal_clearance(prod.production_id, "all_footage", "copyright", "cleared", "AI-generated, company owns")

    legal = engine.legal_clearance_summary(prod.production_id)
    assert legal["all_resolved"] is True
    assert legal["can_deliver"] is True

    # Pass quality gates
    for gate in engine.get_quality_gates(prod.production_id):
        engine.run_quality_gate(prod.production_id, gate.gate_name, 0.9)

    # Deliver
    engine.advance_phase(prod.production_id)
    assert prod.status == ProductionStatus.DELIVERED

    # Final checks
    status = engine.get_status(prod.production_id)
    assert status["phase"] == "delivered"
    assert status["quality_gates"]["all_passed"] is True
    assert len(prod.agents_assigned) >= 10


# ── V5: External client capacity ──────────────────────────────


def test_external_client_capacity():
    """Arbitrary external companies can run full productions with isolation."""
    engine = ProductionEngine()

    # External client 1: Fitness brand
    client_a = engine.start(
        "FitLife hero video", company_id="fitlife-external", format="film"
    )
    steps_a = engine.auto_run(client_a.production_id)
    assert len(steps_a) == 4

    # External client 2: Restaurant
    client_b = engine.start(
        "TacoTuesday menu carousel", company_id="tacotuesday-external", format="carousel"
    )
    steps_b = engine.auto_run(client_b.production_id)
    assert len(steps_b) == 4

    # External client 3: Tech startup
    client_c = engine.start(
        "CodeShip product demo reel", company_id="codeship-external", format="reel"
    )
    steps_c = engine.auto_run(client_c.production_id)

    # Internal company running simultaneously
    internal = engine.start(
        "TransformFit monthly content", company_id="transformfit", format="reel"
    )
    engine.auto_run(internal.production_id)

    # All 4 companies isolated
    assert len(engine.list_productions("fitlife-external")) == 1
    assert len(engine.list_productions("tacotuesday-external")) == 1
    assert len(engine.list_productions("codeship-external")) == 1
    assert len(engine.list_productions("transformfit")) == 1

    # Each has correct format-specific agents
    assert "film-studio-director" in client_a.agents_assigned
    assert "instagram-studio" in client_b.agents_assigned or "production-designer-studio" in client_b.agents_assigned
    assert "instagram-studio" in client_c.agents_assigned

    # Quality gates are format-specific per client
    a_gates = {g.gate_name for g in engine.get_quality_gates(client_a.production_id)}
    b_gates = {g.gate_name for g in engine.get_quality_gates(client_b.production_id)}
    c_gates = {g.gate_name for g in engine.get_quality_gates(client_c.production_id)}

    assert "physics_plausibility" in a_gates  # film
    assert "slide_consistency" in b_gates     # carousel
    assert "hook_impact" in c_gates           # reel


def test_external_client_full_delivery():
    """External client can complete full production through delivery."""
    engine = ProductionEngine()

    prod = engine.start(
        "External brand video", company_id="acme-corp-external", format="film"
    )

    # Auto-run to refinement
    engine.auto_run(prod.production_id)
    assert prod.status == ProductionStatus.REFINEMENT

    # Add legal clearances
    engine.add_legal_clearance(prod.production_id, "all_assets", "copyright", "cleared")
    engine.add_legal_clearance(prod.production_id, "ai_content", "ai_disclosure", "cleared")

    # Pass quality gates (use 0.95 to exceed all thresholds including audio_sync=0.9)
    for gate in engine.get_quality_gates(prod.production_id):
        engine.run_quality_gate(prod.production_id, gate.gate_name, 0.95)

    # Deliver
    engine.advance_phase(prod.production_id)
    assert prod.status == ProductionStatus.DELIVERED

    # Verify no data leaks to other companies
    assert len(engine.list_productions("transformfit")) == 0
    assert len(engine.list_productions("acme-corp-external")) == 1


# ═══════════════════════════════════════════════════════════════
# V5 — Persistence layer tests (ProductionStore + engine integration)
# ═══════════════════════════════════════════════════════════════


# ── ProductionStore serialization round-trip ───────────────────


def test_production_store_to_row_basic():
    """_to_row serializes a Production to a DB-compatible dict."""
    prod = Production(
        production_id="prod-abc123",
        brief="Test brief",
        company_id="test-co",
        format="film",
        status=ProductionStatus.DESIGN,
        agents_assigned=["agent-a", "agent-b"],
        outputs=[{"type": "design_brief"}],
        quality_results=[
            QualityGateResult(gate_name="resolution", passed=True, score=0.95, details="Good"),
        ],
    )
    row = ProductionStore._to_row(prod)
    assert row["production_id"] == "prod-abc123"
    assert row["status"] == "design"
    assert row["agents_assigned"] == ["agent-a", "agent-b"]
    assert len(row["quality_results"]) == 1
    assert row["quality_results"][0]["gate_name"] == "resolution"
    assert row["quality_results"][0]["passed"] is True


def test_production_store_from_row_basic():
    """_from_row deserializes a DB row back to a Production."""
    row = {
        "production_id": "prod-xyz789",
        "brief": "Round-trip test",
        "company_id": "test-co",
        "format": "reel",
        "status": "storyboard",
        "agents_assigned": ["film-studio-director"],
        "outputs": [{"type": "shot_list", "shots": 12}],
        "quality_results": [
            {"gate_name": "hook_impact", "passed": True, "score": 0.88, "details": "Strong hook"},
        ],
    }
    prod = ProductionStore._from_row(row)
    assert prod.production_id == "prod-xyz789"
    assert prod.status == ProductionStatus.STORYBOARD
    assert prod.format == "reel"
    assert len(prod.agents_assigned) == 1
    assert len(prod.quality_results) == 1
    assert prod.quality_results[0].gate_name == "hook_impact"


def test_production_store_round_trip():
    """_to_row → _from_row preserves all fields."""
    original = Production(
        production_id="prod-rt001",
        brief="Round trip",
        company_id="test",
        format="photo",
        status=ProductionStatus.GENERATION,
        agents_assigned=["photography-studio", "image-gen-engine"],
        outputs=[
            {"type": "design_brief", "palette": ["#fff"]},
            {"type": "storyboard", "frames": 6},
        ],
        quality_results=[
            QualityGateResult("resolution", True, 0.95, "OK"),
            QualityGateResult("composition", False, 0.6, "Needs work"),
        ],
    )
    row = ProductionStore._to_row(original)
    restored = ProductionStore._from_row(row)

    assert restored.production_id == original.production_id
    assert restored.brief == original.brief
    assert restored.company_id == original.company_id
    assert restored.format == original.format
    assert restored.status == original.status
    assert restored.agents_assigned == original.agents_assigned
    assert restored.outputs == original.outputs
    assert len(restored.quality_results) == 2
    assert restored.quality_results[0].gate_name == "resolution"
    assert restored.quality_results[1].passed is False


def test_production_store_from_row_missing_optional_fields():
    """_from_row handles missing optional fields gracefully."""
    row = {
        "production_id": "prod-min",
        "brief": "Minimal",
        "company_id": "test",
        "format": "image",
        "status": "design",
    }
    prod = ProductionStore._from_row(row)
    assert prod.agents_assigned == []
    assert prod.outputs == []
    assert prod.quality_results == []


# ── Engine + store integration ────────────────────────────────


def _make_mock_store() -> MagicMock:
    """Create a mock ProductionStore with list_active returning empty."""
    store = MagicMock(spec=ProductionStore)
    store.list_active.return_value = []
    return store


def test_engine_with_store_saves_on_start():
    """Engine calls store.save() when a new production is started."""
    store = _make_mock_store()
    engine = ProductionEngine(store=store)
    prod = engine.start("Test", company_id="test", format="film")
    store.save.assert_called_once()
    saved_prod = store.save.call_args[0][0]
    assert saved_prod.production_id == prod.production_id


def test_engine_with_store_updates_status_on_advance():
    """Engine calls store.update_status() when phase advances."""
    store = _make_mock_store()
    engine = ProductionEngine(store=store)
    prod = engine.start("Test", company_id="test", format="reel")
    engine.advance_phase(prod.production_id)
    store.update_status.assert_called_once_with(prod.production_id, "storyboard")


def test_engine_with_store_updates_agents_on_assign():
    """Engine calls store.update_agents() when agents are assigned."""
    store = _make_mock_store()
    engine = ProductionEngine(store=store)
    prod = engine.start("Test", company_id="test", format="film")
    engine.assign_agents(prod.production_id, ["film-studio-director"])
    store.update_agents.assert_called_once_with(
        prod.production_id, ["film-studio-director"]
    )


def test_engine_with_store_persists_output():
    """Engine calls store.add_output() when output is added."""
    store = _make_mock_store()
    engine = ProductionEngine(store=store)
    prod = engine.start("Test", company_id="test", format="reel")
    output = {"type": "shot_list", "shots": 8}
    engine.add_output(prod.production_id, output)
    store.add_output.assert_called_once_with(prod.production_id, output)


def test_engine_with_store_persists_quality_result():
    """Engine calls store.add_quality_result() when a gate is run."""
    store = _make_mock_store()
    engine = ProductionEngine(store=store)
    prod = engine.start("Test", company_id="test", format="film")
    engine.run_quality_gate(prod.production_id, "resolution", 0.95, "Good")
    store.add_quality_result.assert_called_once()
    call_args = store.add_quality_result.call_args[0]
    assert call_args[0] == prod.production_id
    assert call_args[1]["gate_name"] == "resolution"
    assert call_args[1]["passed"] is True


def test_engine_with_store_orchestrate_persists_agents():
    """orchestrate() persists agent assignments through the store."""
    store = _make_mock_store()
    engine = ProductionEngine(store=store)
    prod = engine.start("Test", company_id="test", format="film")
    engine.orchestrate(prod.production_id)
    # store.update_agents called (once from orchestrate's direct extend)
    store.update_agents.assert_called()
    call_args = store.update_agents.call_args[0]
    assert call_args[0] == prod.production_id
    assert "film-studio-director" in call_args[1]


def test_engine_loads_from_store_on_init():
    """Engine loads active productions from store on initialization."""
    existing = Production(
        production_id="prod-existing",
        brief="Existing production",
        company_id="test",
        format="film",
        status=ProductionStatus.GENERATION,
        agents_assigned=["film-studio-director"],
    )
    store = MagicMock(spec=ProductionStore)
    store.list_active.return_value = [existing]

    engine = ProductionEngine(store=store)
    store.list_active.assert_called_once()

    # Should be able to access the loaded production
    status = engine.get_status("prod-existing")
    assert status["phase"] == "generation"
    assert status["company_id"] == "test"


def test_engine_without_store_works_normally():
    """Engine works without a store (backward compatibility)."""
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    engine.advance_phase(prod.production_id)
    engine.assign_agents(prod.production_id, ["agent-a"])
    engine.add_output(prod.production_id, {"type": "test"})
    engine.run_quality_gate(prod.production_id, "resolution", 0.9)
    # No errors — all in-memory operations work fine
    assert engine.get_status(prod.production_id)["phase"] == "storyboard"


def test_engine_store_failure_doesnt_crash():
    """Store failures are caught and logged, not propagated."""
    store = _make_mock_store()
    store.save.side_effect = Exception("Supabase down")
    store.update_status.side_effect = Exception("Supabase down")
    store.update_agents.side_effect = Exception("Supabase down")
    store.add_output.side_effect = Exception("Supabase down")
    store.add_quality_result.side_effect = Exception("Supabase down")

    engine = ProductionEngine(store=store)
    # All operations should succeed in-memory despite store failures
    prod = engine.start("Test", company_id="test", format="film")
    engine.advance_phase(prod.production_id)
    engine.assign_agents(prod.production_id, ["agent-a"])
    engine.add_output(prod.production_id, {"type": "test"})
    engine.run_quality_gate(prod.production_id, "resolution", 0.9)

    assert engine.get_status(prod.production_id)["phase"] == "storyboard"


def test_engine_store_init_failure_doesnt_crash():
    """If store.list_active fails on init, engine starts with empty state."""
    store = MagicMock(spec=ProductionStore)
    store.list_active.side_effect = Exception("Connection refused")
    engine = ProductionEngine(store=store)
    # Should have no productions
    assert engine.list_productions("any") == []
    # Should still work normally for new productions
    prod = engine.start("New", company_id="test", format="reel")
    assert prod.production_id is not None
