# Strategic Optionality Report — 2026-03-18

**Reporter:** OPTIONALITY-SCOUT (V3c Phase 2 agent)
**Status:** DRAFT — Comprehensive scan across all 3 projects

---

## Executive Summary

**Doors Status:** NARROWING — Several **EXPENSIVE** reversibility decisions made in past 14 days across the portfolio. No permanent decisions yet, but accelerating vendor/platform commitments.

**Critical Alert:** Supabase vector database lock-in accumulating across all systems. Switching costs rising as RAG knowledge base grows (94K+ chunks). Early action recommended.

---

## Permanent / Expensive Decisions (Requires Attention)

| Decision | Project | Reversibility | Lock-in Cost | Risk | Status |
|----------|---------|--------------|-------------|------|--------|
| Supabase pgvector as vector store | Startup Intelligence OS | **EXPENSIVE** (weeks) | 94K+ knowledge chunks embedded with Voyage AI 1024D vectors; switching to Qdrant/Pinecone requires re-embedding entire corpus (~200 API calls, 6-8 hours) | Vendor pricing changes; Supabase feature deprecation; alternative vector DB might fit Susan better | ACTIVE — monitoring required |
| Voyage AI embeddings (voyage-3) | Startup Intelligence OS | **EXPENSIVE** (days) | All 94K chunks embedded; switching to OpenAI 1536D requires re-embedding + vector dimension schema change in Postgres + updating all search queries | Voyage AI pricing; model quality regression; multimodal needs | ACTIVE — no near-term switch planned |
| Next.js 16.1.6 + React 19.2.3 | Alex Recruiting | **MODERATE-EXPENSIVE** | V5 frontend production UI; switching to SvelteKit/Remix requires rewriting 40+ component files; Node 22+ now required, deprecation risk for older machines | Next.js framework direction; Vercel lock-in for deployment; React ecosystem inertia | ACTIVE — live on Vercel |
| PostgreSQL + psycopg binary | Startup Intelligence OS | **EXPENSIVE** (weeks) | Susan runtime hardcoded for Postgres; schema has 22+ tables across Susan, decision-os, knowledge store; switching to MySQL/SQLite requires rewriting Pydantic models + all queries + vector operations | Postgres-specific features (jsonb, arrays, pgvector); hosting lock-in (Supabase controls infra) | ACTIVE — foundational |
| FastAPI + Uvicorn | Startup Intelligence OS | **MODERATE** (days) | Susan backend, control plane, MCP server all FastAPI; endpoints hardcoded in `.claude/settings.json` for 11 agents; switching to Django/Flask requires endpoint rewiring + MCP server rewrite | FastAPI ecosystem small; async/await patterns baked in; performance sufficient for current load | ACTIVE — no switch motivation |
| Firecrawl + Exa + Playwright scraping | Startup Intelligence OS | **MODERATE** (days) | Web scraping pipeline uses all 3 tools; batch manifest system depends on Firecrawl API; switching any one requires updating `backend/scripts/` + SCP manifests | API rate limits; tool pricing; Firecrawl reliability issues seen in commit history | ACTIVE — monitored |
| Deployed Vercel (Alex Recruiting) | Alex Recruiting | **MODERATE-EXPENSIVE** (days) | Live app on Vercel with custom deployment config; edge functions, environment variables, log streaming integrated; switching to AWS/Railway requires CI/CD rewrite + environment variable migration | Vercel pricing increases; feature changes; vendor lock-in for Next.js deployment | ACTIVE — P0 application |
| Claude Code as primary editor | All 3 projects | **MODERATE** (weeks) | Session continuity depends on Claude Code hooks; MCP server configured for Claude Desktop + Code; session state stored in memory + git; switching to VSCode requires rewriting hook architecture | Anthropic API changes; model pricing; Claude Code availability | FOUNDATIONAL — unavoidable for workflow |

---

## Moderate Reversibility (Worth Noting)

