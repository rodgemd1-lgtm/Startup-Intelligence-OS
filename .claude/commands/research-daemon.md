---
description: Run the V10 autonomous research daemon — detect gaps, harvest knowledge, generate digest
---

Run autonomous research. $ARGUMENTS

## Instructions

Execute the V10.0 research daemon cycle:

### Step 1: Detect knowledge gaps
```bash
cd susan-team-architect/backend && python -m research_daemon --command detect-gaps
```
Report gaps found with severity.

### Step 2: Check dependency updates
```bash
cd susan-team-architect/backend && python -m research_daemon --command check-updates
```
Report any new versions or breaking changes.

### Step 3: Run harvest cycle
```bash
cd susan-team-architect/backend && python -m research_daemon --command cycle
```
Report items harvested, quality scores.

### Step 4: Generate digest
```bash
cd susan-team-architect/backend && python -m research_daemon --command digest
```
Present the weekly research digest to the user.

If $ARGUMENTS contains "full", run the complete cycle. If it contains "gaps", only detect gaps. If it contains "updates", only check dependency updates.
