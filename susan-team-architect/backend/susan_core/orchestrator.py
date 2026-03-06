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
from susan_core.phases import intake, analysis, team_design, datasets, execution, behavioral_economics


async def run_susan(company: str, mode: str = "full", output_dir: Path | None = None):
    """Execute Susan's complete planning session."""
    if output_dir is None:
        output_dir = config.companies_dir / company / "susan-outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  SUSAN — Team Architect Planning Session")
    print(f"  Company: {company}")
    print(f"  Mode: {mode}")
    print(f"  Started: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")

    context = {"company": company}

    # Phase 1: Intake
    print("[Phase 1/6] Company Intake...")
    profile = await intake.run(company, context)
    (output_dir / "company-profile.json").write_text(json.dumps(profile, indent=2, default=str))
    context["profile"] = profile
    print(f"  Done — profile generated")

    # Phase 2: Analysis
    print("[Phase 2/6] Gap Analysis...")
    analysis_result = await analysis.run(company, context)
    (output_dir / "analysis-report.json").write_text(json.dumps(analysis_result, indent=2, default=str))
    context["analysis"] = analysis_result
    print(f"  Done — {len(analysis_result.get('capability_gaps', []))} gaps identified")

    # Phase 3: Team Design
    print("[Phase 3/6] Team Design...")
    team = await team_design.run(company, context)
    (output_dir / "team-manifest.json").write_text(json.dumps(team, indent=2, default=str))
    context["team"] = team
    print(f"  Done — {team.get('total_agents', '?')} agents designed")

    # Phase 4: Dataset Planning
    print("[Phase 4/6] Dataset Planning...")
    ds = await datasets.run(company, context)
    (output_dir / "dataset-requirements.json").write_text(json.dumps(ds, indent=2, default=str))
    context["datasets"] = ds
    print(f"  Done — {len(ds.get('datasets', []))} data sources identified")

    # Phase 5: Execution Plan
    print("[Phase 5/6] Execution Plan...")
    plan = await execution.run(company, context)
    (output_dir / "execution-plan.md").write_text(
        plan if isinstance(plan, str) else json.dumps(plan, indent=2, default=str)
    )
    context["execution_plan"] = plan
    print(f"  Done — execution plan generated")

    # Phase 6: Behavioral Economics Audit
    print("[Phase 6/6] Behavioral Economics Audit...")
    be = await behavioral_economics.run(company, context)
    (output_dir / "be-audit.json").write_text(json.dumps(be, indent=2, default=str))
    print(f"  Done — BE audit complete")

    # Store in Supabase
    try:
        from supabase import create_client
        sb = create_client(config.supabase_url, config.supabase_key)
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
    parser.add_argument("--mode", default="full", choices=["full", "quick", "audit"])
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    asyncio.run(run_susan(args.company, args.mode, args.output_dir))


if __name__ == "__main__":
    main()
