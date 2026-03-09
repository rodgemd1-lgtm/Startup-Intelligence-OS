# Codex Prompts

These are copy/paste prompts for Codex.

---

## Prompt 1 — import and reconcile

```text
You are upgrading this repo into a Decision & Capability OS.

Start by reading:
- docs/plans/decision-capability-os/aggressive-plan.md
- docs/plans/decision-capability-os/operating-model.md
- docs/plans/decision-capability-os/interface-spec.md
- docs/plans/decision-capability-os/capability-gap-map.md
- docs/plans/decision-capability-os/implementation-backlog.md
- docs/plans/decision-capability-os/scaffold-seed/AGENTS.md
- docs/plans/decision-capability-os/scaffold-seed/CLAUDE.md
- README.md
- CLAUDE.md
- susan-team-architect/

Task:
1. explain the current repo architecture
2. identify collisions between the current Susan-centered system and the new Jake + Decision & Capability OS direction
3. propose the smallest safe set of runtime changes for Phase A
4. create a concrete implementation plan with exact files to add or modify
5. do not change files yet
```

---

## Prompt 2 — build Phase A runtime foundation

```text
Implement Phase A only.

Goal:
- make Jake the default front door
- preserve Susan
- add workspace-native structure
- keep changes additive and reviewable

Required work:
- add root AGENTS.md
- merge or update root CLAUDE.md without breaking existing Susan instructions
- add .startup-os/workspace.yaml.example
- add bin/jake
- add bin/os-context
- add .claude/agents/jake.md
- add .claude/agents/susan.md
- add .claude/agents/research.md
- add minimal schemas / file-backed records for:
  - decision
  - capability
  - company
  - project
  - artifact
  - run
- add README notes for how to launch Jake

Requirements:
- mention every file path you change
- keep the terminal primary
- do not build the UI yet
- run the relevant tests or validation checks
- summarize risks and follow-ups
```

---

## Prompt 3 — build Phase B kernel

```text
Implement Phase B only.

Goal:
- create the decision and capability kernel as file-backed primitives

Required work:
- add read/write services for the core objects
- add a minimal artifact index
- add a run/session registry
- wire bin/jake to the workspace contract
- make sure structured artifacts can be created from terminal workflows

Output:
- changed files
- schema design
- example records
- checks run
- next steps
```

---

## Prompt 4 — build Phase C operator console shell

```text
Build apps/operator-console as the initial interface shell.

The interface is mission control, not the place where raw coding replaces the terminal.

Must include:
- Workspace Home
- Decision Room
- Capability Foundry
- Artifact Explorer
- Team Console
- Run Timeline

Must show:
- active workspace
- active backend
- active repo
- active branch/worktree
- current company
- current project
- current decision
- recent artifacts
- Jake summary
- Susan summary

Use the interface spec in:
- docs/plans/decision-capability-os/interface-spec.md

Constraints:
- keep it thin and composable
- use mock or file-backed data first
- add a clear path to real data later
- do not create a bloated design system
```

---

## Prompt 5 — add evals and quality gates

```text
Add the minimum eval and governance layer.

Required work:
- add validation tests for schemas
- add launcher tests if practical
- add a protected-files policy
- add a basic workflow regression check for:
  - jake session start
  - decision record creation
  - capability record creation
- document how to run the checks
```

---

## Prompt 6 — issue-by-issue mode

```text
Create a GitHub issue list for the Decision & Capability OS build.

Use these buckets:
- runtime foundation
- kernel objects
- interface shell
- research workflows
- evals and governance

For each issue include:
- title
- problem
- scope
- files likely affected
- acceptance criteria
- dependencies
```
