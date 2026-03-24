# PAI V1: Memory Migration — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Migrate Jake's 99K Supabase memories into the new 3-tier PAI memory architecture (Session → Work → Learning), fix broken brain_search, and establish memory consolidation pipelines — so nothing is lost and everything is findable.

**Architecture:** Map existing 6 Supabase tables (jake_working, jake_episodic, jake_semantic, jake_procedural, jake_entities, jake_relationships) into Miessler's 3-tier model: Session tier (LosslessClaw DAG for live conversation), Work tier (PRD files with ISC for active tasks), Learning tier (extracted patterns, failures, synthesis). Supabase remains the structured data store. LosslessClaw handles conversation memory.

**Depends On:** V0 complete (OpenClaw + LosslessClaw + Claude Code running)

**Process Rule:** Research → Plan → Execute → Lessons Learned → Documentation. Every time. No exceptions.

---

## Pre-Flight Checklist

Before starting ANY task:
- [ ] V0 exit criteria all passed (OpenClaw, LosslessClaw, Claude Code brain running)
- [ ] Supabase baseline counts documented (from V0 Task 13)
- [ ] LosslessClaw confirmed working (DAG context persists across restarts)
- [ ] Git repo is clean (`git status` shows no uncommitted changes)
- [ ] Susan backend venv activates cleanly
- [ ] Voyage AI API key is available (for re-embedding if needed)

---

## Phase 1A: Supabase Backup and Audit

*Before touching anything, we photograph the crime scene.*

### Task 1: Full Supabase Export

**Files:**
- Create: `pai/migration/v1-baseline-counts.json`
- Create: `pai/migration/export/` (directory for exported data)
- Create: `pai/migration/scripts/export_supabase.py`

**Step 1: Create the export script**

```python
# pai/migration/scripts/export_supabase.py
"""Full export of all jake_* tables for migration baseline."""
import json
import os
from datetime import datetime
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_ANON_KEY"]
EXPORT_DIR = "pai/migration/export"

TABLES = [
    "jake_working",
    "jake_episodic",
    "jake_semantic",
    "jake_procedural",
    "jake_entities",
    "jake_relationships",
    "jake_goals",
]

def export_table(client, table_name: str) -> list[dict]:
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

        with open(f"{EXPORT_DIR}/{table}.json", "w") as f:
            json.dump(export_rows, f, indent=2, default=str)

        print(f"  → {len(rows)} rows exported")

    # Write baseline counts
    baseline = {
        "export_date": datetime.now().isoformat(),
        "counts": counts,
        "total": sum(counts.values()),
    }
    with open("pai/migration/v1-baseline-counts.json", "w") as f:
        json.dump(baseline, f, indent=2)

    print(f"\nTotal: {sum(counts.values())} records across {len(TABLES)} tables")

if __name__ == "__main__":
    main()
```

**Step 2: Run the export**

```bash
cd susan-team-architect/backend
source .venv/bin/activate
cd ../../
python pai/migration/scripts/export_supabase.py
```

Expected: ~99K records exported. JSON files in `pai/migration/export/`.

**Step 3: Verify counts match audit**

Expected baseline (from Hermes audit):
- jake_episodic: ~88,000
- jake_semantic: ~5,600
- jake_semantic: ~5,200
- jake_entities: ~63
- jake_relationships: ~56
- jake_working: variable
- jake_goals: variable

**Step 4: Commit baseline**

```bash
git add pai/migration/v1-baseline-counts.json pai/migration/scripts/
# DO NOT commit the export/ directory (too large, contains personal data)
echo "pai/migration/export/" >> .gitignore
git add .gitignore
git commit -m "feat(pai): V1 migration baseline — export script and counts"
```

---

### Task 2: Audit Memory Quality

**Files:**
- Create: `pai/migration/scripts/audit_memory.py`
- Create: `pai/migration/v1-audit-report.md`

**Step 1: Create the audit script**

```python
# pai/migration/scripts/audit_memory.py
"""Audit memory quality — find duplicates, empty records, stale data."""
import json
from collections import Counter
from datetime import datetime

def audit_table(table_name: str) -> dict:
    """Audit a single exported table for quality issues."""
    with open(f"pai/migration/export/{table_name}.json") as f:
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
        if not content or content.strip() == "":
            issues["empty_content"] += 1

        content_hash = hash(content[:200])  # First 200 chars
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
        "jake_entities", "jake_relationships",
    ]

    report = []
    report.append("# V1 Memory Audit Report\n")
    report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")

    for table in tables:
        try:
            issues = audit_table(table)
            report.append(f"\n## {table}\n")
            report.append(f"- **Total records:** {issues['total']}")
            report.append(f"- **Empty content:** {issues['empty_content']}")
            report.append(f"- **Duplicate content:** {issues['duplicate_content']}")
            report.append(f"- **Missing metadata:** {issues['no_metadata']}")
            report.append(f"- **Date range:** {issues['oldest']} → {issues['newest']}")
            report.append(f"- **Types:** {issues['type_distribution']}")
        except FileNotFoundError:
            report.append(f"\n## {table}\n- **SKIPPED** — export file not found")

    with open("pai/migration/v1-audit-report.md", "w") as f:
        f.write("\n".join(report))

    print("\n".join(report))

if __name__ == "__main__":
    main()
```

