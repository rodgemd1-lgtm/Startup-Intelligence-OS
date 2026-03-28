# Session Handoff

**Date**: 2026-03-27 ~21:00 EDT
**Branch**: main
**Project**: Startup Intelligence OS — V1.5 Cost Optimization
**Status**: PARTIAL — Phase A+B complete, Phase C+D pending

## Completed

### Phase A: Stop the Bleeding
- [x] **Audited Anthropic API usage** — 25 Python files calling Anthropic directly. `base_agent.py` is the main cost driver (all 73 agents default to Sonnet at $3/$15 per MTok). `autonomous_worker.py` spawns Claude Code subprocesses.
  - Files: `agents/base_agent.py`, `jake_cost/router.py`, `jake_cost/openrouter_client.py`
- [x] **Built OpenRouter client** — `jake_cost/openrouter_client.py` (NEW). httpx-based, handles reasoning model responses (MiniMax puts output in `reasoning` field). Tested all models live.
- [x] **Built V1.5 model router** — `jake_cost/router.py` (REWRITTEN). 7 tiers across 2 providers:
  - FREE_BULK: `z-ai/glm-4.5-air:free` ($0/$0)
  - VOLUME_OPS: `google/gemini-2.0-flash-001` ($0.10/$0.40) — DEFAULT for all 73 agents
  - SMART_OPS: `deepseek/deepseek-v3.2` ($0.26/$0.38)
  - FALLBACK: `openai/gpt-4o` ($2.50/$10.00)
  - HAIKU/SONNET/OPUS: Anthropic legacy (backward compat)
- [x] **Grok canceled** by Mike ($300/mo saved)
- [x] **Tooljet canceled** by Mike ($99/mo saved)
- [x] **Cancellation checklist written**: `docs/plans/2026-03-27-v15-cancellation-checklist.md`

### Phase B: OpenRouter Routing
- [x] **Wired OpenRouter into base_agent.py** — All 73 Susan agents now route through OpenRouter by default. `FORCE_ANTHROPIC=1` env var for emergency rollback. Tested: $0.000213/run (was $0.02 = 94x cheaper).
  - Files modified: `agents/base_agent.py` (REWRITTEN)
- [x] **Verified scheduled tasks** — Morning pipeline, overnight intel, meeting scanner do NOT call Anthropic API directly. Cost comes from base_agent.py (now fixed).
- [x] **Built cost tracking dashboard** — `apps/operator-console/cost-dashboard.html` (NEW). Live dashboard: savings vs Sonnet, tier distribution, top agent spenders. Auto-refresh 60s.
- [x] **Quality tested 8 models live** via OpenRouter. All scored GOOD on competitive intel prompt.

### Complete Cost Inventory
- [x] **Built master vendor table** from credit cards + Gmail receipts — `docs/plans/2026-03-27-v15-complete-cost-inventory.md`
- [x] **Total current spend**: ~$7,900-8,500/mo
- [x] **Total target spend**: ~$910-1,475/mo (80-90% reduction)
- [x] **Obsidian vs Notion**: Keep Obsidian (V15 L2 knowledge layer), downgrade Notion to free

## Additional Completed (Late Session)
- [x] **Apify CANCELED** via Chrome — $29/mo saved. Active until April 20, 2026.
- [x] **Anthropic API cap VERIFIED** — $500/mo cap already set at console.anthropic.com. $67.33 used this period.
- [x] **Claude Code model routing RESEARCHED** — Claude Code is hardcoded to Claude models only. No OpenRouter possible. Workaround: use /model haiku for simple tasks, agent dispatches already route to Gemini/DeepSeek via OpenRouter.
- [x] **Complete cost inventory built** — `docs/plans/2026-03-27-v15-complete-cost-inventory.md` covers ALL vendors from credit cards + Gmail receipts.

## In Progress (needs Mike's hands — browser tabs open)
- [ ] **Agents In A Box** ($99/mo) — Skool login tab open in Chrome. Log in → group settings → cancel membership.
- [ ] **Cluely Pro+** ($75/mo) — cluely.com/account 404'd. Check Mac System Settings → Subscriptions, or search Gmail for "Cluely receipt" for Stripe cancel link.
- [ ] **Railway shutdown** ($20/mo) — Railway dashboard tab open in Chrome. Log in → delete all projects.

