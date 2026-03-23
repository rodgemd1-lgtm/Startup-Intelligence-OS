#!/usr/bin/env python3
"""Generate monthly Jake cost report.

Usage:
  python scripts/jake_cost_report.py
  python scripts/jake_cost_report.py --month 2026-03
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow running from any directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from supabase import create_client
from susan_core.config import config as susan_config


TABLE = "jake_cost_tracking"

MODEL_SHORT = {
    "claude-haiku-4-5-20251001": "Haiku",
    "claude-sonnet-4-6": "Sonnet",
    "claude-opus-4-6": "Opus",
}


def fetch_month_data(supabase, year: int, month: int) -> list[dict]:
    """Fetch all cost records for the given month."""
    month_start = f"{year}-{month:02d}-01T00:00:00Z"
    # Last day of month (simple: use next month first day minus 1 sec)
    if month == 12:
        month_end = f"{year + 1}-01-01T00:00:00Z"
    else:
        month_end = f"{year}-{month + 1:02d}-01T00:00:00Z"

    try:
        result = (
            supabase.table(TABLE)
            .select("model, input_tokens, output_tokens, estimated_cost_usd, task_type, employee_name, recorded_at")
            .gte("recorded_at", month_start)
            .lt("recorded_at", month_end)
            .execute()
        )
        return result.data or []
    except Exception as exc:
        print(f"  Warning: Supabase query failed — {exc}")
        return []


def aggregate(rows: list[dict]) -> dict[str, dict]:
    """Aggregate rows by model."""
    stats: dict[str, dict] = {}
    for r in rows:
        model = r.get("model", "unknown")
        short = MODEL_SHORT.get(model, model)
        if short not in stats:
            stats[short] = {
                "model_id": model,
                "calls": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0,
            }
        stats[short]["calls"] += 1
        stats[short]["input_tokens"] += int(r.get("input_tokens", 0) or 0)
        stats[short]["output_tokens"] += int(r.get("output_tokens", 0) or 0)
        stats[short]["cost"] += float(r.get("estimated_cost_usd", 0) or 0)
    return stats


def format_report(year: int, month: int, current_stats: dict, prior_stats: dict | None) -> str:
    now = datetime.now(timezone.utc)
    month_label = datetime(year, month, 1).strftime("%B %Y")

    total_calls = sum(s["calls"] for s in current_stats.values())
    total_cost = sum(s["cost"] for s in current_stats.values())
    total_in = sum(s["input_tokens"] for s in current_stats.values())
    total_out = sum(s["output_tokens"] for s in current_stats.values())

    lines = [
        f"╔══════════════════════════════════════════════════════════════╗",
        f"║          Jake Cost Report — {month_label:<32}║",
        f"╚══════════════════════════════════════════════════════════════╝",
        "",
        f"  Total calls   : {total_calls:,}",
        f"  Total tokens  : {total_in + total_out:,}  ({total_in:,} in / {total_out:,} out)",
        f"  Total cost    : ${total_cost:.4f} USD",
        "",
        f"  {'Model':<12} {'Calls':>6} {'Input Tok':>12} {'Output Tok':>12} {'Cost USD':>10}",
        f"  {'-'*12} {'-'*6} {'-'*12} {'-'*12} {'-'*10}",
    ]

    for short, stats in sorted(current_stats.items(), key=lambda x: -x[1]["cost"]):
        lines.append(
            f"  {short:<12} {stats['calls']:>6,} {stats['input_tokens']:>12,} "
            f"{stats['output_tokens']:>12,} ${stats['cost']:>9.4f}"
        )

    if prior_stats is not None:
        prior_total = sum(s["cost"] for s in prior_stats.values())
        delta = total_cost - prior_total
        arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        pct = abs(delta / prior_total * 100) if prior_total > 0 else 0
        lines += [
            "",
            f"  Month-over-month: ${prior_total:.4f} → ${total_cost:.4f} "
            f"({arrow} ${abs(delta):.4f} / {pct:.1f}%)",
        ]

    lines += [
        "",
        f"  Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Jake monthly cost report")
    parser.add_argument("--month", default=None,
                        help="Month to report (YYYY-MM). Defaults to current month.")
    args = parser.parse_args()

    if args.month:
        try:
            year, month = [int(x) for x in args.month.split("-")]
        except ValueError:
            print("Error: --month must be in YYYY-MM format")
            sys.exit(1)
    else:
        now = datetime.now(timezone.utc)
        year, month = now.year, now.month

    supabase = create_client(susan_config.supabase_url, susan_config.supabase_key)

    print(f"\nFetching cost data for {year}-{month:02d}...")
    rows = fetch_month_data(supabase, year, month)
    current_stats = aggregate(rows)

    # Prior month for comparison
    prior_month = month - 1 if month > 1 else 12
    prior_year = year if month > 1 else year - 1
    prior_rows = fetch_month_data(supabase, prior_year, prior_month)
    prior_stats = aggregate(prior_rows) if prior_rows else None

    if not rows:
        print(f"  No cost data found for {year}-{month:02d}.")
        print("  (The jake_cost_tracking table may be empty — run some tasks to populate it.)")
        report = f"No data for {year}-{month:02d}."
    else:
        report = format_report(year, month, current_stats, prior_stats)
        print("\n" + report)

    # Export to file
    log_path = Path(f"~/.hermes/logs/cost_report_{year}-{month:02d}.txt").expanduser()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(report)
    print(f"\n  Saved to: {log_path}")


if __name__ == "__main__":
    main()
