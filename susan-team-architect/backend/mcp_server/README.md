# MCP Server

Susan's Model Context Protocol server exposing tools for Claude Desktop and Claude Code integration.

## Runtime boundary

This directory is a protected runtime surface. Changes should be minimal, explicit, and validated.

## Tools exposed

- `search_knowledge` — RAG search across 22+ data types
- `run_agent` — Execute a Susan agent with RAG context
- `run_simulation` — Monte Carlo cohort lifecycle simulation
- `get_competitor` — Competitive intelligence lookup
- `list_agents` — Agent roster and specializations
- `ingest_url` — Web content ingestion into knowledge base
- `count_knowledge` — Knowledge base statistics

## Running

```bash
cd susan-team-architect/backend
source .venv/bin/activate
python -m mcp_server
```
