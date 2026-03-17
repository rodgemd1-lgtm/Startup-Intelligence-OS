"""Simulated maturity harness for benchmark-backed scenario reviews."""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .models import Artifact, Evidence, OutputContract
from .store import Store
from .telemetry import start_run


ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "susan-team-architect" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from simulations.monte_carlo import run_simulation  # noqa: E402


STRONGER_WAVE_SUMMARY = BACKEND_ROOT / "artifacts" / "stronger_dataset_benchmark_wave" / "latest_summary.json"
GAP_WAVE_SUMMARY = BACKEND_ROOT / "artifacts" / "department_gap_closure_wave" / "latest_summary.json"
SYNTHETIC_REVIEW_FRAMEWORK = ROOT / ".startup-os" / "artifacts" / "research" / "synthetic-run-review-framework-2026-03-12.md"
TRAINING_OPERATOR_PACKET = ROOT / ".startup-os" / "artifacts" / "job-studio-training-operator-packet-2026-03-12.md"


@dataclass
class ScenarioSpec:
    id: str
    name: str
    department_id: str
    company_id: str
    narrative: str
    required_checks: list[str]
    benchmark_refs: list[str] = field(default_factory=list)
    eval_refs: list[str] = field(default_factory=list)
    monte_carlo_variant: str | None = None


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _ensure_evidence(store: Store, title: str, source_path: Path, source_type: str, tags: list[str]) -> Evidence:
    for existing in store.evidence.list_all():
        if existing.source_url == str(source_path):
            return existing
    evidence = Evidence(
        source_url=str(source_path),
        source_type=source_type,
        title=title,
        content=_read_text(source_path)[:12000],
        topic_tags=tags,
        domain="simulated_maturity",
        confidence=0.9,
        normalized=True,
    )
    store.evidence.save(evidence)
    return evidence


def _load_summary_result(summary_path: Path, manifest_file: str) -> dict[str, Any]:
    payload = _read_json(summary_path)
    for result in payload.get("results", []):
        if result.get("manifest_file") == manifest_file:
            return result
    raise KeyError(f"Manifest '{manifest_file}' not found in {summary_path}")


def _benchmark_score(chunks: int) -> float:
    return min(10.0, round(chunks / 32.0, 1))


def _eval_score(chunks: int) -> float:
    return min(10.0, round(chunks / 38.0, 1))


def _training_score(chunks: int) -> float:
    return min(10.0, round(chunks / 12.0, 1))


