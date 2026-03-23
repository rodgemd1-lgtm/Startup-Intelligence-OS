# Jake 75/100 Autonomous Build Dispatch

**Created**: 2026-03-22
**Author**: Jake + Mike
**Purpose**: Self-sustaining dispatch prompt for autonomous agent sessions. Gets Jake from 50/100 to 75/100 on the Mani Kanasani scorecard.
**Status**: READY TO DISPATCH

---

## DISPATCH PROMPT — COPY EVERYTHING BELOW THIS LINE

---

You are executing a multi-session autonomous build to upgrade the Jake intelligence system from 50/100 to 75/100 on the Mani Kanasani Agents-in-a-Box scorecard. You will work continuously, managing your own context health, writing handoffs, and resuming from handoffs until all 6 phases are complete.

## CRITICAL RULES

### Context Health Protocol
- You MUST track your own context health as a percentage estimate.
- **At 60% context usage: STOP IMMEDIATELY.** Do not finish "just one more thing."
- Write a structured HANDOFF.md (format below), commit all working code, and end the session.
- The next session will read HANDOFF.md and resume exactly where you left off.
- Every phase has a natural checkpoint. Prefer stopping at phase boundaries.

### Hardcoded Decisions (NON-NEGOTIABLE)
- **Apple Mail via osascript** — all email integration uses `osascript` to talk to Mail.app. NO Microsoft Graph API. NO Gmail API. The Exchange account in Mail.app is named "Exchange".
- **Apple Calendar via osascript** — all calendar integration uses `osascript` to talk to Calendar.app. NO Google Calendar API for primary use. Google Calendar is ONLY used for kids' events via existing OAuth setup.
- **Supabase instance**: `zqsdadnnpgqhehqxplio.supabase.co` (Susan Intelligence OS). All new tables go here.
- **Embeddings**: Voyage AI `voyage-3`, 1024 dimensions. NOT OpenAI.
- **Python environment**: `susan-team-architect/backend/.venv/bin/python`
- **No new frameworks**. Use what exists: Python backend, existing React shell for dashboard, Supabase for data.

### Build Doctrine
- Research → Design → Plan → Build → Test → Verify. SERIES, not parallel.
- Never start building without understanding what exists first.
- Run tests after each logical unit.
- Commit after each completed phase with conventional commit format.
- If a file needs to be read more than twice, your approach is wrong — rethink.

### What NOT To Do
- Do not refactor existing working code unless required by your task.
- Do not add features not listed in the phases below.
- Do not create new MCP servers or install new MCP tools.
- Do not modify `susan-team-architect/backend/control_plane/`, `mcp_server/`, or `susan_core/`.
- Do not create documentation files unless they're HANDOFF.md.
- Do not ask the user questions. Make the best decision and document it.

---

## SESSION START PROTOCOL

Every session (including the first), do this BEFORE any work:

```
1. Read /Users/mikerodgers/Startup-Intelligence-OS/HANDOFF.md
   - If it references this dispatch (jake-75), resume from the noted phase/step.
   - If it references different work, this is the first session — start at Phase 1.

2. Read this file: .claude/plans/2026-03-22-jake-75-dispatch.md
   - Find your current phase. Check the [ ] boxes to see what's done.

3. Run: git status && git log --oneline -5
   - Verify clean working tree or understand what's uncommitted.

4. Announce: "Resuming jake-75 build at Phase [N], Step [M]. Context health: [X]%."
```

---

## THE 6 PHASES (50 → 75 points)

### PHASE 1: Wire Existing Modules (+6 points → 56/100)
**Goal**: self_improvement, collective, and research_daemon are BUILT but not auto-invoked. Wire them.

**Pre-read** (read these files FIRST, then work):
- `susan-team-architect/backend/self_improvement/__init__.py` or `__main__.py`
- `susan-team-architect/backend/collective/__init__.py` or `__main__.py`
- `susan-team-architect/backend/research_daemon/__init__.py` or `__main__.py`
- `susan-team-architect/backend/jake_brain/config.py`

