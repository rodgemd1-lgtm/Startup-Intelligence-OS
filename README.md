# Startup Intelligence OS (Decision & Capability OS)

This repository is the **Decision & Capability OS** for Apex Ventures.

- **Jake** is the root front door (`bin/jake`)
- **Susan** is the capability foundry (`susan-team-architect/`)
- **Susan runtime source of truth** is `susan-team-architect/backend/`
- **Workspace kernel** is `.startup-os/`

## Quick start

```bash
# Validate OS contract and critical assets
bin/jake

# Print active OS context
bin/os-context

# Print Decision OS object counts
bin/jake status

# Sync agent readiness and operator debrief
bin/jake sync-intel

# Onboard and inspect the Jake/Claw control plane
bin/jake claw onboard
bin/jake claw status
```

## Operating layout

- `.startup-os/` — file-backed workspace kernel (companies, projects, decisions, capabilities, runs)
- `bin/` — root operating commands (`jake`, `os-context`, `mac-push-github`)
- `susan-team-architect/` — foundry/plugin layer for Susan agents/commands/skills
- `susan-team-architect/backend/` — orchestration + MCP + retrieval runtime
- `docs/plans/decision-capability-os/` — architecture and strategy plans
- `apps/operator-console/` — three-zone operator command center
- `archive/resource-hub/` — legacy founder-resource materials

## Decision OS objects and templates

- Schemas: `.startup-os/schemas/*.schema.yaml`
- Templates: `.startup-os/schemas/templates/*`
- Workspaces:
  - `.startup-os/decisions/` (decision records)
  - `.startup-os/capabilities/` (capability YAML records)
  - `.startup-os/projects/` (project YAML records)
  - `.startup-os/companies/` (company snapshot YAML records)
  - `.startup-os/runs/` (execution run YAML records)

## Jake front door commands

| Command | Description |
|---------|-------------|
| `bin/jake` | Validate OS contract and critical assets |
| `bin/jake check` | Same as default — run all checks |
| `bin/jake status` | Print Decision OS object counts |
| `bin/jake sync-intel` | Regenerate agent readiness index and operator debrief |
| `bin/jake context` | Print active OS context (delegates to `bin/os-context`) |
| `bin/jake claw onboard` | Seed the Jake/Claw registry and onboarding profiles |
| `bin/jake claw status` | Show connector state, auth source, and last verification |
| `bin/jake claw sync` | Probe bridge/native connectors and refresh work briefs |
| `bin/jake claw logs` | Show recent control-plane events |
| `bin/jake claw eject <service>` | Disable a connector cleanly with a logged reason |

## Susan runtime quick run

```bash
cd susan-team-architect/backend
source .venv/bin/activate
python3 -c "from susan_core.orchestrator import run_susan; run_susan('TransformFit', mode='full')"
```

## Operator console

The console is a three-zone command center at `apps/operator-console/`:
- **Left rail**: workspaces, navigation, team console
- **Center**: Jake brief, decision room, primary terminal
- **Right rail**: next actions, workspace summary, design rules

Operator-aware greeting:
- default: `Hello, Mike`
- Susan view: `?operator=susan` (shows `Hello, Susan`)

```bash
cd apps/operator-console
python3 -m http.server 4173
# http://localhost:4173
# http://localhost:4173/?operator=susan
```

### Vercel deployment

```bash
cd apps/operator-console
vercel
vercel --prod
```

## Safe push helper

```bash
bin/mac-push-github
```

Handles remote/branch mismatch, optional merge-main flow, and safe push with confirmation.

## Strategic docs

- [Startup Intelligence Overview](docs/startup-intelligence-overview.md)
- [Implementation Roadmap](docs/plans/decision-capability-os/implementation-roadmap.md)
- [Repo Cleanup Assessment](docs/plans/decision-capability-os/repo-cleanup-assessment.md)
- [One-Year 25x Strategy](docs/plans/decision-capability-os/one-year-25x-strategy.md)
- [Gen Chat OS Execution Plan](docs/plans/decision-capability-os/gen-chat-os-25x-execution-plan.md)
- [Parity Migration Plan](docs/plans/decision-capability-os/startup-intelligence-os-1-parity-migration.md)

## Runtime boundaries

We preserve and do not redefine the active runtime contracts in:
- `susan-team-architect/backend/control_plane/`
- `susan-team-architect/backend/mcp_server/`
- `susan-team-architect/backend/susan_core/`

Changes to these surfaces should be minimal, explicit, and validated.
