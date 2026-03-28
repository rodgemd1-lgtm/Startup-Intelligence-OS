# V20: Full Cloud Team — Three Strategic Options

**Date:** 2026-03-28
**Owner:** Mike Rodgers
**Architect:** Jake
**Status:** DRAFT — Awaiting Approval
**Supersedes:** V7, V8, V9, V10 plans (2026-03-24)
**Method:** Strategos Future-Back + 6 Lens Analysis

---

## The V20 End State (Future-Back Starting Point)

**Date: December 2026. What's true:**

Mike opens his phone at 6:01 AM. Jake's morning brief is already there — email triaged, calendar prepped, overnight work completed. 14 tasks done while he slept. Susan's team grew 50% smarter this week across all domains. Three businesses are running. Mike's daily interaction is 8 minutes.

The full 73-agent team is accessible from any device. No servers to maintain. No local dependencies. Open-source models handle 85% of inference at near-zero cost. Claude handles the 15% that requires world-class reasoning. The system evolves itself — proposing new agents, retiring underperformers, discovering new knowledge sources autonomously.

**Working backward from that future — what must be true?**

1. All agents accessible via API from any device (phone, laptop, desktop)
2. All scheduling runs in cloud (not dependent on any machine being on)
3. All knowledge is cloud-native (RAG, memory, embeddings queryable from anywhere)
4. Inference is cost-optimized (open-source for bulk, Claude for critical only)
5. Self-improvement loops run autonomously (scraping, learning, evolving)
6. Communication is proactive (briefs delivered, not pulled)
7. Goal tracking is real-time (Mike sees velocity without asking)
8. The system is antifragile (one component down ≠ whole system down)

---

## 6 Lens Analysis

### Lens 1: User (Mike as Operator)
- **Need:** Full team on phone. Briefs without asking. Work done overnight.
- **Pain today:** Mac must be on. No scheduling. No autonomous work. Credits exhausted.
- **Test:** Can Mike go 48 hours without touching his Mac and the system still works?

### Lens 2: Technology
- **Key finding:** CF Workers now runs Python (Pyodide/WASM). FastAPI supported natively.
- **Key finding:** Modal gives $30/mo free GPU credits. Enough for burst rendering.
- **Key finding:** CF Workers AI provides free inference (Llama 3.1, Mistral, BGE embeddings).
- **Key finding:** Fly.io runs always-on Python for $2.02/mo (cheapest credible option).
- **Implication:** Susan CAN run in cloud. The "must be local" assumption was wrong.

### Lens 3: Economic
- **Budget reality:** Best first, optimize later. Mike is willing to invest to get it right.
- **Cost ceiling:** ~$150/mo acceptable during build. Target $60-90/mo at steady state.
- **ROI frame:** If Jake completes 10 tasks/night × 30 nights = 300 tasks/mo. At $150/mo = $0.50/task. A human VA costs $15-25/hr.

### Lens 4: Competitive
- **Miessler's PAI v4.0.3:** "System Over Intelligence" — scaffolding matters more than the model.
- **Others building PAI:** Most are prompt collections. Very few have autonomous execution.
- **Moat:** The 73-agent roster + 10,788 RAG chunks + Susan's orchestration = real capability.
- **Risk:** If Mike doesn't move to cloud, he's limited by Mac uptime.

### Lens 5: Organizational
- **Team:** Jake (orchestrator), Susan (foundry), 73 specialist agents, 12 departments
- **Authority model:** 4-tier hierarchy already defined and approved
- **Gap:** No cloud execution layer. Agents exist but can't run without Mac.
- **Need:** Cloud runtime that the agents can execute against 24/7

### Lens 6: Risk
- **Biggest risk:** Over-engineering before validating the autonomous loop works
- **Mitigation:** Start with scheduled triggers + API. Prove the loop. Then expand.
- **Data risk:** All sensitive data in Supabase (already cloud). No new exposure.
- **Vendor risk:** Cloudflare free tier = low lock-in. Fly.io = Docker = portable.

---

## Three Options

