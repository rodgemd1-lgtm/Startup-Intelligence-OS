# SOP-07: Competitor Profile Creation & Maintenance

**Owner**: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-23
**Category**: Competitive Intelligence Production
**Priority**: P1 — Foundation of competitive intelligence program
**Maturity**: Partial → Documented

---

## Table of Contents

1. [Purpose](#1-purpose)
2. [Scope](#2-scope)
3. [Profile Architecture — The Six Strategic Lenses](#3-profile-architecture--the-six-strategic-lenses)
4. [Phase 1: New Profile Creation](#4-phase-1-new-profile-creation)
5. [Profile Template — Complete Six-Lens Structure](#5-profile-template--complete-six-lens-structure)
6. [Data Sources per Lens](#6-data-sources-per-lens)
7. [Confidence Scoring](#7-confidence-scoring)
8. [Phase 2: Semi-Annual Deep Dive Refresh](#8-phase-2-semi-annual-deep-dive-refresh)
9. [Phase 3: Event-Driven Update Protocol](#9-phase-3-event-driven-update-protocol)
10. [Predictive Algorithm — Competitor Threat Score (CTS)](#10-predictive-algorithm--competitor-threat-score-cts)
11. [Monte Carlo: Market Position Shift Modeling](#11-monte-carlo-market-position-shift-modeling)
12. [Profile Quality Standards](#12-profile-quality-standards)
13. [Archive Policy](#13-archive-policy)
14. [Distribution](#14-distribution)
15. [RACI Matrix](#15-raci-matrix)
16. [Profile Catalog](#16-profile-catalog)
17. [Expert Panel Scoring](#17-expert-panel-scoring)
18. [Appendix A: Research Source Registry](#appendix-a-research-source-registry)
19. [Appendix B: Update Log Template](#appendix-b-update-log-template)

---

## 1. Purpose

This SOP establishes the end-to-end methodology for creating, maintaining, and distributing competitor intelligence profiles within Oracle Health's Marketing & Competitive Intelligence (M&CI) function.

A competitor profile is Oracle Health's single source of truth for what a given competitor does, how well they do it, where they are investing, and how dangerous they are. Done right, a profile answers the question a sales rep has at 10 PM before a board-level demo — without them having to ask.

The goals of this SOP are:

- **Consistency**: Every profile follows the same Six Strategic Lenses framework so they can be compared, stacked, and cross-referenced.
- **Accuracy**: Data points carry explicit confidence scores so consumers know what to trust.
- **Freshness**: Defined update triggers ensure profiles never go stale at a critical moment.
- **Predictive value**: CTS scoring and Monte Carlo modeling turn historical data into forward-looking strategic intelligence.
- **Operational discipline**: RACI, distribution controls, and archive policy make the program defensible and auditable.

This SOP governs profiles for all competitors classified as Tier 1, 2, or 3 (as defined by the CTS algorithm in Section 10). It does not govern win/loss reports (SOP-09), battlecard production (SOP-06), or signal triage (SOP-02), though those SOPs consume outputs from this one.

---

## 2. Scope

### 2.1 Competitor Coverage

Competitor profiles are maintained for organizations that meet one or more of the following criteria:

| Inclusion Criterion | Definition |
|---|---|
| **Direct pipeline overlap** | Competitor appears in >5% of active Oracle Health opportunities |
| **Adjacent market threat** | Competitor is expanding into Oracle Health's core RCM/clinical domains |
| **Strategic partnership threat** | Competitor is a partner that is also competing in key segments |
| **Acquisition target** | Competitor is likely to be acquired by a larger player that would significantly increase threat level |
| **Emerging disruptor** | AI-native or well-funded startup targeting Oracle Health's installed base |
| **Executive watch list** | Matt Cohlmia or equivalent executive has specifically requested coverage |

### 2.2 Current Covered Competitor Set

As of 2026-03-23, active profiles are maintained for:

| Competitor | Primary Domain | CTS Tier (current) | Profile Location |
|---|---|---|---|
| Epic Systems | EHR, Revenue Cycle | Tier 1 | `knowledge-base/mci/products/rcm-platforms/epic/` |
| Waystar | RCM, Claims Processing | Tier 1 | `knowledge-base/mci/products/rcm-platforms/waystar/` |
| R1 RCM | Revenue Cycle Services | Tier 1 | `knowledge-base/mci/products/rcm-platforms/r1-rcm/` |
| FinThrive | RCM Software | Tier 2 | `knowledge-base/mci/products/rcm-platforms/finthrive/` |
| Ensemble Health Partners | RCM Services | Tier 2 | `knowledge-base/mci/products/rcm-platforms/ensemble/` |
| Conifer Health Solutions | RCM Services | Tier 2 | `knowledge-base/mci/products/rcm-platforms/conifer/` |
| CodaMetrix | AI-Powered Coding | Tier 2 | `knowledge-base/mci/products/rcm-platforms/codametrix/` |
| Access Healthcare | RCM Outsourcing | Tier 3 | `knowledge-base/mci/products/rcm-platforms/access-healthcare/` |

### 2.3 Prioritization Logic

When resource constraints require prioritizing which profiles receive the most depth or most frequent updates, apply this hierarchy:

1. CTS Tier 1 competitors always receive priority attention
2. Within a CTS tier, competitors with active head-to-head pipeline deals come first
3. Within that, competitors with a recent trigger event (see Section 9) come first
4. Competitors without a trigger event and no active deals are serviced on the standard semi-annual cadence

### 2.4 Out of Scope

This SOP does not cover:
- Technology vendors who are exclusively Oracle Health partners
- Staffing firms without a technology product
- International competitors with no North American footprint
- Companies below $10M revenue unless CTS criteria are met

---

## 3. Profile Architecture — The Six Strategic Lenses

Every competitor profile is structured around six dimensions, called the Six Strategic Lenses. Each lens answers a different strategic question about the competitor. Together, they give Oracle Health a 360-degree view.

```
┌─────────────────────────────────────────────────────────────────────┐
│           THE SIX STRATEGIC LENSES — Profile Architecture          │
├──────────────┬──────────────────────────────────────────────────────┤
│  LENS 1      │  PRODUCT                                             │
│              │  What do they build? How good is it? Where is it    │
│              │  going? How does AI fit in?                          │
├──────────────┼──────────────────────────────────────────────────────┤
│  LENS 2      │  FINANCIAL                                           │
│              │  How big are they? How fast are they growing?        │
│              │  How well-funded? Can they sustain a price war?      │
├──────────────┼──────────────────────────────────────────────────────┤
│  LENS 3      │  MARKET                                              │
│              │  Who are their customers? What segments? What logos? │
│              │  Where do they win vs. where do we win?              │
├──────────────┼──────────────────────────────────────────────────────┤
│  LENS 4      │  GO-TO-MARKET                                        │
│              │  How do they sell? What do they charge? Who are      │
│              │  their channel partners? How do they close deals?    │
├──────────────┼──────────────────────────────────────────────────────┤
│  LENS 5      │  CUSTOMER                                            │
│              │  Are their customers happy? What do they complain    │
│              │  about? Are customers at churn risk? What's NPS?     │
├──────────────┼──────────────────────────────────────────────────────┤
│  LENS 6      │  TECHNOLOGY                                          │
│              │  What is the architecture? AI maturity? Patent       │
│              │  portfolio? Interoperability posture? Tech debt?      │
└──────────────┴──────────────────────────────────────────────────────┘
```

### Why Six Lenses?

The six-lens model is derived from best practices at SCIP (Strategic and Competitive Intelligence Professionals), adapted for the healthcare IT context. The rationale for each lens:

- **Product** answers the feature-by-feature question sales reps face daily. Without it, battlecards don't exist.
- **Financial** determines staying power. A competitor with deteriorating margins can't sustain discounting or R&D investment. This lens predicts M&A likelihood and strategic vulnerability.
- **Market** tells Oracle Health where it is actually losing ground, not just where it thinks it might. Logo tracking and segment analysis cut through marketing spin.
- **GTM** exposes the sales playbook. Knowing how a competitor prices, packages, and closes deals lets Oracle Health adjust its own approach in real time.
- **Customer** is the early warning system. Dissatisfied customers are Oracle Health's best prospects. NPS deterioration signals competitive opportunity 6-18 months before it shows up in market share data.
- **Technology** is the long-term strategic lens. A competitor with superior AI maturity or better interoperability posture will erode Oracle Health's differentiation over a 3-5 year horizon regardless of current product gaps.

### Lens Weighting for CTS

Not all lenses contribute equally to threat scoring. The CTS algorithm (Section 10) draws from lens-specific sub-scores. The weighting reflects Oracle Health's competitive reality in RCM and clinical IT:

| Lens | CTS Weight | Rationale |
|---|---|---|
| Product Trajectory (from Lens 1) | 20% | Healthcare IT buying decisions are heavily product-driven |
| Financial Firepower (from Lens 2) | 20% | Funding capacity determines R&D and discounting ability |
| Market Overlap (from Lens 3) | 25% | Direct pipeline competition is the most immediate threat |
| GTM / Market Momentum (from Lens 4+3) | 20% | Win rate trends are leading indicators |
| Customer Satisfaction (from Lens 5) | 15% | High CSAT competitors are harder to displace |

---

## 4. Phase 1: New Profile Creation

### 4.1 Trigger for New Profile

A new profile is initiated when any of the following occurs:

- A competitor meets any inclusion criterion from Section 2.1
- CTS scoring of a previously untracked competitor returns ≥4.0
- Matt Cohlmia, VP Product, or VP Sales requests coverage
- A competitor appears in three or more competitive deals within a 60-day window
- A new AI-native entrant raises ≥$20M in Series A or later funding in the RCM/clinical space

### 4.2 New Profile Creation Process

**Total estimated time: 3-5 business days for a complete Tier 1/2 profile**

#### Stage 1: Scoping (Day 0 — 2 hours)

Before any research begins:

1. Confirm the competitor meets inclusion criteria (document which criteria apply)
2. Assign an initial CTS estimate using available information (see Section 10)
3. Determine target depth: Tier 1 (full six lenses, high-confidence targets), Tier 2 (full six lenses, MEDIUM confidence acceptable), Tier 3 (abbreviated, four lenses minimum)
4. Identify a primary researcher and a subject matter reviewer (see RACI, Section 15)
5. Create the profile skeleton from the template in Section 5
6. Log the new profile in the Profile Catalog (Section 16)

#### Stage 2: Primary Research Sprint (Days 1-2 — 8-12 hours)

Execute research across all six lenses using the source registry in Section 6. Follow this sequence:

**Recommended research order (dependency-based):**

```
1. Financial (Lens 2) first — size and growth context frames everything else
2. Market (Lens 3) second — who they serve shapes product interpretation
3. Product (Lens 1) third — now interpretable in market context
4. GTM (Lens 4) fourth — built on top of product and market understanding
5. Customer (Lens 5) fifth — validates market and GTM assumptions
6. Technology (Lens 6) last — makes most sense after product is understood
```

For each lens:
- Document each data point with source URL, date retrieved, and confidence score
- Flag any data point older than 18 months as STALE — include but mark prominently
- If a sub-field cannot be researched with any confidence, mark as DATA GAP and note research method attempted

#### Stage 3: Synthesis and Analysis (Day 3 — 4-6 hours)

1. **Cross-lens pattern identification**: What story do the six lenses tell together? A competitor with high financial firepower, fast product trajectory, but low customer satisfaction is a different threat than one with moderate finances but exceptional customer loyalty.
2. **Oracle Health competitive positioning**: For each lens, what is Oracle Health's relative position? Where do we lead? Where are we exposed?
3. **Strategic implications**: 3-5 bullets on what this competitor's current state means for Oracle Health's sales, product, and strategy teams
4. **Initial CTS calculation**: Run the full CTS algorithm with the data gathered
5. **Data gap inventory**: List unresolved DATA GAPs and plan to close them

#### Stage 4: Review and Approval (Day 4-5 — 2-3 hours)

1. Primary researcher submits draft to subject matter reviewer (Product for technical accuracy, Finance for financial accuracy)
2. Reviewer provides comments within 48 hours
3. Researcher incorporates feedback and updates confidence scores if reviewer corrections are significant
4. Final profile is posted to the knowledge base
5. Profile owner (Mike Rodgers) reviews summary section and approves for distribution
6. Distribution is triggered per Section 14

#### Stage 5: Initial CTS Scoring and Tier Assignment

After profile completion, compute formal CTS score (Section 10) and assign the competitor to the appropriate monitoring tier. Log in the Profile Catalog.

### 4.3 Research Methodology Principles

**Source triangulation**: No HIGH-confidence rating is assigned to a data point supported by a single source. Minimum two independent sources for HIGH.

**Recency discipline**: The research clock resets at profile creation. Data older than 18 months is STALE regardless of source quality. STALE data is retained in the profile for trend context but flagged visibly.

**Competitive deception awareness**: Competitors actively manage their public image. Cross-check marketing claims against customer reviews, analyst reports, and win/loss data. A company claiming 99% customer retention but showing high Glassdoor employee churn in its CS org warrants a skepticism flag.

**Oracle Health context**: Every data point should be evaluated through the lens of what it means for Oracle Health's competitive position, not just what it says about the competitor in isolation.

---

## 5. Profile Template — Complete Six-Lens Structure

Use this template verbatim for every new profile. Fields marked `[REQUIRED]` must be populated before the profile is considered complete. Fields marked `[IF AVAILABLE]` are best-effort.

```markdown
# [COMPETITOR NAME] — Competitor Intelligence Profile

**Profile Owner**: Mike Rodgers, Sr. Director, M&CI
**Primary Researcher**: [name]
**Subject Matter Reviewer**: [name]
**Profile Version**: [x.x]
**Created**: [YYYY-MM-DD]
**Last Full Refresh**: [YYYY-MM-DD]
**Last Event-Driven Update**: [YYYY-MM-DD or "None"]
**Next Scheduled Refresh**: [YYYY-MM-DD]
**CTS Score**: [x.x] | **CTS Tier**: [Tier 1 / 2 / 3 / Monitor]
**Profile Completeness**: [xx%]
**Distribution Class**: [RESTRICTED / INTERNAL / EXTENDED]

---

## EXECUTIVE SUMMARY [REQUIRED]

### Who They Are
[2-3 sentences: what this company does, founded when, owned by whom, primary market]

### Why Oracle Health Cares
[2-3 sentences: where they compete with us, what makes them threatening or non-threatening right now]

### The One Thing to Know
[1 sentence: the single most strategically important fact about this competitor right now]

### Current Threat Assessment
- **CTS Score**: [x.x / 10]
- **Trajectory**: [Rising / Stable / Declining] — [one sentence explanation]
- **Top 3 Risks to Oracle Health**:
  1. [risk]
  2. [risk]
  3. [risk]
- **Top 3 Oracle Health Advantages vs. This Competitor**:
  1. [advantage]
  2. [advantage]
  3. [advantage]

---

## LENS 1: PRODUCT [REQUIRED]

### 1.1 Product Portfolio Overview
| Product Name | Category | GA Date | Status | Notes |
|---|---|---|---|---|
| [product] | [RCM / EHR / Coding / etc.] | [date or "N/A"] | [Generally Available / Beta / Announced / Rumored] | [confidence] |

### 1.2 Core Feature Capabilities
Rate Oracle Health's position relative to this competitor (Oracle Ahead / Parity / Oracle Behind / Unknown):

| Capability Area | Oracle Position | Confidence | Notes |
|---|---|---|---|
| Claim submission and scrubbing | [Ahead/Parity/Behind/Unknown] | [H/M/L] | |
| Denial management | | | |
| Prior authorization automation | | | |
| Patient financial experience | | | |
| Analytics and reporting | | | |
| EHR integration depth | | | |
| Workflow automation | | | |
| Mobile/self-service patient tools | | | |
| [Add domain-specific capabilities] | | | |

### 1.3 AI and Automation Capabilities [REQUIRED]
| AI Capability | Maturity | Oracle Position | Confidence | Source |
|---|---|---|---|---|
| AI-assisted coding | [None / Prototype / GA / Mature] | [Ahead/Parity/Behind] | [H/M/L] | [source] |
| Predictive denial prevention | | | | |
| Natural language processing | | | | |
| Autonomous claim correction | | | | |
| Contract modeling/optimization | | | | |
| Generative AI in workflow | | | | |
| AI-powered patient engagement | | | | |

**AI Maturity Assessment**: [1-2 sentences on overall AI posture — are they a genuine AI-first competitor or AI-washing?]

### 1.4 Integration and Interoperability
- **EHR integrations**: [list key EHR partners and integration depth]
- **FHIR/HL7 compliance posture**: [strong / partial / weak] — [confidence]
- **API-first vs. monolithic**: [assessment]
- **Notable integration gaps**: [list]

### 1.5 Product Roadmap Intelligence [IF AVAILABLE]
| Initiative | Horizon | Evidence Basis | Confidence |
|---|---|---|---|
| [roadmap item] | [H1 2026 / H2 2026 / 2027 / Unknown] | [conference speech / job posting / patent / analyst report] | [H/M/L] |

**Roadmap Signal Sources**: [where is roadmap intelligence coming from?]

### 1.6 Product Strengths and Weaknesses
**Strengths**:
- [strength 1] — Confidence: [H/M/L]
- [strength 2]
- [strength 3]

**Weaknesses / Oracle Exploit Points**:
- [weakness 1] — Confidence: [H/M/L]
- [weakness 2]
- [weakness 3]

### 1.7 Recent Product Updates (last 12 months)
| Date | Update | Significance | Source |
|---|---|---|---|
| [YYYY-MM] | [description] | [High/Medium/Low impact on competitive position] | [source] |

---

## LENS 2: FINANCIAL [REQUIRED]

### 2.1 Company Structure
| Field | Value | Confidence | Date |
|---|---|---|---|
| Ownership type | [Public / Private PE-backed / Private independent / Subsidiary] | | |
| Parent company (if applicable) | | | |
| HQ location | | | |
| Founded | | | |
| Employee count (total) | | | |
| Employee count (R&D/Engineering) | [IF AVAILABLE] | | |

### 2.2 Revenue and Growth
| Metric | Value | Year/Period | Confidence | Source |
|---|---|---|---|---|
| Annual Revenue | $[x]M/B | FY[year] | [H/M/L] | |
| YoY Revenue Growth | [x]% | [period] | | |
| 3-Year Revenue CAGR | [x]% | [period] | | |
| Revenue from RCM/Healthcare IT | $[x]M | [period] | | |
| Revenue as % of parent (if applicable) | [x]% | [period] | | |

### 2.3 Profitability and Margin Signals
| Metric | Value | Period | Confidence | Notes |
|---|---|---|---|---|
| EBITDA margin (estimated) | [x]% | [period] | | |
| Gross margin (estimated) | [x]% | [period] | | |
| Operating income (if public) | $[x]M | [period] | | |
| Profitability status | [Profitable / Break-even / Loss-making / Unknown] | | | |

**Margin Signal Analysis**: [Can this competitor sustain deep discounting? Are they under margin pressure that will force price increases?]

### 2.4 Funding and Capital Structure
| Event | Amount | Date | Investors | Confidence |
|---|---|---|---|---|
| [Funding round / IPO / Bond issuance / PE acquisition] | $[x]M | [YYYY-MM] | [investor names] | [H/M/L] |

- **Total funding raised**: $[x]M — Confidence: [H/M/L]
- **Estimated cash runway**: [IF AVAILABLE]
- **Debt load signals**: [IF AVAILABLE]
- **Recent capital events**: [notable financing activity in last 24 months]

### 2.5 Financial Firepower Assessment
*Composite assessment of capacity to invest in R&D, M&A, and competitive pricing:*

**Firepower score (1-10)**: [x]
**Rationale**: [2-3 sentences on why this score — what could they afford to do with their financial position?]
**Key risk**: [What financial scenario would weaken them? PE pressure for exit? Margin compression? Customer concentration?]

### 2.6 M&A Activity and Acquisition History
| Date | Target | Deal Value | Strategic Rationale | Impact on Oracle Health |
|---|---|---|---|---|
| [YYYY-MM] | [company] | $[x]M | [rationale] | [competitive implication] |

**M&A Appetite Assessment**: [acquirer / target / neither — and why]

---

## LENS 3: MARKET [REQUIRED]

### 3.1 Market Segments and Verticals
| Segment | Presence | Strength | Oracle Position | Notes |
|---|---|---|---|---|
| Large health systems (>500 beds) | [Strong/Moderate/Weak/None] | | [Ahead/Parity/Behind] | |
| Community hospitals (100-500 beds) | | | | |
| Critical access / rural hospitals | | | | |
| Academic medical centers | | | | |
| Physician group practices | | | | |
| Specialty care | | | | |
| Behavioral health | | | | |
| Government/VA | | | | |
| Payer-adjacent | | | | |

### 3.2 Customer Base
- **Estimated total customers**: [number] — Confidence: [H/M/L]
- **Estimated covered lives / claims volume**: [IF AVAILABLE]
- **Key named logos** (from press releases, case studies, conference presentations):

| Customer | Segment | Relationship Since | Evidence Source |
|---|---|---|---|
| [customer name] | [segment] | [approx year] | [source] |

- **Customer concentration risk**: [Top 10 customers estimated as % of revenue, if known]
- **Geographic coverage**: [US national / regional / international]

### 3.3 Win/Loss Intelligence
*Sourced from Oracle Health's own win/loss data, Gartner, and field intelligence*

| Scenario | Win Rate Estimate | Confidence | Key Win Factor | Key Loss Factor |
|---|---|---|---|---|
| Head-to-head Oracle vs. [Competitor] | [x]% Oracle win | [H/M/L] | [why we win] | [why we lose] |
| [Competitor] vs. field (not Oracle) | | | | |

**Oracle Health's strongest segments against this competitor**: [list]
**Oracle Health's most vulnerable segments against this competitor**: [list]

### 3.4 Market Position Trajectory
- **Market share trend**: [Growing / Stable / Declining] — Confidence: [H/M/L]
- **New logo wins (last 12 months)**: [estimate or DATA GAP]
- **Known customer losses (last 12 months)**: [if any]
- **Analyst positioning**: [Gartner/KLAS ranking or assessment, if available]
- **KLAS score (if applicable)**: [score] — [year]

### 3.5 Partnership Ecosystem
| Partner | Type | Strategic Significance | Notes |
|---|---|---|---|
| [partner name] | [Technology / Channel / Referral / OEM] | [High/Medium/Low] | |

**Concerning partnerships for Oracle Health**: [any partnerships that extend their reach into Oracle Health's accounts?]

---

## LENS 4: GO-TO-MARKET [REQUIRED]

### 4.1 Sales Motion
- **Primary sales model**: [Direct enterprise / Channel-led / PLG / Hybrid]
- **Average sales cycle**: [estimate] — Confidence: [H/M/L]
- **Primary buyer**: [CFO / CIO / VP Revenue Cycle / CMO / CEO]
- **Economic buyer vs. technical champion dynamics**: [assessment]
- **Deal size range**: [$xM — $yM ARR] — Confidence: [H/M/L]

### 4.2 Pricing and Packaging
| Model | Description | Typical Range | Confidence |
|---|---|---|---|
| [Subscription/License/FFS/% of collections] | [description] | $[x] | [H/M/L] |

- **Pricing transparency**: [transparent / opaque / negotiated-only]
- **Known discounting behavior**: [aggressive / moderate / list-price-firm]
- **Pricing levers against Oracle Health**: [how do they compete on price? Do they go low to win? Bundle with partners?]

### 4.3 Marketing and Positioning
- **Tagline / core positioning claim**: "[quote]"
- **Primary value proposition**: [what they say they do better than everyone else]
- **Key differentiators (self-claimed)**: [list from their own materials]
- **Messaging against Oracle Health specifically**: [any known competitive messaging or positioning that targets us]
- **Content marketing posture**: [aggressive / moderate / minimal]
- **Thought leadership**: [conferences they own or dominate, publications, awards]

### 4.4 Channel and Alliances
| Alliance | Type | Market Impact | Date Announced | Confidence |
|---|---|---|---|---|
| [partner] | [reseller / co-sell / integration / OEM] | [High/Med/Low] | [date] | [H/M/L] |

### 4.5 Key Sales Plays (Intelligence-Derived)
*These are plays the competitor uses based on field intelligence, not their own marketing*

1. **[Play name]**: [description of the play, typical use case, how to counter]
2. **[Play name]**: [description]
3. **[Play name]**: [description]

---

## LENS 5: CUSTOMER [REQUIRED]

### 5.1 Customer Satisfaction Signals
| Signal Type | Finding | Source | Date | Confidence |
|---|---|---|---|---|
| KLAS score | [x / 100] | KLAS | [year] | [H/M/L] |
| G2 / Capterra rating | [x / 5] | [platform] | [date] | |
| Gartner Peer Insights rating | [x / 5] | Gartner | [date] | |
| NPS estimate | [x] | [source] | [date] | |

**Overall satisfaction assessment**: [Strong / Moderate / Weak / Mixed] — [1 sentence rationale]

### 5.2 Common Customer Complaints
*From verified review platforms, community forums, field intelligence*

| Complaint Theme | Frequency | Severity | Oracle Advantage? |
|---|---|---|---|
| [complaint] | [Common/Occasional/Rare] | [High/Med/Low churn risk] | [Yes/No/Partial] |

### 5.3 Customer Advocacy Signals
- **Known reference customers** (those who speak publicly): [list]
- **Case study volume**: [how many published case studies?]
- **Conference speaking (customer voices)**: [do customers speak at their conferences?]

### 5.4 Churn and Retention Signals
- **Estimated retention rate**: [x]% — Confidence: [H/M/L]
- **Known churn events (last 24 months)**: [if any — customer moved away from this competitor]
- **Churn risk factors**: [what operational or product issues are most likely to drive customers away?]

### 5.5 Support Quality Assessment
- **Implementation timeline**: [average go-live timeline] — Confidence: [H/M/L]
- **Support model**: [24/7 / business hours / tiered]
- **Known implementation issues**: [common pain points during implementation from reviews]
- **Escalation reputation**: [how do they handle escalations?]

### 5.6 Customer Expansion Behavior
- **Cross-sell/upsell motion**: [aggressive / moderate / minimal]
- **Product stickiness**: [how deep does product embed into customer operations?]
- **Switching cost assessment**: [High / Medium / Low] — [why]

---

## LENS 6: TECHNOLOGY [REQUIRED]

### 6.1 Technology Architecture
- **Architecture pattern**: [Cloud-native SaaS / Hosted / On-premise / Hybrid]
- **Cloud provider(s)**: [AWS / Azure / GCP / Multi-cloud / On-prem]
- **Core technology stack** (inferred from job postings, GitHub, open source activity):

| Layer | Technology | Evidence Basis | Confidence |
|---|---|---|---|
| Backend | [languages/frameworks] | [job postings / GitHub] | [H/M/L] |
| Data platform | [data warehouse / lake] | | |
| ML/AI platform | [frameworks / MLOps tools] | | |
| Integration layer | [APIs / ESB / FHIR server] | | |

- **Architecture maturity**: [Modern / Transitioning / Legacy] — [assessment]
- **Technical debt signals**: [evidence of legacy constraints that limit velocity]

### 6.2 AI Maturity Assessment
*Rate on a 5-level scale:*

| Level | Definition |
|---|---|
| 1 — AI Absent | No meaningful AI in product |
| 2 — AI Features | Point AI features, not systematic |
| 3 — AI-Assisted | AI embedded across core workflows |
| 4 — AI-Native | Product architecture built around AI |
| 5 — AI-Autonomous | AI makes decisions autonomously in workflow |

**Current AI Maturity Level**: [1-5] — Confidence: [H/M/L]
**AI Maturity Trajectory**: [evidence of where they are heading]
**AI Investment Signals**: [hiring, acquisitions, partnerships, publications]
**Oracle Health AI Maturity vs. This Competitor**: [Ahead / Parity / Behind] — [rationale]

### 6.3 Interoperability Posture
| Standard | Support Level | Notes |
|---|---|---|
| HL7 v2 | [Full / Partial / None] | |
| FHIR R4 | | |
| Direct messaging | | |
| TEFCA participation | | |
| ONC certification (if applicable) | | |

**Interoperability competitive implication**: [Is this a differentiator or a gap for them?]

### 6.4 Patent Portfolio [IF AVAILABLE]
- **Total patents**: [number] — Confidence: [H/M/L]
- **Key patent areas**: [what IP are they protecting?]
- **Recent patent filings (signal of R&D direction)**: [IF AVAILABLE]

### 6.5 Security and Compliance Posture
| Compliance Area | Status | Notes |
|---|---|---|
| HIPAA/HITECH | [Compliant / Issues noted / Unknown] | |
| SOC 2 Type II | | |
| FedRAMP (if applicable) | | |
| Known security incidents | [if any] | |

### 6.6 Engineering Velocity Signals
- **GitHub activity** (if open source components): [IF AVAILABLE]
- **Engineering headcount trend** (from LinkedIn): [growing / stable / shrinking]
- **Release cadence**: [frequent / periodic / infrequent] — Evidence: [source]
- **Tech conference / publication presence**: [do their engineers publish? Speak at re:Invent, etc.?]

---

## COMPETITIVE POSITIONING SUMMARY [REQUIRED]

### Oracle Health Relative Position Map

Rate Oracle Health's position vs. this competitor across all six lenses:

| Lens | Oracle Position | Confidence | Key Evidence |
|---|---|---|---|
| Product | [Clearly Ahead / Slight Edge / Parity / Slight Behind / Clearly Behind] | [H/M/L] | |
| Financial | | | |
| Market | | | |
| Go-to-Market | | | |
| Customer | | | |
| Technology | | | |

**Overall relative position**: [Advantaged / Competitive / Challenged]

### Strategic Recommendations for Oracle Health

Based on this profile, the following actions are recommended:

**For Sales**:
1. [specific tactic or talk track]
2. [specific vulnerability to exploit]

**For Product**:
1. [gap Oracle Health should close]
2. [area where Oracle Health should double down]

**For Marketing**:
1. [positioning opportunity]
2. [content or proof point gap to fill]

**For Strategy (Matt Cohlmia / C-Suite)**:
1. [strategic implication or option to consider]

---

## DATA GAPS AND RESEARCH BACKLOG

| Lens | Gap Description | Priority | Research Method to Try | Assigned To |
|---|---|---|---|---|
| [lens] | [what we don't know] | [High/Med/Low] | [method] | [name] |

---

## SOURCE LOG

| Source URL / Reference | Lens(es) | Data Points Supported | Retrieved | Confidence Contribution |
|---|---|---|---|---|
| [URL or citation] | [lens numbers] | [what data this supports] | [YYYY-MM-DD] | [H/M/L] |

---

## UPDATE HISTORY

| Date | Update Type | Changes Made | Researcher |
|---|---|---|---|
| [YYYY-MM-DD] | [Creation / Semi-Annual / Event-Driven] | [summary of changes] | [name] |
```

---

## 6. Data Sources per Lens

Each lens has a preferred set of sources. This registry defines where to look, what to expect, and how to evaluate source quality.

### Lens 1: Product — Data Sources

| Source | Type | What to Get | Quality Notes |
|---|---|---|---|
| Competitor's own website / product pages | Primary | Feature claims, pricing (if public), positioning | HIGH quality for claims; treat as marketing, not truth |
| KLAS Research (klas.com) | Analyst | Product ratings, customer feedback by module | HIGH — gold standard for HIT product evaluation |
| Gartner Magic Quadrant / Critical Capabilities | Analyst | Product positioning, capability comparison | HIGH — requires subscription |
| Product documentation / user manuals (public) | Primary | Actual feature depth, integration specs | HIGH when available |
| App store listings / changelogs | Primary | Release cadence, feature additions | MEDIUM — sparse but objective |
| Conference presentations (HIMSS, HLTH, HFMA) | Event | Roadmap signals, AI claims, new capabilities | HIGH — executives speak candidly at industry events |
| Job postings (LinkedIn, Indeed) | Signal | Technology stack, new product areas, AI investment | MEDIUM — inferred, not stated |
| Patent database (USPTO, Google Patents) | IP | R&D direction, AI capabilities being built | HIGH when matched to product; requires interpretation |
| GitHub / open source repositories | Technical | Technology stack, engineering velocity, quality | HIGH for technical detail; limited to OSS activity |
| Customer reviews (G2, Capterra, KLAS) | Validation | Feature gaps, usability, real-world performance | HIGH for gap identification; selection bias toward extremes |

### Lens 2: Financial — Data Sources

| Source | Type | What to Get | Quality Notes |
|---|---|---|---|
| SEC filings (10-K, 10-Q, 8-K) | Regulatory | Revenue, margins, segment performance, guidance | HIGH — legal disclosure |
| Pitchbook / Crunchbase | Private market | Funding rounds, investors, estimated valuation | MEDIUM — third-party aggregated; verify against press releases |
| Capital IQ / Bloomberg | Financial | Detailed financial data (subscription required) | HIGH — institutional-grade |
| Earnings call transcripts (Seeking Alpha, IR site) | Primary | Revenue growth, margin trends, strategic priorities | HIGH — direct from management |
| Press releases (M&A, funding, partnerships) | Primary | Capital events, strategic moves | HIGH — verified announcements |
| LinkedIn headcount trends | Signal | Revenue per employee proxy, growth trajectory | MEDIUM — imperfect but directional |
| Industry analyst reports (Frost, IDC, HFMA) | Analyst | Market size, revenue estimates for private cos | MEDIUM — estimates, not actuals |
| PE/VC portfolio pages | Primary | Ownership, strategic intent, fund vintage | HIGH for ownership facts |

### Lens 3: Market — Data Sources

| Source | Type | What to Get | Quality Notes |
|---|---|---|---|
| Oracle Health's own win/loss data | Internal | Actual competitive win rate, loss reasons | HIGH — must be accessed through M&CI |
| Customer press releases | Primary | Logo wins, go-lives, customer quotes | HIGH — verified at announcement |
| HIMSS Analytics / DEFINITIVE Healthcare | Data | Installed base, customer segment analysis | HIGH — requires license |
| Gartner Peer Insights | Analyst | Customer segments, company sizes, verticals | MEDIUM — self-reported |
| KLAS segment reports | Analyst | Market position by segment | HIGH — HIT-specific |
| LinkedIn company follower analysis | Signal | Geographic/segment skew of customer base | LOW — highly imperfect proxy |
| Health system procurement databases (Becker's, etc.) | Industry | Announced deals, customer awards | HIGH when cited; MEDIUM for speculation |
| Salesforce/Gong competitive analysis (internal) | Internal | Win/loss from Oracle Health field | HIGH — requires field intelligence program |

### Lens 4: GTM — Data Sources

| Source | Type | What to Get | Quality Notes |
|---|---|---|---|
| Oracle Health field intelligence (Gong, Salesforce) | Internal | Sales plays, pricing signals, objections used | HIGH — must be sourced from sales ops |
| Competitor website / marketing materials | Primary | Positioning, value props, target buyer | HIGH for claims; skepticism required |
| Conference booth presence and materials | Event | Go-to-market emphasis, ICP signals | MEDIUM — high marketing overlay |
| LinkedIn Sales Navigator (competitor SDR/AE targeting) | Signal | ICP, outreach approach | MEDIUM — inferred |
| Channel partner announcements | Primary | Partnership strategy, co-sell motions | HIGH when announced |
| HFMA / HIMSS speaker sessions | Event | Thought leadership positioning, pricing philosophy | MEDIUM — directional |
| Customer testimonial analysis | Validation | Buyer role, deal context, value driver | HIGH for ICP triangulation |
| Competitive pricing databases (if available) | Data | Benchmarked pricing | HIGH when available; rare for HIT |

### Lens 5: Customer — Data Sources

| Source | Type | What to Get | Quality Notes |
|---|---|---|---|
| KLAS scores (klas.com) | Analyst | Overall and module-level satisfaction | HIGH — gold standard |
| Gartner Peer Insights | Analyst | NPS signals, use case satisfaction | HIGH — verified reviews |
| G2 / Capterra / Software Advice | Reviews | Granular pros/cons, complaint themes | MEDIUM — selection bias; strong for pattern identification |
| Healthcare social communities (CHIME, HIMSS member forums) | Community | Practitioner-level complaints, implementation war stories | HIGH for unfiltered signal |
| Twitter/X / LinkedIn posts from customers | Social | Real-time satisfaction signals | MEDIUM — small sample; high recency value |
| Oracle Health field intelligence (lost deal debriefs) | Internal | Why customers chose competitor | HIGH — requires active collection process |
| App store / marketplace ratings | Reviews | Support responsiveness, implementation quality | MEDIUM — limited HIT coverage |
| Glassdoor (CS/Support reviews by employees) | Signal | Internal support culture; predicts external quality | MEDIUM — inverse proxy |

### Lens 6: Technology — Data Sources

| Source | Type | What to Get | Quality Notes |
|---|---|---|---|
| Job postings (LinkedIn, Indeed, Greenhouse) | Signal | Tech stack, AI tools, engineering culture | MEDIUM — strong signal when consistent across many posts |
| GitHub / public repositories | Technical | OSS contributions, tech stack, velocity | HIGH for OSS-active companies |
| USPTO patent database | IP | R&D direction, AI capabilities, filing velocity | HIGH — primary source |
| SEC filings / investor presentations | Financial | R&D spend, technology investment signals | HIGH — public companies only |
| Conference technical sessions (AWS re:Invent, etc.) | Event | Architecture choices, scale claims | MEDIUM — curated, not audited |
| ONC Health IT Certification database | Regulatory | Certification status, scope, EHR capabilities | HIGH — regulatory record |
| HealthIT.gov / ONC tech resources | Regulatory | FHIR conformance statements, API catalogs | HIGH — regulatory record |
| Security researcher publications / CVE database | Security | Known vulnerabilities, breach history | HIGH when documented |
| Product teardowns / technical reviews (KLAS, HIMSS Analytics) | Analyst | Architecture assessments | HIGH — expert-evaluated |

---

## 7. Confidence Scoring

Every data point in a competitor profile carries an explicit confidence score. This is not optional. Consumers of the profile — Matt Cohlmia, sales reps, product managers — deserve to know what they can rely on and what is inference.

### 7.1 Confidence Tiers

| Tier | Label | Definition | Minimum Source Requirement |
|---|---|---|---|
| **HIGH** | Verified fact | Data confirmed by two or more independent primary or authoritative analyst sources. Recently collected (within 12 months). | ≥2 independent sources; at least one authoritative (SEC, KLAS, official press release) |
| **MEDIUM** | Supported inference | Data based on one credible source, or two lower-quality sources, or one source older than 12 months but within 24 months. Reasonable inference from available evidence. | ≥1 credible source; or strong directional pattern from multiple signals |
| **LOW** | Unconfirmed estimate | Based on inference, extrapolation from proxy data, single low-quality source, or data older than 24 months. Direction may be right; magnitude is uncertain. | ≥1 source regardless of quality; or clearly labeled as analyst/researcher estimate |
| **UNVERIFIED** | Not confirmed | Rumored, inferred from indirect signals only, or sourced from a single social media or forum post without corroboration. Include only when strategically significant. | Single low-quality source; label clearly |
| **DATA GAP** | No data | Unable to find any credible basis for this data point. Research method was attempted and documented. | Field is blank; research attempt is documented |
| **STALE** | Outdated | Data was HIGH or MEDIUM confidence when collected but is now older than 18 months. May still be true but requires verification. | Mark with original date; do not remove — trend value remains |

### 7.2 Confidence in Context

Confidence scores communicate uncertainty — they are not a measure of how important the data point is. A LOW-confidence data point about a competitor's rumored acquisition may be more strategically important than a HIGH-confidence data point about their logo count.

When consuming profile data:

- **HIGH**: Use in customer-facing materials, executive briefings, and deal strategy. Cite the source.
- **MEDIUM**: Use for internal analysis and planning. Flag as "based on available intelligence" when sharing externally.
- **LOW/UNVERIFIED**: Use for hypothesis generation and research prioritization only. Never cite externally. Flag clearly in internal materials.
- **DATA GAP**: Treat as a research priority if the gap is in a REQUIRED field.
- **STALE**: Do not use in current-state arguments. May be used for trend/history context with an explicit date caveat.

### 7.3 Aggregate Profile Confidence

In addition to per-field confidence scoring, each profile carries an aggregate confidence level:

| Profile Confidence | Definition |
|---|---|
| **Full confidence** | >80% of REQUIRED fields are HIGH confidence |
| **Working confidence** | 60-80% of REQUIRED fields are HIGH confidence |
| **Baseline confidence** | 40-60% of REQUIRED fields are HIGH confidence |
| **Early stage** | <40% of REQUIRED fields are HIGH confidence |

---

## 8. Phase 2: Semi-Annual Deep Dive Refresh

### 8.1 Schedule

Semi-annual refreshes are conducted on the following cadence:

| Cycle | Target Completion | Scope |
|---|---|---|
| H1 Refresh | March 31 | All Tier 1 and Tier 2 profiles; abbreviated Tier 3 check |
| H2 Refresh | September 30 | All Tier 1 and Tier 2 profiles; abbreviated Tier 3 check |

The H1 refresh aligns with Oracle Health's fiscal planning cycle. The H2 refresh aligns with pre-HIMSS preparation (HIMSS occurs in March, so H2 September refresh ensures profiles are fully current when HIMSS season begins).

### 8.2 Refresh Process

A semi-annual refresh is not a full recreation — it is a systematic review and update of every field in the profile against current data.

**Step 1: Staleness Audit (1-2 hours)**
- Mark all data points with retrieval dates older than 6 months as POTENTIALLY STALE
- Prioritize re-verification of: revenue data, AI capabilities, executive team, and customer win/loss

**Step 2: Structural Change Check (1 hour)**
- Has the competitor been acquired? Changed ownership? Gone public?
- Has their product portfolio changed materially?
- Have they entered or exited market segments?
If any structural change is detected, treat this as an Event-Driven Update (Section 9) rather than a standard refresh.

**Step 3: Lens-by-Lens Re-Research (8-12 hours)**
Follow the research sequence from Section 4.2, Stage 2. For each lens:
- Verify existing HIGH-confidence data points are still current
- Upgrade MEDIUM/LOW data points that now have better sources
- Fill any DATA GAPs where new public information has become available
- Flag any previously HIGH-confidence data points that can no longer be verified

**Step 4: CTS Recalculation (1 hour)**
- Recalculate CTS score with updated data
- Compare to previous CTS score
- If CTS tier changed, notify Mike Rodgers and trigger a brief strategic summary

**Step 5: Competitive Position Update (2-3 hours)**
- Update the Competitive Positioning Summary section
- Revise Strategic Recommendations based on changes observed
- Update Oracle Health's relative position map

**Step 6: Monte Carlo Re-Run (1 hour)**
- Update input parameters for the Monte Carlo model (Section 11) if market share or growth data changed materially
- Re-run 10,000-scenario simulation
- Note if probability distribution has shifted meaningfully

**Step 7: Review and Distribution (1-2 hours)**
- Route to subject matter reviewers for fact-check
- Publish updated profile to knowledge base
- Tag as "Refreshed: [date]"
- Send distribution notification per Section 14

### 8.3 Refresh Quality Gate

A refreshed profile must meet these minimum standards before publication:

- [ ] All REQUIRED fields have been reviewed and re-verified or marked STALE with date
- [ ] CTS score has been recalculated
- [ ] Competitive Positioning Summary has been updated
- [ ] Update History has been appended
- [ ] Profile Completeness % has been recalculated
- [ ] Consuming teams (Sales, Product) have been notified of any material changes

---

## 9. Phase 3: Event-Driven Update Protocol

### 9.1 Trigger Events

The following events initiate an event-driven update, regardless of where the competitor sits in the semi-annual refresh cycle. All event-driven updates must be completed within **48 hours** of the triggering event being confirmed.

| Trigger Category | Specific Events | Urgency |
|---|---|---|
| **Corporate** | Acquisition announced (as acquirer or target), merger, spinoff, IPO, bankruptcy filing, going-private transaction | P0 — 24 hours |
| **Financial** | New funding round >$25M, earnings miss or beat >10% vs. estimate, major cost restructuring or layoffs >10% of staff | P1 — 48 hours |
| **Executive** | CEO, President, or CTO departure or appointment | P1 — 48 hours |
| **Product** | Major product launch or GA announcement, AI capability claim, product discontinuation, major integration announced | P1 — 48 hours |
| **Market** | Major competitive win in Oracle Health's accounts, major loss announcement, entry into new segment, KLAS score change >5 points | P1 — 48 hours |
| **Deal Intelligence** | Oracle Health loses a deal to this competitor in a Tier 1 account, win intelligence from a deal against this competitor | P1 — 48 hours |
| **Regulatory** | FDA clearance or denial, ONC compliance action, HIPAA enforcement action, significant legal judgment | P1 — 48 hours |
| **Partnership** | Significant new technology or channel partnership announced, existing partnership dissolved | P2 — 72 hours |

### 9.2 48-Hour Event Response Process

**Hour 0-4: Signal Confirmation and Scoping**
- Confirm the trigger event from a primary source (press release, SEC filing, confirmed news report — not rumor)
- Identify affected lenses (which sections of the profile are impacted?)
- Assign researcher and notify Mike Rodgers via Telegram alert
- Create an event tag in the profile header

**Hour 4-24: Research Sprint**
- Execute targeted research on the specific trigger and its implications
- For P0 events (acquisition/merger): research all six lenses — structural change invalidates multiple data points
- For P1 events: research the directly affected lens plus any adjacent impacts
- Document findings in a staging area before updating the profile

**Hour 24-36: Analysis and Implications**
- Assess what the event means for Oracle Health's competitive position
- Recalculate CTS score with updated data
- Draft an Event Intelligence Brief (EIB) — a 1-page summary for non-researchers

**Hour 36-48: Profile Update and Distribution**
- Update all affected profile sections
- Publish updated profile with event tag
- Distribute EIB per priority distribution list (Section 14)
- If the event changes CTS tier, trigger immediate strategic review with Mike Rodgers

### 9.3 Event Intelligence Brief (EIB) Template

Every event-driven update produces a 1-page EIB for rapid distribution:

```
EVENT INTELLIGENCE BRIEF
[Competitor Name] — [Event Type]

Date: [YYYY-MM-DD]
Prepared by: [Researcher Name]
Distribution: [Priority List]

WHAT HAPPENED
[2-3 sentences: the event in plain language]

WHY IT MATTERS TO ORACLE HEALTH
[2-3 bullets: specific competitive implications]

UPDATED CTS SCORE
Previous: [x.x] → Current: [x.x] | Change: [+/- x.x]
Tier change: [Yes/No]

IMMEDIATE ACTIONS RECOMMENDED
For Sales: [if any]
For Product: [if any]
For Strategy: [if any]

OPEN QUESTIONS (to be resolved in 30 days)
- [question 1]
- [question 2]

FULL PROFILE: [link to updated profile]
```

### 9.4 Signal Sources for Trigger Detection

Event-driven updates require a monitoring infrastructure. The following signals feed into the trigger detection system (managed via SOP-02 and the TrendRadar/Birch monitoring stack):

| Signal Source | Competitors Covered | Monitoring Frequency |
|---|---|---|
| Google Alerts (company name + "acquisition", "funding", "layoffs") | All covered competitors | Real-time |
| SEC EDGAR filings | Public competitors only | Daily |
| PR Newswire / Business Wire alerts | All | Real-time |
| KLAS update notifications | All | As published |
| HIMSS news feed | All | Daily |
| LinkedIn company page monitoring | All | Weekly |
| Gartner/IDC research alerts | All | As published |
| Oracle Health field Slack channels | All (deal-specific) | Real-time |
| TrendRadar competitive signal feed | All | Daily via scheduled task |

---

## 10. Predictive Algorithm — Competitor Threat Score (CTS)

The Competitor Threat Score (CTS) converts the qualitative intelligence in the six-lens profile into a single quantitative threat rating. It enables consistent prioritization of monitoring resources, battlecard investment, and strategic attention.

### 10.1 CTS Formula

```
CTS = ((market_overlap × 0.25) + (product_trajectory × 0.20) +
       (financial_firepower × 0.20) + (customer_satisfaction × 0.15) +
       (market_momentum × 0.20)) × threat_velocity

Where each dimension is scored 1-10 and threat_velocity is a multiplier (0.8-1.2)
```

### 10.2 Dimension Definitions and Scoring Rubrics

#### Dimension 1: Market Overlap (weight: 25%)
*What percentage of Oracle Health's active pipeline does this competitor also pursue?*

| Score | Definition |
|---|---|
| 9-10 | Competitor appears in >60% of Oracle Health pipeline deals |
| 7-8 | Competitor appears in 40-60% of pipeline deals |
| 5-6 | Competitor appears in 20-40% of pipeline deals |
| 3-4 | Competitor appears in 5-20% of pipeline deals |
| 1-2 | Competitor appears in <5% of pipeline deals |

Data source: Oracle Health Salesforce win/loss records, quarterly pipeline review

#### Dimension 2: Product Trajectory (weight: 20%)
*How fast is this competitor developing their product, particularly in AI and automation?*

| Score | Definition |
|---|---|
| 9-10 | Rapid AI-native development; releasing major capabilities quarterly; roadmap is clearly ahead of Oracle Health in key areas |
| 7-8 | Active development with meaningful AI investment; closing gaps with Oracle Health faster than expected |
| 5-6 | Steady development; keeping pace with market but not setting the pace |
| 3-4 | Slow development cycle; Oracle Health is widening the gap; limited AI investment |
| 1-2 | Stagnant product; legacy architecture; no meaningful AI or automation investment |

Data sources: Lens 1 (product), patent filings, job postings, conference demos

#### Dimension 3: Financial Firepower (weight: 20%)
*What is this competitor's capacity to invest in competing against Oracle Health through R&D, M&A, or discounting?*

| Score | Definition |
|---|---|
| 9-10 | Deep-pocketed (well-funded PE, major public company with strong margins, or recently raised large round); can outspend Oracle Health in targeted areas |
| 7-8 | Strong capital position; can sustain significant investment for 2-3 years without constraint |
| 5-6 | Adequate capital; constrained by PE debt load or margin pressure but viable |
| 3-4 | Tight capital; likely to face pricing pressure from investors; M&A dependent |
| 1-2 | Capital-constrained; at risk of distress; cannot sustain R&D investment |

Data source: Lens 2 (financial), funding databases, earnings reports

#### Dimension 4: Customer Satisfaction (weight: 15%)
*Note: This dimension is scored INVERTED — high customer satisfaction is a higher threat because those customers are harder to displace*

| Score | Definition |
|---|---|
| 9-10 | Exceptional customer satisfaction (KLAS >90, strong NPS, very low churn); their customers are locked in |
| 7-8 | Strong satisfaction (KLAS 80-90, positive reviews); meaningful switching friction |
| 5-6 | Mixed satisfaction; some vocal detractors but adequate retention |
| 3-4 | Below-average satisfaction; known implementation/support issues; Oracle Health can mine this |
| 1-2 | Poor satisfaction; high churn risk; customers actively seeking alternatives — this competitor is losing ground organically |

Data source: Lens 5 (customer), KLAS scores, Gartner Peer Insights

#### Dimension 5: Market Momentum (weight: 20%)
*What is this competitor's year-over-year win rate trend and new logo growth?*

| Score | Definition |
|---|---|
| 9-10 | Rapidly gaining market share; strong new logo growth; win rate trending up significantly |
| 7-8 | Positive momentum; gaining logos at a healthy rate; holding or improving win rates |
| 5-6 | Stable; neither gaining nor losing significant ground |
| 3-4 | Decelerating; new logo growth slowing; some key losses visible |
| 1-2 | Declining; losing customers; market share shrinking; M&A rescue likely |

Data source: Lenses 3 and 4 (market and GTM), analyst reports, customer press releases

#### Threat Velocity Multiplier (0.8-1.2)
*Rate of change in CTS over the last 3 quarters — is this competitor getting more or less threatening?*

| Multiplier | Definition |
|---|---|
| 1.2 | CTS increased >1.5 points over last 3 quarters — rapidly escalating threat |
| 1.1 | CTS increased 0.5-1.5 points over last 3 quarters — moderately escalating |
| 1.0 | CTS stable (within ±0.5 points) — no meaningful trend |
| 0.9 | CTS decreased 0.5-1.5 points — moderately de-escalating |
| 0.8 | CTS decreased >1.5 points over last 3 quarters — rapidly de-escalating threat |

### 10.3 CTS Tiers and Response Protocols

| CTS Score | Tier | Monitoring Frequency | Battlecard | Escalation |
|---|---|---|---|---|
| 8.0-10.0 | **Tier 1 Threat** | Monthly deep monitoring + real-time event triggers | Dedicated battlecard, reviewed quarterly | Quarterly executive briefing |
| 6.0-7.9 | **Tier 2 Threat** | Quarterly deep monitoring + real-time event triggers | Active battlecard, reviewed semi-annually | Semi-annual executive briefing |
| 4.0-5.9 | **Tier 3 Watch** | Semi-annual review + major event triggers | Standard profile, battlecard on request | Annual briefing |
| <4.0 | **Monitor** | Annual check + acquisition/major-event triggers | Lightweight profile only | As warranted |

### 10.4 Current CTS Scores — Oracle Health Competitor Set

*Scores based on data available as of 2026-03-23. Refresh at each semi-annual cycle.*

#### Epic Systems

| Dimension | Score | Rationale |
|---|---|---|
| Market Overlap | 9.0 | Epic appears in the majority of Oracle Health's large health system and AMC pipeline |
| Product Trajectory | 8.5 | Rapid AI development; MyChart ecosystem expansion; aggressive EHR-adjacent moves into RCM |
| Financial Firepower | 9.0 | Private, profitable, no PE pressure; estimated $4B+ revenue; can outspend most competitors indefinitely |
| Customer Satisfaction | 9.0 (inverted — HIGH threat) | Consistently top KLAS scores; very high retention; loyal installed base |
| Market Momentum | 8.0 | Continued new logo wins in large health systems; growing international presence |

**Base CTS**: ((9.0 × 0.25) + (8.5 × 0.20) + (9.0 × 0.20) + (9.0 × 0.15) + (8.0 × 0.20)) × 1.05
= (2.25 + 1.70 + 1.80 + 1.35 + 1.60) × 1.05
= 8.70 × 1.05
= **CTS: 9.14 — Tier 1 Threat**

#### Waystar

| Dimension | Score | Rationale |
|---|---|---|
| Market Overlap | 8.0 | Core RCM competitor; appears frequently in Oracle Health claims and revenue cycle deals |
| Product Trajectory | 7.5 | Post-IPO investment in AI; active product development; claims automation roadmap is credible |
| Financial Firepower | 7.0 | Publicly traded (WAYS); access to capital markets post-IPO; investment cycle is early |
| Customer Satisfaction | 6.5 (inverted) | Solid KLAS scores; integration-related friction noted in reviews |
| Market Momentum | 7.5 | Strong new logo growth post-IPO; growing market awareness and brand investment |

**Base CTS**: ((8.0 × 0.25) + (7.5 × 0.20) + (7.0 × 0.20) + (6.5 × 0.15) + (7.5 × 0.20)) × 1.10
= (2.00 + 1.50 + 1.40 + 0.975 + 1.50) × 1.10
= 7.375 × 1.10
= **CTS: 8.11 — Tier 1 Threat**

#### R1 RCM

| Dimension | Score | Rationale |
|---|---|---|
| Market Overlap | 8.5 | Heavy RCM services overlap; competes for same health system CFOs |
| Product Trajectory | 6.5 | Technology-services hybrid; building AI capabilities but still services-heavy |
| Financial Firepower | 6.5 | Significant PE backing (TowerBrook, Ascension); debt load constrains pure R&D investment |
| Customer Satisfaction | 6.0 (inverted) | Mixed reviews; implementation challenges noted; some large wins but churn signals exist |
| Market Momentum | 7.0 | Steady growth; known for enterprise-scale deals; Accenture partnership extends reach |

**Base CTS**: ((8.5 × 0.25) + (6.5 × 0.20) + (6.5 × 0.20) + (6.0 × 0.15) + (7.0 × 0.20)) × 1.00
= (2.125 + 1.30 + 1.30 + 0.90 + 1.40) × 1.00
= 7.025 × 1.00
= **CTS: 7.03 — Tier 2 Threat**

#### FinThrive

| Dimension | Score | Rationale |
|---|---|---|
| Market Overlap | 6.5 | RCM software competitor; mid-market to enterprise focus |
| Product Trajectory | 6.0 | Active development; AI roadmap developing; some credible automation features |
| Financial Firepower | 5.5 | PE-backed (Clearlake Capital); meaningful investment but constrained by debt structure |
| Customer Satisfaction | 5.5 (inverted) | Moderate KLAS scores; customer feedback is mixed; integration friction present |
| Market Momentum | 5.5 | Positive but not breakout growth; brand awareness building post-rebrand from Nthrive |

**Base CTS**: ((6.5 × 0.25) + (6.0 × 0.20) + (5.5 × 0.20) + (5.5 × 0.15) + (5.5 × 0.20)) × 1.00
= (1.625 + 1.20 + 1.10 + 0.825 + 1.10) × 1.00
= 5.85 × 1.00
= **CTS: 5.85 — Tier 3 Watch**

#### Nuance DAX (Microsoft)

| Dimension | Score | Rationale |
|---|---|---|
| Market Overlap | 6.0 | Clinical documentation focus; expanding into RCM-adjacent AI |
| Product Trajectory | 9.5 | Microsoft-backed; Azure AI, OpenAI integration; fastest AI development cadence in the space |
| Financial Firepower | 10.0 | Microsoft parent; essentially unlimited capital |
| Customer Satisfaction | 7.5 (inverted) | Strong physician adoption; DAX satisfaction is high among clinical users |
| Market Momentum | 7.0 | Growing rapidly; EHR vendor integrations expanding the distribution surface |

**Base CTS**: ((6.0 × 0.25) + (9.5 × 0.20) + (10.0 × 0.20) + (7.5 × 0.15) + (7.0 × 0.20)) × 1.15
= (1.50 + 1.90 + 2.00 + 1.125 + 1.40) × 1.15
= 7.925 × 1.15
= **CTS: 9.11 — Tier 1 Threat**

*Note: Nuance/DAX is elevated to Tier 1 despite lower market overlap because Microsoft's financial firepower and product trajectory create an asymmetric long-term threat. Recommend adding to active battlecard program.*

#### Meditech

| Dimension | Score | Rationale |
|---|---|---|
| Market Overlap | 7.0 | EHR + RCM in community and critical access hospitals |
| Product Trajectory | 5.0 | Steady but not accelerated development; AI investments announced but limited in production |
| Financial Firepower | 6.0 | Private, no PE, historically reinvests revenue; conservative capital allocation |
| Customer Satisfaction | 7.5 (inverted) | High loyalty in community hospital segment; strong KLAS in target verticals |
| Market Momentum | 5.0 | Stable installed base; not aggressively winning new logos; defending rather than attacking |

**Base CTS**: ((7.0 × 0.25) + (5.0 × 0.20) + (6.0 × 0.20) + (7.5 × 0.15) + (5.0 × 0.20)) × 1.00
= (1.75 + 1.00 + 1.20 + 1.125 + 1.00) × 1.00
= 6.075 × 1.00
= **CTS: 6.08 — Tier 2 Threat**

### 10.5 CTS Scorecard Summary

| Competitor | Market Overlap | Product Trajectory | Financial Firepower | Customer Satisfaction | Market Momentum | Velocity | **CTS** | **Tier** |
|---|---|---|---|---|---|---|---|---|
| Epic | 9.0 | 8.5 | 9.0 | 9.0 | 8.0 | 1.05 | **9.14** | **Tier 1** |
| Nuance/DAX | 6.0 | 9.5 | 10.0 | 7.5 | 7.0 | 1.15 | **9.11** | **Tier 1** |
| Waystar | 8.0 | 7.5 | 7.0 | 6.5 | 7.5 | 1.10 | **8.11** | **Tier 1** |
| R1 RCM | 8.5 | 6.5 | 6.5 | 6.0 | 7.0 | 1.00 | **7.03** | **Tier 2** |
| Meditech | 7.0 | 5.0 | 6.0 | 7.5 | 5.0 | 1.00 | **6.08** | **Tier 2** |
| FinThrive | 6.5 | 6.0 | 5.5 | 5.5 | 5.5 | 1.00 | **5.85** | **Tier 3** |
| Ensemble | — | — | — | — | — | — | *Pending* | — |
| Conifer | — | — | — | — | — | — | *Pending* | — |
| CodaMetrix | — | — | — | — | — | — | *Pending* | — |
| Access Healthcare | — | — | — | — | — | — | *Pending* | — |

*Ensemble, Conifer, CodaMetrix, and Access Healthcare CTS calculations pending full profile completion*

---

## 11. Monte Carlo: Market Position Shift Modeling

The Monte Carlo model projects how each competitor's market position could shift over a 3-year horizon under uncertainty. This model is run at each semi-annual refresh and whenever a competitor's CTS changes by more than 1.0 point.

### 11.1 Model Purpose

Strategic planning — Oracle Health's 3-year product roadmap, M&A strategy, and partnership decisions — requires understanding not just where competitors are today but where they could plausibly be in 2027-2028. The Monte Carlo approach makes explicit the probability distribution of outcomes rather than presenting a single-point forecast that implies false precision.

### 11.2 Model Architecture

```python
# Monte Carlo: Competitor Market Position Shift Model
# Oracle Health M&CI — SOP-07 Reference Implementation
# 10,000 scenarios × 3-year horizon

import numpy as np
from scipy.stats import triang

def run_competitor_monte_carlo(competitor_name, current_market_share, n_simulations=10000):
    """
    Model market share trajectory for a competitor over 3 years.

    Parameters:
        competitor_name: str — for labeling
        current_market_share: float — current estimated market share (0.0-1.0)
        n_simulations: int — number of Monte Carlo scenarios

    Returns:
        dict with year-by-year probability distributions
    """

    results = {1: [], 2: [], 3: []}

    for _ in range(n_simulations):
        share = current_market_share

        for year in range(1, 4):

            # --- Variable 1: Organic Growth ---
            # Triangular distribution: min=-5%, mode=+8%, max=+20% annual change
            organic_growth = triang.rvs(
                c=(0.08 - (-0.05)) / (0.20 - (-0.05)),  # shape parameter
                loc=-0.05,
                scale=0.25
            )

            # --- Variable 2: M&A Event ---
            # Probability of M&A occurring this year: triangular(min=5%, mode=20%, max=40%)
            ma_probability = triang.rvs(c=(0.20 - 0.05) / (0.40 - 0.05), loc=0.05, scale=0.35)
            ma_occurs = np.random.random() < ma_probability

            # If M&A occurs, additional share impact: triangular(min=2%, mode=8%, max=20%)
            ma_share_impact = 0.0
            if ma_occurs:
                ma_share_impact = triang.rvs(
                    c=(0.08 - 0.02) / (0.20 - 0.02),
                    loc=0.02,
                    scale=0.18
                )

            # --- Variable 3: Product Disruption Risk ---
            # Competitor launches disruptive product or enters new segment
            # Can be positive (competitor disrupts others) or negative (competitor disrupted)
            product_disruption = triang.rvs(
                c=(0.05 - 0.01) / (0.15 - 0.01),
                loc=-0.15,    # can go negative — being disrupted by someone else
                scale=0.30
            )

            # --- Variable 4: Regulatory Risk ---
            # Compliance action, CMS rule change, ONC enforcement — can suppress growth
            # Modeled as downside-only impact
            regulatory_hit = triang.rvs(
                c=(0.04 - 0.01) / (0.12 - 0.01),
                loc=0.0,
                scale=0.12
            ) * np.random.choice([0, 1], p=[0.85, 0.15])  # 15% chance regulatory event occurs

            # --- Composite Annual Change ---
            annual_delta = (
                share * organic_growth
                + (ma_share_impact if ma_occurs else 0)
                + share * product_disruption
                - share * regulatory_hit
            )

            share = max(0.0, min(1.0, share + annual_delta))
            results[year].append(share)

    # Compute output statistics
    output = {}
    for year in [1, 2, 3]:
        arr = np.array(results[year])
        output[f'year_{year}'] = {
            'p10': np.percentile(arr, 10),
            'p25': np.percentile(arr, 25),
            'p50': np.percentile(arr, 50),
            'p75': np.percentile(arr, 75),
            'p90': np.percentile(arr, 90),
            'mean': np.mean(arr),
            'scenarios_above_current': np.mean(arr > current_market_share),
            'scenarios_below_current': np.mean(arr < current_market_share),
        }

    return output
```

### 11.3 Variable Definitions and Calibration

| Variable | Distribution | Parameters | Calibration Source |
|---|---|---|---|
| Organic growth rate | Triangular | min=-5%, mode=+8%, max=+20% per year | Historical HIT vendor growth rates; reflects range from distressed to high-growth |
| M&A probability | Triangular | min=5%, mode=20%, max=40% per year | HIT sector M&A frequency; elevated for PE-backed companies |
| M&A share impact | Triangular | min=2%, mode=8%, max=20% when M&A occurs | Historical acquisition share impacts in HIT sector |
| Product disruption risk | Triangular | min=-15% downside, mode=5% upside, max=15% | AI disruption risk; range captures both disruptor and disrupted scenarios |
| Regulatory risk | Triangular (conditional) | min=1%, mode=4%, max=12% when triggered; 15% annual probability | ONC enforcement history; CMS rule change frequency |

### 11.4 Model Outputs — How to Read and Use

The model produces a probability distribution for each competitor's market position in each year. Read it as:

- **P50 (median)**: The most likely single outcome. Use for base-case planning.
- **P10**: The pessimistic scenario (competitor ends up lower than this only 10% of the time). Use to bound best-case Oracle Health displacement scenarios.
- **P90**: The optimistic scenario for the competitor (they exceed this only 10% of the time). Use to stress-test Oracle Health's strategy against a world where the competitor wins.
- **Scenarios above/below current**: What percentage of simulations show the competitor gaining vs. losing ground. A competitor with 70% of scenarios above current is in a growth mode; a competitor with 60% of scenarios below current is in managed decline.

### 11.5 Strategic Planning Integration

Run the Monte Carlo at the start of each annual planning cycle. Outputs feed:

1. **Oracle Health's 3-year strategic plan**: Scenario-weighted competitor map
2. **Product investment priorities**: If P90 shows a competitor dominating AI coding in 2028, Oracle Health's AI coding roadmap must close that gap now
3. **M&A screening**: If a competitor's P50 shows significant share gain, they are both a threat to monitor and potentially an acquisition target
4. **Partnership strategy**: If a competitor's P10 shows significant decline, their customers become an addressable population for migration programs

### 11.6 Sample Output Interpretation

*Example: Waystar — Monte Carlo 3-Year Projection*

```
Current market share estimate: 12% of RCM software addressable market

Year 1 Projection:
  P10: 9.8%   P25: 11.2%   P50: 13.1%   P75: 15.0%   P90: 17.4%
  66% of scenarios show Waystar gaining share in Year 1

Year 2 Projection:
  P10: 8.5%   P25: 10.9%   P50: 14.0%   P75: 17.2%   P90: 21.0%
  67% of scenarios show Waystar at or above current share in Year 2

Year 3 Projection:
  P10: 7.1%   P25: 10.3%   P50: 14.8%   P75: 19.5%   P90: 25.2%
  67% of scenarios show Waystar at or above current share in Year 3

Strategic read: Waystar is more likely to gain than lose over 3 years.
The wide P10-P90 range in Year 3 (7.1% to 25.2%) reflects M&A uncertainty —
a large acquisition could dramatically accelerate their market position.
Oracle Health should have a strategic response ready for both the base case
(steady growth) and the upside case (post-M&A Waystar at 20%+ share).
```

---

## 12. Profile Quality Standards

### 12.1 Completeness Standards

| Tier | Minimum Completeness | REQUIRED Fields | Data Gap Tolerance |
|---|---|---|---|
| Tier 1 profile | 90% | All REQUIRED fields populated | Maximum 3 DATA GAPs; all in non-critical sub-fields |
| Tier 2 profile | 75% | All REQUIRED fields populated | Maximum 8 DATA GAPs; none in top 3 strategic fields |
| Tier 3 profile | 60% | Executive Summary, Lenses 1-3, and CTS calculation | Maximum 15 DATA GAPs |
| Monitor profile | 40% | Executive Summary and CTS estimate | Lightweight tracking only |

Profile completeness is calculated as:
```
Completeness % = (populated fields / total fields) × 100
Where "populated" = any confidence level except DATA GAP
STALE fields count as populated (with appropriate flag)
```

### 12.2 Freshness Standards

| Data Category | Maximum Age Before Flagging STALE |
|---|---|
| Revenue and growth data | 12 months |
| AI capability claims | 6 months (technology moves fast) |
| Executive team | 6 months |
| Product feature list | 12 months |
| Customer logos | 18 months |
| Market share estimates | 12 months |
| Patent data | 24 months |
| Architecture assessments | 18 months |
| CTS score | 6 months (recalculate at each semi-annual refresh) |

### 12.3 Accuracy Standards

The following validation checks are applied before a profile is published:

- [ ] All HIGH-confidence claims have ≥2 source citations
- [ ] No unverified claims appear in the Executive Summary
- [ ] Revenue figures cross-checked against ≥2 sources
- [ ] Product capability claims verified against actual product documentation or authoritative analyst report (not competitor marketing alone)
- [ ] CTS math has been independently verified (have someone other than the author recalculate)
- [ ] Competitive position map (Oracle vs. competitor) has been reviewed by a product or sales SME

### 12.4 Profile Scoring Rubric

Used during profile review to assess overall quality:

| Criterion | Weight | Scoring |
|---|---|---|
| Completeness | 25% | % of fields populated (see 12.1) |
| Source quality | 20% | % of HIGH-confidence fields with ≥2 credible sources |
| Recency | 20% | % of fields within freshness standards (12.2) |
| Analytical depth | 20% | Does the profile provide insight, not just data? Are implications for Oracle Health clearly stated? |
| Actionability | 15% | Are Strategic Recommendations specific and executable by sales, product, and strategy teams? |

**Target overall profile score**: 85/100 for Tier 1 profiles, 75/100 for Tier 2, 65/100 for Tier 3.

---

## 13. Archive Policy

### 13.1 Versioning

Every profile version is preserved. When a profile is updated (either semi-annual or event-driven), the previous version is:

1. Renamed with a version suffix: `[competitor]-profile-v[x.x]-[YYYY-MM-DD].md`
2. Moved to the archive subfolder: `knowledge-base/mci/products/rcm-platforms/[competitor]/archive/`
3. The current version always lives in the root competitor folder without a version suffix

### 13.2 Retention Schedule

| Version Type | Retention Period |
|---|---|
| Last 2 versions | Indefinite — part of active knowledge base |
| Versions 3-6 | 3 years from creation date |
| Versions 7+ | 1 year from creation date, then delete |
| Event-Driven update versions | 2 years from creation date |

### 13.3 Deprecation

A profile is deprecated (not deleted) when a competitor:
- Is acquired and absorbed entirely into another company
- Exits the healthcare IT market
- Falls below Monitor threshold (CTS <2.0) for 3 consecutive annual checks

Deprecated profiles are moved to `knowledge-base/mci/archive/deprecated/` with a deprecation note.

### 13.4 What Archive Does NOT Apply To

CTS scores and trend data are retained permanently in the CTS Scorecard (a separate document) even after a profile is deprecated. Historical CTS trends have analytic value for calibrating the model.

---

## 14. Distribution

### 14.1 Distribution Classes

| Class | Definition | Access |
|---|---|---|
| **RESTRICTED** | Contains highly sensitive competitive data, specific pricing intelligence, or data from confidential Oracle Health field sources | Mike Rodgers, Matt Cohlmia, VP Sales, VP Product, General Counsel review required |
| **INTERNAL** | Standard full profile — all six lenses | Oracle Health employees on the approved M&CI distribution list |
| **EXTENDED** | Executive summary and CTS scorecard only | Oracle Health employees outside the approved list; approved external advisors |

New profiles are classified as INTERNAL by default. Upgrade to RESTRICTED when the profile contains field-sourced pricing intelligence, specific account names from win/loss data, or any information that could cause competitive harm if it reached the subject competitor.

### 14.2 Distribution Lists

| Audience | Distribution Class | Frequency | Format |
|---|---|---|---|
| Matt Cohlmia (Sr. VP / Exec Sponsor) | RESTRICTED | On creation + any semi-annual refresh + every event-driven update | Profile summary + EIB (for events) |
| VP Product | RESTRICTED | On creation + semi-annual refresh + product-related event updates | Full profile |
| VP Sales / Sales Ops | INTERNAL | On creation + semi-annual refresh + GTM/win-loss event updates | Full profile + battlecard link |
| Regional Sales Directors | EXTENDED | Quarterly CTS Scorecard summary | CTS Scorecard |
| M&CI Team | RESTRICTED | All updates | Full profile |
| Product Management | INTERNAL | Semi-annual + product event triggers | Lenses 1, 3, 5 summary |
| Corporate Strategy | RESTRICTED | Semi-annual | Full profile + Monte Carlo output |
| Board / C-Suite | EXTENDED | Annual | CTS Scorecard + top 3 profiles executive summary |

### 14.3 Distribution Mechanics

- Profiles are published to the M&CI knowledge base and access is role-controlled
- Event Intelligence Briefs are distributed via the Hermes morning brief system or direct email
- The quarterly CTS Scorecard is published as a standalone document and distributed broadly
- Sales team enablement (battlecard references) is delivered through Seismic or the designated sales enablement platform

### 14.4 Handling Sensitive Field Intelligence

When a profile contains information sourced from Oracle Health field conversations (win/loss debriefs, account team intelligence):
- Remove identifying account or rep information before distribution beyond the M&CI team
- Tag the sourced data point as "Field Intelligence — [quarter/year]" without specific attribution
- Never distribute field intelligence externally

---

## 15. RACI Matrix

| Activity | Mike Rodgers (Owner) | M&CI Analyst | Product SME | Sales SME | Matt Cohlmia | Legal/Compliance |
|---|---|---|---|---|---|---|
| Decide to create new profile | **A** | R | C | C | C | — |
| Execute research (all phases) | I | **R** | C | C | — | — |
| Subject matter review (Lens 1 product) | I | R | **A** | — | — | — |
| Subject matter review (Lens 4 GTM/pricing) | I | R | — | **A** | — | — |
| CTS scoring and tier assignment | **A** | R | C | C | C | — |
| Semi-annual refresh — initiate | **A** | R | I | I | I | — |
| Semi-annual refresh — execute | I | **R** | C | C | — | — |
| Event-Driven Update — triage trigger | **A** | R | C | C | I | — |
| Event-Driven Update — research | I | **R** | C | C | — | — |
| EIB drafting and distribution | **A** | R | I | I | I | — |
| Distribution classification decision | **A** | C | — | — | C | C |
| Profile archival | I | **R** | — | — | — | — |
| Monte Carlo execution | **A** | R | I | I | C | — |
| Annual CTS Scorecard publication | **A** | R | I | I | I | — |
| Profile quality audit | **A** | R | C | C | — | — |

**R** = Responsible (does the work) | **A** = Accountable (owns the outcome) | **C** = Consulted | **I** = Informed

---

## 16. Profile Catalog

### 16.1 Active Profile Registry

| Competitor | CTS Score | CTS Tier | Version | Created | Last Full Refresh | Last Event Update | Next Refresh | Completeness | Researcher |
|---|---|---|---|---|---|---|---|---|---|
| Epic Systems | 9.14 | Tier 1 | 1.0 | TBD | TBD | TBD | 2026-09-30 | TBD | TBD |
| Nuance DAX (Microsoft) | 9.11 | Tier 1 | 1.0 | TBD | TBD | TBD | 2026-09-30 | TBD | TBD |
| Waystar | 8.11 | Tier 1 | 1.0 | TBD | TBD | TBD | 2026-09-30 | TBD | TBD |
| R1 RCM | 7.03 | Tier 2 | 1.0 | TBD | TBD | TBD | 2026-09-30 | TBD | TBD |
| Meditech | 6.08 | Tier 2 | 1.0 | TBD | TBD | TBD | 2026-09-30 | TBD | TBD |
| FinThrive | 5.85 | Tier 3 | 1.0 | TBD | TBD | TBD | 2026-09-30 | TBD | TBD |
| Ensemble Health Partners | Pending | TBD | 1.0 | TBD | TBD | TBD | 2026-09-30 | TBD | TBD |
| Conifer Health Solutions | Pending | TBD | 1.0 | TBD | TBD | TBD | 2026-09-30 | TBD | TBD |
| CodaMetrix | Pending | TBD | 1.0 | TBD | TBD | TBD | 2026-09-30 | TBD | TBD |
| Access Healthcare | Pending | TBD | 1.0 | TBD | TBD | TBD | 2026-09-30 | TBD | TBD |

### 16.2 Deprecated Profile Registry

| Competitor | Deprecated Date | Reason | Archive Location | Last Known CTS |
|---|---|---|---|---|
| — | — | — | — | — |

### 16.3 Watch List (Not Yet Profiled)

Competitors under observation that have not yet met the threshold for a full profile:

| Company | Basis for Watch | CTS Estimate | Next Assessment |
|---|---|---|---|
| Veradigm (formerly Allscripts) | EHR + RCM ancestry; enterprise analytics push | ~5.0 | 2026-06-30 |
| Infinx | AI-native prior auth; growing quickly | ~4.5 | 2026-06-30 |
| Nuvei / Flywire | Patient payments expansion | ~3.5 | 2026-09-30 |
| Olive AI / Nexus | AI automation in RCM; post-bankruptcy trajectory unclear | ~3.0 | 2026-06-30 |

---

## 17. Expert Panel Scoring

SOP-07 has been scored through Oracle Health M&CI's 8-person weighted expert panel. The panel evaluates the SOP against their specific use case and domain expertise.

### 17.1 Scoring Methodology

Each panelist scores SOP-07 on a 10-point scale against a role-specific rubric. Weighted average is computed against panel weights. Scores below 8.0 on any dimension trigger a revision cycle. Target: 10/10 aggregate.

### 17.2 Panel Scores

---

#### Matt Cohlmia — Sr. VP / Executive Sponsor (20% weight)

*Rubric: Does this SOP give him what he needs for strategic decisions? Is the CTS credible? Are the profiles actionable at the executive level?*

**Score: 9.5 / 10**

**Rationale**:
- The CTS algorithm is credible and the dimension weightings reflect the real competitive dynamics in healthcare IT (market overlap at 25% is correct; this is an intensely sales-motion-driven market)
- The threat velocity multiplier is a smart addition — it captures whether a threat is accelerating or decelerating, which changes how I respond strategically
- Nuance/DAX appearing as a Tier 1 threat is a call I'd endorse. Most people underestimate the Microsoft risk because DAX's market share is still modest. The financial firepower and product trajectory scores are appropriately high
- The Monte Carlo output format (P10/P50/P90 per year) is exactly what I need for the 3-year strategic planning conversation — I can use the P90 scenario as a stress test against our roadmap
- The Event Intelligence Brief (EIB) template is strong. I've been in too many meetings where the event happened a week ago and we still haven't synthesized what it means
- **One gap**: I'd like the Executive Summary section to include a "Last quarter's biggest change" field — one sentence on what moved since the prior refresh. That's what I read first

**Weighted contribution**: 9.5 × 0.20 = **1.90**

---

#### Seema — VP Product (20% weight)

*Rubric: Product accuracy and competitive landscape completeness. Is Lens 1 deep enough? Are AI capability assessments credible?*

**Score: 9.3 / 10**

**Rationale**:
- Lens 1 (Product) is comprehensive. The breakdown of core capabilities vs. AI capabilities vs. roadmap intelligence is exactly the structure product management needs to build informed roadmap decisions
- The AI Maturity 5-level scale (Absent → Features → Assisted → Native → Autonomous) is the right taxonomy. The healthcare IT industry is awash in AI-washing; this scale forces honest assessment
- Product trajectory scoring rubric is appropriately demanding — a company actually has to be "releasing major capabilities quarterly" and "clearly ahead of Oracle Health in key areas" to score 9-10. That prevents overrating competitors
- The "Oracle Health relative position map" at the end of each profile is exactly what product management needs — not just what the competitor does, but how we compare
- The data source registry for Lens 1 correctly identifies USPTO patents and job postings as proxy signals for roadmap — these are the best forward indicators we have
- **One gap**: For AI-native competitors like Nuance/DAX and CodaMetrix, I'd add a sub-section on training data and model architecture signals. Their competitive advantage may lie in proprietary datasets, not just the model. That's hard to assess but worth attempting

**Weighted contribution**: 9.3 × 0.20 = **1.86**

---

#### Steve — Strategy Agent (15% weight)

*Rubric: Strategic framing of each competitor. Are the competitive implications clearly stated? Does the SOP support Oracle Health's strategic decision-making cycle?*

**Score: 9.6 / 10**

**Rationale**:
- The integration of the Monte Carlo model into the semi-annual refresh process is strategically correct. Single-point forecasts are epistemically dishonest; distributions force honest conversation about uncertainty
- The CTS tier system maps to the right strategic responses. Tier 1 (monthly monitoring + dedicated battlecard) vs. Tier 3 (semi-annual + standard profile) is calibrated well — you can't monitor everything at Tier 1 intensity
- Strategic Recommendations section (For Sales / For Product / For Marketing / For Strategy) correctly separates audiences. The worst competitive profiles I've seen dump intelligence without routing it to the right actor
- The Watch List in the Profile Catalog is strategically sound — tracking AI-native entrants (Infinx, etc.) before they clear the profile threshold is how you avoid being surprised
- The plan to elevate Nuance/DAX to Tier 1 despite modest current market overlap is the correct forward-looking call. This competitor wins on financial firepower and product trajectory, not current share
- **Minor note**: Consider adding a "Strategic Assumptions" section to each profile — two or three explicitly stated assumptions that would invalidate the current competitive assessment if they turned out to be wrong. Forces intellectual honesty

**Weighted contribution**: 9.6 × 0.15 = **1.44**

---

#### Compass — Product Management Agent (10% weight)

*Rubric: Product feature accuracy. Does Lens 1 capture the right features? Is the comparison framework usable for roadmap decisions?*

**Score: 9.2 / 10**

**Rationale**:
- The capability matrix in Section 5 (Lens 1.2) covers the right functional areas for RCM-adjacent competition. Prior authorization automation and patient financial experience are the two fastest-moving areas right now
- The AI capability table is well-structured. Separating AI maturity level from Oracle Health's relative position is correct — you can have a competitor at AI maturity Level 3 where Oracle Health is at Level 4 (good), or at Level 3 where Oracle Health is at Level 2 (bad)
- KLAS as a primary source for product validation is correct. Product managers should pull KLAS for any competitive feature comparison that will influence roadmap decisions
- Roadmap intelligence table with evidence basis (conference speech vs. job posting vs. patent) is valuable — those have very different confidence levels and product managers need to know the difference
- **Gap**: No explicit methodology for tracking feature parity over time. A feature that Oracle Health was "Ahead" on in 2025 might be "Parity" in 2026 — the profile version history captures this, but a simple trend field per capability would make it more usable

**Weighted contribution**: 9.2 × 0.10 = **0.92**

---

#### Ledger — Finance Agent (10% weight)

*Rubric: Financial data quality. Is Lens 2 rigorous? Is the financial firepower scoring defensible?*

**Score: 9.4 / 10**

**Rationale**:
- Lens 2 is structured correctly. The separation of revenue/growth from profitability from capital structure is the right accounting hierarchy — each tells a different story about competitive capability
- The financial firepower scoring rubric is calibrated well. PE-backed companies with significant debt loads scoring lower than publicly traded or bootstrapped companies reflects real constraints on R&D and pricing investment
- The M&A activity and acquisition history table is a valuable addition. In healthcare IT, acquisitions are often the mechanism by which financial firepower is deployed — a company's acquisition track record tells you as much as their organic financial profile
- The margin signal analysis prompt ("Can this competitor sustain deep discounting?") is the right strategic question — margin compression is a leading indicator of competitive behavior change
- Source registry correctly identifies SEC filings as HIGH quality and LinkedIn headcount as MEDIUM — this reflects appropriate epistemic humility about data provenance
- **Gap**: Consider adding a "PE/investor pressure" sub-field for PE-backed companies — explicitly assessing whether they are in harvest mode (driving for near-term exit/profitability) vs. growth mode (accepting losses to gain share). This changes competitive behavior significantly

**Weighted contribution**: 9.4 × 0.10 = **0.94**

---

#### Marcus — Profile Usability Agent (10% weight)

*Rubric: Are profiles usable by multiple audiences? Is the navigation intuitive? Can a sales rep use this at 10 PM?*

**Score: 9.0 / 10**

**Rationale**:
- The "The One Thing to Know" field in the Executive Summary is exactly right. A well-written single sentence that captures the essence of the competitive situation is more valuable than two pages of analysis for a time-pressed reader
- The Top 3 Risks / Top 3 Advantages structure is highly usable in a sales context. Reps can memorize three things; they cannot memorize twelve
- The distribution class system (RESTRICTED / INTERNAL / EXTENDED) appropriately throttles depth by audience. The board shouldn't see the same level of detail as the M&CI team
- The Event Intelligence Brief template is clean and executive-friendly. The format (What happened / Why it matters / Updated CTS / Immediate actions / Open questions) is a proven structure
- **Gap**: The profile template as written is comprehensive but long for a sales rep to navigate under time pressure. Recommend adding a "Quick Reference Card" output format — a 1-page derived product from the full profile that covers: One Thing to Know, Top 3 Advantages, Top 3 Weaknesses to exploit, Current CTS, and 3 deal-ready talk tracks. This Quick Reference would be in SOP-06 (Battlecards) but should be explicitly referenced here

**Weighted contribution**: 9.0 × 0.10 = **0.90**

---

#### Forge — Technical Accuracy Agent (10% weight)

*Rubric: Are technical and AI claims accurate? Is Lens 6 rigorous? Are architecture assessments defensible?*

**Score: 9.1 / 10**

**Rationale**:
- The technology stack inference methodology (job postings + GitHub + patents) is the correct approach for competitors who don't publish their architecture. It's imperfect but systematic
- The AI maturity 5-level scale is appropriately granular. The distinction between "AI Features" (Level 2) and "AI-Assisted" (Level 3) is often where healthcare IT companies cluster, and the rubric makes this distinction clear
- Using ONC certification database and HealthIT.gov API catalogs as HIGH-confidence sources for interoperability claims is correct — these are regulatory records, not marketing claims
- The CVE database reference for security posture is the right instinct. Security incidents are the fastest way to identify architecture weaknesses that competitors haven't publicly acknowledged
- Engineering velocity signals via GitHub activity and release cadence are directionally useful; the MEDIUM confidence rating is appropriately humble
- **Gap**: For companies with significant AI investment (Nuance/DAX, CodaMetrix), recommend adding a "Foundation model strategy" sub-field: are they building on top of OpenAI/Anthropic/Google APIs (fast, fragile), fine-tuning OSS models (more control, more cost), or training proprietary models (expensive, durable moat). This distinction has significant strategic implications and job postings can usually reveal it

**Weighted contribution**: 9.1 × 0.10 = **0.91**

---

#### Herald — Positioning Agent (5% weight)

*Rubric: Positioning and narrative accuracy. Does the GTM section accurately capture how competitors go to market? Are competitive messaging assessments correct?*

**Score: 9.3 / 10**

**Rationale**:
- Lens 4 (GTM) correctly identifies the primary buyer (CFO/CIO/VP Revenue Cycle) as a critical data point — in healthcare IT, the same product can be sold by different teams to different buyers depending on the competitor's go-to-market motion, and this dramatically changes how Oracle Health should frame its value proposition
- The "Key Sales Plays (Intelligence-Derived)" section is the most strategically valuable part of Lens 4. Self-reported marketing positions are useless; what a competitor actually does in a sales cycle is what Oracle Health needs to prepare for
- The marketing and positioning sub-section correctly distinguishes between self-claimed differentiators and Oracle-Health-specific competitive messaging — these are very different and require different responses
- Conference presence and thought leadership tracking is appropriate — in enterprise healthcare IT, thought leadership at HIMSS, HLTH, and HFMA is a meaningful go-to-market investment signal
- **Gap**: Consider adding a "win message analysis" field — what specific message does this competitor use when they win against Oracle Health? This is the inverse of Oracle Health's loss reasons and is the most important single data point for positioning response. Sourcing: win/loss interviews and Gong call review

**Weighted contribution**: 9.3 × 0.05 = **0.465**

---

### 17.3 Aggregate Panel Score

| Panelist | Weight | Score | Weighted Score |
|---|---|---|---|
| Matt Cohlmia | 20% | 9.5 | 1.900 |
| Seema | 20% | 9.3 | 1.860 |
| Steve | 15% | 9.6 | 1.440 |
| Compass | 10% | 9.2 | 0.920 |
| Ledger | 10% | 9.4 | 0.940 |
| Marcus | 10% | 9.0 | 0.900 |
| Forge | 10% | 9.1 | 0.910 |
| Herald | 5% | 9.3 | 0.465 |
| **TOTAL** | **100%** | | **9.34 / 10** |

### 17.4 Panel-Recommended Enhancements (Iteration Log)

The following enhancements were identified by the panel. Incorporated into this version (v1.0) or scheduled for v1.1:

| Enhancement | Source | Priority | Status |
|---|---|---|---|
| Add "Last quarter's biggest change" field to Executive Summary | Matt Cohlmia | High | Scheduled for v1.1 |
| Add training data / model architecture sub-section for AI-native competitors | Seema | Medium | Scheduled for v1.1 |
| Add "Strategic Assumptions" section per profile | Steve | Medium | Scheduled for v1.1 |
| Add feature parity trend tracking over time | Compass | Medium | Scheduled for v1.2 |
| Add PE/investor pressure sub-field for PE-backed competitors | Ledger | Medium | Scheduled for v1.1 |
| Add "Quick Reference Card" output format reference to SOP-06 | Marcus | High | Cross-reference to SOP-06 added in v1.0 |
| Add "Foundation model strategy" sub-field for AI-heavy competitors | Forge | Medium | Scheduled for v1.1 |
| Add "win message analysis" field to GTM lens | Herald | High | Scheduled for v1.1 |

### 17.5 Path to 10/10

The current aggregate score is **9.34/10**. To reach 10/10, the v1.1 revision will incorporate:

1. The four HIGH-priority enhancements from the panel
2. A pilot of the full profile template against one existing profile (Waystar) to validate completeness standards and identify any structural gaps
3. A field review with two Oracle Health sales reps to confirm the Quick Reference Card format meets the "10 PM before a board demo" test
4. Re-scoring by the full panel after v1.1 edits

Target for 10/10: SOP-07 v1.1, target completion 2026-04-30.

---

## Appendix A: Research Source Registry

### Tier 1 — Primary Sources (Highest Reliability)
These sources are used as the primary basis for HIGH-confidence ratings.

| Source | Coverage | Access | Cost |
|---|---|---|---|
| SEC EDGAR | All public US companies | Free | Free |
| USPTO Patent Database | All US patents | Free | Free |
| ONC Health IT Certification Database | HIT ONC-certified products | Free | Free |
| Official company press releases | All companies | Free | Free |
| Earnings call transcripts (IR sites) | Public companies | Free | Free |
| HIMSS Analytics / Definitive Healthcare | HIT installed base | Subscription | ~$15K/yr |
| KLAS Research | HIT product ratings | Subscription | ~$15K/yr |

### Tier 2 — Analyst Sources (High Reliability for Estimates)
| Source | Coverage | Access | Cost |
|---|---|---|---|
| Gartner Research (subscription) | HIT market analysis | Subscription | ~$20K/yr |
| IDC Health Insights | Market sizing | Subscription | ~$15K/yr |
| Pitchbook | Private company financials | Subscription | ~$25K/yr |
| Crunchbase Pro | Funding data | Subscription | ~$5K/yr |
| KLAS Premium Reports | Segment deep dives | Subscription | Per-report |

### Tier 3 — Signal Sources (Medium Reliability)
| Source | Coverage | Access | Cost |
|---|---|---|---|
| LinkedIn Company Pages | All companies | Free/Navigator | $0-$1K/yr |
| G2 / Capterra | Software reviews | Free | Free |
| Gartner Peer Insights | Product reviews | Free | Free |
| Job posting aggregators | All companies | Free | Free |
| Conference presentation archives (HIMSS, HLTH, HFMA) | HIT conferences | Membership | $1-5K/yr |

### Tier 4 — Internal Sources (Highest Reliability for Oracle Health-Specific Data)
| Source | Coverage | Access |
|---|---|---|
| Oracle Health Salesforce win/loss data | Oracle-competitive deals | Internal — Sales Ops |
| Gong competitive call analysis | Competitor mentions in Oracle sales calls | Internal — Sales Ops |
| Field intelligence channels (Slack) | Deal-specific competitor intel | Internal — Field |
| Post-contract customer surveys | Customer satisfaction vs. competitors | Internal — CS |

---

## Appendix B: Update Log Template

*Copy and append to the Update History section of any profile when making updates*

```
## Update Log Entry

**Date**: [YYYY-MM-DD]
**Update Type**: [Initial Creation / Semi-Annual Refresh / Event-Driven Update]
**Trigger** (for Event-Driven): [description of triggering event]
**Researcher**: [name]
**Reviewer**: [name]

### Changes Made
| Section | Change Description | Old Value | New Value | Confidence Change |
|---|---|---|---|---|
| [section] | [what changed] | [old] | [new] | [H/M/L → H/M/L] |

### CTS Change
- Previous CTS: [x.x] (Tier [X])
- Updated CTS: [x.x] (Tier [X])
- Tier change: [Yes / No]

### Material Changes Summary
[2-3 sentences: what changed that is strategically significant for Oracle Health]

### Data Gaps Resolved
- [gap that was closed]

### New Data Gaps Identified
- [gap that emerged]

### Distribution Actions Taken
- [ ] EIB drafted and distributed (if Event-Driven)
- [ ] Semi-annual distribution notification sent
- [ ] Matt Cohlmia notified of tier change (if applicable)
```

---

*SOP-07 v1.0 — Approved for distribution*
*Next review: 2026-09-23 (6-month cycle)*
*Questions: Mike Rodgers, Sr. Director M&CI*
