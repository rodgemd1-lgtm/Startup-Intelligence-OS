# Plan: Birthday Cron + Brain Auto-Hook + Phase 3-9 Architecture

**Date**: 2026-03-20
**Status**: in-progress
**Confidence**: 8/10 — all infrastructure exists, this is wiring + new scripts
**Estimated files**: 5 new, 1 modified

---

## Context

**What exists today:**
- Jake's Brain: 4-layer cognitive memory (6 Supabase tables, 7 Python modules)
- 43 contacts with birthdays in `jake_entities` (properties.birthday as "MM-DD" string)
- `brain_knowledge_dump.py` — re-runnable script that syncs Claude Code memory → Brain
- 13 hook scripts in `bin/hooks/`, settings.json with 5 lifecycle events
- Telegram bot token in `~/.hermes/.env` (TELEGRAM_BOT_TOKEN)
- Phases 1 (Foundation) and 2 (Brain) COMPLETE

**Why this change:**
- Birthdays are stored but nobody checks them → need daily cron
- Brain sync is manual (`python scripts/brain_knowledge_dump.py`) → need auto-hook on session end
- Phases 3-9 need a concrete plan document to guide the build

---

## Deliverable 1: Birthday Cron

### Approach
Python script that queries `jake_entities` for birthdays matching today or upcoming (next 7 days), sends Telegram message via bot API. Scheduled as a Claude Code scheduled task running daily at 7:00 AM.

### Steps
- [ ] **1.1** Create `susan-team-architect/backend/scripts/birthday_check.py`
  - Load TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from `~/.hermes/.env`
  - Query `jake_entities` where `entity_type = 'person'` and `is_active = True`
  - Filter entities where `properties->>'birthday'` matches today's MM-DD or next 7 days
  - Format message: "🎂 Today: [name]" and "📅 This week: [name] on [date]"
  - Send via Telegram Bot API (`POST https://api.telegram.org/bot{token}/sendMessage`)
  - Exit silently if no birthdays (no spam)
- [ ] **1.2** Create Claude Code scheduled task for daily 7 AM execution
  - Use `anthropic-skills:schedule` or manual cron
- [ ] **1.3** Test: Run script manually, verify Telegram message arrives

### Files
| File | Action | Description |
|------|--------|-------------|
| `susan-team-architect/backend/scripts/birthday_check.py` | CREATE | Birthday check + Telegram notify |

---

## Deliverable 2: Claude Code Brain Auto-Hook

### Approach
Add a Stop hook that runs `brain_knowledge_dump.py` async at session end. This ensures every Claude Code session's memory changes are automatically synced to the shared Brain (Supabase). Runs async with timeout so it doesn't block session close.

### Steps
- [ ] **2.1** Create `bin/hooks/brain-sync.sh`
  - `cd susan-team-architect/backend`
  - Activate venv
  - Run `python scripts/brain_knowledge_dump.py` with stdout/stderr to log file
  - Async, 30s timeout (the dump is fast — reads files + deduplicates)
- [ ] **2.2** Register in `.claude/settings.json` as async Stop hook
  - Add to Stop array alongside existing stop-gate.sh and cost-tracker.sh
  - `"async": true, "timeout": 30`
- [ ] **2.3** Test: End a session, check that brain stats increase

### Files
| File | Action | Description |
|------|--------|-------------|
| `bin/hooks/brain-sync.sh` | CREATE | Async brain sync on session end |
| `.claude/settings.json` | MODIFY | Add brain-sync to Stop hooks |

---

## Deliverable 3: Phase 3-9 Architecture Plan

### Approach
Write a comprehensive plan document defining each remaining phase with concrete deliverables, scripts to create, and success criteria.

### Steps
- [ ] **3.1** Create `.claude/plans/2026-03-20-9phase-architecture.md`
  - Phase 3: THE EYES — Life data ingestion (Gmail, iMessage, Photos, Calendar beyond Apple)
  - Phase 4: THE SPINE — Central routing + priority engine
  - Phase 5: THE HANDS — Action execution (send email, create calendar event, set reminder)
  - Phase 6: EMPLOYEES — Specialized sub-agents (finance agent, health agent, social agent)
  - Phase 7: IMMUNE SYSTEM — Error recovery, self-healing, privacy guards
  - Phase 8: NERVOUS SYSTEM — Real-time event processing + push notifications
  - Phase 9: NETWORK — Multi-device sync, cross-platform presence

### Files
| File | Action | Description |
|------|--------|-------------|
| `.claude/plans/2026-03-20-9phase-architecture.md` | CREATE | Full 9-phase roadmap |

---

## Execution Order
1. Birthday cron (standalone, no dependencies) — ~15 min
2. Brain auto-hook (standalone, no dependencies) — ~10 min
3. Phase 3-9 plan document — ~15 min

Deliverables 1 and 2 can be built in parallel via sub-agents.

---

## Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| TELEGRAM_CHAT_ID not in .env | Birthday messages go nowhere | Script discovers chat ID via getUpdates API or we hardcode Mike's |
| brain_knowledge_dump.py exceeds 30s timeout | Hook times out, no sync | Already fast (reads ~33 files, deduplicates). Increase timeout if needed. |
| Birthday MM-DD format edge cases | Missing birthdays | Script handles both "MM-DD" and "M-D" formats |

---

## Verification
- [ ] Birthday cron: Run `python scripts/birthday_check.py` — see Telegram message
- [ ] Brain hook: Close session, check `~/.claude/metrics/` or brain stats via CLI
- [ ] Phase plan: Document exists and covers all 7 remaining phases with concrete deliverables
