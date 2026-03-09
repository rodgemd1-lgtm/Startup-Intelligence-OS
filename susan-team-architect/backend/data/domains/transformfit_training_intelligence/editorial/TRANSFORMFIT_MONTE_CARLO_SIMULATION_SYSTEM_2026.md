# TransformFit Monte Carlo Simulation System 2026

This artifact defines the simulation layer that turns research and user-failure patterns into predictive intervention priorities.

## Purpose

- estimate where users are most likely to miss, stall, or drop out
- compare different program structures against real-life constraints
- decide where coach cues should intervene first

## What gets simulated

- beginner and returning lifters
- busy intermediate lifters with time pressure
- ambitious hypertrophy users with higher fatigue exposure
- home-gym users with equipment constraints
- confidence-fragile users returning after inconsistency

## Key state variables

- schedule fit
- time pressure
- life stress
- recovery capacity
- soreness sensitivity
- confidence
- coach bond
- equipment match
- novelty need
- plateau tolerance

## High-priority failure windows to model

- session 2 soreness and friction shock
- week 2 schedule collision
- week 4-6 plateau doubt
- first missed session
- second miss inside 10 days
- fatigue spike
- deload resistance
- re-entry after 7+ days

## Outputs TransformFit should use

- risk heatmap by program and archetype
- intervention windows ranked by expected lift
- failure-reason distribution
- predicted completion-rate lift with coaching cues enabled

## Product use

- `algorithm-lab`
  - derive intervention thresholds and confidence bands
- `coaching-architecture-studio`
  - decide what the coach says and when
- `workout-program-studio`
  - reshape programs that have avoidable adherence cliffs
- `ai-evaluation-specialist`
  - score whether cues improve completion, trust, and re-entry

## Current implementation

- simulation outputs live in the `simulations/` folder
- the generator script is `scripts/generate_transformfit_monte_carlo.py`
- generated summaries are ingested as `simulation_models`

## Guardrails

- simulations are priors, not truth
- they should guide intervention design, not override real user telemetry
- coach cues should stay explainable and bounded even when risk scores are high
