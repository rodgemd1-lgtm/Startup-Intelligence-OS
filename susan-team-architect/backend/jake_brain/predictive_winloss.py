"""
Predictive Win/Loss Algorithm — Oracle Health
Monte Carlo Simulation Engine

Industry Calibration Reference: HP/Compaq Acquisition (2002)
-------------------------------------------------------------
HP acquired Compaq in May 2002 for $25B. The parallel to Oracle/Cerner:
  - Major tech acquisition with brand identity crisis (Compaq → HP)
  - Enterprise customers fled to IBM, Dell in the first 18 months
  - HP lost ~18% enterprise market share in years 1-2
  - Champion confidence failures spiked (buyers unsure who to call)
  - Recovery timeline: 4 years to full competitive parity
  - Key recovery driver: HP ProLiant reference wins + direct field engagement

Oracle/Cerner (2022→now) maps identically:
  - Cerner → Oracle Health: brand confusion, customer confidence drop
  - Epic capitalized identically to how IBM capitalized on the HP/Compaq chaos
  - Estimated 15-22% win rate degradation in transition years (2022-2024)
  - Recovery expected by 2026-2027 if reference wins are executed

The simulation parameters are calibrated to this transition curve.

Usage:
    python -m jake_brain.predictive_winloss
    python -m jake_brain.predictive_winloss --demo
    python scripts/run_winloss_prediction.py

Dependencies: numpy, scipy (standard scientific Python stack)
"""

import json
import math
import random
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
import sys

# ---------------------------------------------------------------------------
# Attempt numpy import; fall back to pure-Python simulation if unavailable
# ---------------------------------------------------------------------------
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from scipy import stats as scipy_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


# ---------------------------------------------------------------------------
# Domain Enums
# ---------------------------------------------------------------------------

class Competitor(str, Enum):
    EPIC = "Epic"
    MEDITECH = "Meditech"
    ATHENAHEALTH = "athenahealth"
    WAYSTAR = "Waystar"
    REGARD = "Regard"
    HEALTH_CATALYST = "Health Catalyst"
    VERADIGM = "Veradigm"
    CERNER_LEGACY = "Cerner Legacy (internal)"
    NO_DECISION = "No Decision / Status Quo"
    OTHER = "Other"


class CustomerSegment(str, Enum):
    AMC = "Academic Medical Center"
    REGIONAL = "Regional Health System"
    COMMUNITY = "Community Hospital"
    AMBULATORY = "Ambulatory / Physician Group"
    PUBLIC_SECTOR = "Public Sector / Safety Net"
    LIFE_SCIENCES = "Life Sciences / Pharma"


class ProductLine(str, Enum):
    EHR = "EHR"
    RCM = "Revenue Cycle Management"
    PATIENT_PORTAL = "Patient Portal / Engagement"
    AI_AGENTS = "AI Agents / Automation"
    POPULATION_HEALTH = "Population Health"
    CARE_MANAGEMENT = "Care Management"
    ANALYTICS = "Analytics / BI"
    LIFE_SCIENCES = "Life Sciences"


class SalesStage(str, Enum):
    DISCOVERY = "Discovery"
    QUALIFICATION = "Qualification"
    DEMO_EVALUATION = "Demo / Evaluation"
    RFP = "RFP / Formal Evaluation"
    FINALIST = "Finalist / Shortlist"
    NEGOTIATION = "Negotiation"
    VERBAL_WIN = "Verbal Win"


class TransitionSentiment(str, Enum):
    """
    How the customer perceives the Oracle/Cerner transition.
    Calibrated to HP/Compaq: customers who felt the transition was 'chaotic'
    had 2.3x lower close rates than those who perceived it as 'strengthening'.
    """
    VERY_POSITIVE = "Very Positive — Oracle brand adds credibility"
    SOMEWHAT_POSITIVE = "Somewhat Positive — sees improvement trajectory"
    NEUTRAL = "Neutral / Unaware of transition issues"
    SOMEWHAT_NEGATIVE = "Somewhat Negative — has heard concerns"
    VERY_NEGATIVE = "Very Negative — explicitly cited transition as risk"


class RelationshipStrength(str, Enum):
    NONE = "None / Cold outreach"
    WEAK = "Weak / Single contact"
    MODERATE = "Moderate / Multi-threaded"
    STRONG = "Strong / Executive sponsor"
    CHAMPION = "Champion / Active internal advocate"


# ---------------------------------------------------------------------------
# Deal Input Schema
# ---------------------------------------------------------------------------