## Resolved This Session
- [x] **Replit stopped** by Mike ($1,551/mo saved)
- [x] **Cloudflare clarified** — annual domain registration cost, not monthly. No action needed.

## Not Started (Phase C + D)
- [ ] **Phase C**: Set up Cloudflare Workers Paid ($5/mo), configure Tunnel, Zero Trust, migrate Replit workloads
- [ ] **Phase D**: Monitor OpenRouter spend daily, quality-check outputs, 30-day audit (AutoIGDM, PathSocial, Google Workspace)
- [ ] **Paperclip dashboard integration** — Mike wants cost dashboard in Paperclip, accessible via Cloudflare
- [ ] **7 additional Anthropic-direct callsites**: `meeting_prep.py`, `protocols.py`, `books.py`, `nhanes.py`, `phase_runtime.py` (x3) — lower priority, `susan_core/` is protection zone

## Mike's Immediate Action Items
1. **Set Anthropic API hard cap**: console.anthropic.com → $500/mo
2. **Cancel Cluely Pro+** ($75/mo) — Claude Code replaces it
3. **Cancel Agents In A Box** ($99/mo) — Susan + Jake replace it
4. **Cancel Apify** ($29/mo) — Firecrawl covers it (just renewed $990/yr)
5. **Check Cloudflare accounts**: Why $160/mo? Should be $5-20
6. **Check Replit dashboard**: replit.com → shut down all deployments
7. **Check Railway**: What's deployed? Consider shutting down.
8. **Check Notion**: Free or paid? Downgrade if paid.
9. **Check 5KM Tech, Canva, Topaz Labs**: What are these? Cut if unused.

## Decisions Made
| Decision | Rationale | Reversible? |
|----------|-----------|-------------|
| Claude Pro KEEP ($210) | Required for Claude Code access | Yes |
| ChatGPT KEEP ($200) | Mike needs Codex | Yes |
| Gemini 2.0 Flash as default agent model | Fastest, cheapest, 1M context, GOOD quality tested | Yes — FORCE_ANTHROPIC=1 |
| DeepSeek V3.2 for deep reasoning | Best cost/quality ratio at $0.64/MTok total | Yes |
| GLM-4.5-Air:free for bulk | $0 cost, GOOD quality, slower (34s) | Yes |
| Obsidian over Notion as primary KB | V15 L2 design, local-first, QMD integration, Git-synced | Yes |
| Claude Code is Claude-only | No OpenRouter/Gemini/DeepSeek possible. Use /model haiku for cheap tasks. | N/A |
| Apify canceled | Firecrawl covers same functionality | Yes (can resubscribe) |

## Context for Next Session
- **Key insight**: The router + client are BUILT and TESTED. The savings are real ($0.0002 vs $0.02 per agent run). Next session should focus on Phase C (Cloudflare infra) and/or Mike's manual cancellation actions.
- **Files to read first**: `docs/plans/2026-03-27-v15-complete-cost-inventory.md`, `jake_cost/router.py`, `agents/base_agent.py`
- **Tests to run first**: `cd susan-team-architect/backend && export $(grep OPENROUTER_API_KEY ~/.jake-vault/secrets.env | xargs) && .venv/bin/python -c "from agents.base_agent import BaseAgent; a = BaseAgent(); print(f'{a.provider.value}: {a.model}')"`
- **Risk**: OpenRouter model IDs can change. If Gemini 2.0 Flash disappears, the router falls through to Anthropic Sonnet (safe fallback).

## Build Health
- Files modified this session: 7 (router.py, openrouter_client.py, base_agent.py, cost-dashboard.html, cost-optimization-plan.md, cancellation-checklist.md, complete-cost-inventory.md)
- Tests passing: router tested, client tested, base_agent tested, FORCE_ANTHROPIC tested
- Context health at close: YELLOW — significant session, recommend fresh context for Phase C
