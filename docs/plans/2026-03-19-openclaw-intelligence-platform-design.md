# OpenClaw Intelligence Platform — Design Document

**Author:** Jake + Mike
**Date:** 2026-03-19
**Status:** DRAFT — Awaiting Mike's approval
**Confidence:** DRAFT — Strong research backing, needs Mike's call on a few key decisions
**Context Health:** GREEN

---

## Executive Summary

Transform Mike's OpenClaw + Jake PA stack from a basic Telegram chatbot into a **full-spectrum intelligence platform** that serves three companies (TransformFit, Oracle Health AI Enablement, Startup Intelligence OS) from a single Telegram interface — with sourced answers, proactive alerts, cost-effective model routing, and Susan's 94K-chunk RAG as the intelligence backbone.

**Target date:** July 18, 2026 (4 months)
**Budget constraint:** $100-150/month for AI APIs (NOT $1,000)
**Hardware:** MacBook Pro M4 Pro, 24GB RAM (excellent for local models)

---

## The Vision (Mike's Words)

> "I could be out with my boss, get on Telegram, and ask a question about our strategy for entering the payer space and prior auth. The system should send back a short, concise, and completely sourced message with clickable links."

> "It should help me build my companies by providing feedback like 'Hey, you're getting customer feedback and it's not good.'"

---

## Current State Assessment

### What We Have (Working)
| Component | Status | Location |
|-----------|--------|----------|
| OpenClaw Gateway | Running, port 7841 | ~/.openclaw/ |
| Telegram Bot | Configured, Jake personality | @BirchRodgersbot |
| FastAPI Bridge | 10 REST endpoints | ~/Desktop/jake-assistant/ |
| Hammerspoon | macOS control, 7 commands | ~/.hammerspoon/ |
| 49 OpenClaw Skills | Installed, not orchestrated | ~/clawd/skills/ |
| Susan RAG | 94,143 chunks, 22+ data types | Supabase + Voyage AI |
| Susan MCP Server | 7 tools (search, agents, sim) | susan-team-architect/backend/ |
| 73 Susan Agents | 9 groups, not connected to OpenClaw | susan-team-architect/agents/ |
| V4a Modules | Chains, Birch, Trust (41/41 tests) | susan-team-architect/backend/ |
| KIRA/ARIA/LEDGER | Running, 30 scheduled tasks | Claude Code scheduled tasks |
| OpenClaw Memory | EMPTY — no persistence | ~/clawd/workspace/memory/ |

### What's Missing (The Gaps)
1. **No model routing** — Everything goes to Claude Sonnet ($$$)
2. **No memory** — Every Telegram conversation starts cold
3. **No RAG bridge** — OpenClaw can't query Susan's 94K chunks
4. **No orchestration** — 49 skills are isolated islands
5. **No proactive intelligence** — No alerts, no "hey you should know this"
6. **No cross-company context** — Jake doesn't know which company Mike is asking about
7. **No cost controls** — No visibility into spend, no routing optimization
8. **No offline capability** — Everything requires cloud API calls

---

## Architecture Decision: Bridge + Progressive Migration

### Why This Approach (Option 3 → 4 from migration plan)

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **A: Skills-First** | Clean separation | Two systems to maintain forever | Too fragmented |
| **B: Native Rewrite** | Single system | Massive rewrite, loses Susan's maturity | Too risky |
| **C: Bridge Architecture** | Best of both, fast to build | Bridge complexity | **Winner for V1** |
| **D: Progressive Migration** | Evolves naturally over time | Longer timeline | **Winner for V2-V4** |

