-- Phase F1: Goal Tracking Layer
-- Tables: jake_goals, jake_goal_checkins
-- Semantic search via pgvector (Voyage AI 1024 dimensions)

-- Enable pgvector if not already
create extension if not exists vector;

-- ============================================================
-- jake_goals — goals, milestones, KPIs, OKRs
-- ============================================================

create table if not exists jake_goals (
    id            uuid primary key default gen_random_uuid(),
    title         text not null,
    description   text,
    goal_type     text not null default 'goal',        -- goal | milestone | kpi | okr
    parent_id     uuid references jake_goals(id) on delete set null,
    project       text,
    status        text not null default 'active',      -- active | completed | paused | cancelled
    priority      text not null default 'P2',          -- P0 | P1 | P2 | P3
    target_value  numeric,
    current_value numeric default 0,
    unit          text,
    deadline      timestamptz,
    completed_at  timestamptz,
    people        text[] default '{}',
    tags          text[] default '{}',
    metadata      jsonb default '{}',
    embedding     vector(1024),
    created_at    timestamptz not null default now(),
    updated_at    timestamptz not null default now()
);

-- Indexes
create index if not exists idx_jake_goals_status     on jake_goals(status);
create index if not exists idx_jake_goals_project    on jake_goals(project);
create index if not exists idx_jake_goals_parent_id  on jake_goals(parent_id);
create index if not exists idx_jake_goals_deadline   on jake_goals(deadline);
create index if not exists idx_jake_goals_embedding  on jake_goals
    using ivfflat (embedding vector_cosine_ops) with (lists = 10);

-- Auto-update updated_at
create or replace function update_jake_goals_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

create trigger trg_jake_goals_updated_at
    before update on jake_goals
    for each row
    execute function update_jake_goals_updated_at();

-- ============================================================
-- jake_goal_checkins — progress updates linked to goals
-- ============================================================

create table if not exists jake_goal_checkins (
    id             uuid primary key default gen_random_uuid(),
    goal_id        uuid not null references jake_goals(id) on delete cascade,
    content        text not null,
    previous_value numeric,
    new_value      numeric,
    delta          numeric,
    source         text not null default 'manual',    -- manual | cron | agent | hermes
    metadata       jsonb default '{}',
    embedding      vector(1024),
    created_at     timestamptz not null default now()
);

create index if not exists idx_jake_goal_checkins_goal_id on jake_goal_checkins(goal_id);

-- ============================================================
-- RPC: jake_goal_search — semantic search across goals
-- ============================================================

create or replace function jake_goal_search(
    query_embedding vector(1024),
    match_count     int default 10,
    status_filter   text default null
)
returns table (
    id            uuid,
    title         text,
    description   text,
    goal_type     text,
    project       text,
    status        text,
    priority      text,
    target_value  numeric,
    current_value numeric,
    unit          text,
    deadline      timestamptz,
    completed_at  timestamptz,
    people        text[],
    tags          text[],
    metadata      jsonb,
    created_at    timestamptz,
    updated_at    timestamptz,
    similarity    float
)
language plpgsql
as $$
begin
    return query
    select
        g.id,
        g.title,
        g.description,
        g.goal_type,
        g.project,
        g.status,
        g.priority,
        g.target_value,
        g.current_value,
        g.unit,
        g.deadline,
        g.completed_at,
        g.people,
        g.tags,
        g.metadata,
        g.created_at,
        g.updated_at,
        1 - (g.embedding <=> query_embedding) as similarity
    from jake_goals g
    where g.embedding is not null
      and (status_filter is null or g.status = status_filter)
    order by g.embedding <=> query_embedding
    limit match_count;
end;
$$;
