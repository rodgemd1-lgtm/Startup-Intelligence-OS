# PAI Migration Design — Hermes → OpenClaw + Miessler PAI Architecture

**Date**: 2026-03-24
**Author**: Jake (AI Co-Founder)
**Status**: DESIGN APPROVED — Awaiting implementation plan
**Approach**: Hybrid (Approach 3) — Miessler architecture + OpenClaw channels + Claude Code brain
**End-State**: Option A — Private PAI command center for Mike Rodgers

---

## Executive Summary

Migrate Mike's Personal AI Infrastructure from Hermes.ai (34/100 maturity, actively degrading) to a hybrid architecture modeled after Daniel Miessler's PAI v4.0.3. The new system uses OpenClaw as the channel gateway, LosslessClaw for infinite context memory, Fabric for 233+ prompt patterns, TELOS for structured identity, Supabase for persistent data, and Claude Code as the intelligence brain.

**The thesis**: Don't fix a broken platform. Rebuild on proven foundations.

**OpenClaw version**: v2026.3.23 (released March 23, 2026) — latest stable
**Primary model**: GPT-5.4 (OpenClaw channel layer) + Claude Opus (intelligence brain)
**Hardware**: Mac Studio (always-on daemon) + MacBook Pro (development client)

---

## Infrastructure Topology — Dual Machine + Dual Model

### Hardware Layout

```
MAC STUDIO (always-on, primary host)        MACBOOK PRO (mobile client)
├── OpenClaw Gateway daemon (port 18789)    ├── Claude Code sessions (primary dev)
│   └── GPT-5.4 as agent model              │   └── Opus for deep reasoning
├── LosslessClaw (SQLite DAG at ~/lcm.db)   ├── SSH/Tailscale tunnel to Studio
├── Fabric REST API (port 8080)             ├── Telegram app (direct messaging)
├── Susan MCP server                        ├── Visual dashboard (browser)
├── 16 MCP servers via mcporter             └── Codex + Gravity integration
├── Supabase connection (cloud)
├── Cron jobs (briefs, triage, prep)
├── Health monitoring + alerts
└── State: ~/.openclaw/ (single writer)
```

### Model Routing Strategy

| Model | Role | Cost/msg | Use Case |
|-------|------|----------|----------|
| **GPT-5.4** | OpenClaw agent model | ~$0.02 | Channel messages, cron jobs, rule-following, quick responses |
| **GPT-5.4-mini** | Fabric pattern execution | ~$0.005 | Summarization, extraction, cheap patterns |
| **GPT-5.4-nano** | Classification | ~$0.001 | Intent routing, urgency scoring |
| **Claude Opus** | Intelligence brain | ~$0.15 | Strategic reasoning, architecture, complex decisions |
| **Claude Sonnet** | Mid-tier agent tasks | ~$0.03 | Susan agent execution, research analysis |
| **Claude Haiku** | Cheap classification | ~$0.001 | Intent routing fallback, tagging |

