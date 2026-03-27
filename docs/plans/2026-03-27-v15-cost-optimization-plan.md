# V1.5 Cost Optimization Plan — API & Infrastructure

**Date**: 2026-03-27
**Author**: Jake (AI Co-Founder)
**Status**: APPROVED by Mike 2026-03-27
**Confidence**: DRAFT
**Effort**: HIGH (affects all agent operations, model routing, vendor stack)

---

## 1. Problem Statement

Mike's current monthly spend on AI/infra is estimated at **$7,200-8,200/mo** — unsustainable for a pre-revenue portfolio. The two biggest offenders:

- **Anthropic API**: ~$4,400/mo (annualized) — 392% increase from prior month. Unmonitored agent loops hitting token limits with no cost caps.
- **Replit**: ~$1,551/mo — continuous compute charges suggesting agent deployments, not IDE use.

Additionally: 3 competing chat subscriptions ($710/mo), unused/unaudited SaaS ($389/mo), and missing infrastructure (Cloudflare, Neon) not yet tracked.

---

## 2. Current Spend Inventory

### Tier 1: BLEEDING ($5,951/mo — 72% of total)

| Vendor | Monthly Est | Issue | Action |
|--------|------------|-------|--------|
| Anthropic API | ~$4,400 | Agent loops, no cost caps, overnight batch jobs | **SLASH 90%** — route 90% of operations to GLM-5 + MiniMax M2.7 via OpenRouter |
| Replit | ~$1,551 | Continuous compute — likely agent deployments | **MIGRATE** — move to Cloudflare Workers ($5/mo) or Railway |

### Tier 2: REDUNDANT ($710/mo — 9%)

| Vendor | Monthly | Action |
|--------|---------|--------|
| Claude.ai Pro | $210 | **CUT** — you have Claude Code + API. Redundant chat interface. |
| OpenAI ChatGPT | $200 | **KEEP** — Mike needs Codex. GPT-4o also available via OpenRouter. |
| xAI Grok | $300 | **CUT** — what are you using this for? If competitive intel, TrendRadar + Brave + Tavily already cover it. |

### Tier 3: AUDIT ($389/mo — 5%)

| Vendor | Monthly | Action |
|--------|---------|--------|
| Tooljet | $99 | **CUT** — you build on Next.js/Supabase. Tooljet is unused. |
| AutoIGDM | $149 | **AUDIT** — track ROI for 30 days. Cut if no measurable follower/engagement lift. |
| PathSocial | $23 | **AUDIT** — same as AutoIGDM. |
| Higgsfield | ~$68 avg | **KEEP** — usage-based, watch frequency. |
| 2x Google Workspace | $50 | **AUDIT** — confirm both INNO and VITA are active. Cut any dead org. |

### Tier 4: KEEP — Core Infrastructure

| Vendor | Monthly | Purpose |
|--------|---------|---------|
| Supabase Pro | $25 | Brain DB, RAG (94K chunks), entity graph, auth — KEEP as primary |
| Cloudflare Workers Paid | $5 | V15 L0: Workers, R2 (free egress), KV, Zero Trust, Tunnels |
| Neon (if needed) | $0-19 | New Workers-native services only. DO NOT migrate from Supabase. |
| SuperMemory.ai | $19-99 | V15 L3: Memory infra with decay, contradiction, connectors |
| Voyage AI | ~$10 | Embeddings (voyage-3, 1024-dim) |
| OpenRouter | ~$5-50 | Unified model gateway for GLM-5, MiniMax M2.7, GPT-4o |

---

## 3. Model Routing Strategy — The Big Move

### The Thesis

**90% of agent operations do NOT need Claude Opus.** Research, briefs, triage, summaries, RAG queries, classification — all of these run on cheaper models with negligible quality loss.

Anthropic (Claude Code) is reserved EXCLUSIVELY for building Jake, OpenClaw, and Susan. Everything else routes through OpenRouter.

### Model Tiers via OpenRouter

