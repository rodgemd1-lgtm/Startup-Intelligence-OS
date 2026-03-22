#!/usr/bin/env python3
"""Ingest iMessage conversations into Jake's Brain.

Reads from macOS ~/Library/Messages/chat.db (READ ONLY), groups messages into
conversation chunks by contact/chat, and feeds them through the Brain pipeline
for episodic/semantic/entity extraction.

Requires Full Disk Access for the terminal app running this script.

Usage:
    cd susan-team-architect/backend && source .venv/bin/activate
    python scripts/brain_imessage_ingest.py [--dry-run] [--limit N] [--days N]
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Environment bootstrap (same pattern as all brain ingest scripts)
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Load env from Hermes config
env_file = Path.home() / ".hermes" / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CHAT_DB = Path.home() / "Library" / "Messages" / "chat.db"

# Apple Cocoa epoch: 2001-01-01 00:00:00 UTC
APPLE_EPOCH = datetime(2001, 1, 1, tzinfo=timezone.utc)

# Messages per conversation chunk
MESSAGES_PER_CHUNK = 10

# Minimum chunk length to bother ingesting
MIN_CHUNK_LEN = 50

# Maximum single message length before truncation
MAX_MESSAGE_LEN = 2000

# Default lookback window
DEFAULT_DAYS = 30


def content_hash(text: str) -> str:
    """SHA256 hash of text for deduplication."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def apple_date_to_datetime(apple_date: int | None) -> datetime | None:
    """Convert Apple Cocoa Core Data timestamp to Python datetime.

    Apple stores dates as nanoseconds since 2001-01-01 00:00:00 UTC.
    Some older messages use seconds instead of nanoseconds — handle both.
    """
    if not apple_date or apple_date == 0:
        return None

    # Nanosecond timestamps are > 1e15, second timestamps are < 1e12
    if apple_date > 1_000_000_000_000:
        seconds = apple_date / 1_000_000_000
    else:
        seconds = apple_date

    try:
        return APPLE_EPOCH + timedelta(seconds=seconds)
    except (OverflowError, ValueError):
        return None


def check_db_access() -> bool:
    """Check if we can access the iMessage database."""
    if not CHAT_DB.exists():
        print(f"ERROR: iMessage database not found at {CHAT_DB}")
        print("  This script only works on macOS with an active Messages app.")
        return False

    try:
        conn = sqlite3.connect(f"file:{CHAT_DB}?mode=ro", uri=True)
        conn.execute("SELECT COUNT(*) FROM message LIMIT 1")
        conn.close()
        return True
    except sqlite3.OperationalError as exc:
        print(f"ERROR: Cannot read iMessage database: {exc}")
        print()
        print("  Full Disk Access is required for your terminal app.")
        print("  To grant access:")
        print("    1. Open System Settings → Privacy & Security → Full Disk Access")
        print("    2. Click the + button")
        print("    3. Add your terminal app (Terminal, iTerm2, Warp, etc.)")
        print("    4. Restart the terminal app")
        print("    5. Re-run this script")
        return False


