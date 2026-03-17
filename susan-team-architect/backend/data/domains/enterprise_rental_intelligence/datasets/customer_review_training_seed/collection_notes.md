# Enterprise rental review collection notes (2026-03-12)

## Objective
Populate a starter folder with whatever can be collected immediately for Enterprise customer-review training.

## What was collected
- Source inventory with prioritized review platforms + Exa query targets.
- Direct network probe output for the highest-priority review URLs.

## Current blocker
All direct HTTPS probes to review platforms returned proxy tunnel `403 Forbidden` errors in this environment, so page content could not be fetched during this run.

## Next best actions
1. Run the manifest through Susan on a runtime that has outbound access + configured API keys:
   - `scripts/susan_cli.py scrape batch data/scrape_manifests/enterprise_rental_customer_reviews_training.yaml`
2. If direct scraping remains blocked, switch to Exa-first ingestion and archive raw result URLs into this dataset folder.
3. Add a normalized `review_taxonomy.yaml` once at least 200 review snippets are ingested (pickup flow, upsell friction, billing clarity, vehicle condition, agent behavior, resolution speed).

## Multi-provider run executed
- Script: `scripts/run_enterprise_rental_multitool_scrape.py`
- Run artifact folder: `datasets/customer_review_training_seed/runs/enterprise_multitool_20260312T201124Z/`
- Tools attempted in one run: Exa, Firecrawl, Brave, Jina ("Jing" alias), Apify.
- Outcome in this environment:
  - Exa skipped (missing `EXA_API_KEY`)
  - Firecrawl skipped (missing `FIRECRAWL_API_KEY`)
  - Brave skipped (missing `BRAVE_API_KEY`)
  - Apify skipped (missing `APIFY_TOKEN`)
  - Jina attempted but blocked by `403 Forbidden`

## Team key bootstrap update
- Updated runner to auto-load team env files when present:
  - `susan-team-architect/backend/.env`
  - `.env` at repo root
  - `.startup-os/.env`
- Added env alias support:
  - Brave: `BRAVE_API_KEY` or `BRAVE_SEARCH_API_KEY`
  - Jina/Jing: `JINA_API_KEY` or `JING_API_KEY`
  - Apify: `APIFY_TOKEN` or `APIFY_API_TOKEN`

## Latest run
- Run artifact folder: `datasets/customer_review_training_seed/runs/enterprise_multitool_20260312T203058Z/`
- `team_env_files_loaded` was empty in this environment, so no team key file was available at runtime.

## Latest run (requested re-run)
- Run artifact folder: `datasets/customer_review_training_seed/runs/enterprise_multitool_20260312T204814Z/`
- Folder size in this environment: `16K` (no provider payloads due key/network constraints)
- To target MB–GB scale, provider keys must be loaded and runs repeated with larger query/url batches.

## Latest run (analysis pass)
- Run artifact folder: `datasets/customer_review_training_seed/runs/enterprise_multitool_20260312T210138Z/`
- Folder size in this environment: `16K`
- Notes: still key/network constrained; suitable for pipeline validation, not full market evidence volume.
