#!/usr/bin/env python3
"""Ingest ChatGPT conversation exports into Jake's Brain.

Reads .txt files from data/chatgpt_conversations/, chunks them, and feeds
through the Brain pipeline for episodic/semantic/entity extraction.

Each .txt file should have a header block:
    Title: <conversation title>
    ID: <chatgpt conversation id>
    URL: <chatgpt url>
    Source: ChatGPT

Followed by the conversation text (USER: / ASSISTANT: blocks separated by ---).

Usage:
    cd susan-team-architect/backend && source .venv/bin/activate
    python scripts/brain_chatgpt_ingest.py [--dry-run] [--limit N] [--min-chars N]
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

CONVERSATIONS_DIR = Path(__file__).resolve().parent.parent / "data" / "chatgpt_conversations"

# Minimum chunk length to bother ingesting
MIN_CHUNK_LEN = 50
# Target chunk size range
CHUNK_MIN = 200
CHUNK_MAX = 1500


def content_hash(text: str) -> str:
    """SHA256 hash of text for deduplication."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def parse_conversation_file(filepath: Path) -> list[dict]:
    """Parse a ChatGPT conversation .txt file into chunks.

    Expected format:
    - Header lines: Title, ID, URL, Source
    - Blank line
    - Conversation body with USER: and ASSISTANT: blocks separated by ---
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"  SKIP {filepath.name}: {exc}")
        return []

    if not content.strip():
        return []

    # Parse header
    lines = content.split("\n")
    title = ""
    conv_id = ""
    url = ""

    header_end = 0
    for i, line in enumerate(lines):
        if line.startswith("Title: "):
            title = line[7:].strip()
        elif line.startswith("ID: "):
            conv_id = line[4:].strip()
        elif line.startswith("URL: "):
            url = line[5:].strip()
        elif line.startswith("Source: "):
            continue
        elif line.strip() == "" and i > 0:
            header_end = i + 1
            break

    if not title:
        title = filepath.stem.replace("_", " ")

    # Get conversation body
    body = "\n".join(lines[header_end:]).strip()
    if not body:
        return []

    # Split on --- separators (conversation turn boundaries)
    turns = re.split(r"\n-{3,}\n", body)

    chunks = []
    current_chunk = ""

    for turn in turns:
        turn = turn.strip()
        if not turn:
            continue

        # Skip very short turns (acknowledgments, etc.)
        if len(turn) < 20:
            continue

        # Truncate very long turns (massive code dumps, prompt engineering, etc.)
        if len(turn) > 2000:
            turn = turn[:2000] + "..."

        addition = turn + "\n"

        if current_chunk and len(current_chunk) + len(addition) > CHUNK_MAX:
            if len(current_chunk.strip()) >= MIN_CHUNK_LEN:
                chunks.append({
                    "content": current_chunk.strip(),
                    "title": title,
                    "conv_id": conv_id,
                    "url": url,
                })
            current_chunk = ""

        current_chunk += addition

        # Flush after each turn if chunk is big enough
        if len(current_chunk) >= CHUNK_MIN:
            chunks.append({
                "content": current_chunk.strip(),
                "title": title,
                "conv_id": conv_id,
                "url": url,
            })
            current_chunk = ""

    # Flush remainder
    if current_chunk.strip() and len(current_chunk.strip()) >= MIN_CHUNK_LEN:
        chunks.append({
            "content": current_chunk.strip(),
            "title": title,
            "conv_id": conv_id,
            "url": url,
        })

    return chunks


def gather_conversation_files(limit: int | None = None, min_chars: int = 100) -> list[Path]:
    """Find all .txt conversation files, sorted by size (largest first)."""
    if not CONVERSATIONS_DIR.is_dir():
        print(f"Conversations directory not found: {CONVERSATIONS_DIR}")
        return []

    files = sorted(
        [f for f in CONVERSATIONS_DIR.glob("*.txt") if f.stat().st_size >= min_chars],
        key=lambda f: f.stat().st_size,
        reverse=True,
    )
    if limit:
        files = files[:limit]
    return files


def main():
    parser = argparse.ArgumentParser(
        description="Ingest ChatGPT conversations into Jake's Brain"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be ingested without doing it",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Only process N largest conversation files",
    )
    parser.add_argument(
        "--min-chars", type=int, default=100,
        help="Skip files smaller than N characters (default: 100)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Jake Brain - ChatGPT Conversation Ingestion")
    print(f"Scanning: {CONVERSATIONS_DIR}")
    print("=" * 60)

    files = gather_conversation_files(limit=args.limit, min_chars=args.min_chars)
    if not files:
        print("No conversation files found.")
        return

    print(f"\nFound {len(files)} conversation file(s):")
    for f in files:
        print(f"  - {f.name} ({f.stat().st_size:,} bytes)")

    # Parse all files into chunks
    all_chunks: list[dict] = []
    seen_hashes: set[str] = set()
    file_stats: dict[str, int] = {}

    for filepath in files:
        chunks = parse_conversation_file(filepath)
        if not chunks:
            continue

        file_chunks = 0
        for chunk in chunks:
            if len(chunk["content"]) < MIN_CHUNK_LEN:
                continue

            h = content_hash(chunk["content"])
            if h in seen_hashes:
                continue
            seen_hashes.add(h)

            # Prefix with source context
            chunk["content"] = (
                f"ChatGPT conversation \"{chunk['title']}\": "
                + chunk["content"]
            )
            all_chunks.append(chunk)
            file_chunks += 1

        file_stats[filepath.name] = file_chunks

    print(f"\nFiles parsed: {len(file_stats)}")
    print(f"Unique chunks to ingest: {len(all_chunks)}")
    for fname, count in sorted(file_stats.items()):
        print(f"  {fname}: {count} chunks")

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
                session_id=chunk.get("conv_id", "chatgpt-unknown"),
                source=f"chatgpt:{chunk.get('title', 'unknown')}:{chunk.get('conv_id', 'unknown')}",
                source_type="ingestion",
                occurred_at=datetime.now(timezone.utc).isoformat(),
            )
            extraction = result.get("extraction", {})
            results["success"] += 1
            results["people"].update(extraction.get("people", []))
            results["topics"].update(extraction.get("topics", []))

            if i % 20 == 0 or i == len(all_chunks):
                print(
                    f"  [{i}/{len(all_chunks)}] Ingested - "
                    f"people so far: {len(results['people'])}, "
                    f"topics so far: {len(results['topics'])}"
                )
        except Exception as exc:
            results["failed"] += 1
            print(f"  [{i}/{len(all_chunks)}] FAILED - {exc}")

    print(f"\n{'=' * 60}")
    print("ChatGPT Ingestion Complete")
    print(f"  Files processed:    {len(file_stats)}")
    print(f"  Chunks ingested:    {results['success']}")
    print(f"  Chunks failed:      {results['failed']}")
    print(f"  People discovered:  {sorted(results['people'])}")
    print(f"  Topics discovered:  {sorted(results['topics'])}")
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
