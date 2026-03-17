---
description: Write a HANDOFF.md for session continuity
---

Write session handoff.

## Instructions

1. **Gather state**:
   - Read `.startup-os/workspace.yaml` for active context
   - Run `git status` and `git log --oneline -5` for recent changes
   - Check `.claude/plans/` for any in-progress plans
   - Review what was accomplished in this session

2. **Write HANDOFF.md** at the repo root with:

```markdown
# Session Handoff
Date: <current date and time>
Branch: <current git branch>
Active Company: <from workspace.yaml>
Active Project: <from workspace.yaml>

## Completed
- <what was done this session, with file paths>

## In Progress
- <what's partially done, current state>

## Blocked
- <what's blocked and why, if anything>

## Decisions Made
- <key decisions and their rationale>

## Next Steps
1. <highest priority next action>
2. <second priority>
3. <third priority>

## Files Changed
- <list of modified/created files>

## Notes
- <anything the next session should know>
```

3. **Confirm**: Print a summary of the handoff for the user.
