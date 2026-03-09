# Founder Technical Systems Baseline

The startup foundry should not rely on ad hoc architecture choices.

## Required technical systems

- central backend for routing, retrieval, and orchestration
- company registry and domain registry
- ingestion pipelines with provenance
- metric and event taxonomy
- experiment registry
- decision-log store
- output artifact store
- Supabase-backed operational data and knowledge retrieval

## Baseline rules

- architecture should be simple, composable, and inspectable
- retrieval should favor grounded evidence and clearly labeled source types
- company-level work should be able to pull shared reusable doctrine without forking it
- every company should inherit logging, cadence, and trust defaults from the foundry

## Technical gaps to close

- canonical company genome schema
- first-class decision log
- experiment registry and feature-gate model
- source graph and contradiction tracking
- automatic memory writeback after executions
