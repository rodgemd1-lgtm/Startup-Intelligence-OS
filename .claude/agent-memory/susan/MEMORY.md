# Susan Agent Memory

## System Architecture (verified 2026-03-09)
- 60 agents across 8 groups in `susan-team-architect/agents/` (6,961 total lines)
- 18 cognitive studios with 8-layer cognitive loop (only first 3 layers operational)
- Decision engine in `apps/decision_os/decision_engine.py` uses rule-based options and heuristic scoring, not LLM
- Capability engine in `apps/decision_os/capability_engine.py` scores on evidence/decision counts, not outcomes
- RAG: 10,788 chunks, Voyage AI voyage-3 embeddings (1024 dim), Supabase pgvector
- MCP server: 7 tools in `susan-team-architect/backend/mcp_server/server.py`
- Control plane: FastAPI in `susan-team-architect/backend/control_plane/main.py`
- File store: generic YAML Repository pattern in `apps/decision_os/store.py`
- CLI: `bin/jake` with 10 commands
- Agent routing: keyword-based in `backend/control_plane/protocols.py` (30+ keyword sets)

## Key Assessment Findings (2026-03-09)
- Aggregate maturity: 1.85/5.0 (Emerging)
- Weakest domain: Data & Analytics (1.2) and Platform Infrastructure (1.3)
- Strongest domain: Intelligence & Research (2.8)
- Critical gap: no auth, no CI/CD, no monitoring, no agent memory, no closed-loop learning
- Highest leverage: Agent Orchestration (making 60 agents collaborate)
- Studios have excellent specs but no writeback, no case libraries, no experiment tracking

## File Locations for Assessment
- Assessment artifact: `.startup-os/artifacts/25x-capability-assessment.md`
- Artifacts index: `.startup-os/artifacts/index.yaml`
- Workspace contract: `.startup-os/workspace.yaml`
- Maturity model: `susan-team-architect/backend/data/foundry/maturity_model.yaml`
- Susan modes: `susan-team-architect/backend/data/foundry/susan_modes.yaml`
- Domain packs: `susan-team-architect/backend/data/domains/` (5 packs)
- Company registry: `susan-team-architect/backend/data/company_registry.yaml` (8+ companies)
