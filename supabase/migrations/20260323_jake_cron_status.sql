-- jake_cron_status: tracks V10 scheduled job run history
-- Created: 2026-03-23 as part of jake-75 build (Phase 3)

CREATE TABLE IF NOT EXISTS jake_cron_status (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    job_name    text NOT NULL,
    last_run    timestamptz NOT NULL DEFAULT now(),
    status      text NOT NULL CHECK (status IN ('ok', 'error', 'partial', 'skipped')),
    next_run    timestamptz,
    error_message text,
    output_summary text,
    run_duration_seconds numeric,
    created_at  timestamptz NOT NULL DEFAULT now()
);

-- Index for fast lookups by job name
CREATE INDEX IF NOT EXISTS idx_jake_cron_status_job_name
    ON jake_cron_status (job_name, last_run DESC);

-- Only keep last 30 runs per job (clean up old records)
CREATE INDEX IF NOT EXISTS idx_jake_cron_status_created
    ON jake_cron_status (created_at DESC);

COMMENT ON TABLE jake_cron_status IS 'V10 scheduled job run history — used by operator dashboard (Phase 3)';
