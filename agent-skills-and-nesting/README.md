# Agent Skills, Super Nesting & Claude Code Ecosystem

Master the art of AI-assisted development with Claude Code, agent orchestration, and nested repository management.

---

## 1. Claude Code Ecosystem — Essential GitHub Repos

### Core Tools & Extensions

| Repository | Description | Stars | Link |
|-----------|-------------|-------|------|
| **anthropics/claude-code** | Official Claude Code CLI by Anthropic | — | [github.com/anthropics/claude-code](https://github.com/anthropics/claude-code) |
| **alirezarezvani/claude-skills** | Collection of installable skills and plugins for Claude Code. Engineering and management tasks. | Growing | [github.com/alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| **gwendall/superclaude** | Toolkit that verifies system setup and authentication. Ensures Git, GitHub, Claude auth are correctly configured. | Growing | [github.com/gwendall/superclaude](https://github.com/gwendall/superclaude) |
| **ykdojo/claude-code-tips** | 40+ tips for using Claude Code including commands for outputting content and opening repos in GitHub Desktop. | Growing | [github.com/ykdojo/claude-code-tips](https://github.com/ykdojo/claude-code-tips) |
| **anthropics/anthropic-cookbook** | Official Anthropic cookbook with examples, guides, and patterns | 10k+ | [github.com/anthropics/anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook) |
| **modelcontextprotocol/servers** | Official MCP server implementations (filesystem, GitHub, Slack, etc.) | 15k+ | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |
| **wong2/awesome-mcp-servers** | Curated list of MCP servers | 5k+ | [github.com/wong2/awesome-mcp-servers](https://github.com/wong2/awesome-mcp-servers) |
| **punkpeye/awesome-mcp-servers** | Another curated MCP server list | Growing | [github.com/punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) |

### Claude Code Community Projects

| Repository | Description | Link |
|-----------|-------------|------|
| **claude-capsule-kit** | Session memory and context management across large codebases | Community |
| **awesome-claude-code** | Curated list of Claude Code resources, tips, and tools | Community |
| **claude-code-templates** | CLAUDE.md templates for various project types | Community |

---

## 2. CLAUDE.md Best Practices

### What Goes in CLAUDE.md

CLAUDE.md files are instruction files that Claude Code reads to understand your project. They form a hierarchy:

```
project-root/
├── CLAUDE.md                    ← Root-level: project-wide rules
├── src/
│   ├── CLAUDE.md                ← Module-level: src-specific rules
│   ├── frontend/
│   │   └── CLAUDE.md            ← Package-level: frontend-specific rules
│   └── backend/
│       └── CLAUDE.md            ← Package-level: backend-specific rules
├── .claude/
│   └── settings.local.json      ← Local Claude Code settings
└── tests/
    └── CLAUDE.md                ← Test-specific conventions
```

### Example Root CLAUDE.md

```markdown
# Project: MyAIStartup

## Tech Stack
- Frontend: Next.js 15, React 19, TypeScript, Tailwind CSS, shadcn/ui
- Backend: Python 3.12, FastAPI, SQLAlchemy
- AI: Claude API (Anthropic), LangChain, Pinecone
- Database: PostgreSQL 16, Redis
- Infrastructure: Vercel (frontend), AWS (backend), Docker

## Code Conventions
- Use TypeScript strict mode
- All Python code must pass ruff and mypy
- Use conventional commits (feat:, fix:, chore:, etc.)
- All API endpoints must have OpenAPI docstrings
- Tests required for all new features

## Architecture
- Frontend calls backend API (no direct DB access from frontend)
- All AI interactions go through the /api/ai/ routes
- Use dependency injection for AI model providers
- Environment variables for all secrets (never hardcode)

## Commands
- `npm run dev` — Start frontend dev server
- `cd backend && uvicorn main:app --reload` — Start backend
- `npm run test` — Run frontend tests
- `cd backend && pytest` — Run backend tests
- `npm run lint` — Lint all code

## Important Files
- `src/lib/ai/client.ts` — AI client configuration
- `backend/app/services/ai_service.py` — AI service layer
- `backend/app/core/config.py` — Configuration management
```

### Tips for Effective CLAUDE.md Files
1. **Be specific** — Tell Claude Code your exact tech stack and versions
2. **Include commands** — List how to build, test, lint, and deploy
3. **Document architecture** — Explain how components connect
4. **Set constraints** — Define what Claude should and shouldn't do
5. **Keep it updated** — Treat it like documentation, maintain it
6. **Use hierarchy** — Different CLAUDE.md files for different concerns

---

## 3. Nested Repository Management

### The Problem
Claude Code treats nested `.git` directories as separate repository boundaries. Files in nested repos aren't indexed as part of the parent.

### Solution 1: Git Submodules (Recommended)

```bash
# Add a nested repo as a submodule
git submodule add https://github.com/org/nested-repo.git path/to/nested

# Clone a repo with all submodules
git clone --recurse-submodules https://github.com/org/parent-repo.git

# Update all submodules
git submodule update --init --recursive

# Pull latest for all submodules
git submodule foreach git pull origin main
```

**Benefits:**
- Claude Code properly indexes submodule contents
- Clean separation of concerns
- Each submodule has its own CLAUDE.md
- Version-locked dependencies

### Solution 2: Manual Navigation (Plan Mode)

```
# In Claude Code, use Shift+Tab to enter plan mode
# Then navigate to specific directories:

cd path/to/nested-repo
# Claude Code now focuses on this repo's context

# Or use direct commands:
cat path/to/nested-repo/src/main.py
```

### Solution 3: Monorepo with Workspaces

```
monorepo/
├── CLAUDE.md                     ← Global rules
├── package.json                  ← Workspace config
├── apps/
│   ├── web/
│   │   ├── CLAUDE.md            ← Web app rules
│   │   └── package.json
│   └── api/
│       ├── CLAUDE.md            ← API rules
│       └── package.json
├── packages/
│   ├── shared/
│   │   └── CLAUDE.md            ← Shared lib rules
│   └── ai-core/
│       └── CLAUDE.md            ← AI module rules
└── .claude/
    └── settings.local.json
```

---

## 4. Model Context Protocol (MCP)

### What is MCP?
MCP (Model Context Protocol) is Anthropic's open standard for connecting AI models to external tools and data sources. Think of it as "USB-C for AI" — a universal interface.

### Architecture
```
Claude Code / AI App
       │
       ▼
   MCP Client
       │
       ▼
  MCP Protocol (JSON-RPC)
       │
       ▼
   MCP Server
       │
       ▼
  External Tool / Data Source
  (GitHub, Slack, DB, Files, API, etc.)
```

### Essential MCP Servers

| Server | What It Does | Link |
|--------|-------------|------|
| **filesystem** | Read/write files on the local system | Official |
| **github** | Interact with GitHub repos, issues, PRs | Official |
| **slack** | Read/send Slack messages | Official |
| **postgres** | Query PostgreSQL databases | Official |
| **puppeteer** | Browser automation and web scraping | Official |
| **brave-search** | Web search via Brave API | Official |
| **memory** | Persistent memory across sessions | Official |
| **sequential-thinking** | Enhanced reasoning with step-by-step thinking | Official |
| **sqlite** | SQLite database operations | Official |
| **google-drive** | Access Google Drive files | Community |
| **notion** | Interact with Notion databases and pages | Community |
| **linear** | Manage Linear issues and projects | Community |

### Setting Up MCP Servers

```json
// .claude/settings.local.json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..."
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

---

## 5. Agent Orchestration Patterns

### Pattern 1: Sequential Pipeline

```python
# Agent A processes → passes to Agent B → passes to Agent C
pipeline = [
    ResearchAgent(),     # Gathers information
    AnalysisAgent(),     # Processes and analyzes
    WritingAgent(),      # Produces final output
]

result = input_data
for agent in pipeline:
    result = agent.run(result)
```

### Pattern 2: Hierarchical (Super Nesting)

```python
# Manager agent delegates to specialist agents
class ManagerAgent:
    def __init__(self):
        self.specialists = {
            "code": CodingAgent(),
            "research": ResearchAgent(),
            "review": ReviewAgent(),
            "test": TestingAgent(),
        }

    def run(self, task):
        # Decompose task
        subtasks = self.plan(task)

        # Delegate to specialists
        results = {}
        for subtask in subtasks:
            specialist = self.route(subtask)
            results[subtask.id] = specialist.run(subtask)

        # Synthesize results
        return self.synthesize(results)
```

### Pattern 3: Parallel Fan-Out

```python
# Run multiple agents in parallel, aggregate results
import asyncio

async def parallel_research(topics):
    agents = [ResearchAgent(topic) for topic in topics]
    results = await asyncio.gather(*[agent.run() for agent in agents])
    return AggregatorAgent().synthesize(results)
```

### Pattern 4: Debate / Red Team

```python
# Two agents argue opposing sides
class DebateOrchestrator:
    def run(self, proposition):
        pro_argument = ProponentAgent().argue(proposition)
        con_argument = OpponentAgent().counter(pro_argument)
        rebuttal = ProponentAgent().rebut(con_argument)

        return JudgeAgent().evaluate([
            pro_argument, con_argument, rebuttal
        ])
```

### Pattern 5: Router / Classifier

```python
# Classify intent, route to specialist
class RouterAgent:
    def run(self, query):
        intent = self.classify(query)  # "code", "data", "creative", etc.

        routes = {
            "code": CodingAgent(),
            "data": DataAgent(),
            "creative": CreativeAgent(),
            "general": GeneralAgent(),
        }

        return routes[intent].run(query)
```

---

## 6. Claude Code Hooks & Automation

### Pre/Post Hooks

Claude Code supports hooks that run shell commands in response to events:

```json
// .claude/settings.local.json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": ["echo 'About to run a bash command'"]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": ["npx prettier --write $CLAUDE_FILE_PATH"]
      }
    ],
    "SessionStart": [
      {
        "hooks": ["npm run typecheck 2>&1 | head -20"]
      }
    ]
  }
}
```

### Common Hook Patterns

| Hook | Trigger | Use Case |
|------|---------|----------|
| **Format on Write** | PostToolUse (Write/Edit) | Auto-format code after Claude writes |
| **Lint Check** | PostToolUse (Write/Edit) | Run linter after code changes |
| **Type Check** | PostToolUse (Write/Edit) | Run TypeScript type checking |
| **Test Runner** | PostToolUse (Write/Edit) | Auto-run related tests |
| **Session Setup** | SessionStart | Verify environment, install deps |
| **Security Check** | PreToolUse (Bash) | Prevent dangerous commands |

---

## 7. Agent Memory & Context Management

### Strategies for Long-Term Memory

| Strategy | Description | Implementation |
|----------|-------------|----------------|
| **CLAUDE.md files** | Persistent project context loaded every session | Write rules, conventions, architecture |
| **MCP Memory Server** | Key-value memory that persists across sessions | `@modelcontextprotocol/server-memory` |
| **Structured Logs** | Save agent decisions and learnings to files | JSON/markdown logs in `.claude/` |
| **Vector Memory** | Embed past interactions, retrieve relevant ones | Local ChromaDB or Pinecone |
| **Session Summaries** | Compress each session into a summary for next session | Auto-generate at session end |
| **Decision Journal** | Track what worked and what didn't | Markdown file updated per session |

### Context Window Optimization

```
Strategies for managing Claude Code's context:
1. Use focused CLAUDE.md files (don't dump everything in root)
2. Break large tasks into subtasks using plan mode
3. Use git submodules for clear repo boundaries
4. Leverage the Agent tool for parallel exploration
5. Keep files focused — one concern per file
6. Use .claudeignore to exclude irrelevant files
```

---

## 8. Claude Code Permissions & Settings

### Settings Hierarchy

```
~/.claude/settings.json              ← Global (user-level)
project/.claude/settings.json        ← Project (shared via git)
project/.claude/settings.local.json  ← Local (gitignored, personal)
```

### Key Settings

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git *)",
      "Bash(python *)",
      "Read",
      "Write",
      "Edit",
      "Glob",
      "Grep"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(sudo *)"
    ]
  },
  "mcpServers": { ... },
  "hooks": { ... }
}
```

---

## 9. Tips & Tricks for Power Users

### Productivity Tips

1. **Use plan mode (Shift+Tab)** — Think before acting. Plan complex changes before writing code.
2. **Use `/compact`** — Compress conversation history when context gets large.
3. **Use the Agent tool** — Delegate exploration to sub-agents. Keeps your main context clean.
4. **Write good CLAUDE.md files** — This is the single highest-leverage action.
5. **Use MCP servers** — Connect Claude Code to your tools (GitHub, Slack, databases).
6. **Automate with hooks** — Auto-format, auto-lint, auto-test after changes.
7. **Use git submodules** — For multi-repo projects, make dependencies explicit.
8. **Structured output** — Ask Claude to output JSON when you need parseable results.
9. **Iterative refinement** — Start simple, add complexity. Don't try to do everything at once.
10. **Use `/cost`** — Monitor your usage and optimize expensive operations.

### Keyboard Shortcuts (CLI)

| Shortcut | Action |
|----------|--------|
| `Shift+Tab` | Toggle plan mode |
| `Ctrl+C` | Cancel current generation |
| `Ctrl+D` | Exit Claude Code |
| `Tab` | Autocomplete file paths |
| `Up Arrow` | Previous command |

### Useful Commands

| Command | Description |
|---------|-------------|
| `/help` | Show help |
| `/compact` | Compress conversation context |
| `/cost` | Show token usage and costs |
| `/clear` | Clear conversation history |
| `/config` | Open settings |
| `/review` | Review recent changes |
| `/commit` | Create a git commit |

---

## 10. Community Resources

| Resource | Platform | Description |
|----------|----------|-------------|
| **Anthropic Discord** | Discord | Official community, Claude Code channel |
| **Claude Code GitHub Issues** | GitHub | Bug reports, feature requests, discussions |
| **r/ClaudeAI** | Reddit | Community discussions, tips, showcases |
| **Anthropic Docs** | Web | Official documentation and guides |
| **Anthropic Cookbook** | GitHub | Code examples and patterns |
| **MCP Specification** | Web | Protocol specification and SDKs |
| **X/Twitter #ClaudeCode** | Twitter/X | Community tips and showcases |

---

*Last updated: March 2026*
