# AI Agent Skills, Super Nesting, and Claude Code Tooling
## The Definitive Resource Guide for Startup Founders (2025-2026)

---

## Table of Contents
1. [Claude Code Ecosystem: Best GitHub Repos](#1-claude-code-ecosystem)
2. [Claude Code Techniques](#2-claude-code-techniques)
3. [Agent Orchestration Patterns](#3-agent-orchestration-patterns)
4. [MCP (Model Context Protocol)](#4-mcp-model-context-protocol)
5. [AI Agent Skill Libraries](#5-ai-agent-skill-libraries)
6. [Multi-Repo and Monorepo Management](#6-multi-repo-and-monorepo-management)
7. [Claude Code Hooks and Automation](#7-claude-code-hooks-and-automation)
8. [Best CLAUDE.md Examples](#8-best-claudemd-examples)
9. [Agent Memory and Context Management](#9-agent-memory-and-context-management)
10. [Community Resources](#10-community-resources)

---

## 1. Claude Code Ecosystem

### Tier 1: Must-Know Repositories

| Repository | Stars | What It Does |
|---|---|---|
| [NomenAK/SuperClaude](https://github.com/NomenAK/SuperClaude) | 20.4k | Configuration framework with specialized commands, cognitive personas, and dev methodologies. Slash commands like `/design`, `/build`, `/test`, `/audit`, `/deploy`, `/research`. |
| [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | 2.3k+ | 86 production-ready skill packages across 8 domains (engineering, product, marketing, compliance, finance). Cross-platform: Claude Code, OpenAI Codex, OpenClaw. |
| [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | -- | The canonical "awesome" list: skills, hooks, slash-commands, agent orchestrators, applications, and plugins. |
| [ykdojo/claude-code-tips](https://github.com/ykdojo/claude-code-tips) | -- | 45 battle-tested tips: custom status line, cutting the system prompt in half, using Gemini CLI as a fallback, running Claude in containers, auto half-clone on context overflow. |
| [gwendall/superclaude](https://github.com/gwendall/superclaude) | 312 | CLI tool for GitHub workflow superpowers: AI-powered commits, changelogs, code reviews, README generation. |

### Tier 2: Plugin & Skill Ecosystems

| Repository | Focus |
|---|---|
| [jeremylongshore/claude-code-plugins-plus-skills](https://github.com/jeremylongshore/claude-code-plugins-plus-skills) | 270+ plugins, 1,537 skills across 20 categories, CCPI package manager. |
| [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | Automation skills for GitHub, Supabase, Stripe, Gmail, Slack, Notion, and 500+ services. |
| [ComposioHQ/awesome-claude-plugins](https://github.com/ComposioHQ/awesome-claude-plugins) | Plugin directory with custom commands, agents, hooks, and MCP servers. |
| [BehiSecc/awesome-claude-skills](https://github.com/BehiSecc/awesome-claude-skills) | OWASP security, HashiCorp Terraform, Kaggle integration, 125+ scientific skills. |
| [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | Curated list of skills, resources, and tools for Claude AI workflows. |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 500+ skills from official dev teams (Stripe, Cloudflare, Hugging Face, Google Labs). Cross-platform: Claude Code, Codex, Gemini CLI, Cursor, Copilot. |
| [quemsah/awesome-claude-plugins](https://github.com/quemsah/awesome-claude-plugins) | Automated adoption metrics tracking across GitHub repos via n8n workflows. |

### Tier 3: Tooling & Utilities

| Repository | Focus |
|---|---|
| [alirezarezvani/claude-code-skill-factory](https://github.com/alirezarezvani/claude-code-skill-factory) | Toolkit for building/deploying production-ready skills, agents, slash commands at scale. |
| [FrancyJGLisboa/agent-skill-creator](https://github.com/FrancyJGLisboa/agent-skill-creator) | Turn any workflow into a reusable SKILL.md installable on 14+ AI tools. |
| [anthropics/skills](https://github.com/anthropics/skills) | Official Anthropic reference skills: art, music, testing, MCP server generation, branding. |
| [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) | Reference CLAUDE.md and best-practice patterns. |
| [SuperClaude-Org/SuperClaude_Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework) | The org home for SuperClaude v4.x with deep research capabilities. |

---

## 2. Claude Code Techniques

### CLAUDE.md Best Practices

**File hierarchy (loaded automatically):**
```
~/.claude/CLAUDE.md          # Global - all sessions
./CLAUDE.md                   # Project root - shared via git
./packages/api/CLAUDE.md      # Subdirectory - loaded on demand
.claude/skills/*/SKILL.md     # Skills - loaded when relevant (~100 tokens scan)
```

**What to include:**
- Tech stack and project structure ("State management is Zustand; see `src/stores`")
- Build/test commands (`npm run test`, `npm run build`)
- Code style rules ("Use ES modules, not CommonJS")
- Architectural patterns and key file locations
- What Claude gets wrong repeatedly

**What NOT to do:**
- Exceed 200 lines per file (bloated files get ignored)
- Say "Never use `--foo-bar`" (say "Prefer `--baz` instead")
- Write a comprehensive manual (document only what causes mistakes)

**Power techniques:**
- Use `@path/to/import` syntax to split content into importable files
- Use emphasis (`IMPORTANT`, `YOU MUST`) for critical rules
- Treat CLAUDE.md like code: review, prune, test, check into git

### Plan Mode

Activate with `/plan` or `Shift+Tab`. Separates thinking from execution.

- Reduces context consumption by 25-45% on complex tasks
- Output tokens cost 5x more than input -- Plan mode controls the bill
- Use before any refactoring touching 3+ files
- Agent proposes a structured plan; you validate before execution begins

### Session Memory (Built-in, 2026)

Claude Code v2.x includes automatic session memory ("Recalled/Wrote memories" messages). Gradual rollout as of early 2026.

**Manual techniques for session continuity:**
- `claude --resume` to continue a previous session
- `/clear` aggressively to manage context pollution
- Structured handoff files in `.claude/session-handoff.md` (75% faster session resumption)
- PreCompact hooks to preserve critical state before automatic compaction

### Subagents and Parallel Work

- Main agent can spawn subagents for parallel work (up to 5 simultaneous in v2.x)
- Each subagent gets its own context window -- keeps the main window clean
- Built-in `/batch` command: decomposes work into 5-30 units, spawns one agent per unit in isolated git worktrees
- Built-in `/simplify`: spawns 3 parallel review agents (reuse, quality, efficiency)

---

## 3. Agent Orchestration Patterns

### Super Nesting: The Current State

**Claude Code intentionally prevents nested agent spawning** (agents spawning agents) to avoid infinite recursion and runaway costs. Subagents cannot spawn other subagents.

**Why this matters:**
- Version 1.0.64 fixed a bug where agents could accidentally access the recursive Task tool
- There is an [active feature request](https://github.com/anthropics/claude-code/issues/4182) for hierarchical agent support

**Workarounds that exist:**
1. **Sequential chaining** -- Main agent spawns subagents in sequence, passing results forward
2. **`claude -p` via Bash** -- Subagents can call `claude -p` to spawn non-interactive instances (but: no progress tracking, no interrupt capability, resource management chaos)
3. **Skills** -- Encode complex multi-step workflows as Skills that the main agent can invoke
4. **Agent Teams** -- One session becomes team lead, spawns full independent Claude Code instances as teammates (one team per session, no nested teams)

### Multi-Agent Architecture Patterns

| Pattern | Description | Best For |
|---|---|---|
| **Hub-and-Spoke** | Central orchestrator manages all agent interactions | Predictable workflows, strong consistency |
| **Mesh (Decentralized)** | Agents communicate directly with each other | Resilient systems, graceful failure handling |
| **Hybrid** | High-level orchestrators + local mesh networks | Strategic coordination + tactical execution |
| **Sequential** | Linear pipeline through fixed agent sequence | Clear dependencies, ordered processes |
| **Plan-and-Execute** | Capable model plans, cheaper models execute | 90% cost reduction vs. frontier-only |

### Leading Multi-Agent Frameworks

| Framework | Strength |
|---|---|
| [LangGraph](https://github.com/langchain-ai/langgraph) | Fastest, fewest tokens. Graph-based architecture passes only state deltas. |
| [CrewAI](https://github.com/crewAIInc/crewAI) | Role-based execution, multi-step task orchestration. |
| [AutoGen](https://github.com/microsoft/autogen) | Flexible multi-agent conversations with role/memory/tool assignment. |
| [Semantic Kernel](https://github.com/microsoft/semantic-kernel) | Enterprise workflows, contextual reasoning, legacy system integration. |
| [Langflow](https://github.com/langflow-ai/langflow) | Low-code framework for RAG and multi-agent systems. |

### Interoperability Protocols

- **MCP** (Model Context Protocol) -- Anthropic's open standard for tool/data integration
- **A2A** (Agent-to-Agent Protocol) -- Google, backed by 50+ companies including Microsoft and Salesforce
- **ACP** (Agent Communication Protocol)
- **ANP** (Agent Network Protocol)

### Key Reference

- [Addy Osmani: Claude Code Swarms](https://addyosmani.com/blog/claude-code-agent-teams/) -- Comprehensive guide to multi-agent coordination
- [Claude Code Swarm Orchestration Skill (Gist)](https://gist.github.com/kieranklaassen/4f2aba89594a4aea4ad64d753984b2ea)
- [Lexo: Claude Code Subagents Guide](https://www.lexo.ch/blog/2025/11/claude-code-subagents-guide-build-specialized-ai-teams/)
- [wshobson/agents](https://github.com/wshobson/agents) -- Multi-agent orchestration for Claude Code
- [Microsoft Agent Design Patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)

---

## 4. MCP (Model Context Protocol)

### What Is MCP?

An open protocol (hosted by The Linux Foundation) that enables LLM applications to connect with external data sources and tools through standardized server implementations.

### Official Resources

| Resource | Link |
|---|---|
| Official reference servers | [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |
| MCP organization | [github.com/modelcontextprotocol](https://github.com/modelcontextprotocol) |
| MCP specification | [spec.modelcontextprotocol.io](https://spec.modelcontextprotocol.io) |

### Key Reference Servers (Official)

| Server | Function |
|---|---|
| **Fetch** | Web content fetching and conversion for LLM usage |
| **Filesystem** | Secure file operations with configurable access controls |
| **Git** | Read, search, and manipulate Git repositories |
| **Memory** | Knowledge graph-based persistent memory system |
| **Sequential Thinking** | Dynamic reflective problem-solving through thought sequences |

### Best MCP Servers by Category (2026)

**Development & DevOps:**
- GitHub MCP Server -- Repository management, commits, PRs, issues, branches
- Playwright MCP Server -- Browser automation and UI testing
- Docker MCP Server -- Container management and debugging

**Databases:**
- PostgreSQL MCP Server -- SQL queries via natural language
- MongoDB MCP Server -- NoSQL document exploration and querying
- Supabase MCP Server -- Full Supabase integration

**General Purpose:**
- Brave Search -- Web search integration
- Notion -- Knowledge base and wiki integration
- Desktop Commander -- System-level operations

### Curated MCP Directories

| Directory | Description |
|---|---|
| [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) | Production-ready and experimental servers |
| [wong2/awesome-mcp-servers](https://github.com/wong2/awesome-mcp-servers) | Popular curated list |
| [tolkonepiu/best-of-mcp-servers](https://github.com/tolkonepiu/best-of-mcp-servers) | Ranked list, updated weekly |
| [mcp-awesome.com](https://mcp-awesome.com/) | 1,200+ quality-verified servers with install guides |

### Claude Code MCP Integration

Claude Code's **MCP Tool Search** feature enables lazy loading for MCP servers, reducing context usage by up to 95%. Configure MCP servers in your project's `.claude/` directory or globally in `~/.claude/`.

---

## 5. AI Agent Skill Libraries

### How Skills Work

Skills are folders containing a `SKILL.md` file with YAML frontmatter and instructions. They use progressive disclosure:
1. **Metadata scan** (~100 tokens) -- Claude identifies relevant skills
2. **Full instructions** (<5k tokens) -- Loaded when Claude determines a skill applies
3. **Bundled resources** -- Files and code loaded only as needed

### Skill Registries & Marketplaces

| Platform | Scale |
|---|---|
| [SkillsMP.com](https://skillsmp.com) | 350,000+ searchable agent skills, compatible with Claude Code, Codex, ChatGPT |
| [claude-plugins.dev/skills](https://claude-plugins.dev/skills) | Browsable registry with in-agent install capability |
| [playbooks.com](https://playbooks.com) | Skill hosting and discovery platform |

### Cross-Platform Skill Standard

Claude Code skills follow the **Agent Skills open standard**, which works across:
- Claude Code
- OpenAI Codex CLI
- GitHub Copilot
- Cursor
- Windsurf
- Gemini CLI
- Antigravity
- Kiro

Install skills universally via: `npx agent-skills-cli add <author>/<repo>`

### Building Your Own Skills

```
.claude/skills/
  my-skill/
    SKILL.md          # YAML frontmatter + instructions
    tools/            # Python/Bash scripts (optional)
    docs/             # Reference documentation (optional)
```

Key resources:
- [Official skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [alirezarezvani/claude-code-skill-factory](https://github.com/alirezarezvani/claude-code-skill-factory) -- Toolkit for building skills at scale
- [FrancyJGLisboa/agent-skill-creator](https://github.com/FrancyJGLisboa/agent-skill-creator) -- One SKILL.md, every platform

---

## 6. Multi-Repo and Monorepo Management

### The Problem

Claude Code does not yet natively support git submodules. Its LS, Grep, and Glob tools cannot traverse submodule boundaries. There is an [active feature request](https://github.com/anthropics/claude-code/issues/7852) for this. Multi-repo remote sessions are also [being requested](https://github.com/anthropics/claude-code/issues/23627).

### Pattern 1: The "Spine" Pattern (Meta-Repository)

A lightweight meta-repository that sits above actual codebases as a context orchestration layer. Not a monorepo, not submodules -- just markdown files and systemized context.

```
spine-repo/
  CLAUDE.md              # Routing hierarchy across all repos
  tasks/                 # Templatized task checklists
  docs/                  # Cross-cutting documentation
  # Actual code repos remain independent
```

Reference: [The Spine Pattern](https://tsoporan.com/blog/spine-pattern-multi-repo-ai-development/) by Titus Soporan

### Pattern 2: The "Planning Repo" Pattern

A git repo containing other git repos, intentionally `.gitignore`-ing them. No submodule tracking, no version coupling.

```
planning-repo/
  .gitignore             # Ignores all nested repos
  CLAUDE.md              # Describes entire ecosystem
  portfolio-a/
    repo-1/              # Independent git repo
    repo-2/              # Independent git repo
  portfolio-b/
    repo-3/
```

Reference: [The Planning Repo Pattern](https://medium.com/@jbpoley/the-planning-repo-pattern-160ee57adcaf) by Jason Poley

### Pattern 3: Polyrepo Synthesis (VS Code Multi-Root Workspaces)

Open multiple repositories in a single VS Code window. Claude Code reads `CLAUDE.md` from each root, creating a "context mesh" of interconnected documentation.

Reference: [Polyrepo Synthesis](https://rajiv.com/blog/2025/11/30/polyrepo-synthesis-synthesis-coding-across-multiple-repositories-with-claude-code-in-visual-studio-code/) by Rajiv Pant

### Pattern 4: CLAUDE.md Context Engineering for Monorepos

For monorepos, avoid putting everything in one massive CLAUDE.md.

**Do:**
- Nest CLAUDE.md files in subdirectories (loaded on demand)
- Use `@path/to/doc` imports for modular documentation
- Place skills in specific packages of the monorepo
- Keep each CLAUDE.md under 10k words (not 47k)

**Don't:**
- Put all context in the root CLAUDE.md
- Use `@` imports for content that is not universally needed (it still loads at startup)

Reference: [How I Organized My CLAUDE.md in a Monorepo](https://dev.to/anvodev/how-i-organized-my-claudemd-in-a-monorepo-with-too-many-contexts-37k7)

### Enterprise Best Practices

- Require small, frequent Git commits and draft PRs
- Batch changes to 5-20 files (a logical subset that compiles and tests independently)
- Augment with MCP-based semantic search for repos that outgrow basic grep
- Scope sessions tightly; never let autonomy outrun your tests

---

## 7. Claude Code Hooks and Automation

### Hook Lifecycle Events

Hooks fire at specific points in Claude's workflow. They are **deterministic** -- unlike CLAUDE.md instructions, which are advisory, hooks guarantee execution.

| Hook | When It Fires | Can Block? |
|---|---|---|
| `PreToolUse` | Before any tool action (file edit, command execution) | Yes |
| `PostToolUse` | After a tool action completes | No |
| `SessionStart` | When a new session begins | No |
| `PreCompact` | Before context compaction (Jan 2026+) | No |
| `Stop` | When agent finishes a response | No |

`PreToolUse` is the most powerful: it can approve or deny actions. Use it for security gates, file protection, and mandatory review enforcement.

### Practical Hook Patterns

**Block dangerous git operations:**
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "command": "check-git-safety.sh"
    }]
  }
}
```

**Auto-lint on file save:**
Hook on `PostToolUse` for file write operations to run ESLint/Prettier automatically.

**Secret scanning before commits:**
Hook on `PreToolUse` for `git commit` to scan staged changes for API keys and passwords.

**Context preservation before compaction:**
Hook on `PreCompact` to save critical state (reduces information loss by 30%).

**Auto half-clone on context overflow (ykdojo pattern):**
Stop hook that triggers `/half-clone` when context usage exceeds 80% -- deterministic and fast, keeps actual messages intact instead of AI summarization.

### CI/CD Integration

- **GitHub Actions**: Anthropic provides an [official Claude Code GitHub Actions integration](https://github.com/anthropics/claude-code-action) for AI-powered CI/CD workflows
- **GitLab CI**: Configure hooks to run quality gates (linting, type checking, security) on MRs
- Results post as PR/MR comments; merges blocked until gates pass

### GitButler Integration

Claude Code hooks can communicate with GitButler to isolate generated code into virtual or stacked branches automatically. Multiple simultaneous Claude Code sessions each communicate with GitButler at each step, isolating changes into one branch per session.

Reference: [GitButler Claude Code Hooks docs](https://docs.gitbutler.com/features/ai-integration/claude-code-hooks)

### Pre-Commit Framework Skill

A dedicated skill manages `.pre-commit-config.yaml`, installs git hooks, and integrates hook runs into CI pipelines across multi-language repositories.

Reference: [pre-commit-skill on playbooks.com](https://playbooks.com/skills/julianobarbosa/claude-code-skills/pre-commit-skill)

---

## 8. Best CLAUDE.md Examples

### Official References

- [Official Best Practices](https://code.claude.com/docs/en/best-practices) -- Anthropic's own guide
- [Official Memory docs](https://code.claude.com/docs/en/memory) -- How Claude reads CLAUDE.md

### Community Examples & Guides

| Resource | What You Learn |
|---|---|
| [HumanLayer: Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) | The authoritative blog post on CLAUDE.md craft |
| [shanraisshan/claude-code-best-practice/CLAUDE.md](https://github.com/shanraisshan/claude-code-best-practice/blob/main/CLAUDE.md) | Full reference CLAUDE.md you can fork |
| [ykdojo/claude-code-tips/GLOBAL-CLAUDE.md](https://github.com/ykdojo/claude-code-tips/blob/main/GLOBAL-CLAUDE.md) | Global CLAUDE.md example with Gemini CLI fallback |
| [NomenAK/SuperClaude/CLAUDE.md](https://github.com/NomenAK/SuperClaude/blob/master/CLAUDE.md) | How SuperClaude configures itself |
| [SFEIR Institute Guide](https://institute.sfeir.com/en/claude-code/claude-code-resources/best-practices/) | Training-grade material |
| [rosmur.github.io/claudecode-best-practices](https://rosmur.github.io/claudecode-best-practices/) | Community best practices site |
| [ClaudeLog.com](https://claudelog.com/) | Docs, guides, tutorials, and best practices hub |

### The CLAUDE.md Cheat Sheet

```markdown
# Project Overview
Brief description. Tech stack. Architecture style.

# Structure
- `src/api/` -- REST endpoints (Express)
- `src/models/` -- Sequelize models
- `src/services/` -- Business logic
- `tests/` -- Jest test files

# Commands
- `npm run dev` -- Start dev server
- `npm test` -- Run all tests
- `npm run lint` -- ESLint check

# Code Style
- Use ES modules (import/export), never CommonJS (require)
- Functional components with hooks, no class components
- All new files need corresponding test files

# IMPORTANT Rules
- NEVER modify files in `src/migrations/` without explicit approval
- Always run `npm test` before committing
- Prefer `--baz` flag over deprecated `--foo-bar`

# Architecture Decisions
- State management: Zustand (see src/stores/ for examples)
- API calls: React Query with custom hooks in src/hooks/
- Auth: JWT tokens stored in httpOnly cookies
```

---

## 9. Agent Memory and Context Management

### Claude Code's Built-in Memory System

| Layer | Scope | Mechanism |
|---|---|---|
| **CLAUDE.md** | Persistent across all sessions | File-based, loaded at session start |
| **Skills** | Loaded on demand | Progressive disclosure (~100 tokens scan) |
| **Session Memory** | Automatic cross-session | "Recalled/Wrote memories" (v2.1.30+, rolling out) |
| **Context Window** | Current session only | 200k tokens, managed via compaction |
| **Subagent contexts** | Per-subagent, ephemeral | Independent windows, up to 5 simultaneous |

### Context Management Strategies

1. **Use `/clear` aggressively** -- Polluted context manifests as hallucinations, repetitions, or outdated conventions
2. **Plan mode first** -- 25-45% less context consumed on complex tasks
3. **PreCompact hooks** -- Preserve critical info before automatic summarization (30% less info loss)
4. **Threshold-based backups** -- Snapshot session state at 30%, 15%, and 5% remaining context
5. **Session handoff files** -- Structured `.claude/session-handoff.md` documenting state, decisions, modified files, next steps

### Community Memory Solutions

| Tool | Approach |
|---|---|
| [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | Plugin that captures tool usage, compresses into structured summaries via Agent SDK, stores in local SQLite |
| [MCP Memory Server](https://github.com/modelcontextprotocol/servers) | Knowledge graph-based persistent memory via MCP |
| [Claude Session Restore](https://github.com/hesreallyhim/awesome-claude-code) | Analyzes session files and git history with time-based filtering for large sessions (up to 2GB) |

### The Broader Agent Memory Landscape (2026)

| Product | Architecture |
|---|---|
| **Letta (MemGPT)** | Memory as first-class agent state. Editable memory blocks, stateful runtime. |
| **Mem0** | Dedicated memory layer that extracts, stores, and retrieves "memories" for personalization. |
| **MemMachine** | Open-source universal memory layer for multi-session persistence across models. |
| **MemOS** | Memory as an OS concern: coordinates facts, summaries, and experiences under one abstraction. |

### Key Insight

> "2026 is 'The Year of Context.' The coming era will not be defined by who has the biggest model, but by who has the best architecture for context, continuity, and governance."

---

## 10. Community Resources

### Official Channels

| Resource | Link |
|---|---|
| Anthropic/Claude Discord | [discord.com/invite/prcdpx7qMm](https://discord.com/invite/prcdpx7qMm) (~66k members) |
| Official Claude Blog | [claude.com/blog](https://claude.com/blog) |
| Claude Code Docs | [code.claude.com/docs](https://code.claude.com/docs) |
| Anthropic API Docs | [platform.claude.com/docs](https://platform.claude.com/docs) |

### Community Hubs

| Resource | Description |
|---|---|
| [Claude Community (CC)](https://claudecode.community/) | Community for Claude Code developers to build together |
| [Roadmap.sh Claude Code](https://roadmap.sh/claude-code) | Step-by-step learning path, 45k-member Discord |
| [Claude Hub](https://www.claude-hub.com/) | Resource discovery and navigation for Claude Code tools |
| [AI Developer Accelerator (Skool)](https://www.skool.com/ai-developer-accelerator) | Discussion forum for practical Claude Code workflows |

### Newsletters & Blogs

| Resource | Focus |
|---|---|
| [AI Coding Daily (Substack)](https://aicodingdaily.substack.com/) | Trending AI coding topics, Claude Code tips, plan mode tricks |
| [ClaudeLog.com](https://claudelog.com/) | Anthropic announcements, product updates, AI news timeline |
| [ClaudeFa.st](https://claudefa.st/) | Blog with MCP extensions, tools, and optimization guides |

### Learning Resources

| Resource | Type |
|---|---|
| [Sankalp's Claude Code 2.0 Guide](https://sankalp.bearblog.dev/my-experience-with-claude-code-20-and-how-to-get-better-at-using-coding-agents/) | In-depth blog on getting better with coding agents |
| [ProductTalk: How to Use Claude Code](https://www.producttalk.org/how-to-use-claude-code-features/) | Guide to slash commands, agents, skills, and plugins |
| [Introl: Claude Code CLI Reference](https://introl.com/blog/claude-code-cli-comprehensive-guide-2025) | Definitive technical reference for the CLI |
| [SFEIR Institute](https://institute.sfeir.com/en/claude-code/) | Training-grade material on context management and best practices |
| [Composio: Top Claude Code Plugins](https://composio.dev/blog/top-claude-code-plugins) | Ranked plugin recommendations |
| [Pixelmojo: All 12 Lifecycle Events](https://www.pixelmojo.io/blogs/claude-code-hooks-production-quality-ci-cd-patterns) | Complete hooks guide with CI/CD patterns |

### Discord Bots & Integrations

| Tool | What It Does |
|---|---|
| [zebbern/claude-code-discord](https://github.com/zebbern/claude-code-discord) | Discord bot for Claude Code: chat, shell/git, branch management |
| [Disclaude](https://disclaude.com/) | Run Claude Code sessions from Discord, each session gets its own channel |

---

## Quick-Start Recommendations for Founders

### Week 1: Foundation
1. Install [Claude Code](https://code.claude.com/) and set up your first `CLAUDE.md`
2. Read the [HumanLayer CLAUDE.md guide](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
3. Install 2-3 relevant skills from [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills)
4. Join the [Anthropic Discord](https://discord.com/invite/prcdpx7qMm)

### Week 2: Acceleration
5. Set up hooks for your dev workflow (lint, test, security scanning)
6. Configure MCP servers for your stack (GitHub, your database, Notion)
7. Learn Plan mode (`Shift+Tab`) and subagent patterns
8. Try [SuperClaude](https://github.com/NomenAK/SuperClaude) for structured slash commands

### Week 3: Scale
9. Implement a multi-repo strategy (Spine, Planning Repo, or Polyrepo Synthesis)
10. Set up CI/CD integration with [Claude Code GitHub Actions](https://github.com/anthropics/claude-code-action)
11. Build custom skills for your team's recurring workflows
12. Explore agent teams and the `/batch` command for parallel work

### Week 4: Optimize
13. Implement session memory/handoff patterns for continuity
14. Set up PreCompact hooks and threshold-based context backups
15. Audit your CLAUDE.md -- prune ruthlessly, document only what prevents mistakes
16. Share your CLAUDE.md and skills across your team via git

---

*Last updated: March 2026. This is a living document -- the ecosystem moves fast.*
