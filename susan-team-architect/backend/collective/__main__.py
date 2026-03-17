"""Layer 7 Collective Intelligence CLI.

Usage:
    python -m collective --command [research-plan|agent-factory|transfer|predict|evolve|full]

Commands:
    research-plan  -- Generate research programs for all capability gaps
    agent-factory  -- Propose new agents from task patterns
    transfer       -- Identify and execute knowledge transfers
    predict        -- Predict maturity timelines for all capabilities
    evolve         -- Generate evolution proposals
    full           -- Run all analyses
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_project_root() -> Path:
    """Walk up from this file to find the repo root (contains .startup-os/)."""
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / ".startup-os").exists():
            return parent
    return p.parent.parent.parent


def _memory_dir(project_root: Path) -> Path:
    return project_root / "susan-team-architect" / "backend" / "data" / "memory"


def _runs_dir(project_root: Path) -> Path:
    return project_root / "apps" / "decision_os" / "data" / "runs"


def _agents_dir(project_root: Path) -> Path:
    return project_root / "susan-team-architect" / "agents"


def _tips_dir(project_root: Path) -> Path:
    return _memory_dir(project_root) / "tips"


# ------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------


def cmd_research_plan(project_root: Path) -> None:
    """Generate research programs for all capability gaps."""
    from .research_planner import ResearchPlanner

    memory_dir = _memory_dir(project_root)
    planner = ResearchPlanner(project_root, memory_dir)

    print("Analyzing capability maturity gaps...")
    gaps = planner.analyze_maturity_gaps()
    print(f"  Found {len(gaps)} capabilities with maturity gaps")

    programs = planner.plan_all()
    programs = planner.prioritize(programs)
    print(f"  Generated {len(programs)} research programs")

    for prog in programs[:10]:
        print(f"  [{prog.priority:>8}] {prog.name}")
        print(f"           {len(prog.research_questions)} questions, "
              f"{prog.estimated_duration_weeks} weeks estimated")

    if programs:
        out_path = memory_dir / "research_programs" / "programs.yaml"
        planner.save_programs(programs, out_path)
        print(f"\n  Saved to {out_path}")


def cmd_agent_factory(project_root: Path) -> None:
    """Propose new agents from task patterns."""
    from .agent_factory import AgentFactory

    agents_dir = _agents_dir(project_root)
    perf_dir = _memory_dir(project_root) / "performance"
    runs_dir = _runs_dir(project_root)

    factory = AgentFactory(agents_dir, perf_dir)

    print("Analyzing task patterns in run history...")
    patterns = factory.analyze_task_patterns(runs_dir)
    print(f"  Found {len(patterns)} unserved task patterns")

    proposals = factory.propose_agents(runs_dir)
    print(f"  Proposed {len(proposals)} new agents")

    for bp in proposals:
        validation = bp.test_results or {}
        status = "VALID" if validation.get("valid", False) else "ISSUES"
        print(f"  [{bp.model:>6}] {bp.name} ({status})")
        print(f"           Domain: {bp.domain}, Keywords: {bp.routing_keywords[:5]}")
        warnings = validation.get("warnings", [])
        for w in warnings:
            print(f"           WARNING: {w}")

    if proposals:
        out_dir = _memory_dir(project_root) / "agent_proposals"
        out_dir.mkdir(parents=True, exist_ok=True)
        for bp in proposals:
            bp_file = out_dir / f"{bp.id}.yaml"
            bp_file.write_text(
                yaml.dump(bp.model_dump(), default_flow_style=False, sort_keys=False)
            )
            # Also write the agent .md file preview
            md_content = factory.generate_agent_file(bp)
            md_file = out_dir / f"{bp.id}.md"
            md_file.write_text(md_content)

        print(f"\n  Saved {len(proposals)} proposals to {out_dir}")


def cmd_transfer(project_root: Path) -> None:
    """Identify and report knowledge transfer opportunities."""
    from .knowledge_transfer import KnowledgeTransferEngine

    tips_dir = _tips_dir(project_root)
    agents_dir = _agents_dir(project_root)

    engine = KnowledgeTransferEngine(tips_dir, agents_dir)

    print("Mapping agent domains...")
    domain_map = engine.map_agent_domains()
    print(f"  {len(domain_map)} domains mapped across agents")

    print("Identifying transfer opportunities...")
    opportunities = engine.identify_transfer_opportunities()
    print(f"  Found {len(opportunities)} transfer opportunities")

    report = engine.generate_transfer_report()
    print()
    print(report)

    # Save report
    out_dir = _memory_dir(project_root) / "transfers"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_file = out_dir / "transfer-report.md"
    report_file.write_text(report)
    print(f"\n  Report saved to {report_file}")


def cmd_predict(project_root: Path) -> None:
    """Predict maturity timelines for all capabilities."""
    from .capability_predictor import CapabilityPredictor

    runs_dir = _runs_dir(project_root)
    predictor = CapabilityPredictor(project_root, runs_dir)

    print("Loading capabilities and computing predictions...")
    predictions = predictor.predict_all()
    print(f"  Generated {len(predictions)} predictions")

    forecast = predictor.format_forecast(predictions)
    print()
    print(forecast)

    # Save forecast
    out_dir = _memory_dir(project_root) / "predictions"
    out_dir.mkdir(parents=True, exist_ok=True)
    forecast_file = out_dir / "forecast.md"
    forecast_file.write_text(forecast)

    # Also save structured data
    data_file = out_dir / "predictions.yaml"
    payload = {
        "generated_at": _iso_now(),
        "prediction_count": len(predictions),
        "predictions": [p.model_dump() for p in predictions],
        "build_sequence": predictor.optimal_build_sequence(predictions),
    }
    data_file.write_text(
        yaml.dump(payload, default_flow_style=False, sort_keys=False)
    )

    print(f"\n  Forecast saved to {forecast_file}")
    print(f"  Data saved to {data_file}")


def cmd_evolve(project_root: Path) -> None:
    """Generate evolution proposals."""
    from .evolution_engine import EvolutionEngine

    agents_dir = _agents_dir(project_root)
    departments_dir = project_root / ".startup-os" / "departments"
    runs_dir = _runs_dir(project_root)
    tips_dir = _tips_dir(project_root)

    engine = EvolutionEngine(project_root, agents_dir, departments_dir)

    print("Detecting structural patterns...")
    patterns = engine.detect_patterns(runs_dir, tips_dir)
    print(f"  Found {len(patterns)} patterns")

    proposals = engine.generate_proposals(runs_dir, tips_dir)
    print(f"  Generated {len(proposals)} evolution proposals")

    formatted = engine.format_proposals(proposals)
    print()
    print(formatted)

    if proposals:
        out_dir = _memory_dir(project_root) / "evolutions"
        engine.save_proposals(proposals, out_dir)

        # Also save formatted report
        report_file = out_dir / "evolution-report.md"
        report_file.write_text(formatted)

        print(f"\n  Saved {len(proposals)} proposals to {out_dir}")


def cmd_full(project_root: Path) -> None:
    """Run all analyses."""
    print("=" * 70)
    print("  LAYER 7 COLLECTIVE INTELLIGENCE -- FULL ANALYSIS")
    print(f"  Generated: {_iso_now()}")
    print("=" * 70)

    print("\n" + "-" * 70)
    print("  1. RESEARCH PROGRAMS")
    print("-" * 70)
    cmd_research_plan(project_root)

    print("\n" + "-" * 70)
    print("  2. AGENT FACTORY")
    print("-" * 70)
    cmd_agent_factory(project_root)

    print("\n" + "-" * 70)
    print("  3. KNOWLEDGE TRANSFER")
    print("-" * 70)
    cmd_transfer(project_root)

    print("\n" + "-" * 70)
    print("  4. CAPABILITY PREDICTIONS")
    print("-" * 70)
    cmd_predict(project_root)

    print("\n" + "-" * 70)
    print("  5. SYSTEM EVOLUTION")
    print("-" * 70)
    cmd_evolve(project_root)

    print("\n" + "=" * 70)
    print("  ANALYSIS COMPLETE")
    print("=" * 70)


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="collective",
        description="Layer 7 Collective Intelligence Framework -- "
                    "Self-directed research, agent creation, knowledge transfer, "
                    "predictive maturity modeling, and operating model evolution.",
    )
    parser.add_argument(
        "--command",
        required=True,
        choices=[
            "research-plan",
            "agent-factory",
            "transfer",
            "predict",
            "evolve",
            "full",
        ],
        help="Which analysis to run.",
    )
    args = parser.parse_args()

    project_root = get_project_root()
    print(f"Project root: {project_root}")

    commands = {
        "research-plan": cmd_research_plan,
        "agent-factory": cmd_agent_factory,
        "transfer": cmd_transfer,
        "predict": cmd_predict,
        "evolve": cmd_evolve,
        "full": cmd_full,
    }
    commands[args.command](project_root)


if __name__ == "__main__":
    main()
