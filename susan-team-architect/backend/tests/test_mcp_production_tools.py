"""Tests for the V5 Film & Image Studio MCP tools in server.py.

These tests exercise the MCP tool wrappers around ProductionEngine, verifying
JSON serialization, error handling, and tool registration.  The in-memory
singleton is reset for each test via a fresh ProductionEngine.
"""
from __future__ import annotations

import json
import sys
import types
from unittest.mock import patch

import pytest

# ── Fixtures ──────────────────────────────────────────────────

# The MCP server imports several heavy modules (rag_engine, control_plane,
# supabase) which may not be installed in every test environment.
# We stub out the imports that aren't needed for production-tool testing.

_STUB_MODULES = [
    "mcp",
    "mcp.server",
    "mcp.server.fastmcp",
    "rag_engine",
    "rag_engine.retriever",
    "rag_engine.ingestion",
    "rag_engine.ingestion.web",
    "control_plane",
    "control_plane.protocols",
    "supabase",
    "yaml",
]


class _FakeFastMCP:
    """Minimal stand-in for FastMCP that captures tool registrations."""

    def __init__(self, name: str = ""):
        self.name = name
        self._tools: dict[str, callable] = {}

    def tool(self):
        def decorator(fn):
            self._tools[fn.__name__] = fn
            return fn
        return decorator

    def run(self):
        pass


@pytest.fixture(autouse=True)
def _isolate_mcp_server(monkeypatch):
    """Provide a clean MCP server import with stubbed dependencies."""
    # Remove cached module if previously imported
    for mod in list(sys.modules):
        if mod.startswith("mcp_server"):
            del sys.modules[mod]

    # Stub heavy dependencies
    for mod_name in _STUB_MODULES:
        if mod_name not in sys.modules:
            monkeypatch.setitem(sys.modules, mod_name, types.ModuleType(mod_name))

    # Provide FastMCP on the stub
    fake_fastmcp = _FakeFastMCP
    sys.modules["mcp.server.fastmcp"].FastMCP = fake_fastmcp  # type: ignore[attr-defined]

    # Stub control_plane.protocols with dummy functions
    cp = sys.modules["control_plane.protocols"]
    for name in [
        "get_company_foundry_blueprint",
        "get_company_status",
        "get_team_manifest",
        "get_visual_assets",
        "maybe_model_route",
        "refresh_company_data",
        "route_company_task",
        "search_company_knowledge",
        "sync_project_protocols",
    ]:
        setattr(cp, name, lambda *a, **kw: None)

    # Stub rag_engine
    sys.modules["rag_engine.retriever"].Retriever = type("Retriever", (), {})  # type: ignore[attr-defined]
    sys.modules["rag_engine.ingestion.web"].WebIngestor = type("WebIngestor", (), {})  # type: ignore[attr-defined]

    # Stub yaml
    sys.modules["yaml"].safe_load = lambda f: {}  # type: ignore[attr-defined]

    yield

    # Cleanup
    for mod in list(sys.modules):
        if mod.startswith("mcp_server"):
            del sys.modules[mod]


def _import_server():
    """Import the server module with a fresh engine singleton."""
    import mcp_server.server as srv
    # Reset the singleton so each test is independent
    srv._production_engine = None
    return srv


# ── Tool registration tests ──────────────────────────────────


def test_all_v5_tools_registered():
    """All 6 V5 MCP tools are registered on the FastMCP instance."""
    srv = _import_server()
    tool_names = set(srv.mcp._tools.keys())
    v5_tools = {
        "orchestrate_production",
        "auto_run_production",
        "advance_production",
        "run_quality_gate",
        "route_generation_task",
        "production_legal_clearance",
    }
    for t in v5_tools:
        assert t in tool_names, f"V5 tool '{t}' not registered"


# ── orchestrate_production ───────────────────────────────────


def test_orchestrate_production_returns_json():
    srv = _import_server()
    engine = srv._get_production_engine()
    prod = engine.start("Test film", company_id="test", format="film")
    result = json.loads(srv.orchestrate_production(prod.production_id))
    assert result["phase"] == "design"
    assert "film-studio-director" in result["agents_assigned_this_phase"]
    assert result["next_phase"] == "storyboard"


def test_orchestrate_production_missing_id():
    srv = _import_server()
    result = json.loads(srv.orchestrate_production("nonexistent"))
    assert "error" in result


# ── auto_run_production ──────────────────────────────────────


def test_auto_run_production_returns_steps():
    srv = _import_server()
    engine = srv._get_production_engine()
    prod = engine.start("Auto film", company_id="test", format="film")
    result = json.loads(srv.auto_run_production(prod.production_id))
    assert "steps" in result
    assert len(result["steps"]) == 4
    assert result["steps"][0]["phase"] == "design"
    assert result["steps"][3]["phase"] == "refinement"


def test_auto_run_production_missing_id():
    srv = _import_server()
    result = json.loads(srv.auto_run_production("nonexistent"))
    assert "error" in result


# ── advance_production ───────────────────────────────────────


def test_advance_production_success():
    srv = _import_server()
    engine = srv._get_production_engine()
    prod = engine.start("Test", company_id="test", format="reel")
    result = json.loads(srv.advance_production(prod.production_id))
    assert result["new_phase"] == "storyboard"


