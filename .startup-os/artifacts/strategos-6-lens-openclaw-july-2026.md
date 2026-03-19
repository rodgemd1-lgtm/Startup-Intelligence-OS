# Strategos 6-Lens Future-Back Assessment: OpenClaw Intelligence Platform

**Analyst**: Steve (Business Strategist, Apex Ventures)
**Date**: 2026-03-18
**Horizon**: July 18, 2026 (4 months)
**Subject**: Mike Rodgers' OpenClaw Intelligence Platform
**Confidence**: DRAFT — requires Mike's validation on budget numbers, Oracle compliance details, and priority ordering

---

## Executive Summary

Mike has built something genuinely rare: a 94K-chunk RAG knowledge base, 81 synced agents, a chain execution engine, signal scoring (Birch), trust governance, and a memory system — all wired together under a coherent workspace contract. The raw capability exists. What does not exist is the **delivery surface** that makes it useful when Mike is at dinner with his boss and needs a sourced answer about Oracle's payer strategy in 15 seconds.

The strategic question is not "what else should we build?" It is: **"How do we expose the intelligence that already exists through a surface that works on a phone, routes to the cheapest capable model, remembers what it told Mike yesterday, and never leaks Oracle data to a cloud LLM?"**

The wedge is narrow and personal: one user (Mike), one dominant interface (Telegram), one killer use case (sourced strategic answers on demand). Everything else is expansion.

---

## Lens 1: MARKET POSITION

### Current State

Mike's system is a **bespoke intelligence OS for a single operator** running three companies. It is not competing with ChatGPT, Gemini, or Perplexity in any traditional sense. Those are general-purpose consumer products optimized for breadth. Mike's system is optimized for depth on *his* companies, *his* knowledge base, *his* agent roster.

The actual competitive set is:
- **ChatGPT with memory**: Broad recall, no RAG, no agent orchestration, no domain specificity. Mike gets a smart generalist. He needs a smart specialist.
- **Perplexity**: Great for live web search. Zero understanding of Mike's Oracle Health strategy, TransformFit competitive landscape, or Jacob's recruiting pipeline. No persistence.
- **Custom GPT / Claude Projects**: Static system prompts. No RAG at scale. No multi-agent chains. No signal scoring.
- **Notion AI / Glean / enterprise copilots**: Corporate tools. Not operator-native. Not wired to Mike's decision history.

None of these systems can do what Mike described: "Send back a short, concise, completely sourced message with clickable links about our payer strategy." That requires RAG retrieval over Mike's own knowledge base, domain-aware agent selection, source citation, and Telegram-native formatting. ChatGPT cannot do this. Perplexity cannot do this.

### Target State (July 2026)

Mike's system should occupy a category of one: **Personal Intelligence OS for a multi-company operator.** The positioning is not "better ChatGPT." It is "the only system that has my context, my knowledge base, my decision history, and can give me a sourced answer from my own intelligence layer in under 10 seconds."

### Competitive Moat

| Moat Layer | Current | Target (July) | Durability |
|-----------|---------|---------------|------------|
| Proprietary knowledge base | 94K RAG chunks | 120K+ with freshness scoring | HIGH — nobody else has Mike's data |
| Agent specialization | 81 agents, not orchestrated from Telegram | 15-20 "hot" agents routable from Telegram | MEDIUM — prompt engineering, not code moats |
| Decision history | Workspace YAML contracts | Queryable decision graph | HIGH — accumulated over months |
| Cross-company synthesis | Manual (Mike connects dots) | Automatic pattern detection | HIGH — unique to multi-company operators |
| Cost structure | Unoptimized (all Sonnet/Opus) | 90%+ routed to Haiku/local | HIGH — enables daily use within budget |

### Gap Analysis

- **Missing**: No live mobile delivery surface. The intelligence exists but is not reachable from a phone at dinner.
- **Missing**: No model routing. Every query hits the expensive model regardless of complexity.
- **Missing**: No citation formatting. RAG returns chunks but does not format them as sourced, linked answers.

