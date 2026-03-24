# SOP-20: Research → Define → Design → Build Phase Gate
**Owner**: Mike Rodgers, Sr. Director M&CI
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-23
**Category**: Quality & Governance
**Priority**: P2
**Maturity**: Automated (hard-stop enforced) → Documented

---

## 1. Purpose

This Standard Operating Procedure establishes the mandatory phase-gate process governing all major work produced by Oracle Health Marketing & Competitive Intelligence (M&CI). It operationalizes the principle that phases must be completed sequentially — Research before Design, Design before Build — eliminating the rework cycles, quality failures, and credibility risk that result from skipping or compressing phases.

The phase-gate model is grounded in industry-validated methodology. Cooper's Stage-Gate® process demonstrated that organizations enforcing discrete phase transitions reduce project rework by 30–50% and improve first-pass quality scores by 40–60%. The PMBOK® Guide codifies equivalent phase-transition criteria under project lifecycle management. In intelligence and content production specifically, Intelligence Community Directive 203 (Analytic Standards) establishes equivalent "sourced before synthesized, synthesized before published" doctrine that this SOP adapts for a corporate M&CI context.

The hard-stop rule — you cannot advance to Phase N+1 without meeting Phase N exit criteria — is not procedural bureaucracy. It is rework prevention. Every hour of skipped research translates to an average of 4–6 hours of downstream correction once errors surface in deliverables or reach external stakeholders.

---

## 2. Scope and Exemptions

### 2.1 In Scope

This SOP applies to all M&CI work products that meet one or more of the following criteria:

- **Intelligence deliverables**: Competitive briefs, battlecards, domain intelligence reports, win/loss analyses, market assessments, executive summaries
- **Content deliverables**: SharePoint pages, internal knowledge base articles, briefing decks, newsletters, thought leadership pieces
- **Strategic deliverables**: Go-to-market recommendations, positioning documents, messaging frameworks, competitive response playbooks
- **Tooling and automation**: Any new script, workflow, or automated pipeline that produces M&CI outputs
- **Research initiatives**: Any structured investigation with defined deliverables and stakeholders
- **Any work touching more than 3 files or requiring more than 4 hours of total effort**

### 2.2 Explicit Exemptions

| Exemption Type | Definition | Required Documentation |
|---|---|---|
| Bug fix | Correction of a confirmed defect; root cause already diagnosed | Issue log entry |
| Single-file change | Update confined to exactly one document; reversible in 30 minutes | Change log comment |
| Config edit | Modification to a configuration parameter | Inline comment |
| Urgent intelligence update | Time-critical factual correction; approved by M&CI Director | Director approval on record |
| Routine scheduled update | Recurring deliverable with established template and pipeline | Covered by originating project's phase-gate |

**Important**: The "urgent" exemption cannot be used more than twice per calendar month without triggering a process review.

---

## 3. Phase Definitions

### Phase 0 — Research

**Purpose**: Gather all data, source evidence, and contextual intelligence needed to define the problem clearly.

**What happens**: Primary and secondary source identification, competitive data collection, stakeholder consultations, RAG/KB queries, source credibility assessment, confidence tagging, data gap identification, initial hypothesis formation.

**Outputs**: Research log, source citation registry, data gap register, confidence-tagged findings summary, identified open questions.

**Entry Criteria**: Work scope defined at a level sufficient to direct research; at least one stakeholder identified.

**Exit Criteria**:
- All PRIMARY claims have at least one verified source
- Confidence tags assigned to all material findings
- Data gap register complete
- Research log committed to project record
- PRS ≥ 0.85 (or conditional advance documented)

**Hard Stop Triggers**: >30% of intended claims unsourced; critical data gap that would materially alter conclusions; source credibility cannot be assessed for a major input.

---

### Phase 1 — Define

**Purpose**: Translate research findings into a precise problem statement, success criteria, constraints, and audience specification.

**What happens**: Problem statement formulation, audience identification, success criteria definition, constraint identification, stakeholder alignment, key question formulation, non-goals documentation.

**Outputs**: Problem statement, audience profile, success criteria checklist, constraints register, key questions list, non-goals register, stakeholder sign-off record.

**Exit Criteria**:
- Problem statement approved by at least one stakeholder
- Success criteria are specific enough to evaluate at Phase 4
- All key questions are enumerable
- Non-goals are explicit
- PRS ≥ 0.85

**Hard Stop Triggers**: Problem statement contested; success criteria cannot be made measurable; scope is still actively changing.

---

### Phase 2 — Design

**Purpose**: Determine the architecture, structure, format, and approach of the deliverable before any production work begins.

