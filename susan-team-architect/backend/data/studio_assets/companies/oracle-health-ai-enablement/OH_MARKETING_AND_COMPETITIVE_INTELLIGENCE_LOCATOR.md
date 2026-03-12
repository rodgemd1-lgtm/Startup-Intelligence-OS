# Oracle Health Marketing And Competitive Intelligence Locator

## Purpose

This file registers the local Oracle Health marketing and competitive intelligence corpus for Mike's Oracle Health studio workflows inside Startup Intelligence OS.

## Canonical local path

- repo-local pointer: `/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/data/studio_assets/companies/oracle-health-ai-enablement/raw-docs`
- source corpus: `/Users/mikerodgers/Desktop/OH Marketing and Competitive Intelligence`

## Corpus status

- verification date: `2026-03-10`
- company_id: `oracle-health-ai-enablement`
- collection label: `OH Marketing and Competitive Intelligence`
- source mirror used: `/Users/mikerodgers/Desktop/Oracle Work/Coyp of One Drive Files 10072025`
- source files counted: `580`
- destination files counted: `580`
- verification result: `0 missing`, `0 size mismatches`

## File type coverage

- `220` `.docx`
- `122` `.pptx`
- `122` `.pdf`
- `58` `.xlsx`
- `15` `.eml`
- `10` `.mp4`
- `9` `.msg`
- `4` `.xlsm`
- `3` `.xlsb`
- `3` `.vsdx`
- `2` `.url`
- `2` `.png`
- `2` `.m4a`
- `2` `.doc`
- `2` `.csv`
- `1` `.xls`
- `1` `.lnk`
- `1` `.DS_Store`
- `1` `.conf`

## Retrieval reality

The current Susan ingestors in `susan-team-architect/backend/rag_engine/ingestion/` only index Markdown and selected web/dataset sources. This corpus is fully present on disk, but the Word, PowerPoint, PDF, spreadsheet, email, and media binaries are not automatically embedded into pgvector yet.

What Susan can retrieve today:
- this locator file
- the existing Oracle Health domain markdown
- the existing Oracle Health studio memory markdown

What Claude Code can do today:
- open the repo-local pointer path
- inspect any source file directly from the local filesystem
- convert selected files into markdown for ingestion
- build a binary-document ingestor if needed

## Recommended Claude Code task prompt

```text
Open /Users/mikerodgers/Startup-Intelligence-OS.

Use the Oracle Health company_id `oracle-health-ai-enablement`.

The Oracle Health marketing and competitive intelligence corpus is mounted at:
/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/data/studio_assets/companies/oracle-health-ai-enablement/raw-docs

Start by reading:
/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/data/studio_assets/companies/oracle-health-ai-enablement/OH_MARKETING_AND_COMPETITIVE_INTELLIGENCE_LOCATOR.md

Treat that raw-docs path as the canonical local corpus for Word docs, PowerPoints, PDFs, spreadsheets, emails, and media.

If I ask for search or synthesis across that corpus, first inspect the files directly from disk. If I ask for RAG indexing, convert the highest-value documents into markdown under the Oracle Health domain/studio asset paths and ingest them for company_id oracle-health-ai-enablement.
```

## Notes

- This confirms full fidelity against the local SharePoint mirror used as source on `2026-03-10`.
- This does **not** confirm parity with the live SharePoint site on `2026-03-10`, because the live site required Microsoft login and was not accessible from the automation session.