**Decision:** Start with C (bridge), evolve to D. OpenClaw is the Telegram interface + routing layer. Susan is the intelligence engine. They connect via exec calls to Susan's MCP server and CLI.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    TELEGRAM (User Interface)              │
│                    @BirchRodgersbot                       │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  OPENCLAW GATEWAY (Port 7841)             │
│                                                           │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Intent       │  │ Model Router │  │ Memory (QMD)   │  │
│  │ Classifier   │  │              │  │ + Cross-Company│  │
│  │              │  │ Ollama LOCAL │  │ Context         │  │
│  │ "payer       │  │ Groq  FAST  │  │                 │  │
│  │  strategy"   │  │ Haiku CHEAP │  │ Conversations   │  │
│  │  → research  │  │ Sonnet MED  │  │ Decisions       │  │
│  │  → susan RAG │  │ Opus  HEAVY │  │ Preferences     │  │
│  └──────┬──────┘  └──────┬───────┘  └────────┬────────┘  │
│         │                │                     │           │
│  ┌──────▼──────────────▼─────────────────────▼────────┐  │
│  │              SKILL ORCHESTRATOR                      │  │
│  │  Routes to the right skill based on intent + model  │  │
│  └──────┬────────────┬───────────────┬────────────────┘  │
│         │            │               │                    │
│  ┌──────▼──────┐ ┌──▼─────────┐ ┌──▼──────────────┐    │
│  │ Personal    │ │ Business    │ │ Desktop          │    │
│  │ Skills      │ │ Intelligence│ │ Control          │    │
│  │             │ │ Skills      │ │ Skills           │    │
│  │ Calendar    │ │ Susan Query │ │ Hammerspoon      │    │
│  │ Spotify     │ │ Research    │ │ Screenshot       │    │
│  │ Slack       │ │ Competitive │ │ App Launch       │    │
│  │ Reminders   │ │ Assessment  │ │ Volume           │    │
│  │ Plan My Day │ │ Brief       │ │ Dark Mode        │    │
│  └─────────────┘ └──────┬─────┘ └──────────────────┘    │
│                          │                                │
└──────────────────────────┼────────────────────────────────┘
                           │ exec: curl / python CLI
┌──────────────────────────▼────────────────────────────────┐
│              SUSAN INTELLIGENCE ENGINE                      │
│              (susan-team-architect/backend/)                │
│                                                            │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ RAG Engine   │  │ MCP Server   │  │ V4a Modules      │ │
│  │ 94K chunks   │  │ 7 tools      │  │ Chains + Birch   │ │
│  │ Voyage AI    │  │ Port 7842+   │  │ + Trust          │ │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────────┘ │
│         │                │                   │             │
│  ┌──────▼────────────────▼───────────────────▼──────────┐ │
│  │              73 SUSAN AGENTS                          │ │
│  │  Strategy: Steve, Shield, Bridge, Ledger, Vault      │ │
│  │  Product:  Marcus, Compass, Echo, Prism              │ │
│  │  Research: Research Director, Research Ops            │ │
│  │  Growth:   Aria, Haven, Herald, Beacon               │ │
│  │  ...and 60+ more                                     │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              SUPABASE (Persistence)                   │ │
│  │  Knowledge chunks, embeddings, agent outputs          │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│              LOCAL INFERENCE (Ollama on M4 Pro)             │
│  Llama 3.1 8B  — heartbeats, status, simple classification │
│  Qwen 2.5 7B   — code tasks, structured output             │
│  Nomic-embed    — local embeddings for QMD memory           │
└────────────────────────────────────────────────────────────┘
```

---

## Model Routing Strategy ($100-150/month)

### Tier Configuration

| Tier | Model | Provider | Cost | % of Traffic | Use Cases |
|------|-------|----------|------|-------------|-----------|
| **Local** | Llama 3.2 8B | Ollama (free) | $0/mo | ~30% | Heartbeats, status checks, simple Q&A, memory writes |
| **Economy** | Llama 3.3 70B | Groq (cheap) | ~$15-25/mo | ~25% | Sub-agents, classification, calendar, routine skills |
| **Standard** | Claude Sonnet 4 | Anthropic | ~$60-90/mo | ~40% | Primary conversations, RAG queries, research, writing |
| **Premium** | Claude Opus 4 | Anthropic | ~$10-20/mo | ~5% | Strategy decisions, architecture (manual invoke only) |

**Estimated total: ~$85-135/month** with proper routing.

### Critical Design Note: Routing is Structural, Not Dynamic

OpenClaw does NOT auto-detect query complexity. You design your **agent topology** so lightweight agents use cheap models and complex agents use expensive ones. There is no "keyword-based" or "complexity-based" automatic routing (feature requests open on GitHub).

**What this means for us:** We build separate OpenClaw agents for different tiers, not one agent that switches models. Example:
- `jake-chat` agent → Sonnet (daily driver)
- `jake-triage` agent → Groq (quick lookups, classification)
- `jake-deep-work` agent → Opus (strategy, critical analysis)
- Heartbeats → Ollama local

### Actual OpenClaw Config (JSON in `~/.openclaw/openclaw.json`)

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-20250514",
        "fallbacks": [
          "groq/llama-3.3-70b-versatile",
          "ollama/llama3.2:8b"
        ]
      },
      "subagents": {
        "model": "groq/llama-3.3-70b-versatile",
        "maxConcurrent": 2,
        "archiveAfterMinutes": 60
      },
      "heartbeat": {
        "every": "30m",
        "model": "ollama/llama3.2:3b"
      },
      "contextTokens": 128000
    },
    "list": [
      { "id": "jake-chat", "model": "anthropic/claude-sonnet-4-20250514" },
      { "id": "jake-triage", "model": "groq/llama-3.3-70b-versatile" },
      { "id": "jake-deep-work", "model": "anthropic/claude-opus-4-20250514" },
      { "id": "daily-ops", "model": "groq/llama-3.3-70b-versatile" }
    ]
  },
  "models": {
    "providers": {
      "ollama": {
        "baseUrl": "http://127.0.0.1:11434/v1",
        "apiKey": "ollama-local",
        "api": "openai-completions",
        "models": [
          {
            "id": "llama3.2:8b",
            "name": "Llama 3.2 8B",
            "contextWindow": 65536,
            "maxTokens": 8192
          },
          {
            "id": "llama3.2:3b",
            "name": "Llama 3.2 3B",
            "contextWindow": 32768,
            "maxTokens": 4096
          }
        ]
      }
    }
  }
}
```

