# v5 Jake Console — All Next Moves Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Migrate the v5 Jake Console from a single-file SPA to a Next.js app with live API, debate interaction, capability drill-down, session persistence, and mobile responsive design.

**Architecture:** Next.js 15 App Router with TypeScript. Three-column CSS Grid layout preserved from the original SPA. All views become route segments. Shared state via React context + SWR for API. Static fallback data preserved for offline mode.

**Tech Stack:** Next.js 15, TypeScript, Tailwind CSS v4, SWR, CSS custom properties (ported from v5 palette)

---

### Task 1: Scaffold Next.js Project

**Files:**
- Create: `apps/v5/package.json`
- Create: `apps/v5/next.config.ts`
- Create: `apps/v5/tsconfig.json`
- Create: `apps/v5/tailwind.config.ts`
- Create: `apps/v5/postcss.config.mjs`
- Preserve: `apps/v5/index.html` (rename to `apps/v5/index.reference.html`)

**Step 1: Rename the original SPA for reference**
```bash
cd /Users/mikerodgers/Startup-Intelligence-OS/apps/v5
mv index.html index.reference.html
```

**Step 2: Initialize Next.js with TypeScript and Tailwind**
```bash
cd /Users/mikerodgers/Startup-Intelligence-OS/apps/v5
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --no-import-alias --use-npm
```
Answer prompts: Yes to all defaults. If it complains about existing files, allow overwrite of everything except `index.reference.html`.

**Step 3: Install additional dependencies**
```bash
cd /Users/mikerodgers/Startup-Intelligence-OS/apps/v5
npm install swr
```

**Step 4: Update next.config.ts for the project**

```typescript
// apps/v5/next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8420/api/:path*",
      },
    ];
  },
};

export default nextConfig;
```

This proxies `/api/*` requests to the FastAPI backend on port 8420, avoiding CORS issues.

**Step 5: Verify scaffold works**
```bash
cd /Users/mikerodgers/Startup-Intelligence-OS/apps/v5
npm run dev
```
Expected: Next.js dev server starts on port 3000.

**Step 6: Commit**
```bash
git add apps/v5/
git commit -m "feat(v5): scaffold Next.js project with TypeScript and Tailwind"
```

---

### Task 2: Port CSS Design System to globals.css

**Files:**
- Modify: `apps/v5/src/app/globals.css`
- Reference: `apps/v5/index.reference.html` (lines 10-850 for all CSS)

**Step 1: Write globals.css with all CSS custom properties and component styles**

Port the ENTIRE `<style>` block from `index.reference.html` into `globals.css`. The file should contain:

1. Tailwind directives at top (`@import "tailwindcss"`)
2. All CSS custom properties in `:root` (the exact palette: --bg, --surface-1 through --surface-raised, --border, --text variants, --accent, --success, --warning, --danger, --font, --mono, --radius, --shadow)
3. All component classes from the SPA: `.app`, `.sidebar`, `.main`, `.topbar`, `.pane`, `.rightbar`, scrollbar styles, typography, sidebar nav, workspace cards, topbar badges, cards, metrics, grids, jake brief, list items, tags, progress bars, maturity rows, score bars, debate tabs, agent cards, timeline, terminal, right rail, all animations (@keyframes fadeIn, fadeInUp, slideInLeft, slideInRight, countUp, pulse, softPulse, breathe, shimmer, scaleIn, borderPulse), behavioral science hooks (.urgency-badge, .streak-badge, .critical-path, .progress-since, .wave-label), and responsive breakpoints
4. Add Google Fonts import for Outfit and JetBrains Mono
5. Add NEW mobile responsive styles (Task 14 CSS goes here too):

```css
/* Mobile responsive - bottom nav */
@media (max-width: 768px) {
  .app {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr auto;
  }
  .sidebar, .rightbar { display: none; }
  .topbar { padding: 8px 12px; }
  .topbar .ctx-badges { display: none; }
  .metrics-row { grid-template-columns: repeat(2, 1fr); }
  .grid-2, .grid-3, .grid-equal { grid-template-columns: 1fr; }
  .bottom-nav {
    display: flex;
    justify-content: space-around;
    align-items: center;
    padding: 8px 0;
    background: var(--surface-1);
    border-top: 1px solid var(--border-subtle);
    position: fixed;
    bottom: 0; left: 0; right: 0;
    z-index: 100;
  }
  .bottom-nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    padding: 4px 8px;
    color: var(--text-tertiary);
    font-size: 0.65rem;
    cursor: pointer;
    transition: color 0.2s;
  }
  .bottom-nav-item.active { color: var(--accent); }
  .bottom-nav-item .nav-icon { font-size: 1.1rem; }
  .pane { padding-bottom: 70px; }
  .terminal { position: fixed; bottom: 56px; left: 0; right: 0; max-height: 50vh; z-index: 90; border-radius: 14px 14px 0 0; }
}

@media (min-width: 769px) {
  .bottom-nav { display: none; }
}

@media (max-width: 640px) {
  .metrics-row { grid-template-columns: 1fr; }
  h1 { font-size: 1.1rem; }
  .metric-value { font-size: 1.3rem; }
}
```

