# SOP-29: Deal-Specific Competitive Positioning Package

**Owner**: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-25
**Category**: Sales Enablement — Competitive Intelligence Production
**Priority**: P1 — Direct revenue impact on active competitive deals
**Maturity**: Gap → Implicit → Documented

---

## Purpose

When a sales rep is in an active competitive deal, generic battlecards are not enough. The deal has a specific buyer, a specific competitor positioning narrative, a specific set of objections the prospect is hearing, and a specific price point being offered. This SOP defines how Oracle Health's M&CI function produces a **deal-specific intelligence package** — turning the general competitive intelligence library (battlecards per SOP-08, pricing intel per SOP-10, win/loss patterns per SOP-09) into targeted ammunition that is calibrated to a single deal.

**Why this matters (quantified):**

- Generic battlecards cover ~70% of competitive scenarios. The remaining 30% — buyer-specific positioning, deal-specific pricing dynamics, prospect pain points mapped to competitor weaknesses — is where deals are won or lost.
- Internal data from SOP-09 win/loss interviews shows that deals where reps received deal-specific competitive preparation had a **12-18 percentage point higher win rate** than deals fought with standard enablement materials alone.
- The average Oracle Health enterprise deal exceeds $5M TCV. A 15-point win rate improvement on even 10 competitive deals per quarter represents tens of millions in incremental bookings.
- Speed matters: competitive positioning packages delivered before the vendor shortlist meeting outperform packages delivered after by 2:1 on influence rating (rep survey, Q4 2025).

**What this SOP produces:**

| Output | Audience | Delivery SLA |
|--------|----------|-------------|
| Quick Brief (Tier 1) | AE, Deal Desk | 4 hours |
| Standard Positioning Package (Tier 2) | AE, SE, Deal Desk | 24 hours |
| War Room Package (Tier 3) | Full deal team, Sales VP | 48 hours |

---

## Scope

### In Scope

- All deal-specific competitive intelligence requests from Oracle Health sales teams
- Active deals where a named competitor is confirmed in the evaluation
- Deal sizes: >$2M TCV (Tier 1), >$5M TCV (Tier 2), >$10M TCV or strategic account (Tier 3)
- Competitors: Any competitor in the Oracle Health tracked set (Epic, Meditech, Waystar, R1 RCM, FinThrive, Nuance DAX, and pipeline entrants per SOP-08)
- Outputs: positioning narratives, objection prep sheets, pricing intelligence pulls, demo differentiation notes, risk assessments
- Cross-references: SOP-08 (battlecards), SOP-09 (win/loss), SOP-10 (pricing), SOP-06 (competitive landscape)

### Out of Scope

- General battlecard creation or maintenance (SOP-08)
- Prospect-facing competitive collateral (Product Marketing)
- Deal pricing strategy or discount approval (Deal Desk / Finance)
- RFP response writing (Sales Operations)
- Post-deal win/loss analysis (SOP-09 — though findings feed back into this SOP)

---

## ARCHITECTURE: Deal Intelligence Delivery System

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: DEAL INTAKE & TRIAGE                                          │
│  Channels: Slack #intel-request | Salesforce CI flag | Deal Desk ref    │
│  SLA clock starts at intake acknowledgment                              │
│  Tier assignment: Quick Brief (4hr) | Standard (24hr) | War Room (48hr)│
├─────────────────────────────────────────────────────────────────────────┤
│  PHASE 2: INTELLIGENCE ASSEMBLY                                         │
│  Battlecard pull (SOP-08) → Deal-specific overlay                      │
│  Pricing pull (SOP-10) → Deal-size-adjusted guidance                   │
│  Win/Loss pattern matching (SOP-09) → Look-alike deal analysis         │
│  Prospect research → Buyer priorities, current vendor pain points      │
│  Competitor positioning narrative → Tailored to this deal's dynamics   │
├─────────────────────────────────────────────────────────────────────────┤
│  PHASE 3: POSITIONING & NARRATIVE CONSTRUCTION                          │
│  Deal-specific positioning statement (3-sentence framework)            │
│  Objection matrix with deal-context responses                          │
│  Demo differentiation notes (what to show, what to avoid)              │
│  Pricing intelligence with deal-size comparisons                       │
│  Risk assessment: Where can this deal go wrong?                        │
├─────────────────────────────────────────────────────────────────────────┤
│  PHASE 4: QUALITY GATE & DELIVERY                                       │
│  Tier 1 (Quick Brief): Self-review → deliver                          │
│  Tier 2 (Standard): Peer review → CI Lead sign-off → deliver          │
│  Tier 3 (War Room): Full team review → Mike sign-off → live briefing  │
├─────────────────────────────────────────────────────────────────────────┤
│  PHASE 5: DEAL OUTCOME TRACKING                                         │
│  Package tagged to Salesforce Opportunity ID                           │
│  Win/loss outcome tracked → feeds effectiveness measurement            │
│  Rep feedback captured within 5 days of deal close                     │
└─────────────────────────────────────────────────────────────────────────┘
        │                                                       │
        ▼                                                       ▼
