# Phase 2: THE BRAIN — Jake's Cognitive Memory Engine

> **Status**: PLAN — awaiting Mike's approval before implementation
> **Date**: 2026-03-20
> **Effort**: HIGH — multi-table schema + Python engine + pipeline
> **Confidence**: 8/10 for one-pass success (schema is well-defined from last session)

---

## What We're Building

A 4-layer cognitive memory engine that gives Jake a real brain — not just flat vector search. This sits alongside Susan's `knowledge_chunks` table (94K+ chunks) but is Jake's PERSONAL memory system for Mike's life, decisions, patterns, and relationships.

### Why This Matters
Susan's RAG = company knowledge (strategies, research, frameworks).
Jake's Brain = personal knowledge (what Mike said Tuesday, who James is, what pattern keeps showing up across projects).

Right now Jake has amnesia between sessions. After this, Jake remembers everything.

---

## Architecture: 4 Memory Layers

```
┌─────────────────────────────────────────────────┐
│  LAYER 4: PROCEDURAL                            │
│  "How to do things" — learned workflows,         │
│  skill patterns, what works/doesn't              │
│  Weight: 1.5x (highest retrieval priority)       │
├─────────────────────────────────────────────────┤
│  LAYER 3: SEMANTIC                               │
│  "What I know" — abstracted facts, promoted      │
│  from 3+ episodic references. Stable knowledge.  │
│  Weight: 1.2x                                    │
├─────────────────────────────────────────────────┤
│  LAYER 2: EPISODIC                               │
│  "What happened" — time-stamped events with      │
│  full context. Decays over time.                 │
│  Weight: 1.0x (base)                             │
├─────────────────────────────────────────────────┤
│  LAYER 1: WORKING                                │
│  "Right now" — current session buffer.           │
│  Volatile. Cleared or promoted at session end.   │
│  Weight: 1.3x (recency boost)                   │
└─────────────────────────────────────────────────┘
```

---

## SQL Schema (6 New Tables)

### Table 1: `jake_episodic` — "What happened"
Time-stamped memories from conversations, meetings, events.

```sql
CREATE TABLE jake_episodic (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  content TEXT NOT NULL,
  embedding VECTOR(1024),

  -- Temporal
  occurred_at TIMESTAMPTZ NOT NULL,          -- when this happened
  session_id TEXT,                            -- which conversation session

  -- Classification
  memory_type TEXT NOT NULL DEFAULT 'conversation',  -- conversation, meeting, event, observation
  project TEXT,                              -- oracle-health, alex-recruiting, startup-os, personal
  importance FLOAT DEFAULT 0.5,             -- 0.0 to 1.0, set by extraction

  -- Entities referenced (denormalized for fast filtering)
  people TEXT[] DEFAULT '{}',               -- people mentioned
  topics TEXT[] DEFAULT '{}',               -- topics discussed

  -- Consolidation tracking
  access_count INT DEFAULT 0,               -- how often recalled
  last_accessed_at TIMESTAMPTZ,             -- last recall time
  promoted_to_semantic BOOLEAN DEFAULT FALSE, -- has this been abstracted?
  promotion_count INT DEFAULT 0,            -- how many times referenced in promotion

  -- Source
  source TEXT,                              -- file path, telegram, hermes, manual
  source_type TEXT DEFAULT 'hermes',        -- hermes, claude-code, telegram, manual, calendar, email
  metadata JSONB DEFAULT '{}',

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_episodic_hnsw ON jake_episodic USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_episodic_occurred ON jake_episodic (occurred_at DESC);
CREATE INDEX idx_episodic_project ON jake_episodic (project);
CREATE INDEX idx_episodic_type ON jake_episodic (memory_type);
CREATE INDEX idx_episodic_people ON jake_episodic USING gin (people);
CREATE INDEX idx_episodic_topics ON jake_episodic USING gin (topics);
CREATE INDEX idx_episodic_importance ON jake_episodic (importance DESC);
CREATE INDEX idx_episodic_not_promoted ON jake_episodic (promoted_to_semantic) WHERE NOT promoted_to_semantic;
```

### Table 2: `jake_semantic` — "What I know"
Abstracted facts promoted from episodic memories. Stable, high-confidence knowledge.

