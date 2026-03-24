# PAI V7: Visual Command Center — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** See the whole ecosystem. Build a dashboard app showing all 3 companies, agent status, memory health, task queue, and control plane — mobile-first so Mike can check from his phone.

**Depends On:** V0-V6 complete

**Score Target:** 88 → 91

---

## Pre-Flight Checklist

- [ ] V6 exit criteria all passed (multi-channel operational)
- [ ] All pipelines running (morning brief, email triage, goal progress)
- [ ] Agent registry complete (82 agents with status tracking)
- [ ] Memory health metrics available (consolidation stats, search accuracy)
- [ ] Supabase accessible for real-time data queries

---

## Phase 7A: Dashboard API

### Task 1: Build Dashboard API Server

**Files:**
- Create: `pai/dashboard/api/server.py`
- Create: `pai/dashboard/api/routes.py`
- Create: `pai/dashboard/api/models.py`

**Tech Stack:** FastAPI (Python) — reuses Susan backend venv

**API Endpoints:**
| Endpoint | Method | Data |
|----------|--------|------|
| `/api/status` | GET | System health (all services) |
| `/api/companies` | GET | All 3 companies with key metrics |
| `/api/agents` | GET | 82 agents with status, last invocation |
| `/api/memory` | GET | Memory tier stats (counts, health, freshness) |
| `/api/goals` | GET | Active goals with progress |
| `/api/pipelines` | GET | Pipeline status (last run, success/fail) |
| `/api/signals` | GET | Recent competitive signals (SCOUT) |
| `/api/ratings` | GET | Satisfaction trend (last 30 days) |
| `/api/brief/today` | GET | Today's morning brief |
| `/api/actions/approve` | POST | Approve a pending APPROVE-tier action |
| `/api/actions/pending` | GET | List pending APPROVE-tier actions |

**Implementation steps:**
1. Create FastAPI server with above routes
2. Pull data from: Supabase, pipeline logs, agent registry, health monitor
3. Add WebSocket endpoint for real-time status updates
4. Run on Mac Studio port 4174 (behind Tailscale)
5. Add API key authentication (simple bearer token)
6. Create launchd plist for auto-start

**Commit:** `feat(pai): dashboard API — FastAPI server with 11 endpoints for PAI status`

---

### Task 2: Build Real-Time Status Aggregator

**Files:**
- Create: `pai/dashboard/api/aggregator.py`

**What it does:**
Collects health and status from all PAI subsystems into a unified view.

**Status model:**
```python
{
    "timestamp": "2026-09-15T10:30:00",
    "overall_health": "GREEN",  # GREEN/YELLOW/RED
    "services": {
        "openclaw_gateway": {"status": "up", "uptime": "14d 3h"},
        "claude_brain": {"status": "up", "model": "opus", "context_usage": "35%"},
        "fabric_api": {"status": "up", "patterns_available": 233},
        "losslesclaw": {"status": "up", "dag_size": "2.3GB", "messages": 45000},
        "supabase": {"status": "up", "memories": 102000},
    },
    "pipelines": {
        "morning_brief": {"last_run": "06:00", "status": "success"},
        "email_triage": {"last_run": "10:15", "status": "success", "processed": 8},
        "goal_progress": {"last_run": "20:00", "status": "success"},
    },
    "metrics": {
        "satisfaction_avg_7d": 4.2,
        "pipeline_success_rate_7d": 0.96,
        "agent_invocations_7d": 47,
        "corrections_7d": 3,
    }
}
```

**Commit:** `feat(pai): status aggregator — unified health view across all PAI subsystems`

---

## Phase 7B: Dashboard Frontend

### Task 3: Build Dashboard Frontend

**Files:**
- Create: `pai/dashboard/app/` (Next.js or React PWA)

**Tech Stack:** Next.js 15 + Tailwind CSS + shadcn/ui — PWA-enabled for mobile

