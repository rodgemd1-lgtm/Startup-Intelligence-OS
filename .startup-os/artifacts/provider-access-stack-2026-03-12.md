# Provider Access Stack

**Date:** 2026-03-12  
**Purpose:** Track the live provider key stack for Startup Intelligence OS without committing secrets.

## Secure storage rule
- Live secrets stay only in the ignored file [backend/.env](/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/.env).
- The tracked template is [backend/.env.example](/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/.env.example).
- Health checks run through [provider_key_healthcheck.py](/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/scripts/provider_key_healthcheck.py).

## Current status

| Provider | Status | Notes |
|---|---|---|
| Exa | working | validated through live scrape run |
| Brave Search | working | validated through live scrape run |
| Firecrawl | working | validated through live scrape run |
| Jina | working | validated through live scrape run and direct authenticated probe |
| Supabase | working | healthcheck confirms the existing service key and URL are valid; ingestion now accepts `SUPABASE_SERVICE_KEY` as alias |
| Apify | working | healthcheck confirms the existing `APIFY_API_KEY`; runner now accepts that alias |
| OpenAI | working | key added to the ignored backend env file and validated through the provider healthcheck |

## Operational rule
- Do not commit live keys.
- Keep aliases normalized in code so the ignored env file can remain the single source of truth.
- Use the healthcheck script before large scrape or ingest runs.
