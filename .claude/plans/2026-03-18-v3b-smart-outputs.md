# V3b — Smart Outputs

**Author:** Jake + Mike
**Date:** 2026-03-18
**Status:** COMPLETE — All 3 phases shipped
**Estimated Sessions:** 2-3 focused sessions
**Parent:** V1-V5 Roadmap (`~/.claude/plans/2026-03-18-v1-v5-roadmap.md`)
**Depends On:** V3a (COMPLETE)

---

## Goal

Make the V3a agents produce smarter, audience-specific, actionable outputs. No new infrastructure — all file-based, all shipping independently.

## Scope Changes from Original V3b

- **REMOVED: Persistent knowledge graph** — Moved to V3c. Too much infra for this phase.
- **REMOVED: n8n workflow automation** — Moved to V3c. Hooks/crons work fine.
- **REMOVED: ContextForge/Codebase Memory MCP** — Moved to V3c. Nice-to-have, not blocking.
- **KEPT: HERALD agent** — SCOUT is live, HERALD makes its output actionable.
- **KEPT: ORACLE-BRIEF agent** — Most immediate daily impact.
- **KEPT: Cross-domain pattern matcher** — Lightweight file-based version, no graph DB.

## Phases

### Phase 1: ORACLE-BRIEF Agent (1 session)

**What:** Specialized agent that takes overnight intel + SCOUT signals + Oracle Health domain data → produces a Matt-ready executive brief with forward blurbs.

**Input sources:**
- Overnight intel files (`~/Desktop/oracle-health-ai-enablement/artifacts/morning-briefs/intel-*.md`)
- SCOUT competitive signals (`.startup-os/briefs/scout-signals-*.md`)
- ARIA brief Oracle Health section (`.startup-os/briefs/aria-brief-*.md`)
- Susan RAG Oracle Health domain data (4 layers: market, clinical, regulatory, marketing)

**Output:**
- `.startup-os/briefs/oracle-brief-{date}.md`
- Format: Top 3 priorities + market intel + forward-ready blurbs for Matt/Bharat/Seema
- Must pass SENTINEL-HEALTH clearance before distribution

**Compliance integration:**
- ORACLE-BRIEF auto-invokes SENTINEL-HEALTH on its own output
- Only outputs classified CLEAR or REVIEW (with flagged items) get saved
- BLOCK classification = output suppressed, alert to Mike

**Files to create:**
- `.claude/agents/oracle-brief.md` (new)

**Validation gate:** Generate a test brief from existing intel data. Run through SENTINEL-HEALTH. Confirm CLEAR or REVIEW with appropriate findings.

### Phase 2: HERALD Agent (1 session)

**What:** Takes SCOUT P0/P1 signals → drafts competitive response content (positioning 1-pagers, talking points, blog outlines).

**Input sources:**
- SCOUT signals (`.startup-os/briefs/scout-signals-*.md`) — P0 and P1 only
- Susan RAG Oracle Health domain data (marketing narrative + competitive landscape)
- Brave/Tavily for real-time competitor claim verification

**Output:**
- `.startup-os/briefs/herald-response-{date}.md`
- Format: For each P0/P1 signal → draft response with talking points, recommended channel, urgency

**Files to create:**
- `.claude/agents/herald.md` (new)

**Validation gate:** Feed a P0 signal from SCOUT → HERALD produces a response draft → draft passes SENTINEL-HEALTH clearance.

### Phase 3: Cross-Domain Pattern Matcher (0.5 session)

**What:** Weekly scan of all project briefs, decisions, and patterns. Surfaces what works in one project that could apply to another.

**How it works (no graph DB):**
1. Read all briefs from last 7 days across all projects
2. Read `.claude/docs/cross-domain-pattern-registry.md` for known patterns
3. Compare: Are any patterns from Project A showing up in Project B's signals?
4. Output: Pattern match report with transfer recommendations

**Output:**
- `.startup-os/briefs/patterns-{date}.md`

**Files to create/modify:**
- `.claude/agents/pattern-matcher.md` (new)
- Update `.claude/docs/cross-domain-pattern-registry.md` with new discovered patterns

**Validation gate:** Run against existing briefs. Find at least 1 cross-domain pattern (or confirm "no new patterns" if none exist).

---

## Success Criteria

1. ORACLE-BRIEF produces Matt-ready briefs that pass SENTINEL-HEALTH clearance
2. HERALD drafts competitive responses from SCOUT P0/P1 signals
3. Cross-domain pattern matcher identifies at least 1 transferable pattern (or correctly reports none)
4. All outputs saved to `.startup-os/briefs/` in standardized format
5. All new agents registered in autonomy graduation tracker at T0

---

## What V3b Does NOT Include

- Persistent knowledge graph (V3c)
- n8n workflow automation (V3c)
- ContextForge / Codebase Memory MCP (V3c)
- Generalized stakeholder output adaptation (V3c — ORACLE-BRIEF covers the one stakeholder we have)
- Automated email delivery for ORACLE-BRIEF (use existing Resend pattern from ARIA when ready)

---

## Session Plan

| Session | Focus | Duration |
|---------|-------|----------|
| Session 1 | Phase 1 (ORACLE-BRIEF agent) | ~60 min |
| Session 2 | Phase 2 (HERALD agent) | ~60 min |
| Session 3 | Phase 3 (Cross-domain pattern matcher) | ~30 min |

*Each phase ships independently. No phase depends on a previous phase being complete.*
