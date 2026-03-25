# SOP-30: GTM Intelligence Artifact Production

**Owner**: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-25
**Category**: Sales Enablement — Intelligence Content Factory
**Priority**: P1 — Scales competitive intelligence beyond 1:1 deal support
**Maturity**: Gap → Implicit → Documented

---

## Purpose

SOP-29 governs deal-specific intelligence — one deal, one package, one AE. This SOP governs the **factory** that produces go-to-market intelligence artifacts at scale: the competitive positioning briefs that Marketing uses in campaigns, the market segment overviews that Sales Enablement incorporates into training, the pricing/packaging comparisons that Commercial Strategy uses for annual planning, and the demo intelligence briefs that Solutions Consulting references across dozens of deals.

The distinction is critical: SOP-29 is reactive (a deal exists, a rep needs help now). SOP-30 is proactive (these artifacts should exist before any individual rep asks, so the entire field is pre-armed).

**Why this matters (quantified):**

- Oracle Health's M&CI team serves ~200 AEs and ~50 SEs across multiple segments. Mike Rodgers cannot produce deal-specific packages for every competitive deal. Scalable GTM artifacts ensure baseline competitive readiness for the entire field, reserving deal-specific work (SOP-29) for high-value situations.
- Marketing campaigns that incorporate competitive positioning intelligence see 15-25% higher engagement from sales teams (Forrester, B2B Sales Enablement study 2024). If the content does not reflect what reps hear in the field, they ignore it.
- Sales training materials that include real competitive intelligence (not generic product messaging) increase rep confidence scores by 30% in post-training assessments (internal Oracle Health Q3 2025 data).
- The target is 3+ artifacts per quarter. At steady state, the M&CI artifact library should contain 12-15 active artifacts covering all major competitors, segments, and use cases.

**What this SOP produces:**

| Artifact Type | Primary Audience | Cadence | Shelf Life |
|--------------|-----------------|---------|-----------|
| Competitive Positioning Brief (for campaigns) | Marketing, Demand Gen | Per campaign + quarterly refresh | 90 days |
| Market Segment Intelligence Overview | Sales Enablement, Sales Training | Quarterly | 90 days |
| Pricing/Packaging Comparison Matrix | Commercial Strategy, Deal Desk | Quarterly + event-triggered | 60 days |
| Demo Intelligence Brief | Solutions Consulting, SEs | Per competitor + quarterly refresh | 90 days |
| Competitive Trend Report | GTM Leadership, Product Marketing | Quarterly | 90 days |
| Sales Play Intelligence Insert | Sales Enablement, AEs | Per sales play launch | Tied to play lifecycle |

---

## Scope

### In Scope

- All GTM intelligence artifacts produced by M&CI for consumption by Marketing, Sales Enablement, Commercial Strategy, and Solutions Consulting
- Artifact lifecycle: ideation → research → production → review → distribution → refresh → retirement
- Quality standards, review gates, and distribution channels for each artifact type
- Measurement: adoption tracking, citation in deals, feedback from consuming teams
- Integration with SOP-08 (battlecards), SOP-09 (win/loss), SOP-10 (pricing) as source material

### Out of Scope

- Deal-specific intelligence packages (SOP-29)
- Battlecard creation and maintenance (SOP-08)
- Win/loss interview execution (SOP-09)
- Product Marketing's own collateral (feature sheets, data sheets, customer stories)
- Analyst relations deliverables (Gartner/Forrester/KLAS submissions)

---

