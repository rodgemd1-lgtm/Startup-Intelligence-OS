# Knowledge Lifecycle

Reference doc for V3a knowledge lifecycle management. Defines states, transition rules, freshness windows, and auto-refresh dispatch logic.

## States

| State | Description | Entry Trigger | Exit Trigger |
|-------|-------------|---------------|--------------|
| DRAFT | New data ingested, not yet validated | Initial scrape or ingest | Manual review confirms accuracy |
| REVIEW | Flagged for quality check | Auto: first ingest of new domain; Manual: analyst flags | Reviewer marks PUBLISHED or rejects |
| PUBLISHED | Validated, actively used by agents | Review passes quality gate | Age exceeds domain freshness window |
| AGING | Approaching staleness threshold | Within 7 days of freshness window expiry | Reaches expiry OR manual refresh |
| STALE | Past freshness window, unreliable | Age exceeds domain freshness window | Refresh cycle completes |
| REFRESH | Active re-research in progress | Auto-refresh triggered on STALE record | New data ingested, returns to REVIEW |

## State Flow

```
DRAFT → REVIEW → PUBLISHED → AGING → STALE → REFRESH → REVIEW → ...
```

## Freshness Windows (per domain)

### Oracle Health
| Domain | Window | Cadence |
|--------|--------|---------|
| market_intelligence | 30 days | Monthly |
| clinical_operational | 90 days | Quarterly |
| regulatory_enterprise | 45 days | ~6 weeks |
| marketing_narrative | 30 days | Monthly |
| firecrawl_screenshots | 21 days | ~3 weeks |
| competitor_profiles | 30 days | Monthly |

### Fitness App (TransformFit)
| Domain | Window | Cadence |
|--------|--------|---------|
| pricing | 30 days | Monthly |
| app_features | 90 days | Quarterly |
| company_metrics | 90 days | Quarterly |
| market_reports | 180 days | Semiannual |

### Default (all other domains)
| Window | Cadence |
|--------|---------|
| 92 days | Quarterly |

Matches `FRESHNESS_WINDOWS["quarterly"]` in `control_plane/audits.py`.

## Transition Rules

### Automatic Transitions
1. **PUBLISHED → AGING**: Record age reaches `window - 7 days`
2. **AGING → STALE**: Record age exceeds `window`
3. **STALE → REFRESH**: Auto-refresh trigger fires (stale-watchdog finds matching scheduled task)
4. **REFRESH → REVIEW**: New data ingested for the domain

### Manual Transitions
1. **DRAFT → REVIEW**: Analyst flags for review
2. **REVIEW → PUBLISHED**: Reviewer confirms quality
3. **REVIEW → DRAFT**: Reviewer rejects, needs rework
4. **Any → STALE**: Analyst manually marks unreliable

## Auto-Refresh Dispatch

When stale-watchdog detects STALE records:

1. Check domain against refresh task inventory (11 biweekly tasks exist for Oracle Health)
2. If a scheduled refresh task exists → log "covered by scheduled task [task-name]"
3. If NO scheduled task exists → flag "NEEDS MANUAL RESEARCH" in freshness report
4. Never auto-trigger expensive scrapes without a matching scheduled task

### Covered Domains (biweekly refresh tasks)
- ambient-ai, cloud-infra, cybersecurity, data-analytics, interop
- life-sciences, patient-portal, rcm, regulatory, vbc, workforce

### Uncovered Domains (require manual research)
- Any new domain without a scheduled task
- Cross-company domains (Alex Recruiting, James OS)

## Integration Points

| System | File | Function |
|--------|------|----------|
| Control plane | `control_plane/audits.py` | `freshness_status()` — returns "stale" or "current" |
| Gap detector | `research_daemon/gap_detector.py` | `detect_stale_data()` — scores domain coverage 0.0-1.0 |
| Memory | `memory/consolidator.py` | Decay/promote/prune tips by age and access frequency |
| Stale watchdog | Scheduled task (Sun 3 AM) | Weekly KB freshness audit with file age thresholds |
| Domain refreshers | 11 scheduled tasks (biweekly) | Auto-refresh Oracle Health domains |
| Freshness command | `.claude/commands/knowledge-freshness.md` | On-demand audit with lifecycle state output |

## Output Location

All freshness reports save to: `.startup-os/briefs/freshness-YYYY-MM-DD.md`
