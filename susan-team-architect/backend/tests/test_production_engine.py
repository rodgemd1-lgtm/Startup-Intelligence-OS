"""Tests for the production engine lifecycle manager."""
import pytest
from susan_core.production_engine import ProductionEngine, Production, ProductionStatus


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
    engine.advance_phase(prod.production_id)
    assert engine.get_status(prod.production_id)["phase"] == "delivered"


def test_advance_phase_at_delivered_stays():
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    for _ in range(4):
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