### Option A: Cloudflare-Native (Maximum Edge)

**Everything on Cloudflare. Susan reimplemented as Python Workers.**

```
┌──────────────────────────────────────────────────┐
│ CLOUDFLARE (99% of system — $0-5/mo)              │
│                                                    │
│  jake-gateway (TS Worker)   → API + routing        │
│  susan-brain (Python Worker)→ 73 agents + routing  │
│  jake-scheduler (TS Worker) → Cron triggers        │
│  CF Pages                   → Dashboard PWA        │
│  D1                         → Goals, tasks, briefs │
│  R2                         → Artifacts, archives   │
│  KV                         → Cache, config, state │
│  Workers AI                 → Free LLM inference   │
│  Durable Objects            → WebSocket, sessions  │
│  Queues                     → Async task fan-out   │
│  Vectorize                  → Embeddings (replace  │
│                               Supabase pgvector?)  │
│                                                    │
├──────────────────────────────────────────────────┤
│ MODAL ($0-30/mo — GPU burst only)                  │
│  Video rendering, image gen, heavy ML              │
│  $30/mo free credits cover casual use              │
│                                                    │
├──────────────────────────────────────────────────┤
│ CLAUDE TRIGGERS ($40-80/mo)                        │
│  8 scheduled agents (briefs, work, harvest)        │
│                                                    │
├──────────────────────────────────────────────────┤
│ SERVICES (free tiers)                              │
│  Supabase, SuperMemory, Notion, Gmail, GCal,      │
│  Firecrawl, Tavily, Resend, GitHub                 │
│                                                    │
├──────────────────────────────────────────────────┤
│ LOCAL (Mac Studio — dev workstation only)           │
│  Cursor, Claude Code, Ollama (bonus, not required) │
│  Interactive coding sessions when Mike is present   │
└──────────────────────────────────────────────────┘
```

**Pros:**
- Single vendor for 90% of infrastructure
- Everything on free tier (generous: 10M requests/mo, 100K Workers AI neurons/day)
- Sub-50ms latency globally (edge network)
- Susan lives next to Jake — no network hop between them
- CF Vectorize could replace Supabase pgvector (all-in-one)
- Python on Workers is officially supported (FastAPI, LangChain, Pydantic)

**Cons:**
- Python on Workers is beta — Pyodide has C extension limitations
- Susan's current code uses libraries that may not be Pyodide-compatible (e.g., some ML packages)
- Worker CPU time limit: 30s (free), 15min (paid) — long-running ops need Queues/DO
- Need to validate every Susan dependency works on Pyodide
- If it doesn't work, we've wasted time on the port

**Risk level:** MEDIUM-HIGH (beta technology dependency)

**Monthly cost:**
| Item | Cost |
|------|------|
| CF Workers/Pages/D1/R2/KV/AI (free tier) | $0 |
| CF Workers Paid (if needed) | $5 |
| Modal GPU burst | $0 (free credits) |
| Claude triggers | $40-80 |
| OpenRouter (DeepSeek backup) | $10-15 |
| Firecrawl Growth | $19 |
| **Total** | **$74-119** |

---

### Option B: Cloudflare + Fly.io (Battle-Tested Hybrid)

**Jake on CF edge. Susan on Fly.io as always-on Python. Proven stack.**

