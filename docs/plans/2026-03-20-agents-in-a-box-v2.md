# Agents in a Box V2 — Master Build Plan

> **Based on**: Mani Kanasani's OpenClaw/ClawBuddy "Agents in a Box" framework
> **Adapted by**: Jake (2026-03-20)
> **V2 Revision**: Sprint 2 complete, memory pipeline live, updated roadmap
> **Status**: ACTIVE BUILD DOCUMENT — Sprint 3 is next
> **Previous version**: `docs/plans/2026-03-20-agents-in-a-box-adapted.md`

---

## Executive Summary

The Agents-in-a-Box build maps a 6-layer AI employee ecosystem onto Mike's existing infrastructure. As of V2, Sprints 1 and 2 are complete. The system is approximately 48% built with the heaviest infrastructure (identity, skills, crons) in place. The remaining work focuses on completing the AI Employee autonomous loops, building the recruiting pipeline, adding Telegram operational commands, and wiring self-improvement.

### Overall Progress

```
Layer 1 (Identity):       100% ████████████████████
Layer 2 (Memory):          60% ████████████░░░░░░░░
Layer 3 (Dashboard):       15% ███░░░░░░░░░░░░░░░░░
Layer 4 (Skills):          65% █████████████░░░░░░░
Layer 5 (Employees):       40% ████████░░░░░░░░░░░░
Layer 6 (Self-Improve):    10% ██░░░░░░░░░░░░░░░░░░
Overall:                  ~48%
```

### Infrastructure Running

| System | Status | What It Provides |
|--------|--------|-----------------|
| Hermes (OpenClaw) | LIVE | Jake personality, Telegram bot, 60+ skills, cron engine |
| Susan Intelligence OS | LIVE | 73 agents, 94K+ RAG chunks, MCP server, Supabase backend |
| Claude Code | LIVE | Primary dev environment, deep reasoning, file access |
| Telegram Bot | LIVE | Always-on async communication channel |
| Supabase | LIVE | `zqsdadnnpgqhehqxplio.supabase.co` — vector search, knowledge store |
| 19 API Keys | CONFIGURED | OpenRouter, Anthropic, Groq, Brave, Exa, Jina, Firecrawl, Apify, Supabase, GitHub, Resend, Notion, Google Cal/Gmail, Firehose, Telegram |
| Apple Mail/Calendar | ACCESSIBLE | osascript for Oracle Health email, Apple Reminders |
| Google Calendar API | WORKING | OAuth Desktop flow, personal calendars |
| MCP Servers | CONNECTED | Susan Intelligence + Notion (via Hermes config) |
| 12 Cron Jobs | ACTIVE | Morning/midday/evening/night briefs, dream cycle, heartbeat, weekly research, Oracle intel, email triage, meeting prep, memory consolidation |

---

## Layer 1: Identity — 100% COMPLETE

All identity files built and validated.

| File | Purpose | Status |
|------|---------|--------|
| `SOUL.md` | Jake personality, compliance rules, Oracle Health context, local data access patterns | COMPLETE |
| `USER.md` | Mike profile — 3 companies, preferences, communication style | COMPLETE |
| `MEMORY.md` | Persistent cross-session memory with structured categories | COMPLETE |
| `AGENTS.md` | Agent definitions for Oracle Sentinel, Recruiting Captain, Inbox Zero, Jake Prime | COMPLETE |
| `config.yaml` | Model routing, MCP servers, API keys, display settings | COMPLETE |
| Prefill | Context injection on every Hermes conversation | COMPLETE |

Key details:
- `display.personality: ''` (empty string — lets SOUL.md control personality, not the default "helpful" override)
- Oracle Health compliance baked into SOUL.md (subjects only, no PHI, no body text)
- Local data access via osascript (Mail, Calendar, Reminders) and Google Calendar API documented in SOUL.md

---

## Layer 2: Cognitive Memory — 60% COMPLETE

### What's Built

