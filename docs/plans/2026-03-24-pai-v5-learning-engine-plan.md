# PAI V5: Learning Engine — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Jake gets smarter every day. Build correction capture, rating system, failure analysis, auto-generated patterns, memory consolidation, weekly synthesis, and self-evaluation — so the system improves without manual intervention.

**Depends On:** V0-V4 complete

**Score Target:** 78 → 84

---

## Pre-Flight Checklist

- [ ] V4 exit criteria all passed (proactive intelligence working)
- [ ] Memory consolidation pipeline operational (V1)
- [ ] MEMORY/LEARNING/ directory has data from V3 pipelines
- [ ] ratings.jsonl is being populated (V1 consolidator)

---

## Phase 5A: Signal Capture

### Task 1: Build RatingCapture Hook

**Files:**
- Create: `pai/hooks/rating-capture.sh`
- Create: `pai/learning/rating_system.py`

**What it does:**
Captures satisfaction signals from Mike — both explicit (1-5 rating) and implicit (corrections, re-asks, tone shifts).

**Explicit signals:**
- Mike says "good", "great", "perfect", "that's fire" → auto-rate 4-5
- Mike says "no", "wrong", "try again", "mid" → auto-rate 1-2
- Ask for explicit rating at session end (Stop hook)

**Implicit signals:**
- Re-asking the same question → previous answer was unsatisfactory (rate 2)
- Mike corrects Jake's output → capture correction pair (before/after)
- Long silence after response → possible dissatisfaction (flag for review)
- Mike says "skip" or changes topic → response wasn't useful (rate 2)

**Implementation steps:**
1. Create RatingSystem class with `capture_explicit()`, `capture_implicit()`, `analyze_session()` methods
2. Wire into PostToolUse hook — detect correction patterns
3. Wire into Stop hook — prompt for optional rating
4. Store all signals in `pai/MEMORY/STATE/ratings.jsonl`
5. Weekly analysis: compute average satisfaction, trend direction
6. Target: 100+ satisfaction signals captured in first month

**Commit:** `feat(pai): rating capture system — explicit + implicit satisfaction signals`

---

### Task 2: Build Correction Handler

**Files:**
- Create: `pai/learning/correction_handler.py`
- Adapt from: `susan-team-architect/backend/jake_brain/correction_handler.py`

**What it does:**
When Mike corrects Jake, captures the correction pair and updates rules.

**Correction capture format:**
```json
{
  "timestamp": "2026-04-15T10:30:00",
  "context": "Mike asked about Oracle Health pricing strategy",
  "jake_said": "I'd recommend a freemium model...",
  "mike_corrected": "No, they're enterprise only. Never suggest freemium for healthcare.",
  "rule_extracted": "Oracle Health is enterprise-only. Never suggest freemium or consumer pricing models.",
  "applied_to": ["TELOS/LEARNED.md", "AI Steering Rules"]
}
```

**Implementation steps:**
1. Port `jake_brain/correction_handler.py` to PAI architecture
2. Detect correction patterns: "No,", "Wrong,", "Actually,", "That's not right"
3. Extract the rule from the correction
4. Store in `pai/MEMORY/LEARNING/corrections/`
5. Propose TELOS/LEARNED.md update (CONFIRM tier — notify Mike)
6. If same correction happens 3+ times, auto-update LEARNED.md (pattern is proven)

**Commit:** `feat(pai): correction handler — capture correction pairs, extract rules, update LEARNED.md`

---

### Task 3: Build Failure Capture System

**Files:**
- Create: `pai/learning/failure_capture.py`

**What it does:**
Full context dumps when things go wrong — pipeline failures, low ratings, error chains.

**Failure categories:**
- Pipeline failure (exception in autonomous pipeline)
- Low rating (<= 2 from Mike)
- Tool failure (MCP tool returns error)
- Timeout (response took too long)
- Hallucination detected (Mike flags inaccurate information)

