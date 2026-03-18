---
description: Audit Susan RAG knowledge freshness — identify stale records, coverage gaps, and domain health across all companies
allowed-tools: Bash, Read, Agent, Grep, Glob
---

Run a knowledge freshness audit across Susan's RAG.

## Audit Steps

1. **Count total knowledge chunks** by querying Susan:
!`cd /Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend && ./.venv/bin/python scripts/susan_cli.py count-knowledge 2>/dev/null || echo "Susan CLI not available — check backend setup"`

2. **Check for stale data signals**:
   - Records tagged "General" that need proper domain tags
   - Companies with no recent research (>30 days since last ingest)
   - Data types with low coverage

3. **Produce a freshness report** in this format:

```markdown
# Knowledge Freshness Report — {date}

## Summary
- Total chunks: {count}
- Companies tracked: {count}
- Stale records (>30 days): {count} ({percentage}%)
- Domain coverage gaps: {list}

## By Company
| Company | Chunks | Last Updated | Freshness | Action Needed |
|---------|--------|-------------|-----------|---------------|
| {name}  | {n}    | {date}      | {fresh/aging/stale} | {action or "none"} |

## By Domain
| Domain | Chunks | Coverage | Gap |
|--------|--------|----------|-----|
| {name} | {n}    | {good/partial/poor} | {what's missing} |

## Recommendations
1. {Highest priority refresh action}
2. {Second priority}
3. {Third priority}
```

4. **If stale records >20%**, flag this as a V2 alert:
   "Knowledge freshness below threshold. Recommend running `/scrape` or `/susan-refresh` for affected domains."

Tag output: DRAFT (freshness data requires verification against live Supabase)
