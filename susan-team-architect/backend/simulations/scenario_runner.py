"""Run comprehensive Monte Carlo scenarios and store results in RAG.

Generates simulation data across multiple scenarios:
1. Baseline (industry average)
2. TransformFit with key features
3. Best-case (top-tier execution)
4. Conservative (realistic first year)
5. Sensitivity analysis (which feature matters most)
6. Cohort size projections (1K, 10K, 50K, 100K users)
7. Pricing tier analysis
"""
from __future__ import annotations
from simulations.monte_carlo import run_simulation, SimulationConfig
from simulations.personas import PERSONAS
from rag_engine.retriever import Retriever
from susan_core.schemas import KnowledgeChunk


def run_all_scenarios() -> int:
    """Run all scenarios and store results in RAG. Returns total chunks stored."""
    r = Retriever()
    chunks = []

    # ── Scenario 1: Baseline ──
    print("Running Scenario 1: Industry Baseline...")
    baseline = run_simulation(cohort_size=10_000, months=12, num_trials=200)
    bs = baseline.funnel_summary()
    chunks.append(_make_chunk(
        f"MONTE CARLO SCENARIO: Industry Baseline (200 trials)\n"
        f"Cohort: 10,000 downloads over 12 months\n\n"
        f"Funnel: Onboarding {bs['onboarding_rate']['mean_pct']}% → "
        f"Day1 {bs['day1_activation_rate']['mean_pct']}% → "
        f"Day7 {bs['day7_retention_rate']['mean_pct']}% → "
        f"Day30 {bs['day30_retention_rate']['mean_pct']}% → "
        f"Day90 {bs['day90_retention_rate']['mean_pct']}% → "
        f"Paid {bs['conversion_rate']['mean_pct']}%\n\n"
        f"Revenue: ${bs['revenue']['mean']:.0f} "
        f"(90% CI: ${bs['revenue']['p5']:.0f}-${bs['revenue']['p95']:.0f})\n"
        f"Active at 12mo: {bs['active_at_end']['mean']:.0f} users "
        f"({bs['active_at_end']['mean']/100:.1f}%)\n"
        f"Revenue per download: ${bs['revenue']['mean']/10000:.2f}",
        source="monte_carlo:scenario_baseline",
    ))

    # ── Scenario 2: TransformFit Enhanced ──
    print("Running Scenario 2: TransformFit Enhanced...")
    enhanced = run_simulation(
        cohort_size=10_000, months=12, num_trials=200, seed=42,
        onboarding_quality=1.15, ai_personalization=1.30,
        social_features=1.20, gamification=1.25, pricing_optimization=1.15,
    )
    es = enhanced.funnel_summary()
    chunks.append(_make_chunk(
        f"MONTE CARLO SCENARIO: TransformFit Enhanced (200 trials)\n"
        f"Features: AI personalization +30%, social +20%, gamification +25%, "
        f"onboarding +15%, pricing +15%\n\n"
        f"Funnel: Onboarding {es['onboarding_rate']['mean_pct']}% → "
        f"Day1 {es['day1_activation_rate']['mean_pct']}% → "
        f"Day7 {es['day7_retention_rate']['mean_pct']}% → "
        f"Day30 {es['day30_retention_rate']['mean_pct']}% → "
        f"Day90 {es['day90_retention_rate']['mean_pct']}% → "
        f"Paid {es['conversion_rate']['mean_pct']}%\n\n"
        f"Revenue: ${es['revenue']['mean']:.0f} "
        f"(90% CI: ${es['revenue']['p5']:.0f}-${es['revenue']['p95']:.0f})\n"
        f"Revenue per download: ${es['revenue']['mean']/10000:.2f}\n"
        f"vs Baseline: +{(es['revenue']['mean']-bs['revenue']['mean'])/bs['revenue']['mean']*100:.0f}% revenue",
        source="monte_carlo:scenario_transformfit",
    ))

    # ── Scenario 3: Best Case (Top 10% execution) ──
    print("Running Scenario 3: Best Case...")
    best = run_simulation(
        cohort_size=10_000, months=12, num_trials=200, seed=43,
        onboarding_quality=1.30, ai_personalization=1.50,
        social_features=1.40, gamification=1.35, pricing_optimization=1.25,
    )
    bests = best.funnel_summary()
    chunks.append(_make_chunk(
        f"MONTE CARLO SCENARIO: Best Case - Top Tier Execution (200 trials)\n"
        f"All features at maximum impact\n\n"
        f"Funnel: Onboarding {bests['onboarding_rate']['mean_pct']}% → "
        f"Day30 {bests['day30_retention_rate']['mean_pct']}% → "
        f"Paid {bests['conversion_rate']['mean_pct']}%\n\n"
        f"Revenue: ${bests['revenue']['mean']:.0f}\n"
        f"Revenue per download: ${bests['revenue']['mean']/10000:.2f}\n"
        f"vs Baseline: +{(bests['revenue']['mean']-bs['revenue']['mean'])/bs['revenue']['mean']*100:.0f}% revenue",
        source="monte_carlo:scenario_best_case",
    ))

    # ── Scenario 4: Conservative (Realistic Y1) ──
    print("Running Scenario 4: Conservative Y1...")
    conservative = run_simulation(
        cohort_size=10_000, months=12, num_trials=200, seed=44,
        onboarding_quality=1.05, ai_personalization=1.10,
        social_features=1.05, gamification=1.10, pricing_optimization=1.05,
    )
    cs = conservative.funnel_summary()
    chunks.append(_make_chunk(
        f"MONTE CARLO SCENARIO: Conservative Year 1 (200 trials)\n"
        f"Modest feature impact (5-10% improvements)\n\n"
        f"Funnel: Onboarding {cs['onboarding_rate']['mean_pct']}% → "
        f"Day30 {cs['day30_retention_rate']['mean_pct']}% → "
        f"Paid {cs['conversion_rate']['mean_pct']}%\n\n"
        f"Revenue: ${cs['revenue']['mean']:.0f}\n"
        f"Revenue per download: ${cs['revenue']['mean']/10000:.2f}\n"
        f"vs Baseline: +{(cs['revenue']['mean']-bs['revenue']['mean'])/bs['revenue']['mean']*100:.0f}% revenue",
        source="monte_carlo:scenario_conservative",
    ))

    # ── Scenario 5: Sensitivity Analysis ──
    print("Running Scenario 5: Sensitivity Analysis...")
    features = {
        "ai_personalization": "AI Personalization",
        "social_features": "Social/Community",
        "gamification": "Gamification",
        "onboarding_quality": "Onboarding Quality",
        "pricing_optimization": "Pricing Optimization",
    }
    sensitivity_lines = [
        "MONTE CARLO SENSITIVITY ANALYSIS\n"
        "Each feature tested independently at +30% impact, others at baseline.\n"
        "Shows which feature has the biggest revenue impact.\n\n"
        f"{'Feature':<25} {'Revenue':>10} {'vs Base':>10} {'Δ%':>8}\n"
        f"{'-'*25} {'-'*10} {'-'*10} {'-'*8}"
    ]
    feature_impacts = {}
    for key, label in features.items():
        result = run_simulation(
            cohort_size=10_000, months=12, num_trials=100,
            seed=45, **{key: 1.30},
        )
        rev = result.funnel_summary()["revenue"]["mean"]
        delta = rev - bs["revenue"]["mean"]
        delta_pct = delta / bs["revenue"]["mean"] * 100
        feature_impacts[label] = delta_pct
        sensitivity_lines.append(
            f"{label:<25} ${rev:>9,.0f} +${delta:>8,.0f} +{delta_pct:>6.1f}%"
        )

    sorted_impacts = sorted(feature_impacts.items(), key=lambda x: x[1], reverse=True)
    sensitivity_lines.append(
        f"\nRANKING BY IMPACT: "
        + " > ".join(f"{k} (+{v:.0f}%)" for k, v in sorted_impacts)
    )
    sensitivity_lines.append(
        "\nINSIGHT: Focus engineering resources on the highest-impact feature first."
    )
    chunks.append(_make_chunk(
        "\n".join(sensitivity_lines),
        source="monte_carlo:sensitivity_analysis",
    ))

    # ── Scenario 6: Scale Projections ──
    print("Running Scenario 6: Scale Projections...")
    scale_lines = [
        "MONTE CARLO SCALE PROJECTIONS — TransformFit Enhanced\n"
        "How revenue scales with cohort size (12-month projection)\n\n"
        f"{'Cohort':>10} {'Revenue (Mean)':>15} {'Revenue (P5)':>14} "
        f"{'Revenue (P95)':>15} {'Paid Users':>12} {'RPD':>8}\n"
        f"{'-'*10} {'-'*15} {'-'*14} {'-'*15} {'-'*12} {'-'*8}"
    ]
    for size in [1_000, 5_000, 10_000, 25_000, 50_000, 100_000]:
        result = run_simulation(
            cohort_size=size, months=12, num_trials=100, seed=46,
            onboarding_quality=1.15, ai_personalization=1.30,
            social_features=1.20, gamification=1.25, pricing_optimization=1.15,
        )
        s = result.funnel_summary()
        scale_lines.append(
            f"{size:>10,} ${s['revenue']['mean']:>14,.0f} "
            f"${s['revenue']['p5']:>13,.0f} ${s['revenue']['p95']:>14,.0f} "
            f"{s['active_at_end']['mean']:>11,.0f} "
            f"${s['revenue']['mean']/size:>7.2f}"
        )
    scale_lines.append(
        "\nRPD = Revenue Per Download. Target: >$2.00 RPD for sustainable unit economics."
    )
    chunks.append(_make_chunk(
        "\n".join(scale_lines),
        source="monte_carlo:scale_projections",
    ))

    # ── Scenario 7: 24-Month Projection ──
    print("Running Scenario 7: 24-Month Projection...")
    long_term = run_simulation(
        cohort_size=10_000, months=24, num_trials=200, seed=47,
        onboarding_quality=1.15, ai_personalization=1.30,
        social_features=1.20, gamification=1.25, pricing_optimization=1.15,
    )
    ls = long_term.funnel_summary()
    chunks.append(_make_chunk(
        f"MONTE CARLO 24-MONTH PROJECTION — TransformFit Enhanced (200 trials)\n"
        f"Cohort: 10,000 users over 24 months\n\n"
        f"Revenue: ${ls['revenue']['mean']:.0f} "
        f"(90% CI: ${ls['revenue']['p5']:.0f}-${ls['revenue']['p95']:.0f})\n"
        f"Active at 24mo: {ls['active_at_end']['mean']:.0f} users "
        f"({ls['active_at_end']['mean']/100:.1f}%)\n"
        f"Revenue per download: ${ls['revenue']['mean']/10000:.2f}\n\n"
        f"vs 12-month: Revenue grows {ls['revenue']['mean']/es['revenue']['mean']:.1f}x "
        f"with same cohort (compound retention value).",
        source="monte_carlo:24month_projection",
    ))

    # ── Scenario 8: Persona Deep Dives ──
    print("Running Scenario 8: Persona Profiles...")
    pb = enhanced.persona_breakdown()
    for name, data in sorted(pb.items(), key=lambda x: x[1]["avg_revenue"], reverse=True):
        persona_obj = next((p for p in PERSONAS if p.name == name), None)
        if not persona_obj:
            continue
        chunks.append(_make_chunk(
            f"PERSONA SIMULATION PROFILE: {name}\n"
            f"Description: {persona_obj.description}\n\n"
            f"Demographics: Age {persona_obj.age_range[0]}-{persona_obj.age_range[1]}, "
            f"{persona_obj.female_pct*100:.0f}% female, "
            f"BMI {persona_obj.bmi_mean} (±{persona_obj.bmi_std})\n"
            f"Activity: {persona_obj.activity_level}, "
            f"Tech comfort: {persona_obj.tech_comfort*100:.0f}%, "
            f"Price sensitivity: {persona_obj.price_sensitivity*100:.0f}%\n"
            f"Motivation: {persona_obj.motivation}\n\n"
            f"SIMULATED OUTCOMES (10K cohort, 12mo, 200 trials):\n"
            f"  Market share: {data['avg_users']/100:.0f}%\n"
            f"  Conversion rate: {data['avg_conversion_rate']:.1f}%\n"
            f"  12-month retention: {data['avg_retention_rate']:.1f}%\n"
            f"  LTV: ${data['avg_ltv']:.2f}\n"
            f"  Revenue contribution: ${data['avg_revenue']:.0f}\n\n"
            f"FUNNEL PROBABILITIES:\n"
            f"  Onboarding: {persona_obj.p_complete_onboarding*100:.0f}%\n"
            f"  Day 1 activation: {persona_obj.p_activate_day1*100:.0f}%\n"
            f"  Day 7 retention: {persona_obj.p_retain_day7*100:.0f}%\n"
            f"  Day 30 retention: {persona_obj.p_retain_day30*100:.0f}%\n"
            f"  Monthly churn: {persona_obj.p_churn_monthly*100:.0f}%",
            source=f"monte_carlo:persona_{name.lower().replace(' ', '_')}",
            data_type="user_research",
        ))

    # ── Store everything ──
    print(f"\nStoring {len(chunks)} simulation chunks in knowledge base...")
    count = r.store_chunks(chunks)
    print(f"Stored {count} chunks successfully.")
    return count


def _make_chunk(content: str, source: str, data_type: str = "market_research") -> KnowledgeChunk:
    return KnowledgeChunk(
        content=content,
        company_id="shared",
        data_type=data_type,
        source=source,
        metadata={"simulation": True, "type": "monte_carlo"},
    )


if __name__ == "__main__":
    run_all_scenarios()
