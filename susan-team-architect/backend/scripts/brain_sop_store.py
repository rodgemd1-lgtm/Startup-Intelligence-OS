#!/usr/bin/env python3
"""Store a structured SOP in Jake's Brain as procedural memory.

Accepts SOP content via --content, --file, or --stdin and stores it in
the jake_procedural table with pattern_type='sop'.

Usage:
    cd susan-team-architect/backend && source .venv/bin/activate

    # Inline content
    python scripts/brain_sop_store.py \
        --title "Deploy Hermes Config" \
        --content "Step 1: Edit config.yaml ..." \
        --project hermes \
        --tags "deploy,hermes,config"

    # From a file
    python scripts/brain_sop_store.py \
        --title "Morning Triage" \
        --file /path/to/sop.md \
        --project oracle-health

    # From stdin (pipe)
    cat sop.md | python scripts/brain_sop_store.py \
        --title "Incident Response" \
        --stdin \
        --project devops \
        --tags "incident,oncall"
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Environment bootstrap (same pattern as brain_github_ingest.py)
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Store a structured SOP in Jake's Brain (jake_procedural)",
    )
    parser.add_argument(
        "--title",
        required=True,
        help="SOP title (e.g. 'Deploy Hermes Config')",
    )

    # Content source — exactly one of these three
    content_group = parser.add_mutually_exclusive_group(required=True)
    content_group.add_argument(
        "--content",
        help="SOP content as a string",
    )
    content_group.add_argument(
        "--file",
        type=Path,
        help="Path to a file containing the SOP content",
    )
    content_group.add_argument(
        "--stdin",
        action="store_true",
        help="Read SOP content from stdin",
    )

    parser.add_argument(
        "--project",
        default=None,
        help="Project or domain (e.g. hermes, oracle-health, startup-os, devops)",
    )
    parser.add_argument(
        "--tags",
        default="",
        help="Comma-separated tags (e.g. 'deploy,hermes,config')",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.9,
        help="Confidence score 0-1 (default 0.9 for direct SOP capture)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be stored without storing it",
    )

    args = parser.parse_args()

    # Resolve content
    if args.content:
        sop_text = args.content
    elif args.file:
        if not args.file.exists():
            print(f"ERROR: File not found: {args.file}")
            sys.exit(1)
        sop_text = args.file.read_text().strip()
    elif args.stdin:
        sop_text = sys.stdin.read().strip()
    else:
        print("ERROR: Provide --content, --file, or --stdin")
        sys.exit(1)

    if not sop_text:
        print("ERROR: SOP content is empty")
        sys.exit(1)

    # Parse tags
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
    now_iso = datetime.now(timezone.utc).isoformat()

    # Build metadata
    metadata = {
        "source_type": "sop",
        "title": args.title,
        "tags": tags,
        "captured_date": now_iso,
    }
    if args.project:
        metadata["project"] = args.project

    # Prepend title to content for better embedding context
    full_content = f"SOP: {args.title}\n\n{sop_text}"

    print("=" * 60)
    print("Jake Brain — SOP Store")
    print("=" * 60)
    print(f"  Title:      {args.title}")
    print(f"  Project:    {args.project or '(none)'}")
    print(f"  Tags:       {tags or '(none)'}")
    print(f"  Confidence: {args.confidence}")
    print(f"  Content:    {len(sop_text)} chars")
    print()

    if args.dry_run:
        print("[DRY RUN] Would store the following:\n")
        preview = full_content[:500]
        if len(full_content) > 500:
            preview += "\n... [truncated]"
        print(preview)
        print(f"\nMetadata: {metadata}")
        return

    # Store via BrainStore
    from jake_brain.store import BrainStore

    store = BrainStore()

    result = store.store_procedural(
        content=full_content,
        pattern_type="workflow",
        domain=args.project,
        confidence=args.confidence,
        approved=True,
        metadata=metadata,
    )

    record_id = result.get("id", "unknown")
    print(f"Stored SOP in jake_procedural.")
    print(f"  UUID: {record_id}")
    print(f"  pattern_type: workflow (source_type=sop in metadata)")
    print(f"  domain: {args.project or '(none)'}")
    print(f"  approved: True")
    print("=" * 60)


if __name__ == "__main__":
    main()
