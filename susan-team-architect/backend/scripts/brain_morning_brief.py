#!/usr/bin/env python3
"""brain_morning_brief.py — Auto-assemble Jake's morning brief from brain data.

This script replaces the hardcoded morning brief approach. It:
  1. Pulls fresh signals from the brain (episodic/semantic memories from last 48h)
  2. Scores and triage them using the Priority Engine
  3. Assembles the brief using the Context Assembler
  4. Formats it for delivery (Telegram + email)
  5. Optionally sends via Resend API and/or Telegram bot

Usage:
    python3 brain_morning_brief.py              # print brief to stdout
    python3 brain_morning_brief.py --send       # send via Telegram + email
    python3 brain_morning_brief.py --telegram   # send via Telegram only
    python3 brain_morning_brief.py --email      # send via email only
    python3 brain_morning_brief.py --debug      # verbose output
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import traceback
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone

# Bootstrap
SUSAN_BACKEND = os.path.expanduser(
    "~/Startup-Intelligence-OS/susan-team-architect/backend"
)
if SUSAN_BACKEND not in sys.path:
    sys.path.insert(0, SUSAN_BACKEND)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("brain_morning_brief")


# ---------------------------------------------------------------------------
# Data pulling helpers
# ---------------------------------------------------------------------------

def pull_recent_brain_memories(hours: int = 48) -> list[dict]:
    """Pull recent episodic memories from the brain."""
    try:
        from jake_brain.retriever import BrainRetriever
        retriever = BrainRetriever()
        time_start = datetime.now(timezone.utc) - timedelta(hours=hours)
        memories = retriever.search(
            query="meetings emails reminders tasks priorities events",
            top_k=25,
            time_start=time_start,
        )
        return memories
    except Exception as e:
        logger.error(f"Failed to pull brain memories: {e}")
        return []


def pull_brain_entities() -> list[dict]:
    """Pull key entities (people, projects) for context."""
    try:
        from jake_brain.store import BrainStore
        store = BrainStore()
        entities = []
        for name in ["mike rodgers", "james loehr", "jacob", "alex", "matt cohlmia"]:
            e = store.find_entity(name) or store.find_entity(name.title())
            if e:
                entities.append(e)
        return entities
    except Exception as e:
        logger.error(f"Failed to pull entities: {e}")
        return []


def pull_upcoming_birthdays() -> list[str]:
    """Find any birthdays in the next 7 days from semantic memories."""
    try:
        from jake_brain.retriever import BrainRetriever
        retriever = BrainRetriever()
        mems = retriever.search(query="birthday", top_k=10)
        birthdays = []
        today = datetime.now().date()
        for m in mems:
            content = m.get("content", "").lower()
            if "birthday" in content:
                birthdays.append(m.get("content", "")[:100])
        return birthdays[:5]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Priority scoring
# ---------------------------------------------------------------------------

def score_memories(memories: list[dict]) -> list[dict]:
    """Score and sort memories by priority."""
    from jake_brain.priority import PriorityEngine, PrioritySignal, SourceType

    engine = PriorityEngine()
    signals = []

    source_map = {
        "email": SourceType.EMAIL,
        "calendar": SourceType.CALENDAR,
        "reminder": SourceType.REMINDER,
        "episodic": SourceType.BRAIN,
        "semantic": SourceType.BRAIN,
        "procedural": SourceType.BRAIN,
    }

    for mem in memories:
        layer = mem.get("layer", "episodic")
        source_type = mem.get("metadata", {}).get("source_type", "")
        resolved_source = source_map.get(source_type) or source_map.get(layer, SourceType.BRAIN)

        # Parse event_time from metadata if available
        event_time = None
        meta = mem.get("metadata", {})
        for key in ("event_time", "start_time", "due_date", "date"):
            if meta.get(key):
                try:
                    event_time = datetime.fromisoformat(str(meta[key]).replace("Z", "+00:00"))
                    break
                except Exception:
                    pass

        created_at = None
        if mem.get("created_at"):
            try:
                created_at = datetime.fromisoformat(
                    str(mem["created_at"]).replace("Z", "+00:00")
                )
            except Exception:
                pass

        sig = PrioritySignal(
            content=mem.get("content", ""),
            source_type=resolved_source,
            urgency=0.5,
            importance=float(mem.get("composite_score", 0.5)),
            event_time=event_time,
            created_at=created_at,
            metadata=meta,
        )
        signals.append((engine.score(sig), mem))

    # Sort by composite score descending
    signals.sort(key=lambda x: x[0].composite_score, reverse=True)
    return [mem for sig, mem in signals]


# ---------------------------------------------------------------------------
# Brief formatting
# ---------------------------------------------------------------------------

def format_brief(
    memories: list[dict],
    entities: list[dict],
    birthdays: list[str],
    now: datetime,
) -> tuple[str, str]:
    """Format the brief for Telegram (short) and email (full).

    Returns: (telegram_text, email_html)
    """
    day_str = now.strftime("%A, %B %-d")
    time_str = now.strftime("%-I:%M %p")

    # Group memories by source type
    emails: list[dict] = []
    calendar_events: list[dict] = []
    reminders: list[dict] = []
    other: list[dict] = []

    for mem in memories:
        src = mem.get("metadata", {}).get("source_type", mem.get("layer", ""))
        content = mem.get("content", "")
        if "email" in src or content.lower().startswith("email"):
            emails.append(mem)
        elif "calendar" in src or "event" in src or content.lower().startswith("event"):
            calendar_events.append(mem)
        elif "reminder" in src or content.lower().startswith("reminder"):
            reminders.append(mem)
        else:
            other.append(mem)

    # Determine "the one thing" — enforce today-first priority.
    # Priority order:
    #   1. Overdue reminders (past due_date)
    #   2. Today's events/meetings
    #   3. This week's items
    #   4. Fall back to highest composite_score memory
    one_thing = "No clear single priority identified."
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=0)
    week_end = now.replace(hour=23, minute=59, second=59, microsecond=0)
    def _get_event_time(mem: dict):
        """Extract event time from memory metadata."""
        meta = mem.get("metadata", {}) or {}
        for key in ("event_time", "start_time", "due_date", "date"):
            val = meta.get(key)
            if val:
                try:
                    dt = datetime.fromisoformat(str(val).replace("Z", "+00:00"))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=now.tzinfo or timezone.utc)
                    return dt
                except Exception:
                    pass
        return None

    # Build candidate lists by time tier
    overdue: list[dict] = []
    today_items: list[dict] = []
    this_week: list[dict] = []

    for mem in memories:
        event_time = _get_event_time(mem)
        if event_time is None:
            continue
        if event_time < today_start:
            overdue.append(mem)
        elif today_start <= event_time <= today_end:
            today_items.append(mem)
        elif event_time <= today_start + timedelta(days=7):
            this_week.append(mem)

    # Pick "the one thing"
    if overdue:
        # Most recently overdue (closest to today)
        overdue.sort(key=lambda m: abs((today_start - (_get_event_time(m) or today_start)).total_seconds()))
        one_thing = overdue[0].get("content", "")[:200]
    elif today_items:
        # Highest priority today item (already sorted by composite score in memories list)
        today_items.sort(key=lambda m: memories.index(m))
        one_thing = today_items[0].get("content", "")[:200]
    elif this_week:
        this_week.sort(key=lambda m: memories.index(m))
        one_thing = this_week[0].get("content", "")[:200]
    elif memories:
        one_thing = memories[0].get("content", "")[:200]

    # Telegram version (short, markdown)
    lines_tg = [
        f"☀️ *MORNING BRIEF — {day_str}*",
        f"_{time_str} — assembled from your brain_\n",
    ]

    # The One Thing
    lines_tg.append(f"🎯 *THE ONE THING*\n{one_thing}\n")

    # Calendar
    if calendar_events:
        lines_tg.append("📅 *TODAY'S EVENTS*")
        for e in calendar_events[:5]:
            content = e.get("content", "")[:120]
            lines_tg.append(f"  • {content}")
        lines_tg.append("")

    # Oracle email
    if emails:
        lines_tg.append("📧 *ORACLE EMAIL*")
        for e in emails[:4]:
            content = e.get("content", "")[:120]
            lines_tg.append(f"  • {content}")
        lines_tg.append("")

    # Reminders / tasks
    if reminders:
        lines_tg.append("✅ *REMINDERS / TASKS*")
        for r in reminders[:4]:
            content = r.get("content", "")[:120]
            lines_tg.append(f"  • {content}")
        lines_tg.append("")

    # Birthdays
    if birthdays:
        lines_tg.append("🎂 *BIRTHDAYS (THIS WEEK)*")
        for b in birthdays[:3]:
            lines_tg.append(f"  • {b}")
        lines_tg.append("")

    # Other notable memories
    if other:
        lines_tg.append("🧠 *BRAIN HIGHLIGHTS*")
        for o in other[:3]:
            content = o.get("content", "")[:120]
            lines_tg.append(f"  • {content}")
        lines_tg.append("")

    telegram_text = "\n".join(lines_tg)

    # Email HTML (richer)
    def html_section(icon: str, title: str, items: list[str]) -> str:
        if not items:
            return ""
        rows = "".join(f"<li>{item}</li>" for item in items)
        return f"<h3>{icon} {title}</h3><ul>{rows}</ul>"

    email_sections = [
        f"<h2>☀️ Morning Brief — {day_str}</h2>",
        f"<p><em>Assembled at {time_str} from Jake's Brain</em></p>",
        f"<h3>🎯 The One Thing</h3><p><strong>{one_thing}</strong></p>",
        html_section("📅", "Today's Events", [e.get("content", "")[:200] for e in calendar_events[:6]]),
        html_section("📧", "Oracle Email", [e.get("content", "")[:200] for e in emails[:5]]),
        html_section("✅", "Reminders & Tasks", [r.get("content", "")[:200] for r in reminders[:5]]),
        html_section("🎂", "Birthdays This Week", birthdays[:5]),
        html_section("🧠", "Brain Highlights", [o.get("content", "")[:200] for o in other[:4]]),
    ]
    email_html = "\n".join(email_sections)

    return telegram_text, email_html


# ---------------------------------------------------------------------------
# Delivery helpers
# ---------------------------------------------------------------------------

def send_telegram(text: str) -> bool:
    """Send brief to Mike's Telegram via bot."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("HERMES_TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        logger.error("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return False
    try:
        payload = json.dumps({
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
        }).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            if data.get("ok"):
                logger.info("Telegram delivery: success")
                return True
            else:
                logger.error(f"Telegram API error: {data}")
                return False
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return False


