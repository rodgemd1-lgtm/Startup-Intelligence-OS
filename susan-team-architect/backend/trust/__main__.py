"""CLI entry point for the Trust system.

Usage:
    python -m trust --command dashboard
    python -m trust --command report
    python -m trust --command promote --chain daily-cycle
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _find_repo_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / ".startup-os").is_dir():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return Path(__file__).resolve().parent.parent.parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="trust",
        description="V4 Trust System — Autonomy graduation and dashboard",
    )
    parser.add_argument(
        "--command",
        choices=["dashboard", "report", "promote", "demote"],
        required=True,
    )
    parser.add_argument("--chain", type=str, default="")

    args = parser.parse_args()
    repo_root = _find_repo_root()
    trust_dir = repo_root / ".startup-os" / "runs" / "trust"
    briefs_dir = repo_root / ".startup-os" / "briefs"

    from trust.tracker import TrustTracker
    from trust.dashboard import generate_cli_table, generate_markdown

    tracker = TrustTracker(data_dir=trust_dir)
    tracker.load()

    if args.command == "dashboard":
        print(generate_cli_table(tracker))

    elif args.command == "report":
        briefs_dir.mkdir(parents=True, exist_ok=True)
        from datetime import datetime, timezone
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        report_path = briefs_dir / f"trust-dashboard-{date_str}.md"
        md = generate_markdown(tracker)
        report_path.write_text(md, encoding="utf-8")
        print(f"Trust report saved to: {report_path}")

    elif args.command == "promote":
        if not args.chain:
            print("Error: --chain required", file=sys.stderr)
            sys.exit(1)
        from trust import config
        cap = config.blast_radius_cap(args.chain)
        profile = tracker.get_profile(args.chain)
        if profile.level == "MANUAL":
            if cap and cap == "SUPERVISED":
                profile.level = "SUPERVISED"
                print(f"Promoted {args.chain}: MANUAL -> SUPERVISED (blast radius cap: cannot go higher)")
            else:
                profile.level = "SUPERVISED"
                print(f"Promoted {args.chain}: MANUAL -> SUPERVISED")
        elif profile.level == "SUPERVISED":
            if cap:
                print(f"Cannot promote {args.chain} — blast radius cap at SUPERVISED")
            elif not config.is_autonomous_eligible(args.chain):
                print(f"Cannot promote {args.chain} — not in autonomous-eligible list")
            else:
                profile.level = "AUTONOMOUS"
                print(f"Promoted {args.chain}: SUPERVISED -> AUTONOMOUS")
        else:
            print(f"{args.chain} is already AUTONOMOUS")
        tracker.save()

    elif args.command == "demote":
        if not args.chain:
            print("Error: --chain required", file=sys.stderr)
            sys.exit(1)
        profile = tracker.get_profile(args.chain)
        if profile.level == "AUTONOMOUS":
            profile.level = "SUPERVISED"
            print(f"Demoted {args.chain}: AUTONOMOUS -> SUPERVISED")
        elif profile.level == "SUPERVISED":
            profile.level = "MANUAL"
            print(f"Demoted {args.chain}: SUPERVISED -> MANUAL")
        else:
            print(f"{args.chain} is already MANUAL")
        tracker.save()


if __name__ == "__main__":
    main()
