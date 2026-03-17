# Job Studio Training Factory Locator

## Purpose

This file registers the Job Studio Training Factory corpus, extraction pipeline, and local source layers for strategist AI enablement, Ellen training, behavioral-science grounding, and market and competitive intelligence training.

## Canonical local roots

- generated corpus root: `/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/data/studio_assets/generated/job_studio_training_factory`
- summary artifact root: `/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/artifacts/job_studio_training_factory_corpus`
- Oracle source corpus: `/Users/mikerodgers/Desktop/OH Marketing and Competitive Intelligence`
- Oracle repo-local locator: `/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/data/studio_assets/companies/oracle-health-ai-enablement/OH_MARKETING_AND_COMPETITIVE_INTELLIGENCE_LOCATOR.md`

## Primary source layers

1. Oracle Health marketing and competitive intelligence raw corpus
2. AI Enablement Oracle Chat repo
3. Oracle Health vendor intelligence repo
4. Founder Intelligence OS repo
5. UX Design Scraper repo
6. Susan behavioral-science and training docs

## Expected generated outputs

- `oracle_health_extracted/`
- `repo_harvest/`
- `behavioral_science_seed/`
- `manifest.json`
- `summary.json`
- `failures.json`

## Access protocol

- Use `mike-job-studio` as the company namespace when routing Job Studio training asks.
- Attach context sources from this locator and the Oracle locator before synthesis.
- Keep personal memory and linked company corpus references separate in recommendations.
- Prefer named examples and extracted text over ungrounded summaries.

## Build and ingest entrypoints

- build corpus: `python3 -m scripts.build_job_studio_training_factory_corpus`
- ingest normalized outputs: `python3 -m scripts.ingest_job_studio_training_factory`

## Notes

- This locator is the governed entrypoint for training-factory data access.
- Live crawl manifests extend this corpus once external ingestion keys are configured.
- Current measured checkpoint: `1,080` extracted-or-cached documents and `11,777,481` extracted characters are already available in the active run while the Oracle binary sweep continues.
