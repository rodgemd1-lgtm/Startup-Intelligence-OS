# Decision & Capability OS Implementation Roadmap

## Objective
Build a production-ready Decision OS at repo root while preserving Susan runtime as the orchestration engine.

## Phase A — Contract hardening (complete)
- Root operating model updated (Jake front door, Susan foundry, runtime source of truth).
- Workspace kernel and archive boundaries established.

## Phase B — Workspace execution primitives (complete)
- Added baseline schemas for decisions, capabilities, projects, companies, and runs.
- Added templates for each object type.
- Added directory READMEs to standardize file creation and usage.

## Phase C — Operational workflows (next)
- Add `bin/jake new decision|capability|project|run` generators.
- Add lightweight index files per workspace directory.
- Introduce automated linkage checks (decision -> project/capability references).

## Phase D — Operator experience (next)
- Scaffold operator-console app routes for Decisions, Capabilities, Runs.
- Add API adapters for Susan runtime calls from operator-console.

## Phase E — Governance and quality (next)
- Version schemas and validate records against schema contracts.
- Add decision quality scoring rubric and review cadence.
- Add capability maturity scorecards and monthly portfolio health checks.

