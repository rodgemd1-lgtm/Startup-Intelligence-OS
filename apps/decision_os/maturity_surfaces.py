"""Helpers for operator-facing maturity surfaces."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _safe_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _scan_review_paths(root: Path) -> dict[str, str]:
    review_dir = root / ".startup-os" / "artifacts" / "simulated-maturity"
    if not review_dir.exists():
        return {}

    mapping: dict[str, str] = {}
    for path in sorted(review_dir.glob("*-review.md")):
        if path.name == "simulated-maturity-harness-summary.md":
            continue
        department_id = ""
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.startswith("- department_id:"):
                    department_id = line.split("`")[1]
                    break
        except (IndexError, OSError):
            continue
        if department_id:
            mapping[department_id] = str(path.relative_to(root))
    return mapping


def load_simulated_maturity_state(root: Path) -> dict[str, Any]:
    summary_path = root / ".startup-os" / "artifacts" / "simulated-maturity" / "simulated-maturity-harness-summary.md"
    state: dict[str, Any] = {
        "available": False,
        "summary_path": str(summary_path.relative_to(root)),
        "generated_at": "",
        "age_hours": None,
        "departments": {},
    }
    if not summary_path.exists():
        return state

    generated_at = datetime.fromtimestamp(summary_path.stat().st_mtime, tz=timezone.utc)
    age_hours = round((datetime.now(timezone.utc) - generated_at).total_seconds() / 3600.0, 2)
    state["available"] = True
    state["generated_at"] = generated_at.isoformat()
    state["age_hours"] = age_hours

    review_paths = _scan_review_paths(root)
    for line in summary_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) != 5 or cells[0] in {"Scenario", "---"} or cells[0].startswith("---"):
            continue
        scenario, department_id, score, run_id, artifact_id = cells
        score_value = _safe_float(score)
        state["departments"][department_id] = {
            "scenario": scenario,
            "score": score_value,
            "run_id": run_id,
            "artifact_id": artifact_id,
            "review_path": review_paths.get(department_id, ""),
            "generated_at": state["generated_at"],
        }
    return state


def enrich_department_payload(payload: dict[str, Any], simulated_state: dict[str, Any]) -> dict[str, Any]:
    entry = simulated_state.get("departments", {}).get(payload["id"], {})
    payload["simulated_maturity"] = entry.get("score")
    payload["simulated_run_id"] = entry.get("run_id", "")
    payload["simulated_artifact_id"] = entry.get("artifact_id", "")
    payload["simulated_review_path"] = entry.get("review_path", "")
    payload["simulated_generated_at"] = entry.get("generated_at", "")
    return payload
