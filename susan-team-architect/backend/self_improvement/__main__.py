"""Layer 6 Self-Improvement System CLI.

Usage:
    python -m self_improvement --command timg
    python -m self_improvement --command routing
    python -m self_improvement --command telemetry
    python -m self_improvement --command debate --topic "Should we invest in X?"
    python -m self_improvement --command dashboard
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _get_project_root() -> Path:
    """Walk up from this file to find the repo root (contains .startup-os/)."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / ".startup-os").exists():
            return parent
    # Fallback: assume standard layout
    return current.parent.parent.parent


def _get_backend_root() -> Path:
    """Return the susan-team-architect/backend/ directory."""
    project_root = _get_project_root()
    return project_root / "susan-team-architect" / "backend"


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def cmd_timg(project_root: Path) -> None:
    """Run the TIMG pipeline on all run YAML files."""
    from self_improvement.timg_pipeline import TIMGPipeline

    runs_dir = project_root / "apps" / "decision_os" / "data" / "runs"
    memory_path = _get_backend_root() / "memory"

    print(f"TIMG Pipeline")
    print(f"  Runs directory: {runs_dir}")
    print(f"  Memory module:  {memory_path}")
    print()

    pipeline = TIMGPipeline(memory_module_path=memory_path)
    raw_tips = pipeline.process_all_runs(runs_dir)

    print(f"Extracted {len(raw_tips)} raw tip candidates.")
    print()

    # Format for storage
    formatted = pipeline.format_tips_for_storage(raw_tips)
    print(f"After deduplication: {len(formatted)} unique tips.")
    print()

    # Summary by type
    type_counts: dict[str, int] = {}
    for tip in formatted:
        t = tip.get("tip_type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    print("Tips by type:")
    for tip_type, count in sorted(type_counts.items()):
        print(f"  {tip_type}: {count}")
    print()

    # Show top 10 tips
    print("Top tips (first 10):")
    for tip in formatted[:10]:
        content = tip.get("content", "")
        preview = content[:120] + "..." if len(content) > 120 else content
        conf = tip.get("confidence", 0.0)
        print(f"  [{tip['tip_type']}] (confidence {conf:.2f}) {preview}")
    print()

    # Optionally save to YAML
    output_dir = _get_backend_root() / "data" / "memory" / "performance"
    output_dir.mkdir(parents=True, exist_ok=True)
    import yaml
    from datetime import datetime, timezone

    output_path = output_dir / "timg_latest.yaml"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_tips": len(formatted),
        "tips_by_type": type_counts,
        "tips": formatted[:50],  # Save top 50
    }
    with open(output_path, "w", encoding="utf-8") as fh:
        yaml.dump(payload, fh, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"Saved to: {output_path}")


def cmd_routing(project_root: Path) -> None:
    """Process routing feedback and compute weight adjustments."""
    from self_improvement.routing_feedback import RoutingFeedbackProcessor

    data_dir = project_root / "apps" / "decision_os" / "data"
    departments_dir = project_root / ".startup-os" / "departments"

    print(f"Routing Feedback Processor")
    print(f"  Data directory:       {data_dir}")
    print(f"  Departments directory: {departments_dir}")
    print()

    processor = RoutingFeedbackProcessor(data_dir)

    # Collect feedback
    feedback = processor.collect_feedback()
    print(f"Collected {len(feedback)} feedback records from run files.")

    if not feedback:
        print("No routing feedback found. Exiting.")
        return

    # Show feedback summary
    dept_counts: dict[str, int] = {}
    for fb in feedback:
        dept_counts[fb.routed_department] = dept_counts.get(fb.routed_department, 0) + 1

    print()
    print("Feedback by department:")
    for dept, count in sorted(dept_counts.items()):
        print(f"  {dept}: {count} records")
    print()

    # Compute adjustments
    adjustments = processor.compute_adjustments(feedback, departments_dir)
    print(f"Computed {len(adjustments)} routing weight entries.")
    print()

    # Show adjustments that changed
    changed = [w for w in adjustments if w.learned_adjustment != 0.0]
    if changed:
        print("Adjusted weights:")
        for w in changed[:20]:
            direction = "+" if w.learned_adjustment > 0 else ""
            print(
                f"  {w.department}/{w.keyword}: "
                f"{w.base_weight:.2f} {direction}{w.learned_adjustment:.3f} "
                f"= {w.effective_weight:.3f} "
                f"(samples: {w.sample_count})"
            )
    else:
        print("No weight adjustments needed (all departments in normal range).")
    print()

    # Apply and save
    output_path = processor.apply_adjustments(adjustments, departments_dir)
    print(f"Weights saved to: {output_path}")
    print()

    # Generate report
    report = processor.generate_report()
    report_path = _get_backend_root() / "data" / "memory" / "routing_weights" / "routing_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(report)
    print(f"Report saved to: {report_path}")


