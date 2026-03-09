-- Unified Intelligence OS — Add Frontend Tables to Susan's Supabase
-- Migrates founder-command-center tables to Susan's Supabase project
-- (zqsdadnnpgqhehqxplio.supabase.co)
--
-- SKIPPED: knowledge_chunks (already exists with vector(1024) via Voyage AI)
-- SKIPPED: match_knowledge() RPC (using Susan's search_knowledge() instead)
-- ADAPTED: decisions, customer_intel, research_log use vector(1024) not 1536
--
-- Run: psql $DATABASE_URL -f this_file.sql
-- Or:  supabase db push

-- Extensions (pgcrypto for gen_random_uuid if not on PG14+)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- CORE: Businesses (maps to Susan's companies concept)
-- ============================================================
CREATE TABLE IF NOT EXISTS businesses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  slug text UNIQUE NOT NULL,
  tagline text,
  tag text NOT NULL CHECK (tag IN ('ALL', 'FITNESS', 'INSTAGRAM', 'INTELLIGENCE', 'AUTOMOTIVE')),
  repo text,
  status text NOT NULL DEFAULT 'active',
  metadata jsonb DEFAULT '{}',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS business_metrics (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id uuid REFERENCES businesses(id) ON DELETE CASCADE,
  metric_name text NOT NULL,
  current_value text,
  target_value text,
  status text DEFAULT 'on-track',
  recorded_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS business_domains (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id uuid REFERENCES businesses(id) ON DELETE CASCADE,
  name text NOT NULL,
  progress int DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
  phase text,
  blocker text,
  next_milestone text,
  sort_order int DEFAULT 0
);

CREATE TABLE IF NOT EXISTS blockers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id uuid REFERENCES businesses(id) ON DELETE CASCADE,
  description text NOT NULL,
  blocking text,
  owner text,
  cleared boolean DEFAULT false,
  cleared_at timestamptz,
  created_at timestamptz DEFAULT now()
);

-- ============================================================
-- INTELLIGENCE: File metadata index
-- ============================================================
CREATE TABLE IF NOT EXISTS intelligence_files (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  file_path text UNIQUE NOT NULL,
  file_type text NOT NULL CHECK (file_type IN ('persona', 'framework', 'skill')),
  name text NOT NULL,
  description text,
  tags text[] DEFAULT '{}',
  tier int DEFAULT 1,
  category text,
  content text,
  content_hash text,
  last_synced_at timestamptz DEFAULT now()
);

-- ============================================================
-- DECISIONS: Learning log with vector search
-- Uses vector(1024) to match Susan's Voyage AI embeddings
-- ============================================================
CREATE TABLE IF NOT EXISTS decisions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid,
  business_id text NOT NULL,
  title text NOT NULL,
  description text NOT NULL,
  category text NOT NULL CHECK (category IN ('strategy', 'product', 'marketing', 'technical', 'financial', 'hiring', 'legal')),
  outcome text,
  outcome_rating int CHECK (outcome_rating >= 1 AND outcome_rating <= 10),
  what_worked text,
  what_didnt text,
  lessons_learned text,
  tags text[] DEFAULT '{}',
  status text DEFAULT 'active' CHECK (status IN ('active', 'resolved', 'reversed')),
  embedding vector(1024),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- ============================================================
-- CUSTOMER INTELLIGENCE
-- ============================================================
CREATE TABLE IF NOT EXISTS customer_intel (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid,
  business_id text NOT NULL,
  customer_name text,
  segment text,
  feedback text,
  nps_score int CHECK (nps_score >= 0 AND nps_score <= 10),
  acquisition_channel text,
  mrr_contribution decimal(10,2),
  status text DEFAULT 'active',
  notes text,
  embedding vector(1024),
  created_at timestamptz DEFAULT now()
);

-- ============================================================
-- RESEARCH LOG
-- ============================================================
CREATE TABLE IF NOT EXISTS research_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid,
  business_id text,
  source_url text,
  source_type text CHECK (source_type IN ('youtube', 'reddit', 'web', 'paper', 'manual', 'persona', 'framework', 'skill', 'document')),
  title text NOT NULL,
  summary text NOT NULL,
  key_insights text[] DEFAULT '{}',
  tags text[] DEFAULT '{}',
  embedding vector(1024),
  ingested_at timestamptz DEFAULT now()
);

-- ============================================================
-- VAULT: Encrypted credentials
-- No user_id FK to auth.users (service-role access)
-- ============================================================
CREATE TABLE IF NOT EXISTS credential_vaults (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid,
  business_id uuid REFERENCES businesses(id) ON DELETE SET NULL,
  name text NOT NULL,
  description text,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS credentials (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  vault_id uuid REFERENCES credential_vaults(id) ON DELETE CASCADE,
  label text NOT NULL,
  category text,
  service text,
  encrypted_value text NOT NULL,
  environment text DEFAULT 'production',
  tags text[] DEFAULT '{}',
  last_accessed_at timestamptz,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS credential_access_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  credential_id uuid REFERENCES credentials(id) ON DELETE CASCADE,
  action text NOT NULL,
  accessed_at timestamptz DEFAULT now()
);

-- ============================================================
-- COUNCIL: AI Advisory Sessions
-- ============================================================
CREATE TABLE IF NOT EXISTS advisory_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid,
  business_id uuid REFERENCES businesses(id) ON DELETE SET NULL,
  question text,
  session_type text DEFAULT 'quick_consult',
  participants jsonb DEFAULT '[]',
  status text DEFAULT 'active',
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS advisory_responses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid REFERENCES advisory_sessions(id) ON DELETE CASCADE,
  persona_id text NOT NULL,
  response_text text NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- ============================================================
-- NOTES
-- ============================================================
CREATE TABLE IF NOT EXISTS notes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid,
  business_id uuid REFERENCES businesses(id) ON DELETE SET NULL,
  title text NOT NULL,
  content text,
  tags text[] DEFAULT '{}',
  note_type text DEFAULT 'general',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- ============================================================
-- TASKS
-- ============================================================
CREATE TABLE IF NOT EXISTS fcc_tasks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid,
  business_id uuid REFERENCES businesses(id) ON DELETE SET NULL,
  title text NOT NULL,
  description text,
  status text DEFAULT 'todo' CHECK (status IN ('backlog', 'todo', 'in_progress', 'done', 'cancelled')),
  priority int DEFAULT 2 CHECK (priority >= 0 AND priority <= 3),
  labels text[] DEFAULT '{}',
  due_date date,
  sort_order int DEFAULT 0,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- ============================================================
-- FINANCIAL
-- ============================================================
CREATE TABLE IF NOT EXISTS revenue_entries (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id uuid REFERENCES businesses(id) ON DELETE CASCADE,
  amount numeric NOT NULL,
  type text DEFAULT 'recurring' CHECK (type IN ('one_time', 'recurring')),
  source text,
  period_start date,
  period_end date,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS expenses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id uuid REFERENCES businesses(id) ON DELETE CASCADE,
  amount numeric NOT NULL,
  category text,
  vendor text,
  description text,
  is_recurring boolean DEFAULT false,
  date date,
  created_at timestamptz DEFAULT now()
);

-- ============================================================
-- RESEARCH
-- ============================================================
CREATE TABLE IF NOT EXISTS research_monitors (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id uuid REFERENCES businesses(id) ON DELETE SET NULL,
  name text NOT NULL,
  keywords text[] DEFAULT '{}',
  sources text[] DEFAULT '{}',
  is_active boolean DEFAULT true,
  last_run_at timestamptz,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS research_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  monitor_id uuid REFERENCES research_monitors(id) ON DELETE SET NULL,
  source text,
  title text NOT NULL,
  url text,
  content_snippet text,
  ai_summary text,
  relevance_score numeric,
  is_bookmarked boolean DEFAULT false,
  tags text[] DEFAULT '{}',
  discovered_at timestamptz DEFAULT now()
);

-- ============================================================
-- MORNING BRIEFINGS
-- ============================================================
CREATE TABLE IF NOT EXISTS morning_briefings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid,
  briefing_date date NOT NULL DEFAULT CURRENT_DATE,
  priorities jsonb NOT NULL,
  portfolio_summary jsonb NOT NULL,
  research_highlights jsonb,
  monte_carlo_snapshot jsonb,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS daily_actions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid,
  business_id text NOT NULL,
  briefing_id uuid REFERENCES morning_briefings(id),
  task text NOT NULL,
  status text DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'skipped')),
  outcome text,
  started_at timestamptz,
  completed_at timestamptz,
  created_at timestamptz DEFAULT now()
);

