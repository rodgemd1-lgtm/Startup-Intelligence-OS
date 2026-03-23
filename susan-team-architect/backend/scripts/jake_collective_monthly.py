#!/usr/bin/env python3
"""Jake Collective Intelligence Monthly Runner.

Runs evolution proposals + cross-domain pattern transfer from the Layer 7 collective module.
Reads patterns from all companies, proposes new agent capabilities.
Writes summary to jake_episodic as data_type='collective_run'.

Usage:
  python scripts/jake_collective_monthly.py
  python scripts/jake_collective_monthly.py --dry-run
  python scripts/jake_collective_monthly.py --command evolve   # just evolution proposals
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Load .hermes/.env
_env_file = Path.home() / ".hermes" / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

# Use the same interpreter that's running this script — works in worktrees and main repo
VENV_PYTHON = sys.executable


def _run_module_cmd(module: str, command: str, label: str) -> tuple[bool, str]:
    """Run a backend module command, return (success, output)."""
    print(f"  Running {label}...")
    try:
        result = subprocess.run(
            [VENV_PYTHON, "-m", module, "--command", command],
            cwd=str(BACKEND_DIR),
            capture_output=True,
            text=True,
            timeout=600,  # collective runs can take longer
        )
        output = (result.stdout + result.stderr).strip()
        success = result.returncode == 0
        if success:
            print(f"    ✓ {label} complete")
        else:
            print(f"    ✗ {label} failed (rc={result.returncode})")
            print(f"      {output[:400]}")
        return success, output
    except subprocess.TimeoutExpired:
        msg = f"{label} timed out after 600s"
        print(f"    ✗ {msg}")
        return False, msg
    except Exception as exc:
        msg = f"{label} error: {exc}"
        print(f"    ✗ {msg}")
        return False, msg


def _write_status_to_supabase(summary: str, success: bool, proposals_count: int, dry_run: bool) -> None:
    """Write run status to jake_episodic."""
    if dry_run:
        print("\n[DRY RUN] Would write to jake_episodic:")
        print(f"  {summary[:200]}")
        return
    try:
        from supabase import create_client
        from susan_core.config import config as susan_config

        client = create_client(susan_config.supabase_url, susan_config.supabase_key)
        now = datetime.now(timezone.utc).isoformat()
        row = {
            "content": summary,
            "source": "jake_collective_monthly",
            "data_type": "collective_run",
            "importance": 0.7,  # higher importance — evolution proposals are strategic
            "metadata": {
                "run_at": now,
                "success": success,
                "proposals_count": proposals_count,
                "script": "jake_collective_monthly.py",
            },
        }
        result = client.table("jake_episodic").insert(row).execute()
        if result.data:
            print(f"\n  ✓ Status written to jake_episodic (id: {result.data[0].get('id', '?')})")
        else:
            print(f"\n  ✗ Failed to write to jake_episodic")
    except Exception as exc:
        print(f"\n  ✗ Supabase write failed: {exc}")


def _count_proposals_from_output(output: str) -> int:
    """Extract proposal count from evolve command output."""
    for line in output.splitlines():
        if "Generated" in line and "proposals" in line:
            parts = line.split()
            for i, p in enumerate(parts):
                if p.isdigit():
                    return int(p)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Jake Collective Intelligence Monthly Runner")
    parser.add_argument("--dry-run", action="store_true", help="Run without writing to Supabase")
    parser.add_argument(
        "--command",
        choices=["full", "evolve", "transfer", "predict"],
        default="full",
        help="Which collective analysis to run (default: full)",
    )
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    print(f"Jake Collective Intelligence Monthly — {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    results: list[tuple[str, bool, str]] = []
    proposals_count = 0

    if args.command == "full":
        commands_to_run = [
            ("evolve", "Evolution Proposals"),
            ("transfer", "Knowledge Transfer"),
            ("predict", "Capability Predictions"),
        ]
    else:
        label_map = {
            "evolve": "Evolution Proposals",
            "transfer": "Knowledge Transfer",
            "predict": "Capability Predictions",
        }
        commands_to_run = [(args.command, label_map[args.command])]

    for cmd, label in commands_to_run:
        ok, out = _run_module_cmd("collective", cmd, label)
        results.append((cmd, ok, out))
        if cmd == "evolve" and ok:
            proposals_count = _count_proposals_from_output(out)

    # Build summary
    all_ok = all(r[1] for r in results)
    status_str = "SUCCESS" if all_ok else "PARTIAL"
    lines = [
        f"Collective Intelligence Monthly Run — {now.strftime('%Y-%m-%d %H:%M UTC')}",
        f"Status: {status_str}",
        f"Mode: {args.command}",
        "",
    ]
    for name, ok, out in results:
        icon = "✓" if ok else "✗"
        first_line = next((l for l in out.splitlines() if l.strip()), "no output")
        lines.append(f"{icon} {name}: {first_line[:120]}")

    if proposals_count > 0:
        lines.append(f"\n→ {proposals_count} evolution proposals generated. Review in data/memory/evolutions/")

    summary = "\n".join(lines)

    print("\n" + "=" * 60)
    print(summary)

    _write_status_to_supabase(summary, all_ok, proposals_count, args.dry_run)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