**Step 2: Run the audit**

```bash
python pai/migration/scripts/audit_memory.py
```

**Step 3: Review and decide on cleanup thresholds**

Based on audit results, decide:
- Delete empty content records? (Threshold: content is empty or whitespace-only)
- Deduplicate? (Threshold: identical first 200 chars within same session)
- Archive stale records? (Threshold: older than 12 months with low importance)

**Step 4: Commit audit report**

```bash
git add pai/migration/v1-audit-report.md pai/migration/scripts/audit_memory.py
git commit -m "feat(pai): V1 memory audit — quality analysis of 99K records"
```

---

## Phase 1B: 3-Tier Memory Architecture Setup

*Map existing flat tables into Miessler's tiered model.*

### Task 3: Create PAI Memory Directory Structure

**Files:**
- Create: `pai/MEMORY/WORK/.gitkeep`
- Create: `pai/MEMORY/LEARNING/.gitkeep`
- Create: `pai/MEMORY/WISDOM/.gitkeep`
- Create: `pai/MEMORY/STATE/ratings.jsonl`
- Create: `pai/MEMORY/STATE/work.json`
- Create: `pai/MEMORY/STATE/session-names.json`
- Create: `pai/MEMORY/MEMORY.md`

**Step 1: Create directory structure (Miessler-compatible)**

```bash
mkdir -p pai/MEMORY/{WORK,LEARNING,WISDOM,STATE}
```

**Step 2: Create MEMORY.md (architecture doc)**

```markdown
# PAI Memory Architecture — 3-Tier + Supabase

## Tier 1: Session Memory (LosslessClaw)
**Storage:** SQLite DAG at `~/.openclaw/lcm.db`
**Contains:** Live conversation context, message history, summarization tree
**Lifecycle:** Grows during conversation, DAG summarizes at context threshold (75%)
**Access:** `lcm_grep`, `lcm_describe`, `lcm_expand` (LosslessClaw agent tools)
**Retention:** Infinite (LosslessClaw never forgets)

## Tier 2: Work Memory (File-based PRDs)
**Storage:** `pai/MEMORY/WORK/<session-id>/`
**Contains per session:**
- `META.yaml` — session metadata (start, end, status, tags)
- `ISC.json` — Ideal State Criteria for the session's task
- `PRD-*.md` — Product requirement docs for complex tasks
- `artifacts/` — Generated files, research, outputs
**Lifecycle:** Created at session start (AutoWorkCreation hook), closed at session end
**Access:** File read/search

## Tier 3: Learning Memory (Extracted patterns)
**Storage:** `pai/MEMORY/LEARNING/`
**Contains:**
- `patterns/` — Detected behavioral patterns (what works, what doesn't)
- `failures/` — Full context dumps of failed interactions
- `corrections/` — User corrections with before/after
- `synthesis/` — Weekly synthesized insights
**Lifecycle:** Extracted from completed Work sessions (WorkCompletionLearning hook)
**Access:** Loaded into context at session start

## Structured Data (Supabase — unchanged)
**Tables:** jake_episodic, jake_semantic, jake_procedural, jake_entities, jake_relationships, jake_goals
**Contains:** Persisted facts, people, projects, rules, embeddings
**Access:** BrainStore class (susan-team-architect/backend/jake_brain/store.py)
**Embeddings:** Voyage AI `voyage-3` (1024 dimensions)

## Memory Flow
```
Live conversation → LosslessClaw (Tier 1)
                  ↓ (session end)
            Work PRD (Tier 2)
                  ↓ (WorkCompletionLearning hook)
          Learning patterns (Tier 3)
                  ↓ (consolidation pipeline)
          Supabase tables (structured long-term)
```

## Consolidation Rules (from jake_brain/consolidator.py)
- Working → Episodic: importance >= threshold (session end)
- Episodic → Semantic: 3+ references to same fact within 14 days
- Patterns → Procedural: detected across 3+ episodes (requires approval)

## Wisdom Layer
`pai/MEMORY/WISDOM/` holds accumulated wisdom frames — insights that transcend
individual sessions and inform Jake's worldview. Updated quarterly.
Migrated from TELOS/WISDOM.md when patterns are proven over time.
```

