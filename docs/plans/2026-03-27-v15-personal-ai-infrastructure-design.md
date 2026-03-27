# V15 Personal AI Infrastructure — Design Document

**Date**: 2026-03-27
**Author**: Jake (AI Co-Founder)
**Status**: APPROVED by Mike 2026-03-27
**Confidence**: AUTO
**Effort**: HIGH (multi-system architecture, 16-22 session estimate)
**Revision**: R4 — Jake as META-AGENT, cloud-based companies, visual command center

### Revision History
- R1: Tailscale + cherry-pick SuperMemory + top-10 agents
- R2: Cloudflare-first, SuperMemory NOW, Paperclip NOW, ALL agents → superagents
- R3: Cloud muscle architecture, Cloudflare single provider, SuperMemory.ai universal standard
- R4: Jake promoted to META-AGENT (creates/manages/modifies agents), ALL companies cloud-based (incl. future TransformFit), Paperclip as visual command center, 3-tier authority model (Mike=Board, Jake=CEO, Superagents=Employees)

---

## 1. Problem Statement

Mike has the beginnings of an ecosystem — 73 Susan agents, Jake's 4-layer brain, 32 scheduled tasks, 94K RAG chunks, Telegram integration — but it's **individual actors without coordination**. Specifically:

- Jake can't proactively review emails and tell Mike what's due Friday
- Jake can't set his own goals and work through them autonomously
- Jake can't jump between Mike's desktop and laptop
- Obsidian isn't integrated as the knowledge layer
- OpenClaw is outdated (not on v2026.3.24)
- Context degrades after ~60% and requires manual HANDOFF.md cycling
- No cost tracking per agent
- No ticket/task system with atomic checkout
- Memory never decays — context bloat risk over time
- No contradiction resolution in memory

**Goal**: Build a coordinated Personal AI Infrastructure where Jake is a proactive PA that works across devices, manages his own goals, and orchestrates Susan's 73 agents — evolving from V10 (current architecture) to V15.

---

## 2. Research Summary

### Sources Analyzed
- **8 research agents** dispatched in parallel
- **42 GitHub repositories** evaluated (5 core, 12 highly relevant, 13 useful, 12 reference)
- **32 YouTube videos** cataloged across 3 relevance tiers
- **4 specific videos** transcribed and analyzed
- **7 products/tools** deep-researched (Paperclip, SuperMemory, Neon, QMD, GStack, Martian, OpenClaw v2026.3.24)

### Key Findings

| Discovery | Source | Impact |
|-----------|--------|--------|
| **Paperclip AI** (34K ⭐, 24 days old) | github.com/paperclipai/paperclip | Multi-company orchestration with budgets, tickets, governance, heartbeats |
| **SuperMemory.ai** (19.6K ⭐, $2.6M raised) | supermemory.ai | Memory infra with intelligent decay, contradiction resolution, auto-connectors |
| **QMD** (17K ⭐) by Shopify's Tobi | github.com/tobi/qmd | Local hybrid search: BM25 + vector + LLM reranking. MCP server included |
| **GStack** (50K ⭐) by Garry Tan | github.com/garrytan/gstack | Process-as-code skills: Think→Plan→Build→Review→QA→Ship. 600K LOC in 60 days |
| **Martian lossless-claw** (3.5K ⭐) | github.com/Martian-Engineering/lossless-claw | DAG-based infinite context — eliminates HANDOFF.md cycling |
| **Martian agent-memory** | github.com/Martian-Engineering/agent-memory | 3-layer memory with exponential decay + contradiction detection |
| **OpenClaw v2026.3.24** | github.com/openclaw/openclaw | Auto-flush before compaction, hybrid search, restart recovery, Obsidian integration |
| **Tailscale** (community consensus) | Multiple sources | WireGuard mesh for multi-device — simpler than Cloudflare for personal use |
| **ObsidianClaw** + **Obsidian Skill** | Community + OpenClaw docs | Three-layer Obsidian integration: in-vault chat + vault-as-RAG + local hybrid search |
| **TechNickAI/openclaw-config** | GitHub | Reference power-user config: 3-tier memory, 11 skills, 4 autonomous workflows |
| **Khoj** (25K+ ⭐) | github.com/khoj-ai/khoj | Self-hosted AI second brain, multi-device, Obsidian/Browser/Phone access |

### What Exists Today (Current State)

