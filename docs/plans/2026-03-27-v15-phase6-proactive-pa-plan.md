# V15 Phase 6: Proactive PA — Implementation Plan

**Date**: 2026-03-27
**Author**: Jake
**Status**: DRAFT — awaiting Mike's approval
**Effort**: HIGH
**Estimated Sessions**: 1-2 (most primitives already exist)
**Context Budget**: ~40% (plan + execute in one session)

---

## Current State

### Already Working (Hermes/launchd)
| Cron Job | Schedule | Script | Status |
|----------|----------|--------|--------|
| Brain morning brief | 6:00 AM | `brain_morning_brief.py` → Telegram | ✅ Active |
| Jake morning brief | 7:00 AM | `jake_morning_brief.py` → Telegram | ✅ Active |
| Midday pulse | 12:00 PM | `jake_midday_pulse.sh` → Telegram | ✅ Active |
| EOD report | 6:00 PM | `jake_eod_report.sh` → Telegram | ✅ Active |
| Weekly goals | Sunday 9 AM | `jake_goal_weekly.sh` → Telegram | ✅ Active |

### Already Working (Claude Code Skills)
| Skill | Trigger | Purpose |
|-------|---------|---------|
| `/briefing` | Manual | Morning brief from email + calendar |
| `/triage` | Manual | Email urgency scoring + action recommendations |
| `/prep` | Manual | Meeting prep with context from Susan RAG |

### What's Missing (Phase 6 Scope)
1. **Unified morning pipeline** — combine brain brief + email triage + calendar + competitive signals into ONE comprehensive morning brief
2. **"What's due" skill** — deadline correlation across calendar + email + tasks → proactive Friday-awareness
3. **Calendar awareness automation** — auto-run `/prep` 30 min before meetings
4. **Competitive overnight monitor** — SCOUT + TrendRadar overnight → signals in morning brief
5. **OpenClaw proactive skills** — skills that run on triggers, not just manual invocation
6. **The Mike Test** — end-to-end: wake up → brief ready → meetings prepped → signals flagged

---

## Implementation Tasks

### Task 1: Unified Morning Brief Script
**File**: `bin/jake-morning-pipeline.sh`
**What**: Single orchestrator script that runs the full morning pipeline in order:
1. Email triage (iCloud + Exchange) → score + categorize
2. Calendar scan (Google + Apple) → today's meetings + this week's deadlines
3. SCOUT overnight signals → competitive intelligence summary
4. TrendRadar → market/tech news relevant to 3 companies
5. Brain recall → relevant episodic/semantic context for today
6. Goal progress → weekly goal status check
7. Assemble → unified brief sent to Telegram + email
**Depends on**: Existing scripts (composing, not replacing)
**Exit criteria**: Single Telegram message at 6:00 AM with all sections

### Task 2: "What's Due" OpenClaw Skill
**File**: `~/.openclaw/agents/jake-chat/agent/skills/whats-due.md`
**What**: Skill that answers "what's due this week/Friday/today" by:
1. Querying Google Calendar API for events with deadline keywords
2. Scanning Apple Reminders for due dates
3. Checking email for deadline-related messages (via SuperMemory search)
4. Checking `.claude/plans/` for in-progress plans with dates
5. Correlating and presenting a prioritized deadline list
**Exit criteria**: "Hey Jake, what's due Friday?" → accurate, complete answer

### Task 3: Calendar Awareness Skill
**File**: `~/.openclaw/agents/jake-chat/agent/skills/meeting-prep-auto.md`
**What**: Skill that auto-fires 30 min before meetings:
1. Read Google Calendar for next meeting
2. Extract attendees, topic, related email threads
3. Pull Susan RAG context for attendees/topic
4. Check Brain for relevant episodic memories
5. Send prep brief to Telegram
**Trigger**: Cron job checks every 15 min during business hours (8 AM - 6 PM)
**File**: `bin/jake-meeting-scanner.sh` (the cron trigger)
**Exit criteria**: 30 min before a meeting → Telegram message with prep context

### Task 4: Competitive Overnight Monitor
**File**: `bin/jake-overnight-intel.sh`
**What**: Script that runs at 5:00 AM:
1. Run TrendRadar search for relevant keywords across 3 companies
2. Run SCOUT signal scan against competitor profiles
3. Score signals by priority (P0 = urgent, P1 = important, P2 = interesting)
4. Save raw signals to `.startup-os/briefs/scout-signals-{today}.md`
5. Feed summary into the morning brief pipeline (Task 1)
**Depends on**: TrendRadar MCP, SCOUT agent config
**Exit criteria**: Every morning brief includes a "Competitive Signals" section