**Step 3: Initialize state files**

```json
// pai/MEMORY/STATE/work.json
{
  "sessions": [],
  "active_session": null,
  "total_sessions": 0
}
```

```json
// pai/MEMORY/STATE/session-names.json
{
  "names": {}
}
```

```jsonl
// pai/MEMORY/STATE/ratings.jsonl
// Each line is a JSON object: {"session_id": "...", "rating": 1-5, "timestamp": "..."}
```

**Step 4: Commit**

```bash
git add pai/MEMORY/
git commit -m "feat(pai): create 3-tier PAI memory architecture — WORK, LEARNING, WISDOM, STATE"
```

---

### Task 4: Build Memory Migration Pipeline

**Files:**
- Create: `pai/migration/scripts/migrate_episodic.py`
- Create: `pai/migration/scripts/migrate_semantic.py`
- Create: `pai/migration/scripts/migrate_procedural.py`
- Create: `pai/migration/scripts/migrate_entities.py`

**Step 1: Create episodic migration (88K records → verify and tag)**

```python
# pai/migration/scripts/migrate_episodic.py
"""Migrate jake_episodic records — tag, deduplicate, verify embeddings."""
import json
import os
from datetime import datetime
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_ANON_KEY"]

def main():
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    stats = {"total": 0, "tagged": 0, "deduped": 0, "errors": 0}

    # Step 1: Add migration tag to all episodic records
    # We don't move data — Supabase stays as the store
    # We ADD a migration_status field to track what's been verified
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
            if metadata.get("pai_migration") == "v1":
                continue

            # Tag as migrated
            new_metadata = {**metadata, "pai_migration": "v1", "migrated_at": datetime.now().isoformat()}

            # Classify into Miessler tier
            importance = row.get("importance", 0.5)
            memory_type = row.get("memory_type", "conversation")

            if importance >= 0.8:
                tier = "learning"  # High-importance → learning candidate
            elif memory_type in ("decision", "correction", "lesson"):
                tier = "learning"  # Decision/correction → learning
            else:
                tier = "work"  # Standard episodic → work archive

            new_metadata["pai_tier"] = tier

            try:
                client.table("jake_episodic").update(
                    {"metadata": new_metadata}
                ).eq("id", row["id"]).execute()
                stats["tagged"] += 1
            except Exception as e:
                stats["errors"] += 1
                print(f"  Error on {row['id']}: {e}")

        offset += page_size
        print(f"  Processed {offset} records...")

    print(f"\nMigration complete:")
    print(f"  Total: {stats['total']}")
    print(f"  Tagged: {stats['tagged']}")
    print(f"  Errors: {stats['errors']}")

    # Save migration stats
    with open("pai/migration/v1-episodic-migration-stats.json", "w") as f:
        json.dump(stats, f, indent=2)

if __name__ == "__main__":
    main()
```

**Step 2: Create semantic migration (5.6K records → verify and enrich)**

```python
# pai/migration/scripts/migrate_semantic.py
"""Migrate jake_semantic — these are already distilled facts. Verify embeddings intact."""
import json
import os
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_ANON_KEY"]

def main():
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Semantic memories are already high-quality. Just verify embeddings exist.
    result = client.table("jake_semantic").select("id, content, embedding").execute()

    stats = {"total": 0, "has_embedding": 0, "missing_embedding": 0}
    missing_ids = []

    for row in result.data or []:
        stats["total"] += 1
        if row.get("embedding"):
            stats["has_embedding"] += 1
        else:
            stats["missing_embedding"] += 1
            missing_ids.append(row["id"])

    print(f"Semantic: {stats['total']} total, {stats['has_embedding']} with embeddings, {stats['missing_embedding']} missing")

    if missing_ids:
        print(f"\nRe-embedding {len(missing_ids)} records...")
        # Import embedder to re-embed
        import sys
        sys.path.insert(0, "susan-team-architect/backend")
        from rag_engine.embedder import Embedder
        embedder = Embedder()

        for rid in missing_ids:
            row = client.table("jake_semantic").select("content").eq("id", rid).execute()
            if row.data:
                content = row.data[0]["content"]
                embedding = embedder.embed_query(content)
                client.table("jake_semantic").update({"embedding": embedding}).eq("id", rid).execute()
                print(f"  Re-embedded: {rid}")

    with open("pai/migration/v1-semantic-migration-stats.json", "w") as f:
        json.dump(stats, f, indent=2)

if __name__ == "__main__":
    main()
```

**Step 3: Create procedural migration (5.2K rules → map to LEARNED.md)**

