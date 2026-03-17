# Finance & Operating Cadence Studio Operating Pack

## Objective

Make Finance & Operating Cadence Studio run as a repeatable review system for KPI trees, operating reviews, variance response, and resource calls.

## Current Gap

The studio has a wrapper but not enough reusable operating artifacts. It needs:

- a KPI tree template
- a weekly operating review packet
- a monthly variance response packet
- a resource-call format

## Operating System

### Cadence

1. Weekly operating review
2. Monthly variance review
3. Quarterly resource decision review
4. KPI tree refresh when company priorities change

### Required source stack

- department definition in `.startup-os/departments/finance-operating-cadence-studio.yaml`
- live source manifest in `startup_os_finance_operating_cadence_officials.yaml`
- scorecard and metric inputs from Data & Decision Science Studio
- decision packets when resource tradeoffs become strategic

### Required outputs

- KPI tree
- weekly operating review
- variance brief
- resource call

## Scorecard

| Dimension | Question |
|---|---|
| Metric clarity | Are KPIs legible and decision-linked? |
| Cadence reliability | Is the review rhythm current and repeatable? |
| Variance response speed | How fast can the team act on changes? |
| Resource alignment | Are people, money, and time pointed at the right priorities? |

## Stage Gates

### Gate 1: KPI legibility
- north-star metric named
- leading indicators named
- owner and review horizon named

### Gate 2: Review packet quality
- current state visible
- variance visible
- next move visible

### Gate 3: Resource escalation
- founder decision packet created when budget or priority shifts become material

## Writeback

Write back after every cadence run:

- KPI movement
- major variances
- response actions
- decisions blocked by missing metrics

## Templates

- `.startup-os/artifacts/finance-operating-cadence/kpi-tree-template.md`
- `.startup-os/artifacts/finance-operating-cadence/weekly-operating-review-template.md`

