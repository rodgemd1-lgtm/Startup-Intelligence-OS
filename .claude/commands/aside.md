---
description: Answer a quick side question without losing context from the current task. Resume work automatically after answering.
---

# Aside Command

Ask a question mid-task and get an immediate, focused answer — then continue right where you left off. The current task, files, and context are never modified.

## When to Use

- Curious about something while working and don't want to lose momentum
- Need a quick explanation of code currently being edited
- Want a second opinion or clarification without derailing the task
- Need to understand an error, concept, or pattern before proceeding
- Want to ask something unrelated without starting a new session

## Usage

```
/aside <your question>
/aside what does this function actually return?
/aside is this pattern thread-safe?
/aside why are we using X instead of Y here?
```

## Process

### Step 1: Freeze the current task state

Before answering anything, mentally note:
- What is the active task?
- What step was in progress?
- What was about to happen next?

Do NOT touch, edit, create, or delete any files during the aside.

### Step 2: Answer the question directly

Answer concisely but completely.

- Lead with the answer, not the reasoning
- Keep it short — offer to go deeper after the task if needed
- Reference file path and line number if relevant
- Read-only file access is allowed; never write

Format:

```
ASIDE: [restate the question briefly]

[Your answer here]

— Back to task: [one-line description of what was being done]
```

### Step 3: Resume the main task

After answering, immediately continue the active task from the exact point it was paused. Do not ask for permission to resume unless the answer revealed a blocker.

## Edge Cases

**No question provided:**
```
ASIDE: no question provided

What would you like to know?

— Back to task: [current task]
```

**Answer reveals a problem with the current task:**
```
ASIDE: [answer]

Note: This suggests [issue] with the current approach. Want to address this before continuing, or proceed as planned?
```
Wait for user decision before resuming.

**Question is actually a task redirect:**
```
ASIDE: That sounds like a direction change, not a side question.
Do you want to:
  (a) Answer this as information only and keep the current plan
  (b) Pause the current task and change approach
```

**Answer implies a code change is needed:**
Note it but don't make the change:
```
ASIDE: [answer]

Worth fixing: [what should be changed]. I'll flag this after the current task unless you want to address it now.
```

## Notes

- Never modify files during an aside — read-only access only
- The aside is a conversation pause, not a new task
- Keep answers focused: unblock quickly, don't lecture
- If an aside sparks a larger discussion, finish the current task first unless it reveals a blocker
