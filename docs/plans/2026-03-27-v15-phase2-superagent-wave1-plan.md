# V15 Phase 2: Superagent Wave 1 + Memory — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Upgrade Jake, KIRA, ARIA, SCOUT, Steve, and Compass to full superagents with SuperMemory-backed memory, heartbeat scheduling via Paperclip, and lossless context management.

**Architecture:** Each superagent gets: own SuperMemory container, Paperclip agent registration, heartbeat schedule, budget cap, and goal alignment to JakeStudio company goals.

**Parent Design:** `docs/plans/2026-03-27-v15-personal-ai-infrastructure-design.md` (R4)

**Depends on:** Phase 1 (Cloud Foundation) — COMPLETE

**Estimated Sessions:** 2-3

---

## Prerequisites

Before starting Phase 2, verify Phase 1 is live:
- [x] OpenClaw 2026.3.24 gateway running (LaunchAgent)
- [x] Cloudflare Tunnel to jake.jakestudio.ai (LaunchAgent)
- [x] Jake Gateway Worker deployed (jake-gateway.rodgemd1.workers.dev)
- [x] SuperMemory.ai API working (key stored in ~/.hermes/.env)
- [x] QMD 2.0.1 indexed (311 docs, 6,053 chunks, MCP configured)
- [x] Paperclip running at localhost:3100 with JakeStudio company
- [ ] R2 bucket created (needs dashboard enablement)
- [ ] Zero Trust access policy (manual — Cloudflare dashboard)
- [ ] SuperMemory connectors (Gmail, Notion, GitHub, Drive — manual)

---

## Task 1: Create SuperMemory Containers for Wave 1 Agents

**Files:**
- Reference: SuperMemory.ai API docs

**Step 1: Create container tags for each Wave 1 agent**

```bash
# Via SuperMemory API — create isolated memory containers
# Containers: jake, kira, aria, scout, steve, compass, shared
```

Use the SuperMemory v4 API to add a test memory to each container, confirming container creation:

- `jake` — Jake's personal memories, preferences, decisions
- `kira` — Command routing intelligence, intent patterns
- `aria` — Daily brief context, email summaries, calendar
- `scout` — Competitive intelligence, market signals
- `steve` — Strategy decisions, business analysis
- `compass` — Product roadmap, feature priorities
- `shared` — Cross-agent knowledge visible to all

**Step 2: Verify all containers exist**

Search each container to confirm it was created.

**Step 3: Seed containers with existing knowledge**

Migrate relevant Claude Code memory files to SuperMemory:
- `jake_personality.md` → `jake` container
- `user_mike_profile.md` → `shared` container
- `project_portfolio_full.md` → `shared` container
- KIRA/ARIA/SCOUT agent definitions → respective containers

---

## Task 2: Register Wave 1 Agents in Paperclip

**Files:**
- Reference: Paperclip API at localhost:3100

**Step 1: Register Jake as lead agent**

```bash
curl -X POST http://localhost:3100/api/agents -H "Content-Type: application/json" -d '{
  "name": "Jake",
  "role": "Chief of Staff / Lead PA",
  "companyId": "<jakestudio-id>",
  "adapter": "openclaw",
  "budgetMonthlyCents": 5000,
  "heartbeatIntervalMs": 900000
}'
```

**Step 2: Register remaining Wave 1 agents**

Register each with appropriate role, budget, and heartbeat:
- KIRA — Command Router, $5/mo, 15min heartbeat
- ARIA — Daily Operations, $10/mo, 1hr heartbeat
- SCOUT — Competitive Intel, $5/mo, 6hr heartbeat
- Steve — Strategy Lead, $5/mo, disabled heartbeat (on-demand)
- Compass — Product Lead, $5/mo, disabled heartbeat (on-demand)

**Step 3: Verify all agents show in Paperclip dashboard**

Open http://localhost:3100 and confirm 6 agents under JakeStudio.

---

## Task 3: Install lossless-claw for Infinite Context