**What happens**: Format selection, structure/outline creation, tone calibration, data visualization design, template selection, review routing plan, resource estimation.

**Outputs**: Annotated outline or wireframe, format decision record, review routing plan, timeline estimate, design approval record.

**Exit Criteria**:
- Outline/wireframe approved by stakeholder or Director
- Format decision is final
- Review routing plan confirmed with reviewers
- PRS ≥ 0.85

**Hard Stop Triggers**: Format or structure still being debated; outline doesn't map to Phase 1 key questions; reviewers haven't confirmed availability.

---

### Phase 3 — Build

**Purpose**: Execute the approved design with production-quality output.

**What happens**: Drafting/coding/analysis per approved outline, inline citation to Phase 0 research log, quality self-review against Phase 1 success criteria, iterative drafts.

**Outputs**: Draft deliverable (complete against outline), self-review checklist, citation index, build notes.

**Exit Criteria**:
- Draft complete against every section in approved outline
- Self-review checklist signed off
- All claims cited to Phase 0 sources
- No structural deviations from approved design (or Design amendment on file)
- PRS ≥ 0.85

**Hard Stop Triggers**: Draft structurally incomplete; new research gaps discovered that alter conclusions; structural changes required not in approved design.

---

### Phase 4 — Test

**Purpose**: Subject the completed draft to structured quality review via the Expert Panel.

**What happens**: Expert Panel review (8-person, min 6 for quorum), fact-check against source citations, scoring, stakeholder preview, revision cycles, final approval.

**Outputs**: Expert Panel scorecard, consolidated revision log, approved final version, Phase 4 approval record.

**Exit Criteria**:
- Expert Panel composite score ≥ 8.5/10.0
- All CRITICAL and HIGH-priority revisions resolved
- Final version approved by M&CI Director
- PRS ≥ 0.85

**Hard Stop Triggers**: Panel score < 7.0; any CRITICAL finding unresolved; stakeholder veto not resolved.

---

### Phase 5 — Deploy

**Purpose**: Publish, distribute, or operationalize the approved deliverable.

**What happens**: Channel preparation, metadata tagging, distribution list confirmation, deployment execution, post-deploy confirmation, archive registration, feedback collection activated.

**Outputs**: Deployment confirmation record, distribution record, archive registration entry, post-deploy feedback ticket.

---

## 4. Transition Criteria

### Phase 0 → Phase 1
| Criterion | Check |
|---|---|
| Research log complete and committed | ✓ / ✗ |
| All material claims have confidence tags | ✓ / ✗ |
| Data gap register finalized | ✓ / ✗ |
| No critical unresolved source credibility issues | ✓ / ✗ |
| PRS[0] ≥ 0.85 | ✓ / ✗ |

### Phase 1 → Phase 2
| Criterion | Check |
|---|---|
| Problem statement approved by stakeholder | ✓ / ✗ |
| Success criteria finalized and measurable | ✓ / ✗ |
| Key questions enumerated | ✓ / ✗ |
| Non-goals documented | ✓ / ✗ |
| PRS[1] ≥ 0.85 | ✓ / ✗ |

### Phase 2 → Phase 3
| Criterion | Check |
|---|---|
| Annotated outline or wireframe approved | ✓ / ✗ |
| Format decision final and recorded | ✓ / ✗ |
| Review routing plan confirmed | ✓ / ✗ |
| PRS[2] ≥ 0.85 | ✓ / ✗ |

### Phase 3 → Phase 4
| Criterion | Check |
|---|---|
| Draft complete against every outline section | ✓ / ✗ |
| Self-review checklist signed off | ✓ / ✗ |
| All claims cited to Phase 0 sources | ✓ / ✗ |
| Expert Panel notified and draft distributed | ✓ / ✗ |
| PRS[3] ≥ 0.85 | ✓ / ✗ |

### Phase 4 → Phase 5
| Criterion | Check |
|---|---|
| Expert Panel composite score ≥ 8.5/10.0 | ✓ / ✗ |
| All CRITICAL and HIGH revisions resolved | ✓ / ✗ |
| M&CI Director final approval on record | ✓ / ✗ |
| Distribution channels confirmed | ✓ / ✗ |
| PRS[4] ≥ 0.85 | ✓ / ✗ |

---

## 5. Approval Authority per Phase

| Phase Close | Approval Authority | Delegation |
|---|---|---|
| Phase 0 close | Work Owner | Self-certifies; no upward approval unless critical data gap |
| Phase 1 close | Work Owner + one Stakeholder | Director approval if stakeholder unavailable |
| Phase 2 close | Work Owner + M&CI Director (or delegate) | Director may delegate to Senior Analyst for standard deliverables |
| Phase 3 close | Work Owner | Self-certification against checklist |
| Phase 4 close | Expert Panel Lead + M&CI Director | Panel Lead certifies score; Director provides final approval |
| Phase 5 close | Work Owner | Self-certification post-deployment; Director notified |

