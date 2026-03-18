"""Trust Dashboard — CLI table and markdown report."""
from __future__ import annotations

from datetime import datetime, timezone

from trust import config
from trust.tracker import TrustTracker


def generate_cli_table(tracker: TrustTracker) -> str:
    profiles = tracker.all_profiles()
    if not profiles:
        return "Trust Dashboard\nNo chain trust profiles recorded yet."

    header = f"{'Chain':<25s} {'Level':<12s} {'Runs':<8s} {'Accuracy':<10s} {'Last Run':<20s}"
    sep = "=" * len(header)
    lines = [
        "Trust Dashboard",
        sep,
        header,
        "-" * len(header),
    ]
    for p in sorted(profiles, key=lambda x: x.chain_name):
        cap = config.blast_radius_cap(p.chain_name)
        runs_str = f"{p.total_runs}/inf" if cap else f"{p.total_runs}"
        accuracy_str = f"{p.accuracy:.1f}%" if p.total_runs > 0 else "—"
        last_run = p.last_run_at[:19] if p.last_run_at else "never"
        lines.append(f"{p.chain_name:<25s} {p.level:<12s} {runs_str:<8s} {accuracy_str:<10s} {last_run}")

    lines.append(sep)
    lines.append("  inf = blast radius cap, cannot graduate past SUPERVISED")
    return "\n".join(lines)


def generate_markdown(tracker: TrustTracker) -> str:
    profiles = tracker.all_profiles()
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        f"# Trust Dashboard — {date_str}",
        "",
        "| Chain | Level | Runs | Accuracy | Escalation Rate | Last Run |",
        "|-------|-------|------|----------|-----------------|----------|",
    ]
    for p in sorted(profiles, key=lambda x: x.chain_name):
        cap = config.blast_radius_cap(p.chain_name)
        runs_str = f"{p.total_runs}/inf" if cap else str(p.total_runs)
        accuracy_str = f"{p.accuracy:.1f}%" if p.total_runs > 0 else "—"
        escalation_str = f"{p.escalation_rate:.1f}%" if p.total_runs > 0 else "—"
        last_run = p.last_run_at[:19] if p.last_run_at else "never"
        lines.append(f"| {p.chain_name} | {p.level} | {runs_str} | {accuracy_str} | {escalation_str} | {last_run} |")

    lines.append("")
    lines.append("*inf = blast radius cap, cannot graduate past SUPERVISED*")
    return "\n".join(lines)
