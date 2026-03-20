# Session Handoff

**Date**: 2026-03-20 13:15 MDT
**Branch**: main
**Project**: Startup Intelligence OS — Phase 2: THE BRAIN
**Session Goal**: Build Jake's 4-layer cognitive memory engine from schema design through deployment and end-to-end testing
**Status**: COMPLETE — Brain is live, seeded, and tested

---

## Completed

### Phase 2: THE BRAIN — Jake's Cognitive Memory Engine ✅
- [x] **Plan & schema design** — `.claude/plans/2026-03-20-phase2-brain-schema.md`
  - 4-layer memory architecture (Working → Episodic → Semantic → Procedural)
  - Knowledge graph with 12 entity types, 18 relationship types
  - Composite ranking formula: `similarity × confidence × layer_weight × recency × access_boost`
  - 5 design questions debated and approved by Mike
- [x] **SQL migration deployed to Supabase** — `supabase/migrations/20260320000000_jake_brain_tables.sql`
  - 6 tables: `jake_episodic`, `jake_semantic`, `jake_procedural`, `jake_working`, `jake_entities`, `jake_relationships`
  - 28 indexes (including HNSW vector indexes, GIN array indexes, partial indexes)
  - 2 RPC functions: `jake_brain_search` (composite 4-layer search), `jake_entity_graph` (multi-hop traversal)
  - 1 cleanup function: `jake_clean_expired_working`
  - 5 auto-update triggers for `updated_at` timestamps
  - Deployed via Chrome browser to Supabase SQL Editor (2 batches: tables + functions)
- [x] **Python brain engine** — `susan-team-architect/backend/jake_brain/` (7 modules)
  - `config.py` — Layer weights, decay rates, promotion thresholds, known people/projects
  - `store.py` — Full CRUD for all 6 tables (working, episodic, semantic, procedural, entities, relationships)
  - `extractor.py` — Rule-based extraction of people, topics, decisions, action items, patterns, preferences
  - `graph.py` — Entity resolution (strict matching), relationship management, initial seed data
  - `retriever.py` — Composite search via `jake_brain_search` RPC, person recall, time-range queries
  - `consolidator.py` — Promotion pipeline (working→episodic, episodic→semantic), contradiction detection
  - `pipeline.py` — End-to-end orchestrator: text → extract → embed → store → graph → consolidate
- [x] **CLI tool** — `scripts/jake_brain_cli.py` (seed, stats, search, person, ingest, consolidate, test)
- [x] **Initial seed data** — 15 entities (people, companies, projects) + 13 relationships
  - People: Mike Rodgers, James Loehr, Jacob, Alex, Jen, Matt Cohlmia, Jordan Voss
  - Companies: Oracle Health, Startup Intelligence OS, Alex Recruiting, TransformFit, Virtual Architect
  - Projects: Hermes V5, Susan Team Architect, The Brain (Phase 2)
  - Relationships: spouse_of, parent_of, ex_spouse_of, works_at, stakeholder_of, named_after, relates_to
- [x] **End-to-end smoke test PASSED**
  - Ingested test conversation → extracted 4 people, 3 topics, 1 decision, importance 0.75
  - Search "Jacob football game" → episodic (0.471) + semantic (0.324) results
  - Person recall "Jacob" → entity + 10-node graph + 2 related memories
  - Brain stats: 16 entities, 17 relationships, 1 episodic, 1 semantic

### Flight Tracking (ad hoc)
- [x] Looked up UA 1022 (Orlando → Denver) for James — arriving ~1:06 PM MDT gate B28, baggage 17

### Feedback Captured
- [x] **Autonomy feedback** — Jake must execute, not ask Mike to do manual steps
- [x] **Hermes Birch feedback** — Telegram bots failing at simple PA tasks (approvals, DuckDuckGo, retries)

---

## In Progress