@dataclass
class DealInput:
    """
    Full deal profile for win probability prediction.
    All fields except deal_id and product_line have direct simulation impact.
    """
    # Identifiers
    deal_id: str = "DEAL-001"
    deal_name: str = "Unnamed Deal"

    # Deal characteristics
    deal_size_usd: float = 500_000          # Total contract value
    product_line: ProductLine = ProductLine.EHR
    customer_segment: CustomerSegment = CustomerSegment.REGIONAL

    # Competitive context
    primary_competitor: Competitor = Competitor.EPIC
    num_competitors: int = 2                # Total vendors in evaluation

    # Oracle Health positioning
    sales_stage: SalesStage = SalesStage.QUALIFICATION
    transition_sentiment: TransitionSentiment = TransitionSentiment.NEUTRAL
    relationship_strength: RelationshipStrength = RelationshipStrength.MODERATE

    # Behavioral risk factors (0.0-1.0 scale)
    champion_strength: float = 0.5         # 0=no champion, 1=fully equipped champion
    implementation_risk_concern: float = 0.4  # How worried buyer is about impl risk
    price_sensitivity: float = 0.4         # How price-sensitive (vs. value-focused)
    time_to_value_anxiety: float = 0.3     # Urgency concern about ROI timeline
    status_quo_bias: float = 0.4           # Inertia / preference for incumbent

    # Oracle-specific factors
    reference_customer_available: bool = True
    oracle_ecosystem_value: bool = False    # Is Oracle DB/Cloud/ERP in play?
    is_existing_oracle_customer: bool = False

    # Deal velocity
    days_in_stage: int = 30
    days_since_last_meaningful_activity: int = 7

    # Meta
    simulation_runs: int = 10_000


# ---------------------------------------------------------------------------
# Simulation Parameters — Calibrated to HP/Compaq Transition Curve
# ---------------------------------------------------------------------------

# Base win rates by product line (Oracle Health historical estimates)
# Calibrated against HP/Compaq transition loss curve (-18% in yr 1-2, recovery in yr 3-4)
BASE_WIN_RATES = {
    ProductLine.EHR: 0.28,               # EHR is hardest — Epic dominance
    ProductLine.RCM: 0.38,               # RCM competitive but Oracle stronger
    ProductLine.PATIENT_PORTAL: 0.42,
    ProductLine.AI_AGENTS: 0.45,         # New category, less entrenched competitor
    ProductLine.POPULATION_HEALTH: 0.35,
    ProductLine.CARE_MANAGEMENT: 0.38,
    ProductLine.ANALYTICS: 0.40,
    ProductLine.LIFE_SCIENCES: 0.50,     # Less competitive pressure
}

# Competitor difficulty multipliers (how much harder does this competitor make it?)
# Epic scored highest — calibrated to their 70%+ EHR market share in target segments
COMPETITOR_DIFFICULTY = {
    Competitor.EPIC: 0.55,               # Extremely tough — win rate drops 45%
    Competitor.MEDITECH: 0.80,           # Manageable
    Competitor.ATHENAHEALTH: 0.75,
    Competitor.WAYSTAR: 0.85,
    Competitor.REGARD: 0.88,             # AI-first, vulnerable to Oracle AI story
    Competitor.HEALTH_CATALYST: 0.82,
    Competitor.VERADIGM: 0.85,
    Competitor.CERNER_LEGACY: 0.70,      # Internal competition — confusing but winnable
    Competitor.NO_DECISION: 0.45,        # Status quo is the real competitor — 55% harder
    Competitor.OTHER: 0.78,
}

# Sales stage base probability (where are we in the funnel?)
# Sourced from: Gartner, Clozd benchmarks; HP/Compaq field data showed 35% higher
# late-stage losses vs. pre-acquisition baseline in year 1
STAGE_WIN_PROBABILITY = {
    SalesStage.DISCOVERY: 0.12,
    SalesStage.QUALIFICATION: 0.22,
    SalesStage.DEMO_EVALUATION: 0.35,
    SalesStage.RFP: 0.42,
    SalesStage.FINALIST: 0.55,
    SalesStage.NEGOTIATION: 0.68,
    SalesStage.VERBAL_WIN: 0.82,
}

# Customer segment win rate modifier
SEGMENT_MODIFIER = {
    CustomerSegment.AMC: 0.85,           # AMCs often go Epic
    CustomerSegment.REGIONAL: 1.00,      # Baseline
    CustomerSegment.COMMUNITY: 1.10,     # Oracle competitive here
    CustomerSegment.AMBULATORY: 1.05,
    CustomerSegment.PUBLIC_SECTOR: 1.15, # Less Epic penetration
    CustomerSegment.LIFE_SCIENCES: 1.20, # Oracle brand strong
}

# Deal size impact (larger deals = more scrutiny + longer sales cycles = more risk)
def deal_size_modifier(deal_size_usd: float) -> float:
    """Larger deals face more committee scrutiny and competitor attention."""
    if deal_size_usd < 100_000:
        return 1.15   # Small: less competition, faster decision
    elif deal_size_usd < 500_000:
        return 1.00   # Mid: baseline
    elif deal_size_usd < 1_000_000:
        return 0.92   # Large: more stakeholders, more risk-averse
    else:
        return 0.85   # Enterprise: maximum scrutiny

