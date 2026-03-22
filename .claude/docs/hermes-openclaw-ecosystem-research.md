# Hermes AI / OpenClaw Ecosystem — Deep Research Report

**Date**: 2026-03-19
**Researcher**: Jake (via GitHub Search, Brave, Exa)
**Sources**: Live GitHub API, web search, official docs

---

## 1. OFFICIAL REPOS

### OpenClaw (The Platform)
| Field | Value |
|-------|-------|
| **Repo** | [openclaw/openclaw](https://github.com/openclaw/openclaw) |
| **Stars** | ~325K (as of March 2026) |
| **Creator** | Peter Steinberger (@steipete) |
| **License** | Open source, moving to foundation |
| **Language** | TypeScript |
| **Latest Release** | 2026.3.13 |
| **History** | Started Nov 24, 2025 as "Clawd" / "Clawdbot" / "Moltbot". Renamed to OpenClaw. Steinberger joined OpenAI on Feb 14, 2026; project moved to open-source foundation. |
| **Notable** | 180K+ stars in first months. Most viral GitHub repo of 2025-2026. Plugin-based agent runtime with 36+ installable extensions, 16 messaging channels, 3 AI model providers, 9 workflow tools. |

**Workspace file architecture** (the agent IS the files):
```
my-agent/
├── SOUL.md        # Personality, values, communication style
├── IDENTITY.md    # Core identity layer
├── AGENTS.md      # Agent roster and capabilities
├── USER.md        # User profile and preferences
├── TOOLS.md       # Available tools config
├── HEARTBEAT.md   # Scheduled tasks / cron
└── MEMORY.md      # Persistent memory
```

**Key URLs**:
- Official site: https://openclaw.ai
- Docs: https://docs.openclaw.ai
- Blog: https://openclaw.ai/blog
- Releases: https://github.com/openclaw/openclaw/releases
- Wikipedia: https://en.wikipedia.org/wiki/OpenClaw

### Hermes Agent (Nous Research)
| Field | Value |
|-------|-------|
| **Repo** | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) |
| **Stars** | ~6,000+ (first month) |
| **Creator** | Nous Research (teknium1) |
| **License** | MIT / Apache 2.0 |
| **Language** | Python |
| **Released** | February 26, 2026 |
| **Tagline** | "The agent that grows with you" |

**What makes it different**: Self-improving AI agent with persistent memory, autonomous skill creation, and local inference support. Positions itself "between Claude Code (CLI) and OpenClaw (messaging platform agent)."

**Architecture** (from official docs):
```
hermes-agent/
├── run_agent.py              # AIAgent core loop
├── cli.py                    # Interactive terminal UI
├── model_tools.py            # Tool discovery/orchestration
├── toolsets.py               # Tool groupings and presets
├── hermes_state.py           # SQLite session/state database
├── batch_runner.py           # Batch trajectory generation
├── agent/                    # Prompt building, compression, caching, trajectories
├── hermes_cli/               # Command entrypoints, auth, setup, models, config
├── tools/                    # Tool implementations and terminal environments
├── gateway/                  # Messaging gateway, session routing, delivery, hooks
├── cron/                     # Scheduled job storage and scheduler
├── honcho_integration/       # Honcho memory integration
├── acp_adapter/              # ACP editor integration
```

**Key capabilities**:
- 40+ built-in tools: file management, web browsing, code execution, remote terminal, API calls
- Self-improving via episodic memory — learns from past task failures
- Supports OpenAI, Anthropic, and local models via Ollama/vLLM/llama.cpp
- Runs on a $5/month VPS
- Messaging gateway: Telegram, Discord, Slack, WhatsApp
- Install: `curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash`

**Official docs**: https://hermes-agent.nousresearch.com/docs/

