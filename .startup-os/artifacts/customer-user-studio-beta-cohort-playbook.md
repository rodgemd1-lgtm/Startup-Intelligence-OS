# Customer User Studio — Beta Cohort Playbook

## Objective
Operationalize beta tester feedback in a way that is comparable with synthetic customer-agent evidence.

## Cohort design
- Cohort A: new users (first-week onboarding)
- Cohort B: active users (weekly recurring workflows)
- Cohort C: power users (advanced and edge-case workflows)

## Governance
- Use explicit participant consent with scope of data capture
- Redact sensitive data from session artifacts
- Store only structured findings and linked evidence references

## Instrumentation requirements
- Session replay references
- Error telemetry (console/network)
- Task-level completion metrics
- Post-session preference survey (likes/dislikes/future wants)

## Reconciliation with synthetic users
- Compare synthetic-vs-beta by scenario and module
- Compute alignment score by outcome, friction cluster, and preference trend
- Escalate mismatches over threshold to decision room review

## Escalation policy
- Critical errors in beta: block release until verified fix
- High divergence from synthetic findings: run targeted scenario expansion
- Repeated preference requests: promote to roadmap candidate
