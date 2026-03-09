# Startup Intelligence OS v1 Parity Migration

## Purpose

Document the migration path from the original fragmented repo state to a unified Decision & Capability OS with production-quality scaffolding and working local flows.

## Migration scope

### What moved
- Founder resource hub content -> `archive/resource-hub/`
- Scattered planning docs -> `docs/plans/decision-capability-os/`
- Implicit workspace state -> `.startup-os/workspace.yaml`
- Ad hoc agent definitions -> `.startup-os/capabilities/`

### What was created
- Workspace kernel (`.startup-os/`) with schemas, templates, and records
- Jake front door (`bin/jake`) with validation, status, and sync-intel
- OS context printer (`bin/os-context`)
- Operator console (`apps/operator-console/`) with three-zone layout
- Gen Chat OS system contract
- Company registry with full Apex portfolio
- Strategic planning documents

### What was preserved
- Susan runtime (`susan-team-architect/backend/`)
- Control plane, MCP server, and core orchestrator
- All existing agent definitions
- RAG knowledge base and embeddings

## Parity checklist

- [x] Workspace kernel with all object types
- [x] Schemas for decision, capability, project, company, run
- [x] Templates for all object types
- [x] Jake profile and Susan profile
- [x] Gen Chat OS system contract with debate modes
- [x] Agent readiness index (auto-generated)
- [x] Operator console with three-zone layout
- [x] bin/jake with check, status, sync-intel commands
- [x] bin/os-context for contract printing
- [x] Company registry with all portfolio companies
- [x] Strategic docs (overview, roadmap, 25x strategy, execution plan)
- [x] Archive structure for legacy content
- [x] Runtime boundaries documented and preserved

## Post-migration validation

```bash
bin/jake check
bin/jake status
bin/jake sync-intel
bin/os-context
```

All four commands must pass cleanly.
