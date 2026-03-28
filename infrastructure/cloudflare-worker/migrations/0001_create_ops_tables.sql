-- Jake Operations Database — V20
-- Goals (OKR-style)
CREATE TABLE IF NOT EXISTS goals (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  company TEXT,
  target TEXT NOT NULL,
  current_value REAL DEFAULT 0,
  target_value REAL DEFAULT 100,
  cadence TEXT DEFAULT 'weekly',
  status TEXT DEFAULT 'active',
  notion_page_id TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

-- Tasks (auto-decomposed from goals)
CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  goal_id TEXT REFERENCES goals(id),
  title TEXT NOT NULL,
  description TEXT,
  priority TEXT DEFAULT 'P2',
  executor TEXT DEFAULT 'jake',
  status TEXT DEFAULT 'queued',
  requires_gpu INTEGER DEFAULT 0,
  requires_mike INTEGER DEFAULT 0,
  tool TEXT,
  result TEXT,
  artifact_url TEXT,
  scheduled_for TEXT,
  started_at TEXT,
  completed_at TEXT,
  error TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

-- Briefs
CREATE TABLE IF NOT EXISTS briefs (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  content TEXT NOT NULL,
  goals_snapshot TEXT,
  tasks_completed INTEGER DEFAULT 0,
  tasks_blocked INTEGER DEFAULT 0,
  highlights TEXT,
  needs_mike TEXT,
  sent_via TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

-- Capability growth tracking
CREATE TABLE IF NOT EXISTS capability_growth (
  id TEXT PRIMARY KEY,
  week_start TEXT NOT NULL,
  domain TEXT NOT NULL,
  agent_group TEXT NOT NULL,
  chunks_before INTEGER,
  chunks_after INTEGER,
  growth_pct REAL,
  quality_score REAL,
  sources_scraped INTEGER,
  top_sources TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

-- Scrape queue
CREATE TABLE IF NOT EXISTS scrape_queue (
  id TEXT PRIMARY KEY,
  url TEXT NOT NULL,
  domain TEXT NOT NULL,
  agent_group TEXT NOT NULL,
  priority TEXT DEFAULT 'P2',
  status TEXT DEFAULT 'queued',
  chunks_produced INTEGER DEFAULT 0,
  quality_score REAL,
  discovered_by TEXT DEFAULT 'manual',
  created_at TEXT DEFAULT (datetime('now')),
  completed_at TEXT
);

-- Agent performance
CREATE TABLE IF NOT EXISTS agent_performance (
  id TEXT PRIMARY KEY,
  agent_name TEXT NOT NULL,
  task_type TEXT NOT NULL,
  success INTEGER,
  duration_ms INTEGER,
  model_used TEXT,
  cost_usd REAL,
  quality_rating REAL,
  created_at TEXT DEFAULT (datetime('now'))
);

-- System events
CREATE TABLE IF NOT EXISTS events (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  source TEXT NOT NULL,
  data TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);