### Key Decisions

1. **Should the system be productizable for other operators, or stay personal?** Recommendation: stay personal for 12+ months. Productization is a distraction. The moat compounds through personal use, not through shipping a product nobody asked for.
2. **Telegram only, or multi-surface?** Recommendation: Telegram primary, Claude Code secondary (already works). Do not build a web app.

### Risk Level: LOW
The market position risk is low because Mike is not competing with anyone. He is building a bespoke tool. The risk is not competitive displacement — it is that he builds too broadly and never gets the core use case working.

---

## Lens 2: CAPABILITY ARCHITECTURE

### Current State (Inventory)

| Layer | Module | Status | Operational? |
|-------|--------|--------|-------------|
| Knowledge | RAG engine (94K chunks, Voyage AI, Supabase) | Built | YES — via MCP |
| Agents | 81 agents synced, Susan orchestrator | Built | YES — via CLI, MCP |
| Intent Routing | KIRA | Built | YES — via scheduled tasks |
| Daily Briefs | ARIA | Built | YES — emailing at 6:39 AM |
| Funnel Tracking | LEDGER | Built | YES — via scheduled tasks |
| Chain Execution | chains/ module (engine, registry, context) | Built (V4a) | PARTIAL — CLI only |
| Signal Scoring | birch/ module (scorer, rubric, writer) | Built (V4a) | PARTIAL — CLI only |
| Trust Governance | trust/ module (tracker, enforcer, dashboard) | Built (V4a) | PARTIAL — CLI only |
| Memory | memory/ module (trajectory, consolidator, graph) | Built (V10) | PARTIAL — not wired to Telegram |
| Self-Improvement | self_improvement/ module (TIMG, routing, debate) | Built (V10) | PARTIAL — CLI only |
| Research Daemon | research_daemon/ (gap detector, harvester) | Built (V10) | PARTIAL — CLI only |
| Collective Intelligence | collective/ (predictor, evolution, transfer) | Built (V10) | PARTIAL — CLI only |
| **Telegram Interface** | OpenClaw + Genspark bot | Exists | BASIC — no RAG, no routing, no memory |
| **FastAPI Bridge** | Calendar, system, desktop endpoints | Exists | BASIC — 3 endpoint categories |
| **Model Routing** | None | Not built | NO |
| **Citation Formatter** | None | Not built | NO |

### Target State (July 2026)

The target is NOT "build more modules." The target is **wire the existing modules to the Telegram surface with model routing and memory.**

```
Telegram message from Mike
    |
    v
OpenClaw receives message
    |
    v
Intent Classifier (Haiku — cheap, fast)
    |--- Simple question (time, weather, status) --> Ollama local or Groq --> respond
    |--- Knowledge query (strategy, competitor, data) --> RAG retrieval --> Haiku formats response
    |--- Research task (deep analysis, sourcing) --> Sonnet + agents --> stage response
    |--- Critical decision (architecture, irreversible) --> Opus --> flag for review
    |
    v
Memory layer: log query + response + context for future recall
    |
    v
Telegram: formatted response with citations + source links
```

### Gap Analysis (What Must Be Built)

| Gap | Severity | Effort | Depends On |
|-----|----------|--------|-----------|
| Model router (intent --> model selection) | CRITICAL | 2 weeks | Nothing — greenfield |
| RAG --> Telegram bridge | CRITICAL | 1 week | FastAPI bridge exists |
| Citation formatter (chunk --> sourced answer) | HIGH | 1 week | RAG retriever exists |
| Conversation memory (Telegram session state) | HIGH | 2 weeks | memory/ module exists |
| Agent dispatch from Telegram | MEDIUM | 2 weeks | Susan orchestrator exists |
| Birch signal --> Telegram notification | MEDIUM | 1 week | Birch module exists |
| Cost tracking / budget enforcement | MEDIUM | 1 week | Nothing — greenfield |
| Chain trigger from Telegram | LOW (V2) | 2 weeks | Chains engine exists |