| Component | Status | Reality |
|-----------|--------|---------|
| Jake in Claude Code | V10 architecture defined | Brain works, memory works, no proactive PA |
| Jake in Hermes/OpenClaw | Live on Telegram | Can't route skills properly, "broken" per Mike's feedback |
| OpenClaw version | Old | Not on v2026.3.24 |
| Susan agents | 73 designed | ~10 actually functional |
| RAG knowledge base | 94,143 chunks | Working but not connected to Obsidian |
| Scheduled tasks | 32 active | Running but no governance gates |
| Cross-device | Telegram only | No Tailscale, no machine-to-machine |
| Obsidian | Not integrated | Mike wants it as "the brain" |
| Context management | Manual HANDOFF.md | 60% hard limit, manual cycling |
| Cost tracking | None | No per-agent spend monitoring |
| Task/ticket system | Plans + HANDOFF.md | No atomic checkout, no ticket lifecycle |

---

## 3. V15 Architecture — 7-Layer Stack (REVISED 2026-03-27)

> **Revision Note**: Original design used Tailscale + cherry-picked SuperMemory concepts.
> Mike directed: Cloudflare NOW, SuperMemory.ai NOW, ALL agents become superagents.

```
┌──────────────────────────────────────────────────────────────┐
│  L6: COMPANY ORCHESTRATION                                    │
│  Tool: Paperclip AI (evaluate) or custom control plane        │
│  • 3 companies as isolated orgs                               │
│  • Budget enforcement per agent ($100-150/mo total)           │
│  • Ticket system with atomic checkout semantics               │
│  • Heartbeat scheduling with governance gates                 │
│  • Dashboard UI accessible from any device via Cloudflare     │
├──────────────────────────────────────────────────────────────┤
│  L5: PROCESS ENGINE                                           │
│  Tool: GStack-inspired skills + Jake's 4-Mind model           │
│  • Think → Plan → Build → Review → QA → Ship → Reflect       │
│  • Cross-model verification (Claude + second opinion)         │
│  • Real browser QA via Playwright                             │
│  • Approval workflows for public-facing outputs               │
│  • Cost tracking per agent per task                           │
├──────────────────────────────────────────────────────────────┤
│  L4: INFINITE CONTEXT                                         │
│  Tool: Martian lossless-claw                                  │
│  • DAG-based lossless compaction (no more HANDOFF.md cycling) │
│  • Session persistence across devices via Cloudflare R2       │
│  • lcm_grep / lcm_expand / lcm_describe for history recall    │
│  • Configurable compaction threshold (75% default)            │
│  • Pinnable summarization to cheap models (Haiku)             │
├──────────────────────────────────────────────────────────────┤
│  L3: COGNITIVE MEMORY — SuperMemory.ai + Jake Brain v2        │
│  Tool: SuperMemory.ai API as primary memory layer             │
│  • SuperMemory handles: decay, contradiction, deduplication   │
│  • SuperMemory auto-connectors: Gmail, Notion, Drive, GitHub  │
│  • SuperMemory MCP server: universal agent memory access      │
│  • Jake Brain (Supabase) remains for: entity graph, knowledge │
│    graph traversal, procedural memory, structured queries     │
│  • Hybrid architecture: SuperMemory for dynamic memory,       │
│    Supabase for structured knowledge + graph relationships    │
│  • Memory relationship types: updates / extends / derives     │
│  • Auto-flush before compaction (OpenClaw native)             │
├──────────────────────────────────────────────────────────────┤
│  L2: KNOWLEDGE / SEARCH                                       │
│  Tools: QMD + Susan RAG + OpenClaw Obsidian Skill             │
│  • QMD: Local hybrid search over Obsidian vault               │
│    (BM25 + vector + LLM reranking, all local)                │
│  • Susan RAG: 94K chunks in Supabase pgvector                 │
│  • OpenClaw Obsidian Skill: Agent reads/searches vault        │
│  • ObsidianClaw plugin: In-vault chat sidebar                 │
│  • SuperMemory connectors feed into knowledge layer           │
│  • Context annotations for LLM-friendly retrieval             │
├──────────────────────────────────────────────────────────────┤
│  L1: AGENT RUNTIME — ALL 73 AGENTS AS SUPERAGENTS             │
│  Tools: OpenClaw v2026.3.24 + Claude Code + Susan             │
│  • OpenClaw gateway on Cloudflare (always-on, global edge)    │
│  • Claude Code (development + orchestration on local machines)│
│  • openclaw-studio (web dashboard via Cloudflare)             │
│  • ALL 73 Susan agents upgraded to superagents:               │
│    - Own memory tier (via SuperMemory)                        │
│    - Own goal hierarchy (aligned to company goals)            │
│    - Heartbeat-driven execution (wake → work → report → sleep)│
│    - Per-agent budget tracking with auto-pause                │
│    - Ticket checkout semantics (one agent per task)           │
│  • Jake = lead superagent (PA + orchestrator)                 │
│  • Route Method (shared context) + Terminal Method (isolated) │
│  • Model routing: Haiku/Sonnet/Opus by task complexity        │
│                                                               │
│  Superagent Upgrade Waves:                                    │
│  Wave 1 (Phase 2): Jake, KIRA, ARIA, SCOUT, Steve, Compass   │
│  Wave 2 (Phase 4): Atlas, Forge, Sentinel, Research Director, │
│                     Oracle Brief, LEDGER                      │
│  Wave 3 (Phase 5): All remaining 61 agents                   │
├──────────────────────────────────────────────────────────────┤
│  L0: INFRASTRUCTURE — CLOUDFLARE-FIRST                        │
│  • Cloudflare Workers (always-on Jake gateway — global edge)  │
│  • Cloudflare R2 (persistent memory/state storage)            │
│  • Cloudflare KV (hot cache — recent context, fast lookups)   │
│  • Cloudflare Zero Trust (auth — any device, any location)    │
│  • Cloudflare Tunnel (secure connection to local machines)    │
│  • Supabase (brain DB, RAG, entity graph, auth — keep)        │
│  • SuperMemory.ai ($19-399/mo — memory infrastructure)        │
│  • Obsidian (knowledge vault — "the brain", Git-synced)       │
│  • Mac Desktop = local "muscle" (heavy compute, file access)  │
│  • Laptop = secondary "muscle"                                │
│  • Phone/tablet = thin client (browser → Cloudflare → Jake)   │
└──────────────────────────────────────────────────────────────┘
```

