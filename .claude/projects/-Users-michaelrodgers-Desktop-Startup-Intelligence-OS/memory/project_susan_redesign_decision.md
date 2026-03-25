---
name: Susan Department Redesign Decision
description: Mike decided to adopt VoltAgent's 126 subagents + Susan's 83 into a department-based org structure with Jake as root supervisor
type: project
---

Susan's agent architecture is being completely redesigned to adopt VoltAgent's gold-standard patterns and merge all 126 VoltAgent subagents with Susan's existing 83 agents (~200+ total).

**Why:** Current architecture is flat (zero supervisors, zero tool definitions, zero typed I/O). VoltAgent provides the engineering platform standard. The awesome-claude-code-subagents repo provides 126 production-ready agent definitions across 10 categories.

**How to apply:**
- Jake becomes root supervisor (CEO), routing to department heads
- Susan's 12 groups + VoltAgent's 10 categories merge into ~15 departments
- Every agent gets: typed tools (Zod), supervisor relationships, durable memory, hooks, guardrails
- Two parallel workstreams: A (Jake v5 + OpenClaw runtime), B (Susan department redesign)
- VoltAgent framework is the engineering standard for all agents
- All agents deployable as OpenClaw skills
- Department supervisors manage sub-agents within their domain

**Key decisions by Mike:**
1. All-in on VoltAgent subagents — direct copy, no cherry-picking
2. Reorganize into departments/specialties Jake can route to
3. Keep Susan's unique domain agents (health/fitness, psychology, film, Oracle Health)
4. Use Claude Code and Codex as execution environments
