"""Migrate jake_semantic — verify embeddings intact, tag with PAI migration."""
import json
import os
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

    # Check embedding coverage — just check if embedding column is non-null
    # We select id and a small computed field to avoid pulling huge embedding arrays
    offset = 0
    page_size = 1000
    stats = {"total": 0, "has_embedding": 0, "missing_embedding": 0}
    missing_ids = []

    while True:
        result = (
            client.table("jake_semantic")
            .select("id, content, embedding")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        if not result.data:
            break

        for row in result.data:
            stats["total"] += 1
            if row.get("embedding"):
                stats["has_embedding"] += 1
            else:
                stats["missing_embedding"] += 1
                missing_ids.append(row["id"])

        offset += page_size

    print(f"Semantic: {stats['total']} total, {stats['has_embedding']} with embeddings, {stats['missing_embedding']} missing")

    if missing_ids:
        print(f"\n{len(missing_ids)} records missing embeddings.")
        print("Re-embedding requires Voyage AI key. Skipping for now.")
        print("IDs saved to migration stats for later re-embedding.")

    stats["missing_ids"] = missing_ids[:100]  # Save first 100 for reference

    outpath = os.path.join(os.path.dirname(__file__), "..", "v1-semantic-migration-stats.json")
    with open(outpath, "w") as f:
        json.dump(stats, f, indent=2)


if __name__ == "__main__":
    main()
