-- Phase 4: Autonomous Pipeline Engine
-- Tables: jake_pipeline_runs, jake_cron_status

-- ============================================================
-- jake_pipeline_runs — tracks 8-phase pipeline executions
-- ============================================================

create table if not exists jake_pipeline_runs (
    id               uuid primary key default gen_random_uuid(),
    pipeline_name    text not null,
    task_description text not null,
    task_type        text not null default 'research',  -- research | content | maintenance | custom
    status           text not null default 'running',   -- running | completed | failed | blocked
    current_phase    text not null default 'init',      -- context | plan | build | validate | heal | report | close | learn
    started_at       timestamptz not null default now(),
    completed_at     timestamptz,
    phases_completed jsonb default '{}',                -- phase_name → {status, summary}
    error_log        jsonb default '[]',                -- list of error strings
    metadata         jsonb default '{}',
    created_at       timestamptz not null default now(),
    updated_at       timestamptz not null default now()
);

-- Indexes
create index if not exists idx_jake_pipeline_runs_status       on jake_pipeline_runs(status);
create index if not exists idx_jake_pipeline_runs_pipeline_name on jake_pipeline_runs(pipeline_name);
create index if not exists idx_jake_pipeline_runs_started_at   on jake_pipeline_runs(started_at desc);
create index if not exists idx_jake_pipeline_runs_task_type    on jake_pipeline_runs(task_type);

-- Auto-update updated_at
create or replace function update_jake_pipeline_runs_updated_at()
returns trigger language plpgsql as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists trg_jake_pipeline_runs_updated_at on jake_pipeline_runs;
create trigger trg_jake_pipeline_runs_updated_at
    before update on jake_pipeline_runs
    for each row execute function update_jake_pipeline_runs_updated_at();

-- ============================================================
-- jake_cron_status — tracks scheduled job health
-- ============================================================

create table if not exists jake_cron_status (
    id            uuid primary key default gen_random_uuid(),
    job_name      text not null unique,                 -- e.g. "jake_self_improve_weekly"
    last_run_at   timestamptz,
    next_run_at   timestamptz,
    status        text not null default 'pending',      -- pending | running | success | failed | skipped
    error_message text,
    actions_taken int default 0,                        -- count of meaningful actions in last run
    duration_ms   int,                                  -- run duration in milliseconds
    metadata      jsonb default '{}',
    created_at    timestamptz not null default now(),
    updated_at    timestamptz not null default now()
);

-- Indexes
create index if not exists idx_jake_cron_status_job_name  on jake_cron_status(job_name);
create index if not exists idx_jake_cron_status_status    on jake_cron_status(status);
create index if not exists idx_jake_cron_status_last_run  on jake_cron_status(last_run_at desc);

-- Auto-update updated_at
create or replace function update_jake_cron_status_updated_at()
returns trigger language plpgsql as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists trg_jake_cron_status_updated_at on jake_cron_status;
create trigger trg_jake_cron_status_updated_at
    before update on jake_cron_status
    for each row execute function update_jake_cron_status_updated_at();

-- Seed known cron jobs (upsert)
insert into jake_cron_status (job_name, status) values
    ('jake_self_improve_weekly', 'pending'),
    ('jake_research_daemon_nightly', 'pending'),
    ('jake_collective_monthly', 'pending'),
    ('oracle_sentinel_daily', 'pending'),
    ('inbox_zero_morning', 'pending'),
    ('inbox_zero_midday', 'pending'),
    ('inbox_zero_evening', 'pending')
on conflict (job_name) do nothing;
