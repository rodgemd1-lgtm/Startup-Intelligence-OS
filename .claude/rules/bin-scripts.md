---
paths:
  - "bin/**"
---

# Bin Scripts Rules

## Core Scripts
- `bin/jake` — root validation, preflight, status, sync-intel
- `bin/os-context` — prints active OS contract and topology
- `bin/mac-push-github` — safe push helper

## Conventions
- Bash scripts: use `#!/usr/bin/env bash`, `set -euo pipefail`
- Python scripts: use `#!/usr/bin/env python3`
- Always define `ROOT_DIR` relative to script location:
  ```bash
  ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
  ```
- Validate prerequisites before executing
- Print clear status messages

## Jake Commands
- `bin/jake` — default preflight check
- `bin/jake check` — validate OS contracts
- `bin/jake status` — print Decision OS status
- `bin/jake sync-intel` — sync agent readiness and operator debrief

## Python Bin Scripts
- `bin/build_department_maturity_dashboard.py`
- `bin/refresh_maturity_surfaces.py`
- `bin/run_simulated_maturity_harness.py`
- These read from `.startup-os/` and `apps/decision_os/data/`
