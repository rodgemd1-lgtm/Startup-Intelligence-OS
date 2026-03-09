import json

from fastapi.testclient import TestClient

from control_plane.main import app
from control_plane.protocols import route_company_task, sync_project_target


def test_route_company_task_prefers_studio_and_oracle_marketing(monkeypatch):
    monkeypatch.setattr(
        "control_plane.protocols.search_company_knowledge",
        lambda *args, **kwargs: [
            {
                "data_type": "content_strategy",
                "title": "Oracle Health narrative pack",
                "excerpt": "Messaging and narrative examples",
                "source": "oracle-health-pack",
                "source_url": None,
                "public_url": None,
            }
        ],
    )

    routed = route_company_task(
        "oracle-health-ai-enablement",
        "Build a CIO deck for Oracle Health positioning and interoperability workflow simplification.",
    )

    assert "deck-studio" in routed["recommended_agents"]
    assert "oracle-health-marketing-lead" in routed["recommended_agents"]
    assert routed["need_visual_assets"] is True
    assert "visual_asset" in routed["recommended_data_types"]
    assert "/susan-assets" in routed["next_commands"]


def test_route_company_task_pulls_transformfit_design_doctrine(monkeypatch):
    monkeypatch.setattr(
        "control_plane.protocols.search_company_knowledge",
        lambda *args, **kwargs: [
            {
                "data_type": "emotional_design",
                "title": "TransformFit design principles",
                "excerpt": "5 Whys, JTBD, moments of truth, and coach-first design doctrine.",
                "source": "transformfit-design-principles",
                "source_url": None,
                "public_url": None,
            }
        ],
    )

    routed = route_company_task(
        "transformfit",
        "Redesign the landing page around moments of truth, JTBD, and the 5 whys.",
    )

    assert "design-studio-director" in routed["recommended_agents"]
    assert "landing-page-studio" in routed["recommended_agents"]
    assert "emotional_design" in routed["recommended_data_types"]


def test_route_company_task_understands_cognitive_studio_language(monkeypatch):
    monkeypatch.setattr(
        "control_plane.protocols.search_company_knowledge",
        lambda *args, **kwargs: [],
    )

    routed = route_company_task(
        "transformfit",
        "Design a cognitive studio with case library, design memory, and template cascade workflows.",
    )

    assert "design-studio-director" in routed["recommended_agents"]
    assert "marketing-studio-director" in routed["recommended_agents"]


def test_route_company_task_understands_case_library_language(monkeypatch):
    monkeypatch.setattr(
        "control_plane.protocols.search_company_knowledge",
        lambda *args, **kwargs: [],
    )

    routed = route_company_task(
        "transformfit",
        "Build a studio case library and anti-pattern dataset with templates and eval rubrics.",
    )

    assert "design-studio-director" in routed["recommended_agents"]
    assert "studio_case_library" in routed["recommended_data_types"]
    assert "studio_antipatterns" in routed["recommended_data_types"]


def test_route_company_task_understands_transformfit_training_studios(monkeypatch):
    monkeypatch.setattr(
        "control_plane.protocols.search_company_knowledge",
        lambda *args, **kwargs: [],
    )

    routed = route_company_task(
        "transformfit",
        "Build a hypertrophy mesocycle with autoregulation rules, exercise library support, and competitor review research.",
    )

    assert "workout-program-studio" in routed["recommended_agents"]
    assert "training-research-studio" in routed["recommended_agents"]
    assert "training_research" in routed["recommended_data_types"]
    assert "exercise_catalog" in routed["recommended_data_types"]


def test_route_company_task_understands_relational_coaching_language(monkeypatch):
    monkeypatch.setattr(
        "control_plane.protocols.search_company_knowledge",
        lambda *args, **kwargs: [],
    )

    routed = route_company_task(
        "transformfit",
        "Build the TransformFit coach around love maps, therapeutic alliance, and a personal knowledge map.",
    )

    assert "coaching-architecture-studio" in routed["recommended_agents"]
    assert "freya" in routed["recommended_agents"]
    assert "flow" in routed["recommended_agents"]
    assert "oracle-health-product-marketing" not in routed["recommended_agents"]
    assert "coaching_architecture" in routed["recommended_data_types"]
    assert "behavioral_economics" in routed["recommended_data_types"]
    assert "sports_psychology" in routed["recommended_data_types"]


def test_route_company_task_pulls_fuller_transformfit_experience_bench(monkeypatch):
    monkeypatch.setattr(
        "control_plane.protocols.search_company_knowledge",
        lambda *args, **kwargs: [],
    )

    routed = route_company_task(
        "transformfit",
        "Help me build the rest of the TransformFit UI and workout session experience.",
    )

    assert "design-studio-director" in routed["recommended_agents"]
    assert "app-experience-studio" in routed["recommended_agents"]
    assert "workout-session-studio" in routed["recommended_agents"]
    assert "coaching-architecture-studio" in routed["recommended_agents"]
    assert "conversation-designer" in routed["recommended_agents"]


