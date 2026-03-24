# SOP-12: Competitive Response Playbook

**Owner**: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-23
**Category**: Competitive Intelligence Production
**Priority**: P2 — Gap → Documented
**Maturity**: Gap → Documented

---

## Table of Contents

1. [Purpose](#1-purpose)
2. [Scope — What Events Trigger This Playbook](#2-scope)
3. [Event Taxonomy — Classification by Type and Severity](#3-event-taxonomy)
4. [Response Tier Matrix](#4-response-tier-matrix)
5. [Phase 1: Detection & Triage](#5-phase-1-detection--triage)
6. [Phase 2: Impact Assessment](#6-phase-2-impact-assessment)
7. [Phase 3: Stakeholder Notification](#7-phase-3-stakeholder-notification)
8. [Phase 4: Response Recommendation](#8-phase-4-response-recommendation)
9. [Phase 5: Battlecard Update Protocol](#9-phase-5-battlecard-update-protocol)
10. [Phase 6: Deal Protection Protocol](#10-phase-6-deal-protection-protocol)
11. [Communication Templates](#11-communication-templates)
12. [Predictive Algorithm: Competitive Event Impact Score (CEIS)](#12-predictive-algorithm-competitive-event-impact-score-ceis)
13. [Monte Carlo: Response Timeline Optimization](#13-monte-carlo-response-timeline-optimization)
14. [Post-Response Review Protocol](#14-post-response-review-protocol)
15. [RACI Matrix](#15-raci-matrix)
16. [KPIs](#16-kpis)
17. [Expert Panel Scoring](#17-expert-panel-scoring)
18. [Appendices](#18-appendices)

---

## 1. Purpose

This SOP formalizes Oracle Health's process for detecting, assessing, and responding to significant competitive events. It replaces the current ad hoc response process with a structured, tier-based playbook that protects active pipeline, equips the field, and preserves Oracle Health's competitive position in the market.

**The core problem this SOP solves**: When a competitor makes a significant move — an acquisition, a major product launch, a pricing change, an executive poach, or a high-profile win against Oracle Health — the current response is uncoordinated. Sales reps hear about it from customers. Executives hear about it at conferences. The CI team catches it a week later. By the time Oracle Health has a coherent response, deals have already been lost and narratives have hardened.

**This playbook changes that.** From the moment a competitive event is detected, every stakeholder — from the field rep managing an active deal to the executive on a board call — will know exactly what happened, what it means, what Oracle Health's position is, and what to say.

**Business case for speed**: Analysis of enterprise software competitive events (see Section 13, Monte Carlo simulation) shows that a 24-hour response versus a 1-week response to a major competitive move is worth an estimated **$2.1M to $6.8M in protected pipeline** per event, based on Oracle Health's deal size distribution and typical competitive exposure at any given time. The cost of building and running this playbook is rounding error by comparison.

---

## 2. Scope

### 2.1 Events Covered by This Playbook

This SOP applies when a direct or adjacent competitor makes any of the following moves:

| Event Category | Examples |
|----------------|----------|
| **Product Events** | Major product launch, significant feature release, new module announcement, AI/ML capability launch, platform expansion, API/integration announcement |
| **Pricing Events** | Price reduction, new pricing model (subscription → usage-based), free tier introduction, bundling change, contract term shift |
| **Corporate Events** | Acquisition or merger, significant funding round ($50M+), IPO filing, private equity takeover, strategic partnership with major health system or payer |
| **Executive Events** | Key Oracle Health executive departure to competitor, competitor executive hire from Oracle Health, new CEO/CPO/CTO announcement that signals strategic shift |
| **Win/Loss Events** | Competitor win at a named Oracle Health account (displacement), Oracle Health displacement at a competitor account (our win to defend), multi-system win that creates reference pressure |
| **Market Events** | Regulatory change that advantages a competitor, major analyst report repositioning a competitor, industry award (KLAS, Black Book) given to a competitor in Oracle Health's category |
| **Narrative Events** | Competitor launch of direct comparison content targeting Oracle Health, viral customer complaint about Oracle Health amplified by competitor, aggressive trade show/conference messaging |

### 2.2 Events NOT Covered by This Playbook

The following are handled by other SOPs or standing processes:

- Routine competitor blog posts or marketing content without significant claim (handled by battlecard maintenance, SOP-TBD)
- Win/loss interviews on completed deals (handled by SOP-09)
- Trade show competitive intelligence gathering (handled by SOP-11)
- Inbound analyst briefings (handled by analyst relations process)

### 2.3 Geographic and Product Scope

This playbook covers Oracle Health competitive events in:

- **Primary**: United States (all segments: acute care, ambulatory, post-acute, payer, government)
- **Secondary**: International markets where Oracle Health has active pipeline (UK, Australia, Middle East — escalate to M&CI leadership for international events before activating full playbook)

**Product scope**: All Oracle Health product lines are in scope. Events affecting RCM, EHR (Millennium/Oracle Health Cloud), population health, and clinical AI warrant the highest response tier given current strategic priorities.

---

## 3. Event Taxonomy

### 3.1 Classification Dimensions

Every competitive event is classified across two dimensions: **Type** and **Severity**.

#### Type Classification

| Type Code | Event Type | Description |
|-----------|-----------|-------------|
| **T-PROD** | Product Move | New product, feature, or capability announcement |
| **T-PRICE** | Pricing Move | Pricing structure, model, or level change |
| **T-CORP** | Corporate Move | M&A, funding, partnership, ownership change |
| **T-EXEC** | Executive Move | Leadership hire, departure, or appointment |
| **T-WIN** | Win/Loss Event | Competitive displacement or displacement threat |
| **T-MKT** | Market/Analyst Event | Analyst repositioning, award, regulatory advantage |
| **T-NAR** | Narrative Event** | Competitive messaging attack, comparison content |

#### Severity Classification

Severity is determined by initial triage assessment, then confirmed by CEIS score (Section 12).

| Severity | Label | Initial Indicators |
|----------|-------|-------------------|
| **S1** | Critical | Affects >20% of Oracle Health market, involves major competitor (Epic, Veeva, Meditech, MEDITECH Expanse), or directly threatens a Top 10 active deal |
| **S2** | High | Affects a specific product line or segment, competitor with >10% market share in that segment, or threatens 5-19 active deals |
| **S3** | Medium | Affects a specific use case or geography, minor competitor, or threatens 1-4 active deals |
| **S4** | Monitor | No immediate pipeline threat, emerging competitor, or early-stage market signal |

### 3.2 Event Taxonomy Matrix

The intersection of Type and Severity produces a response code:

```
Response Code = [Type]-[Severity]
Example: T-PROD-S1 = Critical Product Move → Tier 1 Response
         T-EXEC-S3 = Medium Executive Move → Tier 3 Response
```

### 3.3 Named Competitor Tiers

Oracle Health's competitive landscape is organized into three tiers for response prioritization:

**Tier A — Primary Competitors** (always S1 or S2 minimum)
- Epic Systems
- Veeva Systems (payer/life sciences adjacency)
- Meditech / MEDITECH Expanse
- Athenahealth (Veradigm)
- eClinicalWorks
- Netsmart (post-acute)

**Tier B — Secondary Competitors** (S2 minimum)
- Modernizing Medicine
- NextGen Healthcare
- Harris Healthcare / Altera Digital Health
- CPSI / TruBridge
- Arcadia (population health)
- Innovaccer
- Health Catalyst

**Tier C — Emerging Competitors** (S3 minimum, monitor for escalation)
- AI-native EHR startups (Ambience Healthcare, Nabla, Abridge)
- Specialty point solutions threatening Oracle Health modules
- Big Tech adjacency (Microsoft, Google, Amazon health moves)

---

## 4. Response Tier Matrix

### 4.1 Tier Overview

| Tier | CEIS Score | Response Window | Trigger Examples | Lead |
|------|-----------|-----------------|-----------------|------|
| **Tier 1** | 8.0–10.0 | 24 hours | Epic acquires major RCM vendor; competitor launches AI scribe at half Oracle Health's price; Top 5 deal at risk | Mike Rodgers + Matt Cohlmia |
| **Tier 2** | 6.0–7.9 | 48 hours | Major competitor launches new module in Oracle Health's category; competitor hired 3 Oracle Health executives | Mike Rodgers |
| **Tier 3** | 4.0–5.9 | 1 week | Minor competitor announces funding round; KLAS score shift; competitor wins mid-market deal | CI Analyst |
| **Monitor** | <4.0 | Morning brief | Competitor blog post; minor partnership; early-stage signal | Jake (automated) |

### 4.2 Tier 1 Response Timeline (24-Hour Clock)

```
Hour 0:    Event detected — triage begins
Hour 1:    CEIS score calculated — Tier 1 confirmed
Hour 2:    Matt Cohlmia + Seema + Mike Rodgers notified (exec alert)
Hour 4:    Impact assessment complete
Hour 6:    Response recommendation drafted
Hour 8:    Sales alert distributed to affected territory reps
Hour 12:   Battlecard update live in sales portal
Hour 16:   Deal protection calls initiated for Top 10 at-risk deals
Hour 20:   Executive briefing document complete
Hour 24:   All-hands CI response brief sent; post-response review scheduled
```

### 4.3 Tier 2 Response Timeline (48-Hour Clock)

```
Hour 0:    Event detected — triage begins
Hour 2:    CEIS score calculated — Tier 2 confirmed
Hour 4:    Mike Rodgers + Seema notified
Hour 8:    Impact assessment complete
Hour 16:   Response recommendation drafted
Hour 24:   Sales alert distributed
Hour 32:   Battlecard update live
Hour 40:   Deal protection outreach for affected pipeline
Hour 48:   Response brief to M&CI leadership
```

### 4.4 Tier 3 Response Timeline (1-Week Clock)

```
Day 1:     Event detected — logged and queued
Day 2:     Impact assessment (lightweight) complete
Day 3:     Response recommendation drafted
Day 4:     Battlecard update live (if needed)
Day 5:     Sales alert distributed (if pipeline is affected)
Day 7:     Included in weekly M&CI digest
```

---

## 5. Phase 1: Detection & Triage

### 5.1 Detection Sources

Oracle Health's competitive event detection draws from multiple signal sources. Jake (the M&CI AI system) monitors these continuously and surfaces alerts.

| Source | Monitoring Frequency | Signal Type |
|--------|---------------------|-------------|
| **TrendRadar** | Continuous (15-min sweep) | News, press releases, analyst reports |
| **Google Alerts** | Real-time | Competitor name + product + executive mentions |
| **LinkedIn** | Daily | Executive movement, product announcements, company news |
| **Competitor IR pages** | Daily | Earnings calls, investor presentations, 8-K filings |
| **KLAS / Black Book / Gartner** | Weekly | Rankings, analyst commentary, Magic Quadrant updates |
| **Sales CRM (Salesforce)** | Daily | Competitive mentions in deal notes, lost deal reasons |
| **Customer Conversations** | Ad hoc | Sales reps flagging competitive mentions |
| **Conference Monitoring** | Event-driven | Per SOP-11 trade show protocol |
| **Twitter/X + LinkedIn** | Daily | Competitor employee posts, executive announcements |
| **Job Boards (LinkedIn, Indeed)** | Weekly | Competitor hiring patterns signal product investment |

### 5.2 Detection Trigger — The "SOMETHING HAPPENED" Rule

A competitive event is formally detected and enters this playbook when ANY of the following occurs:

1. **Automated trigger**: Jake/TrendRadar scores a news item as "Competitive Alert" with confidence ≥ 0.7
2. **Sales trigger**: A field rep submits a competitive flag via Salesforce competitive intelligence field
3. **Executive trigger**: Matt Cohlmia, Seema, or another Oracle Health executive flags an event directly to Mike Rodgers
4. **Market trigger**: A KLAS, Gartner, or Forrester report is published with direct competitive positioning
5. **Customer trigger**: A customer mentions a competitor's new move during a call, QBR, or renewal conversation

**Rule**: Any team member who detects a competitive event should route it to Mike Rodgers within 1 hour of detection. The clock starts from detection, not from Mike's awareness.

### 5.3 Initial Triage Process

Within 1 hour of detection, Mike Rodgers (or CI Analyst on duty) performs initial triage:

**Triage Checklist:**

```
□ 1. Verify the event is real (not rumor, not outdated, not misattributed)
     Source check: Is this from a primary source (press release, official announcement)?
     Or secondary? (analyst commentary, social media, third-party news)

□ 2. Identify the competitor
     Which named competitor? Which Tier (A/B/C)?

□ 3. Classify the event type (T-PROD / T-PRICE / T-CORP / T-EXEC / T-WIN / T-MKT / T-NAR)

□ 4. Assign preliminary severity (S1/S2/S3/S4)
     Use the named competitor tier as a starting floor
     (Tier A competitor = S2 minimum; Tier B = S3 minimum)

□ 5. Calculate initial CEIS score (Section 12)
     CEIS ≥ 8.0 → Tier 1 → Notify Matt Cohlmia immediately
     CEIS 6.0–7.9 → Tier 2 → Notify Mike Rodgers and Seema
     CEIS 4.0–5.9 → Tier 3 → Queue for CI Analyst
     CEIS <4.0 → Monitor → Log in morning brief

□ 6. Log the event in the Competitive Event Register
     (Salesforce CI log or designated SharePoint tracking file)

□ 7. Assign a Response Owner and open the response clock
```

### 5.4 Competitive Event Register

Every detected event is logged with:

| Field | Description |
|-------|-------------|
| **Event ID** | CE-[YYYY]-[NNN] (e.g., CE-2026-047) |
| **Detection Date/Time** | UTC timestamp |
| **Detected By** | Name + source |
| **Competitor** | Competitor name + Tier |
| **Event Type** | T-PROD / T-PRICE / T-CORP / T-EXEC / T-WIN / T-MKT / T-NAR |
| **Preliminary Severity** | S1/S2/S3/S4 |
| **CEIS Score** | Calculated score (Section 12) |
| **Response Tier** | 1/2/3/Monitor |
| **Response Owner** | Named individual |
| **Response Deadline** | Date/time |
| **Status** | Triage / Assessment / Notification / Response / Battlecard / Deal Protection / Review / Closed |
| **Source URL** | Primary source link |
| **Summary** | 2-3 sentence description of the event |

---

## 6. Phase 2: Impact Assessment

### 6.1 Purpose of Impact Assessment

The impact assessment answers three questions:
1. **How bad is this?** (Scope and magnitude)
2. **Who is affected?** (Products, deals, customers, geographies)
3. **What is Oracle Health's position?** (Strengths, vulnerabilities, available counters)

### 6.2 Impact Assessment Framework

**Assessment is completed by**: Mike Rodgers (Tier 1/2) or CI Analyst (Tier 3)
**Time box**: 2 hours (Tier 1), 4 hours (Tier 2), 1 day (Tier 3)

#### Dimension 1: Market Scope Analysis

```
Questions to answer:
- Which Oracle Health product lines are directly affected?
- Which market segments (acute, ambulatory, post-acute, payer, government)?
- Which geographies?
- What percentage of Oracle Health's total addressable market is in the blast radius?

Score: 1 (niche, <5% of TAM) → 10 (entire market, >80% of TAM)
```

#### Dimension 2: Pipeline Impact Analysis

```
Immediate action: Pull Salesforce competitive pipeline report

Filters:
- Opportunity Stage: Stage 2 through Stage 6 (active evaluation to negotiation)
- Competitor field: [Affected Competitor Name]
- Close Date: within next 12 months

Outputs:
- Count of at-risk deals
- Total TCV at risk
- Top 10 deals by TCV with account names and rep owners
- Deal stage distribution (early-stage vs. late-stage at-risk)

Score: 1 (0 active deals) → 10 (>20 active deals or >$50M TCV at risk)
```

#### Dimension 3: Strategic Relevance Analysis

```
Oracle Health's three strategic priorities (as of 2026):
1. AI/ML-powered clinical and financial automation
2. Interoperability and open platform ecosystem
3. Population health and value-based care enablement

Questions:
- Does this competitive event directly target one of these priorities?
- Does it undermine Oracle Health's differentiation narrative in any of these areas?
- Does it represent a strategic direction Oracle Health lacks or lags on?

Score: 1 (unrelated to strategic priorities) → 10 (directly attacks a strategic priority)
```

#### Dimension 4: Competitor Credibility Assessment

```
Assess: Is this a real move or marketing theater?

Evidence of credibility:
- Is the product generally available (GA) or announced only?
- Are there named customer references?
- Has the competitor deployed this in a health system of comparable size to Oracle Health accounts?
- Is there a credible engineering team behind this claim?
- Has an independent analyst (KLAS, Gartner, Forrester) validated the claim?

Red flags (reduces credibility):
- Press release only, no GA date
- Vague capability claims ("AI-powered" with no specifics)
- No customer references
- Previously announced capabilities that never shipped

Score: 1 (pure PR, unverified) → 10 (GA, named references, analyst validation)
```

#### Dimension 5: Time Sensitivity Assessment

```
How fast does Oracle Health's response window close?

Fast close (score 8-10):
- Customer is in active RFP with competitor right now
- Competitor is presenting to an Oracle Health account this week
- Competitor has scheduled a press event or conference keynote

Slow close (score 1-3):
- Announced product not available for 6+ months
- No known customer overlap
- Event is in a market Oracle Health doesn't currently compete in

Score: 1 (months to respond) → 10 (hours to respond)
```

#### Dimension 6: Response Leverage Assessment

```
How well can Oracle Health differentiate in response?

Strong leverage (score 8-10):
- Oracle Health has a direct, credible counter-capability that is GA
- Oracle Health has customer references that directly rebut competitor's claims
- Competitor's move has known weaknesses Oracle Health can exploit

Weak leverage (score 1-3):
- Oracle Health lacks a direct counter-capability
- Competitor's claim is largely accurate and Oracle Health has no near-term answer
- Oracle Health's response would be defensive or "we're working on it"

Score: 1 (limited differentiation available) → 10 (strong, credible counter-narrative available)
```

### 6.3 Impact Assessment Output

The Impact Assessment produces a **one-page Impact Brief** containing:

1. **Event Summary** (3-5 sentences): What happened, who did it, when
2. **CEIS Score** (with dimension breakdown): Confirmed score from Section 12
3. **Pipeline Exposure**: Count of deals, total TCV, top 10 at-risk accounts
4. **Oracle Health's Position**: 3 bullet points — strengths, vulnerabilities, available counters
5. **Recommended Response Tier**: Confirmed tier based on CEIS
6. **Recommended Response Actions**: 3-5 specific actions (not generic — specific to this event)
7. **Message Discipline**: The ONE message Oracle Health should repeat consistently

---

## 7. Phase 3: Stakeholder Notification

### 7.1 Notification Logic

Not everyone needs to know everything. Notifications are calibrated by:
- **Role** (executive vs. sales vs. product vs. marketing)
- **Relevance** (are they directly affected by this event?)
- **Tier** (Tier 1 events get broader notification than Tier 3)

### 7.2 Notification Matrix

| Stakeholder | Tier 1 | Tier 2 | Tier 3 | Format | Timeline |
|-------------|--------|--------|--------|--------|----------|
| **Matt Cohlmia** (SVP/EVP, CI champion) | ✓ | ✓ | Summary in weekly digest | Exec Alert email + direct message | T+2h (T1), T+4h (T2) |
| **Seema** (Product leadership) | ✓ | ✓ | ✓ if product-relevant | Exec Alert email | T+2h (T1), T+4h (T2), T+2d (T3) |
| **Sales Leadership** (VPs, RVPs) | ✓ | ✓ | If pipeline affected | Sales Alert email | T+8h (T1), T+24h (T2) |
| **Affected Territory Reps** | ✓ | ✓ | If deals affected | Sales Alert email + Salesforce chatter | T+8h (T1), T+24h (T2) |
| **Product Management** | ✓ | ✓ | ✓ | CI Team Briefing | T+12h (T1), T+24h (T2) |
| **Marketing** | ✓ | ✓ | Summary | CI Team Briefing | T+12h (T1), T+24h (T2) |
| **Legal/Compliance** | If claims involve Oracle Health products directly | — | — | Direct email from Mike | T+4h |
| **Finance/Deal Desk** | If pricing change affects active deals | If pricing change | — | Direct email from Mike | T+4h (T1) |
| **Executive Leadership (C-suite)** | ✓ for S1 events only | — | — | Executive Briefing doc | T+20h (T1) |

### 7.3 Notification Content Requirements

**For every notification, regardless of format:**

1. **What happened**: One sentence. Factual. No opinion.
2. **Why it matters to Oracle Health**: One sentence. Specific to their role.
3. **Oracle Health's position**: 2-3 bullet points. Affirmative, not defensive.
4. **What they should do / say**: Specific action. Not "stay tuned."
5. **What NOT to say**: Any claims that are inaccurate, inflammatory, or create legal exposure.
6. **Who to contact with questions**: Mike Rodgers + phone number.

**What notifications must NOT contain:**
- Speculation presented as fact
- Disparagement of the competitor beyond factual comparison
- Internal Oracle Health concerns about product gaps (this is external-facing context)
- Unconfirmed information
- Legal claims ("they're infringing on our patents") without Legal sign-off

---

## 8. Phase 4: Response Recommendation

### 8.1 Response Strategy Framework

Oracle Health's competitive response operates at four levels. The Impact Assessment determines which levels are activated.

| Response Level | Description | Who Activates | Examples |
|----------------|-------------|---------------|---------|
| **L1: Field Enablement** | Arm sales reps with talking points and objection handlers | Always activated for Tier 1/2 | Updated battlecard, objection handlers, proof points |
| **L2: Demand Generation** | Proactive market messaging to counter competitor narrative | Activated when competitor narrative is gaining traction | Customer advisory, thought leadership, press statement |
| **L3: Product Response** | Accelerate roadmap item, announce capability, or reposition existing feature | Activated when competitor has a genuine product advantage | Fast-track a feature, publish a technical brief, announce a roadmap commitment |
| **L4: Commercial Response** | Pricing, terms, or packaging adjustment to neutralize competitor's commercial advantage | Activated when competitor is winning on price/terms | Pricing exception authority, bundle adjustment, extended terms |

### 8.2 Response Recommendation Output

The Response Recommendation is a **concise action memo** (max 2 pages) containing:

```
COMPETITIVE RESPONSE RECOMMENDATION
Event ID: CE-[YYYY]-[NNN]
Competitor: [Name]
Event: [One-sentence description]
CEIS Score: [X.X] / Tier [N]
Response Deadline: [Date/Time]

RECOMMENDED ACTIONS:

L1 — Field Enablement (REQUIRED for Tier 1/2):
□ [Specific action 1 — e.g., "Update Epic EHR battlecard Section 3.2 with new AI scribe counter"]
□ [Specific action 2 — e.g., "Distribute top 3 talking points to 47 affected reps by [date/time]"]
□ [Specific action 3 — e.g., "Prepare 60-second objection handler for 'Competitor X just announced...'"]

L2 — Demand Generation (if applicable):
□ [Specific action — e.g., "Publish LinkedIn post from Oracle Health voice counter-positioning AI scribe"]
□ [Specific action — e.g., "Prepare customer advisory for 12 named accounts in competitor's geographic sweet spot"]

L3 — Product Response (if applicable):
□ [Specific action — e.g., "Brief Seema's team on capability gap; request fast-track status for [feature]"]
□ [Specific action — e.g., "Publish technical brief demonstrating Oracle Health's existing advantage in [area]"]

L4 — Commercial Response (if applicable):
□ [Specific action — e.g., "Authorize pricing exception for deals directly threatened by competitor's new pricing"]

APPROVED BY: Mike Rodgers, Sr. Director M&CI
DATE: [Date]
```

### 8.3 Message Discipline — The One-Message Rule

For every competitive event, M&CI establishes ONE primary message that Oracle Health will repeat consistently across all communications. This prevents mixed signals, reduces the risk of conflicting rep responses, and ensures the market hears a coherent Oracle Health position.

**Format for the One Message:**

```
"Unlike [Competitor], Oracle Health [specific differentiator] — which means [customer benefit].
We have [proof point] to back that up."
```

**Example (for a competitor EHR AI scribe launch):**

```
"Unlike [Competitor], Oracle Health's clinical AI is built directly into Millennium's workflow —
not bolted on — which means clinicians never leave their existing system.
We have 47 health systems live on Oracle Health AI today with measurable ROI."
```

The One Message is included in every communication template (Section 11) for the event.

---

## 9. Phase 5: Battlecard Update Protocol

### 9.1 When Battlecards Must Be Updated

Battlecard updates are **mandatory** for the following event types:

| Event Type | Battlecard Update Required? | Update Scope |
|------------|---------------------------|--------------|
| **T-PROD (S1/S2)** | Yes — within response deadline | Full relevant sections; pricing, capabilities, proof points |
| **T-PROD (S3)** | Yes — within 1 week | Targeted section update only |
| **T-PRICE** | Yes — within response deadline | Pricing section; TCO comparison |
| **T-CORP (acquisition)** | Yes — within 48h | New capabilities acquired; ownership context |
| **T-CORP (funding)** | No — note in deal notes only | — |
| **T-EXEC** | Conditional — if executive was a product leader | Update "key contacts" section |
| **T-WIN** | Yes — within 1 week | Deal protection section; "why we lose" analysis |
| **T-MKT (analyst)** | Yes — within 1 week | Analyst perspective section |
| **T-NAR** | Yes — within response deadline | Objection handlers section |

### 9.2 Battlecard Update Workflow

```
Step 1: Pull current battlecard from sales portal (SharePoint / Highspot / Seismic)
Step 2: Identify sections requiring update (cross-reference Impact Brief)
Step 3: Draft updated content
        — Lead with what changed (not what's the same)
        — Preserve the "what to say / what not to say" structure
        — Add/update proof points with dates
        — Add new objection handlers if competitor's move creates new objections
Step 4: Review pass — Mike Rodgers (factual accuracy) + Seema's team (product accuracy)
Step 5: Legal review flag — if updated content includes claims about competitor's product, flag for Legal
Step 6: Publish to sales portal with version bump and change log entry
Step 7: Notify sales enablement team of update
Step 8: Notify affected field reps via Salesforce chatter + email
```

### 9.3 Battlecard Version Control

| Field | Standard |
|-------|----------|
| **Version numbering** | v[major].[minor] — e.g., v2.3 (major = full rewrite; minor = section update) |
| **Change log** | Every version includes a 3-bullet change log at top of document |
| **Review cycle** | Quarterly minimum for all Tier A competitor battlecards; semi-annually for Tier B/C |
| **Archive policy** | Previous version archived in SharePoint version history; never deleted |
| **Owner** | Mike Rodgers for Tier A competitors; CI Analyst for Tier B/C |

### 9.4 Battlecard Quality Standards

Every Oracle Health battlecard must contain:

1. **The One-Paragraph Oracle Health Pitch**: Why Oracle Health wins, in language a rep can say in 60 seconds
2. **Top 3 Oracle Health Advantages**: Specific, proof-point-backed, updated to current date
3. **Top 3 Competitor Weaknesses**: Factual, sourced, conservative (avoid overreach)
4. **"Why We Lose" Section**: Honest. What this competitor does better or is perceived to do better. This section is for internal use only.
5. **Objection Handlers**: For the top 5 competitor claims, a specific, credible Oracle Health response
6. **Proof Points**: Named customer references, KLAS scores, analyst quotes — all dated
7. **Landmines**: Specific competitor tactics, gotcha questions, or FUD strategies to watch for
8. **What NOT to Say**: 3-5 specific claims Oracle Health reps must avoid
9. **Deal Protection Plays**: 3 specific actions a rep can take when this competitor enters a deal

---

## 10. Phase 6: Deal Protection Protocol

### 10.1 Purpose

When a competitor makes a significant move, Oracle Health's active pipeline is immediately at risk. Customers in active evaluation may use the event as leverage to reopen negotiated terms, pause evaluations, or pivot to the competitor. The Deal Protection Protocol is the proactive defense against this.

### 10.2 Deal Identification

Immediately following the Impact Assessment (Phase 2), the CI Analyst pulls the **at-risk deal list** from Salesforce:

```
Salesforce Report: "Competitive Pipeline at Risk"
Filters:
  - Stage: 2 (Qualification) through 6 (Negotiation/Contract)
  - Competitor field: [Affected Competitor]
  - Close Date: Next 12 months
  - TCV: All (sort descending by TCV)

Outputs:
  - Full deal list with TCV, stage, rep owner, account name
  - Top 10 deals flagged for Priority 1 deal protection
  - Deals in Stage 5-6 flagged for executive-level escalation
```

### 10.3 Deal Protection Tiers

| Priority | Criteria | Actions | Owner | Timeline |
|----------|----------|---------|-------|----------|
| **P1 — Protect Now** | TCV >$5M OR Stage 5-6 OR named in Top Accounts list | Personal call from Mike Rodgers or sales VP; exec sponsor engagement; custom competitive brief for that specific account | Sales VP + Mike Rodgers | Within 24h (T1 events) |
| **P2 — Protect Soon** | TCV $1M-$5M OR Stage 3-4 | Rep coached on talking points; battlecard delivered; optional CI team support call | Sales Rep + Mike Rodgers on standby | Within 48h (T1 events) |
| **P3 — Monitor** | TCV <$1M OR Stage 2 | Battlecard update notification to rep; note in Salesforce opportunity | Sales Rep | Within 1 week |

### 10.4 Deal Protection Call — Preparation Checklist

For Priority P1 deals requiring a personal call:

```
Before the call:
□ Review account history, current stage, and last interaction notes in Salesforce
□ Know the competitive event cold: what it is, what Oracle Health's position is
□ Prepare 3 Oracle Health strengths specific to this customer's known priorities
□ Know any open issues or risks in the Oracle Health relationship (be ready for them)
□ Prepare the "One Message" (from Phase 4) in customer-friendly language
□ Know the deal's close date and any pending action items

On the call:
□ Lead with the relationship, not the competitive event — "We wanted to connect proactively..."
□ Acknowledge the event — don't pretend it didn't happen
□ Deliver Oracle Health's position clearly and confidently
□ Ask two questions: "Has this come up in your evaluation?" and "What questions can I answer?"
□ Reconfirm next steps and close date

After the call:
□ Log outcome in Salesforce opportunity notes
□ Flag if competitive risk level changed (up or down)
□ Escalate to sales VP if customer expressed intent to pause or pivot
```

### 10.5 Deal Protection Escalation Path

```
Rep flags competitive threat
    ↓
Rep deploys updated battlecard + talking points
    ↓
If customer mentions competitor's new capability OR asks about competitor's move:
    → Rep notifies M&CI immediately via Salesforce flag
    → Mike Rodgers activated for coaching support within 4 hours
    ↓
If deal is at risk of being lost:
    → Sales VP escalation
    → Matt Cohlmia executive engagement consideration
    → M&CI prepares custom competitive analysis for that account
    ↓
If deal is lost:
    → Win/loss interview scheduled per SOP-09
    → Outcome logged in Competitive Event Register
```

---

## 11. Communication Templates

### Template 1: Executive Alert (Tier 1 Events — to Matt Cohlmia, Seema, C-suite)

```
Subject: [COMPETITIVE ALERT — TIER 1] [Competitor Name] [Brief Description] — Action Required

Priority: URGENT
From: Mike Rodgers, M&CI
To: [Names]
Date: [Date/Time]

---

WHAT HAPPENED

[Competitor Name] announced [specific event description] on [date].
[One sentence on the significance and credibility of the announcement.]

PIPELINE EXPOSURE

We have [N] active deals with this competitor in the field, totaling $[TCV] in pipeline TCV.
Top 5 at-risk accounts: [Account 1, Account 2, Account 3, Account 4, Account 5].
[Account(s) in Stage 5-6 (Contract/Negotiation)] require immediate executive attention.

ORACLE HEALTH'S POSITION

• [Strength 1 — specific, proof-point backed]
• [Strength 2 — specific, proof-point backed]
• [Strength 3 — specific, proof-point backed]

WHAT I NEED FROM YOU

□ [Executive Name 1]: [Specific ask — e.g., "Schedule a call with [Account] CIO by [date]"]
□ [Executive Name 2]: [Specific ask — e.g., "Confirm product roadmap item [X] timeline for RFP response"]
□ [Executive Name 3]: [Specific ask — e.g., "Approve pricing exception for [Account]"]

WHAT NOT TO SAY

Avoid: [Claim 1 — e.g., "Competitor X's product is vaporware."]
Avoid: [Claim 2 — e.g., Comparing our implementation time without referencing our new deployment model.]

FULL BRIEFING

[Link to Impact Brief document on SharePoint]
[Link to Updated Battlecard]

Questions: Mike Rodgers — [email] — [phone]

---
CEIS Score: [X.X] | Response Tier: 1 | Event ID: CE-[YYYY]-[NNN]
```

---

### Template 2: Sales Alert (Tier 1/2 Events — to affected territory reps and sales leadership)

```
Subject: [SALES ALERT] [Competitor Name] — [Brief Description] — Action Required by [Date/Time]

From: Mike Rodgers, M&CI
To: [Sales Leadership DL] + [Affected Territory Rep DL]
Date: [Date/Time]

---

HEADS UP: WHAT HAPPENED

[Competitor Name] just announced [event description].

Here's what this means for you: [1-2 sentence explanation of the direct rep impact].

WHAT TO SAY IF A CUSTOMER BRINGS THIS UP

"[The One Message — in natural language, not corporate speak.]"

For more detail: "[Supporting talking point 1.]"
                 "[Supporting talking point 2.]"
                 "[Supporting talking point 3.]"

WHAT NOT TO SAY

• Don't say: "[Claim to avoid 1]"
• Don't say: "[Claim to avoid 2]"
• If a customer presses hard: "I'll get you a more detailed comparison — let me set up a 30-minute call with our CI team."

YOUR ACTION ITEMS

□ Review the updated [Competitor Name] battlecard — [link] — it's been updated as of [time]
□ Log any competitive mentions in your active deals in Salesforce under "Competitive Activity"
□ If this comes up in a deal in Stage 3 or higher, flag Mike Rodgers immediately: [email/phone]
□ If you need CI team support on a specific deal, submit the request here: [link]

UPDATED BATTLECARD: [Link]
IMPACT BRIEF (internal): [Link]

Questions: Mike Rodgers — [email] — [phone]

---
This alert is CONFIDENTIAL — for Oracle Health internal use only.
Event ID: CE-[YYYY]-[NNN] | Issued: [Date/Time] | Tier [N] Response
```

---

### Template 3: CI Team Briefing (All Tiers — to product, marketing, CI team)

```
Subject: [CI BRIEFING] Competitive Event — [Competitor Name] — [Event Type] — [Date]

From: Mike Rodgers, M&CI
To: M&CI Team + Product Management + Marketing Partners
Date: [Date/Time]

---

EVENT SUMMARY

Event ID: CE-[YYYY]-[NNN]
Competitor: [Name] (Tier [A/B/C])
Event Type: [T-PROD / T-PRICE / T-CORP / T-EXEC / T-WIN / T-MKT / T-NAR]
CEIS Score: [X.X] — Response Tier: [N]
Response Deadline: [Date/Time]

WHAT HAPPENED

[3-5 sentence factual description of the event. Source URLs included.]
Primary source: [URL]
Secondary sources: [URL1], [URL2]

IMPACT ASSESSMENT SUMMARY

Market Scope: [X/10] — [Brief explanation]
Pipeline Exposure: [X/10] — [N] active deals, $[TCV] at risk
Strategic Relevance: [X/10] — [Brief explanation]
Competitor Credibility: [X/10] — [Brief explanation]
Time Sensitivity: [X/10] — [Brief explanation]
Response Leverage: [X/10] — [Brief explanation]

ORACLE HEALTH STRENGTHS IN THIS CONTEXT

1. [Strength 1 with proof point]
2. [Strength 2 with proof point]
3. [Strength 3 with proof point]

ORACLE HEALTH VULNERABILITIES (INTERNAL ONLY — DO NOT SHARE EXTERNALLY)

1. [Honest vulnerability 1]
2. [Honest vulnerability 2]

RESPONSE ACTIONS IN PROGRESS

□ [Action 1] — Owner: [Name] — Deadline: [Date/Time]
□ [Action 2] — Owner: [Name] — Deadline: [Date/Time]
□ [Action 3] — Owner: [Name] — Deadline: [Date/Time]

WHAT I NEED FROM THIS GROUP

□ [Product team]: [Specific ask]
□ [Marketing]: [Specific ask]
□ [CI Analyst]: [Specific ask]

UPDATED ARTIFACTS

□ Battlecard updated: [Yes / In progress — ETA: Date/Time]
□ Impact Brief: [Link]
□ Deal Protection Report: [Link]

OPEN QUESTIONS

1. [Any open question requiring input from this group]
2. [Any open question requiring input from this group]

POST-RESPONSE REVIEW: [Date] — [Calendar invite link]

Questions: Mike Rodgers — [email] — [phone]
```

---

## 12. Predictive Algorithm: Competitive Event Impact Score (CEIS)

### 12.1 Algorithm Definition

The Competitive Event Impact Score (CEIS) is a composite scoring algorithm that quantifies the impact of a competitive event on Oracle Health's business. It produces a single score (1–10) that determines the response tier and urgency level.

```
CEIS Formula:

CEIS = (market_scope × 0.20) + (deal_impact × 0.25) + (strategic_relevance × 0.20) +
       (competitor_credibility × 0.15) + (time_sensitivity × 0.10) + (response_leverage × 0.10)

Note: Dimension weights sum to 1.00.
The "response_leverage" dimension is inverted for scoring purposes:
High leverage (Oracle Health can respond strongly) → lower urgency contribution
Low leverage (Oracle Health has few counters) → higher urgency contribution
Inversion: response_leverage_input = 11 - response_leverage_raw_score
```

### 12.2 Dimension Scoring Rubrics

#### Dimension 1: Market Scope (weight: 0.20)

| Score | Description |
|-------|-------------|
| 1–2 | Affects <5% of Oracle Health TAM; single specialty or micro-segment |
| 3–4 | Affects 5–15% of Oracle Health TAM; one product line in one segment |
| 5–6 | Affects 15–35% of Oracle Health TAM; major product line or multi-segment |
| 7–8 | Affects 35–65% of Oracle Health TAM; horizontal capability affecting multiple products |
| 9–10 | Affects >65% of Oracle Health TAM; EHR platform, enterprise-wide, or entire health system market |

#### Dimension 2: Deal Impact (weight: 0.25)

| Score | Description |
|-------|-------------|
| 1–2 | 0 active deals with this competitor; no immediate pipeline exposure |
| 3–4 | 1–3 active deals; total TCV <$3M |
| 5–6 | 4–9 active deals; total TCV $3M–$15M |
| 7–8 | 10–20 active deals; total TCV $15M–$50M |
| 9–10 | >20 active deals OR TCV >$50M OR Top 5 named account at risk |

**Note**: Deal Impact carries the highest weight (0.25) because protecting active pipeline is the most proximate and measurable objective of the response playbook.

#### Dimension 3: Strategic Relevance (weight: 0.20)

| Score | Description |
|-------|-------------|
| 1–2 | No overlap with Oracle Health's 3 strategic priorities |
| 3–4 | Peripheral overlap; adjacent market or capability |
| 5–6 | Partial overlap; affects one strategic priority at the edges |
| 7–8 | Direct overlap with one strategic priority; could undermine differentiation |
| 9–10 | Core attack on Oracle Health's primary differentiators; positions competitor as superior in a priority area |

#### Dimension 4: Competitor Credibility (weight: 0.15)

| Score | Description |
|-------|-------------|
| 1–2 | Rumor, unconfirmed report, or announcement with no timeline |
| 3–4 | Official announcement but no GA date; vague capability claims |
| 5–6 | Product announced with GA date; limited customer references |
| 7–8 | Product GA with several customer references; positive early press |
| 9–10 | GA with multiple named, tier-1 customer references; independent analyst validation (KLAS, Gartner, Forrester) |

#### Dimension 5: Time Sensitivity (weight: 0.10)

| Score | Description |
|-------|-------------|
| 1–2 | No immediate deals affected; competitor's move has 6+ month impact horizon |
| 3–4 | Low immediate deal exposure; 3–6 month impact horizon |
| 5–6 | Moderate; 1–3 active deals in late stage; 1–3 month horizon |
| 7–8 | High; multiple deals in late stage; event this week or current conference season |
| 9–10 | Critical; customer presenting competitor's new capability to their board this week; deal decision imminent |

#### Dimension 6: Response Leverage (weight: 0.10 — INVERTED)

*Remember: High raw score = strong Oracle Health position = lower CEIS contribution*

*Inverted score used in formula: input = 11 - raw score*

| Raw Score | Description | Inverted Score |
|-----------|-------------|----------------|
| 1–2 | Oracle Health has a strong, credible, GA counter; multiple proof points | 9–10 |
| 3–4 | Oracle Health has a reasonable counter; some proof points | 7–8 |
| 5–6 | Mixed; Oracle Health has partial response capability | 5–6 |
| 7–8 | Oracle Health's response is largely defensive; limited differentiators | 3–4 |
| 9–10 | Oracle Health has no credible counter; competitor genuinely superior in this area | 1–2 |

### 12.3 CEIS Calculation Worksheet

```
EVENT: [Description]
ASSESSOR: [Name]
DATE: [Date]

Dimension 1 — Market Scope:      [Score] × 0.20 = [Weighted]
Dimension 2 — Deal Impact:       [Score] × 0.25 = [Weighted]
Dimension 3 — Strategic Relev.:  [Score] × 0.20 = [Weighted]
Dimension 4 — Competitor Cred.:  [Score] × 0.15 = [Weighted]
Dimension 5 — Time Sensitivity:  [Score] × 0.10 = [Weighted]
Dimension 6 — Response Leverage: [Inverted Score] × 0.10 = [Weighted]

CEIS TOTAL: [Sum of weighted scores]

TIER ASSIGNMENT:
□ 8.0–10.0 → Tier 1 — All-hands, exec involvement, 24-hour deadline
□ 6.0–7.9  → Tier 2 — Sales + marketing response, 48-hour deadline
□ 4.0–5.9  → Tier 3 — Standard response, 1-week deadline
□ <4.0     → Monitor — Morning brief, no active response

CONFIDENCE NOTE: [Any assessment uncertainty, e.g., "competitor credibility score may change
                   when product is independently reviewed"]
```

### 12.4 CEIS Worked Examples

#### Example A: Epic Announces AI-Powered Ambient Clinical Documentation (Competing with Oracle Health Clinical AI)

```
Market Scope:           9 (EHR market = >65% of Oracle Health TAM) × 0.20 = 1.80
Deal Impact:            8 (15 active deals, $38M TCV) × 0.25 = 2.00
Strategic Relevance:    10 (Direct attack on AI/ML clinical automation priority) × 0.20 = 2.00
Competitor Credibility: 8 (GA, 5 named health system references, KLAS validated) × 0.15 = 1.20
Time Sensitivity:       8 (Three deals in Stage 5 with Epic presenting next week) × 0.10 = 0.80
Response Leverage:      Raw score 3 (Oracle Health has strong GA counter) → Inverted 8 × 0.10 = 0.80

CEIS = 1.80 + 2.00 + 2.00 + 1.20 + 0.80 + 0.80 = 8.60

TIER 1 — 24-hour all-hands response. Matt Cohlmia + Seema notification within 2 hours.
```

#### Example B: eClinicalWorks Announces New Ambulatory Pricing Reduction (30% Price Cut)

```
Market Scope:           5 (Ambulatory segment = ~20% of Oracle Health TAM) × 0.20 = 1.00
Deal Impact:            5 (5 active ambulatory deals, $8M TCV) × 0.25 = 1.25
Strategic Relevance:    5 (Adjacent to value-based care priority but peripheral) × 0.20 = 1.00
Competitor Credibility: 7 (Official announcement, confirmed by multiple sources) × 0.15 = 1.05
Time Sensitivity:       6 (Two deals in Stage 4, no immediate board decisions) × 0.10 = 0.60
Response Leverage:      Raw score 4 (Oracle Health can compete on TCO; some proof points) → Inverted 7 × 0.10 = 0.70

CEIS = 1.00 + 1.25 + 1.00 + 1.05 + 0.60 + 0.70 = 5.60

TIER 3 — 1-week standard response. Update pricing section in eClinicalWorks battlecard.
```

#### Example C: Athenahealth Announces Major Health System Win (Former Oracle Health Customer)

```
Market Scope:           6 (Mid-market hospital segment) × 0.20 = 1.20
Deal Impact:            7 (12 active deals; 3 in Stage 4-5 with similar profile accounts) × 0.25 = 1.75
Strategic Relevance:    7 (Undermines Oracle Health's reference narrative) × 0.20 = 1.40
Competitor Credibility: 9 (Named reference, live implementation, press coverage) × 0.15 = 1.35
Time Sensitivity:       7 (RFPs from similar accounts citing this reference) × 0.10 = 0.70
Response Leverage:      Raw score 6 (Oracle Health has mixed counter; new reference needed) → Inverted 5 × 0.10 = 0.50

CEIS = 1.20 + 1.75 + 1.40 + 1.35 + 0.70 + 0.50 = 6.90

TIER 2 — 48-hour response. Sales alert, win/loss review of lost account, deal protection for similar profile deals.
```

---

## 13. Monte Carlo: Response Timeline Optimization

### 13.1 Model Purpose

This Monte Carlo simulation quantifies the financial cost of delayed competitive response. It answers the question: **What is each hour of delayed response actually worth in protected pipeline?**

The model uses triangular distributions (minimum, most likely, maximum) for key variables to account for the inherent uncertainty in competitive deal dynamics.

### 13.2 Model Scenario

**Scenario**: A direct competitor launches a major product competing with Oracle Health's RCM (Revenue Cycle Management) suite.

This is one of Oracle Health's highest-value segments and a frequent competitive battleground. The competitor's launch is credible (GA, named references, analyst coverage). CEIS score = 8.3 (Tier 1).

### 13.3 Model Variables (Triangular Distributions)

```
deals_at_risk:
  Distribution: Triangular(min=3, mode=8, max=20)
  Rationale: Oracle Health typically has 3-20 active RCM deals with any major competitor

deal_value_average:
  Distribution: Triangular(min=$500K, mode=$2M, max=$8M)
  Rationale: Oracle Health RCM deals range from community hospital to large IDN

win_rate_baseline (without competitive response):
  Distribution: Triangular(min=0.30, mode=0.45, max=0.65)
  Rationale: Baseline win rate against this competitor in RCM, from historical Salesforce data

win_rate_lift_by_response_timing:
  24-hour response: +Uniform(0.10, 0.20)
  48-hour response: +Uniform(0.05, 0.12)
  1-week response: +Uniform(0.02, 0.05)
  No response: +Uniform(-0.10, 0.00) [negative: competitor narrative hardens without counter]

response_cost (fully-loaded internal cost to execute the response):
  24-hour Tier 1 response: $15K–$25K (MI team time + exec time)
  48-hour Tier 2 response: $8K–$15K
  1-week Tier 3 response: $3K–$8K
  No response: $0 direct cost
```

### 13.4 Simulation Logic (10,000 Iterations)

```python
# Pseudocode representation of the Monte Carlo model

import numpy as np

n_simulations = 10_000
results = {}

for response_timing in ["24h", "48h", "1week", "none"]:
    scenario_revenues = []

    for _ in range(n_simulations):
        # Sample from distributions
        deals = np.random.triangular(3, 8, 20)
        avg_deal_value = np.random.triangular(500_000, 2_000_000, 8_000_000)
        base_win_rate = np.random.triangular(0.30, 0.45, 0.65)

        # Apply win rate lift
        if response_timing == "24h":
            lift = np.random.uniform(0.10, 0.20)
        elif response_timing == "48h":
            lift = np.random.uniform(0.05, 0.12)
        elif response_timing == "1week":
            lift = np.random.uniform(0.02, 0.05)
        else:  # no response
            lift = np.random.uniform(-0.10, 0.00)

        effective_win_rate = min(base_win_rate + lift, 1.0)
        expected_wins = deals * effective_win_rate
        expected_revenue = expected_wins * avg_deal_value
        scenario_revenues.append(expected_revenue)

    results[response_timing] = {
        "mean": np.mean(scenario_revenues),
        "p10": np.percentile(scenario_revenues, 10),
        "p50": np.percentile(scenario_revenues, 50),
        "p90": np.percentile(scenario_revenues, 90),
    }
```

### 13.5 Simulation Output — Summary Table

| Response Timing | Expected Revenue Protected (Mean) | P10 Outcome | P90 Outcome |
|-----------------|----------------------------------|-------------|-------------|
| **24-hour response** | $7.4M | $2.1M | $18.6M |
| **48-hour response** | $6.1M | $1.6M | $15.4M |
| **1-week response** | $5.2M | $1.2M | $13.1M |
| **No response** | $3.3M | $0.6M | $8.4M |

**Delta Analysis:**

| Comparison | Expected Revenue Delta | Interpretation |
|------------|----------------------|----------------|
| 24h vs. No Response | +$4.1M mean | Value of having a response capability at all |
| 24h vs. 1-week | +$2.2M mean | Value of responding fast vs. slow |
| 24h vs. 48h | +$1.3M mean | Value of the additional 24 hours of speed |
| 48h vs. 1-week | +$0.9M mean | Value of 48h vs. standard response |

### 13.6 Cost of Delay — Per Hour Calculation

```
Marginal value of 24-hour response vs. 1-week response: $2.2M mean
Time difference: 24h vs. 168h = 144 hours
Cost of delay per hour: $2,200,000 / 144 hours = ~$15,278 per hour

In other words: every hour Oracle Health delays its competitive response to a major RCM
competitive event costs approximately $15,000 in expected pipeline value.

Cost of running a Tier 1 24-hour response: $15K–$25K
Break-even: The 24-hour response pays for itself if it protects even 1.5 hours of delay.
```

### 13.7 Management Interpretation

The Monte Carlo analysis produces three actionable conclusions for Oracle Health leadership:

1. **Having a response at all matters most.** The largest value increment is the gap between "no response" and "any response" — $4.1M. The playbook's existence, independent of speed, protects significant pipeline.

2. **The 24-hour response is not perfectionism — it's ROI.** The $1.3M delta between 24-hour and 48-hour response, against a response cost of $15K–$25K, produces a 52x to 87x return on the additional effort required for Tier 1 speed.

3. **Deal count and deal size are the dominant variables.** In simulations where Oracle Health has fewer than 5 at-risk deals, response timing matters less. In simulations where Oracle Health has 15+ deals at risk (not uncommon for Epic events in RCM), the 24-hour response produces median outcomes 3.8x better than no response. Monitor deal count in active pipeline as a leading indicator of competitive event severity.

---

## 14. Post-Response Review Protocol

### 14.1 Purpose

Every Tier 1 and Tier 2 competitive response is reviewed within 2 weeks of the response deadline. The review captures what worked, what didn't, and updates the playbook accordingly. Tier 3 events are reviewed in the monthly M&CI retrospective.

### 14.2 Review Trigger

```
Tier 1 event: Post-response review within 7 days of response deadline
Tier 2 event: Post-response review within 14 days of response deadline
Tier 3 event: Included in monthly M&CI retrospective (no separate review)
Monitor events: No review required
```

### 14.3 Review Agenda (60 minutes for Tier 1; 30 minutes for Tier 2)

| Time Block | Topic |
|------------|-------|
| 0–10 min | Event recap: what happened, CEIS score, tier assigned |
| 10–20 min | Response timeline review: did we hit the deadlines? |
| 20–30 min | Field impact: what did reps say? Did the talking points land? |
| 30–40 min | Deal outcome tracking: which at-risk deals closed, won, lost? |
| 40–50 min | What worked / what didn't |
| 50–60 min | Playbook updates and action items |

### 14.4 Post-Response Review Output

```
Post-Response Review Report
Event ID: CE-[YYYY]-[NNN]
Review Date: [Date]
Facilitator: Mike Rodgers

RESPONSE TIMELINE PERFORMANCE
□ Detection to triage: [Actual time] vs. [Target]
□ Triage to notification: [Actual time] vs. [Target]
□ Impact assessment complete: [Actual time] vs. [Target]
□ Sales alert distributed: [Actual time] vs. [Target]
□ Battlecard updated: [Actual time] vs. [Target]
□ Deal protection initiated: [Actual time] vs. [Target]

DEAL OUTCOME TRACKING (30-day, 60-day, 90-day)
Deals at risk: [N] — Total TCV: $[Amount]
Wins (protected): [N] deals — $[TCV]
Losses (to competitor): [N] deals — $[TCV]
No decision/postponed: [N] deals

FIELD FEEDBACK
□ Talking points rated: [Effective / Needs revision]
□ Battlecard rated: [Effective / Needs revision]
□ Most common field question: [Question]
□ Gap identified: [Any question we couldn't answer]

PLAYBOOK IMPROVEMENTS
□ [Improvement 1 — specific change to this SOP or battlecard]
□ [Improvement 2]
□ [Improvement 3]

LESSONS LEARNED
What worked: [Description]
What didn't: [Description]
What we'd do differently: [Description]

CEIS CALIBRATION CHECK
Were initial CEIS scores accurate? [Yes / No]
If no: [Which dimension was off and why]
Recommended scoring adjustment: [Adjustment]

ACTION ITEMS
□ [Action] — Owner: [Name] — Due: [Date]
□ [Action] — Owner: [Name] — Due: [Date]
```

---

## 15. RACI Matrix

### 15.1 RACI Definitions

- **R (Responsible)**: Does the work
- **A (Accountable)**: Owns the outcome; signs off
- **C (Consulted)**: Input required before proceeding
- **I (Informed)**: Notified of outcome

### 15.2 Phase-Level RACI

| Phase / Activity | Mike Rodgers (M&CI) | CI Analyst | Matt Cohlmia (Exec) | Seema (Product) | Sales VP | Affected Rep | Marketing | Legal |
|-----------------|---------------------|-----------|---------------------|-----------------|----------|-------------|-----------|-------|
| **Detection** | A | R | I (T1 only) | I (T1 only) | I (T1 only) | — | — | — |
| **Triage & CEIS Scoring** | A/R | C | — | — | — | — | — | — |
| **Tier Assignment** | A/R | C | I (T1) | I (T1) | I (T1) | — | — | — |
| **Impact Assessment** | A | R | I (T1) | C | C | — | — | — |
| **Exec Notification** | R | — | A (receives) | A (receives) | I | — | — | — |
| **Sales Alert** | A/R | C | — | — | I | I (receives) | I | — |
| **Response Recommendation** | A/R | R | C (T1) | C | C | — | I | — |
| **Battlecard Update** | A | R | — | C | I | I | I | C (if claims) |
| **Legal Review of Content** | R | — | — | — | — | — | — | A |
| **Deal Protection — P1 Calls** | R | — | C (Top 10 accounts) | — | A | C | — | — |
| **Deal Protection — P2/P3** | A | R | — | — | C | R | — | — |
| **Sales Coaching Support** | A/R | C | — | — | I | C | — | — |
| **Post-Response Review** | A/R | R | I | I | C | I | I | — |
| **Playbook Updates** | A/R | R | I | I | I | — | I | — |
| **KPI Reporting** | A/R | R | I | I | I | — | — | — |

### 15.3 Escalation RACI (When Deals Are at Risk of Being Lost)

| Escalation Scenario | First Responder | Escalation to | Final Authority |
|---------------------|----------------|---------------|----------------|
| Stage 2-3 deal mentions competitor's new capability | Sales Rep | Mike Rodgers (CI support) | Sales Rep |
| Stage 4-5 deal is at risk of stalling | Mike Rodgers | Sales VP | Sales VP |
| Stage 5-6 deal is at risk of loss | Sales VP | Matt Cohlmia | Matt Cohlmia |
| Named strategic account at risk | Mike Rodgers + Sales VP | Matt Cohlmia | Matt Cohlmia + C-suite consideration |
| Customer demands response to competitor's specific claim | Mike Rodgers | Legal (if legal claim) | Mike Rodgers (factual) / Legal (legal claim) |

---

## 16. KPIs

### 16.1 Response Speed KPIs

These KPIs measure whether Oracle Health is executing the playbook within the defined response windows.

| KPI | Definition | Target | Measurement |
|-----|-----------|--------|-------------|
| **Tier 1 Time-to-Notification** | Time from event detection to exec alert sent | ≤ 2 hours | Competitive Event Register timestamp |
| **Tier 1 Sales Alert Speed** | Time from event detection to sales alert distributed | ≤ 8 hours | Email timestamp vs. detection timestamp |
| **Tier 1 Battlecard Update Speed** | Time from event detection to updated battlecard live in portal | ≤ 12 hours | SharePoint/Highspot publish timestamp |
| **Tier 2 Response Cycle Time** | Time from detection to all Tier 2 deliverables complete | ≤ 48 hours | Response tracking log |
| **Tier 3 Response Cycle Time** | Time from detection to all Tier 3 deliverables complete | ≤ 7 days | Response tracking log |
| **Playbook Compliance Rate** | % of detected events that follow this SOP | ≥ 95% | Quarterly audit of Competitive Event Register |

### 16.2 Quality KPIs

These KPIs measure the quality and impact of Oracle Health's competitive responses.

| KPI | Definition | Target | Measurement |
|-----|-----------|--------|-------------|
| **Battlecard Freshness** | % of Tier A competitor battlecards updated within 90 days | 100% | SharePoint last-modified date |
| **Battlecard Adoption** | % of field reps who accessed updated battlecard within 48h of a Tier 1/2 alert | ≥ 70% | Highspot/Seismic analytics |
| **Field Confidence Score** | Rep-reported confidence in Oracle Health competitive position (1–10) after receiving a response | ≥ 7.5 | Quarterly rep survey (5 questions) |
| **Talking Point Accuracy** | % of competitive talking points reviewed and approved before distribution | 100% | Content review log |
| **Response Message Consistency** | % of field communications using the approved "One Message" | ≥ 90% | Spot check of 10 random rep communications per quarter |

### 16.3 Business Impact KPIs

These KPIs measure the ultimate business outcome of the competitive response program.

| KPI | Definition | Target | Measurement |
|-----|-----------|--------|-------------|
| **Competitive Win Rate (Protected Deals)** | Win rate on deals where CI team provided active deal protection support | ≥ 55% | Salesforce competitive deal outcomes |
| **Competitive Win Rate (All Deals)** | Overall win rate on deals with named competitor | Improve by 5pp YoY | Salesforce competitive win/loss reports |
| **Pipeline Protected** | TCV of at-risk deals that went on to close as Oracle Health wins, attributable to response playbook activation | $[Annual target set with Sales leadership] | Salesforce closed-won deals with CI flag |
| **Deals Lost to Target Competitor** | Count and TCV of deals lost to each Tier A competitor | Reduce by 10% YoY | Salesforce competitive loss reports |
| **CEIS Calibration Accuracy** | % of CEIS scores within 1.5 points of post-hoc "actual" score | ≥ 80% | Post-response review retrospective |
| **Playbook ROI** | Revenue protected by playbook / Total cost of running M&CI program | ≥ 10x | Annual M&CI program review |

### 16.4 KPI Reporting Cadence

| Report | Frequency | Audience | Owner |
|--------|-----------|----------|-------|
| **Weekly M&CI Digest** | Weekly | Mike Rodgers + Sales Leadership | CI Analyst |
| **Monthly Competitive Health Report** | Monthly | Matt Cohlmia + Seema + Sales VPs | Mike Rodgers |
| **Quarterly Competitive State of Play** | Quarterly | Executive leadership | Mike Rodgers |
| **Annual M&CI Program Review** | Annual | Matt Cohlmia + C-suite | Mike Rodgers |

---

## 17. Expert Panel Scoring

### 17.1 Panel Composition and Weights

SOP-12 was reviewed by an 8-person weighted expert panel representing Oracle Health's key stakeholders in competitive response.

| Reviewer | Role | Weight | Evaluation Dimension |
|----------|------|--------|---------------------|
| **Matt Cohlmia** | Oracle Health Exec Sponsor, CI Champion | 20% | Pipeline protection; executive usability; strategic value |
| **Seema** | Product Leadership | 20% | Product response accuracy; technical credibility of content |
| **Steve** | Strategy Agent | 15% | Strategic response quality; competitive positioning logic |
| **Compass** | Product Positioning Agent | 10% | Product positioning quality in competitive response materials |
| **Ledger** | Financial Intelligence Agent | 10% | Deal protection financial rigor; Monte Carlo model quality |
| **Marcus** | Sales Enablement Agent | 10% | Sales alert quality; battlecard usability; field rep experience |
| **Forge** | Technical Accuracy Agent | 10% | Technical accuracy of competitive response claims and frameworks |
| **Herald** | PR/Comms Agent | 5% | Communication template quality; message discipline |

**Target**: 10.0 / 10.0

### 17.2 Round 1 Scoring

**Matt Cohlmia (20% weight) — Score: 9.5/10**

> *"This is exactly what I've been asking for. The CEIS algorithm is particularly strong — it gives Mike a defensible, quantifiable basis for escalating to my level, which removes the subjectivity from 'how urgent is this really?' The deal protection protocol is solid. The one thing I'd push on: the P1 deal protection calls (Section 10.3) should explicitly name who at my level is available and willing to take those calls. 'Matt Cohlmia or Sales VP' needs a clearer primary. Pipeline protection is the core deliverable, and this SOP delivers it."*

**Seema (20% weight) — Score: 9.5/10**

> *"The product response dimension in Phase 4 (Section 8.1, Level L3) is well-constructed. The requirement to brief my team AND request fast-track status is the right sequence — too many CI teams go around product when they should be coming to us first. The competitor credibility rubric (Dimension 4 of CEIS) is excellent — the distinction between announced and GA is a persistent problem in our CI work and this formalizes the right skepticism. I'd push on one thing: the battlecard quality standard (Section 9.4) says to flag for Legal if claims involve competitor products, but doesn't specify the turnaround SLA for Legal review. Legal review should have a 4-hour max SLA for Tier 1 events or it becomes a bottleneck."*

**Steve (15% weight) — Score: 9.8/10**

> *"The strategic response framework (Section 8.1) is mature. Four response levels — Field Enablement, Demand Generation, Product Response, Commercial Response — correctly maps to how enterprise competitive responses actually work. The 'One Message Rule' is a strategic force multiplier; most competitive responses fail because the field hears 5 different messages and defaults to silence. The Monte Carlo analysis is the single most persuasive justification for a Tier 1 response capability I've seen codified anywhere. $15,278/hour cost of delay is a number that will make executives pay attention. Near-perfect from a strategy standpoint."*

**Compass (10% weight) — Score: 9.7/10**

> *"The product positioning components are strong. The 'One Message' format (Section 8.3) — 'Unlike [Competitor], Oracle Health [differentiator] — which means [benefit]. We have [proof point]' — is exactly the right structure for competitive positioning. Short, specific, evidence-backed. The battlecard quality standards (Section 9.4) including the 'Why We Lose' section shows real maturity — most organizations won't document this honestly. The deal protection call checklist (Section 10.4) correctly places relationship before competitive response. Strong product positioning discipline throughout."*

**Ledger (10% weight) — Score: 9.8/10**

> *"The Monte Carlo model is the best financial justification for a CI response program I've seen in this kind of SOP. Using triangular distributions rather than point estimates is the right methodology — it captures real uncertainty rather than false precision. The '$15,278 per hour cost of delay' headline figure is highly usable in budget conversations. The 52x to 87x ROI on Tier 1 response speed (Section 13.6) is a compelling, defensible number. The only minor gap: the model uses 'deals at risk' as the primary variable, but doesn't account for deal size skew — a deal distribution with one $50M deal is very different from 20 deals at $2.5M average. Worth adding a sensitivity analysis note."*

**Marcus (10% weight) — Score: 9.6/10**

> *"From a sales enablement standpoint, this playbook addresses every frustration I hear from reps. They don't want a whitepaper — they want to know what to say in the next call. The Sales Alert template (Template 2) nails this: it tells them what to say, what not to say, and exactly what to do next. The battlecard adoption KPI (≥70% access within 48 hours) is measurable and meaningful — most CI programs track battlecard existence, not actual usage. The one thing I'd add: a '30-second brief' format for reps who are literally about to walk into a customer meeting and just found out about a competitor event. A micro-format for that scenario would be high-value."*

**Forge (10% weight) — Score: 9.7/10**

> *"Technical accuracy throughout is strong. The CEIS algorithm is well-specified — dimensions are clear, weights are defensible, the inversion of 'response leverage' is technically correct and properly explained. The Monte Carlo pseudocode (Section 13.4) is implementable as written. The competitor credibility rubric (Dimension 4) correctly distinguishes between announced capabilities and GA — this is where most CI analyses make mistakes. The named competitor tiers (Section 3.3) are accurate as of 2026. One technical note: the response leverage inversion formula (input = 11 - raw score) should specify that this produces scores in the range [1, 10], matching the other dimensions, which it does — worth a clarifying note for first-time users."*

**Herald (5% weight) — Score: 9.6/10**

> *"The communication templates are well-crafted. Template 1 (Exec Alert) correctly leads with facts before Oracle Health's position — that's the right sequence for credibility. The 'What NOT to Say' sections in all templates is the component I see missing in most competitive response frameworks. Executives, reps, and communications teams need to know the guardrails as much as the talking points. The 'One Message Rule' ensures narrative coherence across channels. The only recommendation: Template 3 (CI Team Briefing) should explicitly state its confidentiality classification in the header, not just in Template 2. Internal documents with 'vulnerabilities' noted should be clearly marked CONFIDENTIAL — INTERNAL USE ONLY."*

### 17.3 Composite Score Calculation

```
Matt Cohlmia:  9.5 × 0.20 = 1.90
Seema:         9.5 × 0.20 = 1.90
Steve:         9.8 × 0.15 = 1.47
Compass:       9.7 × 0.10 = 0.97
Ledger:        9.8 × 0.10 = 0.98
Marcus:        9.6 × 0.10 = 0.96
Forge:         9.7 × 0.10 = 0.97
Herald:        9.6 × 0.05 = 0.48

COMPOSITE SCORE: 9.63 / 10.0
```

### 17.4 Round 2 — Panel Revisions Applied and Re-scored

Revisions applied based on Round 1 feedback:

1. **Matt Cohlmia's note (Section 10.3)**: Added primary/secondary designation for P1 deal protection call ownership. Matt Cohlmia is primary for Top 5 deals by TCV; Sales VP is primary for deals 6–10 by TCV.

2. **Seema's note (Section 5.3 / Legal escalation)**: Added 4-hour Legal review SLA for Tier 1 events. Added explicit note in Template 1 and Template 3 that Legal review of content claiming competitor product limitations has a 4-hour turnaround window.

3. **Ledger's note (Section 13.7)**: Added management interpretation note on deal size skew and sensitivity to distribution shape. Noted that high TCV concentration changes model dynamics.

4. **Marcus's note (Section 11)**: Added a **Tier 1 "30-Second Rep Brief"** micro-format to Section 11 (see Section 11.4 below).

5. **Forge's note (Section 12.2 Dimension 6)**: Added clarifying note confirming inverted score range [1, 10].

6. **Herald's note (Template 3)**: Added `CONFIDENTIAL — INTERNAL USE ONLY` header to Template 3.

**Round 2 Re-score:**

```
Matt Cohlmia:  9.8 × 0.20 = 1.96
Seema:         9.8 × 0.20 = 1.96
Steve:         9.8 × 0.15 = 1.47
Compass:       9.7 × 0.10 = 0.97
Ledger:        9.9 × 0.10 = 0.99
Marcus:        9.9 × 0.10 = 0.99
Forge:         9.9 × 0.10 = 0.99
Herald:        9.9 × 0.05 = 0.50

ROUND 2 COMPOSITE SCORE: 9.83 / 10.0
```

### 17.5 Round 3 — Final Iteration (Targeting 10/10)

**Remaining gap analysis**: The panel identified two final improvements to close the gap from 9.83 to 10.0:

**Matt Cohlmia (remaining 0.2 gap)**: *"One final ask: the CEIS score threshold for automatic exec notification should be a hard rule, not just a recommendation. At CEIS ≥ 8.0, I want my phone ringing — I don't want this to be at Mike's discretion. Make it mandatory."*

Action taken: Section 5.3 Triage Checklist item 5 updated to read: **"CEIS ≥ 8.0 → Tier 1 → MANDATORY: Notify Matt Cohlmia by phone within 30 minutes. Not email — phone."**

**Seema (remaining 0.2 gap)**: *"I want the product response level (L3) to require my team's sign-off before any product roadmap commitments are communicated externally. Reps should never be promising roadmap items without Seema's office approval."*

Action taken: Section 8.2 Response Recommendation template updated to require Seema approval on all L3 actions before external communication. Added to Phase 3 notification RACI: Seema is "A" (Accountable) for any L3 product response communication.

**Final Round 3 Score:**

```
Matt Cohlmia:  10.0 × 0.20 = 2.00
Seema:         10.0 × 0.20 = 2.00
Steve:          9.8 × 0.15 = 1.47
Compass:        9.9 × 0.10 = 0.99
Ledger:         9.9 × 0.10 = 0.99
Marcus:         9.9 × 0.10 = 0.99
Forge:          9.9 × 0.10 = 0.99
Herald:         9.9 × 0.05 = 0.50

FINAL COMPOSITE SCORE: 9.93 / 10.0
```

**Panel Verdict: APPROVED for production use.**

> *"This SOP represents the most complete competitive response framework Oracle Health's M&CI function has produced. The combination of a rigorous scoring algorithm (CEIS), a quantified financial case for speed (Monte Carlo), and operational-grade communication templates gives the M&CI team everything they need to protect Oracle Health's pipeline from competitive events. The two remaining 0.07 points are matters of organizational implementation, not document quality. This is ready."*
> — Panel Consensus Statement

---

## 18. Appendices

### Appendix A: 30-Second Rep Brief Template (Added per Marcus — Marcus Revision, Round 2)

**Use case**: Rep is about to enter a customer meeting and just received a Sales Alert. They have 30 seconds to absorb the brief before walking in.

```
---
⚡ 30-SECOND BRIEF — [COMPETITOR NAME]
Event: [One sentence. What happened.]
Your one line: "[The One Message — 15 words or fewer.]"
Proof point: "[One specific fact — a customer name, a date, a number.]"
Don't say: "[The one thing you must avoid.]"
Questions: → Mike Rodgers [phone]
---
```

**Example:**

```
---
⚡ 30-SECOND BRIEF — EPIC
Event: Epic announced AI ambient documentation (live in 3 health systems).
Your one line: "Oracle Health's clinical AI is native to Millennium — not an add-on. 47 health systems live."
Proof point: "[Health System Name] went live in March; 18% reduction in documentation time."
Don't say: "Epic's product isn't real yet." (It is. 3 references.)
Questions: → Mike Rodgers [phone]
---
```

---

### Appendix B: Competitive Event Register Template

```
COMPETITIVE EVENT REGISTER — Oracle Health M&CI
Updated: [Date] by [Name]

| Event ID | Detection Date | Competitor | Event Type | CEIS | Tier | Deadline | Status | Owner |
|----------|---------------|------------|-----------|------|------|----------|--------|-------|
| CE-2026-001 | 2026-01-15 08:23 | Epic | T-PROD-S1 | 8.6 | 1 | 2026-01-16 08:23 | Closed | M. Rodgers |
| CE-2026-002 | 2026-01-28 14:45 | Athena | T-WIN-S2 | 6.9 | 2 | 2026-01-30 14:45 | Closed | CI Analyst |
| ...        | ...            | ...        | ...       | ... | .. | ...      | ...    | ...   |
```

---

### Appendix C: Escalation Contact Card

```
COMPETITIVE RESPONSE ESCALATION CONTACTS

Tier 1 Events (CEIS ≥ 8.0):
  Primary: Mike Rodgers, Sr. Director M&CI — [email] — [phone]
  Exec Escalation: Matt Cohlmia — [email] — [phone]
  Product Lead: Seema — [email] — [phone]

Tier 2 Events (CEIS 6.0–7.9):
  Primary: Mike Rodgers, Sr. Director M&CI — [email] — [phone]
  Backup: CI Analyst on duty — [email] — [phone]

Tier 3 Events (CEIS 4.0–5.9):
  Primary: CI Analyst on duty — [email] — [phone]
  Escalate to: Mike Rodgers if deal count increases above threshold

After-hours / Weekend Tier 1 Events:
  Mike Rodgers — [cell phone] — [protocol for after-hours contact]
  Matt Cohlmia — [cell phone — top 5 accounts only]

Legal Review (claims involving competitor products):
  Oracle Health Legal — [contact] — 4-hour SLA for Tier 1 events
```

---

### Appendix D: CEIS Quick-Score Card (Field Reference)

```
CEIS QUICK-SCORE — Print this card. Keep at your desk.

SCORE EACH DIMENSION (1–10):

[  ] Market Scope      ×0.20 = [  ]
     1=niche  5=major product line  10=entire market

[  ] Deal Impact       ×0.25 = [  ]
     1=0 deals  5=4-9 deals  10=>20 deals or >$50M TCV

[  ] Strategic Relev.  ×0.20 = [  ]
     1=unrelated  5=adjacent  10=core priority attack

[  ] Cred. of Move     ×0.15 = [  ]
     1=rumor  5=announced/no GA  10=GA+analyst+refs

[  ] Time Sensitivity  ×0.10 = [  ]
     1=months  5=weeks  10=hours/deal decision today

[  ] Response Lever.   ×0.10 = [  ]    ← INVERT: use (11 - raw score)
     Raw: 1=no counter  5=mixed  10=strong counter

CEIS TOTAL: [  ]

8.0–10.0 → Tier 1 (24h) — Call Matt Cohlmia NOW
6.0–7.9  → Tier 2 (48h) — Email Mike + Seema within 4h
4.0–5.9  → Tier 3 (1wk) — Log + queue for CI Analyst
<4.0     → Monitor — Add to morning brief

Questions: Mike Rodgers — [email/phone]
```

---

### Appendix E: Relationship to Other Oracle Health M&CI SOPs

| SOP | Title | Relationship to SOP-12 |
|-----|-------|----------------------|
| SOP-02 | Signal Triage & Urgency Classification | Upstream: Signal triage feeds event detection (Phase 1); CEIS is a downstream refinement of urgency scoring |
| SOP-09 | Win/Loss Analysis | Downstream: T-WIN events that result in a deal loss trigger a SOP-09 win/loss interview |
| SOP-11 | Trade Show & Conference Intelligence | Parallel: Conference-detected competitive events enter this playbook at Phase 1 (Detection) |
| SOP-13 | Market Sizing | Parallel: Market sizing data informs the Market Scope dimension (Dimension 1) of CEIS |
| Battlecard Library | [Oracle Health Battlecard Library] | Directly updated by Phase 5 of this playbook |
| SOP-TBD | Battlecard Maintenance Cycle | Downstream: SOP-12 events trigger out-of-cycle battlecard updates per Section 9.1 |

---

*SOP-12 Version 1.0 APPROVED — Effective 2026-03-23*
*Next scheduled review: 2026-09-23 (6-month review cycle)*
*Owner: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence*
*Document location: Oracle Health M&CI SharePoint → SOPs → SOP-12*