-- ============================================================
-- SCRAPE TRACKING
-- ============================================================
CREATE TABLE IF NOT EXISTS scrape_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  query text NOT NULL,
  api_source text NOT NULL DEFAULT 'brave',
  result_count integer NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- ============================================================
-- EXPERT MAPPING: Frontend experts → Susan agents
-- ============================================================
CREATE TABLE IF NOT EXISTS expert_agent_mapping (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  frontend_expert_id text UNIQUE NOT NULL,
  frontend_expert_name text NOT NULL,
  susan_agent_id text NOT NULL,
  susan_agent_name text NOT NULL,
  notes text,
  created_at timestamptz DEFAULT now()
);

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_decisions_business ON decisions(business_id);
CREATE INDEX IF NOT EXISTS idx_research_log_business ON research_log(business_id);
CREATE INDEX IF NOT EXISTS idx_customer_intel_business ON customer_intel(business_id);
CREATE INDEX IF NOT EXISTS idx_morning_briefings_date ON morning_briefings(briefing_date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_actions_business ON daily_actions(business_id);
CREATE INDEX IF NOT EXISTS idx_daily_actions_status ON daily_actions(status);
CREATE INDEX IF NOT EXISTS idx_scrape_log_created ON scrape_log(created_at);

-- HNSW vector indexes for similarity search (1024 dim, Voyage AI)
CREATE INDEX IF NOT EXISTS idx_decisions_embedding ON decisions
  USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX IF NOT EXISTS idx_research_log_embedding ON research_log
  USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX IF NOT EXISTS idx_customer_intel_embedding ON customer_intel
  USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

-- ============================================================
-- RLS: Service role + authenticated access
-- ============================================================
ALTER TABLE businesses ENABLE ROW LEVEL SECURITY;
ALTER TABLE business_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE business_domains ENABLE ROW LEVEL SECURITY;
ALTER TABLE blockers ENABLE ROW LEVEL SECURITY;
ALTER TABLE intelligence_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_intel ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE credential_vaults ENABLE ROW LEVEL SECURITY;
ALTER TABLE credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE credential_access_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE advisory_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE advisory_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE fcc_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE revenue_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_monitors ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE morning_briefings ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE scrape_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE expert_agent_mapping ENABLE ROW LEVEL SECURITY;

-- Allow authenticated + service_role full access (single-user app)
DO $$
DECLARE
  tbl TEXT;
BEGIN
  FOR tbl IN
    SELECT unnest(ARRAY[
      'businesses', 'business_metrics', 'business_domains', 'blockers',
      'intelligence_files', 'decisions', 'customer_intel', 'research_log',
      'credential_vaults', 'credentials', 'credential_access_log',
      'advisory_sessions', 'advisory_responses', 'notes', 'fcc_tasks',
      'revenue_entries', 'expenses', 'research_monitors', 'research_items',
      'morning_briefings', 'daily_actions', 'scrape_log', 'expert_agent_mapping'
    ])
  LOOP
    EXECUTE format(
      'CREATE POLICY "Full access for authenticated" ON %I FOR ALL USING (
        auth.role() = ''authenticated'' OR auth.role() = ''service_role''
      )',
      tbl
    );
  END LOOP;