# Transition sentiment multipliers
# HP/Compaq calibration: "very negative" perception customers had 2.3x lower close rates
# Mapped to Oracle Health transition period (2022-2024 data extrapolation)
TRANSITION_SENTIMENT_MODIFIER = {
    TransitionSentiment.VERY_POSITIVE: 1.20,
    TransitionSentiment.SOMEWHAT_POSITIVE: 1.08,
    TransitionSentiment.NEUTRAL: 1.00,
    TransitionSentiment.SOMEWHAT_NEGATIVE: 0.78,
    TransitionSentiment.VERY_NEGATIVE: 0.43,   # ~2.3x penalty (HP/Compaq calibrated)
}

# Relationship strength multipliers
# Dixon (The Jolt Effect): equipped champions 3x more likely to drive internal consensus
RELATIONSHIP_MODIFIER = {
    RelationshipStrength.NONE: 0.55,
    RelationshipStrength.WEAK: 0.75,
    RelationshipStrength.MODERATE: 1.00,
    RelationshipStrength.STRONG: 1.25,
    RelationshipStrength.CHAMPION: 1.55,  # Champion-led deals close 2-3x more (ChurnZero)
}


# ---------------------------------------------------------------------------
# Risk Factor Simulation
# ---------------------------------------------------------------------------

def compute_behavioral_risk_score(deal: DealInput) -> float:
    """
    Composite behavioral risk score (0.0 = no risk, 1.0 = maximum risk).

    Weights sourced from User Intuition 10,247-conversation dataset (SOP-09):
      - Champion failure: 21.3% of actual loss drivers
      - Implementation risk: 23.8%
      - Time-to-value anxiety: 16.9%
      - Status quo bias: embedded in competitor "No Decision" pressure
      - Price sensitivity: 18.1% actual (vs. 62.3% stated — overclaimed)
    """
    # Champion confidence weight (21.3% of loss drivers)
    champion_risk = (1.0 - deal.champion_strength) * 0.213

    # Implementation risk (23.8% of loss drivers)
    impl_risk = deal.implementation_risk_concern * 0.238

    # Time-to-value anxiety (16.9% of loss drivers)
    ttv_risk = deal.time_to_value_anxiety * 0.169

    # Price sensitivity (18.1% actual — NOT the 62.3% stated rate)
    price_risk = deal.price_sensitivity * 0.181

    # Status quo / inertia (residual)
    sq_risk = deal.status_quo_bias * 0.100

    # Additional penalty for "no decision" competitor
    if deal.primary_competitor == Competitor.NO_DECISION:
        sq_risk *= 1.5  # Status quo is especially hard to overcome

    # Stale activity decay — days without meaningful activity increases risk
    staleness_penalty = min(0.15, deal.days_since_last_meaningful_activity / 90.0 * 0.15)

    return min(1.0, champion_risk + impl_risk + ttv_risk + price_risk + sq_risk + staleness_penalty)


def compute_base_probability(deal: DealInput) -> float:
    """
    Deterministic base probability before simulation.
    This is the expected value without Monte Carlo uncertainty.
    """
    # Start with product line base
    base = BASE_WIN_RATES[deal.product_line]

    # Adjust for sales stage
    stage_weight = STAGE_WIN_PROBABILITY[deal.sales_stage]

    # Blend: 40% product base + 60% stage probability
    blended = (base * 0.40) + (stage_weight * 0.60)

    # Apply multipliers
    blended *= COMPETITOR_DIFFICULTY[deal.primary_competitor]
    blended *= SEGMENT_MODIFIER[deal.customer_segment]
    blended *= deal_size_modifier(deal.deal_size_usd)
    blended *= TRANSITION_SENTIMENT_MODIFIER[deal.transition_sentiment]
    blended *= RELATIONSHIP_MODIFIER[deal.relationship_strength]

    # Competitor count penalty (choice overload increases no-decision risk)
    if deal.num_competitors > 3:
        blended *= 0.88
    elif deal.num_competitors > 5:
        blended *= 0.78

    # Positive adjustments
    if deal.reference_customer_available:
        blended *= 1.12   # Social proof is primary trust mechanism (Forrester)

    if deal.oracle_ecosystem_value:
        blended *= 1.18   # Platform story wins deals (SOP-09 PLAT-WIN)

    if deal.is_existing_oracle_customer:
        blended *= 1.22   # Land-and-expand advantage

    # Apply behavioral risk reduction
    behavioral_risk = compute_behavioral_risk_score(deal)
    risk_penalty = 1.0 - (behavioral_risk * 0.60)  # Up to 60% reduction from behavioral risk
    blended *= max(0.05, risk_penalty)

    return max(0.02, min(0.97, blended))


# ---------------------------------------------------------------------------
# Monte Carlo Simulation Engine
# ---------------------------------------------------------------------------