```python
# pai/migration/scripts/migrate_procedural.py
"""Migrate jake_procedural rules into TELOS/LEARNED.md and verify in Supabase."""
import json
import os
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_ANON_KEY"]

def main():
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Export all procedural memories, categorize, write to LEARNED.md
    result = (
        client.table("jake_procedural")
        .select("content, memory_type, importance, metadata, created_at")
        .order("importance", desc=True)
        .execute()
    )

    rules = result.data or []
    print(f"Found {len(rules)} procedural rules")

    # Categorize by type
    categories = {}
    for rule in rules:
        cat = rule.get("memory_type", "general")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(rule)

    # Write to LEARNED.md
    lines = ["# Learned — Procedural Rules (Migrated from Hermes)\n"]
    lines.append(f"*Migrated: {len(rules)} rules from jake_procedural*\n")
    lines.append(f"*Categories: {", ".join(categories.keys())}*\n")

    for cat, cat_rules in sorted(categories.items()):
        lines.append(f"\n## {cat.replace('_', ' ').title()}\n")
        # Top 20 by importance per category
        top_rules = sorted(cat_rules, key=lambda r: r.get("importance", 0), reverse=True)[:20]
        for rule in top_rules:
            content = rule["content"].strip().replace("\n", " ")[:200]
            importance = rule.get("importance", 0.5)
            lines.append(f"- [{importance:.1f}] {content}")

    with open("pai/TELOS/LEARNED.md", "w") as f:
        f.write("\n".join(lines))

    print(f"Wrote top rules to pai/TELOS/LEARNED.md")
    print(f"Categories: {list(categories.keys())}")

if __name__ == "__main__":
    main()
```

**Step 4: Create entity migration (63 entities + 56 relationships → verify graph)**

```python
# pai/migration/scripts/migrate_entities.py
"""Verify entity and relationship integrity. Deduplicate entity names."""
import json
import os
from collections import Counter
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_ANON_KEY"]

def main():
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Check entities
    entities = client.table("jake_entities").select("*").execute().data or []
    print(f"Entities: {len(entities)}")

    # Find duplicates (same name, different case or slight variations)
    name_counter = Counter(e["name"].lower().strip() for e in entities)
    duplicates = {name: count for name, count in name_counter.items() if count > 1}

    if duplicates:
        print(f"Duplicate entities found: {duplicates}")

    # Check relationships
    relationships = client.table("jake_relationships").select("*").execute().data or []
    print(f"Relationships: {len(relationships)}")

    # Verify all relationship endpoints exist
    entity_ids = {e["id"] for e in entities}
    orphaned = []
    for rel in relationships:
        if rel.get("source_id") and rel["source_id"] not in entity_ids:
            orphaned.append(("source", rel["id"], rel["source_id"]))
        if rel.get("target_id") and rel["target_id"] not in entity_ids:
            orphaned.append(("target", rel["id"], rel["target_id"]))

    if orphaned:
        print(f"Orphaned relationships: {len(orphaned)}")

    stats = {
        "entities": len(entities),
        "relationships": len(relationships),
        "duplicate_entities": duplicates,
        "orphaned_relationships": len(orphaned),
        "entity_types": dict(Counter(e.get("entity_type", "unknown") for e in entities)),
    }

    with open("pai/migration/v1-entity-migration-stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    print(f"\nEntity types: {stats['entity_types']}")

if __name__ == "__main__":
    main()
```

**Step 5: Run all migrations**

```bash
cd /Users/mikerodgers/Startup-Intelligence-OS
source susan-team-architect/backend/.venv/bin/activate
python pai/migration/scripts/migrate_episodic.py
python pai/migration/scripts/migrate_semantic.py
python pai/migration/scripts/migrate_procedural.py
python pai/migration/scripts/migrate_entities.py
```

**Step 6: Commit**

```bash
git add pai/migration/scripts/ pai/TELOS/LEARNED.md
git commit -m "feat(pai): V1 memory migration scripts — episodic tagging, semantic verification, procedural export, entity audit"
```

---

## Phase 1C: Replace brain_search with New Retrieval

*brain_search is BROKEN (JSON serialization bug). Replace with LosslessClaw + Supabase RPC.*

### Task 5: Build New Memory Retrieval System

**Files:**
- Create: `pai/memory/retriever.py`
- Create: `pai/memory/__init__.py`

**Step 1: Create the unified retriever**

