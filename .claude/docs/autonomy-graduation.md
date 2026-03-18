# Autonomy Graduation

Reference doc for V3a autonomy graduation tracking. Defines tiers, accuracy metrics, promotion criteria, and the 30-day observation window protocol.

## Graduation Tiers

| Tier | Name | Description | Human Involvement |
|------|------|-------------|-------------------|
| T0 | DRAFT | New workflow, unproven | Human triggers + reviews every output |
| T1 | AUTO | Running on schedule, human reviews output | Auto-triggered, human reviews before action |
| T2 | SUPERVISED | Human reviews weekly summary, not every output | Auto-triggered, auto-delivered, weekly spot-check |
| T3 | AUTONOMOUS | Fully autonomous, human reviews exceptions only | Auto-triggered, auto-delivered, alert on anomaly |

## Current Workflows and Tiers

| Workflow | Current Tier | Started | Accuracy | Notes |
|----------|-------------|---------|----------|-------|
| ARIA Daily Brief | T1 (AUTO) | 2026-03-18 | — | Emailing at 6:39 AM, Mike reviews |
| Oracle Health Morning Brief | T1 (AUTO) | 2026-03-18 | — | Emailing at 6:02 AM weekdays |
| LEDGER Funnel Report | T0 (DRAFT) | 2026-03-18 | — | Manually triggered, not yet scheduled |
| SCOUT Competitive Signals | T0 (DRAFT) | 2026-03-18 | — | Agent defined, not yet scheduled |
| SENTINEL-HEALTH Compliance | T0 (DRAFT) | 2026-03-18 | — | Agent defined, runs on-demand |
| Knowledge Freshness Audit | T1 (AUTO) | 2026-03-18 | — | Scheduled weekly |

## Accuracy Metrics (per workflow type)

### Brief Workflows (ARIA, Oracle Health, SCOUT)
- **Signal accuracy**: Were the signals/priorities correct? (1-5 scale)
- **Actionability**: Did the brief lead to a concrete action? (yes/no)
- **False positives**: Did the brief flag something that didn't matter? (count)
- **Missing signals**: Did something important happen that the brief missed? (count)

**Composite score**: `(signal_accuracy * 20) - (false_positives * 10) - (missing_signals * 15) + (actionability * 10)`
- Max score per observation: 110
- Passing threshold for promotion: 80+ average over observation window

### Compliance Workflows (SENTINEL-HEALTH)
- **Correct classifications**: Output matched human judgment (count)
- **False blocks**: Blocked content that was actually safe (count)
- **Missed violations**: Let through content that should have been flagged (count)

**Composite score**: `(correct / total) * 100 - (missed_violations * 20)`
- Passing threshold: 90+ average (compliance has higher bar)

### Data Workflows (Freshness Audit, LEDGER)
- **Data accuracy**: Were the numbers/states correct? (1-5 scale)
- **Completeness**: Did it cover all domains/metrics? (percentage)
- **Timeliness**: Was it delivered on time? (yes/no)

**Composite score**: `(accuracy * 15) + (completeness * 0.5) + (timeliness * 15)`
- Max score per observation: 140
- Passing threshold: 100+ average

## Promotion Rules

### T0 → T1 (DRAFT → AUTO)
- **Requirement**: Workflow definition exists and has been validated manually at least once
- **Observation window**: None (promotion is manual decision)
- **Approver**: Mike

### T1 → T2 (AUTO → SUPERVISED)
- **Requirement**: 30-day observation window with accuracy score above threshold
- **Minimum observations**: 15 (for daily workflows) or 4 (for weekly workflows)
- **No missed violations** in the window (for compliance workflows)
- **Approver**: Jake (auto-recommend) + Mike (confirm)

### T2 → T3 (SUPERVISED → AUTONOMOUS)
- **Requirement**: 60-day observation window at T2 with accuracy above threshold
- **Minimum observations**: 30 (daily) or 8 (weekly)
- **Zero critical failures** in the window
- **Approver**: Mike only (this is a trust decision)

## Demotion Rules

A workflow can be demoted if:

| Trigger | From | To | Auto? |
|---------|------|----|-------|
| 3 consecutive accuracy scores below threshold | Any | One tier down | Yes — Jake auto-demotes and alerts Mike |
| 1 missed critical violation (compliance only) | Any | T0 (DRAFT) | Yes — immediate |
| Mike explicitly requests | Any | Any | Manual |
| Workflow definition changes significantly | Any | T1 (AUTO) max | Yes — re-prove after changes |

## Observation Window Protocol

### Daily Workflows (ARIA, Oracle Health Brief)
1. After each delivery, log: date, delivered (yes/no), score (when reviewed)
2. Score is recorded when Mike reviews and rates (can be async)
3. Unscored deliveries count as "delivered but unrated" — don't count toward promotion
4. If >50% of deliveries in a window are unrated, the window extends

### Weekly Workflows (Freshness Audit, SCOUT, LEDGER)
1. After each delivery, log: date, delivered (yes/no), score (when reviewed)
2. Same rating protocol as daily
3. Window is 30 days minimum, 4 observations minimum

### On-Demand Workflows (SENTINEL-HEALTH)
1. Log every invocation: date, input type, classification, human agreement (when available)
2. Promotion requires 10 observed classifications with human agreement scores
3. Window is 30 days minimum

## Tracker File Format

The canonical tracker lives at `.startup-os/autonomy/graduation-tracker.yaml`. See that file for the schema.

## Integration Points

- **Hook** (`bin/hooks/autonomy-tracker.sh`): PostToolUse hook that logs when AUTO-tagged outputs are generated
- **Scheduled task**: Weekly graduation review checks if any workflow qualifies for tier change
- **ARIA brief**: Includes graduation status summary when tier changes are pending
