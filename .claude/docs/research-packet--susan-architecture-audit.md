# Susan Agent Architecture Audit — Research Packet
**Date:** 2026-03-25
**Purpose:** Complete audit of current Susan agent architecture for VoltAgent redesign

---

## Summary

- **96 total unique agents** across Susan (81) and Claude Code (15 unique)
- **Zero agents have tool definitions** — all are pure system prompts
- **Zero supervisor hierarchy** — completely flat
- **Zero durable memory** (3 CC agents have project memory)
- **No workflow engine** — sequential pipeline only
- **No error handling/retry**
- **No observability spans** — basic Supabase logging only
- **77 of 81 agents are simple prompt-only** — automatable migration
- **10,409 lines of prompt content** — the domain knowledge asset to preserve
- **10,788+ RAG chunks** — existing knowledge base

## Agent Distribution

| Group | Count | Models |
|-------|-------|--------|
| orchestration | 1 | sonnet |
| strategy | 6 | opus(1), sonnet(4), haiku(1) |
| product | 9 | all sonnet |
| engineering | 8 | sonnet(7), haiku(1) |
| science | 7 | sonnet(6), haiku(1) |
| psychology | 3 | all sonnet |
| growth | 7 | all sonnet |
| research | 6 | sonnet(5), haiku(1) |
| studio | 12 | all sonnet |
| film_studio | 17 | all sonnet |
| slideworks | 3 | all opus |
| oracle_health | 2 | all sonnet |

## Architecture Gaps vs VoltAgent

| Dimension | Current | VoltAgent Standard |
|-----------|---------|-------------------|
| Tool definitions | 0 agents | Zod-typed tools on every agent |
| Supervisor hierarchy | Flat | Auto supervisor → sub-agent trees |
| Typed I/O schemas | 0 agents | Zod input/output on every agent |
| Durable memory | None | 3-tier: storage + embedding + vector |
| Workflow engine | Sequential only | 17 step types (conditional, parallel, loops, suspend/resume) |
| Error handling | None | Retry, fallback chains, circuit breakers |
| Observability | Basic logging | OpenTelemetry spans, 12 agent hooks |
| Guardrails | None | Input/output guardrails, PII redaction, prompt injection |
| Middleware | None | Retry-capable input/output middleware |
| Tool routing | None | Semantic search over tool pools |
| Model fallback | None | Ordered fallback chains with retry |

## Strengths to Preserve

1. **Domain knowledge depth** — 10,409 lines of expert prompts with frameworks, contrarian beliefs, failure modes
2. **Consistent template** — every agent follows the same 15-section structure
3. **RAG integration** — 10,788+ chunks with Voyage AI embeddings, per-agent data type scoping
4. **Routing registry** — 30 topic categories mapping to agent lists
5. **Behavioral economics injection** — every agent gets a BE audit checklist
6. **Pydantic schemas** — 40+ models for phase outputs and control plane
7. **Cost tracking** — per-run Supabase logging with tokens, cost, duration

## Migration Estimate

| Category | Count | Effort | Method |
|----------|-------|--------|--------|
| Simple prompt-only agents | 77 | 1-2 days | Automated converter script |
| Complex agents (routing/workflow) | 4 | 2-3 days each | Manual port |
| CC operational agents | 15 | 1 week | Architecture decision needed |
| Backend runtime replacement | 1 | 1-2 weeks | Full rewrite to VoltAgent |

## Key Files

- `susan-team-architect/agents/*.md` — 81 agent definitions
- `pai/agents/registry.json` — routing registry
- `susan-team-architect/backend/agents/base_agent.py` — runtime base
- `susan-team-architect/backend/susan_core/orchestrator.py` — phase pipeline
- `susan-team-architect/backend/susan_core/router.py` — model routing
- `susan-team-architect/backend/susan_core/schemas.py` — Pydantic output schemas
- `susan-team-architect/backend/control_plane/prompts.py` — prompt compiler
- `susan-team-architect/backend/mcp_server/server.py` — MCP tool server
