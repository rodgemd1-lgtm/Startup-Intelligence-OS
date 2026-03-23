#!/usr/bin/env python3
"""CLI runner for Jake's autonomous AI employee loops.

Usage:
    python scripts/jake_employee_runner.py --employee oracle_sentinel
    python scripts/jake_employee_runner.py --employee inbox_zero
    python scripts/jake_employee_runner.py --employee inbox_zero --slot midday
    python scripts/jake_employee_runner.py --list
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("jake.employee_runner")


def update_cron_status(
    job_name: str,
    status: str,
    actions: int = 0,
    error: str | None = None,
    duration_ms: int | None = None,
) -> None:
    """Update cron status in Supabase for monitoring dashboard."""
    try:
        from supabase import create_client
        from susan_core.config import config
        client = create_client(config.supabase_url, config.supabase_key)
        update_data = {
            "status": status,
            "last_run_at": datetime.now(timezone.utc).isoformat(),
            "actions_taken": actions,
            "error_message": error,
        }
        if duration_ms is not None:
            update_data["duration_ms"] = duration_ms
        client.table("jake_cron_status").update(update_data).eq("job_name", job_name).execute()
    except Exception as e:
        logger.warning(f"Failed to update cron status for {job_name}: {e}")


def run_employee(name: str, slot: str = "morning") -> dict:
    """Load and run an employee by name."""
    from jake_brain.employees import get_employee, list_employees

    employee = get_employee(name)
    if employee is None:
        available = [e["name"] for e in list_employees()]
        raise ValueError(f"Unknown employee '{name}'. Available: {available}")

    logger.info(f"Running employee: {name} (slot: {slot})")

    # Dispatch with slot if the employee supports it (Inbox Zero)
    if hasattr(employee, "run") and name == "inbox_zero":
        return employee.run(cron_slot=slot)
    return employee.run()


def print_result(name: str, result: dict) -> None:
    """Print run result in a readable format."""
    success = result.get("success", False)
    status = result.get("status", "unknown")
    symbol = "✓" if success else "✗"

    print(f"\n{symbol} Employee '{name}' [{status.upper()}]")
    print(f"  Run ID   : {result.get('run_id', '?')}")
    print(f"  Pipeline : {result.get('pipeline_name', '?')}")
    if result.get("reason"):
        print(f"  Reason   : {result['reason']}")
    phases = result.get("phases_completed", {})
    if phases:
        print(f"  Phases   : {', '.join(phases.keys())}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Jake autonomous employee runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--employee", help="Employee name to run")
    parser.add_argument(
        "--slot",
        choices=["morning", "midday", "evening"],
        default="morning",
        help="Time slot (for inbox_zero, default: morning)",
    )
    parser.add_argument("--list", action="store_true", help="List all available employees")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    # List mode
    if args.list:
        from jake_brain.employees import list_employees
        employees = list_employees()
        print(f"\n{len(employees)} registered employees:\n")
        for emp in employees:
            print(f"  {emp['name']}")
            print(f"    {emp['description']}")
            print(f"    Schedules: {', '.join(emp.get('cron_schedules', []))}")
            print()
        return

    if not args.employee:
        parser.error("--employee is required (or use --list)")

    # Determine cron job name for status tracking
    name = args.employee
    slot = args.slot
    cron_job = f"{name}_{slot}" if name == "inbox_zero" else f"{name}_daily"

    update_cron_status(cron_job, "running")
    start = time.time()

    try:
        result = run_employee(name, slot=slot)
        elapsed = round((time.time() - start) * 1000)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_result(name, result)

        phases_done = len(result.get("phases_completed", {}))
        update_cron_status(
            cron_job,
            "success" if result.get("success") else "failed",
            actions=phases_done,
            error=result.get("reason") if not result.get("success") else None,
            duration_ms=elapsed,
        )

        sys.exit(0 if result.get("success") else 1)

    except Exception as e:
        elapsed = round((time.time() - start) * 1000)
        logger.error(f"Employee runner failed: {e}", exc_info=True)
        update_cron_status(cron_job, "failed", error=str(e), duration_ms=elapsed)
        sys.exit(2)


if __name__ == "__main__":
    main()
