---
description: View and manage the agent team for a company
allowed-tools: Bash, Read
---

# Susan Team Management

View the current agent team configuration for a company.

## Usage
`/susan-team [company]` — View team manifest for the specified company

## Execution

1. Read `./companies/$1/susan-outputs/team-manifest.json`
2. Display a formatted table of agents with:
   - Agent name and role
   - Model assignment
   - RAG knowledge types
   - Estimated cost per run
   - Group assignment
3. Show total monthly cost estimate
4. Show crew configurations
