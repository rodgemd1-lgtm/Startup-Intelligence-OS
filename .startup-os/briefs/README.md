# Agent Brief Output Hub

Standardized location for all agent-generated briefs. The Genspark bot reads this directory via GitHub API to relay content to Telegram.

## Brief Types

| Brief | Schedule | Agent | Filename Pattern |
|-------|----------|-------|-----------------|
| ARIA Daily Brief | Daily 6:39 AM | ARIA | `aria-brief-YYYY-MM-DD.md` |
| LEDGER Report | Weekly (Mon 7 AM) | LEDGER | `ledger-report-YYYY-MM-DD.md` |
| Freshness Report | Weekly (Sun 3 AM) | Stale Watchdog | `freshness-YYYY-MM-DD.md` |
| SCOUT Signals | TBD (V3a Phase 2) | SCOUT | `scout-signals-YYYY-MM-DD.md` |

## Format Requirements

All briefs must include:
1. H1 title with date
2. "The One Move Today" section (for actionable briefs)
3. Structured sections with H2/H3 headers
4. System Health section at bottom
5. No secrets, API keys, or sensitive data

## Retention

Briefs older than 30 days can be archived to `archive/briefs/`.