**Step 2: Verify CSS loads correctly**
```bash
cd /Users/mikerodgers/Startup-Intelligence-OS/apps/v5
npm run dev
```
Open browser — should see dark background with correct colors.

**Step 3: Commit**
```bash
git add apps/v5/src/app/globals.css
git commit -m "feat(v5): port complete CSS design system with mobile responsive"
```

---

### Task 3: Create Utility Libraries

**Files:**
- Create: `apps/v5/src/lib/utils.ts`
- Create: `apps/v5/src/lib/state.ts`
- Create: `apps/v5/src/lib/api.ts`

**Step 1: Create utils.ts**

```typescript
// apps/v5/src/lib/utils.ts
export function getGreeting(): string {
  const h = new Date().getHours();
  if (h < 12) return "Good morning, Mike";
  if (h < 17) return "Good afternoon, Mike";
  return "Evening, Mike";
}

export function maturityLabel(n: number): string {
  if (n <= 1) return "nascent";
  if (n <= 2) return "emerging";
  if (n <= 3) return "scaling";
  if (n <= 4) return "optimizing";
  return "leading";
}

export function maturityColor(n: number): string {
  if (n <= 1.5) return "danger";
  if (n <= 2.5) return "warning";
  if (n <= 3.5) return "accent";
  return "success";
}

export const groupColors: Record<string, string> = {
  orchestration: "#a78bfa",
  strategy: "#f0b45a",
  product: "#5b8def",
  engineering: "#5cd4a0",
  science: "#e88a5a",
  psychology: "#e06565",
  growth: "#5abbe8",
  research: "#8ba4cc",
  studio: "#d48aef",
};
```

**Step 2: Create state.ts with static fallback data**

Copy the entire `state` object from `index.reference.html` (lines 870-982) into a typed TypeScript module. Define interfaces for Context, Status, Debrief, Decision, Option, Capability, Agent, VisionItem. Export `defaultState`.

**Step 3: Create api.ts**

```typescript
// apps/v5/src/lib/api.ts
const API_BASE = "/api";

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  context: () => fetchJson<Record<string, string>>("/context"),
  status: () => fetchJson<Record<string, number>>("/status"),
  debrief: (operator = "mike") =>
    fetchJson<{ greeting: string; actions: Record<string, string[]>; debrief: string[]; status: string[] }>(
      `/debrief?operator=${operator}`
    ),
  decisions: () => fetchJson<Record<string, unknown>[]>("/decisions"),
  capabilities: () => fetchJson<Record<string, unknown>[]>("/capabilities"),
  debate: (decisionId: string, mode: string) =>
    fetch(`${API_BASE}/decision/${decisionId}/debate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode }),
    }).then((r) => r.json()),
};
```

**Step 4: Commit**
```bash
git add apps/v5/src/lib/
git commit -m "feat(v5): add utility libraries — api, state, utils"
```

---

### Task 4: Create React Hooks

**Files:**
- Create: `apps/v5/src/hooks/useApi.ts`
- Create: `apps/v5/src/hooks/useSession.ts`
- Create: `apps/v5/src/hooks/useKeyboard.ts`

**Step 1: Create useApi hook with SWR + static fallback**

```typescript
// apps/v5/src/hooks/useApi.ts
"use client";
import useSWR from "swr";
import { api } from "@/lib/api";
import { defaultState } from "@/lib/state";

const fetcher = <T,>(fn: () => Promise<T>) => fn();

export function useApi() {
  const ctx = useSWR("context", () => api.context(), {
    fallbackData: defaultState.context,
    onError: () => {},
    refreshInterval: 30000,
  });
  const status = useSWR("status", () => api.status(), {
    fallbackData: defaultState.status,
    onError: () => {},
    refreshInterval: 30000,
  });
  const debrief = useSWR("debrief", () => api.debrief(), {
    fallbackData: defaultState.debrief,
    onError: () => {},
  });

  const apiLive = !ctx.error && !status.error;

  return {
    context: ctx.data ?? defaultState.context,
    status: status.data ?? defaultState.status,
    debrief: debrief.data ?? defaultState.debrief,
    decisions: defaultState.decisions, // Will upgrade when API returns decisions with options
    capabilities: defaultState.capabilities,
    agents: defaultState.agents,
    vision: defaultState.vision,
    apiLive,
    refresh: () => { ctx.mutate(); status.mutate(); debrief.mutate(); },
  };
}
```

**Step 2: Create useSession hook for localStorage persistence**

```typescript
// apps/v5/src/hooks/useSession.ts
"use client";
import { useState, useEffect, useCallback } from "react";

