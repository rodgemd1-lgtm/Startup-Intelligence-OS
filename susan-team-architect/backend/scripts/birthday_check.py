#!/usr/bin/env python3
"""Check Jake's Brain for upcoming birthdays and send Telegram notifications.

Queries the jake_entities table for people with birthdays in the next 7 days
and sends a formatted Telegram message via Bot API.

Usage:
    cd susan-team-architect/backend && source .venv/bin/activate
    python scripts/birthday_check.py
    python scripts/birthday_check.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date, timedelta
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv(Path.home() / ".hermes/.env")

import requests
from supabase import create_client

from susan_core.config import config as susan_config


def get_supabase():
    """Create Supabase client using Susan's config."""
    return create_client(susan_config.supabase_url, susan_config.supabase_key)


def parse_mmdd(mmdd: str) -> tuple[int, int] | None:
    """Parse 'MM-DD' string into (month, day) tuple. Returns None on failure."""
    try:
        parts = mmdd.strip().split("-")
        if len(parts) != 2:
            return None
        month, day = int(parts[0]), int(parts[1])
        if 1 <= month <= 12 and 1 <= day <= 31:
            return (month, day)
        return None
    except (ValueError, AttributeError):
        return None


def days_until(today: date, month: int, day: int) -> int:
    """Calculate days until the next occurrence of month/day, handling year wraparound."""
    try:
        this_year = date(today.year, month, day)
    except ValueError:
        # Handle Feb 29 in non-leap years
        if month == 2 and day == 29:
            this_year = date(today.year, 2, 28)
        else:
            return -1

    delta = (this_year - today).days
    if delta < 0:
        # Birthday already passed this year — check next year
        try:
            next_year = date(today.year + 1, month, day)
        except ValueError:
            next_year = date(today.year + 1, 2, 28)
        delta = (next_year - today).days

    return delta


def fetch_people_with_birthdays(supabase) -> list[dict]:
    """Fetch all active person entities from jake_entities."""
    result = (
        supabase.table("jake_entities")
        .select("name, entity_type, properties")
        .eq("entity_type", "person")
        .eq("is_active", True)
        .execute()
    )
    return result.data or []


def find_upcoming_birthdays(entities: list[dict], lookahead_days: int = 7) -> list[dict]:
    """Find entities with birthdays today or within the next N days.

    Returns a sorted list of dicts with keys: name, birthday_mmdd, days_until, label.
    """
    today = date.today()
    upcoming = []

    for entity in entities:
        props = entity.get("properties") or {}
        birthday_str = props.get("birthday")
        if not birthday_str:
            continue

        parsed = parse_mmdd(birthday_str)
        if parsed is None:
            continue

        month, day = parsed
        delta = days_until(today, month, day)

        if delta < 0 or delta > lookahead_days:
            continue

        if delta == 0:
            label = "\U0001f382 Birthday TODAY"
        elif delta == 1:
            label = "\U0001f4c5 Tomorrow"
        else:
            target = today + timedelta(days=delta)
            label = f"\U0001f4c5 {target.strftime('%A, %b %d')}"

        name = entity.get("name", "Unknown")
        # Title-case the name for display
        display_name = name.title() if name == name.lower() else name

        upcoming.append({
            "name": display_name,
            "birthday_mmdd": birthday_str,
            "days_until": delta,
            "label": label,
        })

    # Sort: today first, then by days_until
    upcoming.sort(key=lambda x: x["days_until"])
    return upcoming


def format_message(upcoming: list[dict]) -> str:
    """Format the Telegram notification message."""
    lines = ["*\U0001f382 Birthday Watch*", ""]

    # Group by label category
    todays = [b for b in upcoming if b["days_until"] == 0]
    coming = [b for b in upcoming if b["days_until"] > 0]

    if todays:
        for b in todays:
            lines.append(f"\U0001f382 *{b['name']}* — Birthday TODAY!")
        lines.append("")

    if coming:
        lines.append("*Coming up:*")
        for b in coming:
            lines.append(f"\U0001f4c5 *{b['name']}* — {b['label']}")
        lines.append("")

    return "\n".join(lines).strip()


def discover_chat_id(token: str) -> str | None:
    """Auto-discover Telegram chat ID from recent bot updates.

    Falls back to a cached file at ~/.jake/telegram_chat_id so this only
    needs to succeed once.
    """
    cache_file = Path.home() / ".jake" / "telegram_chat_id"

    # Check cache first
    if cache_file.is_file():
        cached = cache_file.read_text().strip()
        if cached:
            return cached

    # Try getUpdates API
    try:
        resp = requests.get(
            f"https://api.telegram.org/bot{token}/getUpdates",
            params={"offset": -1, "limit": 1},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("result", [])
            if results:
                msg = results[0].get("message", results[0].get("callback_query", {}).get("message", {}))
                chat = msg.get("chat", {})
                chat_id = str(chat.get("id", ""))
                if chat_id:
                    cache_file.parent.mkdir(parents=True, exist_ok=True)
                    cache_file.write_text(chat_id)
                    return chat_id
    except requests.RequestException:
        pass

    return None


def send_telegram(message: str, token: str, chat_id: str) -> bool:
    """Send a message via Telegram Bot API. Returns True on success."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = requests.post(
            url,
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
            timeout=15,
        )
        if resp.status_code == 200:
            return True
        print(f"Telegram API error: {resp.status_code} — {resp.text}", file=sys.stderr)
        return False
    except requests.RequestException as e:
        print(f"Telegram send failed: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Check Jake's Brain for upcoming birthdays")
    parser.add_argument("--dry-run", action="store_true", help="Print message without sending")
    parser.add_argument("--days", type=int, default=7, help="Lookahead window in days (default: 7)")
    args = parser.parse_args()

    # Validate Telegram credentials (unless dry run)
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

    # Auto-discover chat ID if not set
    if not chat_id and token:
        chat_id = discover_chat_id(token) or ""

    if not args.dry_run and (not token or not chat_id):
        print("Error: TELEGRAM_BOT_TOKEN required and TELEGRAM_CHAT_ID must be set or auto-discoverable", file=sys.stderr)
        sys.exit(1)

    # Connect and query
    supabase = get_supabase()
    entities = fetch_people_with_birthdays(supabase)

    if not entities:
        sys.exit(0)

    upcoming = find_upcoming_birthdays(entities, lookahead_days=args.days)

    if not upcoming:
        # No birthdays coming up — exit silently
        sys.exit(0)

    message = format_message(upcoming)

    if args.dry_run:
        print(message)
        sys.exit(0)

    success = send_telegram(message, token, chat_id)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
