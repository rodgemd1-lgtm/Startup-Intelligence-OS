# Phase 4+: Hermes 10X — Test, Fix, Transform

**Date**: 2026-03-21
**Status**: APPROVED (pending Mike's confirmation)
**Baseline Score**: 31/100
**Target Score**: 85/100 (10 sessions)
**Full Assessment**: `.startup-os/artifacts/hermes-10x-capability-assessment-2026-03-21.md`

## Context

Susan's team ran a 15-domain capability assessment of Hermes. The diagnosis:
> "Mike has a Formula 1 engine bolted to a go-kart chassis."

Brain is extraordinary (37K memories, 4-layer architecture, knowledge graph). But the experience layer is nearly absent. The 3 biggest gaps:
1. **Intent & Routing** (0.5 → 4.0) — every request gets same treatment
2. **Smart Notifications** (0.3 → 4.0) — dumb cron briefs, no urgency scoring
3. **Proactive Intelligence** (1.0 → 4.5) — Jake reacts but never anticipates

## Pre-Phase: ClaudeBirchBot Testing (THIS SESSION or NEXT)

Before building Phase 4, validate ClaudeBirchBot with Forge's test matrix (64 tests across 6 categories). Run P0 tests first:

### P0 Test Sequence (execute from Telegram)
1. **Security first**: Have someone else message the bot (should get no response)
2. **Basic**: `/status` → should show uptime, projects
3. **Basic**: `/projects` → should show routing table
4. **Basic**: `What is the name of the current git repository?` → should say Startup-Intelligence-OS
5. **Routing**: `oracle: what files are in this project root?` → should reference Oracle Health
6. **Routing**: `alex: what is the project name?` → should reference Alex Recruiting
7. **Edge**: `oracle:` (nothing after colon) → should not crash
8. **Real-world**: `What's the git status?` → should return actual status
9. **Real-world**: `Check if the daily brain ingestion ran` → should search for evidence
10. **Reliability**: Kill bot (`pkill -f claude_remote_bot.py`), send `/status` → should auto-restart via launchd

### Known Risks to Watch
- Messages sent while Mac sleeps are **silently dropped** (drop_pending_updates=True)
- No log rotation configured — log will grow unbounded
- Sequential message handling — long tasks block /status
- $2 budget cap may cut off complex answers mid-response

## Phase 4A: THE SPINE (Session 1)
**Goal**: Intent classification + priority engine + brain search weighting
**Impact**: 31 → 42/100

| Step | Build | Owner | Test |
|------|-------|-------|------|
| 4A.1 | Intent classifier (question/action/research/planning/personal/meta) | KIRA + Atlas | 90% accuracy on 50 test prompts |
| 4A.2 | Brain context assembler — select memory layers by intent | Knowledge Engineer | "Tell me about Jacob" returns profile, not calendar |
| 4A.3 | Priority engine — rank signals by urgency x importance | Steve + Nova | "What should I work on?" returns prioritized list |
| 4A.4 | Source-type weighting (profile 3x, semantic 2x, calendar 0.5x) | Atlas | Validated on 20 test queries |

## Phase 4B: SMART NOTIFICATIONS (Session 2)
**Goal**: Urgency scoring + DND + meeting prep auto-delivery
**Impact**: 42 → 48/100

| Step | Build | Owner | Test |
|------|-------|-------|------|
| 4B.1 | Notification manager with urgency scoring | Pulse + Nova | CEO email >0.8, newsletter <0.2 |
| 4B.2 | DND awareness — check calendar before push | Nova | Zero notifications during meetings |
| 4B.3 | Intelligent batching | Pulse | <5 push notifications per day |
| 4B.4 | Meeting prep auto-delivery (15 min before) | ARIA + Knowledge Engineer | Prep brief for 100% of meetings |

## Phase 5A: BOT UNIFICATION (Session 3)
**Goal**: One Jake bot, internal routing, conversation quality
**Impact**: 48 → 58/100

| Step | Build | Owner | Test |
|------|-------|-------|------|
| 5A.1 | Single Telegram bot with Hermes/Claude routing | Atlas + Forge | Mike uses 1 bot for everything |
| 5A.2 | Conversation state persistence | Knowledge Engineer | "What did I ask 10 min ago?" works |
| 5A.3 | Selective brain injection by intent | Atlas + KIRA | No irrelevant brain results |
| 5A.4 | Error recovery in character | Conversation Designer | Tool failures get Jake-voiced retries |
| 5A.5 | Retire Genspark bot → cron job | Nova | Channel still updates, one less bot |

## Phase 5B: ACTION EXECUTION (Session 4)
**Goal**: Jake goes from read-only to read-write
**Impact**: 58 → 62/100

| Step | Build | Owner | Test |
|------|-------|-------|------|
| 5B.1 | Action registry: preview/execute/undo pattern | Forge + Atlas | 7 action types registered |
| 5B.2 | Core actions: send_email, create_event, set_reminder | Forge | Each works standalone |
| 5B.3 | Telegram confirmation flow (inline approve/reject) | Nova + Forge | Tier 2 shows preview |
| 5B.4 | Audit trail to jake_episodic | Knowledge Engineer | "What actions today?" returns list |
| 5B.5 | Extended actions: GitHub issue, Notion, outreach | Forge | All 7 operational |

## Phase 5C: BRAIN QUALITY (Session 5)
**Goal**: Fix "calendar drowns profile" problem
**Impact**: 62 → 68/100

| Step | Build | Owner | Test |
|------|-------|-------|------|
| 5C.1 | Memory utility scoring | Knowledge Engineer + AI Eval | High vs low value differentiated |
| 5C.2 | Nightly auto-consolidation | Knowledge Engineer | Runs nightly, stats in brief |
| 5C.3 | Entity resolution (merge duplicates) | Knowledge Engineer + Algorithm Lab | "Jacob" = "my son" = 1 entity |
| 5C.4 | Graph-enhanced retrieval (1-hop) | Atlas | Person queries return relationships |
| 5C.5 | Smart calendar dedup | Nova | 260 standups → 1 semantic memory |

## Phases 6-9 (Sessions 6-10)
| Phase | Focus | Impact |
|-------|-------|--------|
| 6A | Proactive intelligence (brain-assembled briefs, pattern mining) | 68 → 74 |
| 6B | Learning engine (correction capture, preference tracking) | 74 → 78 |
| 7A | Reliability (health checks, auto-recovery, monitoring) | 78 → 82 |
| 7B | Security (sensitivity tags, context boundaries) | 82 → 85 |
| 8+ | Voice, delegation chains, family access | 85 → 92 |

## Team Manifest (15 Susan Agents)
| Agent | Primary Role | Phases |
|-------|-------------|--------|
| Atlas | Architecture, brain search, bot unification | 4A, 5A, 5C |
| KIRA | Intent classification, routing | 4A, 5A |
| ARIA | Briefs, meeting prep, proactive alerts | 4B, 6A |
| Steve | Priority engine, cross-company ranking | 4A, 6A |
| Nova | Data engineering, notifications, integrations | 4A, 4B, 5A, 5B |
| Forge | Action registry, Telegram flows, engineering | 5A, 5B |
| Knowledge Engineer | Brain quality, consolidation, entity res | 4A, 5A-C, 6A-B |
| Pulse | Monitoring, health, telemetry | 4B, 6B, 7A |
| Sentinel | Reliability, auto-recovery | 7A, 7B |
| Shield | Security, PII classification | 7B |
| AI Eval | Correction capture, quality scoring | 5C, 6A, 6B |
| Algorithm Lab | Pattern mining, clustering | 5C, 6A |
| Conversation Designer | Error recovery UX, personality | 5A |
| Research Director | Competitive intel, deep research | 8B |
| Susan | Orchestration, workflow chains | 8B |

## Critical Path
```
Phase 4A (Spine) → Phase 4B (Notifications) → Phase 5A (Unification)
```
These 3 sessions transform Hermes from "cool tech" to "useful daily assistant."
Everything after amplifies these.

## Success Metric
**10X from current = meaningful daily utility. Achievable after Phase 5B (4 sessions).**
**Mani parity (86/100) = after Phase 7 (8 sessions).**
