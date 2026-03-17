---
description: Research and generate a plan for a new feature
---

Plan a feature: $ARGUMENTS

## Instructions

1. **Read context**: Check `.startup-os/workspace.yaml` for active company/project/decision. Read HANDOFF.md if it exists.

2. **Research**: Dispatch an Explore sub-agent to search the codebase for:
   - Related existing code and patterns
   - Test patterns in use
   - Any existing plans in `.claude/plans/` that relate

3. **Check rules**: Read any relevant `.claude/rules/` files for the affected areas.

4. **Generate plan**: Create a plan file at `.claude/plans/<today>-<slug>.md` with:
   - **Context**: What exists today and why this change is needed
   - **Approach**: High-level strategy
   - **Steps**: Numbered, checkable steps with specific file paths
   - **Files to modify**: List all files that will be created or changed
   - **Risks**: What could go wrong and how to mitigate
   - **Verification**: How to verify the change works (tests, manual checks)

5. **Report**: Summarize the plan and ask for approval before proceeding.

Use the Plan agent for architecture decisions. Keep the plan actionable — every step should be executable.
