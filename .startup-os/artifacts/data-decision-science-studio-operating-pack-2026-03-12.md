# Data & Decision Science Studio Operating Pack

**Date:** 2026-03-12  
**Owner:** Jake  
**Company:** founder-intelligence-os

## Objective
Turn Data & Decision Science Studio into a reliable system for metrics trees, forecasts, experiment readouts, and recalibration instead of ad hoc analysis.

## Operating loop
1. Define the dependent decision, KPI, or forecast target.
2. Audit evidence coverage and data freshness.
3. Build the scorecard, metrics tree, or forecast.
4. Review model usefulness and limits after execution.
5. Recalibrate assumptions and write back the updated system state.

## Required inputs
- decision or KPI target
- source inventory
- time horizon
- baseline metric state

## Default outputs
- metrics tree
- forecast brief
- experiment readout
- recalibration note

## Review cadence
- Weekly: experiment and metric exceptions
- Monthly: forecast recalibration review
- Quarterly: scorecard and instrumentation audit

## Refresh and evaluation rules
- Every forecast must state model limits and confidence.
- Every experiment readout must define the next evidence move.
- Any stale or low-confidence metric should trigger a refresh action.

## Source bundle
- `.startup-os/artifacts/data-decision-science`
- `susan-team-architect/backend/data/scrape_manifests/startup_os_data_decision_science_officials.yaml`
- `susan-team-architect/backend/artifacts`
- `susan-team-architect/backend/artifacts/department_gap_closure_wave/latest_summary.md`

## Templates in this pack
- `.startup-os/artifacts/data-decision-science/metrics-tree-and-forecast-template.md`
- `.startup-os/artifacts/data-decision-science/experiment-recalibration-template.md`

## Success criteria
- Decision support outputs are grounded in named evidence and explicit limits.
- Forecasts are reviewed and recalibrated, not left stale.
- Scorecards and simulations improve from actual operating feedback.