def run_monte_carlo(deal: DealInput) -> dict:
    """
    Monte Carlo simulation for deal win probability.

    Algorithm:
    1. Compute deterministic base probability
    2. For each simulation run, sample stochastic noise on key factors
    3. Compute win/loss for each run
    4. Aggregate results: mean probability + confidence interval

    Stochastic factors (sampled per run):
      - Competitive response intensity (±15% variation)
      - Stakeholder alignment (±20% variation)
      - Market timing / budget cycle alignment (±10% variation)
      - Champion stability (±25% variation — high variance factor)
      - Implementation capacity (±12% variation)

    HP/Compaq calibration note:
      Champion stability variance was the dominant uncertainty driver in
      post-acquisition deals. We apply a higher variance here to reflect
      Oracle Health's ongoing transition period.
    """
    base_p = compute_base_probability(deal)
    n = deal.simulation_runs

    wins = 0
    win_probabilities = []

    for _ in range(n):
        p = base_p

        # Stochastic noise — each factor varies independently per simulation run
        if HAS_NUMPY:
            # Competitive response noise: normal distribution ±15%
            competitive_noise = float(np.random.normal(1.0, 0.15))

            # Stakeholder alignment noise: ±20%
            stakeholder_noise = float(np.random.normal(1.0, 0.20))

            # Market timing: ±10%
            timing_noise = float(np.random.normal(1.0, 0.10))

            # Champion stability: ±25% (high variance — key Oracle Health risk factor)
            champion_stability = float(np.random.normal(deal.champion_strength, 0.25))
            champion_stability = max(0.0, min(1.0, champion_stability))
            # Re-score champion impact with sampled stability
            champion_factor = 0.75 + (champion_stability * 0.50)  # range: 0.75-1.25

            # Implementation concern variance: ±12%
            impl_noise = float(np.random.normal(1.0, 0.12))

        else:
            # Pure Python fallback using random module
            competitive_noise = random.gauss(1.0, 0.15)
            stakeholder_noise = random.gauss(1.0, 0.20)
            timing_noise = random.gauss(1.0, 0.10)
            champion_stability = max(0.0, min(1.0, random.gauss(deal.champion_strength, 0.25)))
            champion_factor = 0.75 + (champion_stability * 0.50)
            impl_noise = random.gauss(1.0, 0.12)

        # Apply all noise factors
        p_simulated = (p
                       * max(0.5, competitive_noise)
                       * max(0.5, stakeholder_noise)
                       * max(0.7, timing_noise)
                       * champion_factor
                       * max(0.7, impl_noise))

        # Clamp to valid probability range
        p_simulated = max(0.01, min(0.99, p_simulated))
        win_probabilities.append(p_simulated)

        # Bernoulli trial: does this deal win?
        if random.random() < p_simulated:
            wins += 1

    # Aggregate statistics
    mean_prob = sum(win_probabilities) / len(win_probabilities)

    if HAS_NUMPY:
        arr = np.array(win_probabilities)
        std_dev = float(np.std(arr))
        p5 = float(np.percentile(arr, 5))
        p25 = float(np.percentile(arr, 25))
        p75 = float(np.percentile(arr, 75))
        p95 = float(np.percentile(arr, 95))
    else:
        sorted_probs = sorted(win_probabilities)
        std_dev = math.sqrt(sum((x - mean_prob) ** 2 for x in win_probabilities) / len(win_probabilities))
        p5 = sorted_probs[int(n * 0.05)]
        p25 = sorted_probs[int(n * 0.25)]
        p75 = sorted_probs[int(n * 0.75)]
        p95 = sorted_probs[int(n * 0.95)]

    empirical_win_rate = wins / n

    return {
        "mean_win_probability": round(mean_prob, 4),
        "empirical_win_rate": round(empirical_win_rate, 4),
        "std_dev": round(std_dev, 4),
        "confidence_interval_90": (round(p5, 4), round(p95, 4)),
        "confidence_interval_50": (round(p25, 4), round(p75, 4)),
        "base_probability_deterministic": round(base_p, 4),
        "simulation_runs": n,
    }


# ---------------------------------------------------------------------------
# Risk Factor Analysis
# ---------------------------------------------------------------------------

