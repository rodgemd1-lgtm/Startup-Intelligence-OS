# Hermes Perfect Score Plan — Operation 10/10

**Created**: 2026-03-21
**Status**: PHASE 1 COMPLETE — Score 8.0-8.5/10
**Current Score**: ~8.5/10 (up from 6.5)
**Target Score**: 10.0/10 (Grade A+)

## Phase 1: NEVER HANG AGAIN (6.5 → 8.0) — COMPLETE 2026-03-21

### Step 1.1: Create universal timeout wrapper
- **File**: `~/.hermes/scripts/safe_osascript.sh`
- **What**: Shell script that wraps osascript in `timeout 10`
- **Returns**: JSON error on timeout instead of hanging forever
- **Includes**: Mail.app auto-restart logic (killall + relaunch)

### Step 1.2: Patch calendar skill
- **File**: `~/.hermes/skills/macos-calendar/scripts/calendar.sh`
- **What**: Replace raw osascript calls with safe_osascript wrapper
- **Test**: "What's on my calendar today?" returns in <15s

### Step 1.3: Patch SOUL.md osascript blocks
- **File**: `~/.hermes/SOUL.md`
- **Lines**: ~146-178 (calendar and email osascript blocks)
- **What**: Wrap in timeout, add error recovery instructions
- **Rule**: "If any tool returns an error, you MUST send a follow-up explaining the failure. Never go silent."

### Step 1.4: Add brain timeout
- **File**: `~/.hermes/plugins/jake-brain-ingest/__init__.py`
- **What**: Wrap Supabase calls in 8-second timeout
- **Fallback**: Return cached/session data if brain is slow

### Step 1.5: Validate
- Re-run tests 3 (calendar) and 4 (email) via Telegram
- Both must return response within 15 seconds
- Score target: 8.0/10

---

## Phase 2: SHIELD UP (8.0 → 8.8)

### Step 2.1: Create shield plugin
- **File**: `~/.hermes/plugins/jake-shield/__init__.py`
- **Hook**: `post_llm_call` — scan response for PII patterns
- **Patterns**: Phone numbers, email addresses, SSNs
- **Action**: Tag with sensitivity markers

### Step 2.2: Add audit logging
- **File**: `~/.hermes/logs/audit.jsonl`
- **Format**: `{"ts", "tool", "status", "duration_ms", "input_summary"}`
- **Logged by**: shield plugin on every tool execution

### Step 2.3: Validate
- Ask "What do you know about Jacob?" — phone number should be tagged
- Check audit.jsonl for brain_person entry

---

## Phase 3: PULSE MONITOR (8.8 → 9.3)

### Step 3.1: Create cron health checker
- **File**: `~/.hermes/scripts/cron_health_check.sh`
- **Schedule**: Every 30 minutes
- **Checks**: Last output time of each cron, Mail.app responsiveness, Google token validity

### Step 3.2: Add Telegram alerting
- If cron missed >2x its interval: send alert to Mike via Telegram
- If Mail.app hung: auto-restart and notify

### Step 3.3: Add recovery playbook to SOUL.md
- Step-by-step self-repair instructions for each known failure mode

### Step 3.4: Validate
- Kill Mail.app → health check should detect and fix within 30 min

---

## Phase 4: LEARNING LOOPS (9.3 → 10.0)

### Step 4.1: Create learner plugin
- **File**: `~/.hermes/plugins/jake-learner/__init__.py`
- **Hook**: `on_session_end` — analyze conversation
- **Tracks**: Tool failures, unanswered queries, corrections

### Step 4.2: Wire procedural memory
- Write learnings to `jake_procedural` table
- SOUL.md checks procedural memory before responding to similar queries

### Step 4.3: Self-evaluation cycle
- Every 10 conversations: Jake generates a self-assessment
- Surfaces patterns: "I keep failing on X" → auto-suggests fix

### Step 4.4: Validate
- Fail a calendar query → next session Jake should say "last time calendar was broken, let me try the workaround first"