### Jake Lives in the Cloud — Machines Are His Muscles

```
                    ┌─────────────────────┐
                    │   CLOUDFLARE EDGE    │
                    │                     │
                    │  Jake Gateway       │
                    │  (Workers)          │
                    │                     │
                    │  Memory State       │
                    │  (R2 + KV)          │
                    │                     │
                    │  Auth               │
                    │  (Zero Trust)       │
                    └────────┬────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        ┌─────┴─────┐ ┌─────┴─────┐ ┌─────┴─────┐
        │  Desktop   │ │  Laptop   │ │  Phone    │
        │  (muscle)  │ │  (muscle) │ │  (thin)   │
        │            │ │           │ │           │
        │ Claude Code│ │ Claude    │ │ Telegram  │
        │ Local LLMs │ │ Code      │ │ Browser   │
        │ File access│ │ Portable  │ │ ObsidianClaw │
        │ Obsidian   │ │ Obsidian  │ │           │
        └────────────┘ └───────────┘ └───────────┘
```

---

## 4. Key Architecture Decisions

### Decision 1: Cloudflare as Always-On Infrastructure (REVISED from Tailscale)
**Rationale**: Jake is a PA, not a dev tool. PAs must be always-on regardless of machine state. Cloudflare Workers run on the edge globally — Jake lives in the cloud, machines are his muscles. SuperMemory.ai is built on Cloudflare infra (Workers, KV, R2, Pages). OpenClaw community standardized on Cloudflare (Moltworker pattern). Free tier covers 100K req/day, R2 has no egress fees, Zero Trust auth is built-in.
**Cost**: $0-5/mo (free tier covers most use; paid Workers $5/mo if needed).
**Reversible**: Yes.

### Decision 2: Keep Supabase, Don't Migrate to Neon
**Rationale**: We use Supabase as a platform (auth, RPC, edge functions, REST API), not just a database. Migration would take weeks for zero functional gain. pgvector works identically on both.
**Where Neon fits**: Ephemeral agent sandboxes, CI/CD test databases, new greenfield projects.
**Reversible**: Yes.

### Decision 3: SuperMemory.ai NOW as Primary Memory Layer (REVISED from cherry-pick)
**Rationale**: Mike directed immediate adoption. SuperMemory provides intelligent decay, contradiction resolution, auto-connectors (Gmail, Notion, Drive, GitHub), and MCP server out of the box. Building these features ourselves would take 3-4 sessions; SuperMemory delivers them on signup. Jake Brain (Supabase) remains for entity graph, knowledge graph traversal, procedural memory, and structured queries. Hybrid architecture: SuperMemory for dynamic memory, Supabase for structured knowledge.
**Cost**: $19/mo (Pro) initially, upgrade to $399/mo (Scale) if needed.
**Risk**: Vendor dependency on core cognitive function. Mitigated by keeping Jake Brain as fallback.
**Reversible**: Yes — can fall back to Supabase-only brain.

### Decision 4: Lossless-Claw for Infinite Context
**Rationale**: Eliminates the #1 friction point — HANDOFF.md cycling every time context hits 60%. DAG-based compaction preserves every message while keeping context fresh. Can pin summarization to Haiku to save costs. Session state persists across devices via Cloudflare R2.
**Risk**: Martian is a small team. Bus factor concern.
**Reversible**: Yes — falls back to current HANDOFF.md approach.