### Fallback Chain Behavior

OpenClaw supports fallback chains via `model.fallbacks` array. Important caveat: **fallbacks trigger on provider errors (429, 500, auth failure), NOT on answer quality.** If Ollama returns a bad answer, OpenClaw will not auto-escalate to Claude.

For API key rotation within a provider: `ANTHROPIC_API_KEYS="key1;key2;key3"` — OpenClaw rotates on 429 errors.

### Ollama Setup (Required for Local Tier)

```bash
# Install Ollama
brew install ollama

# Pull models
ollama pull llama3.2:8b    # Quality local reasoning
ollama pull llama3.2:3b    # Fast heartbeats

# Start server (runs on port 11434)
ollama serve
```

**M4 Pro 24GB can comfortably run:** `llama3.2:8b` (primary local), `llama3.2:3b` (heartbeats), and `qwen2.5-coder:7b` (code tasks) simultaneously.

### Cost Safety Net

- Monthly budget cap in OpenClaw config: $150
- Alert at 80% ($120): Jake messages Mike on Telegram "Yo heads up, we're at 80% of the API budget this month"
- Hard stop at 100%: Fall back to Ollama-only mode
- Weekly cost report via ARIA brief

---

## Skill Architecture

### Skill Categories (Prioritized)

#### Tier 1: Must Have (Week 1-2)
| Skill | Purpose | Model Tier | Source |
|-------|---------|------------|--------|
| `susan-rag-query` | Query Susan's 94K-chunk knowledge base via Telegram | Standard | Custom build |
| `model-router` | Route queries to appropriate model tier | Local | Custom build |
| `company-context` | Detect which company Mike is asking about | Economy | Custom build |
| `cross-company-memory` | Persistent memory across conversations | Local | Custom build |
| `daily-brief-telegram` | Push ARIA daily brief to Telegram | Economy | Custom build |

#### Tier 2: High Value (Week 3-4)
| Skill | Purpose | Model Tier | Source |
|-------|---------|------------|--------|
| `competitive-intel` | TrendRadar signals → Telegram alerts | Standard | Custom build |
| `research-on-demand` | Deep research via Susan agents on demand | Premium | Custom build |
| `oracle-health-query` | Oracle Health strategy queries (compliance-safe) | Standard | Custom build |
| `feedback-monitor` | Monitor customer feedback signals | Economy | Custom build |
| `strategy-advisor` | "What should I do about X?" with sourced answers | Premium | Custom build |

#### Tier 3: Quality of Life (Month 2)
| Skill | Purpose | Model Tier | Source |
|-------|---------|------------|--------|
| `meeting-prep` | Pre-meeting brief based on calendar + company context | Standard | Custom build |
| `weekly-digest` | Friday synthesis of all company activity | Standard | Custom build |
| `idea-capture` | Capture ideas to parking lot with context | Economy | Custom build |
| `decision-log` | Log and retrieve past decisions | Economy | Custom build |

