# V2 Execution Plan — Enhanced Workflows

**Date:** 2026-03-18
**Status:** In Progress
**Author:** Jake
**Confidence:** DRAFT — plan approved, execution begins this session

---

## Prioritized Build Order

V2 has ~25 items. We're NOT building all of them today. Here's the honest priority stack:

### Phase 1: Core Governance (TODAY — this session)
These are the foundation that everything else depends on.

1. **Decision audit trail hook** — Log every significant agent action to `.claude/audit/decisions.jsonl`
2. **Research-first gate hook** — Block implementation on new projects without research phase
3. **ARIA agent definition** — Daily Operator Brief agent (3 bullets, owners, signals, actions)
4. **Project Assessment Scorecard skill** — 6-dimension rated output for any project

### Phase 2: Agent Team (This week)
Define the V2 core agents that power the enhanced workflows.

5. **KIRA agent** — Intent-aware command router
6. **LEDGER agent** — Funnel conversion + 30-day trajectory tracking
7. **Agent contradiction handler hook** — Surface divergent outputs

### Phase 3: Research Pipeline (Week 2)
The research-first pipeline that makes everything else smarter.

8. **Research-First Pipeline skill** — `/project-setup` triggers 5-phase research
9. **Auto-research dispatch pattern** — Parallel MCP researchers
10. **Knowledge freshness loop** — Weekly automated RAG freshness audit

### Phase 4: Deep Workflows (Weeks 3-4)
The 5 workflows that replace 40 shallow features.

11. **Morning brief synthesis** — Susan + Steve + ARIA
12. **Content generation workflow** — Herald + Scout CI-aware content
13. **Strategic memo workflow** — Oracle-Brief + Memo Studio
14. **Coach outreach workflow** — Alex Recruiting deep pipeline
15. **Project assessment workflow** — End-to-end new project scoring

### Phase 5: MCP Installations (As needed)
Install when a workflow requires it, not speculatively.

16. TrendRadar MCP — Already connected! Verify and configure
17. Qdrant MCP — When RAG search needs custom embeddings
18. Kreuzberg MCP — When document ingestion pipeline is built
19. GenAI Toolbox MCP — When database queries are needed
20. n8n MCP — When visual workflow automation is needed

---

## Phase 1 Execution Details (TODAY)

### Item 1: Decision Audit Trail Hook
- **Type:** PostToolUse hook (Agent matcher)
- **File:** `bin/hooks/decision-audit.sh`
- **Output:** Appends JSON line to `.claude/audit/decisions.jsonl`
- **Schema:** `{"timestamp", "tool", "agent_type", "description", "confidence_tier", "files_affected"}`
- **Wiring:** Add to `.claude/settings.json` PostToolUse

### Item 2: Research-First Gate Hook
- **Type:** PreToolUse hook (Write|Edit matcher)
- **File:** `bin/hooks/research-first-gate.sh`
- **Logic:** Check if `.claude/plans/` has a research/plan doc for current work. Advisory, not blocking (V2 = warning, V3 = blocking)
- **Wiring:** Add to `.claude/settings.json` PreToolUse

### Item 3: ARIA Agent Definition
- **Type:** Agent definition (.claude/agents/aria.md)
- **Role:** Daily Operator Brief generator
- **Input:** Git status across projects, HANDOFF.md files, scheduled task outputs, TrendRadar signals
- **Output:** 3-bullet brief with owners, signals, recommended actions
- **Model:** sonnet (generation task, not synthesis)

### Item 4: Project Assessment Scorecard Skill
- **Type:** Skill (.claude/skills/project-assessment/SKILL.md)
- **Dimensions:** Research, Team, Tech, Strategy, Capability, Governance
- **Output:** Rated scorecard (1-10 per dimension) with evidence basis
- **Integration:** Uses Susan agents for assessment

---

## Success Criteria (V2 — Dana Kwon Test)
- [ ] Research-First Pipeline produces rated scorecard for new project in < 15 min
- [ ] 5 deep workflows replace 40 shallow features
- [ ] KIRA routes commands with >0.7 confidence
- [ ] Decision audit trail captures all agent actions
- [ ] Pipeline conversion visible in LEDGER dashboard

## Stage Gates
- **After Phase 1:** Review governance + ARIA. Do hooks fire correctly? Does ARIA produce useful briefs?
- **After Phase 2:** Review agent team. Do KIRA/LEDGER integrate with existing Susan agents?
- **After Phase 3:** Review research pipeline. Does it actually produce better outcomes?
- **After Phase 4:** Full V2 audit. Are the 5 workflows genuinely deep?
- **After Phase 5:** MCP audit. Are all installed MCPs being used?