**Implementation steps:**
1. Create FailureCapture class with `capture()` method
2. On any failure, dump: full context, recent messages, tool calls, memory state
3. Store in `pai/MEMORY/LEARNING/failures/YYYY-MM-DD-{type}-{id}.md`
4. Run Fabric `analyze_risk` on failure to identify root cause
5. Weekly: aggregate failures, detect patterns, propose fixes
6. If same failure type occurs 3+ times: auto-create a rule to prevent it

**Commit:** `feat(pai): failure capture — full context dumps with root cause analysis`

---

## Phase 5B: Pattern Generation

### Task 4: Build Auto-Pattern Generator

**Files:**
- Create: `pai/learning/pattern_generator.py`

**What it does:**
Detects recurring interaction patterns and auto-generates Fabric custom patterns.

**Detection method:**
1. Analyze last 30 days of Work sessions
2. Find repeated task types (e.g., "Mike asks for competitive analysis" happens 5x/month)
3. Extract the common structure from successful completions
4. Generate a custom Fabric pattern with the distilled approach
5. Save to `~/.config/fabric/patterns/custom/` and `pai/patterns/custom/`

**Examples of auto-generated patterns:**
- `jake_competitive_brief` — Mike's preferred competitive analysis format
- `jake_decision_frame` — How Mike likes decisions structured
- `jake_code_review` — Mike's code review checklist
- `jake_meeting_summary` — Meeting summary in Mike's preferred format

**Implementation steps:**
1. Create PatternGenerator class with `detect_patterns()`, `generate_pattern()` methods
2. Run weekly (alongside weekly synthesis)
3. Each generated pattern includes: system prompt, user prompt, output format
4. Patterns are saved but NOT auto-activated — Mike reviews and approves
5. After approval, pattern is installed in Fabric
6. Target: 5+ auto-generated patterns in first 3 months

**Commit:** `feat(pai): auto-pattern generator — detect recurring tasks, generate custom Fabric patterns`

---

### Task 5: Build Memory Consolidation Pipeline

**Files:**
- Create: `pai/learning/consolidation.py`

**What it does:**
Nightly episodic → semantic promotion. Weekly semantic → wisdom promotion.

**Nightly (2 AM):**
1. Scan jake_episodic for clusters: same topic mentioned 3+ times in 14 days
2. Promote clustered facts to jake_semantic with synthesized content
3. Mark source episodic records as "consolidated"
4. Generate consolidation report

**Weekly (Sunday):**
1. Scan jake_semantic for stable facts (unchanged for 30+ days)
2. Cross-reference with LEARNED.md and WRONG.md
3. Promote stable, validated facts to TELOS/WISDOM.md
4. Update knowledge graph entity importance scores

**Implementation steps:**
1. Create ConsolidationPipeline class (extends V1 PAIConsolidator)
2. Add nightly cron job: `0 2 * * *`
3. Add to weekly synthesis pipeline (Sunday 10 AM)
4. Track consolidation stats: records scanned, promoted, skipped
5. Alert if consolidation fails 3 nights in a row
6. Target: runs nightly for 30 days without failure

**Commit:** `feat(pai): memory consolidation pipeline — nightly episodic→semantic, weekly semantic→wisdom`

---

## Phase 5C: Self-Evaluation

### Task 6: Build Weekly Learning Synthesis

**Files:**
- Create: `pai/learning/weekly_synthesis.py`

**What it does:**
Every Sunday, synthesize all learning from the past week into actionable patterns.

**Synthesis pipeline:**
1. Read all LEARNING files from past 7 days
2. Read all corrections from past 7 days
3. Read all failures from past 7 days
4. Read ratings distribution (average, trend)
5. Run Fabric `extract_patterns` on combined input
6. Generate synthesis report with:
   - **Patterns detected** (recurring behaviors, good and bad)
   - **Rules to add** (new entries for LEARNED.md)
   - **Rules to update** (existing rules that need refinement)
   - **WRONG.md updates** (things Jake was wrong about)
   - **TELOS updates** (suggested changes to identity/goals files)