def fetch_conversations(days: int = DEFAULT_DAYS) -> dict[str, list[dict]]:
    """Fetch iMessage conversations grouped by chat/contact.

    Returns a dict mapping contact identifier to a list of message dicts,
    ordered chronologically (oldest first within each conversation).
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_apple = int((cutoff - APPLE_EPOCH).total_seconds() * 1_000_000_000)

    conn = sqlite3.connect(f"file:{CHAT_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    # Query messages joined with handles (contacts) and chats
    # We join through chat_message_join and chat_handle_join to get chat context
    query = """
        SELECT
            m.ROWID as msg_id,
            m.text,
            m.date as msg_date,
            m.is_from_me,
            m.cache_has_attachments,
            h.id as contact_id,
            COALESCE(
                cmj.chat_id,
                0
            ) as chat_id
        FROM message m
        LEFT JOIN handle h ON m.handle_id = h.ROWID
        LEFT JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
        WHERE m.date > ?
          AND m.text IS NOT NULL
          AND m.text != ''
        ORDER BY m.date ASC
    """

    try:
        rows = conn.execute(query, (cutoff_apple,)).fetchall()
    except sqlite3.OperationalError as exc:
        print(f"  SQL error: {exc}")
        conn.close()
        return {}

    conn.close()

    # Group by contact (or chat_id for group chats)
    conversations: dict[str, list[dict]] = {}

    for row in rows:
        text = row["text"]
        if not text or not text.strip():
            continue

        contact = row["contact_id"] or "unknown"
        chat_id = row["chat_id"] or 0

        # For group chats, use chat_id as the key
        # For 1:1 chats, use the contact identifier
        if chat_id > 0:
            # Check if this is a group chat (multiple handles)
            key = f"chat:{chat_id}:{contact}"
        else:
            key = contact

        # Simplify key to just contact for 1:1 conversations
        # Group chats will have chat:N prefix
        simple_key = contact if not contact.startswith("chat:") else key

        msg_dt = apple_date_to_datetime(row["msg_date"])

        conversations.setdefault(simple_key, []).append({
            "text": text.strip(),
            "date": msg_dt,
            "is_from_me": bool(row["is_from_me"]),
            "contact": contact,
            "has_attachments": bool(row["cache_has_attachments"]),
        })

    return conversations


def format_contact(contact_id: str) -> str:
    """Format a contact identifier for display.

    Handles phone numbers (+1XXXXXXXXXX) and email addresses.
    """
    if not contact_id:
        return "unknown"

    # Clean up phone numbers for readability
    if contact_id.startswith("+1") and len(contact_id) == 12:
        return f"({contact_id[2:5]}) {contact_id[5:8]}-{contact_id[8:]}"

    return contact_id


def chunk_conversation(
    contact: str,
    messages: list[dict],
    chunk_size: int = MESSAGES_PER_CHUNK,
) -> list[dict]:
    """Group messages into conversation chunks for ingestion.

    Each chunk contains ~chunk_size messages with speaker labels and timestamps.
    """
    if not messages:
        return []

    chunks = []
    display_contact = format_contact(contact)

    for i in range(0, len(messages), chunk_size):
        batch = messages[i : i + chunk_size]

        lines = []
        earliest_dt = None
        latest_dt = None

        for msg in batch:
            sender = "Mike" if msg["is_from_me"] else display_contact

            text = msg["text"]
            if len(text) > MAX_MESSAGE_LEN:
                text = text[:MAX_MESSAGE_LEN] + "..."

            # Format timestamp
            ts = ""
            if msg["date"]:
                ts = msg["date"].strftime("%Y-%m-%d %H:%M")
                if not earliest_dt or msg["date"] < earliest_dt:
                    earliest_dt = msg["date"]
                if not latest_dt or msg["date"] > latest_dt:
                    latest_dt = msg["date"]

            attachment_note = " [+attachment]" if msg.get("has_attachments") else ""
            lines.append(f"[{ts}] {sender}: {text}{attachment_note}")

        content = "\n".join(lines)
        if len(content) < MIN_CHUNK_LEN:
            continue

        # Build the chunk with source context prefix
        prefixed_content = (
            f"iMessage conversation with {display_contact}:\n{content}"
        )

        chunks.append({
            "content": prefixed_content,
            "contact": contact,
            "display_contact": display_contact,
            "message_count": len(batch),
            "earliest": earliest_dt,
            "latest": latest_dt,
        })

    return chunks


def main():
    parser = argparse.ArgumentParser(
        description="Ingest iMessage conversations into Jake's Brain"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be ingested without doing it",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only process N conversations (by most recent activity)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_DAYS,
        help=f"Only ingest messages from last N days (default: {DEFAULT_DAYS})",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Jake Brain — iMessage Conversation Ingestion")
    print(f"Database: {CHAT_DB}")
    print(f"Lookback: {args.days} days")
    print("=" * 60)

    # 1. Check access
    if not check_db_access():
        sys.exit(1)

    # 2. Fetch conversations
    print(f"\nFetching messages from last {args.days} days...")
    conversations = fetch_conversations(days=args.days)

    if not conversations:
        print("No messages found in the specified time range.")
        return

    # Sort by most recent message (descending) for --limit
    sorted_contacts = sorted(
        conversations.keys(),
        key=lambda c: max(
            (m["date"] for m in conversations[c] if m["date"]),
            default=datetime.min.replace(tzinfo=timezone.utc),
        ),
        reverse=True,
    )

    if args.limit:
        sorted_contacts = sorted_contacts[: args.limit]

    total_messages = sum(len(conversations[c]) for c in sorted_contacts)
    print(f"\nConversations: {len(sorted_contacts)}")
    print(f"Total messages: {total_messages:,}")
    print()

    # 3. Chunk all conversations
    all_chunks: list[dict] = []
    seen_hashes: set[str] = set()
    contact_stats: dict[str, dict] = {}

    for contact in sorted_contacts:
        messages = conversations[contact]
        display = format_contact(contact)
        chunks = chunk_conversation(contact, messages)

        deduped = 0
        for chunk in chunks:
            h = content_hash(chunk["content"])
            if h in seen_hashes:
                continue
            seen_hashes.add(h)
            all_chunks.append(chunk)
            deduped += 1

        if deduped > 0:
            contact_stats[display] = {
                "messages": len(messages),
                "chunks": deduped,
            }
            print(
                f"  {display}: {len(messages)} messages → {deduped} chunks"
            )

    print(f"\n{'=' * 60}")
    print(f"Conversations processed: {len(contact_stats)}")
    print(f"Unique chunks to ingest: {len(all_chunks)}")

    if not all_chunks:
        print("No chunks to ingest.")
        return

    if args.dry_run:
        print(
            f"\n[DRY RUN] Would ingest {len(all_chunks)} chunks. "
            f"Previewing first 10:\n"
        )
        for i, chunk in enumerate(all_chunks[:10], 1):
            preview = chunk["content"][:120].replace("\n", " ")
            print(
                f"  {i}. [{chunk['message_count']} msgs, "
                f"{len(chunk['content']):,} chars] {preview}..."
            )
        if len(all_chunks) > 10:
            print(f"  ... and {len(all_chunks) - 10} more")
        return

    # 4. Ingest via BrainPipeline
    from jake_brain.pipeline import BrainPipeline

    print(f"\nIngesting {len(all_chunks)} chunks into Jake's Brain...")
    pipeline = BrainPipeline()

    results = {"success": 0, "failed": 0, "people": set(), "topics": set()}

    for i, chunk in enumerate(all_chunks, 1):
        try:
            occurred_at = (
                chunk["latest"].isoformat()
                if chunk.get("latest")
                else datetime.now(timezone.utc).isoformat()
            )

            result = pipeline.ingest_conversation(
                text=chunk["content"],
                session_id=f"imessage-ingest-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
                source=f"imessage:{chunk['contact']}",
                source_type="imessage",
                occurred_at=occurred_at,
            )

            extraction = result.get("extraction", {})
            results["success"] += 1
            results["people"].update(extraction.get("people", []))
            results["topics"].update(extraction.get("topics", []))

            if i % 20 == 0 or i == len(all_chunks):
                print(
                    f"  [{i}/{len(all_chunks)}] Ingested — "
                    f"people so far: {len(results['people'])}, "
                    f"topics so far: {len(results['topics'])}"
                )
        except Exception as exc:
            results["failed"] += 1
            print(f"  [{i}/{len(all_chunks)}] FAILED — {exc}")

    print(f"\n{'=' * 60}")
    print("iMessage Ingestion Complete")
    print(f"  Conversations processed: {len(contact_stats)}")
    print(f"  Chunks ingested:         {results['success']}")
    print(f"  Chunks failed:           {results['failed']}")
    print(f"  People discovered:       {sorted(results['people'])}")
    print(f"  Topics discovered:       {sorted(results['topics'])}")
    print(f"{'=' * 60}")

    # Show updated brain stats
    try:
        stats = pipeline.stats()
        print("\nBrain Stats After Ingestion:")
        for key, val in stats.items():
            if isinstance(val, dict):
                for k2, v2 in val.items():
                    print(f"  {k2}: {v2}")
            else:
                print(f"  {key}: {val}")
    except Exception as exc:
        print(f"\nCouldn't get brain stats: {exc}")


if __name__ == "__main__":
    main()
