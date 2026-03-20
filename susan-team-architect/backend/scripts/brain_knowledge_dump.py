#!/usr/bin/env python3
"""One-time knowledge dump: Feed all Claude Code memory files into Jake's Brain.

This script reads every memory file across all Claude Code projects and ingests
them into Jake's 4-layer cognitive memory engine. The result is that Hermes Jake
and Claude Code Jake share the same knowledge base.

Usage:
    cd susan-team-architect/backend && source .venv/bin/activate
    python scripts/brain_knowledge_dump.py [--dry-run]
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from jake_brain.pipeline import BrainPipeline


# All known Claude Code project memory directories
MEMORY_DIRS = [
    Path.home() / ".claude/projects" / d / "memory"
    for d in [
        "-Users-mikerodgers-Startup-Intelligence-OS",
        "-Users-mikerodgers-Desktop-alex-recruiting-project-alex-recruiting",
        "-Users-mikerodgers-Desktop-Dev-Projects-alex-recruiting-project-alex-recruiting",
        "-Users-mikerodgers-Desktop-james-os",
        "-Users-mikerodgers-Desktop-Dev-Projects-james-os",
        "-Users-mikerodgers-Desktop-oracle-health-ai-enablement",
        "-Users-mikerodgers-Desktop-Oracle-Work-oracle-health-ai-enablement",
        "-Users-mikerodgers-Desktop-intelligence-operating-system",
        "-Users-mikerodgers-Desktop-viral-architect-hub",
        "-Users-mikerodgers-Desktop-adapt-evolve-progress",
    ]
]

# Also ingest key handoff and plan files
EXTRA_FILES = [
    Path.home() / "Startup-Intelligence-OS/HANDOFF.md",
    Path.home() / ".claude/plans/2026-03-18-v1-v5-roadmap.md",
    Path.home() / ".claude/plans/2026-03-18-25x-command-center-design.md",
]


def gather_memory_files() -> list[dict]:
    """Collect all memory .md files across all projects."""
    chunks = []
    seen_content = set()  # deduplicate by content hash

    for mem_dir in MEMORY_DIRS:
        if not mem_dir.is_dir():
            continue
        for md_file in sorted(mem_dir.glob("*.md")):
            if md_file.name == "MEMORY.md":
                continue  # index file, skip
            content = md_file.read_text().strip()
            if not content or len(content) < 20:
                continue
            # Deduplicate (same file might exist in multiple project dirs)
            content_hash = hash(content[:500])
            if content_hash in seen_content:
                continue
            seen_content.add(content_hash)

            # Determine source project from path
            project_dir = md_file.parent.parent.name
            project = "unknown"
            if "startup" in project_dir.lower() or "intelligence" in project_dir.lower():
                project = "startup-os"
            elif "alex-recruiting" in project_dir.lower():
                project = "alex-recruiting"
            elif "james-os" in project_dir.lower():
                project = "james-os"
            elif "oracle" in project_dir.lower():
                project = "oracle-health"
            elif "viral" in project_dir.lower():
                project = "startup-os"
            elif "adapt-evolve" in project_dir.lower():
                project = "startup-os"

            chunks.append({
                "content": f"[Source: {md_file.name} from {project}]\n\n{content}",
                "source_file": str(md_file),
                "project": project,
                "occurred_at": datetime.fromtimestamp(
                    md_file.stat().st_mtime, tz=timezone.utc
                ).isoformat(),
            })

    # Add extra files
    for extra in EXTRA_FILES:
        if extra.is_file():
            content = extra.read_text().strip()
            if content and len(content) > 50:
                content_hash = hash(content[:500])
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    chunks.append({
                        "content": f"[Source: {extra.name}]\n\n{content}",
                        "source_file": str(extra),
                        "project": "startup-os",
                        "occurred_at": datetime.fromtimestamp(
                            extra.stat().st_mtime, tz=timezone.utc
                        ).isoformat(),
                    })

    return chunks


def main():
    parser = argparse.ArgumentParser(description="Dump Claude Code knowledge into Jake's Brain")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be ingested without doing it")
    args = parser.parse_args()

    print("=" * 60)
    print("Jake Brain — Knowledge Dump")
    print("Collecting all Claude Code memory files...")
    print("=" * 60)

    chunks = gather_memory_files()
    print(f"\nFound {len(chunks)} unique memory chunks to ingest:\n")

    for i, chunk in enumerate(chunks, 1):
        content_preview = chunk["content"][:80].replace("\n", " ")
        print(f"  {i:2d}. {chunk['source_file'].split('/')[-1]:40s} ({chunk['project']:15s}) {content_preview}...")

    if args.dry_run:
        print(f"\n[DRY RUN] Would ingest {len(chunks)} chunks. Exiting.")
        return

    print(f"\nIngesting {len(chunks)} chunks into Jake's Brain...")
    pipeline = BrainPipeline()

    results = {"success": 0, "failed": 0, "people": set(), "topics": set()}

    for i, chunk in enumerate(chunks, 1):
        try:
            result = pipeline.ingest_conversation(
                text=chunk["content"],
                session_id="knowledge-dump-2026-03-20",
                source=f"claude-code-memory:{chunk['source_file'].split('/')[-1]}",
                source_type="ingestion",
                occurred_at=chunk["occurred_at"],
            )
            extraction = result.get("extraction", {})
            results["success"] += 1
            results["people"].update(extraction.get("people", []))
            results["topics"].update(extraction.get("topics", []))
            print(f"  [{i}/{len(chunks)}] OK — people={extraction.get('people', [])}, "
                  f"topics={extraction.get('topics', [])}, "
                  f"importance={extraction.get('importance', 0):.2f}")
        except Exception as exc:
            results["failed"] += 1
            print(f"  [{i}/{len(chunks)}] FAILED — {exc}")

    print(f"\n{'=' * 60}")
    print(f"Knowledge Dump Complete")
    print(f"  Success: {results['success']}")
    print(f"  Failed:  {results['failed']}")
    print(f"  People discovered:  {sorted(results['people'])}")
    print(f"  Topics discovered:  {sorted(results['topics'])}")
    print(f"{'=' * 60}")

    # Show updated brain stats
    try:
        stats = pipeline.stats()
        print(f"\nBrain Stats After Dump:")
        for key, val in stats.items():
            print(f"  {key}: {val}")
    except Exception as exc:
        print(f"\nCouldn't get brain stats: {exc}")


if __name__ == "__main__":
    main()
