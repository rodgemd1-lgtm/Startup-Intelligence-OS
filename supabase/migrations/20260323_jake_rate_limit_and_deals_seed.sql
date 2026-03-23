-- jake_rate_limit_state — lightweight table for rate limiter persistence
-- Mirrors the in-memory RateLimiter state so the dashboard can query it.
-- Rows are upserted by the rate limiter on each acquire(); TTL via updated_at.

create table if not exists jake_rate_limit_state (
    id             uuid primary key default gen_random_uuid(),
    operation      text not null,
    actor          text not null default 'system',
    call_count     integer not null default 0,
    window_seconds numeric not null,
    max_calls      integer not null,
    last_reset_at  timestamptz not null default now(),
    updated_at     timestamptz not null default now(),
    unique (operation, actor)
);

comment on table jake_rate_limit_state is
    'Persists in-memory rate limiter windows for dashboard observability. '
    'Source of truth for the rate limiter remains in-memory; this table is '
    'a read replica updated periodically by the RateLimiter.persist() call.';

-- Index for dashboard queries (latest state per operation)
create index if not exists jake_rate_limit_state_operation_idx
    on jake_rate_limit_state (operation, updated_at desc);
