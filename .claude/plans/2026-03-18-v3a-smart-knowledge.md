# V3a — Smart Knowledge

**Author:** Jake + Mike
**Date:** 2026-03-18
**Status:** COMPLETE — All 4 phases shipped
**Estimated Sessions:** 3-4 focused sessions over 2-3 weeks
**Parent:** V1-V5 Roadmap (`~/.claude/plans/2026-03-18-v1-v5-roadmap.md`)

---

## Goal

Make the existing V2 system smarter without adding new infrastructure. Focus on knowledge lifecycle, lightweight specialist agents, and autonomy graduation tracking.

## Scope Changes from Original V3

- **REMOVED: Telegram delivery** — Genspark OpenClaw bot handles Telegram channel. Our job is to save outputs to repo files so the bot can read them.
- **REMOVED: Persistent knowledge graph** — Moved to V3b. Too much infra for this phase.
- **REMOVED: n8n workflow automation** — Moved to V3b. Not needed yet.
- **REMOVED: HERALD agent** — Needs SCOUT output proven first. V3b.
- **REMOVED: ORACLE-BRIEF agent** — Needs knowledge quality proven first. V3b.
- **ADDED: Repo-accessible output format** — ARIA/LEDGER outputs saved to `.startup-os/briefs/` so Genspark bot can relay via Telegram.

## Phases

### Phase 1: Knowledge Lifecycle Management (1 session)

**What:** Extend the existing freshness audit into a full lifecycle system.

| Task | Type | Detail |
|------|------|--------|
| Define lifecycle states | Doc | DRAFT → REVIEW → PUBLISHED → AGING → STALE → REFRESH |
| Lifecycle transition rules | Doc | What triggers each state change (age, access frequency, domain changes) |
| Auto-refresh triggers | Scheduled Task | When freshness audit finds STALE records, auto-queue research refresh |
| Freshness dashboard output | File | Weekly report saved to `.startup-os/briefs/freshness-{date}.md` |

**Files to create/modify:**
- `.claude/docs/knowledge-lifecycle.md` (new)
- `.claude/commands/knowledge-freshness.md` (update — add lifecycle states)
- Scheduled task: `mike-studio-stale-watchdog` (update — add auto-refresh dispatch)

**Validation gate:** Run freshness audit, confirm lifecycle states assigned, confirm auto-refresh queues work.

### Phase 2: SCOUT + SENTINEL-HEALTH Agents (1 session)

**What:** Two lightweight specialist agents for competitive monitoring and compliance checking.

| Agent | Purpose | Model | Input | Output |
|-------|---------|-------|-------|--------|
| SCOUT | Competitive intelligence monitoring + content white space detection | sonnet | TrendRadar signals, overnight intel, Susan RAG | Competitive signals with priority scoring |
| SENTINEL-HEALTH | Green/yellow/red compliance clearance on Oracle Health outputs | haiku | Any Oracle Health output + compliance rules | CLEAR / REVIEW / BLOCK with reason |

**Files to create:**
- `.claude/agents/scout.md` (new)
- `.claude/agents/sentinel-health.md` (new)

**Validation gate:** SCOUT correctly identifies a competitive signal from existing overnight intel. SENTINEL-HEALTH correctly flags a compliance concern on a test Oracle Health brief.

### Phase 3: Autonomy Graduation Tracking (1 session)

**What:** Start tracking workflow accuracy so we can graduate proven workflows from DRAFT → AUTO → SUPERVISED → AUTONOMOUS over time.

| Task | Type | Detail |
|------|------|--------|
| Graduation schema | Doc | Define what "accuracy" means per workflow type |
| Tracking file | Data | `.startup-os/autonomy/graduation-tracker.yaml` — records per-workflow metrics |
| 30-day clock starts | Hook | After each AUTO-tagged output, log outcome |
| Graduation review | Scheduled Task | Weekly: check if any workflow qualifies for tier upgrade |

**Files to create/modify:**
- `.claude/docs/autonomy-graduation.md` (new)
- `.startup-os/autonomy/graduation-tracker.yaml` (new)
- `bin/hooks/autonomy-tracker.sh` (new)
- Scheduled task: new weekly graduation review

**Validation gate:** ARIA brief accuracy tracked for 1 week. Graduation tracker file populated with real data.

### Phase 4: Repo-Accessible Output Hub (quick, any session)

**What:** Ensure all ARIA/LEDGER/SCOUT outputs are saved to standardized repo locations so the Genspark bot can find and relay them via Telegram.

| Output | Location | Format |
|--------|----------|--------|
| ARIA daily brief | `.startup-os/briefs/aria-brief-{date}.md` | Already done ✅ |
| LEDGER report | `.startup-os/briefs/ledger-report-{date}.md` | New |
| SCOUT signals | `.startup-os/briefs/scout-signals-{date}.md` | New (Phase 2) |
| Freshness report | `.startup-os/briefs/freshness-{date}.md` | New (Phase 1) |

**Coordination with Genspark bot:** The bot reads the repo via GitHub API. As long as outputs are committed and pushed, it can relay them.

---

## Success Criteria

1. Knowledge lifecycle states assigned to all RAG domains
2. Auto-refresh triggers fire on STALE records without human intervention
3. SCOUT surfaces at least 1 competitive signal from existing overnight intel
4. SENTINEL-HEALTH correctly classifies Oracle Health outputs
5. Autonomy graduation tracker populated with real data after 1 week
6. All agent outputs saved to `.startup-os/briefs/` in standardized format

## What V3a Does NOT Include

- Persistent knowledge graph (V3b)
- HERALD agent (V3b — needs SCOUT proven)
- ORACLE-BRIEF agent (V3b — needs knowledge quality proven)
- n8n workflow automation (V3b)
- Cross-domain pattern detection automation (V3b)
- Stakeholder-specific output adaptation (V3b)

---

## Session Plan

| Session | Focus | Duration |
|---------|-------|----------|
| Session 1 | Phase 1 (Knowledge Lifecycle) + Phase 4 (Output Hub) | ~90 min |
| Session 2 | Phase 2 (SCOUT + SENTINEL-HEALTH agents) | ~60 min |
| Session 3 | Phase 3 (Autonomy Graduation) | ~60 min |
| Session 4 | Integration testing + V3a validation | ~45 min |

---

*V3a is designed to be incrementally valuable. Each phase ships independently. No phase depends on a previous phase being complete.*
