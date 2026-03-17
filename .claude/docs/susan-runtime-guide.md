# Susan Runtime Guide

## Overview
Susan is the startup capabilities foundry — an AI-powered system for capability mapping, operating model design, maturity scoring, team design, and build sequencing.

## Control Plane (`backend/control_plane/`)
- `catalog.py` — Agent catalog: registers, discovers, and routes to agents
- `protocols.py` — Execution protocols: defines how agents communicate and coordinate
- **PROTECTION ZONE** — do not modify without explicit approval

## MCP Server (`backend/mcp_server/`)
- `server.py` — Exposes 7 tools to Claude Desktop and Claude Code
- Tools: search_knowledge, list_agents, invoke_agent, run_simulation, competitor_intel, etc.
- Config: `.mcp.json` (project) and `~/.claude/mcp.json` (global)
- **PROTECTION ZONE** — do not modify without explicit approval

## Susan Core (`backend/susan_core/`)
- Orchestrator: `python3 -m susan_core.orchestrator`
- Agent framework: defines base agent, routing, and execution
- **PROTECTION ZONE** — do not modify without explicit approval

## RAG Engine (`backend/rag_engine/`)
- `batch.py` — Batch processing for RAG ingestion
- `ingestion/` — Data ingestion modules:
  - `web.py` — Web page ingestion
  - `exa_search.py` — Exa search API integration
  - `playwright_scraper.py` — Browser-based scraping
- **Embedding model**: Voyage AI `voyage-3` (1024 dimensions)
- **Vector store**: Supabase with pgvector
- **Chunk count**: 10,788+ across 22+ data types

## CLI Reference

### Susan CLI (`scripts/susan_cli.py`)
```bash
cd susan-team-architect/backend && source .venv/bin/activate

# Foundry mode — full capability analysis
./.venv/bin/python scripts/susan_cli.py foundry <company>

# Route mode — ask Susan to route a request
./.venv/bin/python scripts/susan_cli.py route <company> "<prompt>"
```

### Orchestrator
```bash
python3 -m susan_core.orchestrator --company <company> --mode foundry
```

### Common Scripts
```bash
# Ingestion
python scripts/ingest_founder_intelligence.py
python scripts/ingest_job_studio_training_factory.py

# Scraping
python scripts/run_enterprise_rental_multitool_scrape.py

# Monitoring
python scripts/monitor_department_gap_closure_wave.py
python scripts/monitor_job_studio_pipeline.py

# Health checks
python scripts/provider_key_healthcheck.py
```

## Data Layout
```
backend/data/
├── company_registry.yaml          # All registered companies
├── foundry/
│   └── company_foundry.yaml       # Foundry configuration
├── scrape_manifests/              # Web scraping task definitions
├── domains/                       # Domain-specific data
├── studio_assets/                 # Per-company studio assets
│   └── companies/<company>/
└── startup_os/                    # Startup OS synchronized data
```

## Agent Inventory (33 agents)
Agents are defined in `susan-team-architect/agents/` and symlinked to `~/.claude/agents/`.
Each agent has a specific domain: growth, finance, legal, UX, engineering, security, etc.
Use Susan's routing to determine which agent handles a given request.

## Testing
```bash
cd susan-team-architect/backend && source .venv/bin/activate
python -m pytest tests/ -v

# Key test files
tests/test_exa_ingestor.py
tests/test_mcp_production_tools.py
tests/test_web_crawl.py
```
