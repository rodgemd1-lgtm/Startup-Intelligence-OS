# Startup Intelligence OS — Codex Handoff Packet

This packet is the clean handoff from the **Decision & Capability OS aggressive plan** into the actual
**Startup-Intelligence-OS** repository.

## What this packet is for

Use this packet to do three things:

1. **Push the plan safely** into the GitHub repo without breaking the existing Susan system.
2. **Give Codex unambiguous context** so it can build instead of reverse-engineering intent.
3. **Sequence the build** from plan import → kernel → interface → evals.

## Recommendation in one line

Push this in **three pull requests**, not one:

- **PR 1 — Plan import**
  - Add the aggressive plan, prototype, scaffold seed, and Codex packet under `docs/plans/decision-capability-os/`.
  - No root behavior changes.
- **PR 2 — Runtime foundation**
  - Add `AGENTS.md`, reconcile `CLAUDE.md`, add `bin/jake`, `.startup-os/`, Jake/Susan agents, and core schemas.
- **PR 3 — Interface shell**
  - Build the initial operator console and wire it to the workspace contract.

## Why this is the safest move

The current public repo is doing two jobs at once:
- the root README presents a founder resource hub
- the root `CLAUDE.md` presents Susan as a central intelligence/orchestration system

That means a direct big-bang rewrite would be risky. The plan-first import gives you a clean review surface
and gives Codex concrete files to work from.

## What is included

- `docs/01-recommended-push-plan.md`
- `docs/02-repo-file-map.md`
- `docs/03-codex-handoff.md`
- `docs/04-codex-prompts.md`
- `docs/05-execution-backlog.md`
- `docs/06-pr-template.md`
- `docs/07-sources.md`
- `scripts/stage-into-repo.sh`
- `assets/decision_capability_os_aggressive_pack/` — the aggressive plan, prototype, and scaffold seed

## Fastest path

1. Read `docs/01-recommended-push-plan.md`
2. Run `scripts/stage-into-repo.sh /path/to/Startup-Intelligence-OS`
3. Commit only the imported plan files in PR 1
4. Paste Prompt 1 from `docs/04-codex-prompts.md` into Codex
5. Let Codex build PR 2 on a new branch / worktree
