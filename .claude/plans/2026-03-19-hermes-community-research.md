# Hermes Agent Community Research — Real-World Production Patterns

**Date**: 2026-03-19
**Researcher**: Jake (Claude Opus 4.6)
**Status**: COMPLETE
**Confidence**: DRAFT — based on live web research, not firsthand testing

---

## Executive Summary

Hermes Agent (by Nous Research, MIT license, released Feb 2026) has hit ~8-9K GitHub stars in its first month. It positions itself between Claude Code (CLI coding copilot) and OpenClaw (messaging platform agent). The community is EARLY — most content is setup guides and comparisons, not deep production war stories yet. But several clear patterns are emerging from power users, hackathon builders, and the r/hermesagent + r/LocalLLaMA communities.

The biggest signal: **Teknium (Nous Research co-founder) tweeted "A swarm of hermes approaches" on March 15, 2026** — confirming multi-agent swarm architecture is actively being built. GitHub Issue #344 lays out a detailed 4-phase roadmap for this.

---

## 1. Reddit Communities

### r/hermesagent (dedicated subreddit)
- **Status**: Active, growing. Setup guides pinned.
- **Key post**: "Complete Hermes Agent Setup Guide" — comprehensive walkthrough covering CLI, skills, cron jobs, config reference
- **Validated pattern**: The setup guide is the most-referenced community resource

### r/LocalLLaMA
- **Key thread**: "Anybody who tried Hermes-Agent?" (11 votes, 11 comments) — direct comparison to OpenClaw
  - **User Suitable_Currency440** (switched from OpenClaw): "It's OpenClaw already set up + 1 week worth of debugging free. RAG works, tool calling works, setup is not an ass to do. If I made OpenClaw execute 50+ steps for a complex task, Hermes done the same with 5 correct tool calls and 2:30 minutes less of compute."
  - Running: Qwen3.5-9B on RX 9070XT 16GB VRAM (local model)
  - **Validation level**: Single user, but detailed and specific
- **Thread**: "Hermes Agent with MIT license" (42 votes, 30 comments) — launch announcement discussion
- **Thread**: "Hermes Agent & Recursive Language Models" — advanced user SteppenAxolotl discussing RLM scaffolding integration

### r/openclaw
- **Key thread**: "I just switched to Hermes agent" — migration stories from OpenClaw users
- **Thread**: "I ignored all red flags to give OpenClaw root access to my life" — user looking for real use cases, shows the "what do I actually DO with this" problem both frameworks face

### r/OpenClawCentral
- **Power user According-Sign-9587**: Running 4 agents on one machine for ~$10/month:
  1. Reddit Growth Agent (finds relevant posts, suggests responses)
  2. Cold Outreach Agent (finds prospects, prepares emails)
  3. Social Media Auto Poster (schedules and posts)
  4. Content Repurposing Agent (turns long content into multiple posts)
- **Key advice**: "Keep it under 8 skills at a time or the agent starts forgetting them"
- **Validation level**: Multiple users confirming similar patterns

---

## 2. YouTube Content

### Top Creators
- **AI Profit Lab / Skool community**: "Hermes Agent: New FREE OpenClaw Alternative!" — beginner-friendly walkthrough, links to paid coaching community
- **Theo (@Theo_jpeg on X)**: "3h to learn the process, launch my agent and record everything while making it clear for beginners. 7h to edit this video." — step-by-step beginner guide
  - Self-described beginner who documented his entire learning process
  - **Validation level**: Authentic beginner perspective, not marketing

### Content Pattern
Most YouTube content is still "what is it + how to install" level. No deep production walkthroughs yet. The framework is ~3 weeks old as of this research.

---

## 3. Discord Communities

- **Nous Research Discord** exists (linked from official docs and GitHub)
- **Hermes Agent has dedicated Discord channels** within the Nous Research server
- The official site links to Discord community at nousresearch.com/hermes-agent
- No independent Hermes-specific Discord server found — everything routes through Nous Research's main server

---

## 4. Twitter/X Threads

### Teknium (Nous Research co-founder, @Teknium)
- **March 15, 2026**: "A swarm of hermes approaches" — quoting @glitch_ who built a growth hacking swarm in 36 hours
  - 32.5K views, 326 reposts
  - Confirms multi-agent swarm is the next major feature direction
  - The quoted thread describes a growth experiment swarm using Hermes Agent tool categories

### Shubham Saboo (LinkedIn)
- Popular post: "This open-source AI Agent actually remembers and grows with you. Instead of dumping context into a vector database, it builds Skill Documents."
- **Validation**: High engagement, but more promotional than technical

### Theo (@Theo_jpeg)
- Documented his full beginner-to-running journey as content

