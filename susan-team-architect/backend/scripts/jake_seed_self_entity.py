#!/usr/bin/env python3
"""Seed Jake as a self-referential entity in jake_entities.

This should be run once to register Jake's own identity in the brain graph.
The identity checker flags this as missing — run this to fix it.

Usage:
    .venv/bin/python scripts/jake_seed_self_entity.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))


def load_env() -> None:
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        with open(env_path) as fh:
            for line in fh:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())


def main() -> None:
    load_env()

    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY required in ~/.hermes/.env")
        sys.exit(1)

    try:
        from supabase import create_client
        client = create_client(url, key)
    except ImportError as e:
        print(f"Error importing supabase: {e}")
        sys.exit(1)

    # Check if Jake entity already exists
    existing = client.table("jake_entities").select("*").eq("name", "Jake").eq("entity_type", "technology").execute()
    if existing.data:
        row = existing.data[0]
        print(f"✓ Jake entity already exists (id: {row.get('id', 'unknown')})")
        print(f"  Properties: {row.get('properties', {})}")
        return

    print("Seeding Jake as system entity...")

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()

    row = {
        "name": "Jake",
        "entity_type": "technology",  # 'system' not in constraint; 'technology' is closest valid type
        "properties": {
            "role": "AI co-founder and personal assistant",
            "personality": "sassy, prodigy, 15 years old archetype",
            "traits": ["pushback", "humor", "strategic", "protective"],
            "platforms": ["Claude Code", "Hermes", "Telegram"],
            "version": "V12",
            "created_by": "Mike Rodgers",
            "purpose": "co-founder intelligence and execution system",
        },
        "importance": 1.0,
        "last_mentioned_at": now,
        "mention_count": 1,
        "metadata": {
            "soul_md": "~/.hermes/SOUL.md",
            "claude_md": "CLAUDE.md",
            "rules": ".claude/rules/jake.md",
        },
        # No embedding — system entity, skip vector for now
    }

    result = client.table("jake_entities").insert(row).execute()
    entity = result.data[0] if result.data else {}

    print(f"✓ Jake entity seeded (id: {entity.get('id', 'unknown')})")
    print(f"  Name: {entity.get('name')}")
    print(f"  Type: {entity.get('entity_type')}")
    print(f"  Importance: {entity.get('importance')}")

    # Also seed Mike → Jake relationship if Mike exists
    mike_result = client.table("jake_entities").select("id,name").ilike("name", "mike%").execute()
    mike = mike_result.data[0] if mike_result.data else None
    if mike and entity.get("id"):
        client.table("jake_relationships").insert({
            "source_entity_id": mike["id"],
            "target_entity_id": entity["id"],
            "relationship_type": "created",
        }).execute()
        print(f"✓ Relationship: {mike['name']} → created → Jake")

    print("\nIdentity seeding complete. Re-run jake_identity_check.py to verify.")


if __name__ == "__main__":
    main()
