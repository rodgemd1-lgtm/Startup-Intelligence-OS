---
description: Run the V10 learning cycle — extract tips from runs, consolidate memory, update routing
---

Run V10.0 learning cycle. $ARGUMENTS

## Instructions

Execute the full self-improvement pipeline:

### Step 1: Extract trajectory tips (TIMG)
```bash
cd susan-team-architect/backend && python -m memory --command extract
```
Report how many new tips were extracted.

### Step 2: Consolidate memory
```bash
cd susan-team-architect/backend && python -m memory --command consolidate
```
Report: tips merged, tips pruned, tips promoted.

### Step 3: Update routing weights
```bash
cd susan-team-architect/backend && python -m self_improvement --command routing
```
Report which departments had weight adjustments.

### Step 4: Generate performance dashboard
```bash
cd susan-team-architect/backend && python -m self_improvement --command dashboard
```
Show the top 5 agents and any improvement trends.

### Step 5: Summary
Print a learning cycle summary: tips extracted, memory changes, routing adjustments, performance trends.