### @slimer48484
- "I'm personally a big fan of Hermes agent!" — listed hobby projects built with AI assistance

### Jay Guthrie (@StraughterG)
- "Last night my agent ran overnight on a project we came up with together, and it was ready for review when I woke up this morning."
- **Pattern**: Overnight autonomous operation via cron/scheduled tasks

---

## 5. Blog Posts and Articles

### DEV.to — Most Technical Content
- **OpenWalrus**: "Hermes memory: five layers, one learning loop" (March 15) — the BEST technical deep-dive found
  - Detailed breakdown of all 5 memory layers
  - Comparison tables with Mem0 and Walrus
  - Key finding: "No mechanism to forget. Skills accumulate indefinitely."
  - Open question: "What happens after six months of heavy use with no forgetting?"
- **Hermes Agent official account**: "Hermes: An Autonomous Agent Experiment" series — chronicles of building APIs with Hermes

### Medium
- **Marco Rodrigues** (AI Advances): "Hermes: The Only AI Agent That Truly Competes With OpenClaw" — setup guide + best practices
- **Nikhil** (Neural Notions): "Hermes vs OpenClaw: The First Real Rival in the Autonomous AI Agent Race"
- **Alvin Toms Varghese**: "ElizaOS vs. OpenClaw vs. Hermes: what actually matters in 2026" — three-way comparison after deploying each. Key quote: "Hermes is the most interesting if you live in the terminal and care about persistent intelligence more than raw feature count."

### Substack
- **eli5defi**: "Your AI Agent Forgets You Exist. Hermes Doesn't." — beginner-friendly explainer

### getclaw.sh (independent comparison site)
- 3-part series: strategic comparison, feature comparison, security comparison
- Key finding: "OpenClaw is strongest for one assistant across multiple business channels. Hermes Agent is strongest when you want a persistent personal agent that lives on your own machine."

### Shelldex
- Hermes: 8K stars, Python, memory-focused
- OpenClaw: 317K stars, TypeScript, reference/platform-focused
- Both MIT license, both MCP support

---

## 6. Power User Patterns (Validated)

### SOUL.md Configuration
- **Purpose**: Global agent identity. First thing in system prompt.
- **What goes here**: Personality, tone, communication style, how to handle uncertainty
- **What does NOT go here**: Project-specific instructions (those go in AGENTS.md)
- **Location**: `~/.hermes/SOUL.md` (global) or `$HERMES_HOME/SOUL.md`
- **Pattern**: Power users keep SOUL.md short and personality-focused, use AGENTS.md per-project

### AGENTS.md Configuration
- **Purpose**: Project-specific instructions, architecture notes, coding conventions
- **Hierarchical discovery**: Hermes walks the directory tree and loads ALL AGENTS.md files
- **Monorepo pattern**: Root AGENTS.md for global conventions, subdirectory AGENTS.md for team-specific
- **.cursorrules compatibility**: Hermes reads .cursorrules files too

### Skill Architecture
- **Keep under 8 skills active** — community consensus that agents lose coherence with too many
- **Start with these basic skills**: summarize-url, research, content-draft, social-monitor
- **Skill format**: agentskills.io standard (SKILL.md + optional scripts/references/assets)
- **Portable to 11+ other tools** that support agentskills.io
- **Auto-creation**: Hermes creates skills autonomously when it completes complex tasks
- **Manual creation**: "Save what you just did as a skill called `deploy-staging`"
- **Skill sources**: agentskills.io, ClawHub, LobeHub, GitHub repos

### Cron Job Patterns
- **Natural language scheduling**: `/cron add "every 2h" "Check server status"`
- **Skill attachment**: `/cron add "every 1h" "Summarize new feed items" --skill blogwatcher`
- **Safety**: Cron sessions cannot create more cron jobs (prevents runaway loops)
- **Results delivery**: Results go to home channel (set with `/sethome`)
- **Real pattern**: Users running overnight jobs, waking up to results

### Memory Architecture (5 Layers)
1. **Context window** — session-only, compressed at 50% utilization
2. **Procedural skills** (SKILL.md) — autonomous, persists as markdown files
3. **Contextual persistence** — vector store indexes skills for retrieval
4. **Honcho user modeling** — external service, Theory of Mind snapshots (optional)
5. **FTS5 search** — SQLite full-text search across all past sessions

### Cost Optimization
- **$5-10/month VPS** is the standard deployment target
- **4 of 5 memory layers are fully local** — only Honcho requires external API
- **Use `/compress`** before hitting context limits
- **Delegate for parallel work** — subagents have isolated context, only summaries return
- **Switch models mid-session** with `/model` — frontier for reasoning, fast for boilerplate

---

## 7. Hermes + Claude Code Integration

