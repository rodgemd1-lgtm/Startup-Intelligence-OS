# Mike Job Studio Data Locator

## Purpose

This file registers the currently attached Mike Job Studio datasets inside Startup Intelligence OS.

## Mike Job Studio email corpus

- company_id: `mike-job-studio`
- data_type (all): `mike_job_studio_email`
- data_type (work): `mike_job_studio_email_work`
- data_type (authored): `mike_job_studio_email_authored`
- corpus path: `/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/data/studio_assets/generated/mike-job-studio/email_corpus`
- message path: `/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/data/studio_assets/generated/mike-job-studio/email_corpus/messages`
- work message path: `/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/data/studio_assets/generated/mike-job-studio/email_corpus/work_messages`
- authored message path: `/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/data/studio_assets/generated/mike-job-studio/email_corpus/authored_messages`
- summary path: `/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/artifacts/mike_job_studio_email_corpus/summary.json`
- unique markdown emails written: `111`
- work-related markdown emails written: `26`
- authored by Mike: `6`
- available cache window start: `2026-01-20T17:52:31.214545`
- available cache window end: `2026-03-10T12:52:31.563437`

## Coverage caveat

This corpus reflects the locally available Outlook cache on disk. The discovered cache window is narrower than a full trailing year, so this is not a confirmed full-mailbox export.

## Linked Oracle Health corpus

- Oracle Health raw corpus path: `/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/data/studio_assets/companies/oracle-health-ai-enablement/raw-docs`
- Oracle Health locator: `/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/data/studio_assets/companies/oracle-health-ai-enablement/OH_MARKETING_AND_COMPETITIVE_INTELLIGENCE_LOCATOR.md`
- Oracle Health Supabase bucket: `oracle-health-corpus`
- Oracle Health storage prefix: `oracle-health-ai-enablement/market-intelligence`
- Oracle Health uploaded objects: `566`
- Oracle Health failed objects: `14`

## Mike Job Studio Oracle Health storage mirror

- mirror bucket: `oracle-health-corpus`
- mirror prefix: `mike-job-studio/linked-corpora/oracle-health-market-intelligence`
- files represented: `580`
- remote copies created: `644`
- local repair uploads: `14`
- skipped existing objects: `0`
- failed mirror operations: `0`
- manifest path: `/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/artifacts/mike_job_studio_oracle_health_storage/manifest.json`

## Retrieval instructions

Use the Mike Job Studio company when querying the email corpus. Use the locator files to jump into linked raw corpora that are not fully embedded as markdown.

- Susan company_id: `mike-job-studio`
- Query authored writing style with data_type: `mike_job_studio_email_authored`
- Query work-memory with data_type: `mike_job_studio_email_work`
- Query broad cache recall with data_type: `mike_job_studio_email`