### Task 5: Wire Proactive Triggers (launchd)
**Files**: `~/Library/LaunchAgents/com.jake.proactive-*.plist`
**What**: Create/update launchd jobs for the proactive pipeline:
| Job | Schedule | Script |
|-----|----------|--------|
| `com.jake.proactive-overnight-intel` | 5:00 AM daily | `bin/jake-overnight-intel.sh` |
| `com.jake.proactive-morning-pipeline` | 6:00 AM daily | `bin/jake-morning-pipeline.sh` |
| `com.jake.proactive-meeting-scanner` | Every 15 min, 8 AM - 6 PM weekdays | `bin/jake-meeting-scanner.sh` |
**Replaces**: `com.jake.morning-brief` and `com.jake.brain-morning-brief` (merged into unified pipeline)
**Exit criteria**: `launchctl list | grep proactive` shows 3 active jobs

### Task 6: OpenClaw Skill Wiring
**Files**: `~/.openclaw/agents/jake-chat/agent/skills/` (multiple)
**What**: Register the new capabilities as OpenClaw skills so Jake can invoke them in conversation:
- `morning-brief.md` — trigger the full morning pipeline on demand
- `whats-due.md` — deadline awareness
- `meeting-prep-auto.md` — meeting prep (auto + manual)
- `overnight-intel.md` — competitive intelligence summary
- `daily-goals.md` — goal setting and progress check
**Exit criteria**: Jake can run any of these via conversation ("Jake, what's due Friday?")

### Task 7: The Mike Test
**What**: End-to-end validation:
1. ☐ Wake up → Telegram has morning brief with email + calendar + signals
2. ☐ Ask "what's due Friday?" → accurate deadline list
3. ☐ 30 min before meeting → auto prep appears in Telegram
4. ☐ Ask "how are my goals?" → weekly progress summary
5. ☐ SCOUT flagged a competitor move → it's in the morning brief
**Exit criteria**: All 5 test scenarios pass

---

## Execution Order

```
Task 4 (overnight intel)     ──→ Task 1 (unified morning pipeline) ──→ Task 5 (wire triggers)
Task 2 (what's due skill)    ──→ Task 6 (OpenClaw skill wiring)    ──→ Task 7 (Mike Test)
Task 3 (calendar awareness)  ──→ Task 5 (wire triggers)            ──→ Task 7 (Mike Test)
```

Tasks 2, 3, 4 are independent — can run in parallel.
Task 1 depends on Task 4 (overnight intel feeds into morning brief).
Task 5 depends on Tasks 1, 3 (need the scripts before wiring triggers).
Task 6 depends on Tasks 1, 2, 3 (need the skills before registering them).
Task 7 depends on everything.

---

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Google Calendar API token expired | Check token freshness before building; refresh if needed |
| Mail.app osascript timeout (known issue) | Use killall + relaunch pattern in scripts |
| TrendRadar MCP unavailable | Graceful degradation — morning brief still works without competitive section |
| Context budget exceeded | Tasks 2, 3, 4 are small; Task 1 is the biggest risk — cap at 200 lines |

---

## Files Created/Modified

| File | Action | Type |
|------|--------|------|
| `bin/jake-morning-pipeline.sh` | CREATE | Shell script |
| `bin/jake-overnight-intel.sh` | CREATE | Shell script |
| `bin/jake-meeting-scanner.sh` | CREATE | Shell script |
| `~/.openclaw/agents/jake-chat/agent/skills/whats-due.md` | CREATE | OpenClaw skill |
| `~/.openclaw/agents/jake-chat/agent/skills/meeting-prep-auto.md` | CREATE | OpenClaw skill |
| `~/.openclaw/agents/jake-chat/agent/skills/morning-brief.md` | CREATE | OpenClaw skill |
| `~/.openclaw/agents/jake-chat/agent/skills/overnight-intel.md` | CREATE | OpenClaw skill |
| `~/.openclaw/agents/jake-chat/agent/skills/daily-goals.md` | CREATE | OpenClaw skill |
| `~/Library/LaunchAgents/com.jake.proactive-*.plist` | CREATE | launchd jobs (3) |
| `~/Library/LaunchAgents/com.jake.morning-brief.plist` | DISABLE | Replaced by unified pipeline |
| `~/Library/LaunchAgents/com.jake.brain-morning-brief.plist` | DISABLE | Replaced by unified pipeline |