┌───────────────────┐                               ┌─────────────────────┐
│  WIN RATE DELTA   │                               │  PREDICTIVE MODEL   │
│  Package vs. No   │                               │  Deal Risk Score    │
│  Package deals    │                               │  P10/P50/P90 bands  │
└───────────────────┘                               └─────────────────────┘
```

---

## Phase 1: Deal Intake & Triage

### 1.1 Intake Channels

Deal-specific intelligence requests are accepted through three channels:

**Channel A — Slack #intel-request (primary)**
- Rep or Deal Desk posts in #intel-request with deal context
- M&CI analyst acknowledges within 30 minutes during business hours (8am-6pm ET)
- Acknowledgment starts the SLA clock

**Channel B — Salesforce CI Flag**
- AE sets the "Competitive Intelligence Requested" flag on the Opportunity record
- Automated notification triggers to M&CI Slack channel
- Analyst picks up within 1 hour

**Channel C — Deal Desk Referral**
- Deal Desk includes CI request in deal review package
- Typically for Tier 2/3 requests where deal complexity is already established
- Mike Rodgers or assigned analyst acknowledges within 2 hours

### 1.2 Intake Form (Required Fields)

Every request must capture the following before work begins. The analyst may gather this via Slack thread, Salesforce record, or a 10-minute intake call with the AE.

```
DEAL INTELLIGENCE REQUEST