```
┌──────────────────────────────────────────────────┐
│ CLOUDFLARE ($0-5/mo — Edge Layer)                  │
│                                                    │
│  jake-gateway (TS Worker)   → API + smart routing  │
│  jake-scheduler (TS Worker) → Cron triggers        │
│  CF Pages                   → Dashboard PWA        │
│  D1                         → Goals, tasks, briefs │
│  R2                         → Artifacts, archives   │
│  KV                         → Cache, config, state │
│  Workers AI                 → Free LLM inference   │
│  Durable Objects            → WebSocket, sessions  │
│                                                    │
├──────────────────────────────────────────────────┤
│ FLY.IO ($5-10/mo — Susan's Brain)                  │
│                                                    │
│  susan-cloud-brain (FastAPI)                       │
│  ├── susan_core/     → Orchestrator, 73 agents     │
│  ├── control_plane/  → Authority model, dispatch   │
│  ├── rag_engine/     → Voyage AI query + ingest    │
│  ├── research_daemon/→ Harvest, gap detection      │
│  ├── self_improvement/→ TIMG, evolution, routing   │
│  ├── collective/     → Agent factory, predictor    │
│  ├── memory/         → Graph, consolidation        │
│  ├── oracle_health/  → Battlecards, signals        │
│  ├── jake_cost/      → Model router, tracker       │
│  └── mcp_server/     → Cloud MCP endpoints         │
│                                                    │
│  256MB shared CPU → auto-scale to 1GB on demand    │
│  Always-on: susan.jakestudio.ai                    │
│  Full Python 3.12 — no WASM limitations            │
│                                                    │
├──────────────────────────────────────────────────┤
│ MODAL ($0-30/mo — GPU burst)                       │
│  Video, images, heavy ML when needed               │
│                                                    │
├──────────────────────────────────────────────────┤
│ CLAUDE TRIGGERS ($40-80/mo)                        │
│  8 scheduled agents (briefs, work, harvest)        │
│                                                    │
├──────────────────────────────────────────────────┤
│ SERVICES (free tiers)                              │
│  Supabase, SuperMemory, Notion, Gmail, GCal,      │
│  Firecrawl, Tavily, Resend, GitHub                 │
│                                                    │
├──────────────────────────────────────────────────┤
│ LOCAL (Mac Studio — dev workstation only)           │
│  Cursor, Claude Code, Ollama (bonus $0 inference)  │
│  Interactive coding when Mike is present            │
│  CF Tunnel for optional local GPU passthrough       │
└──────────────────────────────────────────────────┘
```

**Pros:**
- Fly.io is proven, battle-tested, Docker-based ($2.02-$5.92/mo)
- Full Python 3.12 — zero compatibility concerns
- Susan's existing code deploys with minimal changes (add FastAPI wrapper + Dockerfile)
- Jake on CF edge = fast global routing
- Susan on Fly = full compute, no WASM limits
- If Fly.io dies, move Docker image anywhere (Railway, Render, any VPS)
- Can run Susan's existing MCP server in cloud too

**Cons:**
- Two vendors (CF + Fly) instead of one
- Network hop between Jake (CF edge) and Susan (Fly DFW) — adds ~20-50ms
- Fly.io free tier deprecated for new accounts — must pay from day 1
- Need to manage Fly deployments separately from CF

**Risk level:** LOW (proven technologies, minimal code changes)

**Monthly cost:**
| Item | Cost |
|------|------|
| CF Workers/Pages/D1/R2/KV/AI (free tier) | $0 |
| Fly.io (Susan, 512MB shared CPU) | $3-6 |
| Modal GPU burst | $0 (free credits) |
| Claude triggers | $40-80 |
| OpenRouter (DeepSeek V3 + R1) | $15-20 |
| Firecrawl Growth | $19 |
| Resend | $0 |
| **Total** | **$77-125** |

---

### Option C: Full Serverless Platform (Maximum Capability)

**Everything serverless. Scale to zero. Pay only for execution. Maximum tools.**

