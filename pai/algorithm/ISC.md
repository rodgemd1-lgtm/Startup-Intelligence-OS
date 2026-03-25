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

## When to Write ISC
- Algorithm Phase 3 (PLAN) — always
- Any task with 3+ deliverables
- Any task where "done" is ambiguous

## When to Skip ISC
- Single-file edits with clear specs
- Quick questions or status checks
- Casual conversation
