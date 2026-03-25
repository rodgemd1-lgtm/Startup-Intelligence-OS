# SOP-31: Competitive Intelligence Training & Strategist Onboarding

**Owner**: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-25
**Category**: Sales Enablement — Capability Scaling & Training
**Priority**: P1 — Operational scaling: Mike doing everything → 6/6 strategists self-sufficient
**Maturity**: Gap → Implicit → Documented

---

## Purpose

Oracle Health's M&CI function currently operates as a hub-and-spoke model with Mike Rodgers at the center: every competitive intelligence request, every battlecard update, every deal-specific package, every pricing pull flows through one person. This does not scale. This SOP defines the repeatable process for training strategists and sales team members on CI tools (especially Ellen), market intelligence consumption, battlecard usage, and self-serve competitive research — so that the M&CI function evolves from a single-point-of-failure into a distributed capability.

This is the "teach a person to fish" SOP. SOP-08 defines how to build a battlecard. SOP-29 defines how to produce a deal package. SOP-30 defines how to produce GTM artifacts. This SOP defines how to train other people to consume, apply, and eventually produce competitive intelligence without Mike's direct involvement on every request.

**Why this matters (quantified):**

- Mike Rodgers currently handles ~85% of CI requests directly. At current trajectory, this becomes unsustainable at 30+ requests/quarter. The target operating model requires Mike handling only strategic/novel requests (20-30%), with 6 trained strategists handling standard requests (70-80%).
- Organizations with distributed CI capabilities (Klue benchmark study, 2024) respond 3x faster to competitive threats than centralized models. Speed is a competitive advantage in itself.
- Strategists who complete structured CI onboarding produce output rated 40% higher by sales teams compared to strategists who learn informally (Crayon CI Maturity Study, 2024).
- The Ellen AI platform represents a $200K+ annual investment. If only Mike uses it effectively, the ROI is a fraction of what it should be. Target: 6/6 strategists able to run Ellen queries independently by Q3.

**What this SOP produces:**

| Output | Audience | Cadence |
|--------|----------|---------|
| Ellen Onboarding Curriculum (3-session series) | New strategists | Per new hire / quarterly for refreshers |
| Self-Serve Research Training Module | Strategists, senior AEs | Quarterly |
| Battlecard Usage Training | AEs, SEs | Per battlecard launch + quarterly refresh |
| CI Skill Assessment | All strategists | Quarterly |
| Adoption & Proficiency Dashboard | Mike Rodgers, GTM Leadership | Monthly |
| Hub-and-Spoke Transition Tracker | Mike Rodgers | Monthly |

---

## Scope

### In Scope

- All CI training and onboarding activities for Oracle Health M&CI strategists
- Sales team training on consuming and applying competitive intelligence (battlecards, pricing, deal packages)
- Ellen AI platform onboarding and proficiency development
- Self-serve research skill development for strategists
- Ongoing skill development and certification tracking
- Adoption metrics and proficiency measurement
- Hub-and-Spoke operating model transition management

### Out of Scope

- Ellen platform administration and technical configuration (IT / Vendor)
- Sales methodology training (Sales Enablement — separate program)
- Product training (Product Marketing)
- Third-party CI tool procurement decisions
- Hiring and performance management of strategists (HR / Mike as manager)

---

