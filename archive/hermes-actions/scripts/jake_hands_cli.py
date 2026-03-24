#!/usr/bin/env python3
"""Jake Hands CLI — Phase 5 smoke test and action runner.

Usage:
    python scripts/jake_hands_cli.py list
    python scripts/jake_hands_cli.py preview set_reminder --title "Call dentist" --due "March 25, 2026 at 9:00 AM"
    python scripts/jake_hands_cli.py execute set_reminder --title "Call dentist" --due "March 25, 2026 at 9:00 AM"
    python scripts/jake_hands_cli.py preview send_email --to test@example.com --subject "Hey" --body "Test"
    python scripts/jake_hands_cli.py execute send_telegram --text "Jake Hands test ✋"
    python scripts/jake_hands_cli.py smoke
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# Bootstrap path
SUSAN_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SUSAN_BACKEND not in sys.path:
    sys.path.insert(0, SUSAN_BACKEND)

# Load env
try:
    from dotenv import load_dotenv
    for env_file in [
        os.path.expanduser("~/.hermes/.env"),
        os.path.join(SUSAN_BACKEND, ".env"),
    ]:
        if os.path.exists(env_file):
            load_dotenv(env_file)
            break
except ImportError:
    pass


def cmd_list(args):
    """List all registered actions."""
    from jake_brain.actions import list_actions
    import jake_brain.actions.send_email  # noqa
    import jake_brain.actions.create_event  # noqa
    import jake_brain.actions.set_reminder  # noqa
    import jake_brain.actions.send_telegram  # noqa
    import jake_brain.actions.create_github_issue  # noqa
    import jake_brain.actions.update_notion  # noqa

    actions = list_actions()
    tier_labels = {1: "Tier 1 AUTO   ", 2: "Tier 2 CONFIRM", 3: "Tier 3 APPROVE"}
    print("\n✋ Jake's Hands — Available Actions\n" + "=" * 50)
    for a in sorted(actions, key=lambda x: x["tier"]):
        tier_str = tier_labels.get(a["tier"], f"Tier {a['tier']}")
        print(f"  [{tier_str}] {a['name']:<25} {a['description']}")
    print()


def cmd_smoke(args):
    """Run smoke tests — verify all actions instantiate and preview correctly."""
    import jake_brain.actions.send_email  # noqa
    import jake_brain.actions.create_event  # noqa
    import jake_brain.actions.set_reminder  # noqa
    import jake_brain.actions.send_telegram  # noqa
    import jake_brain.actions.create_github_issue  # noqa
    import jake_brain.actions.update_notion  # noqa
    from jake_brain.actions import get_action, SafetyTier

    print("\n✋ Jake Hands Smoke Test\n" + "=" * 50)

    test_cases = [
        ("set_reminder", {
            "title": "Smoke test reminder",
            "due_date": "March 25, 2026 at 9:00 AM",
        }),
        ("send_telegram", {
            "text": "Jake Hands smoke test ✋ — Phase 5 is live",
        }),
        ("send_email", {
            "to": "rodgemd1@gmail.com",
            "subject": "Jake Hands smoke test",
            "body": "Phase 5 action test from Jake Hands CLI.",
        }),
        ("create_event", {
            "title": "Jake test event",
            "start": "2026-03-25T10:00:00-05:00",
            "end": "2026-03-25T10:30:00-05:00",
        }),
        ("create_github_issue", {
            "owner": "mikerodgers",
            "repo": "test",
            "title": "Jake Hands test issue",
            "body": "Created by Jake Hands smoke test",
        }),
        ("update_notion", {
            "database_id": "fake-db-for-preview",
            "title": "Jake Hands test page",
            "content": "Phase 5 test content",
        }),
    ]

    passed = 0
    failed = 0

    for action_name, params in test_cases:
        cls = get_action(action_name)
        if cls is None:
            print(f"  ❌ {action_name}: NOT REGISTERED")
            failed += 1
            continue

        try:
            instance = cls(**params)
            preview = instance.preview()
            tier = instance.tier
            print(f"  ✅ {action_name} (Tier {int(tier)} {tier.name})")
            print(f"     Preview: {preview.splitlines()[0]}")
            passed += 1
        except Exception as exc:
            print(f"  ❌ {action_name}: {exc}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed\n")

    # Now actually execute the Tier 1 actions
    print("Executing Tier 1 actions (auto-execute)...\n")
    reminder_cls = get_action("set_reminder")
    if reminder_cls:
        action = reminder_cls(title="Jake Hands smoke test — Phase 5 live!", due_date="March 22, 2026 at 10:00 AM")
        result = action.execute()
        print(f"  set_reminder: {'✅' if result.success else '❌'} {result.message}")

    telegram_cls = get_action("send_telegram")
    if telegram_cls:
        action = telegram_cls(text="✋ *Jake Hands is live!*\n\nPhase 5 complete — Jake can now take actions in the real world.\n\nActions: send\\_email, create\\_event, set\\_reminder, send\\_telegram, create\\_github\\_issue, update\\_notion\n\nSafety model: Tier 1 auto ✅ | Tier 2 confirm 🤔 | Tier 3 approve 🔒")
        result = action.execute()
        print(f"  send_telegram: {'✅' if result.success else '❌'} {result.message}")

    print()


def cmd_preview(args):
    """Preview an action."""
    params = _parse_action_params(args)
    _load_action_modules()
    from jake_brain.actions import get_action
    cls = get_action(args.action)
    if not cls:
        print(f"❌ Unknown action: {args.action}")
        sys.exit(1)
    instance = cls(**params)
    print(instance.preview())


def cmd_execute(args):
    """Execute an action (with safety tier handling)."""
    params = _parse_action_params(args)
    _load_action_modules()
    from jake_brain.actions import get_action, SafetyTier
    cls = get_action(args.action)
    if not cls:
        print(f"❌ Unknown action: {args.action}")
        sys.exit(1)
    instance = cls(**params)

    if instance.tier == SafetyTier.CONFIRM and not getattr(args, "yes", False):
        print(f"\n⚠️  Tier 2 action — requires confirmation")
        print(instance.preview())
        print("\nAdd --yes to confirm and execute.\n")
        sys.exit(0)

    if instance.tier == SafetyTier.APPROVE and not getattr(args, "yes", False):
        print(f"\n🔒 Tier 3 action — requires explicit approval")
        print(instance.preview())
        print("\nAdd --yes only if you have explicit written approval.\n")
        sys.exit(0)

    result = instance.execute()
    print(f"{'✅' if result.success else '❌'} {result.message}")
    if result.data:
        print(f"   Data: {json.dumps(result.data, indent=2)}")


def _load_action_modules():
    import jake_brain.actions.send_email  # noqa
    import jake_brain.actions.create_event  # noqa
    import jake_brain.actions.set_reminder  # noqa
    import jake_brain.actions.send_telegram  # noqa
    import jake_brain.actions.create_github_issue  # noqa
    import jake_brain.actions.update_notion  # noqa


def _parse_action_params(args) -> dict:
    """Convert --key value CLI args to a dict for action instantiation."""
    params = {}
    known_params = {
        # send_email
        "to": "to", "subject": "subject", "body": "body", "from_addr": "from_addr",
        # create_event
        "title": "title", "start": "start", "end": "end", "location": "location",
        "description_text": "description_text",
        # set_reminder
        "due": "due_date", "list_name": "list_name", "notes": "notes",
        # send_telegram
        "text": "text", "chat_id": "chat_id",
        # create_github_issue
        "owner": "owner", "repo": "repo",
        # update_notion
        "database_id": "database_id", "page_id": "page_id", "content": "content",
    }
    for cli_key, field_key in known_params.items():
        val = getattr(args, cli_key, None)
        if val is not None:
            params[field_key] = val
    # title is shared across actions
    if hasattr(args, "title") and args.title:
        params["title"] = args.title
    return params


def main():
    parser = argparse.ArgumentParser(description="Jake Hands CLI — Phase 5 action runner")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("list", help="List all available actions")
    sub.add_parser("smoke", help="Run smoke tests (preview all + execute Tier 1)")

    preview_p = sub.add_parser("preview", help="Preview an action without executing")
    preview_p.add_argument("action")
    _add_action_args(preview_p)

    exec_p = sub.add_parser("execute", help="Execute an action")
    exec_p.add_argument("action")
    exec_p.add_argument("--yes", action="store_true", help="Confirm Tier 2/3 actions")
    _add_action_args(exec_p)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return

    {"list": cmd_list, "smoke": cmd_smoke, "preview": cmd_preview, "execute": cmd_execute}[args.cmd](args)


def _add_action_args(p):
    """Add all possible action params as optional args."""
    for flag in ["--to", "--subject", "--body", "--from-addr", "--title", "--start",
                 "--end", "--location", "--description-text", "--due", "--notes",
                 "--list-name", "--text", "--chat-id", "--owner", "--repo",
                 "--database-id", "--page-id", "--content"]:
        dest = flag.lstrip("-").replace("-", "_")
        p.add_argument(flag, dest=dest, default=None)


if __name__ == "__main__":
    main()
