#!/usr/bin/env python3
"""Jake AI Employee Runner — dispatch any employee by name.

Usage:
    .venv/bin/python scripts/jake_employee_runner.py --employee meeting_prep
    .venv/bin/python scripts/jake_employee_runner.py --employee research_agent
    .venv/bin/python scripts/jake_employee_runner.py --employee oracle_sentinel
    .venv/bin/python scripts/jake_employee_runner.py --employee inbox_zero
    .venv/bin/python scripts/jake_employee_runner.py --list
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))


def load_env():
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        with open(env_path) as fh:
            for line in fh:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())


def update_cron_status(job_name: str, status: str, error: str = "", duration_ms: int = 0) -> None:
    """Update jake_cron_status table."""
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        if not url or not key:
            return
        client = create_client(url, key)
        client.table("jake_cron_status").upsert({
            "job_name": job_name,
            "last_run": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "error_message": error[:500] if error else "",
            "duration_ms": duration_ms,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }, on_conflict="job_name").execute()
    except Exception:
        pass


def run_employee(name: str) -> dict:
    """Import and run an employee module by name."""
    from jake_brain.employees import EMPLOYEE_REGISTRY
    spec = EMPLOYEE_REGISTRY.get(name)
    if not spec:
        return {"status": "error", "error": f"Unknown employee: '{name}'. Available: {list(EMPLOYEE_REGISTRY.keys())}"}

    start_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    update_cron_status(f"employee:{name}", "running")

    try:
        module = importlib.import_module(spec.module)
        if not hasattr(module, "run"):
            return {"status": "error", "error": f"Module {spec.module} has no run() function"}
        result = module.run()
        duration = int(datetime.now(timezone.utc).timestamp() * 1000) - start_ms
        update_cron_status(f"employee:{name}", "success", duration_ms=duration)
        return result
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        duration = int(datetime.now(timezone.utc).timestamp() * 1000) - start_ms
        update_cron_status(f"employee:{name}", "failed", error=str(e)[:500], duration_ms=duration)
        return {"status": "error", "error": str(e), "traceback": error_msg[:500]}


def main():
    load_env()
    parser = argparse.ArgumentParser(description="Jake AI Employee Runner")
    parser.add_argument("--employee", type=str, help="Employee name to run")
    parser.add_argument("--list", action="store_true", help="List all employees")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    if args.list:
        from jake_brain.employees import EMPLOYEE_REGISTRY
        print("Available AI Employees:")
        for name, spec in EMPLOYEE_REGISTRY.items():
            status = "✓ enabled" if spec.enabled else "○ disabled"
            print(f"  {status}  {name}")
            print(f"           {spec.description}")
            print(f"           Cron: {spec.cron}")
        return

    if not args.employee:
        print("Error: specify --employee <name> or --list")
        sys.exit(1)

    print(f"╔══════════════════════════════════╗")
    print(f"║  AI Employee: {args.employee:<19}║")
    print(f"╚══════════════════════════════════╝")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    result = run_employee(args.employee)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        status = result.get("status", "unknown")
        icon = "✓" if status == "complete" else "✗" if status == "error" else "○"
        print(f"{icon} Status: {status}")
        if result.get("error"):
            print(f"  Error: {result['error']}")
        for k, v in result.items():
            if k not in ("status", "error", "traceback", "results"):
                print(f"  {k}: {v}")
        if result.get("results"):
            print(f"  Results ({len(result['results'])}):")
            for r in result["results"][:5]:
                print(f"    - {r}")

    sys.exit(0 if result.get("status") != "error" else 1)


if __name__ == "__main__":
    main()
