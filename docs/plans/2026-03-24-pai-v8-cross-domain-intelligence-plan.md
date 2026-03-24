# PAI V8: Cross-Domain Intelligence — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Patterns that transfer. Build cross-portfolio synergy detection, predictive capability modeling, knowledge graph federation across all 3 companies, and the Daemon API for machine-readable personal endpoint.

**Depends On:** V0-V7 complete

**Score Target:** 91 → 93

---

## Pre-Flight Checklist

- [ ] V7 exit criteria all passed (dashboard operational)
- [ ] All 3 companies have active data in Susan RAG
- [ ] SCOUT competitive intelligence running for all 3 companies
- [ ] Knowledge graph has 100+ entities across companies
- [ ] Learning engine producing weekly synthesis

---

## Phase 8A: Cross-Portfolio Synergy Detection

### Task 1: Build Synergy Detector

**Files:**
- Create: `pai/intelligence/synergy_detector.py`
- Adapt from: `susan-team-architect/backend/collective/knowledge_transfer.py`

**What it does:**
Automatically detects patterns, techniques, and capabilities that can transfer between companies.

**Synergy types:**
| Type | Example |
|------|---------|
| **Pattern transfer** | Multi-agent orchestration from Startup OS → Oracle Health agent deployment |
| **Capability reuse** | Susan RAG architecture → Alex Recruiting knowledge base |
| **Resource sharing** | ElevenLabs voice setup → used by all 3 companies |
| **Market insight** | Oracle Health enterprise sales learnings → Alex Recruiting B2B strategy |
| **Technical debt** | Bug fix pattern in one → prevent same bug in others |

**Implementation steps:**
1. Port `collective/knowledge_transfer.py` to PAI architecture
2. Build weekly cross-company analysis:
   - Compare SCOUT signals across companies
   - Compare Learning extracts across companies
   - Compare capability maturity scores across companies
3. Use Fabric `extract_patterns` on combined cross-company data
4. Generate synergy report: what patterns transfer, confidence level, suggested actions
5. Deliver synergy report in weekly digest (Sunday, after weekly synthesis)
6. Store synergy records in Supabase `jake_synergies` table
7. Target: 5+ cross-domain pattern transfers identified in first quarter

**Commit:** `feat(pai): synergy detector — cross-portfolio pattern transfer identification`

---

### Task 2: Build Predictive Capability Modeling

**Files:**
- Create: `pai/intelligence/capability_predictor.py`
- Adapt from: `susan-team-architect/backend/collective/capability_predictor.py`

**What it does:**
Forecasts when capabilities will reach maturity milestones based on current trajectory.

**Prediction model:**
1. Track capability maturity scores over time (from self-evaluation)
2. Fit growth curve (logistic — capabilities have natural ceilings)
3. Project: when will each domain reach target score?
4. Identify: which capabilities are growing fastest? Slowest?
5. Recommend: optimal build sequence based on dependencies and velocity

**Implementation steps:**
1. Port `collective/capability_predictor.py` to PAI architecture
2. Pull maturity scores from monthly self-evaluations
3. Build simple time-series prediction (linear regression + logistic ceiling)
4. Generate capability forecast: "Memory will reach 9/10 by July, Autonomous Execution by September"
5. Include in monthly self-evaluation report
6. Dashboard widget: capability trajectory chart

**Commit:** `feat(pai): predictive capability modeling — maturity forecasts with growth curves`

---

## Phase 8B: Knowledge Graph Federation

### Task 3: Build Federated Knowledge Graph

**Files:**
- Create: `pai/intelligence/knowledge_federation.py`

**What it does:**
Connects knowledge graphs across all 3 companies into a unified view.

**Federation model:**
- Each company has its own entity/relationship set in Supabase
- Federation layer creates cross-company links:
  - Same person appears in multiple companies → link
  - Same technology used across companies → link
  - Same competitor threatens multiple companies → link
  - Same market trend affects multiple companies → link

**Implementation steps:**
1. Tag all entities with company context
2. Build cross-company entity resolution (same name → same entity?)
3. Create federated query: "Show me everything about [person] across all companies"
4. Build cross-company relationship graph
5. Visualize in dashboard (force-directed graph with company coloring)
6. Auto-detect: new entity in one company matches existing entity in another
7. Alert: "Mike, [person] from Oracle Health just appeared in Alex Recruiting context"