def test_route_company_task_understands_ux_scraper_gold_standard(monkeypatch):
    monkeypatch.setattr(
        "control_plane.protocols.search_company_knowledge",
        lambda *args, **kwargs: [],
    )

    routed = route_company_task(
        "transformfit",
        "Use the UX scraper gold standard and Double Black Box workflow to build the TransformFit UI system.",
    )

    assert "design-studio-director" in routed["recommended_agents"]
    assert "app-experience-studio" in routed["recommended_agents"]
    assert routed["suggested_mode"] == "design"


def test_route_company_task_returns_mode_options(monkeypatch):
    monkeypatch.setattr(
        "control_plane.protocols.search_company_knowledge",
        lambda *args, **kwargs: [],
    )

    routed = route_company_task(
        "transformfit",
        "Build out the workout studio, coaching system, and domain foundry for TransformFit.",
    )

    assert routed["suggested_mode"] == "foundry"
    assert any(option["recommended"] for option in routed["mode_options"])
    assert "/susan-foundry" in routed["next_commands"]


def test_route_company_task_understands_founder_foundry_language(monkeypatch):
    monkeypatch.setattr(
        "control_plane.protocols.search_company_knowledge",
        lambda *args, **kwargs: [],
    )

    routed = route_company_task(
        "founder-intelligence-os",
        "Build the company genome, evidence graph, stage-gate model, and operating cadence for the startup foundry.",
    )

    assert routed["suggested_mode"] == "foundry"
    assert "susan" in routed["recommended_agents"]
    assert "compass" in routed["recommended_agents"]
    assert "atlas" in routed["recommended_agents"]
    assert "operational_protocols" in routed["recommended_data_types"]


def test_sync_project_target_writes_commands_mcp_skill_and_settings(tmp_path):
    target_root = tmp_path / "project"
    target_root.mkdir()

    result = sync_project_target(
        {
            "path": str(target_root),
            "company_id": "oracle-health-ai-enablement",
            "project_label": "Oracle Health AI Enablement",
        }
    )

    assert result["status"] == "synced"
    assert (target_root / ".claude" / "commands" / "susan-query.md").exists()
    assert (target_root / ".claude" / "skills" / "susan-protocols" / "SKILL.md").exists()
    assert (target_root / ".susan" / "PROTOCOLS.md").exists()
    assert (target_root / ".susan" / "project-context.yaml").exists()

    mcp_payload = json.loads((target_root / ".mcp.json").read_text(encoding="utf-8"))
    assert "susan-intelligence" in mcp_payload["mcpServers"]

    settings_payload = json.loads((target_root / ".claude" / "settings.json").read_text(encoding="utf-8"))
    assert settings_payload["hooks"]["PreToolUse"]


def test_protocol_endpoints(monkeypatch):
    monkeypatch.setattr(
        "control_plane.main.route_company_task",
        lambda company, task, top_k=6: {
            "company_id": company,
            "task": task,
            "need_research_first": False,
            "need_visual_assets": True,
            "recommended_agents": ["deck-studio"],
            "recommended_data_types": ["content_strategy", "visual_asset"],
            "next_commands": ["/susan-query", "/susan-assets"],
            "rationale": ["Deck work should pull studio and visual assets."],
            "evidence_hits": [],
        },
    )
    monkeypatch.setattr(
        "control_plane.main.get_company_status",
        lambda company: {
            "company_id": company,
            "company": {},
            "chunk_count": 12,
            "visual_asset_count": 3,
            "output_dir": "/tmp/susan-outputs",
            "output_files": [],
            "latest_output_at": None,
        },
    )
    monkeypatch.setattr(
        "control_plane.main.get_company_foundry_blueprint",
        lambda company: {
            "company_id": company,
            "company_name": "TransformFit",
            "description": "Foundry blueprint",
            "default_mode": "design",
            "mode_options": [],
            "key_protocols": ["Use the workout-session studio for active session work."],
            "execution_tracks": [],
            "expert_councils": [],
            "project_targets": [],
            "coverage_gaps": [],
            "next_actions": ["Build the workout session studio."],
        },
    )

    client = TestClient(app)

    route_response = client.get(
        "/api/routing/susan",
        params={"company": "oracle-health-ai-enablement", "task": "Build a deck"},
    )
    assert route_response.status_code == 200
    assert route_response.json()["recommended_agents"] == ["deck-studio"]

    status_response = client.get("/api/companies/oracle-health-ai-enablement/status")
    assert status_response.status_code == 200
    assert status_response.json()["visual_asset_count"] == 3

    foundry_response = client.get("/api/foundry/transformfit/blueprint")
    assert foundry_response.status_code == 200
    assert foundry_response.json()["default_mode"] == "design"
