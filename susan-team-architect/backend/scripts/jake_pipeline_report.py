#!/usr/bin/env python3
"""Jake Business Pipeline Report — deal tracking, pipeline health, revenue forecast.

Usage:
    .venv/bin/python scripts/jake_pipeline_report.py
    .venv/bin/python scripts/jake_pipeline_report.py --report pipeline
    .venv/bin/python scripts/jake_pipeline_report.py --report revenue
    .venv/bin/python scripts/jake_pipeline_report.py --report health
    .venv/bin/python scripts/jake_pipeline_report.py --add-deal
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def load_env():
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        import os
        with open(env_path) as fh:
            for line in fh:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())


def main() -> None:
    load_env()
    from jake_pipeline.deals import DealTracker, DealStage
    from jake_pipeline.monitor import PipelineMonitor
    from jake_pipeline.revenue import RevenueAnalyzer
    from jake_pipeline.health import CustomerHealthTracker

    parser = argparse.ArgumentParser(description="Jake Business Pipeline Report")
    parser.add_argument("--report", choices=["pipeline", "revenue", "health", "all"], default="all")
    args = parser.parse_args()

    tracker = DealTracker()
    monitor = PipelineMonitor(tracker)
    analyzer = RevenueAnalyzer(tracker)
    health_tracker = CustomerHealthTracker()

    print("╔══════════════════════════════════╗")
    print("║  JAKE BUSINESS PIPELINE REPORT   ║")
    print("╚══════════════════════════════════╝")

    if args.report in ("pipeline", "all"):
        print()
        print(monitor.weekly_report())

    if args.report in ("revenue", "all"):
        print()
        print(analyzer.revenue_impact_report())

    if args.report in ("health", "all"):
        print()
        print(health_tracker.health_summary())

    # Show overdue actions
    if args.report == "all":
        overdue = tracker.overdue_actions()
        if overdue:
            print("\n══ OVERDUE ACTIONS ══")
            for deal in overdue:
                print(f"  ✗ {deal.company}: {deal.next_action} (due {deal.next_action_due})")

    print("\n✓ Pipeline report complete")


if __name__ == "__main__":
    main()
