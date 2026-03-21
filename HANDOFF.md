# Session Handoff

**Date**: 2026-03-21 ~11:35 MDT
**Project**: Startup Intelligence OS / Hermes (Big Birch)
**Session Goal**: Execute Phase 1 of Operation Perfect Score — "Never Hang Again"
**Status**: COMPLETE — Calendar and Email both working, tested live on Telegram

## Completed

- [x] **safe_osascript.sh** — universal timeout wrapper with auto-restart + retry
  - File: `~/.hermes/scripts/safe_osascript.sh`
  - Handles: timeout kills, -600 app errors, auto-restart Mail/Calendar/Reminders
  - Tested: timeout path, success path, kill-and-retry path all verified
- [x] **calendar_read / email_read / reminders_read tools** — deterministic Hermes plugin tools
  - File: `~/.hermes/plugins/jake-brain-ingest/__init__.py`
  - Why tools instead of SOUL.md code blocks: LLM was improvising raw osascript instead of using the safe wrapper. Tools are deterministic — no improvisation.
  - Fixed positional arg dispatch issue (Hermes passes params as first positional arg, not kwargs)
- [x] **Brain plugin timeouts** — 8s cap on all Supabase calls (brain_search, brain_person, brain_entities)
  - File: `~/.hermes/plugins/jake-brain-ingest/__init__.py`
  - Uses `concurrent.futures.ThreadPoolExecutor` with timeout
- [x] **SOUL.md patches** — error recovery rule + tool routing table
  - File: `~/.hermes/SOUL.md`
  - Added: "NEVER go silent" error recovery rule
  - Added: Tool routing table (calendar→calendar_read, email→email_read, reminders→reminders_read)
  - Removed: raw osascript code blocks for calendar/email/reminders (replaced by tools)
  - Kept: Google Calendar Python API block (not osascript, doesn't need wrapper)
- [x] **calendar.sh patched** — calendar skill uses safe wrapper for all osascript calls
  - File: `~/.hermes/skills/macos-calendar/scripts/calendar.sh`
- [x] **Live Telegram testing** — 5 rounds of testing, both calendar and email working
  - Calendar: F → A+ (reads events, returns in <10s)
  - Email: F → A+ (reads inbox, identifies priority emails, filters spam)

## Test Results (Final Round — 11:31 AM)

| Test | Grade | Details |
|------|-------|---------|
| Calendar | A+ | "Calendar is looking deadass clear. Nothing on the books." |
| Email | A+ | Read 10 emails, flagged Matt Cohlmia HIMSS notes, filtered Amazon spam |
| Response time | A+ | Both tools completed in <15s, response delivered in <30s |
| Error recovery | A+ | When tools failed earlier, communicated clearly with alternatives |
| Tool usage | A | Uses calendar_read/email_read tools (not raw osascript) |

## Files Modified (all in ~/.hermes/, NOT in git repo)

| File | Change |
|------|--------|
| `~/.hermes/scripts/safe_osascript.sh` | NEW — timeout wrapper with auto-restart |
| `~/.hermes/plugins/jake-brain-ingest/__init__.py` | Added 3 tools + brain timeouts + fixed arg dispatch |
| `~/.hermes/SOUL.md` | Error recovery rule, tool routing table, removed raw osascript |
| `~/.hermes/skills/macos-calendar/scripts/calendar.sh` | Wrapped osascript calls in safe_osa |

## Scoring Update

| Dimension | Before (6.5/10) | After Phase 1 |
|-----------|-----------------|---------------|
| Brain | 6.7 | 7.0 (timeouts added) |
| Hands | 5.3 | **8.5** (calendar + email working, no hangs) |
| Feet | 7.0 | 7.5 (error recovery rule) |
| **Overall** | **6.5** | **~8.0-8.5** |

## Remaining Phases (from Operation Perfect Score plan)

### Phase 2: SHIELD UP (8.5 → 9.0)
- PII detection plugin (`~/.hermes/plugins/jake-shield/`)
- Audit logging (`~/.hermes/logs/audit.jsonl`)
- Plan: `.claude/plans/2026-03-21-hermes-perfect-score.md`

### Phase 3: PULSE MONITOR (9.0 → 9.3)
- Cron health checker
- Telegram alerting on cron failures
- Mail.app auto-restart on cron schedule

### Phase 4: LEARNING LOOPS (9.3 → 10.0)
- Conversation analysis plugin
- Procedural memory for learned workarounds

## Decisions Made

| Decision | Rationale | Reversible? |
|----------|-----------|-------------|
| Tools > SOUL.md code blocks | LLM improvises raw osascript, tools are deterministic | Yes |
| safe_osascript.sh auto-restarts apps | Mail.app gets stale after long runtime, -600 errors | Yes |
| params=None pattern for tool handlers | Hermes dispatches tool args as first positional arg | Yes |
| Kept Google Calendar as Python in SOUL.md | Not osascript, doesn't need wrapper treatment | Yes |

## Known Issues

- **Mail.app staleness**: After ~24h of runtime, Mail.app stops responding to osascript (-600). The safe wrapper now auto-restarts it, but a cron health check (Phase 3) would be more proactive.
- **Google Calendar tokens expired**: Getting "Unauthorized" on Google Calendar API. Needs token refresh. Not blocking — Apple Calendar works.

## Context for Next Session

- **Key insight**: The tools approach (calendar_read, email_read) is the right architecture. SOUL.md code blocks are suggestions; tools are deterministic. Always prefer tools for macOS automation.
- **Files to read first**: `~/.hermes/plugins/jake-brain-ingest/__init__.py` (the brain plugin with all tools), `~/.hermes/SOUL.md`
- **Tests to run**: Message Big Birch on Telegram with "What's on my calendar?" and "Check my email" to verify tools still working
- **Risk**: None — all changes are in ~/.hermes/, isolated from the codebase

## Build Health

- Files modified this session: 4 (all in ~/.hermes/)
- Tests passing: Calendar A+, Email A+, both verified live on Telegram
- Context health at close: YELLOW (screenshot-heavy session)