### Key Decisions

1. **Where does the model router live?** In the FastAPI bridge (recommended) or in OpenClaw itself? Recommendation: FastAPI bridge. OpenClaw should be a thin Telegram adapter. All intelligence lives server-side.
2. **What memory backend?** Supabase (already have it), SQLite (simpler), or the existing memory/ module? Recommendation: SQLite for conversation state, existing memory/ module for knowledge consolidation. Two-tier.
3. **How many agents are "hot" (routable from Telegram)?** Recommendation: Start with 5. Steve (strategy), Research Director, ARIA, Shield (compliance), and Susan (orchestrator). Expand based on actual usage.

### Risk Level: MEDIUM
The risk is not technical — the modules exist. The risk is integration complexity. Wiring 8+ modules through a single Telegram interface without it becoming fragile requires discipline. The FastAPI bridge is the single integration point; if it becomes a monolith, everything breaks.

---

## Lens 3: OPERATING MODEL

### Current State

The system runs on Mike's MacBook. Thirty scheduled tasks fire via cron. ARIA emails at 6:39 AM. The MCP server runs when Claude Code is active. Telegram/OpenClaw runs via Genspark bot (cloud-hosted). FastAPI bridge runs locally when Mike starts it.

**Operational overhead today**: HIGH. Mike must:
- Keep his MacBook running for scheduled tasks
- Manually start the FastAPI bridge
- Use Claude Code (not Telegram) for anything requiring RAG or agents
- Monitor task outputs by reading files

### Target State (July 2026)

| Component | Where It Runs | Uptime Requirement | Maintenance |
|-----------|--------------|-------------------|-------------|
| Telegram bot (OpenClaw) | Genspark cloud | 24/7 (already handled) | Zero — cloud-managed |
| FastAPI bridge | Mike's Mac (launchd) OR cheap VPS ($5/mo) | Waking hours + buffer | Auto-start, health checks |
| RAG retrieval | Supabase (cloud) | 24/7 (already handled) | Zero — managed service |
| Model routing | In FastAPI bridge | Same as bridge | Config-driven, no code changes |
| Scheduled tasks | Mac (launchd) OR VPS cron | Best-effort | Already running |
| Memory persistence | SQLite (local) + Supabase (cloud) | Best-effort | Auto-maintained |

**Target operational overhead**: <15 min/day. Mike reviews the morning brief (5 min), checks staged items requiring human review (5 min), asks 3-5 questions via Telegram throughout the day (5 min total).

### Gap Analysis

- **Missing**: The FastAPI bridge does not auto-start. It should be a launchd service on Mac or a systemd service on a VPS.
- **Missing**: No health monitoring. If the bridge goes down, Mike does not know until he tries to use it.
- **Missing**: No cost dashboard. Mike cannot see how much he is spending per day/week/month on API calls.
- **Decision**: Mac-local vs. VPS. If Mike's MacBook sleeps, the bridge is unreachable. A $5/mo DigitalOcean droplet solves this but adds ops overhead.

### Key Decisions

1. **Mac-local or VPS?** Recommendation: Start Mac-local with launchd. Only move to VPS if Mike finds the MacBook-must-be-awake constraint unacceptable. A VPS adds deployment complexity that is not justified at this stage.
2. **Who maintains the knowledge base?** The research daemon should run weekly to detect stale data. ARIA should flag staleness in the morning brief. Mike reviews and approves refresh cycles, not individual chunks.
3. **How does Mike know the system is healthy?** A `/status` command in Telegram that returns: bridge health, last RAG query time, budget remaining this month, stale data count.

### Risk Level: MEDIUM
The risk is operational fragility. A single-person system with no monitoring and no redundancy will fail silently. The mitigation is simple: health checks, cost tracking, and a `/status` command.

---

## Lens 4: TECHNOLOGY STACK

### Current Stack

