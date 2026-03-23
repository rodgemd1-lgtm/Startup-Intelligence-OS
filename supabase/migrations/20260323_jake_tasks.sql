-- Jake Tasks Table — autonomous work system
-- Each task belongs to a goal and tracks autonomous execution

CREATE TABLE IF NOT EXISTS jake_tasks (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_id     UUID REFERENCES jake_goals(id) ON DELETE CASCADE,

    -- The task itself
    task_text   TEXT NOT NULL,
    description TEXT,
    status      TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','in_progress','completed','failed','blocked','skipped')),

    -- Execution routing
    assigned_to TEXT NOT NULL DEFAULT 'auto'
                    CHECK (assigned_to IN ('auto','hermes','claude_code','cron','script','manual')),
    executor_hint TEXT, -- e.g. "scripts/ingest_mci_sops.py" or "claude -p '...'"

    -- Priority & ordering
    priority    TEXT NOT NULL DEFAULT 'P2'
                    CHECK (priority IN ('P0','P1','P2','P3')),
    order_index INT NOT NULL DEFAULT 0,

    -- Execution results
    output      TEXT,
    error_msg   TEXT,
    attempt_count INT NOT NULL DEFAULT 0,
    max_attempts  INT NOT NULL DEFAULT 3,

    -- Timestamps
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at    TIMESTAMPTZ,
    completed_at  TIMESTAMPTZ,
    due_date      TIMESTAMPTZ,

    -- Search embedding
    embedding   VECTOR(1024)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_jake_tasks_goal_id  ON jake_tasks(goal_id);
CREATE INDEX IF NOT EXISTS idx_jake_tasks_status   ON jake_tasks(status);
CREATE INDEX IF NOT EXISTS idx_jake_tasks_priority ON jake_tasks(priority);
CREATE INDEX IF NOT EXISTS idx_jake_tasks_assigned ON jake_tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_jake_tasks_embedding ON jake_tasks
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Semantic search RPC for tasks
CREATE OR REPLACE FUNCTION jake_task_search(
    query_embedding VECTOR(1024),
    match_count     INT DEFAULT 10,
    status_filter   TEXT DEFAULT NULL
)
RETURNS TABLE (
    id           UUID,
    goal_id      UUID,
    task_text    TEXT,
    status       TEXT,
    assigned_to  TEXT,
    priority     TEXT,
    similarity   FLOAT
)
LANGUAGE sql STABLE AS $$
    SELECT
        t.id,
        t.goal_id,
        t.task_text,
        t.status,
        t.assigned_to,
        t.priority,
        1 - (t.embedding <=> query_embedding) AS similarity
    FROM jake_tasks t
    WHERE
        t.embedding IS NOT NULL
        AND (status_filter IS NULL OR t.status = status_filter)
    ORDER BY t.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Task execution log — separate from jake_tasks so we don't blow up the row
CREATE TABLE IF NOT EXISTS jake_task_runs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id     UUID NOT NULL REFERENCES jake_tasks(id) ON DELETE CASCADE,
    attempt     INT NOT NULL DEFAULT 1,
    status      TEXT NOT NULL CHECK (status IN ('started','completed','failed')),
    output      TEXT,
    error_msg   TEXT,
    duration_ms INT,
    executor    TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_jake_task_runs_task_id ON jake_task_runs(task_id);
CREATE INDEX IF NOT EXISTS idx_jake_task_runs_created ON jake_task_runs(created_at DESC);
