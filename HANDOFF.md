# Session Handoff

**Date**: 2026-03-22
**Project**: Startup Intelligence OS — Jake V12
**Session Goal**: Build autonomous work system + recipes + email-to-task + meeting prep
**Status**: PARTIAL — meeting prep full vision documented below, needs next session

---

## ⚡ NEXT SESSION PRIORITY: Full Autonomous Meeting Prep

Mike wants meeting prep to be **autonomous execution**, not just a notification.

### The Full Vision (NOT YET BUILT)

When Jake detects an upcoming meeting, Jake should:

1. **Deep live research** via Susan MCP tools:
   - `search_knowledge` — Susan RAG (94K chunks)
   - `web_search_exa` — live Exa web search on attendees + topics
   - `scrape_url` — attendee LinkedIn/company pages
   - `scrape_search` — deep scrape search results
   - NO Claude training data — live research only

2. **Recipe-driven execution**:
   - Check `~/.hermes/recipes/` for meeting-type recipe (e.g., `oracle-deal-review.yaml`)
   - If YES → execute recipe automatically
   - If NO → Jake CREATES recipe based on meeting context, then executes it

3. **Susan agent team orchestration** (via `claude -p` subprocess):
   - Spin up Claude Code session at Startup-Intelligence-OS
   - Use `run_agent` MCP tool → Steve, Freya, Coach etc.
   - Produce REAL deliverables — battlecard updates, dossiers, talking points, risk assessments

4. **Output delivery**:
   - Save `.md` deliverables to `docs/meeting-prep/YYYY-MM-DD-[slug]/`
   - Store summaries in jake_episodic
   - Send Telegram brief with links + key takeaways

### New Files for Next Session

```
scripts/jake_meeting_prep_autonomous.py    # Full autonomous meeting prep
jake_brain/meeting_orchestrator.py         # Research + agents + deliverables
~/.hermes/recipes/oracle-deal-review.yaml  # Deal review recipe
~/.hermes/recipes/partner-sync.yaml        # Partner sync recipe
~/.hermes/recipes/matt-1on1.yaml           # Matt Cohlmia 1:1 recipe
~/.hermes/recipes/weekly-standup.yaml      # Weekly standup recipe
```

### Integration

Wire into `jake_brain/nervous/meeting_prep.py` — replace prep brief output with autonomous worker task creation. The `jake_meeting_prep_rich.py` (already built) becomes the fallback when full autonomous prep doesn't complete in time.

---

## Completed This Session

- [x] `supabase/migrations/20260322_jake_tasks.sql` — jake_tasks + jake_task_runs
- [x] `jake_brain/goals/tasks.py` — TaskStore with claim/complete/fail/retry
- [x] `jake_brain/autonomous_worker.py` — 24/7 execution engine
- [x] `scripts/jake_autonomous_worker.py` — full CLI (daemon/goal/status/tasks)
- [x] `scripts/jake_autonomous_worker.sh` + `launchd/com.jake.autonomous-worker.plist`
- [x] `~/.hermes/skills/goal-setting/SKILL.md` — Telegram goal interface
- [x] `jake_brain/recipes.py` — YAML recipe engine (7 tool types)
- [x] `scripts/jake_recipe_runner.py` — Recipe CLI
- [x] `~/.hermes/recipes/` — 5 production recipes
- [x] `~/.hermes/skills/jake-recipes/SKILL.md` — Hermes recipe interface
- [x] `scripts/jake_email_task_extractor.py` — Oracle email → jake_tasks pipeline
- [x] `scripts/jake_meeting_prep_rich.py` — Meeting prep with brain context (foundation)
- [x] SOUL.md updated
- [x] Committed: `feat(jake): V12 Phase 3 — autonomous work system, recipes, email-to-task, meeting prep`

## Deployment Steps Mike Needs to Do

### 1. Apply Supabase migration
Run `supabase/migrations/20260322_jake_tasks.sql` in Supabase SQL editor.

### 2. Install the autonomous worker daemon
```bash
cp launchd/com.jake.autonomous-worker.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.jake.autonomous-worker.plist
launchctl start com.jake.autonomous-worker
tail -f ~/.hermes/logs/autonomous_worker.log
```

