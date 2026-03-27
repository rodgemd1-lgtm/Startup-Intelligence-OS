# V15 Research Findings — Complete Reference

**Date**: 2026-03-27
**Research Agents Dispatched**: 8 (all completed)
**Total Sources**: 42 GitHub repos, 32 YouTube videos, 7 products deep-researched

---

## Tier 1: Core Ecosystem (Install These)

### OpenClaw v2026.3.24
- **Repo**: github.com/openclaw/openclaw (331K+ stars)
- **What**: Open-source PA framework. Gateway + skills + memory + 50+ integrations.
- **Key features in v2026.3.24**: Auto-flush before compaction, hybrid BM25+vector search, gateway restart recovery, `before_dispatch` hook, Obsidian integration.
- **Memory**: 3-tier (ephemeral daily logs, durable MEMORY.md, session transcripts). Local embedding fallback chain.
- **Multi-device**: Tailscale (recommended) or Cloudflare Tunnel (enterprise). We're using Cloudflare.
- **Install**: `npm i -g openclaw` (Node 24)

### Paperclip AI
- **Repo**: github.com/paperclipai/paperclip (34K stars, 24 days old)
- **What**: Multi-company orchestration control plane. "If OpenClaw is an employee, Paperclip is the company."
- **Key features**: Org charts, budgets, tickets, governance, heartbeats, 7 agent adapters (incl. OpenClaw + Claude).
- **Tech**: TypeScript monorepo, Express, Drizzle ORM, PostgreSQL (embedded PGlite for dev).
- **Risk**: 24 days old, bus factor (1 contributor has 85% of commits).
- **Install**: `npx paperclipai onboard`

### SuperMemory.ai
- **Product**: supermemory.ai (19.6K GitHub stars, $2.6M raised)
- **What**: Memory infrastructure for AI agents. Decay, contradiction resolution, auto-connectors.
- **Key features**: 3-tier storage (hot KV, warm pgvector, cold), intelligent decay, context rewriting, MCP server.
- **Connectors**: Gmail, Notion, Drive, GitHub, S3, Slack, OneDrive, web crawler.
- **Pricing**: $19/mo Pro (3M tokens), $399/mo Scale (80M tokens).
- **Install**: API signup + MCP server or Claude Code plugin.

### QMD (Tobi Lütke / Shopify)
- **Repo**: github.com/tobi/qmd (17K stars)
- **What**: On-device search engine for personal knowledge. BM25 + vector + LLM reranking.
- **Key features**: SQLite storage, 3 local GGUF models, smart markdown chunking, context annotations.
- **MCP**: 4 tools (query, get, multi_get, status).
- **Install**: `claude plugin add tobi/qmd`

### Martian lossless-claw
- **Repo**: github.com/Martian-Engineering/lossless-claw (3.5K stars)
- **What**: DAG-based lossless context compaction for OpenClaw.
- **Key features**: Preserves every message, summarizes in DAG nodes, tools (lcm_grep, lcm_describe, lcm_expand).
- **Config**: freshTailCount=32, contextThreshold=0.75, can pin to Haiku for cheap summaries.
- **Install**: OpenClaw plugin.

---

## Tier 2: Architecture Patterns (Study These)

### GStack (Garry Tan, YC)
- **Repo**: github.com/garrytan/gstack (50K stars)
- **What**: Process-as-code skills for Claude Code. Think→Plan→Build→Review→QA→Ship.
- **Notable**: 600K+ LOC in 60 days. 20+ skills including /qa (real Playwright browser), /codex (cross-model review), /browse (headed Chrome).
- **Pattern to adopt**: Process skills mapped to Jake's 4-Mind model.

### Martian agent-memory
- **Repo**: github.com/Martian-Engineering/agent-memory
- **What**: 3-layer bash/jq memory: Knowledge Graph + Daily Notes + Tacit Knowledge.
- **Key patterns**: Exponential recency decay (30-day half-life), Jaccard deduplication (70%), contradiction detection.

