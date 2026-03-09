# v5 Jake Console — Next Moves Design Document

**Date:** 2026-03-09
**Status:** Approved
**Approach:** A — Next.js migration first, then features on proper foundation

## Scope

Six features, implemented in order:

1. **Migrate to Next.js** — Port single-file SPA to App Router with components
2. **Wire live API** — Connect all views to FastAPI backend at port 8420
3. **Add debate interaction** — POV tabs trigger backend debate, stream response
4. **Add capability drill-down** — Click domain to expand gaps/agents/actions
5. **Session persistence** — localStorage snapshot + "since last visit" diff
6. **Mobile responsive** — Single column with bottom nav below 768px

## Architecture

```
apps/v5/
├── index.html              (preserved as reference)
├── package.json
├── next.config.ts
├── tailwind.config.ts
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx        (Workspace Home)
│   │   ├── decisions/page.tsx
│   │   ├── capabilities/page.tsx
│   │   ├── innovation/page.tsx
│   │   ├── agents/page.tsx
│   │   └── dashboard/page.tsx
│   ├── components/
│   │   ├── Sidebar.tsx
│   │   ├── Topbar.tsx
│   │   ├── RightRail.tsx
│   │   ├── Terminal.tsx
│   │   ├── MetricCard.tsx
│   │   ├── ProgressBar.tsx
│   │   ├── DebatePanel.tsx
│   │   ├── CapabilityDrilldown.tsx
│   │   └── SessionBanner.tsx
│   ├── hooks/
│   │   ├── useApi.ts
│   │   ├── useSession.ts
│   │   └── useKeyboard.ts
│   ├── lib/
│   │   ├── api.ts
│   │   ├── state.ts
│   │   └── utils.ts
│   └── styles/
│       └── globals.css
```

## Backend Addition

New endpoint in `apps/decision_os/api.py`:

```
POST /api/decision/{id}/debate
Body: { "mode": "builder" | "skeptic" | "contrarian" | "operator" | "red_team" }
Returns: { "mode": str, "argument": str, "confidence": float, "counter": str }
```

## Design Principles

- Preserve exact palette, fonts, animations from v5 SPA
- Static fallback when API offline (same as current behavior)
- Behavioral science hooks carried forward (loss aversion, urgency, endowed progress)
- Keyboard shortcuts preserved (1-6 views, t terminal)