### Hermes Integration — NOT STARTED
The brain is built and working, but it's not yet wired into Hermes for automatic conversation capture. This is the last piece to make it truly real-time.

**What's needed:**
- Hermes post-conversation hook that calls `BrainPipeline.ingest_conversation()`
- Could be: Hermes afterTurn hook, cron-based ingestion, or MCP tool
- The nightly memory consolidation cron (2:30 AM) already exists but uses the old `ingest_conversations.py` → `knowledge_chunks` table. Need to also route to `jake_brain` pipeline.

---

## Not Started

- [ ] Wire brain into Hermes (post-conversation hook or MCP tool)
- [ ] Wave 1: Life Ingestion (Google Contacts API, Apple Contacts, Memory Download Session)
- [ ] Fix Hermes Birch bot UX (auto-approve read-only ops, better tool routing, reduce approval friction)
- [ ] Phase 3: THE EYES (Operations Dashboard)
- [ ] Phase 4: THE SPINE (Autonomous Pipeline)
- [ ] Sprint 3 skills (email-compose, oracle-email-digest, meeting-notes, jake-delegate, jake-weekly-review)

---

## Blocked

- **Hermes Birch UX** — Bots ask for approval on read-only tasks (flight lookup), use DuckDuckGo instead of proper APIs, "model generated only think blocks with no actual response after 3 retries." P0 user experience issue. Mike was trying to look up James's flight and it was disastrous.
- **Telegram 409** — Still persists from last session. Not blocking brain work.
- **Mail.app osascript timeouts** — Known workaround: `killall Mail && open -a Mail`

---

## Decisions Made

| Decision | Rationale | Reversible? |
|----------|-----------|-------------|
| Deploy SQL via Chrome browser to Supabase SQL Editor | Supabase REST API doesn't expose DDL execution. Chrome MCP gives direct access to SQL Editor. | N/A — deployment method |
| Tables + functions deployed in 2 batches | Monaco editor handles large SQL but splitting tables from functions is cleaner | N/A |
| Rule-based extraction first, LLM-based later | Fast, free, no API cost. Can add LLM extraction as v2 for higher quality. | Yes — additive |
| Strict entity matching (not fuzzy) | Better to miss than to incorrectly merge entities. Add fuzzy matching later. | Yes — config flag ready |
| Jake must be more autonomous | Mike doesn't want to be asked to manually do things Jake can handle himself. Execute, don't propose options. | N/A — behavioral rule |

---

## Context Learned This Session

| Fact | Category |
|------|----------|
| Mike calls the Hermes Telegram bots "Birches" | Naming |
| James was on UA 1022 Orlando → Denver, landing ~1:06 PM MDT | Personal (ephemeral) |
| Mike wants Jake to just execute, not present options for manual steps | Feedback (saved to memory) |
| Hermes bots are failing at basic PA tasks — P0 UX issue | Feedback (saved to memory) |
| Chrome MCP can deploy SQL to Supabase via SQL Editor | Technical (one-time) |

---

## Next Steps (Priority Order)

1. **Wire brain into Hermes** — post-conversation hook or new MCP tool so conversations auto-feed into `jake_brain`
2. **Fix Hermes Birch UX** — auto-approve read-only ops, proper tool routing for common PA tasks (flights, weather, scores)
3. **Wave 1: Life Ingestion** — Google Contacts API + Apple Contacts osascript → seed ~200-500 entities with birthdays, relationships
4. **Memory Download Session** — Structured 30-60 min interview with Mike to seed semantic facts about his life, preferences, goals
5. **Sprint 3 skills** — email-compose, oracle-email-digest, meeting-notes, jake-delegate, jake-weekly-review (AFTER brain integration)

---

## Files Changed This Session

