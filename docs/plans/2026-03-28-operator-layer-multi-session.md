# V20 Operator Layer — Multi-Session, Multi-Model, 125x Speed

**Date:** 2026-03-28
**Companion to:** `2026-03-28-always-on-jake-cloudflare-plan.md`
**Status:** DRAFT — Awaiting Approval

---

## The Problem

Mike has ONE Claude Code session tied to ONE repo. One screen. One model. One conversation at a time. Everything runs through this single bottleneck. The infrastructure plan puts the team in the cloud, but the OPERATOR INTERFACE is still a single terminal window.

**What Mike actually needs:**

```
┌─────────────────────────────────────────────────────────┐
│ 5+ CONCURRENT SESSIONS — Different contexts, different   │
│ models, different price points, all running in parallel   │
│                                                           │
│  Session 1: Oracle Health (Mike's job — Sr Dir MCI)       │
│  Session 2: Founder Intelligence OS (this repo)           │
│  Session 3: Alex Recruiting (business)                    │
│  Session 4: Fitness App (business)                        │
│  Session 5: Overnight Autonomous (cloud, no human)        │
│  Session 6+: Ad-hoc research, content production          │
│                                                           │
│ Each session: right model, right cost, right interface     │
└─────────────────────────────────────────────────────────┘
```

---

## The Interface Stack — Best Tool for Each Job

### Tier 1: Command Line (Strategy, Architecture, Multi-File)

| Tool | Best For | Model | Cost | When |
|------|----------|-------|------|------|
| **Claude Code** | Architecture, planning, autonomous work, multi-file changes | Claude Opus/Sonnet | Subscription | Complex work, overnight triggers |
| **Aider** | Open-source alternative to Claude Code, works with ANY model | DeepSeek, Qwen, Claude, GPT | Free + API costs | When Claude Code credits are tight |
| **Claude Code + OpenRouter** | Claude Code with cheaper models via API key override | DeepSeek V3, Qwen 2.5 | $0.14-0.55/M tok | Bulk coding tasks |

### Tier 2: IDE (Interactive Coding, Real-Time)

| Tool | Best For | Model | Cost | When |
|------|----------|-------|------|------|
| **Cursor** | Interactive editing, autocomplete, inline changes | Claude/GPT-4/DeepSeek | $20/mo Pro | Active coding sessions |
| **Continue.dev** | Free open-source Cursor in VS Code, any model | Ollama local, OpenRouter | Free | When Cursor is rate-limited |
| **Cody (Sourcegraph)** | Code search + AI across repos, free tier | Claude/GPT | Free | Cross-repo understanding |
| **Windsurf** | Alternative AI IDE, good for exploration | Multiple | Free tier | Experimentation |

### Tier 3: Conversational (Strategy, Research, Writing)

| Tool | Best For | Model | Cost | When |
|------|----------|-------|------|------|
| **Claude Desktop** | Strategy, Susan MCP, research, writing | Claude Opus/Sonnet | Subscription | Deep thinking sessions |
| **ChatGPT** | Alternative perspective, O3 reasoning | GPT-4o/O3 | $20/mo | Second opinion |
| **Google AI Studio** | Gemini 2.5 Pro, long context (1M tokens) | Gemini 2.5 Pro | Free | Massive context analysis |
| **DeepSeek Chat** | Free reasoning model, code review | DeepSeek R1 | Free | Budget-conscious work |

### Tier 4: Phone (Monitoring, Quick Actions)

| Tool | Best For | Cost | When |
|------|----------|------|------|
| **Dashboard PWA** (CF Pages) | Goal tracking, briefs, status | Free | Anytime, anywhere |
| **Claude Mobile** | Quick questions, approvals | Subscription | On the go |
| **Notion Mobile** | Goal updates, task management | Free | Quick edits |

---

## The Multi-Session Architecture

### Current State (1x speed)
```
Mike → 1 Claude Code session → 1 repo → serial execution
```