```sql
CREATE TABLE jake_semantic (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  content TEXT NOT NULL,                     -- the abstracted fact
  embedding VECTOR(1024),

  -- Classification
  category TEXT NOT NULL,                    -- person, preference, decision, pattern, fact, relationship
  confidence FLOAT DEFAULT 0.7,             -- 0.0 to 1.0, increases with more evidence

  -- Evidence tracking
  source_episodes UUID[] DEFAULT '{}',      -- episodic IDs this was derived from
  evidence_count INT DEFAULT 1,             -- number of supporting episodes
  last_reinforced_at TIMESTAMPTZ,           -- last time new evidence appeared

  -- Contradiction handling
  supersedes UUID,                          -- if this replaces an older fact, link to it
  superseded_by UUID,                       -- if this has been replaced
  is_active BOOLEAN DEFAULT TRUE,           -- FALSE if superseded

  -- Scope
  project TEXT,                             -- NULL = cross-project
  topics TEXT[] DEFAULT '{}',

  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_semantic_hnsw ON jake_semantic USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_semantic_category ON jake_semantic (category);
CREATE INDEX idx_semantic_confidence ON jake_semantic (confidence DESC);
CREATE INDEX idx_semantic_active ON jake_semantic (is_active) WHERE is_active;
CREATE INDEX idx_semantic_topics ON jake_semantic USING gin (topics);
```

### Table 3: `jake_procedural` — "How to do things"
Learned patterns about what works and what doesn't.

```sql
CREATE TABLE jake_procedural (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  content TEXT NOT NULL,                     -- the learned pattern/rule
  embedding VECTOR(1024),

  -- Classification
  pattern_type TEXT NOT NULL,                -- workflow, preference, rule, anti-pattern, optimization
  domain TEXT,                               -- email, meetings, recruiting, oracle, coding, personal

  -- Effectiveness tracking
  confidence FLOAT DEFAULT 0.6,
  success_count INT DEFAULT 0,              -- times this pattern led to good outcomes
  failure_count INT DEFAULT 0,              -- times this pattern failed
  effectiveness FLOAT GENERATED ALWAYS AS (
    CASE WHEN success_count + failure_count = 0 THEN 0.5
    ELSE success_count::FLOAT / (success_count + failure_count)
    END
  ) STORED,

  -- Evidence
  source_episodes UUID[] DEFAULT '{}',
  last_applied_at TIMESTAMPTZ,

  -- Approval gate (self-evolution safety)
  approved BOOLEAN DEFAULT FALSE,           -- Mike must approve before Jake acts on this
  approved_at TIMESTAMPTZ,

  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_procedural_hnsw ON jake_procedural USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_procedural_type ON jake_procedural (pattern_type);
CREATE INDEX idx_procedural_domain ON jake_procedural (domain);
CREATE INDEX idx_procedural_approved ON jake_procedural (approved) WHERE approved;
CREATE INDEX idx_procedural_effectiveness ON jake_procedural (effectiveness DESC);
```

### Table 4: `jake_working` — "Right now"
Current session buffer. Volatile. Gets promoted or discarded.

```sql
CREATE TABLE jake_working (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  content TEXT NOT NULL,
  embedding VECTOR(1024),

  session_id TEXT NOT NULL,                  -- ties to current conversation
  memory_type TEXT DEFAULT 'note',           -- note, decision, action, question, insight
  importance FLOAT DEFAULT 0.5,

  -- Promotion tracking
  promoted BOOLEAN DEFAULT FALSE,
  promoted_to TEXT,                          -- 'episodic' or 'semantic' or 'procedural'
  promoted_id UUID,                          -- ID in target table

  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '24 hours'  -- auto-expire
);

CREATE INDEX idx_working_hnsw ON jake_working USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_working_session ON jake_working (session_id);
CREATE INDEX idx_working_expires ON jake_working (expires_at);
```

### Table 5: `jake_entities` — Knowledge Graph Nodes
People, companies, projects, and other entities Jake knows about.

