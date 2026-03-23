# Oracle Health M&CI — SOP Capture Roadmap

**Date**: 2026-03-23
**Owner**: Mike Rodgers, Sr. Director, M&CI
**Source**: docs/plans/2026-03-22-oracle-mci-sop-master-list.md
**Status**: 4 of 28 SOPs complete

---

## Completed SOPs (4/28)

| SOP | Title | Status | Score |
|-----|-------|--------|-------|
| SOP-02 | Signal Triage & Urgency Classification | ✅ DONE | v1.0 |
| SOP-09 | Win/Loss Analysis | ✅ DONE | v2.1, scored 9.025/10 |
| SOP-11 | Trade Show / Conference Intelligence | ✅ DONE | v1.0 |
| SOP-13 | Market Sizing (R-01 Methodology) | ✅ DONE | v1.0 |

**Files**: `docs/sops/SOP-02-signal-triage-urgency-classification.md`, `SOP-09-win-loss-analysis.md`, `SOP-11-trade-show-intelligence.md`, `SOP-13-market-sizing-r01.md`

---

## Next 5 SOPs — Prioritized Build Order

Priority determined by: **impact × documentation gap × Mike's unique methodology IP**

### #1 — SOP-08: Competitive Battlecard Creation & Maintenance

**Why first**: High-value sales enablement artifact. Currently a GAP → Implicit. The oracle-battlecard-update recipe runs but has no formal SOP backing it. This is the most visible deliverable to field teams.

**Source**: BEST PRACTICE (Klue, Crayon, SCIP) + YOUR (oracle-battlecard-update.yaml, competitive-battlecard-refresh.yaml recipes running)
**Maturity**: Gap → Implicit (recipes exist, no SOP)
**Priority**: P1

**What to capture**:
- Template: Quick Dismiss + Overview + Differentiators + Landmine Questions + Objection Handling + Pricing + Win/Loss Stories + Counter-FUD
- Maintenance cadence: Monthly forced review, 48h event-driven updates, 90-day max
- Owner, update triggers, distribution (CRM integration)
- Sales feedback loop — how field reps submit corrections
- 6 existing battlecards: DAX Copilot, Waystar, Epic, Ensemble, R1 RCM, FinThrive

**Estimated effort**: 2-3 hours (structured interview + template + policy)
**Dependencies**: None (can start immediately)
**Output file**: `docs/sops/SOP-08-battlecard-creation-maintenance.md`

---

### #2 — SOP-14: Executive Offsite Strategy Prep

**Why second**: Complex multi-phase process done twice (Seema offsite) but never formalized. Mike's methodology is proprietary. Quality bar is defined (80+ panelist evaluations, 9.0 average). Risk of losing this IP if not captured now.

**Source**: YOUR (Seema offsite — 18 files across 5 categories)
**Maturity**: Implicit (done twice, not documented)
**Priority**: P1

**What to capture**:
- Phase timeline: Intake → Data Assembly → Framework Analysis → War Games → Synthesis → Expert Panel → Deck
- 6 foundation documents per engagement
- 10 Types framework application, Innosight Dual Transformation, Design Thinking, Future-Back
- Panel scoring: 8 personas, weighted, 7.0+ threshold, Matt + Seema both 7+
- Iteration protocol: 2 passes to reach 9.0 standard
- Deck production process

**Estimated effort**: 3-4 hours (most complex SOP in the program)
**Dependencies**: None (Seema offsite session data available)
**Output file**: `docs/sops/SOP-14-executive-offsite-strategy-prep.md`

---

### #3 — SOP-18: 8-Person Weighted Expert Panel Review

**Why third**: Core quality methodology already automated in Claude Code. Documenting it makes it auditable, transferable to team members, and defensible as a program asset. Highest leverage for quality control.

**Source**: YOUR (CLAUDE.md — already enforced in code)
**Maturity**: Automated (enforced) but undocumented as standalone SOP
**Priority**: P1

**What to capture**:
- Panel composition: Matt (20%), Seema (20%), Steve (15%), Compass (10%), Ledger (10%), Marcus (10%), Forge (10%), Herald (5%)
- Thresholds: 7.0+ average, no single below 5, Matt and Seema both 7+
- 8 Quality Gates: Data Provenance → Structural Integrity → Strategic Altitude → Competitive Accuracy → Financial Integrity → Executive Readiness → Compliance → URL Verification
- Gate failure handling + iteration protocol
- Exemption criteria (when to bypass for speed)
- How to invoke: which deliverable types require full panel vs. fast track

**Estimated effort**: 1.5-2 hours (already documented in CLAUDE.md, needs extraction + expansion)
**Dependencies**: None
**Output file**: `docs/sops/SOP-18-expert-panel-review.md`

---

### #4 — SOP-23: Intelligence Distribution Matrix

**Why fourth**: Who gets what, when, in what format is currently implicit. Without a formal matrix, Mike is the only distribution point — single point of failure. This is table stakes for a functioning CI program.

**Source**: BEST PRACTICE (Crayon, CI Alliance) + YOUR (implicit delivery to Matt, field teams, product)
**Maturity**: Gap → Implicit
**Priority**: P1

**What to capture**:
- RACI matrix: every M&CI deliverable × stakeholder × format × cadence
- Delivery channels: Email, Slack, SharePoint, Teams, Telegram
- Format standards by audience: Matt gets executive brief, field gets battlecard, product gets win/loss themes
- Escalation matrix: which signals go to whom, within what timeframe
- Feedback loop: how each audience signals "this was useful" or "I need something different"

