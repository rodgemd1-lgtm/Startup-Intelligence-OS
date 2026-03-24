# Context Health Monitoring (Jake's Guardian Mind)

## Automatic Tracking

During every session, track these metrics mentally and alert Mike when thresholds are crossed:

### Signal 1: File Scatter
- Count unique files modified in this session
- **YELLOW at 8 files**, ORANGE at 12, RED at 16+
- Say: "We've modified [N] files. Context is spreading thin."

### Signal 2: Architectural Drift
- Compare current modifications against the plan document
- If any change contradicts the plan, immediately ask:
- "This change conflicts with our plan at [section]. Is this intentional?"

### Signal 3: Repeated Reads
- If the same file is read 3+ times in a session, context is aging
- Say: "I keep re-reading [filename] — context is aging. Should we checkpoint?"

### Signal 4: Error Accumulation
- After 3+ consecutive tool failures (Edit rejected, Bash error, test failure):
- STOP and say: "Error rate is climbing. Let me step back and diagnose before continuing."

### Signal 5: Scope Creep
- If work touches files not mentioned in the current plan/task:
- Say: "This file isn't in our plan. Are we expanding scope?"

### Signal 6: Silent Work
- After 15+ tool calls without asking Mike anything:
- Say: "I've been working silently for a while. Here's where we are: [summary]"

## Context Budget Check — 60% HARD LIMIT (DOCTRINE)

**Context health must NEVER exceed 60%. This is non-negotiable.**

Before starting any task estimated to take >10 tool calls:
1. Estimate files to read, modify, and tests to run
2. Check context window usage percentage
3. If estimated work exceeds 60% of remaining budget:
   - Say: "This task will exceed our 60% context budget. Splitting into sessions."
   - Provide session split with clear handoff points
4. If context usage approaches 60% during work:
   - STOP immediately
   - Commit any working code
   - Write structured handoff to HANDOFF.md
   - Push to GitHub
   - Say: "Context at 60%. Handoff written, pushed. Start a new session."

**The 60% rule exists because:**
- Quality degrades past 60% — the model starts losing earlier context
- Errors compound — decisions made at 80% context are based on degraded information
- Handoffs are cheap — starting fresh with HANDOFF.md costs 5 minutes, bad decisions cost days

## Session Boundary Protocol

When any signal hits ORANGE or context approaches 60%:
1. Stop current work
2. Commit any working code
3. Write structured handoff to HANDOFF.md
4. Push commits to GitHub
5. Say: "Context health is [ORANGE/RED]. Handoff written and pushed. Pick up in a new session."

**The handoff-push-new-session cycle is a FIRST-CLASS operation, not a failure mode.**
