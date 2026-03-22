#!/usr/bin/env python3
"""Ingest documents (PDF, Markdown, text, JSON, YAML, CSV) into Jake's Brain.

Reads files, chunks them into ~2000-char segments with 200-char overlap, deduplicates
by SHA256, and stores each chunk as a semantic memory via BrainStore.store_semantic().

Usage:
    cd susan-team-architect/backend && source .venv/bin/activate
    python scripts/brain_doc_ingest.py /path/to/file.md
    python scripts/brain_doc_ingest.py /path/to/dir --project oracle-health --tags research,strategy
    python scripts/brain_doc_ingest.py /path/to/file.pdf --dry-run
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Path + env setup (matches project convention)
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

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
SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf", ".json", ".yaml", ".yml", ".csv"}
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200
MIN_CHUNK_LEN = 40  # Skip tiny chunks


# ---------------------------------------------------------------------------
# File readers
# ---------------------------------------------------------------------------

def read_text_file(path: Path) -> str | None:
    """Read a plain-text file with encoding fallback."""
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except (UnicodeDecodeError, ValueError):
            continue
    return None


def read_pdf_file(path: Path) -> str | None:
    """Extract text from a PDF using pdftotext (poppler-utils)."""
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except FileNotFoundError:
        print(f"    SKIP (pdftotext not installed — brew install poppler)")
    except subprocess.TimeoutExpired:
        print(f"    SKIP (pdftotext timed out)")
    return None


def read_json_file(path: Path) -> str | None:
    """Read a JSON file and return pretty-printed text."""
    raw = read_text_file(path)
    if raw is None:
        return None
    try:
        data = json.loads(raw)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        return raw  # Return raw text if JSON is malformed


def read_csv_file(path: Path) -> str | None:
    """Read a CSV file and return a human-readable text representation."""
    raw = read_text_file(path)
    if raw is None:
        return None
    try:
        reader = csv.reader(io.StringIO(raw))
        rows = list(reader)
        if not rows:
            return None
        # Format: header row + data rows as "key: value" pairs
        header = rows[0]
        lines = []
        for i, row in enumerate(rows[1:], 1):
            parts = [f"{h}: {v}" for h, v in zip(header, row) if v.strip()]
            if parts:
                lines.append(f"Row {i}: {', '.join(parts)}")
        return "\n".join(lines) if lines else None
    except csv.Error:
        return raw


def read_yaml_file(path: Path) -> str | None:
    """Read a YAML file. Returns raw text (avoids pyyaml dependency)."""
    return read_text_file(path)


READERS: dict[str, callable] = {
    ".md": read_text_file,
    ".txt": read_text_file,
    ".pdf": read_pdf_file,
    ".json": read_json_file,
    ".yaml": read_yaml_file,
    ".yml": read_yaml_file,
    ".csv": read_csv_file,
}


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into chunks of ~chunk_size chars with overlap.

    Tries to break at paragraph or sentence boundaries when possible.
    """
    if len(text) <= chunk_size:
        return [text.strip()] if text.strip() else []

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end >= len(text):
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break

        # Try to find a good break point (paragraph > sentence > word)
        segment = text[start:end]
        break_at = None

        # Prefer paragraph break
        last_para = segment.rfind("\n\n")
        if last_para > chunk_size * 0.3:
            break_at = start + last_para + 2

        # Fall back to sentence break
        if break_at is None:
            for sep in (". ", ".\n", "! ", "? "):
                last_sent = segment.rfind(sep)
                if last_sent > chunk_size * 0.3:
                    candidate = start + last_sent + len(sep)
                    if break_at is None or candidate > break_at:
                        break_at = candidate

        # Fall back to word break
        if break_at is None:
            last_space = segment.rfind(" ")
            if last_space > chunk_size * 0.3:
                break_at = start + last_space + 1

        # Hard break as last resort
        if break_at is None:
            break_at = end

        chunk = text[start:break_at].strip()
        if chunk:
            chunks.append(chunk)

        # Advance with overlap
        start = max(start + 1, break_at - overlap)

    return chunks


