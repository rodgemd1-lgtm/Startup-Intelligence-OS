# V1.5 Complete Cost Inventory — All Vendors

**Date**: 2026-03-27
**Sources**: Credit card statements + Gmail receipt analysis + session audit
**Status**: APPROVED — executing

---

## Master Vendor Table

### KEEP — Essential Infrastructure

| Vendor | Monthly | Annual | Purpose | Notes |
|--------|---------|--------|---------|-------|
| **Claude Pro** | $210 | $2,520 | Claude Code access (building Jake/OpenClaw/Susan) | NON-NEGOTIABLE — this is how we build |
| **OpenAI ChatGPT** | $200 | $2,400 | Codex access | Mike confirmed needed |
| **Anthropic API** | ~$4,400 (current) → target $300 | | Agent operations — being migrated to OpenRouter | SET $500 HARD CAP at console.anthropic.com |
| **Supabase Pro** | $25 | $300 | Brain DB, RAG (94K chunks), entity graph, auth | Core infrastructure |
| **Cloudflare** | $160 | $1,920 | Workers, R2, Tunnels, Zero Trust (V15 L0) | AUDIT: Why $160? Two accounts? Should be $5-20/mo |
| **Voyage AI** | ~$10 | ~$120 | Embeddings (voyage-3, 1024-dim) | Low cost, essential |
| **OpenRouter** | ~$30-80 est | | Model gateway for GLM/Gemini/DeepSeek/MiniMax | New — replaces most Anthropic API usage |
| **Verizon** | $151 | $1,812 | Phone/internet — comes from bank account | Utility, not cuttable |
| **Obsidian Sync** | $8.41 | $100.94 | Knowledge vault sync across devices | KEEP (see Obsidian vs Notion decision below) |

### CUT — Already Done or Do Today

| Vendor | Monthly | Status | Savings |
|--------|---------|--------|---------|
| **xAI Grok** | $300 | CANCELED 2026-03-27 | $300/mo |
| **Tooljet** | $99 | CANCELED 2026-03-27 | $99/mo |
| **Claude.ai subscription** | ~~$210~~ | **DO NOT CUT** — Mike needs for Claude Code | $0 |
| **ChatGPT subscription** | ~~$200~~ | **DO NOT CUT** — Mike needs Codex | $0 |

### CUT — Recommended Now

| Vendor | Monthly | Why Cut | Replacement | Savings |
|--------|---------|---------|-------------|---------|
| **Cluely Pro+** | $75 | What is this? If AI coding assistant, Claude Code replaces it | Claude Code | $75/mo |
| **Agents In A Box** | $99 | We built our own agent framework (73 Susan agents + OpenRouter) | Susan + Jake | $99/mo |
| **Apify** | $29 | Overlaps with Firecrawl (which you just renewed for $990/yr) | Firecrawl MCP | $29/mo |
| **Replit** | $1,551 | Continuous compute — migrate to Cloudflare Workers or local | Cloudflare Workers ($5) | $1,546/mo |

### AUDIT — 30 Days

| Vendor | Monthly | Question | Action |
|--------|---------|----------|--------|
| **Cloudflare** | $160 | Why $160/mo? The Workers Paid plan is $5. Do you have 2 accounts, premium DNS, or enterprise features? | Check cloudflare.com for all accounts. Target: $5-20/mo |
| **Firecrawl** | $82.50 ($990/yr) | Just renewed March 23. Already have Brightdata MCP + Tavily + Jina for scraping | Can't refund, but DON'T RENEW. Use until expiry. |
| **AutoIGDM** | $149 | Track ROI vs follower growth for 30 days | Cut if no measurable lift |
| **PathSocial** | $22.59 | Same as AutoIGDM | Cut if no measurable lift |
| **Railway** | $20 | What's deployed here? | Inventory deployments, migrate to Cloudflare Workers |
| **Google Workspace x2** | $50.40 | Are both INNO and VITA active? | Cut dead org ($25/mo savings) |
| **Higgsfield** | ~$68 avg | Usage-based video generation | Watch frequency |
| **Canva** | ? | Check plan level — free tier might suffice | Audit usage |
| **Topaz Labs** | ? | Photo/video AI upscaling — usage-based? | Audit usage |
| **5KM Tech** | ? | What is this? | Investigate and cut if unused |

### NOT ON CARDS (bank/other)

| Vendor | Monthly | Notes |
|--------|---------|-------|
| Verizon | $151 | Bank account |
| Notion | ? | Check if free or paid — if paid, see Obsidian vs Notion section |

---

## Monthly Cost Summary

### Current State (estimated)