### TechNickAI/openclaw-config
- **Repo**: github.com/TechNickAI/openclaw-config
- **What**: Reference power-user setup. 3-tier memory, 11 skills, 4 autonomous workflows.

### Daniel Miessler Ecosystem
- **PAI** (Personal_AI_Infrastructure): v4.0.3 — the philosophical blueprint.
- **Telos**: Structured self-knowledge (mission, goals, problems, strategies).
- **Fabric**: 233 prompt patterns.
- **Substrate**: Collective intelligence framework.
- **Daemon**: AI-to-AI communication API.
- **Ladder**: Autonomous optimization engine.
- **TheAlgorithm**: 7-phase execution loop + ISC methodology.

### Khoj
- **Repo**: github.com/khoj-ai/khoj (25K+ stars)
- **What**: Self-hosted AI second brain. Multi-device (Browser, Obsidian, Desktop, Phone, WhatsApp).

---

## Tier 3: Useful References

| Repo | What | Pattern |
|------|------|---------|
| openclaw-studio | Web dashboard for OpenClaw | Dashboard UI |
| context-infrastructure | Context engineering for AI agents | WISC-like |
| shad (Shannon's Daemon) | PAI + Obsidian + knowledge graph | Obsidian-first PA |
| mcp-memory-sqlite | SQLite memory via MCP | MCP memory |
| claude_code_agent_farm | 20+ parallel Claude Code agents | Multi-agent orchestration |
| Auto-claude-code-research-in-sleep | Autonomous ML research skills | Research daemon |
| arrowhead | Obsidian-aware search for OpenClaw | Obsidian bridge |
| life-pilot-agent | PA with Telegram + Obsidian + Todoist | Multi-integration PA |
| openclaw-ops | Manage OpenClaw via SSH | Remote ops |

---

## YouTube Priority Watch List

### Tier 1 — Must Watch (7 videos)
1. Miessler PAI v2.0 Deep Dive — youtube.com/watch?v=Le0DLrn7ta0
2. How Miessler's Projects Fit Together — youtube.com/watch?v=5x4s2d3YWak
3. Pioneering PAI (Cognitive Revolution) — youtube.com/watch?v=DbNUDMcEjzY
4. The Only OpenClaw Tutorial You Need — youtube.com/watch?v=CxErCGVo-oo
5. 100 Hours of OpenClaw Lessons — youtube.com/watch?v=_kZCoW-Qxnc
6. OpenClaw Memory Sucks + Fix — youtube.com/watch?v=Io0mAsHkiRY
7. Every Memory Plugin Tested — youtube.com/watch?v=u-rDW_wTtWM

### Tier 2 — High Value (11 videos)
8-18. See full YouTube research output for links.

### Mike's 4 Videos (Analyzed)
- OpenClaw multi-agent patterns — youtube.com/watch?v=VwHjR0xxJ1M
- Route vs Terminal method — youtube.com/watch?v=esuPIJeRotI
- Mission Control 15 use cases — youtube.com/watch?v=GzNM_bp1WaE
- 10 Claude Code plugins — youtube.com/watch?v=FZsNP8mO6kA

---

## Cross-Research Patterns (Universal Truths)

1. Multi-agent is non-negotiable — single agents fail at scale
2. Orchestrator + specialists is the standard architecture
3. Context isolation prevents hallucinations
4. Model routing saves money (Haiku/Sonnet/Opus by complexity)
5. Named agents with clear roles and personalities
6. Markdown-first, file-based memory systems
7. Per-agent cost tracking is mandatory
8. Obsidian as knowledge hub (multiple projects converge here)
9. MCP as universal interface (every new tool ships with MCP)
10. Cloudflare as infrastructure standard

---

## Neon Database (Evaluated, NOT Adopted)

Don't migrate from Supabase. Use Neon only for ephemeral agent sandboxes or new greenfield projects.
