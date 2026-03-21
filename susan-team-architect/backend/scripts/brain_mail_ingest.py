#!/usr/bin/env python3
"""Ingest Apple Mail (Exchange/Oracle Health) emails into Jake's Brain.

Reads emails from Mail.app via osascript (AppleScript) and stores them as:
1. Episodic memories (one per email)
2. A semantic memory summarizing recent email themes/senders
3. Entity records for frequent senders

Usage:
    cd susan-team-architect/backend && source .venv/bin/activate
    python scripts/brain_mail_ingest.py [--dry-run] [--days 7] [--account Exchange]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from jake_brain.store import BrainStore
from jake_brain.config import brain_config

# AppleScript template to extract emails from a specific account.
# Returns JSON array to stdout.
JXA_MAIL_SCRIPT = '''
const Mail = Application("Mail");
const daysBack = {days};
const targetAccount = "{account}";
const cutoffDate = new Date();
cutoffDate.setDate(cutoffDate.getDate() - daysBack);

const results = [];
let acct;
try {{
    acct = Mail.accounts.whose({{name: targetAccount}})[0];
}} catch(e) {{
    JSON.stringify([]);
}}

if (!acct) {{
    JSON.stringify([]);
}}

// Only check key mailboxes (Inbox + Sent Items) — not all 20+ mailboxes
const targetMailboxNames = ["Inbox", "Sent Items"];
const mailboxes = acct.mailboxes();

for (let i = 0; i < mailboxes.length; i++) {{
    const mb = mailboxes[i];
    const mbName = mb.name();
    if (targetMailboxNames.indexOf(mbName) === -1) continue;

    let msgs;
    try {{
        msgs = mb.messages();
    }} catch(e) {{
        continue;
    }}

    // Iterate from newest first (index 0 = newest in Mail.app)
    // Stop after hitting emails older than cutoff (they're sorted by date desc)
    const limit = Math.min(msgs.length, 500); // Safety cap
    let oldCount = 0;
    for (let j = 0; j < limit; j++) {{
        try {{
            const msg = msgs[j];
            const recvDate = msg.dateReceived();
            if (recvDate < cutoffDate) {{
                oldCount++;
                if (oldCount > 5) break; // Stop once we hit 5 old emails in a row
                continue;
            }}
            oldCount = 0;

            let snippet = "";
            try {{
                const raw = msg.content();
                if (raw) snippet = raw.substring(0, 500);
            }} catch(e) {{}}

            results.push({{
                message_id: msg.messageId() || "",
                subject: msg.subject() || "(no subject)",
                sender: msg.sender() || "unknown",
                date_received: recvDate.toISOString(),
                is_read: msg.readStatus(),
                is_flagged: msg.flaggedStatus(),
                snippet: snippet,
                mailbox: mbName
            }});
        }} catch(e) {{
            continue;
        }}
    }}
}}
JSON.stringify(results);
'''

OSASCRIPT_TIMEOUT = 90  # seconds (Exchange Inbox can be 26K+ messages)


def extract_sender_name(sender: str) -> str:
    """Extract a display name from an email sender string.

    Handles formats like:
        'John Smith <john@example.com>'
        'john@example.com'
        '"John Smith" <john@example.com>'
    """
    sender = sender.strip()
    if "<" in sender:
        name = sender.split("<")[0].strip().strip('"').strip("'")
        if name:
            return name
    # Just an email address — use the local part
    if "@" in sender:
        return sender.split("@")[0].replace(".", " ").title()
    return sender


def fetch_emails(account: str, days: int) -> list[dict]:
    """Fetch emails from Mail.app via osascript (JXA). Returns list of email dicts."""
    script = JXA_MAIL_SCRIPT.format(days=days, account=account)

    try:
        result = subprocess.run(
            ["osascript", "-l", "JavaScript", "-e", script],
            capture_output=True,
            text=True,
            timeout=OSASCRIPT_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        print(f"ERROR: osascript timed out after {OSASCRIPT_TIMEOUT}s.")
        print("Mail.app may be hung. Try:")
        print("  killall Mail")
        print("  open -a Mail")
        print("Then re-run this script.")
        return []

    if result.returncode != 0:
        print(f"ERROR: osascript failed (exit {result.returncode})")
        if result.stderr:
            print(f"  stderr: {result.stderr.strip()}")
        return []

    raw = result.stdout.strip()
    if not raw or raw == "[]":
        print(f"No emails found in '{account}' account for the last {days} days.")
        return []

    try:
        emails = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Failed to parse osascript JSON output: {exc}")
        print(f"  Raw output (first 500 chars): {raw[:500]}")
        return []

    return emails


def ingest_emails(
    account: str = "Exchange",
    days: int = 7,
    dry_run: bool = False,
):
    """Main ingestion pipeline."""
    print(f"Fetching emails from '{account}' account (last {days} days)...")
    emails = fetch_emails(account, days)

    if not emails:
        return

    print(f"Found {len(emails)} emails.\n")

    if dry_run:
        for e in emails:
            sender = extract_sender_name(e.get("sender", ""))
            subj = e.get("subject", "(no subject)")[:60]
            date = e.get("date_received", "?")[:10]
            flagged = " [FLAGGED]" if e.get("is_flagged") else ""
            unread = " [UNREAD]" if not e.get("is_read") else ""
            print(f"  Would ingest: {date} | {sender:25s} | {subj}{flagged}{unread}")
        print(f"\n[DRY RUN] Would ingest {len(emails)} emails. Exiting.")
        return

    store = BrainStore()
    stats = {
        "episodic": 0,
        "skipped_dedup": 0,
        "entities_created": 0,
        "semantic": 0,
    }

    # --- Dedup check: gather existing message_ids in brain ---
    # We check a batch at a time to avoid huge queries
    existing_msg_ids: set[str] = set()
    try:
        result = (
            store.supabase.table("jake_episodic")
            .select("metadata")
            .eq("source", "apple_mail")
            .execute()
        )
        for row in result.data or []:
            mid = (row.get("metadata") or {}).get("message_id")
            if mid:
                existing_msg_ids.add(mid)
    except Exception:
        pass  # If query fails, we'll just skip dedup

    # --- Build episodic memory batch ---
    memories: list[dict] = []
    sender_counter: Counter = Counter()

    for e in emails:
        msg_id = e.get("message_id", "")
        if msg_id in existing_msg_ids:
            stats["skipped_dedup"] += 1
            continue

        subject = e.get("subject", "(no subject)")
        sender_raw = e.get("sender", "unknown")
        sender_name = extract_sender_name(sender_raw)
        date_received = e.get("date_received", datetime.now(timezone.utc).isoformat())
        is_read = e.get("is_read", True)
        is_flagged = e.get("is_flagged", False)
        snippet = e.get("snippet", "")

        # Importance scoring
        if is_flagged:
            importance = 0.7
        elif not is_read:
            importance = 0.6
        else:
            importance = 0.4

        # Formatted content for the episodic memory
        content = (
            f"Email from {sender_name}: \"{subject}\"\n"
            f"Date: {date_received}\n"
            f"Status: {'flagged' if is_flagged else 'unread' if not is_read else 'read'}\n"
        )
        if snippet:
            content += f"Preview: {snippet[:300]}\n"

        memories.append({
            "content": content,
            "occurred_at": date_received,
            "memory_type": "email",
            "project": "oracle-health",
            "importance": importance,
            "people": [sender_name],
            "topics": ["oracle-health", "email"],
            "source": "apple_mail",
            "source_type": "email",
            "metadata": {
                "message_id": msg_id,
                "account": account,
                "subject": subject,
                "sender": sender_raw,
                "is_flagged": is_flagged,
                "is_read": is_read,
            },
        })

        sender_counter[sender_name] += 1

    # --- Store episodic memories in batch ---
    if memories:
        try:
            stored = store.store_episodic_batch(memories)
            stats["episodic"] = stored
            print(f"  Stored {stored} episodic memories")
        except Exception as exc:
            print(f"  ERROR storing episodic batch: {exc}")
            # Fall back to one-by-one
            for mem in memories:
                try:
                    store.store_episodic(**mem)
                    stats["episodic"] += 1
                except Exception as exc2:
                    print(f"    Failed: {mem['metadata']['subject'][:40]} — {exc2}")

    if stats["skipped_dedup"]:
        print(f"  Skipped {stats['skipped_dedup']} already-ingested emails")

    # --- Create entities for frequent senders ---
    SENDER_THRESHOLD = 2  # create entity if sender appears 2+ times
    for sender_name, count in sender_counter.most_common():
        if count < SENDER_THRESHOLD:
            break
        try:
            existing = (
                store.supabase.table("jake_entities")
                .select("id")
                .eq("name", sender_name)
                .execute()
            )
            if not existing.data:
                embedding = store.embedder.embed_query(
                    f"{sender_name} Oracle Health colleague email sender"
                )
                store.supabase.table("jake_entities").insert({
                    "name": sender_name,
                    "entity_type": "colleague",
                    "properties": {
                        "source": "apple_mail",
                        "account": account,
                        "email_count": count,
                    },
                    "importance": 0.5,
                    "embedding": embedding,
                }).execute()
                print(f"  Created entity: {sender_name} ({count} emails)")
                stats["entities_created"] += 1
        except Exception as exc:
            print(f"  Failed to create entity for {sender_name}: {exc}")

    # --- Store semantic summary ---
    if memories:
        try:
            top_senders = sender_counter.most_common(10)
            summary_lines = [
                f"Email summary from {account} account (last {days} days):",
                f"Total emails ingested: {len(memories)}",
                f"",
                "Top senders:",
            ]
            for name, count in top_senders:
                summary_lines.append(f"  - {name}: {count} emails")

            # Collect unique subjects for theme detection
            subjects = [m["metadata"]["subject"] for m in memories[:20]]
            if subjects:
                summary_lines.append("")
                summary_lines.append("Recent subjects:")
                for s in subjects[:10]:
                    summary_lines.append(f"  - {s}")

            store.store_semantic(
                content="\n".join(summary_lines),
                category="fact",
                confidence=0.85,
                source_episodes=[],
                project="oracle-health",
                topics=["oracle-health", "email", "communication"],
            )
            stats["semantic"] += 1
            print(f"  Stored email summary as semantic memory")
        except Exception as exc:
            print(f"  Failed to store semantic summary: {exc}")

    print(f"\n{'=' * 60}")
    print(f"Mail Ingestion Complete")
    print(f"  Account:           {account}")
    print(f"  Days scanned:      {days}")
    print(f"  Emails found:      {len(emails)}")
    print(f"  Episodic stored:   {stats['episodic']}")
    print(f"  Skipped (dedup):   {stats['skipped_dedup']}")
    print(f"  Entities created:  {stats['entities_created']}")
    print(f"  Semantic memories: {stats['semantic']}")
    print(f"{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(
        description="Ingest Apple Mail emails into Jake's Brain"
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without storing")
    parser.add_argument("--days", type=int, default=7, help="Days of email to fetch (default: 7)")
    parser.add_argument("--account", default="Exchange", help="Mail.app account name (default: Exchange)")
    args = parser.parse_args()
    ingest_emails(account=args.account, days=args.days, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
