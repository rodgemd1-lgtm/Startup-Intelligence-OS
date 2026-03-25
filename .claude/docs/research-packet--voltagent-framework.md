# Research Packet: VoltAgent Framework & OTLP Observability

**Date:** 2026-03-25
**Researcher:** Jake (VoltAgent research agent)
**Decision:** Use OTLP standard, route to Supabase. NOT VoltAgent Cloud.

---

## What Is VoltAgent?

Open-source TypeScript-first AI agent framework with built-in observability.
- **Repo:** [VoltAgent/voltagent](https://github.com/VoltAgent/voltagent) — 5,100+ stars
- **Core packages:** `@voltagent/core` (runtime), `@voltagent/server-hono` (HTTP on port 3141), `@voltagent/logger`, `@voltagent/libsql`
- **Observability:** Built on OpenTelemetry (OTLP over HTTP). Auto-exports when `VOLTAGENT_PUBLIC_KEY`/`VOLTAGENT_SECRET_KEY` are set.
- **Batching:** maxQueueSize 4096, maxExportBatchSize 512, scheduledDelayMillis 4000

## Two Paths to Custom Observability

### Path A: VoltAgent Storage Adapter (Step Data)
- Pluggable adapters: InMemory, LibSQL, Supabase, Postgres
- Covers agent execution records in VoltAgent-specific format
- Not raw OTLP spans — structured step/conversation data

### Path B: OTLP Export to Custom Backend (Trace Data)
- Standard OTLP HTTP endpoint at `localhost:4318`
- Any OTLP-compatible collector can receive
- No off-the-shelf OTel Collector exporter writes directly to Supabase Postgres
- **Our approach:** Lightweight Python bridge on 4318 → batch INSERT to Supabase

## Our Architecture (Decided)

```
Claude Code hook → emit-trace.sh → HTTP POST localhost:4318
                                          ↓
                                   Python OTLP Bridge
                                          ↓
                                   Supabase (agent_traces table)
                                          ↓
                                   Local SQLite fallback
```

**Why not VoltAgent Cloud:** We want full data ownership. Supabase gives us queryable traces with SQL + real-time subscriptions for dashboards.

**Why not DataDog/LangSmith:** Cost. We're <1000 traces/day. Self-hosted Supabase is free-tier compatible.

## Alternatives Assessed

| Tool | Type | Self-hosted? | Cost | Verdict |
|------|------|-------------|------|---------|
| VoltAgent Cloud | SaaS | No | Free tier exists | No — data ownership |
| Langfuse | Open-source | Yes (Docker) | Free self-hosted | Good alternative, heavier setup |
| LangSmith | SaaS | No | $39/mo+ | No — lock-in |
| Phoenix/Arize | Open-source | Yes | Free self-hosted | Good for evals, overkill for traces |
| **Custom OTLP → Supabase** | **Custom** | **Yes** | **Free** | **CHOSEN** |

## Key Implementation Notes

1. Bridge is ~200 lines of Python (FastAPI/aiohttp)
2. Schema: `agent_traces` table with trace_id, span_id, agent_slug, operation, duration_ms, tokens, metadata JSONB
3. Batch insert every 5s or 50 spans (whichever comes first)
4. Health endpoint at `localhost:4318/health`
5. LaunchAgent for auto-start