```python
# pai/memory/retriever.py
"""Unified memory retrieval — replaces broken brain_search.

Search strategy:
1. LosslessClaw (lcm_grep) → recent conversation context
2. Supabase vector search → semantic memory (Voyage AI embeddings)
3. Supabase full-text → episodic and procedural keyword search
4. Knowledge graph → entity/relationship traversal

Results are merged, deduplicated, and ranked by relevance + recency.
"""
import os
import json
import subprocess
from datetime import datetime, timedelta
from typing import Any

from supabase import create_client, Client


class PAIRetriever:
    """Unified retrieval across all memory tiers."""

    def __init__(self):
        self.supabase: Client = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_ANON_KEY"],
        )

    def search(
        self,
        query: str,
        limit: int = 10,
        tiers: list[str] | None = None,
        recency_days: int | None = None,
    ) -> list[dict]:
        """Search across all memory tiers.

        Args:
            query: Natural language search query
            limit: Max results per tier
            tiers: Which tiers to search ["session", "work", "learning", "structured"]
                   Default: all tiers
            recency_days: Only return results from the last N days
        """
        tiers = tiers or ["session", "work", "learning", "structured"]
        results = []

        if "session" in tiers:
            results.extend(self._search_session(query, limit))

        if "structured" in tiers:
            results.extend(self._search_supabase_vector(query, limit, recency_days))
            results.extend(self._search_supabase_keyword(query, limit, recency_days))

        if "work" in tiers:
            results.extend(self._search_work_files(query, limit))

        if "learning" in tiers:
            results.extend(self._search_learning_files(query, limit))

        # Deduplicate by content similarity
        results = self._deduplicate(results)

        # Sort by relevance score (descending)
        results.sort(key=lambda r: r.get("score", 0), reverse=True)

        return results[:limit * 2]  # Return up to 2x limit across all tiers

    def _search_session(self, query: str, limit: int) -> list[dict]:
        """Search LosslessClaw DAG for recent conversation context."""
        try:
            # Use lcm_grep via OpenClaw CLI
            result = subprocess.run(
                ["openclaw", "run", "lcm_grep", "--query", query, "--limit", str(limit)],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                matches = json.loads(result.stdout)
                return [
                    {"tier": "session", "content": m.get("content", ""),
                     "score": m.get("relevance", 0.5), "source": "losslesclaw"}
                    for m in matches
                ]
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pass
        return []

    def _search_supabase_vector(self, query: str, limit: int, recency_days: int | None) -> list[dict]:
        """Vector similarity search on Supabase (Voyage AI embeddings)."""
        try:
            # Use Supabase RPC for vector search
            from rag_engine.embedder import Embedder
            embedder = Embedder()
            query_embedding = embedder.embed_query(query)

            # Search episodic
            rpc_params = {
                "query_embedding": query_embedding,
                "match_count": limit,
                "match_threshold": 0.3,
            }
            result = self.supabase.rpc("match_jake_episodic", rpc_params).execute()

            results = []
            for row in (result.data or []):
                results.append({
                    "tier": "structured",
                    "content": row.get("content", ""),
                    "score": row.get("similarity", 0.5),
                    "source": "jake_episodic",
                    "created_at": row.get("created_at"),
                    "memory_type": row.get("memory_type"),
                })
            return results
        except Exception:
            return []

    def _search_supabase_keyword(self, query: str, limit: int, recency_days: int | None) -> list[dict]:
        """Full-text keyword search on Supabase tables."""
        results = []
        for table in ["jake_episodic", "jake_semantic", "jake_procedural"]:
            try:
                q = self.supabase.table(table).select("content, importance, created_at, memory_type")
                q = q.ilike("content", f"%{query}%")
                if recency_days:
                    cutoff = (datetime.now() - timedelta(days=recency_days)).isoformat()
                    q = q.gte("created_at", cutoff)
                q = q.limit(limit)
                result = q.execute()

                for row in (result.data or []):
                    results.append({
                        "tier": "structured",
                        "content": row.get("content", ""),
                        "score": row.get("importance", 0.5),
                        "source": table,
                        "created_at": row.get("created_at"),
                    })
            except Exception:
                continue
        return results

    def _search_work_files(self, query: str, limit: int) -> list[dict]:
        """Search Work tier PRD files."""
        results = []
        work_dir = "pai/MEMORY/WORK"
        if not os.path.exists(work_dir):
            return results

        try:
            grep_result = subprocess.run(
                ["grep", "-rl", query, work_dir],
                capture_output=True, text=True, timeout=5,
            )
            for filepath in grep_result.stdout.strip().split("\n")[:limit]:
                if filepath and os.path.exists(filepath):
                    with open(filepath) as f:
                        content = f.read()[:500]
                    results.append({
                        "tier": "work",
                        "content": content,
                        "score": 0.6,
                        "source": filepath,
                    })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return results

    def _search_learning_files(self, query: str, limit: int) -> list[dict]:
        """Search Learning tier pattern files."""
        results = []
        learning_dir = "pai/MEMORY/LEARNING"
        if not os.path.exists(learning_dir):
            return results

        try:
            grep_result = subprocess.run(
                ["grep", "-rl", query, learning_dir],
                capture_output=True, text=True, timeout=5,
            )
            for filepath in grep_result.stdout.strip().split("\n")[:limit]:
                if filepath and os.path.exists(filepath):
                    with open(filepath) as f:
                        content = f.read()[:500]
                    results.append({
                        "tier": "learning",
                        "content": content,
                        "score": 0.7,  # Learning tier is higher value
                        "source": filepath,
                    })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return results

    def _deduplicate(self, results: list[dict]) -> list[dict]:
        """Remove duplicate results by content similarity."""
        seen = set()
        unique = []
        for r in results:
            content_key = r["content"][:100]
            if content_key not in seen:
                seen.add(content_key)
                unique.append(r)
        return unique
```