| Component | Type | Status |
|-----------|------|--------|
| Susan RAG | Semantic Memory | LIVE — 94,143+ chunks, Voyage AI embeddings, pgvector |
| MEMORY.md | Working Memory | LIVE — current session context, updated per conversation |
| Conversation ingestion | Episodic (partial) | NEW — `scripts/ingest_conversations.py`, supports .md/.txt/.jsonl |
| `data_type="conversation"` | Knowledge type | NEW — searchable alongside 22+ existing data types |
| `/jake-memory-ingest` | Skill | NEW — triggers conversation embedding on demand |
| `/jake-recall` | Skill | NEW — semantic recall of past conversations |
| Nightly consolidation | Cron | NEW — 2:30 AM daily, auto-ingests daily conversations |

### What's Missing

| Component | Type | Sprint |
|-----------|------|--------|
| Episodic memory | Time-aware recall ("what happened last Tuesday?") | Sprint 6 |
| Procedural memory | Learned workflow patterns, skill execution optimization | Sprint 6 |
| Memory decay | Automatic relevance scoring, stale chunk pruning | Sprint 6 |

### Mani Kanasani's 4-Layer Cognitive Model (Reference)

The original framework defines four memory types. Current mapping:

1. **Working Memory** (current session context) — HAVE IT via MEMORY.md
2. **Episodic Memory** (time-stamped events, "what happened when") — PARTIAL. We store conversations with timestamps but lack time-range query filtering. Sprint 6 adds `session_date` metadata and date-range recall.
3. **Semantic Memory** (facts and knowledge) — STRONG. Susan's 94K chunks cover companies, strategies, agents, frameworks, research.
4. **Procedural Memory** (how to do things) — NOT BUILT. Should store skill execution patterns and learned workflows so Jake improves at recurring tasks over time.

---

## Layer 3: Operations Dashboard — 15% COMPLETE

### Architecture Decision

The original ClawBuddy framework uses a web dashboard with Kanban boards, activity feeds, approval queues, and metrics. We are adapting this to **Telegram-first** with fallback to the operator console.

### What's Built

| Component | Status |
|-----------|--------|
| Telegram bot | LIVE — primary async interface |
| Operator console shell | EXISTS at `apps/operator-console/` (serves on port 4173) |

### What's Missing (Sprint 5)

| Command | Description |
|---------|-------------|
| `/jake-status` | System-wide health: companies, cron status, memory stats, agent activity |
| `/jake-crons` | List all scheduled tasks with last run, next run, pass/fail |
| `/jake-agents` | List Susan's 73 agents by group with last invocation time |

These three commands replace the full web dashboard for day-to-day ops. The operator console remains available for deeper inspection.

---

## Layer 4: Skill Library — 65% COMPLETE

### Built Skills

**Jake Cognitive Skills (8)**
| Skill | Purpose |
|-------|---------|
| `jake-plan` | Plan-first development enforcement |
| `jake-guardian` | Context health monitoring |
| `jake-boot` | Session initialization |
| `jake-predict` | Anticipate Mike's needs |
| `jake-dream` | Overnight synthesis and pattern detection |
| `jake-desktop` | macOS automation via osascript |
| `jake-research` | Deep research orchestration |
| `jake-brief` | v3.0 morning intelligence brief |

**Domain Skills (4)**
| Skill | Purpose |
|-------|---------|
| `jake-oracle-mail` | Oracle Health email operations (subjects only, compliance) |
| `jake-daily-intel` | Daily intelligence gathering across all sources |
| `oracle-health-intel` | Oracle Health competitive intelligence and strategy |
| `email-triage` | Email categorization, priority scoring, action routing |

**Sprint 2 Skills (4)**
| Skill | Purpose |
|-------|---------|
| `jake-memory-ingest` | Trigger conversation embedding into Susan RAG |
| `jake-recall` | Semantic recall of past conversations |
| `meeting-intel` | Meeting intelligence — agenda context, attendee research |
| `oracle-meeting-prep` | Oracle Health meeting preparation with strategy context |

