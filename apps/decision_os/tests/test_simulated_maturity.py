"""Tests for the simulated maturity harness."""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

_test_dir = tempfile.mkdtemp(prefix="decision-os-sim-test-")
os.environ["DECISION_OS_ROOT"] = _test_dir

for rel in [
    ".startup-os/decisions",
    ".startup-os/capabilities",
    ".startup-os/projects",
    ".startup-os/companies",
    ".startup-os/departments",
    ".startup-os/signals",
    ".startup-os/action-packets",
    ".startup-os/graph-links",
    ".startup-os/artifacts/research",
    "apps/decision_os/data/runs",
    "apps/decision_os/data/artifacts",
    "apps/decision_os/data/evidence",
]:
    Path(_test_dir, rel).mkdir(parents=True, exist_ok=True)

from decision_os.store import Store  # noqa: E402
from decision_os.simulated_maturity import run_simulated_maturity_harness  # noqa: E402


def _write(path: str, content: str) -> None:
    target = Path(_test_dir, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def setup_module(module) -> None:
    _write(
        ".startup-os/artifacts/research/synthetic-run-review-framework-2026-03-12.md",
        "# Synthetic Framework\n",
    )
    _write(
        ".startup-os/artifacts/job-studio-training-operator-packet-2026-03-12.md",
        "# Job Studio Packet\n",
    )

    stronger = {
        "started_at": "2026-03-13T00:00:00Z",
        "finished_at": "2026-03-13T00:05:00Z",
        "total_chunks": 821,
        "results": [
            {"manifest_file": "startup_os_stronger_benchmark_case_library.yaml", "total_chunks": 319},
            {"manifest_file": "startup_os_eval_and_synthetic_review_foundations.yaml", "total_chunks": 382},
            {"manifest_file": "job_studio_training_learning_science_stronger.yaml", "total_chunks": 120},
        ],
    }
    gap = {
        "started_at": "2026-03-13T00:00:00Z",
        "finished_at": "2026-03-13T00:20:00Z",
        "total_chunks": 9718,
        "results": [],
    }
    _write(
        "susan-team-architect/backend/artifacts/stronger_dataset_benchmark_wave/latest_summary.json",
        json.dumps(stronger),
    )
    _write(
        "susan-team-architect/backend/artifacts/department_gap_closure_wave/latest_summary.json",
        json.dumps(gap),
    )


def test_run_simulated_maturity_harness_creates_runs_and_artifacts(monkeypatch):
    import decision_os.simulated_maturity as sim

    monkeypatch.setattr(sim, "STRONGER_WAVE_SUMMARY", Path(_test_dir) / "susan-team-architect/backend/artifacts/stronger_dataset_benchmark_wave/latest_summary.json")
    monkeypatch.setattr(sim, "GAP_WAVE_SUMMARY", Path(_test_dir) / "susan-team-architect/backend/artifacts/department_gap_closure_wave/latest_summary.json")
    monkeypatch.setattr(sim, "SYNTHETIC_REVIEW_FRAMEWORK", Path(_test_dir) / ".startup-os/artifacts/research/synthetic-run-review-framework-2026-03-12.md")
    monkeypatch.setattr(sim, "TRAINING_OPERATOR_PACKET", Path(_test_dir) / ".startup-os/artifacts/job-studio-training-operator-packet-2026-03-12.md")

    def fake_monte_carlo(variant: str):
        return {"type": variant, "value": 1}

    monkeypatch.setattr(sim, "_run_monte_carlo_variant", fake_monte_carlo)

    store = Store()
    result = run_simulated_maturity_harness(store=store)

    assert len(result["results"]) == 5
    assert Path(result["summary_path"]).exists()
    assert store.runs.count() == 5
    assert store.artifacts.count() == 6
    assert store.evidence.count() == 4


def teardown_module(module) -> None:
    shutil.rmtree(_test_dir, ignore_errors=True)
