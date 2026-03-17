---
description: Show V10.0 system status across all seven layers
---

Show V10.0 Startup Intelligence OS status.

## Instructions

Report the status of all seven V10.0 layers:

### Layer 1-2: Hook Infrastructure
- Check `.claude/settings.json` for configured hooks (SessionStart, PreToolUse, PostToolUse, Stop)
- Report which hooks are active

### Layer 3: Memory Architecture
- Check if `susan-team-architect/backend/data/memory/tips/` exists and has tips
- Report tip count, graph node count if graph exists
- Run: `cd susan-team-architect/backend && python -m memory --command stats` if available

### Layer 4: Multi-Agent Orchestration
- Check for orchestrator agent in `.claude/agents/orchestrator.md`
- Report available team templates

### Layer 5: Autonomous Research
- Check daemon status: `cd susan-team-architect/backend && python -m research_daemon --command status` if available
- Report gaps detected, items harvested, programs active

### Layer 6: Self-Improvement
- Check if TIMG tips exist in memory
- Check routing weights: `susan-team-architect/backend/data/memory/routing_weights/`
- Check performance telemetry: `susan-team-architect/backend/data/memory/performance/`

### Layer 7: Collective Intelligence
- Check for research programs: `susan-team-architect/backend/data/memory/research_programs/`
- Check for agent proposals: `susan-team-architect/backend/data/memory/agent_proposals/`
- Check for predictions: `susan-team-architect/backend/data/memory/predictions/`

Format as a dashboard with status indicators for each layer.