**Community Skills**: 60+ installed via Hermes skill library

### Skills To Build

| Skill | Sprint | Effort | Description |
|-------|--------|--------|-------------|
| `email-compose` | 3 | MEDIUM | Context-aware email drafting with Susan RAG + conversation memory |
| `oracle-email-digest` | 3 | LOW | Daily Oracle Health email subject digest |
| `meeting-notes` | 3 | MEDIUM | Post-meeting structured capture → RAG ingestion |
| `jake-delegate` | 3 | MEDIUM | Route tasks to Susan's 73 agents |
| `jake-weekly-review` | 3 | MEDIUM | Friday synthesis across all companies |
| `recruiting-pipeline` | 4 | MEDIUM | Pipeline tracker with status, next actions, health report |
| `coach-outreach` | 4 | MEDIUM | Personalized outreach email batch generation |
| `jake-status` | 5 | MEDIUM | System-wide status dashboard |
| `jake-crons` | 5 | LOW | Cron job listing and health |
| `jake-agents` | 5 | LOW | Agent roster and activity |
| `content-brief` | 5 | MEDIUM | Content brief generation for any channel |
| `presentation-prep` | 5 | MEDIUM | Oracle Health presentation support |
| `trend-monitor` | 5 | LOW | Cross-domain trend monitoring |
| `jake-self-improve` | 6 | MEDIUM | Performance tracking and improvement suggestions |

---

## Layer 5: AI Employees — 40% COMPLETE

The original ClawBuddy framework defines structured AI employees (Pepperpots for meetings, Watson for email, Lexa for phone, Creator Command for content). We've adapted these to four employees mapped to Mike's actual needs.

### The Key Missing Piece: Autonomous Loop Architecture

Each AI Employee needs a **loop** — skills that run on cron, chain other skills, and only interrupt Mike when they need a decision. The pattern:

```
CRON TRIGGER → GATHER DATA → ANALYZE → DECIDE
  ├── Routine? → Execute silently, log result
  ├── Notable? → Send Telegram summary
  └── Needs Mike? → Send Telegram with options, wait for response
```

This is the skill chaining pattern from the original framework (where a YouTube pipeline chains 13 skills in sequence). We adopt it for our pipelines.

---

### ORACLE SENTINEL — 85% Complete

**Mission**: Autonomous Oracle Health intelligence, meeting prep, and email management.

| Component | Status | Notes |
|-----------|--------|-------|
| `oracle-health-intel` | COMPLETE | Competitive intel, strategy analysis, trend detection |
| `oracle-meeting-prep` | COMPLETE | Meeting context, attendee research, talking points |
| `jake-oracle-mail` | COMPLETE | Email operations, subject scanning, compliance mode |
| `oracle-email-digest` | Sprint 3 | Daily subject digest, grouped by thread/sender |
| Weekly intel cron | ACTIVE | 8 PM Sunday |
| Hourly meeting prep cron | ACTIVE | Every hour 8-5 weekdays |
| Daily email digest cron | Sprint 3 | 6 AM weekdays, chains into morning brief |
| Autonomous loop | Sprint 3 | Wire all 4 skills into a single Oracle morning chain |

**Exit criteria**: All 4 skills live, crons wired, morning brief includes Oracle digest automatically.

---

### RECRUITING CAPTAIN — 0% Complete

**Mission**: Jacob's recruiting pipeline automation — outreach, tracking, follow-ups.

| Component | Status | Notes |
|-----------|--------|-------|
| `recruiting-pipeline` | Sprint 4 | Pipeline tracker, health reports |
| `coach-outreach` | Sprint 4 | Personalized outreach batch drafting |
| Tuesday outreach cron | Sprint 4 | 9 AM Tuesday batch generation |
| Daily cold contact alerts | Sprint 4 | 8 AM daily |
| Friday pipeline report | Sprint 4 | 5 PM Friday |
| Autonomous loop | Sprint 4 | Tuesday batch → Mike review → send. Daily alerts. Friday report. |