### 3. Install PyYAML (for recipes)
```bash
cd ~/Startup-Intelligence-OS/susan-team-architect/backend
source .venv/bin/activate && pip install pyyaml
```

### 4. Test
```bash
python scripts/jake_autonomous_worker.py status
python scripts/jake_autonomous_worker.py goal "test goal" --priority P3
python scripts/jake_recipe_runner.py list
python scripts/jake_recipe_runner.py run oracle-battlecard-update --dry-run
```

## Context for Next Session

- **Read first**: `scripts/jake_meeting_prep_rich.py`, `jake_brain/nervous/meeting_prep.py`
- **First build**: `scripts/jake_meeting_prep_autonomous.py` with Susan MCP deep research
- **Risk**: Recipe auto-creation is novel — test Claude Code subprocess carefully

## Build Health

- Files this session: 11 new, 1 modified
- Context health at close: YELLOW (~48%)

---

## Previous Handoff (Iron Jarvis Alexa skill)
**Status**: PARTIAL — bug identified and fixed in editor, Lambda deployment not triggered

## Completed
- [x] Identified the bug: Line 770 of `lambda_function.py` had 4 `sb.add_request_handler()` calls on ONE line separated by literal `\n` text (not real newlines) — Python syntax error
- [x] CloudWatch logs confirmed: `Runtime.UserCodeSyntaxError: Syntax error in module 'lambda_function': unexpected character after line continuation`
- [x] Fixed the code in Alexa Developer Console editor — split line 770 into 4 proper separate lines
- [x] Saved fix to editor (persists across page reloads — confirmed committed to CodeCommit)
- [x] Also added `# deploy-fix-v2` marker to line 1 to track which version is deployed
- [x] Rebuilt interaction model via "Build skill" button — succeeded (version 4, 3/22/2026 @ 12:42 AM)

## Blocked
- [ ] **Lambda deployment not triggering** — the Code tab "Save" commits to CodeCommit but the CodePipeline that deploys to Lambda has NOT fired. "Last Deployed" still shows Mar 21, 11:55 PM. Lambda is still running the broken version 4 code.

## Root Cause Analysis
1. **Original bug**: When the skill was built on 3/21, line 770 was written with literal `\n` instead of real newlines. Python interprets `\n` after a function call as a line continuation character `\` followed by `n` — syntax error on import.
2. **Deployment issue**: The Alexa-hosted skill uses CodeCommit → CodePipeline → Lambda. "Save" on Code tab commits to CodeCommit. "Build skill" on Build tab only rebuilds the interaction model. The Lambda deploy pipeline appears to be stuck or requires a different trigger.

## Fix Already Applied (in editor, not yet deployed)
```python
# BEFORE (broken — all on one line with literal \n):
sb.add_request_handler(RememberIntentHandler())\nsb.add_request_handler(RecallIntentHandler())\nsb.add_request_handler(EasterEggIntentHandler())\nsb.add_request_handler(HelpIntentHandler())

