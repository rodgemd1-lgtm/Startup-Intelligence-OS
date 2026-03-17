"""API tests for the ask-driven operator surfaces."""
import importlib
import os
import shutil
import sys
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False))


def _prepare_root(tmp_path: Path) -> Path:
    root = tmp_path / "decision-os-root"
    startup_os = root / ".startup-os"
    for folder in (
        "decisions",
        "capabilities",
        "projects",
        "companies",
        "departments",
        "signals",
        "action-packets",
        "graph-links",
        "artifacts",
    ):
        (startup_os / folder).mkdir(parents=True, exist_ok=True)

    _write_yaml(
        startup_os / "workspace.yaml",
        {
            "name": "startup-intelligence-os",
            "mode": "decision-capability-os",
            "front_door": "jake",
            "foundry": "susan",
            "runtime_source_of_truth": "susan-team-architect/backend",
            "active_company": "founder-intelligence-os",
            "active_project": "decision-capability-os",
            "active_decision": "phase-a-runtime-foundation",
            "active_branch": "main",
        },
    )
    _write_yaml(
        startup_os / "companies" / "founder-intelligence-os.yaml",
        {
            "id": "founder-intelligence-os",
            "name": "Founder Intelligence OS",
            "stage": "active_build",
            "linked_projects": ["decision-capability-os"],
            "linked_capabilities": [
                "department-studios-of-excellence",
                "agentic-operator-console",
            ],
            "linked_decisions": [],
        },
    )
    _write_yaml(
        startup_os / "projects" / "decision-capability-os.yaml",
        {
            "id": "decision-capability-os",
            "name": "Decision & Capability OS",
            "company_id": "founder-intelligence-os",
            "status": "active",
            "linked_decisions": [],
            "linked_capabilities": [
                "department-studios-of-excellence",
                "agentic-operator-console",
            ],
        },
    )
    _write_yaml(
        startup_os / "capabilities" / "department-studios-of-excellence.yaml",
        {
            "id": "department-studios-of-excellence",
            "name": "Department Studios of Excellence",
            "maturity_current": 1.6,
            "maturity_target": 4.2,
            "wave": 1,
            "gaps": ["department wrappers"],
            "owner_agent": "susan",
            "levels": {
                1: {"name": "Nascent", "items": [{"text": "Base registry exists", "done": True}]},
                2: {"name": "Emerging", "items": [{"text": "Wave 1 packs exist", "done": False}]},
            },
        },
    )
    _write_yaml(
        startup_os / "capabilities" / "agentic-operator-console.yaml",
        {
            "id": "agentic-operator-console",
            "name": "Agentic Operator Console",
            "maturity_current": 1.7,
            "maturity_target": 4.4,
            "wave": 1,
            "gaps": ["routing", "signal rail"],
            "owner_agent": "jake",
            "levels": {
                1: {"name": "Nascent", "items": [{"text": "Console exists", "done": True}]},
                2: {"name": "Emerging", "items": [{"text": "Graph-backed operator shell exists", "done": False}]},
            },
        },
    )
    _write_yaml(
        startup_os / "capabilities" / "job-memory-intelligence.yaml",
        {
            "id": "job-memory-intelligence",
            "name": "Job Memory Intelligence",
            "maturity_current": 2.3,
            "maturity_target": 4.4,
            "wave": 1,
            "gaps": ["resume-packets", "interview-routing"],
            "owner_agent": "susan",
            "levels": {
                1: {"name": "Nascent", "items": [{"text": "Job Studio exists", "done": True}]},
                2: {"name": "Emerging", "items": [{"text": "Job routing exists", "done": False}]},
            },
        },
    )

    repo_root = Path(__file__).resolve().parents[3]
    for department_path in (repo_root / ".startup-os" / "departments").glob("*.yaml"):
        shutil.copy(department_path, startup_os / "departments" / department_path.name)
    shutil.copy(
        repo_root / ".startup-os" / "companies" / "mike-job-studio.yaml",
        startup_os / "companies" / "mike-job-studio.yaml",
    )

    return root


@pytest.fixture()
def api_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = _prepare_root(tmp_path)
    monkeypatch.setenv("DECISION_OS_ROOT", str(root))

    import decision_os.store as store_mod
    import decision_os.operator as operator_mod
    import decision_os.api as api_mod

    importlib.reload(store_mod)
    importlib.reload(operator_mod)
    api_mod = importlib.reload(api_mod)

    return TestClient(api_mod.app), root


def test_departments_endpoint_returns_wave_one_registry(api_client):
    client, _root = api_client
    response = client.get("/api/departments")
    assert response.status_code == 200
    departments = response.json()
    department_ids = {department["id"] for department in departments}
    assert len(departments) >= 11
    assert "job-studio" in department_ids
    assert "trust-governance-studio" in department_ids


