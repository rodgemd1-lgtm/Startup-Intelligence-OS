# SOP-35: Deal Strategy Recommendation Engine

**Owner**: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence
**Version**: 1.0 DRAFT — Awaiting Mike's approval
**Last Updated**: 2026-03-25
**Category**: Advanced Analytics & Sales Intelligence
**Priority**: P1 — Closes the loop from Win/Loss insights to proactive deal strategy
**Maturity**: Gap → Documented (this SOP)
**Upstream Dependencies**: SOP-09 (Win/Loss Analysis), SOP-10 (Pricing Intelligence), SOP-32 (Deal Scoring)
**Downstream Consumers**: SOP-29 (Deal Positioning Packages), Sales Ops, Field Sales

---

## Purpose

Transform accumulated win/loss patterns, competitive intelligence, and deal characteristics into proactive, data-driven deal strategy recommendations that tell Sales not just "what to say" but "how to structurally set up this deal to maximize win probability."

**The core problem:**
Oracle Health has intelligence scattered across hundreds of competitive deals — battlecards, win/loss interviews, pricing data, tribal knowledge in the heads of top reps. That intelligence is reactive ("here's what we know about Epic") rather than prescriptive ("here's how to position THIS deal against Epic given your buyer profile, deal size, and care setting"). This SOP builds the engine that converts historical patterns into forward-looking deal strategy.

**What this engine produces:**
A Pre-Call Intelligence Package — a 1-2 page deal strategy brief a rep reviews in 15 minutes before a major call — containing recommended positioning, anticipated competitor counter-moves with pre-built responses, matched proof points, pricing guidance, and stakeholder-specific messaging. Every recommendation is traceable to historical win data.

**Why this matters:**
- Deals that follow data-informed strategy recommendations win at measurably higher rates than those relying on rep intuition alone (Gartner: structured deal strategies improve win rates 15-28%)
- The gap between "having intelligence" and "applying intelligence at the point of decision" is where most CI programs lose impact (Klue 2025: only 22% of CI teams measure revenue influence)
- Top-performing reps already do this intuitively — this engine democratizes that pattern recognition across the entire sales org

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DEAL STRATEGY RECOMMENDATION ENGINE               │
│                                                                      │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────────┐ │
│  │  DATA INPUTS  │   │   ALGORITHM  │   │  OUTPUT: PRE-CALL BRIEF  │ │
│  │              │   │    (DStA)    │   │                          │ │
│  │ Win/Loss DB  │──▶│              │──▶│ Positioning Strategy     │ │
│  │ (SOP-09)     │   │ Pattern Match│   │ Counter-Move Playbook    │ │
│  │              │   │ Monte Carlo  │   │ Matched Proof Points     │ │
│  │ Deal Scoring │──▶│ Simulation   │──▶│ Pricing Guidance         │ │
│  │ (SOP-32)     │   │              │   │ Stakeholder Messaging    │ │
│  │              │   │ Proof Point  │   │ Win Probability Score    │ │
│  │ Pricing Intel│──▶│ Matching     │   │                          │ │
│  │ (SOP-10)     │   │              │   └──────────────────────────┘ │
│  │              │   │ Counter-Move │                                 │
│  │ Battlecards  │──▶│ Prediction   │   ┌──────────────────────────┐ │
│  │              │   │              │   │  FEEDBACK LOOP            │ │
│  │ CRM Data     │──▶│ Expert Panel │   │  Deal outcome → Model    │ │
│  │ (Salesforce)  │   │ Calibration  │   │  recalibration quarterly │ │
│  └──────────────┘   └──────────────┘   └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## PROGRAM GOVERNANCE

### Ownership & RACI

| Role | R | A | C | I |
|------|---|---|---|---|
| **Engine Design & Methodology** | Mike Rodgers | Mike Rodgers | Expert Panel | Matt Cohlmia |
| **Win Pattern Library Curation** | Mike Rodgers | Mike Rodgers | Sales Ops, Top Reps | Field Sales |
| **Deal Input Collection** | Sales Ops | Sales Ops | Mike Rodgers | — |
| **Pre-Call Brief Generation** | Mike Rodgers (manual) / CI Analyst (at scale) | Mike Rodgers | Sales Reps | — |
| **Strategy Recommendation Delivery** | CI Analyst / Sales Enablement | Mike Rodgers | Sales Managers | Field Sales |
| **Model Calibration & Backtesting** | Mike Rodgers | Mike Rodgers | Expert Panel | Matt Cohlmia |
| **Feedback Loop (Outcome Tracking)** | Sales Ops | Mike Rodgers | Sales Reps | — |

