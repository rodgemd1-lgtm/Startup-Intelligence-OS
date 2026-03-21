# Hermes Perfect Score Plan — Operation 10/10

**Created**: 2026-03-21
**Status**: ALL PHASES COMPLETE — Score 9.3-10.0/10
**Current Score**: ~9.5/10 (up from 9.3 — self-eval cycle adds the remainder over time)
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

## Phase 2: SHIELD UP (8.0 → 8.8) — COMPLETE 2026-03-21

### Step 2.1: Create shield plugin ✅
- **File**: `~/.hermes/plugins/jake-shield/__init__.py`
- **Hook**: `post_llm_call` — scan response for PII patterns
- **Patterns**: Phone numbers (US), email addresses, SSNs
- **Action**: Detect + log to audit.jsonl (detect-and-log model)
- **Dedup**: tool_use IDs tracked to prevent double-auditing
- **Manifest**: `~/.hermes/plugins/jake-shield/plugin.yaml`

### Step 2.2: Add audit logging ✅
- **File**: `~/.hermes/logs/audit.jsonl`
- **Format**: `{"ts": ISO8601, "tool": str, "status": str, "duration_ms": int, "input_summary": str}`
- **Logged by**: shield plugin — tool calls from message history + PII detections in responses
- **Thread-safe**: uses `threading.Lock()` on file writes

### Step 2.3: Validate ✅
- Phone, email, SSN detection all passing (unit tested)
- Audit log writes verified end-to-end
- Tool call extraction from Anthropic message format tested
- Deduplication across repeated hook calls verified
- register() with mock context verified

---

## Phase 3: PULSE MONITOR (8.8 → 9.3) — COMPLETE 2026-03-21

### Step 3.1: Create cron health checker ✅
- **File**: `~/.hermes/scripts/cron_health_check.sh`
- **Schedule**: Every 30 min via launchd (`~/Library/LaunchAgents/com.jake.pulse-monitor.plist`)
- **Checks**: Cron job freshness (2x interval threshold), Mail.app responsiveness, Google OAuth token
- **Supports**: `--dry-run` flag for testing without Telegram
- **Known behavior**: Mon-Fri jobs show as stale on weekends — expected, not a bug

### Step 3.2: Telegram alerting ✅
- Consolidated one-message-per-run (not spammy)
- Reads TELEGRAM_BOT_TOKEN from `~/.hermes/.env`, chat ID from `config.yaml`
- Mail.app auto-restart with before/after notification
- Logs to `~/.hermes/logs/pulse.log`

### Step 3.3: Recovery playbook in SOUL.md ✅
- Added section: "System Health & Self-Repair (Pulse Monitor Playbook)"
- Covers: Mail.app hung, cron missed, Google OAuth invalid, brain/Supabase timeout
- Includes "checking system health manually" instructions for Jake to use in-session

### Step 3.4: Validate ✅
- Dry run: all checks passing (Mail OK, Google token OK, cron freshness working)
- Correctly detected Oracle Meeting Prep Scanner as stale (expected on Saturday)
- launchd job loaded: `launchctl list | grep jake.pulse` shows `com.jake.pulse-monitor`
- Pulse log writing to `~/.hermes/logs/pulse.log`

---

## Phase 4: LEARNING LOOPS (9.3 → 10.0) — COMPLETE 2026-03-21

### Step 4.1: Create learner plugin ✅
- **File**: `~/.hermes/plugins/jake-learner/__init__.py`
- **Manifest**: `~/.hermes/plugins/jake-learner/plugin.yaml`
- **Hooks**: `post_llm_call` (incremental signal detection) + `on_session_end` (flush + session counter)
- **Tracks**: tool_failure, correction, capability_gap signals
- **Dedup**: tool_result IDs tracked per session, cleared on session end

### Step 4.2: Wire procedural memory ✅
- Writes to `jake_procedural` via `BrainStore.store_procedural()`
- `pattern_type="rule"`, domain inferred per signal type, confidence: correction=0.8, tool_failure=0.7, gap=0.5
- E2E validated: signal → Supabase → confirmed row with correct domain/confidence
- SOUL.md rule added: "Before responding to tools/calendar/email, run brain_search and check for pattern_type:rule results"

### Step 4.3: Self-evaluation cycle ✅
- Every 10 sessions (SESSION_EVAL_INTERVAL), queries last 30 procedural records
- Tallies by signal_type/domain, writes meta-learning to procedural memory
- Sends Telegram summary: top patterns + "Jake will adapt" message
- State persisted in `~/.hermes/logs/learner_state.json`

### Step 4.4: Validate ✅
- All 8 unit tests passing (tool failure, correction, gap, dedup, domain, confidence, register)
- E2E write to Supabase jake_procedural confirmed (macos_tools domain, conf=0.7)
- SOUL.md procedural rule verified at line 144
