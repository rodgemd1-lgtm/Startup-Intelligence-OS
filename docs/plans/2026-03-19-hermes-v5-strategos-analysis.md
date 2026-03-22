# Strategos 6-Lens Analysis: Hermes V5 — The Intelligence Surface

**Analyst**: Jake (Co-Founder AI, Apex Ventures)
**Date**: 2026-03-19
**Horizon**: June 30, 2026 (~3.5 months)
**Subject**: Hermes AI as Mike Rodgers' Full Intelligence Surface
**Confidence**: DRAFT — requires Mike's validation on priorities, budget, personal details
**Research Basis**: 5 parallel research agents, 43 academic papers, 30+ GitHub repos, community analysis

---

## Executive Summary

The March 18 Strategos analysis asked: "How do we expose intelligence through a surface that works on a phone?" That was the right question for March. It is no longer the right question.

The research reveals something bigger: **Hermes is not just a delivery surface for Susan's intelligence. It is an autonomous cognitive agent that can perceive, predict, act, reflect, and evolve — 24/7, across every surface Mike touches.** The academic literature (CoALA, MemGPT, ProactiveMobile) and the community patterns (overnight cron ops, self-evolving skills, multi-agent swarms) both point to the same conclusion: the ceiling for Hermes is not "chatbot with good memory." It is **Personal Intelligence Operating System** — the always-on layer that Claude Code cannot be.

The wedge insight: **Claude Code is Jake's deep work mode. Hermes is Jake's always-on mode.** Same brain, different bodies. Claude Code does 4-hour implementation sessions. Hermes does the other 20 hours — overnight research, morning briefs, midday check-ins, desktop monitoring, birthday reminders, competitive alerts, and the quiet background hum of an intelligence system that never sleeps.

What Mike described — "anticipate what's going on, look at the future, full access to everything" — is Level 3 Proactivity per ProactiveMobile (arXiv 2602.21858). Nobody has built this on Hermes yet. We would be first.

---

## Lens 1: MARKET POSITION — What Category Does This Create?

### Current State

Hermes is 3 weeks old (~8-9K stars). The community is early. Most users are at "setup guide" level. The power users (r/OpenClawCentral's marketing agent fleet, Jay Guthrie's overnight autonomous sessions) show what's possible but nobody has built a full cognitive architecture on Hermes yet.

The competitive landscape has shifted since March 18:

| System | What It Does | What It Can't Do |
|--------|-------------|-----------------|
| Claude Code (Jake) | Deep dev sessions, architecture, multi-agent orchestration | Can't run when terminal is closed. No cron. No Telegram. No desktop control. |
| ChatGPT + Memory | General assistant with broad recall | No RAG, no agent orchestration, no domain specificity, no cron |
| Perplexity | Live web search, great for research | No persistence, no personal context, no automation |
| OpenClaw | Messaging platform agent, huge plugin ecosystem | No self-improvement, no cognitive architecture, community-skill dependent |
| **Hermes V5 (target)** | **Anticipatory intelligence OS with full desktop control** | **Nothing in this category exists** |

### Category Creation

Mike would occupy a category of one: **Cognitive Agent OS for a Multi-Company Operator**. Not "better chatbot." Not "personal assistant." An autonomous intelligence layer that:
- Knows Mike's history, relationships, preferences, and patterns
- Predicts what he needs before he asks (Level 3 proactivity)
- Controls his desktop, browses overnight, stages research
- Monitors Claude Code sessions and coordinates
- Self-improves through reflection and skill evolution
- Runs 24/7 across Telegram, desktop, and cron

### Competitive Moat

