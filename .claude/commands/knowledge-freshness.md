---
description: Audit Susan RAG knowledge freshness — identify stale records, coverage gaps, lifecycle states, and domain health across all companies
allowed-tools: Bash, Read, Agent, Grep, Glob
---

Run a knowledge freshness audit across Susan's RAG with lifecycle state assignment.

Reference: `.claude/docs/knowledge-lifecycle.md` for state definitions and freshness windows.

## Audit Steps

1. **Count total knowledge chunks** by querying Susan:
!`cd /Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend && ./.venv/bin/python scripts/susan_cli.py count-knowledge 2>/dev/null || echo "Susan CLI not available — check backend setup"`

2. **Check for stale data signals**:
   - Records tagged "General" that need proper domain tags
   - Companies with no recent research (>30 days since last ingest)
   - Data types with low coverage

3. **Assign lifecycle states** per domain using freshness windows from `.claude/docs/knowledge-lifecycle.md`:
   - **PUBLISHED**: Last ingest within freshness window
   - **AGING**: Within 7 days of freshness window expiry
   - **STALE**: Past freshness window
   - **REFRESH**: STALE but has a matching biweekly refresh task (covered)
   - **DRAFT**: No ingest date found or newly added domain

   Freshness windows to use:
   - Oracle Health: market_intelligence (30d), clinical_operational (90d), regulatory_enterprise (45d), marketing_narrative (30d), firecrawl_screenshots (21d), competitor_profiles (30d)
   - Fitness/TransformFit: pricing (30d), app_features (90d), company_metrics (90d), market_reports (180d)
   - Default: 92 days (quarterly)

4. **Produce a freshness report** in this format:

```markdown
# Knowledge Freshness Report — {date}

## Summary
- Total chunks: {count}
- Companies tracked: {count}
- Lifecycle breakdown: {N} PUBLISHED, {N} AGING, {N} STALE, {N} REFRESH, {N} DRAFT

## Lifecycle Status by Domain
| Domain | Last Ingest | Window | State | Auto-Refresh? | Action Needed |
|--------|-------------|--------|-------|---------------|---------------|
| {name} | {date}      | {N days} | {STATE} | {yes: task-name / no} | {none/aging-alert/needs-refresh/needs-research} |

## By Company
| Company | Chunks | Last Updated | Freshness | Action Needed |
|---------|--------|-------------|-----------|---------------|
| {name}  | {n}    | {date}      | {fresh/aging/stale} | {action or "none"} |

## Coverage Gaps
| Domain | Coverage Score | Gap |
|--------|---------------|-----|
| {name} | {0.0-1.0}     | {what's missing} |

## Recommendations
1. {Highest priority — STALE domains with no auto-refresh}
2. {Second priority — AGING domains approaching expiry}
3. {Third priority — DRAFT domains needing initial review}
```

5. **Save the report** to `.startup-os/briefs/freshness-{YYYY-MM-DD}.md`

6. **If stale records >20%**, flag this as a V3a alert:
   "Knowledge freshness below threshold. Recommend running `/scrape` or `/susan-refresh` for affected domains."

Tag output: DRAFT (freshness data requires verification against live Supabase)