def cmd_telemetry(project_root: Path) -> None:
    """Collect and display agent performance telemetry."""
    from self_improvement.performance_telemetry import PerformanceTelemetry

    data_dir = project_root / "apps" / "decision_os" / "data"

    print(f"Agent Performance Telemetry")
    print(f"  Data directory: {data_dir}")
    print()

    telemetry = PerformanceTelemetry(data_dir)
    records = telemetry.collect_records()

    print(f"Collected {len(records)} performance records.")
    print()

    if not records:
        print("No performance records found.")
        return

    # Show per-agent summary
    agent_stats = telemetry.aggregate_by_agent(records)
    print("Agent summary:")
    for name, stats in sorted(agent_stats.items()):
        print(
            f"  {name}: {stats['total_runs']} runs, "
            f"quality={stats['avg_quality']:.3f}, "
            f"success={stats['success_rate']:.0%}, "
            f"avg_tokens={stats['avg_tokens']}"
        )
    print()

    # Show per-domain summary
    domain_stats = telemetry.aggregate_by_domain(records)
    print("Domain summary:")
    for domain, stats in sorted(domain_stats.items()):
        print(
            f"  {domain}: {stats['total_runs']} runs, "
            f"quality={stats['avg_quality']:.3f}, "
            f"success={stats['success_rate']:.0%}"
        )
    print()

    # Show trends
    trends = telemetry.compute_trends(records)
    print(f"Performance trend: {trends.get('trend_direction', 'unknown')}")
    print(f"  Quality delta:      {trends.get('quality_delta', 0):+.4f}")
    print(f"  Token delta:        {trends.get('token_delta', 0):+d}")
    print(f"  Success rate delta: {trends.get('success_rate_delta', 0):+.4f}")
    print()

    # Agent ranking
    ranked = telemetry.rank_agents(records)
    print("Agent rankings:")
    for agent in ranked:
        print(
            f"  #{agent['rank']} {agent['agent_name']}: "
            f"composite={agent['composite_score']:.4f}"
        )
    print()


def cmd_debate(project_root: Path, topic: str) -> None:
    """Run a grounded multi-position debate on a topic."""
    from self_improvement.debate_upgrade import GroundedDebateEngine

    evidence_dir = project_root / "apps" / "decision_os" / "data" / "evidence"
    capabilities_dir = project_root / ".startup-os" / "capabilities"

    print(f"Grounded Debate Engine")
    print(f"  Topic:           {topic}")
    print(f"  Evidence dir:    {evidence_dir}")
    print(f"  Capabilities dir: {capabilities_dir}")
    print()

    engine = GroundedDebateEngine(evidence_dir, capabilities_dir)

    # Gather evidence
    evidence = engine.gather_evidence(topic)
    print(f"Found {len(evidence)} relevant evidence items.")
    if evidence:
        print("Top evidence:")
        for ev in evidence[:5]:
            print(
                f"  [{ev['id']}] {ev['title']} "
                f"(relevance: {ev['relevance_score']:.2f}, "
                f"confidence: {ev['confidence']:.2f})"
            )
    print()

    # Run debate
    arguments = engine.run_debate(topic)
    print(f"Generated {len(arguments)} position arguments.")
    print()

    for arg in arguments:
        print(f"### {arg.position.upper()} (confidence: {arg.confidence:.2f}, source: {arg.source})")
        print(f"Evidence refs: {len(arg.evidence_ids)}")
        # Print first 300 chars of argument
        preview = arg.argument[:300]
        if len(arg.argument) > 300:
            preview += "..."
        print(preview)
        print()

    # Synthesize
    recommendation = engine.synthesize_recommendation(arguments)
    print("=" * 60)
    print("SYNTHESIS")
    print("=" * 60)
    print(f"Confidence: {recommendation['confidence']:.2f}")
    print(f"Grounded arguments: {recommendation['grounded_count']}/{recommendation['argument_count']}")
    print(f"Key evidence: {', '.join(recommendation['key_evidence'][:5])}")
    print()
    print("RECOMMENDATION:")
    print(recommendation["recommendation"])
    print()
    print("COUNTER-RECOMMENDATION:")
    print(recommendation["counter_recommendation"])
    print()

    if "position_confidences" in recommendation:
        print("Position confidences:")
        for pos, conf in recommendation["position_confidences"].items():
            print(f"  {pos}: {conf:.3f}")


def cmd_dashboard(project_root: Path) -> None:
    """Generate and display the full performance dashboard."""
    from self_improvement.performance_telemetry import PerformanceTelemetry

    data_dir = project_root / "apps" / "decision_os" / "data"

    telemetry = PerformanceTelemetry(data_dir)
    records = telemetry.collect_records()

    if not records:
        print("No performance records found. Cannot generate dashboard.")
        return

    dashboard = telemetry.generate_dashboard(records)
    markdown = telemetry.format_dashboard(dashboard)
    print(markdown)

    # Save snapshot
    snapshot_path = telemetry.save_snapshot(records)
    print(f"\nSnapshot saved to: {snapshot_path}")

    # Save markdown report
    report_dir = _get_backend_root() / "data" / "memory" / "performance"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "dashboard_latest.md"
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(markdown)
    print(f"Dashboard saved to: {report_path}")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Parse arguments and dispatch to the appropriate command handler."""
    parser = argparse.ArgumentParser(
        description="Layer 6 Self-Improvement System for Startup Intelligence OS V10.0",
        usage="python -m self_improvement --command [timg|routing|telemetry|debate|dashboard]",
    )
    parser.add_argument(
        "--command",
        required=True,
        choices=["timg", "routing", "telemetry", "debate", "dashboard"],
        help="The self-improvement subsystem to run.",
    )
    parser.add_argument(
        "--topic",
        default="",
        help="Decision topic for the debate command.",
    )

    args = parser.parse_args()
    project_root = _get_project_root()

    print(f"Project root: {project_root}")
    print()

    if args.command == "timg":
        cmd_timg(project_root)
    elif args.command == "routing":
        cmd_routing(project_root)
    elif args.command == "telemetry":
        cmd_telemetry(project_root)
    elif args.command == "debate":
        topic = args.topic
        if not topic:
            topic = "Should we proceed with the current architecture and approach?"
            print(f"No --topic provided, using default: '{topic}'")
            print()
        cmd_debate(project_root, topic)
    elif args.command == "dashboard":
        cmd_dashboard(project_root)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