[ ] Salesforce Opportunity ID: _______________
[ ] Account Name: _______________
[ ] Deal Size (TCV): _______________
[ ] Deal Stage: _______________
[ ] Expected Close Date: _______________
[ ] Confirmed Competitor(s): _______________
[ ] Competitor Source: (rep confirmed / prospect stated / RFP named / inferred)
[ ] Key Buyer Persona: (CIO / CFO / CMIO / VP Revenue Cycle / Other)
[ ] Buyer's Top 3 Priorities: _______________
[ ] Current Vendor (if displacement): _______________
[ ] Known Objections Heard So Far: _______________
[ ] Upcoming Milestone: (shortlist meeting / demo / final presentation / board vote)
[ ] Milestone Date: _______________
[ ] Specific Questions from the AE: _______________
[ ] Requested Tier: (Quick Brief / Standard / War Room / Analyst Decides)
```

### 1.3 Deal Intelligence Tier Assignment

Tier assignment determines scope, SLA, and review requirements. The CI analyst recommends a tier; Mike Rodgers approves Tier 3 assignments.

| Tier | Name | Criteria | SLA | Deliverable | Review |
|------|------|----------|-----|-------------|--------|
| 1 | Quick Brief | Deal <$5M TCV, single competitor, standard scenario | 4 hours | 1-page brief (email/Slack) | Self-review |
| 2 | Standard Package | Deal $5M-$25M TCV, 1-2 competitors, demo stage or later | 24 hours | Full positioning package (5-8 pages) | Peer + CI Lead |
| 3 | War Room | Deal >$25M TCV or strategic account, must-win designation, C-suite involved | 48 hours | War Room package + live briefing session | Full team + Mike sign-off |

**Automatic Tier 3 Triggers** (regardless of deal size):
- Deal is flagged "must-win" by Sales VP or higher
- Prospect is a competitive displacement of an existing Oracle Health customer (defensive deal)
- Deal involves 3+ confirmed competitors in final evaluation
- C-suite (CEO/CFO/Board) is the final decision-maker and has expressed competitor preference

### 1.4 SLA Tracking

- SLA clock starts at analyst acknowledgment, not at request submission
- SLA measured in business hours (8am-6pm ET, Mon-Fri)
- If a Tier 2 request arrives at 5pm Friday, the 24-hour SLA expires Monday 5pm — not Saturday 5pm
- SLA breaches are logged and reviewed in weekly M&CI standup
- Target: <5% SLA breach rate across all tiers

---

## Phase 2: Intelligence Assembly

### 2.1 Source Prioritization by Tier

| Source | Tier 1 | Tier 2 | Tier 3 |
|--------|--------|--------|--------|
| Active battlecard (SOP-08) | Required | Required | Required |
| Pricing workbook pull (SOP-10) | If available | Required | Required |
| Win/loss look-alike deals (SOP-09) | — | Required (3+ matches) | Required (5+ matches) |
| Prospect-specific research (LinkedIn, press, filings) | Optional | Required | Required + deep dive |
| Ellen AI research query | Recommended | Required | Required + multiple queries |
| Rep debrief call (10-15 min) | Optional | Recommended | Required |
| Deal Desk deal model review | — | If available | Required |
| Sales Engineer technical assessment | — | Optional | Required |

### 2.2 Look-Alike Deal Analysis

For Tier 2 and 3 packages, the analyst identifies **look-alike deals** from Salesforce and win/loss records:

**Match criteria (in priority order):**
1. Same competitor in the evaluation
2. Similar deal size (within 50% of TCV)
3. Similar buyer segment (acute care, ambulatory, post-acute, payer)
4. Similar buyer size (bed count or provider count within 30%)
5. Same buyer persona as primary decision-maker

**Minimum look-alike requirements:**
- Tier 2: 3 look-alike deals identified, at least 1 win and 1 loss
- Tier 3: 5 look-alike deals identified, at least 2 wins and 2 losses
- For each look-alike: document what worked, what failed, and what the AE would do differently

### 2.3 Ellen AI Integration

Ellen is queried as a standard step in all Tier 2 and 3 packages:

```
Standard Ellen queries for deal intelligence:
1. "[Competitor] competitive positioning against Oracle Health in [segment]"
2. "[Competitor] recent product announcements last 90 days"
3. "[Prospect name] technology investments and vendor relationships"
4. "[Competitor] known weaknesses in [buyer persona] conversations"
5. "[Competitor] pricing trends in [deal size range]"
```

Ellen outputs are confidence-tagged per SOP-05 standards and included in the package with source attribution.

---

## Phase 3: Positioning & Narrative Construction

### 3.1 Tier 1 — Quick Brief Template

```
DEAL INTELLIGENCE QUICK BRIEF
Opportunity: [Name] | ID: [SFDC ID] | Competitor: [Name]
Prepared by: [Analyst] | Date: [Date] | SLA: 4hr

