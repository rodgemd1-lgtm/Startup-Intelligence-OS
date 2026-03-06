"""Monte Carlo simulator for fitness app user cohort modeling.

Simulates N users through the full app lifecycle funnel:
  Download → Onboarding → Activation → Retention → Conversion → Revenue/Churn

Each user is sampled from persona distributions (personas.py) with
probabilities calibrated to published industry benchmarks:
  - RevenueCat State of Subscription Apps 2025
  - Sensor Tower Health & Fitness 2025
  - Business of Apps retention benchmarks
  - Brian Balfour retention framework
  - Fitbod, Noom, Strava, Peloton published metrics

Usage:
    from simulations.monte_carlo import run_simulation, print_report
    results = run_simulation(cohort_size=10000, months=12)
    print_report(results)
"""
from __future__ import annotations
import random
import statistics
from dataclasses import dataclass, field
from simulations.personas import sample_cohort, PERSONAS


@dataclass
class SimulationConfig:
    """Configuration for a Monte Carlo simulation run."""
    cohort_size: int = 10_000
    months: int = 12
    num_trials: int = 100  # number of Monte Carlo trials
    seed: int | None = None
    # Feature impact modifiers (1.0 = no effect, 1.2 = 20% improvement)
    onboarding_quality: float = 1.0  # better onboarding → higher completion
    ai_personalization: float = 1.0  # AI workout plans → better retention
    social_features: float = 1.0    # community features → lower churn
    gamification: float = 1.0       # streaks, badges → higher activation
    pricing_optimization: float = 1.0  # better pricing → higher conversion


@dataclass
class UserState:
    """Tracks a single simulated user through the funnel."""
    persona: str
    completed_onboarding: bool = False
    activated_day1: bool = False
    retained_day7: bool = False
    retained_day30: bool = False
    retained_day90: bool = False
    converted_to_paid: bool = False
    churned: bool = False
    months_active: int = 0
    total_revenue: float = 0.0


@dataclass
class TrialResult:
    """Results from a single Monte Carlo trial."""
    cohort_size: int
    months: int
    # Funnel metrics
    onboarding_completions: int = 0
    day1_activations: int = 0
    day7_retained: int = 0
    day30_retained: int = 0
    day90_retained: int = 0
    paid_conversions: int = 0
    # Revenue
    total_revenue: float = 0.0
    # Retention at end of period
    active_at_end: int = 0
    # Per-persona breakdown
    persona_results: dict = field(default_factory=dict)


@dataclass
class SimulationResults:
    """Aggregated results across all Monte Carlo trials."""
    config: SimulationConfig
    trials: list[TrialResult]

    @property
    def n_trials(self) -> int:
        return len(self.trials)

    def _metric_distribution(self, attr: str) -> dict:
        values = [getattr(t, attr) for t in self.trials]
        return {
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0,
            "p5": sorted(values)[max(0, int(len(values) * 0.05))],
            "p25": sorted(values)[int(len(values) * 0.25)],
            "p75": sorted(values)[int(len(values) * 0.75)],
            "p95": sorted(values)[min(len(values) - 1, int(len(values) * 0.95))],
        }

    def funnel_summary(self) -> dict:
        cs = self.config.cohort_size
        return {
            "cohort_size": cs,
            "months": self.config.months,
            "n_trials": self.n_trials,
            "onboarding_rate": self._pct_dist("onboarding_completions", cs),
            "day1_activation_rate": self._pct_dist("day1_activations", cs),
            "day7_retention_rate": self._pct_dist("day7_retained", cs),
            "day30_retention_rate": self._pct_dist("day30_retained", cs),
            "day90_retention_rate": self._pct_dist("day90_retained", cs),
            "conversion_rate": self._pct_dist("paid_conversions", cs),
            "revenue": self._metric_distribution("total_revenue"),
            "active_at_end": self._metric_distribution("active_at_end"),
        }

    def _pct_dist(self, attr: str, base: int) -> dict:
        values = [getattr(t, attr) / base * 100 for t in self.trials]
        return {
            "mean_pct": round(statistics.mean(values), 2),
            "std_pct": round(statistics.stdev(values), 2) if len(values) > 1 else 0,
            "p5_pct": round(sorted(values)[max(0, int(len(values) * 0.05))], 2),
            "p95_pct": round(sorted(values)[min(len(values) - 1, int(len(values) * 0.95))], 2),
        }

    def persona_breakdown(self) -> dict:
        """Aggregate persona-level metrics across trials."""
        all_personas = {}
        for trial in self.trials:
            for name, data in trial.persona_results.items():
                if name not in all_personas:
                    all_personas[name] = []
                all_personas[name].append(data)

        breakdown = {}
        for name, trials_data in all_personas.items():
            n_users = [d["count"] for d in trials_data]
            revenues = [d["revenue"] for d in trials_data]
            conversions = [d["conversions"] for d in trials_data]
            active = [d["active_at_end"] for d in trials_data]

            avg_users = statistics.mean(n_users)
            breakdown[name] = {
                "avg_users": round(avg_users),
                "avg_revenue": round(statistics.mean(revenues), 2),
                "avg_ltv": round(statistics.mean(revenues) / max(avg_users, 1), 2),
                "avg_conversion_rate": round(
                    statistics.mean(c / max(n, 1) * 100 for c, n in zip(conversions, n_users)), 2
                ),
                "avg_retention_rate": round(
                    statistics.mean(a / max(n, 1) * 100 for a, n in zip(active, n_users)), 2
                ),
            }
        return breakdown


