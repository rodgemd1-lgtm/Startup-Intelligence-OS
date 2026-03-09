"""Susan Team Architect — Main orchestrator.

Usage:
    python3 -m susan_core.orchestrator --company transformfit --mode full
"""
from __future__ import annotations
import asyncio
import json
import argparse
from pathlib import Path
from datetime import datetime

from susan_core.config import config
from susan_core.phases import (
    intake,
    problem_framing,
    capability_diagnosis,
    evidence_gap_map,
    decision_brief,
    analysis,
    team_design,
    datasets,
    execution,
    behavioral_economics,
)
from susan_core.clients import get_supabase_client


def _runtime_mode(mode: str) -> str:
    return "quick" if mode == "quick" else "full"


def _write_foundry_artifacts(company: str, output_dir: Path) -> None:
    from control_plane.foundry import build_company_blueprint, render_company_blueprint_markdown

    blueprint = build_company_blueprint(company)
    (output_dir / "foundry-blueprint.json").write_text(json.dumps(blueprint, indent=2, default=str))
    (output_dir / "execution-blueprint.md").write_text(render_company_blueprint_markdown(blueprint), encoding="utf-8")


async def run_susan(company: str, mode: str = "full", output_dir: Path | None = None, refresh: bool = False):
    """Execute Susan's complete planning session."""
    if output_dir is None:
        output_dir = config.companies_dir / company / "susan-outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  SUSAN — Team Architect Planning Session")
    print(f"  Company: {company}")
    print(f"  Mode: {mode}")
    if _runtime_mode(mode) != mode:
        print(f"  Runtime mode: {_runtime_mode(mode)}")
    print(f"  Started: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")

    context = {"company": company, "refresh": refresh, "mode": _runtime_mode(mode), "requested_mode": mode}

    # Phase 1: Intake
    print("[Phase 1/6] Company Intake...")
    profile = await intake.run(company, context)
    (output_dir / "company-profile.json").write_text(json.dumps(profile, indent=2, default=str))
    context["profile"] = profile
    print(f"  Done — profile generated")

    # Phase 2: Problem framing
    print("[Phase 2/9] Problem Framing...")
    framing = await problem_framing.run(company, context)
    (output_dir / "problem-framing.json").write_text(json.dumps(framing, indent=2, default=str))
    context["problem_framing"] = framing
    print("  Done — decision frame established")

    # Phase 3: Capability diagnosis
    print("[Phase 3/9] Capability Diagnosis...")
    diagnosis = await capability_diagnosis.run(company, context)
    (output_dir / "capability-diagnosis.json").write_text(json.dumps(diagnosis, indent=2, default=str))
    context["capability_diagnosis"] = diagnosis
    print(f"  Done — {len(diagnosis.get('capability_gaps', []))} capability gaps mapped")

    # Phase 4: Evidence gap map
    print("[Phase 4/9] Evidence Gap Map...")
    evidence_map = await evidence_gap_map.run(company, context)
    (output_dir / "evidence-gap-map.json").write_text(json.dumps(evidence_map, indent=2, default=str))
    context["evidence_gap_map"] = evidence_map
    print(f"  Done — {len(evidence_map.get('research_tracks', []))} research tracks identified")

    # Phase 5: Decision brief
    print("[Phase 5/9] Decision Brief...")
    brief = await decision_brief.run(company, context)
    (output_dir / "decision-brief.json").write_text(json.dumps(brief, indent=2, default=str))
    context["decision_brief"] = brief
    print("  Done — routing brief generated")

    # Phase 6: Composite analysis for backward compatibility
    print("[Phase 6/9] Analysis Synthesis...")
    analysis_result = await analysis.run(company, context)
    (output_dir / "analysis-report.json").write_text(json.dumps(analysis_result, indent=2, default=str))
    context["analysis"] = analysis_result
    print(f"  Done — {len(analysis_result.get('capability_gaps', []))} gaps identified")

    # Phase 7: Team Design
    print("[Phase 7/9] Team Design...")
    team = await team_design.run(company, context)
    (output_dir / "team-manifest.json").write_text(json.dumps(team, indent=2, default=str))
    context["team"] = team
    print(f"  Done — {team.get('total_agents', '?')} agents designed")

    # Phase 8: Dataset Planning
    print("[Phase 8/9] Dataset Planning...")
    print("[Phase 9/9] Behavioral Economics Audit...")
    ds, be = await asyncio.gather(
        datasets.run(company, context),
        behavioral_economics.run(company, context),
    )
    (output_dir / "dataset-requirements.json").write_text(json.dumps(ds, indent=2, default=str))
    context["datasets"] = ds
    print(f"  Done — {len(ds.get('datasets', []))} data sources identified")

    # Phase 9b: Execution Plan
    print("[Execution] Plan...")
    plan = await execution.run(company, context)
    (output_dir / "execution-plan.md").write_text(
        plan if isinstance(plan, str) else json.dumps(plan, indent=2, default=str)
    )
    context["execution_plan"] = plan
    print(f"  Done — execution plan generated")

    (output_dir / "be-audit.json").write_text(json.dumps(be, indent=2, default=str))
    print(f"  Done — BE audit complete")

    _write_foundry_artifacts(company, output_dir)
    print("  Done — foundry blueprint updated")

    # Store in Supabase
    try:
        sb = get_supabase_client()
        sb.table("companies").upsert({
            "id": company,
            "name": profile.get("company", company),
            "domain": profile.get("domain"),
            "stage": profile.get("stage"),
            "profile": profile,
            "team_manifest": team,
            "dataset_requirements": ds,
            "execution_plan": plan if isinstance(plan, str) else json.dumps(plan),
            "be_audit": be,
        }).execute()
    except Exception as e:
        print(f"  Warning: Could not store in Supabase: {e}")

    print(f"\n{'='*60}")
    print(f"  Planning session complete!")
    print(f"  Outputs: {output_dir}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Susan — Team Architect")
    parser.add_argument("--company", required=True, help="Company identifier")
    parser.add_argument("--mode", default="full", choices=["full", "quick", "deep", "design", "foundry", "audit"])
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--refresh", action="store_true", help="Bypass Susan phase cache for this run")
    args = parser.parse_args()
    asyncio.run(run_susan(args.company, args.mode, args.output_dir, args.refresh))


if __name__ == "__main__":
    main()
