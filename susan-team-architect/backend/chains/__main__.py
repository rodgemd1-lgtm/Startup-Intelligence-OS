"""CLI entry point for the Chains engine.

Usage:
    python -m chains --command list
    python -m chains --command run --chain competitive-response
    python -m chains --command status
    python -m chains --command history --chain competitive-response
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


def _build_registry():
    from chains.registry import ChainRegistry
    from chains.chains.competitive_response import competitive_response
    from chains.chains.daily_cycle import daily_cycle

    reg = ChainRegistry()
    reg.register(competitive_response)
    reg.register(daily_cycle)
    return reg


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="chains",
        description="V4 Chain Engine — Sequential multi-agent workflows",
    )
    parser.add_argument(
        "--command",
        choices=["list", "run", "status", "history", "halt"],
        required=True,
        help="Command to execute.",
    )
    parser.add_argument(
        "--chain",
        type=str,
        default="",
        help="Chain name (required for run/history/halt).",
    )

    args = parser.parse_args()
    repo_root = _find_repo_root()
    runs_dir = repo_root / ".startup-os" / "runs" / "chains"

    if args.command == "list":
        reg = _build_registry()
        print("Registered Chains")
        print("=" * 60)
        for name in sorted(reg.list_names()):
            chain = reg.get(name)
            print(f"  {name:<30s} [{chain.autonomy}] {chain.description}")

    elif args.command == "run":
        if not args.chain:
            print("Error: --chain required for run command", file=sys.stderr)
            sys.exit(1)

        reg = _build_registry()

        # Placeholder executor — V4b will wire real agent dispatch
        def placeholder_executor(agent_name: str, input_data=None) -> dict:
            print(f"  [PLACEHOLDER] Would invoke agent: {agent_name}")
            return {"placeholder": True, "agent": agent_name}

        from chains.engine import ChainEngine

        engine = ChainEngine(registry=reg, agent_executor=placeholder_executor, runs_dir=runs_dir)
        print(f"Running chain: {args.chain}")
        run = engine.run(args.chain)
        print(f"  Status: {run.status}")
        print(f"  Steps: {run.steps_completed}/{run.steps_total}")
        print(f"  Run ID: {run.id}")
        print(f"  Audit log: {runs_dir}/")

    elif args.command == "status":
        runs_dir.mkdir(parents=True, exist_ok=True)
        log_files = sorted(runs_dir.glob("chains-*.jsonl"), reverse=True)
        if not log_files:
            print("No chain runs recorded yet.")
            return

        print("Recent Chain Runs")
        print("=" * 60)
        for log_file in log_files[:3]:
            print(f"\n  {log_file.name}")
            for line in log_file.read_text().strip().split("\n")[-5:]:
                record = json.loads(line)
                print(f"    {record['id']} | {record['chain_name']} | {record['status']}")

    elif args.command == "history":
        if not args.chain:
            print("Error: --chain required for history command", file=sys.stderr)
            sys.exit(1)

        runs_dir.mkdir(parents=True, exist_ok=True)
        log_files = sorted(runs_dir.glob("chains-*.jsonl"), reverse=True)
        found = []
        for log_file in log_files:
            for line in log_file.read_text().strip().split("\n"):
                if not line:
                    continue
                record = json.loads(line)
                if record["chain_name"] == args.chain:
                    found.append(record)

        if not found:
            print(f"No runs found for chain: {args.chain}")
            return

        print(f"History for chain: {args.chain}")
        print("=" * 60)
        for record in found[-10:]:
            print(f"  {record['id']} | {record['status']} | steps: {record['steps_completed']}/{record['steps_total']}")

    elif args.command == "halt":
        print("Halt not yet implemented (requires V4b trust enforcer).")


if __name__ == "__main__":
    main()