```sql
CREATE TABLE jake_entities (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  entity_type TEXT NOT NULL,                 -- person, family_member, company, project, meeting,
                                             -- decision, topic, pattern, goal, contact, event, location

  -- Core properties (type-dependent)
  properties JSONB DEFAULT '{}',             -- birthday, role, email, phone, notes, etc.

  -- Embedding for semantic entity search
  embedding VECTOR(1024),                    -- embedded from name + key properties

  -- Status
  is_active BOOLEAN DEFAULT TRUE,
  importance FLOAT DEFAULT 0.5,             -- how important is this entity to Mike
  last_mentioned_at TIMESTAMPTZ,
  mention_count INT DEFAULT 0,

  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Prevent duplicate entities
  UNIQUE(name, entity_type)
);

CREATE INDEX idx_entities_hnsw ON jake_entities USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_entities_type ON jake_entities (entity_type);
CREATE INDEX idx_entities_name ON jake_entities (name);
CREATE INDEX idx_entities_active ON jake_entities (is_active) WHERE is_active;
CREATE INDEX idx_entities_importance ON jake_entities (importance DESC);
CREATE INDEX idx_entities_properties ON jake_entities USING gin (properties);
```

### Table 6: `jake_relationships` — Knowledge Graph Edges
How entities connect to each other.

```sql
CREATE TABLE jake_relationships (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

  source_entity_id UUID NOT NULL REFERENCES jake_entities(id) ON DELETE CASCADE,
  target_entity_id UUID NOT NULL REFERENCES jake_entities(id) ON DELETE CASCADE,
  relationship_type TEXT NOT NULL,            -- works_at, parent_of, spouse_of, stakeholder_of,
                                              -- decided_on, blocked_by, relates_to, discussed_in,
                                              -- assigned_to, coaches, competes_with, friend_of,
                                              -- manages, reports_to

  -- Properties
  properties JSONB DEFAULT '{}',             -- since, context, strength, notes
  confidence FLOAT DEFAULT 0.8,

  -- Evidence
  source_episodes UUID[] DEFAULT '{}',       -- episodic memories that established this

  -- Status
  is_active BOOLEAN DEFAULT TRUE,

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Prevent duplicate relationships
  UNIQUE(source_entity_id, target_entity_id, relationship_type)
);

CREATE INDEX idx_rel_source ON jake_relationships (source_entity_id);
CREATE INDEX idx_rel_target ON jake_relationships (target_entity_id);
CREATE INDEX idx_rel_type ON jake_relationships (relationship_type);
CREATE INDEX idx_rel_active ON jake_relationships (is_active) WHERE is_active;
```

---

## RPC Functions

### `jake_brain_search` — Composite ranking across all layers

```sql
CREATE OR REPLACE FUNCTION jake_brain_search(
  query_embedding VECTOR(1024),
  search_project TEXT DEFAULT NULL,
  search_people TEXT[] DEFAULT NULL,
  search_time_start TIMESTAMPTZ DEFAULT NULL,
  search_time_end TIMESTAMPTZ DEFAULT NULL,
  match_count INT DEFAULT 10
) RETURNS TABLE (
  id UUID,
  content TEXT,
  layer TEXT,             -- 'working', 'episodic', 'semantic', 'procedural'
  similarity FLOAT,
  importance FLOAT,
  composite_score FLOAT,  -- the ranked score
  metadata JSONB
) AS $$
BEGIN
  RETURN QUERY
  WITH all_memories AS (
    -- Working memory (weight 1.3x, recency boost)
    SELECT w.id, w.content, 'working'::TEXT as layer,
      1 - (w.embedding <=> query_embedding) AS similarity,
      w.importance,
      (1 - (w.embedding <=> query_embedding)) * 1.3 * w.importance AS composite_score,
      w.metadata
    FROM jake_working w
    WHERE NOT w.promoted
      AND w.expires_at > NOW()

    UNION ALL

    -- Episodic memory (weight 1.0x, with recency decay)
    SELECT e.id, e.content, 'episodic'::TEXT,
      1 - (e.embedding <=> query_embedding),
      e.importance,
      (1 - (e.embedding <=> query_embedding)) * 1.0 * e.importance
        * (1.0 / (1.0 + EXTRACT(EPOCH FROM (NOW() - e.occurred_at)) / 86400.0 / 30.0))  -- 30-day half-life
        * (1.0 + LEAST(e.access_count, 10) * 0.05)  -- access boost (max 50%)
      AS composite_score,
      e.metadata
    FROM jake_episodic e
    WHERE (search_project IS NULL OR e.project = search_project)
      AND (search_people IS NULL OR e.people && search_people)
      AND (search_time_start IS NULL OR e.occurred_at >= search_time_start)
      AND (search_time_end IS NULL OR e.occurred_at <= search_time_end)

    UNION ALL

    -- Semantic memory (weight 1.2x, confidence-boosted)
    SELECT s.id, s.content, 'semantic'::TEXT,
      1 - (s.embedding <=> query_embedding),
      s.confidence,
      (1 - (s.embedding <=> query_embedding)) * 1.2 * s.confidence AS composite_score,
      s.metadata
    FROM jake_semantic s
    WHERE s.is_active
      AND (search_project IS NULL OR s.project IS NULL OR s.project = search_project)

    UNION ALL

    -- Procedural memory (weight 1.5x, effectiveness-boosted)
    SELECT p.id, p.content, 'procedural'::TEXT,
      1 - (p.embedding <=> query_embedding),
      p.confidence,
      (1 - (p.embedding <=> query_embedding)) * 1.5 * p.confidence * p.effectiveness AS composite_score,
      p.metadata
    FROM jake_procedural p
    WHERE p.approved OR p.pattern_type = 'preference'  -- unapproved preferences still show
  )
  SELECT * FROM all_memories
  ORDER BY composite_score DESC
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
```