def _simulate_user(user: dict, config: SimulationConfig) -> UserState:
    """Simulate a single user through the app lifecycle."""
    state = UserState(persona=user["persona"])

    # ── Stage 1: Onboarding ──
    p_onboard = min(1.0, user["p_complete_onboarding"] * config.onboarding_quality)
    if random.random() >= p_onboard:
        return state
    state.completed_onboarding = True

    # ── Stage 2: Day 1 Activation ──
    p_activate = min(1.0, user["p_activate_day1"] * config.gamification)
    if random.random() >= p_activate:
        return state
    state.activated_day1 = True

    # ── Stage 3: Early Retention ──
    p_d7 = min(1.0, user["p_retain_day7"] * config.ai_personalization)
    if random.random() < p_d7:
        state.retained_day7 = True

    p_d30 = min(1.0, user["p_retain_day30"] * config.ai_personalization)
    if random.random() < p_d30:
        state.retained_day30 = True
        state.months_active = 1
    elif not state.retained_day7:
        return state

    p_d90 = min(1.0, user["p_retain_day90"] * config.ai_personalization * config.social_features)
    if random.random() < p_d90:
        state.retained_day90 = True
        state.months_active = 3

    # ── Stage 4: Conversion ──
    if state.retained_day7:
        p_convert = min(1.0, user["p_convert_to_paid"] * config.pricing_optimization)
        # Users who stay longer are more likely to convert
        if state.retained_day30:
            p_convert = min(1.0, p_convert * 1.5)
        if state.retained_day90:
            p_convert = min(1.0, p_convert * 2.0)

        if random.random() < p_convert:
            state.converted_to_paid = True

    # ── Stage 5: Monthly Churn Simulation ──
    if state.converted_to_paid:
        p_churn = user["p_churn_monthly"]
        # Social features reduce churn
        p_churn = max(0.01, p_churn / config.social_features)

        for month in range(max(state.months_active, 1), config.months + 1):
            if random.random() < p_churn:
                state.churned = True
                state.months_active = month
                break
            state.months_active = month
            state.total_revenue += user["expected_arpu_monthly"]
    elif state.retained_day30:
        # Free user who stuck around — count as active but no revenue
        state.months_active = max(state.months_active, 1)
        p_churn_free = min(0.95, user["p_churn_monthly"] * 1.5)
        for month in range(state.months_active, config.months + 1):
            if random.random() < p_churn_free:
                state.churned = True
                state.months_active = month
                break
            state.months_active = month

    return state


def _run_single_trial(config: SimulationConfig) -> TrialResult:
    """Run one complete Monte Carlo trial."""
    cohort = sample_cohort(config.cohort_size)
    result = TrialResult(cohort_size=config.cohort_size, months=config.months)
    persona_data: dict[str, dict] = {}

    for user in cohort:
        state = _simulate_user(user, config)
        pname = state.persona

        if pname not in persona_data:
            persona_data[pname] = {
                "count": 0, "revenue": 0.0, "conversions": 0, "active_at_end": 0
            }
        persona_data[pname]["count"] += 1

        if state.completed_onboarding:
            result.onboarding_completions += 1
        if state.activated_day1:
            result.day1_activations += 1
        if state.retained_day7:
            result.day7_retained += 1
        if state.retained_day30:
            result.day30_retained += 1
        if state.retained_day90:
            result.day90_retained += 1
        if state.converted_to_paid:
            result.paid_conversions += 1
            persona_data[pname]["conversions"] += 1

        result.total_revenue += state.total_revenue
        persona_data[pname]["revenue"] += state.total_revenue

        if not state.churned and state.months_active >= config.months:
            result.active_at_end += 1
            persona_data[pname]["active_at_end"] += 1

    result.persona_results = persona_data
    return result


def run_simulation(
    cohort_size: int = 10_000,
    months: int = 12,
    num_trials: int = 100,
    seed: int | None = 42,
    **feature_impacts,
) -> SimulationResults:
    """Run a full Monte Carlo simulation.

    Args:
        cohort_size: Number of users per trial
        months: Simulation duration in months
        num_trials: Number of Monte Carlo trials to run
        seed: Random seed for reproducibility
        **feature_impacts: Override SimulationConfig fields like
            onboarding_quality=1.2, ai_personalization=1.3

    Returns:
        SimulationResults with aggregated metrics and distributions
    """
    if seed is not None:
        random.seed(seed)

    config = SimulationConfig(
        cohort_size=cohort_size,
        months=months,
        num_trials=num_trials,
        seed=seed,
        **{k: v for k, v in feature_impacts.items() if hasattr(SimulationConfig, k)},
    )

    trials = [_run_single_trial(config) for _ in range(num_trials)]
    return SimulationResults(config=config, trials=trials)


