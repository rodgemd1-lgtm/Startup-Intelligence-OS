"""
CLI entry point for the Research Daemon.

Usage:
    python -m research_daemon --command detect-gaps
    python -m research_daemon --command check-updates
    python -m research_daemon --command harvest
    python -m research_daemon --command digest
    python -m research_daemon --command status
    python -m research_daemon --command cycle

All commands resolve paths relative to the repository root, which is
auto-detected by walking up from this file's location.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _find_repo_root() -> Path:
    """Walk up from this file to find the repository root (contains .startup-os/)."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / ".startup-os").is_dir():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    # Fallback: assume standard layout
    return Path(__file__).resolve().parent.parent.parent.parent


def _find_backend_root() -> Path:
    """Locate the susan-team-architect/backend/ directory."""
    repo = _find_repo_root()
    backend = repo / "susan-team-architect" / "backend"
    if backend.is_dir():
        return backend
    # Fallback: we are inside backend already
    return Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="research_daemon",
        description="Layer 5 Autonomous Research Engine — Startup Intelligence OS",
    )
    parser.add_argument(
        "--command",
        choices=[
            "detect-gaps",
            "check-updates",
            "harvest",
            "digest",
            "status",
            "cycle",
        ],
        required=True,
        help="Command to execute.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of top-priority gaps to process (for harvest/cycle).",
    )
    parser.add_argument(
        "--stale-days",
        type=int,
        default=30,
        help="Maximum age in days before data is considered stale.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Optional output file path (overrides default).",
    )

    args = parser.parse_args()

    repo_root = _find_repo_root()
    backend_root = _find_backend_root()
    workspace_root = repo_root / ".startup-os"
    data_dir = backend_root / "data"
    memory_dir = data_dir / "memory"
    gaps_dir = memory_dir / "research_gaps"
    harvest_dir = memory_dir / "harvest_results"

    # Ensure directories exist
    gaps_dir.mkdir(parents=True, exist_ok=True)
    harvest_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------
    # Command: detect-gaps
    # ---------------------------------------------------------------
    if args.command == "detect-gaps":
        from research_daemon.gap_detector import GapDetector

        detector = GapDetector(workspace_root=workspace_root, rag_data_dir=data_dir)

        print("Detecting knowledge gaps...")
        coverage_gaps = detector.detect_gaps()
        stale_gaps = detector.detect_stale_data(max_age_days=args.stale_days)

        all_gaps = detector.prioritize_gaps(coverage_gaps + stale_gaps)

        output_path = Path(args.output) if args.output else gaps_dir / "latest_gaps.yaml"
        detector.save_gaps(all_gaps, output_path)

        print(f"\nDetected {len(coverage_gaps)} coverage gaps, {len(stale_gaps)} stale data gaps.")
        print(f"Total: {len(all_gaps)} gaps (prioritized).")
        print(f"Saved to: {output_path}")

        # Print top 10
        print("\nTop gaps:")
        for i, gap in enumerate(all_gaps[:10], 1):
            print(
                f"  {i}. [{gap.severity.upper():8s}] {gap.domain} "
                f"(coverage: {gap.current_coverage:.1f})"
            )
            print(f"     {gap.description[:100]}")

    # ---------------------------------------------------------------
    # Command: check-updates
    # ---------------------------------------------------------------
    elif args.command == "check-updates":
        from research_daemon.changelog_monitor import ChangelogMonitor

        monitor = ChangelogMonitor(project_root=repo_root)

        print("Scanning dependencies...")
        deps = monitor.scan_dependencies()
        print(f"Found {len(deps)} dependencies.")

        entries = monitor.check_for_updates(deps)
        report = monitor.generate_update_report(entries)

        output_path = (
            Path(args.output)
            if args.output
            else repo_root / ".claude" / "docs" / "dependency-updates.md"
        )
        monitor.save_report(report, output_path)

        print(f"\nFound {len(entries)} available updates:")
        breaking = [e for e in entries if e.severity == "breaking"]
        minor = [e for e in entries if e.severity == "minor"]
        patch = [e for e in entries if e.severity == "patch"]
        print(f"  Breaking: {len(breaking)}")
        print(f"  Minor:    {len(minor)}")
        print(f"  Patch:    {len(patch)}")
        print(f"\nReport saved to: {output_path}")

        if breaking:
            print("\nBreaking changes:")
            for entry in breaking:
                print(f"  - {entry.package}: -> {entry.version}")

    # ---------------------------------------------------------------
    # Command: harvest
    # ---------------------------------------------------------------
    elif args.command == "harvest":
        from research_daemon.gap_detector import GapDetector
        from research_daemon.auto_harvest import AutoHarvester

        detector = GapDetector(workspace_root=workspace_root, rag_data_dir=data_dir)
        harvester = AutoHarvester(
            data_dir=data_dir,
            manifests_dir=data_dir / "scrape_manifests",
        )

        print("Detecting gaps for harvest...")
        gaps = detector.detect_gaps()
        prioritized = detector.prioritize_gaps(gaps)
        top_gaps = prioritized[:args.top_n]

        print(f"Processing top {len(top_gaps)} gaps...")

        all_results = []
        for gap in top_gaps:
            print(f"\n  Generating manifest for: {gap.domain} ({gap.severity})")
            manifest = harvester.generate_manifest_from_gap(gap)
            results = harvester.harvest(manifest)
            all_results.extend(results)
            print(f"    -> {len(results)} harvest targets generated")

        output_path = (
            Path(args.output)
            if args.output
            else harvest_dir / "latest_harvest.yaml"
        )
        harvester.save_results(all_results, output_path)

        print(f"\nTotal harvest targets: {len(all_results)}")
        print(f"Saved to: {output_path}")

    # ---------------------------------------------------------------
    # Command: digest
    # ---------------------------------------------------------------
    elif args.command == "digest":
        from research_daemon.auto_harvest import AutoHarvester
        from research_daemon.schemas import HarvestResult

        import yaml

        harvester = AutoHarvester(
            data_dir=data_dir,
            manifests_dir=data_dir / "scrape_manifests",
        )

        # Load latest harvest results
        latest_harvest = harvest_dir / "latest_harvest.yaml"
        results: list[HarvestResult] = []

        if latest_harvest.exists():
            with open(latest_harvest, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            for record in data.get("results", []):
                results.append(HarvestResult(**record))

        digest = harvester.generate_digest(results)

        output_path = (
            Path(args.output)
            if args.output
            else memory_dir / "latest_digest.md"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(digest, encoding="utf-8")

        print(f"Digest generated with {len(results)} items.")
        print(f"Saved to: {output_path}")

    # ---------------------------------------------------------------
    # Command: status
    # ---------------------------------------------------------------
    elif args.command == "status":
        import yaml

        status_path = memory_dir / "daemon_status.yaml"

        if status_path.exists():
            with open(status_path, "r", encoding="utf-8") as fh:
                status = yaml.safe_load(fh) or {}

            ds = status.get("daemon_status", {})
            print("Research Daemon Status")
            print("=" * 40)
            print(f"  Health:          {ds.get('health', 'unknown')}")
            print(f"  Last run:        {ds.get('last_run', 'never')}")
            print(f"  Next run:        {ds.get('next_run', 'unscheduled')}")
            print(f"  Gaps detected:   {ds.get('gaps_detected', 0)}")
            print(f"  Gaps filled:     {ds.get('gaps_filled', 0)}")
            print(f"  Items harvested: {ds.get('items_harvested', 0)}")
            print(f"  Programs active: {ds.get('programs_active', 0)}")

            summary = status.get("summary", {})
            top_gaps = summary.get("top_gaps", [])
            if top_gaps:
                print(f"\n  Top gaps:")
                for g in top_gaps[:5]:
                    print(f"    - [{g.get('severity', '?'):8s}] {g.get('domain', '?')}")
        else:
            print("Research Daemon Status: No previous run found.")
            print(f"  Status file: {status_path}")
            print("  Run 'python -m research_daemon --command cycle' to start.")

    # ---------------------------------------------------------------
    # Command: cycle
    # ---------------------------------------------------------------
    elif args.command == "cycle":
        from research_daemon.daemon import ResearchDaemon

        daemon = ResearchDaemon(
            workspace_root=workspace_root,
            backend_root=backend_root,
        )

        print("Starting research daemon cycle...")
        print(f"  Workspace: {workspace_root}")
        print(f"  Backend:   {backend_root}")
        print(f"  Top-N:     {args.top_n}")
        print()

        try:
            status = daemon.run_cycle(top_n=args.top_n)

            # Save status
            status_path = memory_dir / "daemon_status.yaml"
            daemon.save_status(status_path)

            print("Cycle complete.")
            print(f"  Health:          {status.health}")
            print(f"  Gaps detected:   {status.gaps_detected}")
            print(f"  Gaps filled:     {status.gaps_filled}")
            print(f"  Items harvested: {status.items_harvested}")
            print(f"  Programs active: {status.programs_active}")
            print(f"  Next run:        {status.next_run}")
            print(f"\n  Status saved to: {status_path}")
            print(f"  Digest at:       {memory_dir / 'latest_digest.md'}")

        except RuntimeError as exc:
            print(f"Cycle failed: {exc}", file=sys.stderr)
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
