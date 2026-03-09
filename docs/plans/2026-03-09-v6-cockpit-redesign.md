# Jake Console v6 — Cockpit Redesign

**Date**: 2026-03-09
**Status**: Approved
**Authors**: Jake, Susan (Marcus UX, Echo Neuro-Design)

## Problem Statement

The v5 Jake Console treats the terminal as a toggleable overlay at the bottom of the center column. The terminal is fake (React stub with hardcoded string matching). Capability ratings are static stubs with no rubric or progression system. The operator's primary interaction surface (CLI) is buried behind a dashboard.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Terminal type | Real xterm.js shell via WebSocket | Operator needs `claude`, `git`, `bin/jake` — real commands |
| Layout | Cockpit Pattern | Terminal dominates top 60-70%, context panel below 30-40% |
| Rating scale | 5-level Maturity Model | Nascent/Emerging/Scaling/Optimizing/Leading with per-level checklists |

## 1. Layout — The Cockpit Pattern

```
┌──────────┬──────────────────────────────┬──────────┐
│          │         TOPBAR (context)      │          │
│ SIDEBAR  ├──────────────────────────────┤ RIGHT    │
│ nav +    │                              │ RAIL     │
│ workspace│   TERMINAL (xterm.js)        │ next     │
│ team     │   60-70% height, resizable   │ actions  │
│          │   real PTY shell session      │ workspace│
│ 220px    ├── drag handle ───────────────┤ 280px    │
│          │   CONTEXT PANEL (30-40%)     │          │
│          │   reactive — switches by     │          │
│          │   nav click or terminal cmd  │          │
└──────────┴──────────────────────────────┴──────────┘
```

### Terminal Zone (top 60-70%)
- Full xterm.js terminal connected via WebSocket to a PTY shell
- Minimum height: 300px, no maximum
- Resizable via drag handle between terminal and context panel
- Background: `#060810` bleeds to edges — no card wrapper
- Shell starts in repo root: `/Users/mikerodgers/Startup-Intelligence-OS`
- Supports ANSI colors, cursor movement, tab completion, everything a real terminal does

### Context Panel (bottom 30-40%)
- Renders the active view: capability map, decisions, agents, innovation, dashboard
- Switches via sidebar navigation clicks
- Scrollable independently from terminal
- Acts as reference surface, not primary interaction surface

### Drag Handle
- 4px horizontal bar between terminal and context panel
- Cursor: `row-resize`
- Stores split position in localStorage
- Hover highlight: accent color

### Sidebar (220px, left)
- Navigation: Home, Decision Room, Capability Map, Innovation Studio, Agent Console, 25X Dashboard
- Workspace context: active company, project, decision
- Team indicators: Jake, Susan, Research, Build
- Live badge counts from API

### Right Rail (280px, right)
- Next actions (from debrief API)
- Workspace metadata (mode, front door, foundry, company)
- System connection status

## 2. Terminal — Real xterm.js Shell

### Architecture

```
Browser (Next.js)          Server (Node.js)
┌─────────────┐           ┌─────────────────┐
│  xterm.js   │◄─WebSocket─►│  node-pty       │
│  + fit      │           │  spawns shell   │
│  + weblinks │           │  (zsh/bash)     │
└─────────────┘           └─────────────────┘
```

### Server Component
- Lightweight Express + `ws` WebSocket server
- Uses `node-pty` to spawn a PTY shell process
- Runs on a dedicated port (e.g., 8421)
- Shell: user's default shell (zsh)
- CWD: repo root
- Environment: inherits user's shell env (PATH, API keys, etc.)

### Client Component
- `xterm.js` with addons: `xterm-addon-fit`, `xterm-addon-web-links`
- Connects to WebSocket on mount
- Auto-fits to container on resize
- Reconnects on disconnect

### What the operator can do
- Run `claude` to start Claude Code sessions
- Run `bin/jake status`, `bin/os-context`
- Run `git` commands
- Run any shell command
- Full ANSI color support, cursor movement, tab completion

## 3. Capability Rating System — Strategos Maturity Model

### 5-Level Scale

| Level | Name | Color | Description |
|-------|------|-------|-------------|
| 1 | Nascent | `#e06565` (red) | Identified and scoped. No reliable execution. |
| 2 | Emerging | `#e8a84c` (amber) | Manual, inconsistent. Depends on operator attention. |
| 3 | Scaling | `#5b8def` (blue) | Works reliably. Has process. Produces consistent outputs. |
| 4 | Optimizing | `#5cd4a0` (green) | Automated, measured, self-improving. Operator can step back. |
| 5 | Leading | `#c4a1f7` (purple) | Benchmark-setting. Generates leverage. Produces new capabilities. |

### Per-Level Checklists

Each capability domain has 3-5 verifiable items per level, stored in YAML:

