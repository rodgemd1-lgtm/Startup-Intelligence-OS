# PAI V3X: Ecosystem Supercharge — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Supercharge Jake's agent ecosystem with external knowledge (5,490+ skills, 500+ papers, 127+ agent templates), full observability (OTLP → Supabase), multi-channel webhook routing (Cloudflare Workers), and all 83 Susan agents deployed to OpenClaw messaging channels.

**Architecture:** Git submodules in `vendor/` for external knowledge. OTLP bridge collects agent traces and writes to Supabase. Cloudflare Workers handle multi-channel webhook routing (Telegram/Discord/Slack). OpenClaw workspace files deploy all Susan agents to every channel.

**Depends On:** V0-V3 complete (infrastructure, memory, agents, autonomous pipelines)

**Critical Path:** V4 (proactive intelligence) needs observable agents + multi-channel reach. V5 (learning engine) needs trace data in Supabase. V6 (multi-channel) is partially completed by V3X.

**Build Order:** V0 → V1 → V2 → V3 → **V3X** → V4 → V5 → V6 → V7 → V8 → V9 → V10

**Decisions Already Made (Mike):**
1. All-in on submodules (no phasing)
2. All-in on OpenClaw deployment (every agent, every channel)
3. Supabase for observability (NOT VoltAgent Cloud or DataDog)
4. Cloudflare Workers for edge webhook routing

**Process Rule:** Research → Plan → Execute → Lessons Learned → Documentation. Every time. No exceptions.

---

## Pre-Flight Checklist

