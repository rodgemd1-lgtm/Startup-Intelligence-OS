---
paths:
  - ".claude/agents/**"
  - ".claude/skills/**"
  - ".claude/commands/**"
---

# Agent, Skill & Command Definitions

## Agents (`.claude/agents/`)
- YAML frontmatter with `name:`, `description:`, `model:` (optional)
- Body is the system prompt
- Current agents: Jake (front-door), Susan (foundry), research variants
- Global agents symlinked in `~/.claude/agents/` (33 Susan agents)

## Skills (`.claude/skills/<name>/SKILL.md`)
- Each skill is a directory with a `SKILL.md` file
- SKILL.md contains the full skill prompt and instructions
- Current project skills: research-enrichment, link-checker, decision-room, capability-gap-map, company-builder, research-packet, susan-protocols, scrape, film-production

## Commands (`.claude/commands/<name>.md`)
- YAML frontmatter: `description:` (shown in `/` menu)
- Body is the command prompt template
- Use `$ARGUMENTS` placeholder for user input
- Current project commands: 14 susan-* commands, scrape, produce
- Global commands symlinked: susan-ingest, susan-plan, susan-query, susan-status, susan-team

## Routing Integration
- Commands can invoke skills and agents
- Jake routes ambiguous requests to appropriate agent/skill
- Susan commands map to backend CLI operations

## Naming Conventions
- Commands: kebab-case (`plan-feature.md`)
- Skills: kebab-case directory (`optimize-startup/`)
- Agents: kebab-case (`jake.md`)
- Avoid name collisions between project and global levels
