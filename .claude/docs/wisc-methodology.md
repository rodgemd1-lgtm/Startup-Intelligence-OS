# WISC Methodology — Workspace-Informed Structured Context

## What is WISC?
WISC is a three-tier context engineering system for Claude Code projects. It ensures Claude always has the right context at the right time without overloading the context window.

## Three Tiers

### Tier 1 — CLAUDE.md (Always Loaded)
- Mission, identity, routing rules
- Quick start commands
- Architecture overview
- Keep under 500 lines
- This is your "elevator pitch" to Claude

### Tier 2 — Rules (`.claude/rules/`, Loaded by Path)
- Each rule file has YAML frontmatter with `paths:` triggers
- Loaded automatically when Claude works on matching files
- Domain-specific guidance: conventions, patterns, gotchas
- 30-80 lines each

### Tier 3 — Docs (`.claude/docs/`, Loaded on Demand)
- Deep reference material: architecture, APIs, schemas
- Claude reads these when it needs deeper context
- Not auto-loaded — pulled when relevant
- Can be longer (100-300 lines)

## Plan File Format (`.claude/plans/`)

```markdown
# Plan: <Feature Name>
Date: YYYY-MM-DD
Status: draft | approved | in-progress | completed

## Context
What exists today and why this change is needed.

## Approach
High-level strategy.

## Steps
1. [ ] Step one with specific files
2. [ ] Step two with specific files
...

## Risks
- Risk and mitigation

## Verification
- How to verify the change works
```

## HANDOFF.md Format

```markdown
# Session Handoff
Date: YYYY-MM-DD HH:MM
Branch: <current branch>

## Completed
- What was done this session

## In Progress
- What's partially done

## Blocked
- What's blocked and why

## Decisions Made
- Key decisions and rationale

## Next Steps
1. First priority
2. Second priority
```

## Commit Conventions
```
type(scope): description

Types: feat, fix, refactor, docs, test, chore, style, perf
Scope: startup-os, decision-os, susan, v5, console, bin, agents
```

## Sub-Agent Strategy
- **Explore**: Broad codebase searches, file discovery
- **Plan**: Architecture decisions, implementation strategy
- **Debugger**: Error investigation, test failures
- **Test-automator**: Test creation and validation
- **Code-reviewer**: Quality review before commit
- Keep main context clean by delegating research
