#!/usr/bin/env python3
"""Jake Cost Report — monthly spend, model routing analysis, optimization recommendations.

Usage:
    .venv/bin/python scripts/jake_cost_report.py
    .venv/bin/python scripts/jake_cost_report.py --report monthly
    .venv/bin/python scripts/jake_cost_report.py --report routing
    .venv/bin/python scripts/jake_cost_report.py --report budget
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def load_env():
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        with open(env_path) as fh:
            for line in fh:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())


def main():
    load_env()
    from jake_cost.reporter import SpendReporter
    from jake_cost.router import ModelRouter
    from jake_cost.budget import BudgetEnforcer

    parser = argparse.ArgumentParser(description="Jake Cost Optimization Report")
    parser.add_argument("--report", choices=["monthly", "routing", "budget", "all"], default="all")
    args = parser.parse_args()

    reporter = SpendReporter()
    router = ModelRouter()
    enforcer = BudgetEnforcer()

    print("╔══════════════════════════════════╗")
    print("║  JAKE COST OPTIMIZATION REPORT   ║")
    print("╚══════════════════════════════════╝")

    if args.report in ("monthly", "all"):
        print()
        print(reporter.monthly_report())

    if args.report in ("routing", "all"):
        print()
        print("═══ MODEL ROUTING TABLE ═══")
        print(router.pricing_table())
        print()
        print(reporter.savings_estimate())

    if args.report in ("budget", "all"):
        print()
        print(enforcer.budget_summary())

    print("\n✓ Cost report complete")


if __name__ == "__main__":
    main()