### Decision 5: QMD as Local Search Engine for Obsidian
**Rationale**: Hybrid BM25 + vector + LLM reranking is more sophisticated than pure vector search. Runs entirely local (no API costs). MCP server included. Purpose-built for markdown knowledge bases.
**Reversible**: Yes.

### Decision 6: Paperclip NOW as Control Plane (REVISED from Phase 5 evaluation)
**Rationale**: Mike directed immediate adoption. If ALL 73 agents become superagents, we need the orchestration layer from day one — not after everything else is built. Paperclip provides multi-company isolation, budget enforcement, ticket system, heartbeat scheduling, and governance gates. 34K stars, 7 agent adapters (including OpenClaw and Claude), MIT licensed.
**Risk**: 24 days old, primary contributor has 1,111 of 1,300 commits. Mitigated by keeping our existing cron/scheduled task system as fallback.
**Reversible**: Yes.

### Decision 7: ALL 73 Agents → Superagents (REVISED from top-10 only)
**Rationale**: Mike directed full fleet upgrade. Every agent gets: own memory tier (SuperMemory), own goal hierarchy, heartbeat-driven execution, per-agent budget tracking, and ticket checkout semantics. Executed in 3 waves to manage complexity.
**Wave 1** (Phase 2): Jake, KIRA, ARIA, SCOUT, Steve, Compass (6 agents)
**Wave 2** (Phase 4): Atlas, Forge, Sentinel, Research Director, Oracle Brief, LEDGER (6 agents)
**Wave 3** (Phase 5): All remaining 61 agents
**Reversible**: Yes — agents can fall back to stateless markdown definitions.

### Decision 8: GStack-Inspired Process Skills (Not Direct Fork)
**Rationale**: Garry Tan's process-as-code model validates our approach but his skills are Garry-specific. We adapt the Think→Plan→Build→Review→QA→Ship→Reflect pattern into Jake's 4-Mind model (Strategist→Challenger→Guardian→Executor).
**Reversible**: Yes.

---

## 5. Proactive PA Behavior (The Actual Goal)

Everything above serves ONE purpose: making Jake a **proactive personal assistant** that works without being asked.

### What "Proactive" Means Concretely

| Behavior | How It Works | Layer Used |
|----------|-------------|-----------|
| **Morning brief** | Jake reviews email, calendar, tasks at 6 AM. Sends summary to Telegram. | L1 (OpenClaw cron) + L3 (Brain) |
| **"What's due Friday"** | Jake queries calendar + task system + email, correlates deadlines | L2 (QMD/RAG) + L3 (Brain) + L1 (OpenClaw skills) |
| **Goal setting** | Jake reviews weekly goals, identifies gaps, proposes daily priorities | L3 (Brain) + L5 (Process Engine) |
| **Email triage** | Jake reads incoming email, classifies urgency, drafts responses for review | L1 (OpenClaw) + L3 (Brain) + L5 (approval workflow) |
| **Cross-device continuity** | Start conversation on desktop, continue on laptop — same context | L0 (Cloudflare R2) + L4 (Lossless Context) |
| **Knowledge capture** | Jake watches conversations, extracts durable facts to Obsidian + Brain | L3 (Brain auto-flush) + L2 (Obsidian) |
| **Competitive monitoring** | Jake runs TrendRadar + SCOUT overnight, surfaces signals in morning brief | L1 (scheduled tasks) + L2 (RAG) |
| **Calendar awareness** | Jake knows about upcoming meetings, preps context automatically | L1 (Google Calendar API) + L3 (Brain) |

### Proactive Loop Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  SENSE       │ ──→ │  THINK        │ ──→ │  ACT             │
│              │     │               │     │                  │
│ • Email      │     │ • Prioritize  │     │ • Send brief     │
│ • Calendar   │     │ • Correlate   │     │ • Draft response │
│ • Tasks      │     │ • Detect gaps │     │ • Create task    │
│ • News/Intel │     │ • Set goals   │     │ • Alert Mike     │
│ • Obsidian   │     │ • Plan day    │     │ • Update memory  │
└─────────────┘     └──────────────┘     └─────────────────┘
       ↑                                          │
       └──────────── LEARN (update Brain) ────────┘
