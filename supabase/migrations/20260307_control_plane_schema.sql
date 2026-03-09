-- Startup Intelligence Cockpit control-plane schema
-- Extends the initial Susan knowledge store with typed operator-plane tables.

CREATE TABLE IF NOT EXISTS sources (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  tenant_id TEXT NOT NULL DEFAULT 'shared',
  layer_id TEXT NOT NULL CHECK (layer_id IN ('layer_1', 'layer_2', 'layer_3', 'layer_4', 'layer_5')),
  source_type TEXT NOT NULL,
  title TEXT NOT NULL,
  source_url TEXT,
  source_path TEXT,
  freshness_cadence TEXT DEFAULT 'quarterly',
  freshness_status TEXT DEFAULT 'unknown',
  captured_at TIMESTAMPTZ,
  effective_date TIMESTAMPTZ,
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sources_tenant ON sources (tenant_id);
CREATE INDEX IF NOT EXISTS idx_sources_layer ON sources (layer_id);

CREATE TABLE IF NOT EXISTS evidence_nodes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  source_id UUID REFERENCES sources(id) ON DELETE CASCADE,
  tenant_id TEXT NOT NULL DEFAULT 'shared',
  title TEXT NOT NULL,
  excerpt TEXT,
  confidence NUMERIC(4,3) DEFAULT 0.0,
  verification_status TEXT DEFAULT 'unverified',
  evidence_grade TEXT DEFAULT 'strong_secondary',
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evidence_nodes_source ON evidence_nodes (source_id);
CREATE INDEX IF NOT EXISTS idx_evidence_nodes_tenant ON evidence_nodes (tenant_id);

CREATE TABLE IF NOT EXISTS claims (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  tenant_id TEXT NOT NULL DEFAULT 'shared',
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  field_name TEXT NOT NULL,
  value TEXT NOT NULL,
  as_of_date TIMESTAMPTZ,
  confidence NUMERIC(4,3) DEFAULT 0.0,
  contradiction_state TEXT DEFAULT 'unknown',
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_claims_entity ON claims (entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_claims_tenant ON claims (tenant_id);

CREATE TABLE IF NOT EXISTS claim_evidence (
  claim_id UUID REFERENCES claims(id) ON DELETE CASCADE,
  evidence_node_id UUID REFERENCES evidence_nodes(id) ON DELETE CASCADE,
  PRIMARY KEY (claim_id, evidence_node_id)
);

CREATE TABLE IF NOT EXISTS protocols (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  tenant_id TEXT NOT NULL DEFAULT 'shared',
  name TEXT NOT NULL,
  family TEXT NOT NULL,
  status TEXT DEFAULT 'active',
  source_path TEXT,
  summary TEXT,
  owners TEXT[] DEFAULT '{}',
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS prompt_bundles (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  tenant_id TEXT NOT NULL DEFAULT 'shared',
  bundle_key TEXT NOT NULL,
  name TEXT NOT NULL,
  source_agent TEXT NOT NULL,
  active_version_id UUID,
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_prompt_bundles_key ON prompt_bundles (tenant_id, bundle_key);

CREATE TABLE IF NOT EXISTS prompt_versions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  bundle_id UUID REFERENCES prompt_bundles(id) ON DELETE CASCADE,
  tenant_id TEXT NOT NULL DEFAULT 'shared',
  version TEXT NOT NULL,
  digest TEXT NOT NULL,
  status TEXT DEFAULT 'draft',
  meta_policy TEXT NOT NULL,
  agent_kernel TEXT NOT NULL,
  task_program TEXT NOT NULL,
  context_pack TEXT NOT NULL,
  critic_program TEXT NOT NULL,
  source_paths TEXT[] DEFAULT '{}',
  compiled_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_prompt_versions_bundle_version ON prompt_versions (bundle_id, version);

ALTER TABLE prompt_bundles
  ADD CONSTRAINT prompt_bundles_active_version_fk
  FOREIGN KEY (active_version_id) REFERENCES prompt_versions(id);

CREATE TABLE IF NOT EXISTS prompt_evals (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  prompt_version_id UUID REFERENCES prompt_versions(id) ON DELETE CASCADE,
  tenant_id TEXT NOT NULL DEFAULT 'shared',
  schema_valid BOOLEAN DEFAULT FALSE,
  citations_present BOOLEAN DEFAULT FALSE,
  eval_passed BOOLEAN DEFAULT FALSE,
  ready_for_promotion BOOLEAN DEFAULT FALSE,
  failures JSONB NOT NULL DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_capabilities (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  tenant_id TEXT NOT NULL DEFAULT 'shared',
  agent_id TEXT NOT NULL,
  role TEXT NOT NULL,
  agent_group TEXT NOT NULL,
  authored BOOLEAN DEFAULT FALSE,
  registered BOOLEAN DEFAULT FALSE,
  prompt_status TEXT DEFAULT 'missing',
  required_data_types TEXT[] DEFAULT '{}',
  missing_data_types TEXT[] DEFAULT '{}',
  gap_count INT DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}',
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_agent_capabilities_agent ON agent_capabilities (tenant_id, agent_id);

CREATE TABLE IF NOT EXISTS coverage_gaps (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  tenant_id TEXT NOT NULL DEFAULT 'shared',
  gap_key TEXT NOT NULL,
  gap_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  title TEXT NOT NULL,
  detail TEXT NOT NULL,
  owner TEXT,
  layer_id TEXT,
  evidence TEXT[] DEFAULT '{}',
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_coverage_gaps_key ON coverage_gaps (tenant_id, gap_key);

CREATE TABLE IF NOT EXISTS mcp_servers (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  server_key TEXT NOT NULL UNIQUE,
  tenant_id TEXT NOT NULL DEFAULT 'shared',
  name TEXT NOT NULL,
  transport TEXT NOT NULL,
  status TEXT NOT NULL,
  health TEXT DEFAULT 'unknown',
  scopes TEXT[] DEFAULT '{}',
  tools_count INT DEFAULT 0,
  command TEXT,
  endpoint TEXT,
  dependent_workflows TEXT[] DEFAULT '{}',
  metadata JSONB NOT NULL DEFAULT '{}',
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mcp_tools (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  tool_key TEXT NOT NULL UNIQUE,
  server_id UUID REFERENCES mcp_servers(id) ON DELETE CASCADE,
  tenant_id TEXT NOT NULL DEFAULT 'shared',
  name TEXT NOT NULL,
  description TEXT,
  status TEXT NOT NULL,
  tenant_scoped BOOLEAN DEFAULT FALSE,
  latency_ms INT,
  failure_rate NUMERIC(6,3),
  metadata JSONB NOT NULL DEFAULT '{}',
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS run_traces (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  trace_key TEXT NOT NULL UNIQUE,
  tenant_id TEXT NOT NULL DEFAULT 'shared',
  kind TEXT NOT NULL,
  status TEXT NOT NULL,
  started_at TIMESTAMPTZ NOT NULL,
  finished_at TIMESTAMPTZ,
  prompt_version_id UUID REFERENCES prompt_versions(id),
  retrieval_lanes TEXT[] DEFAULT '{}',
  model_route TEXT,
  tool_names TEXT[] DEFAULT '{}',
  cost_usd NUMERIC(10,6),
  quality_score NUMERIC(6,3),
  metadata JSONB NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_run_traces_tenant ON run_traces (tenant_id, started_at DESC);

CREATE TABLE IF NOT EXISTS routing_policies (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  policy_key TEXT NOT NULL UNIQUE,
  tenant_id TEXT NOT NULL DEFAULT 'shared',
  name TEXT NOT NULL,
  mode TEXT NOT NULL,
  default_route TEXT NOT NULL,
  allowed_workloads TEXT[] DEFAULT '{}',
  provenance_required BOOLEAN DEFAULT FALSE,
  description TEXT,
  metadata JSONB NOT NULL DEFAULT '{}',
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tenant_scores (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  tenant_id TEXT NOT NULL UNIQUE,
  health_score INT NOT NULL,
  freshness_score INT NOT NULL,
  layer_scores JSONB NOT NULL DEFAULT '{}',
  summary JSONB NOT NULL DEFAULT '{}',
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