─── POSITIONING STATEMENT (use verbatim with prospect) ───
[3 sentences: Why Oracle Health wins this deal against this competitor,
calibrated to the buyer's stated priorities]

─── TOP 3 DEAL-SPECIFIC OBJECTIONS ───
1. They'll say: [objection]     → You say: [response]
2. They'll say: [objection]     → You say: [response]
3. They'll say: [objection]     → You say: [response]

─── PRICING GUIDANCE ───
[1 paragraph: Expected competitor pricing range for this deal size,
known discount patterns, packaging traps to watch for]
Confidence: [HIGH/MEDIUM/LOW per SOP-10]

─── ONE THING TO SHOW IN DEMO ───
[The single Oracle Health capability that this competitor cannot match
in the context of this deal's requirements]

─── RED FLAG ───
[The one scenario where this deal is at highest risk of loss.
What must the rep avoid or address proactively.]
```

### 3.2 Tier 2 — Standard Positioning Package Template

The Standard Package is a structured document (5-8 pages) delivered as a PDF or internal wiki page, containing:

**Section 1: Deal Context Summary** (1 page)
- Opportunity details, buyer profile, competitive landscape for this deal
- Deal stage and upcoming milestones
- Buyer's stated priorities mapped to Oracle Health strengths and competitor strengths

**Section 2: Competitive Positioning Narrative** (1-2 pages)
- Deal-specific positioning statement (3-sentence framework)
- Differentiation matrix: Oracle Health vs. [Competitor] on this buyer's top 5 criteria
- "Where we win" and "Where we're vulnerable" — honest assessment calibrated to this deal

**Section 3: Objection Preparation Matrix** (1 page)
- 5-7 objections specific to this competitor + deal context
- Each objection includes: What they'll say | Why they say it | Your response | Proof point to cite

**Section 4: Pricing Intelligence** (1 page)
- Competitor pricing estimate for this deal size and configuration
- Oracle Health pricing positioning recommendations
- Discount band expectations (from SOP-10 Monte Carlo model if available)
- Packaging comparison: what is included/excluded in competitor vs. Oracle Health proposals

**Section 5: Demo Differentiation Notes** (1 page)
- Top 3 capabilities to demonstrate that create maximum separation
- Top 2 capabilities to avoid or de-emphasize (where competitor is strong)
- Recommended demo narrative flow tied to buyer priorities
- Technical differentiators the SE should highlight

**Section 6: Look-Alike Deal Intelligence** (1 page)
- Summary of 3+ look-alike deals: what worked, what did not
- Pattern analysis: common win themes and loss themes against this competitor at this deal size
- Recommended deal strategy based on pattern analysis

**Section 7: Risk Assessment** (0.5 page)
- Top 3 deal risks with mitigation recommendations
- Competitive risk score: LOW / MEDIUM / HIGH / CRITICAL
- Early warning indicators to monitor

### 3.3 Tier 3 — War Room Package

The War Room Package includes everything in Tier 2, plus:

**Section 8: Executive Briefing Deck** (5-7 slides)
- For internal use: prepared for Sales VP or higher to review deal strategy
- Includes competitive landscape map, win probability assessment, resource allocation recommendation

**Section 9: Competitor Deep Dive** (2-3 pages)
- Extended competitor analysis beyond battlecard content
- Recent competitive movements specific to this market segment
- Competitor's likely deal strategy based on their known playbook
- Personnel intelligence: who is the competitor's likely sales lead and what is their style

**Section 10: Decision-Maker Mapping** (1 page)
- Key decision-makers and influencers at the prospect
- Each mapped to: known vendor preferences, priorities, concerns
- Recommended engagement strategy per persona

**War Room Live Briefing:**
- 60-minute session with full deal team (AE, SE, Deal Desk, Sales VP)
- CI analyst presents findings and facilitates competitive strategy discussion
- Action items documented and tracked in Salesforce
- Follow-up support committed (CI analyst available for deal-specific questions through close)

---

## Phase 4: Quality Gate & Delivery

### 4.1 Quality Standards by Tier

| Quality Dimension | Tier 1 | Tier 2 | Tier 3 |
|-------------------|--------|--------|--------|
| Confidence tagging on all claims | Required | Required | Required |
| Source citation for pricing data | Required | Required | Required |
| Look-alike deal evidence | — | Required | Required |
| Peer review | — | Required | Required |
| CI Lead (Mike) review | — | Required | Required |
| Sales VP review | — | — | Required for exec briefing deck |
| Legal review | — | If pricing data is HIGH sensitivity | Required |

### 4.2 Delivery Protocol

**Tier 1 (Quick Brief):**
- Delivered via Slack DM to requesting AE + posted in deal Slack channel if one exists
- Simultaneously attached to Salesforce Opportunity record
- No formal delivery meeting required

**Tier 2 (Standard Package):**
- Delivered as PDF via email to AE + SE + Deal Desk contact
- Attached to Salesforce Opportunity record
- Optional 15-minute walkthrough call offered (recommended but not required)
- CI analyst available for follow-up questions for 10 business days

**Tier 3 (War Room Package):**
- Delivered as PDF + slide deck to full deal team
- Salesforce Opportunity record updated with CI engagement tag
- 60-minute War Room briefing scheduled within 48 hours of package delivery
- CI analyst assigned to deal through close (available for ad hoc questions, follow-up research)
- Weekly check-in with AE until deal resolves

### 4.3 Feedback Capture

Within 5 business days of deal close (win or loss), the CI analyst contacts the AE:

```
DEAL INTELLIGENCE FEEDBACK

Opportunity ID: _______________
Package Tier Delivered: _______________
Deal Outcome: WIN / LOSS / NO DECISION / DELAYED

1. Did you use the positioning package in the deal? (Y/N)
2. Which sections were most valuable? (rank 1-3)
3. Which sections were least valuable or not used?
4. Was any information inaccurate or outdated? (If yes, specify)
5. Did the competitor behave as predicted? (Y/N — explain)
6. Would you request a package again for a similar deal? (Y/N)
7. What would you add or change?
8. NPS: How likely are you to recommend deal intelligence packages
   to another AE? (0-10)
```

---

## Phase 5: Deal Outcome Tracking & Effectiveness Measurement

### 5.1 Win Rate Delta Tracking

The primary effectiveness measure is the win rate difference between deals that received a positioning package and those that did not:

```
Win Rate (with package) - Win Rate (without package) = Package Lift

Calculation methodology:
- Cohort A: All competitive deals (>$2M TCV) where a positioning package
  was delivered at any tier
- Cohort B: All competitive deals (>$2M TCV) where no package was
  requested or delivered
- Control for: deal size, competitor, segment, sales rep experience level
- Minimum sample: 20 deals per cohort before reporting lift as statistically significant
- Quarterly reporting cadence
```

### 5.2 Predictive Deal Risk Score

For Tier 3 (War Room) packages, the CI analyst assigns a **Deal Risk Score** based on competitive intelligence:

| Score | Label | Definition |
|-------|-------|-----------|
| 1-3 | LOW | Oracle Health is well-positioned; competitor is weak in this segment/deal size |
| 4-6 | MEDIUM | Competitive deal with no clear favorite; outcome depends on execution |
| 7-8 | HIGH | Competitor has structural advantages; Oracle Health must overcome specific gaps |
| 9-10 | CRITICAL | Competitor is heavily favored; deal requires executive intervention or unique strategy |

Risk scores are logged at package delivery and compared to deal outcomes to calibrate the model over time. Target: Risk Score should predict loss with >70% accuracy for scores 8+ within 6 months of tracking.

---

## RACI Matrix

| Activity | CI Lead (Mike) | CI Analyst | AE / Rep | SE | Deal Desk | Sales VP |
|----------|---------------|------------|----------|-----|-----------|----------|
| Request intake & triage | A | **R** | **R** (initiator) | I | C | I |
| Tier assignment | **R/A** (Tier 3) | **R** (Tier 1-2) | I | I | C | I (Tier 3) |
| Battlecard pull & overlay | A | **R** | — | — | — | — |
| Pricing intelligence pull | A | **R** | — | — | C | — |
| Look-alike deal analysis | A | **R** | C | — | C | — |
| Ellen AI research | A | **R** | — | — | — | — |
| Rep debrief call | A | **R** | **R** (participant) | C | — | — |
| Positioning narrative draft | A | **R** | — | C | — | — |
| Objection matrix construction | A | **R** | C | C | — | — |
| Demo differentiation notes | A | **R** | — | **R** (co-author) | — | — |
| Quality gate review | **R/A** | C | — | — | — | C (Tier 3) |
| Package delivery | A | **R** | I | I | I | I |
| War Room live briefing | **R** (facilitator) | C | **R** (participant) | **R** (participant) | C | **R** (participant) |
| Feedback capture | A | **R** | **R** (respondent) | — | — | — |
| Win rate tracking | **R/A** | C | — | — | — | I |
| SOP update | **R/A** | C | I | I | I | I |

**Key:** R = Responsible, A = Accountable, C = Consulted, I = Informed

### Escalation Path

| Situation | Escalate To | Timeline |
|-----------|------------|---------|
| SLA breach imminent (Tier 2/3) | Mike Rodgers | 4 hours before SLA expiry |
| Conflicting intelligence from multiple sources | Mike Rodgers for resolution | Before package delivery |
| Tier 3 request without adequate Salesforce data | AE's Sales Manager | Within 4 hours of request |
| AE disputes positioning recommendation | Mike Rodgers + Sales VP | Within 1 business day |
| Package delivered but deal team not using it | Mike Rodgers → Sales VP | At next deal review |

---

## KPIs

### Delivery Performance KPIs

| KPI | Description | Target | Measurement |
|-----|-------------|--------|-------------|
| **SLA Compliance Rate** | % of packages delivered within tier SLA | ≥95% | Intake log vs. delivery timestamp |
| **Tier 1 Avg Delivery Time** | Average hours from intake to Quick Brief delivery | ≤3 hours | Intake log |
| **Tier 2 Avg Delivery Time** | Average hours from intake to Standard Package delivery | ≤20 hours | Intake log |
| **Tier 3 Avg Delivery Time** | Average hours from intake to War Room Package delivery | ≤40 hours | Intake log |
| **Request Volume** | Total positioning packages requested per quarter | ≥15/quarter (growing) | Intake log |

### Quality KPIs

| KPI | Description | Target | Measurement |
|-----|-------------|--------|-------------|
| **Rep NPS** | AE Net Promoter Score on package quality | ≥8.0/10 | Post-deal feedback form |
| **Section Utilization** | % of package sections that AEs report using | ≥70% of sections | Post-deal feedback form |
| **Accuracy Rate** | % of packages where no intelligence was flagged as inaccurate | ≥90% | Post-deal feedback form |
| **Competitive Prediction Accuracy** | % of deals where competitor behaved as predicted | ≥75% | Post-deal feedback form |

### Business Impact KPIs

| KPI | Description | Target | Measurement |
|-----|-------------|--------|-------------|
| **Win Rate Lift** | Win rate delta: deals with package vs. without | ≥10 percentage points | Salesforce cohort analysis |
| **Revenue Influenced** | Total TCV of deals where package was delivered | Track quarterly | Salesforce attribution |
| **Deal Risk Score Accuracy** | % of deals scored 8+ that resulted in loss | ≥70% predictive accuracy | Score vs. outcome tracking |
| **Repeat Request Rate** | % of AEs who request a second package after first | ≥60% | Intake log |
| **Time-to-Close Impact** | Average days to close: package deals vs. no-package deals | Measure for correlation | Salesforce analysis |

### Process Health KPIs

| KPI | Description | Target | Measurement |
|-----|-------------|--------|-------------|
| **Intake Completeness** | % of requests with all required fields at intake | ≥80% | Intake form audit |
| **Feedback Response Rate** | % of closed deals where AE provides feedback | ≥70% | Feedback log |
| **SOP Adherence** | % of packages passing quality gate without rework | ≥85% | Quality gate log |
| **Quarterly Review Completion** | Win rate delta report delivered on schedule | 100% | CI calendar |

---

## Appendix A: Cross-SOP Dependencies

| Dependency | Source SOP | Data Used |
|-----------|-----------|-----------|
| Battlecard content | SOP-08 | Competitor positioning, objections, proof points, differentiators |
| Pricing intelligence | SOP-10 | Competitor pricing ranges, discount bands, packaging comparisons |
| Win/loss patterns | SOP-09 | Look-alike deal analysis, loss pattern identification |
| Competitive landscape | SOP-06 | Market context, competitor strategy, segment dynamics |
| Source credibility | SOP-05 | Ellen AI confidence tagging, source validation |

## Appendix B: Deal Intelligence Tier Decision Tree

```
Is deal >$25M TCV or flagged must-win?
  YES → Tier 3 (War Room)
  NO  ↓

Is deal >$5M TCV with confirmed competitor at demo stage or later?
  YES → Tier 2 (Standard Package)
  NO  ↓

Is deal >$2M TCV with competitive signal?
  YES → Tier 1 (Quick Brief)
  NO  → Decline request (below threshold — direct rep to battlecard library)
```

---

**End of SOP-29**
