# DEATHSTAR Walls Phase — Build Plan

**Date**: 2026-03-23
**Author**: Jake
**Status**: READY TO BUILD
**Dependencies**: Foundation (85% → 100% this session)
**Design reference**: `docs/plans/2026-03-21-25x-deathstar-design.md`

---

## Current State Audit

| Studio | Status | What's Done | What's Missing |
|--------|--------|-------------|----------------|
| AI Dev Studio | 5% | Design doc, market research | Hermes skill, MCP commands, TransformFit integration |
| AI Social Studio | ~40% | Film Studio build plan (3/7 steps), characters + locations generated, design doc complete | Hermes skill, SPREAD framework integration, brand voice capture, Viral Architect pipeline test, posting workflow |

---

## WALL 1: AI Dev Studio

### What It Is

Jake-powered software development studio. Mike describes a product or feature, Jake (with Susan's Atlas + Forge + Nova + Sentinel team) designs, specs, builds, and deploys it. Callable via Telegram. First client: TransformFit.

### What Needs to Be Built (4 deliverables)

#### W1.1 — Hermes Skill: `ai-dev-studio`
**File**: `~/.hermes/skills/ai-dev-studio/SKILL.md`
**Status**: Does not exist
**Effort**: 1 session

This skill conducts a structured dev studio session. When Mike says "Jake, start a dev studio session for TransformFit onboarding flow":

1. **Context load**: Pull company context from brain (brain_search for company name)
2. **Team assembly**: Select agents based on build type:
   - Web app → Atlas + Forge + Nova + Sentinel
   - Mobile → Atlas + Forge + Nova + mobile-developer
   - API/data pipeline → Atlas + Forge + backend-architect
   - AI feature → Atlas + Nova + ml-engineer + Forge
3. **Discovery interview**: Ask 5 scoping questions (what, why, who, constraints, definition of done)
4. **Spec generation**: Produce a structured spec doc (purpose, user stories, architecture, file list, API surface)
5. **Implementation plan**: Break into milestones with time estimates and validation gates
6. **Execute or hand off**: If it's a Claude Code task, Jake creates the plan and hands off. If it's a full build, Jake kicks off the first milestone.
7. **Progress reporting**: Telegram updates at each milestone gate

**SKILL.md Structure**:
```
# AI Dev Studio
trigger_keywords: dev studio, build session, start a build, spec out, design session
---
[Full interview flow, agent assembly logic, spec template, milestone format]
```

#### W1.2 — MCP Commands
**Files**: `.claude/commands/dev-studio-start.md`, `dev-studio-status.md`, `dev-studio-ship.md`
**Status**: Does not exist
**Effort**: 0.5 sessions

```
/dev-studio start [company] [feature]   → kick off full build session
/dev-studio status                       → where are we, what's next
/dev-studio ship                         → final QA + deploy confirmation
```

#### W1.3 — TransformFit Context in Brain
**Status**: Partial (company context exists in brain from prior sessions)
**What's missing**: TransformFit-specific tech context
- Stack decision: React Native (mobile first), Supabase (auth + db), Expo (deployment)
- Core features Phase 1: coach onboarding, client import, program builder
- Store as `jake_semantic` with project=transformfit and tags=['tech','architecture','decision']

#### W1.4 — First Studio Session: TransformFit MVP
**Status**: Not started
**What it produces**:
- `docs/plans/transformfit-mvp-spec.md` — full product spec
- `docs/plans/transformfit-mvp-implementation.md` — step-by-step build plan
- First milestone committed to code

**Success criteria**: Mike types "Jake, start a dev studio session for TransformFit" and gets a complete spec doc + implementation plan within one Telegram conversation.

---

### AI Dev Studio Build Sequence

```
Session A (0.5): Write ai-dev-studio SKILL.md
Session B (0.5): Write MCP commands + test with mock input
Session C (1.0): Run first real studio session → TransformFit MVP spec
```

---

## WALL 2: AI Social Studio

### What's Done (40%)

Per `2026-03-23-social-media-film-studio-build-plan.md` (Session 1 complete):
- ✅ Step 1: Higgsfield API configured, SDK installed
- ✅ Step 2: Soul Cast characters created (TF-COACH, TF-ATHLETE + existing @Rogers, @James)
- ✅ Step 3: Location library generated (6 locations)

### What's Missing (60%)

#### W2.1 — Viral Architect Pipeline (Step 4 of build plan)
**Status**: Not started
**File**: `~/viral-architect-hub/backend/services/instagram_publisher.py`
**What**: Verify posting to @rodgemd1 via existing Viral Architect infrastructure
**Effort**: 0.5 sessions
**Blocking**: Steps 5, 6, 7 (can't test end-to-end without this)

#### W2.2 — First Reel Production (Step 5)
**Status**: Not started
**What**: End-to-end production of "Behind the Build" reel for @rodgemd1 (Mike's IG)
**Character**: @Rogers | **Location**: MR-LOC-01 (Home Office)
**Effort**: 1 session
**Output**: 30s posted reel on @rodgemd1

#### W2.3 — First TransformFit Reel (Step 6)
**Status**: Not started
**What**: First branded fitness content for TransformFit
**Character**: TF-COACH | **Pillar**: "Coach's Corner" (education/expertise)
**Effort**: 1 session
**Output**: Posted reel with TF branding

#### W2.4 — Hermes Skill: `ai-social-studio`
**File**: `~/.hermes/skills/ai-social-studio/SKILL.md`
**Status**: Does not exist (this is different from the Film Studio build plan — that's the production workflow, this is the strategic layer)
**Effort**: 1 session

This skill handles the STRATEGY layer on top of the film production workflow:
1. **Brand voice capture**: Interview to extract brand personality, tone, content pillars
2. **Content calendar generation**: Weekly/monthly calendar based on pillars and goals
3. **SPREAD scoring**: Score each piece of content against viral dimensions before posting
4. **Analytics ingestion**: Pull from Instagram Insights, adapt strategy
5. **Agent team**: Aria (growth) + Herald (PR) + Prism (brand) + Beacon (SEO/ASO)

**SPREAD Framework implementation** (Viral Architect's proprietary methodology):
- **S**ensitive (touches something people care about deeply)
- **P**rovocative (challenges assumptions or comfort zones)
- **R**eplicable (easy to recreate or remix)
- **E**motional (creates a feeling, not just information)
- **A**mbiguous (slightly open-ended — triggers comment/debate)
- **D**istributive (designed to be shared, not just liked)

Score content 1-5 on each dimension. Target: 3+ total score on 3+ dimensions for publish.

#### W2.5 — SPREAD Scoring Tool
**File**: `susan-team-architect/backend/scripts/viral_architect_spread_score.py`
**Status**: Does not exist
**Effort**: 0.5 sessions
**What**: Takes a caption, hook, or content idea. Returns SPREAD score + suggestions.

---

### AI Social Studio Build Sequence

```
Session A (0.5): Step 4 — verify Viral Architect pipeline
Session B (1.0): Step 5 — produce + post first reel (@rodgemd1)
Session C (1.0): Step 6 — produce + post first TransformFit reel
Session D (1.0): Write ai-social-studio SKILL.md with SPREAD framework
Session E (0.5): Build SPREAD scoring script
```

---

## Critical Path

The critical path through Walls to Roof is:

```
Foundation 100% (THIS SESSION)
    → AI Dev Studio skill (Session A)
        → TransformFit MVP spec (Session C)
            → TransformFit MVP build begins (ROOF)
    → Social Studio pipeline test (Session A)
        → First reel live (Session B)
            → Content flywheel starts (ROOF)
```

**The roof cannot start without the walls. The walls cannot finish without the foundation.**

---

## Session Assignments (Next 5 Sessions)

| Session | Wall | Task | Deliverable |
|---------|------|------|-------------|
| Next | Foundation → complete | Wrap F5 audit, commit | Foundation 100% |
| S+1 | Wall 1 | Write ai-dev-studio SKILL.md | Skill exists, tested |
| S+2 | Wall 2 | Viral Architect pipeline + first reel | @rodgemd1 has first AI reel |
| S+3 | Wall 1 | TransformFit spec via dev studio | MVP spec + plan written |
| S+4 | Wall 2 | First TransformFit reel + SPREAD tool | Content flywheel started |
| S+5 | Both | ai-social-studio SKILL.md | Both studios Telegram-callable |

---

## Open Questions for Mike

1. **Dev Studio pricing**: $15K-50K per external build — are we starting external clients now, or is TransformFit the internal proof-of-concept first?
2. **Social Studio cadence**: How often per week are we posting to @rodgemd1 vs TransformFit? (Affects content calendar)
3. **SPREAD framework**: Do we want the scoring tool to be interactive (Jake asks questions) or automated (analyzes the content text directly)?
4. **TransformFit stack**: Confirm: React Native + Expo + Supabase? Or different choices?