```yaml
# .startup-os/capabilities/decision-kernel.yaml
id: decision-kernel
name: Decision Kernel
maturity_current: 2
maturity_target: 4
wave: 1
owner_human: Mike Rodgers
owner_agent: jake
gaps:
  - automated lineage
  - outcome tracking
levels:
  1:
    name: Nascent
    items:
      - text: "Capability identified and scoped"
        done: true
      - text: "Owner assigned"
        done: true
      - text: "Build sequence defined"
        done: true
  2:
    name: Emerging
    items:
      - text: "Decision record template created"
        done: true
      - text: "At least 2 decisions written as records"
        done: true
      - text: "Options scoring available"
        done: false
  3:
    name: Scaling
    items:
      - text: "All decisions use record schema"
        done: false
      - text: "Decision engine runs autonomously"
        done: false
      - text: "Debate modes operational"
        done: false
      - text: "Decision outcome tracking v1"
        done: false
  4:
    name: Optimizing
    items:
      - text: "Automated decision lineage"
        done: false
      - text: "Decision quality scoring"
        done: false
      - text: "Self-improving option generation"
        done: false
      - text: "Cross-decision pattern detection"
        done: false
```

### Maturity Auto-Advancement

When all items in a level are marked `done`, the capability's `maturity_current` auto-advances to that level. Partial completion within a level shows as sub-level progress (e.g., 2/4 items in Level 3 = maturity 2.5).

### API Endpoints (New)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/capabilities/{id}/levels` | GET | Full level checklist for a capability |
| `PUT /api/capabilities/{id}/levels/{level}/items/{index}` | PUT | Toggle a checklist item done/undone |
| `GET /api/capabilities/summary` | GET | All capabilities with current/target maturity and next-action |

### Visualization

**List view (Capability Map)**: Segmented maturity bars with level abbreviations (NAS/EMR/SCL/OPT/LDG), gradient fill within partially-completed levels, dashed outline for target.

```
DECISION KERNEL    [NAS][EMR][SCL     ][OPT----][   ]  2.5 → 4.0
                                ^next milestone
```

**Drill-down (single domain)**: Vertical level stack showing all 5 levels, filled/partial/empty segments, and the specific checklist items for the next incomplete level.

**Overview (25X Dashboard)**: Domain heat map — 12 domains in a grid, color-coded by maturity level. Wave grouping (W1/W2/W3).

## 4. Behavioral Science Integration

### Single-Focus Urgency
- Context panel shows ONE focus capability at a time (the lowest-maturity Wave 1 domain)
- "X capabilities waiting behind this one" — explains sequencing, creates leverage feeling
- Loss frame + gain frame paired: "Without this: X. With this: Y."
- Never red-flag more than one item simultaneously

### Threshold Signals
- When a capability is 1 item from leveling up, it gets a `THRESHOLD >>` marker
- This activates anticipatory dopamine — concrete, achievable micro-goal

### Endowed Progress
- Show completed Level 1 and 2 items explicitly — the operator is further along than the maturity number suggests
- "7/13 steps complete (54%)" alongside "Maturity: 2/4"

### Session Continuity
- "Day N" counter (elapsed days since first session, not streak)
- "Welcome back" framing on return — capabilities held, nothing degraded
- Pre-loaded next action on session open

## 5. Scope — What Changes

### Stays from v5
- Sidebar navigation structure (6 views)
- Right rail (actions + workspace)
- Topbar (context breadcrumbs)
- Dark theme and color palette
- Behavioral science CSS hooks
- SWR data fetching with static fallback
- Mobile bottom nav

### Changes
- Terminal moves from overlay at bottom to hero position top 60-70%
- Home page becomes cockpit summary (session status + focus capability)
- Capability Map gets new maturity visualization with drill-down checklists
- AppShell layout restructured for cockpit split

### New
- WebSocket terminal server (`apps/v5/server/terminal.ts`)
- xterm.js client integration
- Capability level YAML schema and seed data for all 12 domains
- New API endpoints for level management
- Maturity auto-advancement logic in capability engine
- Drag-handle resize component

## 6. 12 Capability Domains

All must reach Level 4 (Optimizing):

| Domain | Current | Target | Wave | Focus |
|--------|---------|--------|------|-------|
| Data & Analytics | 1.2 | 4.0 | W1 | Telemetry, metrics pipeline |
| Platform Infrastructure | 1.3 | 4.0 | W1 | Runtime, deployment, CI |
| Operator Experience | 1.5 | 4.0 | W1 | Console, session protocol |
| Innovation & Strategy | 1.8 | 4.0 | W2 | Vision, scenario planning |
| Studio Operations | 1.8 | 4.0 | W2 | Writeback, experiments |
| Portfolio Management | 1.8 | 4.0 | W3 | Multi-company orchestration |
| Content & Marketing | 1.8 | 4.0 | W3 | Publishing, proof spines |
| Agent Orchestration | 2.0 | 4.5 | W1 | Routing, memory, multi-agent |
| Decision Kernel | 2.0 | 4.0 | W1 | Records, engine, debate |
| Capability Management | 2.0 | 4.0 | W1 | This system itself |
| UX & Design | 2.2 | 4.0 | W2 | Design system, Figma |
| Intelligence & Research | 2.8 | 4.5 | W1 | RAG, triangulation |