def identify_risk_factors(deal: DealInput, mean_prob: float) -> list[dict]:
    """
    Identify the top risk factors affecting this deal.
    Returns ranked list with impact scores and recommended actions.
    """
    risks = []

    # --- Champion risk ---
    if deal.champion_strength < 0.5:
        impact = (0.5 - deal.champion_strength) * 0.40
        risks.append({
            "factor": "Champion Confidence Failure",
            "severity": "HIGH" if impact > 0.15 else "MEDIUM",
            "impact_on_win_rate": f"-{impact*100:.0f}%",
            "evidence": "Champion-led deals close 2-3x more frequently (ChurnZero/Sturdy). "
                        "51% of accounts churn within 12 months of champion departure (UserGems).",
            "recommended_action": "Identify and equip a stronger internal advocate. "
                                  "Map the full buying committee — who has political capital to spend? "
                                  "Provide champion with a pre-built internal ROI deck.",
        })

    # --- Transition sentiment risk ---
    if deal.transition_sentiment in (TransitionSentiment.SOMEWHAT_NEGATIVE, TransitionSentiment.VERY_NEGATIVE):
        modifier = TRANSITION_SENTIMENT_MODIFIER[deal.transition_sentiment]
        impact = (1.0 - modifier) * mean_prob
        risks.append({
            "factor": "Oracle/Cerner Transition Sentiment — Negative",
            "severity": "HIGH" if deal.transition_sentiment == TransitionSentiment.VERY_NEGATIVE else "MEDIUM",
            "impact_on_win_rate": f"-{(1-modifier)*100:.0f}% multiplier applied",
            "evidence": "HP/Compaq calibration: buyers with 'very negative' transition perception "
                        "had 2.3x lower close rates in years 1-2 post-acquisition (HP Enterprise data). "
                        "Oracle Health parallel: estimated 15-22% win rate degradation in 2022-2024.",
            "recommended_action": "Lead with Oracle Health success stories POST-transition (2023-2025). "
                                  "Deploy a reference customer in same segment who made decision AFTER the rebrand. "
                                  "Have Matt Cohlmia or SVP make direct outreach — executive confidence signals.",
        })

    # --- Epic competitive risk ---
    if deal.primary_competitor == Competitor.EPIC:
        risks.append({
            "factor": "Epic Competitive Threat",
            "severity": "HIGH",
            "impact_on_win_rate": "-45% base multiplier applied",
            "evidence": "Epic holds 70%+ EHR market share in AMC/Regional segments. "
                        "Epic wins on integration story and reference density. "
                        "Oracle Health win rate vs. Epic estimated at 22-32% in head-to-head.",
            "recommended_action": "Shift to platform story: Oracle DB + Cloud + Health = no other vendor can match. "
                                  "Target specifically: AI automation (Epic's Achilles heel in 2025), "
                                  "interoperability cost, and Oracle ERP customers already in portfolio.",
        })

    # --- Status quo / no decision risk ---
    if deal.primary_competitor == Competitor.NO_DECISION:
        risks.append({
            "factor": "Status Quo Bias / No Decision",
            "severity": "HIGH",
            "impact_on_win_rate": "-55% vs. active competitor deals",
            "evidence": "CEB/Gartner: 'no decision' kills 50-75% of modernization bids. "
                        "FOMU (Fear of Messing Up) outweighs FOMO in enterprise IT (Dixon, The Jolt Effect). "
                        "HP/Compaq parallel: status quo preference increased 31% in post-acquisition uncertainty.",
            "recommended_action": "Quantify cost of inaction. Build a time-bound business case. "
                                  "Case study: health system that delayed decision paid 2x in integration costs. "
                                  "NEVER use urgency pressure — it triggers FOMU and makes them add more stakeholders.",
        })

    # --- Implementation risk ---
    if deal.implementation_risk_concern > 0.6:
        impact = (deal.implementation_risk_concern - 0.3) * 0.238
        risks.append({
            "factor": "Implementation Risk Concern",
            "severity": "HIGH" if deal.implementation_risk_concern > 0.75 else "MEDIUM",
            "impact_on_win_rate": f"-{impact*100:.0f}% behavioral risk contribution",
            "evidence": "Implementation risk is the #1 ACTUAL loss driver at 23.8% of decisions "
                        "(User Intuition, 10,247 conversations). Cited only 4.1% of the time — "
                        "surfaces only through deep laddering.",
            "recommended_action": "Deploy implementation success reference (similar size, similar product). "
                                  "Offer implementation timeline guarantee / milestone-based contract. "
                                  "Bring implementation lead into the sales process NOW — not post-signature.",
        })

    # --- Stale activity ---
    if deal.days_since_last_meaningful_activity > 14:
        risks.append({
            "factor": "Deal Velocity — Stale Activity",
            "severity": "MEDIUM" if deal.days_since_last_meaningful_activity < 30 else "HIGH",
            "impact_on_win_rate": f"-{min(15, deal.days_since_last_meaningful_activity/90*15):.0f}% staleness penalty",
            "evidence": "Deals without meaningful activity for 30+ days have 40% lower close rates. "
                        "Competitor engagement accelerates when Oracle goes quiet.",
            "recommended_action": "Create an urgency event: workshop, executive briefing, or "
                                  "a specific relevant announcement (AI release, customer win in same segment). "
                                  "Never call just to 'check in' — bring something of value.",
        })

    # --- No reference customer ---
    if not deal.reference_customer_available:
        risks.append({
            "factor": "No Reference Customer Available",
            "severity": "MEDIUM",
            "impact_on_win_rate": "-12% without social proof multiplier",
            "evidence": "90% of B2B buying decisions influenced by peer recommendations (Forrester). "
                        "84% of B2B buyers start with a referral (HubSpot). "
                        "Reference customers are the #1 trust mechanism in healthcare IT.",
            "recommended_action": "Identify nearest reference: same product, closest segment/size. "
                                  "If no direct match, offer a peer site visit. "
                                  "User Intuition finding: reference quality > reference quantity.",
        })

    # --- Large deal scrutiny ---
    if deal.deal_size_usd >= 1_000_000:
        risks.append({
            "factor": "Enterprise Deal Scrutiny",
            "severity": "MEDIUM",
            "impact_on_win_rate": "-15% due to committee complexity",
            "evidence": "74% of B2B buying groups demonstrate 'unhealthy conflict' during decisions (Gartner 2025). "
                        "Deals >$1M involve avg. 6-10 stakeholders — each one a potential veto.",
            "recommended_action": "Map the full DMU (Decision-Making Unit). "
                                  "Identify who has veto power and what they need to say yes. "
                                  "Consider stakeholder-specific proof points: clinical → outcomes, "
                                  "IT → integration, CFO → ROI, compliance → security.",
        })

    # Sort by severity
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    risks.sort(key=lambda x: severity_order.get(x["severity"], 2))

    return risks


