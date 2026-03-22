#!/usr/bin/env python3
"""Ingest Oracle email into Jake's Brain via Microsoft Graph API.

This replaces brain_mail_ingest.py (which used Mail.app osascript).
Mail.app/Outlook osascript is unreliable on macOS 26.x — this uses
the Microsoft Graph REST API directly. No Mail.app needed.

Prerequisites:
    python scripts/ms_graph_auth.py --setup  (one-time)

Usage:
    python scripts/brain_mail_ingest_graph.py [--dry-run] [--days 1]
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from jake_brain.store import BrainStore
from scripts.ms_graph_auth import get_access_token

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


# ---------------------------------------------------------------------------
# Graph API email fetcher
# ---------------------------------------------------------------------------

def fetch_recent_emails(days: int = 1, max_messages: int = 50) -> list[dict]:
    """Fetch recent emails from Oracle inbox via Graph API."""
    token = get_access_token()
    if not token:
        print("ERROR: Microsoft Graph API not configured.")
        print("Run: python scripts/ms_graph_auth.py --setup")
        return []

    headers = {"Authorization": f"Bearer {token}"}
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")

    results = []
    for folder in ["inbox", "sentItems"]:
        url = (
            f"{GRAPH_BASE}/me/mailFolders/{folder}/messages"
            f"?$filter=receivedDateTime ge {cutoff}"
            f"&$select=id,subject,from,toRecipients,receivedDateTime,isRead,importance,bodyPreview"
            f"&$top={max_messages}"
            f"&$orderby=receivedDateTime desc"
        )
        try:
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code == 200:
                msgs = r.json().get("value", [])
                for m in msgs:
                    m["_folder"] = folder
                results.extend(msgs)
            elif r.status_code == 401:
                print("ERROR: Graph token expired. Run: python scripts/ms_graph_auth.py --setup")
                return []
            else:
                print(f"  Warning: {folder} fetch failed: {r.status_code} — {r.text[:100]}")
        except requests.exceptions.Timeout:
            print(f"  Warning: Graph API timeout for {folder} — skipping")
        except Exception as exc:
            print(f"  Warning: {folder} failed: {exc}")

    return results


def _dedup_key(message_id: str) -> str:
    return hashlib.sha256(message_id.encode()).hexdigest()[:16]


def _format_email_content(msg: dict) -> str:
    """Format a Graph API message dict into a readable content string."""
    sender = msg.get("from", {}).get("emailAddress", {})
    from_addr = f"{sender.get('name', '')} <{sender.get('address', '')}>".strip(" <>")
    subject = msg.get("subject") or "(no subject)"
    received = msg.get("receivedDateTime", "")
    is_read = msg.get("isRead", True)
    importance = msg.get("importance", "normal")
    folder = msg.get("_folder", "inbox")
    preview = (msg.get("bodyPreview") or "").strip()[:300]

    parts = [f"[{'UNREAD' if not is_read else 'read'}] {subject}"]
    if importance == "high":
        parts[0] += " [IMPORTANT]"
    parts.append(f"From: {from_addr}")
    parts.append(f"Received: {received}")
    parts.append(f"Folder: {folder}")
    if preview:
        parts.append(f"Preview: {preview}")
    return " | ".join(parts)


def _topics_from_email(msg: dict) -> list[str]:
    """Infer topic tags from email metadata."""
    topics = ["email", "oracle_health"]
    sender = (msg.get("from", {}).get("emailAddress", {}).get("address") or "").lower()

    if not msg.get("isRead"):
        topics.append("unread")
    if msg.get("importance") == "high":
        topics.append("important")
    if "oracle.com" in sender:
        topics.append("work")
    if msg.get("_folder") == "sentItems":
        topics.append("sent")
    return list(set(topics))


# ---------------------------------------------------------------------------
# Ingestion logic
# ---------------------------------------------------------------------------

def ingest_emails(dry_run: bool = False, days: int = 1):
    print(f"Fetching Oracle emails via Microsoft Graph API (last {days} days)...")
    messages = fetch_recent_emails(days=days)

    inbox = [m for m in messages if m.get("_folder") == "inbox"]
    sent = [m for m in messages if m.get("_folder") == "sentItems"]
    unread = [m for m in inbox if not m.get("isRead")]

    print(f"Total emails: {len(messages)}")
    print(f"  Inbox: {len(inbox)} ({len(unread)} unread)")
    print(f"  Sent: {len(sent)}")
    print()

    if not messages:
        print("No emails found.")
        return

    if dry_run:
        print("=== EMAILS (would store as episodic) ===")
        for m in messages[:10]:
            print(f"  {_format_email_content(m)[:100]}")
        print(f"\n[DRY RUN] Would ingest {len(messages)} emails. Exiting.")
        return

    store = BrainStore()
    sb = store.supabase
    stats = {"episodic": 0, "skipped_dupe": 0, "semantic": 0}

    # Check existing email dedup keys
    existing_keys: set[str] = set()
    try:
        res = (
            sb.table("jake_episodic")
            .select("metadata")
            .eq("source", "graph_email")
            .execute()
        )
        for row in res.data or []:
            dk = (row.get("metadata") or {}).get("dedup_key")
            if dk:
                existing_keys.add(dk)
    except Exception as exc:
        print(f"  Warning: could not check existing records: {exc}")

    print(f"Existing email dedup keys: {len(existing_keys)}")

    # Ingest each email as episodic memory
    for msg in messages:
        msg_id = msg.get("id", "")
        dk = _dedup_key(msg_id)
        if dk in existing_keys:
            stats["skipped_dupe"] += 1
            continue

        content = _format_email_content(msg)
        topics = _topics_from_email(msg)

        received_str = msg.get("receivedDateTime", "")
        try:
            occurred = datetime.fromisoformat(received_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            occurred = datetime.now(timezone.utc)

        importance = 0.6 if not msg.get("isRead") else 0.4
        if msg.get("importance") == "high":
            importance = 0.8

        try:
            store.store_episodic(
                content=content,
                occurred_at=occurred,
                memory_type="email_received",
                project="oracle-health",
                importance=importance,
                people=[],
                topics=topics,
                session_id=None,
                source="graph_email",
                source_type="email",
                metadata={
                    "dedup_key": dk,
                    "message_id": msg_id,
                    "subject": msg.get("subject", ""),
                    "from": msg.get("from", {}).get("emailAddress", {}).get("address", ""),
                    "folder": msg.get("_folder", "inbox"),
                    "is_read": msg.get("isRead", True),
                },
            )
            stats["episodic"] += 1
            existing_keys.add(dk)
        except Exception as exc:
            print(f"  Failed: {msg.get('subject', '?')} — {exc}")

    # Summary: sender frequency + unread count
    if messages:
        sender_counts: Counter = Counter()
        for m in inbox:
            addr = m.get("from", {}).get("emailAddress", {}).get("address", "unknown")
            sender_counts[addr] += 1

        summary_lines = [
            f"Oracle email summary (last {days} days):",
            f"  Total: {len(messages)} ({len(unread)} unread in inbox)",
        ]
        if unread:
            summary_lines.append("\nUnread emails:")
            for m in unread[:10]:
                sender = m.get("from", {}).get("emailAddress", {}).get("name") or \
                         m.get("from", {}).get("emailAddress", {}).get("address", "?")
                summary_lines.append(f"  - {m.get('subject', '?')} (from: {sender})")

        summary_content = "\n".join(summary_lines)
        summary_dk = "email_summary"

        try:
            existing = (
                sb.table("jake_semantic")
                .select("id")
                .eq("category", "email_summary")
                .execute()
            )
            for row in existing.data or []:
                sb.table("jake_semantic").delete().eq("id", row["id"]).execute()

            store.store_semantic(
                content=summary_content,
                category="email_summary",
                confidence=0.9,
                source_episodes=[],
                project="oracle-health",
                topics=["email", "oracle_health", "summary"],
                metadata={
                    "source": "graph_email",
                    "dedup_key": summary_dk,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "unread_count": len(unread),
                    "total_count": len(messages),
                },
            )
            stats["semantic"] += 1
            print(f"  [SEMANTIC] Email summary ({len(unread)} unread)")
        except Exception as exc:
            print(f"  Failed to store summary: {exc}")

    print(f"\n{'=' * 60}")
    print(f"Email Ingestion Complete (Graph API)")
    print(f"  Episodic created:    {stats['episodic']}")
    print(f"  Semantic summaries:  {stats['semantic']}")
    print(f"  Skipped (dupes):     {stats['skipped_dupe']}")
    print(f"{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(description="Ingest Oracle email via Microsoft Graph API")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to brain")
    parser.add_argument("--days", type=int, default=1, help="Days of email history to fetch (default: 1)")
    args = parser.parse_args()
    ingest_emails(dry_run=args.dry_run, days=args.days)


if __name__ == "__main__":
    main()