interface SessionSnapshot {
  lastVisit: string;
  decisionCount: number;
  capabilityAvgMaturity: number;
  totalGaps: number;
  agentCount: number;
}

interface SessionDiff {
  daysSince: number;
  decisionsDelta: number;
  maturityDelta: number;
  gapsDelta: number;
  agentsDelta: number;
  isReturning: boolean;
}

const STORAGE_KEY = "jake-console-session";

export function useSession(current: {
  decisionCount: number;
  avgMaturity: number;
  totalGaps: number;
  agentCount: number;
}) {
  const [diff, setDiff] = useState<SessionDiff | null>(null);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const prev: SessionSnapshot = JSON.parse(stored);
        const daysSince = Math.floor(
          (Date.now() - new Date(prev.lastVisit).getTime()) / 86400000
        );
        setDiff({
          daysSince,
          decisionsDelta: current.decisionCount - prev.decisionCount,
          maturityDelta: +(current.avgMaturity - prev.capabilityAvgMaturity).toFixed(1),
          gapsDelta: current.totalGaps - prev.totalGaps,
          agentsDelta: current.agentCount - prev.agentCount,
          isReturning: daysSince > 0,
        });
      }
    } catch {}
  }, [current.decisionCount, current.avgMaturity, current.totalGaps, current.agentCount]);

  const saveSession = useCallback(() => {
    const snapshot: SessionSnapshot = {
      lastVisit: new Date().toISOString(),
      decisionCount: current.decisionCount,
      capabilityAvgMaturity: current.avgMaturity,
      totalGaps: current.totalGaps,
      agentCount: current.agentCount,
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
  }, [current]);

  // Auto-save on mount
  useEffect(() => {
    const timer = setTimeout(saveSession, 5000);
    return () => clearTimeout(timer);
  }, [saveSession]);

  return { diff, saveSession };
}
```

**Step 3: Create useKeyboard hook**

```typescript
// apps/v5/src/hooks/useKeyboard.ts
"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

const VIEW_MAP: Record<string, string> = {
  "1": "/",
  "2": "/decisions",
  "3": "/capabilities",
  "4": "/innovation",
  "5": "/agents",
  "6": "/dashboard",
};