```
┌──────────────────────────────────────────────────┐
│ CLOUDFLARE ($0-5/mo — Edge + Dashboard)            │
│                                                    │
│  jake-gateway (TS Worker)   → API + routing        │
│  CF Pages                   → Dashboard PWA        │
│  D1                         → Goals, tasks, briefs │
│  R2                         → Artifacts            │
│  KV                         → Cache, state         │
│  Workers AI                 → Free LLM inference   │
│                                                    │
├──────────────────────────────────────────────────┤
│ MODAL ($0-50/mo — Susan + GPU, Serverless)         │
│                                                    │
│  Susan (Python, scale-to-zero):                    │
│  ├── Web endpoint: susan.modal.run                 │
│  ├── All 73 agents as Modal functions              │
│  ├── RAG query/ingest as endpoints                 │
│  ├── Research daemon as scheduled Modal cron        │
│  ├── Self-improvement as scheduled cron            │
│  └── Cost: $0 when idle, ~$0.01/invocation         │
│                                                    │
│  GPU Burst (when needed):                          │
│  ├── Image generation (T4: $0.59/hr)               │
│  ├── Video rendering (A100: $2.10/hr)              │
│  ├── ML training (H100: $3.95/hr)                  │
│  └── $30/mo free credits cover casual use          │
│                                                    │
│  Scheduled Functions (replaces some Claude         │
│  triggers):                                        │
│  ├── Research harvest (Modal cron, free)            │
│  ├── Gap detection (Modal cron, free)              │
│  ├── Evolution cycle (Modal cron, free)            │
│  └── Reduces Claude trigger spend                  │
│                                                    │
├──────────────────────────────────────────────────┤
│ CLAUDE TRIGGERS ($30-60/mo — Reduced)              │
│  Only for tasks needing MCP access:                │
│  Morning brief, evening summary, goal check-in     │
│  Overnight work (needs Gmail, Notion, Firecrawl)   │
│                                                    │
├──────────────────────────────────────────────────┤
│ OPEN-SOURCE INFERENCE MESH                         │
│                                                    │
│  CF Workers AI    → Llama 3.1, Mistral ($0)        │
│  Together AI      → DeepSeek, Qwen ($0.10/M tok)  │
│  HuggingFace      → Free ZeroGPU for experiments  │
│  Replicate        → Community models on demand     │
│  Modal            → Self-hosted open-source models │
│                                                    │
├──────────────────────────────────────────────────┤
│ SERVICES (free tiers)                              │
│  Supabase, SuperMemory, Notion, Gmail, GCal,      │
│  Firecrawl, Tavily, Resend, GitHub                 │
│                                                    │
├──────────────────────────────────────────────────┤
│ LOCAL (Mac Studio — power user sessions only)       │
│  Cursor + Claude Code + Ollama                     │
│  Only used when Mike sits down to code             │
│  System does NOT depend on this being on            │
└──────────────────────────────────────────────────┘
```

**Pros:**
- Pay-per-use everywhere — $0 when idle
- GPU access when needed (Modal T4 at $0.59/hr, free credits)
- Modal's Python-native design: no Docker, decorators on functions
- Can self-host open-source models on Modal (Llama, Mistral, DeepSeek)
- Modal crons replace some Claude triggers → saves $10-20/mo
- Maximum flexibility — can add new compute instantly
- HuggingFace ZeroGPU for free experimentation
- Most scalable — handles 10x traffic without config changes

**Cons:**
- Cold starts (1-5s for CPU, 10-30s for GPU containers)
- More complex architecture (CF + Modal + Claude triggers)
- Modal's free tier may not cover if usage spikes
- Susan as Modal functions = requires refactoring into decorated functions
- More vendor surface area than Option A or B
- Cold start kills real-time dashboard feel

**Risk level:** MEDIUM (refactoring needed, cold start UX concern)

**Monthly cost:**
| Item | Cost |
|------|------|
| CF Workers/Pages/D1/R2/KV/AI | $0 |
| Modal (Susan serverless + GPU) | $0-30 (free credits) |
| Claude triggers (reduced: 4-5/day) | $30-60 |
| Together AI / OpenRouter | $10-15 |
| Firecrawl Growth | $19 |
| **Total** | **$59-124** |

---

## Option Comparison Matrix