### Expert Panel

A standing review body that calibrates the engine quarterly:

| Panelist Role | Why They're On the Panel |
|---------------|-------------------------|
| Top-performing Enterprise Rep (rotating) | Pattern recognition from the field; validates that recommendations match reality |
| Sales Engineering Lead | Technical positioning accuracy; knows what proof points actually land |
| Solutions Consulting Lead | Implementation feasibility of recommended positioning; catches over-promises |
| Mike Rodgers (Chair) | Competitive intelligence synthesis; methodology integrity |
| Sales Ops Analyst | Data quality; CRM accuracy; deal characteristic validation |

Panel meets quarterly to review model accuracy, recalibrate weights, and retire stale patterns.

---

## SECTION 1: DEAL STRATEGY ALGORITHM (DStA)

### 1.1 Input Vector

Every deal entering the engine is characterized by a **Deal DNA Vector** — the set of attributes that determine which historical patterns are most relevant:

| Input Factor | Source | Weight in Similarity Matching |
|-------------|--------|-------------------------------|
| Primary Competitor | CRM / Rep input | 0.25 (highest — competitor identity is the strongest predictor) |
| Care Setting | CRM | 0.15 (community hospital vs. academic medical center vs. ambulatory) |
| Deal Size (TCV) | CRM | 0.12 |
| Buyer Profile (primary decision-maker role) | Rep input | 0.12 |
| Deal Stage at engagement | CRM | 0.10 |
| Incumbent System | Rep input / research | 0.08 |
| Decision Timeline | Rep input | 0.06 |
| Number of Competitors in Eval | Rep input | 0.05 |
| Geographic Region | CRM | 0.04 |
| Regulatory/Compliance Drivers | Rep input | 0.03 |

**Total**: 1.00

### 1.2 DStA Pseudocode

```
FUNCTION generate_deal_strategy(deal_input):

    # STEP 1: Build the Deal DNA Vector
    deal_vector = construct_vector(
        competitor    = deal_input.primary_competitor,
        care_setting  = deal_input.care_setting,
        deal_size     = normalize_tcv(deal_input.tcv),
        buyer_profile = deal_input.primary_buyer_role,
        stage         = deal_input.current_stage,
        incumbent     = deal_input.incumbent_system,
        timeline      = deal_input.decision_timeline_days,
        num_competitors = deal_input.competitor_count,
        region        = deal_input.geo_region,
        compliance    = deal_input.regulatory_drivers
    )

    # STEP 2: Retrieve Historical Win Patterns
    # Cosine similarity against all closed deals in Win Pattern Library
    similar_deals = win_pattern_library.query(
        vector = deal_vector,
        similarity_threshold = 0.65,
        min_results = 10,
        max_results = 50,
        outcome_filter = None  # include both wins and losses
    )

    # STEP 3: Extract Candidate Strategies
    # Group similar deals by the positioning strategy used
    strategy_clusters = cluster_by_strategy(similar_deals)

    FOR EACH cluster IN strategy_clusters:
        cluster.win_rate = count(cluster.wins) / count(cluster.total)
        cluster.avg_deal_size = mean(cluster.tcv)
        cluster.recency_weight = apply_decay(cluster.close_dates, half_life=180_days)
        cluster.sample_size_confidence = wilson_score_interval(cluster.wins, cluster.total)

    # STEP 4: Monte Carlo Simulation
    # For each candidate strategy, simulate 1,000 deal outcomes
    FOR EACH cluster IN strategy_clusters:
        cluster.simulated_win_prob = monte_carlo_simulate(
            base_win_rate = cluster.win_rate,
            deal_similarity = cluster.avg_similarity_score,
            recency_factor = cluster.recency_weight,
            sample_confidence = cluster.sample_size_confidence,
            competitor_trend = get_competitor_trend(deal_input.primary_competitor, 90_days),
            n_simulations = 1000
        )

    # STEP 5: Rank and Select Top 3 Strategies
    ranked_strategies = sort_by(strategy_clusters, key=simulated_win_prob, descending=True)
    top_strategies = ranked_strategies[:3]

    # STEP 6: Enrich Each Strategy
    FOR EACH strategy IN top_strategies:
        strategy.counter_moves = predict_counter_moves(strategy, deal_input.primary_competitor)
        strategy.proof_points = match_proof_points(strategy, deal_vector)
        strategy.pricing_guidance = get_pricing_envelope(deal_vector, strategy)
        strategy.stakeholder_messages = generate_stakeholder_map(deal_input, strategy)

    # STEP 7: Generate Pre-Call Intelligence Package
    RETURN build_pre_call_brief(
        deal = deal_input,
        strategies = top_strategies,
        confidence_level = top_strategies[0].simulated_win_prob,
        data_freshness = max(similar_deals.close_dates)
    )
```