## ARCHITECTURE: CI Training & Scaling System

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: ONBOARDING — ELLEN AI PLATFORM (3-Session Series)             │
│  Session 1: Foundations (2 hrs) — CI concepts, Ellen basics, first query│
│  Session 2: Applied Research (2 hrs) — Multi-source, confidence tagging │
│  Session 3: Production (2 hrs) — Deal support, artifact contribution    │
│  Certification: Pass practical exam to earn "Ellen Certified" status   │
├─────────────────────────────────────────────────────────────────────────┤
│  PHASE 2: SELF-SERVE RESEARCH TRAINING                                  │
│  Source hierarchy mastery (SOP-05/08/10 source tiers)                  │
│  Confidence tagging practicum                                          │
│  Research workflow: question → sources → synthesis → confidence → output│
│  Peer review protocol for strategist-produced research                 │
├─────────────────────────────────────────────────────────────────────────┤
│  PHASE 3: BATTLECARD & DEAL INTELLIGENCE TRAINING (Sales-Facing)        │
│  For AEs: How to read and use a battlecard in 60 seconds               │
│  For SEs: Demo differentiation and technical objection handling        │
│  For Deal Desk: Pricing intelligence consumption and deal sizing       │
│  For all: When to request deal-specific support (SOP-29 triggers)     │
├─────────────────────────────────────────────────────────────────────────┤
│  PHASE 4: ONGOING SKILL DEVELOPMENT                                     │
│  Monthly CI office hours (open Q&A with Mike)                          │
│  Quarterly skill assessments (practical + knowledge)                   │
│  Peer learning: strategist-led brown bag sessions                      │
│  Competitive event rapid-response exercises (simulated drills)         │
├─────────────────────────────────────────────────────────────────────────┤
│  PHASE 5: ADOPTION TRACKING & HUB-AND-SPOKE TRANSITION                 │
│  Measure: % of standard requests handled without Mike                  │
│  Measure: Ellen query volume and quality by strategist                 │
│  Measure: Strategist-produced output quality scores                    │
│  Target: 6/6 strategists self-sufficient by Q3                        │
│  Target: Hub-and-Spoke model operational by Q4                        │
└─────────────────────────────────────────────────────────────────────────┘
        │                                                       │
        ▼                                                       ▼
┌───────────────────┐                               ┌─────────────────────┐
│  PROFICIENCY       │                               │  PREDICTIVE MODEL   │
│  DASHBOARD         │                               │  Self-Sufficiency   │
│  Per Strategist    │                               │  Timeline Forecast  │
│  Per Skill Area    │                               │  by Strategist      │
└───────────────────┘                               └─────────────────────┘
```

---

## Phase 1: Ellen AI Onboarding Curriculum (3-Session Series)

### 1.1 Prerequisite Requirements

Before entering the Ellen onboarding series, each strategist must:

```
ELLEN ONBOARDING PREREQUISITES

