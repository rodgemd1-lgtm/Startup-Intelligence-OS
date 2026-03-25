# SOP-32: Predictive Deal Scoring & Win Probability Engine

**Owner**: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence
**Version**: 1.0 DRAFT — Awaiting Mike's approval
**Last Updated**: 2026-03-25
**Category**: Advanced Analytics & Sales Intelligence
**Priority**: P1 — Transforms CI from backward-looking analysis to forward-looking deal prediction
**Maturity**: Gap → Designed (this SOP)

---

## Table of Contents

1. [Purpose](#1-purpose)
2. [Scope](#2-scope)
3. [Architecture: Predictive Deal Intelligence System](#3-architecture-predictive-deal-intelligence-system)
4. [Deal Scoring Algorithm (DSA)](#4-deal-scoring-algorithm-dsa)
5. [Competitive Threat Index (CTI)](#5-competitive-threat-index-cti)
6. [Monte Carlo Win Probability Simulation](#6-monte-carlo-win-probability-simulation)
7. [Early Warning System](#7-early-warning-system)
8. [Model Training & Feedback Loop](#8-model-training--feedback-loop)
9. [Integration Map](#9-integration-map)
10. [RACI Matrix](#10-raci-matrix)
11. [KPIs](#11-kpis)
12. [Maturity Roadmap](#12-maturity-roadmap)

---

## 1. Purpose

CRM win probability is a lie. Salesforce "probability" is a stage-gate proxy — when a deal reaches Stage 4, it says 60% regardless of whether Epic just scheduled a C-suite dinner or the buyer's champion just got promoted. It measures process, not reality.

This SOP defines a CI-informed predictive deal scoring engine that tells Sales which deals are actually at risk, which are stronger than they appear, and — critically — **why**. It combines competitive landscape data, buyer behavior signals, deal structural characteristics, and historical win/loss patterns into a multi-factor model that produces probabilistic win estimates, not point forecasts.

**Why this matters (quantified):**

- CRM stage-based probability has a **correlation of 0.31 with actual outcomes** across enterprise software (Gartner Sales Analytics, 2025). That is barely better than a coin flip.
- Deals where reps received early risk warnings and adjusted strategy showed a **22% higher save rate** versus deals where risk was identified after the loss (SOP-09 internal win/loss data, Q3-Q4 2025).
- The average Oracle Health competitive deal has a 6-9 month cycle. Identifying risk 30 days earlier gives the team a full competitive response cycle (SOP-29 War Room activation takes 48 hours; strategy adjustment takes 2-4 weeks).
- Forrester reports that organizations using predictive deal intelligence see **15-25% improvements in forecast accuracy** and **10-18% increases in win rates** on competitive deals.

**What this SOP produces:**

| Output | Audience | Cadence |
|--------|----------|---------|
| Deal Score Dashboard | Sales VPs, AEs, Deal Desk | Real-time (updated on signal change) |
| Weekly Risk Report | Sales Leadership, CI Team | Weekly (Monday delivery) |
| Deal-Specific Win Probability Brief | AE, SE (per request) | On-demand + auto-trigger on score change |
| Quarterly Model Performance Report | CI Team, Sales Ops | Quarterly |
| Early Warning Alerts | AE, Sales VP, CI Team | Event-triggered (within 4 hours) |

---

## 2. Scope

### In Scope

- All active competitive deals in the Oracle Health pipeline where a named competitor is confirmed
- Deal sizes: >$2M TCV (scored), >$5M TCV (scored + monitored), >$10M TCV (scored + monitored + Early Warning active)
- Competitors: Full tracked set per SOP-08 (Epic, Meditech, Waystar, R1 RCM, FinThrive, Nuance/Microsoft DAX, athenahealth, PointClickCare, Netsmart, NextGen, emerging entrants)
- Data inputs: Salesforce activity data, win/loss interview findings (SOP-09), pricing intelligence (SOP-10), competitive signal data (SOP-33), deal support requests (SOP-29)
- Outputs: probabilistic win estimates (P10/P50/P90 bands), competitive threat scores, early warning alerts, model performance metrics

### Out of Scope

- Non-competitive deals (sole-source, renewals without competitive threat)
- Deal pricing strategy or discount recommendations (Deal Desk / Finance — though pricing intelligence from SOP-10 is an input)
- Sales forecasting (Sales Ops owns the forecast; this model informs it but does not replace it)
- CRM probability field management (Sales Ops — though we recommend alignment over time)

---

## 3. Architecture: Predictive Deal Intelligence System

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    PREDICTIVE DEAL INTELLIGENCE ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │  DATA LAYER: Signal Collection                                          │   │
│  │                                                                          │   │
│  │  Salesforce         Win/Loss DB       Pricing Intel     Signal Engine   │   │
│  │  (SOP-29 reqs)      (SOP-09)          (SOP-10)          (SOP-33)       │   │
│  │  ┌──────────┐      ┌──────────┐      ┌──────────┐     ┌──────────┐    │   │
│  │  │ Activity │      │ Interview│      │ Price    │     │ Comp     │    │   │
│  │  │ Timeline │      │ Themes   │      │ Position │     │ Signals  │    │   │
│  │  │ Stage    │      │ Loss     │      │ Discount │     │ Threat   │    │   │
│  │  │ Contacts │      │ Drivers  │      │ Bands    │     │ Moves    │    │   │
│  │  └────┬─────┘      └────┬─────┘      └────┬─────┘     └────┬─────┘    │   │
│  └───────┼─────────────────┼─────────────────┼────────────────┼──────────┘   │
│          └─────────────────┴─────────────────┴────────────────┘              │
│                                    │                                         │
│  ┌─────────────────────────────────▼────────────────────────────────────┐    │
│  │  SCORING LAYER: Deal Scoring Algorithm (DSA)                         │    │
│  │                                                                       │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │    │
│  │  │ Competitive  │  │ Buyer        │  │ Deal         │               │    │
│  │  │ Intensity    │  │ Behavior     │  │ Structure    │               │    │
│  │  │ Score (CIS)  │  │ Score (BBS)  │  │ Fit (DSF)   │               │    │
│  │  │ Weight: 0.30 │  │ Weight: 0.35 │  │ Weight: 0.20│               │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │    │
│  │         └─────────────────┼─────────────────┘                        │    │
│  │                           │                                           │    │
│  │         ┌─────────────────▼─────────────────┐                        │    │
│  │         │ Historical Pattern Match (HPM)     │                        │    │
│  │         │ Weight: 0.15                       │                        │    │
│  │         │ Bayesian prior from SOP-09 data    │                        │    │
│  │         └─────────────────┬─────────────────┘                        │    │
│  └───────────────────────────┼──────────────────────────────────────────┘    │
│                              │                                               │
│  ┌───────────────────────────▼──────────────────────────────────────────┐    │
│  │  SIMULATION LAYER: Monte Carlo Win Probability                       │    │
│  │                                                                       │    │
│  │  DSA Score + Variable Ranges → 10,000 simulated outcomes             │    │
│  │  Output: P10 / P50 / P90 win probability bands                      │    │
│  │  Confidence interval: ±8% at n=10,000 iterations                    │    │
│  └───────────────────────────┬──────────────────────────────────────────┘    │
│                              │                                               │
│  ┌───────────────────────────▼──────────────────────────────────────────┐    │
│  │  ACTION LAYER: Early Warning System + Deal Intelligence Output       │    │
│  │                                                                       │    │
│  │  P50 < 40% → Red Alert (AE + Sales VP notified, SOP-29 activated)  │    │
│  │  P50 drops >15pts in 7 days → Trajectory Alert                      │    │
│  │  CTI > 0.8 → Competitive Escalation (War Room recommended)          │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Deal Scoring Algorithm (DSA)

The DSA produces a composite score from 0-100 for every active competitive deal. The score is not a win probability — it is an input to the Monte Carlo simulation that produces probability bands. The DSA measures **deal health** across four dimensions.

### 4.1 Component Weights

| Component | Weight | Rationale |
|-----------|--------|-----------|
| **Buyer Behavior Score (BBS)** | 0.35 | SOP-09 data: buyer behavior signals are the strongest predictor of outcomes. Champion engagement, stakeholder access, and evaluation momentum predict wins/losses better than any other factor. |
| **Competitive Intensity Score (CIS)** | 0.30 | Who you're competing against and how aggressively they're pursuing the deal is the second-strongest predictor. Epic in a hospital deal is a different competitive event than NextGen in an ambulatory deal. |
| **Deal Structure Fit (DSF)** | 0.20 | How well the deal's characteristics (size, segment, requirements) match Oracle Health's historical strengths. We win certain deal shapes consistently; we lose others consistently. |
| **Historical Pattern Match (HPM)** | 0.15 | Bayesian prior: how have deals with this profile resolved historically? Small weight because each deal is unique, but patterns exist. |

**Composite DSA Formula:**

```
DSA = (BBS × 0.35) + (CIS × 0.30) + (DSF × 0.20) + (HPM × 0.15)

Where each component is normalized to 0-100 scale.
Higher DSA = healthier deal position.
```

### 4.2 Buyer Behavior Score (BBS) — Weight 0.35

The BBS captures observable buyer engagement signals that predict deal trajectory. These are sourced from Salesforce activity logs, rep-reported intel, and deal review notes.

```
BBS = Σ(signal_i × weight_i × recency_decay_i)

Signals and weights:
┌──────────────────────────────────────┬────────┬──────────────────────────┐
│ Signal                               │ Weight │ Measurement              │
├──────────────────────────────────────┼────────┼──────────────────────────┤
│ Champion Engagement Level            │ 0.25   │ Contact frequency,       │
│                                      │        │ response time, internal  │
│                                      │        │ advocacy evidence        │
├──────────────────────────────────────┼────────┼──────────────────────────┤
│ Stakeholder Access Breadth           │ 0.20   │ # of unique buyer-side   │
│                                      │        │ contacts engaged, seniority│
│                                      │        │ mix (C-suite, VP, Director)│
├──────────────────────────────────────┼────────┼──────────────────────────┤
│ Evaluation Momentum                  │ 0.20   │ Stage progression speed   │
│                                      │        │ vs. median for deal size  │
│                                      │        │ and segment. Stalls       │
│                                      │        │ penalized exponentially.  │
├──────────────────────────────────────┼────────┼──────────────────────────┤
│ Information Sharing Reciprocity      │ 0.15   │ Is the buyer sharing     │
│                                      │        │ internal docs, timelines, │
│                                      │        │ budgets? Asymmetric info  │
│                                      │        │ flow = losing position.   │
├──────────────────────────────────────┼────────┼──────────────────────────┤
│ Meeting Quality Index                │ 0.10   │ Meetings with decision   │
│                                      │        │ makers vs. gatekeepers.   │
│                                      │        │ Discovery depth.          │
├──────────────────────────────────────┼────────┼──────────────────────────┤
│ Competitor Reference Frequency       │ 0.10   │ How often does the buyer  │
│                                      │        │ mention competitors?      │
│                                      │        │ Increasing = threat.      │
└──────────────────────────────────────┴────────┴──────────────────────────┘

Recency Decay Function:
  recency_decay = e^(-λt)
  where λ = 0.05, t = days since last signal observation
  Signals older than 45 days receive <10% weight.
  Signals older than 90 days are excluded entirely.
```

**Behavioral Science Integration (from SOP-09):**

The BBS incorporates behavioral indicators mapped to SOP-09's decision driver framework:

| Behavioral Force | Observable Signal | BBS Impact |
|-----------------|-------------------|------------|
| Champion Risk (SOP-09) | Champion stops forwarding internal emails, reduces meeting attendance | BBS drops 15-25 points |
| Status Quo Bias | Buyer delays timeline >2x, adds "additional evaluation steps" | BBS drops 10-20 points |
| FOMU > FOMO | Buyer requests 3rd+ reference call, asks about implementation failures | BBS neutral (information seeking) but flags risk |
| DMU Conflict | Different stakeholders give contradictory priority signals | BBS drops 10-15 points |

### 4.3 Competitive Intensity Score (CIS) — Weight 0.30

The CIS measures how difficult the competitive environment is for a specific deal. It is derived from the Competitive Threat Index (CTI, see Section 5) plus deal-specific competitive dynamics.

```
CIS = 100 - (CTI × 100)

Where CTI is normalized to 0-1 (see Section 5).
CIS of 100 = no competitive threat (sole source).
CIS of 0 = maximum competitive threat (strong incumbent + aggressive challenger).

Adjustments:
  - Competitor scheduled C-suite executive briefing: CIS -= 10
  - Competitor offering extended POC / pilot: CIS -= 8
  - Competitor below Oracle Health price by >20%: CIS -= 12
  - Oracle Health is incumbent: CIS += 15
  - Oracle Health has live reference in buyer's peer set: CIS += 10
```

### 4.4 Deal Structure Fit (DSF) — Weight 0.20

The DSF measures how well the deal's characteristics match Oracle Health's historical win profile. This is derived from segmentation analysis of SOP-09 win/loss data.

```
DSF = Σ(factor_j × match_score_j)

Factors:
┌──────────────────────────────┬────────┬──────────────────────────────────┐
│ Factor                       │ Weight │ Scoring                          │
├──────────────────────────────┼────────┼──────────────────────────────────┤
│ Organization Size Match      │ 0.25   │ 100 if deal size in Oracle's    │
│                              │        │ win-rate sweet spot; scaled      │
│                              │        │ down by distance from optimum    │
├──────────────────────────────┼────────┼──────────────────────────────────┤
│ Product-Market Fit           │ 0.25   │ Oracle's win rate in this        │
│                              │        │ specific product category         │
│                              │        │ (EHR vs. RCM vs. AI/Clinical)   │
├──────────────────────────────┼────────┼──────────────────────────────────┤
│ Buyer Priority Alignment     │ 0.20   │ Overlap between buyer's stated  │
│                              │        │ priorities and Oracle Health's    │
│                              │        │ top 5 differentiators            │
├──────────────────────────────┼────────┼──────────────────────────────────┤
│ Implementation Complexity    │ 0.15   │ Inverse score: higher complexity │
│                              │        │ = lower DSF (implementation      │
│                              │        │ risk is Oracle's #2 loss driver  │
│                              │        │ per SOP-09)                      │
├──────────────────────────────┼────────┼──────────────────────────────────┤
│ Geographic / Segment         │ 0.15   │ Oracle's win rate in this        │
│ Familiarity                  │        │ region and care setting           │
└──────────────────────────────┴────────┴──────────────────────────────────┘
```

### 4.5 Historical Pattern Match (HPM) — Weight 0.15

The HPM is a Bayesian prior derived from historical deal outcomes. It answers: "When we've seen deals that look like this one before, what happened?"

```
HPM Algorithm (k-Nearest Neighbors with Bayesian Updating):

1. Feature vector for current deal:
   F = [competitor_set, deal_size_bucket, segment, product_mix,
        buyer_org_size, evaluation_timeline, stakeholder_count]

2. Find k=15 nearest historical deals by cosine similarity on F
   (minimum k=5 required; if <5 matches, HPM returns 50 — neutral prior)

3. Calculate base rate:
   P_base = wins_in_k / k

4. Apply Bayesian update with current BBS as likelihood:
   P_posterior = (P_base × L(BBS)) / P(BBS)
   where L(BBS) = P(BBS | win) from historical BBS distributions

5. HPM = P_posterior × 100
```

---

## 5. Competitive Threat Index (CTI)

The CTI is a per-deal score that quantifies the competitive threat level. It feeds into the DSA as the basis for the Competitive Intensity Score and also serves as a standalone metric for deal triage.

### 5.1 CTI Calculation

```
CTI = max(CTI_per_competitor) × (1 + multi_competitor_penalty)

For each competitor c in the deal:

  CTI_c = (base_threat_c × 0.40)
        + (deal_specific_threat_c × 0.35)
        + (recent_momentum_c × 0.25)

Where:

  base_threat_c:
    Historical win rate of competitor c against Oracle Health
    in this segment and deal size bucket.
    Source: SOP-09 win/loss database.
    Scale: 0 (competitor never wins) to 1 (competitor always wins).

  deal_specific_threat_c:
    ┌────────────────────────────────┬──────────┐
    │ Factor                         │ Score    │
    ├────────────────────────────────┼──────────┤
    │ Competitor is incumbent        │ +0.25    │
    │ Competitor pricing advantage   │ +0.15    │
    │ Competitor has reference at    │          │
    │   buyer's peer institution     │ +0.15    │
    │ Competitor demo scheduled      │ +0.10    │
    │ Competitor C-suite engaged     │ +0.10    │
    │ Competitor offering migration  │          │
    │   incentives / credits         │ +0.10    │
    │ Competitor has buyer's         │          │
    │   consultant aligned           │ +0.15    │
    └────────────────────────────────┴──────────┘
    Capped at 1.0.

  recent_momentum_c:
    Signal-derived momentum from SOP-33 signal engine.
    Product launches, acquisitions, KLAS score changes in last 90 days.
    Scale: 0 (dormant) to 1 (aggressive market push).

  multi_competitor_penalty:
    0.00 for 1 competitor
    0.10 for 2 competitors
    0.20 for 3 competitors
    0.30 for 4+ competitors
    (More competitors = longer evaluation = more uncertainty = higher risk)
```

### 5.2 CTI Thresholds & Actions

| CTI Range | Threat Level | Recommended Action |
|-----------|-------------|-------------------|
| 0.00 - 0.30 | Low | Standard deal support. Monitor per normal cadence. |
| 0.31 - 0.55 | Moderate | Proactive battlecard refresh. AE briefing recommended. |
| 0.56 - 0.75 | High | Activate SOP-29 Standard Package. Pricing intelligence pull. |
| 0.76 - 1.00 | Critical | Activate SOP-29 War Room. Sales VP engagement. Executive sponsor consideration. |

---

## 6. Monte Carlo Win Probability Simulation

### 6.1 Why Monte Carlo, Not Point Estimates

A point estimate of "65% win probability" is false precision. It implies a confidence that doesn't exist. Monte Carlo simulation produces probability **distributions** that honestly represent uncertainty. A deal with P10=30%, P50=55%, P90=75% tells a very different story than one with P10=50%, P50=55%, P90=60% — even though both have the same median. The first deal is volatile and uncertain; the second is stable and predictable.

### 6.2 Simulation Design

```
MONTE CARLO WIN PROBABILITY SIMULATION

Inputs:
  DSA composite score (from Section 4)
  Component-level scores: BBS, CIS, DSF, HPM
  Uncertainty ranges for each component (derived from data quality)

Procedure:

  FOR i = 1 TO 10,000:

    1. Sample each DSA component from its uncertainty distribution:
       BBS_i ~ Normal(BBS_observed, σ_BBS)
       CIS_i ~ Normal(CIS_observed, σ_CIS)
       DSF_i ~ Normal(DSF_observed, σ_DSF)
       HPM_i ~ Normal(HPM_observed, σ_HPM)

       Where σ values reflect data quality:
         σ_BBS = 8  (behavioral signals have moderate noise)
         σ_CIS = 10 (competitive intelligence has higher uncertainty)
         σ_DSF = 5  (structural fit is more stable)
         σ_HPM = 12 (historical patterns have highest variance)

    2. Compute simulated DSA:
       DSA_i = (BBS_i × 0.35) + (CIS_i × 0.30)
             + (DSF_i × 0.20) + (HPM_i × 0.15)
       Clamp DSA_i to [0, 100]

    3. Map DSA_i to win probability using logistic function:
       P_win_i = 1 / (1 + e^(-k × (DSA_i - midpoint)))

       Where:
         k = 0.08 (slope — calibrated from historical data)
         midpoint = 50 (DSA of 50 maps to ~50% win probability)

       This logistic mapping ensures:
         DSA = 20 → ~8% win probability
         DSA = 35 → ~23% win probability
         DSA = 50 → ~50% win probability
         DSA = 65 → ~77% win probability
         DSA = 80 → ~92% win probability

    4. Introduce external shock variable:
       shock_i ~ Uniform(-0.10, +0.10)
       P_win_i = P_win_i + shock_i
       Clamp P_win_i to [0.01, 0.99]

       (External shocks model events the model can't predict:
        C-suite departures, M&A announcements, budget freezes,
        regulatory changes. These are irreducible uncertainty.)

  END FOR

  OUTPUT:
    P10 = 10th percentile of {P_win_1 ... P_win_10000}
    P50 = 50th percentile (median)
    P90 = 90th percentile
    σ   = standard deviation (deal volatility indicator)
    Skew = distribution skewness (negative skew = downside risk)
```

### 6.3 Interpreting Simulation Output

| Metric | Meaning | Decision Guidance |
|--------|---------|-------------------|
| **P50** | Median expected outcome | Primary probability estimate for dashboards |
| **P10** | Downside scenario (10th percentile) | "If things go wrong, this is our floor" |
| **P90** | Upside scenario (90th percentile) | "If everything breaks our way, this is our ceiling" |
| **P90 - P10 spread** | Deal volatility | Wide spread = high uncertainty = needs more intelligence gathering |
| **Negative skew** | Distribution tilted toward downside | More ways to lose than win — defensive strategy recommended |
| **Positive skew** | Distribution tilted toward upside | Strong position with limited downside — press advantage |

### 6.4 Calibration Protocol

The model is only useful if its predictions match reality. Calibration runs quarterly:

```
CALIBRATION PROCEDURE (Quarterly)

1. Collect all deals scored in the previous quarter that have resolved (won or lost).
2. For each deal, compare the P50 prediction at three points:
   - T-90 days (early prediction)
   - T-30 days (mid-cycle prediction)
   - T-7 days (late prediction)

3. Bin deals into probability buckets:
   [0-10%], [10-20%], ..., [90-100%]

4. Calculate actual win rate per bucket.

5. Plot calibration curve:
   Perfect calibration = 45-degree line.
   Above the line = model is under-confident (good — safe).
   Below the line = model is over-confident (bad — dangerous).

6. If any bucket deviates >10 percentage points from calibration line:
   Investigate and adjust DSA weights or logistic mapping parameters.

7. Track Brier Score (mean squared error of probabilistic predictions):
   Brier = (1/N) × Σ(P_predicted_i - outcome_i)²
   Target: Brier < 0.20 (substantially better than CRM stage-gate).
   CRM stage-gate benchmark: Brier ≈ 0.28-0.35.
```

---

## 7. Early Warning System

The Early Warning System monitors scored deals for signals that indicate deteriorating win probability. It triggers alerts before the deal is lost — not after.

### 7.1 Alert Triggers

```
EARLY WARNING TRIGGER MATRIX

┌─────────────────────────────────────────────┬──────────┬─────────────────────┐
│ Trigger Condition                           │ Severity │ Action              │
├─────────────────────────────────────────────┼──────────┼─────────────────────┤
│ P50 drops below 40% (any scored deal)       │ RED      │ AE + Sales VP       │
│                                             │          │ notified. SOP-29    │
│                                             │          │ War Room activation │
│                                             │          │ recommended.        │
├─────────────────────────────────────────────┼──────────┼─────────────────────┤
│ P50 drops >15 points in 7 calendar days     │ RED      │ Trajectory alert.   │
│                                             │          │ Immediate deal      │
│                                             │          │ review with AE.     │
├─────────────────────────────────────────────┼──────────┼─────────────────────┤
│ BBS drops below 30 (champion disengagement) │ ORANGE   │ Champion risk       │
│                                             │          │ protocol. AE        │
│                                             │          │ coaching call.      │
├─────────────────────────────────────────────┼──────────┼─────────────────────┤
│ CTI exceeds 0.80 (critical threat)          │ ORANGE   │ SOP-29 activation.  │
│                                             │          │ Competitive         │
│                                             │          │ response plan.      │
├─────────────────────────────────────────────┼──────────┼─────────────────────┤
│ No buyer-side activity in 21+ days          │ YELLOW   │ "Going dark" alert. │
│ (on deals in stages 3-5)                    │          │ AE re-engagement    │
│                                             │          │ recommended.        │
├─────────────────────────────────────────────┼──────────┼─────────────────────┤
│ Evaluation timeline extended >30 days       │ YELLOW   │ Status quo bias     │
│ beyond original plan                        │          │ indicator. Review   │
│                                             │          │ champion strength.  │
├─────────────────────────────────────────────┼──────────┼─────────────────────┤
│ New competitor enters deal (SOP-33 signal)  │ YELLOW   │ CTI recalculation.  │
│                                             │          │ Battlecard pull.    │
├─────────────────────────────────────────────┼──────────┼─────────────────────┤
│ P90-P10 spread widens >40 points            │ INFO     │ High uncertainty.   │
│                                             │          │ Intelligence        │
│                                             │          │ gathering needed.   │
└─────────────────────────────────────────────┴──────────┴─────────────────────┘
```

### 7.2 Alert Delivery

| Severity | Channel | SLA | Escalation |
|----------|---------|-----|------------|
| **RED** | Slack DM to AE + Sales VP + Mike. Email backup. | Within 4 hours of trigger. | If no response in 24 hours: escalate to Matt Cohlmia. |
| **ORANGE** | Slack #competitive-intel channel + AE DM. | Within 8 hours. | If no response in 48 hours: Sales VP notified. |
| **YELLOW** | Weekly Risk Report (Monday delivery). | Batch delivery. | Included in weekly pipeline review deck. |
| **INFO** | Deal Score Dashboard (self-service). | Real-time update. | No escalation. |

---

## 8. Model Training & Feedback Loop

### 8.1 Training Data Sources

| Source | Data Provided | Refresh |
|--------|--------------|---------|
| SOP-09 Win/Loss Database | Outcome labels, behavioral drivers, competitor presence, deal characteristics | Per interview (8-12/quarter) |
| Salesforce Deal History | Stage progression, activity logs, close dates, deal values, competitor fields | Nightly sync |
| SOP-10 Pricing Intelligence | Competitive pricing observations, discount bands | Quarterly refresh |
| SOP-33 Signal Engine | Competitive movement signals, threat assessments | Continuous |
| Rep Feedback | Model accuracy ratings on scored deals (thumbs up/down + comments) | Per deal |

### 8.2 Model Improvement Cycle

```
QUARTERLY MODEL IMPROVEMENT CYCLE

1. COLLECT: Gather all resolved deals with predictions (Q-1)
2. CALIBRATE: Run calibration procedure (Section 6.4)
3. ANALYZE: Identify systematic prediction errors:
   - Competitor-specific bias (do we consistently under/overestimate specific competitors?)
   - Segment bias (are we better at predicting hospital deals than ambulatory?)
   - Timing bias (are early predictions systematically wrong in one direction?)
4. ADJUST: Modify DSA weights, CTI factors, or logistic mapping parameters
5. BACKTEST: Run adjusted model against Q-2 data to validate improvement
6. DEPLOY: Update scoring parameters for next quarter
7. REPORT: Publish Model Performance Report to Sales Ops and CI team
```

### 8.3 Cold Start Protocol

At launch (before sufficient historical data exists to train the model):

1. **Phase 1 (Months 1-3):** Use expert-calibrated weights based on SOP-09 qualitative findings. HPM component set to neutral (50) for all deals. Run simulation but flag all outputs as "calibrating — directional only."
2. **Phase 2 (Months 4-6):** With 25+ resolved scored deals, run first calibration. Adjust weights. Remove "calibrating" flag if Brier score < 0.25.
3. **Phase 3 (Months 7+):** Full production mode. Quarterly calibration cycle active.

---

## 9. Integration Map

```
SOP-32 INTEGRATION DEPENDENCIES

┌─────────────┐     feeds model training     ┌─────────────┐
│   SOP-09    │ ──────────────────────────▶  │   SOP-32    │
│  Win/Loss   │     outcome data, drivers    │ Deal Scoring │
└─────────────┘                              └──────┬──────┘
                                                    │
┌─────────────┐     pricing inputs              │
│   SOP-10    │ ──────────────────────────▶     │
│  Pricing    │     discount bands, position    │
└─────────────┘                                 │
                                                │
┌─────────────┐     competitive signals         │
│   SOP-33    │ ──────────────────────────▶     │
│  Signals    │     threat data, momentum       │
└─────────────┘                                 │
                                                │
┌─────────────┐     triggers War Room        ◀──┘
│   SOP-29    │ ◀──────────────────────────
│ Deal Support│     when P50 < 40% or CTI > 0.8
└─────────────┘

┌─────────────┐     scenario inputs          ◀──┘
│   SOP-34    │ ◀──────────────────────────
│  War Gaming │     deal scores feed scenario modeling
└─────────────┘
```

---

## 10. RACI Matrix

| Activity | Mike Rodgers | Sales Ops | AE / Sales VP | Data Engineering | Matt Cohlmia |
|----------|:---:|:---:|:---:|:---:|:---:|
| Model design & weight calibration | **R/A** | C | I | C | I |
| Data pipeline (Salesforce sync) | C | **R** | I | **A** | I |
| Deal scoring execution | **R** | C | I | **A** | I |
| Early Warning alert delivery | **R/A** | I | **I** | C | I |
| Alert response & deal strategy | C | I | **R/A** | — | I |
| Quarterly calibration | **R/A** | C | I | C | **I** |
| Model Performance Report | **R** | C | I | C | **A** |
| Executive briefing on model results | **R** | I | I | — | **A** |

---

## 11. KPIs

### Leading Indicators (measured monthly)

| KPI | Target | Measurement |
|-----|--------|-------------|
| Deals scored as % of competitive pipeline | >80% of deals >$2M TCV | Scored deals / total competitive deals |
| Alert response rate (RED/ORANGE) | >90% response within SLA | Alerts responded to / alerts issued |
| Rep feedback participation | >60% of scored deals get thumbs up/down | Deals with rep feedback / scored deals |

### Lagging Indicators (measured quarterly)

| KPI | Target | Measurement |
|-----|--------|-------------|
| Model calibration (Brier Score) | <0.20 | Quarterly calibration procedure |
| Win rate on RED-alerted deals that implemented strategy changes | >25% (vs. baseline loss rate) | Deals saved / RED alerts issued |
| Forecast accuracy improvement | >10% improvement vs. CRM-only forecast | MAE comparison: model vs. CRM stage |
| Time-to-detection of at-risk deals | 30+ days before loss | Average days between first alert and deal close |

### North Star Metric

**Net Win Rate Lift on Scored Deals**: The difference in win rate between deals that were scored + acted upon vs. a matched cohort of similar deals without scoring. Target: +8 percentage points within 12 months of deployment.

---

## 12. Maturity Roadmap

| Phase | Timeline | Capability | Dependencies |
|-------|----------|-----------|-------------|
| **Phase 1: Manual Scoring** | Q2 2026 | Excel-based DSA scoring for top 20 competitive deals. Manual Monte Carlo via Python script. Weekly risk report. | SOP-09 data (min 25 resolved deals). Salesforce access. |
| **Phase 2: Semi-Automated** | Q3-Q4 2026 | Automated Salesforce data pull. Dashboard in Tableau/Power BI. Automated alert delivery via Slack. Monthly calibration. | Data engineering support. BI tool access. |
| **Phase 3: Full Production** | H1 2027 | Real-time scoring. Automated signal ingestion from SOP-33. API integration with Deal Desk. AI-assisted pattern matching for HPM. | SOP-33 operational. Data science team allocation. |
| **Phase 4: Prescriptive** | H2 2027+ | Model recommends specific actions (not just risk assessment). "To increase P50 by 10 points, the highest-impact action is [X]." Strategy simulation via SOP-34 integration. | Full model maturity. SOP-34 operational. |

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| **DSA** | Deal Scoring Algorithm — composite 0-100 score of deal health |
| **BBS** | Buyer Behavior Score — weighted index of buyer engagement signals |
| **CIS** | Competitive Intensity Score — inverse of competitive threat (100 = no threat) |
| **DSF** | Deal Structure Fit — how well deal characteristics match Oracle Health's win profile |
| **HPM** | Historical Pattern Match — Bayesian prior from similar historical deals |
| **CTI** | Competitive Threat Index — per-deal competitive danger score (0-1) |
| **P10/P50/P90** | Monte Carlo percentile outputs representing downside/median/upside scenarios |
| **Brier Score** | Mean squared error of probabilistic predictions (lower = better; 0 = perfect) |

---

*SOP-32 is designed by Mike Rodgers. It does not replace CRM probability or Sales Ops forecasting — it provides a CI-informed intelligence layer that makes those systems more accurate. The model is only as good as its inputs: SOP-09 win/loss data quality and SOP-33 signal coverage are the binding constraints on model performance.*
