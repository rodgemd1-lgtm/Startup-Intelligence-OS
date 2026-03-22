#!/usr/bin/env python3
"""CLI for Jake's Goal Tracking Layer — create, track, search, and dashboard goals.

Usage:
    python scripts/jake_goals_cli.py create "Ship v2.0" --project startup-os --priority P1 --target 100 --unit percent --deadline 2026-04-15
    python scripts/jake_goals_cli.py list                          # List active goals
    python scripts/jake_goals_cli.py list --status completed       # List completed goals
    python scripts/jake_goals_cli.py checkin <goal_id> "Finished auth module" --value 35
    python scripts/jake_goals_cli.py dashboard                     # Full dashboard
    python scripts/jake_goals_cli.py dashboard --project startup-os
    python scripts/jake_goals_cli.py search "recruiting pipeline"
    python scripts/jake_goals_cli.py milestone <parent_id> "Auth module complete"
    python scripts/jake_goals_cli.py complete <goal_id>
    python scripts/jake_goals_cli.py smoke                         # End-to-end smoke test
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jake_brain.goals.store import GoalStore


def cmd_create(store: GoalStore, args: argparse.Namespace) -> None:
    """Create a new goal."""
    goal = store.create_goal(
        title=args.title,
        description=args.description,
        goal_type=args.type or "goal",
        project=args.project,
        priority=args.priority or "P2",
        target_value=args.target,
        unit=args.unit,
        deadline=args.deadline,
        people=args.people.split(",") if args.people else None,
        tags=args.tags.split(",") if args.tags else None,
    )
    print(f"\nGoal created:")
    print(f"  ID:       {goal.get('id')}")
    print(f"  Title:    {goal.get('title')}")
    print(f"  Type:     {goal.get('goal_type')}")
    print(f"  Project:  {goal.get('project')}")
    print(f"  Priority: {goal.get('priority')}")
    if goal.get("target_value"):
        print(f"  Target:   {goal['target_value']} {goal.get('unit', '')}")
    if goal.get("deadline"):
        print(f"  Deadline: {goal['deadline']}")
    print()


def cmd_list(store: GoalStore, args: argparse.Namespace) -> None:
    """List goals."""
    goals = store.list_goals(
        status=args.status,
        project=args.project,
        goal_type=args.type,
        limit=args.limit or 50,
    )
    if not goals:
        print("\nNo goals found.\n")
        return

    print(f"\n=== Goals ({len(goals)}) ===\n")
    for g in goals:
        status_icon = {"active": "[ ]", "completed": "[x]", "paused": "[-]", "cancelled": "[~]"}.get(g["status"], "[?]")
        progress = ""
        if g.get("target_value"):
            pct = (float(g.get("current_value") or 0) / float(g["target_value"])) * 100
            progress = f" ({pct:.0f}%)"
        deadline = f" | due {g['deadline'][:10]}" if g.get("deadline") else ""
        print(f"  {status_icon} [{g['priority']}] {g['title']}{progress}{deadline}")
        print(f"       id={g['id']}  project={g.get('project', '-')}  type={g['goal_type']}")
    print()


def cmd_checkin(store: GoalStore, args: argparse.Namespace) -> None:
    """Add a check-in to a goal."""
    checkin = store.add_checkin(
        goal_id=args.goal_id,
        content=args.content,
        new_value=args.value,
        source=args.source or "manual",
    )
    print(f"\nCheck-in recorded:")
    print(f"  Goal ID:  {checkin.get('goal_id')}")
    print(f"  Content:  {checkin.get('content')}")
    if checkin.get("new_value") is not None:
        print(f"  Value:    {checkin.get('previous_value')} -> {checkin.get('new_value')} (delta: {checkin.get('delta')})")
    print()


def cmd_dashboard(store: GoalStore, args: argparse.Namespace) -> None:
    """Show goal dashboard."""
    dash = store.dashboard(project=args.project)

    print(f"\n=== Goal Dashboard ===")
    if args.project:
        print(f"  Project: {args.project}")
    print(f"\n  Total:    {dash['total']}")
    print(f"  Active:   {dash['active']}")
    print(f"  Complete: {dash['completed']}")
    print(f"  Overdue:  {dash['overdue']}")
    print(f"  Behind:   {dash['behind_schedule']}")

    if dash["overdue_goals"]:
        print(f"\n  OVERDUE:")
        for g in dash["overdue_goals"]:
            print(f"    - {g['title']} (due {g['deadline'][:10] if g.get('deadline') else '?'})")

    if dash["behind_goals"]:
        print(f"\n  BEHIND SCHEDULE:")
        for g in dash["behind_goals"]:
            print(f"    - {g['title']} ({g['current_value']}/{g['target_value']})")

    if dash["active_goals"]:
        print(f"\n  ACTIVE GOALS:")
        for g in dash["active_goals"]:
            print(f"    [{g['priority']}] {g['title']}  (project={g.get('project', '-')})")
    print()


def cmd_search(store: GoalStore, args: argparse.Namespace) -> None:
    """Semantic search across goals."""
    print(f'\nSearching goals for: "{args.query}"')
    results = store.search_goals(
        query=args.query,
        status=args.status,
        limit=args.limit or 10,
    )
    if not results:
        print("  No goals found.\n")
        return

    print(f"\n  Found {len(results)} goals:\n")
    for i, g in enumerate(results, 1):
        sim = g.get("similarity", 0)
        print(f"  {i}. [{g['priority']}] {g['title']}  (sim={sim:.3f}, status={g['status']})")
        if g.get("description"):
            print(f"     {g['description'][:120]}")
    print()


def cmd_milestone(store: GoalStore, args: argparse.Namespace) -> None:
    """Create a milestone under a parent goal."""
    goal = store.create_goal(
        title=args.title,
        description=args.description,
        goal_type="milestone",
        parent_id=args.parent_id,
        project=args.project,
        priority=args.priority or "P2",
        target_value=args.target,
        unit=args.unit,
        deadline=args.deadline,
    )
    print(f"\nMilestone created:")
    print(f"  ID:       {goal.get('id')}")
    print(f"  Title:    {goal.get('title')}")
    print(f"  Parent:   {goal.get('parent_id')}")
    print()


def cmd_complete(store: GoalStore, args: argparse.Namespace) -> None:
    """Mark a goal as completed."""
    goal = store.complete_goal(args.goal_id)
    if goal:
        print(f"\nGoal completed: {goal.get('title')}")
        print(f"  Completed at: {goal.get('completed_at')}")
    else:
        print(f"\nGoal not found: {args.goal_id}")
    print()


def cmd_smoke(store: GoalStore, args: argparse.Namespace) -> None:
    """End-to-end smoke test."""
    print("\n=== Jake Goals Smoke Test ===\n")
    results = {}
    test_ids = []

    # 1. Create a test goal
    try:
        print("1. Creating test goal...")
        goal = store.create_goal(
            title="Smoke Test: Ship v2.0 beta",
            description="End-to-end test goal for the goal tracking layer",
            goal_type="goal",
            project="smoke-test",
            priority="P1",
            target_value=100,
            unit="percent",
            deadline="2026-12-31T00:00:00+00:00",
            people=["mike", "jake"],
            tags=["test", "smoke"],
        )
        goal_id = goal.get("id")
        test_ids.append(goal_id)
        print(f"   PASS  goal_id={goal_id}")
        results["create_goal"] = "PASS"
    except Exception as e:
        print(f"   FAIL  {e}")
        results["create_goal"] = f"FAIL: {e}"
        print("\n=== Cannot continue without goal. Aborting. ===\n")
        _print_results(results)
        return

    # 2. Create a milestone
    try:
        print("2. Creating milestone...")
        milestone = store.create_goal(
            title="Smoke Test: Auth module complete",
            goal_type="milestone",
            parent_id=goal_id,
            project="smoke-test",
            target_value=100,
            unit="percent",
        )
        milestone_id = milestone.get("id")
        test_ids.append(milestone_id)
        print(f"   PASS  milestone_id={milestone_id}")
        results["create_milestone"] = "PASS"
    except Exception as e:
        print(f"   FAIL  {e}")
        results["create_milestone"] = f"FAIL: {e}"

    # 3. Add a check-in
    try:
        print("3. Adding check-in with value update...")
        checkin = store.add_checkin(
            goal_id=goal_id,
            content="Finished the auth module, 35% done overall",
            new_value=35,
            source="smoke-test",
        )
        print(f"   PASS  delta={checkin.get('delta')}, new_value={checkin.get('new_value')}")
        results["add_checkin"] = "PASS"
    except Exception as e:
        print(f"   FAIL  {e}")
        results["add_checkin"] = f"FAIL: {e}"

    # 4. Semantic search
    try:
        print("4. Searching for 'ship beta release'...")
        search_results = store.search_goals("ship beta release", limit=5)
        found = any(r.get("id") == goal_id for r in search_results)
        if found:
            sim = next(r["similarity"] for r in search_results if r["id"] == goal_id)
            print(f"   PASS  found test goal (similarity={sim:.3f})")
            results["search"] = "PASS"
        else:
            print(f"   WARN  test goal not in top 5 results ({len(search_results)} returned)")
            results["search"] = "WARN: not in top results"
    except Exception as e:
        print(f"   FAIL  {e}")
        results["search"] = f"FAIL: {e}"

    # 5. Dashboard
    try:
        print("5. Running dashboard...")
        dash = store.dashboard(project="smoke-test")
        print(f"   total={dash['total']}, active={dash['active']}, completed={dash['completed']}")
        ok = dash["total"] >= 2 and dash["active"] >= 2
        print(f"   {'PASS' if ok else 'WARN'}  expected >=2 total, >=2 active")
        results["dashboard"] = "PASS" if ok else "WARN"
    except Exception as e:
        print(f"   FAIL  {e}")
        results["dashboard"] = f"FAIL: {e}"

    # 6. Get milestones
    try:
        print("6. Getting milestones for goal...")
        milestones = store.get_milestones(goal_id)
        ok = len(milestones) >= 1
        print(f"   {'PASS' if ok else 'FAIL'}  found {len(milestones)} milestone(s)")
        results["get_milestones"] = "PASS" if ok else "FAIL"
    except Exception as e:
        print(f"   FAIL  {e}")
        results["get_milestones"] = f"FAIL: {e}"

    # 7. Complete the goal
    try:
        print("7. Completing goal...")
        completed = store.complete_goal(goal_id)
        ok = completed.get("status") == "completed" and completed.get("completed_at") is not None
        print(f"   {'PASS' if ok else 'FAIL'}  status={completed.get('status')}")
        results["complete_goal"] = "PASS" if ok else "FAIL"
    except Exception as e:
        print(f"   FAIL  {e}")
        results["complete_goal"] = f"FAIL: {e}"

    # 8. Cleanup
    try:
        print("8. Cleaning up test data...")
        for tid in reversed(test_ids):
            store.delete_goal(tid)
        print("   PASS  test data deleted")
        results["cleanup"] = "PASS"
    except Exception as e:
        print(f"   FAIL  {e}")
        results["cleanup"] = f"FAIL: {e}"

    # Summary
    _print_results(results)


def _print_results(results: dict) -> None:
    """Print smoke test summary."""
    print("\n=== Results ===\n")
    passed = sum(1 for v in results.values() if v == "PASS")
    total = len(results)
    for step, result in results.items():
        icon = "OK" if result == "PASS" else "!!" if "WARN" in str(result) else "XX"
        print(f"  [{icon}] {step}: {result}")
    print(f"\n  {passed}/{total} passed")
    print("\n=== Smoke Test Complete ===\n")


def main():
    parser = argparse.ArgumentParser(description="Jake's Goal Tracking CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # create
    p_create = sub.add_parser("create", help="Create a new goal")
    p_create.add_argument("title", help="Goal title")
    p_create.add_argument("--description", help="Goal description")
    p_create.add_argument("--type", help="Goal type: goal|milestone|kpi|okr")
    p_create.add_argument("--project", help="Project slug")
    p_create.add_argument("--priority", help="P0|P1|P2|P3")
    p_create.add_argument("--target", type=float, help="Target value")
    p_create.add_argument("--unit", help="Unit of measurement")
    p_create.add_argument("--deadline", help="Deadline (ISO 8601)")
    p_create.add_argument("--people", help="Comma-separated people")
    p_create.add_argument("--tags", help="Comma-separated tags")

    # list
    p_list = sub.add_parser("list", help="List goals")
    p_list.add_argument("--status", help="Filter by status")
    p_list.add_argument("--project", help="Filter by project")
    p_list.add_argument("--type", help="Filter by goal type")
    p_list.add_argument("--limit", type=int, help="Max results")

    # checkin
    p_checkin = sub.add_parser("checkin", help="Add a check-in")
    p_checkin.add_argument("goal_id", help="Goal UUID")
    p_checkin.add_argument("content", help="Check-in description")
    p_checkin.add_argument("--value", type=float, help="New current value")
    p_checkin.add_argument("--source", help="Source: manual|cron|agent|hermes")

    # dashboard
    p_dash = sub.add_parser("dashboard", help="Goal dashboard")
    p_dash.add_argument("--project", help="Filter by project")

    # search
    p_search = sub.add_parser("search", help="Semantic search goals")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--status", help="Filter by status")
    p_search.add_argument("--limit", type=int, help="Max results")

    # milestone
    p_mile = sub.add_parser("milestone", help="Create a milestone under a goal")
    p_mile.add_argument("parent_id", help="Parent goal UUID")
    p_mile.add_argument("title", help="Milestone title")
    p_mile.add_argument("--description", help="Description")
    p_mile.add_argument("--project", help="Project slug")
    p_mile.add_argument("--priority", help="P0|P1|P2|P3")
    p_mile.add_argument("--target", type=float, help="Target value")
    p_mile.add_argument("--unit", help="Unit of measurement")
    p_mile.add_argument("--deadline", help="Deadline (ISO 8601)")

    # complete
    p_complete = sub.add_parser("complete", help="Complete a goal")
    p_complete.add_argument("goal_id", help="Goal UUID")

    # smoke
    sub.add_parser("smoke", help="Run end-to-end smoke test")

    args = parser.parse_args()
    store = GoalStore()

    commands = {
        "create": cmd_create,
        "list": cmd_list,
        "checkin": cmd_checkin,
        "dashboard": cmd_dashboard,
        "search": cmd_search,
        "milestone": cmd_milestone,
        "complete": cmd_complete,
        "smoke": cmd_smoke,
    }
    commands[args.command](store, args)


if __name__ == "__main__":
    main()