**Estimated effort**: 2-3 hours (requires thinking through all stakeholder relationships)
**Dependencies**: None (build from existing delivery patterns)
**Output file**: `docs/sops/SOP-23-intelligence-distribution-matrix.md`

---

### #5 — SOP-27: Intelligence Cycle (8-Step)

**Why fifth**: Mike's 8-step cycle is a unique adaptation of the SCIP 5-step standard. Documenting it formalizes the department's operating methodology and makes it auditable. The oracle-signal-triage recipe implements steps 3-4 — the SOP ties the whole cycle together.

**Source**: YOUR (ChatGPT — designed your own 8-step) + BEST PRACTICE (SCIP 5-step)
**Maturity**: Implicit (cycle exists in practice, not documented)
**Priority**: P1

**What to capture**:
- Full 8-step cycle with handoff points: Prioritize KITs → Frame hypotheses → Collect/source → Validate/curate → Analyze/model → Synthesize/recommend → Activate in forums → Track outcomes
- Tool usage per step (which MCP, which recipe, which script)
- Quality checkpoints within the cycle
- Cadence: Annual (full refresh), Quarterly (market + competitor review), Monthly (signal dashboard + KPI), Event-driven (shock response)
- Distinction from SCIP standard: what Mike's version adds and why

**Estimated effort**: 2 hours
**Dependencies**: Benefits from SOP-23 (Distribution Matrix) being done first
**Output file**: `docs/sops/SOP-27-intelligence-cycle-8-step.md`

---

## Full 24 Remaining SOPs — Prioritized Backlog

| Rank | SOP # | Title | Category | Priority | Maturity | Effort |
|------|-------|-------|----------|----------|----------|--------|
| 1 | SOP-08 | Battlecard Creation & Maintenance | CI Production | P1 | Gap→Implicit | 2-3h |
| 2 | SOP-14 | Executive Offsite Strategy Prep | Strategic Analysis | P1 | Implicit | 3-4h |
| 3 | SOP-18 | 8-Person Expert Panel Review | Quality & Governance | P1 | Automated | 1.5-2h |
| 4 | SOP-23 | Intelligence Distribution Matrix | Knowledge Mgmt | P1 | Gap | 2-3h |
| 5 | SOP-27 | Intelligence Cycle (8-Step) | Dept Operations | P1 | Implicit | 2h |
| 6 | SOP-01 | Daily Morning Brief Assembly | Daily Operations | P1 | Automated | 1h |
| 7 | SOP-03 | Weekly Executive Briefing (Matt) | Daily Operations | P1 | Automated | 1h |
| 8 | SOP-05 | Source Evaluation & Data Provenance | Daily Operations | P1 | Partial | 1.5h |
| 9 | SOP-07 | Competitor Profile Creation & Maintenance | CI Production | P1 | Partial | 2h |
| 10 | SOP-10 | Pricing & Packaging Intelligence | CI Production | P1 | Automated | 1.5h |
| 11 | SOP-15 | Strategic Framing & Innovation Analysis | Strategic Analysis | P2 | Partial | 2h |
| 12 | SOP-17 | War Gaming & Scenario Planning | Strategic Analysis | P2 | Implicit | 2-3h |
| 13 | SOP-19 | Executive Writing Pipeline (Matt/Seema) | Quality | P2 | Automated | 1h |
| 14 | SOP-20 | Research→Define→Design→Build Phase Gate | Quality | P2 | Automated | 1h |
| 15 | SOP-21 | SharePoint Content Governance | Quality | P2 | Partial | 2h |
| 16 | SOP-22 | Ellen OS Package Build & Distribution | Knowledge Mgmt | P2 | Automated | 1h |
| 17 | SOP-24 | Knowledge Base Curation & Ingestion | Knowledge Mgmt | P2 | Automated | 1.5h |
| 18 | SOP-26 | M&CI Department Operating Model | Dept Operations | P1 | Implicit | 3h |
| 19 | SOP-28 | Program Effectiveness Measurement | Dept Operations | P2 | Gap | 2h |
| 20 | SOP-04 | Data Freshness Audit | Daily Operations | P2 | Automated | 1h |
| 21 | SOP-06 | Regulatory & Compliance Monitoring | Daily Operations | P2 | Partial | 2h |
| 22 | SOP-12 | Competitive Response Playbook | CI Production | P2 | Gap | 2-3h |
| 23 | SOP-16 | Monthly Strategic Intelligence Report | Strategic Analysis | P2 | Automated | 1h |
| 24 | SOP-25 | Stakeholder Request Intake & Tracking | Knowledge Mgmt | P2 | Gap | 1.5h |

**Total remaining effort estimate**: 40-50 hours across 24 SOPs
**Recommended cadence**: 2-3 SOPs per week → complete in 8-12 weeks

---

## Automation Mapping

| SOP # | Jake's Role |
|-------|------------|
| 01, 03, 04, 06, 16, 22 | Already automated via crons — just document |
| 08, 10, 12, 17, 24 | Jake drafts from data, Mike validates |
| 02✓, 11✓, 13✓, 14, 26, 27 | SOP Capture skill interviews Mike, structures output |
| 09✓, 15, 19, 20, 21, 23, 25, 28 | Mike owns process, Jake tracks and monitors |

**SOP Capture skill**: `~/.hermes/skills/jake-sop-capture` — invoke with `jake sop-capture` to start structured interview

---

## Storage Protocol

Each SOP → stored as `jake_procedural` in brain:
```bash
python scripts/jake_brain_cli.py store-procedural \
  --source-type sop \
  --content "$(cat docs/sops/SOP-XX-*.md)" \
  --tags "sop,oracle-health,mci"
```

Also publish to SharePoint M&CI Program Operations section after each SOP is complete.
