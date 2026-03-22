#!/usr/bin/env python3
"""Ingest Hermes session conversations into Jake's Brain.

Scans ~/.hermes/sessions/ for .json and .jsonl session files, extracts
conversation content, chunks it, and feeds it through the Brain pipeline.

Usage:
    cd susan-team-architect/backend && source .venv/bin/activate
    python scripts/brain_hermes_ingest.py [--dry-run] [--limit N]
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

SESSIONS_DIR = Path.home() / ".hermes" / "sessions"

# Minimum chunk length to bother ingesting
MIN_CHUNK_LEN = 50
# Target chunk size range
CHUNK_MIN = 200
CHUNK_MAX = 1500


def content_hash(text: str) -> str:
    """SHA256 hash of text for deduplication."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def parse_json_session(filepath: Path) -> list[dict]:
    """Parse a Hermes .json session file into conversation chunks.

    Format: {"session_id": "...", "model": "...", "messages": [{"role": "user/assistant", "content": "..."}]}
    """
    try:
        data = json.loads(filepath.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        print(f"  SKIP {filepath.name}: {exc}")
        return []

    session_id = data.get("session_id", filepath.stem)
    messages = data.get("messages", [])
    if not messages:
        return []

    # Extract date from filename or session data
    session_date = data.get("session_start", "")
    if not session_date:
        # Try to parse from filename like session_20260319_124142_ecd37d.json
        parts = filepath.stem.split("_")
        if len(parts) >= 3 and parts[1].isdigit():
            try:
                session_date = datetime.strptime(
                    f"{parts[1]}_{parts[2]}", "%Y%m%d_%H%M%S"
                ).replace(tzinfo=timezone.utc).isoformat()
            except ValueError:
                session_date = datetime.now(timezone.utc).isoformat()

    # Combine sequential user+assistant pairs into chunks
    chunks = []
    current_chunk = ""

    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if not isinstance(content, str):
            content = str(content) if content else ""

        if role not in ("user", "assistant"):
            continue
        if not content.strip():
            continue

        prefix = "User: " if role == "user" else "Assistant: "
        addition = prefix + content.strip() + "\n"

        # If adding this would exceed max, flush current chunk
        if current_chunk and len(current_chunk) + len(addition) > CHUNK_MAX:
            chunks.append({
                "content": current_chunk.strip(),
                "session_id": session_id,
                "occurred_at": session_date,
            })
            current_chunk = ""

        current_chunk += addition

        # If we have a user+assistant pair and it's big enough, flush
        if role == "assistant" and len(current_chunk) >= CHUNK_MIN:
            chunks.append({
                "content": current_chunk.strip(),
                "session_id": session_id,
                "occurred_at": session_date,
            })
            current_chunk = ""

    # Flush remainder
    if current_chunk.strip() and len(current_chunk.strip()) >= MIN_CHUNK_LEN:
        chunks.append({
            "content": current_chunk.strip(),
            "session_id": session_id,
            "occurred_at": session_date,
        })

    return chunks


def parse_jsonl_session(filepath: Path) -> list[dict]:
    """Parse a Hermes .jsonl session file into conversation chunks.

    Format: First line has role: "session_meta", rest are conversation entries.
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

    # Try to parse date from filename like 20260320_050825_8f761124.jsonl
    parts = filepath.stem.split("_")
    if len(parts) >= 2 and parts[0].isdigit():
        try:
            session_date = datetime.strptime(
                f"{parts[0]}_{parts[1]}", "%Y%m%d_%H%M%S"
            ).replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            pass

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

        role = entry.get("role", "")

        # Skip session_meta and tool-related entries
        if role == "session_meta":
            session_id = entry.get("session_id", session_id)
            if entry.get("session_start"):
                session_date = entry["session_start"]
            continue
        if role in ("tool", "system", "function"):
            continue

        content = entry.get("content", "")
        if not isinstance(content, str):
            # Could be a list of content blocks
            if isinstance(content, list):
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    elif isinstance(block, str):
                        text_parts.append(block)
                content = " ".join(text_parts)
            else:
                content = str(content) if content else ""

        if not content.strip():
            continue

        if role in ("user", "assistant"):
            prefix = "User: " if role == "user" else "Assistant: "
            addition = prefix + content.strip() + "\n"

            if current_chunk and len(current_chunk) + len(addition) > CHUNK_MAX:
                chunks.append({
                    "content": current_chunk.strip(),
                    "session_id": session_id,
                    "occurred_at": session_date or datetime.now(timezone.utc).isoformat(),
                })
                current_chunk = ""

            current_chunk += addition

            if role == "assistant" and len(current_chunk) >= CHUNK_MIN:
                chunks.append({
                    "content": current_chunk.strip(),
                    "session_id": session_id,
                    "occurred_at": session_date or datetime.now(timezone.utc).isoformat(),
                })
                current_chunk = ""

    if current_chunk.strip() and len(current_chunk.strip()) >= MIN_CHUNK_LEN:
        chunks.append({
            "content": current_chunk.strip(),
            "session_id": session_id,
            "occurred_at": session_date or datetime.now(timezone.utc).isoformat(),
        })

    return chunks


def gather_sessions(limit: int | None = None) -> list[tuple[Path, str]]:
    """Gather all session files, sorted by modification time (newest first).

    Returns list of (filepath, format) tuples.
    """
    if not SESSIONS_DIR.is_dir():
        print(f"Hermes sessions directory not found: {SESSIONS_DIR}")
        return []

    files = []
    for f in SESSIONS_DIR.iterdir():
        if f.suffix == ".json" and f.name.startswith("session_"):
            files.append((f, "json"))
        elif f.suffix == ".jsonl":
            files.append((f, "jsonl"))

    # Sort by mtime descending (newest first)
    files.sort(key=lambda x: x[0].stat().st_mtime, reverse=True)

    if limit:
        files = files[:limit]

    return files


def main():
    parser = argparse.ArgumentParser(
        description="Ingest Hermes session conversations into Jake's Brain"
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be ingested without doing it")
    parser.add_argument("--limit", type=int, default=None, help="Only process N most recent sessions")
    args = parser.parse_args()

    print("=" * 60)
    print("Jake Brain — Hermes Session Ingestion")
    print(f"Scanning: {SESSIONS_DIR}")
    print("=" * 60)

    session_files = gather_sessions(limit=args.limit)
    if not session_files:
        print("No session files found.")
        return

    print(f"\nFound {len(session_files)} session files to process.\n")

    # Parse all sessions into chunks
    all_chunks = []
    seen_hashes: set[str] = set()
    sessions_processed = 0

    for filepath, fmt in session_files:
        if fmt == "json":
            chunks = parse_json_session(filepath)
        else:
            chunks = parse_jsonl_session(filepath)

        if not chunks:
            continue

        sessions_processed += 1
        for chunk in chunks:
            if len(chunk["content"]) < MIN_CHUNK_LEN:
                continue
            h = content_hash(chunk["content"])
            if h in seen_hashes:
                continue
            seen_hashes.add(h)

            # Prefix with source context
            chunk["content"] = (
                f"Hermes conversation ({chunk.get('occurred_at', 'unknown date')}): "
                + chunk["content"]
            )
            all_chunks.append(chunk)

    print(f"Sessions parsed: {sessions_processed}")
    print(f"Unique chunks to ingest: {len(all_chunks)}")

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
                session_id=chunk.get("session_id", "hermes-unknown"),
                source=f"hermes-session:{chunk.get('session_id', 'unknown')}",
                source_type="hermes",
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
    print("Hermes Ingestion Complete")
    print(f"  Sessions processed: {sessions_processed}")
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
