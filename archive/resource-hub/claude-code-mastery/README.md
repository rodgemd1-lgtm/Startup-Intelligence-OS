# Claude Code Mastery — Skills, Subagents, Hooks & Configuration

> The definitive guide to maximizing Claude Code for AI-native startup development.

---

## 1. CLAUDE.md Configuration

### What Goes in CLAUDE.md
Your `CLAUDE.md` is Claude Code's project memory. It should contain:

```markdown
# CLAUDE.md

## Project Overview
Brief description of what this project does and its architecture.

## Development Commands
- `npm run dev` — Start dev server
- `npm run test` — Run tests
- `npm run build` — Production build
- `npm run lint` — Lint code

## Architecture
- Framework: Next.js 15 + App Router
- Styling: Tailwind CSS v4 + shadcn/ui
- Database: Supabase (Postgres)
- Auth: Clerk
- Hosting: Vercel

## Key Directories
- `src/app/` — Next.js pages and API routes
- `src/components/` — React components
- `src/lib/` — Utilities and helpers
- `src/db/` — Database schema and queries

## Coding Standards
- TypeScript strict mode
- Functional components with hooks
- Server components by default, 'use client' only when needed
- Use Drizzle ORM for database queries
- All API routes return typed responses

## Testing
- Vitest for unit tests
- Playwright for E2E
- Test files co-located with source files (*.test.ts)

## Common Patterns
- Use `cn()` utility for conditional classNames
- Error boundaries wrap all pages
- AI features use streaming responses
```

### CLAUDE.md Hierarchy
1. **`~/.claude/CLAUDE.md`** — Global defaults (your preferences)
2. **`./CLAUDE.md`** — Project root (shared with team)
3. **`./src/CLAUDE.md`** — Directory-specific context
4. **`.claude/CLAUDE.local.md`** — Personal, not committed