def print_report(results: SimulationResults) -> None:
    """Print a formatted simulation report."""
    summary = results.funnel_summary()
    cs = summary["cohort_size"]

    print("=" * 65)
    print(f"  MONTE CARLO SIMULATION REPORT")
    print(f"  {cs:,} users × {summary['months']} months × {summary['n_trials']} trials")
    print("=" * 65)

    print("\n── FUNNEL CONVERSION ──")
    for stage, label in [
        ("onboarding_rate", "Onboarding Complete"),
        ("day1_activation_rate", "Day 1 Activation"),
        ("day7_retention_rate", "Day 7 Retention"),
        ("day30_retention_rate", "Day 30 Retention"),
        ("day90_retention_rate", "Day 90 Retention"),
        ("conversion_rate", "Paid Conversion"),
    ]:
        d = summary[stage]
        print(f"  {label:.<30} {d['mean_pct']:>6.1f}%  "
              f"(90% CI: {d['p5_pct']:.1f}% – {d['p95_pct']:.1f}%)")

    rev = summary["revenue"]
    print(f"\n── REVENUE ({summary['months']} months) ──")
    print(f"  Mean total revenue .......... ${rev['mean']:>12,.0f}")
    print(f"  Median ....................... ${rev['median']:>12,.0f}")
    print(f"  90% CI ....................... ${rev['p5']:>12,.0f} – ${rev['p95']:>12,.0f}")

    arpu = rev["mean"] / cs
    print(f"  Revenue per download ......... ${arpu:>12.2f}")

    active = summary["active_at_end"]
    print(f"\n── END-OF-PERIOD ({summary['months']} months) ──")
    print(f"  Active users (mean) .......... {active['mean']:>10,.0f}  "
          f"({active['mean'] / cs * 100:.1f}%)")
    print(f"  Active users (90% CI) ........ {active['p5']:>10,.0f} – {active['p95']:>10,.0f}")

    print(f"\n── PERSONA BREAKDOWN ──")
    breakdown = results.persona_breakdown()
    print(f"  {'Persona':<25} {'Users':>6} {'Conv%':>7} {'Retain%':>8} "
          f"{'Revenue':>10} {'LTV':>8}")
    print(f"  {'-' * 25} {'-' * 6} {'-' * 7} {'-' * 8} {'-' * 10} {'-' * 8}")

    sorted_personas = sorted(breakdown.items(), key=lambda x: x[1]["avg_revenue"], reverse=True)
    for name, data in sorted_personas:
        print(f"  {name:<25} {data['avg_users']:>6,} {data['avg_conversion_rate']:>6.1f}% "
              f"{data['avg_retention_rate']:>7.1f}% ${data['avg_revenue']:>9,.0f} "
              f"${data['avg_ltv']:>7.2f}")

    print("\n" + "=" * 65)


def compare_scenarios(
    base_results: SimulationResults,
    enhanced_results: SimulationResults,
    labels: tuple[str, str] = ("Baseline", "Enhanced"),
) -> None:
    """Compare two simulation scenarios side by side."""
    base = base_results.funnel_summary()
    enhanced = enhanced_results.funnel_summary()

    print("=" * 70)
    print(f"  SCENARIO COMPARISON: {labels[0]} vs {labels[1]}")
    print("=" * 70)

    stages = [
        ("onboarding_rate", "Onboarding"),
        ("day1_activation_rate", "Day 1 Activation"),
        ("day7_retention_rate", "Day 7 Retention"),
        ("day30_retention_rate", "Day 30 Retention"),
        ("day90_retention_rate", "Day 90 Retention"),
        ("conversion_rate", "Paid Conversion"),
    ]

    print(f"\n  {'Metric':<25} {labels[0]:>12} {labels[1]:>12} {'Δ':>10}")
    print(f"  {'-' * 25} {'-' * 12} {'-' * 12} {'-' * 10}")

    for key, label in stages:
        b_val = base[key]["mean_pct"]
        e_val = enhanced[key]["mean_pct"]
        delta = e_val - b_val
        sign = "+" if delta > 0 else ""
        print(f"  {label:<25} {b_val:>11.1f}% {e_val:>11.1f}% {sign}{delta:>8.1f}pp")

    b_rev = base["revenue"]["mean"]
    e_rev = enhanced["revenue"]["mean"]
    delta_rev = e_rev - b_rev
    delta_pct = (delta_rev / b_rev * 100) if b_rev > 0 else 0
    sign = "+" if delta_rev > 0 else ""

    print(f"\n  {'Revenue':<25} ${b_rev:>10,.0f} ${e_rev:>10,.0f} {sign}${delta_rev:>7,.0f} ({sign}{delta_pct:.0f}%)")
    print("=" * 70)
