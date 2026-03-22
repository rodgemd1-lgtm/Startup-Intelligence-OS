#!/usr/bin/env python3
"""Jake Autonomous Worker — daemon entry point.

This is what launchd runs. It also doubles as a CLI for manual control.

Usage:
    # Daemon mode (launchd or manual)
    python scripts/jake_autonomous_worker.py daemon

    # Run one task and exit
    python scripts/jake_autonomous_worker.py run-once

    # Create a goal (Jake decomposes it into tasks automatically)
    python scripts/jake_autonomous_worker.py goal "Build out recipes for my job" --priority P1

    # Show current status
    python scripts/jake_autonomous_worker.py status

    # List pending tasks
    python scripts/jake_autonomous_worker.py tasks --status pending

    # Manually complete a task
    python scripts/jake_autonomous_worker.py complete <task_id>

    # Skip a blocked task
    python scripts/jake_autonomous_worker.py skip <task_id>

    # Add a single task (not tied to a goal)
    python scripts/jake_autonomous_worker.py add-task "Write oracle battlecard update" --assigned claude_code
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Load ~/.hermes/.env for Supabase keys etc.
env_file = Path.home() / ".hermes" / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


# ─── helpers ────────────────────────────────────────────────────────────────

def _worker():
    from jake_brain.autonomous_worker import AutonomousWorker
    return AutonomousWorker()


def _tasks():
    from jake_brain.goals.tasks import TaskStore
    return TaskStore()


# ─── commands ────────────────────────────────────────────────────────────────

def cmd_daemon(args: argparse.Namespace) -> None:
    """Run the worker loop indefinitely."""
    print(f"[jake-worker] Starting daemon. interval={args.interval}s executor={args.executor or 'all'}")
    worker = _worker()
    worker.run_loop(
        interval_seconds=args.interval,
        executor_filter=args.executor or None,
    )


def cmd_run_once(args: argparse.Namespace) -> None:
    """Claim and execute one task."""
    worker = _worker()
    task = worker.run_once(executor_filter=args.executor or None)
    if task is None:
        print("[jake-worker] No pending tasks.")
    else:
        print(f"[jake-worker] Processed task: {task.get('task_text','')[:60]}")
        print(f"  Status:  {task.get('status')}")
        print(f"  Output:  {(task.get('output') or '')[:200]}")


def cmd_goal(args: argparse.Namespace) -> None:
    """Create a goal and auto-decompose into tasks."""
    worker = _worker()
    result = worker.create_goal_with_tasks(
        goal_text=args.goal_text,
        priority=args.priority or "P2",
        deadline=args.deadline,
        project=args.project,
    )
    goal = result.get("goal", {})
    tasks = result.get("tasks", [])
    print(f"\nGoal created:")
    print(f"  ID:       {goal.get('id')}")
    print(f"  Title:    {goal.get('title')}")
    print(f"  Priority: {goal.get('priority')}")
    print(f"\nDecomposed into {len(tasks)} tasks:")
    for i, t in enumerate(tasks, 1):
        print(f"  {i}. [{t.get('priority','?')}][{t.get('assigned_to','?')}] {t.get('task_text','')[:70]}")
    print(f"\nThe autonomous worker will pick these up on next cycle.")


def cmd_status(args: argparse.Namespace) -> None:
    """Print current worker status."""
    worker = _worker()
    print(worker.status_report())


def cmd_tasks(args: argparse.Namespace) -> None:
    """List tasks with optional filters."""
    store = _tasks()
    items = store.list_tasks(
        status=args.status,
        assigned_to=args.executor,
        limit=args.limit,
    )
    if not items:
        print("No tasks found.")
        return
    print(f"\n{'ID':<10} {'PRI':<4} {'STATUS':<12} {'ASSIGNED':<12} TEXT")
    print("-" * 80)
    for t in items:
        print(
            f"{t['id'][:8]:<10} {t.get('priority','?'):<4} "
            f"{t.get('status','?'):<12} {t.get('assigned_to','?'):<12} "
            f"{t.get('task_text','')[:40]}"
        )
    print(f"\n{len(items)} task(s) shown.")


def cmd_complete(args: argparse.Namespace) -> None:
    """Manually mark a task complete."""
    store = _tasks()
    result = store.complete_task(args.task_id, output="Manually completed via CLI")
    if result:
        print(f"Task {args.task_id[:8]} marked complete.")
    else:
        print(f"Task {args.task_id} not found.")


def cmd_skip(args: argparse.Namespace) -> None:
    """Skip a blocked/failing task."""
    store = _tasks()
    result = store.skip_task(args.task_id, reason=args.reason or "Manually skipped")
    if result:
        print(f"Task {args.task_id[:8]} skipped.")
    else:
        print(f"Task {args.task_id} not found.")


def cmd_add_task(args: argparse.Namespace) -> None:
    """Add a single task without a goal."""
    store = _tasks()
    task = store.create_task(
        task_text=args.task_text,
        assigned_to=args.assigned or "auto",
        executor_hint=args.hint,
        priority=args.priority or "P2",
    )
    print(f"\nTask created:")
    print(f"  ID:       {task.get('id')}")
    print(f"  Text:     {task.get('task_text')}")
    print(f"  Executor: {task.get('assigned_to')}")
    print(f"  Priority: {task.get('priority')}")
    print(f"\nWorker will pick this up within one cycle.")


def cmd_dashboard(args: argparse.Namespace) -> None:
    """Full task dashboard as JSON."""
    store = _tasks()
    dash = store.dashboard(goal_id=args.goal or None)
    print(json.dumps(dash, indent=2, default=str))


# ─── parser ──────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="jake_autonomous_worker",
        description="Jake's autonomous task execution system",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # daemon
    d = sub.add_parser("daemon", help="Run the worker loop forever")
    d.add_argument("--interval", type=int, default=60, help="Poll interval in seconds")
    d.add_argument("--executor", help="Only process tasks for this executor type")

    # run-once
    r = sub.add_parser("run-once", help="Process one pending task and exit")
    r.add_argument("--executor", help="Filter by executor type")

    # goal
    g = sub.add_parser("goal", help="Create a goal and auto-decompose into tasks")
    g.add_argument("goal_text", help="Goal description")
    g.add_argument("--priority", default="P2", choices=["P0","P1","P2","P3"])
    g.add_argument("--deadline", help="ISO date e.g. 2026-04-15")
    g.add_argument("--project", help="Project tag")

    # status
    sub.add_parser("status", help="Print current status report")

    # tasks
    t = sub.add_parser("tasks", help="List tasks")
    t.add_argument("--status", help="Filter by status")
    t.add_argument("--executor", help="Filter by executor")
    t.add_argument("--limit", type=int, default=20)

    # complete
    c = sub.add_parser("complete", help="Manually complete a task")
    c.add_argument("task_id")

    # skip
    sk = sub.add_parser("skip", help="Skip a task")
    sk.add_argument("task_id")
    sk.add_argument("--reason", default="")

    # add-task
    at = sub.add_parser("add-task", help="Add a standalone task")
    at.add_argument("task_text")
    at.add_argument("--assigned", help="Executor type")
    at.add_argument("--hint", help="executor_hint (e.g. script path)")
    at.add_argument("--priority", default="P2", choices=["P0","P1","P2","P3"])

    # dashboard
    db = sub.add_parser("dashboard", help="Full task dashboard as JSON")
    db.add_argument("--goal", help="Filter by goal ID")

    return p


COMMANDS = {
    "daemon":    cmd_daemon,
    "run-once":  cmd_run_once,
    "goal":      cmd_goal,
    "status":    cmd_status,
    "tasks":     cmd_tasks,
    "complete":  cmd_complete,
    "skip":      cmd_skip,
    "add-task":  cmd_add_task,
    "dashboard": cmd_dashboard,
}

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    handler = COMMANDS.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