[ ] Has Oracle Health SSO access and Ellen platform credentials
[ ] Has read SOP-05 (Intelligence Source Management) — sections 1-4
[ ] Has read SOP-08 (Battlecard Creation) — sections 1-3
[ ] Has reviewed at least 2 active battlecards in the CI library
[ ] Has access to Salesforce competitive deal reports
[ ] Has joined Slack channels: #intel-request, #intel-updates, #ci-team
[ ] Has been assigned a CI mentor (Mike or senior strategist)
[ ] Has scheduled all 3 sessions in their calendar
```

### 1.2 Session 1: Foundations (2 Hours)

**Objective:** Strategist can navigate Ellen, execute a basic query, and interpret results with confidence tagging.

**Agenda:**

| Time | Topic | Format | Facilitator |
|------|-------|--------|-------------|
| 0:00-0:20 | CI at Oracle Health: mission, SOPs, operating model | Lecture + Q&A | Mike Rodgers |
| 0:20-0:40 | Ellen platform overview: interface, data sources, capabilities | Screen share demo | Mike Rodgers |
| 0:40-1:00 | Guided query: Run a competitive query on Epic together | Hands-on paired exercise | Mike + strategist |
| 1:00-1:20 | Interpreting results: source attribution, confidence tagging | Lecture + live examples | Mike Rodgers |
| 1:20-1:40 | Independent exercise: Run 3 queries on assigned competitor | Hands-on solo | Strategist (Mike observes) |
| 1:40-2:00 | Review exercise outputs, Q&A, assign homework | Discussion | Mike Rodgers |

**Session 1 Homework:**
- Run 5 Ellen queries on their assigned competitor
- For each query: document the question, top 3 results, and a confidence assessment
- Submit homework via Slack DM to Mike within 3 business days
- Mike reviews and provides written feedback before Session 2

**Session 1 Success Criteria:**
- [ ] Can log into Ellen and navigate the interface independently
- [ ] Can formulate a competitive intelligence query
- [ ] Can execute a query and retrieve results
- [ ] Can identify source attribution on query results
- [ ] Can assign a preliminary confidence tag (VERIFIED / INFERRED / ESTIMATED)

### 1.3 Session 2: Applied Research (2 Hours)

**Objective:** Strategist can conduct multi-source research using Ellen + supplementary sources and produce a confidence-tagged intelligence brief.

**Prerequisite:** Session 1 homework reviewed and accepted by Mike.

**Agenda:**

| Time | Topic | Format | Facilitator |
|------|-------|--------|-------------|
| 0:00-0:15 | Homework review: what worked, common mistakes | Group discussion | Mike Rodgers |
| 0:15-0:35 | Multi-source research: Ellen + SEC filings + KLAS + press | Lecture + demo | Mike Rodgers |
| 0:35-0:55 | Source hierarchy deep dive: Tier 1/2/3 sources per SOP-05 | Lecture + examples | Mike Rodgers |
| 0:55-1:25 | Practicum: Produce a 1-page intel brief on [assigned competitor topic] | Hands-on solo | Strategist |
| 1:25-1:50 | Peer review: exchange briefs with another strategist, provide feedback | Paired exercise | Strategists |
| 1:50-2:00 | Mike reviews both briefs, models quality feedback | Group | Mike Rodgers |

**Session 2 Homework:**
- Produce a complete 2-page intelligence brief on an assigned topic
- Must include: 5+ Ellen queries, 2+ supplementary sources, confidence tagging on every claim
- Must follow the intelligence brief template (provided at session)
- Submit within 5 business days
- Mike reviews and scores using the quality rubric (Section 1.6)

**Session 2 Success Criteria:**
- [ ] Can conduct multi-source research (Ellen + 2 other source types)
- [ ] Can cross-reference Ellen output against supplementary sources
- [ ] Can produce a confidence-tagged intelligence brief
- [ ] Can provide constructive peer review on another strategist's output
- [ ] Understands when to escalate (data conflicts, low confidence, novel competitor)

### 1.4 Session 3: Production (2 Hours)

**Objective:** Strategist can contribute to real M&CI outputs — deal support, battlecard updates, and GTM artifacts — with appropriate quality and review protocols.

**Prerequisite:** Session 2 homework scored ≥7.0/10 on quality rubric.

**Agenda:**

| Time | Topic | Format | Facilitator |
|------|-------|--------|-------------|
| 0:00-0:15 | Session 2 homework debrief | Group discussion | Mike Rodgers |
| 0:15-0:35 | Production workflows: SOP-08 (battlecard), SOP-29 (deal package), SOP-30 (GTM artifact) | Lecture | Mike Rodgers |
| 0:35-0:55 | Live exercise: Produce a Tier 1 Quick Brief (SOP-29) for a simulated deal | Hands-on solo | Strategist |
| 0:55-1:15 | Live exercise: Draft an update to one section of an active battlecard | Hands-on solo | Strategist |
| 1:15-1:35 | Quality gate simulation: Submit both outputs for peer + Mike review | Paired + Mike | All |
| 1:35-1:50 | Review results, discuss production standards and handoff expectations | Group | Mike Rodgers |
| 1:50-2:00 | Certification exam overview + schedule | Logistics | Mike Rodgers |

**Session 3 Success Criteria:**
- [ ] Can produce a Tier 1 Quick Brief that meets SOP-29 quality standards
- [ ] Can draft a battlecard section update that meets SOP-08 quality standards
- [ ] Understands the review/approval workflow for each production type
- [ ] Knows when to handle independently vs. when to escalate to Mike
- [ ] Ready for certification exam

### 1.5 Certification Exam

The Ellen Certification Exam is a practical assessment conducted within 2 weeks of Session 3 completion.

**Exam Structure:**

| Component | Weight | Format | Time Limit |
|-----------|--------|--------|-----------|
| Ellen Query Practical | 30% | Execute 5 queries, produce confidence-tagged results | 45 minutes |
| Intelligence Brief | 35% | Produce a 2-page brief on assigned topic using Ellen + sources | 90 minutes |
| Deal Support Simulation | 25% | Produce a Tier 1 Quick Brief for a simulated competitive deal | 30 minutes |
| Oral Review | 10% | 15-minute discussion with Mike on research decisions and confidence calls | 15 minutes |

**Scoring:**
- Each component scored 1-10 by Mike Rodgers
- Weighted composite must be ≥7.5/10 to earn "Ellen Certified" status
- If score is 6.0-7.4: remediation plan created, re-exam in 2 weeks
- If score is <6.0: repeat Session 2 and Session 3 before re-exam

**Certification Status:**

| Status | Definition | Permissions |
|--------|-----------|-------------|
| **Not Started** | Has not begun onboarding | No independent CI work |
| **In Training** | Currently in Session 1-3 series | Supervised CI work only |
| **Ellen Certified** | Passed certification exam ≥7.5 | Independent Tier 1 work, supervised Tier 2 |
| **CI Proficient** | 3+ months of certified work, ≥8.0 quality average | Independent Tier 1-2 work, supervised Tier 3 |
| **CI Expert** | 6+ months, ≥8.5 quality average, mentoring others | Full independence, can supervise new strategists |

### 1.6 Quality Rubric for Strategist Output

All strategist-produced CI output is scored against this rubric:

| Dimension | Weight | 9-10 (Excellent) | 7-8 (Good) | 5-6 (Needs Work) | 1-4 (Unacceptable) |
|-----------|--------|-----------------|------------|-------------------|-------------------|
| **Accuracy** | 25% | All claims verified, zero errors | Minor inference gaps, no factual errors | Some claims unsubstantiated | Factual errors present |
| **Confidence Tagging** | 20% | Every claim tagged, tags are correct | Most claims tagged, rare mis-tags | Inconsistent tagging | No tagging or systematic mis-tags |
| **Source Quality** | 20% | 3+ sources, Tier 1-2 dominant | 2+ sources, mix of tiers | Single source reliance | No source citation |
| **Actionability** | 20% | Sales team can use immediately | Minor interpretation needed | Significant rework to be usable | Not usable without full rewrite |
| **Timeliness** | 15% | Delivered within SLA | Delivered within 120% of SLA | Delivered late but usable | Missed SLA entirely |

---

## Phase 2: Self-Serve Research Training

### 2.1 Research Skill Modules

Beyond Ellen-specific training, strategists need broader research skills. These are delivered as standalone modules (60-90 minutes each) that can be taken in any order after Ellen Certification.

**Module R1: Source Hierarchy Mastery**
- Deep dive into SOP-05 source tiers
- Practical: classify 20 source examples by tier and confidence
- Assessment: source classification quiz (≥80% to pass)

**Module R2: Competitive Signal Detection**
- How to monitor: earnings calls, press releases, job postings, patent filings, social media
- Tools: Google Alerts, LinkedIn, SEC EDGAR, Ellen monitoring features
- Practical: set up monitoring for assigned competitor, produce 1 week of signal summary
- Assessment: signal summary quality review by Mike

**Module R3: Synthesis & Triangulation**
- How to combine multiple sources into a confidence-tagged claim
- Composite confidence calculation (per SOP-10 §5.3)
- Handling conflicting sources: escalation vs. parallel reporting
- Practical: given 5 sources with conflicting claims, produce a synthesis memo
- Assessment: synthesis memo quality review by Mike

**Module R4: Research Workflow Automation**
- Saved Ellen queries and automated monitoring
- Salesforce report configuration for competitive intelligence
- Template usage: standardized output formats for efficiency
- Practical: automate 3 recurring research tasks for assigned competitor

### 2.2 Self-Serve Readiness Levels

| Level | Definition | Criteria | Typical Timeline |
|-------|-----------|----------|-----------------|
| L0: Dependent | Cannot perform CI research independently | Pre-training | — |
| L1: Guided | Can research with step-by-step guidance | Post-Session 1 | Week 1-2 |
| L2: Supervised | Can research independently, outputs reviewed before use | Ellen Certified | Month 1-2 |
| L3: Independent | Can research and produce standard outputs independently | CI Proficient + Modules R1-R3 | Month 3-4 |
| L4: Autonomous | Can handle novel research, mentor others, improve processes | CI Expert + Module R4 | Month 6+ |

---

## Phase 3: Battlecard & Deal Intelligence Training (Sales-Facing)

### 3.1 AE Battlecard Usage Training

**Format:** 45-minute session, delivered quarterly and at every new battlecard launch
**Audience:** All AEs in competitive segments
**Facilitator:** CI Analyst or certified strategist

**Curriculum:**

| Module | Duration | Content |
|--------|----------|---------|
| Why Battlecards Exist | 5 min | Win rate data, quick success stories |
| Anatomy of a Battlecard | 10 min | Walk through each section, what to use when |
| The 60-Second Drill | 10 min | How to scan a battlecard in 60 seconds before a prospect call |
| Objection Role Play | 10 min | Live practice: trainer plays prospect, AE uses battlecard to respond |
| When to Call for Backup | 5 min | SOP-29 triggers: how and when to request deal-specific support |
| Q&A | 5 min | Open questions |

**Post-Training Assessment:**
- 5-question quiz delivered via LMS within 48 hours
- Questions test: battlecard navigation, objection response, escalation triggers
- Target: ≥80% pass rate on first attempt

### 3.2 SE Demo Differentiation Training

**Format:** 60-minute session, delivered per competitor and at demo intelligence brief launches
**Audience:** All SEs in competitive segments
**Facilitator:** Mike Rodgers or CI Analyst + SE Manager

**Curriculum:**

| Module | Duration | Content |
|--------|----------|---------|
| Competitor Demo Playbook Review | 15 min | What the competitor shows, their narrative, their strengths |
| Oracle Health Demo Differentiation Plays | 15 min | Where to create separation, what to emphasize |
| Live Demo Walkthrough | 20 min | SE demonstrates recommended demo flow, group critique |
| Prospect Questions Strategy | 10 min | Questions that expose competitor weaknesses in demo context |

### 3.3 Deal Desk CI Consumption Training

**Format:** 30-minute session, delivered quarterly
**Audience:** Deal Desk team
**Facilitator:** Mike Rodgers

**Curriculum:**
- Pricing intelligence workbook navigation (SOP-10 output)
- Confidence levels and what they mean for deal sizing
- When to request a deal-specific pricing memo
- How to interpret Monte Carlo discount band outputs

---

## Phase 4: Ongoing Skill Development

### 4.1 Monthly CI Office Hours

- **Format:** 60-minute open session, first Thursday of each month
- **Host:** Mike Rodgers
- **Audience:** All strategists + any sales team members who want to attend
- **Agenda:** Open Q&A, recent competitive developments, strategist questions on active work, technique sharing
- **Recording:** Sessions recorded and posted to CI team SharePoint for async viewing

### 4.2 Quarterly Skill Assessment

Every certified strategist undergoes a quarterly skill assessment:

```
QUARTERLY CI SKILL ASSESSMENT