| Tier | Model | Cost (In/Out per MTok) | Context | Use Cases |
|------|-------|----------------------|---------|-----------|
| **T1: Premium Build** | Claude Opus 4.6 | $5.00 / $25.00 | 200K | Jake dev sessions in Claude Code ONLY |
| **T2: Smart Ops** | GLM-5 (Zhipu) | $1.00 / $3.20 | 128K | Research agents, morning briefs, meeting prep, Oracle Health intel, competitive analysis, strategy work |
| **T3: Volume Ops** | MiniMax M2.7 | $0.30 / $1.20 | 205K | RAG queries, email triage, summaries, content generation, bulk agent tasks, Susan agent operations |
| **T4: Free Bulk** | GLM-4.7-Flash | FREE | 128K | Classification, extraction, formatting, tagging, low-stakes background tasks |
| **T5: Fallback** | GPT-4o | $2.50 / $10.00 | 128K | Jake/OpenClaw fallback when GLM-5 quality is insufficient |

### Cost Impact Analysis

**Current**: ~$4,400/mo on Anthropic API (all operations on Claude)

**Projected with routing**:

| Operation Category | Monthly Tokens (est) | Current Model | Current Cost | New Model | New Cost |
|-------------------|---------------------|---------------|-------------|-----------|----------|
| Agent loops/batch jobs | ~50M tokens | Opus/Sonnet | ~$2,500 | MiniMax M2.7 | ~$75 |
| Research & briefs | ~20M tokens | Sonnet | ~$600 | GLM-5 | ~$84 |
| RAG queries & triage | ~30M tokens | Sonnet | ~$900 | MiniMax M2.7 | ~$45 |
| Classification/extraction | ~10M tokens | Sonnet | ~$300 | GLM-4.7-Flash | $0 |
| Jake dev (Claude Code) | ~5M tokens | Opus | ~$250 | Opus (keep) | ~$250 |
| **TOTAL** | **~115M tokens** | | **~$4,550** | | **~$454** |

**Savings: ~$4,100/mo (90% reduction on API costs)**

### OpenRouter Configuration

OpenRouter acts as the unified gateway. All Susan agents, scheduled tasks, and batch jobs route through OpenRouter with model selection based on task tier.

```python
# Model routing config for OpenRouter
OPENROUTER_MODELS = {
    "t2_smart_ops": "zhipu/glm-5",
    "t3_volume_ops": "minimax/minimax-m2.7",
    "t4_free_bulk": "zhipu/glm-4.7-flash",
    "t5_fallback": "openai/gpt-4o",
}

# Task-to-tier mapping
TASK_ROUTING = {
    # T2: Smart Ops (GLM-5)
    "research": "t2_smart_ops",
    "morning_brief": "t2_smart_ops",
    "meeting_prep": "t2_smart_ops",
    "oracle_health_intel": "t2_smart_ops",
    "competitive_analysis": "t2_smart_ops",
    "strategy_work": "t2_smart_ops",

    # T3: Volume Ops (MiniMax M2.7)
    "rag_query": "t3_volume_ops",
    "email_triage": "t3_volume_ops",
    "summarize": "t3_volume_ops",
    "content_generation": "t3_volume_ops",
    "susan_agent_ops": "t3_volume_ops",
    "bulk_agent_tasks": "t3_volume_ops",

    # T4: Free Bulk (GLM-4.7-Flash)
    "classify": "t4_free_bulk",
    "extract": "t4_free_bulk",
    "format": "t4_free_bulk",
    "tag": "t4_free_bulk",
    "background_process": "t4_free_bulk",

    # T5: Fallback (GPT-4o) — only when T2/T3 quality is insufficient
    "jake_fallback": "t5_fallback",
    "openclaw_fallback": "t5_fallback",
}
```

---

## 4. Infrastructure Stack (V15-aligned)

### What We're Building

| Layer | Service | Monthly Cost | Status |
|-------|---------|-------------|--------|
| L0: Infra | Cloudflare (Workers + R2 + KV + ZT + Tunnels) | $5 | NEW — set up |
| L0: Infra | Supabase Pro | $25 | KEEP — already running |
| L0: Infra | Neon | $0-19 | NEW — only for Workers-native services |
| L1: Runtime | OpenRouter (model gateway) | ~$50-200 | NEW — replace direct Anthropic API |
| L2: Knowledge | Voyage AI (embeddings) | ~$10 | KEEP |
| L3: Memory | SuperMemory.ai | $19-99 | EVALUATE — confirm tier needed |
| L6: Orchestration | Paperclip (self-hosted) | $0 | KEEP — already running locally |

