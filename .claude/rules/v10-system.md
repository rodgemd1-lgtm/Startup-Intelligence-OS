---
paths:
  - "susan-team-architect/backend/memory/**"
  - "susan-team-architect/backend/research_daemon/**"
  - "susan-team-architect/backend/self_improvement/**"
  - "susan-team-architect/backend/collective/**"
  - "bin/hooks/**"
---

# V10.0 System Rules

## Architecture
V10 adds four new Python modules alongside the existing Susan backend:
- `memory/` — Three-tier memory, TIMG trajectory learning, knowledge graph
- `research_daemon/` — Autonomous research, gap detection, auto-harvest
- `self_improvement/` — TIMG pipeline, routing feedback, performance telemetry
- `collective/` — Research planner, agent factory, knowledge transfer, predictions

## Module Guidelines
- All modules use Pydantic V2 for schemas
- All data persists to `backend/data/memory/` subdirectories as YAML
- No external dependencies beyond pydantic and pyyaml
- Each module has `__main__.py` for CLI access: `python -m <module> --command <cmd>`
- Schemas are defined in each module's `schemas.py`

## Data Directories
```
backend/data/memory/
├── tips/                 # TIMG learned tips
├── graph/                # Knowledge graph JSON
├── research_gaps/        # Detected knowledge gaps
├── harvest_results/      # Auto-harvested research
├── routing_weights/      # Learned routing adjustments
├── performance/          # Agent performance telemetry
├── research_programs/    # Self-directed research programs
├── agent_proposals/      # Proposed new agents
├── transfers/            # Cross-agent knowledge transfers
├── predictions/          # Capability maturity predictions
└── evolutions/           # System evolution proposals
```

## Hook Scripts
- `bin/hooks/session-start.sh` — SessionStart: auto-detect, inject context
- `bin/hooks/session-end.sh` — SessionEnd: auto-HANDOFF
- `bin/hooks/quality-gate.sh` — PostToolUse: syntax/quality checks
- `bin/hooks/stop-gate.sh` — Stop: completeness reminders
- `bin/hooks/model-router.sh` — PreToolUse: cost optimization advisor

## Protection Rules
- These V10 modules are NEW and CAN be modified
- The existing protection zones still apply: control_plane/, mcp_server/, susan_core/
- V10 modules should import FROM protection zones but never modify them

## CLI Reference
```bash
cd susan-team-architect/backend

# Memory system
python -m memory --command extract     # TIMG tip extraction
python -m memory --command consolidate # Memory consolidation
python -m memory --command query "topic" # Query tips
python -m memory --command stats       # Memory statistics
python -m memory --command graph       # Build knowledge graph

# Research daemon
python -m research_daemon --command detect-gaps
python -m research_daemon --command check-updates
python -m research_daemon --command cycle
python -m research_daemon --command status

# Self-improvement
python -m self_improvement --command timg
python -m self_improvement --command routing
python -m self_improvement --command telemetry
python -m self_improvement --command dashboard

# Collective intelligence
python -m collective --command research-plan
python -m collective --command agent-factory
python -m collective --command transfer
python -m collective --command predict
python -m collective --command evolve
```