**Approval SLAs**: Standard — 48h. Time-sensitive — 24h. Urgent — 4h (verbal/Slack acceptable).

---

## 6. Hard Stop Rules

### 6.1 Hard Stop Catalog

| Stop Code | Trigger | Resolution Path |
|---|---|---|
| HS-01 | >30% of Phase 0 claims unsourced at Research close | Return to Phase 0; source the gap or downgrade claims |
| HS-02 | Critical data gap discovered that would alter conclusions | Evaluate whether to fill gap or scope out with stakeholder acknowledgment |
| HS-03 | Problem statement contested among stakeholders at Phase 1 close | Facilitate alignment session; document resolution |
| HS-04 | New research gap discovered during Build that alters conclusions | Return to Phase 0 for targeted research |
| HS-05 | Structural change required during Build not in approved Design | Complete a Design Amendment |
| HS-06 | Expert Panel composite score < 7.0 | Full revision cycle; re-enter Phase 3 |
| HS-07 | CRITICAL Expert Panel finding unresolved | Work Owner resolves; panelist sign-off required |
| HS-08 | Deployment channel failure at Phase 5 | Investigate failure; confirm resolution before retry |
| HS-09 | Post-deployment error reported within 24 hours | Immediate triage; rollback if feasible |

### 6.2 Pattern Detection
If any single Hard Stop code triggers more than 3 times in 60 days, the M&CI Director initiates a root-cause review.

---

## 7. Predictive Algorithm: Phase Readiness Score (PRS)

### 7.1 PRS Formula

```
PRS[phase] = (w_d × D) + (w_q × Q) + (w_s × S)

Where:
  D = Deliverable Completeness Score  (0.0–1.0)
  Q = Quality Score                   (0.0–1.0)
  S = Stakeholder Sign-off Score      (0.0–1.0)

Weights:
  w_d = 0.40  (completeness is primary gate)
  w_q = 0.35  (quality is near-equal weight)
  w_s = 0.25  (stakeholder alignment required but tertiary)
```

### 7.2 Component Scoring

**D — Deliverable Completeness**
| Condition | Score |
|---|---|
| All required outputs complete, committed, accessible | 1.0 |
| All required outputs complete; minor formatting gaps | 0.9 |
| One optional output missing; all required complete | 0.85 |
| One required output incomplete but scoped out with rationale | 0.75 |
| One required output missing, no rationale | 0.60 |
| Multiple required outputs missing | ≤ 0.40 |

**Q — Quality Score**

For Phase 0 (Research):
```
Q[0] = (sourced_claims / total_claims) × confidence_factor
  confidence_factor: HIGH=1.0, MEDIUM=0.85, LOW/MIXED=0.70
```

For Phase 1 (Define):
```
Q[1] = (measurable_criteria / total_criteria) × 0.5
     + (key_questions_enumerated / total_questions) × 0.3
     + (non_goals_documented ? 0.2 : 0.0)
```

For Phase 2 (Design):
```
Q[2] = (outline_sections_approved / total_sections) × 0.5
     + (format_decision_final ? 0.25 : 0.0)
     + (review_routing_confirmed ? 0.25 : 0.0)
```

For Phase 3 (Build):
```
Q[3] = (draft_sections_complete / outline_sections) × 0.5
     + (claims_cited / total_claims) × 0.35
     + (self_review_complete ? 0.15 : 0.0)
```

For Phase 4 (Test):
```
Q[4] = (expert_panel_score / 10.0) × 0.6
     + (critical_findings_resolved / critical_findings_total) × 0.4
```

**S — Stakeholder Sign-off**
| Condition | Score |
|---|---|
| All required approvers signed off | 1.0 |
| One approver pending but within SLA | 0.85 |
| One approver overdue; escalation initiated | 0.70 |
| One required approver declined; unresolved | 0.40 |
| Multiple approvers not yet engaged | 0.20 |

### 7.3 PRS Decision Rules

```
PRS ≥ 0.85          → Advance. Log PRS in project record.
PRS 0.65–0.84       → Conditional Advance with documented gap list,
                       remediation plan, and M&CI Director acknowledgment.
PRS < 0.65          → HOLD. Phase is not complete. Return to work.
                       No exceptions without Director written override.
```

---

## 8. Monte Carlo: Rework Cost Modeling

### 8.1 Model Parameters

