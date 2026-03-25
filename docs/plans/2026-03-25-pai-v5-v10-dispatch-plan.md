# PAI V5-V10 Dispatch Plan

**Date**: 2026-03-25
**Purpose**: Comprehensive execution plan for Dispatch (parallel agent execution)
**Scope**: V5 Learning Engine → V10 Full Autonomy
**Status**: V4 COMPLETE, V5 modules built but unwired, V6-V10 partial

---

## Architecture Summary

```
V4 (COMPLETE) — Intent routing, decision support, priority engine, briefs
  ↓
V5: Learning Engine — Jake improves from every interaction
  ↓
V6: Multi-Channel — Same intelligence, every surface
  ↓
V7: Visual Command Center — See the whole system at a glance
  ↓
V8: Cross-Domain Intelligence — Patterns transfer between companies
  ↓
V9: Marketplace — Share what works, revenue potential
  ↓
V10: Full Autonomy — <15 min/day, 90%+ automated
```

---

## V5: Learning Engine (Score: 78 → 84)

### What Exists
- `pai/learning/rating_system.py` (10.9 KB) — explicit + implicit satisfaction signals
- `pai/learning/correction_handler.py` (9.1 KB) — correction pair extraction
- `pai/learning/failure_capture.py` (9.8 KB) — failure context dumps
- `pai/learning/pattern_generator.py` (12.1 KB) — auto-detect recurring patterns
- `pai/learning/consolidation.py` (10.9 KB) — nightly episodic→semantic
- `pai/learning/weekly_synthesis.py` (7.9 KB) — weekly semantic→wisdom
- `pai/learning/self_evaluation.py` (16.2 KB) — monthly maturity scorecard
- `pai/retrieval/consolidator.py` (172 lines) — V1 predecessor
- `jake_brain/correction_handler.py` (203 lines) — V1 predecessor

### What's Missing
- WRONG.md auto-tracker (systematic error detection)
- Integration hooks (wire into dispatcher + OpenClaw)
- Tests for all 7 modules
- Rating capture hook for OpenClaw skill responses
- 30-day validation run

### Tasks

| ID | Task | Files | Depends | Est. |
|----|------|-------|---------|------|
| 5.1 | Wire learning modules into dispatcher — after each response, capture rating signal | `pai/dispatcher.py`, `pai/learning/rating_system.py` | V4 | 1h |
| 5.2 | Build WRONG.md auto-tracker — detect systematic errors, write to WRONG.md | `pai/learning/wrong_tracker.py`, `pai/MEMORY/WRONG.md` | 5.1 | 1h |
| 5.3 | Create rating capture hook for OpenClaw — capture thumbs up/down on Telegram | `pai/hooks/rating-capture.sh`, OpenClaw skill config | 5.1 | 1h |
| 5.4 | Wire correction handler into message flow — detect "no, I meant..." patterns | `pai/dispatcher.py`, `pai/learning/correction_handler.py` | 5.1 | 1h |
| 5.5 | Create consolidation LaunchAgent — nightly at 2 AM | `~/Library/LaunchAgents/ai.jake.consolidation.plist` | 5.1 | 30m |
| 5.6 | Create weekly synthesis LaunchAgent — Sunday 3 AM | `~/Library/LaunchAgents/ai.jake.weekly-synthesis.plist` | 5.5 | 30m |
| 5.7 | Write tests for all 7 learning modules | `pai/learning/tests/test_*.py` | 5.1-5.4 | 2h |
| 5.8 | Self-evaluation CLI command — `jake-dispatch eval` | `pai/cli/jake_dispatch.py` | 5.7 | 30m |

### Exit Criteria
- [ ] 100+ satisfaction signals captured in 14 days
- [ ] Correction handler operational (detects + stores correction pairs)
- [ ] Failure capture generates dumps for all error types
- [ ] 5+ auto-generated Fabric patterns awaiting approval
- [ ] Nightly consolidation runs 14 days without failure
- [ ] Weekly synthesis produces actionable patterns
- [ ] WRONG.md has 3+ entries from auto-detection
- [ ] All tests pass

---

## V6: Multi-Channel (Score: 84 → 88)

### What Exists
- `pai/channels/base.py` (3.4 KB) — ChannelAdapter ABC, IncomingMessage, OutgoingMessage
- `pai/channels/context_manager.py` (6.3 KB) — cross-channel context (LosslessClaw)
- `pai/channels/discord/adapter.py` — skeleton
- `pai/channels/imessage/adapter.py` — BlueBubbles polling skeleton
- `pai/channels/slack/adapter.py` — Socket Mode skeleton
- `pai/channels/voice/adapter.py` — skeleton
- `pai/intelligence/channel_personality.py` (7.2 KB) — 6 channel profiles

