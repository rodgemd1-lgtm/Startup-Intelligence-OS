#!/usr/bin/env python3
"""
Agent Budget Report — Jake's Fleet Cost Governance
Reads ~/.openclaw/agent-budgets.json and displays current month budget status.

Usage:
    python3 bin/agent-budget-report.py
    python3 bin/agent-budget-report.py --json     # machine-readable output
"""

import json
import os
import sys
import random
from datetime import datetime, date
from pathlib import Path

BUDGET_CONFIG = Path.home() / ".openclaw" / "agent-budgets.json"

# ---------------------------------------------------------------------------
# Placeholder usage data
# In production this would pull from:
#   - Anthropic API usage dashboard
#   - OpenClaw session logs
#   - ~/.openclaw/logs/governance-audit.jsonl
# For now we generate realistic placeholder estimates based on expected patterns.
# ---------------------------------------------------------------------------

def load_budget_config() -> dict:
    if not BUDGET_CONFIG.exists():
        print(f"ERROR: Budget config not found at {BUDGET_CONFIG}")
        sys.exit(1)
    with open(BUDGET_CONFIG) as f:
        return json.load(f)


def get_placeholder_usage(agent_budgets: dict) -> dict:
    """
    Generate placeholder usage estimates for current month.
    Weights reflect expected usage patterns:
      - Jake: heavy daily use (40-70% of budget)
      - ARIA/Oracle Brief: scheduled daily runs (30-60%)
      - Others: moderate sporadic use (10-40%)
    """
    today = date.today()
    days_in_month = 30
    day_of_month = today.day
    month_progress = day_of_month / days_in_month

    usage_patterns = {
        "jake":              (0.40, 0.70),
        "kira":              (0.10, 0.35),
        "aria":              (0.30, 0.60),
        "scout":             (0.10, 0.30),
        "steve":             (0.05, 0.25),
        "compass":           (0.05, 0.25),
        "atlas":             (0.15, 0.40),
        "forge":             (0.10, 0.35),
        "sentinel":          (0.05, 0.20),
        "research_director": (0.10, 0.30),
        "oracle_brief":      (0.30, 0.60),
        "ledger":            (0.05, 0.20),
    }

    usage = {}
    # Use deterministic seed so report is stable within a given day
    rng = random.Random(today.toordinal())

    for agent_id, config in agent_budgets.items():
        budget = config["monthly_budget"]
        lo, hi = usage_patterns.get(agent_id, (0.10, 0.30))
        # Scale by how far into the month we are
        pct = rng.uniform(lo, hi) * month_progress
        spent = round(budget * pct, 2)
        usage[agent_id] = spent

    return usage


def format_bar(pct: float, width: int = 20) -> str:
    filled = int(pct / 100 * width)
    filled = min(filled, width)
    bar = "#" * filled + "-" * (width - filled)
    return f"[{bar}]"


def status_indicator(pct: float, alert_pct: float, pause_pct: float) -> str:
    if pct >= pause_pct:
        return "!! PAUSED"
    elif pct >= alert_pct:
        return "!! ALERT"
    elif pct >= 50:
        return "   watch"
    else:
        return "   ok"


def run_report(as_json: bool = False):
    config = load_budget_config()
    agent_budgets = config["agent_budgets"]
    total_budget = config["total_monthly_budget"]
    alert_pct = config.get("alert_threshold_pct", 75)
    pause_pct = config.get("auto_pause_threshold_pct", 90)

    usage = get_placeholder_usage(agent_budgets)
    total_spent = sum(usage.values())
    total_pct = round(total_spent / total_budget * 100, 1)

    today = date.today()
    month_label = today.strftime("%B %Y")

    if as_json:
        output = {
            "month": month_label,
            "date": today.isoformat(),
            "total_budget": total_budget,
            "total_spent": round(total_spent, 2),
            "total_remaining": round(total_budget - total_spent, 2),
            "total_pct_used": total_pct,
            "status": "PAUSED" if total_pct >= pause_pct else "ALERT" if total_pct >= alert_pct else "OK",
            "agents": {},
        }
        for agent_id, cfg in agent_budgets.items():
            spent = usage[agent_id]
            budget = cfg["monthly_budget"]
            pct = round(spent / budget * 100, 1) if budget > 0 else 0
            output["agents"][agent_id] = {
                "display_name": cfg["display_name"],
                "budget": budget,
                "spent": spent,
                "remaining": round(budget - spent, 2),
                "pct_used": pct,
                "model": cfg["default_model"],
                "status": "PAUSED" if pct >= pause_pct else "ALERT" if pct >= alert_pct else "OK",
            }
        print(json.dumps(output, indent=2))
        return

    # ---- Human-readable report ----
    print()
    print("=" * 72)
    print(f"  AGENT FLEET BUDGET REPORT — {month_label}")
    print(f"  Generated: {today.isoformat()}")
    print(f"  Data: placeholder estimates (wire to API for actuals)")
    print("=" * 72)
    print()

    # Per-agent table
    header = f"  {'Agent':<22} {'Budget':>7} {'Spent':>7} {'Left':>7} {'%':>5}  {'Bar':<22} {'Status'}"
    print(header)
    print("  " + "-" * 68)

    flagged = []
    for agent_id, cfg in agent_budgets.items():
        name = cfg["display_name"]
        budget = cfg["monthly_budget"]
        spent = usage[agent_id]
        remaining = budget - spent
        pct = round(spent / budget * 100, 1) if budget > 0 else 0
        bar = format_bar(pct)
        status = status_indicator(pct, alert_pct, pause_pct)

        print(f"  {name:<22} ${budget:>6.2f} ${spent:>6.2f} ${remaining:>6.2f} {pct:>4.1f}%  {bar}  {status}")

        if pct >= alert_pct:
            flagged.append((name, pct, budget, spent))

    # Totals
    print("  " + "-" * 68)
    total_remaining = total_budget - total_spent
    total_bar = format_bar(total_pct)
    total_status = status_indicator(total_pct, alert_pct, pause_pct)
    print(f"  {'TOTAL':<22} ${total_budget:>6.2f} ${total_spent:>6.2f} ${total_remaining:>6.2f} {total_pct:>4.1f}%  {total_bar}  {total_status}")
    print()

    # Flags
    if flagged:
        print("  FLAGGED AGENTS:")
        for name, pct, budget, spent in flagged:
            overage = "" if pct < pause_pct else f" — AUTO-PAUSED at {pause_pct}%"
            print(f"    {name}: {pct:.1f}% of ${budget:.2f} budget used (${spent:.2f} spent){overage}")
        print()
    else:
        print("  No agents approaching budget limits.")
        print()

    # Model rates reference
    print("  MODEL RATES:")
    print(f"    Opus   — $15.00/M input, $75.00/M output")
    print(f"    Sonnet — $ 3.00/M input, $15.00/M output")
    print(f"    Haiku  — $ 0.25/M input, $ 1.25/M output")
    print()
    print("  NOTE: Usage data is placeholder. Wire to Anthropic API usage")
    print("  dashboard or OpenClaw session logs for actual cost tracking.")
    print("=" * 72)
    print()


if __name__ == "__main__":
    as_json = "--json" in sys.argv
    run_report(as_json=as_json)
