# Operator Console Live Metrics

**Date:** 2026-03-12

## Current live metrics sources
- `susan-team-architect/backend/artifacts/department_gap_closure_wave/latest_summary.md`
- `.startup-os/artifacts/job-studio-pipeline-monitor-2026-03-12.md`
- `.startup-os/artifacts/department-gap-closure-wave-monitor-2026-03-12.md`
- `.startup-os/artifacts/department-maturity-dashboard-2026-03-12.md`

## Metrics to surface
- latest chunk counts by department manifest
- latest error counts by manifest
- corpus readiness by company
- maturity deltas by department
- newest operator packets and decisions

## Refresh rule
The console is only considered fresh when the latest summary and monitor artifacts have timestamps newer than the prior run.