def _run_monte_carlo_variant(variant: str) -> dict[str, Any]:
    if variant == "revenue_growth":
        baseline = run_simulation(cohort_size=4_000, months=12, num_trials=40, seed=21)
        enhanced = run_simulation(
            cohort_size=4_000,
            months=12,
            num_trials=40,
            seed=22,
            onboarding_quality=1.12,
            ai_personalization=1.22,
            social_features=1.12,
            gamification=1.18,
            pricing_optimization=1.15,
        )
        base_summary = baseline.funnel_summary()
        enhanced_summary = enhanced.funnel_summary()
        delta = (
            (enhanced_summary["revenue"]["mean"] - base_summary["revenue"]["mean"])
            / max(base_summary["revenue"]["mean"], 1)
        ) * 100
        return {
            "type": "revenue_growth",
            "baseline_revenue_mean": round(base_summary["revenue"]["mean"], 2),
            "enhanced_revenue_mean": round(enhanced_summary["revenue"]["mean"], 2),
            "revenue_delta_pct": round(delta, 2),
            "conversion_mean_pct": enhanced_summary["conversion_rate"]["mean_pct"],
            "retention_day30_pct": enhanced_summary["day30_retention_rate"]["mean_pct"],
        }

    if variant == "finance_operating":
        finance = run_simulation(
            cohort_size=5_000,
            months=12,
            num_trials=40,
            seed=31,
            onboarding_quality=1.08,
            ai_personalization=1.16,
            pricing_optimization=1.18,
        )
        summary = finance.funnel_summary()
        monthly_revenue = summary["revenue"]["mean"] / 12
        baseline_burn = 180_000
        starting_cash = 2_400_000
        net_burn = max(1.0, baseline_burn - monthly_revenue)
        runway_months = starting_cash / net_burn
        return {
            "type": "finance_operating",
            "monthly_revenue_mean": round(monthly_revenue, 2),
            "revenue_p5": round(summary["revenue"]["p5"], 2),
            "revenue_p95": round(summary["revenue"]["p95"], 2),
            "assumed_monthly_burn": baseline_burn,
            "estimated_runway_months": round(runway_months, 1),
        }

    if variant == "data_decision_science":
        results = run_simulation(
            cohort_size=3_000,
            months=12,
            num_trials=60,
            seed=41,
            onboarding_quality=1.1,
            ai_personalization=1.2,
            social_features=1.15,
            pricing_optimization=1.1,
        )
        summary = results.funnel_summary()
        revenue_mean = summary["revenue"]["mean"]
        spread = max(summary["revenue"]["p95"] - summary["revenue"]["p5"], 1)
        stability = max(0.0, 1.0 - (spread / revenue_mean)) if revenue_mean else 0.0
        return {
            "type": "data_decision_science",
            "revenue_mean": round(revenue_mean, 2),
            "revenue_p5": round(summary["revenue"]["p5"], 2),
            "revenue_p95": round(summary["revenue"]["p95"], 2),
            "forecast_stability": round(stability, 3),
            "active_users_mean": round(summary["active_at_end"]["mean"], 2),
        }

    if variant == "founder_decision":
        scenario_a = run_simulation(cohort_size=2_000, months=12, num_trials=40, seed=51, onboarding_quality=1.18)
        scenario_b = run_simulation(cohort_size=2_000, months=12, num_trials=40, seed=52, ai_personalization=1.25, pricing_optimization=1.12)
        a_rev = scenario_a.funnel_summary()["revenue"]["mean"]
        b_rev = scenario_b.funnel_summary()["revenue"]["mean"]
        winning = "option_a_onboarding" if a_rev >= b_rev else "option_b_personalization"
        return {
            "type": "founder_decision",
            "option_a_revenue_mean": round(a_rev, 2),
            "option_b_revenue_mean": round(b_rev, 2),
            "winning_option": winning,
        }

    return {}


def _score_scenario(
    scenario: ScenarioSpec,
    benchmark_summary: dict[str, Any],
    eval_summary: dict[str, Any],
    training_summary: dict[str, Any],
    monte_carlo: dict[str, Any] | None,
) -> dict[str, Any]:
    checks: dict[str, bool] = {
        "benchmark_library_attached": bool(scenario.benchmark_refs),
        "eval_library_attached": bool(scenario.eval_refs),
        "synthetic_framework_attached": True,
        "reviewable_output_shape": True,
        "monte_carlo_attached": scenario.monte_carlo_variant is None or bool(monte_carlo),
    }

    benchmark_score = _benchmark_score(benchmark_summary["total_chunks"])
    eval_score = _eval_score(eval_summary["total_chunks"])
    training_score = _training_score(training_summary["total_chunks"])
    checklist_score = round((sum(1 for value in checks.values() if value) / len(checks)) * 10, 1)

    weighted = [benchmark_score, eval_score, checklist_score]
    if scenario.company_id == "mike-job-studio":
        weighted.append(training_score)
    if scenario.monte_carlo_variant:
        weighted.append(10.0 if monte_carlo else 0.0)

    return {
        "checks": checks,
        "benchmark_score": benchmark_score,
        "eval_score": eval_score,
        "training_score": training_score,
        "checklist_score": checklist_score,
        "simulated_maturity_score": round(sum(weighted) / len(weighted), 1),
    }