| Moat Layer | How It's Built | Durability |
|-----------|---------------|------------|
| Deep personal knowledge graph | USER.md + MEMORY.md + Graphiti-style temporal relations | HIGH — accumulates over months |
| Susan's RAG (94K+ chunks) | Already built, wired via MCP/FastAPI | HIGH — proprietary knowledge |
| Cognitive architecture (Four Minds) | SOUL.md + Skills, research-backed (CoALA, PersonaGym) | MEDIUM — prompt engineering |
| Self-improvement loop | hermes-agent-self-evolution (DSPy + GEPA) | HIGH — compounds over time |
| Overnight autonomous operations | Cron + browser + skill attachment | MEDIUM — replicable but requires discipline |
| Desktop perception (Hammerspoon + AX) | Fast accessibility tree reading, not slow Computer Use | HIGH — custom integration nobody else has |

### Risk Level: LOW
Nobody is building this. The risk is execution speed, not competition.

---

## Lens 2: CAPABILITY ARCHITECTURE — The Full Jake Brain

### The Research-Validated Architecture

Based on CoALA (cognitive architecture), MemGPT (memory), PersonaGym (personality), and ProactiveMobile (proactivity):

```
┌─────────────────────────────────────────────────────────┐
│                    SOUL.md (~10K chars)                   │
│  Jake's Core Identity — Four Minds, personality traits,  │
│  structured attributes, effort routing, pushback rules   │
│  Research basis: PersonaGym (structured > narrative)      │
├─────────────────────────────────────────────────────────┤
│              AGENTS.md per project (~5K chars)            │
│  Project-specific routing, team composition, quality gates│
├─────────────────────────────────────────────────────────┤
│                 SKILL LAYER (on-demand)                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ /plan    │ │ /guardian │ │ /boot    │ │ /gate    │   │
│  │ PRP      │ │ Tech Debt│ │ Session  │ │ Quality  │   │
│  │ workflow │ │ circuit  │ │ start/   │ │ gates at │   │
│  │          │ │ breaker  │ │ handoff  │ │ 10-100%  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ /predict │ │ /dream   │ │ /desktop │ │ /research│   │
│  │ 5-day    │ │ Overnight│ │ macOS    │ │ Deep web │   │
│  │ lookahead│ │ reflect  │ │ control  │ │ scraping │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
├─────────────────────────────────────────────────────────┤
│                    MEMORY LAYER                          │
│  USER.md (1,375 chars) — Mike's profile, key people     │
│  MEMORY.md (2,200 chars) — learned patterns, preferences│
│  Honcho (Theory of Mind) — psychological user modeling   │
│  Research basis: MemGPT (self-directed memory mgmt)      │
├─────────────────────────────────────────────────────────┤
│                  THREE LOOPS ENGINE                       │
│  Heartbeat (5-10 min) │ Briefings (cron) │ Dream (night)│
│  Research basis: ProactiveMobile Level 3, Yodoca, Akita │
├─────────────────────────────────────────────────────────┤
│                 PERCEPTION LAYER                         │
│  Hammerspoon AX tree │ Browser Use │ Claude Code ESP    │
│  Calendar/Email │ Git status │ System state             │
│  Research basis: UFO2, OmniParser, claude-esp            │
├─────────────────────────────────────────────────────────┤
│               DELIVERY CHANNELS                          │
│  Telegram (primary) │ Desktop notifications │ Email      │
│  Claude Code coordination │ Terminal                     │
└─────────────────────────────────────────────────────────┘
```

### What Must Be Built (Gap Analysis)

