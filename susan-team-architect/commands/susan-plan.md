---
description: Run Susan's full 6-phase planning session for a company
allowed-tools: Bash, Read, Write, WebSearch, WebFetch, Agent
---

# Susan Planning Session

Run Susan's complete Team Architect planning session for the specified company.

## Usage
Provide the company name as an argument: `/susan-plan TransformFit`

## Execution

1. Load the company profile from `backend/data/company_registry.yaml`
2. Run the Python orchestrator:

```bash
cd susan-team-architect/backend && python3 -m susan_core.orchestrator --company "$1" --mode full
```

3. Read and summarize the outputs from `./companies/$1/susan-outputs/`:
   - `company-profile.json` — Company overview
   - `analysis-report.json` — Capability gaps and complexity scores
   - `team-manifest.json` — Agent team with roles, models, and costs
   - `dataset-requirements.json` — Data needs per agent
   - `execution-plan.md` — Phased deployment roadmap
   - `be-audit.json` — Behavioral economics retention architecture

4. Present a summary to the user with key decisions and recommendations