**Dashboard Layout (3-zone):**
```
┌──────────────────────────────────────────────────────┐
│ HEADER: Jake PAI — System Health: [GREEN] 🟢          │
├────────────────────┬─────────────────────────────────┤
│ LEFT SIDEBAR       │ MAIN CONTENT                     │
│                    │                                   │
│ Companies          │ ┌─────────────────────────────┐  │
│ • Startup Intel OS │ │ THE ONE THING TODAY          │  │
│ • Oracle Health    │ │ > [Priority engine output]   │  │
│ • Alex Recruiting  │ └─────────────────────────────┘  │
│                    │                                   │
│ Quick Actions      │ ┌──────────┐ ┌──────────┐       │
│ • Approve (3)      │ │ Goals    │ │ Signals  │       │
│ • View Brief       │ │ ████░ 65%│ │ 2 P1     │       │
│ • Ask Jake         │ │ ██░░░ 40%│ │ 5 P2     │       │
│                    │ └──────────┘ └──────────┘       │
│ Health             │                                   │
│ • Memory: 102K     │ ┌─────────────────────────────┐  │
│ • Agents: 82       │ │ Pipeline Status              │  │
│ • Pipelines: 5     │ │ Brief ✅ Triage ✅ Goals ✅   │  │
│ • Channels: 4      │ └─────────────────────────────┘  │
│                    │                                   │
│ Satisfaction       │ ┌─────────────────────────────┐  │
│ ████████░ 4.2/5    │ │ Recent Agent Activity        │  │
│ Trend: ↑           │ │ • steve-strategy (2h ago)    │  │
│                    │ │ • research-director (5h ago) │  │
└────────────────────┴─────────────────────────────────┘
```

**Implementation steps:**
1. Create Next.js 15 app with Tailwind + shadcn/ui
2. Pages: Dashboard (home), Companies, Agents, Memory, Pipelines, Settings
3. Real-time updates via WebSocket connection to API
4. Mobile responsive (PWA — installable on phone)
5. Action approval: tap to approve pending APPROVE-tier actions
6. Brief viewer: read morning brief in formatted view
7. "Ask Jake" widget: type a question, get Jake response inline
8. Deploy on Mac Studio port 4174

**Commit:** `feat(pai): dashboard frontend — Next.js PWA with real-time PAI status`

---

### Task 4: Build Company Detail Views

**Per-company view:**
- Agent team assigned to this company
- RAG knowledge: chunk count, freshness, coverage gaps
- Recent research outputs
- Competitive signals specific to this company
- Goals and progress
- Key metrics (whatever's relevant per company)

**Implementation steps:**
1. Create CompanyDetail component
2. Pull data from Susan RAG (per-company chunk counts)
3. Pull agent invocation history filtered by company
4. Pull SCOUT signals filtered by company
5. Pull goals filtered by company tag

**Commit:** `feat(pai): company detail views — per-company agents, knowledge, signals, goals`

---

### Task 5: Build Conversation DAG Visualization

**What it does:**
Visual representation of LosslessClaw's DAG structure — shows how conversations are connected, summarized, and referenced.

**Implementation steps:**
1. Read LosslessClaw DAG structure via `lcm_describe` tool
2. Render as interactive tree/graph (d3.js or react-flow)
3. Click a node → expand to see the conversation content
4. Color-code: green (active), blue (summarized), gray (archived)
5. Show which conversations are connected (shared context)

**Commit:** `feat(pai): conversation DAG visualization — interactive LosslessClaw graph`

---

## Phase 7C: Mobile Experience

### Task 6: PWA Configuration and Mobile Optimization

**Implementation steps:**
1. Configure Next.js PWA (next-pwa plugin)
2. Add service worker for offline reading of last brief
3. Add push notifications for P0 alerts (Web Push API)
4. Optimize for mobile viewport (375px width)
5. Add "Add to Home Screen" prompt
6. Test on iPhone (Safari) and Android (Chrome)

**Commit:** `feat(pai): mobile PWA — offline brief, push notifications, home screen install`

---

## Phase 7D: Verification

### Task 7: Dashboard Verification

**Tests:**
1. Dashboard loads on desktop with all widgets populated
2. Dashboard loads on mobile (phone browser) with responsive layout
3. Real-time updates: restart a service → dashboard shows status change within 30s
4. Action approval: approve a pending action from dashboard
5. Brief viewer: today's morning brief renders correctly
6. Company view: each company shows relevant agents and signals
7. Mike uses dashboard daily for 2+ weeks

**Commit:** `feat(pai): V7 visual command center verification complete`

---

## V7 Exit Criteria (All Must Pass)

- [ ] Dashboard API running on Mac Studio (FastAPI, port 4174)
- [ ] 11 API endpoints returning live data
- [ ] Dashboard frontend deployed (Next.js PWA)
- [ ] Mobile-responsive layout working on phone
- [ ] Real-time status updates via WebSocket
- [ ] All 3 company detail views populated
- [ ] Pipeline status visible and accurate
- [ ] Goal progress visible with trend
- [ ] Action approval from dashboard works
- [ ] Satisfaction trend chart renders
- [ ] PWA installable on phone
- [ ] Mike uses dashboard daily for 2+ weeks

**Score target: 88 → 91**
