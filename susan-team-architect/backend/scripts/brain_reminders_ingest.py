#!/usr/bin/env python3
"""Ingest Apple Reminders into Jake's Brain.

Reads reminders via osascript (JXA) and:
1. Stores incomplete reminders as semantic memories (category=task)
2. Stores completed reminders as episodic memories (task_completed)
3. Stores a summary of all open tasks grouped by list

Usage:
    cd susan-team-architect/backend && source .venv/bin/activate
    python scripts/brain_reminders_ingest.py [--dry-run] [--include-completed]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from jake_brain.store import BrainStore
from jake_brain.config import brain_config

# JXA script to extract reminders from Reminders.app
JXA_SCRIPT = """
(() => {
    const app = Application("Reminders");
    const now = new Date();
    const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
    const results = [];

    const lists = app.lists();
    for (const list of lists) {
        const listName = list.name();
        const reminders = list.reminders();
        for (const r of reminders) {
            try {
                const completed = r.completed();
                const completionDate = r.completionDate();

                // Skip completed reminders older than 30 days
                if (completed && completionDate && completionDate < thirtyDaysAgo) {
                    continue;
                }

                const obj = {
                    name: r.name() || "",
                    body: r.body() || "",
                    list: listName,
                    completed: completed,
                    priority: r.priority() || 0,
                };

                const dueDate = r.dueDate();
                if (dueDate) {
                    obj.due_date = dueDate.toISOString();
                }

                const creationDate = r.creationDate();
                if (creationDate) {
                    obj.creation_date = creationDate.toISOString();
                }

                if (completed && completionDate) {
                    obj.completion_date = completionDate.toISOString();
                }

                results.push(obj);
            } catch (e) {
                // Skip problematic reminders
            }
        }
    }

    return JSON.stringify(results);
})()
"""


def _dedup_key(name: str, list_name: str) -> str:
    """Generate a deterministic dedup key from reminder name + list."""
    raw = f"{name.strip().lower()}|{list_name.strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def fetch_reminders() -> list[dict]:
    """Extract reminders from Apple Reminders via osascript JXA."""
    try:
        result = subprocess.run(
            ["osascript", "-l", "JavaScript", "-e", JXA_SCRIPT],
            capture_output=True,
            text=True,
            timeout=90,
        )
    except subprocess.TimeoutExpired:
        print("ERROR: osascript timed out after 90s.")
        print("Reminders.app may need a restart. Try:")
        print("  killall Reminders")
        print("  open -a Reminders")
        print("Then re-run this script.")
        return []

    if result.returncode != 0:
        print(f"ERROR: osascript failed: {result.stderr}")
        return []

    raw = result.stdout.strip()
    if not raw:
        print("No reminders found.")
        return []

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Failed to parse JSON: {exc}")
        return []


def _format_priority(p: int) -> str:
    if p == 0:
        return ""
    if p <= 4:
        return " [HIGH]"
    if p <= 7:
        return " [MEDIUM]"
    return " [LOW]"


def _format_reminder_content(r: dict) -> str:
    """Format a single reminder into readable content."""
    parts = [r["name"]]
    prio = _format_priority(r.get("priority", 0))
    if prio:
        parts[0] += prio

    if r.get("due_date"):
        try:
            dt = datetime.fromisoformat(r["due_date"].replace("Z", "+00:00"))
            parts.append(f"Due: {dt.strftime('%Y-%m-%d %I:%M %p')}")
        except (ValueError, TypeError):
            parts.append(f"Due: {r['due_date']}")

    parts.append(f"List: {r['list']}")

    if r.get("body"):
        parts.append(f"Notes: {r['body']}")

    return " | ".join(parts)


def _topics_from_list(list_name: str) -> list[str]:
    """Derive topic tags from the reminder list name."""
    name_lower = list_name.lower()
    topics = ["reminders"]

    mapping = {
        "work": ["work"],
        "personal": ["personal"],
        "shopping": ["shopping", "personal"],
        "groceries": ["shopping", "personal"],
        "oracle": ["oracle_health", "work"],
        "alex": ["alex_recruiting", "work"],
        "jacob": ["family", "jacob"],
        "family": ["family"],
        "health": ["health"],
        "fitness": ["health", "fitness"],
        "home": ["home", "personal"],
        "susan": ["susan", "work"],
        "jake": ["jake", "work"],
    }

    for key, tags in mapping.items():
        if key in name_lower:
            topics.extend(tags)
            break

    return list(set(topics))


def ingest_reminders(dry_run: bool = False, include_completed: bool = False):
    print("Fetching reminders from Apple Reminders.app...")
    reminders = fetch_reminders()

    incomplete = [r for r in reminders if not r.get("completed")]
    completed = [r for r in reminders if r.get("completed")]

    print(f"Total reminders fetched: {len(reminders)}")
    print(f"  Incomplete: {len(incomplete)}")
    print(f"  Completed (last 30 days): {len(completed)}")
    print()

    if dry_run:
        print("=== INCOMPLETE (would store as semantic) ===")
        for r in incomplete:
            print(f"  {_format_reminder_content(r)}")
        if include_completed:
            print(f"\n=== COMPLETED (would store as episodic) ===")
            for r in completed:
                print(f"  [DONE] {_format_reminder_content(r)}")
        print(f"\n[DRY RUN] Would ingest {len(incomplete)} incomplete"
              f"{f' + {len(completed)} completed' if include_completed else ''}. Exiting.")
        return

    store = BrainStore()
    stats = {"semantic": 0, "episodic": 0, "skipped_dupe": 0}

    # Check existing reminders for deduplication
    existing_sources = set()
    try:
        existing_semantic = (
            store.supabase.table("jake_semantic")
            .select("id, metadata")
            .eq("category", "task")
            .execute()
        )
        for row in existing_semantic.data or []:
            meta = row.get("metadata") or {}
            dk = meta.get("dedup_key")
            if dk:
                existing_sources.add(dk)

        existing_episodic = (
            store.supabase.table("jake_episodic")
            .select("id, metadata")
            .eq("source", "apple_reminders")
            .execute()
        )
        for row in existing_episodic.data or []:
            meta = row.get("metadata") or {}
            dk = meta.get("dedup_key")
            if dk:
                existing_sources.add(dk)
    except Exception as exc:
        print(f"  Warning: could not check existing records: {exc}")

    print(f"Existing dedup keys found: {len(existing_sources)}")
    print()

    # --- Incomplete reminders → semantic memories (tasks) ---
    for r in incomplete:
        dk = _dedup_key(r["name"], r["list"])
        if dk in existing_sources:
            stats["skipped_dupe"] += 1
            continue

        content = _format_reminder_content(r)
        topics = _topics_from_list(r["list"])

        try:
            store.store_semantic(
                content=content,
                category="task",
                confidence=0.95,
                source_episodes=[],
                project=None,
                topics=topics,
                metadata={
                    "source": "apple_reminders",
                    "dedup_key": dk,
                    "list": r["list"],
                    "due_date": r.get("due_date"),
                    "priority": r.get("priority", 0),
                },
            )
            print(f"  [SEMANTIC] {content[:80]}")
            stats["semantic"] += 1
            existing_sources.add(dk)
        except Exception as exc:
            print(f"  Failed: {r['name']} — {exc}")

    # --- Completed reminders → episodic memories ---
    if include_completed:
        for r in completed:
            dk = _dedup_key(r["name"], r["list"])
            if dk in existing_sources:
                stats["skipped_dupe"] += 1
                continue

            content = f"Completed task: {r['name']} (list: {r['list']})"
            if r.get("body"):
                content += f" — {r['body']}"

            completion_date = r.get("completion_date")
            try:
                occurred = (
                    datetime.fromisoformat(completion_date.replace("Z", "+00:00"))
                    if completion_date
                    else datetime.now(timezone.utc)
                )
            except (ValueError, TypeError):
                occurred = datetime.now(timezone.utc)

            topics = _topics_from_list(r["list"])

            try:
                store.store_episodic(
                    content=content,
                    occurred_at=occurred,
                    memory_type="task_completed",
                    project=None,
                    importance=0.4,
                    people=[],
                    topics=topics,
                    session_id=None,
                    source="apple_reminders",
                    source_type="reminders",
                    metadata={
                        "dedup_key": dk,
                        "list": r["list"],
                        "priority": r.get("priority", 0),
                    },
                )
                print(f"  [EPISODIC] {content[:80]}")
                stats["episodic"] += 1
                existing_sources.add(dk)
            except Exception as exc:
                print(f"  Failed: {r['name']} — {exc}")

    # --- Summary of open tasks grouped by list ---
    if incomplete:
        by_list: dict[str, list[str]] = {}
        for r in incomplete:
            by_list.setdefault(r["list"], []).append(_format_reminder_content(r))

        summary_parts = ["Mike's open Apple Reminders:\n"]
        for list_name in sorted(by_list.keys()):
            summary_parts.append(f"## {list_name}")
            for item in by_list[list_name]:
                summary_parts.append(f"- {item}")
            summary_parts.append("")

        summary_content = "\n".join(summary_parts)

        # Check for existing summary
        summary_dk = "reminders_open_summary"
        try:
            existing_summary = (
                store.supabase.table("jake_semantic")
                .select("id")
                .eq("category", "task_summary")
                .execute()
            )
            # Delete old summary if exists, then insert fresh
            if existing_summary.data:
                for row in existing_summary.data:
                    store.supabase.table("jake_semantic").delete().eq("id", row["id"]).execute()
                print("  Replaced existing task summary")

            store.store_semantic(
                content=summary_content,
                category="task_summary",
                confidence=0.95,
                source_episodes=[],
                project=None,
                topics=["reminders", "tasks", "summary"],
                metadata={
                    "source": "apple_reminders",
                    "dedup_key": summary_dk,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            stats["semantic"] += 1
            print(f"  [SEMANTIC] Open tasks summary ({len(incomplete)} items across {len(by_list)} lists)")
        except Exception as exc:
            print(f"  Failed to store summary: {exc}")

    print(f"\n{'=' * 60}")
    print(f"Reminders Ingestion Complete")
    print(f"  Semantic memories (tasks): {stats['semantic']}")
    print(f"  Episodic memories (done):  {stats['episodic']}")
    print(f"  Skipped (duplicates):      {stats['skipped_dupe']}")
    print(f"{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(description="Ingest Apple Reminders into Jake's Brain")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to brain")
    parser.add_argument("--include-completed", action="store_true", help="Also ingest completed reminders from last 30 days")
    args = parser.parse_args()
    ingest_reminders(dry_run=args.dry_run, include_completed=args.include_completed)


if __name__ == "__main__":
    main()
