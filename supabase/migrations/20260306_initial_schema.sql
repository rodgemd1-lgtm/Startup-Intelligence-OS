-- Susan Team Architect — Supabase pgvector Schema
-- Run in Supabase Dashboard > SQL Editor

-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Core knowledge store
CREATE TABLE knowledge_chunks (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  content TEXT NOT NULL,
  embedding VECTOR(1024),
  company_id TEXT NOT NULL,
  agent_id TEXT,
  access_level TEXT DEFAULT 'company' CHECK (access_level IN ('public', 'company', 'agent_private')),
  data_type TEXT NOT NULL,
  source TEXT,
  source_url TEXT,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chunks_hnsw ON knowledge_chunks
  USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_chunks_company ON knowledge_chunks (company_id);
CREATE INDEX idx_chunks_agent ON knowledge_chunks (agent_id);
CREATE INDEX idx_chunks_type ON knowledge_chunks (data_type);
CREATE INDEX idx_chunks_access ON knowledge_chunks (access_level);

-- Company profiles
CREATE TABLE companies (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  domain TEXT,
  stage TEXT,
  profile JSONB NOT NULL DEFAULT '{}',
  team_manifest JSONB,
  dataset_requirements JSONB,
  execution_plan TEXT,
  be_audit JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent run cost tracking
CREATE TABLE agent_runs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  company_id TEXT NOT NULL REFERENCES companies(id),
  agent_id TEXT NOT NULL,
  phase TEXT,
  model TEXT NOT NULL,
  input_tokens INT,
  output_tokens INT,
  cost_usd DECIMAL(10,6),
  duration_ms INT,
  status TEXT DEFAULT 'success',
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_runs_company ON agent_runs (company_id);
CREATE INDEX idx_runs_agent ON agent_runs (agent_id);

-- Filtered similarity search function
CREATE OR REPLACE FUNCTION search_knowledge(
  query_embedding VECTOR(1024),
  filter_company TEXT,
  filter_access TEXT[] DEFAULT ARRAY['public', 'company'],
  filter_types TEXT[] DEFAULT NULL,
  filter_agent TEXT DEFAULT NULL,
  match_count INT DEFAULT 5
) RETURNS TABLE (
  id UUID,
  content TEXT,
  company_id TEXT,
  data_type TEXT,
  metadata JSONB,
  similarity FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    kc.id,
    kc.content,
    kc.company_id,
    kc.data_type,
    kc.metadata,
    1 - (kc.embedding <=> query_embedding) AS similarity
  FROM knowledge_chunks kc
  WHERE kc.company_id IN (filter_company, 'shared')
    AND kc.access_level = ANY(filter_access)
    AND (filter_types IS NULL OR kc.data_type = ANY(filter_types))
    AND (filter_agent IS NULL OR kc.agent_id IS NULL OR kc.agent_id = filter_agent)
  ORDER BY kc.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