### 1.3 Minimum Data Thresholds

The engine produces recommendations only when sufficient historical data exists:

| Confidence Tier | Min Similar Deals | Min Wins in Cluster | Output Label |
|----------------|-------------------|---------------------|--------------|
| **High Confidence** | 30+ | 10+ | "Data-Backed Recommendation" |
| **Moderate Confidence** | 15-29 | 5-9 | "Directional Recommendation — Limited Sample" |
| **Low Confidence** | 5-14 | 2-4 | "Exploratory Recommendation — Expert Review Required" |
| **Insufficient Data** | <5 | <2 | No automated recommendation; escalate to Expert Panel |

---

## SECTION 2: WIN PATTERN LIBRARY

### 2.1 Structure

Every validated win pattern is stored as a structured record indexed across five dimensions:

**Primary Index**: `Competitor × Care Setting × Deal Size Tier × Buyer Profile`

Each pattern record contains:

| Field | Description | Example |
|-------|-------------|---------|
| `pattern_id` | Unique identifier | `WP-EPIC-AMC-ENT-CMIO-014` |
| `competitor` | Primary competitor | Epic |
| `care_setting` | Hospital type | Academic Medical Center |
| `deal_size_tier` | S (<$5M), M ($5-20M), L ($20-50M), XL (>$50M) | L |
| `buyer_profile` | Primary decision-maker role | CMIO |
| `positioning_approach` | The strategic frame that worked | "Platform consolidation — reduce vendor count from 7 to 2" |
| `proof_points_used` | References and data that resonated | [REF-AMC-032, CS-PLATFORM-008] |
| `pricing_structure` | How the deal was commercially structured | "Phased implementation with milestone-based payments" |
| `objections_overcome` | Top objections raised and the response that worked | {"implementation risk": "Dedicated go-live team + penalty clause"} |
| `stakeholder_map` | Who was involved and what mattered to each | {"CMIO": "clinical workflow", "CFO": "TCO reduction", "CNO": "nursing satisfaction"} |
| `win_factors` | Top 3 reasons the customer chose Oracle Health (from SOP-09 interview) | ["Platform breadth", "Reference site visit", "Implementation commitment"] |
| `loss_risk_factors` | What almost lost the deal | ["Epic's brand strength with the board", "Nursing staff familiarity with Epic"] |
| `date_closed` | When the deal closed | 2025-11-15 |
| `validated_by` | Expert Panel sign-off | Mike Rodgers, 2025-12-01 |

### 2.2 Pattern Lifecycle

```
New Win/Loss Data (SOP-09)
    │
    ▼
CANDIDATE PATTERN extracted by Mike
    │
    ▼
CORROBORATION CHECK — Does this pattern appear in 3+ deals?
    │
    ├── YES → VALIDATED PATTERN → enters Win Pattern Library
    │         (Expert Panel reviews quarterly)
    │
    └── NO → EMERGING PATTERN → flagged for monitoring
              (requires 2 more corroborating deals to validate)
```

### 2.3 Pattern Retirement