Strategist: _______________
Assessment Period: Q[X] 2026
Assessor: Mike Rodgers

1. ELLEN PROFICIENCY (scored 1-10)
   - Query quality (specificity, relevance): ___
   - Output interpretation accuracy: ___
   - Advanced feature utilization: ___

2. RESEARCH QUALITY (scored 1-10)
   - Source diversity (# of source types used): ___
   - Confidence tagging accuracy: ___
   - Synthesis quality (triangulation, conflict resolution): ___

3. PRODUCTION OUTPUT (scored 1-10)
   - Volume: # of deliverables produced this quarter: ___
   - Quality: average quality score per rubric (Section 1.6): ___
   - Timeliness: % delivered within SLA: ___

4. INDEPENDENCE LEVEL (scored 1-10)
   - % of work completed without Mike's involvement: ___
   - Escalation appropriateness: ___
   - Novel situation handling: ___

COMPOSITE SCORE: ___ / 10 (weighted average)
PROFICIENCY LEVEL: [Not Started / In Training / Certified / Proficient / Expert]
RECOMMENDED ACTIONS: _______________
NEXT ASSESSMENT: _______________
```

### 4.3 Competitive Rapid-Response Drills

Quarterly simulation exercises that test the team's ability to respond to competitive events:

**Drill Format:**
1. Mike announces a simulated competitive event (e.g., "Epic just announced a new AI module at HIMSS")
2. Each strategist independently produces a response deliverable within the drill SLA:
   - Tier 1 drill: 2-hour SLA for a Quick Brief
   - Tier 2 drill: 8-hour SLA for a battlecard update recommendation
3. Outputs are peer-reviewed and scored
4. Debrief session: what worked, what broke, what to improve

**Drill Calendar:** One drill per quarter, rotating through Tier 1, Tier 2, and Tier 3 scenarios.

### 4.4 Peer Learning Program

- **Brown Bag Sessions:** Each certified strategist presents one topic per quarter to the CI team (30 minutes)
- **Mentorship Pairs:** New strategists paired with CI Proficient/Expert strategists for first 3 months
- **Research Showcases:** Best research of the quarter presented at GTM leadership meeting

---

## Phase 5: Adoption Tracking & Hub-and-Spoke Transition

### 5.1 Hub-and-Spoke Operating Model Definition

**Current State (Hub-and-Spoke v0):**
- Mike = Hub (handles 85% of CI requests)
- Strategists = Spokes (handle overflow, with supervision)
- All quality review flows through Mike
- Single point of failure

**Target State (Hub-and-Spoke v1.0 — Q3 target):**
- Mike = Hub (handles 20-30% of requests — novel, strategic, Tier 3 War Room)
- 6 Certified Strategists = Spokes (handle 70-80% of standard requests independently)
- Peer review replaces Mike review for Tier 1 work
- Mike reviews Tier 2 and approves Tier 3
- Any strategist can handle a Tier 1 Quick Brief independently

**Target State (Hub-and-Spoke v2.0 — Q4+ target):**
- Mike = Strategic CI Director (handles Tier 3 War Room, GTM strategy, program development)
- 2-3 CI Experts = Senior Spokes (handle Tier 2, supervise Tier 1, mentor new strategists)
- 3-4 CI Proficient Strategists = Standard Spokes (handle Tier 1 independently, contribute to Tier 2)
- Peer review + Senior Spoke review for all non-Tier-3 work

### 5.2 Transition Milestones

| Milestone | Definition | Target Date | Measurement |
|-----------|-----------|-------------|-------------|
| M1: All Strategists in Training | 6/6 strategists have completed Session 1 | End of Q1 | Training log |
| M2: First Certifications | 3/6 strategists Ellen Certified | End of Q1+6 weeks | Certification log |
| M3: Full Certification | 6/6 strategists Ellen Certified | End of Q2 | Certification log |
| M4: Independent Tier 1 | 4/6 strategists handling Tier 1 independently | Mid-Q3 | Request routing log |
| M5: Proficiency | 3/6 strategists at CI Proficient level | End of Q3 | Quarterly assessment |
| M6: Hub-and-Spoke v1.0 Operational | Mike handling <30% of standard requests | End of Q3 | Request routing log |
| M7: Expert Development | 2/6 strategists at CI Expert level | End of Q4 | Quarterly assessment |
| M8: Hub-and-Spoke v2.0 Operational | Senior Spoke layer functioning | End of Q4 | Operating model audit |

### 5.3 Monthly Transition Dashboard

```
HUB-AND-SPOKE TRANSITION DASHBOARD — [Month] [Year]

STRATEGIST STATUS:
| Strategist | Ellen Status | Proficiency Level | Self-Serve Level | Q Score |
|-----------|-------------|-------------------|-----------------|---------|
| [Name 1]  | Certified   | Proficient        | L3 Independent  | 8.2     |
| [Name 2]  | Certified   | Certified         | L2 Supervised   | 7.6     |
| [Name 3]  | In Training | In Training       | L1 Guided       | —       |
| [Name 4]  | Certified   | Certified         | L2 Supervised   | 7.8     |
| [Name 5]  | In Training | In Training       | L1 Guided       | —       |
| [Name 6]  | Not Started | Not Started       | L0 Dependent    | —       |

REQUEST ROUTING:
| Request Type | Mike Handled | Strategist Handled | Target (Strategist) |
|-------------|-------------|-------------------|-------------------|
| Tier 1 Quick Brief | [N] ([%]) | [N] ([%]) | 80% strategist |
| Tier 2 Standard | [N] ([%]) | [N] ([%]) | 50% strategist |
| Tier 3 War Room | [N] ([%]) | [N] ([%]) | 0% strategist (Mike only) |
| Battlecard Update | [N] ([%]) | [N] ([%]) | 70% strategist |
| Ellen Query (standalone) | [N] ([%]) | [N] ([%]) | 90% strategist |

QUALITY METRICS:
| Metric | This Month | Last Month | Trend |
|--------|-----------|-----------|-------|
| Avg Strategist Quality Score | [X.X] | [X.X] | ↑/↓/→ |
| SLA Compliance (strategist-led) | [X%] | [X%] | ↑/↓/→ |
| Escalation Rate (to Mike) | [X%] | [X%] | ↓ is good |
| Rep NPS on Strategist Output | [X.X] | [X.X] | ↑/↓/→ |

MILESTONE STATUS: [M1-M8 tracker with dates]
NEXT ACTIONS: _______________
```

---

## RACI Matrix

| Activity | CI Lead (Mike) | CI Analyst / Strategist | Sales Enablement | SE Manager | Deal Desk | HR |
|----------|---------------|------------------------|-----------------|-----------|-----------|-----|
| Onboarding curriculum design | **R/A** | C | C | C | C | — |
| Ellen Session 1-3 facilitation | **R** | I (attendee) | — | — | — | — |
| Homework review & feedback | **R/A** | **R** (submitter) | — | — | — | — |
| Certification exam administration | **R/A** | **R** (examinee) | — | — | — | — |
| Certification status tracking | **R/A** | I | I | I | I | I |
| Self-serve module delivery | **R/A** | **R** (participant) | — | — | — | — |
| AE battlecard training delivery | A | **R** (if certified) | C | — | — | — |
| SE demo differentiation training | **R** | C | — | **R** (co-facilitator) | — | — |
| Deal Desk CI training delivery | **R** | C | — | — | I | — |
| Monthly office hours facilitation | **R** | **R** (participant) | I | I | I | — |
| Quarterly skill assessment | **R/A** | **R** (assessed) | — | — | — | — |
| Rapid-response drill design | **R/A** | C | — | — | — | — |
| Rapid-response drill execution | A | **R** (participant) | — | — | — | — |
| Peer learning program coordination | A | **R** (presenters) | — | — | — | — |
| Transition dashboard production | **R/A** | C | I | I | I | — |
| Hub-and-spoke model decisions | **R/A** | C | I | I | I | C |
| SOP update | **R/A** | C | I | I | I | — |

**Key:** R = Responsible, A = Accountable, C = Consulted, I = Informed

### Escalation Path

| Situation | Escalate To | Timeline |
|-----------|------------|---------|
| Strategist fails certification exam twice | Mike Rodgers + HR (performance concern) | After second failure |
| Strategist quality score drops below 6.0 for 2 consecutive quarters | Mike Rodgers (remediation plan) | At quarterly assessment |
| Sales team training attendance <50% | Sales VP | Within 1 week of session |
| Hub-and-spoke transition milestone missed | Mike Rodgers + GTM Leadership | At monthly dashboard review |
| Strategist-produced output causes deal issue (inaccurate intel) | Mike Rodgers (immediate review) | Within 24 hours |
| Ellen platform access or functionality issue | IT + Ellen vendor support | Within 4 hours |

---

## KPIs

### Training Delivery KPIs

| KPI | Description | Target | Measurement |
|-----|-------------|--------|-------------|
| **Onboarding Completion Rate** | % of strategists completing 3-session series within 6 weeks of start | 100% | Training log |
| **Certification Pass Rate** | % of strategists passing certification exam on first attempt | ≥80% | Certification log |
| **Time to Certification** | Average weeks from Session 1 to certification | ≤8 weeks | Training log |
| **Sales Training Coverage** | % of AEs who attend battlecard training at least once per year | ≥75% | LMS records |
| **SE Training Coverage** | % of SEs who attend demo differentiation training per competitor | ≥80% | Training log |

### Proficiency Development KPIs

| KPI | Description | Target | Measurement |
|-----|-------------|--------|-------------|
| **Average Strategist Quality Score** | Mean quality rubric score across all strategists | ≥7.5/10 | Quarterly assessment |
| **Proficiency Level Distribution** | # of strategists at each level (Certified / Proficient / Expert) | 6/6 Certified by Q2, 3/6 Proficient by Q3 | Quarterly assessment |
| **Ellen Query Quality** | Average relevance score of strategist Ellen queries (Mike-rated) | ≥7.0/10 | Monthly Ellen usage review |
| **Research Module Completion** | % of certified strategists completing all 4 research modules | ≥80% by Q3 | Module log |
| **Drill Performance** | Average score on quarterly rapid-response drill | ≥7.0/10 | Drill log |

### Hub-and-Spoke Transition KPIs

| KPI | Description | Target | Measurement |
|-----|-------------|--------|-------------|
| **Mike's Request Share** | % of standard CI requests handled directly by Mike | ≤30% by Q3 | Request routing log |
| **Strategist Independence Rate** | % of strategist-produced Tier 1 outputs requiring no Mike revision | ≥80% by Q3 | Quality gate log |
| **Self-Serve Resolution Rate** | % of standard CI requests handled without M&CI direct involvement | ≥20% by Q3, ≥40% by Q4 | Request log |
| **Escalation Appropriateness** | % of strategist escalations that Mike agrees were necessary | ≥90% | Escalation review |
| **Transition Milestone Adherence** | % of M1-M8 milestones hit on schedule | ≥75% | Monthly dashboard |

### Business Impact KPIs

| KPI | Description | Target | Measurement |
|-----|-------------|--------|-------------|
| **Response Time Improvement** | Average response time for Tier 1 requests (current vs. baseline) | 30% faster by Q3 | Request log |
| **CI Capacity Utilization** | Total CI deliverables produced per quarter (all producers) | ≥150% of current baseline | Production log |
| **Rep Satisfaction with CI** | AE/SE NPS on CI support quality | ≥8.0/10 (maintain or improve) | Quarterly survey |
| **Ellen ROI** | Ellen queries per month across all users / Ellen annual cost | ≥50 queries/month by Q3 | Ellen usage analytics |
| **Knowledge Retention** | % of certified strategists still active and producing after 6 months | ≥90% | HR + training log |

---

## Appendix A: Strategist Onboarding Checklist (Week 1-8)

```
WEEK 1:
[ ] Complete prerequisites (accounts, reading, channel access)
[ ] Meet CI mentor
[ ] Attend Session 1: Foundations
[ ] Begin Session 1 homework (5 Ellen queries)

WEEK 2:
[ ] Submit Session 1 homework
[ ] Receive Mike's feedback
[ ] Shadow Mike on 1 live CI request

WEEK 3:
[ ] Attend Session 2: Applied Research
[ ] Begin Session 2 homework (2-page intel brief)

WEEK 4:
[ ] Submit Session 2 homework
[ ] Receive Mike's feedback and score
[ ] Begin self-study: SOP-05, SOP-10 relevant sections

WEEK 5:
[ ] Attend Session 3: Production
[ ] Begin certification exam preparation
[ ] Shadow Mike on 1 deal-specific package (SOP-29)

WEEK 6:
[ ] Take certification exam
[ ] Receive results and feedback

WEEK 7-8 (if certified):
[ ] Handle first supervised Tier 1 Quick Brief
[ ] Attend first Monthly CI Office Hours
[ ] Begin Module R1: Source Hierarchy Mastery
[ ] Schedule first quarterly skill assessment

WEEK 7-8 (if not certified):
[ ] Complete remediation plan
[ ] Retake relevant sessions
[ ] Schedule re-exam for Week 8-9
```

## Appendix B: Cross-SOP Training Dependencies

| SOP | Training Touchpoint | Audience |
|-----|-------------------|----------|
| SOP-05 (Source Management) | Module R1: Source Hierarchy Mastery | Strategists |
| SOP-08 (Battlecards) | Session 3 + AE Battlecard Usage Training | Strategists + AEs |
| SOP-09 (Win/Loss) | Module R3: Synthesis & Triangulation | Strategists |
| SOP-10 (Pricing) | Deal Desk CI Training + Module R1 | Strategists + Deal Desk |
| SOP-29 (Deal Packages) | Session 3 + ongoing production supervision | Strategists |
| SOP-30 (GTM Artifacts) | Post-certification artifact contribution | Strategists (CI Proficient+) |

---

**End of SOP-31**