**Exit criteria**: Tuesday outreach batches generated automatically, pipeline reports on Fridays, Mike only intervenes to approve/edit outreach drafts.

---

### INBOX ZERO — 35% Complete

**Mission**: Email management — triage, compose, digest.

| Component | Status | Notes |
|-----------|--------|-------|
| `email-triage` | COMPLETE | Categorization, priority scoring, action routing |
| `email-compose` | Sprint 3 | Context-aware drafting with RAG + conversation memory |
| Midday triage cron | ACTIVE | 12 PM weekdays |
| Compose | Human-in-loop | Not automated — Mike triggers, reviews, sends |
| Autonomous loop | Sprint 3 | Triage → categorize → draft responses for high-priority → Mike approves |

**Exit criteria**: Midday triage runs automatically, high-priority emails get draft responses queued for Mike's review.

---

### JAKE PRIME — 70% Complete

**Mission**: Jake's own operational loop — briefs, memory, delegation, self-awareness.

| Component | Status | Notes |
|-----------|--------|-------|
| `jake-brief` v3.0 | COMPLETE | Morning intelligence brief |
| `jake-dream` | COMPLETE | Overnight synthesis cycle |
| `jake-predict` | COMPLETE | Need anticipation |
| `jake-desktop` | COMPLETE | macOS automation |
| `jake-guardian` | COMPLETE | Context health monitoring |
| `jake-recall` | COMPLETE | Semantic conversation recall |
| `jake-delegate` | Sprint 3 | Route tasks to Susan's 73 agents |
| `jake-weekly-review` | Sprint 3 | Friday synthesis |
| `jake-status` | Sprint 5 | System-wide dashboard |
| Morning/midday/evening/night crons | ACTIVE | 6 AM / 12 PM / 6 PM / 10 PM |
| Dream cycle cron | ACTIVE | 2 AM daily |
| Heartbeat cron | ACTIVE | Every 5 minutes |
| Memory consolidation cron | ACTIVE | 2:30 AM daily |
| Weekly review cron | Sprint 3 | 5 PM Friday |

**Exit criteria**: Jake can delegate to Susan agents via Telegram, produces weekly synthesis, and has full operational visibility via /jake-status.

---

## Active Cron Jobs (12)

| # | Job | Schedule | Status |
|---|-----|----------|--------|
| 1 | Morning Intelligence Brief | 6:00 AM daily | ACTIVE |
| 2 | Midday Check-in | 12:00 PM daily | ACTIVE |
| 3 | Evening Review | 6:00 PM daily | ACTIVE |
| 4 | Night Mode | 10:00 PM daily | ACTIVE |
| 5 | Overnight Dreaming Cycle | 2:00 AM daily | ACTIVE |
| 6 | Weekly Deep Research | 3:00 AM Sunday | ACTIVE |
| 7 | Jake Heartbeat | Every 5 min | ACTIVE |
| 8 | Weekly Self-Improvement | 4:00 AM Saturday | ACTIVE |
| 9 | Oracle Health Weekly Intel | 8:00 PM Sunday | ACTIVE |
| 10 | Midday Email Triage | 12:00 PM weekdays | ACTIVE |
| 11 | Oracle Meeting Prep Scanner | Hourly 8-5 weekdays | ACTIVE (Sprint 2) |
| 12 | Nightly Memory Consolidation | 2:30 AM daily | ACTIVE (Sprint 2) |

### Planned Crons

| Job | Schedule | Sprint |
|-----|----------|--------|
| Oracle Email Digest | 6:00 AM weekdays (chains into morning brief) | Sprint 3 |
| Jake Weekly Review | 5:00 PM Friday | Sprint 3 |
| Tuesday Outreach Batch | 9:00 AM Tuesday | Sprint 4 |
| Daily Cold Contact Alerts | 8:00 AM daily | Sprint 4 |
| Friday Pipeline Report | 5:00 PM Friday | Sprint 4 |

