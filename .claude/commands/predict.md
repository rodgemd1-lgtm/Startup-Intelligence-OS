---
description: Run V10 predictive capability modeling — forecast maturity timelines and optimal build sequence
---

Run capability predictions. $ARGUMENTS

## Instructions

Execute the V10.0 predictive modeling pipeline:

### Step 1: Predict maturity timelines
```bash
cd susan-team-architect/backend && python -m collective --command predict
```

### Step 2: Generate optimal build sequence
Show which capabilities to build in what order, considering dependencies and impact.

### Step 3: Identify blockers
For any capability that's predicted to miss its target, list the blockers and suggested unblocking actions.

### Step 4: Format forecast
Present the forecast as a structured table:

| Capability | Current | Target | Weeks to Target | Confidence | Top Blocker |
|-----------|---------|--------|-----------------|------------|-------------|

If $ARGUMENTS specifies a capability name, show detailed prediction for that capability only.