### Target State (125x speed)
```
Mike ─┬→ Session 1 (Oracle Health)     → Claude Code + OH repo
      ├→ Session 2 (Founder Intel OS)   → Claude Code + this repo
      ├→ Session 3 (Alex Recruiting)    → Cursor + Alex repo
      ├→ Session 4 (Fitness App)        → Cursor + Fitness repo
      ├→ Session 5 (Research)           → Aider + DeepSeek (cheap)
      │
      ├→ Trigger 1 (Morning Brief)      → Claude Schedule (autonomous)
      ├→ Trigger 2 (Midday Update)      → Claude Schedule (autonomous)
      ├→ Trigger 3 (Evening Summary)    → Claude Schedule (autonomous)
      ├→ Trigger 4 (Overnight Worker)   → Claude Schedule (autonomous)
      ├→ Trigger 5 (Research Harvest)   → Claude Schedule (autonomous)
      ├→ Trigger 6 (Goal Check-In)      → Claude Schedule (autonomous)
      ├→ Trigger 7 (Source Discovery)   → Claude Schedule (autonomous)
      ├→ Trigger 8 (Evolution Cycle)    → Claude Schedule (autonomous)
      │
      ├→ Worker A (OH Scraping)         → Modal cron (Python)
      ├→ Worker B (Fitness Scraping)    → Modal cron (Python)
      ├→ Worker C (Recruiting Scraping) → Modal cron (Python)
      ├→ Worker D (AI/ML Scraping)      → Modal cron (Python)
      │
      └→ GPU (when needed)             → Modal burst (rendering)
```

**That's 5 interactive + 8 scheduled + 4 cron + GPU burst = 18+ concurrent streams**

---

## Per-Context Session Design

### Session 1: Oracle Health (Sr Dir Marketing Competitive Intelligence)

**Repo:** Separate repo or branch of this repo with OH-specific workspace
**Primary tool:** Claude Code (needs MCP access to Gmail, GCal, Notion, Firecrawl)
**Model:** Claude Sonnet (complex competitive analysis needs quality)
**Susan agents:** Oracle Health department (12 agents — Director, Monitor, Signal Analyst, Battlecard Manager, Content Positioning, Sales Enablement, Objection Handler, Persona Specialist, Herald, Sentinel)

**Dedicated workflows:**
- Competitive signal monitoring (Epic, Microsoft, AWS, Google, Meditech, Veeva)
- Battlecard generation and refresh
- Executive brief production
- HIMSS and industry event prep
- Win/loss analysis
- Sales enablement asset production

**Scheduled triggers (OH-specific):**
| Trigger | Schedule | Purpose |
|---------|----------|---------|
| OH Morning Intel | 06:30 CT | Overnight competitive signals + email triage |
| OH Signal Scan | 14:00 CT | Midday competitive scan |
| OH Weekly Digest | Fri 16:00 | Week's competitive intelligence summary |
| OH Battlecard Refresh | Sun 03:00 | Auto-refresh all battlecards with new data |

**Interface:** Claude Code for complex analysis. Dashboard for signal monitoring. Phone for quick signal review.

---

### Session 2: Founder Intelligence OS (This Repo)

**Repo:** /Users/mikerodgers/Desktop/Startup-Intelligence-OS
**Primary tool:** Claude Code (architecture, multi-file, infrastructure)
**Model:** Claude Sonnet/Opus for architecture, DeepSeek V3 for bulk tasks
**Susan agents:** Full 73-agent roster

**Dedicated workflows:**
- Infrastructure development (CF Workers, Fly.io, D1)
- Agent development and evolution
- OS kernel maintenance (.startup-os/)
- Cross-domain intelligence

**This session IS the command center.** Everything routes through here.

---

### Session 3: Alex Recruiting

**Repo:** Separate Alex Recruiting repo (to be created)
**Primary tool:** Cursor (interactive product development)
**Model:** Claude Sonnet (Cursor) + Ollama qwen2.5-coder:32b (local backup)
**Susan agents:** Growth + Strategy + Product agents

**Dedicated workflows:**
- Product development (MVP build)
- Landing page + app experience
- Outreach system
- Recruiting agent development

**Scheduled triggers:**
| Trigger | Schedule | Purpose |
|---------|----------|---------|
| Alex Market Scan | Mon/Wed/Fri 07:00 | Recruiting industry signals |
| Alex Growth Report | Fri 17:00 | Weekly metrics and next moves |

---

### Session 4: Fitness App

**Repo:** Separate Fitness App repo (to be created)
**Primary tool:** Cursor (interactive product development)
**Model:** Claude Sonnet + Ollama for coding
**Susan agents:** Science + Psychology + Product agents

**Dedicated workflows:**
- App development
- Coaching content
- Workout programming
- Research integration

**Scheduled triggers:**
| Trigger | Schedule | Purpose |
|---------|----------|---------|
| Fitness Research Digest | Tue/Thu 08:00 | New coaching/training research |
| Fitness Growth Report | Fri 17:00 | Weekly metrics |

