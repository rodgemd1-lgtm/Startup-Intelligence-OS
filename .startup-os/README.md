# .startup-os Workspace Kernel

This directory is the file-backed workspace kernel for the Decision & Capability OS.

## Structure

- `workspace.yaml` — active workspace contract (root source of truth)
- `companies/` — company snapshots and profile state
- `projects/` — initiative records and execution tracks
- `decisions/` — decision memos, assumptions, and outcomes
- `capabilities/` — capability definitions and maturity state
- `artifacts/` — generated outputs (maps, plans, briefs)
- `runs/` — execution run manifests and logs
- `sessions/` — operator session breadcrumbs
- `schemas/` — file contracts and templates for OS resources

The runtime source-of-truth remains `susan-team-architect/backend/`.

## Operating rule

At repo root, chat is not the system of record.
The system of record is the combination of:
- `.startup-os/` structured files
- `susan-team-architect/backend/` runtime state
- linked artifacts written by Susan and the control plane

## Workflow

1. Validate contract with `bin/jake`.
2. Use templates from `.startup-os/schemas/templates/` to create new records.
3. Keep linked evidence in `artifacts/` and update run/session breadcrumbs.
4. Refresh operator debrief and agent readiness index with `bin/jake sync-intel`.
5. Run `bin/jake customer-studio seed|validate|report|push-susan|publish [local_drive_path]` to execute and publish Customer User Studio workflows to Susan backend data and local-drive mirrors.

## Role and readiness artifacts

- `capabilities/jake.profile.yaml` — Jake role contract
- `capabilities/susan.profile.yaml` — Susan role contract
- `capabilities/agent-readiness-index.yaml` — synced view of all Susan agents
- `capabilities/gen-chat-os.system.yaml` — Gen Chat OS system contract