Patterns are retired when:
- Win rate for deals using the pattern drops below 30% for two consecutive quarters
- The competitive landscape shifts (e.g., competitor releases a major new product that invalidates the positioning)
- Expert Panel votes to retire during quarterly review

Retired patterns move to an archive with a `retired_reason` field. They are excluded from the recommendation engine but retained for longitudinal analysis.

---

## SECTION 3: COMPETITIVE COUNTER-MOVE PREDICTION

### 3.1 Decision Tree Framework

For each recommended positioning strategy, the engine predicts the most likely competitor response and pre-builds the counter.

**Structure**: `IF we position on X → THEY counter with Y → WE respond with Z`

```
RECOMMENDED STRATEGY: "Platform consolidation — reduce vendor sprawl"
│
├── IF competitor = Epic:
│   ├── LIKELY COUNTER: "Epic is the only true single-platform — Oracle still
│   │                    requires integration across modules"
│   │   └── PRE-BUILT RESPONSE: "Show unified data model architecture diagram.
│   │       Reference [SITE-AMC-032] who migrated from 6 vendors to Oracle
│   │       Health with zero integration middleware. Offer architecture
│   │       deep-dive with customer's IT team."
│   │
│   ├── LIKELY COUNTER: "Epic Community Connect gives you network effects
│   │                    Oracle can't match"
│   │   └── PRE-BUILT RESPONSE: "Acknowledge network value, pivot to data
│   │       ownership and interoperability. Reference TEFCA compliance and
│   │       Oracle Health's open API architecture."
│   │
│   └── LIKELY COUNTER: "Your install base is shrinking / momentum is with Epic"
│       └── PRE-BUILT RESPONSE: "Cite recent competitive wins [anonymized].
│           Pivot to customer outcomes: '[SITE-REF] went live on-time,
│           on-budget and saw X% improvement in Y.'"
│
├── IF competitor = MEDITECH:
│   ├── LIKELY COUNTER: "MEDITECH Expanse is modern, cloud-native, and
│   │                    purpose-built for community hospitals"
│   │   └── PRE-BUILT RESPONSE: "Acknowledge community fit, then expand
│   │       the frame: 'What happens when you add ambulatory, revenue
│   │       cycle, population health? MEDITECH requires bolt-ons. Oracle
│   │       Health is one platform across the continuum.'"
│   ...
│
└── IF competitor = Other/Unknown:
    └── DEFAULT COUNTER-MOVE SET based on generic positioning defense
```

### 3.2 Counter-Move Confidence Scoring

Each predicted counter-move carries a confidence score based on how frequently it has been observed:

| Confidence | Observation Frequency | Label |
|-----------|----------------------|-------|
| **High** | Observed in 70%+ of deals with this competitor | "Almost certain they will say this" |
| **Medium** | Observed in 40-69% of deals | "Likely response — be prepared" |
| **Low** | Observed in 15-39% of deals | "Possible response — have material ready" |
| **Emerging** | Observed in <15% but trending upward | "New tactic — monitor" |

---

## SECTION 4: MONTE CARLO STRATEGY SIMULATION

### 4.1 Simulation Design

For each candidate strategy, the engine runs 1,000 simulated deal outcomes to produce a probability-weighted recommendation.

**Input variables (each with a probability distribution):**

| Variable | Distribution Type | Source |
|----------|------------------|--------|
| Base win rate for this strategy cluster | Beta(wins, losses) | Win Pattern Library |
| Deal similarity score | Normal(mean_sim, std_sim) | DStA similarity calculation |
| Recency factor | Exponential decay, half-life = 180 days | Deal close dates |
| Competitor momentum | Uniform(-0.10, +0.10) adjustment | Last 90 days win/loss trend |
| Deal complexity factor | Triangular(min, mode, max) | Number of stakeholders, modules, sites |

### 4.2 Simulation Pseudocode