**Files:**
- Modify: `~/.openclaw/openclaw.json` (plugin config)
- Reference: github.com/martian-engineering/lossless-claw

**Step 1: Install lossless-claw**

```bash
npm i -g lossless-claw
# OR install as OpenClaw plugin
openclaw plugins install martian-engineering/lossless-claw
```

**Step 2: Configure compaction threshold**

Set to 75% (vs current 60% hard limit):
- Auto-flush memory to SuperMemory before compaction
- Summarize with Haiku to save costs
- Store full DAG in Cloudflare R2 (when enabled)

**Step 3: Test context preservation**

Start a conversation, fill context to 75%, verify lossless-claw compacts without losing information. Search compacted content via `lcm_grep`.

---

## Task 4: Wire SuperMemory MCP to Claude Code

**Files:**
- Modify: `.mcp.json` (add SuperMemory MCP server)

**Step 1: Check if SuperMemory has an MCP server**

Research SuperMemory.ai docs for MCP integration or build a thin MCP wrapper.

**Step 2: Add SuperMemory MCP to project config**

Either install their MCP server or create a minimal one that wraps the v4 API.

**Step 3: Test from Claude Code**

Use the MCP tools to:
- Add a memory to the `jake` container
- Search across containers
- List recent memories

---

## Task 5: Create Superagent OpenClaw Configs

**Files:**
- Modify: `~/.openclaw/agents/` (agent workspace configs)

**Step 1: Upgrade Jake's OpenClaw agent config**

Add to Jake's agent config:
- SuperMemory container: `jake`
- Memory flush on session end
- Goal hierarchy connected to Paperclip
- Heartbeat handler

**Step 2: Create KIRA agent in OpenClaw**

KIRA routes commands to the right agent. Config includes:
- Intent classification patterns
- Agent routing table
- SuperMemory container: `kira`

**Step 3: Create ARIA agent in OpenClaw**

ARIA handles daily operations. Config includes:
- Email triage skill
- Calendar awareness
- Daily brief generation
- SuperMemory container: `aria`

**Step 4: Create SCOUT agent in OpenClaw**

SCOUT monitors competitive landscape. Config includes:
- TrendRadar integration
- Competitor tracking
- SuperMemory container: `scout`

**Step 5: Create Steve and Compass agents**

On-demand agents for strategy and product:
- Steve: strategy analysis, decision framing
- Compass: roadmap prioritization, feature specs

---

## Task 6: Test Full Superagent Loop

**Step 1: Test Jake → SuperMemory → Paperclip flow**

Send a message to Jake via Telegram. Verify:
- Jake receives it (OpenClaw gateway)
- Jake stores context in SuperMemory (`jake` container)
- Jake's activity shows in Paperclip dashboard
- Heartbeat fires and reports status

**Step 2: Test KIRA routing**

Ask Jake to route a task to SCOUT. Verify KIRA:
- Classifies the intent
- Routes to SCOUT
- SCOUT writes findings to `scout` container
- Results visible from Jake's context

**Step 3: Test cross-agent memory**

Have ARIA write a daily brief finding. Verify Jake can access it through `shared` container.

---

## Phase 2 Exit Criteria

- [ ] 6 SuperMemory containers created and seeded
- [ ] 6 agents registered in Paperclip with budgets
- [ ] lossless-claw installed and configured (75% threshold)
- [ ] SuperMemory accessible from Claude Code via MCP
- [ ] Jake, KIRA, ARIA superagent configs in OpenClaw
- [ ] SCOUT, Steve, Compass superagent configs in OpenClaw
- [ ] Full loop test: message → route → execute → memory → dashboard
- [ ] Cross-agent memory working (shared container)
- [ ] Heartbeat scheduling active for Jake, KIRA, ARIA, SCOUT

---

## Phase 2 → Phase 3 Handoff

Phase 3: Obsidian Integration + Process Engine
- ObsidianClaw plugin for in-vault chat
- GStack-inspired process skills (Think→Plan→Build→Review→QA→Ship)
- Obsidian vault synced between desktop + laptop
- QMD deep integration with OpenClaw