### No Direct Integration Found
Nobody is running a documented Hermes + Claude Code bridge yet. The frameworks occupy adjacent but different niches:
- **Claude Code**: IDE-attached, coding-focused, Anthropic ecosystem
- **Hermes Agent**: Server-resident, multi-platform messaging, model-agnostic

### Parallel Usage Pattern
- The r/LocalLLaMA user who switched from OpenClaw mentioned using "claude code or codex" alongside Hermes for coding tasks
- **Pattern**: Hermes for persistent personal agent / messaging / cron tasks, Claude Code for coding sessions
- This is how Jake's architecture already works — Claude Code for development, external agents for operations

### Relevant Claude Code Patterns (for reference)
- Rick Hightower (Medium): "Claude Code Agent Teams: Multiple Claudes Working Together"
- Ilyas Ibrahim: "How I Made Claude Code Agents Coordinate 100%" — skills + agent-management-protocol
- 8 parallel Claude Code agents for infrastructure project (r/ClaudeAI)
- These patterns could inform how Hermes multi-agent maps to our architecture

---

## 8. Multi-Agent Orchestration on Hermes

### Current State: `delegate_task` Tool
- Spawns ephemeral child AIAgent instances
- Single task or batch (up to 3 parallel via ThreadPoolExecutor)
- Children get isolated context, restricted toolsets, own terminal
- Children CANNOT talk to each other, share state, or communicate mid-task
- Depth limit: 2 levels (parent > child OK, child > grandchild blocked)
- No crash recovery, no retry logic, no synthesis step

### `mixture_of_agents` Tool
- Queries 4 frontier models in parallel, aggregator synthesizes
- One-shot, not iterative
- Closest thing to multi-perspective reasoning currently

### Coming: Full Multi-Agent Architecture (GitHub Issue #344)
Teknium authored this detailed roadmap:

**Phase 1 — Workflow DAG + Synthesis** (Foundation)
- Dependency-aware task graphs with topological sort
- Downstream steps receive upstream results as context
- Synthesis parameter for parallel task aggregation
- ~300-400 LOC change, no new dependencies

**Phase 2 — Resilient Execution**
- Checkpointing (persist state after each tool call)
- Retry with configurable count
- Stuck detection with activity monitoring
- Replan on failure (meta-agent rewrites failed task)
- Inception prompting (hardened sub-agent communication)

**Phase 3 — Agent Roles & Cooperation**
- Pre-defined archetypes: Coordinator, Researcher, Developer, Browser Agent, Reviewer, Synthesizer
- LLM-based coordinator for auto-assignment
- Shared memory pools between agents
- Acceptance criteria with independent judge
- Agent pooling (reuse instances)

**Phase 4 — Advanced Patterns**
- Adversarial debate mode (two-agent iterative refinement)
- Cross-platform agent distribution
- Persistent agent teams (survive across sessions)
- Auto-orchestration (simple vs complex routing)
- Workflow templates (reusable definitions)

### Related Issues
- #356: Acceptance Criteria & Independent Judge
- #375: Inception Prompting (anti-communication-failure)
- #376: Adversarial Debate Mode
- #377: Shared Memory Pools
- #404: Symphony-Style Autonomous Issue Resolution (poll-dispatch-resolve-land)
- #412: Consensus & Voting Engine for Multi-Agent Decision Making
- #477: OpenHands Coding Agent Skill (sandboxed code agent delegation)

---

## 9. Best MCP Server Combinations

### Hermes MCP Integration
- Config in `~/.hermes/config.yaml` under `mcp_servers` key
- Supports stdio and HTTP/StreamableHTTP transports
- Mix and match multiple servers simultaneously
- No code changes needed — add config lines, tools appear

### Community MCP Stacks (general, not Hermes-specific yet)
The MCP ecosystem is too new for Hermes-specific stack patterns. General 2026 recommendations from Builder.io, Firecrawl, and others:
- **Supabase/PostgreSQL MCP**: Production relational data with RLS awareness
- **GitHub MCP**: Repo management, issue tracking, PR workflows
- **Brave Search / Tavily**: Web search integration
- **Playwright / Browser**: Browser automation
- **Filesystem MCP**: Local file operations

### Hermes Built-in Tools vs MCP
Hermes already ships 40+ built-in tools covering most of what MCP servers provide:
- Web search, browser automation, terminal, file editing
- Memory, delegation, RL training, messaging delivery
- Home Assistant integration
The MCP layer extends beyond these when you need specialized integrations.

---

## 10. Hermes Roadmap / What's Coming

