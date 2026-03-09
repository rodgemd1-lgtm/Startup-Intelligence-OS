# UX Design Scraper To Susan System

> Source repo: `/Users/mikerodgers/ux-design-scraper`
> Purpose: absorb the standalone UX scraper's reusable knowledge into Susan's design and studio system instead of maintaining a separate intelligence repo.

## Keep vs discard

Keep:
- pipeline method
- UX doctrine and heuristics
- design-review and critique methodology
- export packaging conventions
- schema lessons from the original Supabase model

Discard as standalone source of truth:
- separate product-level Supabase schema
- duplicate knowledge base ownership
- extension-specific storage model as the long-term system

## What the UX scraper actually contributes

### 1. Capture pipeline
The scraper already broke the problem into reusable extraction waves. Those are valuable as studio methodology even if the extension UI eventually goes away.

Key pipeline steps (32 total):
- `inject`: Inject Content Script
- `tokens`: Design Tokens
- `typography`: Typography System
- `icons`: Icon Extraction
- `grid`: Grid Layout
- `nav`: Navigation Structure
- `copy`: Copy Analysis
- `a11y`: Accessibility Audit
- `thirdparty`: Third-Party Stack
- `darkmode`: Dark Mode Detection
- `images`: Image Assets
- `conversion`: Conversion Patterns
- `seo`: SEO & Metadata
- `whitespace`: Whitespace Analysis
- `components`: Component Extraction
- `states`: State Variants
- `animations`: Animations
- `scroll`: Scroll Behavior
- `flow`: Flow Analysis
- `color-intelligence`: Color Intelligence
- `...` additional steps omitted for brevity

### 2. Embedded UX doctrine
`ux-knowledge-base.ts` packages:
- Nielsen heuristics
- WCAG criteria
- UI patterns
- component blueprints
- design-token guidance
- quality checks
- interaction principles

### 3. Design intelligence library
`industry-design-data.ts` packages:
- industry palettes
- typography pairings
- style definitions
- landing-page patterns
- reasoning rules

Sample industries represented (0 inferred from exported palettes/config):



### 4. Structured prompt workflow
The repo ships a strong design workflow instead of one-off prompts. Susan should retain the method, not the repo.

Prompt templates (19):
- `ab-test-prompt.ts`
- `analysis-prompt.ts`
- `copy-rewrite-prompt.ts`
- `critique-prompt.ts`
- `define-phase-prompt.ts`
- `deliver-phase-prompt.ts`
- `design-review-prompt.ts`
- `develop-phase-prompt.ts`
- `discover-phase-prompt.ts`
- `diverge-phase-prompt.ts`
- `gate-phase-prompt.ts`
- `generation-prompt.ts`
- `handoff-prompt.ts`
- `inspiration-prompt.ts`
- `measure-phase-prompt.ts`
- `persona-prompt.ts`
- `reconstruction-prompt.ts`
- `research-prompt.ts`
- `spec-artifacts-prompt.ts`

Prompt roles:
- `ab-test-prompt.ts` -> a structured design specialist
- `analysis-prompt.ts` -> a structured design specialist
- `copy-rewrite-prompt.ts` -> a structured design specialist
- `critique-prompt.ts` -> a structured design specialist
- `define-phase-prompt.ts` -> a structured design specialist
- `deliver-phase-prompt.ts` -> a structured design specialist
- `design-review-prompt.ts` -> a structured design specialist
- `develop-phase-prompt.ts` -> a structured design specialist
- `discover-phase-prompt.ts` -> a structured design specialist
- `diverge-phase-prompt.ts` -> a structured design specialist
- `gate-phase-prompt.ts` -> a structured design specialist
- `generation-prompt.ts` -> a structured design specialist
- `handoff-prompt.ts` -> a structured design specialist
- `inspiration-prompt.ts` -> a structured design specialist

## Susan-side mapping

| UX scraper layer | Susan destination |
|---|---|
| UX heuristics and design system doctrine | `studio_expertise` |
| Double Black Box workflow and prompt chain | `studio_templates` |
| Teardown / critique / output examples | `studio_case_library` |
| Lessons learned from the repo architecture | `studio_memory` |
| What not to replicate | `studio_antipatterns` |
| Schema and capture model | `ux_research` |
| Future exported screenshots | `visual_asset` |

## Recommended operating model

1. Keep the UX scraper repo as a tooling archive or browser-side extractor.
2. Promote all reusable learnings into Startup Intelligence OS.
3. Import exported runs into Susan instead of storing the intelligence in a parallel schema.
4. Route Marcus, Mira, Prism, Lens, Echo, Design Studio Director, and App Experience Studio through these imported assets.