END $$;

-- ============================================================
-- RPC: Decision similarity search (adapted for vector(1024))
-- ============================================================
CREATE OR REPLACE FUNCTION match_decisions(
  query_embedding vector(1024),
  match_business_id text,
  match_threshold float DEFAULT 0.7,
  match_count int DEFAULT 5
)
RETURNS TABLE (
  id uuid,
  business_id text,
  title text,
  description text,
  outcome text,
  lessons_learned text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    d.id,
    d.business_id,
    d.title,
    d.description,
    d.outcome,
    d.lessons_learned,
    1 - (d.embedding <=> query_embedding) AS similarity
  FROM decisions d
  WHERE (d.business_id = match_business_id OR d.business_id = 'all')
    AND d.embedding IS NOT NULL
    AND 1 - (d.embedding <=> query_embedding) > match_threshold
  ORDER BY d.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- ============================================================
-- Seed: Expert → Agent mapping
-- ============================================================
INSERT INTO expert_agent_mapping (frontend_expert_id, frontend_expert_name, susan_agent_id, susan_agent_name, notes) VALUES
  ('marcus-chen', 'Marcus Chen', 'coach', 'Coach', 'Fitness Analyst → Exercise Science'),
  ('yuki-tanaka', 'Dr. Yuki Tanaka', 'nova', 'Nova', 'AI Architect → AI/ML Specialist'),
  ('soren-erikson', 'Soren Erikson', 'marcus', 'Marcus', 'Mobile UX → UX/UI Designer'),
  ('nina-patel', 'Nina Patel', 'aria', 'Aria', 'Growth Strategist → Growth Marketing'),
  ('derek-hoffman', 'Derek Hoffman', 'steve', 'Steve', 'Pricing → Business Strategy'),
  ('jake', 'Jake', 'susan', 'Susan', 'Co-Founder → Orchestrator'),
  ('victoria-sterling', 'Victoria Sterling', 'ledger', 'Ledger', 'Revenue Ops → Finance'),
  ('james-mitchell', 'James Mitchell', 'shield', 'Shield', 'Legal Advisor → Legal/Compliance'),
  ('elena-vasquez', 'Elena Vasquez', 'compass', 'Compass', 'Product Strategy → Product Management'),
  ('raj-krishnan', 'Raj Krishnan', 'atlas', 'Atlas', 'Backend Architect → Full-Stack Engineering'),
  ('sarah-lindgren', 'Sarah Lindgren', 'sage', 'Sage', 'Nutrition Expert → Nutrition Science'),
  ('alex-rivera', 'Alex Rivera', 'prism', 'Prism', 'Brand Designer → Brand Strategy'),
  ('maya-johnson', 'Maya Johnson', 'freya', 'Freya', 'Behavioral Scientist → Behavioral Economics'),
  ('tony-zhang', 'Tony Zhang', 'sentinel', 'Sentinel', 'Security Lead → Security & Infrastructure'),
  ('rachel-kim', 'Rachel Kim', 'haven', 'Haven', 'Community Manager → Community & Social'),
  ('david-okafor', 'David Okafor', 'pulse', 'Pulse', 'Data Scientist → Data Science & Churn'),
  ('lisa-park', 'Lisa Park', 'guide', 'Guide', 'Customer Success → Customer Success'),
  ('omar-hassan', 'Omar Hassan', 'drift', 'Drift', 'Sleep Specialist → Sleep & Recovery'),
  ('kate-williams', 'Kate Williams', 'herald', 'Herald', 'PR Director → PR & Communications'),
  ('ben-taylor', 'Ben Taylor', 'quest', 'Quest', 'Gamification Designer → Gamification'),
  ('anna-schmidt', 'Anna Schmidt', 'beacon', 'Beacon', 'SEO/ASO → ASO & SEO'),
  ('chris-morgan', 'Chris Morgan', 'flow', 'Flow', 'Sports Psychologist → Sports Psychology'),
  ('diana-flores', 'Diana Flores', 'echo', 'Echo', 'Neuroscience → Neuroscience-Informed Design'),
  ('frank-butler', 'Frank Butler', 'bridge', 'Bridge', 'Partnerships → Partnerships & Ecosystem'),
  ('grace-lee', 'Grace Lee', 'lens', 'Lens', 'Accessibility → Accessibility & Inclusive'),
  ('henry-wright', 'Henry Wright', 'vault', 'Vault', 'Investor Relations → Fundraising')
ON CONFLICT (frontend_expert_id) DO NOTHING;
