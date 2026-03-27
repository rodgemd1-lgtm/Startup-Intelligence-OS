# Cost Routing & MCP Optimization Plan

**Date**: 2026-03-27
**Status**: DRAFT — awaiting Mike's approval
**Effort**: HIGH (multi-file, infrastructure)
**Confidence**: DRAFT

## Goals
1. Remove the $150/mo agent API budget cap — let OpenRouter routing handle cost control
2. Consolidate 28 MCP servers down to ~18 (cut 10 redundant ones)
3. Add LiteLLM + Ollama local fallback for Susan's Python agents
4. Wire Firehose into the Birch signal pipeline

---

## Part 1: Remove Budget Cap + Update Cost Controls

### Problem
`jake_cost/budget.py` has a hard $150/mo cap that blocks agent operations. With OpenRouter routing (FREE_BULK at $0, VOLUME_OPS at $0.10/$0.40 per MTok), the routing itself is the cost control — the cap is now redundant and restrictive.

### Changes
**File: `susan-team-architect/backend/jake_cost/budget.py`**
- Remove `MONTHLY_BUDGET_USD = 150.0` hard cap
- Replace with soft monitoring: `MONTHLY_SOFT_LIMIT = 500.0` (alert, don't block)
- Keep per-operation token budgets (these prevent runaway single calls)
- Change `check_monthly()` to return warning but never block (`ok=True` always)
- Add `MONTHLY_HARD_LIMIT = 1000.0` as emergency kill switch (only blocks above $1K)

### Why This Works
- FREE_BULK tier costs $0 — classification, tagging, extraction
- VOLUME_OPS costs $0.10/MTok input — 73 agents at 10K tokens/call = ~$0.001/call
- Even 10,000 agent calls/month at VOLUME_OPS = ~$5-10/month
- SMART_OPS (research) at $0.26/MTok — 1,000 research calls = ~$5/month
- Realistic monthly spend with OpenRouter: **$15-50/month**

---

## Part 2: MCP Consolidation

### Current State: 28 MCP servers active

#### SEARCH/RESEARCH MCPs (11 servers — massive overlap)
| MCP | Unique Capability | Cost | Verdict |
|-----|-------------------|------|---------|
| **brave-search** | Local search, cheap web search | ~$5/mo | KEEP — cheapest general search |
| **tavily** | AI search + crawl + extract + research | $30/mo | KEEP — best AI search integration |
| **exa** | Semantic search, company research | $40/mo | CUT — Tavily covers this |
| **jina** | Webpage reader, fact check | Free tier | KEEP — free fallback reader |
| **firecrawl** | Premium scraping + browser + agent | Annual (paid) | KEEP — already paid |
| **brightdata** | Proxy scraping | Enterprise | CUT — Firecrawl covers this |
| **apify** | Actor-based automation | $29/mo | CUT — Firecrawl covers this |
| **gpt-researcher** | Deep autonomous research | Uses underlying APIs | KEEP — unique deep research |
| **deep-research** | Octagon deep research | Uses underlying APIs | CUT — overlaps gpt-researcher |
| **trendradar** | News aggregation, trending, sentiment | Self-hosted (free) | KEEP — unique real-time intel |
| **context7** | Library/framework docs | Free | KEEP — essential for coding |

**Search MCP verdict: Cut 4, keep 7. Savings: ~$69/mo (Exa + Apify)**

#### PRODUCTIVITY MCPs (keep all)
| MCP | Purpose | Cost | Verdict |
|-----|---------|------|---------|
| **github** | Repo/PR/issue management | Free | KEEP |
| **notion-custom** | Workspace access | Free (with sub) | KEEP |
| **gmail** | Email access | Free | KEEP |
| **google_drive** | File access | Free | KEEP |
| **scheduled-tasks** | Cron scheduling | Free | KEEP |
| **taskmaster** | Task management | Free | KEEP |

#### DEVELOPMENT MCPs (review)
| MCP | Purpose | Cost | Verdict |
|-----|---------|------|---------|
| **playwright** | Browser testing | Free | KEEP |
| **Claude_in_Chrome** | Browser control | Free | CUT — overlaps playwright |
| **Claude_Preview** | Dev server preview | Free | KEEP — unique preview capability |
| **stitch** | Design system | Free | KEEP |
| **xcode-build** | iOS development | Free | CUT — not actively used |
| **mcp-registry** | MCP discovery | Free | CUT — rarely used |
| **promptx** | Prompt management | Free | CUT — QMD covers doc search |

#### MEDIA MCPs (keep)
| MCP | Purpose | Cost | Verdict |
|-----|---------|------|---------|
| **gemini** | Image/video gen | Usage-based | KEEP |
| **quickchart** | Chart generation | Free | KEEP |
| **youtube-transcript** | Content extraction | Free | KEEP |

#### DOMAIN MCPs (keep)
| MCP | Purpose | Cost | Verdict |
|-----|---------|------|---------|
| **financial-datasets** | Market data | Free/OAuth | KEEP |
| **susan-intelligence** | Core system | Free (local) | KEEP |
| **higgsfield** | Video gen | Annual (paid) | KEEP |
| **qmd** | Local doc search | Free (local) | KEEP |
| **supermemory** | Memory layer | Sub-based | KEEP |

### MCP Removal Commands
```bash
# Cut redundant search MCPs
claude mcp remove exa
claude mcp remove brightdata
claude mcp remove apify
claude mcp remove deep-research

# Cut redundant dev MCPs
claude mcp remove Claude_in_Chrome
claude mcp remove xcode-build
claude mcp remove mcp-registry
claude mcp remove promptx
```

### Final MCP Stack (20 servers)
**Search (7)**: brave-search, tavily, jina, firecrawl, gpt-researcher, trendradar, context7
**Productivity (6)**: github, notion, gmail, google_drive, scheduled-tasks, taskmaster
**Development (3)**: playwright, Claude_Preview, stitch
**Media (3)**: gemini, quickchart, youtube-transcript
**Domain (5)**: financial-datasets, susan-intelligence, higgsfield, qmd, supermemory
**Global (2)**: oracle-health, sp-design-agent

---

## Part 3: LiteLLM + Ollama Local Fallback

### What This Does
Adds a local LLM (Qwen2.5-Coder:32b via Ollama) as a fallback tier in Susan's Python agent router. NOT for Claude Code — for Susan's 73 agents only.

### New Tier: LOCAL_FALLBACK
```python
ModelTier.LOCAL = "local"  # Ollama — $0, runs on Mac's 48GB unified memory

_MODEL_PRICING[ModelTier.LOCAL] = {
    "model_id": "ollama/qwen2.5-coder:32b",
    "provider": Provider.LOCAL,
    "input_per_1m": 0.00,
    "output_per_1m": 0.00,
    "max_tokens": 8192,
    "context_window": 32768,
    "description": "Local Ollama — zero cost, offline capable, ~20GB RAM",
}
```

### Routing Integration
- Add `Provider.LOCAL` enum value
- Add `_run_local()` method to `base_agent.py` using httpx to Ollama API
- LOCAL tier used when: OpenRouter is down, or for tasks that don't need cloud quality
- Task routing: `background_process`, `embed_prep`, `format` → LOCAL if Ollama is running

### Prerequisites (Mike runs on Mac)
```bash
brew install ollama
ollama pull qwen2.5-coder:32b
# Ollama auto-starts as a service on macOS
```

### LiteLLM (Optional Layer)
LiteLLM can sit between Susan and all providers (OpenRouter + Ollama + direct Anthropic) for:
- Unified API interface
- Redis caching (avoid duplicate calls)
- Automatic fallback chain

However, Susan's router ALREADY handles multi-provider routing. LiteLLM would add complexity without much gain right now. **Recommend: Skip LiteLLM, add Ollama directly to the existing router.**

---

## Part 4: Firehose Integration

### What Firehose Does
Push-based real-time web monitoring from Ahrefs. Free during beta. Sends SSE events when new web content matches your rules.

### Where It Fits
Birch signal scoring pipeline already has Firehose as a source type:
- `susan-team-architect/backend/birch/sources/firehose.py` (placeholder exists)
- Schema: `source: Literal["firehose", "trendradar", "morning_intel", "manual"]`
- `aiohttp>=3.9.0` already in `pyproject.toml`

### Implementation
1. Implement the SSE listener in `birch/sources/firehose.py`
2. Create 5-10 Lucene rules for monitoring:
   - Competitor mentions (Oracle Health competitors, fitness app competitors)
   - Industry keywords (AI agents, startup tools, recruiting tech)
   - Tech stack changes (Supabase, OpenRouter, Claude announcements)
3. Feed SSE events → Birch signal scorer → priority queue
4. High-priority signals surface in ARIA daily brief

### Cost: $0 (beta)

---

## Execution Order

1. **Budget cap removal** (5 min, 1 file) — immediate value
2. **MCP consolidation** (10 min, CLI commands) — cleaner toolset
3. **Ollama local fallback** (30 min, 3 files) — zero-cost agent tier
4. **Firehose wiring** (45 min, 2 files) — real-time monitoring

## Risk Assessment
- Budget cap removal: LOW risk (routing already controls cost)
- MCP removal: LOW risk (can re-add any MCP in 30 seconds)
- Ollama: MEDIUM risk (needs testing, may not match cloud quality)
- Firehose: LOW risk (additive, doesn't change existing flows)

## Expected Monthly Cost After Optimization
- Agent API (OpenRouter): ~$15-50/mo (uncapped but cheap)
- Removed MCP subs (Exa, Apify): -$69/mo
- Local Ollama: $0 (electricity only)
- Firehose: $0 (beta)