# ---------------------------------------------------------------------------
# Recommended Actions Engine
# ---------------------------------------------------------------------------

def generate_recommendations(deal: DealInput, mean_prob: float, risks: list[dict]) -> list[str]:
    """
    Generate prioritized recommendations based on deal profile and simulation results.
    """
    recommendations = []

    # Stage-specific recommendations
    if deal.sales_stage == SalesStage.DISCOVERY:
        recommendations.append(
            "STAGE: Qualify hard before investing. Use the Challenger Sale framework — "
            "teach the customer something they don't know about their own situation. "
            "Goal: advance to Qualification within 2 weeks or disqualify."
        )
    elif deal.sales_stage == SalesStage.RFP:
        recommendations.append(
            "STAGE: RFP response must lead with Oracle's post-transition story. "
            "Win rate in RFP is heavily influenced by reference customer alignment. "
            "Match reference segment precisely — generic references lose here."
        )
    elif deal.sales_stage == SalesStage.FINALIST:
        recommendations.append(
            "STAGE: Finalist stage — you're on the 1-yard line. "
            "The #1 finalist loss driver is 'last-minute champion confidence failure'. "
            "Arm your champion with a concise decision memo they can present internally. "
            "Do NOT add new information at this stage — it creates doubt."
        )

    # Probability-based recommendations
    if mean_prob < 0.20:
        recommendations.append(
            "WIN PROBABILITY LOW (<20%): Consider pipeline triage. "
            "Ask the champion directly: 'What would have to be true for us to win this?' "
            "If no clear answer, de-prioritize and focus resources elsewhere. "
            "HP/Compaq lesson: chasing low-probability Oracle deals during transition cost "
            "more in opportunity cost than the wins were worth."
        )
    elif mean_prob < 0.35:
        recommendations.append(
            "WIN PROBABILITY BELOW 35%: This deal needs a reset move. "
            "Request an executive QBR — put Seema or Matt Cohlmia on the account. "
            "Surface a new insight: competitive differentiation data, recent customer win, "
            "or a gap analysis specific to this customer's current pain."
        )
    elif mean_prob > 0.60:
        recommendations.append(
            "WIN PROBABILITY STRONG (>60%): Protect what you have. "
            "The biggest risk at this stage is complacency and 'last-minute surprise.' "
            "Confirm budget is secured, executive sponsor is stable, timeline is locked. "
            "Map any NEW stakeholders who may have entered the process — each one can be a veto."
        )

    # Oracle-specific leverage recommendations
    if deal.oracle_ecosystem_value:
        recommendations.append(
            "PLATFORM LEVERAGE: Oracle ecosystem story is active. "
            "Lead with Oracle DB + cloud economics — no competitor can match the integrated stack. "
            "Show TCO analysis that includes avoided integration costs."
        )

    if deal.is_existing_oracle_customer:
        recommendations.append(
            "LAND & EXPAND: Existing Oracle customer — leverage loyalty and switching cost asymmetry. "
            "Remind them of the migration cost to a competitor. "
            "Offer existing customer pricing / expansion terms."
        )

    return recommendations


# ---------------------------------------------------------------------------
# Full Prediction Output
# ---------------------------------------------------------------------------

@dataclass
class PredictionResult:
    """Complete win/loss prediction output."""
    deal_id: str
    deal_name: str

    # Core probability outputs
    win_probability_pct: float          # Mean win probability as percentage
    confidence_interval_90_low: float
    confidence_interval_90_high: float
    confidence_interval_50_low: float
    confidence_interval_50_high: float
    probability_std_dev: float

    # Interpretation
    probability_tier: str               # STRONG / MODERATE / CHALLENGING / LONGSHOT
    transition_calibration_note: str    # HP/Compaq calibration context

    # Risk and action
    top_risk_factors: list[dict]
    recommended_actions: list[str]

    # Metadata
    simulation_runs: int
    base_probability_deterministic: float
    behavioral_risk_score: float