export function useKeyboard(onToggleTerminal: () => void) {
  const router = useRouter();

  useEffect(() => {
    function handleKeydown(e: KeyboardEvent) {
      if ((e.target as HTMLElement).tagName === "INPUT" || (e.target as HTMLElement).tagName === "TEXTAREA") return;
      if (VIEW_MAP[e.key]) {
        router.push(VIEW_MAP[e.key]);
      }
      if (e.key === "t" || e.key === "`") {
        e.preventDefault();
        onToggleTerminal();
      }
    }
    document.addEventListener("keydown", handleKeydown);
    return () => document.removeEventListener("keydown", handleKeydown);
  }, [router, onToggleTerminal]);
}
```

**Step 4: Commit**
```bash
git add apps/v5/src/hooks/
git commit -m "feat(v5): add hooks — useApi (SWR+fallback), useSession (localStorage), useKeyboard"
```

---

### Task 5: Create Shared Components

**Files:**
- Create: `apps/v5/src/components/Sidebar.tsx`
- Create: `apps/v5/src/components/Topbar.tsx`
- Create: `apps/v5/src/components/RightRail.tsx`
- Create: `apps/v5/src/components/Terminal.tsx`
- Create: `apps/v5/src/components/MetricCard.tsx`
- Create: `apps/v5/src/components/ProgressBar.tsx`
- Create: `apps/v5/src/components/SessionBanner.tsx`
- Create: `apps/v5/src/components/BottomNav.tsx`

**Step 1: Create MetricCard and ProgressBar (smallest, most reused)**

MetricCard: Takes `label`, `value`, `color` ("accent"|"warning"|"success"|"danger"), `delay` (number). Renders the `.metric-card` with `.m-{color}` class and `.reveal` animation.

ProgressBar: Takes `value` (0-100), `color` string, `animated` boolean. Renders `.progress-track` > `.progress-fill` with `data-width` and animation.

**Step 2: Create Sidebar**

Port `renderNav()` from index.reference.html. Takes `currentPath` prop. Uses `useRouter()` for navigation. Renders: logo, section labels, workspace cards, nav items with active state based on pathname, team nav, sidebar footer with API status.

Navigation items map to routes:
- home → `/`
- decisions → `/decisions`
- capabilities → `/capabilities`
- innovation → `/innovation`
- agents → `/agents`
- dashboard → `/dashboard`

**Step 3: Create Topbar**

Port `renderTopbar()`. Takes `context` prop. Renders context badges (company, project, decision, branch) and toolbar buttons.

**Step 4: Create RightRail**

Port `renderRightRail()`. Takes `debrief` and `context` props. Renders next actions list and workspace summary.

**Step 5: Create Terminal**

Port the terminal from index.reference.html (lines 1400-1477). This is a client component with internal state for `history` and `visible`. Supports static commands (help, status, context, clear), dynamic commands (decisions, capabilities with ASCII bars), and API forwarding for unknown commands. Add boot message on mount.

**Step 6: Create SessionBanner**

New component for session persistence feature. Takes `diff` prop from `useSession`. Renders a `.progress-since` styled banner showing:
- "Welcome back — X days since last session"
- Delta indicators: "+N decisions", "maturity +0.X", "N gaps resolved"
- Only renders if `diff.isReturning` is true

**Step 7: Create BottomNav**

New component for mobile responsive. Renders nav items as icons with labels in a fixed bottom bar. Only visible below 768px (via CSS class `.bottom-nav`). Takes `currentPath` and `onNavigate` props.

**Step 8: Commit**
```bash
git add apps/v5/src/components/
git commit -m "feat(v5): create shared components — Sidebar, Topbar, RightRail, Terminal, MetricCard, ProgressBar, SessionBanner, BottomNav"
```

---

### Task 6: Create Root Layout

**Files:**
- Modify: `apps/v5/src/app/layout.tsx`

**Step 1: Create the three-column layout shell**

```typescript
// apps/v5/src/app/layout.tsx
import type { Metadata } from "next";
import { Outfit, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { AppShell } from "@/components/AppShell";

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-outfit",
  display: "swap",
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Jake Console — Startup Intelligence OS v5",
  description: "Command center for the Startup Intelligence OS",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${outfit.variable} ${jetbrains.variable}`}>
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
```

**Step 2: Create AppShell client component**

Create `apps/v5/src/components/AppShell.tsx` — a client component that wraps everything:
- Uses `useApi()` to get state
- Uses `useKeyboard()` for shortcuts
- Manages terminal visibility state
- Renders `.app` grid with `<Sidebar>`, `<main>` (children), `<RightRail>`, `<BottomNav>`
- Passes state down via React Context (`AppContext`)

```typescript
// apps/v5/src/components/AppShell.tsx
"use client";
import { createContext, useCallback, useContext, useState } from "react";
import { usePathname } from "next/navigation";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { RightRail } from "./RightRail";
import { BottomNav } from "./BottomNav";
import { useApi } from "@/hooks/useApi";
import { useKeyboard } from "@/hooks/useKeyboard";

// Context type matches useApi return
type AppState = ReturnType<typeof useApi>;
export const AppContext = createContext<AppState | null>(null);
export function useAppState() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppState must be inside AppShell");
  return ctx;
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const state = useApi();
  const pathname = usePathname();
  const [terminalVisible, setTerminalVisible] = useState(false);

  const toggleTerminal = useCallback(() => setTerminalVisible((v) => !v), []);
  useKeyboard(toggleTerminal);

  return (
    <AppContext.Provider value={state}>
      <div className="app">
        <Sidebar currentPath={pathname} apiLive={state.apiLive} agentCount={state.agents.length} />
        <div className="main">
          <Topbar context={state.context} />
          <div className="pane">
            <div className="pane-inner">{children}</div>
          </div>
        </div>
        <RightRail debrief={state.debrief} context={state.context} />
        <BottomNav currentPath={pathname} />
      </div>
    </AppContext.Provider>
  );
}
```

**Step 3: Verify layout renders**
```bash
cd /Users/mikerodgers/Startup-Intelligence-OS/apps/v5
npm run dev
```
Expected: Three-column layout visible at localhost:3000 with dark background, sidebar, and right rail.

**Step 4: Commit**
```bash
git add apps/v5/src/app/layout.tsx apps/v5/src/components/AppShell.tsx
git commit -m "feat(v5): create root layout with three-column AppShell"
```

---

### Task 7: Port Home View (Workspace Home)

**Files:**
- Modify: `apps/v5/src/app/page.tsx`

**Step 1: Port viewHome() from index.reference.html**

This is the main page at `/`. It renders:
1. Metrics row (4 cards: decisions, capability gaps, active runs, agents)
2. Session context badge + urgency badge
3. SessionBanner (if returning user — uses useSession hook)
4. Jake brief card with glow
5. Grid-2 with Decision Room preview and Capability Foundry preview (wave-sorted, critical-path on W1 low-maturity)
6. Terminal component

Use `useAppState()` to access state. Use `useSession()` for session diff.

Port the exact HTML structure from `viewHome()` (lines 1122-1183 in reference), converting to JSX.

**Step 2: Add useEffect for animating bars**

```typescript
useEffect(() => {
  const timer = setTimeout(() => {
    document.querySelectorAll(".bar-anim").forEach((bar) => {
      const w = bar.getAttribute("data-width");
      if (w) (bar as HTMLElement).style.width = `${w}%`;
    });
  }, 200);
  return () => clearTimeout(timer);
}, []);
```

**Step 3: Verify Home view renders**
Expected: Metrics row, Jake brief, decision/capability previews, terminal — all with animations.

**Step 4: Commit**
```bash
git add apps/v5/src/app/page.tsx
git commit -m "feat(v5): port Workspace Home view with session banner"
```

---

### Task 8: Port Decision Room with Debate Interaction

**Files:**
- Create: `apps/v5/src/app/decisions/page.tsx`
- Create: `apps/v5/src/components/DebatePanel.tsx`

**Step 1: Create DebatePanel component**

This is the NEW debate interaction feature. When a user clicks a POV tab (Builder, Skeptic, Contrarian, Operator, Red Team):
1. Tab becomes active with visual feedback
2. If API is live, POST to `/api/decision/{id}/debate` with `{ mode }`
3. Show loading spinner while waiting
4. Display the debate response: mode name, argument text, confidence bar, counter argument
5. If API offline, show static stub response per mode

```typescript
// apps/v5/src/components/DebatePanel.tsx
"use client";
import { useState } from "react";
import { api } from "@/lib/api";

const MODES = ["builder", "skeptic", "contrarian", "operator", "red_team"];
const MODE_LABELS: Record<string, string> = {
  builder: "Builder",
  skeptic: "Skeptic",
  contrarian: "Contrarian",
  operator: "Operator",
  red_team: "Red Team",
};

// Static fallback debate responses when API is offline
const STUB_DEBATES: Record<string, { argument: string; confidence: number; counter: string }> = {
  builder: {
    argument: "This approach maximizes value delivery speed and aligns with our north star. The technical foundations are solid and the team has the capability to execute.",
    confidence: 0.82,
    counter: "Execution speed may come at the cost of technical debt that compounds later.",
  },
  skeptic: {
    argument: "The assumptions underlying this decision have not been stress-tested. We lack evidence that the projected outcomes are achievable within the proposed timeline.",
    confidence: 0.65,
    counter: "Waiting for perfect information is itself a decision with opportunity cost.",
  },
  contrarian: {
    argument: "What if the opposite approach would yield better results? The conventional wisdom here may be anchoring us to suboptimal framing.",
    confidence: 0.58,
    counter: "Contrarian positions are valuable for pressure-testing but shouldn't override strong evidence.",
  },
  operator: {
    argument: "From a resource allocation perspective, this requires careful sequencing. The dependencies need to be mapped before committing capacity.",
    confidence: 0.75,
    counter: "Over-planning can be as damaging as under-planning. Ship and iterate.",
  },
  red_team: {
    argument: "If this decision fails, what is the blast radius? The failure modes need explicit enumeration and mitigation strategies must be pre-positioned.",
    confidence: 0.70,
    counter: "Red team concerns are valid but should not create decision paralysis.",
  },
};

interface DebatePanelProps {
  decisionId: string;
}

export function DebatePanel({ decisionId }: DebatePanelProps) {
  const [activeMode, setActiveMode] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<{
    mode: string;
    argument: string;
    confidence: number;
    counter: string;
  } | null>(null);

  async function handleModeClick(mode: string) {
    setActiveMode(mode);
    setLoading(true);
    try {
      const data = await api.debate(decisionId, mode);
      setResponse(data);
    } catch {
      // Fallback to stub
      setResponse({ mode, ...STUB_DEBATES[mode] });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="debate-tabs">
        {MODES.map((mode) => (
          <div
            key={mode}
            className={`debate-tab${activeMode === mode ? " active" : ""}`}
            onClick={() => handleModeClick(mode)}
          >
            {MODE_LABELS[mode]}
          </div>
        ))}
      </div>
      {loading && (
        <div style={{ padding: "16px", color: "var(--text-secondary)", fontSize: "0.85rem" }}>
          Running {activeMode} analysis...
        </div>
      )}
      {response && !loading && (
        <div style={{ padding: "14px", background: "var(--surface-2)", borderRadius: "var(--radius-sm)", marginTop: "10px", border: "1px solid var(--border-subtle)" }}>
          <div className="label" style={{ marginBottom: "8px" }}>{MODE_LABELS[response.mode]} POV</div>
          <p style={{ fontSize: "0.85rem", lineHeight: 1.6, marginBottom: "10px" }}>{response.argument}</p>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
            <span className="tertiary" style={{ fontSize: "0.72rem", width: "70px" }}>confidence</span>
            <div className="score-bar-track">
              <div
                className="score-bar-fill best"
                style={{ width: `${response.confidence * 100}%`, transition: "width 0.6s ease" }}
              />
            </div>
            <span className="mono tertiary" style={{ fontSize: "0.7rem" }}>{Math.round(response.confidence * 100)}</span>
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--warning)", fontStyle: "italic" }}>
            Counter: {response.counter}
          </div>
        </div>
      )}
    </div>
  );
}
```

**Step 2: Create decisions/page.tsx**

Port `viewDecisions()` from reference (lines 1187-1229). Replace static debate tabs with `<DebatePanel decisionId={d.id} />`. Keep the scoring bars and output contract sections.

**Step 3: Verify Decision Room renders with clickable debate tabs**
Expected: Click "Skeptic" tab → shows debate response with confidence bar.

**Step 4: Commit**
```bash
git add apps/v5/src/app/decisions/ apps/v5/src/components/DebatePanel.tsx
git commit -m "feat(v5): port Decision Room with interactive debate panel"
```

---

### Task 9: Port Capability Map with Drill-Down

**Files:**
- Create: `apps/v5/src/app/capabilities/page.tsx`
- Create: `apps/v5/src/components/CapabilityDrilldown.tsx`

**Step 1: Create CapabilityDrilldown component**

This is the NEW drill-down feature. When a user clicks a capability domain:
1. Row expands with animation to show detailed view
2. Lists each gap with description
3. Shows assigned agents (matched by domain→group mapping)
4. Shows recommended actions per gap
5. "Run gap analysis" button (calls Susan agent if API live)
6. Click again to collapse

Agent matching logic: Map capability domains to agent groups:
- Decision Kernel → orchestration, strategy
- Agent Orchestration → engineering, orchestration
- Intelligence & Research → research
- UX & Design → product, studio
- Platform Infrastructure → engineering
- Data & Analytics → engineering, science
- etc.

```typescript
// apps/v5/src/components/CapabilityDrilldown.tsx
"use client";
import { useState } from "react";
import { groupColors } from "@/lib/utils";

const DOMAIN_AGENTS: Record<string, string[]> = {
  "Decision Kernel": ["orchestration", "strategy"],
  "Capability Management": ["orchestration", "strategy"],
  "Innovation & Strategy": ["strategy", "studio"],
  "UX & Design": ["product", "studio"],
  "Agent Orchestration": ["engineering", "orchestration"],
  "Studio Operations": ["studio", "product"],
  "Intelligence & Research": ["research"],
  "Portfolio Management": ["strategy", "orchestration"],
  "Operator Experience": ["product", "engineering"],
  "Platform Infrastructure": ["engineering"],
  "Content & Marketing": ["growth", "studio"],
  "Data & Analytics": ["engineering", "science"],
};

// Recommended actions per gap type
const GAP_ACTIONS: Record<string, string> = {
  "LLM debate": "Wire DecisionEngine to Claude API for multi-POV debate",
  "evidence scoring": "Implement confidence scoring on evidence records",
  "outcome tracking": "Add outcome fields to decision records with feedback loops",
  "automated discovery": "Build capability scanner from codebase and docs",
  "design system": "Create Figma token pipeline with Tailwind integration",
  "semantic routing": "Implement intent-based agent routing with embeddings",
  "agent memory": "Add conversation persistence with pgvector storage",
  "auth": "Set up NextAuth with GitHub OAuth provider",
  "CI/CD": "Configure GitHub Actions for test + deploy pipeline",
  "monitoring": "Add Sentry error tracking and Vercel Analytics",
  "WebSockets": "Implement real-time updates with Socket.io or SSE",
  // Default for unmapped gaps
};

interface CapabilityDrilldownProps {
  capability: {
    name: string;
    maturity: number;
    target: number;
    gaps: string[];
    wave: number;
  };
  agents: { name: string; group: string; role: string }[];
}

export function CapabilityDrilldown({ capability, agents }: CapabilityDrilldownProps) {
  const [expanded, setExpanded] = useState(false);
  const relevantGroups = DOMAIN_AGENTS[capability.name] || [];
  const relevantAgents = agents.filter((a) => relevantGroups.includes(a.group));

  if (!expanded) return null;

  return (
    <div
      className="reveal"
      style={{
        padding: "14px",
        background: "var(--surface-2)",
        borderRadius: "var(--radius-sm)",
        marginTop: "8px",
        border: "1px solid var(--border)",
        animation: "fadeInUp 0.3s ease",
      }}
    >
      {/* Gaps with actions */}
      <div className="label" style={{ marginBottom: "8px" }}>
        Gaps & Recommended Actions
      </div>
      {capability.gaps.map((gap) => (
        <div key={gap} style={{ marginBottom: "8px", fontSize: "0.82rem" }}>
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <span className="danger">●</span>
            <strong>{gap}</strong>
          </div>
          <div className="item-meta" style={{ marginLeft: "18px" }}>
            {GAP_ACTIONS[gap] || `Address ${gap} gap to reach target maturity`}
          </div>
        </div>
      ))}

      {/* Assigned agents */}
      {relevantAgents.length > 0 && (
        <>
          <div className="label" style={{ margin: "12px 0 8px" }}>
            Assigned Agents ({relevantAgents.length})
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
            {relevantAgents.map((a) => (
              <span
                key={a.name}
                className="agent-group-badge"
                style={{
                  background: `${groupColors[a.group] || "#8ba4cc"}20`,
                  color: groupColors[a.group] || "#8ba4cc",
                  padding: "3px 8px",
                  borderRadius: "6px",
                  fontSize: "0.72rem",
                }}
              >
                {a.name}
              </span>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
```

Note: The `expanded` state should be managed by the parent (capabilities/page.tsx) which tracks which domain is currently expanded. The component above should receive `expanded` as a prop instead of managing it internally.

**Step 2: Create capabilities/page.tsx**

Port `viewCapabilities()` from reference (lines 1233-1278). Make each `.maturity-row` and critical gap `.list-item` clickable. Track `expandedDomain` state. When a domain is clicked, show `<CapabilityDrilldown>` inline below it.

**Step 3: Verify capability drill-down works**
Expected: Click "Platform Infrastructure" → expands to show gaps (auth, CI/CD, monitoring, WebSockets), assigned agents (Atlas, Nova, Sentinel, Forge), and recommended actions.

**Step 4: Commit**
```bash
git add apps/v5/src/app/capabilities/ apps/v5/src/components/CapabilityDrilldown.tsx
git commit -m "feat(v5): port Capability Map with interactive drill-down"
```

---

### Task 10: Port Remaining Views

**Files:**
- Create: `apps/v5/src/app/innovation/page.tsx`
- Create: `apps/v5/src/app/agents/page.tsx`
- Create: `apps/v5/src/app/dashboard/page.tsx`

**Step 1: Port Innovation Studio**

Port `viewInnovation()` from reference (lines 1282-1314). Three strategic bets cards, 5-year timeline, highest-risk assumptions. Straightforward JSX conversion.

**Step 2: Port Agent Console**

Port `viewAgents()` from reference (lines 1318-1345). Group agents, render grid-3 agent cards with color badges.

**Step 3: Port 25X Dashboard**

Port `viewDashboard()` from reference (lines 1348-1398). Include the endowed progress `.progress-since` banner, aggregate metrics, domain progress bars with wave labels, and 25X multiplier targets.

**Step 4: Verify all views render**

Navigate to each route:
- `/` — Home
- `/decisions` — Decision Room
- `/capabilities` — Capability Map
- `/innovation` — Innovation Studio
- `/agents` — Agent Console
- `/dashboard` — 25X Dashboard

**Step 5: Commit**
```bash
git add apps/v5/src/app/innovation/ apps/v5/src/app/agents/ apps/v5/src/app/dashboard/
git commit -m "feat(v5): port Innovation Studio, Agent Console, and 25X Dashboard"
```

---

### Task 11: Add Debate API Endpoint to Backend

**Files:**
- Modify: `apps/decision_os/api.py` (after line 253)

**Step 1: Add the debate endpoint**

```python
# Add after the get_decision endpoint

class DebateRequest(BaseModel):
    mode: str  # builder, skeptic, contrarian, operator, red_team


DEBATE_STUBS: dict[str, dict] = {
    "builder": {
        "argument": "This approach maximizes value delivery and aligns with strategic goals. The technical foundation supports execution at the proposed pace.",
        "confidence": 0.82,
        "counter": "Speed of execution may introduce technical debt.",
    },
    "skeptic": {
        "argument": "Key assumptions remain untested. The projected outcomes lack supporting evidence within the proposed timeline.",
        "confidence": 0.65,
        "counter": "Perfect information is unavailable — waiting has its own cost.",
    },
    "contrarian": {
        "argument": "The opposite approach may yield better results. Conventional framing could be anchoring us to a suboptimal path.",
        "confidence": 0.58,
        "counter": "Contrarian positions should pressure-test, not override strong evidence.",
    },
    "operator": {
        "argument": "Resource allocation and dependency sequencing need careful mapping before capacity commitment.",
        "confidence": 0.75,
        "counter": "Over-planning can be as costly as under-planning.",
    },
    "red_team": {
        "argument": "Failure modes need explicit enumeration. Blast radius analysis and mitigation strategies must be pre-positioned.",
        "confidence": 0.70,
        "counter": "Risk analysis should inform, not paralyze, decision-making.",
    },
}


@app.post("/api/decision/{decision_id}/debate")
def run_debate(decision_id: str, req: DebateRequest) -> dict:
    """Run a single-mode debate on a decision. Returns the perspective's argument."""
    dec = store.decisions.get(decision_id)
    if dec is None:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")

    valid_modes = {"builder", "skeptic", "contrarian", "operator", "red_team"}
    if req.mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Mode must be one of {valid_modes}")

    # Use engine if available
    if _engine_available and engine is not None and hasattr(engine, "debate"):
        result = engine.debate(decision_id=decision_id, mode=req.mode)
        return {"mode": req.mode, **result}

    # Stub response
    stub = DEBATE_STUBS.get(req.mode, DEBATE_STUBS["builder"])
    return {"mode": req.mode, **stub}
```

**Step 2: Also add CORS entry for port 3000 (Next.js dev server)**

In the CORS middleware `allow_origins` list, ensure `"http://localhost:3000"` is present. (It already is based on the existing code.)

**Step 3: Verify endpoint works**
```bash
cd /Users/mikerodgers/Startup-Intelligence-OS/apps/decision_os
# Start the API if not running
python -m uvicorn decision_os.api:app --port 8420 &
# Test the endpoint
curl -X POST http://localhost:8420/api/decision/dec-87215ce29d09/debate \
  -H "Content-Type: application/json" \
  -d '{"mode": "skeptic"}'
```
Expected: JSON with mode, argument, confidence, counter fields.

**Step 4: Commit**
```bash
git add apps/decision_os/api.py
git commit -m "feat(api): add debate endpoint for multi-POV decision analysis"
```

---

### Task 12: Update launch.json for Next.js Dev Server

**Files:**
- Modify: `apps/v5/.claude/launch.json` or root `.claude/launch.json`

**Step 1: Update launch configuration**

Replace the python http.server entry with the Next.js dev server:

```json
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "v5-console",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["run", "dev"],
      "port": 3000,
      "cwd": "apps/v5"
    }
  ]
}
```

**Step 2: Commit**
```bash
git add .claude/launch.json
git commit -m "chore: update launch.json for Next.js dev server"
```

---

### Task 13: Final Verification

**Step 1: Start both servers**
- Next.js dev server on port 3000 (via launch.json or `npm run dev` in apps/v5)
- FastAPI backend on port 8420 (if available)

**Step 2: Verify all 6 features**

1. **Live API**: Check that context badges update from API. Check "API connected" status in sidebar footer.
2. **Debate interaction**: Go to `/decisions`, click "Skeptic" tab, verify response appears with confidence bar.
3. **Capability drill-down**: Go to `/capabilities`, click "Platform Infrastructure" row, verify expansion shows gaps, agents, actions.
4. **Session persistence**: Visit Home, wait 5 seconds (auto-save), close tab, reopen — verify SessionBanner shows "Welcome back".
5. **Mobile responsive**: Resize viewport to 375px width — verify single column layout with bottom nav, no horizontal scroll.
6. **Next.js migration**: Verify all 6 routes work: `/`, `/decisions`, `/capabilities`, `/innovation`, `/agents`, `/dashboard`. Verify keyboard shortcuts (1-6, t).

**Step 3: Check for console errors**
Open browser dev tools, navigate through all views. Zero JS errors expected.

**Step 4: Final commit**
```bash
git add -A
git commit -m "feat(v5): complete all next moves — Next.js migration, live API, debate, drill-down, sessions, mobile"
```