def _scenario_markdown(
    scenario: ScenarioSpec,
    scores: dict[str, Any],
    monte_carlo: dict[str, Any] | None,
) -> str:
    lines = [
        f"# {scenario.name}",
        "",
        f"- department_id: `{scenario.department_id}`",
        f"- company_id: `{scenario.company_id}`",
        f"- simulated_maturity_score: `{scores['simulated_maturity_score']}`",
        "",
        "## Narrative",
        scenario.narrative,
        "",
        "## Required Checks",
    ]
    for check in scenario.required_checks:
        lines.append(f"- {check}")
    lines.extend(
        [
            "",
            "## Score Breakdown",
            f"- benchmark_score: `{scores['benchmark_score']}`",
            f"- eval_score: `{scores['eval_score']}`",
            f"- training_score: `{scores['training_score']}`",
            f"- checklist_score: `{scores['checklist_score']}`",
            "",
            "## Check Status",
        ]
    )
    for key, value in scores["checks"].items():
        lines.append(f"- {key}: `{str(value).lower()}`")
    if monte_carlo:
        lines.extend(["", "## Monte Carlo", "```json", json.dumps(monte_carlo, indent=2), "```"])
    return "\n".join(lines) + "\n"


def default_scenarios() -> list[ScenarioSpec]:
    return [
        ScenarioSpec(
            id="founder-decision-simulated-review",
            name="Founder Decision Room Simulated Review",
            department_id="founder-decision-room",
            company_id="founder-intelligence-os",
            narrative="Compare two strategic options with benchmark-backed framing and a simple Monte Carlo option check.",
            required_checks=[
                "Named benchmark cases attached",
                "Synthetic review framework attached",
                "Option comparison is reviewable",
                "Monte Carlo option comparison included",
            ],
            benchmark_refs=[
                ".startup-os/artifacts/founder-decision-room/benchmark-case-library.md",
                "susan-team-architect/backend/artifacts/stronger_dataset_benchmark_wave/latest_summary.md",
            ],
            eval_refs=[
                ".startup-os/artifacts/research/synthetic-run-review-framework-2026-03-12.md",
            ],
            monte_carlo_variant="founder_decision",
        ),
        ScenarioSpec(
            id="revenue-growth-simulated-review",
            name="Revenue & Growth Simulated Review",
            department_id="revenue-growth-studio",
            company_id="founder-intelligence-os",
            narrative="Stress-test pricing and onboarding changes against stronger benchmark and evaluation sources.",
            required_checks=[
                "Benchmark case library attached",
                "Synthetic eval sources attached",
                "Monte Carlo revenue scenario included",
            ],
            benchmark_refs=[
                ".startup-os/artifacts/revenue-growth/revenue-benchmark-case-library.md",
                "susan-team-architect/backend/artifacts/stronger_dataset_benchmark_wave/latest_summary.md",
            ],
            eval_refs=[
                ".startup-os/artifacts/research/synthetic-run-review-framework-2026-03-12.md",
            ],
            monte_carlo_variant="revenue_growth",
        ),
        ScenarioSpec(
            id="finance-operating-simulated-review",
            name="Finance & Operating Cadence Simulated Review",
            department_id="finance-operating-cadence-studio",
            company_id="founder-intelligence-os",
            narrative="Convert stronger benchmark and eval evidence into a runway and variance stress-test packet.",
            required_checks=[
                "Operating metrics attached",
                "Eval foundation attached",
                "Runway Monte Carlo included",
            ],
            benchmark_refs=[
                ".startup-os/artifacts/finance-operating-cadence/operating-metrics-scoreboard-template.md",
                "susan-team-architect/backend/artifacts/stronger_dataset_benchmark_wave/latest_summary.md",
            ],
            eval_refs=[
                ".startup-os/artifacts/research/synthetic-run-review-framework-2026-03-12.md",
            ],
            monte_carlo_variant="finance_operating",
        ),
        ScenarioSpec(
            id="data-decision-science-simulated-review",
            name="Data & Decision Science Simulated Review",
            department_id="data-decision-science-studio",
            company_id="founder-intelligence-os",
            narrative="Grade a forecast scenario against stronger eval sources and quantify stability from Monte Carlo output spread.",
            required_checks=[
                "Eval foundations attached",
                "Forecast review template attached",
                "Monte Carlo forecast spread included",
            ],
            benchmark_refs=[
                ".startup-os/artifacts/data-decision-science/experiment-recalibration-template.md",
            ],
            eval_refs=[
                "susan-team-architect/backend/artifacts/stronger_dataset_benchmark_wave/latest_summary.md",
                ".startup-os/artifacts/research/synthetic-run-review-framework-2026-03-12.md",
            ],
            monte_carlo_variant="data_decision_science",
        ),
        ScenarioSpec(
            id="job-studio-simulated-review",
            name="Job Studio Training Simulated Review",
            department_id="job-studio",
            company_id="mike-job-studio",
            narrative="Review a synthetic training-session build against stronger learning-science and eval foundations.",
            required_checks=[
                "Learning-science sources attached",
                "Training eval pack attached",
                "Synthetic review framework attached",
            ],
            benchmark_refs=[
                ".startup-os/artifacts/job-studio/training-evaluation-and-stage-gate-pack.md",
                ".startup-os/artifacts/job-studio-training-operator-packet-2026-03-12.md",
            ],
            eval_refs=[
                ".startup-os/artifacts/research/synthetic-run-review-framework-2026-03-12.md",
                "susan-team-architect/backend/artifacts/stronger_dataset_benchmark_wave/latest_summary.md",
            ],
        ),
    ]


