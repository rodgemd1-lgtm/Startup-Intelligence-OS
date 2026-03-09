# Fitness App Intelligence Domain

This directory is the merged home for the former `fitness-app-intelligence` repository.

## Contents

- `editorial/apps/`, `editorial/analysis/`, `editorial/docs/`: editorial markdown corpus
- `pilot/`, `registry/`, `contracts/`: structured seed data and domain contract
- `../../../../fitness_intel/`: parsing, backfill, chunking, retrieval, and export code

## Ingestion

From `susan-team-architect/backend/`:

```bash
python3 scripts/ingest_fitness_intelligence.py
```

This writes:

- `artifacts/fitness_intelligence/inventory.json`
- `artifacts/fitness_intelligence/app_records.jsonl`
- `artifacts/fitness_intelligence/chunks.jsonl`
- `artifacts/fitness_intelligence/startup_os_chunks.jsonl`

Those `startup_os_chunks` records are shaped for the existing `knowledge_chunks` ingestion path in Susan's RAG backend.
