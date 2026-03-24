# PAI V4: Proactive Intelligence — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Jake anticipates, Mike decides. Build intent classification (KIRA-style routing), smart notifications with urgency scoring and DND awareness, cross-company competitive intelligence, decision support, and the Priority Engine that passes the Jordan Voss test ("What's the ONE thing today?" in <30 seconds).

**Depends On:** V0-V3 complete (infrastructure, memory, agents, autonomous pipelines)

**Score Target:** 70 → 78

---

## Pre-Flight Checklist

- [ ] V3 exit criteria all passed (pipelines running autonomously for 14 days)
- [ ] Morning brief, email triage, goal tracking all operational
- [ ] Safety tier system enforced and working
- [ ] All 82 Susan agents callable from any channel

---

## Phase 4A: Intent Classification (KIRA-style Router)

### Task 1: Build Intent Classifier

**Files:**
- Create: `pai/intelligence/intent_router.py`
- Adapt from: `susan-team-architect/backend/jake_brain/intent_router.py`

**What it does:**
Classifies every incoming message into intent categories, then routes to the right model tier, agent, and response style.

**Intent categories:**
| Intent | Model | Agent | Example |
|--------|-------|-------|---------|
| `quick_answer` | nano | none | "What time is Jacob's game?" |
| `status_check` | cheap | none | "How are the goals looking?" |
| `research` | mid | research-director | "What's the latest on Oracle Health competitors?" |
| `strategy` | expensive | steve-strategy | "Should we pivot the Alex Recruiting pricing?" |
| `build` | expensive | atlas-engineering | "Add dark mode to the dashboard" |
| `decision` | expensive | multiple | "Should I take this meeting?" |
| `casual` | cheap | none | "Hey Jake" |

**Implementation steps:**
1. Port `jake_brain/intent_router.py` to `pai/intelligence/intent_router.py`
2. Add confidence scoring (0-1) for each classification
3. If confidence < 0.6, escalate to Opus for disambiguation
4. Wire into OpenClaw message handler as first processing step
5. Log all classifications to `pai/intelligence/logs/intent-classifications.jsonl`
6. Measure routing accuracy over 7 days, tune thresholds

**Commit:** `feat(pai): KIRA-style intent classifier — 7 intent categories with confidence scoring`

---

### Task 2: Build Smart Notification System

**Files:**
- Create: `pai/intelligence/notifications.py`
- Create: `pai/config/notification-rules.json`

**What it does:**
Urgency scoring with DND awareness. Not every alert deserves a ping.

**Urgency scoring:**
- **P0 (interrupt):** Family emergency, service outage, deadline in <2 hours → Always deliver
- **P1 (soon):** Important email, meeting in 30 min, goal blocked → Deliver unless DND
- **P2 (batch):** Status update, research complete, low-priority email → Batch to next brief
- **P3 (archive):** Newsletter, notification, no action → Don't notify, log only

**DND rules (from notification-rules.json):**
```json
{
  "dnd": {
    "enabled": true,
    "quiet_hours": {"start": "22:00", "end": "06:00"},
    "override_for": ["P0"],
    "weekend_mode": "relaxed",
    "family_time": {"enabled": true, "hours": ["17:00-20:00"]}
  },
  "batching": {
    "P2": {"interval_minutes": 120, "max_items": 10},
    "P3": {"interval_minutes": 1440, "max_items": 50}
  },
  "channels": {
    "P0": ["telegram", "imessage"],
    "P1": ["telegram"],
    "P2": ["morning_brief"],
    "P3": ["log_only"]
  }
}
```

**Implementation steps:**
1. Create NotificationManager class with urgency scoring
2. Implement DND checker (time-aware, calendar-aware)
3. Implement batching for P2/P3 notifications
4. Wire into all pipeline outputs (morning brief, email triage, goal progress)
5. Test: send P0 during quiet hours (should deliver), P2 during quiet hours (should batch)
6. Run for 2 weeks, collect notification quality ratings

**Commit:** `feat(pai): smart notifications — urgency scoring, DND, batching, channel routing`

---

## Phase 4B: Cross-Company Intelligence

### Task 3: Build SCOUT Competitive Intelligence Pipeline

**Files:**
- Create: `pai/intelligence/scout.py`
- Create: `pai/config/scout-sources.json`
- Adapt from: `susan-team-architect/backend/chains/chains/competitive_response.py`

**What it does:**
Monitors competitive landscape across all 3 companies (Startup Intelligence OS, Oracle Health, Alex Recruiting). Surfaces P0/P1 signals, content white space, and market moves.

**Sources:**
- Company blogs/press (RSS feeds)
- Product Hunt, Hacker News (new launches)
- LinkedIn company pages (hiring signals)
- GitHub repos (feature releases)
- Industry news (Google Alerts)
- Susan RAG (existing competitive data)

**Implementation steps:**
1. Create SCOUT agent combining herald-pr + aria-growth agent capabilities
2. Define competitive watchlist per company in `scout-sources.json`
3. Build daily scrape + classify pipeline (runs at 5 AM before morning brief)
4. Classify signals: P0 (competitor launched something that directly threatens us), P1 (market shift), P2 (interesting but not urgent)
5. Feed P0/P1 signals into morning brief
6. Store all signals in Supabase `jake_competitive_signals` table
7. Weekly competitive digest using Fabric `summarize` pattern

