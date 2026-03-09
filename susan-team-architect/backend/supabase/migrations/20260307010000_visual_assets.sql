-- Optional structured asset table for screenshot and media metadata.
-- Apply this migration in Supabase when ready to promote screenshot assets
-- from knowledge_chunks metadata into a dedicated relational table.

create table if not exists visual_assets (
  id uuid default gen_random_uuid() primary key,
  company_id text not null,
  title text not null,
  asset_type text not null default 'screenshot',
  bucket_name text not null,
  storage_path text not null unique,
  public_url text,
  source_url text,
  data_type text not null default 'visual_asset',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_visual_assets_company on visual_assets (company_id);
create index if not exists idx_visual_assets_type on visual_assets (data_type);
create index if not exists idx_visual_assets_meta on visual_assets using gin (metadata);
