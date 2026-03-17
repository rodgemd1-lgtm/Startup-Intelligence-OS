# Architecture Deep Dive — Startup Intelligence OS

## System Topology

```
┌──────────────────────────────────────────────────────┐
│                    User (Terminal)                     │
│                         │                             │
│                    Claude Code                        │
│                    ┌────┴────┐                        │
│                    │  Jake   │  (front-door agent)    │
│                    └────┬────┘                        │
│                         │                             │
│            ┌────────────┼────────────┐                │
│            ▼            ▼            ▼                │
│    .startup-os/    Susan Runtime   Decision OS        │
│    (YAML kernel)   (Python BE)    (FastAPI)           │
│            │            │            │                │
│            ▼            ▼            ▼                │
│    Workspace       Supabase      File Store           │
│    Contracts       (RAG/vectors) (YAML)               │
└──────────────────────────────────────────────────────┘
```

## Service Map

### 1. Workspace Kernel (`.startup-os/`)
- **Purpose**: File-backed system of record for companies, projects, decisions, capabilities
- **Format**: YAML contracts with deterministic IDs
- **Validation**: `bin/jake check`
- **No runtime dependencies** — pure file system

### 2. Susan Runtime (`susan-team-architect/backend/`)
- **Purpose**: AI agent orchestration, RAG knowledge base, capability analysis
- **Stack**: Python 3.11+, Voyage AI embeddings, Supabase vector store
- **Entry points**: MCP server, CLI, orchestrator
- **Protection zones**: control_plane/, mcp_server/, susan_core/

### 3. Decision OS (`apps/decision_os/`)
- **Purpose**: Decision lifecycle management, maturity scoring, debate framework
- **Stack**: FastAPI, Pydantic v2, file-backed YAML store
- **Port**: 8420
- **Modules**: customer_user_studio, maturity_surfaces, simulated_maturity

### 4. V5 Frontend (`apps/v5/`)
- **Purpose**: Web dashboard for capabilities and maturity
- **Stack**: Next.js App Router, React, TypeScript, Tailwind

### 5. Operator Console (`apps/operator-console/`)
- **Purpose**: Lightweight operator command center
- **Stack**: Static HTML/JS, no build tools

## Data Flow

```
User Request → Jake (routing) → Susan Agent / Decision OS API
                                       │
                                       ▼
                              Supabase (RAG search)
                              or File Store (YAML)
                                       │
                                       ▼
                              Response + Artifact
                                       │
                                       ▼
                              .startup-os/ update
```

## Protection Zones

These directories contain production runtime code. Never modify without explicit user approval:

| Zone | Path | Contains |
|------|------|----------|
| Control Plane | `susan-team-architect/backend/control_plane/` | Agent routing, catalog, protocols |
| MCP Server | `susan-team-architect/backend/mcp_server/` | Claude Desktop/Code integration |
| Susan Core | `susan-team-architect/backend/susan_core/` | Orchestrator, agent framework |

## Key Integration Points

### MCP Tools (7 exposed)
- Search knowledge base
- List/invoke agents
- Run simulations
- Competitor intelligence
- Config in `.mcp.json` and `~/.claude/mcp.json`

### Agent Symlinks
- 33 global agents: `~/.claude/agents/susan-*.md` → `susan-team-architect/agents/`
- 4 project agents: `.claude/agents/` (jake, susan, research variants)

### Command Symlinks
- 5 global commands: `~/.claude/commands/susan-*.md` → project commands
- 14 project commands: `.claude/commands/`

## Environment

- **Supabase**: `zqsdadnnpgqhehqxplio.supabase.co`
- **Embeddings**: Voyage AI `voyage-3`, 1024 dimensions
- **RAG chunks**: 10,788+ across 22+ data types
- **Python venv**: `susan-team-architect/backend/.venv/`