#### Tier 4: From ClawHub (Install directly)
| Skill | Purpose | Source | Why |
|-------|---------|--------|-----|
| `digitaladaption/model-router` | Task classifier + cost optimization modes | ClawHub | Maps to Jake's effort system, automates model selection |
| `arminnaimi/agent-team-orchestration` | Multi-agent handoff protocol + roles | ClawHub | Production-grade patterns for Jake + Susan agent dispatch |
| `1kalin/morning-daily-briefing` | Daily brief template | ClawHub | Template for ARIA's Telegram brief |
| `gmail` | Email awareness (subject lines only per Oracle compliance) | ClawHub | Already installed |
| `slack` | Already installed — enhance with Susan context | ClawHub | Already installed |
| `notion` | Already installed — sync with company docs | ClawHub | Already installed |

#### Patterns to Steal (Don't Install, Adapt)
| Pattern | Source Skill | What to Take |
|---------|-------------|-------------|
| Session compression | `0range-x/triple-layer-memory` | Auto-compress at 150k tokens, retain last 50k, semantic dedup (>0.88 rejects) |
| Cost circuit breakers | `atlaspa/cost-governor` | Budget limits (hourly/daily/monthly), auto-stop at threshold |
| Cron conventions | `brennerspear/cron-setup` | Default Sonnet for cron (never Opus), self-contained task instructions |

**Key insight from analysis of 7,714 skills:** The highest-value move is not installing skills wholesale but stealing the best patterns and integrating them into Jake's architecture. Most skills are prompt engineering + lightweight Python — our custom skills with Susan integration will be better than generic ClawHub skills.

### Skill Format (SKILL.md Standard)

```markdown
---
name: susan-rag-query
description: Query Susan's knowledge base for sourced answers
version: 1.0.0
triggers:
  - "what do we know about"
  - "research"
  - "find me"
  - "strategy for"
  - "prior auth"
  - "payer"
model_tier: standard
company_aware: true
---

# Susan RAG Query

When the user asks a knowledge question:

1. Detect company context (Oracle Health, TransformFit, Startup Intelligence OS)
2. Call Susan's search_knowledge endpoint via exec:
   ```
   curl -s http://localhost:7842/api/susan/search \
     -H "Content-Type: application/json" \
     -d '{"query": "<user question>", "company": "<detected company>", "limit": 5}'
   ```
3. Format response as:
   - **Short answer** (2-3 sentences max — this is Telegram, not an essay)
   - **Sources** (clickable links where available)
   - **Confidence** (HIGH/MEDIUM/LOW based on chunk match scores)
4. If confidence is LOW, say so: "I found some related info but I'm not super confident. Want me to do a deeper dig?"

## Compliance Rules
- Oracle Health: NEVER include email bodies. Subject lines only.
- Always cite sources. Never make up citations.
- If asked about PHI or patient data, refuse and explain why.
```

---

## Memory Architecture (Adopting TechNickAI Three-Tier Pattern)

