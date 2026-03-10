"""Tests for the production engine lifecycle manager and quality gate automation."""
import pytest
from susan_core.production_engine import (
    ProductionEngine,
    Production,
    ProductionStatus,
    QualityGateConfig,
    QualityGateError,
    QualityGateResult,
)


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
