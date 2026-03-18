---
name: structured-context
description: Save or restore machine-readable session state for cross-session continuity. Use when ending a session, checkpointing complex work, or resuming from a prior session.
---

# Structured Context Protocol

Machine-readable session state that survives session boundaries. Replaces prose-based handoffs with structured data Jake can parse on boot.

## When to Invoke
- End of any session with >5 file modifications
- Context health drops to ORANGE or RED
- Switching between projects mid-session
- User says "save state", "checkpoint", "handoff", or "save session"
- At natural milestone boundaries (10%, 25%, 50%, 75%, 90%, 100%)

## Save Protocol

Write `HANDOFF.md` at the project root using this exact schema:

```markdown
# Session Handoff

**Date**: YYYY-MM-DD
**Project**: [project name]
**Session Goal**: [what we set out to do]
**Status**: COMPLETE | PARTIAL | BLOCKED
**Context Health**: GREEN | YELLOW | ORANGE | RED
**Debt Score**: [current technical debt score, 0-50]
**Files Modified**: [count]

## Completed
- [x] Task description — files: `path/to/file1`, `path/to/file2`

## In Progress
- [ ] Task description — state: [description of current state]
  - Files touched: `path/to/file`
  - Next step: [exactly what to do first]
  - Blocker: [none | description]

## Not Started
- [ ] Task description — blocked by: [none | dependency]

## Decisions Made
| Decision | Rationale | Reversible? |
|----------|-----------|-------------|
| [what was decided] | [why] | [yes/no] |

## Active Plan
- Plan file: `.claude/plans/[filename]`
- Current step: [N of M]
- Plan status: [on-track | behind | blocked]

## Memory Updates
- [list any new memories saved this session]

## Parking Lot Additions
- [list any ideas parked this session]

## Resume Instructions
1. Read this file first
2. Read plan file: [path]
3. Run: [specific command or test]
4. Continue from: [exact task and step]
```

## Restore Protocol

On session start, if `HANDOFF.md` exists:

1. Parse the structured fields (Date, Status, Context Health, Debt Score)
2. Load the referenced plan file if one exists
3. Check git status for any uncommitted changes since the handoff
4. Surface the "Resume Instructions" to the user
5. Present a 3-line summary: what was done, what's next, any blockers

## Context Health Thresholds

| Signal | Trigger Save |
|--------|-------------|
| Files modified > 8 | Auto-suggest checkpoint |
| Same file read 3x | Context aging — suggest save |
| 3+ consecutive errors | Quality dropping — force save |
| 15+ tool calls without user interaction | Silent work — suggest checkpoint |
| Plan step completed | Natural checkpoint |

## Integration with Jake's Boot Sequence

Jake's boot (`.claude/rules/jake-boot.md`) already reads `HANDOFF.md` silently during ORIENT phase. This skill ensures the handoff is always machine-parseable so boot can extract:
- What to resume
- Which plan to load
- What the debt score was
- Whether context was healthy when we stopped