| Dimension | A: CF-Native | B: CF+Fly | C: Full Serverless |
|-----------|-------------|-----------|-------------------|
| **Cloud coverage** | 99% | 95% | 98% |
| **Monthly cost (build)** | $74-119 | $77-125 | $59-124 |
| **Monthly cost (steady)** | $50-80 | $60-90 | $40-80 |
| **Code changes needed** | HIGH (port to Pyodide) | LOW (add FastAPI + Docker) | MEDIUM (Modal decorators) |
| **Time to deploy** | 3-4 sessions | 2-3 sessions | 3-4 sessions |
| **Risk** | Medium-High | Low | Medium |
| **Latency** | Best (all edge) | Good (20-50ms hop) | Variable (cold starts) |
| **GPU access** | Modal burst | Modal burst | Native Modal |
| **Python compat** | Limited (WASM) | Full | Full |
| **Portability** | CF lock-in | Docker portable | Modal lock-in |
| **Antifragility** | Medium | High | Medium |
| **Phone access** | Full | Full | Full |
| **Mac independence** | 100% | 100% | 100% |

---

## Jake's Recommendation: Option B (CF + Fly.io), Then Migrate to A

**Why B first:**
1. **Fastest to production** — Susan's existing Python deploys to Fly.io with 3 file changes (Dockerfile, fly.toml, api.py wrapper). No rewriting.
2. **Zero compatibility risk** — Full Python 3.12, all libraries work. No WASM surprises.
3. **Cheapest to start** — $77-125/mo, drops to $60-90 once optimized.
4. **Portable** — Docker image runs anywhere if Fly.io becomes a problem.
5. **Proven at scale** — Fly.io serves millions of requests/day for companies much larger.

**Then migrate to A when:**
- CF Python Workers exits beta (stable, full library support)
- CF Vectorize replaces Supabase pgvector (one less vendor)
- We've validated the autonomous loop works (don't change infra AND behavior simultaneously)

**Option C as supplement:**
- Add Modal for GPU burst (image gen, video rendering) regardless of A or B
- Add Modal crons for scheduled Python jobs that don't need MCP
- Use together with B, not instead of

---

## Implementation Plan (Option B, Then Evolve)

### Session 1: Susan Goes Cloud (~3 hrs)

**1.1 Create Susan FastAPI Cloud Wrapper**
```
File: susan-team-architect/backend/api.py
Purpose: Expose all 73 agents as REST endpoints
Endpoints: /health, /route, /foundry, /agents, /rag/query, /rag/ingest,
           /research/harvest, /research/gaps, /oracle/status,
           /oracle/battlecard/:competitor, /memory/stats,
           /evolve/propose, /cost/report
```

**1.2 Create Dockerfile**
```
File: susan-team-architect/backend/Dockerfile
Base: python:3.12-slim
Deps: requirements.txt (existing)
CMD: uvicorn api:app --host 0.0.0.0 --port 8080
```

**1.3 Create fly.toml**
```
App: susan-cloud-brain
Region: dfw (closest to Mike)
VM: shared-cpu-1x, 512MB
Auto-scale: stop when idle, start on request
Min machines: 1 (always-on)
```

**1.4 Deploy + Set Secrets**
```bash
fly launch --name susan-cloud-brain --region dfw
fly secrets set ANTHROPIC_API_KEY=xxx VOYAGE_API_KEY=xxx \
  SUPABASE_URL=xxx SUPABASE_SERVICE_KEY=xxx
fly deploy
fly certs create susan.jakestudio.ai
```

**1.5 Update Jake Gateway to Route to Susan Cloud**
```
File: infrastructure/cloudflare-worker/src/index.ts
Change: /susan/* routes → https://susan.jakestudio.ai/*
        /oracle/* routes → https://susan.jakestudio.ai/oracle/*
        /rag/* routes → https://susan.jakestudio.ai/rag/*
Add: Health check — if Susan down, return cached response from KV
```

**Exit criteria:**
- `curl https://susan.jakestudio.ai/health` → 200 OK
- `curl https://susan.jakestudio.ai/agents` → 73 agents listed
- `curl https://jake-gateway.rodgemd1.workers.dev/susan/agents` → routed to Fly.io
- Dashboard shows Susan status from cloud

---

### Session 2: Dashboard + Database (~3 hrs)

**2.1 Create D1 Database**
```bash
wrangler d1 create jake-ops
```

Schema: goals, tasks, briefs, capability_growth, scrape_queue, agent_performance, events
(Full schema from previous plan version — 7 tables)

