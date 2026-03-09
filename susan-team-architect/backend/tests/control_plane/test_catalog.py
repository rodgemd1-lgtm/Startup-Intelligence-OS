from fastapi.testclient import TestClient

from control_plane.catalog import ControlPlaneCatalog
from control_plane.main import app


def test_catalog_detects_reconciliation_issues():
    catalog = ControlPlaneCatalog()
    report = catalog.reconciliation()

    issue_ids = {issue.id for issue in report.issues}
    assert "agent-registry-drift" in issue_ids
    assert "claude-agent-count-stale" in issue_ids
    assert report.backlog


def test_catalog_search_returns_lane_statuses():
    catalog = ControlPlaneCatalog()
    response = catalog.search_knowledge("nutrition science coverage", top_k=5)

    assert response.results
    assert {"lexical", "structured", "protocol", "vector"}.issubset({lane.lane for lane in response.lanes})


def test_catalog_exposes_agent_profiles_and_prompt_research_snapshot():
    catalog = ControlPlaneCatalog()

    profiles = catalog.agent_profiles()
    snapshot = catalog.prompt_research_snapshot

    assert any(profile.id == "susan" for profile in profiles)
    assert snapshot.providers
    assert snapshot.topics


def test_api_serves_tenants_and_scorecard():
    client = TestClient(app)

    tenants = client.get("/api/tenants")
    assert tenants.status_code == 200
    payload = tenants.json()
    assert any(tenant["id"] == "transformfit" for tenant in payload)

    scorecard = client.get("/api/tenants/transformfit/scorecard")
    assert scorecard.status_code == 200
    assert scorecard.json()["tenant"]["id"] == "transformfit"

    profiles = client.get("/api/agents/profiles")
    assert profiles.status_code == 200
    assert any(profile["id"] == "susan" for profile in profiles.json())

    research = client.get("/api/research/prompt-intelligence")
    assert research.status_code == 200
    assert "providers" in research.json()