### What's Missing
- Working Telegram adapter (OpenClaw handles this, but no Python adapter)
- Working iMessage adapter (BlueBubbles REST API)
- Working Slack adapter (Socket Mode events)
- Working Discord adapter (discord.py bot)
- Voice interface (ElevenLabs TTS + Whisper STT)
- Channel personality wired into response formatting
- Cross-channel context verification

### Tasks

| ID | Task | Files | Depends | Est. |
|----|------|-------|---------|------|
| 6.1 | Complete iMessage adapter — BlueBubbles REST on Mac Studio | `pai/channels/imessage/adapter.py` | V5 | 2h |
| 6.2 | Complete Slack adapter — Socket Mode, DM-only | `pai/channels/slack/adapter.py` | V5 | 2h |
| 6.3 | Complete Discord adapter — DMs + allowed channels | `pai/channels/discord/adapter.py` | V5 | 2h |
| 6.4 | Build Voice interface — ElevenLabs TTS + Whisper STT | `pai/channels/voice/adapter.py`, `pai/channels/voice/tts.py`, `pai/channels/voice/stt.py` | V5 | 3h |
| 6.5 | Wire channel personality into dispatcher — format responses per channel | `pai/dispatcher.py`, `pai/intelligence/channel_personality.py` | 6.1-6.4 | 1h |
| 6.6 | Wire cross-channel context — LosslessClaw persistence | `pai/channels/context_manager.py`, `pai/dispatcher.py` | 6.5 | 1h |
| 6.7 | Build channel orchestrator — unified receive/route/respond loop | `pai/channels/orchestrator.py` | 6.5, 6.6 | 2h |
| 6.8 | Tests + verification — all channels send/receive correctly | `pai/channels/tests/test_*.py` | 6.7 | 2h |

### Exit Criteria
- [ ] Jake reachable on 4+ channels simultaneously (Telegram, iMessage, Slack, Discord)
- [ ] Voice interface working (speak to Jake, hear response)
- [ ] Channel personality adapts per channel (formal Slack, casual Telegram)
- [ ] Context persists across channels (start on Telegram, continue on Slack)
- [ ] Cross-channel handoffs work ("I told you on Telegram..." works on Slack)

---

## V7: Visual Command Center (Score: 88 → 91)

### What Exists
- `pai/dashboard/` — directory structure only
- `apps/operator-console/` — existing simple console (HTML/JS)
- `apps/v5/` — Next.js app (previous attempt, reference)

### What's Missing
- FastAPI dashboard server (11 endpoints)
- Real-time status aggregator
- Next.js PWA frontend
- Company detail views
- WebSocket real-time updates

### Tasks

| ID | Task | Files | Depends | Est. |
|----|------|-------|---------|------|
| 7.1 | Build Dashboard API — FastAPI with 11 endpoints | `pai/dashboard/api/server.py`, `pai/dashboard/api/routes/` | V6 | 3h |
| 7.2 | Build real-time aggregator — collect status from all subsystems | `pai/dashboard/api/aggregator.py` | 7.1 | 2h |
| 7.3 | Add WebSocket endpoint — push updates to connected clients | `pai/dashboard/api/websocket.py` | 7.2 | 1h |
| 7.4 | Build Next.js frontend — mobile-first PWA with Tailwind | `pai/dashboard/frontend/` | 7.1 | 4h |
| 7.5 | Company detail views — 3 companies with agent/pipeline status | `pai/dashboard/frontend/src/app/companies/` | 7.4 | 2h |
| 7.6 | Pipeline visualizer — DAG view of running pipelines | `pai/dashboard/frontend/src/components/PipelineDAG.tsx` | 7.4 | 2h |
| 7.7 | Action approval UI — approve/reject from dashboard | `pai/dashboard/frontend/src/components/ApprovalQueue.tsx`, `pai/dashboard/api/routes/approvals.py` | 7.4 | 2h |
| 7.8 | PWA config + LaunchAgent — installable, auto-start server | `pai/dashboard/frontend/public/manifest.json`, LaunchAgent plist | 7.4-7.7 | 1h |

