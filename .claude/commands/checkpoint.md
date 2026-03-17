---
description: Create or verify a named git checkpoint for tracking progress and comparing before/after state.
---

# Checkpoint Command

Create, verify, or list named checkpoints in your workflow. Checkpoints are lightweight git tags that let you compare state before and after a change.

## Usage

```
/checkpoint create <name>     — snapshot current state
/checkpoint verify <name>     — compare current state vs checkpoint
/checkpoint list              — show all checkpoints
/checkpoint clear             — remove old checkpoints (keeps last 5)
```

## Create Checkpoint

1. Verify current state is clean (no broken tests, no syntax errors)
2. Create a git stash or lightweight tag with the checkpoint name
3. Log to `.claude/checkpoints.log`:
   ```
   YYYY-MM-DD HH:MM | <name> | <git-short-sha> | <branch>
   ```
4. Report checkpoint created

## Verify Checkpoint

Compare current state against a named checkpoint:

1. Read checkpoint SHA from log
2. Compare:
   - Files changed since checkpoint
   - Lines added/removed
   - Test pass rate now vs then (if tests exist)
3. Report:

```
CHECKPOINT COMPARISON: <name>
============================
SHA then: abc1234  |  SHA now: def5678
Files changed: X
Lines: +Y / -Z
Tests: [pass count] passed / [fail count] failed
Build: [PASS/FAIL]
```

## List Checkpoints

Show all checkpoints with:
- Name
- Timestamp
- Git SHA
- Status (current, behind, ahead)

## Workflow Example

```
[Start feature]    → /checkpoint create feature-start
[Build core]       → /checkpoint create core-done
[Add tests]        → /checkpoint verify core-done
[Refactor]         → /checkpoint create refactor-done
[Ready for PR]     → /checkpoint verify feature-start
```

## Notes

- Checkpoints are local to the session — they use `.claude/checkpoints.log`, not git tags
- The verify step is non-destructive — it only reads and compares
- Pairs well with `/save-session` for end-of-session state capture
