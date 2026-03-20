-- Jake's Cognitive Memory Engine — Phase 2: THE BRAIN
-- 6 tables: episodic, semantic, procedural, working, entities, relationships
-- 2 RPC functions: jake_brain_search, jake_entity_graph
-- Uses existing pgvector extension and Voyage AI 1024-dim embeddings

-- ============================================================
-- TABLE 1: jake_episodic — "What happened"
-- Time-stamped memories from conversations, meetings, events
-- ============================================================
CREATE TABLE jake_episodic (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  content TEXT NOT NULL,
  embedding VECTOR(1024),

  -- Temporal
  occurred_at TIMESTAMPTZ NOT NULL,
  session_id TEXT,

  -- Classification
  memory_type TEXT NOT NULL DEFAULT 'conversation'
    CHECK (memory_type IN ('conversation', 'meeting', 'event', 'observation', 'email', 'decision')),
  project TEXT,
  importance FLOAT DEFAULT 0.5 CHECK (importance >= 0 AND importance <= 1),

  -- Entities referenced (denormalized for fast filtering)
  people TEXT[] DEFAULT '{}',
  topics TEXT[] DEFAULT '{}',

  -- Consolidation tracking
  access_count INT DEFAULT 0,
  last_accessed_at TIMESTAMPTZ,
  promoted_to_semantic BOOLEAN DEFAULT FALSE,
  promotion_count INT DEFAULT 0,

  -- Source
  source TEXT,
  source_type TEXT DEFAULT 'hermes'
    CHECK (source_type IN ('hermes', 'claude-code', 'telegram', 'manual', 'calendar', 'email', 'ingestion')),
  metadata JSONB DEFAULT '{}',

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_episodic_hnsw ON jake_episodic USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_episodic_occurred ON jake_episodic (occurred_at DESC);
CREATE INDEX idx_episodic_project ON jake_episodic (project);
CREATE INDEX idx_episodic_type ON jake_episodic (memory_type);
CREATE INDEX idx_episodic_people ON jake_episodic USING gin (people);
CREATE INDEX idx_episodic_topics ON jake_episodic USING gin (topics);
CREATE INDEX idx_episodic_importance ON jake_episodic (importance DESC);
CREATE INDEX idx_episodic_not_promoted ON jake_episodic (promoted_to_semantic) WHERE NOT promoted_to_semantic;


-- ============================================================
-- TABLE 2: jake_semantic — "What I know"
-- Abstracted facts promoted from episodic memories
-- ============================================================
CREATE TABLE jake_semantic (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  content TEXT NOT NULL,
  embedding VECTOR(1024),

  -- Classification
  category TEXT NOT NULL
    CHECK (category IN ('person', 'preference', 'decision', 'pattern', 'fact', 'relationship', 'goal', 'rule')),
  confidence FLOAT DEFAULT 0.7 CHECK (confidence >= 0 AND confidence <= 1),

  -- Evidence tracking
  source_episodes UUID[] DEFAULT '{}',
  evidence_count INT DEFAULT 1,
  last_reinforced_at TIMESTAMPTZ,

  -- Contradiction handling
  supersedes UUID REFERENCES jake_semantic(id),
  superseded_by UUID REFERENCES jake_semantic(id),
  is_active BOOLEAN DEFAULT TRUE,

  -- Scope
  project TEXT,
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


-- ============================================================
-- TABLE 3: jake_procedural — "How to do things"
-- Learned patterns about what works and what doesn't
-- ============================================================
CREATE TABLE jake_procedural (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  content TEXT NOT NULL,
  embedding VECTOR(1024),

  -- Classification
  pattern_type TEXT NOT NULL
    CHECK (pattern_type IN ('workflow', 'preference', 'rule', 'anti-pattern', 'optimization', 'technique')),
  domain TEXT,

  -- Effectiveness tracking
  confidence FLOAT DEFAULT 0.6 CHECK (confidence >= 0 AND confidence <= 1),
  success_count INT DEFAULT 0,
  failure_count INT DEFAULT 0,
  effectiveness FLOAT GENERATED ALWAYS AS (
    CASE WHEN success_count + failure_count = 0 THEN 0.5
    ELSE success_count::FLOAT / (success_count + failure_count)
    END
  ) STORED,

  -- Evidence
  source_episodes UUID[] DEFAULT '{}',
  last_applied_at TIMESTAMPTZ,

  -- Approval gate
  approved BOOLEAN DEFAULT FALSE,
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


-- ============================================================
-- TABLE 4: jake_working — "Right now"
-- Current session buffer. Volatile.
-- ============================================================
CREATE TABLE jake_working (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  content TEXT NOT NULL,
  embedding VECTOR(1024),

  session_id TEXT NOT NULL,
  memory_type TEXT DEFAULT 'note'
    CHECK (memory_type IN ('note', 'decision', 'action', 'question', 'insight', 'preference')),
  importance FLOAT DEFAULT 0.5 CHECK (importance >= 0 AND importance <= 1),

  -- Promotion tracking
  promoted BOOLEAN DEFAULT FALSE,
  promoted_to TEXT CHECK (promoted_to IN ('episodic', 'semantic', 'procedural')),
  promoted_id UUID,

  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '24 hours'
);

CREATE INDEX idx_working_hnsw ON jake_working USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_working_session ON jake_working (session_id);
CREATE INDEX idx_working_expires ON jake_working (expires_at);


-- ============================================================
-- TABLE 5: jake_entities — Knowledge Graph Nodes
-- ============================================================
CREATE TABLE jake_entities (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  entity_type TEXT NOT NULL
    CHECK (entity_type IN ('person', 'family_member', 'company', 'project', 'meeting',
                           'decision', 'topic', 'pattern', 'goal', 'contact', 'event', 'location')),

  properties JSONB DEFAULT '{}',
  embedding VECTOR(1024),

  is_active BOOLEAN DEFAULT TRUE,
  importance FLOAT DEFAULT 0.5 CHECK (importance >= 0 AND importance <= 1),
  last_mentioned_at TIMESTAMPTZ,
  mention_count INT DEFAULT 0,

  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(name, entity_type)
);

CREATE INDEX idx_entities_hnsw ON jake_entities USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_entities_type ON jake_entities (entity_type);
CREATE INDEX idx_entities_name ON jake_entities (name);
CREATE INDEX idx_entities_active ON jake_entities (is_active) WHERE is_active;
CREATE INDEX idx_entities_importance ON jake_entities (importance DESC);
CREATE INDEX idx_entities_properties ON jake_entities USING gin (properties);


-- ============================================================
-- TABLE 6: jake_relationships — Knowledge Graph Edges
-- ============================================================
CREATE TABLE jake_relationships (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

  source_entity_id UUID NOT NULL REFERENCES jake_entities(id) ON DELETE CASCADE,
  target_entity_id UUID NOT NULL REFERENCES jake_entities(id) ON DELETE CASCADE,
  relationship_type TEXT NOT NULL
    CHECK (relationship_type IN ('works_at', 'parent_of', 'spouse_of', 'child_of',
                                  'stakeholder_of', 'decided_on', 'blocked_by', 'relates_to',
                                  'discussed_in', 'assigned_to', 'coaches', 'competes_with',
                                  'friend_of', 'manages', 'reports_to', 'sibling_of',
                                  'ex_spouse_of', 'named_after')),

  properties JSONB DEFAULT '{}',
  confidence FLOAT DEFAULT 0.8 CHECK (confidence >= 0 AND confidence <= 1),
  source_episodes UUID[] DEFAULT '{}',
  is_active BOOLEAN DEFAULT TRUE,

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(source_entity_id, target_entity_id, relationship_type)
);

CREATE INDEX idx_rel_source ON jake_relationships (source_entity_id);
CREATE INDEX idx_rel_target ON jake_relationships (target_entity_id);
CREATE INDEX idx_rel_type ON jake_relationships (relationship_type);
CREATE INDEX idx_rel_active ON jake_relationships (is_active) WHERE is_active;


-- ============================================================
-- RPC: jake_brain_search — Composite ranking across all layers
-- ============================================================
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
  layer TEXT,
  similarity FLOAT,
  importance FLOAT,
  composite_score FLOAT,
  metadata JSONB
) AS $$
BEGIN
  RETURN QUERY
  WITH all_memories AS (
    -- Working memory (1.3x weight)
    SELECT w.id, w.content, 'working'::TEXT AS layer,
      (1 - (w.embedding <=> query_embedding))::FLOAT AS similarity,
      w.importance::FLOAT,
      ((1 - (w.embedding <=> query_embedding)) * 1.3 * w.importance)::FLOAT AS composite_score,
      w.metadata
    FROM jake_working w
    WHERE NOT w.promoted
      AND w.expires_at > NOW()
      AND w.embedding IS NOT NULL

    UNION ALL

    -- Episodic memory (1.0x weight + recency decay + access boost)
    SELECT e.id, e.content, 'episodic'::TEXT,
      (1 - (e.embedding <=> query_embedding))::FLOAT,
      e.importance::FLOAT,
      ((1 - (e.embedding <=> query_embedding)) * 1.0 * e.importance
        * (1.0 / (1.0 + EXTRACT(EPOCH FROM (NOW() - e.occurred_at)) / 86400.0 / 30.0))
        * (1.0 + LEAST(e.access_count, 10) * 0.05))::FLOAT
      AS composite_score,
      e.metadata
    FROM jake_episodic e
    WHERE e.embedding IS NOT NULL
      AND (search_project IS NULL OR e.project = search_project)
      AND (search_people IS NULL OR e.people && search_people)
      AND (search_time_start IS NULL OR e.occurred_at >= search_time_start)
      AND (search_time_end IS NULL OR e.occurred_at <= search_time_end)

    UNION ALL

    -- Semantic memory (1.2x weight)
    SELECT s.id, s.content, 'semantic'::TEXT,
      (1 - (s.embedding <=> query_embedding))::FLOAT,
      s.confidence::FLOAT,
      ((1 - (s.embedding <=> query_embedding)) * 1.2 * s.confidence)::FLOAT AS composite_score,
      s.metadata
    FROM jake_semantic s
    WHERE s.is_active
      AND s.embedding IS NOT NULL
      AND (search_project IS NULL OR s.project IS NULL OR s.project = search_project)

    UNION ALL

    -- Procedural memory (1.5x weight)
    SELECT p.id, p.content, 'procedural'::TEXT,
      (1 - (p.embedding <=> query_embedding))::FLOAT,
      p.confidence::FLOAT,
      ((1 - (p.embedding <=> query_embedding)) * 1.5 * p.confidence * p.effectiveness)::FLOAT AS composite_score,
      p.metadata
    FROM jake_procedural p
    WHERE p.embedding IS NOT NULL
      AND (p.approved OR p.pattern_type = 'preference')
  )
  SELECT am.id, am.content, am.layer, am.similarity, am.importance, am.composite_score, am.metadata
  FROM all_memories am
  ORDER BY am.composite_score DESC
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- RPC: jake_entity_graph — Multi-hop entity traversal
-- ============================================================
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
    SELECT e.id AS entity_id, e.name AS entity_name, e.entity_type,
      'root'::TEXT AS relationship, 0 AS depth, e.properties
    FROM jake_entities e WHERE e.id = root_entity_id AND e.is_active

    UNION

    SELECT e2.id, e2.name, e2.entity_type,
      r.relationship_type, g.depth + 1, e2.properties
    FROM graph g
    JOIN jake_relationships r ON (r.source_entity_id = g.entity_id OR r.target_entity_id = g.entity_id) AND r.is_active
    JOIN jake_entities e2 ON e2.id = CASE
      WHEN r.source_entity_id = g.entity_id THEN r.target_entity_id
      ELSE r.source_entity_id
    END AND e2.is_active
    WHERE g.depth < max_depth
  )
  SELECT DISTINCT ON (g2.entity_id) g2.entity_id, g2.entity_name, g2.entity_type,
    g2.relationship, g2.depth, g2.properties
  FROM graph g2
  ORDER BY g2.entity_id, g2.depth;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- Helper: Auto-update updated_at timestamps
-- ============================================================
CREATE OR REPLACE FUNCTION jake_update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_episodic_updated BEFORE UPDATE ON jake_episodic
  FOR EACH ROW EXECUTE FUNCTION jake_update_timestamp();
CREATE TRIGGER trg_semantic_updated BEFORE UPDATE ON jake_semantic
  FOR EACH ROW EXECUTE FUNCTION jake_update_timestamp();
CREATE TRIGGER trg_procedural_updated BEFORE UPDATE ON jake_procedural
  FOR EACH ROW EXECUTE FUNCTION jake_update_timestamp();
CREATE TRIGGER trg_entities_updated BEFORE UPDATE ON jake_entities
  FOR EACH ROW EXECUTE FUNCTION jake_update_timestamp();
CREATE TRIGGER trg_relationships_updated BEFORE UPDATE ON jake_relationships
  FOR EACH ROW EXECUTE FUNCTION jake_update_timestamp();


-- ============================================================
-- Helper: Clean expired working memory
-- ============================================================
CREATE OR REPLACE FUNCTION jake_clean_expired_working()
RETURNS INT AS $$
DECLARE
  deleted_count INT;
BEGIN
  DELETE FROM jake_working WHERE expires_at < NOW() AND NOT promoted;
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;
