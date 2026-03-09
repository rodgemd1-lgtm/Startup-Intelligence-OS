# UX Scraper Gold Standard Reference

> Source repo: `/Users/mikerodgers/ux-design-scraper`
> Position: this repo is the gold-standard reference for Susan's design studios because it encodes a full-stack design workflow, a quality critique model, exportable implementation artifacts, and a disciplined operator UI.

## What makes it the standard

- it does not stop at inspiration; it turns analysis into deliverables
- it packages design work into reusable artifacts rather than loose notes
- it has a real operator interface, not just prompt text
- it blends research, critique, reconstruction, design system work, and handoff

## Gold-standard layers Susan should inherit

### 1. Workflow operating system
The workflow is not a generic brainstorm. It is an explicit sequence of research, definition, checkpointing, divergence, build, handoff, and measurement.

### 2. Operator shell quality
The sidepanel app demonstrates a compact operator shell:
- left navigation with badges
- dense but readable dark surfaces
- streaming/chat patterns
- progress and preview panels
- compare/critique/persona/results tabs
- workflow and batch queue views

### 3. Design-system discipline
The repo has a normalized token language:
- `brand` palette block with structured token steps
- `surface` palette block with structured token steps
- `dark` palette block with structured token steps

Typography:
- `Inter` for primary sans UI
- `JetBrains Mono` for system and technical detail

Useful CSS utilities:
- `animate-in`
- `glass-card`
- `glow-brand`
- `progress-ring-circle`
- `scrollbar-none`
- `scrollbar-thin`
- `shimmer`
- `streaming-dot`
- `text-balance`
- `transition-height`

### 4. Deliverable completeness
The output package expects:
- tokens
- screenshots
- analysis docs
- prompt packs
- CLAUDE execution files
- Storybook artifacts
- prototype output
- performance and accessibility guidance

## Adoption rule

When Mike says the UX scraper is the gold standard, Susan should interpret that as:
1. use its workflow structure
2. use its critique and deliverable rigor
3. use its operator-shell clarity and compactness
4. do not blindly copy the browser-extension UI into product surfaces
5. translate the standard into company-specific UX, especially TransformFit