### API Endpoints (7.1)
```
GET  /api/status              — overall system health
GET  /api/companies            — all 3 companies summary
GET  /api/companies/:id        — company detail
GET  /api/agents               — 218 agent status
GET  /api/agents/:id           — agent detail + traces
GET  /api/pipelines            — active pipeline runs
GET  /api/pipelines/:id        — pipeline detail + DAG
GET  /api/memory/health        — memory stats (TELOS, RAG, consolidation)
GET  /api/goals                — goal progress
GET  /api/signals              — SCOUT competitive signals
WS   /ws/live                  — real-time status stream
POST /api/approvals/:id/action — approve/reject pending action
```

### Exit Criteria
- [ ] Dashboard API running on port 4174
- [ ] 11+ API endpoints returning live data
- [ ] Mobile-responsive PWA installable on phone
- [ ] Real-time updates via WebSocket (no manual refresh)
- [ ] All 3 company views populated
- [ ] Pipeline status visible
- [ ] Action approval working from dashboard
- [ ] Mike uses daily for 2+ weeks

---

## V8: Cross-Domain Intelligence (Score: 91 → 93)

### What Exists
- `pai/intelligence/synergy_detector.py` (7.0 KB) — cross-portfolio patterns
- `pai/intelligence/predictive_modeling.py` (6.2 KB) — maturity forecasts
- Susan RAG (6,693+ chunks across 22 data types)

### What's Missing
- Federated knowledge graph (entity resolution across companies)
- Daemon API (Miessler-style personal endpoint)
- Gap-triggered research pipelines

### Tasks

| ID | Task | Files | Depends | Est. |
|----|------|-------|---------|------|
| 8.1 | Build federated knowledge graph — entity resolution across 3 companies | `pai/intelligence/knowledge_federation.py`, `pai/intelligence/entity_resolver.py` | V7 | 3h |
| 8.2 | Enhance synergy detector — LLM-driven pattern discovery (not just heuristic) | `pai/intelligence/synergy_detector.py` | 8.1 | 2h |
| 8.3 | Enhance predictive modeling — capability dependency graph, Monte Carlo forecasts | `pai/intelligence/predictive_modeling.py` | 8.1 | 2h |
| 8.4 | Build Daemon API — personal machine-readable endpoint on Tailscale | `pai/daemon/server.py`, `pai/daemon/schema.py` | V7 | 3h |
| 8.5 | Build gap-triggered research — auto-detect knowledge gaps, dispatch research | `pai/intelligence/gap_detector.py`, `pai/intelligence/research_dispatcher.py` | 8.1, 8.2 | 2h |
| 8.6 | Add cross-domain view to dashboard | `pai/dashboard/frontend/src/app/synergies/` | 8.1-8.3 | 2h |

### Exit Criteria
- [ ] 5+ cross-domain pattern transfers identified
- [ ] Predictive model generates forecasts (>70% accuracy at 30 days)
- [ ] Federated knowledge graph links entities across companies
- [ ] Daemon API running on Tailscale (port 8889)
- [ ] 3+ knowledge gaps automatically filled by research pipeline
- [ ] Weekly synergy report delivered automatically

---

## V9: Marketplace (Score: 93 → 95)

### What Exists
- `pai/marketplace/packager.py` (7.1 KB) — basic pattern/skill packaging

### What's Missing
- Pattern curation pipeline
- TELOS onboarding wizard
- Personality framework templates
- Revenue infrastructure (Stripe)
- ClawHub publishing

### Tasks

| ID | Task | Files | Depends | Est. |
|----|------|-------|---------|------|
| 9.1 | Build pattern curation pipeline — evaluate, clean, package battle-tested patterns | `pai/marketplace/pattern_curator.py` | V8 | 2h |
| 9.2 | Package Susan skills as OpenClaw skills — export 15+ skills to ClawHub format | `pai/marketplace/skill_exporter.py` | 9.1 | 2h |
| 9.3 | Build TELOS onboarding wizard — interactive Q&A for new founders | `pai/marketplace/telos_wizard.py`, `pai/marketplace/templates/` | V8 | 3h |
| 9.4 | Build personality framework — custom AI personality creation toolkit | `pai/marketplace/personality_framework.py`, `pai/marketplace/examples/` | V8 | 2h |
| 9.5 | Publish to ClawHub — 3+ patterns, 3+ skills | `pai/marketplace/publisher.py` | 9.1, 9.2 | 2h |
| 9.6 | Revenue infrastructure — Stripe integration, pricing tiers, landing page | `pai/marketplace/billing/`, `pai/marketplace/landing/` | 9.5 | 3h |

