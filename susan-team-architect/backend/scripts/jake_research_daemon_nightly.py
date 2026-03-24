#!/usr/bin/env python3
"""Jake Research Daemon Nightly Runner.

Runs gap detection + changelog monitoring from the Layer 5 research_daemon module.
Flags domains with >20% stale records in Susan RAG.
Writes run status to jake_episodic as data_type='research_daemon_run'.

Usage:
  python scripts/jake_research_daemon_nightly.py
  python scripts/jake_research_daemon_nightly.py --dry-run
  python scripts/jake_research_daemon_nightly.py --stale-days 30
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
STALE_THRESHOLD_PCT = 0.20  # Flag if >20% of records in a domain are stale


def _run_module_cmd(module: str, command: str, label: str, extra_args: list[str] | None = None) -> tuple[bool, str]:
    """Run a backend module command, return (success, output)."""
    print(f"  Running {label}...")
    cmd = [VENV_PYTHON, "-m", module, "--command", command] + (extra_args or [])
    try:
        result = subprocess.run(
            cmd,
            cwd=str(BACKEND_DIR),
            capture_output=True,
            text=True,
            timeout=300,
        )
        output = (result.stdout + result.stderr).strip()
        success = result.returncode == 0
        if success:
            print(f"    ✓ {label} complete")
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


def _check_rag_freshness(stale_days: int) -> dict:
    """Check Susan RAG for stale records per domain. Returns domain -> stale pct."""
    flagged = {}
    try:
        from supabase import create_client
        from susan_core.config import config as susan_config

        client = create_client(susan_config.supabase_url, susan_config.supabase_key)

        # Get total count by data_type
        result = client.table("knowledge_chunks").select("data_type").execute()
        if not result.data:
            return {}

        domain_counts: dict[str, int] = {}
        for row in result.data:
            dt = row.get("data_type", "unknown")
            domain_counts[dt] = domain_counts.get(dt, 0) + 1

        # Get stale count (no updated_at within stale_days, or check created_at)
        from datetime import timedelta
        cutoff = (datetime.now(timezone.utc) - timedelta(days=stale_days)).isoformat()

        stale_result = client.table("knowledge_chunks").select("data_type").lt(
            "created_at", cutoff
        ).execute()

        stale_counts: dict[str, int] = {}
        for row in (stale_result.data or []):
            dt = row.get("data_type", "unknown")
            stale_counts[dt] = stale_counts.get(dt, 0) + 1

        for domain, total in domain_counts.items():
            stale = stale_counts.get(domain, 0)
            pct = stale / total if total > 0 else 0
            if pct > STALE_THRESHOLD_PCT:
                flagged[domain] = round(pct, 3)

    except Exception as exc:
        print(f"    ✗ RAG freshness check failed: {exc}")
    return flagged


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
            "source": "jake_research_daemon_nightly",
            "data_type": "research_daemon_run",
            "importance": 0.5,
            "metadata": {
                "run_at": now,
                "success": success,
                "script": "jake_research_daemon_nightly.py",
            },
        }
        result = client.table("jake_episodic").insert(row).execute()
        if result.data:
            print(f"\n  ✓ Status written to jake_episodic (id: {result.data[0].get('id', '?')})")
        else:
            print(f"\n  ✗ Failed to write to jake_episodic")
    except Exception as exc:
        print(f"\n  ✗ Supabase write failed: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Jake Research Daemon Nightly Runner")
    parser.add_argument("--dry-run", action="store_true", help="Run without writing to Supabase")
    parser.add_argument("--stale-days", type=int, default=30, help="Days before data is stale")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    print(f"Jake Research Daemon Nightly — {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    results: list[tuple[str, bool, str]] = []

    # Step 1: Detect knowledge gaps
    ok, out = _run_module_cmd(
        "research_daemon", "detect-gaps", "Gap Detection",
        ["--stale-days", str(args.stale_days)]
    )
    results.append(("detect-gaps", ok, out))

    # Step 2: Check for dependency updates
    ok2, out2 = _run_module_cmd("research_daemon", "check-updates", "Changelog Monitor")
    results.append(("check-updates", ok2, out2))

    # Step 3: RAG freshness check
    print("  Running RAG Freshness Check...")
    flagged_domains = _check_rag_freshness(args.stale_days)
    if flagged_domains:
        print(f"    ✗ {len(flagged_domains)} domains flagged as stale (>{STALE_THRESHOLD_PCT:.0%}):")
        for domain, pct in sorted(flagged_domains.items(), key=lambda x: -x[1])[:10]:
            print(f"      - {domain}: {pct:.1%} stale")
    else:
        print(f"    ✓ All domains within freshness threshold (<{STALE_THRESHOLD_PCT:.0%} stale)")
    results.append(("rag-freshness", True, f"Flagged domains: {list(flagged_domains.keys())[:5]}"))

    # Build summary
    all_ok = all(r[1] for r in results)
    status_str = "SUCCESS" if all_ok else "PARTIAL"
    lines = [
        f"Research Daemon Nightly Run — {now.strftime('%Y-%m-%d %H:%M UTC')}",
        f"Status: {status_str}",
        f"Stale threshold: {args.stale_days} days",
        "",
    ]
    for name, ok, out in results:
        icon = "✓" if ok else "✗"
        first_line = next((l for l in out.splitlines() if l.strip()), "no output")
        lines.append(f"{icon} {name}: {first_line[:120]}")

    if flagged_domains:
        lines.append(f"\n⚠ Stale domains ({len(flagged_domains)}): {', '.join(list(flagged_domains.keys())[:5])}")

    summary = "\n".join(lines)

    print("\n" + "=" * 60)
    print(summary)

    _write_status_to_supabase(summary, all_ok, args.dry_run)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
