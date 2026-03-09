# Repo File Map

## Current repo shape that matters

The public repo currently shows:
- a root `README.md` that describes a startup founder resource hub
- a root `CLAUDE.md` that describes Susan as the central intelligence/orchestration system
- a `susan-team-architect/` directory that contains the active plugin/runtime
- a `docs/plans/` area that is the safest landing zone for new architecture plans

That means the right move is to land this work in two layers:
1. **plan layer**
2. **runtime layer**

## Recommended landing zones

### PR 1 — plan layer only

```text
docs/plans/decision-capability-os/
  README.md
  aggressive-plan.md
  operating-model.md
  interface-spec.md
  capability-gap-map.md
  implementation-backlog.md
  prototype/
    jake-console.html
  scaffold-seed/
    AGENTS.md
    CLAUDE.md
    .startup-os/
    .claude/
    .agents/
    bin/
  codex-handoff/
    README.md
    01-recommended-push-plan.md
    02-repo-file-map.md
    03-codex-handoff.md
    04-codex-prompts.md
    05-execution-backlog.md
    06-pr-template.md
    07-sources.md
```

### PR 2 — promote selected runtime files to active use

```text
AGENTS.md
CLAUDE.md                  # merge carefully with existing intent
.startup-os/
  workspace.yaml.example
  decisions/
  capabilities/
  companies/
  projects/
  artifacts/
  runs/
bin/
  jake
  os-context
.claude/
  agents/
    jake.md
    susan.md
    research.md
  skills/
    decision-room/
    capability-gap-map/
    company-builder/
    research-packet/
.agents/
  skills/
    decision-room/
    capability-gap-map/
    company-builder/
    research-packet/
```

### PR 3 — interface shell

```text
apps/operator-console/
  app/
  components/
  lib/
  public/
  package.json
```

## Promotion rules

- Treat `scaffold-seed/` as **source material**, not the final runtime.
- Let Codex reconcile naming, file placement, and collisions with existing repo structure.
- Do not overwrite root `CLAUDE.md` mechanically; merge it.
- Keep `susan-team-architect/` working during the transition.

## What Codex should preserve

- Susan and the existing Susan workflows
- anything required by the current backend orchestration
- the ability to run terminal-first
- compatibility with the current repo’s RAG and orchestration concepts

## What Codex should add

- Jake as the default front door
- workspace contract
- decision records
- capability records
- artifact index
- run/session registry
- interface shell
