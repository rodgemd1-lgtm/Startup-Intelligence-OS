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
**Access:** Supabase Python client with service_role key
**Embeddings:** Voyage AI `voyage-3` (1024 dimensions)
**Project:** Susan Intelligence OS (zqsdadnnpgqhehqxplio)

## Memory Flow
```
Live conversation -> LosslessClaw (Tier 1)
                  | (session end)
            Work PRD (Tier 2)
                  | (WorkCompletionLearning hook)
          Learning patterns (Tier 3)
                  | (consolidation pipeline)
          Supabase tables (structured long-term)
```

## Consolidation Rules
- Working -> Episodic: importance >= threshold (session end)
- Episodic -> Semantic: 3+ references to same fact within 14 days
- Patterns -> Procedural: detected across 3+ episodes (requires approval)

## Wisdom Layer
`pai/MEMORY/WISDOM/` holds accumulated wisdom frames — insights that transcend
individual sessions and inform Jake's worldview. Updated quarterly.
Migrated from TELOS/WISDOM.md when patterns are proven over time.

## Audit Baseline (2026-03-24)
- Total records: 99,204
- Unique records: ~19,919 (79.8% duplicates)
- Date range: Mar 20-24, 2026 (4 days of Hermes data)
- Largest table: jake_episodic (88,228 rows, 128MB)
