from fastapi.testclient import TestClient
import json

from control_plane import foundry_ops
from control_plane.main import app


def test_foundry_ops_endpoints(monkeypatch):
    monkeypatch.setattr(
        "control_plane.main.build_foundry_assessment",
        lambda: {
            "companies": [
                {
                    "company_id": "transformfit",
                    "company_name": "TransformFit",
                    "default_mode": "design",
                    "genome": {"ready_track_count": 3, "track_count": 5},
                    "track_statuses": [],
                    "maturity": [],
                    "coverage_gaps": [],
                    "stage_gates": [],
                    "next_actions": [],
                }
            ]
        },
    )
    monkeypatch.setattr(
        "control_plane.main.list_foundry_decisions",
        lambda company_id, limit=50: [
            {
                "decision_id": "dec-1",
                "company_id": company_id,
                "owner": "mike",
                "summary": "Choose TransformFit as flagship",
                "chosen_option": "transformfit",
            }
        ],
    )
    monkeypatch.setattr(
        "control_plane.main.save_foundry_decision",
        lambda payload: payload,
    )
    monkeypatch.setattr(
        "control_plane.main.list_foundry_experiments",
        lambda company_id, limit=50: [
            {
                "experiment_id": "exp-1",
                "company_id": company_id,
                "hypothesis": "Coach thread increases completion",
                "owner": "mike",
            }
        ],
    )
    monkeypatch.setattr("control_plane.main.save_foundry_experiment", lambda payload: payload)
    monkeypatch.setattr(
        "control_plane.main.list_foundry_metrics",
        lambda company_id, limit=50: [
            {
                "metric_id": "metric-1",
                "company_id": company_id,
                "name": "Workout completion",
                "category": "engagement",
                "owner": "pulse",
            }
        ],
    )
    monkeypatch.setattr("control_plane.main.save_foundry_metric", lambda payload: payload)
    monkeypatch.setattr(
        "control_plane.main.list_foundry_stage_reviews",
        lambda company_id, limit=50: [
            {
                "company_id": company_id,
                "stage_gate_id": "launch",
                "reviewer": "susan",
                "status": "ready",
                "summary": "Launch gate passed",
            }
        ],
    )
    monkeypatch.setattr("control_plane.main.save_foundry_stage_review", lambda payload: payload)

    client = TestClient(app)

    assessment = client.get("/api/foundry/assessment")
    assert assessment.status_code == 200
    assert assessment.json()["companies"][0]["company_id"] == "transformfit"

    decisions = client.get("/api/foundry/transformfit/decisions")
    assert decisions.status_code == 200
    assert decisions.json()[0]["decision_id"] == "dec-1"

    create_decision = client.post(
        "/api/foundry/decisions",
        json={
            "decision_id": "dec-2",
            "company_id": "transformfit",
            "owner": "mike",
            "summary": "Choose narrative motion",
            "chosen_option": "native motion",
        },
    )
    assert create_decision.status_code == 200
    assert create_decision.json()["decision_id"] == "dec-2"

    experiments = client.get("/api/foundry/transformfit/experiments")
    assert experiments.status_code == 200
    assert experiments.json()[0]["experiment_id"] == "exp-1"

    metrics = client.get("/api/foundry/transformfit/metrics")
    assert metrics.status_code == 200
    assert metrics.json()[0]["metric_id"] == "metric-1"

    stage_reviews = client.get("/api/foundry/transformfit/stage-reviews")
    assert stage_reviews.status_code == 200
    assert stage_reviews.json()[0]["stage_gate_id"] == "launch"


def test_foundry_ops_fall_back_to_local_writeback(monkeypatch, tmp_path):
    companies_dir = tmp_path / "companies"
    output_dir = companies_dir / "transformfit" / "susan-outputs"
    output_dir.mkdir(parents=True)
    (output_dir / "foundry-writeback.json").write_text(
        json.dumps(
            {
                "records": {
                    "decisions": [
                        {
                            "decision_id": "dec-local-1",
                            "company_id": "transformfit",
                            "owner": "susan",
                            "summary": "Local fallback decision",
                            "chosen_option": "instrument-first",
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(foundry_ops.config, "companies_dir", companies_dir)
    monkeypatch.setattr(foundry_ops, "_list_rows", lambda *args, **kwargs: [])

    rows = foundry_ops.list_foundry_decisions("transformfit")

    assert rows[0]["decision_id"] == "dec-local-1"
