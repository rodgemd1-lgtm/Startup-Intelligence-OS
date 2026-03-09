# Execution Backlog

## Phase ordering

| Order | Phase | Why first | Deliverables |
|---|---|---|---|
| 1 | Plan import | safest review surface | docs, prototype, scaffold seed, Codex packet |
| 2 | Runtime foundation | creates the operating contract | AGENTS, CLAUDE merge, Jake launcher, workspace files, agents |
| 3 | Kernel objects | creates durable system state | decision, capability, company, project, artifact, run records |
| 4 | Interface shell | makes the system visible | operator console with core pages |
| 5 | Research + evals | raises quality and repeatability | source grading, packet workflow, evals |
| 6 | Governance | prevents drift | file protections, gates, audit trail |

## Acceptance criteria by phase

### 1. Plan import
- all plan files exist under `docs/plans/decision-capability-os/`
- no active runtime behavior changes
- prototype opens locally

### 2. Runtime foundation
- Jake launcher exists and works
- root instructions are explicit
- workspace contract is documented
- Susan remains usable

### 3. Kernel objects
- core schemas exist
- example records exist
- artifact index and run registry exist
- terminal workflows can write structured state

### 4. Interface shell
- app launches locally
- pages render from file-backed or mock data
- workspace state is visible in UI
- terminal remains primary

### 5. Research + evals
- research packet flow exists
- source quality rubric exists
- at least one regression-style check exists per core workflow

### 6. Governance
- protected files policy exists
- review guidance exists
- validation steps are documented

## Suggested GitHub issues

1. import aggressive plan and Codex handoff
2. reconcile root instructions for Jake + Susan
3. add workspace contract and launcher
4. add core decision/capability/company/project schemas
5. implement artifact index and run registry
6. scaffold operator console app
7. implement workspace home
8. implement decision room
9. implement capability foundry
10. implement artifact explorer and team console
11. add research packet workflow + source grading
12. add evals, checks, and protected-file policy
