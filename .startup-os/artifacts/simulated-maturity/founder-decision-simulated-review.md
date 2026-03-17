# Founder Decision Room Simulated Review

- department_id: `founder-decision-room`
- company_id: `founder-intelligence-os`
- simulated_maturity_score: `10.0`

## Narrative
Compare two strategic options with benchmark-backed framing and a simple Monte Carlo option check.

## Required Checks
- Named benchmark cases attached
- Synthetic review framework attached
- Option comparison is reviewable
- Monte Carlo option comparison included

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
  "type": "founder_decision",
  "option_a_revenue_mean": 1862.68,
  "option_b_revenue_mean": 2395.45,
  "winning_option": "option_b_personalization"
}
```
