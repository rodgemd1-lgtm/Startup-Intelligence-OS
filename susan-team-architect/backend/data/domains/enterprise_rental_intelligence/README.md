# Enterprise Rental Intelligence

This domain captures customer-review and service-training intelligence for Enterprise Rent-A-Car.

## Purpose

- build a reusable corpus of customer experience signals from public review sources
- map recurring complaint and praise patterns into trainable service categories
- maintain traceable evidence files under `datasets/customer_review_training_seed/`

## Datasets

- `datasets/customer_review_training_seed/source_inventory.yaml` — candidate and priority sources
- `datasets/customer_review_training_seed/collection_probe_2026-03-12.json` — network probe results from this workspace
- `datasets/customer_review_training_seed/collection_notes.md` — operator notes + unblock actions

## Ingestion entrypoint

- Scrape manifest: `data/scrape_manifests/enterprise_rental_customer_reviews_training.yaml`
- Execute with: `scripts/susan_cli.py scrape batch data/scrape_manifests/enterprise_rental_customer_reviews_training.yaml`
