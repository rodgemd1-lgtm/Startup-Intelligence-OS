#!/usr/bin/env python3
"""Jake Self-Improvement Weekly Runner.

Runs TIMG pipeline + routing feedback from the Layer 6 self_improvement module.
Writes improvement summary back to jake_episodic as data_type='self_improvement_run'.

Usage:
  python scripts/jake_self_improve_weekly.py
  python scripts/jake_self_improve_weekly.py --dry-run
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


def _run_module(module: str, command: str, label: str) -> tuple[bool, str]:
    """Run a backend module command, return (success, output)."""
    print(f"  Running {label}...")
    try:
        result = subprocess.run(
            [VENV_PYTHON, "-m", module, "--command", command],
            cwd=str(BACKEND_DIR),
            capture_output=True,
            text=True,
            timeout=300,
        )
        output = (result.stdout + result.stderr).strip()
        success = result.returncode == 0
        if success:
            print(f"    ✓ {label} complete ({len(output)} chars output)")
        else:
            print(f"    ✗ {label} failed (rc={result.returncode})")
            print(f"      {output[:300]}")
        return success, output
    except subprocess.TimeoutExpired:
        msg = f"{label} timed out after 300s"
        print(f"    ✗ {msg}")
        return False, msg
    except Exception as exc:
        msg = f"{label} error: {exc}"
        print(f"    ✗ {msg}")
        return False, msg


def _write_status_to_supabase(summary: str, success: bool, dry_run: bool) -> None:
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
            "source": "jake_self_improve_weekly",
            "data_type": "self_improvement_run",
            "importance": 0.6,
            "metadata": {
                "run_at": now,
                "success": success,
                "script": "jake_self_improve_weekly.py",
            },
        }
        result = client.table("jake_episodic").insert(row).execute()
        if result.data:
            print(f"\n  ✓ Status written to jake_episodic (id: {result.data[0].get('id', '?')})")
        else:
            print(f"\n  ✗ Failed to write to jake_episodic: {result}")
    except Exception as exc:
        print(f"\n  ✗ Supabase write failed: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Jake Self-Improvement Weekly Runner")
    parser.add_argument("--dry-run", action="store_true", help="Run without writing to Supabase")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    print(f"Jake Self-Improvement Weekly — {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    results: list[tuple[str, bool, str]] = []

    # Step 1: TIMG pipeline
    ok, out = _run_module("self_improvement", "timg", "TIMG Pipeline")
    results.append(("timg", ok, out))

    # Step 2: Routing feedback
    ok2, out2 = _run_module("self_improvement", "routing", "Routing Feedback")
    results.append(("routing", ok2, out2))

    # Step 3: Telemetry
    ok3, out3 = _run_module("self_improvement", "telemetry", "Performance Telemetry")
    results.append(("telemetry", ok3, out3))

    # Build summary
    all_ok = all(r[1] for r in results)
    status_str = "SUCCESS" if all_ok else "PARTIAL"
    lines = [
        f"Self-Improvement Weekly Run — {now.strftime('%Y-%m-%d %H:%M UTC')}",
        f"Status: {status_str}",
        "",
    ]
    for name, ok, out in results:
        icon = "✓" if ok else "✗"
        # Extract first meaningful line of output
        first_line = next((l for l in out.splitlines() if l.strip()), "no output")
        lines.append(f"{icon} {name}: {first_line[:120]}")

    summary = "\n".join(lines)

    print("\n" + "=" * 60)
    print(summary)

    _write_status_to_supabase(summary, all_ok, args.dry_run)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
