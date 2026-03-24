#!/usr/bin/env python3
"""Generate Jake business pipeline report.

Usage:
  python scripts/jake_business_report.py
  python scripts/jake_business_report.py --source oracle_health
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow running from any directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jake_brain.business_pipeline import PipelineManager, STAGES


def format_currency(value: float) -> str:
    """Format a float as USD string."""
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:.0f}"


def format_report(summary: dict, stale_deals: list, source_filter: str | None) -> str:
    now = datetime.now(timezone.utc)
    source_label = source_filter or "All Sources"

    lines = [
        f"╔══════════════════════════════════════════════════════════════╗",
        f"║       Jake Business Pipeline — {source_label:<29}║",
        f"╚══════════════════════════════════════════════════════════════╝",
        "",
        f"  Total Deal Value    : {format_currency(summary['total_value'])}",
        f"  Weighted Pipeline   : {format_currency(summary['weighted_value'])}",
        f"  Active Deals        : {summary['deal_count']}",
        "",
        "  Pipeline by Stage:",
        f"  {'Stage':<16} {'Deals':>5} {'Value':>10} {'Weighted':>10}",
        f"  {'-'*16} {'-'*5} {'-'*10} {'-'*10}",
    ]

    # Only show non-closed stages in the main table
    active_stages = [s for s in STAGES if s != "CLOSED_LOST"]
    for stage in active_stages:
        deals = summary["stages"].get(stage, [])
        if not deals and stage == "CLOSED_WON":
            continue  # Skip empty won
        stage_value = sum(d["value_usd"] for d in deals)
        stage_weighted = sum(d["weighted_value"] for d in deals)
        lines.append(
            f"  {stage:<16} {len(deals):>5} {format_currency(stage_value):>10} "
            f"{format_currency(stage_weighted):>10}"
        )

    # Deal details for active stages
    for stage in ["PROPOSAL", "NEGOTIATION", "DEMO"]:
        deals = summary["stages"].get(stage, [])
        if not deals:
            continue
        lines += ["", f"  {stage} Deals:"]
        for d in deals:
            lines += [
                f"    • {d['name']}",
                f"      Company: {d['company']}  |  Value: {format_currency(d['value_usd'])}  "
                f"|  Prob: {d['probability']:.0%}  |  Weighted: {format_currency(d['weighted_value'])}",
                f"      Next: {d['next_action'] or 'No action set'}",
            ]

    # Stale deals
    if stale_deals:
        lines += [
            "",
            f"  ⚠️  Deals Needing Action ({len(stale_deals)} stale >7 days):",
        ]
        for d in stale_deals:
            last_update = d.updated_at.strftime("%Y-%m-%d")
            lines.append(
                f"    • [{d.stage}] {d.name} — {d.company} — last updated {last_update}"
            )
            if d.next_action:
                lines.append(f"      Next: {d.next_action}")
    else:
        lines += ["", "  All deals are up to date (no stale deals)."]

    lines += [
        "",
        f"  Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Jake business pipeline report")
    parser.add_argument("--source", default=None,
                        help="Filter by source: oracle_health | alex_recruiting | susan_commercial")
    args = parser.parse_args()

    pipeline = PipelineManager()

    print(f"\nFetching pipeline data{' for ' + args.source if args.source else ''}...")

    summary = pipeline.get_pipeline_summary(source=args.source)
    stale_deals = pipeline.get_deals_needing_action(days_stale=7)

    if args.source:
        stale_deals = [d for d in stale_deals if d.source == args.source]

    if summary["deal_count"] == 0:
        print("  No active deals found.")
        print("  Run: python scripts/jake_business_report.py --seed to add sample data.")
        report = "No pipeline data available."
    else:
        report = format_report(summary, stale_deals, args.source)
        print("\n" + report)

    # Export to file
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_path = Path(f"~/.hermes/logs/business_report_{today}.txt").expanduser()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(report)
    print(f"\n  Saved to: {log_path}")


if __name__ == "__main__":
    main()
