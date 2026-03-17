---
description: Load the most recent session file and resume work with full context from where the last session ended.
---

# Resume Session Command

Load the last saved session state and orient fully before doing any work. Counterpart to `/save-session`.

## When to Use

- Starting a new session to continue previous work
- After starting fresh due to context limits
- When handed a session file from another source

## Usage

```
/resume-session                                    # loads most recent
/resume-session 2026-03-17                         # loads most recent for that date
/resume-session ~/.claude/sessions/2026-03-17-abc123de-session.tmp  # specific file
```

## Process

### Step 1: Find the session file

If no argument:
1. Check `~/.claude/sessions/`
2. Pick the most recently modified `*-session.tmp` file
3. If none found:
   ```
   No session files found in ~/.claude/sessions/
   Run /save-session at the end of a session to create one.
   ```
   Then stop.

If argument provided:
- Date (`YYYY-MM-DD`): search for matching files, pick most recent
- File path: read directly
- Not found: report and stop

### Step 2: Read the entire session file

Read the complete file. Do not summarize yet.

### Step 3: Confirm understanding

Respond with a structured briefing:

```
SESSION LOADED: [path]
════════════════════════════════════════════════

PROJECT: [project name / topic]

WHAT WE'RE BUILDING:
[2-3 sentence summary in your own words]

CURRENT STATE:
  Working: [count] items confirmed
  In Progress: [list files in progress]
  Not Started: [list planned but untouched]

WHAT NOT TO RETRY:
[list every failed approach with its reason — this is critical]

OPEN QUESTIONS / BLOCKERS:
[list any blockers or unanswered questions]

NEXT STEP:
[exact next step if defined]
[if not defined: "No next step defined — recommend reviewing 'What Has NOT Been Tried Yet' together"]

════════════════════════════════════════════════
Ready to continue. What would you like to do?
```

### Step 4: Wait for the user

Do NOT start working automatically. Do NOT touch any files. Wait for the user.

- If next step is defined and user says "continue" → proceed with that step
- If no next step → ask where to start, suggest from "What Has NOT Been Tried Yet"

## Edge Cases

**Session file references files that no longer exist:**
Note during briefing: "Warning: `path/to/file.ts` referenced in session but not found on disk."

**Session file is from more than 7 days ago:**
Note: "Warning: This session is from N days ago. Things may have changed." Then proceed.

**Session file is empty or malformed:**
Report: "Session file found but appears empty or unreadable. Create a new one with /save-session."

## Notes

- Never modify the session file when loading it — read-only
- The briefing format is fixed — do not skip sections even if empty
- "What Not To Retry" must always be shown — it's too important to miss
- After resuming, run `/save-session` at the end of the new session