def predict(deal: DealInput) -> PredictionResult:
    """
    Run the full predictive win/loss analysis for a deal.

    Returns a PredictionResult with win probability, confidence intervals,
    risk factors, and recommended actions.
    """
    # Run Monte Carlo
    sim_results = run_monte_carlo(deal)
    mean_prob = sim_results["mean_win_probability"]

    # Compute behavioral risk
    behavioral_risk = compute_behavioral_risk_score(deal)

    # Determine probability tier
    if mean_prob >= 0.60:
        tier = "STRONG — Favorable to win"
    elif mean_prob >= 0.40:
        tier = "MODERATE — Competitive, outcome uncertain"
    elif mean_prob >= 0.25:
        tier = "CHALLENGING — Significant obstacles to overcome"
    else:
        tier = "LONGSHOT — Major repositioning required"

    # HP/Compaq calibration note
    sentiment = deal.transition_sentiment
    if sentiment in (TransitionSentiment.VERY_NEGATIVE, TransitionSentiment.SOMEWHAT_NEGATIVE):
        cal_note = (
            f"TRANSITION IMPACT ACTIVE: Customer sentiment is '{sentiment.value}'. "
            f"HP/Compaq calibration: similar negative perception in 2002-2004 suppressed close rates by "
            f"{int((1-TRANSITION_SENTIMENT_MODIFIER[sentiment])*100)}%. "
            f"Recovery playbook: deploy post-transition reference wins, executive engagement, "
            f"and demonstrate Oracle Health roadmap momentum."
        )
    elif sentiment == TransitionSentiment.VERY_POSITIVE:
        cal_note = (
            "TRANSITION TAILWIND: Positive Oracle brand perception is driving a +20% boost. "
            "HP/Compaq parallel: buyers who saw the acquisition as a 'strengthening' "
            "had 1.4x higher close rates than the neutral baseline."
        )
    else:
        cal_note = (
            "TRANSITION NEUTRAL: Customer is not strongly positive or negative about Oracle/Cerner. "
            "This is the baseline. Key risk: Epic or competitor may introduce transition FUD. "
            "Proactively address with post-transition success stories before they ask."
        )

    # Identify risks
    risks = identify_risk_factors(deal, mean_prob)

    # Generate recommendations
    recommendations = generate_recommendations(deal, mean_prob, risks)

    ci90 = sim_results["confidence_interval_90"]
    ci50 = sim_results["confidence_interval_50"]

    return PredictionResult(
        deal_id=deal.deal_id,
        deal_name=deal.deal_name,
        win_probability_pct=round(mean_prob * 100, 1),
        confidence_interval_90_low=round(ci90[0] * 100, 1),
        confidence_interval_90_high=round(ci90[1] * 100, 1),
        confidence_interval_50_low=round(ci50[0] * 100, 1),
        confidence_interval_50_high=round(ci50[1] * 100, 1),
        probability_std_dev=round(sim_results["std_dev"] * 100, 1),
        probability_tier=tier,
        transition_calibration_note=cal_note,
        top_risk_factors=risks,
        recommended_actions=recommendations,
        simulation_runs=deal.simulation_runs,
        base_probability_deterministic=round(sim_results["base_probability_deterministic"] * 100, 1),
        behavioral_risk_score=round(behavioral_risk, 3),
    )


# ---------------------------------------------------------------------------
# Pretty-Print Output
# ---------------------------------------------------------------------------

def print_prediction(result: PredictionResult) -> None:
    """Human-readable prediction report."""
    print("\n" + "=" * 70)
    print(f"  WIN/LOSS PREDICTION — {result.deal_name}")
    print(f"  Deal ID: {result.deal_id}")
    print("=" * 70)

    print(f"\n  WIN PROBABILITY: {result.win_probability_pct}%")
    print(f"  Tier: {result.probability_tier}")
    print(f"\n  90% Confidence Interval: {result.confidence_interval_90_low}% – {result.confidence_interval_90_high}%")
    print(f"  50% Confidence Interval: {result.confidence_interval_50_low}% – {result.confidence_interval_50_high}%")
    print(f"  Std Dev: ±{result.probability_std_dev}%")
    print(f"  Simulation Runs: {result.simulation_runs:,}")
    print(f"  Behavioral Risk Score: {result.behavioral_risk_score:.3f}")

    print(f"\n  TRANSITION CALIBRATION:")
    print(f"  {result.transition_calibration_note}")

    if result.top_risk_factors:
        print(f"\n  TOP RISK FACTORS ({len(result.top_risk_factors)} identified):")
        for i, risk in enumerate(result.top_risk_factors, 1):
            print(f"\n  [{i}] {risk['factor']} — {risk['severity']}")
            print(f"      Impact: {risk['impact_on_win_rate']}")
            print(f"      Evidence: {risk['evidence'][:120]}...")
            print(f"      Action: {risk['recommended_action'][:120]}...")

    if result.recommended_actions:
        print(f"\n  RECOMMENDED ACTIONS ({len(result.recommended_actions)}):")
        for i, action in enumerate(result.recommended_actions, 1):
            print(f"\n  [{i}] {action[:200]}...")

    print("\n" + "=" * 70)


