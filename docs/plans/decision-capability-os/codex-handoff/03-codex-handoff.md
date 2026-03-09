# Codex Handoff

## Build objective

Turn the current repository into a **Decision & Capability OS** while preserving the existing Susan system.

The system should help the user:
- build new companies
- build new projects
- manage decisions explicitly
- diagnose and improve capabilities
- keep terminal work and interface work in sync
- use Jake as the front door and Susan as the capability foundry

## Product principle

The **terminal stays primary**.
The **interface is the control plane**.

## Non-negotiables

1. Jake greets at the start of a new session.
2. Susan remains available, but is not the default front door.
3. Every major recommendation should create or update structured artifacts.
4. Workspace state must survive between terminal and interface.
5. The existing repo should not be broken during migration.

## What to read first

Read these files before making changes:

```text
docs/plans/decision-capability-os/aggressive-plan.md
docs/plans/decision-capability-os/operating-model.md
docs/plans/decision-capability-os/interface-spec.md
docs/plans/decision-capability-os/capability-gap-map.md
docs/plans/decision-capability-os/implementation-backlog.md
docs/plans/decision-capability-os/scaffold-seed/AGENTS.md
docs/plans/decision-capability-os/scaffold-seed/CLAUDE.md
```

Then inspect:
```text
README.md
CLAUDE.md
susan-team-architect/
```

## Definition of done for the first build cycle

Ship these in order:

### Phase A — runtime foundation
- add root `AGENTS.md`
- merge root `CLAUDE.md` so Jake is the default front door
- add `.startup-os/workspace.yaml.example`
- add `bin/jake`
- add `bin/os-context`
- add Jake/Susan/research agent files
- add minimal decision/capability/company/project/artifact/run schemas

### Phase B — workspace-native kernel
- create read/write helpers for the core objects
- create file-backed storage under `.startup-os/`
- create a minimal artifact index
- create a run/session registry

### Phase C — interface shell
- create `apps/operator-console/`
- implement Workspace Home
- implement Decision Room
- implement Capability Foundry
- implement Artifact Explorer
- implement Team Console
- show active repo / branch / worktree / company / project / decision

### Phase D — eval and governance basics
- add basic tests for launcher and schema validation
- add minimal regression checks
- add protected-file policy and quality gates

## Important constraints

- Avoid large unreviewable rewrites.
- Prefer additive changes first.
- Keep file paths explicit in prompts and logs.
- Do not treat the current root `CLAUDE.md` as disposable; reconcile it.
- Preserve the current Susan backend and plugin unless a change is necessary and low-risk.

## Recommended working style

- Use a **new worktree or feature branch per phase**.
- Keep each PR reviewable.
- Mention exact file paths in every task.
- Validate after each phase.

## Expected outputs from Codex

For each phase, produce:
- changed file list
- short rationale
- tests / checks run
- open risks
- next recommended phase

## Acceptance criteria

A build is acceptable when:
- the repo still works
- Jake can be launched from the terminal
- workspace state is explicit
- the interface shell reflects workspace state
- decisions and capabilities have first-class structured files
- the handoff between terminal and interface is visible, not implied