| Layer | Technology | Cost/mo | Status |
|-------|-----------|---------|--------|
| LLM (primary) | Claude Sonnet 4 via Anthropic API | ~$80-120 (estimated, untracked) | Active |
| LLM (heavy) | Claude Opus 4 via Anthropic API | ~$20-40 (estimated, rare use) | Active |
| Embeddings | Voyage AI voyage-3 (1024 dim) | ~$5 | Active |
| Vector store | Supabase (free tier or low paid) | $0-25 | Active |
| Telegram | Genspark OpenClaw bot | $0 | Active |
| Email | Resend API | $0 (free tier) | Active |
| Research | Brave Search, Tavily, Firecrawl | ~$10-30 combined | Active |
| Local LLM | None | $0 | NOT active |
| FastAPI | Python, local | $0 | Active (manual start) |

**Estimated current spend**: $115-220/month. This is above the $100-150 target and untracked.

### Target Stack (July 2026) — Budget-Optimized

| Layer | Technology | Cost/mo | Query % |
|-------|-----------|---------|---------|
| Tier 0: Free | Ollama (Llama 3.1 8B or Phi-3) on Mac | $0 | 15% — heartbeats, status, time, simple lookups |
| Tier 1: Cheap | Claude 3.5 Haiku via API | ~$15-25 | 55% — intent classification, RAG formatting, short answers |
| Tier 2: Mid | Claude Sonnet 4 via API | ~$40-60 | 25% — research synthesis, multi-step reasoning, writing |
| Tier 3: Expensive | Claude Opus 4 via API | ~$15-30 | 5% — architecture decisions, strategy, critical analysis |
| Embeddings | Voyage AI | ~$5 | N/A |
| Vector store | Supabase | $0-25 | N/A |
| Research tools | Brave + Tavily (reduced) | ~$10-15 | N/A |
| **Total** | | **$85-160** | |

### Model Routing Logic

```python
# Pseudocode for the router
def route_query(intent: str, complexity: float, blast_radius: str) -> str:
    if intent in ("time", "status", "heartbeat", "greeting"):
        return "ollama_local"       # FREE
    if intent == "knowledge_lookup" and complexity < 0.3:
        return "haiku"              # ~$0.001 per query
    if intent in ("research", "synthesis", "writing"):
        return "sonnet"             # ~$0.01 per query
    if intent in ("architecture", "strategy", "irreversible_decision"):
        return "opus"               # ~$0.10 per query
    return "haiku"                  # default cheap
```

### Key Technical Decisions

1. **Ollama model choice**: Llama 3.1 8B is the best balance of speed and quality for simple tasks on a MacBook. Phi-3 is an alternative if memory is tight. Groq is the cloud fallback if Mac is asleep.
2. **Haiku vs. Groq for Tier 1**: Haiku is better at instruction-following and formatting. Groq (Llama 70B) is free but less reliable for structured output. Recommendation: Haiku for Tier 1, Groq as Tier 0 backup when Mac is asleep.
3. **Cost tracking**: Every API call logs model, tokens, cost to a SQLite table. The `/budget` Telegram command shows spend-to-date. Hard cap: if monthly spend exceeds $150, downgrade all Tier 2 queries to Tier 1 until the month resets.

### Gap Analysis

- **Missing**: Ollama not installed/configured for local inference.
- **Missing**: No cost tracking anywhere in the stack.
- **Missing**: No model routing layer. Every query goes to the same model.
- **Missing**: No Groq integration as cloud-free fallback.

### Risk Level: MEDIUM
The primary risk is cost overrun. Without tracking, Mike has no visibility into spend. The secondary risk is Ollama quality — local models are noticeably worse than Haiku for nuanced tasks. The routing logic must be conservative: when in doubt, route to Haiku, not local.

---

## Lens 5: RISK & GOVERNANCE

### Risk 1: Oracle Compliance (CRITICAL)

