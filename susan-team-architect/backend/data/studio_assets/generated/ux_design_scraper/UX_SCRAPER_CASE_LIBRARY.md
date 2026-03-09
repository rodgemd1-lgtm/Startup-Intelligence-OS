# UX Design Scraper Case Library

> Source repo: `/Users/mikerodgers/ux-design-scraper`
> This document captures the patterns from the UX scraper that are worth reusing in Susan's studios.

## Case 1: Topological scrape orchestration

Source:
- `src/background/scrape-orchestrator.ts`

Why it matters:
- the extension separates independent DOM extraction, dependent extraction, screenshots, external APIs, and enhanced MCP/API enrichment into waves
- this is a good precedent for Susan-side design intelligence jobs because it models dependencies explicitly instead of relying on one giant scrape

What Susan should keep:
- wave-based orchestration
- dependency-aware execution
- enhancement layers: Firecrawl, Exa, MCP, screenshots, motion capture

## Case 2: Output packaging into reusable artifacts

Source:
- `src/background/file-output-manager.ts`

Reusable pattern:
- produce a design package rather than raw scrape results
- package includes `CLAUDE.md`, research insights, prompts, analysis docs, tokens, component artifacts, screenshots, accessibility, performance, and knowledge-base summaries

Susan-side implication:
- any future UX scraper export folder should be treated as a compound studio asset pack
- markdown should go into `studio_templates`, `studio_case_library`, and `ux_research`
- screenshots should go into `visual_asset`

## Case 3: Structured critique engine

Source:
- `src/background/design-critique-engine.ts`

Reusable pattern:
- critique should cover visual hierarchy, whitespace, color harmony, typography, CTA effectiveness, mobile-first quality, emotional design, consistency, microinteractions, and innovation

Susan-side implication:
- use this as a design review rubric input for Marcus, Mira, Prism, and Design Studio Director

## Case 4: Schema lessons from the original Supabase model

Source:
- `supabase/migrations/001_initial_schema.sql`

Tables already modeled there:
- `projects`
- `design_tokens`
- `components`
- `screenshots`
- `heatmaps`
- `knowledge_base`
- `competitor_analysis`
- `flow_analysis`
- `design_versions`

Susan-side implication:
- keep the entity ideas, not the duplicate database
- merge them into Susan's foundry via `ux_research`, `studio_memory`, `studio_templates`, and `visual_asset`