**Step 2: Create Supabase RPC function for vector search**

```sql
-- Run in Supabase SQL Editor
-- Creates the vector search function for episodic memories

CREATE OR REPLACE FUNCTION match_jake_episodic(
    query_embedding vector(1024),
    match_count int DEFAULT 10,
    match_threshold float DEFAULT 0.3
)
RETURNS TABLE (
    id uuid,
    content text,
    memory_type text,
    importance float,
    created_at timestamptz,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        je.id,
        je.content,
        je.memory_type,
        je.importance,
        je.created_at,
        1 - (je.embedding <=> query_embedding) AS similarity
    FROM jake_episodic je
    WHERE 1 - (je.embedding <=> query_embedding) > match_threshold
    ORDER BY je.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

Save this SQL to: `pai/migration/sql/match_jake_episodic.sql`

**Step 3: Commit**

```bash
git add pai/memory/ pai/migration/sql/
git commit -m "feat(pai): unified PAI retriever — replaces broken brain_search with LosslessClaw + Supabase vector/keyword search"
```

---

### Task 6: Build Consolidation Pipeline (Miessler-adapted)

**Files:**
- Create: `pai/memory/consolidator.py`

**Step 1: Create the PAI consolidation pipeline**

```python
# pai/memory/consolidator.py
"""PAI Memory Consolidation Pipeline.

Adapted from:
- jake_brain/consolidator.py (existing promotion rules)
- Miessler PAI WorkCompletionLearning hook (session → learning extraction)

Three consolidation cycles:
1. Session End → Work (create PRD from session, auto)
2. Work Completion → Learning (extract patterns, auto)
3. Learning Review → Wisdom (promote proven patterns, weekly + approval)
"""
import json
import os
from datetime import datetime
from pathlib import Path