---

### Session 5: Overnight Autonomous

**Repo:** Access to ALL repos via Claude scheduled triggers
**Primary tool:** Claude Code (scheduled, no human)
**Model:** Claude Sonnet (needs reliability for autonomous work)

**This is the "Jake works while you sleep" session.**

All 8 overnight triggers run here. Cross-repo task execution. Growth engine. Research harvest.

---

## Model Routing Strategy — Quality First, Optimize Later

### Phase 1: Best Models (Month 1-2)

| Task Category | Model | Why | Cost |
|--------------|-------|-----|------|
| Architecture + Planning | Claude Opus | Best reasoning, fewest errors | $$$ |
| Complex coding (multi-file) | Claude Sonnet | Best code quality | $$ |
| Interactive coding (IDE) | Claude Sonnet (via Cursor) | Real-time, high quality | $20/mo |
| Competitive analysis | Claude Sonnet | Nuance matters for OH work | $$ |
| Research synthesis | DeepSeek V3 | 90% of Claude quality, 5% cost | $ |
| Complex reasoning | DeepSeek R1 | Strong reasoning, very cheap | $ |
| Code review | DeepSeek V3 | Good enough for review | $ |
| Bulk formatting | CF Workers AI (Llama 3.1) | Free, adequate quality | $0 |
| Classification | CF Workers AI (Llama 3.1) | Free, good for binary tasks | $0 |
| Summarization | CF Workers AI (Mistral 7B) | Free, good summaries | $0 |
| Embeddings | Voyage AI / CF Workers AI BGE | Best quality / free fallback | $ / $0 |
| Local coding (Mac on) | Ollama qwen2.5-coder:32b | Free, fast, good quality | $0 |
| Local reasoning (Mac on) | Ollama deepseek-r1:14b | Free, good for local tasks | $0 |

### Phase 2: Optimize (Month 3+)

Move tasks DOWN the cost ladder after validating quality:
1. If DeepSeek V3 handles coding → move from Claude Sonnet for routine code
2. If Workers AI handles research → move from DeepSeek for simple queries
3. If Ollama handles most coding → reduce OpenRouter spend
4. If Aider + DeepSeek works → use instead of Claude Code for bulk sessions

**The key insight: start with Claude quality, then measure what actually needs it.**

---

## Aider: The Open-Source Multiplier

**Aider is the key to 125x speed with open-source models.**

What Aider does:
- Open-source Claude Code alternative (MIT license)
- Works with ANY model (Claude, GPT, DeepSeek, Qwen, Ollama, OpenRouter)
- Git-aware: auto-commits, understands repo structure
- Multi-file editing with diff-based changes
- Supports architect mode (one model plans, another executes)

**Aider + DeepSeek V3 = 90% of Claude Code at 5% of the cost**

```bash
# Install
pip install aider-chat

# Use with DeepSeek (cheapest quality option)
export OPENROUTER_API_KEY=xxx
aider --model openrouter/deepseek/deepseek-chat-v3-0324

# Use with Ollama (completely free)
aider --model ollama/qwen2.5-coder:32b

# Use with Claude (when quality matters)
aider --model claude-3-5-sonnet-20241022

# Architect mode: Claude plans, DeepSeek executes
aider --architect --model claude-3-5-sonnet-20241022 \
      --editor-model openrouter/deepseek/deepseek-chat-v3-0324
```

**Multi-session with Aider:**
```
Terminal 1: aider --model deepseek (Alex Recruiting repo)
Terminal 2: aider --model deepseek (Fitness App repo)
Terminal 3: aider --model ollama/qwen2.5-coder:32b (bulk refactoring)
Terminal 4: Claude Code (Founder Intel OS — complex architecture)
Terminal 5: Claude Code (Oracle Health — needs MCP)
```

**5 concurrent coding sessions. 3 of them near-free.**

---

## The Speed Architecture: How to Hit 125x

### Current: 1x
```
1 session × 1 task at a time × 1 model = 1x throughput
```