def send_email(subject: str, html_body: str) -> bool:
    """Send brief via Resend API."""
    api_key = os.environ.get("RESEND_API_KEY")
    from_addr = os.environ.get("RESEND_FROM_EMAIL", "jake@apex-ventures.co")
    to_addr = os.environ.get("MIKE_EMAIL", "mike@apex-ventures.co")
    if not api_key:
        logger.error("Missing RESEND_API_KEY")
        return False
    try:
        payload = json.dumps({
            "from": from_addr,
            "to": [to_addr],
            "subject": subject,
            "html": html_body,
        }).encode()
        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            if data.get("id"):
                logger.info(f"Email delivery: success (id={data['id']})")
                return True
            else:
                logger.error(f"Resend API error: {data}")
                return False
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Jake Morning Brief from Brain")
    parser.add_argument("--send", action="store_true", help="Send via Telegram + email")
    parser.add_argument("--telegram", action="store_true", help="Send via Telegram only")
    parser.add_argument("--email", action="store_true", help="Send via email only")
    parser.add_argument("--debug", action="store_true", help="Verbose output")
    parser.add_argument("--hours", type=int, default=48, help="Look-back window hours")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load env from Hermes
    hermes_env = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(hermes_env):
        with open(hermes_env) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())

    now = datetime.now(timezone.utc).astimezone()
    logger.info(f"Assembling morning brief at {now.strftime('%H:%M %Z')}")

    # Pull data
    logger.info("Pulling brain memories...")
    raw_memories = pull_recent_brain_memories(hours=args.hours)
    logger.info(f"  Found {len(raw_memories)} memories")

    logger.info("Pulling brain entities...")
    entities = pull_brain_entities()
    logger.info(f"  Found {len(entities)} key entities")

    logger.info("Pulling upcoming birthdays...")
    birthdays = pull_upcoming_birthdays()
    logger.info(f"  Found {len(birthdays)} birthday memories")

    # Score and rank
    logger.info("Scoring by priority...")
    ranked_memories = score_memories(raw_memories)

    # Format
    telegram_text, email_html = format_brief(ranked_memories, entities, birthdays, now)

    # Output
    print("\n" + "="*60)
    print(telegram_text)
    print("="*60 + "\n")

    if args.debug:
        print(f"\n[DEBUG] Top memories by priority:")
        for i, m in enumerate(ranked_memories[:5], 1):
            print(f"  {i}. [{m.get('layer')}] {m.get('content', '')[:100]}")

    # Delivery
    if args.send or args.telegram:
        logger.info("Sending via Telegram...")
        send_telegram(telegram_text)

    if args.send or args.email:
        day_str = now.strftime("%A, %B %-d")
        logger.info("Sending via email...")
        send_email(f"☀️ Morning Brief — {day_str}", email_html)

    logger.info("Done.")


if __name__ == "__main__":
    main()
