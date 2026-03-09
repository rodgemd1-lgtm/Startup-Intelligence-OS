# UX Scraper Workflow Operating System

> Source repo: `/Users/mikerodgers/ux-design-scraper`
> Source file: `src/shared/workflow-constants.ts`

## Canonical phases

- `discover` / `Discover` -> BB1 Diverge — Research & data gathering. Brave deep search, multi-site scrape, trend analysis, knowledge enrichment.
- `define` / `Define` -> BB1 Converge — Personas, journey maps, design principles, design brief, accessibility requirements.
- `gate` / `Gate` -> Review & approval checkpoint. All BB1 outputs reviewed before entering BB2.
- `diverge` / `Diverge` -> BB2 Diverge — Generate 3-5 design directions, moodboards, critique, competitive positioning.
- `develop` / `Develop` -> BB2 Build — Component reconstruction, design system, copy rewriting, Storybook, prototype.
- `deliver` / `Deliver` -> BB2 Converge — CLAUDE.md, Figma tokens, performance budget, accessibility report, output folder.
- `measure` / `Measure` -> Post-ship — A/B test plans, heatmap analysis, performance monitoring, iteration roadmap.

## Why this matters for Susan

This is the clearest reusable design workflow currently in your system:
- Discover gathers evidence
- Define converts evidence into principles and requirements
- Gate forces review before more expensive design work
- Diverge creates multiple routes instead of locking onto the first idea
- Develop turns a direction into a buildable system
- Deliver packages the work for execution
- Measure closes the loop with post-ship learning

## Susan-native translation

- `susan-fast` should use a compressed Discover + Define + Deliver path
- `susan-design` should use the full workflow with Gate and Diverge
- `susan-foundry` should capture Deliver + Measure outputs into foundry memory

## TransformFit implication

TransformFit UI/UX work should stop skipping from concept to code. The minimum standard becomes:
1. discover the workout context and moments of truth
2. define gym-state constraints, emotional goals, and a11y rules
3. gate the experience direction
4. diverge on session, onboarding, and dashboard concepts
5. develop with tokens, component rules, and coaching behaviors
6. deliver engineering-ready specs and prompts
7. measure adherence, friction, trust, and session completion