### Sources
| Source | URL |
|--------|-----|
| HumanLayer — Writing a Good CLAUDE.md | [humanlayer.dev](https://www.humanlayer.dev/blog/writing-a-good-claude-md) |
| AlexOp — CLAUDE.md, Slash Commands, Skills, Subagents | [alexop.dev](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/) |
| Claude Directory — Complete Guide to CLAUDE.md | [claudedirectory.org](https://www.claudedirectory.org/blog/claude-md-guide) |
| GitHub — claude-code-best-practice CLAUDE.md | [github.com/shanraisshan](https://github.com/shanraisshan/claude-code-best-practice/blob/main/CLAUDE.md) |

---

## 2. Skills System

### What Are Skills?
Skills are reusable prompt templates stored in `.claude/skills/` that Claude Code can invoke with slash commands.

### Skill File Structure
```
.claude/
  skills/
    review-pr.md      → /review-pr
    deploy.md          → /deploy
    write-tests.md     → /write-tests
    create-component.md → /create-component
```

### Example Skill: Code Review
```markdown
# /review-pr

Review the current PR changes with these criteria:

## Security
- Check for injection vulnerabilities (SQL, XSS, command)
- Verify auth checks on all protected routes
- Ensure secrets are not hardcoded

## Performance
- Check for N+1 queries
- Verify proper memoization
- Look for unnecessary re-renders

## Code Quality
- Ensure TypeScript types are correct
- Check for proper error handling
- Verify test coverage for new code

## Output
Provide a structured review with:
1. Critical issues (must fix)
2. Suggestions (should fix)
3. Nitpicks (nice to have)
```

### Example Skill: Component Generator
```markdown
# /create-component

Create a new React component following our standards:

1. Use TypeScript with proper interfaces
2. Use shadcn/ui primitives where applicable
3. Use Tailwind CSS for styling
4. Export from the component's index.ts
5. Include basic Storybook story
6. Add unit tests for any logic

Component name and requirements: {user input}
```

### Startup-Specific Skills to Build
| Skill | Purpose |
|-------|---------|
| `/review-pr` | Automated code review |
| `/write-tests` | Generate tests for current file |
| `/create-component` | Scaffold new React component |
| `/create-api-route` | Scaffold new API endpoint |
| `/create-migration` | Generate database migration |
| `/deploy` | Run deployment pipeline |
| `/debug` | Systematic debugging workflow |
| `/optimize` | Performance optimization audit |
| `/security-audit` | Security review of codebase |
| `/docs` | Generate documentation |

---

## 3. Subagents

### What Are Subagents?
Subagents are specialized Claude instances you can delegate tasks to, running in parallel.

### Creating Custom Subagents
Store in `.claude/agents/`:

```markdown
# .claude/agents/ux-designer.md

You are a UX/UI design expert. Your role is to:

1. Review UI implementations for usability issues
2. Suggest improvements based on UX best practices
3. Ensure accessibility (WCAG 2.1 AA)
4. Check responsive design across breakpoints
5. Verify design system consistency

When reviewing components:
- Check touch targets (min 44x44px)
- Verify color contrast ratios
- Ensure keyboard navigation works
- Check loading states and error states
- Verify animation performance
```

```markdown
# .claude/agents/security-auditor.md

You are a security expert. Your role is to:

1. Scan code for OWASP Top 10 vulnerabilities
2. Check authentication and authorization logic
3. Verify input validation and sanitization
4. Review API endpoint security
5. Check for sensitive data exposure

Report format:
- CRITICAL: Must fix before deploy
- HIGH: Fix within 24 hours
- MEDIUM: Fix within sprint
- LOW: Track for future fix
```

### Built-in Agent Types
| Agent | Purpose |
|-------|---------|
| **general-purpose** | Research, search, multi-step tasks |
| **Explore** | Fast codebase exploration |
| **Plan** | Architecture and implementation planning |

### Using Parallel Subagents
```
Use parallel subagents to:
1. Research the best approach for implementing OAuth with Clerk
2. Analyze our current auth implementation for security issues
3. Compare Clerk vs Auth0 vs Supabase Auth for our use case
```

---

## 4. Hooks System

### What Are Hooks?
Hooks are shell commands that run in response to Claude Code events.

### Hook Configuration (`.claude/settings.json`)
```json
{
  "hooks": {
    "SessionStart": {
      "command": "echo 'Session started' && npm run typecheck"
    },
    "PreToolCall": {
      "command": "echo 'About to use tool: $TOOL_NAME'",
      "tools": ["Write", "Edit"]
    },
    "PostToolCall": {
      "command": "npm run lint -- --fix",
      "tools": ["Write", "Edit"]
    }
  }
}
```

### Useful Hook Examples

**Auto-lint after file changes:**
```json
{
  "PostToolCall": {
    "command": "npx eslint --fix $FILE_PATH",
    "tools": ["Write", "Edit"]
  }
}
```

**Run tests after code changes:**
```json
{
  "PostToolCall": {
    "command": "npm run test -- --changed",
    "tools": ["Write", "Edit"]
  }
}
```

---

## 5. MCP (Model Context Protocol) Servers

### Essential MCP Servers for Startups
| Server | Purpose | Setup |
|--------|---------|-------|
| **GitHub MCP** | Full GitHub integration | `npx @anthropic-ai/mcp-server-github` |
| **Filesystem MCP** | Enhanced file operations | Built-in |
| **PostgreSQL MCP** | Direct database access | `npx @anthropic-ai/mcp-server-postgres` |
| **Brave Search MCP** | Web search | `npx @anthropic-ai/mcp-server-brave` |
| **Memory MCP** | Persistent memory | `npx @anthropic-ai/mcp-server-memory` |
| **Puppeteer MCP** | Browser automation | `npx @anthropic-ai/mcp-server-puppeteer` |
| **Slack MCP** | Team communication | `npx @anthropic-ai/mcp-server-slack` |

### MCP Configuration (`.claude/settings.json`)
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["@anthropic-ai/mcp-server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["@anthropic-ai/mcp-server-postgres"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

---

## 6. Advanced Workflows

### Opus Plan Mode + Sonnet Execution
```
/model opusplan
```
Uses Opus for planning (better reasoning), Sonnet for execution (faster + cheaper).

### Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| `Shift+Tab` | Toggle auto-accept edits |
| `Shift+Tab+Tab` | Toggle plan mode |
| `Esc Esc` | Open rewind menu |
| `@file.ts` | Reference specific file |
| `!command` | Run shell command |

### Slash Commands Reference
| Command | Purpose |
|---------|---------|
| `/init` | Create CLAUDE.md |
| `/model` | Switch model |
| `/compact` | Compress context |
| `/review` | Code review |
| `/clear` | Clear context |
| `/doctor` | Diagnostics |
| `/memory` | Edit memory |
| `/agents` | List/create agents |
| `/mcp` | MCP server status |

### Best Practice: Session Workflow
1. Start with `/init` if no CLAUDE.md
2. Set `/model opusplan` for complex tasks
3. Use `Shift+Tab+Tab` for plan mode first
4. Review plan, then `Shift+Tab` for auto-accept execution
5. Use `/compact` when context gets long
6. Use `Esc Esc` to rewind if something goes wrong

---

## Sources

| Source | URL |
|--------|-----|
| Elliot J Reed — Claude Code Guide & Tips (Jan 2026) | [elliotjreed.com](https://www.elliotjreed.com/amp/ai/claude-code-guide-and-tips) |
| Level Up Coding — Mental Model: Skills, Subagents, Plugins | [levelup.gitconnected.com](https://levelup.gitconnected.com/a-mental-model-for-claude-code-skills-subagents-and-plugins-3dea9924bf05) |
| GenAI Unplugged — Skills, Commands, Hooks & Agents Guide | [genaiunplugged.substack.com](https://genaiunplugged.substack.com/p/claude-code-skills-commands-hooks-agents) |
| Claude Code Masterclass — CLAUDE.md From Start to Finish | [newsletter.claudecodemasterclass.com](https://newsletter.claudecodemasterclass.com/p/claudemd-masterclass-from-start-to) |
| Official Docs — Create Custom Subagents | [code.claude.com](https://code.claude.com/docs/en/sub-agents) |
| Official Docs — Skill Authoring Best Practices | [platform.claude.com](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) |
| KeonArmin — Claude Code Setup & Config | [keonarmin.com](https://keonarmin.com/blog/claude-code-configs) |
| Builder.io — Claude Code MCP Servers | [builder.io](https://builder.io/blog/claude-code-mcp-servers) |

---

*Compiled from live Exa AI + Firecrawl research, March 2026*
