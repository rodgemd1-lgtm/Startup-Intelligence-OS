# UX Scraper Sidepanel UI System

> Source repo: `/Users/mikerodgers/ux-design-scraper`
> Source files:
> - `src/sidepanel/App.tsx`
> - `src/sidepanel/styles.css`
> - `tailwind.config.js`

## Core shell

The sidepanel is a compact operator interface with:
- persistent sidebar navigation
- badge-based information scent
- compact header with live run state
- a single main content frame that swaps tools without losing shell stability

## Imported component patterns

Primary components discovered from the app shell:
- `BatchQueuePanel`
- `ChatContainer`
- `ComparisonView`
- `CritiquePanel`
- `OnboardingFlow`
- `PersonaList`
- `PreviewPanel`
- `ReconstructedGallery`
- `ResultsOverview`
- `ScrapeProgress`
- `SettingsPanel`
- `WorkflowPanel`

## Reusable interaction patterns

- streaming status indicator instead of blocking spinners
- glass-card surfaces for dense operator contexts
- shimmer loading for data-heavy panels
- badge counts for queue/workflow awareness
- compact typography and dense spacing without collapsing readability

## Reuse rule for company apps

Use this shell as precedent for:
- design/research studios
- founder operator consoles
- internal dashboards
- QA, workflow, and review panels

Do not copy it literally for:
- consumer landing pages
- active workout screens
- emotionally warm coaching moments

For TransformFit specifically:
- borrow the operator clarity for internal studio tools and coach/admin views
- borrow the streaming/chat/container patterns for coach threads
- do not turn the consumer workout session into an extension-style dashboard