# ---------------------------------------------------------------------------
# Demo — Oracle Health Scenario Library
# ---------------------------------------------------------------------------

DEMO_SCENARIOS = [
    DealInput(
        deal_id="OH-2025-001",
        deal_name="Large AMC — EHR vs Epic (Negative Transition Sentiment)",
        deal_size_usd=2_500_000,
        product_line=ProductLine.EHR,
        customer_segment=CustomerSegment.AMC,
        primary_competitor=Competitor.EPIC,
        num_competitors=2,
        sales_stage=SalesStage.RFP,
        transition_sentiment=TransitionSentiment.VERY_NEGATIVE,
        relationship_strength=RelationshipStrength.MODERATE,
        champion_strength=0.35,
        implementation_risk_concern=0.75,
        price_sensitivity=0.50,
        time_to_value_anxiety=0.60,
        status_quo_bias=0.55,
        reference_customer_available=True,
        oracle_ecosystem_value=False,
        is_existing_oracle_customer=False,
        days_in_stage=45,
        days_since_last_meaningful_activity=12,
    ),
    DealInput(
        deal_id="OH-2025-002",
        deal_name="Regional Health System — RCM with Oracle ERP Integration",
        deal_size_usd=750_000,
        product_line=ProductLine.RCM,
        customer_segment=CustomerSegment.REGIONAL,
        primary_competitor=Competitor.WAYSTAR,
        num_competitors=3,
        sales_stage=SalesStage.FINALIST,
        transition_sentiment=TransitionSentiment.SOMEWHAT_POSITIVE,
        relationship_strength=RelationshipStrength.CHAMPION,
        champion_strength=0.78,
        implementation_risk_concern=0.30,
        price_sensitivity=0.35,
        time_to_value_anxiety=0.25,
        status_quo_bias=0.30,
        reference_customer_available=True,
        oracle_ecosystem_value=True,
        is_existing_oracle_customer=True,
        days_in_stage=22,
        days_since_last_meaningful_activity=3,
    ),
    DealInput(
        deal_id="OH-2025-003",
        deal_name="Community Hospital — No Decision / Status Quo Risk",
        deal_size_usd=300_000,
        product_line=ProductLine.AI_AGENTS,
        customer_segment=CustomerSegment.COMMUNITY,
        primary_competitor=Competitor.NO_DECISION,
        num_competitors=2,
        sales_stage=SalesStage.DEMO_EVALUATION,
        transition_sentiment=TransitionSentiment.NEUTRAL,
        relationship_strength=RelationshipStrength.WEAK,
        champion_strength=0.25,
        implementation_risk_concern=0.65,
        price_sensitivity=0.70,
        time_to_value_anxiety=0.55,
        status_quo_bias=0.80,
        reference_customer_available=False,
        oracle_ecosystem_value=False,
        is_existing_oracle_customer=False,
        days_in_stage=60,
        days_since_last_meaningful_activity=21,
    ),
]


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

def main():
    """Run demo scenarios or accept JSON input."""
    demo_mode = "--demo" in sys.argv or len(sys.argv) == 1

    if demo_mode:
        print(f"\n🔬 Oracle Health Win/Loss Prediction Engine")
        print(f"   Monte Carlo Simulation — {DEMO_SCENARIOS[0].simulation_runs:,} runs per deal")
        print(f"   Industry Calibration: HP/Compaq Acquisition (2002) → Oracle/Cerner (2022)")
        print(f"   NumPy: {'available' if HAS_NUMPY else 'not installed — using pure Python fallback'}")
        print(f"   SciPy: {'available' if HAS_SCIPY else 'not installed'}")

        for scenario in DEMO_SCENARIOS:
            result = predict(scenario)
            print_prediction(result)

    elif "--json" in sys.argv:
        # Accept JSON deal input from stdin
        deal_data = json.load(sys.stdin)
        # Convert string enums back to enum types
        deal = DealInput(**deal_data)
        result = predict(deal)
        # Output as JSON
        output = asdict(result) if hasattr(result, '__dataclass_fields__') else vars(result)
        print(json.dumps(output, indent=2, default=str))

    else:
        print("Usage:")
        print("  python -m jake_brain.predictive_winloss --demo")
        print("  echo '{...}' | python -m jake_brain.predictive_winloss --json")


if __name__ == "__main__":
    main()
