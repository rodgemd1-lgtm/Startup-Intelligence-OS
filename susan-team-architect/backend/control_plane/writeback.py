"""Automatic foundry writeback from Susan run outputs."""

from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
import re
from typing import Any

from .foundry import build_company_blueprint
from .foundry_ops import (
    save_foundry_decision,
    save_foundry_experiment,
    save_foundry_metric,
    save_foundry_stage_review,
)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "item"


def _truncate(text: str, limit: int = 240) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _metric_category(text: str) -> str:
    lowered = text.lower()
    if "retention" in lowered or "return" in lowered:
        return "retention"
    if "completion" in lowered:
        return "completion"
    if "cost" in lowered or "$" in lowered:
        return "cost"
    if "trust" in lowered or "context persists" in lowered:
        return "trust"
    if "personalization" in lowered:
        return "personalization"
    return "growth"


def _derive_decisions(
    job_id: str,
    company_id: str,
    problem_framing: dict[str, Any],
    decision_brief: dict[str, Any],
) -> list[dict[str, Any]]:
    recommended_path = decision_brief.get("recommended_path")
    if not recommended_path:
        return []

    chosen_option = None
    for option in decision_brief.get("options", []):
        option_name = option.get("name", "")
        if "recommend" in option_name.lower():
            chosen_option = option_name
            break
    if not chosen_option and decision_brief.get("options"):
        chosen_option = decision_brief["options"][0].get("name")
    if not chosen_option:
        chosen_option = "recommended_path"

    return [
        {
            "decision_id": f"{job_id}-recommended-path",
            "company_id": company_id,
            "owner": "susan",
            "summary": _truncate(recommended_path, 140),
            "context": problem_framing.get("primary_objective"),
            "chosen_option": chosen_option,
            "why_this_won": recommended_path,
            "status": "active",
            "source_refs": [
                "decision-brief.json",
                "problem-framing.json",
            ],
            "risks_accepted": decision_brief.get("execution_risks", []),
            "linked_experiments": [
                f"{job_id}-exp-{index + 1}"
                for index, _ in enumerate(decision_brief.get("prioritized_workstreams", [])[:3])
            ],
            "metadata": {
                "generated_by": "automatic_writeback",
                "job_id": job_id,
                "immediate_agent_team": decision_brief.get("immediate_agent_team", []),
                "research_first": decision_brief.get("research_first", False),
                "studio_needed": decision_brief.get("studio_needed", False),
            },
            "decided_at": datetime.now(UTC).isoformat(),
        }
    ]


def _derive_experiments(
    job_id: str,
    company_id: str,
    problem_framing: dict[str, Any],
    decision_brief: dict[str, Any],
) -> list[dict[str, Any]]:
    experiments: list[dict[str, Any]] = []
    success_definition = problem_framing.get("success_definition", [])
    primary_metric = success_definition[0] if success_definition else problem_framing.get("primary_objective")
    for index, workstream in enumerate(decision_brief.get("prioritized_workstreams", [])[:3]):
        experiments.append(
            {
                "experiment_id": f"{job_id}-exp-{index + 1}",
                "company_id": company_id,
                "hypothesis": f"If we execute this workstream, the primary objective should improve: {workstream}",
                "owner": "susan",
                "status": "proposed",
                "user_or_workflow": problem_framing.get("primary_objective"),
                "metric_moved": _truncate(primary_metric or "", 120),
                "leading_signal": _truncate(workstream, 160),
                "disconfirming_signal": "No measurable movement in the target user workflow or success definition.",
                "intervention": workstream,
                "linked_decisions": [f"{job_id}-recommended-path"],
                "metadata": {
                    "generated_by": "automatic_writeback",
                    "job_id": job_id,
                    "rank": index + 1,
                },
            }
        )
    return experiments


def _derive_metrics(job_id: str, company_id: str, problem_framing: dict[str, Any]) -> list[dict[str, Any]]:
    metrics: list[dict[str, Any]] = []
    for index, definition in enumerate(problem_framing.get("success_definition", [])[:6]):
        metrics.append(
            {
                "metric_id": f"{job_id}-metric-{index + 1}",
                "company_id": company_id,
                "name": _truncate(definition, 80),
                "category": _metric_category(definition),
                "owner": "pulse",
                "definition": definition,
                "cadence": "weekly",
                "metadata": {
                    "generated_by": "automatic_writeback",
                    "job_id": job_id,
                    "source": "problem-framing.json",
                },
            }
        )
    return metrics


