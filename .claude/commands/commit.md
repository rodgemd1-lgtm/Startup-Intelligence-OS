---
description: Create a conventional commit with auto-detected type and scope
---

Create a commit for the current changes.

## Instructions

1. **Analyze changes**: Run `git diff --staged` and `git diff` to understand all changes. If nothing is staged, suggest what to stage.

2. **Auto-detect type**:
   - New files/features → `feat`
   - Bug fixes → `fix`
   - Code restructuring → `refactor`
   - Documentation only → `docs`
   - Test files only → `test`
   - Build/config changes → `chore`
   - Formatting only → `style`
   - Performance improvements → `perf`

3. **Auto-detect scope** from changed file paths:
   - `.startup-os/` → `startup-os`
   - `apps/decision_os/` → `decision-os`
   - `susan-team-architect/` → `susan`
   - `apps/v5/` → `v5`
   - `apps/operator-console/` → `console`
   - `bin/` → `bin`
   - `.claude/` → `agents` or `skills` or `commands` as appropriate
   - Multiple areas → use the primary area or omit scope

4. **Draft message**: `type(scope): description`
   - Description: imperative mood, lowercase, no period
   - Keep under 72 characters
   - Add body if the change is complex

5. **Present to user**: Show the proposed commit message and what will be committed. Wait for approval.

6. **Commit**: Stage the relevant files and create the commit. Do not use `git add -A` — add specific files.