**2.2 Deploy Dashboard to CF Pages**
```bash
cd apps/v5
# Update API endpoints to jake-gateway
npm run build
npx wrangler pages deploy .next --project-name jake-dashboard
# Custom domain
wrangler pages project add-domain jake-dashboard dashboard.jakestudio.ai
```

Add PWA manifest for phone home screen install.

**2.3 Expand Jake Gateway API**
Full REST API: /goals, /tasks, /briefs, /growth, /scrape-queue, /status, /susan/*, /ai/*

**Exit criteria:**
- Dashboard accessible at dashboard.jakestudio.ai from phone
- Can create goals and tasks via API
- Can query briefs and growth data

---

### Session 3: Autonomous Operations (~3 hrs)

**3.1 Create 8 Claude Scheduled Triggers**

| Trigger | Schedule (CT) | Purpose |
|---------|--------------|---------|
| Morning Brief | 06:00 daily | Email triage + calendar + goals + overnight report |
| Midday Update | 12:00 daily | Progress + blockers + pace check |
| Evening Summary | 20:00 daily | Day results + overnight queue |
| Overnight Worker | 01:00 daily | Execute 10-15 cloud tasks |
| Research Harvest | 03:00 daily | Scrape + ingest + grow 50%/wk |
| Goal Check-In | Mon/Thu 09:00 | Velocity + adjustments + Notion sync |
| Source Discovery | Sun 05:00 | Find new knowledge sources |
| Evolution Cycle | Sun 22:00 | Propose agent improvements |

Each trigger:
- Calls jake-gateway API for state (goals, tasks, growth)
- Calls susan.jakestudio.ai for agent work (research, analysis)
- Uses MCP tools (Gmail, GCal, Notion, Firecrawl, Tavily, Resend)
- Writes results back to D1 via jake-gateway
- Sends notifications via Resend email

**3.2 Wire Resend Email**
- Morning brief template
- Progress update template
- Goal check-in template
- Alert template (urgent items)

**3.3 Wire Telegram to CF Worker**
- Move bot logic from launchd to Worker
- Quick alerts for P0 items

**Exit criteria:**
- All 8 triggers visible via `schedule list`
- Test morning brief delivered to email
- Test overnight worker executes a sample task

---

### Session 4: Growth Engine + Open-Source Models (~3 hrs)

**4.1 Scraping Pipeline**
```
Source Discovery (Sunday) → scrape_queue
  → Research Harvest (Daily) → Firecrawl scrape
    → Workers AI relevance scoring (free)
    → Susan RAG ingest (Fly.io)
    → Supabase pgvector store
      → Growth tracking in D1
```

Target: 50% chunk growth per week.
Starting: 10,788 chunks → 16,000 (W1) → 24,000 (W2) → 54,000 (W4)

Quality gate: relevance >0.7, freshness <12 months, authority score, dedup.

**4.2 Workers AI Integration**
```toml
# wrangler.toml
[ai]
binding = "AI"
```

Free models:
- @cf/meta/llama-3.1-8b-instruct (classify, format, triage)
- @cf/mistral/mistral-7b-instruct-v0.2 (summarize, extract)
- @cf/meta/llama-3.2-11b-vision-instruct (image analysis)
- @cf/baai/bge-base-en-v1.5 (embeddings)

**4.3 Smart Model Router**
```
classify/triage → CF Workers AI ($0)
format/template → CF Workers AI ($0)
summarize      → CF Workers AI ($0)
embed          → CF Workers AI ($0) or Voyage AI
research       → DeepSeek V3 via OpenRouter ($0.14/M tok)
reasoning      → DeepSeek R1 via OpenRouter ($0.55/M tok)
code (cloud)   → Qwen 2.5 Coder via OpenRouter ($0.16/M tok)
code (local)   → Ollama qwen2.5-coder:32b ($0)
architecture   → Claude Sonnet ($3/M tok)
strategy       → Claude Opus ($15/M tok)
```

**4.4 Local Ollama Fleet** (optional, bonus speed when Mac on)
```bash
ollama pull qwen2.5-coder:32b   # 20GB, primary coding
ollama pull deepseek-r1:14b     # 9GB, local reasoning
ollama pull llama3.1:8b         # 5GB, fast tasks
ollama pull nomic-embed-text    # 274MB, local embeddings
```

**Exit criteria:**
- Research harvest trigger scrapes and ingests successfully
- Workers AI handling classify/format tasks in gateway
- Growth dashboard shows first week's numbers

---

### Session 5: Goals + Daily Rhythm (~2 hrs)

**5.1 Goal System**
- Create goals from: phone dashboard, Claude Code, Notion, email reply
- Auto-decompose: goal → tasks with executor, priority, cloud/local tag
- Velocity tracking: daily delta, weekly pace, projected completion
- Notion two-way sync via scheduled goal check-in

**5.2 Task Routing**
```
requires_gpu=0 AND requires_mike=0 → Jake cloud (overnight trigger)
requires_gpu=1 AND requires_mike=0 → Queue for Mac (CF Tunnel when online)
requires_mike=1                     → Flag in next brief
```

**5.3 Mike's Daily Rhythm**
```
06:00  📧 Morning Brief arrives (email)        — 2 min read
09:00  🖥️ Mac on → Cursor/Claude Code session  — active dev
12:00  📧 Midday Update (email)                — 1 min scan
20:00  📧 Evening Summary (email)              — 2 min review
22:00  🌙 Mac sleeps or stays on               — system works either way
01:00  🤖 Jake overnight: 10-15 tasks          — autonomous
03:00  🔬 Research harvest: scrape + ingest     — autonomous
Mon/Thu 📊 Goal Check-In (email)               — 3 min review

Total daily: ~8 minutes
Total weekly: ~70 minutes (including goal reviews)
```

**Exit criteria:**
- Can create goal from phone → auto-decomposes → tasks appear in D1
- Morning brief references goal progress
- Overnight worker picks up and completes cloud tasks

---

### Session 6: Cross-Domain Intelligence + Evolution (~2 hrs)

**6.1 Synergy Detection**
- Weekly cross-company analysis (part of evolution trigger)
- Surfaces patterns that transfer between businesses
- "You learned X in Oracle Health — apply to Alex Recruiting?"

**6.2 Knowledge Graph**
- Susan endpoint: POST /susan/graph/build
- Entity relationships across all RAG chunks
- Companies ↔ Technologies ↔ People ↔ Concepts

**6.3 Daemon API**
- GET /daemon → structured JSON about Mike's current state
- Machine-readable personal endpoint for AI-to-AI communication

**Exit criteria:**
- Evolution report includes cross-domain synergies
- Knowledge graph queryable from dashboard
- /daemon endpoint returns structured Mike profile

---

## The 50%/Week Growth Engine (Detail)

### How It Works

```
SUNDAY: Source Discovery Trigger
├── Tavily: search each domain for new content
├── Firecrawl: map discovered sites for scrapable pages
├── Score: authority × freshness × relevance
└── Queue: top 100 URLs → scrape_queue in D1

DAILY (03:00): Research Harvest Trigger
├── Pull 30 URLs from scrape_queue
├── Firecrawl: scrape each URL (full content extraction)
├── Workers AI: classify relevance (free, >0.7 threshold)
├── Susan (Fly.io): POST /rag/ingest for each chunk
│   ├── Voyage AI: generate 1024-dim embeddings
│   └── Supabase: insert to pgvector
├── D1: update capability_growth stats
└── D1: log scrape_queue completion

WEEKLY: Growth Report
├── Chunks before vs after per domain
├── Quality scores
├── Top sources
├── Domains below 50% target → increase scrape priority
└── Surfaced in Sunday evening summary
```

### Domain-Specific Source Strategy

| Domain | Priority Sources | Expected Yield |
|--------|-----------------|---------------|
| Oracle Health | Epic UserWeb, KLAS, HIMSS News, Modern Healthcare, CMS.gov, competitor engineering blogs | 200+ chunks/week |
| Fitness | PubMed Central, ACSM journals, NSCA, coaching certification materials | 150+ chunks/week |
| Recruiting | Greenhouse blog, Lever blog, SHRM, LinkedIn Talent Blog, recruiting tech reviews | 100+ chunks/week |
| Startup Intel | YC library, a16z blog, First Round Review, Lenny's, Stratechery, Not Boring | 200+ chunks/week |
| AI/ML | Arxiv digest, HuggingFace blog, Papers With Code trending, The Batch | 300+ chunks/week |
| Film | No Film School, Frame.io, StudioBinder, Filmmaker Magazine | 50+ chunks/week |
| Product Design | NN/g, Figma blog, Laws of UX, product analytics posts | 100+ chunks/week |

**Total: ~1,100+ new chunks/week minimum → easily 50%+ of current 10,788 baseline**

---

## Cost Summary (Option B)

### Build Phase (Months 1-2)
| Item | Monthly |
|------|---------|
| CF free tier (Workers, Pages, D1, R2, KV, Workers AI) | $0 |
| Fly.io (Susan, 512MB shared-cpu-1x) | $3-6 |
| Modal (GPU burst, free credits) | $0 |
| Claude scheduled triggers (8/day) | $40-80 |
| OpenRouter (DeepSeek V3+R1, Qwen) | $15-25 |
| Firecrawl Growth tier | $19 |
| Tavily (free 1000/mo) | $0 |
| Resend (free 3000/mo) | $0 |
| Supabase (free tier) | $0 |
| SuperMemory (free tier) | $0 |
| Cursor Pro (local IDE) | $20 |
| **Total** | **$97-150** |

### Steady State (Month 3+, after optimization)
| Optimization | Savings |
|-------------|---------|
| Shorter Claude trigger prompts | -$10-20 |
| More tasks to Workers AI (free) | -$5-10 |
| Firecrawl → free tier after growth plateau | -$19 |
| Ollama local when Mac on | -$5-10 |
| **Optimized Total** | **$58-91** |

---

## Success Metrics

| Metric | V16 (Month 1) | V17 (Month 2) | V20 (Month 6) |
|--------|---------------|---------------|---------------|
| Mike's daily time | < 15 min | < 10 min | < 8 min |
| Overnight tasks completed | 5/night | 10/night | 25/night |
| RAG chunk growth | 50%/week | 50%/week | Steady-state quality |
| System uptime (cloud) | 99% | 99.9% | 99.99% |
| Phone access | Dashboard + briefs | Full command center | Voice commands |
| Goals tracked | 80% | 100% | Auto-adjusted |
| Agent evolution | Manual | Weekly proposals | Semi-autonomous |
| Mac dependency | Dev only | Dev only | Optional |
| Businesses running | 1 active | 2 active | 3 active |
| Cross-domain synergies | None | Detected | Auto-applied |

---

## V16 → V20 Roadmap

| Version | Target | Key Capability |
|---------|--------|---------------|
| **V16** | Month 1 | Susan cloud, autonomous triggers, 2x daily updates |
| **V17** | Month 2 | Dashboard PWA, goal system, 50%/wk growth running |
| **V18** | Month 3 | Self-evolving agents, cross-domain intelligence |
| **V19** | Month 4 | Multi-user access, Daemon API, federated knowledge |
| **V20** | Month 6 | Full autonomy — <8 min/day, 3 businesses, self-healing |

---

## Decision Required

**Mike — which option and when do we start?**

| | A: CF-Native | B: CF+Fly (Recommended) | C: Full Serverless |
|---|---|---|---|
| Speed to production | 3-4 sessions | **2-3 sessions** | 3-4 sessions |
| Risk | Medium-High | **Low** | Medium |
| Cost (build) | $74-119 | **$97-150** | $59-124 |
| Cost (steady) | $50-80 | **$58-91** | $40-80 |
| Code changes | High | **Low** | Medium |
| Mac needed? | No | **No** | No |

**My recommendation: Start B now. Session 1 today. Susan in cloud by end of session.**
