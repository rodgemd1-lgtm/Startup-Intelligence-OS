# Studio Assets

This directory holds the shared retrieval assets that make the design and marketing studios compounding systems rather than one-shot expert prompts.

## Asset layers

- `shared/case_library`
  - named examples
  - teardown notes
  - when-to-use and what-not-to-copy guidance
- `shared/antipatterns`
  - failure patterns
  - detection signals
  - rescue moves
- `shared/memory`
  - schemas
  - memory capture rules
  - experiment and critique logging
- `shared/templates`
  - template cascades
  - briefing skeletons
  - derivative asset systems
- `shared/evals`
  - scoring rubric
  - fail conditions
  - review workflow
- `open_sources`
  - scraped public references
  - official design and motion guidance
  - JTBD, discovery, and moments-of-truth research
  - open structured datasets and evidence feeds
- `companies`
  - company-specific memory seeds, wins, risks, and experiments
- `generated`
  - curated imports from external source repos and tool chains
  - normalized so Susan can retrieve the method without depending on the external repo

## Retrieval data types

- `studio_case_library`
- `studio_antipatterns`
- `studio_memory`
- `studio_templates`
- `studio_evals`
- `studio_open_research`

## Structured schemas

Machine-readable templates live in `shared/schemas`:
- `case_memory_entry.yaml`
- `antipattern_entry.yaml`
- `experiment_memory_entry.yaml`
- `template_asset_entry.yaml`
- `eval_scorecard.yaml`

## Current seed companies

- `transformfit`
- `oracle-health-ai-enablement`

These assets are designed to be ingested into Supabase so Susan and the studio agents can retrieve real examples, anti-patterns, memory, and rubrics while working.

## External repo absorption

When a standalone design or research repo should no longer remain a parallel source of truth, absorb it here:
- normalize its reusable doctrine and workflow into curated markdown
- import future output folders as `ux_research`, `studio_templates`, `studio_case_library`, and `visual_asset`
- keep the external repo as a source/tooling archive, not the intelligence system