| Category | Monthly |
|----------|---------|
| AI Subscriptions (Claude Pro, ChatGPT) | $410 |
| AI API (Anthropic direct — uncapped) | ~$4,400 |
| Compute (Replit) | $1,551 |
| Canceled subs (Grok, Tooljet) | ~~$399~~ → $0 |
| Recommended cuts (Cluely, Agents In A Box, Apify) | $203 |
| Infrastructure (Supabase, Cloudflare, Voyage, OpenRouter) | ~$230-300 |
| SaaS tools (Firecrawl, AutoIGDM, PathSocial, Railway, etc.) | ~$390 |
| Telecom (Verizon) | $151 |
| Media (Higgsfield, Canva, Topaz, Obsidian) | ~$180 |
| **TOTAL ESTIMATED** | **~$7,900-8,500/mo** |

### Target State (after all optimizations)

| Category | Monthly |
|----------|---------|
| AI Subscriptions (Claude Pro, ChatGPT) | $410 |
| AI API — OpenRouter (Gemini/DeepSeek/GLM) | ~$50-100 |
| AI API — Anthropic direct (capped, Claude Code only) | ~$200-500 |
| Infrastructure (Supabase $25, Cloudflare $5-20, Voyage $10, OpenRouter $50) | ~$90-105 |
| Obsidian Sync | $8 |
| Verizon | $151 |
| 30-day audit survivors (some may stay) | ~$0-200 |
| **TOTAL TARGET** | **~$910-1,475/mo** |

### **Projected savings: $6,400-7,600/mo (80-90%)**

---

## Obsidian vs Notion Decision

### Context
- Obsidian Sync: $8.41/mo ($100.94/yr) — charged 2026-03-27
- Notion: Unknown if free or paid tier
- V15 architecture designates Obsidian as "the brain" (knowledge vault, Git-synced)
- QMD (Shopify's Tobi) provides local hybrid search over Obsidian vault
- ObsidianClaw plugin enables in-vault AI chat
- Susan RAG (94K chunks) lives in Supabase, NOT Obsidian

### Recommendation: KEEP Obsidian, DOWNGRADE Notion

**Obsidian wins because:**
1. V15 architecture already chose it as the knowledge layer (L2)
2. Local-first = no vendor lock-in, Git-synced, works offline
3. QMD gives hybrid search (BM25 + vector) over vault — free
4. ObsidianClaw plugin integrates with Claude Code/OpenClaw
5. $8/mo for sync is cheap

**Notion should be:**
- Kept on FREE tier for any team/collaboration needs
- NOT used as primary knowledge base (that's Obsidian's job)
- If you're paying for Notion, downgrade to free

**Action items:**
1. Check if Notion is free or paid → downgrade if paid
2. Confirm Obsidian Sync is working across devices
3. Future: Set up QMD over Obsidian vault (V15 Phase 2)

---

## Model Routing Through Claude Code

### Mike's Ask
> "Can I route models like MiniMax 2.7 or GLM through Claude Code — like I'm using right now — so it wouldn't go to Anthropic for some of the easier stuff?"

### Answer: Not directly, but we can get close

**How Claude Code works today:**
- Claude Code ALWAYS uses Anthropic's API (Opus/Sonnet/Haiku)
- You control the model with `/model` command
- Sub-agents inherit the session model
- There's no native "route to OpenRouter" option in Claude Code

**What we CAN do:**
1. **Jake as the router** — When you ask Jake to do research, triage, or summaries, Jake dispatches those tasks to Susan agents which NOW route through OpenRouter automatically (we just built this). So the expensive Opus context stays in Claude Code for YOUR conversation, but the agent work happens on Gemini/DeepSeek/GLM.

2. **`/effort` controls** — Use `/effort low` for simple tasks (uses fewer thinking tokens), `/effort high` for architecture. This controls Anthropic spend within Claude Code itself.

3. **Anthropic API hard cap** — Set a $500/mo cap at console.anthropic.com. This forces discipline without killing capability.

4. **Future: OpenRouter-native Claude Code alternative** — Projects like Cline/Continue/Aider support OpenRouter natively. If you wanted a second coding agent for simpler tasks routed through Gemini/DeepSeek, that's possible but a separate project.

### The practical workflow:
```
Mike types in Claude Code (Opus) → Jake interprets
  ├── Simple research/triage → Susan agent → OpenRouter (Gemini 2.0 Flash) = $0.0002
  ├── Deep analysis → Susan agent → OpenRouter (DeepSeek V3.2) = $0.0006
  ├── Classification/tagging → Susan agent → OpenRouter (GLM-4.5-Air:free) = $0.00
  └── Architecture/building → Claude Code direct (Opus) = normal Claude Code cost
```

Jake's router already handles this. The savings happen on the AGENT side, not the Claude Code side.
