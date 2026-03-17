---
description: Execute an approved plan step by step
---

Execute plan: $ARGUMENTS

## Instructions

1. **Find the plan**: Look in `.claude/plans/` for the specified plan or the most recent one if none specified.

2. **Validate**: Ensure the plan has been reviewed. Check that all referenced files exist and the approach is still valid.

3. **Check protection zones**: Before executing, verify no steps modify:
   - `susan-team-architect/backend/control_plane/`
   - `susan-team-architect/backend/mcp_server/`
   - `susan-team-architect/backend/susan_core/`
   If they do, flag and get explicit approval.

4. **Execute step by step**:
   - Mark each step as in-progress
   - Implement the change
   - Run relevant tests after each step
   - Mark as complete or flag if blocked

5. **Validate after each step**:
   - Run `bin/jake check` if `.startup-os/` files changed
   - Run relevant test suite if code changed
   - Verify no regressions

6. **Update plan**: Mark completed steps in the plan file.

7. **Summary**: Print what was completed, what's remaining, and any issues found.

If a step fails, stop and report rather than continuing with broken state.
