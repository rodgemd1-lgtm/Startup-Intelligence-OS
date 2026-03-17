# Simulated Maturity Harness Implementation

## Objective
Bind the stronger benchmark, eval, and learning-science datasets into repeatable simulated-maturity review runs for the departments where benchmark-backed proof can move maturity fastest.

## Framing
The stronger dataset wave created the right source spine, but it was still inert until those benchmark and `studio_evals` assets were actually used in reviewable scenario runs. The goal here was not to claim live 10 out of 10 maturity. The goal was to convert stronger evidence into stored simulated proof for Founder, Revenue, Finance, Data Science, and Job Studio.

## Options
- Leave the stronger dataset wave as passive research inventory.
- Attach the new benchmark and eval corpora to a repeatable simulated-review harness with stored run outputs.

## Recommendation
Use the repeatable harness. It gives Jake and Susan a benchmark-backed simulated proof layer that can be rerun, inspected, and compared without pretending it replaces live operating maturity.

## Results
- Stronger benchmark chunks used: `319`
- Stronger eval chunks used: `382`
- Stronger training chunks used: `216`
- Gap-closure chunks available in the broader evidence base: `9718`
- Simulated review scenarios executed: `5`
- Scenario scores: Founder `10.0`, Revenue `10.0`, Finance `10.0`, Data Science `10.0`, Job Studio `10.0`

These scores are simulated-maturity scores only. They prove benchmark-backed scenario readiness under the harness contract, not live 10 out of 10 operating maturity.

## Assumptions
- The stronger benchmark wave remains the current best source of named examples, eval guidance, and synthetic-review material.
- Monte Carlo is a useful synthetic proof layer for Founder, Revenue, Finance, and Data Science scenarios.
- Job Studio gets more signal from benchmark, eval, and learning-science evidence than from Monte Carlo alone.

## Risks
- A perfect simulated score can be misread as a live maturity claim if the dashboard does not show the distinction clearly.
- Strong benchmark density can hide weak real-world adoption if the harness is not paired with live run reviews.
- Static thresholds can go stale if new benchmark sources materially raise what “world-class” should mean.

## Artifacts Created Or Updated
- [simulated_maturity.py](/Users/mikerodgers/Startup-Intelligence-OS/apps/decision_os/simulated_maturity.py)
- [run_simulated_maturity_harness.py](/Users/mikerodgers/Startup-Intelligence-OS/bin/run_simulated_maturity_harness.py)
- [test_simulated_maturity.py](/Users/mikerodgers/Startup-Intelligence-OS/apps/decision_os/tests/test_simulated_maturity.py)
- [simulated-maturity-harness-summary.md](/Users/mikerodgers/Startup-Intelligence-OS/.startup-os/artifacts/simulated-maturity/simulated-maturity-harness-summary.md)
- [founder-decision-simulated-review.md](/Users/mikerodgers/Startup-Intelligence-OS/.startup-os/artifacts/simulated-maturity/founder-decision-simulated-review.md)
- [revenue-growth-simulated-review.md](/Users/mikerodgers/Startup-Intelligence-OS/.startup-os/artifacts/simulated-maturity/revenue-growth-simulated-review.md)
- [finance-operating-simulated-review.md](/Users/mikerodgers/Startup-Intelligence-OS/.startup-os/artifacts/simulated-maturity/finance-operating-simulated-review.md)
- [data-decision-science-simulated-review.md](/Users/mikerodgers/Startup-Intelligence-OS/.startup-os/artifacts/simulated-maturity/data-decision-science-simulated-review.md)
- [job-studio-simulated-review.md](/Users/mikerodgers/Startup-Intelligence-OS/.startup-os/artifacts/simulated-maturity/job-studio-simulated-review.md)
- [simulated-maturity-harness.yaml](/Users/mikerodgers/Startup-Intelligence-OS/.startup-os/capabilities/simulated-maturity-harness.yaml)

## Next Actions
- Surface simulated-maturity outputs in the department dashboard next to operational maturity.
- Add recurring harness runs so simulated score movement is visible over time.
- Define per-department live-proof thresholds so the simulated layer and operational layer stay aligned.
