---
paths:
  - "susan-team-architect/**"
---

# Susan Runtime Rules

## PROTECTION ZONES — NEVER MODIFY
These directories are production runtime. Do not edit, rewrite, or restructure:
1. `susan-team-architect/backend/control_plane/` — orchestration and routing
2. `susan-team-architect/backend/mcp_server/` — MCP tool server for Claude Desktop/Code
3. `susan-team-architect/backend/susan_core/` — core orchestrator and agent framework

If a change seems needed in a protection zone, discuss with the user first.

## Safe Zones (can modify with care)
- `backend/scripts/` — CLI tools and batch scripts
- `backend/data/` — company registries, scrape manifests, studio assets
- `backend/rag_engine/` — RAG ingestion and search (Voyage AI embeddings)
- `backend/artifacts/` — generated output files
- `backend/tests/` — test files
- `backend/fitness_intel/` — fitness intelligence pipeline

## RAG Configuration
- Embedding model: Voyage AI `voyage-3` (1024 dimensions)
- NOT OpenAI embeddings (1536 dimensions) — never mix
- Supabase vector store: `zqsdadnnpgqhehqxplio.supabase.co`
- 10,788+ chunks across 22+ data types

## CLI Patterns
```bash
# Activate venv first
cd susan-team-architect/backend && source .venv/bin/activate

# Susan CLI
./.venv/bin/python scripts/susan_cli.py foundry <company>
./.venv/bin/python scripts/susan_cli.py route <company> "<prompt>"

# Orchestrator
python3 -m susan_core.orchestrator --company <company> --mode foundry
```

## MCP Server
- 7 tools exposed: search, agents, simulation, competitor intel, etc.
- Config: `.mcp.json` at repo root and `~/.claude/mcp.json`
- Server entry: `backend/mcp_server/server.py`

## Agent Inventory
- 33 agents available via symlinks in `~/.claude/agents/`
- Project agents in `.claude/agents/` (Jake, Susan, research, etc.)
- Agent definitions in `susan-team-architect/agents/`

## Data Patterns
- Company data: `backend/data/company_registry.yaml`
- Foundry config: `backend/data/foundry/company_foundry.yaml`
- Scrape manifests: `backend/data/scrape_manifests/`
- Domain data: `backend/data/domains/`

## Compatibility
- Preserve all `susan-*` synced commands and MCP flows
- Global command symlinks in `~/.claude/commands/susan-*.md` must remain valid