7. Write to `pai/MEMORY/WISDOM/synthesis-YYYY-WNN.md`
8. Deliver summary to Telegram

**Implementation steps:**
1. Create WeeklySynthesis class
2. Add to Sunday 10 AM cron job (existing)
3. Require Mike's approval for TELOS updates (APPROVE tier)
4. Auto-apply LEARNED.md updates (CONFIRM tier)
5. Track synthesis quality: are the patterns actually useful?

**Commit:** `feat(pai): weekly learning synthesis — aggregate patterns, update rules, propose TELOS changes`

---

### Task 7: Build Self-Evaluation Cycle

**Files:**
- Create: `pai/learning/self_evaluation.py`

**What it does:**
Monthly self-evaluation against the PAI maturity scorecard.

**Evaluation domains (from Hermes audit):**
| Domain | V4 Target | Measurement |
|--------|-----------|-------------|
| Memory & Context | 8/10 | Search accuracy, recall quality |
| Autonomous Execution | 7/10 | Pipeline success rate, task completion |
| Multi-System Integration | 7/10 | MCP availability, agent success rate |
| Proactive Intelligence | 8/10 | Jordan Voss test pass rate |
| Personal Context Depth | 8/10 | TELOS completeness, entity accuracy |
| Communication Quality | 8/10 | Rating average, correction frequency |
| Multi-Agent Orchestration | 6/10 | Agent invocation success, routing accuracy |
| Learning & Self-Improvement | 7/10 | Patterns generated, consolidation runs |
| Reliability & Error Recovery | 7/10 | Uptime, self-repair success rate |

**Implementation steps:**
1. Create SelfEvaluation class with `evaluate()` method
2. Pull metrics from: pipeline logs, ratings.jsonl, failure logs, cron status
3. Score each domain 1-10 with evidence
4. Compare to previous month's score
5. Generate action items for lowest-scoring domains
6. Write to `pai/MEMORY/WISDOM/evaluation-YYYY-MM.md`
7. Run on 1st of each month

**Commit:** `feat(pai): self-evaluation cycle — monthly maturity scorecard with evidence-based scoring`

---

## Phase 5D: WRONG.md and Knowledge Graph Evolution

### Task 8: Build WRONG.md Auto-Update System

**Files:**
- Update: `pai/TELOS/WRONG.md`
- Create: `pai/learning/wrong_tracker.py`

**What it does:**
Tracks things Jake was wrong about — corrections that reveal systematic errors.

**Auto-update triggers:**
- Same correction from Mike 3+ times → add to WRONG.md
- Failure analysis reveals a flawed assumption → add to WRONG.md
- Self-evaluation identifies a declining domain → investigate and document

**WRONG.md format:**
```markdown
## [Date] — [What Jake Was Wrong About]
**Context:** What happened
**Wrong assumption:** What Jake believed
**Reality:** What's actually true
**Impact:** What went wrong because of this
**Rule added:** The corrective rule now in LEARNED.md
```

**Commit:** `feat(pai): WRONG.md auto-update — systematic error tracking from corrections and failures`

---

## V5 Exit Criteria (All Must Pass)

- [ ] 100+ satisfaction signals captured (explicit + implicit)
- [ ] Correction handler captures and extracts rules from Mike's corrections
- [ ] Failure capture generates full context dumps for all failure types
- [ ] 5+ auto-generated custom Fabric patterns (awaiting Mike's approval)
- [ ] Nightly consolidation runs for 30 consecutive days without failure
- [ ] Weekly synthesis generates actionable patterns every Sunday
- [ ] Monthly self-evaluation produces evidence-based scorecard
- [ ] WRONG.md has 3+ entries from auto-detection
- [ ] LEARNED.md grows by 10+ rules from corrections and synthesis
- [ ] Overall satisfaction trend is improving (month-over-month)

**Score target: 78 → 84**
