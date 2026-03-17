from pathlib import Path
import yaml

from decision_os.customer_user_studio import CustomerUserStudio


def _write_schemas(root: Path) -> None:
    (root / ".startup-os" / "schemas").mkdir(parents=True)
    (root / ".startup-os" / "schemas" / "customer-persona.schema.yaml").write_text(
        yaml.safe_dump({"required": ["id", "name", "segment", "applications", "goals", "constraints", "preferences", "behavioral_profile"]})
    )
    (root / ".startup-os" / "schemas" / "customer-scenario.schema.yaml").write_text(
        yaml.safe_dump({"required": ["id", "app_id", "persona_id", "objective", "entry_state", "tasks", "success_criteria", "adaptation_rules"]})
    )
    (root / ".startup-os" / "schemas" / "customer-session-evidence.schema.yaml").write_text(
        yaml.safe_dump({"required": ["id", "app_id", "persona_id", "scenario_id", "run_at", "result", "findings", "preference_signals", "roadmap_candidates"]})
    )


def test_seed_validate_and_ranked_report(tmp_path: Path) -> None:
    root = tmp_path
    _write_schemas(root)

    studio = CustomerUserStudio(root)
    created = studio.seed()

    assert Path(root / created["persona"]).exists()
    assert Path(root / created["scenario"]).exists()
    assert Path(root / created["session"]).exists()

    results = studio.validate_all()
    assert results
    assert all(r.valid for r in results)

    out = studio.generate_ranked_opportunities()
    data = yaml.safe_load(out.read_text())
    assert data["count"] >= 1
    assert data["opportunities"][0]["priority_score"] >= data["opportunities"][-1]["priority_score"]


def test_push_to_susan_backend(tmp_path: Path) -> None:
    root = tmp_path
    _write_schemas(root)

    backend_root = root / "susan-team-architect" / "backend"
    backend_root.mkdir(parents=True)

    studio = CustomerUserStudio(root)
    studio.seed()
    studio.generate_ranked_opportunities()

    result = studio.push_to_susan_backend(backend_root)
    assert result["count"] >= 4

    target_root = root / result["target_root"]
    assert (target_root / "personas").exists()
    assert (target_root / "scenarios").exists()
    assert (target_root / "sessions").exists()
    assert (target_root / "reports").exists()
    assert (target_root / "sync-index.yaml").exists()


def test_publish_bundle(tmp_path: Path) -> None:
    root = tmp_path
    _write_schemas(root)

    backend_root = root / "susan-team-architect" / "backend"
    backend_root.mkdir(parents=True)

    studio = CustomerUserStudio(root)
    studio.seed()

    # bind publish to tmp backend by creating expected default backend path
    (root / "susan-team-architect" / "backend").mkdir(parents=True, exist_ok=True)
    local_drive = root / "local-drive"
    local_drive.mkdir(parents=True, exist_ok=True)

    result = studio.publish_bundle(local_drive_root=local_drive)

    assert (root / result["manifest"]).exists()
    assert result["backend_index"].endswith("sync-index.yaml")
    assert result["local_drive_path"] is not None
    assert (Path(result["local_drive_path"]) / "reports" / "ranked-opportunities.yaml").exists()
