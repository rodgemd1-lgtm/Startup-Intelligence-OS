# Recommended Push Plan

## Answer

**Yes — you should push this to the GitHub repo.**
But do it as a **staged import**, not a one-shot rewrite.

## Why

The current repo already has a working Susan-centered architecture and a root `CLAUDE.md`.
Pushing this aggressive plan directly into root files would create unnecessary risk and make review harder.

The safer path is:

1. **Import the plan and scaffold as reference material**
2. **Let Codex reconcile the runtime**
3. **Build the interface shell on top of the workspace contract**

## Recommended branch sequence

| PR | Branch name | Goal | Risk |
|---|---|---|---|
| PR 1 | `plan/decision-capability-os-import` | Import docs, prototype, scaffold seed, and Codex packet under `docs/plans/decision-capability-os/` | Low |
| PR 2 | `feat/decision-kernel-foundation` | Add root/runtime files: `AGENTS.md`, merged `CLAUDE.md`, `.startup-os/`, agents, launcher, schemas | Medium |
| PR 3 | `feat/operator-console-shell` | Build initial interface shell and connect it to workspace + artifact contracts | Medium |
| PR 4 | `feat/research-and-evals` | Add research packet workflow, source grading, evals, and regression checks | Medium |

## What to import in PR 1

Import these as **plan artifacts**, not active runtime files:

```text
docs/plans/decision-capability-os/
  README.md
  aggressive-plan.md
  operating-model.md
  interface-spec.md
  capability-gap-map.md
  implementation-backlog.md
  prototype/jake-console.html
  scaffold-seed/
  codex-handoff/
```

## What not to change in PR 1

Do **not** modify these yet:

- root `README.md`
- root `CLAUDE.md`
- existing `susan-team-architect/`
- existing runtime code under `susan-team-architect/backend/`

## Exact git flow

```bash
cd /path/to/Startup-Intelligence-OS
git checkout main
git pull origin main

git checkout -b plan/decision-capability-os-import

# from the packet directory
bash scripts/stage-into-repo.sh /path/to/Startup-Intelligence-OS

cd /path/to/Startup-Intelligence-OS
git status
git add docs/plans/decision-capability-os
git commit -m "Add Decision & Capability OS aggressive plan and Codex handoff packet"
git push -u origin plan/decision-capability-os-import
```

## Exact PR title

`Add Decision & Capability OS aggressive plan, prototype, scaffold seed, and Codex handoff`

## Merge bar for PR 1

Accept PR 1 if:
- it adds only plan artifacts
- it does not change runtime behavior
- it gives Codex enough material to build PR 2 without guessing