def content_hash(text: str) -> str:
    """SHA256 hash of text content for deduplication."""
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def discover_files(target: Path) -> list[Path]:
    """Find all supported files at a path (single file or recursive directory)."""
    if target.is_file():
        if target.suffix.lower() in SUPPORTED_EXTENSIONS:
            return [target]
        else:
            print(f"  Unsupported extension: {target.suffix} (supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))})")
            return []

    if target.is_dir():
        files = []
        for ext in SUPPORTED_EXTENSIONS:
            files.extend(sorted(target.rglob(f"*{ext}")))
        # Also catch uppercase extensions
        for ext in SUPPORTED_EXTENSIONS:
            files.extend(sorted(target.rglob(f"*{ext.upper()}")))
        # Deduplicate (case-insensitive filesystems)
        seen = set()
        unique = []
        for f in files:
            resolved = f.resolve()
            if resolved not in seen:
                seen.add(resolved)
                unique.append(f)
        return sorted(unique)

    print(f"  Path does not exist: {target}")
    return []


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Ingest documents into Jake's Brain as semantic memory"
    )
    parser.add_argument(
        "path",
        type=str,
        help="File or directory to ingest (supports: .md, .txt, .pdf, .json, .yaml, .yml, .csv)",
    )
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Project/domain tag (e.g. oracle-health, alex-recruiting)",
    )
    parser.add_argument(
        "--tags",
        type=str,
        default=None,
        help="Comma-separated tags (e.g. research,strategy,meeting-notes)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be ingested without storing anything",
    )
    args = parser.parse_args()

    target = Path(args.path).expanduser().resolve()
    tag_list = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
    domain = args.project or "general"
    now_iso = datetime.now(timezone.utc).isoformat()

    print("=" * 60)
    print("Jake Brain — Document Ingestion")
    print(f"Target:  {target}")
    print(f"Project: {domain}")
    if tag_list:
        print(f"Tags:    {', '.join(tag_list)}")
    if args.dry_run:
        print("Mode:    DRY RUN")
    print("=" * 60)

    # Discover files
    files = discover_files(target)
    if not files:
        print("\nNo supported files found.")
        return

    print(f"\nFound {len(files)} file(s):")
    for f in files:
        print(f"  {f}")

    # Process all files into chunks
    all_chunks: list[dict] = []
    seen_hashes: set[str] = set()
    file_stats: dict[str, dict] = {}

    for filepath in files:
        fname = filepath.name
        ext = filepath.suffix.lower()
        reader = READERS.get(ext)

        if reader is None:
            print(f"\n  {fname}: unsupported extension, skipping")
            continue

        print(f"\n  Reading {fname}...")

        # Read content
        text = reader(filepath)
        if not text or not text.strip():
            print(f"    SKIP — empty or unreadable")
            file_stats[str(filepath)] = {"chunks_created": 0, "chunks_stored": 0, "skipped": "empty"}
            continue

        print(f"    Size: {len(text):,} chars")

        # Chunk
        chunks = chunk_text(text)
        chunks_created = len(chunks)
        chunks_stored = 0

        for idx, chunk_text_content in enumerate(chunks):
            if len(chunk_text_content) < MIN_CHUNK_LEN:
                continue

            c_hash = content_hash(chunk_text_content)

            # Deduplicate within this run
            if c_hash in seen_hashes:
                continue
            seen_hashes.add(c_hash)

            # Prefix chunk with document context
            prefixed_content = f"Document ({fname}, chunk {idx + 1}/{chunks_created}): {chunk_text_content}"

            all_chunks.append({
                "content": prefixed_content,
                "category": "document",
                "project": args.project,
                "topics": tag_list if tag_list else [],
                "metadata": {
                    "filename": fname,
                    "filepath": str(filepath),
                    "chunk_index": idx,
                    "total_chunks": chunks_created,
                    "content_hash": c_hash,
                    "tags": tag_list,
                    "file_extension": ext,
                    "ingested_at": now_iso,
                },
            })
            chunks_stored += 1

        print(f"    Chunks: {chunks_created} created, {chunks_stored} unique")
        file_stats[str(filepath)] = {
            "chunks_created": chunks_created,
            "chunks_stored": chunks_stored,
        }

    # Summary before ingestion
    print(f"\n{'=' * 60}")
    print(f"Files processed:  {len(file_stats)}")
    print(f"Total chunks:     {len(all_chunks)}")
    for fpath, stats in file_stats.items():
        name = Path(fpath).name
        if "skipped" in stats:
            print(f"  {name}: SKIPPED ({stats['skipped']})")
        else:
            print(f"  {name}: {stats['chunks_stored']} chunks")

    if not all_chunks:
        print("\nNo chunks to ingest.")
        return

    if args.dry_run:
        print(f"\n[DRY RUN] Would ingest {len(all_chunks)} chunks. Previewing first 10:\n")
        for i, chunk in enumerate(all_chunks[:10], 1):
            preview = chunk["content"][:120].replace("\n", " ")
            print(f"  {i}. [{chunk['metadata']['filename']:30s}] [{len(chunk['content']):5d} chars] {preview}...")
        if len(all_chunks) > 10:
            print(f"  ... and {len(all_chunks) - 10} more")
        return

    # Ingest via BrainStore.store_semantic()
    from jake_brain.store import BrainStore

    print(f"\nIngesting {len(all_chunks)} chunks into Jake's Brain (semantic layer)...")
    store = BrainStore()

    results = {"success": 0, "failed": 0, "errors": []}

    for i, chunk in enumerate(all_chunks, 1):
        try:
            store.store_semantic(
                content=chunk["content"],
                category="document",
                confidence=0.7,
                project=chunk["project"],
                topics=chunk["topics"],
                metadata=chunk["metadata"],
            )
            results["success"] += 1

            if i % 10 == 0 or i == len(all_chunks):
                print(f"  [{i}/{len(all_chunks)}] Stored ({results['success']} ok, {results['failed']} failed)")

        except Exception as exc:
            results["failed"] += 1
            err_msg = str(exc)[:100]
            results["errors"].append(f"{chunk['metadata']['filename']}[{chunk['metadata']['chunk_index']}]: {err_msg}")
            print(f"  [{i}/{len(all_chunks)}] FAILED — {err_msg}")

    # Final report
    print(f"\n{'=' * 60}")
    print("Document Ingestion Complete")
    print(f"  Files processed:   {len(file_stats)}")
    print(f"  Chunks stored:     {results['success']}")
    print(f"  Chunks failed:     {results['failed']}")
    print(f"  Domain:            {domain}")
    if tag_list:
        print(f"  Tags:              {', '.join(tag_list)}")
    print(f"{'=' * 60}")

    if results["errors"]:
        print(f"\nErrors ({len(results['errors'])}):")
        for err in results["errors"][:20]:
            print(f"  - {err}")
        if len(results["errors"]) > 20:
            print(f"  ... and {len(results['errors']) - 20} more")

    # Show updated brain stats
    try:
        stats = store.brain_stats()
        print(f"\nBrain Stats After Ingestion:")
        for key, val in stats.items():
            print(f"  {key}: {val}")
    except Exception as exc:
        print(f"\nCouldn't get brain stats: {exc}")


if __name__ == "__main__":
    main()
