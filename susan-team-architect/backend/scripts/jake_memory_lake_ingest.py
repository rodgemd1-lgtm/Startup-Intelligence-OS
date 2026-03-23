#!/usr/bin/env python3
"""Jake Memory Lake — bulk ingest of key knowledge directories into Jake's Brain.

Scans and ingests the following document types into jake_semantic:
  - docs/sops/          → procedural knowledge   (domain: devops / project-specific)
  - docs/battlecards/   → competitive intel       (domain: competitive-intel)
  - docs/plans/         → strategic plans          (domain: strategy)
  - docs/research/      → research findings        (domain: research)

Uses brain_doc_ingest.py under the hood but handles directory routing,
tagging, and incremental updates (skips already-ingested files by SHA256).

Usage:
    cd ~/Startup-Intelligence-OS/susan-team-architect/backend && source .venv/bin/activate
    python scripts/jake_memory_lake_ingest.py                        # Ingest all
    python scripts/jake_memory_lake_ingest.py --dir docs/sops        # One directory
    python scripts/jake_memory_lake_ingest.py --dry-run              # Preview
    python scripts/jake_memory_lake_ingest.py --force                # Re-ingest all (ignore dedup)
    python scripts/jake_memory_lake_ingest.py --since 2026-03-01     # Only files modified after date

Cron (via launchd, weekly on Sunday at 3 AM):
    ~/Library/LaunchAgents/com.jake.memory-lake.plist
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Path + env setup
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
REPO_ROOT = BACKEND_DIR.parent.parent  # ~/Startup-Intelligence-OS

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Load .env
env_file = Path.home() / ".hermes" / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

# ---------------------------------------------------------------------------
# Directory → metadata mapping
# ---------------------------------------------------------------------------
LAKE_DIRECTORIES = [
    {
        "path": REPO_ROOT / "docs" / "sops",
        "domain": "devops",
        "tags": ["sop", "process", "procedure"],
        "category": "sop",
        "description": "Standard Operating Procedures",
    },
    {
        "path": REPO_ROOT / "docs" / "battlecards",
        "domain": "competitive-intel",
        "tags": ["battlecard", "competitive", "intel"],
        "category": "battlecard",
        "description": "Competitive Intelligence Battlecards",
    },
    {
        "path": REPO_ROOT / "docs" / "plans",
        "domain": "strategy",
        "tags": ["plan", "strategy", "roadmap"],
        "category": "plan",
        "description": "Strategic Plans and Roadmaps",
    },
    {
        "path": REPO_ROOT / "docs" / "research",
        "domain": "research",
        "tags": ["research", "analysis", "findings"],
        "category": "research",
        "description": "Research Findings and Analysis",
    },
]

SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf", ".json", ".yaml", ".yml", ".csv"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def file_sha256(path: Path) -> str:
    """Compute SHA256 of a file for deduplication."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_files(directory: Path, since: datetime | None = None) -> list[Path]:
    """Recursively collect supported files, optionally filtered by mtime."""
    if not directory.exists():
        return []
    files = []
    for p in sorted(directory.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if since is not None:
            mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
            if mtime < since:
                continue
        files.append(p)
    return files


def run_ingest(
    filepath: Path,
    domain: str,
    tags: list[str],
    dry_run: bool = False,
) -> bool:
    """Call brain_doc_ingest.py for a single file."""
    cmd = [
        sys.executable,
        str(SCRIPT_DIR / "brain_doc_ingest.py"),
        str(filepath),
        "--project", domain,
        "--tags", ",".join(tags),
    ]
    if dry_run:
        cmd.append("--dry-run")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR ({filepath.name}): {result.stderr.strip()[:200]}")
        return False
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Jake Memory Lake — bulk ingest key knowledge dirs")
    parser.add_argument("--dir", metavar="PATH",
                        help="Ingest only this directory (relative or absolute)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview what would be ingested, no writes")
    parser.add_argument("--force", action="store_true",
                        help="Re-ingest even if file was previously ingested")
    parser.add_argument("--since", metavar="YYYY-MM-DD",
                        help="Only ingest files modified after this date")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show per-file detail")
    args = parser.parse_args()

    # Parse --since filter
    since_dt: datetime | None = None
    if args.since:
        try:
            since_dt = datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"Invalid --since date: {args.since}. Use YYYY-MM-DD.")
            sys.exit(1)

    # Determine which directories to process
    lake_dirs = LAKE_DIRECTORIES
    if args.dir:
        target = Path(args.dir).expanduser().resolve()
        lake_dirs = [d for d in LAKE_DIRECTORIES if d["path"].resolve() == target]
        if not lake_dirs:
            # Treat as a custom path with generic metadata
            lake_dirs = [{
                "path": target,
                "domain": "general",
                "tags": ["document"],
                "category": "document",
                "description": f"Custom: {target}",
            }]

    # Print header
    print("=" * 65)
    print("Jake Memory Lake — Bulk Knowledge Ingest")
    print(f"Time:      {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Dry run:   {args.dry_run}")
    print(f"Force:     {args.force}")
    if since_dt:
        print(f"Since:     {args.since}")
    print("=" * 65)

    # Track totals
    total_files = 0
    total_ok = 0
    total_skip = 0
    total_error = 0
    ingested_hashes: set[str] = set()

    for lake_dir in lake_dirs:
        dir_path = lake_dir["path"]
        domain = lake_dir["domain"]
        tags = lake_dir["tags"]
        description = lake_dir["description"]

        files = collect_files(dir_path, since=since_dt)

        if not files:
            print(f"\n{description}: (no files found in {dir_path})")
            continue

        print(f"\n{description} ({len(files)} files)")
        print(f"  Directory: {dir_path}")
        print(f"  Domain:    {domain} | Tags: {', '.join(tags)}")

        for filepath in files:
            total_files += 1

            # Deduplication check (unless --force)
            if not args.force:
                file_hash = file_sha256(filepath)
                if file_hash in ingested_hashes:
                    if args.verbose:
                        print(f"  SKIP (dup hash): {filepath.name}")
                    total_skip += 1
                    continue
                ingested_hashes.add(file_hash)

            if args.verbose or args.dry_run:
                print(f"  → {filepath.name}")

            success = run_ingest(filepath, domain=domain, tags=tags, dry_run=args.dry_run)
            if success:
                total_ok += 1
            else:
                total_error += 1

    # Summary
    print("\n" + "=" * 65)
    print("Memory Lake Ingest Complete")
    print(f"  Total files:  {total_files}")
    print(f"  Ingested:     {total_ok}")
    print(f"  Skipped:      {total_skip}")
    print(f"  Errors:       {total_error}")
    if args.dry_run:
        print("\n  [DRY RUN] No changes written.")
    print("=" * 65)


if __name__ == "__main__":
    main()
