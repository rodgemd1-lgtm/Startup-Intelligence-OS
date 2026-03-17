---
description: Save current session state to a dated file so work can be resumed in a future session with full context.
---

# Save Session Command

Capture everything that happened in this session — what was built, what worked, what failed, what's left — and write it to a dated file so the next session can pick up exactly where this one left off.

## When to Use

- End of a work session before closing Claude Code
- Before hitting context limits (save first, then start fresh)
- After solving a complex problem you want to remember
- Any time you need to hand off context to a future session

## Process

### Step 1: Gather context

Before writing the file, collect:
- All files modified during this session (use git diff or recall from conversation)
- What was discussed, attempted, and decided
- Any errors encountered and how they were resolved (or not)
- Current test/build status if relevant

### Step 2: Create the sessions folder

```bash
mkdir -p ~/.claude/sessions
```

### Step 3: Write the session file

Create `~/.claude/sessions/YYYY-MM-DD-<short-id>-session.tmp` using today's date and a short ID (8+ lowercase alphanumeric chars or hyphens).

### Step 4: Populate every section below

Write every section honestly. Do not skip sections — write "Nothing yet" or "N/A" if a section has no content. An incomplete file is worse than an honest empty section.

### Step 5: Show the file to the user

After writing, display the full contents and ask:
```
Session saved to [path]

Does this look accurate? Anything to correct or add before we close?
```

## Session File Format

```markdown
# Session: YYYY-MM-DD

**Started:** [approximate time if known]
**Last Updated:** [current time]
**Project:** [project name or path]
**Topic:** [one-line summary]

---

## What We Are Building

[1-3 paragraphs with enough context that someone with zero memory of this session can understand the goal.]

---

## What WORKED (with evidence)

[List only confirmed working items. For each, include WHY you know it works — test passed, ran successfully, output verified, etc.]

- **[thing]** — confirmed by: [specific evidence]

If nothing confirmed: "Nothing confirmed working yet."

---

## What Did NOT Work (and why)

[THIS IS THE MOST IMPORTANT SECTION. List every failed approach with the EXACT reason so the next session doesn't retry it.]

- **[approach]** — failed because: [exact reason / error message]

If nothing failed: "No failed approaches yet."

---

## What Has NOT Been Tried Yet

[Promising approaches not yet attempted. Specific enough for the next session to know exactly what to try.]

- [approach / idea]

---

## Current State of Files

| File | Status | Notes |
|------|--------|-------|
| `path/to/file` | Complete | [what it does] |
| `path/to/file` | In Progress | [what's done, what's left] |
| `path/to/file` | Broken | [what's wrong] |
| `path/to/file` | Not Started | [planned but not touched] |

---

## Decisions Made

[Architecture choices, tradeoffs, approaches chosen and why. Prevents relitigating settled decisions.]

- **[decision]** — reason: [why chosen over alternatives]

---

## Blockers & Open Questions

[Anything unresolved the next session needs to address.]

- [blocker / open question]

---

## Exact Next Step

[The single most important thing to do when resuming. Precise enough that resuming requires zero thinking about where to start.]
```

## Notes

- Each session gets its own file — never append to a previous session's file
- The "What Did NOT Work" section is the most critical — future sessions will blindly retry failed approaches without it
- The file is meant to be read by Claude at the start of the next session via `/resume-session`
- Uses the canonical global session store: `~/.claude/sessions/`