# AFTER (fixed — 4 separate lines):
sb.add_request_handler(RememberIntentHandler())
sb.add_request_handler(RecallIntentHandler())
sb.add_request_handler(EasterEggIntentHandler())
sb.add_request_handler(HelpIntentHandler())
```

## Next Session: Deploy the Fix
Three options, in order of preference:

### Option 1: Download + Re-import (simplest)
1. Go to Code tab → click "Download Skill" button
2. Unzip locally, verify `lambda_function.py` has the fix (lines 770-773 should be 4 separate `sb.add_request_handler` calls)
3. If fix is NOT in the downloaded zip, apply it locally
4. Click "Import Code" → upload the fixed zip
5. This should force a fresh deploy
6. Test in simulator: "open iron jarvis"

### Option 2: ASK CLI (most control)
1. `npm install -g ask-cli`
2. `ask configure` (link to Amazon developer account)
3. `ask smapi get-skill-package --skill-id amzn1.ask.skill.7366f2b5-f2d4-430a-bfcf-6fe17642ce00`
4. Fix the code locally
5. `ask deploy` — deploys both model and Lambda
6. Test

### Option 3: Delete + Recreate (nuclear)
1. Delete the Jarvis skill from console
2. Create new Alexa-hosted Python skill
3. Paste the fixed 779-line `lambda_function.py`
4. Copy interaction model JSON from old skill (it's already built, might be recoverable)
5. Build + deploy fresh

## Key References
- **Skill ID**: `amzn1.ask.skill.7366f2b5-f2d4-430a-bfcf-6fe17642ce00`
- **Alexa Console**: `developer.amazon.com/alexa/console/ask`
- **CloudWatch Logs**: `/aws/lambda/7366f2b5-f2d4-430a-bfcf-6fe17642ce00` in us-east-1
- **Lambda ARN**: `arn:aws:lambda:us-east-1:227593615582:...`
- **Local research DB**: `artifacts/alexa-jarvis/jarvis_responses.py` (232 MCU responses, not yet merged)
- **Lambda code is ONLY in the Alexa Developer Console** (cloud-hosted, not in local repo)

## Decisions Made
| Decision | Rationale | Reversible? |
|----------|-----------|-------------|
| Fix via editor JS API | Fastest way to edit in the console | Yes |
| "Build skill" to trigger deploy | Thought it would trigger full pipeline — only rebuilt model | N/A |
| Recommend Download+Import approach | Most reliable way to force a fresh Lambda deployment | Yes |

## Context for Next Session
- **Key insight**: The fix IS in the editor. The problem is purely a deployment issue. Don't re-diagnose the bug.
- **First action**: Try Option 1 (Download → verify fix → Import) to force deploy
- **Test command**: "open iron jarvis" in simulator or on Echo device
- **Risk**: If Download doesn't include the fix, the CodeCommit commit may have been lost — apply fix manually to downloaded code before re-importing

## Build Health
- Files modified this session: 0 local files (all work was in Alexa Developer Console)
- Tests passing: N/A (can't test until Lambda deploys)
- Context health at close: **ORANGE** — heavy context burn on deployment debugging

---

# Session Handoff — M&CI SOP Documentation (Session #4)

**Date**: 2026-03-22 (Saturday late night)
**Session Goal**: Commit prior SOP work, write SOP-13 Market Sizing, start SOP-08 research
**Status**: COMPLETE — SOP-13 shipped, SOP-08 research partially complete

## SOPs Shipped This Session: 4
- SOP-02: Signal Triage — commit `90caca6`
- SOP-09: Win/Loss Analysis — commit `90caca6`
- SOP-11: Trade Show Intelligence — commit `90caca6`
- **SOP-13: Market Sizing (R-01)** — commit `06955e8`

## SOP-13 Research Corpus (1.93 MB, 150+ sources)
All in `docs/research/sop-13-market-sizing/`:
- `01-enterprise-best-practices.md` — McKinsey/BCG/Bain, Strategex $33B case
- `02-healthcare-specific-methods.md` — KLAS, Gartner, CMS NHEA, VBC waste
- `03-academic-papers.md` — HBS, Stanford Biodesign, Bass R²=0.91, Wharton conjoint
- `04-training-data-payer-rcm-provider.md` — 34.1M MA, KLAS share, HFMA benchmarks
- `05-training-data-lifesci-erp-interop-data.md` — 7 domains, TEFCA, eClinical, GenAI
- `06-government-data-sources.md` — 40+ verified URLs, hard anchor table

## SOP-08 Battlecard Research (Next Up)
- Agent 2 DONE: `docs/research/sop-08-battlecards/02-templates-metrics-meddpicc.md` (committed)
- Agent 1 MAY BE in `/tmp`: check `/private/tmp/claude-501/.../tasks/a1631c1d7d1ea8d52.output`
- If not found, re-dispatch research agent for battlecard best practices + AI platforms + healthcare CI

## Next Session Priority Order
1. Finish SOP-08 research → synthesize → draft (Battlecard Creation & Maintenance)
2. SOP-14: Executive Offsite Strategy Prep
3. SOP-18: 8-Person Expert Panel Review

## Key Decisions
- Monte Carlo for SOP-09 = Phase 2 unlock (after ~50 interviews)
- Build Doctrine hookify rule created (warn mode): `.claude/hookify.build-doctrine-enforcement.local.md`
- 3 new methods added to R-01: Installed Base Analysis, Bass Diffusion, VBC Waste Sizing

## Build Health
- Commits: 2 (`90caca6`, `06955e8`)
- Total research corpus: 5.29 MB across 14 files
- Context at close: **ORANGE**
