# Revenue & Growth Simulated Review

- department_id: `revenue-growth-studio`
- company_id: `founder-intelligence-os`
- simulated_maturity_score: `10.0`

## Narrative
Stress-test pricing and onboarding changes against stronger benchmark and evaluation sources.

## Required Checks
- Benchmark case library attached
- Synthetic eval sources attached
- Monte Carlo revenue scenario included

## Score Breakdown
- benchmark_score: `10.0`
- eval_score: `10.0`
- training_score: `10.0`
- checklist_score: `10.0`

## Check Status
- benchmark_library_attached: `true`
- eval_library_attached: `true`
- synthetic_framework_attached: `true`
- reviewable_output_shape: `true`
- monte_carlo_attached: `true`

## Monte Carlo
```json
{
  "type": "revenue_growth",
  "baseline_revenue_mean": 3084.68,
  "enhanced_revenue_mean": 5936.03,
  "revenue_delta_pct": 92.44,
  "conversion_mean_pct": 0.82,
  "retention_day30_pct": 6.62
}
```
