---
paths:
  - ".startup-os/**"
---

# Startup OS Kernel Rules

## File Types
All files under `.startup-os/` are YAML contracts. Treat them as the system of record.

## Workspace Contract
- `.startup-os/workspace.yaml` is the root contract — always read it before making workspace-level decisions
- Fields: workspace_id, repo_root, active_company, active_project, active_decision, runtime_root, artifact_root

## ID Generation
- All IDs use deterministic SHA256 hashing: `sha256(input)[:12]` with a type prefix
- Company: `co-<hash>`, Project: `proj-<hash>`, Decision: `dec-<hash>`, Capability: `cap-<hash>`
- Run: `run-<hash>`, Artifact: `art-<hash>`

## Maturity Model
- Scale: 0 (not started) to 5 (world-class)
- Each capability record has `current_maturity` and `target_maturity`
- Maturity changes must be evidenced — link to artifact or run

## Directory Structure
- `companies/` — company profiles and metadata
- `projects/` — active project definitions
- `decisions/` — decision records (adopted, proposed, rejected)
- `capabilities/` — capability definitions with maturity scores
- `artifacts/` — produced outputs and deliverables
- `runs/` — execution records and session logs
- `sessions/` — session state snapshots

## Templates
- Check `schemas/templates/` for YAML templates before creating new records
- Always include required fields: id, name, created_at, status

## Validation
- Run `bin/jake check` after modifying workspace contracts
- Ensure all cross-references (company→project→decision) resolve
