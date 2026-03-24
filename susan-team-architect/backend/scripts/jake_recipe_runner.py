#!/usr/bin/env python3
"""Jake Recipe Runner — execute YAML workflow recipes.

Usage:
    # List all available recipes
    python scripts/jake_recipe_runner.py list

    # Run a recipe
    python scripts/jake_recipe_runner.py run oracle-battlecard-update

    # Dry-run (no side effects, just show what would happen)
    python scripts/jake_recipe_runner.py run morning-research --dry-run

    # Run with context variables
    python scripts/jake_recipe_runner.py run deal-analysis --context '{"deal_name": "Acme Health"}'

    # Show recipe details
    python scripts/jake_recipe_runner.py show oracle-battlecard-update
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

env_file = Path.home() / ".hermes" / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


def cmd_list(args: argparse.Namespace) -> None:
    from jake_brain.recipes import list_recipes
    recipes = list_recipes()
    if not recipes:
        print("No recipes found. Add YAML files to ~/.hermes/recipes/ to get started.")
        return
    print(f"\n{'NAME':<35} {'STEPS':<7} DESCRIPTION")
    print("-" * 80)
    for r in recipes:
        tags = f" [{','.join(r['tags'])}]" if r.get("tags") else ""
        print(f"{r['name']:<35} {r['steps']:<7} {r['description'][:35]}{tags}")
    print(f"\n{len(recipes)} recipe(s) available.")


def cmd_run(args: argparse.Namespace) -> None:
    from jake_brain.recipes import RecipeRunner

    context = {}
    if args.context:
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON for --context: {e}")
            sys.exit(1)

    runner = RecipeRunner()

    print(f"\nRunning recipe: {args.name}" + (" [DRY RUN]" if args.dry_run else ""))
    print("-" * 40)

    result = runner.run(
        name=args.name,
        context=context,
        dry_run=args.dry_run,
        stop_on_error=not args.continue_on_error,
    )

    print(f"\nStatus: {result['status'].upper()}")
    print(f"Steps:  {result['steps_run']} run, {result['steps_failed']} failed")

    if args.verbose:
        print("\nStep outputs:")
        for step_out in result["outputs"]:
            icon = "✅" if step_out["success"] else "❌"
            print(f"\n{icon} {step_out['step']}")
            if step_out.get("output"):
                print(f"   {step_out['output'][:200]}")

    if result["status"] == "failed":
        sys.exit(1)


def cmd_show(args: argparse.Namespace) -> None:
    from jake_brain.recipes import load_recipe
    try:
        recipe = load_recipe(args.name)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print(f"\n{'='*50}")
    print(f"Recipe: {recipe.get('name', args.name)}")
    print(f"{'='*50}")
    if recipe.get("description"):
        print(f"Description: {recipe['description']}")
    if recipe.get("tags"):
        print(f"Tags:        {', '.join(recipe['tags'])}")
    print(f"Version:     {recipe.get('version', '1.0')}")
    print(f"Path:        {recipe.get('_path', 'unknown')}")
    print(f"\nSteps ({len(recipe.get('steps', []))}):")
    for i, step in enumerate(recipe.get("steps", []), 1):
        print(f"  {i}. [{step.get('tool','?')}] {step.get('name', 'Unnamed step')}")
        args_keys = [k for k in step.get("args", {}).keys() if k not in ("prompt",)]
        if args_keys:
            print(f"       args: {', '.join(args_keys)}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="jake_recipe_runner", description="Jake recipe executor")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List available recipes")

    r = sub.add_parser("run", help="Execute a recipe")
    r.add_argument("name", help="Recipe name")
    r.add_argument("--dry-run", action="store_true")
    r.add_argument("--context", help="JSON context variables")
    r.add_argument("--continue-on-error", action="store_true",
                   help="Continue even if a step fails")
    r.add_argument("-v", "--verbose", action="store_true", help="Show step outputs")

    s = sub.add_parser("show", help="Show recipe details")
    s.add_argument("name", help="Recipe name")

    return p


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    {"list": cmd_list, "run": cmd_run, "show": cmd_show}[args.command](args)