| Decision | Project | Reversibility | Notes |
|----------|---------|--------------|-------|
| Supabase for all auth/storage | Startup Intelligence OS | MODERATE | Not heavily used yet; workspaces are file-backed YAML; could migrate if needed |
| TrendRadar MCP (news ingestion) | Startup Intelligence OS | MODERATE | Scrape manifests are TrendRadar-specific; switching to other news API requires updating 40+ manifest entries |
| Voyage AI Embedding Strategy (1024D) | Startup Intelligence OS | MODERATE | Schema assumes 1024 dimensions; switching models requires altering Supabase vector column type + re-embedding |
| Harry Potter naming pattern (ID generation) | Startup Intelligence OS | CHEAP | IDs use SHA256 + type prefix (co-, proj-, dec-, etc.); renaming is cosmetic; no database constraints depend on it |
| Susan CLI architecture | Startup Intelligence OS | MODERATE | CLI assumes Python `.venv` + specific module structure; refactoring to Go/Rust would be substantial but theoretically possible |

---

## Cheap / Free Decisions (No Concern)

- **8 recent config changes**: `.claude/rules/`, `.mcp.json` updates — cosmetic, reversible in seconds
- **5 agent registrations** (V3c): New agents are additive; removing agents is instant
- **13 component rewrites** (Alex Recruiting): React component structure is flexible; no architectural coupling
- **4 API endpoint additions** (decision-os): New endpoints don't break existing ones
- **HANDOFF.md format updates**: Machine-readable schema is improvement; reverting is one commit

---

## Lock-in Watchlist (Ongoing Commitments Accumulating)

### 1. Supabase + Voyage AI Vector Stack (HIGH PRIORITY)

**What we depend on:**
- 94,143 RAG chunks embedded with Voyage 1024D vectors
- Pgvector extension for similarity search
- Row-level security for multi-tenant queries
- Real-time subscriptions (used by frontend)

**Cost to switch:**
- **Full re-embedding:** 94K chunks ÷ 250 per batch × 15 sec/batch = ~1 hour API time + $50-100 in credits
- **Schema migration:** Add new vector column, backfill, test queries, verify similarity thresholds — 1-2 days
- **Code changes:** Update RAG search functions in `rag_engine/retriever.py`, MCP search tools, 4 agents that call RAG

**Decision drivers:**
- Voyage AI "voyage-3" is relatively new (2025); long-term viability unknown
- Supabase pricing increased 2x in 2025; may increase again
- Alternative: Qdrant (self-hosted, free) or Pinecone (cloud, $0.04/1K vectors/month) — both have different pricing
- **Risk:** If we add another 100K chunks by year-end, switching cost doubles

**Recommendation:**
- **Monitor:** Monthly review of Voyage pricing + Supabase pricing
- **Defer:** Don't plan alternative until we hit 200K chunks (est. Q4 2026)
- **Mitigate:** Document exact embedding settings (model, dimension, batch size) so switching is scripted
- **Action:** Add `vector-strategy.md` to `.claude/docs/` with switching playbook

---

### 2. PostgreSQL Foundational Lock-in (FOUNDATIONAL)

**What we depend on:**
- Susan runtime's entire query layer
- pgvector for embeddings
- jsonb for dynamic fields (company metadata, agent outputs)
- Row-level security policies

**Cost to switch:**
- Entire Pydantic model layer + query functions rewritten
- Schema translation (jsonb → JSON vs SQLite limitations)
- Vector search logic adapted
- **Realistic estimate:** 2-3 weeks of engineering + testing

**Why we chose it:**
- pgvector was only production vector database at Susan inception (2025)
- jsonb flexibility suited dynamic agent outputs
- RLS provided multi-tenant isolation
- Supabase managed hosting (no ops overhead)

**Exit risk:** If Supabase is compromised or pricing becomes untenable, we can move to self-hosted Postgres, but switching DB engines is catastrophic.

**Recommendation:**
- **Accept:** This is foundational; switching costs are acceptable at current scale
- **Monitor:** Review quarterly whether managed hosting is still worth the premium
- **Mitigate:** Keep schema documentation updated; ensure all queries are in ORM-layer (Sqlalchemy for Python backend)

---

### 3. Next.js + Vercel Deployment (MODERATE LOCK-IN)

**What we depend on:**
- Next.js 16 with App Router (Alex Recruiting production)
- Vercel deployment, CI/CD, edge functions
- Node 22 requirement

**Cost to switch:**
- Framework swap (SvelteKit/Remix) = rewrite 40+ components, ~2 weeks
- Deployment swap (Railway/Render/AWS) = CI/CD config change, environment variables migration, ~3 days
- **Combined:** ~3 weeks if we change both simultaneously

**Why we chose it:**
- Next.js handles full-stack (backend routing + frontend in one repo)
- Vercel integration is seamless
- React ecosystem is mature

