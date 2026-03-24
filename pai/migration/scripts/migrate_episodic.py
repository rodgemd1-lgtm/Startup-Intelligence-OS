"""Migrate jake_episodic records — tag with PAI tier, track migration status."""
import json
import os
from datetime import datetime

# Load .env
env_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "susan-team-architect", "backend", ".env")
if os.path.exists(env_path):
    for line in open(env_path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]


def main():
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    stats = {"total": 0, "tagged": 0, "already_tagged": 0, "errors": 0}

    offset = 0
    page_size = 1000

    while True:
        result = (
            client.table("jake_episodic")
            .select("id, content, memory_type, importance, metadata, created_at")
            .range(offset, offset + page_size - 1)
            .execute()
        )

        if not result.data:
            break

        for row in result.data:
            stats["total"] += 1

            # Skip if already migrated
            metadata = row.get("metadata") or {}
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}

            if metadata.get("pai_migration") == "v1":
                stats["already_tagged"] += 1
                continue

            # Tag as migrated
            new_metadata = {**metadata, "pai_migration": "v1", "migrated_at": datetime.now().isoformat()}

            # Classify into Miessler tier
            importance = row.get("importance") or 0.5
            if isinstance(importance, str):
                try:
                    importance = float(importance)
                except:
                    importance = 0.5
            memory_type = row.get("memory_type", "conversation")

            if importance >= 0.8:
                tier = "learning"
            elif memory_type in ("decision", "correction", "lesson"):
                tier = "learning"
            else:
                tier = "work"

            new_metadata["pai_tier"] = tier

            try:
                client.table("jake_episodic").update(
                    {"metadata": new_metadata}
                ).eq("id", row["id"]).execute()
                stats["tagged"] += 1
            except Exception as e:
                stats["errors"] += 1
                if stats["errors"] <= 5:
                    print(f"  Error on {row['id']}: {e}")

        offset += page_size
        if stats["total"] % 10000 == 0:
            print(f"  Processed {stats['total']} records...")

    print(f"\nEpisodic migration complete:")
    print(f"  Total: {stats['total']}")
    print(f"  Tagged: {stats['tagged']}")
    print(f"  Already tagged: {stats['already_tagged']}")
    print(f"  Errors: {stats['errors']}")

    outpath = os.path.join(os.path.dirname(__file__), "..", "v1-episodic-migration-stats.json")
    with open(outpath, "w") as f:
        json.dump(stats, f, indent=2)


if __name__ == "__main__":
    main()