```
FUNCTION monte_carlo_simulate(strategy_cluster, deal_input, n=1000):

    outcomes = []

    FOR i = 1 TO n:
        # Sample from each distribution
        base_rate = sample_beta(cluster.wins, cluster.losses)
        similarity = sample_normal(cluster.avg_similarity, cluster.sim_std)
        recency = sample_exponential(cluster.recency_weight)
        momentum = sample_uniform(-0.10, +0.10) * get_momentum_direction(competitor)
        complexity = sample_triangular(deal_input.complexity_min,
                                        deal_input.complexity_mode,
                                        deal_input.complexity_max)

        # Composite win probability for this simulation run
        sim_win_prob = base_rate * similarity * recency * (1 + momentum) * complexity
        sim_win_prob = clamp(sim_win_prob, 0.05, 0.95)  # floor/ceiling

        # Simulate binary outcome
        outcome = random() < sim_win_prob
        outcomes.append(outcome)

    RETURN {
        win_probability: mean(outcomes),
        confidence_interval_90: percentile(outcomes, [5, 95]),
        worst_case: percentile(outcomes, 10),
        best_case: percentile(outcomes, 90)
    }
```

### 4.3 Output Interpretation

The simulation produces a comparison table for the rep:

```
┌─────────────────────────────────────────────────────────────┐
│  STRATEGY SIMULATION RESULTS — Deal #OH-2026-4471           │
│  Competitor: Epic | Care Setting: AMC | TCV: $28M           │
├─────────────────────┬──────────┬──────────────┬─────────────┤
│ Strategy            │ Win Prob │ 90% CI       │ Sample Size │
├─────────────────────┼──────────┼──────────────┼─────────────┤
│ A: Platform Consol. │   68%    │ [54%, 79%]   │ 34 deals    │
│ B: Clinical Depth   │   52%    │ [38%, 64%]   │ 22 deals    │
│ C: TCO Reduction    │   41%    │ [28%, 55%]   │ 18 deals    │
└─────────────────────┴──────────┴──────────────┴─────────────┘
  RECOMMENDATION: Strategy A — Platform Consolidation
  Confidence: HIGH (30+ similar deals, 90% CI excludes 50%)
```

---

## SECTION 5: PROOF POINT MATCHING ENGINE

### 5.1 Matching Algorithm

The engine does not serve a generic reference list. It matches the most relevant proof points to the specific deal profile using a weighted scoring model.

```
FUNCTION match_proof_points(strategy, deal_vector, max_results=5):

    all_proof_points = proof_point_database.get_all_active()
    scored = []

    FOR EACH proof_point IN all_proof_points:
        score = 0

        # Dimension 1: Care setting match (0-30 points)
        IF proof_point.care_setting == deal_vector.care_setting:
            score += 30
        ELIF proof_point.care_setting IN same_category(deal_vector.care_setting):
            score += 15

        # Dimension 2: Deal size proximity (0-20 points)
        size_ratio = min(proof_point.deal_size, deal_vector.deal_size) /
                     max(proof_point.deal_size, deal_vector.deal_size)
        score += 20 * size_ratio

        # Dimension 3: Competitor match (0-25 points)
        IF proof_point.displaced_competitor == deal_vector.competitor:
            score += 25  # This reference displaced the SAME competitor
        ELIF proof_point.competed_against == deal_vector.competitor:
            score += 15  # Competed against them even if different outcome

        # Dimension 4: Recency (0-15 points)
        months_old = age_in_months(proof_point.date)
        score += max(0, 15 - (months_old * 0.5))  # loses 0.5 points per month

        # Dimension 5: Buyer role match (0-10 points)
        IF proof_point.champion_role == deal_vector.buyer_profile:
            score += 10

        scored.append((proof_point, score))

    # Return top matches above minimum threshold
    scored.sort(key=lambda x: x[1], reverse=True)
    RETURN [pp FOR pp, s IN scored[:max_results] IF s >= 40]
```

### 5.2 Proof Point Record Structure

| Field | Description |
|-------|-------------|
| `proof_point_id` | Unique identifier (e.g., `PP-AMC-EPIC-2025-032`) |
| `type` | Case Study / ROI Data / Customer Quote / Reference Visit / Analyst Report |
| `customer_name` | (only for referenceable customers with consent) |
| `care_setting` | Community Hospital / AMC / Health System / Ambulatory / Specialty |
| `deal_size` | TCV of the referenced deal |
| `displaced_competitor` | Who they replaced (if applicable) |
| `key_metric` | The headline result ("32% reduction in physician documentation time") |
| `buyer_resonance` | Which buyer persona this proof point resonates with most |
| `last_verified` | Date the proof point was confirmed still accurate and referenceable |
| `expiry_date` | Auto-expires 18 months after `last_verified` unless renewed |

