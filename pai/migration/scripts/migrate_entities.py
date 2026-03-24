"""Verify entity and relationship integrity. Deduplicate entity names."""
import json
import os
from collections import Counter
from supabase import create_client

# Load .env
env_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "susan-team-architect", "backend", ".env")
if os.path.exists(env_path):
    for line in open(env_path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]


def main():
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Check entities
    entities = client.table("jake_entities").select("*").execute().data or []
    print(f"Entities: {len(entities)}")

    # Find duplicates (same name, different case or slight variations)
    name_counts = Counter()
    for e in entities:
        name = (e.get("name") or "").strip().lower()
        if name:
            name_counts[name] += 1

    dupes = {k: v for k, v in name_counts.items() if v > 1}
    if dupes:
        print(f"Duplicate entity names: {dupes}")
    else:
        print("No duplicate entity names found")

    # Entity type distribution
    type_counts = Counter()
    for e in entities:
        etype = e.get("entity_type") or e.get("type") or "unknown"
        type_counts[etype] += 1
    print(f"Entity types: {dict(type_counts)}")

    # Check relationships
    rels = client.table("jake_relationships").select("*").execute().data or []
    print(f"\nRelationships: {len(rels)}")

    # Relationship type distribution
    rel_types = Counter()
    for r in rels:
        rtype = r.get("relationship_type") or r.get("type") or "unknown"
        rel_types[rtype] += 1
    print(f"Relationship types: {dict(rel_types)}")

    # Check for orphaned relationships (references to non-existent entities)
    entity_ids = {e["id"] for e in entities}
    orphaned = 0
    for r in rels:
        src = r.get("source_id") or r.get("from_entity_id")
        tgt = r.get("target_id") or r.get("to_entity_id")
        if src and src not in entity_ids:
            orphaned += 1
        if tgt and tgt not in entity_ids:
            orphaned += 1
    print(f"Orphaned relationship references: {orphaned}")

    stats = {
        "entities": len(entities),
        "entity_types": dict(type_counts),
        "duplicate_names": dupes,
        "relationships": len(rels),
        "relationship_types": dict(rel_types),
        "orphaned_refs": orphaned,
    }
    outpath = os.path.join(os.path.dirname(__file__), "..", "v1-entity-migration-stats.json")
    with open(outpath, "w") as f:
        json.dump(stats, f, indent=2)


if __name__ == "__main__":
    main()