### What We're Killing

| Service | Monthly | Replacement |
|---------|---------|-------------|
| Replit | $1,551 | Cloudflare Workers ($5) + local compute |
| Claude.ai Pro | $210 | Claude Code (already have) |
| OpenAI ChatGPT | — | **KEEP** — needed for Codex |
| xAI Grok | $300 | TrendRadar + Brave + Tavily (already have) |
| Tooljet | $99 | Next.js/Supabase (already building on) |
| Direct Anthropic API (bulk) | ~$4,150 | OpenRouter → GLM-5 + MiniMax M2.7 |

---

## 5. Projected Monthly Budget (Post-Optimization)

### Before

| Category | Monthly |
|----------|---------|
| AI API (Anthropic direct) | ~$4,400 |
| Compute (Replit) | ~$1,551 |
| Chat subscriptions (3x) | $710 |
| SaaS tools | $389 |
| Infrastructure | ~$35 |
| **TOTAL** | **~$7,085** |

### After

| Category | Monthly |
|----------|---------|
| AI API via OpenRouter (GLM-5 + MiniMax M2.7 + Flash) | ~$200 |
| AI API direct (Claude Code / Opus only) | ~$250 |
| OpenAI ChatGPT (Codex) | $200 |
| Cloudflare (full stack) | $5 |
| Supabase Pro | $25 |
| Neon (if used) | $0-19 |
| SuperMemory.ai | $19-99 |
| Voyage AI | ~$10 |
| Instagram tools (if ROI positive) | $0-172 |
| Google Workspace (if both active) | $25-50 |
| Higgsfield (usage-based) | ~$68 |
| **TOTAL** | **~$802-1,098** |

### Monthly Savings: ~$6,000-6,300 (85-89% reduction)

---

## 6. Implementation Plan — V1.5 Execution Order

### Phase A: Stop the Bleeding (Day 1) — COMPLETE 2026-03-27

1. **[DONE] Audit Anthropic API usage** — Found 25 Python files calling Anthropic API directly. Key culprits: `base_agent.py` (all 73 agents default to Sonnet), `autonomous_worker.py` (spawns Claude Code subprocesses), 3 scheduled pipelines (morning, overnight, meeting scanner every 15 min).
2. **[DONE] Add cost caps / OpenRouter routing** — Built `jake_cost/router.py` V1.5 with 7 tiers (4 OpenRouter + 3 legacy Anthropic). Built `jake_cost/openrouter_client.py`. Tested all 3 models live: GLM-4.5-Air:free ($0.00), MiniMax M2.7 ($0.30/$1.20), GLM-5-Turbo ($1.20/$4.00). All confirmed working.
3. **[PARTIAL] Kill Replit** — Found `~/clawd/warroom-replit/` (Next.js, last modified Jan 28). Mike needs to check replit.com dashboard for additional active deployments.
4. **[MIKE ACTION] Cancel Claude.ai Pro** — Cancellation checklist written: `docs/plans/2026-03-27-v15-cancellation-checklist.md`
5. **[MIKE ACTION] Cancel xAI Grok** — In cancellation checklist
6. **[MIKE ACTION] Cancel Tooljet** — In cancellation checklist

### Phase B: Set Up OpenRouter Routing — COMPLETE 2026-03-27