**The threat**: Mike works at Oracle. Oracle has strict policies about corporate data flowing to external AI systems. If email bodies, internal strategy documents, or patient-adjacent data reach Claude's API, Mike faces termination and potential legal exposure.

**Current state**: The Oracle Health AI Enablement project lives in a separate repo. Susan's RAG contains Oracle Health agent definitions and marketing strategies. It is unclear whether any of the 94K RAG chunks contain Oracle-internal data that should not reach a cloud LLM.

**Mitigation (must implement before July)**:

| Control | Description | Priority |
|---------|-------------|----------|
| Data classification tags | Every RAG chunk tagged: PUBLIC, INTERNAL, ORACLE-RESTRICTED | P0 |
| Query filter | Telegram queries auto-exclude ORACLE-RESTRICTED chunks from RAG results | P0 |
| Oracle-safe mode | A `/work-safe` toggle that activates restricted RAG scope + disables Opus calls | P0 |
| Audit log | Every query + response logged locally (not in cloud) for compliance review | P1 |
| Local-only mode | For Oracle-sensitive questions: route to Ollama (never leaves the machine) | P1 |

**The work-safe profile already exists** at `.startup-os/control-plane/claw/profiles/work-safe.yaml`. This is good. It needs to be wired to the Telegram interface and enforced at the RAG retrieval layer.

### Risk 2: Single Point of Failure (HIGH)

**The threat**: Mike's MacBook is the entire system. If it is lost, stolen, crashes, or is asleep at the wrong time, everything stops.

**Mitigation**:
- Git repo is on GitHub (code is backed up)
- Supabase has the RAG vectors (knowledge is backed up)
- SQLite conversation memory should sync to iCloud or a backup service
- FastAPI bridge should degrade gracefully: if unreachable, Telegram bot returns "Bridge offline — try again when Mike's Mac is awake" instead of silence

### Risk 3: Cost Overrun (MEDIUM)

**The threat**: One bad chain execution or research task could burn $20 in a single Opus call. Ten of those in a month blows the budget.

**Mitigation**:
- Per-query cost estimation before execution
- Hard budget cap with automatic downgrade
- Daily cost summary in ARIA brief
- Opus gated behind explicit confirmation for any query estimated >$0.50

### Risk 4: Scope Creep / Over-Architecture (HIGH)

**The threat**: Mike has already built 10+ backend modules, 81 agents, a workspace contract system, department structures, maturity scoring, and a 7-layer intelligence stack. The system is architecturally rich and operationally thin. The risk is continuing to build infrastructure instead of shipping the one feature that matters: sourced answers on Telegram.

**Mitigation**:
- This assessment. Read the build sequence in Lens 6. Ship the Telegram surface first. Everything else is expansion.
- Freeze new module development until the core Telegram --> RAG --> sourced answer loop works end-to-end.
- Jake's circuit breaker should apply: no new architecture until the delivery surface is proven.

### Risk 5: Data Freshness (MEDIUM)

**The threat**: 94K RAG chunks sound impressive, but if 60% are stale, the system gives Mike confident answers based on outdated information. Worse: Mike trusts the answer because it has citations.

**Mitigation**:
- Freshness scoring on every chunk (date ingested, last validated)
- Research daemon runs weekly to flag stale competitive data
- Responses include a freshness indicator: "Based on data from [date]. Flag if stale."
- ARIA morning brief includes a "stale data" count

### Key Decisions

1. **Does Mike commit to the Oracle data classification sweep?** This is non-negotiable before any Oracle-related queries flow through Telegram. Estimate: 1 day of work to tag the existing RAG chunks.
2. **Budget hard cap or soft cap?** Recommendation: Hard cap at $150/month with automatic model downgrade. Mike can override for a specific query but must explicitly opt in.

### Risk Level: HIGH (Oracle compliance dominates)

---

## Lens 6: EVOLUTION PATH

### Build Sequence: 4 Months, 4 Sprints