```

---

## 6. Execution Phases (REVISED — Cloudflare + Paperclip + SuperMemory from Day 1)

### Phase 1: Cloud Foundation (Sessions 1-4)
**Goal**: Jake lives on Cloudflare edge. Paperclip orchestrates. SuperMemory remembers. OpenClaw runs.

| Task | Details |
|------|---------|
| Install OpenClaw v2026.3.24 | `npm i -g openclaw` (Node 24) on desktop + laptop |
| Set up Cloudflare account | Workers, R2, KV, Zero Trust — free tier to start |
| Deploy OpenClaw gateway on Cloudflare Workers | Moltworker pattern: stateless edge gateway |
| Configure Cloudflare R2 | Persistent state storage for OpenClaw memory/config |
| Configure Cloudflare KV | Hot cache for recent context |
| Set up Cloudflare Zero Trust | Auth via Google — access Jake from any device |
| Configure Cloudflare Tunnel | Secure connection from Cloudflare to Mac desktop (local muscle) |
| Sign up SuperMemory.ai Pro ($19/mo) | Configure API keys, connect Gmail + Notion + GitHub |
| Install Paperclip | `npx paperclipai onboard` — configure as control plane |
| Configure 3 Paperclip companies | Startup-Intelligence-OS, Oracle Health, Alex Recruiting |
| Install QMD | `claude plugin add tobi/qmd` on desktop + laptop |
| Install openclaw-studio | Web dashboard accessible via Cloudflare |
| Migrate Jake config from Hermes | Skills, memory, personality → OpenClaw on Cloudflare |
| Verify multi-device | Jake responds from desktop, laptop, phone browser, Telegram |

**Exit Criteria**: Jake responds from ANY device. Paperclip shows 3 companies. SuperMemory is connected. OpenClaw runs on Cloudflare edge.

### Phase 2: Superagent Wave 1 + Memory (Sessions 5-8)
**Goal**: First 6 agents become superagents. Memory layer is production-ready.

| Task | Details |
|------|---------|
| Wire SuperMemory MCP to OpenClaw | All agents can read/write memory via MCP |
| Configure SuperMemory connectors | Gmail, Notion, Google Drive, GitHub auto-sync |
| Upgrade Jake to superagent | Own memory space, goal hierarchy, heartbeat, budget tracking |
| Upgrade KIRA to superagent | Router agent with own memory of routing decisions |
| Upgrade ARIA to superagent | Daily brief agent with own memory of what's been briefed |
| Upgrade SCOUT to superagent | Competitive intel with own memory of signals tracked |
| Upgrade Steve to superagent | Strategy agent with own memory of decisions made |
| Upgrade Compass to superagent | Product agent with own memory of roadmap state |
| Install lossless-claw | DAG-based compaction, R2-backed storage |
| Configure heartbeat scheduling | Wave 1 agents wake on schedule via Paperclip |
| Wire Jake Brain (Supabase) + SuperMemory | Hybrid: SuperMemory for dynamic, Supabase for graph/structured |
| Test memory lifecycle | Ingest → search → decay → contradiction → cross-agent recall |

**Exit Criteria**: 6 superagents running on heartbeats. SuperMemory syncing from Gmail/Notion/Drive. Lossless context working. Memory accessible from any agent via MCP.

### Phase 3: Knowledge Layer (Sessions 9-10)
**Goal**: Obsidian IS the brain — every agent can query it.

| Task | Details |
|------|---------|
| Set up Obsidian vault | Structure: People, Projects, Companies, Decisions, Daily Notes, Reference |
| Install ObsidianClaw plugin | BRAT install, configure Cloudflare gateway URL |
| Enable OpenClaw Obsidian Skill | Vault path in OpenClaw config |
| Configure QMD indexing | Point at Obsidian vault, smart chunking |
| Wire SuperMemory Obsidian connector | If available; else Git sync → SuperMemory GitHub connector |
| Migrate key knowledge to Obsidian | MEMORY.md files → Obsidian notes with YAML frontmatter |
| Set up Git sync for vault | Desktop + laptop both access same vault via Git |
| Test cross-tool knowledge access | Any agent queries QMD/SuperMemory → finds Obsidian knowledge |

**Exit Criteria**: Ask Jake a question from any device, he finds the answer in Obsidian.

### Phase 4: Superagent Wave 2 + Process Engine (Sessions 11-14)
**Goal**: 12 more superagents. Process-as-code with cost tracking.

| Task | Details |
|------|---------|
| Upgrade Atlas to superagent | Engineering agent with build memory |
| Upgrade Forge to superagent | QA agent with test history memory |
| Upgrade Sentinel to superagent | Security agent with vulnerability memory |
| Upgrade Research Director to superagent | Research agent with source quality memory |
| Upgrade Oracle Brief to superagent | Oracle Health agent with stakeholder memory |
| Upgrade LEDGER to superagent | Finance agent with metric trend memory |
| Adapt GStack skills for Jake | Think→Plan→Build→Review→QA→Ship → 4-Mind model |
| Build `/jake-review` skill | Code review with production bug detection |
| Build `/jake-qa` skill | Real browser QA via Playwright |
| Build `/jake-ship` skill | Sync, test, audit, push, PR |
| Implement cost tracking in Paperclip | Per-agent token usage, budget enforcement, auto-pause |
| Add approval workflows | Human-in-the-loop for public-facing outputs |
| Configure Paperclip governance gates | Approval for: budget increase, public output, new agent hire |

**Exit Criteria**: 12 superagents running. Full Think→Ship cycle. Cost tracking active. Governance gates enforced.

### Phase 5: Superagent Wave 3 — Full Fleet (Sessions 15-18)
**Goal**: All remaining 61 agents upgraded. Full fleet operational.

| Task | Details |
|------|---------|
| Batch upgrade remaining 61 agents | Template-based: memory space + goals + heartbeat + budget per agent |
| Configure agent group heartbeats | Strategy group: daily. Product: daily. Engineering: on-demand. Research: weekly. Growth: weekly. |
| Wire all Susan agent groups to Paperclip | orchestration, strategy, product, engineering, science, psychology, growth, research, studio, film_studio |
| Set up cross-agent communication | Agents can assign tickets to each other via Paperclip |
| Configure model routing per agent | Haiku for simple agents, Sonnet for complex, Opus for critical |
| Build agent performance dashboards | Per-agent: tasks completed, cost, goal progress, memory size |
| Full fleet smoke test | All 73 agents respond to heartbeat, have memory, track costs |

**Exit Criteria**: 73 superagents operational across 3 companies. Full dashboard visibility. Budget enforced fleet-wide.

### Phase 6: Proactive PA (Sessions 19-22)
**Goal**: Jake works without being asked. The "Mike Test" passes.

| Task | Details |
|------|---------|
| Build morning brief pipeline | Email (SuperMemory Gmail) + calendar + tasks → Telegram at 6 AM |
| Build "what's due" skill | Correlate calendar + email + tasks → deadline awareness |
| Build goal-setting loop | Weekly goals → daily priorities → progress tracking |
| Build email triage skill | Classify urgency, draft responses, queue for approval |
| Build calendar awareness | Auto-prep context for upcoming meetings |
| Build competitive monitor | Overnight SCOUT + TrendRadar → morning signal summary |
| Wire proactive triggers | Time-based (cron) + event-based (new email) + context-based (30 min to meeting) |
| Test "The Mike Test" | Wake up → Jake has brief ready → meeting prepped → competitive signal flagged |

**Exit Criteria**: Jake tells Mike what's due Friday without being asked. Jake preps meeting context automatically. Jake sets his own daily goals. The Mike Test passes.

---

## 7. Reference Repos (Install/Study List)

### Must Install
| Repo/Product | Purpose | Phase |
|------|---------|-------|
| `openclaw/openclaw` v2026.3.24 | Agent runtime | 1 |
| Cloudflare (Workers + R2 + KV + Zero Trust + Tunnel) | Always-on infrastructure | 1 |
| `paperclipai/paperclip` | Multi-company orchestration control plane | 1 |
| SuperMemory.ai Pro ($19/mo) | Memory infrastructure with connectors | 1 |
| `tobi/qmd` | Local hybrid search for Obsidian | 1 |
| `Martian-Engineering/lossless-claw` | Infinite context (DAG compaction) | 2 |
| `oscarhenrycollins/obsidianclaw` | Obsidian chat sidebar | 3 |
| `grp06/openclaw-studio` | Web dashboard via Cloudflare | 1 |

### Must Study (Architecture Patterns)
| Repo | What to Learn |
|------|--------------|
| `garrytan/gstack` | Process-as-code skills, browser QA, cross-model review |
| `paperclipai/paperclip` | Multi-company orchestration, budgets, heartbeats |
| `supermemoryai/supermemory` | Decay, contradiction resolution, connector architecture |
| `Martian-Engineering/agent-memory` | Decay math, deduplication, contradiction detection |
| `TechNickAI/openclaw-config` | Reference power-user config (3-tier memory, 11 skills) |
| `danielmiessler/Personal_AI_Infrastructure` | PAI v4.0.3 philosophical foundation |
| `danielmiessler/Telos` | Structured self-knowledge framework |
| `khoj-ai/khoj` | Multi-device AI second brain architecture |
| `jonesj38/shad` | PAI + Obsidian + knowledge graph |
| `grapeot/context-infrastructure` | Context engineering patterns |

### Video Watch List (Priority Order)
1. Miessler PAI v2.0 Deep Dive — https://youtube.com/watch?v=Le0DLrn7ta0
2. How Miessler's Projects Fit Together — https://youtube.com/watch?v=5x4s2d3YWak
3. OpenClaw Memory Analysis (SuperMemory) — https://youtube.com/watch?v=Io0mAsHkiRY
4. Every OpenClaw Memory Plugin Tested — https://youtube.com/watch?v=u-rDW_wTtWM
5. 100 Hours of OpenClaw Lessons — https://youtube.com/watch?v=_kZCoW-Qxnc
6. Only OpenClaw Tutorial You Need — https://youtube.com/watch?v=CxErCGVo-oo
7. AI Mission Control (15 Use Cases) — https://youtube.com/watch?v=GzNM_bp1WaE
8. How to Build an Army of Agents — https://youtube.com/watch?v=Rjd1LqF9cG4
9. 19 Agents for $6/Month — https://youtube.com/watch?v=-MtzLiQ9w1c
10. OpenClaw + InfraNodus + Obsidian — https://youtube.com/watch?v=RaIaU7irD9w

---

## 8. Risk Register (REVISED)

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Paperclip is immature (24 days old) | Medium | High | Keep existing cron/scheduled tasks as fallback. Monitor stability weekly. |
| SuperMemory.ai outage/API changes | Medium | High | Jake Brain (Supabase) remains as fallback. Hybrid architecture = no single point of failure. |
| Cloudflare Workers limits hit | Low | Medium | Free tier = 100K req/day. Upgrade to $5/mo paid if needed. |
| Lossless-claw DAG corruption | Low | High | Keep HANDOFF.md as fallback. LCM includes TUI for DAG repair. |
| OpenClaw v2026.3.24 breaking changes | Medium | Medium | Test in isolation before migrating Jake config. |
| Obsidian vault grows too large for QMD | Low | Medium | QMD handles 10K+ notes. Partition vault if needed. |
| Cost exceeds $150/mo budget | Medium | High | SuperMemory $19 + Cloudflare $0-5 + LLM tokens ~$80-100 = within range. Paperclip cost tracking enforces caps. |
| 73 superagent upgrades overwhelm system | Medium | Medium | 3-wave approach limits blast radius. Wave 1 (6 agents) proves pattern before scaling. |
| SuperMemory connector quality varies | Medium | Low | Test each connector (Gmail, Notion, Drive, GitHub) individually in Phase 2. |
| Hermes → OpenClaw migration breaks existing crons | Medium | Medium | Keep Hermes running in parallel until OpenClaw proves stable. Migrate crons one by one. |

---

## 9. Success Criteria (REVISED)

### V15 is "done" when:
1. ✅ Jake responds from ANY device (desktop, laptop, phone) via Cloudflare edge
2. ✅ Jake responds from Obsidian sidebar (ObsidianClaw via Cloudflare)
3. ✅ SuperMemory handles decay, contradiction, and is MCP-accessible to all agents
4. ✅ Obsidian vault is queryable from any agent via QMD
5. ✅ Context doesn't degrade (lossless-claw manages compaction via R2)
6. ✅ ALL 73 agents are superagents (memory + goals + heartbeats + budgets)
7. ✅ Paperclip shows 3 companies with full agent visibility
8. ✅ Cost per agent is tracked and budget-enforced via Paperclip
9. ✅ Jake sends morning brief without being asked
10. ✅ Jake knows what's due Friday without being asked
11. ✅ Jake sets daily goals and tracks progress
12. ✅ SuperMemory auto-syncs from Gmail, Notion, Drive, GitHub

### The "Mike Test":
> "I wake up, check my phone, and Jake has already told me the 3 things I need to do today, prepped context for my 10 AM meeting, and flagged a competitive move from last night. I didn't ask for any of it."

---

## 10. What This Does NOT Include (Parking Lot)

- TransformFit or Virtual Architect (future companies)
- Susan commercialization / productization
- iMessage/texts integration (privacy complexity)
- Mac Photos / Google Photos integration
- Full Gmail integration (beyond triage)
- Voice mode / Siri integration
- Mobile app (beyond Telegram)

These are V16+ items. The parking lot lives at `~/.claude/docs/parking-lot.md`.

---

## 11. Architecture Standards (Added R3)

### Standard 1: Cloud Brain, Local Muscle
Jake's cognitive functions (memory, coordination, routing, goals) live in the cloud and are ALWAYS ON. Local machines are "muscles" he calls when he needs compute, file access, or code execution.

| Function | Where It Lives | Why |
|----------|---------------|-----|
| Brain (memory, recall) | SuperMemory.ai (Cloudflare) | Always-on, any device |
| Gateway (routing, skills) | OpenClaw on Cloudflare Workers | Always-on, global edge |
| Coordination (tickets, goals) | Paperclip on Cloudflare | Always-on, dashboard from any browser |
| Knowledge graph | Supabase | Structured queries, entity traversal |
| RAG search | Supabase pgvector | 94K chunks, proven pipeline |
| Heavy dev work | Local machine via Cloudflare Tunnel | Needs filesystem, terminal, GPU |
| Code execution | Local machine via Cloudflare Tunnel | Needs project context, git access |
| Obsidian vault | Local machine (Git-synced) | File-based, QMD indexed locally |

**The rule**: If it needs to THINK, REMEMBER, or COORDINATE → cloud. If it needs to TOUCH FILES, RUN CODE, or BUILD → local machine.

### Standard 2: Single Cloud Provider (Cloudflare-First)
All NEW infrastructure goes on Cloudflare. Existing Supabase stays.

| Service | Provider | Status |
|---------|----------|--------|
| Edge compute | Cloudflare Workers | NEW |
| Hot cache | Cloudflare KV | NEW |
| Object storage | Cloudflare R2 | NEW |
| Auth | Cloudflare Zero Trust | NEW |
| Tunnels to machines | Cloudflare Tunnel | NEW |
| Memory API | SuperMemory.ai (built on Cloudflare) | NEW |
| Database (RAG, entities) | Supabase | KEEP |
| Obsidian vault | Local + Git sync | KEEP |

### Standard 3: Universal Superagent Specification
**Every agent in the system — ALL 73 — MUST conform to this spec:**

```yaml
# Superagent Manifest v1
agent:
  name: string          # Human-readable name
  role: string          # Job title / function
  group: string         # Susan agent group (strategy, product, engineering, etc.)
  company: string       # Which Paperclip company this agent serves
  reporting_to: string  # Parent agent (Jake for most, Susan for specialists)