### Hermes Agent Self-Evolution
| Field | Value |
|-------|-------|
| **Repo** | [NousResearch/hermes-agent-self-evolution](https://github.com/NousResearch/hermes-agent-self-evolution) |
| **Stars** | 233 |
| **Notable** | Uses DSPy + GEPA (Genetic-Pareto Prompt Evolution) to automatically evolve skills, tool descriptions, system prompts, and code. No GPU training required — ~$2-10 per optimization run via API calls. |

---

## 2. POWER-USER CONFIGS

### TechNickAI/openclaw-config (THE reference setup)
| Field | Value |
|-------|-------|
| **Repo** | [TechNickAI/openclaw-config](https://github.com/TechNickAI/openclaw-config) |
| **Description** | "Give your AI assistant memory, skills, and autonomy. Persistent memory, 11 integration skills, and 4 autonomous workflows — all in markdown and Python scripts." |
| **Notable** | Fleet state management via `~/openclaw-fleet/` (one markdown file per server). Gateway-restart skill for graceful restarts. Integration tests auto-skip when API keys aren't set. Self-contained skills with inline dependencies. |
| **Tagline** | "Your AI deserves to remember you." |
| **Pattern** | Config-as-code approach — everything in markdown and Python scripts. The gold standard for OpenClaw power-user configuration. |

### Claudius Blog Setup Guide (6-week production config)
- **URL**: https://claudius.blog/blog/openclaw-setup-guide-6-weeks/
- **Notable**: Real production config with timeout tables by task type, sub-agent sizing rules. Written from perspective of the agent itself ("I'm Claudius, Bobby's OpenClaw agent").
- **Key insight**: Agent timeout table (Quick lookup 60s, Single file edit 180s, Multi-step research 300s, Complex multi-doc 600s, Large codebase 900s)

### digitalknk Gist (Sanitized Config Example)
- **URL**: https://gist.github.com/digitalknk/4169b59d01658e20002a093d544eb391
- **Notable**: Full security hardening workflow — `openclaw doctor --fix`, `openclaw security audit --deep`, permission lockdowns, localhost binding verification

---

## 3. SOUL.md & PERSONALITY CONFIGS

### aaronjmars/soul.md (The Soul Builder)
| Field | Value |
|-------|-------|
| **Repo** | [aaronjmars/soul.md](https://github.com/aaronjmars/soul.md) |
| **Description** | "The best way to build a personality for your agent. Let Claude Code / OpenClaw ingest your data & build your AI soul." |
| **Notable** | Identity is composable, forkable, evolvable. Works with Claude Code, OpenClaw, and any agent that reads markdown. |

### openclawsoul.org (Community Soul Hub)
- **URL**: https://openclawsoul.org/
- **Features**: Curated SOUL.md templates, guided conversation tool for crafting personality, directory of community souls
- **Tutorial**: https://openclawsoul.org/create-openclaw-soul.html

### will-assistant/openclaw-agents (Persona Collection)
| Field | Value |
|-------|-------|
| **Repo** | [will-assistant/openclaw-agents](https://github.com/will-assistant/openclaw-agents) |
| **Description** | "Curated collection of OpenClaw agent personalities — SOUL.md, AGENTS.md, IDENTITY.md configs" |
| **Notable** | Personality overlays that change how your AI assistant talks and thinks. Copy SOUL.md, IDENTITY.md, and AGENTS.md into workspace. |

### OpenClaw Identity Architecture Deep Dive
- **URL**: https://www.mmntm.net/articles/openclaw-identity-architecture
- **Notable**: Real TypeScript showing soul files, identity resolution cascades, and multi-agent architecture

### Official SOUL.md Guide
- **URL**: https://openclaws.io/blog/openclaw-soul-md-guide
- **Key concept**: SOUL.md is the foundational identity layer — defines personality, communication style, core values, and behavioral guardrails

---

## 4. MULTI-AGENT / ORCHESTRATION SYSTEMS

### cft0808/edict (Chinese "Three Departments Six Ministries" System)
| Field | Value |
|-------|-------|
| **Repo** | [cft0808/edict](https://github.com/cft0808/edict) |
| **Description** | "OpenClaw Multi-Agent Orchestration System — 9 specialized AI agents with real-time dashboard, model config, and full audit trails" |
| **Notable** | Historical Chinese governance model applied to AI agent orchestration. 9 specialized agents. Real-time dashboard. Full audit trails. |

### raulvidis/openclaw-multi-agent-kit (Production-Tested)
| Field | Value |
|-------|-------|
| **Repo** | [raulvidis/openclaw-multi-agent-kit](https://github.com/raulvidis/openclaw-multi-agent-kit) |
| **Description** | "Production-tested templates for deploying multi-agent AI teams on OpenClaw with Telegram supergroup integration. 10 agent personalities, shared context workflows, bot-to-bot communication." |
| **Notable** | Built from a LIVE 10-agent setup. Telegram supergroup integration. Bot-to-bot communication. Step-by-step AI-readable setup instructions. THIS IS VERY RELEVANT TO JAKE. |

### shenhao-stu/openclaw-agents (One-Command Multi-Agent)
| Field | Value |
|-------|-------|
| **Repo** | [shenhao-stu/openclaw-agents](https://github.com/shenhao-stu/openclaw-agents) |
| **Description** | "One-command multi-agent setup for OpenClaw — 9 specialized AI agents, group routing, safe config merge." |

### jnMetaCode/agency-agents-zh (180 Chinese Agent Personas)
| Field | Value |
|-------|-------|
| **Repo** | [jnMetaCode/agency-agents-zh](https://github.com/jnMetaCode/agency-agents-zh) |
| **Description** | "180 plug-and-play AI agent personas (Chinese) — 17 departments, supports Claude Code / OpenClaw / Cursor / Trae and 11 tools" |

### mergisi/awesome-openclaw-agents (162 Agent Templates)
| Field | Value |
|-------|-------|
| **Repo** | [mergisi/awesome-openclaw-agents](https://github.com/mergisi/awesome-openclaw-agents) |
| **Description** | "162 production-ready AI agent templates for OpenClaw. SOUL.md configs across 19 categories." |

### win4r/team-tasks (Pipeline Coordination)
| Field | Value |
|-------|-------|
| **Repo** | [win4r/team-tasks](https://github.com/win4r/team-tasks) |
| **Description** | "Multi-agent pipeline coordination: Linear, DAG, and Debate modes for AI agent orchestration" |
| **Notable** | Three orchestration modes: Linear (sequential), DAG (dependency graph), Debate (adversarial). |

---

## 5. MISSION CONTROL / DASHBOARDS

### abhi1693/openclaw-mission-control
- **Description**: "AI Agent Orchestration Dashboard — Manage AI agents, assign tasks, coordinate multi-agent collaboration via OpenClaw Gateway."

### builderz-labs/mission-control
- **Description**: "Open-source dashboard for AI agent orchestration. Manage agent fleets, track tasks, monitor costs — with direct CLI integration, GitHub sync, real-time monitoring."

### JohnRiceML/clawport-ui
- **Description**: "Open-source AI agent command center for Claude Code agent teams. Built on OpenClaw."

### mudrii/openclaw-dashboard
- **Description**: "Beautiful, zero-dependency command center for OpenClaw AI agents"

### tugcantopaloglu/openclaw-dashboard
- **Description**: "Secure, real-time monitoring dashboard for OpenClaw AI agents. Auth, TOTP MFA, cost tracking, live feed, memory browser."

### crabwise-ai/crabwalk
- **Description**: "Real-time companion monitor for OpenClaw agents."

---

## 6. SKILL REPOSITORIES

### VoltAgent/awesome-openclaw-skills (THE Definitive List)
| Field | Value |
|-------|-------|
| **Repo** | [VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) |
| **Stars** | ~39,731 |
| **Skills Count** | 5,490+ |
| **Website** | https://clawskills.sh/ |
| **Notable** | THE definitive curated list. Sourced from ClawHub (official registry). Categorized: Coding Agents & IDEs (1,200 skills), plus 18+ other categories. Security scanning via VirusTotal. MIT licensed. 50 contributors. |
| **Install** | `clawhub install <skill-slug>` |

### LeoYeAI/openclaw-master-skills
| Field | Value |
|-------|-------|
| **Repo** | [LeoYeAI/openclaw-master-skills](https://github.com/LeoYeAI/openclaw-master-skills) |
| **Description** | "339+ best OpenClaw skills — weekly updated by MyClaw.ai from ClawHub, GitHub & community" |

### natan89/awesome-openclaw-skills
| Field | Value |
|-------|-------|
| **Repo** | [natan89/awesome-openclaw-skills](https://github.com/natan89/awesome-openclaw-skills) |
| **Description** | "1,715 community-driven OpenClaw skills, sorted by category" |

### sundial-org/awesome-openclaw-skills
| Field | Value |
|-------|-------|
| **Stars** | 483 |
| **Skills** | 913 curated top skills |
| **Install** | `npx sundial-hub add <name>` |
| **Notable** | Top skills by downloads. ByteRover (14,376 downloads) leads for project knowledge management. |

### SamurAIGPT/awesome-openclaw (General Resources)
| Field | Value |
|-------|-------|
| **Repo** | [SamurAIGPT/awesome-openclaw](https://github.com/SamurAIGPT/awesome-openclaw) |
| **Description** | "Curated list of OpenClaw resources, tools, skills, tutorials & articles" |

### ProSkillsMD/proskills
- **Description**: "Community-curated OpenClaw skill listings — browse, submit, and contribute"
- **Website**: ProSkills.md

### openclaw-commons/openclaw-skill-commons
- **Description**: "Decentralized skill reputation system for OpenClaw agents — community-driven, agent-voted, self-improving"

### memepilot/clawlodge
- **Description**: "Community hub for sharing well-tuned OpenClaw setups, skills, and agent workflows"

---

## 7. DESKTOP CONTROL & BROWSER AUTOMATION

OpenClaw has THREE browser automation modes:

### Browser Relay (Most Powerful)
- Chrome extension that gives agents full browser control
- Screenshots, form filling, element clicking, page navigation
- Requires: Chrome extension + running OpenClaw instance + node host relay
- **URL**: https://masterprompting.net/blog/openclaw-browser-relay

### Built-in Browser Tool
```yaml
agents:
  web-agent:
    model: openai/gpt-4o
    tools:
      - browser
    browser:
      headless: true
      viewport: { width: 1280, height: 720 }
      timeout: 30
```
- Install: `openclaw browser install` (downloads compatible Chromium)
- Actions: navigate, click (CSS selectors), type, screenshot, extract data
- **Docs**: https://openclawdoc.com/docs/agents/browser-automation/

### Browser Plugin
- Install: `openclaw plugins install @openclaw/browser-control`
- Enable: `openclaw config set browser.enabled true`
- Debug mode: `openclaw config set browser.headless false`

### Desktop Automation MCP Servers
| Repo | Description |
|------|-------------|
| [dddabtc/winremote-mcp](https://github.com/dddabtc/winremote-mcp) | Windows Remote MCP — 40+ tools for desktop automation, process management, file operations |
| [redf0x1/camofox-mcp](https://github.com/redf0x1/camofox-mcp) | Anti-detection browser MCP server — navigate/interact without getting blocked |

---

## 8. MCP SERVERS FOR OPENCLAW

### Direct OpenClaw-MCP Bridges
| Repo | Description |
|------|-------------|
| [freema/openclaw-mcp](https://github.com/freema/openclaw-mcp) | MCP server for OpenClaw — secure bridge between Claude.ai and self-hosted OpenClaw with OAuth2 |
| [Helms-AI/openclaw-mcp-server](https://github.com/Helms-AI/openclaw-mcp-server) | MCP server exposing OpenClaw Gateway tools to Claude Code and other MCP-compatible clients |
| [androidStern-personal/openclaw-mcp-adapter](https://github.com/androidStern-personal/openclaw-mcp-adapter) | OpenClaw plugin that exposes MCP server tools as native agent tools |
| [Agnuxo1/p2pclaw-mcp-server](https://github.com/Agnuxo1/p2pclaw-mcp-server) | MCP server for OpenClaw Agents protocol |

### Skills-as-MCP
| Repo | Description |
|------|-------------|
| [nj19257/FastSkills](https://github.com/nj19257/FastSkills) | MCP server that brings Agent Skills (the open standard behind Claude Code, OpenClaw & nanobot) to any MCP-compatible agent. Discover, load, create & execute skills. |

### Knowledge / Memory MCP
| Repo | Description |
|------|-------------|
| [destinyfrancis/openclaw-knowledge-distiller](https://github.com/destinyfrancis/openclaw-knowledge-distiller) | Turn YouTube/Bilibili videos into structured knowledge articles. Local Qwen3-ASR MLX + AI summarization. MCP server for Claude Code / OpenClaw agents. |
| [Dataojitori/nocturne_memory](https://github.com/Dataojitori/nocturne_memory) | Lightweight, rollbackable Long-Term Memory Server for MCP Agents. Graph-like structured memory. Drop-in replacement for OpenClaw memory. |

### Security MCP
| Repo | Description |
|------|-------------|
| [sinewaveai/agent-security-scanner-mcp](https://github.com/sinewaveai/agent-security-scanner-mcp) | Security scanner MCP — prompt injection firewall, package hallucination detection (4.3M+ packages), 1000+ vulnerability rules |
| [2pidata/openclaw-security-guard](https://github.com/2pidata/openclaw-security-guard) | Complete security layer — CLI Scanner + Dashboard. Secrets detection, config hardening, prompt injection scanning, MCP server auditing. |

### Utility MCP
| Repo | Description |
|------|-------------|
| [Shelpuk-AI-Technology-Consulting/kindly-web-search-mcp-server](https://github.com/Shelpuk-AI-Technology-Consulting/kindly-web-search-mcp-server) | Web search + content retrieval for AI coding tools and agents. Supports Serper, Tavily, SearXNG. |
| [SixHq/Overture](https://github.com/SixHq/Overture) | MCP server that visually maps execution plans of any AI coding agent as interactive flowchart before code writing begins. |

---

## 9. INTEGRATION / BRIDGE REPOS

### OpenClaw <-> Claude Code Bridges

#### ACP Persona Bridge (Official PR #33586)
- **URL**: https://github.com/openclaw/openclaw/pull/33586
- **What it does**: When fleet agents are spawned into ACP CLI backends (Claude Code), their persona is lost. This PR bridges SOUL.md and AGENTS.md into CLAUDE.md format that CLI backends understand.
- **Pattern**: `bridgeAgentPersonaToClaudeMd()` — reads SOUL.md + AGENTS.md, synthesizes CLAUDE.md in session CWD. Non-destructive (never overwrites existing CLAUDE.md).
- **STATUS**: MERGED. This is the official way to bridge OpenClaw personas to Claude Code.

#### Claude Agent SDK as Runtime (PR #33475)
- **URL**: https://github.com/openclaw/openclaw/pull/33475
- **What it does**: Adds Claude Agent SDK as alternative agent runtime. New `claude-sdk-runner` module translating Claude Agent SDK sessions into OpenClaw's event/tool/session contracts.
- **Why**: Anthropic clarified that using Claude Code/Max OAuth with third-party tools violates ToS. This provides a compliant path.
- **STATUS**: Open (draft), 15,461 additions, 87 files changed. MASSIVE PR.

#### elvatis/openclaw-cli-bridge-elvatis
| Field | Value |
|-------|-------|
| **Repo** | [elvatis/openclaw-cli-bridge-elvatis](https://github.com/elvatis/openclaw-cli-bridge-elvatis) |
| **Description** | "OpenClaw plugin: Bridge Codex, Gemini, and Claude Code CLIs as model providers" |
| **Notable** | Slash commands for instant model switching. Local OpenAI-compatible HTTP proxy on 127.0.0.1:31337. Prompt delivery via stdin (avoids E2BIG for long sessions). 59 releases, latest v2.0.0. |

---

## 10. MEMORY SYSTEMS

| Repo | Description |
|------|-------------|
| [EverMind-AI/EverMemOS](https://github.com/EverMind-AI/EverMemOS) | Memory OS that makes OpenClaw agents more personal while saving tokens |
| [MemTensor/MemOS](https://github.com/MemTensor/MemOS) | AI memory OS for LLM and Agent systems — persistent skill memory for cross-task skill reuse and evolution |
| [Dataojitori/nocturne_memory](https://github.com/Dataojitori/nocturne_memory) | Graph-like structured memory. "Say goodbye to Vector RAG and amnesia." |

---

## 11. ALTERNATIVE PLATFORMS / FORKS

| Repo | Description |
|------|-------------|
| [zeroclaw-labs/zeroclaw](https://github.com/zeroclaw-labs/zeroclaw) | "Fast, small, fully autonomous AI personal assistant infrastructure, ANY OS, ANY PLATFORM — deploy anywhere, swap anything" (Rust) |
| [memovai/mimiclaw](https://github.com/memovai/mimiclaw) | "Run OpenClaw on a $5 chip. No OS. No Node.js. No Mac mini. Hardware agents OS." |
| [ValueCell-ai/ClawX](https://github.com/ValueCell-ai/ClawX) | Desktop GUI app for OpenClaw — turns CLI-based AI orchestration into desktop experience |
| [heshengtao/super-agent-party](https://github.com/heshengtao/super-agent-party) | "All-in-one AI companion = Self hosted neuro sama + openclaw" |
| [AstrBotDevs/AstrBot](https://github.com/AstrBotDevs/AstrBot) | Agentic IM Chatbot infrastructure — OpenClaw alternative |
| [CherryHQ/cherry-studio](https://github.com/CherryHQ/cherry-studio) | AI productivity studio with smart chat, autonomous agents, 300+ assistants |
| [voocel/openclaw-mini](https://github.com/voocel/openclaw-mini) | Minimal reproduction of OpenClaw core architecture — sessionKey, queue serialization, tool-based memory retrieval, on-demand context loading |
| [iamsharathbhaskar/amazo.ai](https://github.com/iamsharathbhaskar/amazo.ai) | Autonomous AI agent inspired by OpenClaw + Hermes Agent — continuous loop, journals, builds projects, learns skills |

---

## 12. SECURITY & TOOLING

| Repo | Description |
|------|-------------|
| [Tencent/AI-Infra-Guard](https://github.com/Tencent/AI-Infra-Guard) | Full-stack AI Red Teaming platform — OpenClaw Security Scan, Agent Scan, Skills Scan, MCP scan |
| [LeoYeAI/openclaw-backup](https://github.com/LeoYeAI/openclaw-backup) | One-click backup & restore — workspace, credentials, skills, agent history |
| [jiulingyun/Claw-CLI](https://github.com/jiulingyun/Claw-CLI) | CLI tool for interacting with OpenClaw-CN ecosystem — manage skills, community forum, documentation |

---

## 13. EDUCATIONAL / REFERENCE

| Repo | Description |
|------|-------------|
| [0xtresser/OpenClaw-Book](https://github.com/0xtresser/OpenClaw-Book) | "First book about OpenClaw" — written by OpenClaw + OpenCode + Opus 4.6 |
| [czl9707/build-your-own-openclaw](https://github.com/czl9707/build-your-own-openclaw) | Step-by-step guide to build your own AI agent |
| [mudrii/hermes-agent-docs](https://github.com/mudrii/hermes-agent-docs) | Comprehensive documentation for Hermes Agent v0.2.0 |
| [jasperan/orahermes-agent](https://github.com/jasperan/orahermes-agent) | Oracle AI Agent Harness — fork of hermes-agent powered by OCI GenAI |

---

## 14. ARCHITECTURAL PATTERNS WORTH COPYING

### Pattern 1: Workspace-as-Identity (OpenClaw)
The agent IS the workspace files. SOUL.md + AGENTS.md + USER.md + TOOLS.md + HEARTBEAT.md + MEMORY.md. Git-versioned. Portable. Copy to another server = identical agent. **We already do this with CLAUDE.md + .claude/rules/ + .claude/docs/. OpenClaw just formalized it into named files.**

### Pattern 2: ACP Persona Bridge (PR #33586)
When spawning agents into different runtimes, automatically synthesize the target runtime's config format from the source. SOUL.md -> CLAUDE.md translation. **We should do this when Jake dispatches sub-agents.**

### Pattern 3: Fleet State as Markdown (TechNickAI)
One markdown file per server in `~/openclaw-fleet/`. Agent state is human-readable, git-trackable, and grep-able. **Susan already does this with `.startup-os/` artifacts.**

### Pattern 4: Self-Evolution via DSPy + GEPA (NousResearch)
Automatically evolve skills/prompts/tools through genetic-Pareto prompt evolution. $2-10 per run. No GPU. **This is the self-improvement loop Jake's V6 needs.**

### Pattern 5: Multi-Agent Telegram Supergroup (raulvidis)
10 agents in a Telegram supergroup with bot-to-bot communication and shared context workflows. **Direct blueprint for Jake's multi-agent Telegram setup.**

### Pattern 6: Timeout Tables by Task Type (Claudius)
Size agent timeouts to the task: 60s for lookups, 180s for single file edits, 300s for multi-step research, 600s for complex work, 900s for large codebase changes. **Jake's effort levels should map to timeout budgets.**

### Pattern 7: Three Orchestration Modes (win4r/team-tasks)
Linear (sequential), DAG (dependency graph), Debate (adversarial). Different tasks need different coordination patterns. **Jake should support all three when dispatching Susan's agents.**

### Pattern 8: Skills as Portable Standard (agentskills.io)
Hermes Agent uses the agentskills.io standard — skills portable to 11+ tools including Claude Code and OpenClaw. **Our .claude/skills/ should follow this standard for portability.**

---

## 15. KEY ECOSYSTEM STATS

| Metric | Value |
|--------|-------|
| OpenClaw GitHub stars | ~325,000 |
| VoltAgent/awesome-openclaw-skills stars | ~39,731 |
| Skills on ClawHub (official registry) | 13,729+ |
| Curated skills (VoltAgent) | 5,490+ |
| Hermes Agent stars | ~6,000+ |
| OpenClaw messaging channels | 16 (WhatsApp, Telegram, Discord, Slack, Signal, iMessage, etc.) |
| OpenClaw plugins | 36+ installable extensions |
| Agent template collections | 162+ (mergisi), 180+ (jnMetaCode) |
| Mission control dashboards | 5+ active projects |
| MCP bridge projects | 4+ dedicated repos |
| Memory system projects | 3+ dedicated repos |
| Community SOUL.md collections | 3+ repos + openclawsoul.org |