```
Empirical baselines (PMI Pulse of the Profession, CMMI Institute, Cooper Stage-Gate):

Phase 0 (Research):
  T_phase[0]   = 2–8 hours
  R_prob[0→1]  = 0.72  (72% probability of rework if skipped)
  R_mult[0]    = 4.2   (4.2 rework hours per skipped research hour)

Phase 1 (Define):
  T_phase[1]   = 1–3 hours
  R_prob[1→2]  = 0.65
  R_mult[1]    = 3.1

Phase 2 (Design):
  T_phase[2]   = 1–4 hours
  R_prob[2→3]  = 0.58
  R_mult[2]    = 2.8
```

### 8.2 Expected Rework Cost Formula

```
E[ReworkCost | skip Phase n] = T_phase[n] × R_prob[n→n+1] × R_mult[n] × 1.30
  (1.30 = cascade factor: 30% additional rework in downstream phases)
```

### 8.3 Example Monte Carlo Output

**Scenario**: Skip Phase 0 on a mid-sized competitive brief (T_phase[0] = 4 hours avg)

```
Simulation: N=10,000
  T_phase[0] ~ Uniform(2, 8)
  R_prob[0→1] ~ Beta(7.2, 2.8)
  R_mult[0] ~ LogNormal(μ=1.43, σ=0.25)

Results:
  Mean rework cost:           21.8 hours
  95th percentile:            38.4 hours
  5th percentile:              6.2 hours
  Probability rework > 8h:    0.87
  Phase gate investment cost:  4.0 hours
  Net benefit (avg):          17.8 hours saved
  ROI:                        4.5x
```

---

## 9. Expert Panel Scoring

See SOP-18: 8-Person Weighted Expert Panel Review for full panel methodology.

For phase gate purposes:
- Phase 4 gate: Expert Panel composite ≥ 8.5/10.0
- Quorum: minimum 6 of 8 panelists
- CRITICAL findings: must be resolved before Phase 4 closes

---

## 10. RACI Matrix

| Activity | Work Owner | M&CI Director | Expert Panel | Stakeholders | AI (Jake/Susan) |
|---|---|---|---|---|---|
| Phase 0: Research execution | R | I | — | C | C |
| Phase 0: Confidence tagging | R | I | — | — | C |
| Phase 0→1 close (PRS calc) | R/A | I | — | — | C |
| Phase 1: Problem statement | R | C | — | C | C |
| Phase 1: Stakeholder sign-off | R | A | — | R | — |
| Phase 2: Outline/wireframe | R | C | — | C | C |
| Phase 2: Format decision | R | A | — | C | — |
| Phase 3: Draft production | R | I | — | — | C |
| Phase 3: Self-review | R/A | — | — | — | C |
| Phase 4: Expert Panel review | C | A | R | — | — |
| Phase 4: Finding resolution | R | A | C | C | — |
| Phase 5: Deployment | R | I | — | I | C |
| Phase 5: Archive registration | R/A | I | — | — | — |
| Hard Stop logging | R | A | — | I | — |
| Quarterly pattern review | I | R/A | — | — | — |

---

## 11. KPIs

| KPI | Target | Measurement |
|---|---|---|
| Phase gate compliance rate | >95% | % of eligible deliverables following full phase sequence |
| Hard Stop frequency | <2 per month per stop code | Count per 60-day rolling window |
| Rework rate (post-Deploy) | <10% | % of deployed deliverables requiring post-deploy correction |
| Phase 4 first-pass score | >8.5 avg | Expert Panel composite on first submission |
| Exemption invocation rate | <4/month | Count of urgent exemptions per calendar month |
| Phase 0→1 PRS score (avg) | >0.88 | Rolling 30-day average of Phase 0 PRS |

---

## Appendix A: Phase Gate Quick Reference

```
PHASE   → GATE → PHASE
  0 (Research)  → PRS ≥ 0.85 + research log committed
  1 (Define)    → PRS ≥ 0.85 + stakeholder sign-off
  2 (Design)    → PRS ≥ 0.85 + outline approved
  3 (Build)     → PRS ≥ 0.85 + self-review complete
  4 (Test)      → PRS ≥ 0.85 + panel score ≥ 8.5 + Director approval
  5 (Deploy)    → Deployment confirmed + archive registered
```

## Appendix B: Exemption Log Template

```
Date:           [YYYY-MM-DD]
Work Owner:     [Name]
Exemption Type: [bug fix | single-file | config | urgent | routine]
Deliverable:    [Brief description]
Rationale:      [Why exemption applies]
Approval:       [Director name / N/A]
Outcome:        [Post-delivery quality outcome — fill in after completion]
```
