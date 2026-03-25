# SOP-33: AI-Powered Competitive Signal Detection & Early Warning

**Owner**: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence
**Version**: 1.0 DRAFT — Awaiting Mike's approval
**Last Updated**: 2026-03-25
**Category**: Proactive Intelligence & Monitoring
**Priority**: P1 — Shifts M&CI from reactive to predictive competitive intelligence
**Maturity**: Gap → Designed (this SOP)

---

## Table of Contents

1. [Purpose](#1-purpose)
2. [Scope](#2-scope)
3. [Architecture: Signal Detection & Early Warning System](#3-architecture-signal-detection--early-warning-system)
4. [Signal Source Taxonomy](#4-signal-source-taxonomy)
5. [Signal Scoring Algorithm (SSA)](#5-signal-scoring-algorithm-ssa)
6. [Competitive Movement Prediction Model](#6-competitive-movement-prediction-model)
7. [Weekly "What Changed" Brief](#7-weekly-what-changed-brief)
8. [Forecast Board: Predictive Competitive Dashboard](#8-forecast-board-predictive-competitive-dashboard)
9. [Alert Cascade: Tiered Notification System](#9-alert-cascade-tiered-notification-system)
10. [Monte Carlo Signal Detection Effectiveness Model](#10-monte-carlo-signal-detection-effectiveness-model)
11. [AI Integration Architecture](#11-ai-integration-architecture)
12. [Integration Map](#12-integration-map)
13. [RACI Matrix](#13-raci-matrix)
14. [KPIs](#14-kpis)
15. [Maturity Roadmap](#15-maturity-roadmap)

---

## 1. Purpose

Today, Oracle Health's M&CI function discovers competitive threats when a sales rep calls to say "Epic just showed up in my deal." That is reactive intelligence — the threat is already in the building. This SOP defines the system that surfaces competitive threats and opportunities **before** they reach active deals, giving Oracle Health a structural time advantage.

The goal is not to monitor everything. It is to monitor the **right things** with sufficient analytical depth to distinguish noise from signal, and to predict competitor moves before they are announced.

**Why this matters (quantified):**

- The average enterprise healthcare IT competitive move (product launch, pricing change, acquisition) is visible in leading indicators **3-9 months before** it hits the market. Job postings, patent filings, conference presentations, and regulatory submissions all leak intent.
- Organizations with proactive competitive monitoring identify threats **an average of 47 days earlier** than reactive programs (Crayon State of CI, 2025 — 1,200+ CI professionals surveyed).
- Early detection matters because response time matters: SOP-08 battlecard updates take 5-10 business days. SOP-12 competitive response playbook activation takes 2-4 weeks. SOP-29 War Room packages take 48 hours. If the signal is detected the day Epic launches, Oracle Health is already behind.
- Microsoft's acquisition of Nuance was visible in patent co-citation analysis and joint conference appearances 14 months before the announcement. Competitive signal systems that detected this pattern had a full year to prepare positioning.

**What this SOP produces:**

| Output | Audience | Cadence |
|--------|----------|---------|
| Weekly "What Changed" Brief | Sales Leadership, Product, CI Team | Weekly (Friday delivery) |
| P0 Immediate Alerts | Sales VP, Mike, affected AEs | Real-time (within 2 hours) |
| P1 Same-Day Alerts | CI Team, Sales Leadership | Same business day |
| Competitive Forecast Board | Strategy, Product, Sales Leadership | Continuously updated dashboard |
| Quarterly Signal Analysis Report | Executive Team | Quarterly |
| Competitive Movement Predictions | Strategy, Sales Leadership | Monthly update cycle |

---

## 2. Scope

### In Scope

**Competitors monitored** (tiered monitoring depth):

| Tier | Competitors | Monitoring Depth |
|------|------------|-----------------|
| **Tier 1 — Full Spectrum** | Epic Systems, Meditech | All signal sources, daily sweep, prediction modeling |
| **Tier 2 — Active Monitoring** | Waystar, R1 RCM, FinThrive, Nuance/Microsoft (DAX), athenahealth | All signal sources, 2x/week sweep |
| **Tier 3 — Watch List** | PointClickCare, Netsmart, NextGen, Greenway, TruBridge | News + SEC + job postings, weekly sweep |
| **Tier 4 — Emerging** | AI-native entrants (Regard, Abridge, Ambience), Big Tech (Google Health, Amazon Health) | Quarterly landscape scan + event-triggered |

**Signal categories monitored:**
- Corporate actions (M&A, funding, partnerships, executive changes)
- Product signals (launches, patents, regulatory filings, feature announcements)
- Go-to-market signals (pricing changes, new verticals, channel partnerships)
- Talent signals (hiring patterns, layoffs, key departures)
- Market signals (KLAS updates, analyst reports, regulatory changes)
- Customer signals (reference wins/losses, implementation news, churn indicators)

### Out of Scope

- Oracle Health's own product roadmap monitoring (Product Management)
- Customer satisfaction monitoring for Oracle Health's install base (Customer Success)
- General healthcare industry news curation (Communications)
- Classified or proprietary competitor information (Legal/Ethics — see Section 11.4)

---

## 3. Architecture: Signal Detection & Early Warning System

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│              COMPETITIVE SIGNAL DETECTION & EARLY WARNING ARCHITECTURE            │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐     │
│  │  LAYER 1: SIGNAL COLLECTION (Multi-Source Ingestion)                    │     │
│  │                                                                         │     │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐         │     │
│  │  │ News &  │ │ SEC /   │ │ Job     │ │ Patent  │ │ Product │         │     │
│  │  │ Press   │ │ Regul-  │ │ Posting │ │ & IP    │ │ Release │         │     │
│  │  │ Feeds   │ │ atory   │ │ Monitor │ │ Filings │ │ Tracker │         │     │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘         │     │
│  │       │           │           │           │           │               │     │
│  │  ┌────┴────┐ ┌────┴────┐ ┌────┴────┐ ┌────┴────┐ ┌────┴────┐         │     │
│  │  │ Social  │ │ Confer- │ │ KLAS /  │ │ GitHub  │ │ Field   │         │     │
│  │  │ Media & │ │ ence &  │ │ Analyst │ │ & Open  │ │ Intel   │         │     │
│  │  │ Forums  │ │ Event   │ │ Reports │ │ Source  │ │ Reports │         │     │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘         │     │
│  └───────┴───────────┴───────────┴───────────┴───────────┴───────────────┘     │
│                                  │                                              │
│  ┌───────────────────────────────▼──────────────────────────────────────────┐   │
│  │  LAYER 2: SIGNAL PROCESSING (AI-Powered Classification)                  │   │
│  │                                                                           │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │   │
│  │  │ Entity          │  │ Deduplication &  │  │ Signal Scoring  │          │   │
│  │  │ Extraction &    │  │ Correlation      │  │ Algorithm (SSA) │          │   │
│  │  │ Classification  │  │ Engine           │  │ Impact × Rele-  │          │   │
│  │  │ (NER + LLM)     │  │ (cross-source    │  │ vance × Time    │          │   │
│  │  │                 │  │  linkage)        │  │ Sensitivity     │          │   │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘          │   │
│  └───────────┴────────────────────┴────────────────────┴────────────────────┘   │
│                                   │                                              │
│  ┌────────────────────────────────▼─────────────────────────────────────────┐   │
│  │  LAYER 3: ANALYSIS & PREDICTION                                          │   │
│  │                                                                           │   │
│  │  ┌───────────────────┐  ┌───────────────────┐  ┌──────────────────┐     │   │
│  │  │ Competitive       │  │ Pattern           │  │ Forecast Board   │     │   │
│  │  │ Movement          │  │ Recognition       │  │ (predictive      │     │   │
│  │  │ Prediction Model  │  │ (historical       │  │  landscape       │     │   │
│  │  │ (next move        │  │  signal-to-event  │  │  dashboard)      │     │   │
│  │  │  forecasting)     │  │  correlation)     │  │                  │     │   │
│  │  └─────────┬─────────┘  └─────────┬─────────┘  └────────┬─────────┘     │   │
│  └────────────┴──────────────────────┴─────────────────────┴────────────────┘   │
│                                      │                                           │
│  ┌───────────────────────────────────▼──────────────────────────────────────┐   │
│  │  LAYER 4: ACTION & DISTRIBUTION                                          │   │
│  │                                                                           │   │
│  │  P0: Immediate (2hr) → Slack DM + email + phone if deal-impacting       │   │
│  │  P1: Same-day        → Slack #competitive-intel + email digest           │   │
│  │  P2: Weekly digest   → "What Changed" brief (Friday delivery)            │   │
│  │  P3: Quarterly       → Landscape trend report + prediction scorecard     │   │
│  │                                                                           │   │
│  │  Downstream triggers:                                                     │   │
│  │  → SOP-08 battlecard refresh when product signal detected                │   │
│  │  → SOP-12 competitive response activation when P0/P1 signal             │   │
│  │  → SOP-32 CTI recalculation when deal-relevant signal                   │   │
│  │  → SOP-34 war game scenario trigger when strategic signal                │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Signal Source Taxonomy

### 4.1 Source Categories & Collection Methods

```
SIGNAL SOURCE MATRIX

┌────────────────────────┬───────────────────────────────┬──────────┬──────────────┐
│ Source Category         │ Specific Sources              │ Refresh  │ Collection   │
├────────────────────────┼───────────────────────────────┼──────────┼──────────────┤
│ News & Press Releases  │ PR Newswire, Business Wire,   │ Daily    │ RSS + API    │
│                        │ Globe Newswire, company        │          │ feeds, Google │
│                        │ newsrooms, healthcare trade    │          │ Alerts,       │
│                        │ (Becker's, HIMSS, HIT         │          │ Crayon/Klue   │
│                        │ Consultant, Modern Healthcare) │          │              │
├────────────────────────┼───────────────────────────────┼──────────┼──────────────┤
│ SEC / Regulatory       │ SEC EDGAR (10-K, 10-Q, 8-K,  │ Daily    │ SEC API +    │
│ Filings                │ S-1), FDA 510(k) submissions, │          │ manual review │
│                        │ ONC Health IT certifications,  │          │ for Tier 1    │
│                        │ CMS rule changes               │          │              │
├────────────────────────┼───────────────────────────────┼──────────┼──────────────┤
│ Job Postings           │ LinkedIn, Indeed, company      │ 2x/week │ API + web    │
│                        │ career pages, Glassdoor        │          │ scrape (job  │
│                        │                               │          │ taxonomy map) │
├────────────────────────┼───────────────────────────────┼──────────┼──────────────┤
│ Patent & IP Filings    │ USPTO, Google Patents,         │ Monthly  │ Patent API + │
│                        │ WIPO (international)           │          │ keyword      │
│                        │                               │          │ monitoring    │
├────────────────────────┼───────────────────────────────┼──────────┼──────────────┤
│ Product Releases       │ Company blogs, product         │ Daily    │ RSS + manual │
│                        │ changelogs, app store updates, │          │ review for   │
│                        │ developer documentation        │          │ Tier 1       │
├────────────────────────┼───────────────────────────────┼──────────┼──────────────┤
│ Conference & Events    │ HIMSS, CHIME, ViVE, HLTH,     │ Event-   │ Agenda       │
│                        │ HFMA, MGMA, vendor user        │ driven   │ monitoring + │
│                        │ conferences (UGM, XGM)         │          │ attendee     │
│                        │                               │          │ reports      │
├────────────────────────┼───────────────────────────────┼──────────┼──────────────┤
│ KLAS / Analyst         │ KLAS Research, Gartner (Magic │ Quarterly│ Subscription │
│ Reports                │ Quadrant, Hype Cycle), CHIME  │ + event  │ access +     │
│                        │ Digital Health Most Wired      │ trigger  │ manual       │
│                        │                               │          │ extraction   │
├────────────────────────┼───────────────────────────────┼──────────┼──────────────┤
│ Social Media /         │ LinkedIn posts (competitor     │ Daily    │ Social       │
│ Community              │ execs), X/Twitter, Reddit      │          │ listening    │
│                        │ (r/healthIT, r/nursing),       │          │ tools +      │
│                        │ CHIME/AMDIS listservs          │          │ keyword      │
│                        │                               │          │ monitoring   │
├────────────────────────┼───────────────────────────────┼──────────┼──────────────┤
│ Open Source / GitHub   │ Competitor OSS repos, FHIR    │ Weekly   │ GitHub API + │
│                        │ implementation guides, API     │          │ starred repo │
│                        │ documentation changes          │          │ tracking     │
├────────────────────────┼───────────────────────────────┼──────────┼──────────────┤
│ Field Intelligence     │ Sales rep reports, partner     │ Cont-    │ Salesforce   │
│                        │ intel, customer conversations, │ inuous   │ CI field +   │
│                        │ consultant relationships       │          │ Slack intake │
└────────────────────────┴───────────────────────────────┴──────────┴──────────────┘
```

### 4.2 Source Reliability Weighting

Not all sources are equal. A 10-K filing is fact. A Reddit post is rumor. The SSA (Section 5) applies reliability weights:

| Reliability Tier | Sources | Weight Multiplier |
|-----------------|---------|-------------------|
| **Tier A — Verified** | SEC filings, FDA submissions, patent grants, official press releases, KLAS published scores | 1.0 |
| **Tier B — Credible** | Job postings (direct from company), conference presentations, product documentation, analyst reports | 0.8 |
| **Tier C — Indicative** | News articles (third-party), LinkedIn executive posts, partner announcements | 0.6 |
| **Tier D — Anecdotal** | Field rep reports (single source), social media, forum posts, unverified customer conversations | 0.3 |

**Corroboration Rule:** A Tier D signal that is corroborated by a Tier B or Tier A signal gets upgraded to Tier B weighting. Two independent Tier C signals from different source categories get upgraded to Tier B. Corroboration is the mechanism that turns noise into signal.

---

## 5. Signal Scoring Algorithm (SSA)

The SSA evaluates every detected signal on three dimensions and produces a composite score that determines routing priority.

### 5.1 Scoring Dimensions

```
SSA COMPOSITE SCORE

SSA = Impact × Relevance × Time_Sensitivity × Source_Reliability

Each dimension is scored 1-5. Maximum SSA = 5 × 5 × 5 × 1.0 = 125.

DIMENSION 1: IMPACT SEVERITY (1-5)
  How significantly could this signal change the competitive landscape?

  5 — Market-reshaping (M&A of top-3 competitor, new regulatory mandate,
      platform architecture change affecting entire market)
  4 — Segment-shifting (new product category entry, pricing model overhaul,
      major partnership that changes competitive dynamics)
  3 — Deal-impacting (product feature launch, key executive hire,
      competitive win in strategic account, KLAS score change >5 points)
  2 — Incrementally relevant (minor product update, small partnership,
      regional expansion, non-executive hire)
  1 — Background noise (routine PR, minor event appearance,
      social media activity without substance)

DIMENSION 2: RELEVANCE TO ORACLE HEALTH (1-5)
  How directly does this signal affect Oracle Health's competitive position?

  5 — Directly targets Oracle Health (competitor launches "migrate from
      Oracle" campaign, poaches Oracle Health executive, wins Oracle
      Health reference account)
  4 — Affects active deals (competitor action in segment where Oracle
      Health has >3 active deals, pricing change in Oracle Health's
      primary market)
  3 — Affects strategic positioning (competitor moves into Oracle
      Health's growth areas, technology shift that changes buying
      criteria)
  2 — Affects adjacent markets (competitor action in a segment Oracle
      Health plans to enter, partnership in complementary technology)
  1 — General market relevance (industry trend, distant competitor
      action, technology development with unclear timing)

DIMENSION 3: TIME SENSITIVITY (1-5)
  How quickly must Oracle Health act on this signal?

  5 — Immediate action required (competitor in active deal, pricing
      undercut in live negotiation, product launch affecting current
      quarter pipeline)
  4 — This week (strategic move that will affect deals in next 30 days,
      executive departure creating window of opportunity)
  3 — This month (market shift requiring positioning adjustment,
      product launch requiring battlecard update)
  2 — This quarter (trend requiring strategic planning, technology
      development requiring roadmap consideration)
  1 — Tracking horizon (early indicator, long-range signal, no
      immediate action but worth monitoring pattern)
```

### 5.2 SSA Priority Classification

```
SSA PRIORITY ROUTING

SSA Score → Priority Level → Routing

  SSA ≥ 60 (or Impact=5 with Relevance≥4)
    → P0 — IMMEDIATE
    → Alert: Mike + Sales VP + affected AEs within 2 hours
    → Actions: SOP-12 activation review, SOP-08 emergency update,
               SOP-32 CTI recalculation for affected deals

  SSA 30-59
    → P1 — SAME DAY
    → Alert: Slack #competitive-intel + email to CI distribution list
    → Actions: Brief prepared for next leadership touchpoint,
               battlecard review queued

  SSA 10-29
    → P2 — WEEKLY DIGEST
    → Included in Friday "What Changed" brief
    → Actions: Logged in signal database, pattern analysis queued

  SSA < 10
    → P3 — ARCHIVE
    → Logged in signal database for pattern analysis
    → No active distribution
```

### 5.3 AI-Assisted Scoring

For Phases 2+ of the maturity roadmap, SSA scoring is AI-assisted:

```
AI SCORING PIPELINE

1. Signal ingested from collection layer (raw text + metadata)

2. Entity Extraction (NER model):
   - Identify: competitor name, product, person, organization, dollar amount
   - Classify: signal category (corporate, product, GTM, talent, market, customer)

3. LLM Classification (GPT-4 / Claude with structured output):
   Prompt template:
   """
   You are a healthcare IT competitive intelligence analyst.
   Given this competitive signal, score it on three dimensions:

   Signal: {signal_text}
   Source: {source_type}
   Competitor: {extracted_competitor}

   Score each dimension 1-5 with a one-sentence justification:
   1. Impact Severity: [1-5] — {justification}
   2. Relevance to Oracle Health: [1-5] — {justification}
   3. Time Sensitivity: [1-5] — {justification}

   Output as JSON.
   """

4. Human-in-the-Loop Review:
   - P0 signals: Mike reviews and confirms before alert dispatch
   - P1 signals: Mike reviews within same business day
   - P2/P3 signals: Batch review in weekly signal review session

5. Feedback Loop:
   - Mike's adjustments to AI scores are logged as training data
   - Quarterly retraining of scoring calibration
   - Target: AI scoring matches Mike's scoring 85%+ of the time
     within 6 months of deployment
```

---

## 6. Competitive Movement Prediction Model

### 6.1 Concept

The Prediction Model analyzes patterns in historical signals to forecast likely competitor moves before they are announced. This is the most advanced capability in the system — it transforms competitive intelligence from "what happened" to "what is likely to happen next."

### 6.2 Prediction Algorithm

```
COMPETITIVE MOVEMENT PREDICTION MODEL (CMPM)

Principle: Competitor actions are rarely surprises. They follow observable
patterns. A product launch is preceded by engineering hires, patent filings,
beta program announcements, and conference preview sessions. An acquisition
is preceded by executive meetings, joint ventures, co-development agreements,
and unusual hiring patterns.

PATTERN LIBRARY (seeded from industry analysis, refined with Oracle data):

┌────────────────────────────────┬─────────────────────────────────────────┐
│ Leading Indicator Pattern      │ Predicted Outcome                       │
│                                │ (Confidence | Typical Lead Time)        │
├────────────────────────────────┼─────────────────────────────────────────┤
│ 15+ ML/AI engineering hires    │ AI product launch                       │
│ in 90-day window               │ (0.75 confidence | 6-12 months)        │
├────────────────────────────────┼─────────────────────────────────────────┤
│ Patent cluster (3+ filings)    │ New product category or major feature  │
│ in related technology area     │ (0.65 confidence | 12-24 months)       │
├────────────────────────────────┼─────────────────────────────────────────┤
│ Executive hire from adjacent   │ Market entry into that executive's     │
│ industry or competitor         │ domain                                  │
│                                │ (0.70 confidence | 6-18 months)        │
├────────────────────────────────┼─────────────────────────────────────────┤
│ Joint conference appearances   │ Partnership or acquisition             │
│ + co-authored content with     │ (0.55 confidence | 6-24 months)        │
│ another company                │                                        │
├────────────────────────────────┼─────────────────────────────────────────┤
│ Sudden headcount reduction     │ Strategic pivot, product line           │
│ in specific division           │ rationalization, or financial pressure  │
│                                │ (0.60 confidence | 3-9 months)         │
├────────────────────────────────┼─────────────────────────────────────────┤
│ Sales/BD hiring surge in       │ Market expansion into that geography   │
│ new geography                  │ or segment                             │
│                                │ (0.80 confidence | 3-6 months)         │
├────────────────────────────────┼─────────────────────────────────────────┤
│ Regulatory certification       │ Product launch in regulated category   │
│ application filed              │ (0.85 confidence | 6-18 months)        │
├────────────────────────────────┼─────────────────────────────────────────┤
│ Pricing page restructured +    │ Pricing model change or new tier       │
│ new packaging language         │ (0.75 confidence | 1-3 months)         │
├────────────────────────────────┼─────────────────────────────────────────┤
│ Key customer win in new        │ Vertical expansion strategy            │
│ vertical + case study          │ (0.70 confidence | ongoing)            │
│ published                      │                                        │
└────────────────────────────────┴─────────────────────────────────────────┘
```

### 6.3 Prediction Scoring

```
PREDICTION CONFIDENCE CALCULATION

For each detected pattern match:

  P_move = P_base × corroboration_factor × recency_factor × competitor_history

Where:

  P_base = Pattern library base confidence (from table above)

  corroboration_factor:
    1 signal source category:  1.0 (base)
    2 source categories:       1.15
    3+ source categories:      1.25
    Cap at 0.95 (no prediction is certain)

  recency_factor:
    Signals all within 30 days:  1.1
    Signals within 90 days:      1.0
    Signals spanning 90-180 days: 0.85
    Signals older than 180 days: 0.60

  competitor_history:
    Has this competitor executed this type of move before?
    Yes (within 3 years): 1.1
    No prior history:     0.9
    Counter-pattern (competitor explicitly denied this direction): 0.7

OUTPUT: Prediction Card
  ┌─────────────────────────────────────────────────┐
  │ PREDICTION: [Competitor] likely to [Action]      │
  │ Confidence: [P_move as percentage]               │
  │ Estimated Timeline: [Range from pattern library] │
  │ Evidence: [List of contributing signals]          │
  │ Impact on Oracle Health: [Assessment]             │
  │ Recommended Response: [Action items]              │
  │ Last Updated: [Date]                              │
  │ Status: Active | Confirmed | Disconfirmed         │
  └─────────────────────────────────────────────────┘
```

### 6.4 Prediction Tracking & Calibration

```
PREDICTION SCORECARD (Quarterly Review)

For each prediction made in Q-1:

  Outcome:
    CONFIRMED — Predicted move occurred within estimated timeline
    PARTIALLY CONFIRMED — Move occurred but with significant variation
    DISCONFIRMED — Move did not occur within 2x the estimated timeline
    PENDING — Still within estimated timeline window

  Metrics:
    Prediction Accuracy = CONFIRMED / (CONFIRMED + DISCONFIRMED)
    Target: >55% accuracy (substantially above random baseline)
    Note: 55% may seem low, but in competitive intelligence,
    predicting competitor moves with >50% accuracy is valuable
    because the base rate of any specific prediction is <10%.

    Calibration: Are 70%-confidence predictions confirmed ~70% of the time?
    Plot calibration curve quarterly (same methodology as SOP-32 Section 6.4).
```

---

## 7. Weekly "What Changed" Brief

### 7.1 Format & Structure

The "What Changed" brief is a concise, executive-readable digest of the week's competitive intelligence. It is the primary distribution vehicle for P2 signals and prediction updates.

```
WEEKLY "WHAT CHANGED" BRIEF — FORMAT TEMPLATE

Delivery: Every Friday by 12:00 PM ET
Length: 2 pages maximum (executive attention span = 90 seconds for CI)
Distribution: Email + Slack #competitive-intel + SharePoint archive

Structure:

  1. TOP SIGNAL (1 paragraph)
     The single most important competitive development this week.
     What happened, why it matters, what Oracle Health should consider.

  2. SIGNAL SUMMARY TABLE (5-8 rows max)
     ┌──────────┬──────────┬──────────┬──────────┬───────────┐
     │ Date     │ Compet-  │ Signal   │ SSA      │ Action    │
     │          │ itor     │ Summary  │ Score    │ Required  │
     ├──────────┼──────────┼──────────┼──────────┼───────────┤
     │ [date]   │ [name]   │ [1 line] │ [score]  │ [Y/N/Mon] │
     └──────────┴──────────┴──────────┴──────────┴───────────┘

  3. PREDICTION UPDATES (if any)
     New predictions, confidence changes, confirmed/disconfirmed outcomes.

  4. DEAL IMPACT ASSESSMENT (if applicable)
     Which active deals are affected by this week's signals?
     Cross-reference with SOP-32 deal scores.

  5. LOOKING AHEAD
     Events, earnings calls, conferences in next 2 weeks
     that may generate competitive signals.
```

### 7.2 Auto-Generation Pipeline

```
BRIEF GENERATION WORKFLOW (AI-Assisted)

1. Thursday 4:00 PM: System compiles all P1/P2 signals from the week
2. Thursday 4:30 PM: LLM generates draft brief from signal database
   - Summarizes each signal into one-line description
   - Ranks signals by SSA score
   - Cross-references with active deal pipeline
   - Generates "Looking Ahead" from event calendar
3. Thursday 5:00 PM: Mike reviews and edits draft
   - Adds strategic interpretation
   - Adjusts signal prioritization
   - Adds deal-specific context that AI cannot infer
4. Friday 8:00 AM: Final brief approved
5. Friday 12:00 PM: Brief distributed via email + Slack

Target: AI generates 70% of brief content; Mike adds 30% strategic value.
Time savings: 3 hours/week vs. fully manual brief production.
```

---

## 8. Forecast Board: Predictive Competitive Dashboard

### 8.1 Dashboard Design

The Forecast Board is a continuously updated dashboard that visualizes the competitive landscape not as it is today, but as it is likely to evolve over the next 3-12 months.

```
FORECAST BOARD LAYOUT

┌──────────────────────────────────────────────────────────────┐
│  COMPETITIVE FORECAST BOARD — Oracle Health M&CI             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─── THREAT RADAR ───────────────────────────────────┐     │
│  │                                                     │     │
│  │  Concentric rings: 0-3mo | 3-6mo | 6-12mo | 12mo+ │     │
│  │  Competitor markers sized by impact severity        │     │
│  │  Color: Red (confirmed) | Orange (predicted) |      │     │
│  │         Gray (monitoring)                           │     │
│  │                                                     │     │
│  │  [Competitors positioned by predicted move timing]  │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌─── ACTIVE PREDICTIONS ─────────────────────────────┐     │
│  │  Prediction | Competitor | Confidence | Timeline    │     │
│  │  AI launch  | Epic       | 72%        | Q3-Q4 2026 │     │
│  │  RCM pivot  | Waystar    | 65%        | Q2 2026    │     │
│  │  [sorted by confidence × impact]                    │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌─── SIGNAL VELOCITY ────────────────────────────────┐     │
│  │  Competitor signal volume (trailing 30 days)        │     │
│  │  Spike detection: Which competitor is generating     │     │
│  │  abnormal signal volume? (>2σ above baseline)       │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌─── PIPELINE EXPOSURE ──────────────────────────────┐     │
│  │  Active deals × CTI overlay                        │     │
│  │  $TCV at risk by competitor                        │     │
│  │  Trend: improving / stable / deteriorating          │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 9. Alert Cascade: Tiered Notification System

### 9.1 Alert Tier Definitions

| Priority | Trigger | Channel | SLA | Example |
|----------|---------|---------|-----|---------|
| **P0 — Immediate** | SSA ≥ 60, or Impact=5 + Relevance ≥ 4 | Slack DM to Mike + Sales VP + affected AEs. Email. Phone call for deal-impacting signals. | 2 hours from signal detection to alert delivery. | Epic announces cloud-native EHR, directly competing with Oracle Health's modernization narrative. |
| **P1 — Same Day** | SSA 30-59 | Slack #competitive-intel + email to CI distribution. | Same business day. | Competitor hires Oracle Health's former VP of Engineering. |
| **P2 — Weekly** | SSA 10-29 | Included in Friday "What Changed" brief. | Friday delivery. | Competitor publishes case study in new vertical. |
| **P3 — Archive** | SSA < 10 | Signal database only. | No distribution SLA. | Competitor exec posts on LinkedIn about AI vision. |

### 9.2 Alert Content Template

```
P0/P1 ALERT FORMAT

Subject: [P0/P1] [Competitor]: [Signal headline]

SIGNAL: [What happened — 2 sentences max]
SOURCE: [Source type + reliability tier]
SSA SCORE: [Score] (Impact: X | Relevance: X | Time Sensitivity: X)

DEAL IMPACT: [Which active deals are affected, if any]
  - [Deal name] — CTI impact: [current → projected]
  - [Deal name] — CTI impact: [current → projected]

RECOMMENDED ACTIONS:
  1. [Specific action with owner]
  2. [Specific action with owner]

SOP TRIGGERS:
  □ SOP-08 battlecard update required? [Y/N]
  □ SOP-12 competitive response activation? [Y/N]
  □ SOP-29 deal support activation? [Y/N]
  □ SOP-32 CTI recalculation? [Y/N]
  □ SOP-34 war game scenario trigger? [Y/N]

CONTEXT: [1-2 sentences of strategic context — why this matters beyond the obvious]
```

---

## 10. Monte Carlo Signal Detection Effectiveness Model

### 10.1 Purpose

How confident are we that our signal detection system is actually catching what matters? This Monte Carlo simulation models the system's detection coverage and identifies blind spots.

### 10.2 Simulation Design

```
SIGNAL DETECTION EFFECTIVENESS SIMULATION

Objective: Estimate the probability that a significant competitive move
(Impact ≥ 4) is detected by our system before it becomes public knowledge.

Model:

  FOR i = 1 TO 10,000:

    1. Simulate a competitive event:
       event_type ~ Categorical(corporate: 0.15, product: 0.30,
                                GTM: 0.20, talent: 0.15,
                                market: 0.10, customer: 0.10)
       impact ~ Uniform(4, 5)  [only modeling significant events]
       lead_time ~ LogNormal(μ=4.5, σ=0.8) months [time from first
                                                     signal to public
                                                     announcement]

    2. For each signal source s in our taxonomy:
       P_detects_s = source_coverage[event_type][s]
       detected_s ~ Bernoulli(P_detects_s)
       if detected_s:
         detection_time_s ~ Uniform(0, lead_time × 0.8)
         [most signals appear in the first 80% of lead time]

    3. System detects event if ANY source detects it:
       system_detected = OR(detected_s for all s)
       earliest_detection = MIN(detection_time_s for detected sources)
       advance_warning = lead_time - earliest_detection

  END FOR

  OUTPUT:
    Detection Rate = system_detected events / total events
    Median Advance Warning = median(advance_warning | detected)
    P10 Advance Warning = 10th percentile (worst case for detected events)
    Blind Spot Map = event types with detection rate < 50%
```

### 10.3 Source Coverage Matrix (Model Input)

```
SOURCE COVERAGE BY EVENT TYPE [P(detection)]

                    News  SEC   Jobs  Patent  Product  Social  Conf  KLAS  Field
Corporate (M&A)    0.90  0.85  0.40  0.10    0.05     0.50    0.30  0.05  0.30
Product Launch      0.70  0.10  0.60  0.50    0.95     0.60    0.70  0.40  0.50
GTM / Pricing       0.40  0.15  0.30  0.05    0.60     0.30    0.40  0.20  0.70
Talent Shift        0.30  0.05  0.90  0.05    0.05     0.70    0.20  0.05  0.40
Market / Regulatory 0.80  0.70  0.10  0.20    0.30     0.40    0.50  0.60  0.20
Customer Win/Loss   0.50  0.05  0.05  0.05    0.30     0.40    0.30  0.50  0.80

Expected system detection rate (at least 1 source):
  Corporate: ~99%    (highly public events — hard to miss)
  Product:   ~99%    (many signal sources)
  GTM:       ~92%    (pricing moves are harder to detect)
  Talent:    ~97%    (job postings are leading indicators)
  Market:    ~98%    (regulatory and analyst signals are strong)
  Customer:  ~95%    (field intel is the crucial source here)

Weighted average detection rate: ~97%
Median advance warning: 2.3 months (for detected events)

PRIMARY BLIND SPOT: Pricing/GTM moves — lowest detection rate.
Mitigation: Increase field intelligence collection focus on pricing signals.
```

---

## 11. AI Integration Architecture

### 11.1 Technology Stack

| Component | Tool / Platform | Role |
|-----------|----------------|------|
| Signal Ingestion | Crayon / Klue / custom RSS aggregator | Automated collection from 50+ sources |
| Entity Extraction | SpaCy NER + custom healthcare IT entity model | Identify competitors, products, people |
| Signal Scoring | LLM (Claude/GPT-4) with structured output | AI-assisted SSA scoring with human review |
| Deduplication | Embedding similarity (>0.92 cosine = duplicate) | Prevent same signal from multiple sources inflating scores |
| Brief Generation | LLM with weekly signal database as context | Auto-draft "What Changed" brief |
| Prediction Engine | Pattern matching + Bayesian updating | Competitive movement forecasting |
| Dashboard | Tableau / Power BI | Forecast Board visualization |

### 11.2 Ellen v13 Integration Roadmap

This SOP aligns with the Ellen v13 Proactive Intelligence capability roadmap:

| Ellen v13 Phase | SOP-33 Capability | Timeline |
|----------------|-------------------|----------|
| Ellen v13.1 — Automated Collection | Layer 1 (signal collection) fully automated | Q2 2026 |
| Ellen v13.2 — AI-Assisted Scoring | Layer 2 (SSA scoring) AI-assisted with human review | Q3 2026 |
| Ellen v13.3 — Predictive Intelligence | Layer 3 (prediction model) operational | Q4 2026 |
| Ellen v13.4 — Autonomous Alerting | Full pipeline: collect → score → predict → alert → trigger SOPs | H1 2027 |

### 11.3 Data Pipeline Architecture

```
SIGNAL DATA FLOW

  Raw Sources → Collection APIs → Raw Signal Store (JSON)
                                        │
                                        ▼
                              Entity Extraction (NER)
                                        │
                                        ▼
                              Deduplication Engine
                              (embedding similarity)
                                        │
                                        ▼
                              SSA Scoring (AI + Human)
                                        │
                              ┌─────────┴─────────┐
                              ▼                   ▼
                        Signal Database      Alert Dispatch
                        (scored, classified) (P0/P1 routing)
                              │                   │
                              ▼                   ▼
                        Pattern Matching     SOP Triggers
                        (CMPM predictions)   (08, 12, 29, 32)
                              │
                              ▼
                        Forecast Board
                        (dashboard)
```

### 11.4 Legal & Ethical Guardrails

All signal collection must comply with Oracle's legal and ethical standards:

| Rule | Enforcement |
|------|-------------|
| **Public sources only** — No hacking, social engineering, misrepresentation to obtain competitor information | All sources documented; no anonymous accounts or false pretenses |
| **No trade secrets** — If a signal appears to contain competitor trade secrets (e.g., leaked internal document), do not ingest; notify Legal | Mike reviews all P0 signals before distribution |
| **Employee boundary** — Former competitor employees may share general knowledge but not proprietary processes, customer lists, or code | Interview guardrails in SOP-09 apply to any source interaction |
| **GDPR/Privacy** — No collection of individual consumer data; executive and public figure data only from public sources | No scraping of private social media; LinkedIn public profiles only |

---

## 12. Integration Map

```
SOP-33 INTEGRATION DEPENDENCIES

SOP-33 (Signal Detection) FEEDS:
  → SOP-08 (Battlecards): Product signals trigger battlecard refresh
  → SOP-12 (Competitive Response): P0/P1 signals trigger response protocol
  → SOP-29 (Deal Support): Deal-relevant signals trigger package updates
  → SOP-32 (Deal Scoring): Signals update CTI and momentum scores
  → SOP-34 (War Gaming): Strategic signals trigger scenario modeling

SOP-33 RECEIVES FROM:
  ← SOP-09 (Win/Loss): Interview findings generate new signal categories
  ← SOP-29 (Deal Support): Field intel from deal teams
  ← SOP-34 (War Gaming): Scenario outcomes prioritize monitoring focus
```

---

## 13. RACI Matrix

| Activity | Mike Rodgers | CI Analyst (Future) | Sales Ops | Data Engineering | Matt Cohlmia |
|----------|:---:|:---:|:---:|:---:|:---:|
| Signal collection configuration | **R/A** | C | I | C | I |
| Daily signal review & scoring | **R** | **R** (Phase 2+) | — | — | — |
| P0 alert validation & dispatch | **R/A** | C | I | — | **I** |
| Weekly "What Changed" brief | **R/A** | C (draft assist) | I | — | **I** |
| Prediction model maintenance | **R/A** | C | I | C | I |
| Quarterly Signal Analysis Report | **R** | C | I | C | **A** |
| AI pipeline development & tuning | C | C | — | **R/A** | I |
| Legal compliance review | **R** | — | — | — | **A** |

---

## 14. KPIs

### Leading Indicators (Monthly)

| KPI | Target | Measurement |
|-----|--------|-------------|
| Signals processed per week | >50 (Phase 1), >200 (Phase 2+) | Count of scored signals |
| P0/P1 alert-to-delivery SLA compliance | >95% within SLA | Alerts delivered on time / total P0/P1 alerts |
| Signal source diversity | All 10 source categories active | Sources contributing signals per month |
| "What Changed" brief delivery rate | 100% weekly on Friday | Briefs delivered / weeks in quarter |

### Lagging Indicators (Quarterly)

| KPI | Target | Measurement |
|-----|--------|-------------|
| Significant events detected before public announcement | >80% | Events detected / total significant events (post-hoc audit) |
| Median advance warning time | >30 days | Median days between first signal and public event |
| Prediction accuracy | >55% | Confirmed predictions / (Confirmed + Disconfirmed) |
| Stakeholder satisfaction (brief utility) | >4.0/5.0 | Quarterly survey of brief recipients |
| Signal-to-action conversion | >30% of P0/P1 signals result in documented action | Actions taken / P0+P1 signals |

### North Star Metric

**Competitive Surprise Rate**: The percentage of significant competitive events (Impact ≥ 4) that Oracle Health first learns about from external sources (customer call, press coverage) rather than from this signal detection system. Target: <10% surprise rate within 12 months of full deployment.

---

## 15. Maturity Roadmap

| Phase | Timeline | Capability | Dependencies |
|-------|----------|-----------|-------------|
| **Phase 1: Foundation** | Q2 2026 | Manual signal collection from top 5 sources. Manual SSA scoring. Weekly brief (Mike-authored). Google Alerts + Crayon basic license. | Crayon/Klue license. Mike time allocation (8-10 hrs/week). |
| **Phase 2: Semi-Automated** | Q3-Q4 2026 | Automated collection from all 10 source categories. AI-assisted SSA scoring. Auto-draft weekly brief. Signal database operational. | Data engineering support. LLM API access. CI Analyst hire. |
| **Phase 3: Predictive** | H1 2027 | Prediction model operational. Forecast Board dashboard. Automated alert cascade. SOP integration triggers automated. | 12+ months of signal history. BI tool access. Data science consultation. |
| **Phase 4: Autonomous** | H2 2027+ | Full Ellen v13.4 capability. System operates with minimal human intervention for P2/P3 signals. Mike focuses on P0/P1 strategic interpretation and prediction calibration. | Full pipeline maturity. Proven AI scoring accuracy. |

---

*SOP-33 is designed by Mike Rodgers. The system's value is proportional to the breadth and consistency of signal collection. Phase 1 is manual and labor-intensive by design — it builds the pattern recognition intuition and signal taxonomy that make Phase 2+ automation accurate rather than noisy. Do not skip Phase 1.*