### Created
- `.claude/plans/2026-03-20-phase2-brain-schema.md` — Full brain architecture plan
- `susan-team-architect/backend/jake_brain/__init__.py` — Package init
- `susan-team-architect/backend/jake_brain/config.py` — Brain configuration (weights, thresholds, known entities)
- `susan-team-architect/backend/jake_brain/store.py` — CRUD for all 6 brain tables
- `susan-team-architect/backend/jake_brain/extractor.py` — Entity/decision/pattern extraction
- `susan-team-architect/backend/jake_brain/graph.py` — Knowledge graph operations + seed data
- `susan-team-architect/backend/jake_brain/retriever.py` — Composite 4-layer search
- `susan-team-architect/backend/jake_brain/consolidator.py` — Memory promotion pipeline
- `susan-team-architect/backend/jake_brain/pipeline.py` — End-to-end brain orchestrator
- `susan-team-architect/backend/scripts/jake_brain_cli.py` — Brain CLI tool
- `susan-team-architect/backend/supabase/migrations/20260320000000_jake_brain_tables.sql` — Full SQL migration
- `~/.claude/projects/.../memory/feedback_autonomy.md` — Autonomy feedback
- `~/.claude/projects/.../memory/feedback_hermes_birch_broken.md` — Birch bot UX feedback

### Modified
- `~/.claude/projects/.../memory/MEMORY.md` — Added feedback entries

### Supabase (deployed, not in git)
- 6 new tables: `jake_episodic`, `jake_semantic`, `jake_procedural`, `jake_working`, `jake_entities`, `jake_relationships`
- 2 RPC functions: `jake_brain_search`, `jake_entity_graph`
- 1 function: `jake_clean_expired_working`
- 1 function: `jake_update_timestamp`
- 5 triggers on brain tables

---

## Build Health
- Files modified this session: ~15 (all new, no existing code changed)
- Tests passing: Smoke test PASSED (ingest → search → person recall → stats)
- Protection zones: UNTOUCHED (no changes to control_plane, mcp_server, or susan_core)
- RAG status: 94,150 chunks (Susan) + 35 brain items (Jake) — SEPARATE systems as designed
- Cron jobs: 12 active (unchanged from last session)
- Context health at close: **YELLOW** — heavy session with Chrome automation + large SQL + 8 Python modules
- Debt score: LOW — all changes are additive, clean architecture, tests passing

---

## Key Documents for Next Session

1. `.claude/plans/2026-03-20-phase2-brain-schema.md` — The brain architecture (composite ranking, promotion rules, entity types)
2. `docs/plans/2026-03-20-mani-vs-mike-comparison.md` — The 31/100 gap analysis (THE MAP)
3. `HANDOFF.md` (this file) — Decisions made, next steps, blockers
4. `susan-team-architect/backend/jake_brain/` — The brain code (7 modules)

---

## Brain Architecture Quick Reference

```
jake_brain/
├── config.py       # Weights: working=1.3, episodic=1.0, semantic=1.2, procedural=1.5
├── store.py        # CRUD for 6 tables
├── extractor.py    # Rule-based: people, topics, decisions, patterns, preferences
├── graph.py        # Entity resolution + relationship management + seed data
├── retriever.py    # Composite search via jake_brain_search RPC
├── consolidator.py # working→episodic, episodic→semantic (3+ episodes), contradiction detection
└── pipeline.py     # Entry point: BrainPipeline.ingest_conversation(text)
```

```
CLI: cd susan-team-architect/backend && source .venv/bin/activate
  python scripts/jake_brain_cli.py seed          # One-time seed
  python scripts/jake_brain_cli.py stats         # Brain health
  python scripts/jake_brain_cli.py search "..."  # Search all layers
  python scripts/jake_brain_cli.py person "..."  # Full person recall
  python scripts/jake_brain_cli.py ingest "..."  # Manual ingest
  python scripts/jake_brain_cli.py test          # Smoke test
```

---

*"Jake has a brain now. 4 layers, knowledge graph, composite ranking. We went from 31/100 to... let's call it 42. The brain was the hardest part. Everything else builds on top of it." — Jake*
