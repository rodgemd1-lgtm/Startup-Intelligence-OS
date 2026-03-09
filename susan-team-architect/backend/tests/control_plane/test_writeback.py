from __future__ import annotations

import json
from pathlib import Path

from control_plane.writeback import write_foundry_records_for_output_dir


def test_writeback_derives_and_stores_records(monkeypatch, tmp_path: Path):
    output_dir = tmp_path
    (output_dir / "problem-framing.json").write_text(
        json.dumps(
            {
                "primary_objective": "Improve retention",
                "success_definition": [
                    "Day-7 retention rate improves materially",
                    "First-session completion exceeds 75%",
                ],
            }
        ),
        encoding="utf-8",
    )
    (output_dir / "decision-brief.json").write_text(
        json.dumps(
            {
                "recommended_path": "Instrument first, redesign second, retention third.",
                "options": [{"name": "Instrument-First Sequential Path (Recommended)"}],
                "prioritized_workstreams": [
                    "Install event logging",
                    "Redesign onboarding",
                    "Ship one behavioral mechanic",
                ],
                "execution_risks": ["Instrumentation privacy risk"],
                "immediate_agent_team": ["pulse", "atlas"],
                "research_first": True,
                "studio_needed": True,
            }
        ),
        encoding="utf-8",
    )
    (output_dir / "foundry-blueprint.json").write_text(
        json.dumps(
            {
                "stage_gates": [
                    {
                        "id": "launch",
                        "status": "partial",
                        "why": "Launch inputs are incomplete.",
                        "artifact_names": ["KPI Tree and Scorecards"],
                        "required_artifacts": ["KPI tree"],
                        "blocking_gaps": ["support plan"],
                        "missing_artifacts": ["Launch Readiness Checklist"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    saved = {"decisions": [], "experiments": [], "metrics": [], "reviews": []}
    monkeypatch.setattr("control_plane.writeback.save_foundry_decision", lambda payload: saved["decisions"].append(payload) or payload)
    monkeypatch.setattr("control_plane.writeback.save_foundry_experiment", lambda payload: saved["experiments"].append(payload) or payload)
    monkeypatch.setattr("control_plane.writeback.save_foundry_metric", lambda payload: saved["metrics"].append(payload) or payload)
    monkeypatch.setattr("control_plane.writeback.save_foundry_stage_review", lambda payload: saved["reviews"].append(payload) or payload)

    summary = write_foundry_records_for_output_dir("job-123", "transformfit", output_dir)

    assert summary["generated_counts"]["decisions"] == 1
    assert summary["generated_counts"]["experiments"] == 3
    assert summary["generated_counts"]["metrics"] == 2
    assert summary["generated_counts"]["stage_reviews"] == 1
    assert summary["stored_counts"]["decisions"] == 1
    assert len(saved["experiments"]) == 3
    assert saved["reviews"][0]["stage_gate_id"] == "launch"
