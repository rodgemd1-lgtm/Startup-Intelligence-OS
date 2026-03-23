-- Migration: Jake Autonomous Pipeline Runs table
-- Date: 2026-03-22
-- Purpose: Track 8-phase autonomous pipeline executions for Jake AI Employees

CREATE TABLE IF NOT EXISTS jake_pipeline_runs (
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    pipeline_name   text NOT NULL,
    employee_name   text,
    task_type       text,
    started_at      timestamptz DEFAULT now(),
    current_phase   text,
    status          text DEFAULT 'running',
    phases_completed jsonb DEFAULT '[]',
    outputs         jsonb DEFAULT '{}',
    error_log       jsonb DEFAULT '[]',
    completed_at    timestamptz,
    metadata        jsonb DEFAULT '{}'
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status
    ON jake_pipeline_runs(status);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_employee
    ON jake_pipeline_runs(employee_name);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_task_type
    ON jake_pipeline_runs(task_type);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_started_at
    ON jake_pipeline_runs(started_at DESC);

-- Comments for documentation
COMMENT ON TABLE jake_pipeline_runs IS
    'Tracks each autonomous 8-phase pipeline execution by Jake AI Employees';

COMMENT ON COLUMN jake_pipeline_runs.pipeline_name IS
    'Composite name: {employee_name}_{task_type}';

COMMENT ON COLUMN jake_pipeline_runs.current_phase IS
    'Last known phase: CONTEXT|PLAN|BUILD|VALIDATE|HEAL|REPORT|CLOSE|LEARN';

COMMENT ON COLUMN jake_pipeline_runs.status IS
    'Final status: running|success|partial|flagged|failed';

COMMENT ON COLUMN jake_pipeline_runs.phases_completed IS
    'JSON array of PhaseRecord objects with timing and status per phase';

COMMENT ON COLUMN jake_pipeline_runs.outputs IS
    'JSON dict of outputs produced by the BUILD phase';

COMMENT ON COLUMN jake_pipeline_runs.error_log IS
    'JSON array of error dicts: {phase, error, attempt?}';
