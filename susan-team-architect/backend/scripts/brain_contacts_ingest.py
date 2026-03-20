#!/usr/bin/env python3
"""Ingest Apple Contacts into Jake's Brain as entities with birthdays.

Reads the JSON export from Swift Contacts framework and:
1. Creates entities for each contact with birthday data
2. Creates relationships (family, friend, colleague)
3. Stores a semantic memory for birthday tracking

Usage:
    cd susan-team-architect/backend && source .venv/bin/activate
    python scripts/brain_contacts_ingest.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from jake_brain.store import BrainStore
from jake_brain.config import brain_config

CONTACTS_FILE = Path("/tmp/contacts_all.json")

# Relationship mapping from Apple Contacts labels to brain relationship types
APPLE_REL_MAP = {
    "_$!<Spouse>!$_": "spouse_of",
    "_$!<Child>!$_": "parent_of",
    "_$!<Parent>!$_": "child_of",
    "_$!<Sibling>!$_": "sibling_of",
    "_$!<Partner>!$_": "partner_of",
    "_$!<Friend>!$_": "friend_of",
    "unknown": "knows",
}

# Known family members — map contact names to relationship types with Mike
# This enriches what Apple Contacts doesn't explicitly track
KNOWN_RELATIONSHIPS = {
    "james loehr": {"rel": "spouse_of", "type": "family_member"},
    "jacob rodgers": {"rel": "parent_of", "type": "family_member"},
    "jennifer rodgers": {"rel": "ex_spouse_of", "type": "family_member"},
    "michael rodgers": {"rel": "self", "type": "person"},
    "david (dad)": {"rel": "child_of", "type": "family_member", "display": "David Rodgers (Dad)"},
    # James's family (Loehrs) — use relates_to since in_law_of isn't in schema
    "kyle loehr": {"rel": "relates_to", "type": "family_member"},
    "kasey loehr": {"rel": "relates_to", "type": "family_member"},
    "aubrey loehr": {"rel": "relates_to", "type": "family_member"},
    "jen loehr": {"rel": "relates_to", "type": "family_member"},
}


def ingest_contacts(dry_run: bool = False):
    if not CONTACTS_FILE.exists():
        print(f"ERROR: {CONTACTS_FILE} not found. Run the Swift export first.")
        return

    with open(CONTACTS_FILE) as f:
        all_contacts = json.load(f)

    # Filter to contacts with birthdays (these are people Mike cares about)
    with_bday = [c for c in all_contacts if "birthday" in c]

    print(f"Total contacts: {len(all_contacts)}")
    print(f"With birthdays: {len(with_bday)}")
    print()

    if dry_run:
        for c in with_bday:
            name = f"{c.get('first', '')} {c.get('last', '')}".strip()
            bday = c.get("birthday", "?")
            year = c.get("birth_year", "")
            print(f"  Would ingest: {name:30s} | {bday} {year}")
        print(f"\n[DRY RUN] Would ingest {len(with_bday)} contacts. Exiting.")
        return

    store = BrainStore()
    stats = {"entities_created": 0, "entities_updated": 0, "relationships": 0, "semantic": 0}

    for c in with_bday:
        first = c.get("first", "").strip()
        last = c.get("last", "").strip()
        name = f"{first} {last}".strip()
        if not name:
            continue

        name_lower = name.lower()
        birthday = c.get("birthday", "")
        birth_year = c.get("birth_year")
        email = c.get("email", "")
        phone = c.get("phone", "")

        # Determine entity type
        known = KNOWN_RELATIONSHIPS.get(name_lower, {})
        entity_type = known.get("type", "person")
        display_name = known.get("display", name)

        # Build properties
        props = {}
        if birthday:
            props["birthday"] = birthday
        if birth_year:
            props["birth_year"] = birth_year
        if email:
            props["email"] = email
        if phone:
            props["phone"] = phone

        # Skip self
        if known.get("rel") == "self":
            # Update Mike's own entity with birthday
            print(f"  Updating Mike's birthday: {birthday} {birth_year or ''}")
            try:
                # Find Mike's entity and update
                result = store.supabase.table("jake_entities").select("id, properties").eq("name", "Mike Rodgers").execute()
                if result.data:
                    existing_props = result.data[0].get("properties", {})
                    existing_props.update(props)
                    store.supabase.table("jake_entities").update({"properties": existing_props}).eq("id", result.data[0]["id"]).execute()
                    stats["entities_updated"] += 1
            except Exception as exc:
                print(f"  Failed to update Mike: {exc}")
            continue

        # Check if entity already exists
        try:
            existing = store.supabase.table("jake_entities").select("id, properties").eq("name", display_name).execute()
            if existing.data:
                # Update existing entity with contact data
                existing_props = existing.data[0].get("properties", {})
                existing_props.update(props)
                store.supabase.table("jake_entities").update({"properties": existing_props}).eq("id", existing.data[0]["id"]).execute()
                print(f"  Updated: {display_name:30s} | {birthday} {birth_year or ''}")
                stats["entities_updated"] += 1
            else:
                # Create new entity
                embedding = store.embedder.embed_query(f"{display_name} birthday {birthday}")
                store.supabase.table("jake_entities").insert({
                    "name": display_name,
                    "entity_type": entity_type,
                    "properties": props,
                    "importance": 0.6 if entity_type == "family_member" else 0.4,
                    "embedding": embedding,
                }).execute()
                print(f"  Created: {display_name:30s} | {birthday} {birth_year or ''} | {entity_type}")
                stats["entities_created"] += 1
        except Exception as exc:
            print(f"  Failed: {display_name} — {exc}")
            continue

        # Create relationship to Mike if known
        rel_type = known.get("rel")
        if rel_type and rel_type not in ("self",):
            try:
                # Find Mike's entity ID
                mike = store.supabase.table("jake_entities").select("id").eq("name", "Mike Rodgers").execute()
                target = store.supabase.table("jake_entities").select("id").eq("name", display_name).execute()
                if mike.data and target.data:
                    mike_id = mike.data[0]["id"]
                    target_id = target.data[0]["id"]
                    # Check if relationship already exists
                    existing_rel = store.supabase.table("jake_relationships").select("id").eq("source_entity_id", mike_id).eq("target_entity_id", target_id).eq("relationship_type", rel_type).execute()
                    if not existing_rel.data:
                        store.supabase.table("jake_relationships").insert({
                            "source_entity_id": mike_id,
                            "target_entity_id": target_id,
                            "relationship_type": rel_type,
                            "confidence": 0.95,
                            "properties": {"source": "apple_contacts"},
                        }).execute()
                        print(f"    + Relationship: Mike → {rel_type} → {display_name}")
                        stats["relationships"] += 1
            except Exception as exc:
                print(f"    Failed relationship: {exc}")

    # Store a semantic memory about birthday tracking
    try:
        birthday_summary = "Mike's contacts with birthdays:\n"
        for c in sorted(with_bday, key=lambda x: x.get("birthday", "")):
            name = f"{c.get('first', '')} {c.get('last', '')}".strip()
            bday = c.get("birthday", "?")
            year = c.get("birth_year", "")
            birthday_summary += f"- {name}: {bday} {year}\n"

        store.store_semantic(
            content=birthday_summary,
            category="fact",
            confidence=0.95,
            source_episodes=[],
            project=None,
            topics=["family", "birthdays", "contacts"],
        )
        stats["semantic"] += 1
        print(f"\n  Stored birthday calendar as semantic memory")
    except Exception as exc:
        print(f"\n  Failed to store birthday summary: {exc}")

    print(f"\n{'=' * 60}")
    print(f"Contact Ingestion Complete")
    print(f"  Entities created:  {stats['entities_created']}")
    print(f"  Entities updated:  {stats['entities_updated']}")
    print(f"  Relationships:     {stats['relationships']}")
    print(f"  Semantic memories: {stats['semantic']}")
    print(f"{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(description="Ingest Apple Contacts into Jake's Brain")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    ingest_contacts(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
