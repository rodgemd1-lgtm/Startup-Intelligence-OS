# Session Handoff

**Date**: 2026-03-27
**Project**: Startup Intelligence OS
**Session Goal**: Cost optimization — remove budget cap, consolidate MCPs, add local LLM, research Firehose
**Status**: COMPLETE

## Completed
- [x] Budget cap removed — $150 hard block → $500 soft alert / $1K emergency kill
  - Files: `jake_cost/budget.py`, `jake_cost/reporter.py`
- [x] MCP servers consolidated — 26 → 18 (removed 8: deep-research, brightdata, promptx, xcode-build, perplexity-ask, genai-toolbox, cognee, graphiti)
  - Config: `~/.claude.json` (user-level MCP config)
- [x] Ollama local inference tier added — Provider.LOCAL + ModelTier.LOCAL
  - Files: `jake_cost/router.py`, `jake_cost/ollama_client.py`, `agents/base_agent.py`
  - Test: `tests/test_jake_cost_router.py` (63/63 passing)
  - Model: `qwen2.5-coder:14b` pulled and smoke-tested on M4 Pro
- [x] Firehose researched — LIVE, FREE beta, ready to wire into Birch
- [x] Cost audit completed — identified $3K+/mo in cuts across all services

## Not Started
- [ ] Wire Firehose SSE listener into `birch/sources/firehose.py`
- [ ] Sign up for Firehose beta at `firehose.com/signup`
- [ ] Cancel remaining paid services: CrewAI ($85.50), Neural Frames ($99), LangSmith ($39), Aimtell ($49)
- [ ] Audit: Cloudflare ($160/mo — should be $5-20), Google Workspace (2 orgs?), AutoIGDM ($149)
- [ ] Transfer to M5 Max and set `OLLAMA_MODEL=qwen2.5-coder:32b`

## Decisions Made
| Decision | Rationale | Reversible? |
|----------|-----------|-------------|
| Removed $150/mo hard budget cap | OpenRouter routing controls cost via tier selection; $0-$0.40/MTok models handle 90% of tasks | Yes — change MONTHLY_HARD_LIMIT in budget.py |
| Cut 8 MCP servers | 4 redundant (deep-research, brightdata, promptx, xcode-build), 4 broken (perplexity-ask, genai-toolbox, cognee, graphiti) | Yes — `claude mcp add` to restore any |
| Default to qwen2.5-coder:14b local | 32b won't fit on M4 Pro 24GB; 14b runs at ~40-55 tok/s comfortably | Yes — set OLLAMA_MODEL env var |
| Skipped LiteLLM | Susan's jake_cost/router.py already handles multi-provider routing; LiteLLM would add unnecessary complexity | Yes — can add later |

## Computer Transfer Notes (M4 Pro → M5 Max)

### What transfers automatically (via git)
- All code changes (already pushed to GitHub)
- `.mcp.json` (project-level MCP config)
- Susan backend, jake_cost routing, Ollama client

### What needs manual setup on M5 Max
1. **Clone repo**: `git clone https://github.com/rodgemd1-lgtm/Startup-Intelligence-OS.git`
2. **Python venv**: `cd susan-team-architect/backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
3. **Environment variables**: Copy `~/.hermes/.env` from old machine (19 API keys)
4. **Ollama**: `brew install ollama && ollama pull qwen2.5-coder:32b`
5. **Set model for M5 Max**: Add to `~/.hermes/.env`:
   ```
   OLLAMA_MODEL=qwen2.5-coder:32b
   OLLAMA_NUM_GPU=999
   OLLAMA_KEEP_ALIVE=30m
   OLLAMA_MAX_LOADED_MODELS=1
   OLLAMA_FLASH_ATTENTION=1
   ```
6. **Claude Code MCPs**: Run `claude mcp list` — project-level MCPs auto-load, but user-level MCPs (tavily, firecrawl, brave-search, etc.) need re-adding via `claude mcp add`
7. **Claude Code plugins**: Check `~/.claude/settings.json` — 99 plugins need to sync
8. **Redis** (optional, for future caching): `brew install redis && brew services start redis`

### MCP servers to re-add on new machine
```bash
# Search & Research
claude mcp add tavily -- npx -y tavily-mcp@latest
claude mcp add firecrawl -- npx -y firecrawl-mcp@latest
claude mcp add gpt-researcher -- uvx gpt-researcher-mcp
claude mcp add context7 -- npx -y @upstash/context7-mcp@latest

# Productivity
claude mcp add github -- npx -y @modelcontextprotocol/server-github
claude mcp add notion-custom -- npx -y notion-mcp-server
claude mcp add taskmaster -- npx -y task-master-ai@latest
claude mcp add playwright -- npx -y @playwright/mcp@latest

# Media
claude mcp add gemini -- npx -y @fre4x/gemini@latest
claude mcp add quickchart -- npx -y @gongrzhe/quickchart-mcp-server
claude mcp add youtube-transcript -- npx -y @kimtaeyoon83/mcp-server-youtube-transcript

# Intelligence
claude mcp add trendradar -- uv --directory ~/TrendRadar run python -m mcp_server.server
```

## Cost Routing Architecture (Final State)
```
LOCAL ($0)        → format, embed_prep, background_process, summarize_short
FREE_BULK ($0)    → classify, categorize, extract_fields, tag
VOLUME_OPS ($0.10)→ triage, email, RAG, content, 73 agents default
SMART_OPS ($0.26) → research, briefs, competitive analysis, strategy
FALLBACK ($2.50)  → jake_fallback, openclaw_fallback (escalation only)
OPUS ($5.00)      → architecture, security_audit (Claude Code only)
```

## Build Health
- Files modified this session: 6
- Tests passing: 63/63 (router), 412/412 (non-pre-existing)
- Context health at close: GREEN
- All changes committed and pushed to `origin/main`

## Plan Document
- Full plan: `docs/plans/2026-03-27-cost-routing-mcp-optimization.md`

## Service Cancellation Checklist (Mike's TODO)
- [ ] CrewAI ($85.50/mo)
- [ ] Neural Frames ($99/mo)
- [ ] LangSmith ($39/mo)
- [ ] Aimtell ($49/mo)
- [ ] Cloudflare audit — why $160/mo?
- [ ] Google Workspace audit — are both INNO and VITA orgs active?
- [ ] AutoIGDM ($149/mo) — 30-day ROI check
- [ ] PathSocial ($22.59/mo) — 30-day ROI check
- [ ] Sports Reelz ($50/mo) — still using?
- [ ] Sign up for Firehose beta (free): firehose.com/signup
