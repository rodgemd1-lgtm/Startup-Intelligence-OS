"""Persona archetypes grounded in NHANES/BRFSS population data.

Each persona defines a probability distribution over user characteristics
that feeds into the Monte Carlo simulator.
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field


@dataclass
class Persona:
    """A user persona with probabilistic attributes."""
    name: str
    description: str
    # Demographics
    age_range: tuple[int, int] = (25, 45)
    female_pct: float = 0.5
    # Health (NHANES-grounded)
    bmi_mean: float = 27.0
    bmi_std: float = 5.0
    activity_level: str = "lightly_active"  # sedentary, lightly_active, moderate, very_active
    # Behavioral
    tech_comfort: float = 0.7  # 0-1 scale
    price_sensitivity: float = 0.5  # 0=insensitive, 1=very sensitive
    motivation: str = "general_health"
    # Probabilities (calibrated to published benchmarks)
    p_complete_onboarding: float = 0.65
    p_activate_day1: float = 0.30
    p_retain_day7: float = 0.15
    p_retain_day30: float = 0.08
    p_retain_day90: float = 0.04
    p_convert_to_paid: float = 0.017  # RevenueCat industry average
    p_churn_monthly: float = 0.12  # industry average
    # Economics
    expected_arpu_monthly: float = 12.99
    # Population weight (how common is this persona in target market)
    market_share_pct: float = 10.0

    def sample_age(self) -> int:
        return random.randint(*self.age_range)

    def sample_bmi(self) -> float:
        return max(16.0, random.gauss(self.bmi_mean, self.bmi_std))

    def sample_is_female(self) -> bool:
        return random.random() < self.female_pct


# ── Persona Library ──────────────────────────────────────────────
# Calibrated using: NHANES population distributions, CDC BRFSS,
# Sensor Tower benchmarks, RevenueCat subscription data,
# Business of Apps retention curves, Fitbod/Noom/Strava metrics

PERSONAS: list[Persona] = [
    Persona(
        name="Fresh Starter",
        description="New to fitness, motivated by weight loss after a life event. "
                    "High initial enthusiasm but high churn risk. "
                    "NHANES: 42% of US adults are obese (BMI 30+), most common segment.",
        age_range=(28, 45),
        female_pct=0.62,
        bmi_mean=31.5,
        bmi_std=4.0,
        activity_level="sedentary",
        tech_comfort=0.6,
        price_sensitivity=0.6,
        motivation="weight_loss",
        p_complete_onboarding=0.55,
        p_activate_day1=0.25,
        p_retain_day7=0.12,
        p_retain_day30=0.05,
        p_retain_day90=0.02,
        p_convert_to_paid=0.015,
        p_churn_monthly=0.18,
        expected_arpu_monthly=9.99,
        market_share_pct=25.0,
    ),
    Persona(
        name="Returning Athlete",
        description="Used to be fit, getting back after injury/life change. "
                    "Knows what they want, impatient with bad UX. "
                    "Higher retention if app delivers progressive overload.",
        age_range=(30, 50),
        female_pct=0.45,
        bmi_mean=27.0,
        bmi_std=3.5,
        activity_level="lightly_active",
        tech_comfort=0.7,
        price_sensitivity=0.4,
        motivation="return_to_fitness",
        p_complete_onboarding=0.72,
        p_activate_day1=0.38,
        p_retain_day7=0.22,
        p_retain_day30=0.12,
        p_retain_day90=0.07,
        p_convert_to_paid=0.035,
        p_churn_monthly=0.10,
        expected_arpu_monthly=14.99,
        market_share_pct=15.0,
    ),
    Persona(
        name="Fitness Enthusiast",
        description="Already active, wants optimization. Tracks macros, cares about "
                    "progressive overload. Most likely to convert and retain. "
                    "NHANES: ~23% of adults meet both aerobic and strength guidelines.",
        age_range=(22, 38),
        female_pct=0.40,
        bmi_mean=24.5,
        bmi_std=2.5,
        activity_level="very_active",
        tech_comfort=0.85,
        price_sensitivity=0.3,
        motivation="performance",
        p_complete_onboarding=0.82,
        p_activate_day1=0.55,
        p_retain_day7=0.35,
        p_retain_day30=0.25,
        p_retain_day90=0.18,
        p_convert_to_paid=0.06,
        p_churn_monthly=0.05,
        expected_arpu_monthly=19.99,
        market_share_pct=12.0,
    ),
    Persona(
        name="Busy Professional",
        description="Time-constrained, wants efficient workouts. Will pay premium "
                    "for convenience but will churn if app wastes their time. "
                    "High ARPU, moderate retention.",
        age_range=(30, 50),
        female_pct=0.50,
        bmi_mean=26.0,
        bmi_std=3.0,
        activity_level="lightly_active",
        tech_comfort=0.80,
        price_sensitivity=0.2,
        motivation="time_efficiency",
        p_complete_onboarding=0.70,
        p_activate_day1=0.32,
        p_retain_day7=0.18,
        p_retain_day30=0.10,
        p_retain_day90=0.06,
        p_convert_to_paid=0.04,
        p_churn_monthly=0.08,
        expected_arpu_monthly=24.99,
        market_share_pct=18.0,
    ),
    Persona(
        name="Health-Conscious Senior",
        description="50+ focused on longevity, mobility, fall prevention. "
                    "Lower tech comfort but high commitment once activated. "
                    "NHANES: fastest growing fitness app demographic.",
        age_range=(50, 70),
        female_pct=0.55,
        bmi_mean=28.0,
        bmi_std=4.5,
        activity_level="lightly_active",
        tech_comfort=0.45,
        price_sensitivity=0.35,
        motivation="health_longevity",
        p_complete_onboarding=0.48,
        p_activate_day1=0.22,
        p_retain_day7=0.15,
        p_retain_day30=0.10,
        p_retain_day90=0.08,
        p_convert_to_paid=0.03,
        p_churn_monthly=0.06,
        expected_arpu_monthly=14.99,
        market_share_pct=10.0,
    ),
    Persona(
        name="Social Fitness Seeker",
        description="Motivated by community, accountability, and social proof. "
                    "Will stay if they find workout buddies, churn without social hooks. "
                    "Strava's core: 2.23% interaction rate vs Facebook's 0.15%.",
        age_range=(22, 35),
        female_pct=0.58,
        bmi_mean=25.0,
        bmi_std=3.0,
        activity_level="moderate",
        tech_comfort=0.85,
        price_sensitivity=0.5,
        motivation="social_accountability",
        p_complete_onboarding=0.68,
        p_activate_day1=0.35,
        p_retain_day7=0.20,
        p_retain_day30=0.12,
        p_retain_day90=0.08,
        p_convert_to_paid=0.025,
        p_churn_monthly=0.10,
        expected_arpu_monthly=12.99,
        market_share_pct=12.0,
    ),
    Persona(
        name="Data-Driven Optimizer",
        description="Quantified self enthusiast. Wants charts, trends, HRV, sleep scores. "
                    "Will export data, cross-reference with Apple Health. "
                    "Small but vocal — drives word-of-mouth and App Store reviews.",
        age_range=(25, 40),
        female_pct=0.35,
        bmi_mean=24.0,
        bmi_std=2.0,
        activity_level="very_active",
        tech_comfort=0.95,
        price_sensitivity=0.25,
        motivation="data_optimization",
        p_complete_onboarding=0.85,
        p_activate_day1=0.60,
        p_retain_day7=0.40,
        p_retain_day30=0.30,
        p_retain_day90=0.22,
        p_convert_to_paid=0.08,
        p_churn_monthly=0.04,
        expected_arpu_monthly=24.99,
        market_share_pct=8.0,
    ),
]


def sample_cohort(n: int, personas: list[Persona] | None = None) -> list[dict]:
    """Sample n users from persona distributions, weighted by market share."""
    personas = personas or PERSONAS
    weights = [p.market_share_pct for p in personas]
    total = sum(weights)
    weights = [w / total for w in weights]

    cohort = []
    for _ in range(n):
        persona = random.choices(personas, weights=weights, k=1)[0]
        user = {
            "persona": persona.name,
            "age": persona.sample_age(),
            "is_female": persona.sample_is_female(),
            "bmi": round(persona.sample_bmi(), 1),
            "activity_level": persona.activity_level,
            "tech_comfort": persona.tech_comfort,
            "price_sensitivity": persona.price_sensitivity,
            "motivation": persona.motivation,
            "p_complete_onboarding": persona.p_complete_onboarding,
            "p_activate_day1": persona.p_activate_day1,
            "p_retain_day7": persona.p_retain_day7,
            "p_retain_day30": persona.p_retain_day30,
            "p_retain_day90": persona.p_retain_day90,
            "p_convert_to_paid": persona.p_convert_to_paid,
            "p_churn_monthly": persona.p_churn_monthly,
            "expected_arpu_monthly": persona.expected_arpu_monthly,
        }
        cohort.append(user)
    return cohort
