#!/usr/bin/env python3
"""Ingest Claude Code session conversations into Jake's Brain.

Scans ~/.claude/projects/ for .jsonl session files, extracts user messages
and assistant text responses, chunks them, and feeds through the Brain pipeline.

Usage:
    cd susan-team-architect/backend && source .venv/bin/activate
    python scripts/brain_claude_code_ingest.py [--dry-run] [--limit N] [--project NAME]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

PROJECTS_DIR = Path.home() / ".claude" / "projects"

# Minimum chunk length to bother ingesting
MIN_CHUNK_LEN = 50
# Target chunk size range
CHUNK_MIN = 200
CHUNK_MAX = 1500


def content_hash(text: str) -> str:
    """SHA256 hash of text for deduplication."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def dir_to_project_name(dirname: str) -> str:
    """Convert a Claude Code project directory name to a readable project name.

    E.g. '-Users-mikerodgers-Startup-Intelligence-OS' -> 'Startup-Intelligence-OS'
    """
    # Strip leading dash and path prefix
    parts = dirname.strip("-").split("-")

    # Find the interesting part (skip Users, mikerodgers, Desktop, Dev-Projects, etc.)
    skip = {"Users", "mikerodgers", "Desktop", "Dev", "Projects"}
    meaningful = []
    found_meaningful = False
    for part in parts:
        if part in skip and not found_meaningful:
            continue
        found_meaningful = True
        meaningful.append(part)

    if meaningful:
        return "-".join(meaningful)
    return dirname


def extract_text_from_message(message: object) -> str:
    """Extract text content from a Claude Code message object.

    Messages can be:
    - A string
    - A dict with 'content' that is a string
    - A dict with 'content' that is a list of content blocks
    """
    if isinstance(message, str):
        return message

    if isinstance(message, dict):
        content = message.get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text_parts = []
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    # Skip tool_use, tool_result, thinking blocks
                elif isinstance(block, str):
                    text_parts.append(block)
            return " ".join(text_parts)

    return ""


def parse_session_file(filepath: Path, project_name: str) -> list[dict]:
    """Parse a Claude Code .jsonl session file into conversation chunks.

    Line types:
    - type: "queue-operation" with operation: "enqueue" — user messages
    - type: "user" — user messages (including tool results, skip those)
    - type: "assistant" — assistant responses (may contain tool_use, thinking, text)
    - type: "progress" — skip
    """
    try:
        lines = filepath.read_text().strip().splitlines()
    except OSError as exc:
        print(f"  SKIP {filepath.name}: {exc}")
        return []

    if not lines:
        return []

    session_id = filepath.stem
    session_date = ""

    chunks = []
    current_chunk = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        entry_type = entry.get("type", "")

        # Extract user messages from queue-operation enqueue events
        if entry_type == "queue-operation" and entry.get("operation") == "enqueue":
            content = entry.get("content", "")
            if isinstance(content, str) and content.strip():
                # Skip task notifications and XML-heavy messages
                if content.strip().startswith("<task-notification"):
                    continue
                # Get timestamp if available
                ts = entry.get("timestamp")
                if ts and not session_date:
                    try:
                        ts_num = float(ts) if isinstance(ts, str) else ts
                        session_date = datetime.fromtimestamp(
                            ts_num / 1000 if ts_num > 1e12 else ts_num, tz=timezone.utc
                        ).isoformat()
                    except (ValueError, OSError, TypeError):
                        pass

                addition = "User: " + content.strip() + "\n"
                if current_chunk and len(current_chunk) + len(addition) > CHUNK_MAX:
                    chunks.append({
                        "content": current_chunk.strip(),
                        "session_id": session_id,
                        "occurred_at": session_date,
                    })
                    current_chunk = ""
                current_chunk += addition
            continue

        # Extract assistant text responses (skip tool_use and thinking)
        if entry_type == "assistant":
            text = extract_text_from_message(entry.get("message", {}))
            if not text.strip():
                continue

            # Skip very short assistant responses (usually just acknowledgments)
            if len(text.strip()) < 20:
                continue

            # Truncate very long assistant responses (code dumps, etc.)
            if len(text) > 2000:
                text = text[:2000] + "..."

            addition = "Assistant: " + text.strip() + "\n"
            if current_chunk and len(current_chunk) + len(addition) > CHUNK_MAX:
                chunks.append({
                    "content": current_chunk.strip(),
                    "session_id": session_id,
                    "occurred_at": session_date,
                })
                current_chunk = ""
            current_chunk += addition

            # Flush after assistant response if chunk is big enough
            if len(current_chunk) >= CHUNK_MIN:
                chunks.append({
                    "content": current_chunk.strip(),
                    "session_id": session_id,
                    "occurred_at": session_date,
                })
                current_chunk = ""
            continue

        # Skip: progress, user (tool results), tool_use, tool_result, etc.

    # Flush remainder
    if current_chunk.strip() and len(current_chunk.strip()) >= MIN_CHUNK_LEN:
        chunks.append({
            "content": current_chunk.strip(),
            "session_id": session_id,
            "occurred_at": session_date or datetime.now(timezone.utc).isoformat(),
        })

    # Backfill date if we didn't find one
    if not session_date:
        try:
            session_date = datetime.fromtimestamp(
                filepath.stat().st_mtime, tz=timezone.utc
            ).isoformat()
        except OSError:
            session_date = datetime.now(timezone.utc).isoformat()

        for chunk in chunks:
            if not chunk["occurred_at"]:
                chunk["occurred_at"] = session_date

    return chunks