**Steps**:
- [ ] **1a**: Create `scripts/jake_self_improve_weekly.py` — wrapper that runs TIMG extract + consolidate + routing feedback. Reads from jake_brain Supabase tables, writes improvement suggestions back. Must be runnable as: `.venv/bin/python scripts/jake_self_improve_weekly.py`
- [ ] **1b**: Create `scripts/jake_research_daemon_nightly.py` — wrapper that runs gap detection + changelog monitoring. Checks Susan RAG freshness, flags domains with >20% stale records. Must be runnable standalone.
- [ ] **1c**: Create `scripts/jake_collective_monthly.py` — wrapper that runs evolution proposals + cross-domain pattern transfer. Reads patterns from all companies, proposes new agent capabilities.
- [ ] **1d**: Add cron entries to Hermes. Create/update the cron job definitions:
  - Self-improvement: Weekly, Sunday 3 AM
  - Research daemon: Nightly, 2 AM
  - Collective: Monthly, 1st of month, 4 AM
  - Add to `~/.hermes/jobs.json` if that's where crons live, or document the right location.
- [ ] **1e**: Wire outputs to daily brief. Modify the ARIA daily brief skill/script so it includes a "System Health" section showing: last self-improvement run, last research daemon run, any evolution proposals pending.
- [ ] **1f**: Test all three scripts run without errors (they can produce empty results — that's fine, just no crashes).
- [ ] **1g**: Commit: `feat(v10): wire self-improvement, research daemon, and collective to scheduled execution`

**Acceptance**: All 3 scripts run clean. Cron entries exist. Daily brief template includes system health section.

---

### PHASE 2: Cognitive Memory Polish (+3 points → 59/100)
**Goal**: Add auto-promotion, contradiction detection, and memory decay to jake_brain.

**Pre-read**:
- `susan-team-architect/backend/jake_brain/store.py`
- `susan-team-architect/backend/jake_brain/consolidator.py`
- `susan-team-architect/backend/jake_brain/retriever.py`

**Steps**:
- [ ] **2a**: Add **auto-promotion logic** to `consolidator.py`: When 3+ episodic memories reference the same entity/concept within 14 days, auto-promote to a semantic memory. Log the promotion. Don't delete the episodic sources.
- [ ] **2b**: Add **contradiction detection** to `store.py` or a new `contradiction.py`: Before inserting a new semantic memory, check existing semantics for contradictions (cosine similarity > 0.85 but opposite sentiment/facts). Flag contradictions with a `contradicted_by` field rather than silently overwriting.
- [ ] **2c**: Add **memory decay** to `retriever.py`: Apply a recency boost formula: `score = similarity * (0.7 + 0.3 * recency_factor)` where `recency_factor = max(0, 1 - days_since_access / 90)`. Memories not accessed in 90+ days get 0.7x weight, not deleted.
- [ ] **2d**: Add **access tracking**: When a memory is retrieved, update its `last_accessed_at` timestamp in Supabase. This feeds the decay formula.
- [ ] **2e**: Write tests in `tests/test_brain_polish.py`: test promotion triggers at 3 episodes, test contradiction flagging, test decay scoring, test access tracking.
- [ ] **2f**: Run tests, fix any failures.
- [ ] **2g**: Commit: `feat(brain): add auto-promotion, contradiction detection, and memory decay`

**Acceptance**: Tests pass. Promotion fires at 3+ episodes. Contradictions are flagged not overwritten. Decay formula applied to retrieval scoring.

---

### PHASE 3: Dashboard / Ops Center (+7 points → 66/100)
**Goal**: Real-time operational dashboard connected to Supabase.

**Pre-read**:
- `apps/operator-console/index.html`
- `apps/operator-console/main.js`
- Check what Supabase tables exist: jake_episodic, jake_semantic, jake_procedural, jake_working, jake_entities, jake_relationships, jake_goals, jake_tasks

**Architecture Decision**: Build as a single-page vanilla JS app (no React build step needed). Use Supabase JS client directly from CDN. This keeps it simple and deployable with `python3 -m http.server`.

**Steps**:
- [ ] **3a**: Design the dashboard layout — 5 panels:
  1. **Task Board**: jake_tasks table → Kanban columns (pending, in_progress, blocked, done)
  2. **Brain Stats**: Count of episodic/semantic/procedural memories, entities, relationships. Last consolidation time.
  3. **Agent Activity Log**: Recent jake_episodic entries (last 24h) as a timeline.
  4. **Cron Health**: Status of scheduled jobs — last run time, success/fail, next scheduled.
  5. **Goals Tracker**: jake_goals table → progress bars per active goal.

- [ ] **3b**: Create `apps/operator-console/supabase-client.js` — Initialize Supabase JS client. Use anon key (read-only queries only). Fetch functions for each panel's data.
- [ ] **3c**: Build the Task Board panel — query jake_tasks, render as Kanban columns. Include: task title, assignee, priority, created date. Allow status updates via Supabase update (if anon key allows, otherwise read-only).
- [ ] **3d**: Build the Brain Stats panel — aggregate counts from jake_episodic, jake_semantic, jake_procedural, jake_entities, jake_relationships. Show last consolidation timestamp.
- [ ] **3e**: Build the Agent Activity Log — query jake_episodic ORDER BY created_at DESC LIMIT 50. Render as timeline with timestamps, content preview, source.
- [ ] **3f**: Build the Cron Health panel — read from a status file or Supabase table that cron scripts write to (create `jake_cron_status` table if needed: job_name, last_run, status, next_run, error_message).
- [ ] **3g**: Build the Goals Tracker — query jake_goals, render progress bars with title, target, current, percentage.
- [ ] **3h**: Add auto-refresh (every 30 seconds) and a manual refresh button.
- [ ] **3i**: Style it clean — dark theme, monospace font, no bloat. Should look like a terminal ops center, not a marketing page.
- [ ] **3j**: Test by running `cd apps/operator-console && python3 -m http.server 4173` and verifying all 5 panels load with real data.
- [ ] **3k**: Commit: `feat(console): operational dashboard with task board, brain stats, activity log, cron health, goals`

**Acceptance**: Dashboard loads at localhost:4173, shows real data from Supabase across all 5 panels, auto-refreshes.

---

### PHASE 4: Autonomous Pipeline Engine (+7 points → 73/100)
**Goal**: 8-phase execution pipeline with self-healing.

**Pre-read**:
- `susan-team-architect/backend/jake_brain/pipeline.py`
- `susan-team-architect/backend/jake_brain/store.py` (for memory patterns)
- `susan-team-architect/backend/jake_brain/config.py`

**Steps**:
- [ ] **4a**: Create `susan-team-architect/backend/jake_brain/autonomous_pipeline.py` — the 8-phase engine:
  ```
  Phase 1: CONTEXT   — Load relevant memories, recent episodic, active goals
  Phase 2: PLAN      — Generate execution plan from context (what to do, which skills/agents)
  Phase 3: BUILD     — Execute the plan steps sequentially
  Phase 4: VALIDATE  — Check outputs against success criteria
  Phase 5: HEAL      — If validation fails, retry with different approach (max 2 retries)
  Phase 6: REPORT    — Generate execution report (what was done, what succeeded, what failed)
  Phase 7: CLOSE     — Update task status, mark goals progress, write episodic memory
  Phase 8: LEARN     — Feed results to self_improvement TIMG pipeline for pattern extraction
  ```
  Each phase is a method. The pipeline runner calls them in sequence. Phase transitions are logged.

- [ ] **4b**: Add **self-healing logic** to Phase 5:
  - On failure: log the error, classify it (API error, data error, logic error)
  - Retry strategy: API error → retry with backoff. Data error → try alternate data source. Logic error → escalate to FLAG tier (don't retry, mark for human review).
  - Max 2 retries per step. After 2 failures, mark task as BLOCKED with error details.

- [ ] **4c**: Add **pipeline status tracking** — create Supabase table `jake_pipeline_runs`:
  - id, pipeline_name, started_at, current_phase, status (running/completed/failed/blocked), phases_completed (jsonb), error_log, completed_at

- [ ] **4d**: Create `scripts/jake_pipeline_runner.py` — CLI wrapper:
  - `python scripts/jake_pipeline_runner.py --task "Research competitor X" --type research`
  - `python scripts/jake_pipeline_runner.py --task "Draft Oracle brief" --type content`
  - `python scripts/jake_pipeline_runner.py --task "Update stale RAG records" --type maintenance`
  - Task types determine which skills/agents get loaded in Phase 2.

- [ ] **4e**: Wire pipeline to dashboard — add a 6th panel to the operator console: "Pipeline Runs" showing active/recent pipeline executions with phase progress indicator.

- [ ] **4f**: Write tests in `tests/test_autonomous_pipeline.py`: test happy path (all 8 phases), test self-healing on simulated failure, test max retry limit, test BLOCKED escalation.

- [ ] **4g**: Run tests, fix failures.

- [ ] **4h**: Commit: `feat(pipeline): 8-phase autonomous execution engine with self-healing and pipeline tracking`

**Acceptance**: Pipeline runner executes all 8 phases. Self-healing retries on failure. Pipeline runs tracked in Supabase. Dashboard shows pipeline status.

---

### PHASE 5: AI Employee Loops — First Two (+2 points → 75/100)
**Goal**: Build 2 of 4 autonomous employee loops using the pipeline engine.

**Pre-read**:
- The autonomous_pipeline.py you just built in Phase 4
- `susan-team-architect/backend/jake_brain/meeting_orchestrator.py`
- Existing Hermes skills: `~/.hermes/skills/oracle-health-intel/`, `~/.hermes/skills/oracle-jake/`

**Employee 1: Oracle Sentinel**
- [ ] **5a**: Create `susan-team-architect/backend/jake_brain/employees/oracle_sentinel.py`:
  - **Trigger**: Cron (daily 6 AM weekdays) OR manual dispatch
  - **Pipeline**:
    1. CONTEXT: Load Oracle Health RAG context, recent TrendRadar signals, last briefing
    2. PLAN: Identify stale competitor profiles, new signals to analyze, briefing due
    3. BUILD: Run Susan search_knowledge for each competitor, check TrendRadar via MCP
    4. VALIDATE: Verify findings have sources, check for contradictions with existing intel
    5. HEAL: If TrendRadar fails, fall back to existing RAG data
    6. REPORT: Generate Oracle Health intelligence summary
    7. CLOSE: Update jake_episodic with new intel, mark task complete
    8. LEARN: Feed to TIMG for pattern extraction
  - **Output**: Intelligence summary written to `jake_episodic` with data_type="oracle_intel"
  - **Escalation**: FLAG if competitor makes major announcement (detected via keyword triggers)

**Employee 2: Inbox Zero (Apple Mail)**
- [ ] **5b**: Create `susan-team-architect/backend/jake_brain/employees/inbox_zero.py`:
  - **Trigger**: Cron (3x daily: 8 AM, 12 PM, 5 PM weekdays)
  - **Pipeline**:
    1. CONTEXT: Load recent email subjects via osascript (`tell application "Mail"` → get subjects of messages of inbox). Load Mike's priorities from jake_goals.
    2. PLAN: Categorize emails: URGENT (needs response today), IMPORTANT (needs response this week), FYI (read later), NOISE (archive/delete)
    3. BUILD: For URGENT emails, draft response bullets. For IMPORTANT, add to jake_tasks. For NOISE, flag for archive.
    4. VALIDATE: Check categorization against sender importance (known contacts from jake_entities get priority boost)
    5. HEAL: If osascript times out (known issue), kill and relaunch Mail.app, retry once
    6. REPORT: Generate email triage summary with action items
    7. CLOSE: Write triage results to jake_episodic, create jake_tasks for follow-ups
    8. LEARN: Track which categorizations Mike overrides to improve future accuracy
  - **Apple Mail osascript pattern** (HARDCODED — use this exact approach):
    ```python
    import subprocess
    def get_inbox_subjects(limit=20):
        script = f'''
        tell application "Mail"
            set msgs to messages 1 through {limit} of inbox
            set output to ""
            repeat with m in msgs
                set output to output & subject of m & "|" & sender of m & "|" & date received of m & linefeed
            end repeat
            return output
        end tell
        '''
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            # Known fix: kill and relaunch Mail.app
            subprocess.run(["killall", "Mail"], capture_output=True)
            import time; time.sleep(3)
            subprocess.run(["open", "-a", "Mail"], capture_output=True)
            time.sleep(5)
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=30)
        return result.stdout.strip().split("\n")
    ```
  - **Apple Calendar osascript pattern** (HARDCODED — use for any calendar needs):
    ```python
    def get_today_events():
        script = '''
        tell application "Calendar"
            set today to current date
            set tomorrow to today + 1 * days
            set output to ""
            repeat with cal in calendars
                set evts to (every event of cal whose start date >= today and start date < tomorrow)
                repeat with e in evts
                    set output to output & summary of e & "|" & start date of e & "|" & end date of e & linefeed
                end repeat
            end repeat
            return output
        end tell
        '''
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=30)
        return result.stdout.strip().split("\n")
    ```

- [ ] **5c**: Create `susan-team-architect/backend/jake_brain/employees/__init__.py` — registry of all employees with their cron schedules and trigger conditions.

- [ ] **5d**: Create `scripts/jake_employee_runner.py` — CLI to run any employee:
  - `python scripts/jake_employee_runner.py --employee oracle_sentinel`
  - `python scripts/jake_employee_runner.py --employee inbox_zero`
  - Wraps the autonomous pipeline with employee-specific config.

- [ ] **5e**: Add cron entries for both employees to Hermes jobs.json.

- [ ] **5f**: Add "AI Employees" panel to operator console dashboard — show employee name, last run, status, next run, actions taken count.

- [ ] **5g**: Test both employees run without crashes (they can produce empty/minimal results on first run).

- [ ] **5h**: Commit: `feat(employees): Oracle Sentinel and Inbox Zero autonomous employee loops`

**Acceptance**: Both employees run via CLI. Pipeline phases execute in order. Results written to Supabase. Dashboard shows employee status.

---

### PHASE 6: Integration Test + Score Verification
**Goal**: Verify the system scores 75/100.

- [ ] **6a**: Run all test files in `tests/` — document pass/fail.
- [ ] **6b**: Run each script manually:
  - `scripts/jake_self_improve_weekly.py`
  - `scripts/jake_research_daemon_nightly.py`
  - `scripts/jake_collective_monthly.py`
  - `scripts/jake_pipeline_runner.py --task "test" --type maintenance`
  - `scripts/jake_employee_runner.py --employee oracle_sentinel`
  - `scripts/jake_employee_runner.py --employee inbox_zero`
- [ ] **6c**: Load dashboard at localhost:4173, verify all 7 panels show data.
- [ ] **6d**: Write final scorecard to `docs/plans/2026-03-22-jake-75-scorecard.md`:

  | Layer | Score | Evidence |
  |-------|-------|----------|
  | Identity | 9/10 | SOUL.md, shared brain identity |
  | Cognitive Memory | 10/10 | 4-layer + promotion + contradiction + decay |
  | Dashboard/Ops | 9/10 | 7-panel real-time dashboard |
  | Skill Library | 8/10 | 81 Hermes + 12 Claude Code skills |
  | AI Employees | 6/10 | 2 autonomous employees (Oracle Sentinel, Inbox Zero) |
  | Autonomous Pipeline | 9/10 | 8-phase engine with self-healing |
  | Self-Evolution | 8/10 | TIMG wired + weekly auto-invoke |
  | Security | 3/10 | jake-shield (unchanged — not in scope) |
  | Cost Optimization | 5/10 | Smart routing (unchanged — not in scope) |
  | Business Pipeline | 5/10 | Connected via employees (unchanged — not in scope) |
  | **TOTAL** | **72-75/100** | |

- [ ] **6e**: Commit: `docs(scorecard): jake 75/100 verification scorecard`
- [ ] **6f**: Update HANDOFF.md with final status: JAKE-75 BUILD COMPLETE.

---

## HANDOFF FORMAT

When context hits 60%, write this EXACTLY to `/Users/mikerodgers/Startup-Intelligence-OS/HANDOFF.md`:

```markdown
# Session Handoff

**Date**: [YYYY-MM-DD]
**Project**: Startup Intelligence OS
**Session Goal**: Jake 75/100 Build — Phase [N]
**Status**: PARTIAL
**Dispatch**: .claude/plans/2026-03-22-jake-75-dispatch.md

## Completed
- [x] Phase 1 — [if done]
- [x] Phase 2 — [if done]

## Current Phase
- Phase [N], Step [X]
- Current state: [exactly what's done and what's next]
- Files modified so far: [list]
- Tests passing: [yes/no]

## Not Started
- [ ] Phase [N+1]
- [ ] Phase [N+2]

## Context Health
- Context at close: [percentage]%
- Files read this session: [count]
- Files modified this session: [count]
- Reason for handoff: Context health approaching 60%

## Resume Instructions
1. Read this HANDOFF.md
2. Read .claude/plans/2026-03-22-jake-75-dispatch.md
3. Jump to Phase [N], Step [X]
4. Do NOT re-read files already processed (listed above)
5. Continue building
```

## COMMIT AFTER EVERY PHASE
Use conventional commits:
```
feat(v10): wire self-improvement, research daemon, and collective to scheduled execution
feat(brain): add auto-promotion, contradiction detection, and memory decay
feat(console): operational dashboard with task board, brain stats, activity log, cron health, goals
feat(pipeline): 8-phase autonomous execution engine with self-healing
feat(employees): Oracle Sentinel and Inbox Zero autonomous employee loops
docs(scorecard): jake 75/100 verification scorecard
```

## KEY FILE LOCATIONS

| What | Where |
|------|-------|
| Jake Brain | `susan-team-architect/backend/jake_brain/` |
| Self-Improvement | `susan-team-architect/backend/self_improvement/` |
| Collective | `susan-team-architect/backend/collective/` |
| Research Daemon | `susan-team-architect/backend/research_daemon/` |
| Memory TIP | `susan-team-architect/backend/memory/` |
| Operator Console | `apps/operator-console/` |
| Scripts | `susan-team-architect/backend/scripts/` |
| Tests | `susan-team-architect/backend/tests/` |
| Hermes Config | `~/.hermes/config.yaml` |
| Hermes Jobs | `~/.hermes/jobs.json` |
| Hermes Skills | `~/.hermes/skills/` |
| Hermes Plugins | `~/.hermes/plugins/` |
| Supabase Migrations | `supabase/migrations/` |
| Python venv | `susan-team-architect/backend/.venv/bin/python` |

## SUPABASE TABLES (existing)
- jake_episodic, jake_semantic, jake_procedural, jake_working
- jake_entities, jake_relationships
- jake_goals, jake_tasks
- knowledge_chunks (Susan RAG — 94K+ chunks)

## SUPABASE TABLES (to create in this build)
- jake_cron_status (Phase 3)
- jake_pipeline_runs (Phase 4)

## NOW GO BUILD. START AT PHASE 1 (or resume from HANDOFF.md).
