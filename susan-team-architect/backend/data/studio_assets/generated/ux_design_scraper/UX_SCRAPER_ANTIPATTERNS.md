# UX Design Scraper Anti-Pattern Dataset

> Source repo: `/Users/mikerodgers/ux-design-scraper`

## Anti-pattern 1: Parallel source-of-truth database

Signal:
- a second Supabase schema is used to store design intelligence separately from Susan

Why it is bad:
- duplicate retrieval systems
- drift between repos
- the design team learns things that Susan cannot naturally route

Rescue move:
- treat the UX scraper repo as an ingestion/source tool
- keep Susan's backend as the intelligence system of record

## Anti-pattern 2: Repo-bound knowledge instead of shared studio memory

Signal:
- heuristics, prompt methodology, and design patterns only exist in extension source files

Why it is bad:
- studio agents cannot retrieve them directly
- the methodology disappears from company work unless someone remembers it manually

Rescue move:
- normalize those learnings into `studio_expertise`, `studio_templates`, and `studio_memory`

## Anti-pattern 3: Tool-specific schema over reusable ontology

Signal:
- tables were designed around scrape sessions and extension outputs, not long-lived foundry knowledge

Why it is bad:
- hard to share across TransformFit, Alex Recruiting, Oracle Health, and founder work
- makes cross-company design memory harder

Rescue move:
- preserve the concepts: screenshots, flow analysis, competitor analysis, components, tokens
- map them into Susan's existing knowledge and asset model

## Anti-pattern 4: Raw extraction without studio curation

Signal:
- raw design tokens, HTML, CSS, and screenshots are stored, but not consistently turned into precedent, lessons, anti-patterns, or operating doctrine

Rescue move:
- every UX scraper import should yield:
  - a case library entry
  - a template or workflow artifact
  - a memory note
  - optional visual assets