- [ ] V3 exit criteria all passed (pipelines running, Orchard MCP working)
- [ ] Supabase project URL and service key available
- [ ] Cloudflare account with Workers enabled
- [ ] OpenClaw running locally (ws://127.0.0.1:18789)
- [ ] GCP OAuth credentials configured (Clawdbot project)
- [ ] Git LFS not needed (submodules are shallow clones)

---

## Phase 3X-A: External Knowledge Submodules

*Add 5 git submodules providing 5,490+ skills, 500+ papers, and 127+ agent templates.*

### Task 1: Add Git Submodules

**Files:**
- Modify: `.gitmodules`
- Create: `vendor/` directory structure

**Submodules to add:**

| Repo | Purpose | Content | Size Est. |
|------|---------|---------|-----------|
| `danielmiessler/fabric` | 233+ prompt patterns | Skills, extractors, analyzers | ~15MB |
| `papers-we-love/papers-we-love` | 500+ CS papers | AI, distributed systems, PLT | ~200MB (shallow) |
| `mergisi/awesome-openclaw-agents` | 162 agent templates | SOUL.md configs, 19 categories | ~5MB |
| `raulvidis/openclaw-multi-agent-kit` | Multi-agent orchestration | Telegram supergroup, bot-to-bot | ~3MB |
| `NousResearch/hermes-agent` | Self-improving agent reference | Gateway, cron, memory patterns | ~50MB |

**Commands:**
```bash
mkdir -p vendor
git submodule add --depth 1 https://github.com/danielmiessler/fabric.git vendor/fabric
git submodule add --depth 1 https://github.com/papers-we-love/papers-we-love.git vendor/papers-we-love
git submodule add --depth 1 https://github.com/mergisi/awesome-openclaw-agents.git vendor/awesome-openclaw-agents
git submodule add --depth 1 https://github.com/raulvidis/openclaw-multi-agent-kit.git vendor/openclaw-multi-agent-kit
git submodule add --depth 1 https://github.com/NousResearch/hermes-agent.git vendor/hermes-agent
```

**Validation:**
```bash
git submodule status
ls vendor/fabric/patterns/ | wc -l    # expect 233+
ls vendor/papers-we-love/ | wc -l     # expect 50+ topic dirs
```

### Task 2: Build Submodule Index

**Files:**
- Create: `pai/knowledge/index.py`
- Create: `pai/knowledge/fabric_index.json`
- Create: `pai/knowledge/papers_index.json`
- Create: `pai/knowledge/agents_index.json`

**What it does:**
- Scans all submodules and builds a searchable JSON index
- Fabric: index pattern name, description, input/output types
- Papers: index by topic, title, relevance tags
- Agents: index SOUL.md templates by category, capabilities
- Index is regenerable via `python -m pai.knowledge.index --rebuild`

### Task 3: Create 4 Knowledge Agents

**Files:**
- Create: `pai/agents/skill_scout.md`
- Create: `pai/agents/paper_harvester.md`
- Create: `pai/agents/codex_analyst.md`
- Create: `pai/agents/pattern_librarian.md`

**Agent definitions:**

| Agent | Role | Primary Data Source |
|-------|------|-------------------|
| skill-scout | Search vendor/ for relevant Fabric patterns and skills | `vendor/fabric/patterns/` |
| paper-harvester | Find and summarize relevant academic papers | `vendor/papers-we-love/` |
| codex-analyst | Analyze code patterns from agent templates | `vendor/awesome-openclaw-agents/`, `vendor/hermes-agent/` |
| pattern-librarian | Cross-reference patterns across all sources | All indexes |

**Validation:**
- Each agent has frontmatter: name, slug, group, description
- Added to `pai/agents/registry.json` under new `knowledge` group
- Callable from Claude Code as sub-agents

---

## Phase 3X-B: Observability (OTLP → Supabase)

*All agent traces stored in Supabase. No third-party observability cloud.*

### Task 4: Create Supabase Schema

**Files:**
- Create: `pai/observability/schema.sql`

**Tables:**
```sql
-- Agent execution traces
CREATE TABLE agent_traces (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    trace_id TEXT NOT NULL,
    span_id TEXT NOT NULL,
    parent_span_id TEXT,
    agent_slug TEXT NOT NULL,
    agent_group TEXT,
    operation TEXT NOT NULL,
    status TEXT DEFAULT 'ok',
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    duration_ms INTEGER,
    input_tokens INTEGER,
    output_tokens INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Pipeline execution runs
CREATE TABLE pipeline_runs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    status TEXT DEFAULT 'running',
    started_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    steps JSONB DEFAULT '[]',
    output JSONB DEFAULT '{}',
    error TEXT
);

-- Indexes
CREATE INDEX idx_traces_agent ON agent_traces(agent_slug);
CREATE INDEX idx_traces_time ON agent_traces(start_time DESC);
CREATE INDEX idx_runs_pipeline ON pipeline_runs(pipeline_name);
CREATE INDEX idx_runs_time ON pipeline_runs(started_at DESC);
```

### Task 5: Build OTLP Bridge

**Files:**
- Create: `pai/observability/bridge.py`
- Create: `pai/observability/collector.py`

**Architecture:**
```
Agent executes → Hook fires → HTTP POST to localhost:4318
                                    ↓
                            OTLP Bridge (Python)
                                    ↓
                            Supabase INSERT
```

**What it does:**
- Lightweight Python HTTP server on port 4318
- Accepts OTLP-format trace data (JSON over HTTP)
- Transforms OTLP spans into `agent_traces` rows
- Batch inserts to Supabase every 5 seconds or 50 spans
- Fallback: write to local SQLite if Supabase unreachable

**LaunchAgent:** `~/Library/LaunchAgents/com.jake.otlp-bridge.plist`

### Task 6: Wire Claude Code Hooks

**Files:**
- Modify: `.claude/settings.json` (add PostToolUse hook for trace emission)
- Create: `bin/hooks/emit-trace.sh`

**Hook behavior:**
- On every PostToolUse, emit a span to the OTLP bridge
- Include: agent name, tool used, duration, token counts, status
- Lightweight — must not add >50ms latency to any tool call

### Task 7: Create Observability Agents

**Files:**
- Create: `pai/agents/voltagent_bridge.md`
- Create: `pai/agents/capability_auditor.md`

| Agent | Role |
|-------|------|
| voltagent-bridge | Manages OTLP bridge, queries traces, generates observability reports |
| capability-auditor | Audits agent capabilities against target state, flags gaps |

---

## Phase 3X-C: Multi-Channel Webhook Routing (Cloudflare Workers)

*Single edge endpoint routes messages to/from Telegram, Discord, Slack.*

### Task 8: Create Cloudflare Worker

**Files:**
- Create: `pai/workers/webhook-router/wrangler.toml`
- Create: `pai/workers/webhook-router/src/index.ts`
- Create: `pai/workers/webhook-router/src/channels/telegram.ts`
- Create: `pai/workers/webhook-router/src/channels/discord.ts`
- Create: `pai/workers/webhook-router/src/channels/slack.ts`

**Architecture:**
```
Telegram webhook → CF Worker → normalize → route to OpenClaw/backend
Discord webhook  →     ↑
Slack webhook    →     ↑
                       ↓
              Response → denormalize → reply on correct channel
```

**Worker logic:**
1. Receive POST from any channel
2. Identify channel from URL path (`/webhook/telegram`, `/webhook/discord`, `/webhook/slack`)
3. Normalize message format: `{ channel, sender, text, metadata }`
4. Route to OpenClaw gateway or direct to Claude Code via MCP
5. Denormalize response and reply on originating channel

**Secrets (via `wrangler secret put`):**
- `TELEGRAM_BOT_TOKEN`
- `DISCORD_BOT_TOKEN`
- `SLACK_BOT_TOKEN`
- `OPENCLAW_GATEWAY_URL`

**Deployment:**
```bash
cd pai/workers/webhook-router
npm install
npx wrangler deploy
npx wrangler secret put TELEGRAM_BOT_TOKEN
```

**Cost:** Free tier = 100K requests/day. At ~100 msgs/day we're at 0.1% of quota.

### Task 9: Create Guardrail Agent

**Files:**
- Create: `pai/agents/guardrail_engineer.md`

| Agent | Role |
|-------|------|
| guardrail-engineer | Safety/quality gates for agent outputs before they reach external channels |

**Guardrail checks:**
- No PII leakage in outbound messages
- No credential exposure
- Message length limits per channel
- Rate limiting per user/channel
- Content safety scoring before send

---

## Phase 3X-D: OpenClaw Full Agent Deployment

*All 83 Susan agents deployed to every OpenClaw messaging channel.*

### Task 10: Generate OpenClaw Workspace Files

**Files:**
- Create: `pai/openclaw/SOUL.md` (Jake's identity for OpenClaw)
- Create: `pai/openclaw/AGENTS.md` (all 83 agents registered)
- Create: `pai/openclaw/HEARTBEAT.md` (scheduled pipeline triggers)
- Create: `pai/openclaw/TOOLS.md` (available tools config)

**AGENTS.md structure:**
```markdown
# Agent Roster

## Routing
- @strategy → strategy group (6 agents)
- @product → product group (9 agents)
- @engineering → engineering group (8 agents)
- @research → research group (6 agents)
- @studio → studio group (12 agents)
- @film → film_studio group (17 agents)
- @science → science group (7 agents)
- @growth → growth group (7 agents)
- @psychology → psychology group (3 agents)
- @knowledge → knowledge group (4 agents) [NEW in V3X]
- @ops → ops group (4 agents) [NEW in V3X]

## Agent Registry
[Auto-generated from pai/agents/registry.json — one entry per agent with slug, group, capabilities]
```

### Task 11: Create OpenClaw Gateway Agent

**Files:**
- Create: `pai/agents/openclaw_gateway.md`

| Agent | Role |
|-------|------|
| openclaw-gateway | Manages OpenClaw channel registration, health checks, agent routing |

### Task 12: Build Registration Script

**Files:**
- Create: `pai/openclaw/register_agents.py`

**What it does:**
- Reads `pai/agents/registry.json`
- For each agent: generates OpenClaw-compatible skill config
- Writes to OpenClaw workspace directory
- Validates all agents are reachable from all channels
- Reports: `83/83 agents registered, 3 channels active`

### Task 13: Wire OpenClaw Multi-Agent Kit Patterns

**Reference:** `vendor/openclaw-multi-agent-kit` (from Phase 3X-A)

**What we adopt:**
- Telegram supergroup architecture (one group per agent domain)
- Bot-to-bot communication pattern (agents can message each other)
- Shared context workflow (context persists across agent handoffs)
- Group routing rules (messages route to correct agent by @mention or /command)

---

## Phase 3X-E: Integration Testing & Validation

### Task 14: End-to-End Test Suite

**Files:**
- Create: `pai/tests/test_v3x_submodules.py`
- Create: `pai/tests/test_v3x_observability.py`
- Create: `pai/tests/test_v3x_webhooks.py`
- Create: `pai/tests/test_v3x_openclaw.py`

**Test matrix:**

| Test | What it validates |
|------|------------------|
| Submodule integrity | All 5 submodules clone, indexes build |
| Fabric pattern count | >= 233 patterns indexed |
| OTLP bridge | Trace received → Supabase row created |
| Webhook routing | Telegram msg → CF Worker → normalized → response |
| Agent registration | 83+ agents visible in OpenClaw |
| Guardrail checks | PII blocked, rate limits enforced |
| Cross-channel | Same query via Telegram and Discord → same answer |

### Task 15: Update Agent Registry

**Files:**
- Modify: `pai/agents/registry.json`

**Add 8 new agents:**
- knowledge group: skill-scout, paper-harvester, codex-analyst, pattern-librarian
- ops group: voltagent-bridge, openclaw-gateway, guardrail-engineer, capability-auditor

**New totals:** 91 agents, 14 groups, 18 routing categories

---

## Exit Criteria

| # | Criterion | How to verify |
|---|-----------|--------------|
| 1 | 5 submodules cloned and indexed | `git submodule status` shows 5 clean |
| 2 | Knowledge indexes built | `pai/knowledge/*_index.json` exist, >5000 entries total |
| 3 | 8 new agents registered | `registry.json` shows 91 agents, 14 groups |
| 4 | OTLP bridge running | `curl localhost:4318/health` returns 200 |
| 5 | Traces in Supabase | `SELECT count(*) FROM agent_traces` > 0 |
| 6 | CF Worker deployed | `curl https://jake-webhooks.<domain>.workers.dev/health` returns 200 |
| 7 | Telegram webhook via CF | Send test message → get response via CF Worker |
| 8 | All agents in OpenClaw | `openclaw agents list` shows 91 |
| 9 | Guardrails active | PII test blocked, rate limit test throttled |
| 10 | Cross-channel test passes | Same query via 2+ channels → same answer |

---

## Risk Register

| Risk | Mitigation |
|------|-----------|
| Submodules bloat repo | Shallow clones (`--depth 1`), `.gitmodules` tracks only |
| Supabase rate limits | Batch inserts (50/5s), local SQLite fallback |
| CF Worker cold starts | Keep worker warm with `/health` pings |
| OpenClaw API changes | Pin to specific OpenClaw release |
| Agent count overwhelms routing | Group-based routing, not individual agent routing |

---

## Estimated Effort

| Phase | Tasks | Est. Hours |
|-------|-------|-----------|
| 3X-A: Submodules + Knowledge | 3 tasks | 3-4h |
| 3X-B: Observability | 4 tasks | 4-5h |
| 3X-C: Webhook Routing | 2 tasks | 3-4h |
| 3X-D: OpenClaw Deployment | 4 tasks | 3-4h |
| 3X-E: Testing | 2 tasks | 2-3h |
| **Total** | **15 tasks** | **15-20h** |

---

## Research Sources

- Existing: `.claude/docs/hermes-openclaw-ecosystem-research.md`
- New: `.claude/docs/research-packet--voltagent-framework.md`
- New: `.claude/docs/research-packet--agent-skills-and-papers.md`
- Reference: `vendor/openclaw-multi-agent-kit` (production multi-agent patterns)
- Reference: `vendor/fabric/patterns/` (233+ prompt patterns)