## ARCHITECTURE: GTM Artifact Production System

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: ARTIFACT PLANNING & PRIORITIZATION                            │
│  Quarterly planning cycle aligned to GTM calendar                       │
│  Inputs: Marketing campaign calendar, Sales training calendar,          │
│  Commercial Strategy roadmap, field feedback, competitive signals       │
│  Output: Quarterly Artifact Production Plan (3+ artifacts committed)   │
├─────────────────────────────────────────────────────────────────────────┤
│  PHASE 2: RESEARCH & INTELLIGENCE SYNTHESIS                             │
│  Pull from: Battlecards (SOP-08), Pricing (SOP-10), Win/Loss (SOP-09) │
│  New research: Ellen queries, market analysis, segment-specific intel  │
│  Synthesis: Cross-source triangulation → confidence-tagged claims      │
├─────────────────────────────────────────────────────────────────────────┤
│  PHASE 3: ARTIFACT PRODUCTION                                           │
│  Template-driven production per artifact type                          │
│  Audience-calibrated: Marketing language vs. Sales language vs. Tech   │
│  Confidence tagging inherited from source SOPs                         │
│  Draft → Internal review → Revision → Final                           │
├─────────────────────────────────────────────────────────────────────────┤
│  PHASE 4: REVIEW & APPROVAL                                             │
│  Consuming team review (Marketing/Sales Enablement/Deal Desk)          │
│  CI Lead sign-off on intelligence accuracy                             │
│  Legal review if pricing data or competitor claims involved            │
├─────────────────────────────────────────────────────────────────────────┤
│  PHASE 5: DISTRIBUTION & ACTIVATION                                     │
│  Channels: Highspot/Seismic, SharePoint, Slack #intel, email          │
│  Activation: Training session, campaign launch integration, Slack post │
│  Tagging: artifact ID, version, competitors covered, expiry date      │
├─────────────────────────────────────────────────────────────────────────┤
│  PHASE 6: LIFECYCLE MANAGEMENT                                          │
│  Freshness tracking: 60-90 day shelf life per type                    │
│  Refresh triggers: market event, new data, consuming team request     │
│  Retirement: artifacts past expiry with no refresh → archived         │
│  Usage analytics: downloads, views, citations in deals                │
└─────────────────────────────────────────────────────────────────────────┘
        │                                                       │
        ▼                                                       ▼
┌───────────────────┐                               ┌─────────────────────┐
│  ADOPTION METRICS │                               │  PREDICTIVE MODEL   │
│  Downloads + Views│                               │  Artifact Demand    │
│  Deal Citations   │                               │  Forecast by Type   │
│  Rep Feedback     │                               │  + Segment          │
└───────────────────┘                               └─────────────────────┘
```

---

## Phase 1: Artifact Planning & Prioritization

### 1.1 Quarterly Planning Cycle

At the start of each quarter, M&CI conducts a planning session to determine the artifact production slate:

**Planning Inputs:**
- Marketing campaign calendar (what campaigns need competitive positioning support)
- Sales Enablement training calendar (what training sessions need CI content)
- Commercial Strategy priorities (what pricing/packaging analyses are needed)
- Solutions Consulting requests (what demo intelligence is most needed)
- Field feedback from previous quarter (what gaps did reps report)
- Competitive signal analysis (what market events require proactive artifacts)
- SOP-29 request patterns (what deal-specific requests reveal systemic gaps)

**Planning Meeting:**
- Attendees: Mike Rodgers, Marketing Ops lead, Sales Enablement lead, Deal Desk lead
- Frequency: Quarterly (first 2 weeks of each quarter)
- Duration: 60 minutes
- Output: Quarterly Artifact Production Plan

### 1.2 Artifact Prioritization Framework

Each candidate artifact is scored on four dimensions:

| Dimension | Weight | Scoring |
|-----------|--------|---------|
| **Field Demand** | 30% | HIGH (3+ reps/teams requesting), MEDIUM (1-2 requests), LOW (proactive only) |
| **Revenue Impact** | 30% | HIGH (supports $50M+ pipeline), MEDIUM ($10-50M), LOW (<$10M) |
| **Freshness Gap** | 20% | HIGH (no current artifact exists), MEDIUM (artifact >90 days old), LOW (current artifact exists) |
| **Production Effort** | 20% | LOW effort = higher score (quick wins prioritized when impact is equal) |

**Quarterly commitment:** Minimum 3 artifacts, target 5, stretch goal 8. This accounts for M&CI bandwidth alongside SOP-29 deal-specific work and ongoing SOP-08/09/10 maintenance.

### 1.3 Artifact Production Plan Template

```
QUARTERLY ARTIFACT PRODUCTION PLAN — Q[X] 2026

