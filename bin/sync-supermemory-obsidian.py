#!/usr/bin/env python3
"""
Bidirectional sync: SuperMemory ↔ Obsidian vault.

Push: Obsidian Memory/*.md → SuperMemory containers (based on filename prefix)
Pull: SuperMemory containers → Obsidian Memory/SuperMemory/<container>.md

Run via cron or manually: python3 bin/sync-supermemory-obsidian.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# === CONFIG ===
VAULT = Path("/Users/mikerodgers/Obsidian/JakeStudio")
MEMORY_DIR = VAULT / "Memory"
SM_SYNC_DIR = VAULT / "Memory" / "SuperMemory"
API_BASE = "https://api.supermemory.ai"
API_KEY = os.environ.get(
    "SUPERMEMORY_API_KEY",
    "sm_UhNTEYCgzg7N3u17XTTFoh_scZZyoIIdXztSIJLauuqcexSQXXozaoqEyesDiWwyiwEMXYpXRdzqQwGvYbGruGD",
)

CONTAINERS = ["jake", "kira", "aria", "scout", "steve", "compass", "shared"]

# Map filename prefixes to SuperMemory containers
PREFIX_TO_CONTAINER = {
    "feedback_": "jake",
    "user_": "jake",
    "jake_": "jake",
    "project_": "shared",
    "reference_": "shared",
}

stats = {"pushed": 0, "pulled": 0, "skipped": 0, "errors": 0}


def api(method: str, path: str, body: dict | None = None) -> dict:
    req = Request(
        f"{API_BASE}{path}",
        method=method,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
    )
    if body:
        req.data = json.dumps(body).encode()
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        return {"error": e.code, "message": e.read().decode()[:200]}


def push_obsidian_to_supermemory():
    """Push Obsidian Memory files → SuperMemory containers."""
    print("=== PUSH: Obsidian → SuperMemory ===")

    for md_file in sorted(MEMORY_DIR.glob("*.md")):
        if md_file.name.startswith("_") or md_file.name == "MEMORY.md":
            continue

        content = md_file.read_text(encoding="utf-8", errors="replace").strip()
        if not content or len(content) < 20:
            stats["skipped"] += 1
            continue

        # Determine container from prefix
        container = "shared"
        for prefix, ctr in PREFIX_TO_CONTAINER.items():
            if md_file.name.startswith(prefix):
                container = ctr
                break

        # Check if already in SuperMemory by searching for the filename
        search_result = api("POST", "/v4/search", {
            "q": md_file.stem.replace("_", " "),
            "containerTag": container,
            "limit": 3,
        })

        results = search_result.get("results", [])
        # Skip if a high-similarity match exists (already synced)
        if results and results[0].get("similarity", 0) > 0.85:
            stats["skipped"] += 1
            continue

        # Push to SuperMemory
        # Prefix content with filename for searchability
        tagged_content = f"# {md_file.stem}\n\n{content}"
        result = api("POST", "/v4/memories", {
            "memories": [{"content": tagged_content}],
            "containerTag": container,
        })

        if "error" in result:
            print(f"  ERROR pushing {md_file.name}: {result.get('message', result)}")
            stats["errors"] += 1
        else:
            print(f"  Pushed {md_file.name} → {container}")
            stats["pushed"] += 1


def pull_supermemory_to_obsidian():
    """Pull SuperMemory containers → Obsidian markdown files."""
    print("\n=== PULL: SuperMemory → Obsidian ===")
    SM_SYNC_DIR.mkdir(parents=True, exist_ok=True)

    for container in CONTAINERS:
        result = api("POST", "/v4/memories/list", {
            "containerTags": [container],
        })

        entries = result.get("memoryEntries", [])
        if not entries:
            continue

        lines = [
            "---",
            f"title: SuperMemory — {container}",
            f"tags: [supermemory, {container}]",
            f"synced: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"count: {len(entries)}",
            "---",
            "",
            f"# SuperMemory: {container}",
            "",
            f"> {len(entries)} memories in the `{container}` container.",
            "",
        ]

        for entry in entries:
            mem = entry.get("memory", "")
            created = entry.get("createdAt", "")[:10]
            mem_id = entry.get("id", "")[:8]

            lines.append(f"## {mem_id} ({created})")
            lines.append("")
            lines.append(mem)
            lines.append("")
            lines.append("---")
            lines.append("")

        out_path = SM_SYNC_DIR / f"{container}.md"
        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"  Pulled {len(entries)} memories from {container}")
        stats["pulled"] += len(entries)


def main():
    print(f"SuperMemory ↔ Obsidian Sync — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Vault: {VAULT}")
    print()

    push_obsidian_to_supermemory()
    pull_supermemory_to_obsidian()

    print("\n=== SYNC COMPLETE ===")
    print(f"  Pushed:  {stats['pushed']}")
    print(f"  Pulled:  {stats['pulled']}")
    print(f"  Skipped: {stats['skipped']} (already synced)")
    print(f"  Errors:  {stats['errors']}")


if __name__ == "__main__":
    main()
