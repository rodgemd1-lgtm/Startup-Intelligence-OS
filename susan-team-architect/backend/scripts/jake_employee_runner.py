#!/usr/bin/env python3
"""CLI to run any Jake AI Employee.

Usage:
    python scripts/jake_employee_runner.py --employee oracle_sentinel
    python scripts/jake_employee_runner.py --employee research_agent
    python scripts/jake_employee_runner.py --employee content_creator
    python scripts/jake_employee_runner.py --employee family_coordinator
    python scripts/jake_employee_runner.py --list
    python scripts/jake_employee_runner.py --employee oracle_sentinel --dry-run
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Ensure backend is on the path when running as a script
_BACKEND_DIR = Path(__file__).parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("jake_employee_runner")


def _load_registry():
    """Import the employee registry (deferred to avoid import errors at top level)."""
    from jake_brain.employees import EMPLOYEE_REGISTRY, EMPLOYEE_SCHEDULES
    return EMPLOYEE_REGISTRY, EMPLOYEE_SCHEDULES


def _load_store():
    """Load BrainStore, returning None on failure."""
    try:
        from jake_brain.store import BrainStore
        return BrainStore()
    except Exception as exc:
        logger.warning("BrainStore unavailable (no Supabase?): %s", exc)
        return None


def _json_default(obj):
    """JSON serializer for non-serializable types."""
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    return str(obj)


def cmd_list(registry: dict, schedules: dict) -> None:
    """Print all employees and their cron schedules."""
    print("\nJake AI Employees\n" + "=" * 40)
    for name, cls in sorted(registry.items()):
        schedule = schedules.get(name, "no schedule")
        doc = (cls.__doc__ or "").strip().split("\n")[0]
        print(f"\n  {name}")
        print(f"    Schedule : {schedule}")
        print(f"    Class    : {cls.__name__}")
        if doc:
            print(f"    Desc     : {doc}")
    print()


def cmd_run(employee_name: str, registry: dict, dry_run: bool = False) -> None:
    """Run a specific employee and print results."""
    if employee_name not in registry:
        print(f"ERROR: Unknown employee '{employee_name}'")
        print(f"Available: {', '.join(sorted(registry.keys()))}")
        sys.exit(1)

    cls = registry[employee_name]

    if dry_run:
        print(f"\n[DRY RUN] Would run: {cls.__name__}")
        print(f"  Employee : {employee_name}")
        print(f"  Class    : {cls.__qualname__}")
        print(f"  Task type: {getattr(cls, 'TASK_TYPE', 'unknown')}")
        print(f"  Hints    : {getattr(cls, 'CONTEXT_HINTS', [])}")
        print(f"  Criteria : {getattr(cls, 'SUCCESS_CRITERIA', [])}")
        print("\n[DRY RUN] No actions taken.")
        return

    logger.info("Starting employee: %s", employee_name)
    store = _load_store()

    # Instantiate and run
    employee = cls(store=store)

    try:
        # Each employee has a different run() signature — handle per employee
        if employee_name == "oracle_sentinel":
            result = employee.run()
        elif employee_name == "research_agent":
            result = employee.run()
        elif employee_name == "content_creator":
            result = employee.run()
        elif employee_name == "family_coordinator":
            result = employee.run()
        else:
            # Generic fallback — try calling run() with no args
            result = employee.run()

        print("\n" + "=" * 50)
        print(f"Employee: {employee_name} — COMPLETE")
        print("=" * 50)
        print(json.dumps(result, indent=2, default=_json_default))

    except Exception as exc:
        logger.exception("Employee %s failed: %s", employee_name, exc)
        print(f"\nERROR: {employee_name} failed — {exc}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Jake AI Employee Runner — run autonomous employees manually.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--employee",
        "-e",
        metavar="NAME",
        help="Employee name to run (e.g. oracle_sentinel, research_agent)",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List all available employees and their schedules",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be done without actually running",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable DEBUG logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load registry
    try:
        registry, schedules = _load_registry()
    except Exception as exc:
        print(f"ERROR: Failed to load employee registry: {exc}")
        sys.exit(1)

    if args.list:
        cmd_list(registry, schedules)
        return

    if args.employee:
        cmd_run(args.employee, registry, dry_run=args.dry_run)
        return

    # No args — show help
    parser.print_help()
    print("\nQuick start:")
    print("  python scripts/jake_employee_runner.py --list")
    print("  python scripts/jake_employee_runner.py --employee oracle_sentinel --dry-run")


if __name__ == "__main__":
    main()