Planned Artifacts:

1. [Artifact Type]: [Title]
   Competitor(s): [names]
   Audience: [team]
   Trigger: [campaign launch / training event / gap identified]
   Target Delivery: [date]
   Assigned To: [analyst name]
   Priority Score: [X.X / 10]

2. [Artifact Type]: [Title]
   ...

Deferred to Next Quarter:
- [Artifact idea + reason for deferral]

Dependencies:
- [SOP-08 battlecard refresh needed before artifact X]
- [SOP-10 pricing data needed for artifact Y]
```

---

## Phase 2: Research & Intelligence Synthesis

### 2.1 Source Material Hierarchy

GTM artifacts are synthesis products — they pull from existing intelligence and add audience-specific framing. The research phase should leverage existing SOP outputs first, then fill gaps with new research.

**Layer 1: Existing SOP Outputs (pull first)**
- Battlecards (SOP-08): Competitor positioning, objections, proof points, differentiators
- Pricing workbook (SOP-10): Pricing comparisons, discount bands, packaging analysis
- Win/loss patterns (SOP-09): Win themes, loss themes, competitive dynamics by segment
- Competitive landscape (SOP-06): Market context, competitor strategy, trend analysis

**Layer 2: New Research (fill gaps)**
- Ellen AI queries targeted to artifact topic
- Analyst reports (KLAS, Gartner, Forrester) relevant to the segment
- Public filings, press releases, product announcements
- Industry event intelligence (HIMSS, HLTH, ViVE takeaways)
- Customer advisory board feedback (if available through Product Marketing)

**Layer 3: Subject Matter Expert Input**
- Sales Engineering for technical differentiation content
- Product Marketing for product roadmap context (what can we say publicly)
- Deal Desk for commercial and packaging intelligence
- Field reps for "what are you actually hearing" validation

### 2.2 Research Quality Standards

Every claim in a GTM artifact must meet the same confidence standards as SOP-08 battlecards:

- **VERIFIED**: Claim supported by Tier 1 source (direct documentation, confirmed data)
- **INFERRED**: Claim supported by Tier 2 source (analyst report, pattern analysis, multiple secondary sources)
- **ESTIMATED**: Claim based on Tier 3 source (single secondary source, market inference, dated data)

GTM artifacts intended for external-facing campaigns (used by Marketing in customer-facing materials) must contain only VERIFIED and INFERRED claims. ESTIMATED claims are permitted only in internal-use artifacts (training materials, strategy documents).

---

## Phase 3: Artifact Production

### 3.1 Artifact Type Templates

#### Type A: Competitive Positioning Brief (for Marketing Campaigns)

```
COMPETITIVE POSITIONING BRIEF
Campaign: [Name] | Competitor: [Name] | Segment: [Name]
Version: [X] | Expiry: [Date — 90 days max]

─── CAMPAIGN CONTEXT ───
[What is the campaign? What is the target audience? What message is
Marketing delivering? Where does competitive positioning fit?]

─── COMPETITIVE LANDSCAPE FOR THIS SEGMENT ───
[2-3 paragraphs: Who are the competitors in this segment? What is
their market position? What are buyers hearing from them?]

─── ORACLE HEALTH POSITIONING (for this campaign) ───
[The specific competitive narrative Marketing should use in this campaign.
Not generic "Oracle Health is great" — specific to this segment, this
competitor, this buyer persona.]

─── KEY CLAIMS (with confidence tags) ───
| Claim | Confidence | Source | Approved for External Use? |
|-------|-----------|--------|---------------------------|
| [claim 1] | VERIFIED | [source] | YES / NO |
| [claim 2] | INFERRED | [source] | YES (with caveats) / NO |