The sequence is designed around one principle: **ship the smallest thing that delivers the "dinner with my boss" use case, then expand.**

---

#### Sprint 1: The Wire (Weeks 1-4, March 18 - April 18)

**Goal**: Mike can ask a question on Telegram and get a sourced answer from his RAG knowledge base.

| Task | Effort | Deliverable |
|------|--------|-------------|
| FastAPI bridge: add `/query` endpoint that calls RAG retriever | 2 days | Endpoint returns top-K chunks with sources |
| Citation formatter: chunks --> Telegram-formatted answer with links | 2 days | Formatted response with [Source: title, date] |
| OpenClaw: wire Telegram --> FastAPI `/query` --> formatted response | 2 days | End-to-end message flow |
| Haiku integration: format + summarize RAG results via Haiku | 1 day | Haiku produces the final response text |
| FastAPI as launchd service | 1 day | Auto-starts, survives reboot |
| Oracle data classification: tag RAG chunks | 2 days | PUBLIC/INTERNAL/RESTRICTED tags on all chunks |
| Work-safe mode: wire to RAG filter | 1 day | `/work-safe` toggle in Telegram excludes restricted chunks |

**Sprint 1 exit criteria**: Mike is at dinner, opens Telegram, types "What's our strategy for the payer space and prior auth?", and receives a 3-paragraph sourced answer with links in under 15 seconds. Work-safe mode excludes Oracle-restricted data.

**What we are NOT building in Sprint 1**: Model routing, memory, agent dispatch, chain triggers, cost tracking. Not yet.

---

#### Sprint 2: The Router (Weeks 5-8, April 19 - May 18)

**Goal**: Queries route to the cheapest capable model. Cost tracking is live. Budget is enforced.

| Task | Effort | Deliverable |
|------|--------|-------------|
| Install Ollama + Llama 3.1 8B on Mac | 1 day | Local inference for simple queries |
| Intent classifier (Haiku-based, ~50ms) | 3 days | Classifies: simple / knowledge / research / critical |
| Model router in FastAPI bridge | 2 days | Routes to Ollama/Haiku/Sonnet/Opus based on intent |
| Cost tracking: SQLite table, per-query logging | 2 days | Every call logged with model, tokens, cost |
| Budget enforcer: hard cap + auto-downgrade | 1 day | Exceeding $150 triggers Haiku-only mode |
| `/budget` command in Telegram | 1 day | Shows spend-to-date, projected month-end |
| `/status` command in Telegram | 1 day | Bridge health, RAG status, budget, stale data count |

**Sprint 2 exit criteria**: Mike's average query costs <$0.005. Monthly projected spend is visible. Simple questions ("What time is it?") never hit the API. Knowledge queries hit Haiku. Research queries hit Sonnet. Budget hard cap is enforced.

---

#### Sprint 3: The Memory (Weeks 9-12, May 19 - June 18)

**Goal**: The system remembers. Conversations persist across sessions. Cross-company patterns surface automatically.

| Task | Effort | Deliverable |
|------|--------|-------------|
| Conversation memory: SQLite store for Telegram sessions | 3 days | Last 50 messages per conversation, searchable |
| Context injection: recent conversation history prepended to queries | 2 days | "As we discussed yesterday..." follow-up works |
| Wire existing memory/ module to Telegram | 3 days | Trajectory extraction, consolidation on Telegram conversations |
| Cross-company pattern detector | 3 days | Weekly digest: "Pattern from Oracle Health applies to TransformFit" |
| Freshness scoring on RAG chunks | 2 days | Every chunk has ingest date, staleness flag |
| ARIA brief integration: stale data + cost summary | 1 day | Morning brief includes system health section |

**Sprint 3 exit criteria**: Mike asks a follow-up question and the system remembers the prior context. Morning brief includes cross-company patterns, cost summary, and stale data alerts. Mike spends <10 min/day on system operations.

---

#### Sprint 4: The Agents (Weeks 13-16, June 19 - July 18)