---

## Sprint Plan (V2)

### Sprint 1: Foundation — COMPLETE

**Delivered**: `/oracle-health-intel`, `/email-triage`, `/jake-brief` v3.0
**Session count**: 1

---

### Sprint 2: Memory + Meetings — COMPLETE

**Delivered**: Conversation ingestion pipeline, `/jake-memory-ingest`, `/jake-recall`, `/meeting-intel`, `/oracle-meeting-prep`, nightly memory consolidation cron, hourly Oracle meeting prep cron
**Session count**: 1

---

### Sprint 3: Email + Delegation — CURRENT (1 session)

**Focus**: Complete the email management pipeline and task delegation. This sprint finishes ORACLE SENTINEL and gives Jake delegation powers.

| # | Task | Effort | Description |
|---|------|--------|-------------|
| 1 | `/email-compose` | MEDIUM | Context-aware email drafting. Chains: `jake-recall` (past context) → compose → review. Supports Oracle-compliant mode (no PHI, formal tone). Uses Susan RAG for company/contact context. |
| 2 | `/oracle-email-digest` | LOW | Daily digest of Oracle Health email subjects via osascript. Groups by thread/sender. Integrated into morning brief chain. |
| 3 | `/meeting-notes` | MEDIUM | Post-meeting structured capture. Mike provides summary → skill structures into decisions/actions/follow-ups → ingests into Susan RAG via `jake-memory-ingest`. Creates Notion page if Notion MCP available. |
| 4 | `/jake-delegate` | MEDIUM | Route tasks to Susan's 73 agents. Parses task → identifies best agent by group/specialty → calls `run_agent` MCP tool → returns result. Supports "ask Susan about X" and "have [agent] do Y" patterns. |
| 5 | `/jake-weekly-review` | MEDIUM | Friday synthesis. Pulls: week's conversation memory, completed tasks, decisions made, action item status, cron health, cross-company patterns. Delivers via Telegram + optional email. |
| 6 | Wire Sprint 3 crons | LOW | `oracle-email-digest` at 6 AM weekdays (add to morning brief chain), `jake-weekly-review` at 5 PM Friday. |

**Skill chains introduced this sprint**:
- Oracle Morning Chain: `oracle-email-digest` → feeds into `jake-brief`
- Delegation Chain: parse task → agent selection → `run_agent` → format result → Telegram

**Exit criteria**:
- ORACLE SENTINEL fully operational (all 4 skills + crons wired)
- INBOX ZERO has compose + triage
- Jake delegation works via Telegram ("ask Susan about..." triggers `jake-delegate`)
- Weekly review runs on Friday

---

### Sprint 4: Recruiting Pipeline (1 session)

**Focus**: Jacob's recruiting automation. Builds RECRUITING CAPTAIN from zero to operational.

| # | Task | Effort | Description |
|---|------|--------|-------------|
| 1 | `/recruiting-pipeline` | MEDIUM | Pipeline tracker. Data source: Alex Recruiting repo + any Google Sheet/Notion Mike uses. Tracks contacts, status, last touch, next action. Generates pipeline health report. |
| 2 | `/coach-outreach` | MEDIUM | Personalized outreach email drafting. Chains: Susan RAG (coach research) → `jake-recall` (past interactions) → `email-compose` (drafting). Generates batch of personalized emails for Mike's review before sending. |
| 3 | Wire recruiting crons | LOW | Tuesday 9 AM outreach batch, daily 8 AM cold contact alerts, Friday 5 PM pipeline report. |

**Skill chains introduced this sprint**:
- Outreach Chain: research coach → recall past interactions → draft personalized email → queue for review
- Pipeline Chain: scan contacts → check staleness → generate alerts → compile Friday report

