"""Full export of all jake_* tables for migration baseline."""
import json
import os
import sys
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
EXPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "export")

TABLES = [
    "jake_episodic",
    "jake_semantic",
    "jake_procedural",
    "jake_entities",
    "jake_relationships",
    "jake_working",
    "jake_goals",
]


def export_table(client, table_name: str) -> list:
    """Export all rows from a table, paginating in chunks of 1000."""
    all_rows = []
    offset = 0
    page_size = 1000
    while True:
        result = (
            client.table(table_name)
            .select("*")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        if not result.data:
            break
        all_rows.extend(result.data)
        offset += page_size
        if len(result.data) < page_size:
            break
    return all_rows


def main():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    counts = {}
    for table in TABLES:
        print(f"Exporting {table}...")
        rows = export_table(client, table)
        counts[table] = len(rows)

        # Write export (exclude embeddings to keep file size manageable)
        export_rows = []
        for row in rows:
            clean = {k: v for k, v in row.items() if k != "embedding"}
            export_rows.append(clean)

        outpath = os.path.join(EXPORT_DIR, f"{table}.json")
        with open(outpath, "w") as f:
            json.dump(export_rows, f, indent=2, default=str)

        print(f"  -> {len(rows)} rows exported")

    # Write baseline counts
    baseline = {
        "export_date": datetime.now().isoformat(),
        "counts": counts,
        "total": sum(counts.values()),
    }
    baseline_path = os.path.join(os.path.dirname(__file__), "..", "v1-baseline-counts.json")
    with open(baseline_path, "w") as f:
        json.dump(baseline, f, indent=2)

    print(f"\nTotal: {sum(counts.values())} records across {len(TABLES)} tables")


if __name__ == "__main__":
    main()