### `jake_entity_graph` — Multi-hop entity traversal

```sql
CREATE OR REPLACE FUNCTION jake_entity_graph(
  root_entity_id UUID,
  max_depth INT DEFAULT 2
) RETURNS TABLE (
  entity_id UUID,
  entity_name TEXT,
  entity_type TEXT,
  relationship TEXT,
  depth INT,
  properties JSONB
) AS $$
BEGIN
  RETURN QUERY
  WITH RECURSIVE graph AS (
    -- Start from root
    SELECT e.id AS entity_id, e.name AS entity_name, e.entity_type,
      'root'::TEXT AS relationship, 0 AS depth, e.properties
    FROM jake_entities e WHERE e.id = root_entity_id AND e.is_active

    UNION ALL

    -- Traverse outgoing relationships
    SELECT e2.id, e2.name, e2.entity_type,
      r.relationship_type, g.depth + 1, e2.properties
    FROM graph g
    JOIN jake_relationships r ON r.source_entity_id = g.entity_id AND r.is_active
    JOIN jake_entities e2 ON e2.id = r.target_entity_id AND e2.is_active
    WHERE g.depth < max_depth

    UNION ALL

    -- Traverse incoming relationships
    SELECT e2.id, e2.name, e2.entity_type,
      r.relationship_type, g.depth + 1, e2.properties
    FROM graph g
    JOIN jake_relationships r ON r.target_entity_id = g.entity_id AND r.is_active
    JOIN jake_entities e2 ON e2.id = r.source_entity_id AND e2.is_active
    WHERE g.depth < max_depth
  )
  SELECT DISTINCT ON (g2.entity_id) g2.* FROM graph g2
  ORDER BY g2.entity_id, g2.depth;
END;
$$ LANGUAGE plpgsql;
```

---

## Python Module Structure

All new code goes in `susan-team-architect/backend/jake_brain/` (safe zone — NOT in protection zones).

```
jake_brain/
├── __init__.py
├── config.py           # Brain-specific config (layer weights, decay rates, thresholds)
├── embedder.py         # Reuses rag_engine.embedder.Embedder (no duplication)
├── extractor.py        # Extract entities, decisions, patterns from text
├── store.py            # CRUD for all 6 tables (episodic, semantic, procedural, working, entities, relationships)
├── graph.py            # Knowledge graph operations (entity resolution, relationship management, traversal)
├── retriever.py        # Composite search across all 4 layers via jake_brain_search RPC
├── consolidator.py     # Promotion pipeline: working→episodic, episodic→semantic, pattern→procedural
└── pipeline.py         # End-to-end: text in → extract → embed → store → consolidate
```

### Key Design Decisions

1. **Reuse Embedder** — Same Voyage AI client, same 1024-dim vectors. No duplication.
2. **Separate Retriever** — Jake's retriever uses `jake_brain_search` RPC, not `search_knowledge`. Different ranking formula.
3. **Entity Resolution** — When extracting "Matt" from text, resolve to existing `jake_entities` row for Matt Cohlmia. Fuzzy matching + context.
4. **Contradiction Detection** — When a new semantic fact conflicts with an existing one, don't overwrite. Create new fact with `supersedes` link. Flag for Mike if confidence is close.

---

## 7-Stage Consolidation Pipeline