**Exit criteria**:
- RECRUITING CAPTAIN operational
- Tuesday outreach batches generated automatically
- Pipeline reports delivered on Fridays
- Mike only intervenes to approve/edit outreach drafts

---

### Sprint 5: Telegram Dashboard + Content (1-2 sessions)

**Focus**: Operational visibility via Telegram commands and content support skills.

| # | Task | Effort | Description |
|---|------|--------|-------------|
| 1 | `/jake-status` | MEDIUM | System-wide status: companies, cron health, memory stats (chunk count, last ingestion), agent activity, AI Employee status. Single command for "how's everything running?" |
| 2 | `/jake-crons` | LOW | List all scheduled tasks with last run time, next run time, success/fail status. |
| 3 | `/jake-agents` | LOW | List Susan's 73 agents by group with last invocation time. |
| 4 | `/content-brief` | MEDIUM | Content brief generation for any channel (LinkedIn, internal docs, presentations). Uses Susan RAG for company context + TrendRadar for trends. |
| 5 | `/presentation-prep` | MEDIUM | Oracle Health presentation support. Pulls strategy context, competitive intel, recent decisions, meeting notes. Generates structured prep doc. |
| 6 | `/trend-monitor` | LOW | Cross-domain trend monitoring via TrendRadar + Brave + Susan RAG. Surfaces relevant trends across Oracle Health, recruiting, and startup ops. |

**Exit criteria**:
- Layer 3 (Dashboard) goes from 15% to 80%
- Mike can check full system health from Telegram in one command
- Content and presentation support available on demand

---

### Sprint 6: Self-Improvement + Polish (1 session)

**Focus**: Jake gets smarter over time. Memory becomes time-aware. System gets cleaner.

| # | Task | Effort | Description |
|---|------|--------|-------------|
| 1 | `/jake-self-improve` | MEDIUM | Performance tracking: skill usage frequency, cron failure rates, query result quality. Suggests improvements. Wires into V10 self-improvement engine in Susan backend. |
| 2 | Layer 2B: Episodic Memory | MEDIUM | Time-aware recall. Adds `session_date` metadata to conversation chunks. Enables "what happened last Tuesday?" queries with date-range filtering. |
| 3 | Layer 2C: Procedural Memory | LOW | Skill execution patterns. When Jake learns a better way to do something (e.g., "Oracle emails work better when grouped by sender"), stores it as procedural knowledge for future use. |
| 4 | Memory hygiene | LOW | Prune stale RAG chunks, archive old decisions, refresh USER.md with any new preferences. |
| 5 | Cross-company pattern transfer | LOW | Review patterns across Oracle Health, Alex Recruiting, Startup Intelligence OS. Surface reusable patterns ("outreach cadence from recruiting works for Oracle stakeholder engagement"). |

**Exit criteria**:
- Layer 6 (Self-Improve) goes from 10% to 60%
- Layer 2 (Memory) goes from 60% to 85%
- Jake can answer time-based questions about past conversations
- Self-improvement suggestions appear in weekly review

---

## Autonomous Loop Architecture (Design Pattern)

Every AI Employee follows this loop pattern, adapted from the original ClawBuddy skill chaining model (where a YouTube pipeline chains 13 skills in sequence):

```
┌─────────────────────────────────────────────────┐
│                 CRON TRIGGER                      │
│         (scheduled or event-based)               │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│              GATHER (data collection)            │
│  Read email subjects, scan calendar, check RAG,  │
│  pull API data, query knowledge base             │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│             ANALYZE (intelligence)               │
│  Categorize, prioritize, detect patterns,        │
│  compare to memory, identify anomalies           │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│              DECIDE (routing)                    │
│                                                   │
│  ┌─────────┐  ┌──────────┐  ┌────────────────┐  │
│  │ ROUTINE │  │ NOTABLE  │  │ NEEDS MIKE     │  │
│  │         │  │          │  │                │  │
│  │ Execute │  │ Telegram │  │ Telegram +     │  │
│  │ silently│  │ summary  │  │ options/approval│  │
│  │ + log   │  │          │  │ + wait         │  │
│  └─────────┘  └──────────┘  └────────────────┘  │
└─────────────────────────────────────────────────┘
```