### Exit Criteria
- [ ] 3+ patterns published to ClawHub
- [ ] 3+ skills published to ClawHub
- [ ] TELOS wizard works end-to-end for a new user
- [ ] Personality framework published with 4+ examples
- [ ] 1+ external user running a published skill
- [ ] Landing page deployed
- [ ] Revenue infrastructure set up (Stripe connected)

---

## V10: Full Autonomy (Score: 95 → 98)

### What Exists
- `pai/evolution/agent_evolution.py` (10.9 KB) — propose/retire/optimize agents
- `pai/evolution/capability_upgrade.py` (10.2 KB) — self-upgrade proposals

### What's Missing
- Advanced self-healing (root cause diagnosis, preventive maintenance)
- System evolution engine (track external updates)
- Operational handoff system
- Human 3.0 dashboard

### Tasks

| ID | Task | Files | Depends | Est. |
|----|------|-------|---------|------|
| 10.1 | Enhance agent evolution — wire into live agent performance data | `pai/evolution/agent_evolution.py` | V9 | 2h |
| 10.2 | Enhance capability upgrade — wire into self-evaluation scores | `pai/evolution/capability_upgrade.py` | V9 | 2h |
| 10.3 | Build advanced self-healing — root cause diagnosis, preventive actions | `pai/evolution/self_healing.py` | 10.1 | 3h |
| 10.4 | Build system evolution engine — track package updates, model releases, tool changes | `pai/evolution/system_evolution.py` | 10.1 | 2h |
| 10.5 | Build operational handoff — audit manual ops, automate each one | `pai/evolution/ops_handoff.py` | 10.1-10.4 | 3h |
| 10.6 | Build Human 3.0 dashboard — time saved, automation rate, learning velocity | `pai/dashboard/frontend/src/app/human30/`, `pai/dashboard/api/routes/human30.py` | 10.5 | 2h |
| 10.7 | Full system verification — 30-day autonomous run | All systems | 10.6 | Ongoing |

### Exit Criteria
- [ ] Jake proposes 3+ capability upgrades autonomously
- [ ] Susan agent roster evolved (agents added/retired based on data)
- [ ] System improves month-over-month without manual intervention
- [ ] Self-healing diagnosing root causes and taking preventive action
- [ ] 90%+ routine operations automated
- [ ] <15 min/day manual interaction for 30 consecutive days
- [ ] Overall PAI maturity score: 95+/100
- [ ] Human 3.0 dashboard showing all metrics

---

## Dispatch Execution Strategy

### Parallelization Opportunities

These version phases can run in parallel where dependencies allow:

```
Session 1: V5 integration (5.1-5.4) + V5 tests (5.7)
Session 2: V5 LaunchAgents (5.5-5.6, 5.8) + V6 channels (6.1-6.4)
Session 3: V6 wiring (6.5-6.8) + V7 API (7.1-7.3)
Session 4: V7 frontend (7.4-7.8) + V8 knowledge (8.1-8.3)
Session 5: V8 Daemon (8.4-8.6) + V9 packaging (9.1-9.2)
Session 6: V9 wizard + revenue (9.3-9.6) + V10 evolution (10.1-10.2)
Session 7: V10 healing + handoff (10.3-10.6) + V10 verification (10.7)
```

### Estimated Total
- **46 tasks** across 6 versions
- **~7 sessions** at 60% context budget each
- **~80 hours** of agent work
- **Target completion**: 2-3 weeks with daily sessions

### Risk Mitigations
| Risk | Mitigation |
|------|-----------|
| V5 learning data takes time to accumulate | Start V6 in parallel, validation runs in background |
| Channel adapters depend on external services | Mock adapters for testing, real services for integration |
| Dashboard frontend is large | Use apps/v5/ as reference, shadcn/ui for components |
| V9 marketplace needs external users | Start with internal dogfooding, publish when proven |
| V10 30-day validation window | Start early, measure continuously |

---

## File Count Summary

| Version | New Files | Modified Files | Total |
|---------|-----------|---------------|-------|
| V5 | 5 | 3 | 8 |
| V6 | 8 | 2 | 10 |
| V7 | 15+ | 2 | 17+ |
| V8 | 6 | 3 | 9 |
| V9 | 8 | 1 | 9 |
| V10 | 6 | 4 | 10 |
| **Total** | **48+** | **15** | **63+** |