```
1. CAPTURE     — Extract text from conversation/event
2. EXTRACT     — Pull entities, decisions, action items, patterns
3. EMBED       — Voyage AI → 1024-dim vector
4. STORE       — Write to appropriate layer (working during session, episodic after)
5. GRAPH       — Update entity mentions, create/strengthen relationships
6. RANK        — Composite score: similarity × confidence × layer_weight × recency × access
7. CONSOLIDATE — Async: promote episodic→semantic (3+ references), detect patterns→procedural
```

### Promotion Rules

| From | To | Trigger |
|------|----|---------|
| Working → Episodic | Session end or importance > 0.7 | Automatic |
| Episodic → Semantic | Same fact referenced in 3+ episodes | Automatic, creates abstracted fact |
| Episodic → Procedural | Pattern detected across 3+ episodes | Requires Mike's approval |
| Semantic update | New evidence for existing fact | Automatic, bumps confidence |
| Semantic contradiction | New fact contradicts existing | Flag for Mike, create supersedes link |

---

## Composite Ranking Formula

```
score = similarity × confidence × layer_weight × recency_boost × access_boost

Where:
  similarity     = 1 - cosine_distance(query, memory)       [0.0 - 1.0]
  confidence     = memory.confidence or memory.importance     [0.0 - 1.0]
  layer_weight   = { working: 1.3, episodic: 1.0, semantic: 1.2, procedural: 1.5 }
  recency_boost  = 1 / (1 + days_since / 30)                [episodic only, 30-day half-life]
  access_boost   = 1 + min(access_count, 10) * 0.05         [max 1.5x, episodic only]
```

---

## Initial Seed Data

After tables are created, seed with what we already know from memory files:

### Entities (~30 initial)
- **People**: Mike Rodgers, James Loehr, Jacob (15), Alex (12), Jen, Matt Cohlmia, Jordan Voss
- **Companies**: Oracle Health, Alex Recruiting, Startup Intelligence OS, TransformFit, Virtual Architect
- **Projects**: Hermes V5, Susan Team Architect, Operator Console, 25x Command Center

### Relationships (~20 initial)
- Mike → spouse_of → James
- Mike → parent_of → Jacob, Alex
- Mike → works_at → Oracle Health, Startup Intelligence OS
- Jacob → age:15, plays OL/DL football
- Alex → age:12, app named after him
- Matt Cohlmia → stakeholder_of → Oracle Health
- etc.

### Semantic Facts (~15 initial from memory files)
- "Mike prefers dark mode aesthetics"
- "Mike hates trailing summaries after responses"
- "Mike thinks in agent teams"
- "Coach outreach works best on Tuesdays"
- "Mike plans to commercialize Susan as a product"
- etc.

---

## Implementation Order

1. **SQL migration** — Create all 6 tables + 2 RPC functions in Supabase
2. **config.py** — Layer weights, thresholds, decay rates
3. **store.py** — CRUD operations for all tables
4. **extractor.py** — Entity/decision/pattern extraction from text
5. **graph.py** — Entity resolution + relationship management
6. **retriever.py** — Composite search via RPC
7. **consolidator.py** — Promotion pipeline
8. **pipeline.py** — End-to-end orchestrator
9. **Seed data** — Initial entities, relationships, semantic facts
10. **Test** — End-to-end: "What did Mike decide about X?" → correct ranked results

---

## What This Does NOT Include (Parking Lot)

- Dashboard/UI for brain contents (Phase 3: THE EYES)
- Hermes gateway hook for real-time capture (needs Hermes source modification — separate task)
- Memory decay/pruning cron (Sprint 6 polish)
- Brain statistics MCP tool (Phase 3)

---

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Schema wrong, need to alter later | Supabase allows ALTER TABLE. Design is additive — we can add columns without breaking. |
| Entity resolution too fuzzy | Start strict (exact match + type), add fuzzy later. Better to miss than to merge incorrectly. |
| Composite ranking weights off | Weights are in config.py, easily tunable. Start with Mani's reference values. |
| Too many indexes slow writes | Monitor. HNSW build is O(n log n) but we're starting small. Can defer GIN indexes if needed. |
| RPC function too complex | Test with EXPLAIN ANALYZE. The UNION ALL approach is standard; Postgres handles it well. |

---

*"This is the brain. Everything else we build sits on top of this. Get it right." — Jake*