def _derive_stage_reviews(job_id: str, company_id: str, blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    reviews: list[dict[str, Any]] = []
    for gate in blueprint.get("stage_gates", []):
        reviews.append(
            {
                "company_id": company_id,
                "stage_gate_id": gate["id"],
                "reviewer": "susan",
                "status": gate.get("status", "unknown"),
                "summary": gate.get("why", gate.get("summary", "")),
                "blocking_gaps": gate.get("blocking_gaps", []) + gate.get("missing_artifacts", []),
                "artifact_refs": gate.get("artifact_names", []),
                "metadata": {
                    "generated_by": "automatic_writeback",
                    "job_id": job_id,
                    "required_artifacts": gate.get("required_artifacts", []),
                },
                "reviewed_at": datetime.now(UTC).isoformat(),
            }
        )
    return reviews


def write_foundry_records_for_output_dir(job_id: str, company_id: str, output_dir: Path) -> dict[str, Any]:
    problem_framing = _read_json(output_dir / "problem-framing.json")
    decision_brief = _read_json(output_dir / "decision-brief.json")
    blueprint = _read_json(output_dir / "foundry-blueprint.json")
    if not blueprint:
        blueprint = build_company_blueprint(company_id)

    decisions = _derive_decisions(job_id, company_id, problem_framing, decision_brief)
    experiments = _derive_experiments(job_id, company_id, problem_framing, decision_brief)
    metrics = _derive_metrics(job_id, company_id, problem_framing)
    stage_reviews = _derive_stage_reviews(job_id, company_id, blueprint)

    summary = {
        "job_id": job_id,
        "company_id": company_id,
        "generated_at": datetime.now(UTC).isoformat(),
        "source_files": [
            str(path)
            for path in [
                output_dir / "problem-framing.json",
                output_dir / "decision-brief.json",
                output_dir / "foundry-blueprint.json",
            ]
            if path.exists()
        ],
        "generated_counts": {
            "decisions": len(decisions),
            "experiments": len(experiments),
            "metrics": len(metrics),
            "stage_reviews": len(stage_reviews),
        },
        "stored_counts": {
            "decisions": 0,
            "experiments": 0,
            "metrics": 0,
            "stage_reviews": 0,
        },
        "record_ids": {
            "decisions": [decision["decision_id"] for decision in decisions],
            "experiments": [experiment["experiment_id"] for experiment in experiments],
            "metrics": [metric["metric_id"] for metric in metrics],
            "stage_reviews": [review["stage_gate_id"] for review in stage_reviews],
        },
        "records": {
            "decisions": decisions,
            "experiments": experiments,
            "metrics": metrics,
            "stage_reviews": stage_reviews,
        },
        "errors": [],
    }

    for decision in decisions:
        try:
            stored = save_foundry_decision(decision)
            if "_persistence_error" in (stored.get("metadata") or {}):
                summary["errors"].append(
                    f"decision:{decision['decision_id']}: {(stored.get('metadata') or {}).get('_persistence_error')}"
                )
            else:
                summary["stored_counts"]["decisions"] += 1
        except Exception as exc:  # pragma: no cover - exercised in runtime
            summary["errors"].append(f"decision:{decision['decision_id']}: {exc}")
    for experiment in experiments:
        try:
            stored = save_foundry_experiment(experiment)
            if "_persistence_error" in (stored.get("metadata") or {}):
                summary["errors"].append(
                    f"experiment:{experiment['experiment_id']}: {(stored.get('metadata') or {}).get('_persistence_error')}"
                )
            else:
                summary["stored_counts"]["experiments"] += 1
        except Exception as exc:  # pragma: no cover - exercised in runtime
            summary["errors"].append(f"experiment:{experiment['experiment_id']}: {exc}")
    for metric in metrics:
        try:
            stored = save_foundry_metric(metric)
            if "_persistence_error" in (stored.get("metadata") or {}):
                summary["errors"].append(
                    f"metric:{metric['metric_id']}: {(stored.get('metadata') or {}).get('_persistence_error')}"
                )
            else:
                summary["stored_counts"]["metrics"] += 1
        except Exception as exc:  # pragma: no cover - exercised in runtime
            summary["errors"].append(f"metric:{metric['metric_id']}: {exc}")
    for review in stage_reviews:
        try:
            stored = save_foundry_stage_review(review)
            if "_persistence_error" in (stored.get("metadata") or {}):
                summary["errors"].append(
                    f"stage_review:{review['stage_gate_id']}: {(stored.get('metadata') or {}).get('_persistence_error')}"
                )
            else:
                summary["stored_counts"]["stage_reviews"] += 1
        except Exception as exc:  # pragma: no cover - exercised in runtime
            summary["errors"].append(f"stage_review:{review['stage_gate_id']}: {exc}")

    return summary
