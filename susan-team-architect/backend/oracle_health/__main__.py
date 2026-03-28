"""Oracle Health Department CLI.

Usage:
    python -m oracle_health --command status
    python -m oracle_health --command freshness
    python -m oracle_health --command battlecard --competitor epic
    python -m oracle_health --command battlecard-all
    python -m oracle_health --command search --query "Epic Cosmos AI"
"""
from __future__ import annotations
import argparse
import json
from datetime import datetime

from oracle_health.schemas import Competitor


def cmd_status():
    """Print department status dashboard."""
    from oracle_health.director import get_department_status
    status = get_department_status()
    print(f"""
╔══════════════════════════════════════════════════╗
║  ORACLE HEALTH DEPARTMENT STATUS                 ║
║  Generated: {status.generated.strftime('%Y-%m-%d %H:%M')}                    ║
╠══════════════════════════════════════════════════╣
║  Total Agents:     {status.total_agents:<28}║
║  Battlecards:                                    ║
║    Fresh:          {status.battlecards_fresh:<28}║
║    Aging:          {status.battlecards_aging:<28}║
║    Stale:          {status.battlecards_stale:<28}║
╠══════════════════════════════════════════════════╣
║  NEXT ACTIONS                                    ║
╠══════════════════════════════════════════════════╣""")
    for i, action in enumerate(status.next_actions[:5], 1):
        # Truncate long actions
        display = action[:47]
        print(f"║  {i}. {display:<44}║")
    print("╚══════════════════════════════════════════════════╝")


def cmd_freshness():
    """Print freshness report for all competitors."""
    from oracle_health.director import get_freshness_report, COMPETITORS
    report = get_freshness_report()
    print(f"\n{'='*60}")
    print(f"  ORACLE HEALTH — FRESHNESS REPORT")
    print(f"  Generated: {report.generated.strftime('%Y-%m-%d %H:%M')}")
    print(f"  Overall: {report.overall_health}")
    print(f"  Total RAG Chunks: {report.total_chunks}")
    print(f"{'='*60}\n")
    print(f"{'Competitor':<20} {'Status':<10} {'Chunks':<8} {'Latest':<12} {'Gaps'}")
    print(f"{'-'*20} {'-'*10} {'-'*8} {'-'*12} {'-'*20}")
    for cf in report.competitors:
        name = COMPETITORS[cf.competitor]["name"][:18]
        latest = cf.latest_data.strftime('%Y-%m-%d') if cf.latest_data else "NONE"
        gap_count = len(cf.gaps)
        icon = "🟢" if cf.freshness.value == "FRESH" else "🟡" if cf.freshness.value == "AGING" else "🔴"
        print(f"{name:<20} {icon} {cf.freshness.value:<7} {cf.chunk_count:<8} {latest:<12} {gap_count} gaps")
    print()


def cmd_battlecard(competitor_name: str):
    """Generate a battlecard for a specific competitor."""
    try:
        competitor = Competitor(competitor_name.lower())
    except ValueError:
        print(f"Unknown competitor: {competitor_name}")
        print(f"Valid: {', '.join(c.value for c in Competitor)}")
        return

    from oracle_health.battlecards import save_battlecard
    path = save_battlecard(competitor)
    print(f"Battlecard saved: {path}")

    # Also print to stdout
    print(path.read_text())


def cmd_battlecard_all():
    """Generate battlecards for all P0/P1 competitors."""
    from oracle_health.battlecards import save_all_battlecards
    paths = save_all_battlecards()
    for p in paths:
        print(f"  ✓ {p.name}")
    print(f"\n{len(paths)} battlecards generated.")


def cmd_search(query: str):
    """Search Oracle Health RAG for intelligence."""
    from oracle_health.director import search_all_intel
    results = search_all_intel(query, top_k=10)
    if not results:
        print("No results found.")
        return

    print(f"\n{len(results)} results for: {query}\n")
    for i, r in enumerate(results, 1):
        content = r.get("content", "")[:200]
        data_type = r.get("data_type", "unknown")
        source = r.get("source", "")
        similarity = r.get("similarity", 0)
        print(f"  [{i}] ({data_type}) sim={similarity:.3f}")
        print(f"      {content}...")
        if source:
            print(f"      Source: {source}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Oracle Health Department CLI")
    parser.add_argument("--command", required=True,
                        choices=["status", "freshness", "battlecard", "battlecard-all", "search"])
    parser.add_argument("--competitor", default="epic", help="Competitor name for battlecard command")
    parser.add_argument("--query", default="", help="Search query")
    args = parser.parse_args()

    if args.command == "status":
        cmd_status()
    elif args.command == "freshness":
        cmd_freshness()
    elif args.command == "battlecard":
        cmd_battlecard(args.competitor)
    elif args.command == "battlecard-all":
        cmd_battlecard_all()
    elif args.command == "search":
        if not args.query:
            print("--query required for search command")
            return
        cmd_search(args.query)


if __name__ == "__main__":
    main()
