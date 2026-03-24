"""Audit memory quality — find duplicates, empty records, stale data."""
import json
import os
from collections import Counter
from datetime import datetime

EXPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "export")


def audit_table(table_name: str) -> dict:
    """Audit a single exported table for quality issues."""
    filepath = os.path.join(EXPORT_DIR, f"{table_name}.json")
    with open(filepath) as f:
        rows = json.load(f)

    issues = {
        "total": len(rows),
        "empty_content": 0,
        "duplicate_content": 0,
        "no_metadata": 0,
        "oldest": None,
        "newest": None,
        "type_distribution": Counter(),
    }

    seen_content = set()
    for row in rows:
        content = row.get("content", "")
        if not content or str(content).strip() == "":
            issues["empty_content"] += 1

        content_hash = hash(str(content)[:200])
        if content_hash in seen_content:
            issues["duplicate_content"] += 1
        seen_content.add(content_hash)

        if not row.get("metadata"):
            issues["no_metadata"] += 1

        if row.get("memory_type"):
            issues["type_distribution"][row["memory_type"]] += 1

        created = row.get("created_at") or row.get("occurred_at")
        if created:
            if issues["oldest"] is None or created < issues["oldest"]:
                issues["oldest"] = created
            if issues["newest"] is None or created > issues["newest"]:
                issues["newest"] = created

    issues["type_distribution"] = dict(issues["type_distribution"])
    return issues


def main():
    tables = [
        "jake_episodic", "jake_semantic", "jake_procedural",
        "jake_entities", "jake_relationships", "jake_goals",
    ]

    report = []
    report.append("# V1 Memory Audit Report\n")
    report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")

    total_records = 0
    total_empty = 0
    total_dupes = 0

    for table in tables:
        try:
            issues = audit_table(table)
            total_records += issues["total"]
            total_empty += issues["empty_content"]
            total_dupes += issues["duplicate_content"]

            report.append(f"\n## {table}\n")
            report.append(f"- **Total records:** {issues['total']}")
            report.append(f"- **Empty content:** {issues['empty_content']}")
            report.append(f"- **Duplicate content:** {issues['duplicate_content']}")
            report.append(f"- **Missing metadata:** {issues['no_metadata']}")
            report.append(f"- **Date range:** {issues['oldest']} -> {issues['newest']}")
            if issues["type_distribution"]:
                report.append(f"- **Types:** {issues['type_distribution']}")
        except FileNotFoundError:
            report.append(f"\n## {table}\n- **SKIPPED** -- export file not found")

    report.append(f"\n## Summary\n")
    report.append(f"- **Total records:** {total_records}")
    report.append(f"- **Total empty:** {total_empty} ({total_empty/max(total_records,1)*100:.1f}%)")
    report.append(f"- **Total duplicates:** {total_dupes} ({total_dupes/max(total_records,1)*100:.1f}%)")
    report.append(f"- **Clean records:** {total_records - total_empty - total_dupes}")

    output = "\n".join(report)
    outpath = os.path.join(os.path.dirname(__file__), "..", "v1-audit-report.md")
    with open(outpath, "w") as f:
        f.write(output)

    print(output)


if __name__ == "__main__":
    main()