---

## SECTION 6: PRE-CALL INTELLIGENCE PACKAGE

### 6.1 Output Format

The final deliverable is a structured brief a sales rep reviews in 15 minutes before a critical call.

```
╔══════════════════════════════════════════════════════════════════╗
║  PRE-CALL INTELLIGENCE PACKAGE                                  ║
║  Deal: [Customer Name] — [Deal ID]                              ║
║  Generated: [Date] | Confidence: [HIGH/MODERATE/LOW]            ║
║  Prepared by: M&CI — Mike Rodgers                               ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  1. DEAL SNAPSHOT                                                ║
║     Competitor: [X] | Care Setting: [Y] | TCV: [Z]              ║
║     Stage: [N] | Timeline: [M weeks] | Key Buyer: [Role]        ║
║                                                                  ║
║  2. RECOMMENDED POSITIONING (Strategy A — [Name])                ║
║     Core narrative: [2-3 sentences]                              ║
║     Why this works: [Historical basis — X wins in Y deals]       ║
║     Win probability: [N%] (90% CI: [low%-high%])                 ║
║                                                                  ║
║  3. COMPETITOR COUNTER-MOVES                                     ║
║     ┌─────────────────────────────────────────────────────┐      ║
║     │ They will likely say:  [Counter-move 1]             │      ║
║     │ Your response:         [Pre-built response]         │      ║
║     │ Confidence:            [HIGH — seen in 80% of deals]│      ║
║     ├─────────────────────────────────────────────────────┤      ║
║     │ They may also say:     [Counter-move 2]             │      ║
║     │ Your response:         [Pre-built response]         │      ║
║     │ Confidence:            [MEDIUM — seen in 45%]       │      ║
║     └─────────────────────────────────────────────────────┘      ║
║                                                                  ║
║  4. MATCHED PROOF POINTS                                         ║
║     #1: [Customer] — [Key metric] (Match score: 92/100)          ║
║         Why relevant: Same care setting, displaced same competitor║
║     #2: [Customer] — [Key metric] (Match score: 85/100)          ║
║     #3: [Customer] — [Key metric] (Match score: 78/100)          ║
║                                                                  ║
║  5. PRICING GUIDANCE                                             ║
║     Recommended structure: [e.g., phased implementation]         ║
║     Benchmark range: [$X - $Y per bed/provider]                  ║
║     Discount authority needed: [Standard / VP / SVP]             ║
║     Source: SOP-10 pricing model + similar deal analysis          ║
║                                                                  ║
║  6. STAKEHOLDER-SPECIFIC MESSAGING                               ║
║     ┌─────────────┬────────────────────────────────────┐         ║
║     │ CMIO        │ Lead with: [clinical workflow]      │         ║
║     │ CFO         │ Lead with: [TCO + risk reduction]   │         ║
║     │ CNO         │ Lead with: [nursing satisfaction]   │         ║
║     │ CIO         │ Lead with: [platform + security]    │         ║
║     └─────────────┴────────────────────────────────────┘         ║
║                                                                  ║
║  7. ALTERNATE STRATEGY (if Strategy A stalls)                    ║
║     Pivot to: Strategy B — [Name] (Win prob: [N%])               ║
║     Trigger to pivot: [What signal indicates A isn't working]    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

### 6.2 Delivery Mechanism

| Stage | Trigger | Delivery |
|-------|---------|----------|
| **Stage 2 (Discovery)** | Deal registered with competitor identified | Auto-generate brief; deliver to rep via email + Salesforce attachment |
| **Stage 4 (Proposal)** | Deal advances to proposal stage | Refresh brief with updated intelligence; flag any new counter-moves |
| **Pre-Demo / Pre-Exec Meeting** | Rep requests or calendar trigger | On-demand refresh with latest proof points and pricing data |
| **Stage 6 (Negotiation)** | Deal enters negotiation | Final refresh focused on pricing guidance and closing strategy |

### 6.3 Generation SLA

| Deal Priority | Generation Time | Review |
|---------------|----------------|--------|
| **P1 (Top 20 deals)** | 4 business hours | Mike reviews before delivery |
| **P2 (Named accounts)** | 2 business days | CI Analyst generates; Mike spot-checks |
| **P3 (All competitive deals)** | 5 business days | Automated template with manual enrichment |

---

## SECTION 7: INTEGRATION MAP

### 7.1 Upstream SOPs (Data Sources)

| SOP | What It Feeds to This Engine | Refresh Cadence |
|-----|------------------------------|-----------------|
| **SOP-09: Win/Loss Analysis** | Interview-coded win/loss drivers, behavioral patterns, validated quotes, decision factor weights | Per interview (ongoing) |
| **SOP-10: Pricing Intelligence** | Competitor pricing benchmarks, discount patterns, deal structure trends | Monthly |
| **SOP-32: Deal Scoring** | Deal risk score, competitive threat level, win probability baseline | Real-time (CRM-triggered) |

### 7.2 Downstream SOPs (Consumers)

| SOP | What It Pulls from This Engine | How |
|-----|-------------------------------|-----|
| **SOP-29: Deal Positioning Packages** | Pre-Call Intelligence Package is the core input for positioning kits | CI Analyst assembles positioning package starting from the Pre-Call brief |

### 7.3 Data Flow Diagram

```
SOP-09 Win/Loss ──────┐
                       │