**Commit:** `feat(pai): federated knowledge graph — cross-company entity resolution and linking`

---

## Phase 8C: Daemon API

### Task 4: Build Daemon API (Personal API Endpoint)

**Files:**
- Create: `pai/daemon/server.py`
- Create: `pai/daemon/endpoints.py`
- Create: `pai/config/daemon.json`

**What it does:**
Miessler's Daemon concept — a machine-readable API that represents Mike's PAI. Other AI systems can query it. Think of it as Mike's "API endpoint."

**Daemon endpoints:**
| Endpoint | Method | Response |
|----------|--------|----------|
| `/daemon/status` | GET | Mike's availability, current focus, DND status |
| `/daemon/capabilities` | GET | What Mike's PAI can do (agent list, pattern list) |
| `/daemon/ask` | POST | Ask Jake a question (authenticated) |
| `/daemon/brief` | GET | Latest morning brief (authenticated) |
| `/daemon/goals` | GET | Active goals and progress (authenticated) |
| `/daemon/context` | POST | Provide context to Jake (authenticated) |

**Security:**
- API key authentication (bearer token)
- Rate limiting (10 req/min)
- Tailscale-only access (not exposed to public internet)
- Audit log for all requests

**Implementation steps:**
1. Create FastAPI Daemon server (separate from dashboard API)
2. Run on port 8889 (Tailscale only)
3. Implement API key auth with rate limiting
4. Wire `/daemon/ask` to Claude Code bridge
5. Wire `/daemon/brief` to morning brief output
6. Wire `/daemon/goals` to goal tracking
7. Create audit log for all Daemon requests

**Commit:** `feat(pai): Daemon API — machine-readable personal endpoint for AI-to-AI communication`

---

## Phase 8D: Automated Research Pipelines

### Task 5: Build Gap-Triggered Research Pipelines

**Files:**
- Create: `pai/intelligence/research_trigger.py`
- Adapt from: `susan-team-architect/backend/research_daemon/`

**What it does:**
Automatically detects knowledge gaps and triggers research to fill them.

**Gap detection signals:**
- Jake doesn't know something Mike asks about → log as knowledge gap
- SCOUT finds competitor move we have no context for → research trigger
- Self-evaluation identifies weak domain → targeted research
- New project started → auto-research the domain

**Implementation steps:**
1. Build GapDetector class that monitors:
   - "I don't know" responses from Jake
   - Low-confidence intent classifications
   - Missing entity references
   - SCOUT signals with no existing RAG context
2. When gap detected, queue research job:
   - Dispatch Susan research agents (web, arxiv, reddit, appstore)
   - Run Fabric `extract_wisdom` on findings
   - Ingest into Susan RAG via `rag_engine`
   - Alert Mike: "I noticed a knowledge gap about X. I researched it and ingested Y chunks."
3. Track research effectiveness: did the gap get filled? Did subsequent queries succeed?

**Commit:** `feat(pai): gap-triggered research — auto-detect knowledge gaps and dispatch research agents`

---

## Phase 8E: Verification

### Task 6: Cross-Domain Intelligence Verification

**Tests:**
1. Synergy detector identifies a real pattern transfer between 2 companies
2. Capability predictor generates growth forecast for all 9 domains
3. Federated graph links an entity across 2+ companies
4. Daemon API responds to authenticated `/daemon/status` request
5. Gap-triggered research fills a real knowledge gap end-to-end
6. Dashboard shows cross-company view with synergy highlights

**Commit:** `feat(pai): V8 cross-domain intelligence verification complete`

---

## V8 Exit Criteria (All Must Pass)

- [ ] 5+ cross-domain pattern transfers identified and documented
- [ ] Predictive model generates maturity forecasts with >70% accuracy
- [ ] Federated knowledge graph links entities across companies
- [ ] Daemon API running on Tailscale (port 8889), authenticated
- [ ] Gap-triggered research has filled 3+ knowledge gaps automatically
- [ ] Dashboard shows cross-company synergy view
- [ ] Weekly synergy report delivered alongside weekly synthesis

**Score target: 91 → 93**
