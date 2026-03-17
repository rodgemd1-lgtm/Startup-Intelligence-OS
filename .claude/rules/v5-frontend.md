---
paths:
  - "apps/v5/**"
---

# V5 Frontend Rules

## Stack
- Next.js (App Router)
- React with TypeScript
- Tailwind CSS
- ESLint configured (`eslint.config.mjs`)

## Layout
- Three-zone layout: navigation, main content, right rail
- `AppShell.tsx` — main layout wrapper
- `RightRail.tsx` — context panel
- Dark theme default

## Key Components
- `src/app/page.tsx` — home/dashboard
- `src/app/capabilities/page.tsx` — capability browser
- `src/components/LevelChecklist.tsx` — maturity level UI
- `src/components/AskRouterPanel.tsx` — routing panel
- `src/hooks/useApi.ts` — API hook
- `src/lib/api.ts` — API client

## Conventions
- Use App Router patterns (not Pages Router)
- Components in `src/components/`
- Pages in `src/app/`
- Hooks in `src/hooks/`
- Utilities in `src/lib/`
- Prefer server components where possible
- Client components marked with `'use client'`

## Development
```bash
cd apps/v5
npm run dev
npm run build
npm run lint
```