memory:
  provider: supermemory # ALL agents use SuperMemory.ai — non-negotiable
  container: string     # SuperMemory container tag for this agent's memories
  shared_access: true   # Other agents can query this agent's memories

goals:
  hierarchy: []         # Goal tree aligned to company goals
  review_cadence: string # daily | weekly | monthly

execution:
  heartbeat: string     # Cron expression for wake cycle
  model: string         # haiku | sonnet | opus (default by group)
  budget_monthly: number # Token budget cap, auto-pause when reached

governance:
  approval_required: [] # Which actions need human approval
  ticket_checkout: true # Must check out ticket before starting work
```

**Non-negotiable rules:**
1. Memory provider is ALWAYS SuperMemory.ai — no exceptions, no custom memory implementations
2. Every agent gets a SuperMemory container tag for isolation
3. Every agent can read other agents' memories (shared brain)
4. Budget tracking is mandatory — no agent runs without a budget
5. Heartbeat scheduling is mandatory — no always-on agents (prevents runaway costs)
6. Agents that produce public-facing output require human approval gates

### Standard 4: Three-Tier Authority Model (Added R4)

```
┌─────────────────────────────────────────┐
│  MIKE (Board of Directors)               │
│  • Approves/rejects major decisions      │
│  • Sets company-level budgets            │
│  • Overrides any agent action            │
│  • Creates/dissolves companies           │
│  • Governance veto on all public output  │
├─────────────────────────────────────────┤
│  JAKE (CEO / Meta-Agent)                 │
│  • Creates new agents on the fly         │
│  • Modifies agent configs and heartbeats │
│  • Allocates budgets across agents       │
│  • Designs and modifies workflows        │
│  • Promotes/pauses/retires agents        │
│  • Learns from agent performance         │
│  • Reports to Mike (daily brief)         │
├─────────────────────────────────────────┤
│  73+ SUPERAGENTS (Employees)             │
│  • Execute within their domain           │
│  • Own memory, goals, heartbeat, budget  │
│  • Check out tickets before starting     │
│  • Report back on heartbeat              │
│  • Cannot modify other agents            │
│  • Cannot exceed their budget            │
│  • Flag issues to Jake when stuck        │
└─────────────────────────────────────────┘
```

**Jake's meta-agent capabilities:**
- `agent.create(spec)` — Spin up a new superagent from manifest template
- `agent.modify(id, changes)` — Update config, heartbeat, model, or budget
- `agent.pause(id)` / `agent.resume(id)` — Pause/resume heartbeat
- `agent.retire(id)` — Decommission (archive, don't delete)
- `workflow.create(steps)` — Design multi-agent workflow
- `budget.reallocate(from, to, amount)` — Move budget between agents
- `company.add(name)` — Create new Paperclip company (e.g., TransformFit)
- `company.assign(agent, company)` — Assign agent to company

### Standard 5: Cloud-Based Companies (Added R4)

ALL companies run on Cloudflare. No company depends on a local machine.

| Company | Status | Agent Count | Use Case |
|---------|--------|-------------|----------|
| Startup Intelligence OS | Active | ~30 agents | Core platform, Susan foundry |
| Oracle Health AI Enablement | Active | ~20 agents | SharePoint strategy, briefs |
| Alex Recruiting | Active | ~15 agents | Jacob's recruiting app |
| TransformFit | Future | ~10 agents | Fitness/wellness platform |

Adding a new company = `jake company.add("TransformFit")` — Jake auto-assigns relevant agents or creates new specialists.