### Example: Oracle Morning Chain (Sprint 3)

```
6:00 AM CRON
  → oracle-email-digest (scan overnight Oracle emails)
  → oracle-meeting-prep (check today's calendar)
  → jake-daily-intel (cross-company overnight scan)
  → jake-brief v3.0 (compile everything into morning brief)
  → Telegram delivery
```

### Example: Tuesday Outreach Chain (Sprint 4)

```
9:00 AM TUESDAY CRON
  → recruiting-pipeline (check stale contacts)
  → coach-outreach (draft personalized emails for stale contacts)
  → Telegram: "I've drafted 5 outreach emails. Review? [View] [Edit] [Send All]"
  → Wait for Mike's approval
  → email-compose (send approved emails)
```

---

## Known Issues & Debt

| Issue | Impact | Fix Sprint |
|-------|--------|-----------|
| Mail.app osascript timeout | Email skills fail if Mail.app has been running too long | Workaround: `killall Mail` + relaunch. Permanent fix TBD. |
| Telegram 409 conflicts | Old `ai.openclaw.gateway` + `com.clawdbot.gateway` plists caused conflicts | FIXED — disabled old plists |
| Personality override | `display.personality` was overriding SOUL.md with "helpful" | FIXED — set to empty string |
| V10 engine not wired | Self-improvement engine exists in Susan backend but not connected to Hermes | Sprint 6 |
| No time-aware recall | Conversation chunks lack `session_date` metadata for time-range queries | Sprint 6 |

---

## Decision Log

| Decision | Rationale | Date |
|----------|-----------|------|
| Telegram-first, not web dashboard | Mike lives in Telegram. Web dashboard adds maintenance burden for rarely-used UI. | 2026-03-20 |
| Conversation ingestion via Susan RAG | Leverage existing 94K chunk infrastructure rather than building separate memory store. | 2026-03-20 |
| Oracle compliance in SOUL.md | Bake compliance rules into identity layer so every skill inherits them automatically. | 2026-03-19 |
| Skill chaining over monolithic skills | Smaller composable skills that chain together. Easier to test, reuse, and debug. | 2026-03-20 |
| `display.personality: ''` | Empty string lets SOUL.md control Jake's personality. Any other value overrides it. | 2026-03-20 |
| 4 AI Employees (not 6) | Mapped to Mike's actual needs, not the original framework's generic employee types. | 2026-03-20 |

---

## Session Estimates

| Sprint | Sessions | Key Deliverable |
|--------|----------|----------------|
| Sprint 3 (Email + Delegation) | 1 | Oracle Sentinel complete, Jake delegation |
| Sprint 4 (Recruiting) | 1 | Recruiting Captain operational |
| Sprint 5 (Dashboard + Content) | 1-2 | Telegram ops commands, content skills |
| Sprint 6 (Self-Improvement) | 1 | Episodic memory, self-improvement loop |
| **Total remaining** | **4-5 sessions** | **System at ~90%** |

---

## Success Criteria (Full System)

When all 6 sprints are complete, the system should pass these tests:

1. **Morning test**: Mike wakes up to a Telegram brief that includes Oracle email digest, today's meetings with prep notes, overnight intel, and any alerts — without Mike doing anything.
2. **Delegation test**: Mike types "ask Susan about competitor X" in Telegram and gets a researched answer within 60 seconds.
3. **Recruiting test**: Every Tuesday, outreach drafts appear in Telegram for review. Every Friday, a pipeline report arrives.
4. **Memory test**: Mike asks "what did we decide about X last week?" and gets an accurate answer with context.
5. **Status test**: Mike types `/jake-status` and sees full system health in one message.
6. **Self-improvement test**: Weekly review includes at least one suggestion for system improvement based on usage patterns.