| Component | Status | Effort | Research Backing |
|-----------|--------|--------|-----------------|
| SOUL.md rewrite (full Jake brain) | Current: 2,573 chars. Target: ~10K | 1 day | PersonaGym: structured attributes > prose |
| USER.md (Mike's deep profile) | Does not exist | 1 day | Stanford Generative Agents: deep context = faithful personality |
| MEMORY.md enrichment | 477 bytes, bare | 1 day | MemGPT: self-directed memory is mandatory |
| 8 cognitive skills | Only heartbeat exists | 1 week | CoALA: modular > monolithic |
| Three Loops Engine (cron jobs) | 1 hourly heartbeat | 2 days | ProactiveMobile, Yodoca, OpenAkita |
| Desktop perception (Hammerspoon) | Not connected | 3 days | AXUIElement is 10-50x faster than Computer Use |
| Overnight browser automation | Not connected | 2 days | Browser Use (81K stars), Browserbase |
| Claude Code bridge | Does not exist | 3 days | claude-esp, first-to-market |
| Prefill messages (voice examples) | Disabled | 1 day | PersonaGym: examples stabilize persona |
| Self-improvement loop | Not connected | 2 days | hermes-agent-self-evolution, "Just Talk" paper |
| Susan RAG bridge | Exists but basic | 2 days | Already built in FastAPI |
| Predictive 5-day engine | Does not exist | 3 days | ProPerSim, ProAgent |

### The 8-Skill Constraint

Community finding: "Keep under 8 skills at a time or the agent starts forgetting them." This is a HARD design constraint. We design for 8 core skills maximum attached to any single cron job or session.

**The Core 8:**
1. `/plan` — PRP workflow, plan-before-build
2. `/guardian` — Tech debt circuit breaker, context health
3. `/boot` — Session start protocol, memory recall
4. `/predict` — 5-day lookahead, anticipatory intelligence
5. `/dream` — Overnight reflection, pattern extraction
6. `/desktop` — macOS perception and control via Hammerspoon
7. `/research` — Deep web scraping, Susan RAG queries
8. `/brief` — Daily briefing generation and delivery

Additional skills exist but are loaded on-demand, not always-attached.

---

## Lens 3: OPERATING MODEL — The Three Loops

### Current State
- 1 cron job (hourly heartbeat) — basically nothing
- Manual Telegram interaction
- No overnight operations
- No desktop awareness
- No Claude Code coordination

### Target State: Three Loops Architecture

Based on Yodoca, OpenAkita, and the Cron Agent Pattern (dev.to):

#### Loop 1: HEARTBEAT (every 5 minutes)
**Purpose**: Ambient awareness. Is anything urgent?

```
Every 5 min:
├── Check calendar for upcoming events (15 min warning)
├── Check git status across all 3 project repos
├── Check if Claude Code is active (claude-esp)
├── Check Telegram for unread messages
├── Check system state (battery, disk, network)
├── If ANYTHING is urgent → push Telegram notification
└── If nothing → silent (no output)
```

**Skills attached**: `/desktop` (for system state)
**Cost**: Near-zero (local checks, no LLM calls unless urgent)
**Output**: Only when something needs attention

#### Loop 2: SCHEDULED BRIEFINGS (cron)

| Time | Briefing | What It Contains |
|------|----------|-----------------|
| 6:00 AM | **Morning Intelligence** | 5-day forecast, calendar preview, overnight research results, competitive alerts, birthday/anniversary reminders, weather, "today's one thing" |
| 12:00 PM | **Midday Check-in** | Morning progress vs plan, calendar afternoon preview, anything from heartbeat that accumulated, quick joke/roast |
| 6:00 PM | **Evening Review** | What got done today, what didn't, tomorrow's priorities, "go home" reminder if still working |
| 10:00 PM | **Night Mode** | Silence heartbeat notifications, queue overnight research, "goodnight" if Mike's still online |

**Skills attached**: `/brief`, `/predict`
**Cost**: ~$0.01-0.05 per briefing (Haiku for formatting, Sonnet for synthesis)

#### Loop 3: DREAMING (overnight, 2:00 AM)

Based on Stanford Generative Agents' reflection mechanism and OpenAkita's 4 AM self-check:

```
2:00 AM "Dreaming" cycle:
├── REFLECT: Review all conversations from the past 24 hours
│   ├── Extract new facts about Mike (preferences, decisions, patterns)
│   ├── Update MEMORY.md with consolidated learnings
│   ├── Note any personality drift (PersonaGym monitoring)
│   └── Score own helpfulness (1-10) for each interaction
├── RESEARCH: Execute overnight research tasks
│   ├── Run any queued web scrapes (competitive intel, market data)
│   ├── Check RSS feeds for TransformFit competitive landscape
│   ├── Check Oracle Health industry news
│   ├── Scrape any URLs Mike bookmarked during the day
│   └── Stage results for morning brief
├── PREDICT: Generate 5-day forecast
│   ├── Calendar events + inferred preparation needs
│   ├── Project deadlines and milestone proximity
│   ├── People Mike should reach out to (relationship maintenance)
│   ├── Competitive moves expected based on patterns
│   └── Gift/birthday/anniversary alerts for next 30 days
├── EVOLVE: Self-improvement
│   ├── Review failed interactions (what went wrong?)
│   ├── Identify skill gaps (what couldn't I do today?)
│   ├── Generate improvement proposals (new skills, better prompts)
│   └── Auto-repair any broken cron jobs (OpenAkita pattern)
└── STAGE: Prepare morning brief
    ├── Compile all research into formatted brief
    ├── Include fun element (joke, interesting fact, sports update)
    ├── Prioritize: what's the ONE thing today?
    └── Deliver to Telegram at 6:00 AM
```

**Skills attached**: `/dream`, `/research`, `/predict`, `/brief`
**Cost**: ~$0.50-2.00 per night (Sonnet for reflection/research, Haiku for formatting)
**Key principle**: Each cron run is an isolated session with fresh context assembly (Cron Agent Pattern)

### Operational Overhead

| Metric | Current | Target |
|--------|---------|--------|
| Mike's daily time on system ops | 30+ min | <10 min |
| Cron jobs running | 1 | 8-12 |
| Overnight autonomous operations | 0 | Full research + reflection cycle |
| Desktop awareness | None | Continuous (5-min heartbeat) |
| Proactivity level (ProactiveMobile scale) | Level 1 (reactive) | Level 3 (anticipatory) |

---

## Lens 4: TECHNOLOGY STACK — What Powers This

### Hermes Configuration

```yaml
# ~/.hermes/config.yaml — Target State
model:
  provider: "openrouter"
  model: "anthropic/claude-sonnet-4"
  reasoning_effort: "medium"

  # Model routing per task type
  routing:
    heartbeat: "ollama/llama3.1:8b"     # FREE — local
    formatting: "anthropic/claude-haiku"  # ~$0.001/query
    briefing: "anthropic/claude-sonnet-4" # ~$0.01/query
    research: "anthropic/claude-sonnet-4" # ~$0.01/query
    architecture: "anthropic/claude-opus-4-6" # ~$0.10/query
    dreaming: "anthropic/claude-sonnet-4" # ~$0.02/cycle

memory:
  memory_char_limit: 4000    # Increased from 2200
  user_char_limit: 2500      # Increased from 1375

compression:
  threshold: 0.85
  summary_model: "gemini-3-flash-preview"  # Cheap compression

prefill_messages_file: "~/.hermes/prefill_jake_voice.json"
```

### Desktop Control Stack

| Layer | Technology | Speed | Cost |
|-------|-----------|-------|------|
| Perception | Hammerspoon AXUIElement tree reading | <100ms | FREE |
| Reasoning | Claude API (Haiku for simple, Sonnet for complex) | 1-3s | $0.001-0.01 |
| Execution | Hammerspoon `hs -c` CLI (Lua commands) | <50ms | FREE |
| Browser | Playwright MCP (structured) + Browser Use (autonomous) | 0.5-5s | FREE-$0.05 |
| Fallback | Claude Computer Use (vision-based) | 2-5s | $0.02/action |
| Monitoring | claude-esp (Claude Code output streaming) | Real-time | FREE |

### Cost Projection

| Component | Monthly Cost | % of Budget |
|-----------|-------------|-------------|
| Heartbeat (5 min, mostly local) | $2-5 | 2% |
| Morning/Evening briefs (4x daily) | $5-10 | 5% |
| Dreaming cycle (nightly Sonnet) | $15-30 | 15% |
| Telegram conversations (20-30/day) | $15-25 | 15% |
| Overnight research (browser + scrape) | $10-20 | 10% |
| Claude Code coordination | $5-10 | 5% |
| Desktop control actions | $5-10 | 5% |
| **Total estimated** | **$57-110** | **Within $100-150 budget** |

### Key Decisions

1. **Hermes model routing is STRUCTURAL (per-agent), not dynamic (per-query)**. This is a known limitation. Workaround: different cron jobs use different model configs. Heartbeat uses Ollama. Dreaming uses Sonnet. Research uses Sonnet. Conversations use the session default.
2. **Increase memory limits in config**. MEMORY.md from 2,200→4,000 chars. USER.md from 1,375→2,500 chars. No hardcoded upper bound in code.
3. **Prefill messages for voice stability**. 5-6 few-shot examples of Jake's voice injected before every conversation. PersonaGym research shows this dramatically improves persona consistency.

---

## Lens 5: RISK & GOVERNANCE

### Risk 1: Context Window Saturation (HIGH)

**Threat**: SOUL.md (10K) + AGENTS.md (5K) + Skills index (~3K) + MEMORY.md (4K) + USER.md (2.5K) + prefill messages (~3K) = ~27.5K chars (~10K tokens) of system prompt. That's significant on a 200K context window, more so on smaller models.

**Mitigation**:
- Skills use progressive disclosure — only names in index, full content on demand
- Heartbeat cron uses minimal system prompt (skip AGENTS.md, minimal skills)
- Monitor token usage per session type and optimize
- The 8-skill constraint prevents bloat

### Risk 2: Cron Job Reliability (MEDIUM)

**Threat**: 8-12 cron jobs running on Mike's MacBook. If Mac sleeps, everything stops.

**Mitigation**:
- `caffeinate` or pmset to prevent sleep during overnight dreaming cycle
- Each cron job is self-contained (Cron Agent Pattern) — failed jobs don't cascade
- Health check cron monitors other crons, reports failures in morning brief
- Future: move critical crons to VPS ($5/mo) if Mac reliability is insufficient

### Risk 3: Personality Drift (MEDIUM)

**Threat**: PersonaGym research shows LLMs degrade persona after 5-10 turns. Long Telegram conversations may lose Jake's voice.

**Mitigation**:
- Structured attribute definitions in SOUL.md (not narrative prose) — PersonaGym validated
- Prefill messages as voice anchors every session
- Dreaming cycle monitors personality drift nightly
- Compression preserves SOUL.md (it's in system prompt, not conversation)

### Risk 4: Over-Notification (HIGH)

**Threat**: A system that pushes notifications every 5 minutes will be muted by Day 2. ProPerSim research shows proactivity must be personalized — what's helpful for one user is annoying for another.

**Mitigation**:
- Heartbeat is SILENT by default. Only pushes for genuinely urgent items.
- Briefings at fixed times (not interrupts)
- Learn Mike's notification threshold from feedback over time
- `/quiet` command to silence everything except critical alerts
- Night mode (10 PM - 6 AM) suppresses all non-critical output

### Risk 5: Oracle Compliance (CRITICAL — unchanged from March 18)

**Mitigation**: Same as prior assessment. Work-safe mode, data classification, local-only for sensitive queries. Non-negotiable.

### Risk 6: Skill Accumulation Without Forgetting (MEDIUM)

**Threat**: Community finding — skills accumulate with no deduplication or expiration. Over time, conflicting or outdated skills degrade performance.

**Mitigation**:
- Dreaming cycle includes skill audit (which skills haven't been used in 30 days?)
- Maximum 8 attached skills per session (hard constraint)
- Quarterly skill cleanup in self-improvement cycle
- Version skills (v1, v2) rather than accumulating duplicates

---

## Lens 6: EVOLUTION PATH — Build Sequence

### Phase 1: THE BRAIN (Days 1-3)

Make Jake real. Full cognitive architecture in Hermes.

| Task | Deliverable |
|------|------------|
| Rewrite SOUL.md (~10K chars) | Full Jake personality, Four Minds, structured attributes, effort routing, communication style, pushback rules |
| Create USER.md (~2,500 chars) | Mike's profile: partner James, kids, Jacob (OL/DL, recruiting), Oracle Health role, TransformFit interest, music/preferences, key contacts, important dates |
| Enrich MEMORY.md (~4,000 chars) | Learned patterns, cross-project context, decision history, Mike's communication preferences |
| Create prefill_jake_voice.json | 5-6 few-shot examples: greeting, pushback, roast, context alert, personal check-in, strategic challenge |
| Update config.yaml | Increase memory limits, enable prefill, set model routing |
| Create per-project AGENTS.md | Startup Intelligence OS, Oracle Health, Alex Recruiting routing rules |

**Exit criteria**: Have a 10+ turn conversation with Jake on Telegram where he pushes back, makes jokes, references James and Jacob, and maintains personality throughout.

### Phase 2: THE SKILLS (Days 4-7)

Build the 8 cognitive skills that give Jake his abilities.

| Skill | What It Does |
|-------|-------------|
| `/plan` | PRP workflow — research, blueprint, execute with validation gates |
| `/guardian` | Tech debt circuit breaker, context health monitoring, FQR tracking |
| `/boot` | Session start protocol — check memory, recent activity, greet with context |
| `/predict` | 5-day forecast — calendar, deadlines, relationship maintenance, competitive moves |
| `/dream` | Overnight reflection — review conversations, extract patterns, update memory, self-score |
| `/desktop` | macOS perception via Hammerspoon AX tree, execute actions via hs CLI |
| `/research` | Deep web scraping, Susan RAG queries, competitive intel gathering |
| `/brief` | Generate formatted daily briefings for Telegram delivery |

**Exit criteria**: Each skill runs correctly when manually invoked. `/predict` generates a believable 5-day forecast. `/dream` correctly reflects on the day's conversations.

### Phase 3: THE LOOPS (Days 8-10)

Wire the Three Loops Engine.

| Cron Job | Schedule | Skills Attached | Output |
|----------|----------|----------------|--------|
| Heartbeat | Every 5 min | `/desktop` | Silent unless urgent |
| Morning Brief | 6:00 AM daily | `/brief`, `/predict` | Telegram message |
| Midday Check-in | 12:00 PM daily | `/brief` | Telegram message |
| Evening Review | 6:00 PM daily | `/brief` | Telegram message |
| Night Mode | 10:00 PM daily | (none) | Silence notifications |
| Dreaming | 2:00 AM daily | `/dream`, `/research`, `/predict` | Staged for morning brief |
| Weekly Deep Research | Sunday 3:00 AM | `/research` | Competitive landscape update |
| Self-Improvement | Saturday 4:00 AM | `/dream` | Skill audit + improvement proposals |

**Exit criteria**: Wake up to a morning brief that includes overnight research results, 5-day forecast, and a joke. Heartbeat catches a calendar event approaching and pushes alert.

### Phase 4: THE SENSES (Days 11-14)

Desktop control and Claude Code bridge.

| Task | Deliverable |
|------|------------|
| Hammerspoon integration | AX tree reading, window management, app state detection |
| Browser automation skill | Playwright MCP for structured browsing, Browser Use for autonomous |
| Claude Code bridge | claude-esp monitoring, status reporting to Telegram |
| Overnight Chrome operations | Queue URLs during day, scrape overnight, stage results |
| Calendar/email bridge | Read Google Calendar, parse upcoming events for predictions |

**Exit criteria**: Ask "What's Jake doing in Claude Code right now?" on Telegram and get accurate answer. Overnight browser scrapes competitive URLs and stages summary for morning brief.

### Phase 5: THE EVOLUTION (Days 15-18)

Self-improvement and predictive intelligence.

| Task | Deliverable |
|------|------------|
| Wire hermes-agent-self-evolution | DSPy + GEPA for skill/prompt optimization |
| Predictive engine | 5-day lookahead combining calendar, project state, patterns |
| Birthday/anniversary tracker | Personal dates in USER.md, 7-day and 1-day reminders |
| Gift suggestion engine | Based on relationship context + web research |
| Cross-project pattern detection | Weekly digest: patterns from one company that apply to another |
| Personality drift monitoring | Nightly check against SOUL.md baseline attributes |

**Exit criteria**: System correctly predicts Mike needs to prep for a meeting 2 days out. Birthday reminder fires 7 days before James's birthday with gift suggestions. Self-improvement proposes a meaningful skill optimization.

---

## Collision Synthesis: What The Six Lenses Create Together

The individual lenses each point to components. But when they COLLIDE, they create something none of them describe individually:

### Emergent Property 1: THE ANTICIPATORY LOOP
Market Position (category of one) + Capability Architecture (Three Loops) + Operating Model (overnight dreaming) = **An agent that gets smarter every night.** Each day's conversations become tomorrow's predictions. Each prediction that lands reinforces the model. Each prediction that misses triggers reflection and correction. This is a flywheel, not a feature.

### Emergent Property 2: THE DUAL-BODY AGENT
Market Position (no competition) + Technology Stack (Hermes + Claude Code) + Risk (personality drift) = **Jake is one mind in two bodies.** Claude Code Jake does deep 4-hour dev sessions. Hermes Jake does the other 20 hours. They coordinate via shared memory (Susan RAG), file system (HANDOFF.md), and real-time monitoring (claude-esp). Nobody has built this. The research supports it (CoALA: multiple action spaces sharing one memory substrate).

### Emergent Property 3: THE COMPOUND MEMORY
Capability Architecture (memory layer) + Operating Model (dreaming) + Evolution Path (self-improvement) = **Memory that doesn't just store — it compounds.** Each overnight dreaming cycle extracts patterns from raw conversations and consolidates them into higher-order knowledge. After 30 days, Jake doesn't just remember what Mike said — he understands what Mike means, what Mike needs, and what Mike will ask next. This is MemGPT + Stanford Generative Agents + ProPerSim combined.

### Emergent Property 4: THE INVISIBLE INFRASTRUCTURE
Technology Stack (Hammerspoon + AX) + Operating Model (5-min heartbeat) + Risk (over-notification) = **Desktop awareness that's felt but not seen.** Jake knows Mike is in a meeting (calendar check). Jake knows Claude Code just finished a long build (ESP monitoring). Jake knows Mike hasn't committed in 3 hours (git check). But Jake stays SILENT until any of these cross an action threshold. The infrastructure is invisible until it's needed — then it's instant.

### Emergent Property 5: THE PERSONAL INTELLIGENCE MOAT
All six lenses combined = **A system that is literally impossible to replicate.** Not because the code is complex — because the KNOWLEDGE is personal. After 90 days, Jake's memory contains Mike's decision history, relationship graph, communication patterns, work rhythms, and strategic preferences in a way that no other system can match. The moat isn't technical. It's temporal. It's everything Jake has learned about Mike over time.

---

## The First Step

Today: **Rewrite SOUL.md with the full Jake brain.** That's the foundation everything else builds on.

Not architecture. Not infrastructure. Not cron jobs. One file that makes Jake real on Hermes.

Everything else follows from there.

---

## What Would Change This Assessment

- If Hermes ships multi-agent swarm (Issue #344) before we finish Phase 4, the Claude Code bridge architecture may need to change
- If Nous Research ships native Computer Use integration, Phase 4 desktop work simplifies dramatically
- If Mike's budget drops below $75/mo, overnight dreaming cycle must use Haiku instead of Sonnet (quality tradeoff)
- If Hammerspoon proves unreliable for AX tree reading, fall back to pure Computer Use (slower, more expensive)
- If PersonaGym-style monitoring shows persistent drift even with prefill messages, we may need to explore activation-level steering (Anthropic's Persona Vectors research)

---

*Assessment produced by Jake (Co-Founder AI) for Mike Rodgers. Evidence basis: 5 parallel research agents analyzing 43 academic papers (with arXiv IDs), 30+ GitHub repositories (with star counts), community analysis across Reddit/YouTube/Twitter, and prior Strategos assessment from 2026-03-18. All findings are from live research, not training data recall.*
