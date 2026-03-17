# Workspace Contract Guide

## Root Contract: `.startup-os/workspace.yaml`

The workspace contract is the single source of truth for the OS state.

### Required Fields
```yaml
workspace_id: <string>
workspace_name: <string>
repo_root: /Users/mikerodgers/Startup-Intelligence-OS
active_company: <company-id>
active_project: <project-id>
active_decision: <decision-id>  # optional
active_branch: <git-branch>
runtime_root: susan-team-architect/backend
artifact_root: .startup-os/artifacts
```

## ID Generation
All IDs use deterministic SHA256 hashing:
```
sha256("<type>:<name>:<timestamp>")[:12]
```

| Type | Prefix | Example |
|------|--------|---------|
| Company | `co-` | `co-a1b2c3d4e5f6` |
| Project | `proj-` | `proj-f6e5d4c3b2a1` |
| Decision | `dec-` | `dec-123456789abc` |
| Capability | `cap-` | `cap-abcdef012345` |
| Run | `run-` | `run-fedcba987654` |
| Artifact | `art-` | `art-0123456789ab` |

## Company Records (`.startup-os/companies/`)
```yaml
id: co-<hash>
name: <string>
description: <string>
created_at: <ISO datetime>
status: active | archived
domains: [<string>]
```

## Project Records (`.startup-os/projects/`)
```yaml
id: proj-<hash>
name: <string>
company_id: <company-id>
description: <string>
created_at: <ISO datetime>
status: active | completed | paused
capabilities: [<capability-id>]
decisions: [<decision-id>]
```

## Decision Records (`.startup-os/decisions/`)
```yaml
id: dec-<hash>
name: <string>
project_id: <project-id>
description: <string>
created_at: <ISO datetime>
status: proposed | adopted | rejected | superseded
evidence: [<string>]
outcome: <string>
```

## Capability Records (`.startup-os/capabilities/`)
```yaml
id: cap-<hash>
name: <string>
description: <string>
current_maturity: <0-5>
target_maturity: <0-5>
owner: <string>
dependencies: [<capability-id>]
```

## Maturity Model (0-5 Scale)
| Level | Name | Description |
|-------|------|-------------|
| 0 | Not Started | No capability exists |
| 1 | Ad Hoc | Informal, person-dependent |
| 2 | Defined | Documented process exists |
| 3 | Managed | Measured and controlled |
| 4 | Optimized | Continuously improving |
| 5 | World-Class | Industry-leading, automated |

## Artifact Index (`.startup-os/artifacts/index.yaml`)
Tracks all produced outputs with metadata, dates, and links.

## Run Registry (`.startup-os/runs/registry.yaml`)
Tracks all execution runs with status, timestamps, and outputs.

## Validation
```bash
bin/jake check   # Validates all contracts
bin/jake status  # Prints current state
```
