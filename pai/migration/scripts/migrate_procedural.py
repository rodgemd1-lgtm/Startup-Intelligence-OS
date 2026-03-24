"""Migrate jake_procedural rules — extract top rules to TELOS/LEARNED.md."""
import json
import os
from collections import defaultdict
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

    # Export all procedural memories, categorize
    offset = 0
    page_size = 1000
    rules = []

    while True:
        result = (
            client.table("jake_procedural")
            .select("content, pattern_type, domain, confidence, effectiveness, metadata, created_at")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        if not result.data:
            break
        rules.extend(result.data)
        offset += page_size

    print(f"Found {len(rules)} procedural rules")

    # Deduplicate by content
    seen = set()
    unique_rules = []
    for rule in rules:
        content = str(rule.get("content", "")).strip()[:200]
        if content and content not in seen:
            seen.add(content)
            unique_rules.append(rule)

    print(f"Unique rules after dedup: {len(unique_rules)}")

    # Categorize by type
    categories = defaultdict(list)
    for rule in unique_rules:
        cat = rule.get("domain", "general") or "general"
        categories[cat].append(rule)

    # Write to LEARNED.md
    lines = ["# Learned — Procedural Rules (Migrated from Hermes)\n"]
    lines.append(f"*Migrated: {len(rules)} total, {len(unique_rules)} unique rules from jake_procedural*\n")
    lines.append(f"*Categories: {', '.join(sorted(categories.keys()))}*\n")

    for cat in sorted(categories.keys()):
        cat_rules = categories[cat]
        lines.append(f"\n## {cat.replace('_', ' ').title()}\n")
        # Top 20 by importance per category
        top_rules = sorted(cat_rules, key=lambda r: float(r.get("confidence", 0) or 0), reverse=True)[:20]
        for rule in top_rules:
            content = str(rule["content"]).strip().replace("\n", " ")[:200]
            confidence = float(rule.get("confidence", 0) or 0)
            lines.append(f"- [{confidence:.1f}] {content}")

    telos_path = os.path.join(os.path.dirname(__file__), "..", "..", "TELOS", "LEARNED.md")
    os.makedirs(os.path.dirname(telos_path), exist_ok=True)
    with open(telos_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Wrote top rules to pai/TELOS/LEARNED.md")
    print(f"Categories: {list(categories.keys())}")

    stats = {
        "total": len(rules),
        "unique": len(unique_rules),
        "categories": {k: len(v) for k, v in categories.items()},
    }
    outpath = os.path.join(os.path.dirname(__file__), "..", "v1-procedural-migration-stats.json")
    with open(outpath, "w") as f:
        json.dump(stats, f, indent=2)


if __name__ == "__main__":
    main()
