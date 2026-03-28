# Plan: Scorched Earth Simplification + Oracle Health Department Build

**Date:** 2026-03-28
**Status:** PENDING APPROVAL
**Author:** Jake
**Approver:** Mike Rodgers

---

## Problem Statement

The system has 81+ defined agents, 8,500 lines of dead PAI code, stub apps with no implementation, and broken Python imports. Oracle Health — Mike's actual job — has only 3 agents with no orchestration. The architecture is wide, shallow, and fragile.

## Goals

1. **Cut dead weight** — remove code and config that isn't wired to anything running
2. **Fix what's broken** — resolve Python import failures so the real backend works
3. **Build Oracle Health deep** — full department with meta-agent, super-agents, agents, sub-agents, real data pipelines, and gold-standard outputs

---

## Phase 1: Cut (This Session)

### 1A. Delete Dead Code
- [ ] `rm -rf pai/` — 8,500 lines, zero imports from production code, explicitly deprecated in HANDOFF.md
- [ ] `rm -rf apps/intelligence-cockpit/` — 1 JS file, no backend, UI mockup only
- [ ] `rm -rf apps/ios-device-probe/` — README only, no implementation
- [ ] `rm -rf apps/roadmap-viewer/` — no implementation files

### 1B. Fix Broken Python Imports
- [ ] `cd susan-team-architect/backend && source .venv/bin/activate`
- [ ] `pip install pyyaml pydantic` (fixes memory.signal_processor, susan_core.phase_runtime, research_daemon, collective)
- [ ] Fix supabase import issue in jake_cost/router.py (API version mismatch)
- [ ] Verify all core modules import cleanly: `python -c "import susan_core; import memory; import research_daemon; import collective; import jake_cost"`

### 1C. Clean Briefing Skill
- [ ] Update `.claude/skills/briefing/SKILL.md` — remove PAI pipeline reference, point to `bin/jake-morning-pipeline.sh`

---

## Phase 2: Oracle Health Department (This Session — Structure + Director)

### Current State
- 3 agents: oracle-brief (lead), oracle-health-marketing-lead, oracle-health-product-marketing
- 10,788 RAG chunks in Supabase
- Oracle Sentinel running daily at 6 AM
- 19 domain data files
- 510-line competitive intelligence inventory
- NO orchestration between agents
- NO content production pipeline
- NO win-loss feedback loop

### Target State — Full Department Hierarchy

```
Oracle Health Department (Tier 1 Meta-Agent: Oracle Health Director)
│
├── Super Agent: Market Intelligence (Tier 2)
│   ├── Agent: Competitive Monitor — continuous Epic/Microsoft/AWS/Meditech/Veeva tracking
│   ├── Agent: Signal Analyst — triage, score, route competitive signals
│   └── Sub-agent: News Harvester — Firecrawl feeds into Supabase RAG
│
├── Super Agent: Content & Positioning (Tier 2)
│   ├── Agent: Marketing Lead (existing oracle-health-marketing-lead — enhanced)
│   ├── Agent: Persona Specialist — CIO, CMIO, Ops, Clinical messaging banks
│   └── Sub-agent: Proof Collector — screenshots, workflow evidence, claims registry
│
├── Super Agent: Sales Enablement (Tier 2)
│   ├── Agent: Battlecard Manager — Klue-format cards, auto-update from signals
│   ├── Agent: Objection Handler — per-persona objection/response pairs
│   └── Sub-agent: Asset Producer — decks, one-pagers, executive briefs
│
└── Gold Standard Agent: Oracle Sentinel (existing — enhanced)
    └── Daily brief, stale data alerts, coverage gaps, freshness scoring
```

### 2A. Create Oracle Health Director (Meta-Agent)
**File:** `.claude/agents/oracle-health-director.md`

The Director is the orchestrator. When Mike says "I need a battlecard on Epic's new release" or "What's Microsoft doing in ambient clinical?" — the Director:
1. Routes to the right super-agent
2. Ensures research completes before content production
3. Validates outputs against compliance rules
4. Delivers finished artifacts

### 2B. Create Super-Agent Definitions
**Files:**
- `.claude/agents/oh-market-intelligence.md`
- `.claude/agents/oh-content-positioning.md`
- `.claude/agents/oh-sales-enablement.md`

Each super-agent knows:
- What agents it manages
- What data sources it owns
- What outputs it produces
- Quality gates before delivery

### 2C. Create Agent Definitions
**Files:**
- `.claude/agents/oh-competitive-monitor.md`
- `.claude/agents/oh-signal-analyst.md`
- `.claude/agents/oh-persona-specialist.md`
- `.claude/agents/oh-battlecard-manager.md`
- `.claude/agents/oh-objection-handler.md`

Each agent has:
- Clear input/output contract
- Data sources (Supabase tables, RAG namespaces)
- Quality criteria
- Example outputs

### 2D. Enhance Oracle Sentinel
- Add freshness scoring per competitor per data type
- Add gap detection: "No Microsoft DAX data in 14 days"
- Add auto-alert routing to Director

### 2E. Update agent-hierarchy.yaml
- Promote Oracle Health Director to Tier 1 meta-agent (alongside Jake, KIRA, Susan)
- Add 3 super-agents at Tier 2
- Add 5 new agents at Tier 3
- Budget: $25/mo ceiling for full department

### 2F. Create Oracle Health Gold Standard Outputs
**Directory:** `susan-team-architect/backend/data/domains/oracle_health_intelligence/gold_standards/`

Templates for every output the department produces:
- Executive brief (1-pager for Matt)
- Competitive battlecard (Klue format)
- Persona messaging bank (per buyer role)
- Objection response sheet
- Weekly intelligence digest

---

## Phase 3: Wire Orchestration (Next Session)

NOT in this session. Noted here for continuity:
- Python orchestration code in `susan-team-architect/backend/oracle_health/`
- Firecrawl → Supabase ingestion pipeline
- Director dispatch logic
- Automated battlecard refresh

---

## What This Session Delivers

1. ~9,000 lines of dead code removed
2. Python backend imports fixed
3. Oracle Health promoted from 3-agent afterthought to 12-agent department with meta-agent
4. Gold standard output templates for every deliverable
5. Updated agent-hierarchy.yaml reflecting reality

---

## What This Does NOT Do (Explicitly Deferred)

- No new Python runtime code (orchestration is next session)
- No Firecrawl pipeline wiring
- No cloud API deployment
- No changes to other departments