def run_simulated_maturity_harness(store: Store | None = None) -> dict[str, Any]:
    store = store or Store()
    artifact_dir = store.startup_os / "artifacts" / "simulated-maturity"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    stronger_wave = _read_json(STRONGER_WAVE_SUMMARY)
    gap_wave = _read_json(GAP_WAVE_SUMMARY)

    benchmark_summary = _load_summary_result(STRONGER_WAVE_SUMMARY, "startup_os_stronger_benchmark_case_library.yaml")
    eval_summary = _load_summary_result(STRONGER_WAVE_SUMMARY, "startup_os_eval_and_synthetic_review_foundations.yaml")
    training_summary = _load_summary_result(STRONGER_WAVE_SUMMARY, "job_studio_training_learning_science_stronger.yaml")

    benchmark_ev = _ensure_evidence(
        store,
        "Stronger Dataset Benchmark Wave Summary",
        STRONGER_WAVE_SUMMARY,
        "json",
        ["benchmark", "studio_evals", "synthetic_review"],
    )
    gap_ev = _ensure_evidence(
        store,
        "Department Gap Closure Wave Summary",
        GAP_WAVE_SUMMARY,
        "json",
        ["department_gap_closure", "coverage"],
    )
    framework_ev = _ensure_evidence(
        store,
        "Synthetic Run Review Framework",
        SYNTHETIC_REVIEW_FRAMEWORK,
        "markdown",
        ["synthetic_review", "framework"],
    )
    training_ev = _ensure_evidence(
        store,
        "Job Studio Training Operator Packet",
        TRAINING_OPERATOR_PACKET,
        "markdown",
        ["job_studio", "training"],
    )

    evidence_ids = [benchmark_ev.id, gap_ev.id, framework_ev.id, training_ev.id]

    summary_rows: list[str] = []
    result_rows: list[dict[str, Any]] = []
    run_ids: list[str] = []

    for scenario in default_scenarios():
        tracer = start_run(
            store,
            trigger=f"simulated-maturity:{scenario.id}",
            company=scenario.company_id,
            project="job-studio-maturity-and-training-factory",
            mode="simulation",
        )
        run_ids.append(tracer.run.id)
        tracer.log("load_benchmark_evidence", data={"benchmark_chunks": benchmark_summary["total_chunks"]}, evidence_ids=evidence_ids, confidence=0.95)
        tracer.log("load_eval_evidence", data={"eval_chunks": eval_summary["total_chunks"], "training_chunks": training_summary["total_chunks"]}, evidence_ids=evidence_ids, confidence=0.95)
        monte_carlo = _run_monte_carlo_variant(scenario.monte_carlo_variant) if scenario.monte_carlo_variant else None
        if monte_carlo:
            tracer.log("run_monte_carlo", data=monte_carlo, evidence_ids=[gap_ev.id, benchmark_ev.id], confidence=0.82)

        scores = _score_scenario(scenario, benchmark_summary, eval_summary, training_summary, monte_carlo)
        artifact_path = artifact_dir / f"{scenario.id}.md"
        artifact_path.write_text(_scenario_markdown(scenario, scores, monte_carlo), encoding="utf-8")
        artifact = Artifact(
            name=scenario.name,
            type="simulated_maturity_review",
            run_id=tracer.run.id,
            source_refs=[str(STRONGER_WAVE_SUMMARY), str(GAP_WAVE_SUMMARY), str(SYNTHETIC_REVIEW_FRAMEWORK)],
            confidence=min(0.95, scores["simulated_maturity_score"] / 10.0),
            path=str(artifact_path.relative_to(store.root)),
        )
        store.artifacts.save(artifact)
        tracer.run.artifacts_produced.append(artifact.id)
        output = OutputContract(
            recommendation=f"Use {scenario.name} as a benchmark-backed simulated maturity review packet.",
            counter_recommendation="Do not treat synthetic proof as live 10/10 proof.",
            why_now="The stronger benchmark and eval corpora are now available for grounded scenario grading.",
            failure_modes=[
                "Benchmark corpus may still be too generic for some domains.",
                "Monte Carlo scenarios remain proxies, not live operating proof.",
            ],
            next_experiment="Promote this scenario into a repeated eval and compare synthetic scores to live outcomes.",
        )
        tracer.complete(output)

        result_rows.append(
            {
                "scenario_id": scenario.id,
                "department_id": scenario.department_id,
                "company_id": scenario.company_id,
                "run_id": tracer.run.id,
                "artifact_id": artifact.id,
                "simulated_maturity_score": scores["simulated_maturity_score"],
                "benchmark_score": scores["benchmark_score"],
                "eval_score": scores["eval_score"],
                "training_score": scores["training_score"],
                "checklist_score": scores["checklist_score"],
            }
        )
        summary_rows.append(
            f"| {scenario.name} | {scenario.department_id} | {scores['simulated_maturity_score']} | {tracer.run.id} | {artifact.id} |"
        )

    summary_path = artifact_dir / "simulated-maturity-harness-summary.md"
    summary_lines = [
        "# Simulated Maturity Harness Summary",
        "",
        f"- stronger_benchmark_chunks: `{benchmark_summary['total_chunks']}`",
        f"- stronger_eval_chunks: `{eval_summary['total_chunks']}`",
        f"- stronger_training_chunks: `{training_summary['total_chunks']}`",
        f"- gap_closure_total_chunks: `{gap_wave['total_chunks']}`",
        "",
        "## Scenario Results",
        "",
        "| Scenario | Department | Simulated score | Run | Artifact |",
        "|---|---|---:|---|---|",
    ]
    summary_lines.extend(summary_rows)
    summary_lines.append("")
    summary_lines.append("Synthetic scores indicate benchmark-backed simulated maturity only, not live 10/10 operating maturity.")
    summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    summary_artifact = Artifact(
        name="Simulated Maturity Harness Summary",
        type="simulated_maturity_summary",
        source_refs=[str(STRONGER_WAVE_SUMMARY), str(GAP_WAVE_SUMMARY)],
        confidence=0.92,
        path=str(summary_path.relative_to(store.root)),
    )
    store.artifacts.save(summary_artifact)

    return {
        "summary_path": str(summary_path),
        "summary_artifact_id": summary_artifact.id,
        "run_ids": run_ids,
        "results": result_rows,
    }