def test_departments_endpoint_attaches_simulated_maturity_when_summary_exists(api_client):
    client, root = api_client
    summary_dir = root / ".startup-os" / "artifacts" / "simulated-maturity"
    summary_dir.mkdir(parents=True, exist_ok=True)
    (summary_dir / "simulated-maturity-harness-summary.md").write_text(
        "\n".join(
            [
                "# Simulated Maturity Harness Summary",
                "",
                "| Scenario | Department | Simulated score | Run | Artifact |",
                "|---|---|---:|---|---|",
                "| Founder Decision Room Simulated Review | founder-decision-room | 10.0 | run-1 | art-1 |",
                "| Job Studio Training Simulated Review | job-studio | 9.8 | run-2 | art-2 |",
            ]
        ),
        encoding="utf-8",
    )
    (summary_dir / "founder-decision-simulated-review.md").write_text(
        "# Founder\n\n- department_id: `founder-decision-room`\n",
        encoding="utf-8",
    )
    (summary_dir / "job-studio-simulated-review.md").write_text(
        "# Job Studio\n\n- department_id: `job-studio`\n",
        encoding="utf-8",
    )

    response = client.get("/api/departments")
    assert response.status_code == 200
    departments = {department["id"]: department for department in response.json()}
    assert departments["founder-decision-room"]["simulated_maturity"] == 10.0
    assert departments["job-studio"]["simulated_maturity"] == 9.8
    assert departments["founder-decision-room"]["simulated_review_path"].endswith(
        "founder-decision-simulated-review.md"
    )


@pytest.mark.parametrize(
    ("request_text", "expected_primary"),
    [
        ("help me build a project", "founder-decision-room"),
        ("help me understand users and define roadmap", "consumer-user-studio"),
        ("help me redesign the onboarding workflow and feature path", "product-experience-studio"),
        ("help me launch and message this", "marketing-narrative-studio"),
        ("help me harden the agent orchestration architecture", "engineering-agent-systems-studio"),
    ],
)
def test_route_request_covers_wave_one_departments(api_client, request_text: str, expected_primary: str):
    client, root = api_client
    response = client.post("/api/route/request", json={"request_text": request_text})
    assert response.status_code == 200
    payload = response.json()
    packet = payload["action_packet"]
    assert packet["primary_department"] == expected_primary
    assert Path(root / packet["artifact_paths"][0]).exists()


def test_route_request_build_project_orders_founder_then_product_then_engineering(api_client):
    client, root = api_client
    response = client.post("/api/route/request", json={"request_text": "help me build a project"})
    assert response.status_code == 200
    payload = response.json()
    packet = payload["action_packet"]
    assert packet["dependency_order"][:3] == [
        "founder-decision-room",
        "product-experience-studio",
        "engineering-agent-systems-studio",
    ]
    assert packet["decision_requirement"] == "required"
    assert payload["linked_decision_id"].startswith("dec-")

    summary_path = root / packet["artifact_paths"][0]
    summary_text = summary_path.read_text()
    assert "Founder Decision Room" in summary_text
    assert "Engineering & Agent Systems Studio" in summary_text


def test_signals_and_graph_endpoints_reflect_operator_state(api_client):
    client, _root = api_client

    signals_before = client.get("/api/signals")
    assert signals_before.status_code == 200
    signal_types = {item["signal_type"] for item in signals_before.json()}
    assert "missing_active_decision" in signal_types
    assert "no_action_packets" in signal_types

    route_response = client.post(
        "/api/route/request",
        json={"request_text": "help me understand users and define roadmap"},
    )
    assert route_response.status_code == 200

    graph_response = client.get("/api/graph")
    assert graph_response.status_code == 200
    graph = graph_response.json()
    node_types = {node["type"] for node in graph["nodes"]}
    assert "department" in node_types
    assert "action_packet" in node_types
    assert "decision" in node_types
    assert graph["summary"]["link_count"] > 0


@pytest.mark.parametrize(
    ("request_text", "expected_track", "expected_supporting", "expected_decision_requirement"),
    [
        ("help me build a resume packet for this role", "resume_packets", "marketing-narrative-studio", "none"),
        ("recover my writing style from authored emails", "writing_intelligence", "marketing-narrative-studio", "none"),
        ("help me prepare for an Oracle Health interview", "interview_prep", "consumer-user-studio", "optional"),
        ("create an opportunity brief for this employer", "opportunity_briefs", "founder-decision-room", "optional"),
    ],
)
def test_job_studio_requests_use_job_company_context(
    api_client,
    request_text: str,
    expected_track: str,
    expected_supporting: str,
    expected_decision_requirement: str,
):
    client, root = api_client
    response = client.post("/api/route/request", json={"request_text": request_text})
    assert response.status_code == 200
    payload = response.json()
    packet = payload["action_packet"]
    assert packet["company_context_id"] == "mike-job-studio"
    assert packet["execution_track_id"] == expected_track
    assert packet["primary_department"] == "job-studio"
    assert expected_supporting in packet["supporting_departments"]
    assert packet["decision_requirement"] == expected_decision_requirement
    assert any("mike_job_studio" in source for source in packet["context_sources"])

    summary_path = root / packet["artifact_paths"][0]
    summary_text = summary_path.read_text()
    assert "Mike Job Studio" in summary_text
    assert expected_track in summary_text


def test_training_requests_route_to_job_studio_department(api_client):
    client, root = api_client
    response = client.post(
        "/api/route/request",
        json={"request_text": "build an eight-session strategist AI training workshop with Ellen in Gen Chat"},
    )
    assert response.status_code == 200
    payload = response.json()
    packet = payload["action_packet"]
    assert packet["company_context_id"] == "mike-job-studio"
    assert packet["primary_department"] == "job-studio"
    assert packet["execution_track_id"] in {
        "training_factory",
        "ai_strategist_enablement",
        "ellen_enablement",
    }
    summary_path = root / packet["artifact_paths"][0]
    assert summary_path.exists()