**Goal**: Mike can dispatch agents from Telegram. Chains run autonomously. Trust layer governs outputs.

| Task | Effort | Deliverable |
|------|--------|-------------|
| Agent dispatch from Telegram: `/ask steve`, `/ask research-director` | 3 days | 5 "hot" agents routable from Telegram |
| Wire Birch signal scoring to Telegram notifications | 2 days | High-signal competitive moves push-notify Mike |
| Chain trigger from Telegram: `/run competitive-response` | 3 days | Chains execute, trust layer gates output |
| Trust dashboard: daily markdown in ARIA brief | 2 days | Autonomy graduation visible, staged items listed |
| Decision history query: "What did we decide about X?" | 2 days | Queries .startup-os/decisions/ YAML files |
| End-to-end integration testing | 3 days | All four sprints working together |

**Sprint 4 exit criteria**: Mike types `/ask steve What's our competitive position against [competitor]?` and receives a Steve-voiced strategic analysis with sources. Competitive signals auto-notify. Chains run without Mike. Trust layer catches high-blast-radius outputs. The "dinner with my boss" scenario works flawlessly.

---

### What We Are Choosing NOT To Do

These are deliberate exclusions. They are not forgotten — they are deferred because they do not serve the core use case within the 4-month window.

| Excluded | Why |
|----------|-----|
| Web/mobile app | Telegram is the interface. A web app is maintenance overhead for zero incremental value. |
| Productization | Mike is the only user. Building for others is a distraction. |
| New agent development | 81 agents exist. The problem is not agent quantity — it is agent reachability. |
| VPS deployment | Mac-local is fine for a single user. VPS adds ops burden. Revisit if Mac-asleep is a real pain point. |
| Frontend dashboard | Terminal + Telegram + ARIA brief. No React app needed. |
| New RAG ingestion pipelines | 94K chunks is sufficient. Focus on freshness, not volume. |
| V10 Layer 7 (Collective Intelligence) | Intellectually exciting. Operationally premature. The system cannot serve a basic query from Telegram yet — collective intelligence is not the bottleneck. |

---

## Unified Future-Back Narrative

### July 18, 2026 — What The System Looks Like

It is a Friday evening. Mike is at dinner with his boss at Oracle Health. The conversation turns to Oracle's payer strategy and prior authorization workflows. Mike's boss asks, "Where do we stand on the payer engagement model?"

Mike opens Telegram under the table. Types: "What's our current payer engagement strategy and where are we on prior auth integration?"

Three seconds later, the system:
1. Classifies intent: knowledge query, Oracle Health domain, medium complexity.
2. Activates work-safe mode (auto-detected: Oracle Health topic).
3. Queries RAG with Oracle-public-only filter: retrieves 4 relevant chunks from the AI enablement knowledge base.
4. Routes to Haiku (cost: $0.002).
5. Returns a 3-paragraph summary with inline citations: [Source: Oracle Health Payer Strategy Brief, Feb 2026], [Source: Prior Auth Workflow Analysis, Jan 2026].
6. Logs the query, model used, cost, and response to conversation memory.

Mike glances at the response. Confirms it matches his understanding. Paraphrases it to his boss with specific data points. His boss is impressed.

Cost of that interaction: less than half a cent.

Later that evening, Mike checks his Telegram. ARIA has posted the daily brief:
- System health: GREEN. Bridge uptime 99.2%. Budget: $67 of $150 used this month.
- Stale data alert: 3 TransformFit competitor profiles older than 60 days. Research daemon queued refresh.
- Cross-company pattern: "Oracle Health's clinician engagement model maps to TransformFit's coach engagement funnel. Bridge partnership approach could transfer."
- Staged for review: 1 competitive response chain output (Birch scored 82/100 — above auto-publish threshold but flagged because it references a new market entrant).

Mike reviews the staged output in 2 minutes. Approves it. It publishes to the brief archive.

Total time Mike spent on system operations today: 8 minutes.

