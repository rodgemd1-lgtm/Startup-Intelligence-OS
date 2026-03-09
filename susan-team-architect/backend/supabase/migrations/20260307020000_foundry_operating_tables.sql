create table if not exists public.foundry_decisions (
  id uuid primary key default gen_random_uuid(),
  decision_id text not null unique,
  company_id text not null,
  owner text not null,
  summary text not null,
  context text,
  chosen_option text not null,
  why_this_won text,
  status text not null default 'active',
  review_date date,
  source_refs jsonb not null default '[]'::jsonb,
  risks_accepted jsonb not null default '[]'::jsonb,
  linked_experiments jsonb not null default '[]'::jsonb,
  metadata jsonb not null default '{}'::jsonb,
  decided_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists foundry_decisions_company_idx
  on public.foundry_decisions (company_id, decided_at desc);

create table if not exists public.foundry_experiments (
  id uuid primary key default gen_random_uuid(),
  experiment_id text not null unique,
  company_id text not null,
  hypothesis text not null,
  owner text not null,
  status text not null default 'proposed',
  user_or_workflow text,
  metric_moved text,
  leading_signal text,
  disconfirming_signal text,
  intervention text,
  start_date date,
  stop_date date,
  result_summary text,
  linked_decisions jsonb not null default '[]'::jsonb,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists foundry_experiments_company_idx
  on public.foundry_experiments (company_id, status, created_at desc);

create table if not exists public.foundry_metrics (
  id uuid primary key default gen_random_uuid(),
  metric_id text not null unique,
  company_id text not null,
  name text not null,
  category text not null,
  owner text not null,
  definition text,
  cadence text,
  leading_or_lagging text,
  threshold_green text,
  threshold_yellow text,
  threshold_red text,
  source_events jsonb not null default '[]'::jsonb,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists foundry_metrics_company_idx
  on public.foundry_metrics (company_id, category, name);

create table if not exists public.foundry_stage_reviews (
  id uuid primary key default gen_random_uuid(),
  company_id text not null,
  stage_gate_id text not null,
  reviewer text not null,
  status text not null,
  summary text not null,
  blocking_gaps jsonb not null default '[]'::jsonb,
  artifact_refs jsonb not null default '[]'::jsonb,
  metadata jsonb not null default '{}'::jsonb,
  reviewed_at timestamptz not null default now()
);

create index if not exists foundry_stage_reviews_company_idx
  on public.foundry_stage_reviews (company_id, stage_gate_id, reviewed_at desc);
