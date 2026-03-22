#!/usr/bin/env python3
"""Ingest GitHub repo data into Jake's Brain.

Fetches README content, repo metadata, and recent commit messages from all repos
under the rodgemd1-lgtm GitHub org using the `gh` CLI and feeds them through the
Brain pipeline.

Usage:
    cd susan-team-architect/backend && source .venv/bin/activate
    python scripts/brain_github_ingest.py [--dry-run] [--limit N] [--repo NAME]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

GITHUB_ORG = "rodgemd1-lgtm"

# All 19 repos in the org (ordered by activity)
REPOS = [
    "Startup-Intelligence-OS",
    "alex-recruiting",
    "james-os",
    "adapt-evolve-progress",
    "oracle-health-ai-enablement",
    "viral-architect-hub",
    "gothic-reckoning",
    "founder-intelligence-os",
    "ux-design-scraper",
    "founder-command-center",
    "nextjs-boilerplate",
    "oracle-health-vendor-intelligence",
    "fitness-app-intelligence",
    "apex-ventures-hq",
    "transform-40-fit",
    "transform-fit-app",
    "ios-intelligence-engine",
    "viral-architect-backend",
    "tigerteam-ai",
]

# Commits per repo to fetch
COMMITS_PER_REPO = 50

# Minimum chunk length to bother ingesting
MIN_CHUNK_LEN = 50

# Max README length before truncation
MAX_README_LEN = 3000


def content_hash(text: str) -> str:
    """SHA256 hash of text for deduplication."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def gh_api(endpoint: str) -> dict | list | None:
    """Call the GitHub API via gh CLI and return parsed JSON."""
    try:
        result = subprocess.run(
            ["gh", "api", endpoint],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return None


def fetch_repo_metadata(repo: str) -> dict | None:
    """Fetch repo metadata (description, language, stars, topics, etc.)."""
    data = gh_api(f"/repos/{GITHUB_ORG}/{repo}")
    if not data:
        return None
    return {
        "name": data.get("name", repo),
        "full_name": data.get("full_name", f"{GITHUB_ORG}/{repo}"),
        "description": data.get("description") or "",
        "language": data.get("language") or "unknown",
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "topics": data.get("topics", []),
        "created_at": data.get("created_at", ""),
        "updated_at": data.get("updated_at", ""),
        "default_branch": data.get("default_branch", "main"),
        "private": data.get("private", True),
    }


def fetch_readme(repo: str) -> str | None:
    """Fetch README content for a repo."""
    # gh api returns base64-encoded content
    data = gh_api(f"/repos/{GITHUB_ORG}/{repo}/readme")
    if not data:
        return None

    import base64

    content_b64 = data.get("content", "")
    if not content_b64:
        return None

    try:
        content = base64.b64decode(content_b64).decode("utf-8", errors="replace")
        if len(content) > MAX_README_LEN:
            content = content[:MAX_README_LEN] + "\n\n... [truncated]"
        return content.strip()
    except Exception:
        return None


def fetch_commits(repo: str, limit: int = COMMITS_PER_REPO) -> list[dict]:
    """Fetch recent commits for a repo."""
    data = gh_api(
        f"/repos/{GITHUB_ORG}/{repo}/commits?per_page={limit}"
    )
    if not data or not isinstance(data, list):
        return []

    commits = []
    for item in data:
        commit_data = item.get("commit", {})
        author = commit_data.get("author", {})
        message = commit_data.get("message", "").strip()
        if not message:
            continue

        # Truncate very long commit messages (merge commits, etc.)
        if len(message) > 500:
            message = message[:500] + "..."

        commits.append({
            "sha": item.get("sha", "")[:8],
            "message": message,
            "author": author.get("name", "unknown"),
            "date": author.get("date", ""),
        })

    return commits


def build_metadata_chunk(repo: str, meta: dict) -> dict | None:
    """Build a semantic chunk from repo metadata."""
    parts = [f"Repository: {GITHUB_ORG}/{repo}"]

    if meta["description"]:
        parts.append(f"Description: {meta['description']}")
    parts.append(f"Language: {meta['language']}")
    if meta["topics"]:
        parts.append(f"Topics: {', '.join(meta['topics'])}")
    parts.append(f"Created: {meta['created_at'][:10] if meta['created_at'] else 'unknown'}")
    parts.append(f"Last updated: {meta['updated_at'][:10] if meta['updated_at'] else 'unknown'}")
    parts.append(f"Stars: {meta['stars']}, Forks: {meta['forks']}")
    parts.append(f"Visibility: {'private' if meta['private'] else 'public'}")

    content = "\n".join(parts)
    if len(content) < MIN_CHUNK_LEN:
        return None

    return {
        "content": f"GitHub ({repo}, metadata): {content}",
        "source": f"github:{repo}:metadata",
        "source_type": "ingestion",
        "occurred_at": meta.get("updated_at") or datetime.now(timezone.utc).isoformat(),
    }


def build_readme_chunk(repo: str, readme: str, meta: dict) -> dict | None:
    """Build a semantic chunk from README content."""
    if not readme or len(readme) < MIN_CHUNK_LEN:
        return None

    return {
        "content": f"GitHub ({repo}, README): {readme}",
        "source": f"github:{repo}:readme",
        "source_type": "ingestion",
        "occurred_at": meta.get("updated_at") or datetime.now(timezone.utc).isoformat(),
    }


def build_commit_chunks(repo: str, commits: list[dict]) -> list[dict]:
    """Build episodic chunks from commit messages.

    Groups commits into chunks of ~5 to avoid one-chunk-per-commit noise.
    """
    if not commits:
        return []

    chunks = []
    batch: list[str] = []
    batch_date = ""

    for commit in commits:
        date_str = commit["date"][:10] if commit["date"] else "unknown"
        line = f"  [{commit['sha']}] ({date_str}, {commit['author']}): {commit['message']}"
        batch.append(line)

        if not batch_date and commit["date"]:
            batch_date = commit["date"]

        # Flush every 5 commits
        if len(batch) >= 5:
            content = f"GitHub ({repo}, commits):\n" + "\n".join(batch)
            chunks.append({
                "content": content,
                "source": f"github:{repo}:commits:{batch[0].split(']')[0].strip(' [')}",
                "source_type": "ingestion",
                "occurred_at": batch_date or datetime.now(timezone.utc).isoformat(),
            })
            batch = []
            batch_date = ""

    # Flush remainder
    if batch:
        content = f"GitHub ({repo}, commits):\n" + "\n".join(batch)
        chunks.append({
            "content": content,
            "source": f"github:{repo}:commits:{batch[0].split(']')[0].strip(' [')}",
            "source_type": "ingestion",
            "occurred_at": batch_date or datetime.now(timezone.utc).isoformat(),
        })

    return chunks


def main():
    parser = argparse.ArgumentParser(
        description="Ingest GitHub repo data into Jake's Brain"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be ingested without doing it",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Only process N repos (from the top of the list)",
    )
    parser.add_argument(
        "--repo", type=str, default=None,
        help="Only process a specific repo (substring match)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Jake Brain — GitHub Repo Ingestion")
    print(f"Org: {GITHUB_ORG} ({len(REPOS)} repos)")
    print("=" * 60)

    # Filter repos
    repos = REPOS
    if args.repo:
        repos = [r for r in repos if args.repo.lower() in r.lower()]
        if not repos:
            print(f"No repos matched filter: {args.repo}")
            return
    if args.limit:
        repos = repos[:args.limit]

    print(f"\nProcessing {len(repos)} repo(s):")
    for r in repos:
        print(f"  - {GITHUB_ORG}/{r}")

    # Gather all chunks
    all_chunks: list[dict] = []
    seen_hashes: set[str] = set()
    repo_stats: dict[str, dict] = {}

    for repo in repos:
        print(f"\n  Fetching {repo}...")
        stats = {"metadata": 0, "readme": 0, "commits": 0}

        # 1. Repo metadata
        meta = fetch_repo_metadata(repo)
        if not meta:
            print(f"    SKIP — could not fetch metadata")
            continue

        meta_chunk = build_metadata_chunk(repo, meta)
        if meta_chunk:
            h = content_hash(meta_chunk["content"])
            if h not in seen_hashes:
                seen_hashes.add(h)
                all_chunks.append(meta_chunk)
                stats["metadata"] = 1

        # 2. README
        readme = fetch_readme(repo)
        if readme:
            readme_chunk = build_readme_chunk(repo, readme, meta)
            if readme_chunk:
                h = content_hash(readme_chunk["content"])
                if h not in seen_hashes:
                    seen_hashes.add(h)
                    all_chunks.append(readme_chunk)
                    stats["readme"] = 1
            print(f"    README: {len(readme)} chars")
        else:
            print(f"    README: not found")

        # 3. Commits
        commits = fetch_commits(repo)
        commit_chunks = build_commit_chunks(repo, commits)
        for chunk in commit_chunks:
            h = content_hash(chunk["content"])
            if h not in seen_hashes:
                seen_hashes.add(h)
                all_chunks.append(chunk)
                stats["commits"] += 1

        print(f"    Commits: {len(commits)} fetched, {stats['commits']} chunk(s)")
        repo_stats[repo] = stats

    print(f"\n{'=' * 60}")
    print(f"Chunks gathered: {len(all_chunks)}")
    for repo, stats in repo_stats.items():
        total = stats["metadata"] + stats["readme"] + stats["commits"]
        print(f"  {repo}: {total} chunks "
              f"(meta={stats['metadata']}, readme={stats['readme']}, "
              f"commits={stats['commits']})")

    if not all_chunks:
        print("No chunks to ingest.")
        return

    if args.dry_run:
        print(f"\n[DRY RUN] Would ingest {len(all_chunks)} chunks. Previewing first 10:\n")
        for i, chunk in enumerate(all_chunks[:10], 1):
            preview = chunk["content"][:120].replace("\n", " ")
            print(f"  {i}. [{chunk['source_type']:15s}] [{len(chunk['content']):5d} chars] {preview}...")
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
                session_id=f"github-ingest-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
                source=chunk["source"],
                source_type=chunk["source_type"],
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
    print("GitHub Ingestion Complete")
    print(f"  Repos processed:    {len(repo_stats)}")
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
