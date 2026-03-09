# v5 Jake Console — Design Document

**Date:** 2026-03-09
**Status:** Built and verified
**Surface:** `apps/v5/index.html` — single-file progressive web application
**Preview:** `python3 -m http.server 8080 --directory apps/v5`

## Design Decision

Build a fully operational three-column command center as the primary operator interface for the Startup Intelligence OS. The application serves as both a real-time dashboard and an execution surface — the operator should never wonder what workspace, company, branch, or decision is active.

## Architecture

### Surface Model
- **Single HTML file** with embedded CSS and JS (~1000 lines)
- **Three-column CSS Grid** layout: 252px sidebar / flexible center / 300px right rail
- **6 switchable views** with animated transitions
- **Live API integration** with static fallback when API is offline
- **Keyboard shortcuts** (1-6 for views, t for terminal)

### Views
| View | Purpose | Key Elements |
|------|---------|-------------|
| Workspace Home | Situational awareness | Metrics, Jake brief, decision/capability previews, terminal |
| Decision Room | Multi-perspective debate | 5 POV tabs, weighted scoring bars, output contract |
| Capability Map | Maturity assessment | Wave summary, maturity segments, critical gaps with urgency framing |
| Innovation Studio | Strategos future-back | 3 strategic bets, 5-year timeline, risk assumptions |
| Agent Console | Team visibility | 40 agents across 8 groups with color-coded badges |
| 25X Dashboard | Progress tracking | Progress-since indicator, domain bars, multiplier targets |

### Tech Stack
- **Fonts:** Outfit (headings/body) + JetBrains Mono (code/data)
- **Palette:** Navy dark (#07090e base), blue (#5b8def), mint (#5cd4a0), amber (#e8a84c), coral (#e06565)
- **Layout:** CSS Grid with responsive breakpoints at 1100px and 860px
- **API:** Fetches from localhost:8420 (FastAPI backend) with Promise.all, falls back to embedded state

## Design Principles Applied

### From Design Studio Doctrine
- **Trust before conversion** — system shows all state upfront, no hidden context
- **Clarity before spectacle** — information hierarchy drives layout, not decoration
- **Motion must explain** — staggered fadeInUp reveals, transition crossfades on view switch, progress bar animations that show direction

### From App Experience Studio
- **Moments of truth** — first open shows Jake brief with specific context and next moves
- **Progress visibility** — maturity bars, wave badges, % of target indicators throughout
- **Return trigger** — session badge, urgency badges, and "what changed" framing

## Behavioral Science Hooks

| Mechanism | Implementation | Location |
|-----------|---------------|----------|
| Loss aversion | Red "CRITICAL PATH" markers on Wave 1 low-maturity items | Home, Capability Map |
| Urgency framing | Pulsing "Wave 1: 7 capabilities unresolved" badge | Home |
| Endowed progress | "38% of the way to baseline" in progress-since banner | 25X Dashboard |
| Attention hierarchy | Danger-colored metrics, green first-action pulse | Home, Right Rail |
| Session continuity | Date badge, boot terminal message with timestamp | Home, Terminal |
| Next-best-action | Right rail with softPulse animation on first item | All views |

## Terminal

Interactive terminal embedded in Home and Decision Room views:
- **Static commands:** help, status, context, clear
- **Dynamic commands:** decisions (lists open decisions with scores), capabilities (ASCII bar chart with maturity and wave)
- **API commands:** Forwards unknown commands to API endpoint
- **Boot sequence:** Shows version, session timestamp, prompt

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| 1 | Workspace Home |
| 2 | Decision Room |
| 3 | Capability Map |
| 4 | Innovation Studio |
| 5 | Agent Console |
| 6 | 25X Dashboard |
| t / ` | Toggle terminal |

## Data Model

State is embedded for offline use and overwritten when API responds:
- `context` — workspace identity (company, project, decision, branch)
- `status` — counts (decisions, capabilities, runs)
- `debrief` — operator greeting and next actions
- `decisions` — 2 active decisions with options, scores, and metadata
- `capabilities` — 12 domains with maturity, target, wave, and gaps
- `agents` — 40 agents with name, role, group
- `vision` — 6 timeline items (2026-2031)

## 5-Year Vision (Strategos Future-Back)

| Year | Label | North Star |
|------|-------|-----------|
| 2026 | Year 0 | Stabilize + Ship — Decision kernel stable, TransformFit prototype |
| 2027 | Year 1 | Foundation — TransformFit ships, Susan proven for 3+ companies |
| 2028 | Year 2 | Portfolio Expansion — 5+ companies, automated daily ops |
| 2029 | Year 3 | Inflection Point — Multi-operator alpha, 70% autonomous studios |
| 2030 | Year 4 | Platform Maturity — 5+ paying operators, $100K+ ARR |
| 2031 | Year 5 | North Star — 10+ companies, $500K+ ARR, 120+ agents |

## Strategic Bets

1. **Intelligence Compounding** — Knowledge from Company N makes Company N+1 faster
2. **Agent Factory as Platform** — Other founders configure their own agent teams
3. **TransformFit as Proof** — A company built by 60 agents + 1 human with real users

## What's Next

1. **Wire live API** — Connect all views to FastAPI backend endpoints
2. **Migrate to Next.js** — Progressive enhancement for SSR, routing, auth
3. **Add debate interaction** — Click POV tabs to trigger real Claude debate
4. **Add capability drill-down** — Click a domain to see gaps, agents, and actions
5. **Session persistence** — Track operator sessions and show "since last visit" diffs
6. **Mobile responsive** — Collapse to single column with bottom nav on mobile