SOP-10 Pricing ────────┼──▶ DStA Algorithm ──▶ Pre-Call Brief ──▶ SOP-29 Positioning
                       │         │
SOP-32 Deal Score ─────┘         │
                                 ▼
Battlecard Library ──────▶ Counter-Move Engine
                                 │
CRM (Salesforce) ────────▶ Deal DNA Vector
                                 │
                                 ▼
                          Feedback Loop
                    (outcome → recalibration)
```

---

## KPIs AND MEASUREMENT

### Primary KPIs

| KPI | Target | Measurement Method |
|-----|--------|-------------------|
| **Win Rate Lift (Recommended vs. Non-Recommended)** | +10pp win rate on deals that follow engine recommendations vs. those that don't | Tag deals in CRM as "Strategy Recommended" / "Strategy Followed" / "No Recommendation"; compare win rates quarterly |
| **Rep Adoption Rate** | 60% of P1/P2 reps request or use Pre-Call briefs within 6 months | Track brief generation requests and downloads in Salesforce |
| **Recommendation Accuracy** | 70%+ of "High Confidence" recommendations result in wins | Backtest quarterly: did deals following the top-ranked strategy win at the predicted rate? |
| **Time-to-Brief** | Meet SLA targets (4hr / 2d / 5d by priority tier) | Track generation timestamp vs. delivery timestamp |

### Secondary KPIs

| KPI | Target | Measurement Method |
|-----|--------|-------------------|
| **Win Pattern Library Coverage** | Validated patterns exist for 80% of Competitor × Care Setting combinations | Quarterly gap analysis of the library |
| **Counter-Move Prediction Accuracy** | 65%+ of predicted counter-moves observed in actual deals | Post-deal debrief confirms which counter-moves were encountered |
| **Proof Point Freshness** | 90%+ of served proof points verified within last 12 months | Automated expiry tracking in proof point database |
| **Feedback Loop Completion** | 80%+ of recommended deals have outcome data fed back within 30 days of close | CRM automation + Sales Ops tracking |

### Measurement Methodology: Recommended vs. Non-Recommended Deals

To avoid selection bias (better deals naturally get more attention), measurement uses:

1. **Propensity Score Matching**: Match recommended deals to non-recommended deals with similar Deal DNA Vectors. Compare outcomes on matched pairs, not raw populations.
2. **Time-Series Analysis**: Track win rate trends before and after engine deployment per rep, per segment, per competitor.
3. **Rep Self-Report**: Post-deal survey asks "Did you follow the recommended strategy? Fully / Partially / No." Segment results accordingly.

---

## PHASED ROLLOUT

### Phase 1: Foundation (Months 1-3)
- Build Win Pattern Library from existing SOP-09 data (target: 50+ validated patterns)
- Define Deal DNA Vector schema and integrate with Salesforce
- Manual Pre-Call brief generation for top 10 deals
- Expert Panel inaugural meeting and weight calibration

### Phase 2: Engine Build (Months 4-6)
- Implement DStA similarity matching algorithm
- Build Proof Point Matching Engine with initial proof point database
- Develop Counter-Move Prediction trees for top 3 competitors
- Monte Carlo simulation prototype and backtesting against historical deals

### Phase 3: Scale (Months 7-9)
- Automate Pre-Call brief generation for P1/P2 deals
- Expand counter-move trees to all tracked competitors
- Launch feedback loop: outcome data flows back to model quarterly
- First quarterly calibration with Expert Panel

### Phase 4: Optimization (Months 10-12)
- Full measurement framework operational; publish first win rate lift report
- Pattern Library exceeds 100 validated patterns
- Model recalibration based on first two quarters of outcome data
- Evaluate automation/tooling needs for sustained operation at scale

---

## EXPERT PANEL SCORING CRITERIA

When the Expert Panel reviews and validates win patterns or calibrates model weights, they score using:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Repeatability** | 30% | Has this pattern produced wins in 3+ distinct deals? |
| **Recency** | 25% | Are the supporting deals from the last 12 months? |
| **Defensibility** | 20% | Can competitors easily neutralize this positioning? |
| **Proof Point Availability** | 15% | Do we have referenceable customers and data to support it? |
| **Execution Simplicity** | 10% | Can an average rep execute this strategy without heroics? |

**Scoring scale**: 1-5 per criterion, weighted. Patterns scoring below 3.0 weighted average are flagged for review. Below 2.5 are not entered into the active library.

---

## RISK MANAGEMENT

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Insufficient historical data for new competitors/segments** | High (early stages) | Medium | Expert Panel provides manual recommendations; flag "Insufficient Data" clearly |
| **Overfitting to historical patterns that no longer hold** | Medium | High | 180-day recency half-life decay; quarterly Expert Panel review; pattern retirement process |
| **Rep over-reliance on recommendations ("just tell me what to do")** | Medium | Medium | Brief explicitly states "Recommendation, not prescription — adapt to your buyer's context" |
| **Selection bias in measurement (better reps use the tool more)** | High | Medium | Propensity score matching; control for rep tenure and historical win rate |
| **Stale proof points damage credibility** | Medium | High | 18-month auto-expiry; quarterly verification sweep |
| **Competitor shifts strategy faster than model updates** | Low | High | Real-time battlecard updates feed into counter-move trees between quarterly calibrations |

---

## APPENDIX A: GLOSSARY

| Term | Definition |
|------|-----------|
| **Deal DNA Vector** | The multi-dimensional attribute set that characterizes a deal for pattern matching |
| **DStA** | Deal Strategy Algorithm — the core recommendation engine |
| **Win Pattern** | A validated, repeatable positioning strategy that has produced wins in 3+ similar deals |
| **Counter-Move** | A predicted competitor response to a recommended positioning strategy |
| **Pre-Call Intelligence Package** | The 1-2 page deal strategy brief delivered to reps |
| **Proof Point** | A verified customer reference, case study, or ROI data point matched to a deal profile |
| **Monte Carlo Simulation** | Probabilistic modeling that simulates 1,000+ deal outcomes to estimate win probability |
| **Expert Panel** | Standing review body (top rep, SE lead, SC lead, Mike, Sales Ops) that calibrates the engine quarterly |
| **Pattern Retirement** | Process of removing stale or underperforming win patterns from the active library |
| **Propensity Score Matching** | Statistical technique to control for selection bias when comparing recommended vs. non-recommended deals |

---

*This SOP is the connective tissue between intelligence (knowing what happened) and strategy (deciding what to do next). It converts M&CI from a reporting function into a deal strategy function.*

*Document generated: 2026-03-25 | Next review: Q2 2026 Expert Panel inaugural session*