def gather_projects(project_filter: str | None = None) -> list[tuple[Path, str]]:
    """Gather all project directories with their readable names.

    Returns list of (project_dir, project_name) tuples.
    """
    if not PROJECTS_DIR.is_dir():
        print(f"Claude Code projects directory not found: {PROJECTS_DIR}")
        return []

    projects = []
    for d in sorted(PROJECTS_DIR.iterdir()):
        if not d.is_dir():
            continue
        name = dir_to_project_name(d.name)

        if project_filter and project_filter.lower() not in name.lower():
            continue

        projects.append((d, name))

    return projects


def gather_session_files(
    project_dir: Path, limit: int | None = None
) -> list[Path]:
    """Find all .jsonl session files in a project directory, sorted newest first."""
    files = sorted(
        project_dir.glob("*.jsonl"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    if limit:
        files = files[:limit]
    return files


def main():
    parser = argparse.ArgumentParser(
        description="Ingest Claude Code session conversations into Jake's Brain"
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be ingested without doing it")
    parser.add_argument("--limit", type=int, default=None, help="Only process N most recent sessions per project")
    parser.add_argument("--project", type=str, default=None, help="Filter to sessions from a specific project (substring match)")
    args = parser.parse_args()

    print("=" * 60)
    print("Jake Brain — Claude Code Session Ingestion")
    print(f"Scanning: {PROJECTS_DIR}")
    print("=" * 60)

    projects = gather_projects(project_filter=args.project)
    if not projects:
        print("No project directories found.")
        return

    print(f"\nFound {len(projects)} project(s):")
    for _, name in projects:
        print(f"  - {name}")

    # Parse all sessions into chunks
    all_chunks = []
    seen_hashes: set[str] = set()
    total_sessions = 0
    project_stats: dict[str, int] = {}

    for project_dir, project_name in projects:
        session_files = gather_session_files(project_dir, limit=args.limit)
        if not session_files:
            continue

        print(f"\n  {project_name}: {len(session_files)} session file(s)")
        project_chunks = 0

        for filepath in session_files:
            chunks = parse_session_file(filepath, project_name)
            if not chunks:
                continue

            total_sessions += 1
            for chunk in chunks:
                if len(chunk["content"]) < MIN_CHUNK_LEN:
                    continue
                h = content_hash(chunk["content"])
                if h in seen_hashes:
                    continue
                seen_hashes.add(h)

                # Prefix with source context
                chunk["content"] = (
                    f"Claude Code conversation ({project_name}, "
                    f"{chunk.get('occurred_at', 'unknown date')}): "
                    + chunk["content"]
                )
                chunk["project_name"] = project_name
                all_chunks.append(chunk)
                project_chunks += 1

        project_stats[project_name] = project_chunks

    print(f"\nSessions parsed: {total_sessions}")
    print(f"Unique chunks to ingest: {len(all_chunks)}")
    for proj, count in sorted(project_stats.items()):
        print(f"  {proj}: {count} chunks")

    if not all_chunks:
        print("No conversation chunks found.")
        return

    if args.dry_run:
        print(f"\n[DRY RUN] Would ingest {len(all_chunks)} chunks. Previewing first 10:\n")
        for i, chunk in enumerate(all_chunks[:10], 1):
            preview = chunk["content"][:120].replace("\n", " ")
            print(f"  {i}. [{len(chunk['content'])} chars] {preview}...")
        if len(all_chunks) > 10:
            print(f"  ... and {len(all_chunks) - 10} more")
        return

    # Ingest
    from jake_brain.pipeline import BrainPipeline

    print(f"\nIngesting {len(all_chunks)} chunks into Jake's Brain...")
    pipeline = BrainPipeline()

    results = {"success": 0, "failed": 0, "people": set(), "topics": set()}

    for i, chunk in enumerate(all_chunks, 1):
        try:
            result = pipeline.ingest_conversation(
                text=chunk["content"],
                session_id=chunk.get("session_id", "claude-code-unknown"),
                source=f"claude-code:{chunk.get('project_name', 'unknown')}:{chunk.get('session_id', 'unknown')}",
                source_type="claude-code",
                occurred_at=chunk.get("occurred_at"),
            )
            extraction = result.get("extraction", {})
            results["success"] += 1
            results["people"].update(extraction.get("people", []))
            results["topics"].update(extraction.get("topics", []))

            if i % 20 == 0 or i == len(all_chunks):
                print(f"  [{i}/{len(all_chunks)}] Ingested — "
                      f"people so far: {len(results['people'])}, "
                      f"topics so far: {len(results['topics'])}")
        except Exception as exc:
            results["failed"] += 1
            print(f"  [{i}/{len(all_chunks)}] FAILED — {exc}")

    print(f"\n{'=' * 60}")
    print("Claude Code Ingestion Complete")
    print(f"  Sessions processed: {total_sessions}")
    print(f"  Chunks ingested:    {results['success']}")
    print(f"  Chunks failed:      {results['failed']}")
    print(f"  People discovered:  {sorted(results['people'])}")
    print(f"  Topics discovered:  {sorted(results['topics'])}")
    print(f"{'=' * 60}")

    # Show updated brain stats
    try:
        stats = pipeline.stats()
        print(f"\nBrain Stats After Ingestion:")
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
