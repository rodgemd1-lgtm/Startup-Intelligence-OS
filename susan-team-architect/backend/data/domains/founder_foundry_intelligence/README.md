# Founder Foundry Intelligence

This domain is the evidence, doctrine, and operating layer for building companies through Susan's production-grade startup foundry.

## Purpose

- turn founder knowledge and frameworks into queryable company-building systems
- promote Founder Intelligence OS into a first-class company context instead of treating it as generic shared knowledge
- give Susan a reusable company-building kernel for new domains, studios, governance, and operating cadences
- keep the central backend authoritative while making the founder repo a native workspace

## Main layers

- `editorial`
  - curated foundry briefs, build matrices, and operating cadences
- `artifact_inventory.yaml`
  - machine-readable founder artifacts used by stage gates and blueprint rendering
- `schemas`
  - machine-readable entry shapes for decision logs, experiment registry, KPI metrics, and source claims
- `datasets`
  - official-source manifests for agent systems, design systems, AI governance, accessibility, security, and founder operating frameworks

## Retrieval types used

- `business_strategy`
- `operational_protocols`
- `expert_knowledge`
- `market_research`
- `technical_docs`
- `legal_compliance`
- `security`
- `ux_research`
- `studio_open_research`

## Ingestion

Run:

```bash
./.venv/bin/python scripts/ingest_founder_intelligence.py
```

That script:

- ingests founder repo personas, frameworks, and docs
- ingests the founder foundry domain briefs
- scrapes the official open-source references in the manifest
- stores everything into Supabase under company `founder-intelligence-os`