Based on analysis of [TechNickAI/openclaw-config](https://github.com/TechNickAI/openclaw-config) — the reference power-user OpenClaw setup.

### Three-Tier Memory System

| Tier | Files | Loading | Purpose |
|------|-------|---------|---------|
| **Tier 1** | `MEMORY.md` | Always loaded (main session only) | Curated essentials, ~100 lines max |
| **Tier 2** | `memory/YYYY-MM-DD.md` | Today + yesterday auto-loaded | Raw daily observations |
| **Tier 3** | `memory/companies/`, `people/`, `topics/` | Searched via QMD on demand | Deep knowledge |

### Directory Structure

```
~/clawd/workspace/memory/
├── MEMORY.md              # Tier 1: curated essentials (always loaded)
├── 2026-03-19.md          # Tier 2: today's observations (auto-loaded)
├── 2026-03-18.md          # Tier 2: yesterday's observations (auto-loaded)
├── companies/
│   ├── oracle-health.md   # Tier 3: OH context, stakeholders, strategy
│   ├── transformfit.md    # Tier 3: TF context, metrics, feedback
│   └── startup-ios.md     # Tier 3: SiOS context, architecture, status
├── people/
│   ├── jacob.md           # Tier 3: Jacob's schedule, recruiting, training
│   ├── matt-cohlmia.md   # Tier 3: Oracle Health stakeholder
│   └── key-contacts.md   # Tier 3: Important people across companies
├── preferences/
│   ├── mike-profile.md   # Communication style, pet peeves
│   └── work-patterns.md  # Time of day, energy patterns
├── decisions/
│   └── YYYY-MM-DD-topic.md # Important decisions with reasoning
└── knowledge/
    ├── patterns.md        # Cross-domain patterns
    └── lessons.md         # Lessons learned
```

### Librarian Skill (Memory Maintenance Loop)

Adopted from TechNickAI: a periodic skill that promotes knowledge upward:
1. Daily observations → structured knowledge files (companies/, people/, topics/)
2. Structured knowledge → curated MEMORY.md summaries
3. Sections in MEMORY.md past ~30 lines get extracted to topic files
4. People mentioned across 5+ days get their own file

### Critical Sub-Agent Pattern

**Sub-agents CANNOT read workspace files.** When delegating to sub-agents (e.g., jake-triage on Groq), the delegating agent must inline SOUL.md personality, USER.md context, and relevant memory into the spawn prompt. This is the critical difference between useful and generic sub-agent results.

### Memory Sync with Susan

- **Susan → QMD**: Nightly sync of key findings, agent outputs, and knowledge digests into OpenClaw's memory
- **QMD → Susan**: Important decisions and feedback captured in Telegram get written back to Susan's RAG
- **Bidirectional**: Memory is the bridge between "Jake on Telegram" and "Susan the intelligence engine"

### Patterns Adopted from TechNickAI Reference Config

| Pattern | What It Is | Why We're Adopting It |
|---------|-----------|----------------------|
| Workflow state separation | AGENT.md (algorithm) + rules.md (user prefs) + agent_notes.md (learned) | Clean update-without-clobber |
| Daily memory files | memory/YYYY-MM-DD.md auto-loaded | Raw capture without polluting curated memory |
| Librarian skill | Periodic memory promotion loop | Automated knowledge curation |
| Setup interviews | First-run conversational config | User-friendly preference capture |
| Self-contained UV scripts | Each skill carries its own deps inline | No dependency conflicts |
| CLAUDE.local.md persistence | Gitignored working memory between health checks | Discover once, check repeatedly |
| Batched heartbeat | Single periodic check vs many cron jobs | Simpler cron, comprehensive checks |

---

## The "Payer Strategy" Query Flow (End-to-End Example)

Mike is at dinner with his boss. He opens Telegram and types:
> "What's our strategy for entering the payer space and prior auth?"

### What Happens:

1. **OpenClaw receives message** via Telegram channel
2. **Intent classifier** (local Llama) tags: `research_query`, `company:oracle-health`, `topic:payer-strategy`
3. **Model router** selects: Standard tier (Claude Sonnet) — this needs RAG + reasoning
4. **Company context** loaded from `memory/companies/oracle-health.md`
5. **Susan RAG query** fires via exec:
   ```
   curl -s localhost:7842/api/susan/search \
     -d '{"query":"payer space strategy prior authorization","company":"oracle-health","limit":5}'
   ```
6. **Susan returns** 5 relevant chunks with sources, match scores, and data types
7. **Claude Sonnet synthesizes** a concise answer with:
   - 2-3 sentence strategy summary
   - 3-4 clickable source links
   - Confidence level
8. **Response sent to Telegram** in under 8 seconds:

   > **Payer Strategy — Oracle Health**
   >
   > Our primary wedge is CMS interoperability mandates (2026 deadline) forcing payers to adopt FHIR-based prior auth. Oracle Health's position: leverage existing EHR integration to offer pre-built prior auth workflows that reduce payer admin costs by 30-40%.
   >
   > **Sources:**
   > - [CMS Prior Auth Final Rule](link) (RAG: oracle-health-research)
   > - [Competitor Analysis: Epic vs Cerner PA](link) (RAG: competitive-intel)
   > - [Internal Strategy Brief 2026-03-15](link) (RAG: oracle-health-briefs)
   >
   > **Confidence:** HIGH (4/5 chunks matched at >0.85)

### Response time budget:
- Intent classification (local): ~200ms
- RAG query (Supabase): ~800ms
- Sonnet synthesis: ~3-5s
- Telegram delivery: ~500ms
- **Total: ~5-7 seconds**

---

## Proactive Intelligence ("Adapt, Evolve, Progress")

### Alert Categories

| Alert Type | Trigger | Frequency | Model Tier |
|-----------|---------|-----------|------------|
| **Competitive Signal** | TrendRadar detects competitor move | Real-time | Economy |
| **Customer Feedback** | Negative feedback pattern detected | Daily digest | Standard |
| **Calendar Prep** | 30 min before important meetings | Per-meeting | Economy |
| **Strategy Drift** | Actions diverge from stated strategy | Weekly | Premium |
| **Opportunity Alert** | Cross-company pattern detected | As found | Standard |
| **Budget Warning** | API spend approaching limit | At 80% | Local |

### Proactive Message Format (Telegram)

```
⚡ COMPETITIVE SIGNAL — Oracle Health

Epic just announced a native prior auth module at HIMSS.
This affects our payer strategy wedge.

What I know:
- Epic's module ships Q3 2026 (vs our Q2 target)
- Their pricing is per-transaction, ours is flat-rate
- 3 existing customers have asked about our timeline

Recommended action: Accelerate PA module launch by 2 weeks.

Sources: [TrendRadar signal], [Customer feedback log]
Confidence: HIGH

Reply /deep-dive for full analysis
Reply /dismiss to acknowledge
```

---

## Cost Projection (Monthly)

| Category | Cost | Notes |
|----------|------|-------|
| **Anthropic API** | | |
| Claude Haiku (40% traffic) | ~$15 | ~500 queries/day × cheap |
| Claude Sonnet (25% traffic) | ~$60 | ~300 queries/day, RAG + reasoning |
| Claude Opus (5% traffic) | ~$30 | ~30 queries/day, strategy only |
| **Local (Ollama)** | $0 | Runs on M4 Pro, 30% of traffic |
| **Supabase** | $0 | Free tier sufficient for current scale |
| **Total** | **~$105/mo** | Well within $100-150 target |

### Cost Reduction Levers (If Needed)
- Increase local Ollama percentage (30% → 50%) = saves ~$20/mo
- Cache frequent RAG queries (many questions repeat) = saves ~$10/mo
- Batch non-urgent queries to off-peak = saves ~$5/mo
- Use Groq for medium-tier instead of Sonnet = saves ~$30/mo but lower quality

---

## Strategos 6-Lens Assessment

> **Full 489-line assessment:** `.startup-os/artifacts/strategos-6-lens-openclaw-july-2026.md`
>
> **Core thesis:** "Mike has built the engine room of a battleship but has not yet connected the steering wheel. The 4-month plan is about wiring, not building."

### Lens 1: Market Position
**Current:** Basic chatbot, no differentiation from ChatGPT/Perplexity
**Target (July 2026):** Personal intelligence platform with company-specific RAG, proactive alerts, and multi-company context switching — something no consumer AI product offers
**Moat:** Susan's 94K curated knowledge chunks + 73 specialized agents + Oracle Health compliance boundaries
**Risk:** LOW — this is a personal tool, not a product (yet)

### Lens 2: Capability Architecture
**Current capabilities:** 8/30 target capabilities implemented
**Critical gaps:**
- RAG bridge to OpenClaw (blocks everything)
- Model routing (blocks cost control)
- Memory persistence (blocks context continuity)
- Proactive alerting (blocks "Adapt, Evolve, Progress")

### Lens 3: Operating Model
**Day-to-day:** Jake runs autonomously. Mike interacts via Telegram. Susan processes in background.
**Maintenance:** ~30 min/week for Mike (review trust dashboard, approve staged outputs, update memory)
**Monitoring:** Cost dashboard, query success rate, response time p95

### Lens 4: Technology Stack
**Optimal given constraints:**
- OpenClaw (Telegram + routing + memory + skills)
- Susan backend (RAG + agents + chains)
- Ollama (local inference, M4 Pro)
- Supabase (persistence, embeddings)
- FastAPI bridge (connectors)
- Hammerspoon (macOS control)

### Lens 5: Risk & Governance
| Risk | Severity | Mitigation |
|------|----------|------------|
| Oracle compliance (email bodies) | HIGH | Hard-coded in SOUL.md + skill rules |
| API cost overrun | MEDIUM | Budget cap + alerts + local fallback |
| Single point of failure (Mac) | MEDIUM | Supabase persists data; Mac is execution layer only |
| Stale knowledge | LOW | Knowledge freshness daemon already running |
| Model quality degradation | LOW | Tiered routing ensures critical queries get best model |

### Lens 6: Evolution Path (4-Month Timeline)

#### Phase 1: Foundation (Weeks 1-2) — "Jake Gets a Brain"
- Install Ollama + local models
- Configure model routing in OpenClaw
- Build `susan-rag-query` skill (the killer feature)
- Build `company-context` skill
- Seed OpenClaw memory with cross-company context
- Wire daily brief to Telegram

#### Phase 2: Intelligence (Weeks 3-4) — "Jake Gets Street Smart"
- Build competitive intel alerts (TrendRadar → Telegram)
- Build `research-on-demand` skill
- Build `oracle-health-query` skill (compliance-safe)
- Connect V4a chains to OpenClaw (signal-triggered alerts)
- Implement feedback monitoring

#### Phase 3: Autonomy (Weeks 5-8) — "Jake Runs the Show"
- Wire V4b (real agent dispatch in chains)
- Build `strategy-advisor` skill
- Build `meeting-prep` skill
- Implement memory sync (QMD ↔ Susan RAG)
- Trust graduation: more queries go to AUTO

#### Phase 4: Mastery (Weeks 9-16) — "Jake is the OS"
- Progressive migration of KIRA/ARIA/LEDGER into OpenClaw native
- Cross-company pattern detection via Telegram
- Weekly digest automation
- Decision log with retrieval
- Full "Adapt, Evolve, Progress" loop running

---

## Future-Back Narrative (July 18, 2026)

It's July 18. Mike is at HIMSS 2026. Between sessions, he pulls out his phone and opens Telegram.

> **Mike:** "What should I know before my 2pm with the Humana VP?"
>
> **Jake:** "Your calendar shows 'Humana PA Demo' at 2pm in Hall B. Here's your prep:
>
> 1. **Their pain:** Humana's prior auth denial rate is 18% (industry avg 12%). They announced a 'PA modernization initiative' 6 weeks ago [TrendRadar signal].
>
> 2. **Our angle:** Oracle Health's PA module reduced denial rates by 40% in the Cigna pilot. Lead with that.
>
> 3. **Watch out:** Their CTO was at the Epic booth this morning for 45 minutes [conference intel]. They're comparing.
>
> 4. **Your prep doc:** [Link to full brief in Susan RAG]
>
> Good luck. Don't let them lowball you on pricing."

That's what we're building. A co-founder in your pocket that actually knows your business.

---

## Session Plan Recommendation

Given the scope, Jake recommends **3 focused sessions**:

### Session A: Foundation (Tonight/Tomorrow)
- Install Ollama + configure model routing
- Build `susan-rag-query` skill
- Build `company-context` skill
- Seed memory
- **Deliverable:** Mike can ask business questions on Telegram and get sourced answers

### Session B: V4b Engine Wiring (Separate session)
- Wire real agent dispatch into chains
- Firehose SSE listener for Birch
- Trust graduation automation
- **Deliverable:** Semi-autonomous chain execution

### Session C: Intelligence Layer (Separate session)
- Competitive intel alerts
- Proactive feedback monitoring
- Meeting prep skill
- Memory sync
- **Deliverable:** Proactive intelligence on Telegram

---

## Key Decisions for Mike

| # | Decision | Jake's Recommendation | Needs Mike's Call? |
|---|----------|----------------------|-------------------|
| 1 | Model routing: Ollama local vs Groq cloud for economy tier | **Ollama** — free, private, M4 Pro handles it | Yes |
| 2 | Memory format: QMD native vs Susan RAG sync | **Both** — QMD for fast Telegram context, Susan for deep search | No (both) |
| 3 | Phase 1 priority: RAG query skill vs model routing | **RAG query first** — it's the killer feature | Yes |
| 4 | Oracle compliance boundary: how strict? | **Subject lines only**, never email bodies, no PHI | Confirm |
| 5 | Proactive alerts: Telegram DM vs separate channel? | **DM for urgent**, channel for digest | Yes |

---

## Success Criteria

| Metric | Target | How to Measure |
|--------|--------|---------------|
| Query-to-answer time | < 8 seconds (p95) | Telegram timestamp delta |
| RAG answer accuracy | > 80% useful | Mike's subjective rating (thumbs up/down) |
| Monthly API cost | < $150 | Anthropic dashboard |
| Local model coverage | > 30% of queries | OpenClaw routing logs |
| Memory continuity | Context persists across sessions | Can reference yesterday's conversation |
| Proactive alerts | 3-5 useful alerts/week | Count of non-dismissed alerts |
| Mike's daily interaction time | < 30 min for operations | Self-reported |
