# UX Design Scraper Schema And Import Model

> Source repo: `/Users/mikerodgers/ux-design-scraper`
> Source schema: `supabase/migrations/001_initial_schema.sql`

## Original tables

- `projects`
- `design_tokens`
- `components`
- `screenshots`
- `heatmaps`
- `knowledge_base`
- `competitor_analysis`
- `flow_analysis`
- `design_versions`

## What those tables mean in Susan

| Original table | Susan-side meaning |
|---|---|
| `projects` | scrape session / imported design analysis package |
| `design_tokens` | structured design token evidence |
| `components` | component precedent and implementation reference |
| `screenshots` | visual assets |
| `heatmaps` | experience evidence / behavior signal |
| `knowledge_base` | studio knowledge and prompt artifacts |
| `competitor_analysis` | case library / competitive design intelligence |
| `flow_analysis` | UX research / journey and friction analysis |
| `design_versions` | precedent history / visual evolution |

## Import protocol

### Repo knowledge import
- normalize source methodology into curated shared markdown docs
- ingest them into:
  - `studio_expertise`
  - `studio_case_library`
  - `studio_antipatterns`
  - `studio_memory`
  - `studio_templates`
  - `ux_research`

### Export folder import
- markdown analysis files -> `ux_research` or `studio_templates`
- `CLAUDE.md` and prompt packs -> `studio_templates`
- research summaries and teardowns -> `studio_case_library`
- screenshots -> `visual_asset`
- JSON artifacts -> summarized `ux_research`

## Why this is better than keeping a separate repo

- Susan can route and retrieve the intelligence natively
- TransformFit, Alex Recruiting, Oracle Health, and founder work all benefit from the same memory
- the extension becomes a tool, not a second intelligence platform
