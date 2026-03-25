# SOP-34: Competitive Landscape Simulation & War Gaming

**Owner**: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence
**Version**: 1.0 DRAFT — Awaiting Mike's approval
**Last Updated**: 2026-03-25
**Category**: Strategic Intelligence & Advanced Analytics
**Priority**: P1 — Highest-order CI capability: modeling future states, not just understanding current ones
**Maturity**: Gap → Designed (this SOP)

---

## Table of Contents

1. [Purpose](#1-purpose)
2. [Scope](#2-scope)
3. [Architecture: Competitive Simulation & War Gaming System](#3-architecture-competitive-simulation--war-gaming-system)
4. [War Game Framework](#4-war-game-framework)
5. [Monte Carlo Scenario Modeling](#5-monte-carlo-scenario-modeling)
6. [Red Team / Blue Team Protocol](#6-red-team--blue-team-protocol)
7. [Decision Tree Analysis](#7-decision-tree-analysis)
8. [Competitive Equilibrium Modeling](#8-competitive-equilibrium-modeling)
9. [Strategic Positioning Optimizer](#9-strategic-positioning-optimizer)
10. [Application Examples](#10-application-examples)
11. [Integration Map](#11-integration-map)
12. [RACI Matrix](#12-raci-matrix)
13. [KPIs](#13-kpis)
14. [Maturity Roadmap](#14-maturity-roadmap)

---

## 1. Purpose

Most competitive intelligence answers the question: "What is happening?" The best competitive intelligence answers: "What is likely to happen?" This SOP answers the question that creates the most strategic value: **"What should we do about it — and what will they do in response?"**

Competitive landscape simulation and war gaming is the practice of modeling competitive scenarios before they occur, pressure-testing Oracle Health's strategies against simulated competitor responses, and identifying the positioning that maximizes win probability across the broadest set of market conditions. It is the difference between reacting to the market and shaping it.

**Why this matters (quantified):**

- Organizations that conduct structured competitive war games are **2.3x more likely to achieve above-market growth** than those relying solely on traditional competitive analysis (McKinsey, "War Gaming for Corporate Strategy," adapted from 200+ strategic planning engagements).
- Oracle Health competes in a market with 3-5 year technology cycle decisions. A strategic positioning error in 2026 compounds through 2029. War gaming the decision space before committing reduces the probability of irreversible positioning mistakes.
- The healthcare IT market is entering an inflection point: AI/ML integration, cloud migration, value-based care infrastructure, and interoperability mandates are simultaneously reshaping buyer priorities. The competitors that model these shifts and pre-position win; the ones that react lose 12-18 months of market positioning.
- Internal data: Oracle Health's Q4 2025 strategic planning cycle identified 3 "high-confidence" assumptions about Epic's AI strategy that subsequent signal analysis (SOP-33 pattern) showed were incorrect. War gaming would have stress-tested those assumptions before they were baked into the plan.

**What this SOP produces:**

| Output | Audience | Cadence |
|--------|----------|---------|
| Competitive Scenario Report | Strategy, Product, Sales Leadership | Per war game (quarterly or event-triggered) |
| Monte Carlo Scenario Analysis | Strategy, Product | Per scenario request |
| Strategic Positioning Recommendation | Executive Team | Quarterly + event-triggered |
| Red Team / Blue Team Debrief | War game participants | Post-exercise (within 5 business days) |
| Decision Tree for Strategic Options | Executive Team | Per strategic decision |

---

## 2. Scope

### In Scope

- Strategic competitive scenarios affecting Oracle Health's market position over 12-36 month horizons
- Tactical competitive scenarios affecting active competitive dynamics in the current and next quarter
- Scenario categories: market entry/exit, pricing strategy changes, product architecture shifts, M&A impacts, regulatory changes, technology platform transitions
- Competitors: All Tier 1-2 competitors per SOP-33 monitoring framework (Epic, Meditech, Waystar, R1 RCM, FinThrive, Nuance/Microsoft DAX, athenahealth)
- War game exercises involving Oracle Health stakeholders playing competitor roles
- Quantitative scenario modeling using Monte Carlo simulation and decision tree analysis

### Out of Scope

- Oracle Health's internal product roadmap decisions (Product Management — though war game outputs inform roadmap)
- Financial modeling of Oracle Health's P&L under scenarios (Finance — though we provide competitive revenue impact estimates)
- Customer-facing competitive positioning messaging (Product Marketing — though war game outputs inform messaging strategy)
- Basic competitive war gaming covered by SOP-17 (this SOP extends SOP-17 with quantitative modeling, simulation frameworks, and structured analytical methods)

---

## 3. Architecture: Competitive Simulation & War Gaming System

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│           COMPETITIVE SIMULATION & WAR GAMING ARCHITECTURE                        │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │  INPUT LAYER: Intelligence Foundation                                    │    │
│  │                                                                          │    │
│  │  SOP-09         SOP-10         SOP-32         SOP-33                    │    │
│  │  Win/Loss       Pricing        Deal Scores    Signal                    │    │
│  │  Patterns       Intelligence   & CTI Data     Detection                 │    │
│  │  ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐                 │    │
│  │  │Buyer   │    │Price   │    │Active  │    │Predict-│                 │    │
│  │  │Decision│    │Points, │    │Pipeline│    │ions,   │                 │    │
│  │  │Drivers │    │Discount│    │Risk    │    │Signals │                 │    │
│  │  │& Biases│    │Bands   │    │Profile │    │& Moves │                 │    │
│  │  └───┬────┘    └───┬────┘    └───┬────┘    └───┬────┘                 │    │
│  └──────┴─────────────┴────────────┴──────────────┴──────────────────────┘    │
│                               │                                                │
│  ┌────────────────────────────▼─────────────────────────────────────────────┐  │
│  │  SIMULATION LAYER: Quantitative Modeling                                  │  │
│  │                                                                           │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐         │  │
│  │  │ Monte Carlo     │  │ Decision Tree   │  │ Competitive      │         │  │
│  │  │ Scenario        │  │ Analysis        │  │ Equilibrium      │         │  │
│  │  │ Modeling         │  │ (multi-move     │  │ Modeling         │         │  │
│  │  │ (10,000+        │  │  game theory)   │  │ (Nash equilibria │         │  │
│  │  │  simulations)   │  │                 │  │  + stability)    │         │  │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬─────────┘         │  │
│  └───────────┴────────────────────┴─────────────────────┴───────────────────┘  │
│                               │                                                │
│  ┌────────────────────────────▼─────────────────────────────────────────────┐  │
│  │  WAR GAME LAYER: Human-in-the-Loop Strategic Exercise                     │  │
│  │                                                                           │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐         │  │
│  │  │ Red Team        │  │ Blue Team       │  │ Control Team     │         │  │
│  │  │ (plays          │  │ (plays Oracle   │  │ (facilitates,    │         │  │
│  │  │  competitors)   │  │  Health)        │  │  scores, rules)  │         │  │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬─────────┘         │  │
│  └───────────┴────────────────────┴─────────────────────┴───────────────────┘  │
│                               │                                                │
│  ┌────────────────────────────▼─────────────────────────────────────────────┐  │
│  │  OPTIMIZATION LAYER: Strategic Positioning Optimizer                       │  │
│  │                                                                           │  │
│  │  Inputs: Scenario outcomes + war game insights + equilibrium analysis    │  │
│  │  Process: Maximize expected win probability across scenario distribution │  │
│  │  Output: Recommended positioning strategy with confidence bounds         │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. War Game Framework

### 4.1 War Game Types

| Type | Duration | Participants | Trigger | Depth |
|------|----------|-------------|---------|-------|
| **Strategic War Game** | Full day (6-8 hours) | 12-20 participants across Strategy, Product, Sales, Marketing, Engineering | Annual planning cycle, major market event, M&A | Full Red/Blue/Control team with multiple rounds |
| **Tactical War Game** | Half day (3-4 hours) | 6-10 participants from Sales, Product, CI | Competitor product launch, pricing change, major deal strategy | Focused scenario with 2 rounds |
| **Rapid War Game** | 90 minutes | 4-6 participants (CI team + key stakeholders) | Urgent competitive situation, deal-specific strategy | Single scenario, single round, rapid output |
| **Tabletop Simulation** | 2 hours | Mike + 2-3 CI/Strategy team members | Routine quarterly scenario testing, prediction validation | Monte Carlo-driven, minimal roleplay |

### 4.2 War Game Lifecycle

```
WAR GAME LIFECYCLE — 6 PHASES

PHASE 1: SCENARIO DESIGN (2-3 weeks before game)
  Owner: Mike Rodgers
  Activities:
  ├── Define the strategic question the war game answers
  ├── Select scenario variables (competitor moves, market conditions)
  ├── Build competitor briefing packages (from SOP-08, SOP-09, SOP-10, SOP-33)
  ├── Run preliminary Monte Carlo simulation to identify key variables
  ├── Design exercise structure (rounds, moves, scoring)
  └── Prepare participant pre-read materials

PHASE 2: INTELLIGENCE BRIEFING (1 week before game)
  Owner: Mike Rodgers
  Activities:
  ├── Brief all participants on current competitive landscape
  ├── Red Team receives competitor-specific intelligence packages:
  │   ├── Competitor's publicly stated strategy and priorities
  │   ├── Competitor's financial position and resource constraints
  │   ├── Competitor's recent moves and predicted next moves (SOP-33)
  │   ├── Competitor's win/loss patterns (SOP-09 data)
  │   └── Competitor's pricing and packaging (SOP-10 data)
  ├── Blue Team receives Oracle Health's position:
  │   ├── Current product capabilities and roadmap
  │   ├── Active pipeline and deal scoring data (SOP-32)
  │   ├── Win/loss patterns from Oracle Health's perspective
  │   └── Current positioning and messaging
  └── All participants read pre-brief materials

PHASE 3: WAR GAME EXECUTION (game day)
  Owner: Mike (facilitation) + Control Team
  Structure:
  ├── Opening: Strategic question framing (15 min)
  ├── Round 1 — Competitor Moves:
  │   ├── Red Team presents competitor strategies (30 min per competitor)
  │   ├── Blue Team observes and takes notes
  │   └── Control Team scores move plausibility (1-5)
  ├── Round 2 — Oracle Health Response:
  │   ├── Blue Team develops response strategies (45 min)
  │   ├── Blue Team presents to Red Team and Control
  │   └── Control Team scores response effectiveness (1-5)
  ├── Round 3 — Counter-Moves:
  │   ├── Red Team responds to Oracle Health's strategy (30 min)
  │   ├── Blue Team adjusts (20 min)
  │   └── Control Team facilitates discussion
  ├── Round 4 — Synthesis:
  │   ├── Control Team presents scoring summary
  │   ├── All teams discuss surprises and insights
  │   └── Identify key uncertainties and decision points
  └── Closing: Strategic implications and action items (30 min)

PHASE 4: ANALYSIS (1-3 days after game)
  Owner: Mike Rodgers
  Activities:
  ├── Code and analyze all war game moves and counter-moves
  ├── Run Monte Carlo simulation on war game scenarios
  ├── Build decision trees for key strategic options
  ├── Identify consensus strategies vs. high-uncertainty strategies
  └── Draft Competitive Scenario Report

PHASE 5: DEBRIEF & RECOMMENDATIONS (within 5 business days)
  Owner: Mike Rodgers
  Activities:
  ├── Present Competitive Scenario Report to executive sponsor
  ├── Deliver Red Team / Blue Team debrief to participants
  ├── Document strategic recommendations with confidence levels
  ├── Identify "no regret" moves (win in most scenarios) vs.
  │   "big bet" moves (win in some scenarios, lose in others)
  └── Update SOP-33 monitoring priorities based on key uncertainties

PHASE 6: FOLLOW-UP (ongoing)
  Owner: Mike Rodgers
  Activities:
  ├── Track which war game scenarios actually materialize
  ├── Score prediction accuracy of Red Team moves
  ├── Update competitive model parameters based on observed outcomes
  └── Feed results back into SOP-32 (deal scoring) and SOP-33 (signal detection)
```

### 4.3 Move Plausibility Scoring

Red Team moves must be grounded in actual competitive intelligence, not fantasy. The Control Team scores plausibility:

```
MOVE PLAUSIBILITY SCORE (Control Team Assessment)

5 — HIGHLY PLAUSIBLE
    Based on confirmed intelligence (SOP-33 Tier A/B sources).
    Competitor has resources, motivation, and track record to execute.
    Example: Epic extending into ambulatory AI — confirmed by patent filings,
    hiring patterns, and conference demonstrations.

4 — PLAUSIBLE
    Consistent with competitor's stated strategy and capabilities.
    No contradicting signals. Reasonable resource allocation.
    Example: Waystar bundling RCM + CDI in a competitive package.

3 — POSSIBLE
    Within competitor's theoretical capability but requires assumptions.
    Some supporting signals but also some contradicting signals.
    Example: Meditech launching a cloud-native platform by Q4 2026.

2 — UNLIKELY BUT WORTH CONSIDERING
    Requires significant capability stretch or strategic pivot.
    Useful for stress-testing but not for planning.
    Example: Epic offering outcomes-based pricing.

1 — IMPLAUSIBLE
    Contradicts known constraints (financial, technical, regulatory).
    Include only if it exposes a critical vulnerability.
    Example: Google acquiring Epic (antitrust constraints).

RULE: Moves scoring <3 are noted but not used in Monte Carlo simulation.
Moves scoring ≥3 are fed into the quantitative modeling pipeline.
```

---

## 5. Monte Carlo Scenario Modeling

### 5.1 Purpose

War games are qualitative. Monte Carlo simulation makes them quantitative. After the war game identifies the key scenarios and variables, the simulation models 10,000+ outcomes to quantify the probability distribution of each strategic option.

### 5.2 Simulation Architecture

```
MONTE CARLO COMPETITIVE SCENARIO SIMULATION

SETUP:

  Define scenario variables (from war game output):
    V = {v_1, v_2, ..., v_n}

  For each variable, define distribution:
    v_i ~ Distribution_i(parameters)

  Example scenario variables for "Epic AI Strategy Response":
    v_1: Epic AI product maturity at launch
         ~ Beta(α=3, β=2) scaled to [0.4, 0.9]
         (skewed right — Epic has resources to execute)

    v_2: Oracle Health AI product maturity at same time
         ~ Beta(α=2, β=3) scaled to [0.3, 0.8]
         (skewed left — honest about current position)

    v_3: Buyer AI requirement intensity
         ~ Normal(μ=0.6, σ=0.15) clamped to [0.1, 1.0]
         (growing but uncertain)

    v_4: Price sensitivity in AI-influenced deals
         ~ Uniform(0.3, 0.7)
         (unknown — no historical data)

    v_5: Regulatory impact on AI in clinical settings
         ~ Bernoulli(p=0.35) × Uniform(0.5, 0.9)
         (35% chance of significant regulation; if so, moderate-to-high impact)

SIMULATION:

  FOR i = 1 TO 10,000:

    1. Sample all variables:
       v_1_i, v_2_i, ..., v_n_i ~ respective distributions

    2. For each Oracle Health strategic option S_j:
       Calculate outcome_ij = f(S_j, v_1_i, v_2_i, ..., v_n_i)

       Where f() is the scenario outcome function:
       outcome = market_share_impact × deal_win_rate_impact × revenue_impact

       Scenario outcome function (example for "Epic AI Response"):

       IF oracle_ai_maturity > epic_ai_maturity × 0.9:
         ai_advantage = oracle_ai_maturity - epic_ai_maturity
         win_rate_lift = ai_advantage × buyer_ai_requirement × 0.30
       ELSE:
         ai_gap = epic_ai_maturity - oracle_ai_maturity
         win_rate_penalty = ai_gap × buyer_ai_requirement × 0.25
         win_rate_lift = -win_rate_penalty

       IF regulation_impact > 0:
         # Regulation slows both, but larger vendor (Epic) absorbs better
         win_rate_lift -= regulation_impact × 0.10

       price_factor = 1.0 - (price_sensitivity × price_gap)
       outcome_ij = baseline_win_rate + win_rate_lift × price_factor

    3. Record outcome for each strategy option across all simulations

  END FOR

OUTPUT:

  For each strategy option S_j:
    ┌─────────────────────────────────────────────────┐
    │ Strategy: [S_j description]                      │
    │ P10 outcome: [10th percentile]                   │
    │ P50 outcome: [median]                            │
    │ P90 outcome: [90th percentile]                   │
    │ Expected value: mean(outcomes)                   │
    │ Downside risk: P(outcome < baseline)             │
    │ Upside potential: P(outcome > baseline + 10%)    │
    │ Volatility: std(outcomes)                        │
    │ Robustness: P(outcome > 0 across all scenarios)  │
    └─────────────────────────────────────────────────┘

  Strategy comparison:
    Rank strategies by: Expected Value × Robustness
    This rewards strategies that perform well on average AND
    are resilient across different market conditions.
```

### 5.3 Sensitivity Analysis

```
SENSITIVITY ANALYSIS (Post-Simulation)

For each scenario variable v_i:

  1. Hold all other variables at their median values
  2. Sweep v_i from its 5th to 95th percentile
  3. Record the change in outcome for each strategy

  Output: Tornado diagram showing which variables have the
  highest impact on strategy outcome.

  Purpose: Identify which uncertainties matter most.
  If v_3 (buyer AI requirement intensity) dominates the
  tornado diagram, then reducing uncertainty about buyer
  AI demand becomes the #1 intelligence priority.

  Feed back to SOP-33: Prioritize signal collection on
  the variables that Monte Carlo sensitivity analysis
  identifies as highest-impact.
```

---

## 6. Red Team / Blue Team Protocol

### 6.1 Team Composition

```
RED TEAM (Plays Competitors)
  Composition: 4-8 people per competitor team
  Required roles:
  ├── Team Lead: Someone who deeply understands the competitor
  │   (Ideal: former employee, consultant, or CI analyst with deep coverage)
  ├── Product Rep: Understands competitor's product capabilities
  ├── Sales Rep: Understands competitor's GTM motion and pricing
  └── Strategy Rep: Understands competitor's corporate strategy

  Selection criteria:
  - Willingness to genuinely advocate for the competitor position
  - No "sandbag" players who will make the competitor look weak
  - Briefed with actual CI data, not assumptions
  - Empowered to make bold, plausible moves

BLUE TEAM (Plays Oracle Health)
  Composition: 4-8 people
  Required roles:
  ├── Team Lead: Sales or Strategy leader
  ├── Product Rep: Product Management representative
  ├── Sales Rep: Senior AE or Sales VP
  └── Marketing Rep: Product Marketing or CI representative

  Selection criteria:
  - Authority to represent Oracle Health's actual strategic options
  - Mix of optimists and skeptics (avoid groupthink)
  - At least one person willing to challenge conventional wisdom

CONTROL TEAM (Facilitates & Scores)
  Composition: 2-3 people
  Required roles:
  ├── Facilitator: Mike Rodgers (designs game, manages timing, enforces rules)
  ├── Scorer: CI analyst (scores plausibility, tracks moves, documents outcomes)
  └── Market Referee: External or neutral stakeholder who validates market
  │   assumptions when teams disagree
```

### 6.2 Rules of Engagement

| Rule | Rationale |
|------|-----------|
| **No hero scenarios.** Red Team cannot propose moves that require competitor to be incompetent. Blue Team cannot propose responses that require perfect execution. | Real strategy must work against competent opponents and imperfect execution. |
| **Resource constraints are real.** Teams must account for budget, headcount, technology, and time limitations. | "We'll just build a better AI" is not a strategy without specifying how. |
| **Moves must be time-bound.** Every move includes an execution timeline and dependencies. | Strategy without time = aspiration, not plan. |
| **Information asymmetry is enforced.** Red Team does not know Blue Team's full strategy, and vice versa. Control Team manages information flow. | Real competition operates under uncertainty. |
| **Kill your darlings.** Blue Team must consider abandoning current strategies if they don't survive Red Team pressure testing. | The purpose of war gaming is to find weak strategies before the market does. |
| **Data beats opinion.** When teams disagree on market assumptions, Control Team consults SOP-09/10/33 data. If data doesn't exist, the disagreement is logged as a key uncertainty for Monte Carlo modeling. | Prevents the loudest voice from driving conclusions. |

### 6.3 Cognitive Bias Mitigation

War games are susceptible to the same biases that affect all strategic planning. The following countermeasures are built into the protocol:

```
BIAS MITIGATION MATRIX

┌──────────────────────────┬──────────────────────────────────────────────┐
│ Bias                     │ Countermeasure                               │
├──────────────────────────┼──────────────────────────────────────────────┤
│ Confirmation Bias        │ Red Team is explicitly incentivized to find  │
│ (seeking info that       │ scenarios where Oracle Health loses. Scoring │
│  confirms existing       │ rewards creative, plausible competitor moves │
│  beliefs)                │ that Blue Team didn't anticipate.            │
├──────────────────────────┼──────────────────────────────────────────────┤
│ Anchoring                │ All teams receive scenario briefings before  │
│ (over-relying on first   │ hearing any strategic proposals. Monte Carlo │
│  piece of information)   │ simulation provides data-driven anchors.    │
├──────────────────────────┼──────────────────────────────────────────────┤
│ Groupthink               │ Anonymous pre-game strategy submissions.     │
│ (conforming to group     │ Mandatory "strongest objection" round where  │
│  consensus)              │ each participant must voice a concern.       │
├──────────────────────────┼──────────────────────────────────────────────┤
│ Optimism Bias            │ "Pre-mortem" exercise: Before Blue Team      │
│ (overestimating          │ finalizes strategy, everyone writes: "It's   │
│  positive outcomes)      │ 2028 and this strategy failed. Why?"         │
├──────────────────────────┼──────────────────────────────────────────────┤
│ Status Quo Bias          │ One Blue Team member is designated           │
│ (preferring current      │ "Disruption Advocate" — must propose at      │
│  approach)               │ least one strategy that breaks from current  │
│                          │ positioning.                                 │
├──────────────────────────┼──────────────────────────────────────────────┤
│ Dunning-Kruger           │ All competitor capability assessments must   │
│ (over/underestimating    │ cite specific evidence from SOP-08/33 data. │
│  competitor capability)  │ "They can't do that" requires proof.         │
└──────────────────────────┴──────────────────────────────────────────────┘
```

---

## 7. Decision Tree Analysis

### 7.1 Purpose

Decision trees map Oracle Health's strategic options as a branching structure, with competitor counter-moves at each node. They make the sequential nature of competitive strategy explicit and quantifiable.

### 7.2 Decision Tree Construction

```
DECISION TREE METHODOLOGY

Step 1: Define Oracle Health's strategic options (from war game output)
  Decision node: [Oracle Health chooses strategy S_1, S_2, or S_3]

Step 2: For each strategy, define competitor response options
  (scored by plausibility from war game)
  Chance node: [Competitor responds with R_1 (p=0.5), R_2 (p=0.3), R_3 (p=0.2)]

Step 3: For each competitor response, define Oracle Health's counter-move options
  Decision node: [Oracle Health counters with C_1 or C_2]

Step 4: For each path, estimate outcome value
  Terminal node: [Win rate impact, market share impact, revenue impact]
  Value derived from Monte Carlo simulation of that scenario path

Step 5: Backward induction to find optimal strategy
  At each decision node, choose the option that maximizes expected value
  considering all possible competitor responses and their probabilities

EXAMPLE DECISION TREE (simplified):

Oracle Health AI Strategy
│
├── S1: Accelerate clinical AI (invest heavily)
│   ├── [p=0.5] Epic matches with DAX integration
│   │   ├── C1: Differentiate on EHR-native integration → EV = +3% win rate
│   │   └── C2: Shift to outcomes-based value prop  → EV = +5% win rate ★
│   ├── [p=0.3] Epic delays / underfunds AI push
│   │   └── C1: Press advantage with AI-first messaging → EV = +8% win rate ★
│   └── [p=0.2] New entrant (Abridge/Ambience) disrupts
│       ├── C1: Acquire/partner with entrant → EV = +4% win rate
│       └── C2: Build proprietary alternative → EV = +2% win rate
│
├── S2: Fast-follow (match competitor AI features, don't lead)
│   ├── [p=0.5] Epic leads with DAX → Oracle position weakens
│   │   └── EV = -3% win rate
│   ├── [p=0.3] Market AI demand lower than expected
│   │   └── EV = +1% win rate (saved investment)
│   └── [p=0.2] New entrant disrupts → Oracle can acquire
│       └── EV = +2% win rate
│
├── S3: AI partnership strategy (partner, don't build)
│   ├── [p=0.5] Partner delivers quality AI layer
│   │   └── EV = +4% win rate (fast to market, lower cost)
│   ├── [p=0.3] Partner underdelivers or pivots
│   │   └── EV = -5% win rate (dependency risk realized)
│   └── [p=0.2] Partner acquired by competitor
│       └── EV = -8% win rate (worst case)

EXPECTED VALUES (backward induction):
  S1 (Accelerate): EV = 0.5(+5%) + 0.3(+8%) + 0.2(+3%) = +5.5% ★ OPTIMAL
  S2 (Fast-follow): EV = 0.5(-3%) + 0.3(+1%) + 0.2(+2%) = -0.8%
  S3 (Partnership): EV = 0.5(+4%) + 0.3(-5%) + 0.2(-8%) = -0.1%

NOTE: Expected value alone is insufficient. S3 has the worst downside
(-8% in the partner-acquired scenario). Risk-adjusted analysis (Section 5)
should complement this analysis.
```

### 7.3 Multi-Period Extension

For strategic decisions playing out over multiple years:

```
MULTI-PERIOD DECISION TREE

Period 1 (2026): Oracle Health strategic choice
Period 2 (2027): Competitor response + market evolution
Period 3 (2028): Oracle Health adaptation + competitor counter-adaptation

Each period adds a layer to the decision tree.
Full 3-period tree for 3 strategies × 3 competitor responses × 2 market states
= 3 × 3 × 2 × 3 × 3 × 2 = 324 terminal nodes.

Monte Carlo simulation evaluates all 324 terminal paths simultaneously.
Human analysis focuses on the 10-15 most probable paths (>2% probability mass).
```

---

## 8. Competitive Equilibrium Modeling

### 8.1 Concept

Competitive equilibrium analysis identifies the market positions where no competitor has an incentive to change strategy — Nash equilibria. It also identifies unstable positions where a competitor WILL move, creating predictable dynamics.

### 8.2 Equilibrium Analysis Framework

```
COMPETITIVE EQUILIBRIUM MODEL

Market Position Space:
  Each competitor has a position P_c defined by:
  - Price point (relative to market average)
  - Product scope (breadth of clinical/financial/operational coverage)
  - Innovation posture (leading edge vs. proven/reliable)
  - Market focus (segments: large hospital, mid-market, ambulatory, post-acute)

Payoff Function:
  For each competitor c, payoff is approximated by:
  payoff_c = market_share_c × margin_c × retention_c

  Where:
  market_share_c = f(P_c, P_-c, buyer_preferences)
    (function of own position, competitor positions, and buyer preferences)
  margin_c = g(price_c, cost_structure_c)
  retention_c = h(product_quality_c, switching_costs_c)

Equilibrium Detection:

  FOR each pair of competitors (c1, c2):
    FOR each position dimension d:

      1. Calculate c1's optimal position given c2's current position:
         P_c1_optimal = argmax payoff_c1(P_c1, P_c2_current)

      2. Calculate c2's optimal position given c1's current position:
         P_c2_optimal = argmax payoff_c2(P_c2, P_c1_current)

      3. If P_c1_optimal ≈ P_c1_current AND P_c2_optimal ≈ P_c2_current:
         → STABLE EQUILIBRIUM (neither wants to move)
         → Low competitive volatility expected in this dimension.

      4. If P_c1_optimal ≠ P_c1_current:
         → UNSTABLE for c1 (c1 has incentive to change position)
         → Predict c1 will move toward P_c1_optimal
         → Timeline: proportional to switching cost and organizational inertia

STABILITY CLASSIFICATION:

  STABLE — Both competitors at optimal position given the other's position.
  PREDICTION: Market structure holds. Focus on execution, not repositioning.

  UNSTABLE — One or both competitors have incentive to shift.
  PREDICTION: Movement is coming. Question is timing, not whether.
  Monitor for leading indicators (SOP-33) of the predicted movement.

  TIPPING POINT — Small perturbation (new entrant, regulation, technology
  shift) would push the system from one equilibrium to another.
  PREDICTION: High sensitivity to exogenous shocks. War game the scenarios.
```

### 8.3 Market State Transition Map

```
ORACLE HEALTH MARKET STATE TRANSITIONS (Simplified)

Current State:                   Possible Future States:
┌─────────────────────┐
│ Epic dominant in     │ ───→ [State A] AI disruption creates new leaders
│ large hospitals,     │ ───→ [State B] Oracle consolidates #2 position
│ Oracle strong in     │ ───→ [State C] Cloud-native entrants fragment mid-market
│ mid-market + RCM,    │ ───→ [State D] Regulatory mandate reshuffles positioning
│ Specialists own      │ ───→ [State E] Platform convergence (EHR + RCM + AI merge)
│ point solutions      │
└─────────────────────┘

Transition Probabilities (from Monte Carlo):
  A: 15% — high impact, moderate probability
  B: 35% — base case, Oracle executes well
  C: 20% — disruption scenario, painful for incumbents
  D: 10% — exogenous, unpredictable timing
  E: 20% — long-term trend, already in motion

STRATEGIC IMPLICATION:
  Oracle Health needs a strategy robust to B, C, and E
  (combined 75% probability). Pure B optimization is tempting
  but leaves Oracle vulnerable to C and E.
```

---

## 9. Strategic Positioning Optimizer

### 9.1 Purpose

The Strategic Positioning Optimizer (SPO) is the algorithmic synthesis of all preceding analyses. It answers: "Given everything we know about the competitive landscape, buyer behavior, and market trajectory, what positioning maximizes Oracle Health's win probability across the broadest set of scenarios?"

### 9.2 Optimization Algorithm

```
STRATEGIC POSITIONING OPTIMIZER (SPO)

Objective Function:
  Maximize: E[win_rate(P_oracle)] × Robustness(P_oracle)

  Where:
  P_oracle = Oracle Health's positioning vector
    [price_position, product_scope, innovation_posture,
     market_focus, messaging_emphasis]

  E[win_rate] = Expected win rate across all Monte Carlo scenarios
  Robustness = Fraction of scenarios where win rate > baseline

Algorithm (Grid Search + Monte Carlo):

  1. Define positioning grid:
     For each dimension, define 3-5 feasible positions.
     Total grid: 3^5 = 243 possible positioning combinations.

  2. For each positioning combination P_j:
     Run Monte Carlo simulation (Section 5) with P_j fixed as Oracle's strategy.
     Record: E[win_rate_j], Robustness_j, P10_j, P90_j

  3. Calculate composite score:
     Score_j = E[win_rate_j] × Robustness_j × (1 - downside_penalty_j)

     Where:
     downside_penalty = max(0, baseline_win_rate - P10_j) / baseline_win_rate
     (Penalizes strategies with severe worst-case scenarios)

  4. Rank all 243 positions by Score_j.

  5. Top 5 positions form the "efficient frontier" of strategies.
     Present to executive team with:
     - Expected win rate
     - Robustness score
     - Best-case / worst-case scenarios
     - Key assumptions and sensitivities
     - Required investments and capability gaps

OUTPUT: Strategic Positioning Recommendation
  ┌──────────────────────────────────────────────────────────────┐
  │ RECOMMENDED POSITIONING: [Description]                       │
  │                                                              │
  │ Expected Win Rate: +X.X% vs. current baseline               │
  │ Robustness: X% of scenarios produce positive outcome         │
  │ P10 (worst case): [scenario description + impact]            │
  │ P90 (best case): [scenario description + impact]             │
  │ Key Assumption: [The assumption this strategy depends on]    │
  │ Key Risk: [What would make this strategy fail]               │
  │ Required Investment: [What Oracle Health needs to execute]   │
  │ Timeline to Impact: [When we'd expect to see results]        │
  │                                                              │
  │ ALTERNATIVE POSITIONS (efficient frontier):                  │
  │ [2-4 alternatives with trade-off summary]                    │
  └──────────────────────────────────────────────────────────────┘
```

---

## 10. Application Examples

### 10.1 ERP Strategy Positioning

**Scenario**: Oracle's broader cloud ERP portfolio creates both opportunities and baggage in healthcare deals. Buyers associate "Oracle" with ERP, which can be an advantage (integration story) or liability (not a healthcare pure-play).

**War Game Setup**:
- Red Team plays Epic ("We're healthcare-only — Oracle is an ERP company selling healthcare on the side")
- Blue Team tests 3 positioning responses: (1) Integration advantage, (2) Healthcare-first autonomy, (3) Best of both worlds
- Monte Carlo models buyer response to each framing across deal sizes and segments

### 10.2 RCM Competitive Defense

**Scenario**: Waystar and R1 RCM are aggressively targeting Oracle Health's RCM install base with "rip-and-replace" campaigns emphasizing modern architecture and outcomes-based pricing.

**War Game Setup**:
- Red Team plays Waystar and R1 simultaneously (coalition threat)
- Blue Team tests defensive vs. offensive strategies: (1) Retention pricing + integration lock-in, (2) Counter-attack with AI-powered RCM, (3) Outcomes-based pricing match
- Decision tree maps 2-year competitive dynamics with market share impact at each node

### 10.3 AI/Clinical Differentiation vs. Nuance DAX

**Scenario**: Microsoft/Nuance DAX is becoming the ambient clinical documentation standard. Epic has deep DAX integration. Oracle Health needs to determine its AI clinical strategy: build, buy, partner, or pivot.

**War Game Setup**:
- Red Team plays Microsoft/Nuance (platform play) and Epic (integration play)
- Blue Team evaluates 4 Oracle Health AI strategies (see Section 7.2 Decision Tree)
- Equilibrium modeling determines whether the market is tipping toward a single AI standard or remaining fragmented
- SPO identifies the positioning that works across both market structure outcomes

---

## 11. Integration Map

```
SOP-34 INTEGRATION DEPENDENCIES

SOP-34 (War Gaming & Simulation) RECEIVES FROM:
  ← SOP-09 (Win/Loss): Decision drivers inform Red Team briefing packages
  ← SOP-10 (Pricing): Pricing intelligence informs scenario variables
  ← SOP-32 (Deal Scoring): Active pipeline data informs tactical scenarios
  ← SOP-33 (Signal Detection): Competitor predictions trigger war games;
     signal data informs Red Team intelligence packages
  ← SOP-17 (Existing War Gaming): Extends with quantitative methods

SOP-34 FEEDS:
  → SOP-08 (Battlecards): War game insights update competitive messaging
  → SOP-12 (Competitive Response): Scenario outputs pre-position response plans
  → SOP-29 (Deal Support): Strategic positioning recommendations inform
     deal-level positioning
  → SOP-32 (Deal Scoring): Scenario probabilities update baseline assumptions
  → SOP-33 (Signal Detection): Key uncertainties from scenarios prioritize
     monitoring focus
  → Strategic Planning: Annual plan inputs, product roadmap recommendations,
     market expansion priorities
```

---

## 12. RACI Matrix

| Activity | Mike Rodgers | CI Analyst | Strategy Lead | Product Leader | Sales VP | Matt Cohlmia |
|----------|:---:|:---:|:---:|:---:|:---:|:---:|
| War game design & scenario selection | **R/A** | C | C | C | I | **I** |
| Intelligence briefing package assembly | **R** | **R** | I | I | I | I |
| War game facilitation (Control Team) | **R/A** | **R** | I | I | I | I |
| Red Team leadership | I | C | **R** | C | C | I |
| Blue Team leadership | I | I | C | **R** | **R** | I |
| Monte Carlo simulation execution | **R/A** | C | I | I | I | I |
| Decision tree construction | **R/A** | C | C | C | I | I |
| Strategic Positioning Recommendation | **R** | C | C | C | C | **A** |
| Scenario Report delivery | **R** | C | I | I | I | **A** |
| Follow-up tracking (scenario validation) | **R/A** | **R** | I | I | I | I |

---

## 13. KPIs

### Leading Indicators (Per War Game)

| KPI | Target | Measurement |
|-----|--------|-------------|
| Red Team move plausibility (avg score) | ≥3.5 / 5.0 | Control Team scoring |
| Blue Team surprise count | ≥2 per game | Strategies Blue Team didn't anticipate |
| Participant Net Promoter Score | >50 | Post-game survey: "Would you recommend this exercise to a colleague?" |
| Action items generated | ≥5 concrete, assigned actions | Debrief action item count |

### Lagging Indicators (Quarterly / Annual)

| KPI | Target | Measurement |
|-----|--------|-------------|
| Scenario prediction accuracy | >40% of modeled scenarios confirmed directionally within 12 months | Confirmed / total predictions |
| Strategic decision quality | >70% of war-game-informed decisions rated "good" or "excellent" in retrospective | Annual strategy review assessment |
| War game cadence | ≥4 per year (1 strategic + 3 tactical/rapid) | Games conducted / games planned |
| Signal-to-scenario conversion | >50% of P0/P1 signals from SOP-33 feed into scenario modeling within 30 days | Signals incorporated / P0+P1 signals |

### North Star Metric

**Strategic Surprise Rate**: The percentage of significant competitive or market events in a 12-month period that Oracle Health's war gaming and simulation system did NOT anticipate. Target: <20% surprise rate within 18 months of program maturity. This means 80%+ of significant market events were modeled in some form before they occurred, giving Oracle Health a prepared response rather than a reactive scramble.

---

## 14. Maturity Roadmap

| Phase | Timeline | Capability | Dependencies |
|-------|----------|-----------|-------------|
| **Phase 1: Qualitative War Games** | Q2-Q3 2026 | Structured war games using SOP-17 framework + this SOP's protocol enhancements (bias mitigation, plausibility scoring, structured Red/Blue team composition). 2 games minimum. | SOP-17 operational. SOP-08/09/10/33 data available for briefing packages. Executive sponsor buy-in. |
| **Phase 2: Quantitative Extension** | Q4 2026 | Monte Carlo simulation added post-war-game. Decision tree analysis for key strategic options. Python/R simulation scripts operational. | Data science consultation (can be external). Historical deal data for model calibration. |
| **Phase 3: Integrated Simulation** | H1 2027 | Full SOP-32/33/34 integration. Signal detection (33) auto-triggers scenario modeling (34). Deal scoring (32) incorporates scenario probabilities. Equilibrium modeling operational. | All three SOPs (32/33/34) operational. Data pipeline integrated. |
| **Phase 4: Continuous Simulation** | H2 2027+ | Strategic Positioning Optimizer runs continuously with live data feeds. Quarterly "state of the competitive landscape" simulation update. AI-assisted scenario generation. Predictive competitive strategy (not just reactive war gaming). | Full data maturity. AI model access. Organizational buy-in for simulation-driven strategy. |

---

## Appendix A: War Game Pre-Read Template

```
WAR GAME PRE-READ PACKAGE — [Competitor Name]

Section 1: Company Overview
  - Revenue, headcount, growth rate, financial health
  - Corporate strategy (public statements, 10-K/annual report themes)
  - Recent executive changes

Section 2: Product Position
  - Product portfolio (from SOP-08 battlecards)
  - Recent launches and roadmap signals (from SOP-33)
  - KLAS/analyst positioning
  - Known strengths and weaknesses

Section 3: Go-to-Market
  - Pricing and packaging intelligence (from SOP-10)
  - Sales motion (direct, channel, consultant relationships)
  - Target market and recent wins/losses

Section 4: Against Oracle Health
  - Head-to-head win rate and key drivers (from SOP-09)
  - Known competitive messaging against Oracle Health
  - Active deals where this competitor is present (from SOP-32 CTI data)

Section 5: Predicted Next Moves
  - SOP-33 predictions for this competitor
  - Pattern analysis: What has this competitor done in similar market conditions?
  - Key uncertainties: What don't we know?
```

---

*SOP-34 is designed by Mike Rodgers. War gaming is the highest-leverage CI activity when done well and the biggest time waste when done poorly. The difference is rigor: briefing packages grounded in data (not assumptions), Red Teams that genuinely advocate for competitors (not straw men), quantitative modeling that honestly represents uncertainty (not false precision), and follow-up that tracks whether predictions materialized (not one-and-done exercises). This SOP enforces that rigor at every step.*