─── COMPETITOR COUNTER-MESSAGING ───
[What is the competitor saying in this segment? What is their campaign
message? How should Oracle Health's campaign address or neutralize it?]

─── DO NOT SAY ───
[Claims or positioning that should NOT be used in this campaign — legally
sensitive, unverified, or strategically counterproductive]
```

#### Type B: Market Segment Intelligence Overview (for Sales Training)

```
MARKET SEGMENT INTELLIGENCE OVERVIEW
Segment: [Name] | Date: [Date] | Version: [X]
Expiry: [Date — 90 days max]

─── SEGMENT PROFILE ───
[Market size, growth rate, buyer characteristics, buying patterns,
typical deal structures, key decision-makers]

─── COMPETITIVE LANDSCAPE ───
[For each major competitor in this segment:]
  Competitor: [Name]
  Market Share: [X% — confidence tag]
  Key Strengths: [2-3 bullets]
  Key Weaknesses: [2-3 bullets]
  Typical Deal Size: [range]
  Win Rate Against: [Oracle Health win rate in this segment]

─── ORACLE HEALTH POSITION IN THIS SEGMENT ───
[Where we are strong, where we are weak, what the field should know]

─── TOP 5 THINGS EVERY REP SHOULD KNOW ───
[The five most important competitive intelligence points for this segment.
Written in rep-friendly language. Each must be deliverable in a single
sentence during a prospect conversation.]

─── RECOMMENDED SALES PLAYS ───
[Which existing sales plays apply to this segment? What competitive
adaptations are needed?]

─── DATA SOURCES & CONFIDENCE ───
[Source list with confidence tags. Training content should be transparent
about what we know vs. what we infer.]
```

#### Type C: Pricing/Packaging Comparison Matrix

```
PRICING/PACKAGING COMPARISON MATRIX
Competitors: [Names] | Segment: [Name] | Date: [Date]
Expiry: [Date — 60 days max] | INTERNAL USE ONLY

─── COMPARISON TABLE ───
| Dimension | Oracle Health | [Competitor 1] | [Competitor 2] |
|-----------|-------------|----------------|----------------|
| Pricing Model | [description] | [description + confidence] | [description + confidence] |
| Base Package Includes | [list] | [list + confidence] | [list + confidence] |
| Common Add-ons | [list + price range] | [list + confidence] | [list + confidence] |
| Typical Discount Range | [range] | [range + confidence] | [range + confidence] |
| Contract Terms | [standard] | [standard + confidence] | [standard + confidence] |
| TCO at [size tier 1] | [$range] | [$range + confidence] | [$range + confidence] |
| TCO at [size tier 2] | [$range] | [$range + confidence] | [$range + confidence] |

─── PACKAGING TRAPS ───
[Where does the competitor's packaging create hidden costs or lock-in?
What should Oracle Health's proposal highlight to expose these?]

─── COMMERCIAL STRATEGY RECOMMENDATIONS ───
[Based on this comparison, what pricing/packaging strategies should
Oracle Health consider? What deal structures create maximum advantage?]

Data sourced from SOP-10 Pricing Workbook. Confidence tags per SOP-10 §5.
```

#### Type D: Demo Intelligence Brief

```
DEMO INTELLIGENCE BRIEF
Competitor: [Name] | Date: [Date] | Version: [X]
Expiry: [Date — 90 days max]

─── COMPETITOR DEMO PLAYBOOK ───
[What does this competitor typically show in demos? What is their
narrative flow? What are they trying to prove?]

─── WHERE THEY DEMO WELL ───
[2-3 areas where the competitor's demo is genuinely strong.
SEs must know this to avoid head-to-head comparisons in these areas.]

─── WHERE THEY DEMO POORLY ───
[2-3 areas where the competitor's demo has known gaps, clunky UX,
or missing functionality. These are opportunities for Oracle Health.]

─── ORACLE HEALTH DEMO DIFFERENTIATION PLAYS ───
For each of the competitor's weak areas:
| Their Weakness | Our Strength | Demo Move | Talk Track |
|---------------|-------------|-----------|-----------|
| [gap 1] | [capability] | [what to show] | [what to say] |
| [gap 2] | [capability] | [what to show] | [what to say] |

─── DEMO SEQUENCE RECOMMENDATION ───
[Recommended Oracle Health demo flow when competing against this
competitor. What to show first, what to save for last, what to skip.]

─── PROSPECT QUESTIONS THAT FAVOR ORACLE HEALTH ───
[5 questions the SE can encourage the prospect to ask during the
competitor's demo that expose weaknesses]
```

---

## Phase 4: Review & Approval

### 4.1 Review Protocol by Artifact Type

| Artifact Type | Reviewer 1 | Reviewer 2 | Approver | Legal Required? |
|--------------|-----------|-----------|---------|----------------|
| Competitive Positioning Brief | Marketing Ops lead | — | Mike Rodgers | If claims used externally |
| Market Segment Overview | Sales Enablement lead | Product Marketing | Mike Rodgers | No (internal only) |
| Pricing/Packaging Matrix | Deal Desk lead | — | Mike Rodgers | Yes (pricing data) |
| Demo Intelligence Brief | SE Manager | — | Mike Rodgers | No (internal only) |
| Competitive Trend Report | Product Marketing | — | Mike Rodgers | No (internal only) |
| Sales Play Intelligence Insert | Sales Enablement lead | Sales Ops | Mike Rodgers | If pricing included |

### 4.2 Review Criteria

Reviewers evaluate each artifact against:

1. **Accuracy**: Are all claims confidence-tagged and source-cited? Are there any claims that seem outdated or unsupported?
2. **Audience fit**: Is the artifact written for its intended audience? (Marketing language ≠ Sales language ≠ Technical language)
3. **Actionability**: Can the consuming team use this immediately? Or does it require interpretation?
4. **Completeness**: Does the artifact cover the scope committed in the production plan?
5. **Freshness**: Are all source data points within their confidence windows per SOP-05/08/10?

### 4.3 Revision Cycle

- Reviewer feedback due within 3 business days of draft delivery
- CI analyst incorporates feedback within 2 business days
- Maximum 2 revision cycles before escalation to Mike for final decision
- Total production-to-approval target: 10 business days per artifact

---

## Phase 5: Distribution & Activation

### 5.1 Distribution Channels

| Channel | Artifact Types | Audience |
|---------|---------------|----------|
| Highspot / Seismic (sales enablement platform) | All | AEs, SEs, Sales Enablement |
| SharePoint CI Library | All | All internal stakeholders |
| Slack #intel-updates | New artifact announcements | All Sales, Marketing, GTM |
| Email (targeted) | Artifact-specific | Consuming team leadership |
| Sales Training LMS | Segment Overviews, Demo Briefs | AEs, SEs (enrolled in training) |

### 5.2 Activation Protocol

Distribution alone is insufficient. Each artifact requires an **activation event** to drive adoption:

| Artifact Type | Activation Event | Owner |
|--------------|-----------------|-------|
| Competitive Positioning Brief | 15-min briefing with Marketing campaign team | CI Analyst |
| Market Segment Overview | Incorporated into next Sales Training session | Sales Enablement lead + CI Analyst |
| Pricing/Packaging Matrix | Briefing with Deal Desk team | Mike Rodgers |
| Demo Intelligence Brief | Live walkthrough with SE team | CI Analyst + SE Manager |
| Competitive Trend Report | GTM Leadership review meeting | Mike Rodgers |
| Sales Play Intelligence Insert | Integrated into Sales Play launch | Sales Enablement lead |

### 5.3 Artifact Metadata & Tagging

Every published artifact carries:

```
Artifact ID: GTM-[TYPE]-[COMPETITOR/SEGMENT]-[YYYY]-[QX]-[VERSION]
Example: GTM-POS-EPIC-2026-Q2-v1.0

Published Date: [date]
Expiry Date: [date — 60 or 90 days from publish]
Competitors Covered: [list]
Segment: [if applicable]
Audience: [primary consuming team]
Confidence Floor: [minimum confidence level of any claim in this artifact]
Source SOPs: [list of SOPs that provided source material]
Version: [major.minor]
Status: ACTIVE / EXPIRING / ARCHIVED
```

---

## Phase 6: Lifecycle Management

### 6.1 Freshness Tracking

| Artifact Type | Shelf Life | Refresh Trigger |
|--------------|-----------|----------------|
| Competitive Positioning Brief | 90 days | Campaign end, competitor event, quarterly review |
| Market Segment Overview | 90 days | Quarterly cycle, major market event |
| Pricing/Packaging Matrix | 60 days | SOP-10 workbook refresh, competitor pricing event |
| Demo Intelligence Brief | 90 days | Competitor product release, SE feedback |
| Competitive Trend Report | 90 days | Quarterly cycle |
| Sales Play Intelligence Insert | Tied to play lifecycle | Play refresh or retirement |

### 6.2 Refresh vs. Retire Decision

At expiry, the CI analyst evaluates:

```
ARTIFACT LIFECYCLE DECISION

Artifact ID: _______________
Current Status: EXPIRING
Last Usage (downloads/views in final 30 days): _______________
Deal Citations (Salesforce) in lifetime: _______________
Consuming Team Feedback: _______________

Decision:
[ ] REFRESH — artifact is still relevant, update with current intelligence
[ ] RETIRE — artifact has low usage, topic is no longer priority, or replaced by newer artifact
[ ] MERGE — combine with another artifact for efficiency

If REFRESH: target delivery date for updated version: _______________
If RETIRE: archive location: SharePoint CI Archive / [path]
```

### 6.3 Artifact Library Health Dashboard

Reviewed monthly by Mike Rodgers:

```
ARTIFACT LIBRARY HEALTH — [Month] [Year]

Total Active Artifacts: [N]
Artifacts Expiring This Month: [N]
Artifacts Overdue for Refresh: [N] ← RED if >0
Artifacts Published This Quarter: [N] vs. Target: [3+]

Coverage Gaps:
- Competitors with no active artifact: [list]
- Segments with no active overview: [list]
- Consuming teams with unfulfilled requests: [list]

Top 5 Artifacts by Usage: [ranked list]
Bottom 5 Artifacts by Usage: [ranked list — candidates for retirement]
```

---

## RACI Matrix

| Activity | CI Lead (Mike) | CI Analyst | Marketing Ops | Sales Enablement | Deal Desk | Product Mktg |
|----------|---------------|------------|--------------|-----------------|-----------|-------------|
| Quarterly production planning | **R/A** | C | C | C | C | C |
| Artifact prioritization scoring | **R/A** | **R** | C | C | C | — |
| Research & intelligence synthesis | A | **R** | — | — | C | C |
| Artifact drafting | A | **R** | — | — | — | — |
| Consuming team review | A | C | **R** (campaigns) | **R** (training) | **R** (pricing) | C |
| CI accuracy review | **R/A** | C | — | — | — | — |
| Legal review (when required) | A | **R** (initiates) | — | — | — | — |
| Distribution | A | **R** | I | I | I | I |
| Activation event delivery | **R** (pricing/trends) | **R** (campaigns/demo) | C | **R** (training) | C | — |
| Usage tracking & analytics | A | **R** | C | C | — | — |
| Refresh/retire decisions | **R/A** | C | C | C | C | — |
| Quarterly artifact review | **R/A** | C | I | I | I | I |
| SOP update | **R/A** | C | I | I | I | I |

**Key:** R = Responsible, A = Accountable, C = Consulted, I = Informed

### Escalation Path

| Situation | Escalate To | Timeline |
|-----------|------------|---------|
| Quarterly target at risk (<3 artifacts committed) | Mike Rodgers + GTM Leadership | Week 3 of quarter |
| Consuming team review stalled (>5 business days) | Consuming team manager | After 5 business days |
| Legal blocks distribution of artifact with pricing data | Mike Rodgers + Legal | Within 2 business days |
| Artifact contains claims disputed by Product Marketing | Mike Rodgers + PMM lead | Before publication |
| Artifact usage <5 views in first 30 days | Mike Rodgers for root cause | At 30-day review |

---

## KPIs

### Production Volume KPIs

| KPI | Description | Target | Measurement |
|-----|-------------|--------|-------------|
| **Quarterly Artifact Output** | Number of artifacts published per quarter | ≥3, target 5 | Artifact registry |
| **Production Cycle Time** | Average business days from plan commitment to publication | ≤10 business days | Production log |
| **Plan Completion Rate** | % of planned artifacts delivered on schedule | ≥80% | Quarterly plan vs. actuals |
| **Artifact Library Size** | Total active artifacts in library | ≥12 by end of Year 1 | Library audit |
| **Coverage Completeness** | % of P1 competitors with ≥1 active artifact per type | ≥80% | Library audit |

### Adoption & Usage KPIs

| KPI | Description | Target | Measurement |
|-----|-------------|--------|-------------|
| **Artifact Download/View Rate** | Average views per artifact in first 30 days | ≥25 views | Highspot/SharePoint analytics |
| **Deal Citation Rate** | Number of deals where GTM artifacts cited as resource | ≥10/quarter | Salesforce notes + rep survey |
| **Marketing Campaign Adoption** | % of competitive campaigns using CI positioning brief | ≥80% | Marketing Ops tracking |
| **Sales Training Incorporation** | % of competitive training sessions using CI segment overview | ≥90% | Sales Enablement log |
| **Repeat Consumer Rate** | % of consuming teams requesting follow-up artifacts | ≥60% | Request log |

### Quality KPIs

| KPI | Description | Target | Measurement |
|-----|-------------|--------|-------------|
| **Review Pass Rate** | % of artifacts approved without major revision | ≥70% | Review log |
| **Accuracy Challenge Rate** | % of artifacts where a claim was challenged post-publication | ≤10% | Feedback tracking |
| **Freshness Compliance** | % of active artifacts within shelf life | ≥90% | Library health dashboard |
| **Consuming Team NPS** | Net Promoter Score from Marketing/Sales Enablement/Deal Desk | ≥8.0/10 | Quarterly survey |

### Business Impact KPIs

| KPI | Description | Target | Measurement |
|-----|-------------|--------|-------------|
| **Revenue Influenced by Artifacts** | Total pipeline supported by deals citing GTM artifacts | Track quarterly | Salesforce attribution |
| **Campaign Performance Lift** | Engagement delta on campaigns with vs. without CI positioning brief | Measure for correlation | Marketing analytics |
| **Training Effectiveness Score** | Post-training competitive confidence score (reps) | ≥7.5/10 | Post-training survey |
| **Self-Serve Ratio** | % of competitive questions answered by artifact library vs. ad hoc request | ≥40% by Q4 | Request log comparison |

---

## Appendix A: Cross-SOP Dependencies

| Dependency | Source SOP | Artifact Types Served |
|-----------|-----------|----------------------|
| Battlecard content | SOP-08 | All artifact types (foundation layer) |
| Pricing intelligence | SOP-10 | Pricing/Packaging Matrix, Positioning Briefs |
| Win/loss patterns | SOP-09 | Segment Overviews, Positioning Briefs |
| Competitive landscape | SOP-06 | Trend Reports, Segment Overviews |
| Source credibility | SOP-05 | All artifact types (confidence tagging) |
| Deal-specific patterns | SOP-29 | Identifies systemic gaps that become GTM artifacts |

## Appendix B: Artifact Type Selection Guide

```
Is the consuming team Marketing running a competitive campaign?
  YES → Competitive Positioning Brief (Type A)

Is the consuming team Sales Enablement running competitive training?
  YES → Market Segment Intelligence Overview (Type B)

Is the consuming team Deal Desk or Commercial Strategy?
  YES → Pricing/Packaging Comparison Matrix (Type C)

Is the consuming team Solutions Consulting or SE leadership?
  YES → Demo Intelligence Brief (Type D)

Is the request for GTM leadership strategic planning?
  YES → Competitive Trend Report (Type E)

Is the request tied to a specific sales play launch?
  YES → Sales Play Intelligence Insert (Type F)

None of the above?
  → Evaluate if this is a deal-specific request (route to SOP-29)
  → Or a new artifact type (propose to Mike for inclusion in next quarterly plan)
```

---

**End of SOP-30**
