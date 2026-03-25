# OpenClaw Skills Ecosystem — Research Packet
**Date:** 2026-03-25

## Key Numbers
- 13,729 total published skills on ClawHub
- 5,211 curated by VoltAgent's awesome list
- 20+ categories
- 111 prebuilt ClawFlows workflows

## SKILL.md Format
YAML frontmatter (name, description, version, metadata gates) + markdown body.
Three archetypes: prompt-only, code-backed, MCP-wrapper.
65%+ of active skills wrap MCP servers.

## VoltAgent ↔ OpenClaw Bridge
- VoltAgent agents → OpenClaw skills: via MCP server (port 3141+N) + SKILL.md wrapper
- OpenClaw skills → VoltAgent tools: via MCP client in VoltAgent's Tool Registry
- Both directions are native and production-ready

## Security
- 13.4% of ClawHub skills flagged with critical issues (Snyk)
- 341 skills found actively stealing data (Koi Security)
- Use MCP-wrapper pattern for credential-touching agents
- Pin Docker image digests, scope env vars to agent runs

## Susan Migration Pattern
1. Convert prompt-only agents (strategy, studio) to SKILL.md format
2. Add MCP tools for engineering/research agents
3. Build ClawFlows workflows for multi-agent pipelines
4. Publish to ClawHub for community access

## Relevant Skills to Adopt
- self-improving-agent (338 stars) — structured self-improvement methodology
- capability-evolver (35K downloads) — Gene Evolution Protocol
- agent-swarm — multi-agent coordination
- agent-memory — persistent memory
- super-research — combines 8 research skills
- agentic-devops — Docker/process/logs
- apple-mail-search, apple-contacts, apple-music — native Apple integration
