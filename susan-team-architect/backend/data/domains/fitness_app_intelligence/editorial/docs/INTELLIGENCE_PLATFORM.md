# Fitness Intelligence Platform Foundation

This repository now supports two layers:

1. Editorial markdown research in `apps/`, `analysis/`, and `docs/`
2. Structured intelligence and ingestion tooling via `fitness_intel/`

## What Changed

- Added a canonical schema for `App`, `Company`, `Feature`, `Metric`, `Claim`, `Source`, `Evidence`, `PricingPlan`, `Integration`, and `Opportunity`.
- Added a markdown backfill pipeline that converts app profiles into machine-readable records.
- Added RAG-ready chunk generation with metadata for filters and provenance.
- Added a local hybrid retriever for deterministic metadata filtering plus lexical ranking.
- Added pilot structured records in `data/pilot/`.
- Added a compatibility layer that exports chunk payloads into the shape expected by `Startup-Intelligence-OS`.

## Operating Model

- Markdown remains the editorial layer.
- Structured records become the system of record for reusable facts and claims.
- Raw and editorial documents are chunked for retrieval.
- Sources and evidence are attached at the fact level for auditability.

## Commands

From the repo root:

```bash
python -m fitness_intel --repo-root . inventory
python -m fitness_intel --repo-root . backfill --limit 10
python -m fitness_intel --repo-root . chunks
python -m fitness_intel --repo-root . audit
python -m fitness_intel --repo-root . query "GLP-1 strength training"
```

## Startup-Intelligence-OS Integration

`Startup-Intelligence-OS` should host shared services for ingestion orchestration, storage, embeddings, retrieval, and analyst workflows. This repo now exports a fitness-specific domain pack contract via:

- `fitness_intel/startup_os.py`
- `data/contracts/startup_os_domain_pack.yaml`

The intended flow is:

1. Backfill structured app records from markdown.
2. Build chunk manifests from markdown and future raw-source captures.
3. Export Startup-OS-compatible chunk payloads.
4. Ingest those payloads into the shared RAG backend.