def test_advance_production_quality_gate_error():
    srv = _import_server()
    engine = srv._get_production_engine()
    prod = engine.start("Test", company_id="test", format="film")
    for _ in range(3):
        engine.advance_phase(prod.production_id)
    # Should fail — gates not passed
    result = json.loads(srv.advance_production(prod.production_id))
    assert "error" in result


def test_advance_production_force():
    srv = _import_server()
    engine = srv._get_production_engine()
    prod = engine.start("Test", company_id="test", format="film")
    for _ in range(3):
        engine.advance_phase(prod.production_id)
    result = json.loads(srv.advance_production(prod.production_id, force=True))
    assert result["new_phase"] == "delivered"


def test_advance_production_missing_id():
    srv = _import_server()
    result = json.loads(srv.advance_production("nonexistent"))
    assert "error" in result


# ── run_quality_gate ─────────────────────────────────────────


def test_run_quality_gate_pass():
    srv = _import_server()
    engine = srv._get_production_engine()
    prod = engine.start("Test", company_id="test", format="film")
    result = json.loads(srv.run_quality_gate(prod.production_id, "resolution", 0.95))
    assert result["passed"] is True
    assert result["gate_name"] == "resolution"
    assert result["score"] == 0.95


def test_run_quality_gate_fail():
    srv = _import_server()
    engine = srv._get_production_engine()
    prod = engine.start("Test", company_id="test", format="film")
    result = json.loads(srv.run_quality_gate(prod.production_id, "resolution", 0.3, "Too low"))
    assert result["passed"] is False
    assert result["details"] == "Too low"


def test_run_quality_gate_invalid_gate():
    srv = _import_server()
    engine = srv._get_production_engine()
    prod = engine.start("Test", company_id="test", format="film")
    result = json.loads(srv.run_quality_gate(prod.production_id, "fake_gate", 0.9))
    assert "error" in result


# ── route_generation_task ────────────────────────────────────


def test_route_generation_task_image():
    srv = _import_server()
    result = json.loads(srv.route_generation_task("photorealistic"))
    assert result["recommended_tool"] == "Flux Pro 1.1 Ultra"
    assert result["engine"] == "image-gen-engine"


def test_route_generation_task_video():
    srv = _import_server()
    result = json.loads(srv.route_generation_task("dialogue_scene"))
    assert result["recommended_tool"] == "Sora 2"
    assert result["engine"] == "film-gen-engine"


def test_route_generation_task_audio():
    srv = _import_server()
    result = json.loads(srv.route_generation_task("voice_dialogue"))
    assert result["recommended_tool"] == "ElevenLabs"
    assert result["engine"] == "audio-gen-engine"


def test_route_generation_task_unknown():
    srv = _import_server()
    result = json.loads(srv.route_generation_task("nonexistent"))
    assert result["recommended_tool"] is None
    assert "error" in result
    assert "available_types" in result


# ── production_legal_clearance ───────────────────────────────


def test_production_legal_clearance_success():
    srv = _import_server()
    engine = srv._get_production_engine()
    prod = engine.start("Test", company_id="test", format="film")
    result = json.loads(srv.production_legal_clearance(
        prod.production_id, "music_track", "music_sync", "cleared", "Licensed"
    ))
    assert result["asset_name"] == "music_track"
    assert result["clearance_type"] == "music_sync"
    assert result["status"] == "cleared"


def test_production_legal_clearance_invalid_type():
    srv = _import_server()
    engine = srv._get_production_engine()
    prod = engine.start("Test", company_id="test", format="film")
    result = json.loads(srv.production_legal_clearance(
        prod.production_id, "asset", "invalid_type"
    ))
    assert "error" in result


def test_production_legal_clearance_missing_production():
    srv = _import_server()
    result = json.loads(srv.production_legal_clearance(
        "nonexistent", "asset", "copyright"
    ))
    assert "error" in result


# ── Integration: full MCP workflow ───────────────────────────


def test_mcp_full_production_workflow():
    """End-to-end: start → auto_run → quality gates → legal → advance to delivered."""
    srv = _import_server()
    engine = srv._get_production_engine()

    # Start production (using engine directly — start_production MCP tool tested separately)
    prod = engine.start("MCP workflow test", company_id="test", format="reel")

    # Auto-run to refinement
    run_result = json.loads(srv.auto_run_production(prod.production_id))
    assert len(run_result["steps"]) == 4

    # Run all quality gates via MCP tool (aspect_ratio threshold is 1.0)
    reel_gates = ["hook_impact", "aspect_ratio", "duration", "caption_safe", "audio_sync"]
    for gate in reel_gates:
        gate_result = json.loads(srv.run_quality_gate(prod.production_id, gate, 1.0))
        assert gate_result["passed"] is True

    # Add legal clearance via MCP tool
    legal_result = json.loads(srv.production_legal_clearance(
        prod.production_id, "all_assets", "copyright", "cleared"
    ))
    assert legal_result["status"] == "cleared"

    # Route a generation task
    route_result = json.loads(srv.route_generation_task("social_reels"))
    assert route_result["recommended_tool"] == "Runway Gen-4.5"

    # Advance to delivered
    advance_result = json.loads(srv.advance_production(prod.production_id))
    assert advance_result["new_phase"] == "delivered"
