from __future__ import annotations

from control_plane.foundry import build_company_blueprint, render_company_blueprint_markdown


class _FakeResponse:
    def __init__(self, count: int):
        self.count = count


class _FakeQuery:
    def __init__(self, counts: dict[tuple[str, str], int]):
        self._counts = counts
        self._company_id: str | None = None
        self._data_type: str | None = None

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, key: str, value: str):
        if key == "company_id":
            self._company_id = value
        elif key == "data_type":
            self._data_type = value
        return self

    def execute(self):
        return _FakeResponse(self._counts.get((self._company_id or "", self._data_type or ""), 0))


class _FakeSupabase:
    def __init__(self, counts: dict[tuple[str, str], int]):
        self._counts = counts

    def table(self, _name: str):
        return _FakeQuery(self._counts)


def test_founder_blueprint_includes_artifact_inventory_and_stage_gates(monkeypatch):
    counts = {
        ("founder-intelligence-os", "business_strategy"): 4,
        ("founder-intelligence-os", "market_research"): 4,
        ("founder-intelligence-os", "operational_protocols"): 4,
        ("founder-intelligence-os", "technical_docs"): 4,
        ("founder-intelligence-os", "expert_knowledge"): 4,
        ("founder-intelligence-os", "studio_case_library"): 4,
        ("founder-intelligence-os", "studio_antipatterns"): 4,
        ("founder-intelligence-os", "studio_memory"): 4,
        ("founder-intelligence-os", "studio_templates"): 4,
        ("founder-intelligence-os", "studio_evals"): 4,
        ("founder-intelligence-os", "studio_open_research"): 4,
        ("founder-intelligence-os", "legal_compliance"): 4,
        ("founder-intelligence-os", "security"): 4,
        ("founder-intelligence-os", "ux_research"): 4,
        ("founder-intelligence-os", "finance"): 4,
        ("founder-intelligence-os", "user_research"): 4,
    }
    monkeypatch.setattr("control_plane.foundry.create_client", lambda *_args, **_kwargs: _FakeSupabase(counts))

    blueprint = build_company_blueprint("founder-intelligence-os")

    assert blueprint["genome"]["domain"] == "startup_foundry"
    assert any(artifact["id"] == "company_genome_spec" for artifact in blueprint["artifact_inventory"])
    assert any(gate["id"] == "launch" and "KPI Tree and Scorecards" in gate["artifact_names"] for gate in blueprint["stage_gates"])
    assert all(gate["status"] == "ready" for gate in blueprint["stage_gates"])

    markdown = render_company_blueprint_markdown(blueprint)
    assert "## Artifact Inventory" in markdown
    assert "## Stage Gates" in markdown
    assert "## Maturity" in markdown
