# Decision & Capability OS Repo Cleanup Assessment

## Classification

### Keep as active runtime
- `susan-team-architect/backend/` (runtime, orchestration, retrieval, MCP)
- `susan-team-architect/agents/`, `commands/`, `skills/`, `hooks/` (Susan foundry/plugin surfaces)
- `supabase/` (database migrations and environment assets)

### Promote to root operating system
- `README.md` and `CLAUDE.md` (Jake + Susan operating model)
- `bin/jake` (front door validation)
- `bin/os-context` (OS context command)
- `.startup-os/` (workspace kernel)
- `docs/plans/decision-capability-os/` (transformation plans)
- `apps/operator-console/` (future shell scaffold)
- `.claude/`, `.agents/skills/` (root command/agent/skill surfaces)

### Archive as legacy/reference
- Founder resource-hub categories moved under `archive/resource-hub/`

### Remove if redundant
- No destructive removals in this phase; moved to archive for safety and recoverability.

## Collision and confusion findings
- Root `README.md` described a founder resource hub, conflicting with OS role.
- Root `CLAUDE.md` heavily Susan-centric, without clear Jake front-door contract.
- No explicit `.startup-os/` workspace contract existed.
- Resource-hub categories at root obscured active runtime and OS surfaces.

## Target architecture

```
AGENTS.md
CLAUDE.md
README.md
.startup-os/
  workspace.yaml
  companies/
  projects/
  decisions/
  capabilities/
  artifacts/
  runs/
  sessions/
  schemas/
bin/
  jake
  os-context
.claude/
  agents/
  skills/
.agents/skills/
docs/plans/decision-capability-os/
apps/operator-console/
susan-team-architect/
  agents/
  commands/
  backend/
archive/resource-hub/
```

## Implementation phases
1. Establish OS contract and front door docs/scripts.
2. Archive root-level founder resource-hub directories.
3. Validate contract and runtime-facing assets with `bin/jake` and `bin/os-context`.