The system knows him. It remembers that he asked about payer strategy last Tuesday and adjusts the context. It knows Jacob's game schedule and does not push notifications during games. It knows Oracle data stays local.

### Working Backward From July 18 to Today

| When | What | Why First |
|------|------|-----------|
| **Today** (March 18) | Start Sprint 1: The Wire | Nothing else matters until a Telegram query returns a sourced answer |
| **Week 1** | FastAPI `/query` endpoint + citation formatter | The smallest vertical slice of the entire system |
| **Week 2** | OpenClaw wiring + Haiku integration | End-to-end message flow |
| **Week 3** | Oracle data classification + work-safe mode | Compliance before daily use |
| **Week 4** | launchd service + integration testing | Reliability for daily use |
| **April 19** | Start Sprint 2: The Router | Cost control enables daily use within budget |
| **May 19** | Start Sprint 3: The Memory | Persistence makes the system compounding, not transactional |
| **June 19** | Start Sprint 4: The Agents | Multi-agent dispatch from Telegram is the full vision |
| **July 18** | Target state achieved | Mike at dinner. Sourced answer. Half a cent. |

### The First Step

Today, the first step is: **add a `/query` endpoint to the FastAPI bridge that calls `rag_engine.retriever.Retriever` and returns formatted, sourced results.**

That is the entire first day's work. Not architecture. Not planning. Not new modules. One endpoint that takes a question and returns a sourced answer.

Everything else follows from there.

---

## Appendix: Decision Register

| Decision | Recommendation | Alternative Rejected | Rationale | Reversible? |
|----------|---------------|---------------------|-----------|-------------|
| Interface | Telegram only | Web app, mobile app | One surface, done well, for one user | Yes |
| Hosting | Mac-local (launchd) | VPS ($5/mo) | Simpler ops, single user, no deployment pipeline | Yes |
| Model routing | 4-tier (Ollama/Haiku/Sonnet/Opus) | Single model (Sonnet for everything) | Budget constraint forces routing; routing is the moat enabler | Yes |
| Memory backend | SQLite (conversation) + existing memory/ module | Supabase for everything | SQLite is simpler for local conversation state; memory/ module handles knowledge-level consolidation | Yes |
| Agent exposure | 5 hot agents on Telegram | All 81 agents | Constraint forces prioritization; expand based on usage data | Yes |
| Build sequence | Wire --> Router --> Memory --> Agents | Agents first, then wire | Cannot dispatch agents from a surface that does not exist yet | No (sequence matters) |
| Oracle compliance | P0, Sprint 1 | Deferred to Sprint 3 | Non-negotiable. One leaked Oracle email body = termination. | No (must be Sprint 1) |
| Productization | Deferred indefinitely | Build for others now | No market validation, no users, no revenue model. Personal tool first. | Yes |

---

## What Would Change This Assessment

- If Mike gets a second user (even one), productization timing moves up and VPS becomes necessary.
- If Oracle tightens AI policy, local-only mode (Ollama for everything) becomes the dominant path, and the budget constraint relaxes (local is free).
- If Anthropic ships a persistent-memory Claude product that matches this system's RAG depth, the build-vs-buy calculus shifts. Watch for Claude Projects with vector search.
- If Mike's monthly API spend is actually $200+ (untracked), Sprint 2 (The Router) must move to Sprint 1 position — cost control before feature development.
- If the FastAPI bridge proves too fragile for daily use, a managed backend (Railway, Fly.io, ~$7/mo) replaces Mac-local earlier than planned.

---

*Assessment produced by Steve (Business Strategist) for Apex Ventures. Evidence basis: direct codebase analysis of 81 agent definitions, 10+ backend Python modules, workspace contract system, and existing plan documents. Assumptions: budget is $100-150/mo as stated, Oracle compliance is a hard constraint, Mike is the sole user for the foreseeable future. Inferences: current untracked API spend likely exceeds stated budget based on module count and Sonnet/Opus default routing.*
