-- Jake Security tables: audit log, rate limit state, and deal pipeline
-- Migration: 20260322000000_jake_security

-- =====================================================================
-- Audit Log
-- =====================================================================
CREATE TABLE IF NOT EXISTS jake_audit_log (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event       TEXT NOT NULL,
    actor       TEXT NOT NULL,
    resource    TEXT DEFAULT '',
    outcome     TEXT DEFAULT 'success',
    context     JSONB DEFAULT '{}',
    error       TEXT DEFAULT '',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_event      ON jake_audit_log(event);
CREATE INDEX IF NOT EXISTS idx_audit_log_actor      ON jake_audit_log(actor);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON jake_audit_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_outcome    ON jake_audit_log(outcome);

-- =====================================================================
-- Cron Status (for dashboard Cron Health panel)
-- =====================================================================
CREATE TABLE IF NOT EXISTS jake_cron_status (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_name        TEXT NOT NULL UNIQUE,
    last_run        TIMESTAMPTZ,
    status          TEXT DEFAULT 'never_run',  -- running, success, failed, never_run
    next_run        TIMESTAMPTZ,
    error_message   TEXT DEFAULT '',
    duration_ms     INTEGER DEFAULT 0,
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cron_status_job_name ON jake_cron_status(job_name);

-- =====================================================================
-- Pipeline Runs (for dashboard Pipeline panel)
-- =====================================================================
CREATE TABLE IF NOT EXISTS jake_pipeline_runs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_name       TEXT NOT NULL,
    task_description    TEXT DEFAULT '',
    task_type           TEXT DEFAULT 'general',
    started_at          TIMESTAMPTZ DEFAULT NOW(),
    current_phase       INTEGER DEFAULT 0,
    status              TEXT DEFAULT 'running',  -- running, completed, failed, blocked
    phases_completed    JSONB DEFAULT '{}',
    error_log           TEXT DEFAULT '',
    result_summary      TEXT DEFAULT '',
    completed_at        TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_name       ON jake_pipeline_runs(pipeline_name);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status     ON jake_pipeline_runs(status);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_started_at ON jake_pipeline_runs(started_at DESC);

-- =====================================================================
-- Cost Tracking
-- =====================================================================
CREATE TABLE IF NOT EXISTS jake_cost_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service         TEXT NOT NULL,   -- anthropic, voyage, supabase, etc.
    operation       TEXT NOT NULL,   -- api_call, embed, read, write
    model           TEXT DEFAULT '',
    input_tokens    INTEGER DEFAULT 0,
    output_tokens   INTEGER DEFAULT 0,
    cost_usd        NUMERIC(10, 6) DEFAULT 0,
    actor           TEXT DEFAULT 'system',
    pipeline_run_id UUID REFERENCES jake_pipeline_runs(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cost_events_service    ON jake_cost_events(service);
CREATE INDEX IF NOT EXISTS idx_cost_events_created_at ON jake_cost_events(created_at DESC);

-- =====================================================================
-- Business Pipeline (Deals)
-- =====================================================================
CREATE TABLE IF NOT EXISTS jake_deals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company         TEXT NOT NULL,
    contact_name    TEXT DEFAULT '',
    contact_email   TEXT DEFAULT '',
    deal_type       TEXT DEFAULT 'sales',   -- sales, partnership, sponsorship, licensing
    stage           TEXT DEFAULT 'prospect', -- prospect, qualified, proposal, negotiation, closed_won, closed_lost
    value_usd       NUMERIC(12, 2) DEFAULT 0,
    probability     INTEGER DEFAULT 0,      -- 0-100
    expected_close  DATE,
    notes           TEXT DEFAULT '',
    next_action     TEXT DEFAULT '',
    next_action_due DATE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_deals_company ON jake_deals(company);
CREATE INDEX IF NOT EXISTS idx_deals_stage   ON jake_deals(stage);

CREATE TABLE IF NOT EXISTS jake_pipeline_events (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id     UUID REFERENCES jake_deals(id) ON DELETE CASCADE,
    event_type  TEXT NOT NULL,  -- stage_change, note_added, contact_made, task_completed
    from_stage  TEXT DEFAULT '',
    to_stage    TEXT DEFAULT '',
    notes       TEXT DEFAULT '',
    actor       TEXT DEFAULT 'jake',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pipeline_events_deal_id    ON jake_pipeline_events(deal_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_events_created_at ON jake_pipeline_events(created_at DESC);