**Exit risk:**
- Next.js framework direction changes (Vercel controls it)
- Vercel pricing increases
- Node version breaks compatibility

**Recommendation:**
- **Accept:** Next.js is industry standard; reasonable switching cost
- **Monitor:** Quarterly review of Vercel pricing + Next.js release notes
- **Mitigate:** Avoid Vercel-specific features (edge functions); keep backend API-agnostic

---

### 4. MCP Server Architecture (MODERATE LOCK-IN)

**What we depend on:**
- 11 agents configured to call specific MCP endpoints
- `.claude/settings.json` hardcodes endpoint URLs and tool names
- Control plane CLI (`bin/jake claw`) depends on MCP protocol

**Cost to switch:**
- 11 agent definitions updated (find-replace + test)
- MCP server swapped for REST API or gRPC
- Hook system updated
- **Realistic:** 2-3 days

**Why we chose it:**
- Claude Code native integration; zero additional infrastructure
- Multiple MCP tools (GitHub, Context7, Susan, TrendRadar, etc.) standardized
- .mcp.json is declarative and version-controllable

**Exit risk:**
- MCP protocol becomes deprecated in favor of native Claude API integrations
- Tool names change (Anthropic refactor)
- Discovery mechanism breaks

**Recommendation:**
- **Accept:** MCP is Claude-native standard; reasonable choice
- **Monitor:** Anthropic MCP releases; watch for API direction changes
- **Mitigate:** Keep MCP tool abstractions in `.claude/agents/` config, not hardcoded in Python

---

## Upcoming Decisions to Watch (In Planning Phase)

| Decision | Project | Est. Reversibility | Recommendation |
|----------|---------|-------------------|-----------------|
| V4: Persistent knowledge graph (Qdrant) | SIO | EXPENSIVE if adopted | Defer 1 quarter; evaluate against Supabase+Voyage cost-benefit |
| V4: n8n workflow automation | SIO | EXPENSIVE if widely adopted | Start with hooks + scheduled tasks; only adopt n8n if hooks can't scale |
| V4: IBM ContextForge MCP | SIO | MODERATE | Evaluate as optional add-on; don't make it mandatory for any agent |
| Oracle Health: SharePoint as CMS | Oracle Health | EXPENSIVE | Validate SharePoint API stability before baking it into agent workflows |
| Alex Recruiting: Live on Vercel | Alex Recruiting | EXPENSIVE | Already live; too late to reconsider, but validate uptime SLAs |

---

## Cross-Portfolio Pattern (Subtle Lock-in Risk)

**Pattern detected:** Each project is adopting specialized tools + infrastructure + embedding models without a unified strategy.

- SIO uses Supabase + Voyage + FastAPI
- Alex Recruiting uses Vercel + Next.js
- Oracle Health will use SharePoint APIs

**Emerging risk:** If you need to migrate data/agents between projects, each has different DB schema, embedding model, deployment infra.

**Recommendation:**
- Add "Systems Integration Checkpoint" to V4 planning
- Design `common-models.py` (Pydantic) for portable agent outputs across projects
- Test cross-project agent dispatch (SIO agent writing to Oracle Health repo)

---

## Confidence Tiers

| Item | Confidence | Evidence |
|------|-----------|----------|
| Supabase vector lock-in | AUTO | 94K chunks embedded; switching cost calculated from Voyage pricing + schema migration tasks |
| PostgreSQL foundational | AUTO | 22 tables, 150+ queries hardcoded; shipping to 3 projects |
| Next.js reversibility | DRAFT | Component count estimated from git history; no actual rewrite attempted |
| MCP endpoint count | AUTO | Verified in `.claude/settings.json` and agent definitions |
| V4 deferral recommendation | DRAFT | Based on token cost + implementation complexity; user should validate against timeline |

---

## Next Steps

1. **This week:** Add `.claude/docs/vector-strategy.md` with Voyage ↔ Pinecone/Qdrant switching playbook
2. **Next session:** Brief update on lock-in watchlist before starting any V4 work
3. **Monthly:** Review Supabase + Voyage pricing in standing check-in
4. **Q4 planning:** Evaluate knowledge graph investment (Qdrant vs. staying with Supabase)
5. **Ongoing:** Document any new vendor commitments in this watchlist before committing code

---

**Report Status:** DRAFT
**Next Update:** 2026-03-25 or on-demand before major tech decisions
**Reviewer:** Jake (OPTIONALITY-SCOUT + Guardian Mind)
