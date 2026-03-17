---
description: Run V10 evolution engine — propose new agents, capabilities, departments, and routing changes
---

Run evolution analysis. $ARGUMENTS

## Instructions

Execute the V10.0 evolution engine:

### Step 1: Analyze task patterns
```bash
cd susan-team-architect/backend && python -m collective --command agent-factory
```
Report any proposed new agents.

### Step 2: Analyze knowledge transfers
```bash
cd susan-team-architect/backend && python -m collective --command transfer
```
Report cross-agent knowledge transfer opportunities.

### Step 3: Generate evolution proposals
```bash
cd susan-team-architect/backend && python -m collective --command evolve
```
Present proposals for:
- New agents (from recurring task patterns)
- New capabilities (from maturity tracking gaps)
- Routing changes (from feedback data)
- Architecture changes (from structural analysis)

### Step 4: Present for approval
Each proposal should include:
- What changes
- Why (evidence)
- Impact assessment
- Reversibility

The user decides which proposals to approve. Do NOT auto-implement.
