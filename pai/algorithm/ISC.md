# ISC — Ideal State Criteria

Adapted from Daniel Miessler's ISC methodology for Jake PAI.

## Format
Each criterion follows this exact format:
```
ISC-C{N} [{Confidence}] {Description in 8-12 words} | Verify: {Method}
```

## Confidence Tags
- **[E]** — Explicit: User stated this directly
- **[I]** — Inferred: Logically follows from what user said
- **[R]** — Reverse-engineered: Deduced from context/domain knowledge

## Anti-Criteria
Prohibited states that MUST NOT be true:
```
ISC-A-{N} {Description} | Verify: {Method}
```

## Example
Task: "Add dark mode to the dashboard"

```
ISC-C1 [E] Dashboard supports both light and dark color themes | Verify: Toggle switch works
ISC-C2 [I] User preference persists across browser sessions | Verify: Reload retains theme
ISC-C3 [I] All text maintains WCAG AA contrast in both modes | Verify: Lighthouse audit
ISC-C4 [R] No flash of wrong theme on page load | Verify: Fresh load in each mode
ISC-C5 [I] System theme preference detected on first visit | Verify: prefers-color-scheme
ISC-A-1 No hardcoded color values in component files | Verify: grep for hex codes
ISC-A-2 No broken layouts when switching themes | Verify: Visual regression test
```

## Rules
1. Exactly 8-12 words per criterion description
2. Binary testable — every criterion has a clear PASS/FAIL
3. Evidence required — VERIFY field must name concrete method
4. Define BEFORE building — criteria are set in PLAN phase
5. Anti-criteria catch edge cases — what MUST NOT happen
6. Minimum 5 criteria, maximum 12 per task
7. At least 2 anti-criteria per task

## Usage in Algorithm v1

ISC criteria are created in Phase 3 (PLAN) and verified in Phase 6 (VERIFY).
The verification matrix in Phase 6 maps 1:1 to ISC criteria with evidence.