### Confirmed (from GitHub Issues + Teknium's tweets)
1. **Multi-Agent Swarm** — The biggest upcoming feature. Issue #344 is the umbrella. Teknium's "swarm of hermes approaches" tweet (March 15) confirms active development.
2. **Workflow DAG Engine** — Dependency-aware task graphs replacing flat parallel dispatch
3. **Agent Roles** — Pre-defined archetypes with specialized toolsets
4. **Resilient Execution** — Checkpointing, retry, stuck detection, replan on failure
5. **Symphony-Style Issue Resolution** — Poll-dispatch-resolve-land workflow (#404)
6. **Consensus & Voting Engine** — Multi-agent decision making (#412)
7. **OpenHands Integration** — Sandboxed coding agent delegation (#477)

### From Official Timeline (hermesagent.agency)
- Mid 2025: Skills Hub at agentskills.io goes live (DONE)
- 2025-2026: Continuous self-improvement loop, Honcho user modeling, MCP integration, Daytona/Modal serverless (DONE/IN PROGRESS)
- Active Hackathon: $7,500 first prize, driving community skill creation

### What's NOT on the Roadmap (gaps)
- No forgetting/memory decay mechanism planned
- No skill deduplication or versioning
- No published benchmarks for learning loop effectiveness
- No Claude Code bridge or direct integration

---

## 11. Hackathon Projects (Real Builds)

### Glippy Swarm (DutchSEOnerd, r/buildinpublic)
- **What**: Autonomous GEO (Generative Engine Optimization) platform
- **Architecture**: 7 AI agents — Scout, Crawler, Investigator, Web Presence Tracker, Analyst, Optimizer, Reporter
- **Uses**: All 18 Hermes tool categories including browser automation, multi-model reasoning, persistent memory, subagent delegation, cron scheduling
- **Insight**: "AI visibility isn't just about technical SEO. It's about content depth, authority signals, web presence."
- **Validation**: Hackathon entry, not production-tested yet

### Self-Improve Agent (jungleteemosupport, r/SideProject)
- **What**: Framework-agnostic toolkit inspired by Hermes for persistent memory + reusable skills
- **Components**: memory_manager.py, skill_manager.py, session_recall.py, insights_analyzer.py, security_scanner.py
- **Insight**: Scans git history/reverts to identify failure patterns and proactively suggests areas the AI is struggling with
- **Validation**: Open-source project, inspired by Hermes but independent

---

## Key Takeaways for Our 25x Upgrade

### What to Steal from Hermes
1. **SKILL.md format (agentskills.io)** — Portable, standardized, works across 11+ tools. Our skills should adopt this format.
2. **5-layer memory architecture** — Especially the procedural skill creation loop. Our memory is currently 3-tier (session/curated/search). Adding procedural skills and FTS5 session search would close the gap.
3. **Cron with natural language + skill attachment** — `/cron add "every 2h" "task" --skill skillname` is elegant.
4. **AGENTS.md hierarchical discovery** — Similar to our CLAUDE.md + rules system but with directory-tree walking.
5. **Keep skills under 8 active** — Community-validated limit on agent coherence.

### What Hermes Lacks That We Have
1. **Multi-company awareness** — Hermes is single-user, single-context. Our 3-company cross-domain pattern detection is unique.
2. **Quality gates and circuit breakers** — No equivalent in Hermes ecosystem.
3. **Structured handoff protocol** — Hermes has session resume (`hermes -c`) but not machine-readable handoffs.
4. **Agent team design** — Our Susan 73-agent roster with role specialization is more mature than Hermes's current delegate_task. But their Phase 3 roadmap (agent roles + cooperation) is heading in our direction.
5. **Effort level control** — No equivalent to our /effort system in Hermes.

### What to Watch
1. **Multi-agent swarm launch** — When Phase 1 of Issue #344 ships, evaluate for integration
2. **agentskills.io ecosystem growth** — If this becomes the standard, our skills should be compatible
3. **Honcho user modeling** — If benchmarks prove it works, consider for our USER.md system
4. **Forgetting problem** — First framework to solve memory decay wins long-term
5. **Hermes Hackathon results** — Will surface real production patterns

---

## Source Quality Assessment

| Source | Type | Reliability |
|--------|------|-------------|
| Hermes official docs | Primary | HIGH — first-party, current |
| GitHub Issue #344 (Teknium) | Primary | HIGH — from co-founder, detailed |
| r/LocalLLaMA threads | Community | MEDIUM — real users, small sample |
| r/OpenClawCentral patterns | Community | MEDIUM — validated by multiple users |
| OpenWalrus DEV.to analysis | Independent | HIGH — technical, evidence-based |
| getclaw.sh comparisons | Independent | MEDIUM — well-researched but promotional |
| YouTube tutorials | Community | LOW-MEDIUM — mostly setup guides |
| Twitter/X threads | Signal | LOW — promotional, short-form |
| Hackathon projects | Experimental | LOW — unproven, deadline-driven |
