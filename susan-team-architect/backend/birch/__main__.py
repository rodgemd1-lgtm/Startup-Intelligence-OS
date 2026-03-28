"""CLI entry point for the Birch signal scorer.

Usage:
    python -m birch --command score --file signals.json
    python -m birch --command stats
    python -m birch --command stats --days 7
    python -m birch --command listen          (V4b — Firehose SSE)
"""
from __future__ import annotations

import argparse
import json
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
        prog="birch",
        description="V4 Birch Signal Scorer — Real-time signal scoring and routing",
    )
    parser.add_argument(
        "--command",
        choices=["score", "stats", "listen"],
        required=True,
        help="Command to execute.",
    )
    parser.add_argument("--file", type=str, default="", help="Input file for batch scoring.")
    parser.add_argument("--days", type=int, default=1, help="Days of history for stats.")

    args = parser.parse_args()
    repo_root = _find_repo_root()
    signals_dir = repo_root / ".startup-os" / "signals"

    if args.command == "score":
        if not args.file:
            print("Error: --file required for score command", file=sys.stderr)
            sys.exit(1)

        from birch.scorer import BirchScorer
        from birch.schemas import RawSignal
        from birch.rubric import Rubric, CompanyRubric
        from birch.writer import SignalWriter

        # Load default rubric — TODO: load from config file in V4b
        rubric = Rubric(companies={
            "oracle-health": CompanyRubric(
                keywords=["epic", "ehr", "himss", "clinical ai", "oracle health", "cerner",
                           "health it", "ehrs", "interoperability", "fhir"],
                competitors=["epic", "meditech", "athenahealth", "cerner", "microsoft nuance"],
            ),
            "transformfit": CompanyRubric(
                keywords=["fitness app", "ai coaching", "workout", "personal trainer",
                           "health tech", "wearable"],
                competitors=["peloton", "fitbod", "future", "caliber", "trainiac"],
            ),
            "alex-recruiting": CompanyRubric(
                keywords=["college recruiting", "athletic recruiting", "ncaa", "nil"],
                competitors=["fieldlevel", "ncsa", "berecruited"],
            ),
        })

        scorer = BirchScorer(rubric=rubric)
        writer = SignalWriter(signals_dir=signals_dir)

        input_path = Path(args.file)
        signals = json.loads(input_path.read_text())
        if isinstance(signals, dict):
            signals = [signals]

        print(f"Scoring {len(signals)} signals...")
        for raw_data in signals:
            raw = RawSignal(**raw_data)
            scored = scorer.score(raw)
            writer.append(scored)
            print(f"  [{scored.tier}] {scored.score:3d} — {scored.title[:60]}")

        print(f"\nResults written to: {signals_dir}/")

    elif args.command == "stats":
        from birch.writer import SignalWriter

        writer = SignalWriter(signals_dir=signals_dir)
        stats = writer.stats(days=args.days)
        print("Birch Signal Stats")
        print("=" * 40)
        print(f"  Total signals:  {stats['total']}")
        print(f"  Tier 1 (80+):   {stats['tier_1']}")
        print(f"  Tier 2 (50-79): {stats['tier_2']}")
        print(f"  Tier 3 (<50):   {stats['tier_3']}")

    elif args.command == "listen":
        import asyncio
        from birch.sources.firehose import FirehoseConfig, listen as firehose_listen
        from birch.scorer import BirchScorer
        from birch.rubric import Rubric, CompanyRubric
        from birch.writer import SignalWriter

        rubric = Rubric(companies={
            "oracle-health": CompanyRubric(
                keywords=["epic", "ehr", "himss", "clinical ai", "oracle health", "cerner",
                           "health it", "ehrs", "interoperability", "fhir"],
                competitors=["epic", "meditech", "athenahealth", "cerner", "microsoft nuance"],
            ),
            "transformfit": CompanyRubric(
                keywords=["fitness app", "ai coaching", "workout", "personal trainer",
                           "health tech", "wearable"],
                competitors=["peloton", "fitbod", "future", "caliber", "trainiac"],
            ),
            "alex-recruiting": CompanyRubric(
                keywords=["college recruiting", "athletic recruiting", "ncaa", "nil"],
                competitors=["fieldlevel", "ncsa", "berecruited"],
            ),
        })

        scorer = BirchScorer(rubric=rubric)
        writer = SignalWriter(signals_dir=signals_dir)

        try:
            config = FirehoseConfig.from_env()
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            print("Set FIREHOSE_API_KEY in ~/.hermes/.env", file=sys.stderr)
            sys.exit(1)

        async def _on_signal(raw):
            scored = scorer.score(raw)
            writer.append(scored)
            tier_label = {1: "TIER-1 ***", 2: "TIER-2", 3: "tier-3"}
            print(f"  [{tier_label.get(scored.tier, '?')}] {scored.score:3d} — {scored.title[:80]}")

        print("Starting Firehose SSE listener...")
        print(f"Signals → {signals_dir}/")
        print("Press Ctrl+C to stop.\n")

        try:
            asyncio.run(firehose_listen(config, _on_signal))
        except KeyboardInterrupt:
            print("\nFirehose listener stopped.")


if __name__ == "__main__":
    main()