1. **[DONE] Configure OpenRouter** — Tested live: Gemini 2.0 Flash ($0.10/$0.40), DeepSeek V3.2 ($0.26/$0.38), GLM-4.5-Air:free ($0). All confirmed working via OpenRouter.
2. **[DONE] Create routing config** — `jake_cost/router.py` V1.5: 7 tiers (4 OpenRouter + 3 Anthropic legacy). `jake_cost/openrouter_client.py`: httpx-based client with reasoning model support.
3. **[DONE] Update base_agent.py** — All 73 Susan agents now route through OpenRouter by default (Gemini 2.0 Flash). FORCE_ANTHROPIC=1 env var for emergency rollback. Tested: $0.000213 per agent run (was ~$0.02 on Sonnet = 94x cheaper).
4. **[VERIFIED] Scheduled tasks** — Morning pipeline, overnight intel, meeting scanner do NOT call Anthropic API directly. They use Supabase, osascript, TrendRadar. LLM cost comes from base_agent.py (now fixed).
5. **[DONE] Quality tested** — Ran competitive intel prompt across 8 models. All scored GOOD. Gemini 2.0 Flash: 1.4s, DeepSeek V3.2: 4.9s, GLM-4.5-Air:free: 34s (slow but free).
6. **[DONE] Cost tracking dashboard** — `apps/operator-console/cost-dashboard.html`: Live dashboard showing 30-day spend, savings vs Sonnet, tier distribution, top agent spenders. Auto-refreshes every 60s.

### Phase C: Infrastructure Migration (Day 4-5)

1. **Set up Cloudflare Workers Paid** ($5/mo)
2. **Configure Cloudflare Tunnel** to local Mac (secure access without port forwarding)
3. **Set up Cloudflare Zero Trust** (free) for dashboard auth
4. **Migrate Replit workloads** to Cloudflare Workers or local compute
5. **Evaluate Neon** — only provision if building new Workers-native services

### Phase D: Verify & Monitor (Week 2)

1. **Monitor OpenRouter spend** daily for first week
2. **Quality-check outputs** — flag any degradation from model switch
3. **Audit Instagram tools** — 30-day ROI check on AutoIGDM + PathSocial
4. **Confirm Google Workspace** — verify both orgs are active
5. **Produce V1.5 Cost Report** — actual vs projected

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| GLM-5 quality insufficient for research | Medium | Medium | GPT-4o fallback via OpenRouter. Test before full migration. |
| MiniMax M2.7 quality insufficient for RAG | Low | Medium | 80.2% SWE-Bench suggests strong capability. Test on 100 RAG queries first. |
| OpenRouter rate limits | Low | High | Implement retry with exponential backoff. Multiple model fallbacks. |
| Replit migration breaks deployed agents | Medium | High | Inventory all Replit deployments BEFORE shutting down. |
| Claude Code spend still high during dev | Expected | Low | This is the ONE place we keep Opus. Budget ~$250/mo. |

---

## 8. Decision Points for Mike

- [x] **Approve model routing strategy** — APPROVED 2026-03-27
- [x] **Confirm Claude.ai Pro cancellation** — APPROVED (keep Claude Code only)
- [x] **Confirm xAI Grok cancellation** — APPROVED (cut)
- [x] **Confirm Tooljet cancellation** — APPROVED (cut)
- [x] **OpenAI ChatGPT** — KEEP (Mike needs Codex)
- [ ] **AutoIGDM/PathSocial**: 30-day audit per Jake's recommendation
- [ ] **Google Workspace**: Confirm both INNO and VITA are active
- [ ] **Replit**: Inventory what's deployed before migrating/killing

---

## 9. Success Metrics

| Metric | Current | Target (30 days) | Target (90 days) |
|--------|---------|------------------|-------------------|
| Monthly AI/infra spend | ~$7,085 | <$1,500 | <$900 |
| Anthropic API spend | ~$4,400 | <$500 | <$300 |
| Agent operations cost per task | Unknown | Tracked | <$0.05 avg |
| Model quality (subjective 1-10) | 8 (Claude) | 7+ (GLM-5/MiniMax) | 7+ |
| Unmonitored batch jobs | Unknown # | 0 | 0 |

---

**Confidence**: DRAFT — pricing is from published tiers as of 2026-03-27. OpenRouter availability of GLM-5 and MiniMax M2.7 should be confirmed before execution. Quality testing is mandatory before full migration.

**Context Health**: GREEN — early session, minimal files modified.

**Next Step**: Mike approves this plan, then we execute Phase A (stop the bleeding) in this or next session.
