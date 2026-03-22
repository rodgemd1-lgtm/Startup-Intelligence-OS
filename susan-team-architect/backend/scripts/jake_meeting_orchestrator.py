#!/usr/bin/env python3
"""Jake Meeting Orchestrator CLI — test, trigger, and inspect meeting prep.

Usage:
  python scripts/jake_meeting_orchestrator.py upcoming            # show meetings needing prep in next 2h
  python scripts/jake_meeting_orchestrator.py run --event-json '{"summary":"...","attendees":[]}'
  python scripts/jake_meeting_orchestrator.py test                # run with fake Oracle Health meeting
  python scripts/jake_meeting_orchestrator.py classify <title>   # classify meeting type
  python scripts/jake_meeting_orchestrator.py recipes             # list available recipes
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ── Path setup ─────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Load env
env_file = Path.home() / ".hermes" / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("jake.meeting")


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_upcoming(args: argparse.Namespace) -> None:
    """Show meetings needing prep in the next 2 hours."""
    print("\n📅 Checking upcoming meetings...\n")

    # Import calendar fetchers from meeting_prep.py
    from jake_brain.nervous.meeting_prep import _fetch_google_events_soon, _fetch_apple_events_soon, _minutes_until

    lookahead = args.minutes if hasattr(args, "minutes") else 120
    events = _fetch_google_events_soon(minutes_ahead=lookahead)
    events += _fetch_apple_events_soon(minutes_ahead=lookahead)

    if not events:
        print(f"No meetings in the next {lookahead} minutes.")
        return

    print(f"Found {len(events)} meetings in the next {lookahead} min:\n")
    for ev in sorted(events, key=lambda e: e.get("start", "")):
        mins = _minutes_until(ev.get("start", ""))
        mins_str = f"~{int(mins)} min" if mins is not None else "unknown"
        attendees = ev.get("attendees", [])
        att_str = f" | {len(attendees)} attendees" if attendees else ""
        print(f"  [{mins_str:>10}]  {ev.get('summary', 'Untitled')}{att_str}")

    print()


def cmd_run(args: argparse.Namespace) -> None:
    """Run full orchestration for a meeting specified by JSON."""
    try:
        event = json.loads(args.event_json)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON — {e}")
        sys.exit(1)

    from jake_brain.nervous.meeting_prep import _minutes_until
    start_str = event.get("start", "")
    if start_str:
        mins = _minutes_until(start_str) or 15.0
    else:
        # No start time — set 15 min as default
        mins = 15.0
        event["start"] = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()

    print(f"\n🚀 Running meeting prep orchestration...")
    print(f"   Meeting: {event.get('summary', 'Untitled')}")
    print(f"   Starts in: ~{int(mins)} min")
    print(f"   Attendees: {len(event.get('attendees', []))}\n")

    from jake_brain.meeting_orchestrator import MeetingOrchestrator
    orch = MeetingOrchestrator()

    package = orch.orchestrate(event, mins)

    print("\n" + "=" * 60)
    print("✅ PREP COMPLETE")
    print("=" * 60)
    print(f"Research phases: {len(package.research)}")
    for r in package.research:
        status = "✓" if r.success else "✗"
        print(f"  {status} {r.phase}: {len(r.content)} chars")

    print(f"\nDeliverables: {len(package.deliverables)}")
    for name, path in package.deliverables.items():
        print(f"  📄 {name}: {path}")

    if package.brain_episode_id:
        print(f"\nBrain episode: {package.brain_episode_id}")

    print(f"\nTelegram brief preview:\n{'-'*40}")
    print(package.telegram_brief)
    print()


def cmd_test(args: argparse.Namespace) -> None:
    """Test with a fake Oracle Health meeting."""
    now = datetime.now(timezone.utc)
    meeting_start = now + timedelta(minutes=15)

    fake_event = {
        "id": "test-oracle-deal-001",
        "summary": "Oracle Health Q2 Deal Review — Regional Health System",
        "start": meeting_start.isoformat(),
        "location": "",
        "description": "Review MEDDPICC scores for the 5,000-bed health system deal. Epic is the main competitor. Decision expected Q2.",
        "attendees": [
            "mike.rodgers@oracle.com",
            "sarah.chen@oracle.com",
            "john.smith@regionalhealthsystem.org",
        ],
        "hangout": "https://meet.google.com/test-abc-xyz",
        "source": "google",
    }

    print("\n🧪 TEST MODE — Oracle Health Deal Review")
    print(f"   Fake meeting in 15 minutes from now\n")

    # Show what the classifier picks up
    from jake_brain.meeting_orchestrator import MeetingOrchestrator
    orch = MeetingOrchestrator()
    context = orch.extract_context(fake_event, 15.0)

    print(f"Context extracted:")
    print(f"  Meeting type: {context.meeting_type}")
    print(f"  Keywords: {context.keywords}")
    print(f"  Output dir: {context.output_dir}")

    recipe = orch.match_recipe(context)
    if recipe:
        print(f"  Recipe matched: {recipe.get('name')}")
    else:
        recipe = orch.auto_create_recipe(context)
        print(f"  Recipe auto-created: {recipe.get('name')}")

    if args.dry_run:
        print("\n[DRY RUN] Would run full orchestration. Pass --no-dry-run to actually run.")
        return

    print("\nRunning full orchestration (this may take 3-5 minutes)...\n")

    # Pass through to cmd_run logic
    import json
    fake_args = argparse.Namespace()
    fake_args.event_json = json.dumps(fake_event)
    cmd_run(fake_args)


def cmd_classify(args: argparse.Namespace) -> None:
    """Classify a meeting type from its title."""
    from jake_brain.meeting_orchestrator import MeetingOrchestrator
    orch = MeetingOrchestrator()

    fake_event = {"summary": args.title, "description": "", "attendees": []}
    context = orch.extract_context(fake_event, minutes_left=15.0)

    print(f"\nMeeting: {args.title}")
    print(f"Type: {context.meeting_type}")
    print(f"Keywords: {context.keywords}")

    recipe = orch.match_recipe(context)
    if recipe:
        print(f"Recipe: {recipe.get('name')} — {recipe.get('description', '')}")
    else:
        print("Recipe: (none — would auto-create)")
    print()


def cmd_recipes(args: argparse.Namespace) -> None:
    """List all available recipes."""
    from jake_brain.meeting_orchestrator import RECIPES_DIR
    recipes_dir = RECIPES_DIR

    print(f"\n📋 Recipes in {recipes_dir}:\n")
    if not recipes_dir.exists():
        print("  No recipes directory found.")
        return

    yaml_files = sorted(recipes_dir.glob("*.yaml"))
    if not yaml_files:
        print("  No recipes found.")
        return

    try:
        import yaml
        for recipe_file in yaml_files:
            try:
                with open(recipe_file) as f:
                    r = yaml.safe_load(f)
                name = r.get("name", recipe_file.stem)
                desc = r.get("description", "")
                tags = ", ".join(r.get("tags", []))
                steps = len(r.get("steps", []))
                print(f"  {name:<30} {steps} steps  [{tags}]")
                if desc:
                    print(f"    {desc}")
            except Exception:
                print(f"  {recipe_file.name} (could not parse)")
    except ImportError:
        # No yaml module — just list files
        for recipe_file in yaml_files:
            print(f"  {recipe_file.stem}")
    print()


def cmd_daemon_trigger(args: argparse.Namespace) -> None:
    """Called by the nervous daemon when a meeting is detected.

    Accepts meeting data via --event-json and runs background orchestration.
    """
    try:
        event = json.loads(args.event_json)
    except (json.JSONDecodeError, AttributeError):
        logger.error("Invalid or missing --event-json")
        sys.exit(1)

    mins = args.minutes_left if hasattr(args, "minutes_left") else 15.0

    from jake_brain.meeting_orchestrator import MeetingOrchestrator
    orch = MeetingOrchestrator()

    if args.background:
        thread = orch.orchestrate_background(event, mins)
        logger.info("Meeting prep launched in background thread: %s", thread.name)
        # Don't wait — daemon resumes
    else:
        package = orch.orchestrate(event, mins)
        logger.info("Meeting prep complete: %d phases, brief sent", len(package.research))


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Jake Meeting Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command")

    # upcoming
    up_parser = sub.add_parser("upcoming", help="Show meetings needing prep in next 2h")
    up_parser.add_argument("--minutes", type=int, default=120, help="Look-ahead window in minutes")

    # run
    run_parser = sub.add_parser("run", help="Run orchestration for a specific meeting")
    run_parser.add_argument("--event-json", required=True, help="Calendar event as JSON string")

    # test
    test_parser = sub.add_parser("test", help="Test with fake Oracle Health meeting")
    test_parser.add_argument("--dry-run", action="store_true", default=True, help="Show plan without running (default)")
    test_parser.add_argument("--no-dry-run", action="store_false", dest="dry_run", help="Actually run orchestration")

    # classify
    classify_parser = sub.add_parser("classify", help="Classify meeting type from title")
    classify_parser.add_argument("title", help="Meeting title to classify")

    # recipes
    sub.add_parser("recipes", help="List available recipes")

    # daemon-trigger (internal — called by nervous daemon)
    dt_parser = sub.add_parser("daemon-trigger", help="Internal: trigger from nervous daemon")
    dt_parser.add_argument("--event-json", required=True, help="Calendar event as JSON")
    dt_parser.add_argument("--minutes-left", type=float, default=15.0, help="Minutes until meeting")
    dt_parser.add_argument("--background", action="store_true", default=True)

    args = parser.parse_args()

    if args.command == "upcoming":
        cmd_upcoming(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "test":
        cmd_test(args)
    elif args.command == "classify":
        cmd_classify(args)
    elif args.command == "recipes":
        cmd_recipes(args)
    elif args.command == "daemon-trigger":
        cmd_daemon_trigger(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
