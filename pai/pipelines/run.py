#!/usr/bin/env python3
"""PAI V3: Pipeline Runner

Unified entry point for all PAI autonomous pipelines.

Usage:
    python run.py briefing          # Morning briefing (email + calendar)
    python run.py briefing --json   # JSON output
    python run.py triage            # Email triage with urgency scoring
    python run.py triage --json     # JSON output
    python run.py prep "Meeting"    # Meeting prep for specific meeting
    python run.py prep --next       # Prep for next upcoming meeting
    python run.py status            # Show pipeline health
    python run.py all               # Run briefing + triage
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Ensure pai/pipelines is importable
PIPELINE_DIR = Path(__file__).parent
sys.path.insert(0, str(PIPELINE_DIR))

from morning_briefing import build_briefing, print_text_brief
from email_triage import run_triage, print_triage
from meeting_prep import prep_meeting, print_prep


def cmd_briefing(args: list[str]):
    """Run morning briefing pipeline."""
    brief = build_briefing()
    if "--json" in args:
        print(json.dumps(brief, indent=2))
    else:
        print_text_brief(brief)
    return brief


def cmd_triage(args: list[str]):
    """Run email triage pipeline."""
    result = run_triage()
    if "--json" in args:
        print(json.dumps(result, indent=2))
    else:
        print_triage(result)
    return result


def cmd_prep(args: list[str]):
    """Run meeting prep pipeline."""
    # Filter out flags
    title_parts = [a for a in args if not a.startswith("--")]
    title = " ".join(title_parts) if title_parts else "Next Meeting"

    if "--next" in args:
        title = get_next_meeting_title()

    result = prep_meeting(title)
    if "--json" in args:
        print(json.dumps(result, indent=2))
    else:
        print_prep(result)
    return result


def get_next_meeting_title() -> str:
    """Get the title of the next upcoming meeting from Calendar."""
    import subprocess
    try:
        # Use Orchard MCP if available, fall back to osascript
        result = subprocess.run(
            ["osascript", "-e", '''
            tell application "Calendar"
                set now to current date
                set endDay to now + (1 * days)
                set nextTitle to ""
                repeat with calName in {"Work", "Home", "Calendar"}
                    try
                        set evts to every event of calendar calName whose start date >= now and start date < endDay
                        repeat with e in evts
                            if nextTitle is "" then
                                set nextTitle to summary of e
                            else if start date of e < start date of (first event of calendar calName whose summary is nextTitle) then
                                set nextTitle to summary of e
                            end if
                        end repeat
                    end try
                end repeat
                return nextTitle
            end tell'''],
            capture_output=True, text=True, timeout=15
        )
        title = result.stdout.strip()
        return title if title else "Next Meeting"
    except Exception:
        return "Next Meeting"


def cmd_all(args: list[str]):
    """Run briefing + triage together."""
    print("=" * 60)
    cmd_briefing(args)
    print("\n" + "=" * 60)
    cmd_triage(args)


def cmd_status(args: list[str]):
    """Show pipeline health and tool availability."""
    import subprocess
    print("=== PAI PIPELINE STATUS ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check mail-app-cli
    mail_cli = Path.home() / "go" / "bin" / "mail-app-cli"
    if mail_cli.exists():
        try:
            result = subprocess.run(
                [str(mail_cli), "accounts", "list"],
                capture_output=True, text=True, timeout=10
            )
            accounts = json.loads(result.stdout)
            acct_names = [a["Name"] for a in accounts]
            print(f"  mail-app-cli: OK ({', '.join(acct_names)})")
        except Exception as e:
            print(f"  mail-app-cli: ERROR ({e})")
    else:
        print("  mail-app-cli: NOT FOUND")

    # Check Orchard MCP
    try:
        import urllib.request
        req = urllib.request.Request(
            "http://localhost:8086/mcp",
            data=json.dumps({
                "jsonrpc": "2.0", "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "pai-status", "version": "1.0"}
                },
                "id": 1
            }).encode(),
            headers={"Content-Type": "application/json", "Accept": "application/json"}
        )
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read())
        if "result" in data:
            print("  Orchard MCP: OK (localhost:8086)")
        else:
            print("  Orchard MCP: ERROR (bad response)")
    except Exception:
        print("  Orchard MCP: NOT RUNNING")

    # Check Calendar (osascript)
    try:
        result = subprocess.run(
            ["osascript", "-e", 'tell application "Calendar" to get name of calendars'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print(f"  Calendar (osascript): OK")
        else:
            print(f"  Calendar (osascript): ERROR")
    except Exception:
        print("  Calendar (osascript): TIMEOUT")

    # Check .env
    env_file = PIPELINE_DIR / ".env"
    if env_file.exists():
        print(f"  GCP credentials: OK (.env present)")
    else:
        print(f"  GCP credentials: MISSING (.env not found)")

    # Pipeline files
    print()
    print("  Pipelines:")
    for name in ["morning_briefing.py", "email_triage.py", "meeting_prep.py"]:
        path = PIPELINE_DIR / name
        print(f"    {name}: {'OK' if path.exists() else 'MISSING'}")

    print()
    print("=== END STATUS ===")


COMMANDS = {
    "briefing": cmd_briefing,
    "triage": cmd_triage,
    "prep": cmd_prep,
    "all": cmd_all,
    "status": cmd_status,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print(__doc__)
        sys.exit(0)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command not in COMMANDS:
        print(f"Unknown command: {command}")
        print(f"Available: {', '.join(COMMANDS.keys())}")
        sys.exit(1)

    COMMANDS[command](args)


if __name__ == "__main__":
    main()