**Why dual-model**: GPT-5.4 excels at rule-following and quick responses (OpenClaw's default). Claude Opus excels at deep reasoning and multi-step planning. 80% of messages are simple (GPT-5.4) and 20% need deep thinking (Opus). Cost-optimized AND quality-optimized.

### Sync Strategy

- **Git repo** (Startup-Intelligence-OS): Synced between both machines. TELOS files, Fabric patterns, agent definitions, config — all version controlled.
- **Supabase**: Cloud database — accessible from both machines. Memories, entities, graph, goals.
- **OpenClaw state** (`~/.openclaw/`): Mac Studio only. Single writer for LosslessClaw SQLite. MacBook Pro connects to Studio's gateway via WebSocket.
- **Claude Code sessions**: Can run on either machine. MacBook Pro is primary dev surface.

---

## Current State (Hermes) — What We're Leaving Behind

### Audit Summary (March 24, 2026)
| Domain | Score | Key Issue |
|--------|-------|-----------|
| Memory & Context | 5/10 | 99K memories but brain_search BROKEN (JSON serialization bug) |
| Autonomous Execution | 1/10 | autonomous_worker.py DOES NOT EXIST (vaporware) |
| Multi-System Integration | 4/10 | Susan RAG at localhost:7842 UNREACHABLE |
| Proactive Intelligence | 3/10 | 4/8 cron jobs FAILING (morning brief, email triage, check-in) |
| Personal Context Depth | 7/10 | Strongest domain — rich personal context |
| Communication Quality | 5/10 | Good when working, but delivery unreliable |
| Multi-Agent Orchestration | 2/10 | 73 agents defined, 0 autonomously invoked |
| Learning & Self-Improvement | 1/10 | Learner has recorded 0 corrections since install |
| Reliability & Error Recovery | 3/10 | 8 failures logged, 0 self-repaired |
| **TOTAL** | **34/100** | **Ferrari on blocks** |

### What Must Be Preserved
- 99,194 Supabase memories (88K episodic, 5.6K semantic, 5.2K procedural)
- 63 entities + 56 relationships (knowledge graph)
- Voyage AI embeddings (1024 dimensions)
- Jake's personality and voice
- Susan's 73 agent definitions + 6,693 RAG chunks
- 16 MCP server configurations
- Personal context (family, work patterns, career history)
- Telegram bot token + chat ID

### What Gets Killed
- Hermes daemon (`~/.hermes/`)
- 3 disconnected Telegram bots
- Mac-specific osascript hacks
- Manual cron health checks (launchd)
- Vaporware autonomous worker
- Broken brain_search plugin
- Non-functional learner hooks

---

## Target Architecture — The Miessler-Inspired Hybrid

### Design Philosophy
Following Daniel Miessler's 5-layer model:
1. **TELOS** — Structured self-knowledge AI can use
2. **PAI** — Personal AI Infrastructure scaffolding
3. **Substrate** — Foundation for human-AI interaction
4. **Fabric** — Crowdsourced prompt patterns for common tasks
5. **Human 3.0** — AI handles routine, human handles meaning

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    MIKE'S PAI (Hybrid)                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  IDENTITY LAYER (TELOS)                                      │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ MISSION.md  GOALS.md  PROJECTS.md  BELIEFS.md       │     │
│  │ MODELS.md   STRATEGIES.md  NARRATIVES.md  LEARNED.md│     │
│  │ CHALLENGES.md  IDEAS.md  WISDOM.md  WRONG.md        │     │
│  │ FRAMES.md  PREDICTIONS.md  BOOKS.md  PROBLEMS.md    │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  INTELLIGENCE LAYER (Claude Code)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Jake (brain)  │  │ Susan (73    │  │ Fabric (233  │       │
│  │ Personality   │  │ agents, RAG) │  │ patterns)    │       │
│  │ Algorithm     │  │ MCP server   │  │ REST API     │       │
│  │ Decision loop │  │ Research     │  │ Pipe chains  │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                  │                  │               │
│  ORCHESTRATION LAYER (Hooks + Agents)                        │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ SessionStart → LoadContext, TELOS injection          │     │
│  │ PreToolUse  → SecurityValidator (<50ms)              │     │
│  │ PostToolUse → PRDSync, QuestionAnswered              │     │
│  │ Stop        → VoiceCompletion, IntegrityCheck        │     │
│  │ SessionEnd  → WorkCompletionLearning, RatingCapture  │     │
│  │ Agent tiers → Task / Named / Custom (composable)     │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  MEMORY LAYER                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ LosslessClaw │  │ Supabase     │  │ Susan RAG    │       │
│  │ DAG context  │  │ 99K memories │  │ 6,693 chunks │       │
│  │ SQLite+FTS5  │  │ Entities     │  │ Vector search│       │
│  │ Never forgets│  │ Graph        │  │ Research     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  CHANNEL LAYER (OpenClaw Gateway)                            │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ Telegram │ iMessage │ Slack │ Discord │ Voice │ Web │     │
│  │          │          │       │         │       │     │     │
│  │ openclaw-claude-code-skill (bridge to Claude Code)  │     │
│  │ mcporter (bridge to 16 MCP servers)                 │     │
│  │ LosslessClaw (context engine plugin)                │     │
│  │ Cron + Webhooks + Gmail Pub/Sub                     │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  SECURITY LAYER (4-Layer Miessler Model)                     │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ L1: Settings Hardening (permissions, allow/deny)    │     │
│  │ L2: Constitutional Defense (AI Steering Rules)      │     │
│  │ L3: PreToolUse Validation (SecurityValidator hook)  │     │
│  │ L4: Safe Code Patterns (no shell exec, no traversal)│     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  DATA LAYER (Supabase + SQLite)                              │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ Supabase: jake_episodic, jake_semantic,             │     │
│  │           jake_procedural, jake_entities,           │     │
│  │           jake_relationships, jake_goals            │     │
│  │ SQLite:   LosslessClaw DAG (lcm.db)                 │     │
│  │ Local:    TELOS files, Fabric patterns, SOUL.md     │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  INFRASTRUCTURE                                              │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ Repo: Startup-Intelligence-OS (single monorepo)     │     │
│  │ Runtime: OpenClaw daemon + Claude Code sessions      │     │
│  │ Dispatch: Telegram → OpenClaw → Claude Code → Codex │     │
│  │ CI/CD: GitHub Actions                                │     │
│  │ Monitoring: OpenClaw health + Supabase metrics       │     │
│  └─────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Component Boundaries (Clean Seams)

| Component | Owns | Does NOT Own |
|-----------|------|-------------|
| **OpenClaw** | Channel routing, message delivery, cron, webhooks | Intelligence, reasoning, agent orchestration |
| **Claude Code** | Reasoning, planning, code generation, agent dispatch | Channel management, message transport |
| **LosslessClaw** | Conversation memory, DAG summarization, recall | Structured data, entities, domain knowledge |
| **Supabase** | Structured data, entities, relationships, goals, embeddings | Conversation state, context management |
| **Susan** | Agent definitions, RAG knowledge, research pipeline | Personality, identity, channel routing |
| **Fabric** | Prompt patterns, model routing, pipe chains | State, memory, orchestration |
| **TELOS** | Identity, mission, beliefs, goals, self-knowledge | Runtime behavior, code execution |
| **Jake** | Personality, voice, decision-making, user relationship | Infrastructure, data storage, channels |

---

## TELOS Files — Mike's Version

Adapted from Miessler's 18-file system for Mike's context:

### Core Philosophy
| File | Content for Mike |
|------|-----------------|
| `TELOS.md` | Framework overview, how these files connect |
| `MISSION.md` | "Build AI-powered operating systems that let founders run companies at 25x efficiency" |
| `BELIEFS.md` | AI augments humans, research-first, agents > manual work, plan before build |
| `WISDOM.md` | Accumulated lessons from Army, ISU, Aurora, Oracle Health, startup building |

### Life Data
| File | Content for Mike |
|------|-----------------|
| `BOOKS.md` | Books that shaped thinking (leadership, strategy, AI, business) |
| `LEARNED.md` | Migrate from jake_procedural (2K rules) |
| `WRONG.md` | Things Mike was wrong about (scope creep, "just code it", Hermes bet) |

### Mental Models
| File | Content for Mike |
|------|-----------------|
| `FRAMES.md` | "Think in agent teams", "Research before build", "25x or nothing" |
| `MODELS.md` | Strategos (5yr lookback), Jordan Voss test, FQR ratio, debt circuit breaker |
| `NARRATIVES.md` | "Army vet who builds AI companies", "Father of athletes who codes at night" |
| `STRATEGIES.md` | Cross-portfolio synergy, dogfood-then-productize, Mani-level operations |

### Goals & Challenges
| File | Content for Mike |
|------|-----------------|
| `GOALS.md` | Short: PAI at 86/100. Medium: 3 companies profitable. Long: Human 3.0 lifestyle |
| `PROJECTS.md` | Startup Intelligence OS, Oracle Health AI, Alex Recruiting |
| `PROBLEMS.md` | Hermes at 34/100, Susan RAG offline, autonomous execution vaporware |
| `CHALLENGES.md` | Scope creep, building too much/fixing too little, context rot |
| `PREDICTIONS.md` | Where AI agents will be in 2027, 2029, 2031 |

---

## V0-V10 Strategos Roadmap

### Reverse-Engineered from 2031 Vision

**2031 End-State**: Mike's PAI autonomously runs routine operations across 3 companies. Jake delivers structured intelligence, dispatches agents, self-repairs, and learns continuously. Mike focuses on high-leverage human decisions. The visual command center provides real-time ecosystem visibility. Score: 95/100.

### Stage Breakdown

#### V0: Foundation (Weeks 1-2) — Score Target: 34→40
**Theme**: Standing on new ground

- Install OpenClaw, connect Telegram (same bot token)
- Create TELOS identity files (18 files)
- Install LosslessClaw as context engine
- Install Fabric, configure top 50 patterns
- Create SOUL.md (Jake personality for OpenClaw)
- Configure Supabase bridge skill
- Implement 4-layer security model
- Kill Hermes daemon after verification

**Exit Gate**: Telegram message → OpenClaw → Jake responds → LosslessClaw persists → Fabric patterns callable

#### V1: Memory Migration (Weeks 3-4) — Score Target: 40→50
**Theme**: Nothing lost, everything found

- Export + migrate 99K Supabase memories to new 3-tier architecture
- Session tier: LosslessClaw DAG (conversation context)
- Work tier: PRD files with ISC checkboxes (active tasks)
- Learning tier: Failures, synthesis, signals (self-improvement data)
- Fix brain_search → replaced by lcm_grep + Supabase RPC
- Preserve Voyage AI embeddings for Supabase vectors
- Entity/relationship migration with dedup cleanup

**Exit Gate**: All 99K memories accessible via new architecture. Zero broken search calls for 48 hours.

#### V2: Agent Integration (Weeks 5-8) — Score Target: 50→60
**Theme**: The team shows up

- Susan MCP server as OpenClaw skill
- 16 MCP servers via mcporter bridge
- Fabric REST API as sidecar service
- Per-pattern model mapping (Haiku→summaries, Opus→strategy)
- Top 50 Fabric patterns as callable skills
- Claude Code bridge (openclaw-claude-code-skill)
- Codex + Gravity connection for complex reasoning
- Algorithm v1 (adapted from Miessler's 7-phase loop)

**Exit Gate**: End-to-end pipeline works: Telegram → OpenClaw → Susan agent → Fabric pattern → response. 73 agents callable. 16 MCP servers connected.

#### V3: Autonomous Execution (Months 3-4) — Score Target: 60→70
**Theme**: Jake works while Mike sleeps

- Real task worker (OpenClaw cron + webhook-driven)
- Goal tracking in Supabase with auto-progress updates
- Morning brief pipeline (overnight triage → Fabric summarize → Telegram)
- Meeting prep pipeline (calendar trigger → research → brief)
- Email triage pipeline (Gmail Pub/Sub → analyze → priority queue)
- Safety-tiered actions (AUTO/CONFIRM/APPROVE) on OpenClaw tools
- Self-repair: LosslessClaw recovery + gateway auto-restart + alerts

**Exit Gate**: Morning brief, meeting prep, and email triage delivered autonomously for 14 consecutive days. Task completion rate >80%.

#### V4: Proactive Intelligence (Months 5-6) — Score Target: 70→78
**Theme**: Jake anticipates, Mike decides

- Intent classification (KIRA-style routing)
- Smart notifications with urgency scoring + DND awareness
- Cross-company competitive intelligence digest
- Decision support (analyze_risk + t_red_team_thinking on pending decisions)
- Structured brief format (Miessler-style sections)
- Priority engine output ("Here's the ONE thing today")

**Exit Gate**: Mike identifies the one move in <30 seconds (Jordan Voss test). Notification quality rated 8+/10 for 2 weeks.

#### V5: Learning Engine (Months 7-9) — Score Target: 78→84
**Theme**: Jake gets smarter every day

- Correction capture (Mike corrects → log → learn → update patterns)
- RatingCapture hook (satisfaction signals, 1-5 scale)
- Failure capture with full context dumps
- Pattern detection → auto-generate Fabric custom patterns
- Memory consolidation (nightly episodic → semantic promotion)
- Weekly synthesis (LearningPatternSynthesis)
- Self-evaluation cycle
- Knowledge graph evolution (entity resolution, contradiction detection)
- WRONG.md updates (things Jake was wrong about)

**Exit Gate**: 100+ satisfaction signals captured. 5+ auto-generated custom patterns. Consolidation runs nightly for 30 days without failure.

#### V6: Multi-Channel (Months 10-12) — Score Target: 84→88
**Theme**: Jake is everywhere

- iMessage channel (BlueBubbles integration)
- Slack workspace channel
- Discord server channel
- Voice Wake on Mac (ElevenLabs TTS)
- Canvas (A2UI) for visual workspace
- Channel-aware personality (formal on Slack, casual on Telegram)

**Exit Gate**: Jake reachable on 4+ channels. Voice interaction working on Mac. Context persists across all channels via LosslessClaw.

#### V7: Visual Command Center (Year 2, Q1-Q2) — Score Target: 88→91
**Theme**: See the whole ecosystem

- Dashboard app (React/Next.js or React Native PWA)
- Ecosystem view: all 3 companies, agent status, memory health, task queue
- Real-time metrics: conversation DAG visualization, pattern usage, model costs
- Control plane: start/stop agents, approve actions, review briefs
- Mobile-first design (check from phone)
- Potential product candidate for sale/demo

**Exit Gate**: Dashboard deployed, showing real-time state of all 3 companies. Mike uses it daily for 2+ weeks.

#### V8: Cross-Domain Intelligence (Year 2, Q3-Q4) — Score Target: 91→93
**Theme**: Patterns that transfer

- Cross-portfolio synergy detection (Alex Recruiting ↔ Oracle Health ↔ Startup OS)
- Predictive capability modeling
- Fabric patterns that compose across domains
- Automated research pipelines triggered by gap detection
- Knowledge graph federation across all 3 companies

**Exit Gate**: 5+ cross-domain pattern transfers identified and applied. Predictive model accuracy >70%.

#### V9: Marketplace (Year 3) — Score Target: 93→95
**Theme**: Share what works

- Package custom patterns for ClawHub distribution
- Susan skills as installable OpenClaw skills
- Jake personality framework as template
- TELOS onboarding wizard for other founders
- Revenue potential from skill marketplace

**Exit Gate**: 3+ skills published to ClawHub. 1+ external user running a skill Mike built.

#### V10: Full Autonomy (Year 4-5) — Score Target: 95→98
**Theme**: Human 3.0

- Jake proposes his own capability upgrades
- Susan evolves her agent roster based on usage patterns
- System improves without Mike's intervention
- Self-healing, self-evolving, self-improving
- Mike focuses on high-leverage human decisions
- The routine is fully automated

**Exit Gate**: Jake handles 90%+ of routine operations across all 3 companies. Mike's daily PAI interaction is <15 minutes. System improves month-over-month without manual intervention.

---

## Migration Risk Matrix

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| Data loss during 99K memory migration | HIGH | LOW | Full Supabase backup before migration. Parallel run: old tables read-only until verified. |
| OpenClaw security vulnerability (CVE-2026-25253) | HIGH | MEDIUM | Patch immediately. Tailscale for remote access. No public exposure. |
| LosslessClaw DAG corruption | MEDIUM | LOW | SQLite WAL mode + daily backups. Built-in TUI repair tools. |
| Susan MCP bridge latency | MEDIUM | MEDIUM | Run locally, not over network. mcporter persistent connection. |
| Telegram bot token migration | LOW | LOW | Same token, different handler. OpenClaw supports existing tokens. |
| Fabric pattern quality variance | LOW | MEDIUM | Curate top 50 first. Custom patterns for specific workflows. |
| Two-runtime complexity (OpenClaw + Claude Code) | MEDIUM | MEDIUM | Clean boundaries documented. Health checks on both. |
| OpenClaw platform risk (pivots/acquired) | MEDIUM | LOW | Pin versions. Fork if necessary. Core intelligence stays in Claude Code. |

---

## Research Sources

All findings based on primary source analysis by 7 research agents:

1. **OpenClaw** (github.com/openclaw/openclaw) — 333,873★, 22+ channels, plugin SDK, 5,400+ skills
2. **LosslessClaw** (github.com/Martian-Engineering/lossless-claw) — 3,383★, DAG context engine, SQLite
3. **HiClaw** (hiclaw.app) — Managed hosting ($39/mo), redundant for self-hosting
4. **Fabric** (github.com/danielmiessler/fabric) — 40,147★, 233 patterns, REST API, pipe chains
5. **PAI** (github.com/danielmiessler/Personal_AI_Infrastructure) — 10,464★, TELOS, 7-component arch
6. **Masterclass Prompts** (masterclass-prompts.netlify.app) — 23-chapter OpenClaw deployment guide
7. **Hermes Audit** (current system) — 34/100, 99K memories, 9 domains scored

---

## Decision Record

| Decision | Rationale | Reversible? |
|----------|-----------|-------------|
| Approach 3 (Hybrid) over full OpenClaw adoption | Keep ownership of intelligence layer. OpenClaw for channels only. | Yes — can deepen OpenClaw integration later |
| Option A (private) over SaaS | Build for Mike first. Productize later if it works. | Yes — can extract platform in V9 |
| Miessler PAI as architecture model | Most mature open-source PAI. 18 TELOS files, 20 hooks, 4-layer security. | N/A — it's a design influence, not a dependency |
| Keep Supabase | 99K memories already there. Voyage AI embeddings. No reason to migrate data layer. | Yes — could move to Postgres/SQLite later |
| LosslessClaw for context | DAG-based, never loses data, agent recall tools. Best-in-class for conversation memory. | Yes — OpenClaw's context engine is pluggable |
| Kill Hermes | 34/100 score, 4 domains declining, autonomous worker is vaporware. Not fixable — rebuildable. | No — this is a one-way door. Backup everything first. |

---

## Next Steps

1. Get Mike's approval on this design
2. Create implementation plan (writing-plans skill)
3. Start V0 execution