class PAIConsolidator:
    """Manages memory promotion between tiers."""

    WORK_DIR = "pai/MEMORY/WORK"
    LEARNING_DIR = "pai/MEMORY/LEARNING"
    WISDOM_DIR = "pai/MEMORY/WISDOM"
    STATE_DIR = "pai/MEMORY/STATE"

    def create_work_session(self, session_id: str, description: str) -> str:
        """Create a new work session directory (Tier 2).

        Called by AutoWorkCreation hook equivalent.
        """
        session_dir = os.path.join(self.WORK_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        os.makedirs(os.path.join(session_dir, "artifacts"), exist_ok=True)

        # Create META.yaml
        meta = {
            "session_id": session_id,
            "description": description,
            "started_at": datetime.now().isoformat(),
            "status": "active",
            "tags": [],
        }
        with open(os.path.join(session_dir, "META.yaml"), "w") as f:
            import yaml
            yaml.dump(meta, f, default_flow_style=False)

        # Update state
        self._update_state(session_id, "active")
        return session_dir

    def close_work_session(self, session_id: str, rating: int = 0) -> dict:
        """Close a work session and extract learning.

        Called at session end. Triggers learning extraction.
        """
        session_dir = os.path.join(self.WORK_DIR, session_id)
        if not os.path.exists(session_dir):
            return {"error": "Session not found"}

        # Update META
        meta_path = os.path.join(session_dir, "META.yaml")
        if os.path.exists(meta_path):
            import yaml
            with open(meta_path) as f:
                meta = yaml.safe_load(f) or {}
            meta["ended_at"] = datetime.now().isoformat()
            meta["status"] = "completed"
            meta["rating"] = rating
            with open(meta_path, "w") as f:
                yaml.dump(meta, f, default_flow_style=False)

        # Record rating
        if rating > 0:
            self._record_rating(session_id, rating)

        # Extract learning
        learning = self._extract_learning(session_id)

        self._update_state(session_id, "completed")
        return {"session_id": session_id, "learning_extracted": learning}

    def _extract_learning(self, session_id: str) -> dict:
        """Extract learning patterns from a completed session.

        Equivalent to Miessler's WorkCompletionLearning hook.
        """
        session_dir = os.path.join(self.WORK_DIR, session_id)
        learning_file = os.path.join(
            self.LEARNING_DIR,
            f"{datetime.now().strftime('%Y-%m-%d')}-{session_id[:8]}.md",
        )

        # Read all artifacts from the session
        artifacts = []
        artifacts_dir = os.path.join(session_dir, "artifacts")
        if os.path.exists(artifacts_dir):
            for fname in os.listdir(artifacts_dir):
                fpath = os.path.join(artifacts_dir, fname)
                if os.path.isfile(fpath):
                    with open(fpath) as f:
                        artifacts.append({"name": fname, "content": f.read()[:1000]})

        # Write learning file (to be enriched by Claude at session end)
        with open(learning_file, "w") as f:
            f.write(f"# Learning Extract — {session_id}\n\n")
            f.write(f"**Session:** {session_id}\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
            f.write("## What Happened\n\n*(Auto-populated at session close)*\n\n")
            f.write("## What Worked\n\n\n")
            f.write("## What Didn't Work\n\n\n")
            f.write("## Patterns Detected\n\n\n")
            f.write("## Rules to Add/Update\n\n\n")
            if artifacts:
                f.write(f"\n## Artifacts ({len(artifacts)})\n\n")
                for a in artifacts:
                    f.write(f"- `{a['name']}`\n")

        return {"learning_file": learning_file, "artifacts_count": len(artifacts)}

    def _record_rating(self, session_id: str, rating: int):
        """Append a rating to the ratings ledger."""
        ratings_path = os.path.join(self.STATE_DIR, "ratings.jsonl")
        entry = {
            "session_id": session_id,
            "rating": rating,
            "timestamp": datetime.now().isoformat(),
        }
        with open(ratings_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def _update_state(self, session_id: str, status: str):
        """Update the work state registry."""
        state_path = os.path.join(self.STATE_DIR, "work.json")
        with open(state_path) as f:
            state = json.load(f)

        if status == "active":
            state["active_session"] = session_id
            state["total_sessions"] += 1
            state["sessions"].append({
                "id": session_id,
                "status": status,
                "started_at": datetime.now().isoformat(),
            })
        else:
            state["active_session"] = None
            for s in state["sessions"]:
                if s["id"] == session_id:
                    s["status"] = status
                    s["ended_at"] = datetime.now().isoformat()

        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)

    def weekly_synthesis(self) -> str:
        """Weekly learning synthesis — aggregate patterns, update WISDOM.

        Runs every Sunday. Reads all LEARNING files from the past 7 days,
        synthesizes common patterns, writes to WISDOM if pattern appears 3+ times.
        """
        learning_dir = self.LEARNING_DIR
        synthesis_file = os.path.join(
            self.WISDOM_DIR,
            f"synthesis-{datetime.now().strftime('%Y-W%V')}.md",
        )

        # Read recent learning files
        recent_files = []
        if os.path.exists(learning_dir):
            for fname in sorted(os.listdir(learning_dir)):
                if fname.endswith(".md"):
                    fpath = os.path.join(learning_dir, fname)
                    with open(fpath) as f:
                        recent_files.append({"name": fname, "content": f.read()})

        with open(synthesis_file, "w") as f:
            f.write(f"# Weekly Synthesis — {datetime.now().strftime('%Y-W%V')}\n\n")
            f.write(f"**Learning files reviewed:** {len(recent_files)}\n\n")
            f.write("## Cross-Session Patterns\n\n*(Requires Claude analysis)*\n\n")
            f.write("## Rules to Promote to WISDOM\n\n\n")
            f.write("## TELOS Updates Suggested\n\n\n")

        return synthesis_file
```

**Step 2: Commit**

```bash
git add pai/memory/consolidator.py
git commit -m "feat(pai): PAI consolidation pipeline — session→work→learning→wisdom promotion"
```

---

## Phase 1D: Hooks Integration

*Wire memory operations into Claude Code lifecycle hooks.*

### Task 7: Create Memory Hooks

**Files:**
- Create: `pai/hooks/session-start-memory.sh`
- Create: `pai/hooks/session-end-memory.sh`

**Step 1: Create session start hook (inject TELOS + recent learning)**

```bash
#!/bin/bash
# pai/hooks/session-start-memory.sh
# Injects TELOS context and recent learning into every session.

PAI_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TELOS_DIR="$PAI_DIR/TELOS"
LEARNING_DIR="$PAI_DIR/MEMORY/LEARNING"

echo "---"
echo "## TELOS Context (Identity)"
echo ""

# Inject key TELOS files
for file in MISSION.md GOALS.md PROJECTS.md CHALLENGES.md; do
    if [ -f "$TELOS_DIR/$file" ]; then
        echo "### $file"
        head -20 "$TELOS_DIR/$file"
        echo ""
    fi
done

# Inject recent learning (last 3 files)
echo "## Recent Learning"
echo ""
if [ -d "$LEARNING_DIR" ]; then
    ls -t "$LEARNING_DIR"/*.md 2>/dev/null | head -3 | while read -r f; do
        echo "### $(basename "$f")"
        head -10 "$f"
        echo ""
    done
fi

echo "---"
```

**Step 2: Create session end hook (trigger consolidation)**

```bash
#!/bin/bash
# pai/hooks/session-end-memory.sh
# Triggers memory consolidation at session end.

PAI_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SESSION_ID="${CLAUDE_SESSION_ID:-$(date +%s)}"

# Run consolidation (non-blocking)
cd "$PAI_DIR/.."
python -c "
from pai.memory.consolidator import PAIConsolidator
c = PAIConsolidator()
result = c.close_work_session('$SESSION_ID')
print(f'Session closed: {result}')
" 2>/dev/null &

echo "Memory consolidation triggered for session $SESSION_ID"
```

**Step 3: Wire hooks into .claude/settings.json**

Add to the existing hooks configuration:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "bash pai/hooks/session-start-memory.sh"
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "bash pai/hooks/session-end-memory.sh"
      }
    ]
  }
}
```

**Step 4: Commit**

```bash
chmod +x pai/hooks/*.sh
git add pai/hooks/
git commit -m "feat(pai): memory lifecycle hooks — TELOS injection at start, consolidation at end"
```

---

## Phase 1E: Verification

### Task 8: End-to-End Memory Verification

**Files:**
- Create: `pai/verification/v1-test-results.md`

**Step 1: Test retriever**

```bash
cd /Users/mikerodgers/Startup-Intelligence-OS
source susan-team-architect/backend/.venv/bin/activate
python -c "
from pai.memory.retriever import PAIRetriever
r = PAIRetriever()
results = r.search('Jacob football')
for result in results[:5]:
    print(f'[{result[\"tier\"]}] {result[\"content\"][:100]}')
"
```

Expected: Results from Supabase (structured tier) mentioning Jacob.

**Step 2: Test consolidation**

```bash
python -c "
from pai.memory.consolidator import PAIConsolidator
c = PAIConsolidator()
session = c.create_work_session('test-session-001', 'V1 verification test')
print(f'Created: {session}')
result = c.close_work_session('test-session-001', rating=4)
print(f'Closed: {result}')
"
```

Expected: Work directory created, learning file extracted, rating recorded.

**Step 3: Verify migration stats**

Check all migration stat files exist and show expected counts:
- `pai/migration/v1-baseline-counts.json`
- `pai/migration/v1-episodic-migration-stats.json`
- `pai/migration/v1-semantic-migration-stats.json`
- `pai/migration/v1-entity-migration-stats.json`

**Step 4: Verify brain_search is replaced**

Send via Telegram: "Jake, search your memory for anything about Oracle Health"

Expected: Uses PAIRetriever, NOT broken brain_search. Returns relevant results.

**Step 5: Document results**

Create `pai/verification/v1-test-results.md` with pass/fail for each test.

**Step 6: Commit**

```bash
git add pai/verification/v1-test-results.md
git commit -m "feat(pai): V1 memory migration verification complete"
```

---

## V1 Exit Criteria (All Must Pass)

- [ ] All 99K memories exported and baseline documented
- [ ] Memory audit report generated (duplicates, empties, stale data quantified)
- [ ] 3-tier memory directory structure created (WORK, LEARNING, WISDOM, STATE)
- [ ] Episodic records tagged with PAI tier classification
- [ ] Semantic records verified (all embeddings present or re-embedded)
- [ ] Top procedural rules exported to TELOS/LEARNED.md
- [ ] Entity/relationship graph verified (duplicates identified, orphans flagged)
- [ ] PAIRetriever works: LosslessClaw + Supabase vector + keyword search
- [ ] Supabase RPC function `match_jake_episodic` deployed
- [ ] Consolidation pipeline works: session create → close → learning extract
- [ ] Session start hook injects TELOS context
- [ ] Session end hook triggers consolidation
- [ ] brain_search is NOT called anywhere (replaced by PAIRetriever)
- [ ] Zero broken search calls for 48 hours

**Score target: 40 → 50** (memory accessible, consolidation active, nothing lost)