### Target: 125x
```
Throughput = Interactive Sessions × Scheduled Triggers × Background Workers × Parallelism

Interactive: 5 sessions × ~3 tasks/hr = 15 tasks/hr
Scheduled:   8 triggers × ~10 tasks/trigger = 80 tasks/day
Background:  4 cron workers × ~20 tasks/day = 80 tasks/day
Overnight:   1 worker × ~15 tasks/night = 15 tasks/night

Daily throughput: (15 × 8 work hrs) + 80 + 80 + 15 = 295 tasks/day
Current:     ~2-3 tasks/day (manual, serial)

295 / 2.5 = ~125x improvement
```

### How the Sessions Parallelize

**Morning (06:00-09:00):**
- Automated: Morning brief delivered, overnight report ready
- Mike: Read briefs on phone (5 min), approve/flag items

**Work Block 1 (09:00-12:00):**
- Session 1 (Oracle Health): Claude Code — battlecard refresh, competitive analysis
- Session 3 (Alex Recruiting): Cursor — product development
- Background: Research harvest running, scrape queue processing
- Susan: Processing research daemon tasks on Fly.io

**Lunch + Midday (12:00-13:00):**
- Automated: Midday update delivered
- Mike: Quick scan (2 min)

**Work Block 2 (13:00-17:00):**
- Session 2 (Founder Intel OS): Claude Code — infrastructure, agent development
- Session 4 (Fitness App): Cursor — app development
- Session 5 (Research): Aider + DeepSeek — bulk research synthesis
- Background: All cron workers running

**Evening (17:00-22:00):**
- Automated: Evening summary delivered
- Mike: Review (3 min), approve overnight queue
- Optional: Light work on phone via dashboard

**Overnight (22:00-06:00):**
- All 8 scheduled triggers execute
- Overnight worker: 10-15 cloud tasks
- Research harvest: scrape + ingest
- Source discovery (Sunday)
- Evolution cycle (Sunday)

---

## Team Screens — Who Sees What

### Mike (Full Access — All Screens)
- Dashboard: Full command center (all businesses, all goals, all agents)
- Claude Code: Any session, any repo
- Phone: Full dashboard + briefs

### Oracle Health Team View (If Shared)
- Dashboard: OH signals, battlecards, competitive landscape only
- No access to: personal goals, other businesses, financial data
- Read-only: competitive signals and battlecard library

### Business Advisor View (If Shared)
- Dashboard: Goal progress, financial metrics, milestone tracking
- No access to: code, infrastructure, agent internals

### Implementation:
```
CF Pages Dashboard supports role-based views:
  /dashboard           → Mike's full view
  /dashboard/oracle    → Oracle Health team view
  /dashboard/advisor   → Advisor/investor view
  /dashboard/public    → Public metrics only
```

Auth via Supabase Auth (email + magic link, or CF Access for team).

---

## True V10/V15 PAI in the Cloud

### Can we build multiple concurrent PAI instances?

**YES.** With the cloud architecture (Option B), each "business" becomes its own PAI context:

```
jake-gateway.rodgemd1.workers.dev
├── /oracle-health/*   → OH-specific agents, data, goals
├── /alex-recruiting/* → Alex-specific agents, data, goals
├── /fitness-app/*     → Fitness-specific agents, data, goals
├── /founder-os/*      → OS-level agents, cross-domain
└── /mike/*            → Personal goals, unified view
```

Each context has:
- Its own Susan agent subset (filtered from 73)
- Its own RAG namespace in Supabase (company_id filter)
- Its own goals and tasks in D1
- Its own scheduled triggers
- Its own growth targets

But they ALL share:
- The same infrastructure (CF + Fly.io + Supabase)
- The same model routing (cheapest capable model)
- Cross-domain intelligence (synergies detected between contexts)
- Unified Mike dashboard (all businesses on one screen)

**This IS the PAI vision — multiple concurrent intelligence streams, one operator.**

---

## Dedicated Session Triggers Per Business

### Oracle Health (Mike's Job)
| Trigger | Schedule | Model | Purpose |
|---------|----------|-------|---------|
| OH Morning Intel | 06:30 CT daily | Claude Sonnet | Competitive signals + email triage |
| OH Signal Scan | 14:00 CT daily | DeepSeek V3 | Midday competitive scan |
| OH Battlecard Refresh | Sun 03:00 CT | Claude Sonnet | Auto-refresh all battlecards |
| OH Weekly Digest | Fri 16:00 CT | Claude Sonnet | Weekly CI summary for leadership |

### Alex Recruiting
| Trigger | Schedule | Model | Purpose |
|---------|----------|-------|---------|
| Alex Market Scan | Mon/Wed/Fri 07:00 | DeepSeek V3 | Recruiting industry signals |
| Alex Growth Report | Fri 17:00 | DeepSeek V3 | Weekly metrics |