**Commit:** `feat(pai): SCOUT competitive intelligence — cross-company signal monitoring with P0/P1 classification`

---

### Task 4: Build Decision Support Engine

**Files:**
- Create: `pai/intelligence/decision_support.py`
- Create: `pai/intelligence/decision_templates/`

**What it does:**
When Mike faces a decision, Jake structures it: options, risks, evidence, recommendation.

**Decision framework:**
1. **Frame** — What's the actual decision? (Often the stated question isn't the real decision)
2. **Options** — Generate 3-5 options (always include "do nothing")
3. **Analyze** — Run Fabric `analyze_risk` + `t_red_team_thinking` on each option
4. **Evidence** — Search memory + RAG for relevant precedent
5. **Recommend** — Rank options, state confidence, flag reversibility

**Implementation steps:**
1. Create DecisionSupport class with `frame()`, `analyze()`, `recommend()` methods
2. Create decision templates: binary, multi-option, resource allocation, timing
3. Wire into Algorithm v1 — when intent is "decision", trigger decision support
4. Store decisions in `pai/MEMORY/WORK/<session>/decisions/`
5. Run Fabric `t_red_team_thinking` on recommended option
6. Output: structured decision brief (Miessler format)

**Commit:** `feat(pai): decision support engine — structured decision framing with red team analysis`

---

## Phase 4C: Priority Engine (The Jordan Voss Test)

### Task 5: Build Priority Engine

**Files:**
- Create: `pai/intelligence/priority_engine.py`

**What it does:**
Every morning, answers: "What is the ONE move today?" in <30 seconds. This is the Jordan Voss test.

**Priority scoring factors:**
- Deadline proximity (exponential weight as deadline approaches)
- Goal alignment (TELOS/GOALS.md connection strength)
- Blocking dependencies (is this blocking other work?)
- Effort/impact ratio (quick wins score higher early in day)
- Competitive urgency (SCOUT P0 signals)
- Calendar constraints (meetings limit available deep work time)

**Implementation steps:**
1. Create PriorityEngine class with `calculate_one_thing()` method
2. Pull inputs: goals, calendar, email P0/P1, SCOUT signals, blocked items
3. Score each candidate action on 6 factors (weighted)
4. Output: "THE ONE THING: [action] — because [reason]"
5. Include in morning brief header
6. If Mike asks "What should I do?" at any time, re-calculate live
7. Track accuracy: did Mike actually do the recommended thing? (V5 learning input)

**Output format:**
```
THE ONE THING TODAY:
> [Action in imperative form]

WHY: [One sentence — the most compelling reason]
IMPACT: [What changes if you do this]
TIME: [Estimated time to complete]
BLOCKED BY: [Nothing / specific blocker]
```

**Commit:** `feat(pai): priority engine — Jordan Voss test, 6-factor scoring, one-thing output`

---

## Phase 4D: Structured Brief Format

### Task 6: Implement Miessler-Style Brief Format

**Files:**
- Create: `pai/intelligence/brief_formatter.py`
- Create: `pai/templates/brief-morning.md`
- Create: `pai/templates/brief-decision.md`
- Create: `pai/templates/brief-meeting.md`

**What it does:**
All briefs follow a consistent structure inspired by Miessler's PAI output format.

**Morning brief template:**
```markdown
# {date} — Morning Brief

## THE ONE THING
> {priority_engine_output}

## Calendar ({count} meetings, {free_hours}h deep work)
{meeting_list}

## Email ({p0_count} urgent, {total_count} unread)
{urgent_emails}

## Goals ({active_count} active, {blocked_count} blocked)
{goal_status}

## Signals ({signal_count})
{competitive_signals}

## Learning (yesterday)
{recent_learning_summary}

---
*Generated by Jake PAI at {timestamp}*
```

**Implementation steps:**
1. Create BriefFormatter class with template rendering
2. Create templates for morning, decision, meeting, competitive
3. Update morning_brief.py to use BriefFormatter
4. Update meeting_prep.py to use BriefFormatter
5. All briefs include timestamp and source attribution

**Commit:** `feat(pai): structured brief format — Miessler-style templates for all brief types`

---

## Phase 4E: Verification

### Task 7: End-to-End Proactive Intelligence Verification

**Tests:**
1. Send ambiguous message → intent classifier routes correctly
2. Send during DND hours → P2/P3 notifications are batched, P0 still delivered
3. Ask "What should I do today?" → Priority engine responds in <30 seconds with ONE thing
4. Ask "Should I take this meeting?" → Decision support generates structured analysis
5. Check morning brief → includes THE ONE THING header + SCOUT signals
6. Run for 2 weeks → notification quality rated 8+/10 by Mike

**Commit:** `feat(pai): V4 proactive intelligence verification complete`

---

## V4 Exit Criteria (All Must Pass)

- [ ] Intent classifier routes messages to correct model tier (>85% accuracy over 7 days)
- [ ] Smart notifications respect DND hours and urgency tiers
- [ ] P0 always delivered, P2/P3 batched correctly
- [ ] SCOUT pipeline runs daily, surfaces competitive signals across 3 companies
- [ ] Decision support generates structured analysis with red team
- [ ] Priority engine passes Jordan Voss test (<30 seconds to THE ONE THING)
- [ ] Structured brief format applied to all brief types
- [ ] Mike identifies the one move in <30 seconds for 14 consecutive days
- [ ] Notification quality rated 8+/10 for 2 weeks

**Score target: 70 → 78**