### Fitness App
| Trigger | Schedule | Model | Purpose |
|---------|----------|-------|---------|
| Fitness Research | Tue/Thu 08:00 | DeepSeek V3 | New coaching/training research |
| Fitness Growth | Fri 17:00 | DeepSeek V3 | Weekly metrics |

### Cross-Domain (Founder Intelligence OS)
| Trigger | Schedule | Model | Purpose |
|---------|----------|-------|---------|
| Morning Brief | 06:00 CT daily | Claude Sonnet | Unified brief across all |
| Midday Update | 12:00 CT daily | Claude Sonnet | Progress across all |
| Evening Summary | 20:00 CT daily | Claude Sonnet | Day results across all |
| Overnight Worker | 01:00 CT daily | Claude Sonnet | Execute queued tasks |
| Research Harvest | 03:00 CT daily | Claude Sonnet | Scrape + ingest |
| Goal Check-In | Mon/Thu 09:00 | Claude Sonnet | Velocity review |
| Source Discovery | Sun 05:00 | DeepSeek V3 | Find new sources |
| Evolution Cycle | Sun 22:00 | Claude Sonnet | Propose improvements |

**Total: 18 scheduled triggers across all contexts**

---

## Cost Model — Full Multi-Session Stack

### Monthly Investment (Quality First)

| Category | Item | Cost |
|----------|------|------|
| **Infrastructure** | CF free tier | $0 |
| | Fly.io (Susan) | $5-10 |
| | Modal (GPU burst) | $0-30 |
| **Models (Cloud)** | Claude scheduled triggers (18/day) | $60-120 |
| | OpenRouter (DeepSeek V3+R1, Qwen) | $20-35 |
| **Models (Local)** | Ollama (4 models) | $0 |
| **Tools** | Claude Code subscription | Existing |
| | Cursor Pro | $20 |
| | Aider (open-source) | $0 |
| **Services** | Firecrawl Growth | $19 |
| | Tavily, Resend, SuperMemory | $0 |
| | Supabase | $0 |
| **Total** | | **$124-234** |

### After Optimization (Month 3+)

| Optimization | Savings |
|-------------|---------|
| Move OH triggers to DeepSeek where quality allows | -$15-25 |
| More Aider sessions, fewer Claude Code | -$10-20 |
| Shorter trigger prompts | -$10-20 |
| Workers AI for more tasks | -$5-10 |
| Firecrawl to free after plateau | -$19 |
| **Optimized Total** | **$65-140** |

---

## Implementation Additions (To Cloud Plan)

### Add to Session 1: Set Up Aider
```bash
pip install aider-chat
# Configure with OpenRouter
echo "OPENROUTER_API_KEY=xxx" >> ~/.hermes/.env
# Test with DeepSeek
aider --model openrouter/deepseek/deepseek-chat-v3-0324
```

### Add to Session 2: Create Per-Business Triggers
- Add OH-specific triggers (4 triggers)
- Add Alex triggers (2 triggers)
- Add Fitness triggers (2 triggers)
- Total: 18 triggers instead of 8

### Add to Session 3: Multi-Repo Setup
```bash
# Create business-specific repos (or worktrees)
mkdir -p ~/Desktop/Oracle-Health-Intelligence
mkdir -p ~/Desktop/Alex-Recruiting
mkdir -p ~/Desktop/Fitness-App

# Each gets its own CLAUDE.md with context
# Each gets Susan bootstrap via /susan-bootstrap
```

### Add to Session 5: Role-Based Dashboard
- Add auth layer (Supabase Auth or CF Access)
- Create role-based views (/oracle, /advisor, /public)
- Test phone access with PWA install

---

## Decision Required

Mike — the cloud plan (Option B) plus this operator layer gives you:

1. **5+ concurrent interactive sessions** (Claude Code, Cursor, Aider)
2. **18 scheduled triggers** (autonomous work per business + cross-domain)
3. **50%/week growth** across all domains
4. **Full phone access** via PWA dashboard
5. **Role-based team views** if you share with others
6. **125x throughput** vs current single-session approach
7. **Open-source models** handling 80%+ of inference

**Total investment: $124-234/mo (quality first) → $65-140/mo (optimized)**

**Shall we start Session 1 now?** Susan goes cloud. Aider gets installed. First triggers get created.
