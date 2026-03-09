# TransformFit Training Intelligence

This domain is the evidence and structured-data layer for TransformFit's workout-program and training-research studios.

## Purpose

- ground workout design in open exercise-science evidence instead of generic fitness prompting
- maintain a reusable exercise catalog and user-research corpus for programming decisions
- give TransformFit a queryable source layer for splits, progression logic, exercise substitution, adherence risks, and competitive program expectations
- define the coaching relationship model, memory rules, and session-level trust architecture
- define the staffing, role, and expert-council architecture needed to build TransformFit as a company

## Main layers

- `editorial`
  - curated studio briefs and source maps
- `datasets`
  - public-source manifests for guidelines, open-access reviews, structured exercise catalogs, Reddit user research, and app-store reviews
  - operational, AI-product, and coaching-science sources that inform org design and coach-system quality

## Retrieval types used

- `training_research`
- `exercise_catalog`
- `exercise_science`
- `sleep_recovery`
- `nutrition`
- `user_research`
- `coaching_architecture`
- `session_ux`
- `sports_psychology`
- `behavioral_economics`
- `business_strategy`
- `market_research`
- `operational_protocols`
- `expert_knowledge`
- `visual_asset`
- `program_library`
- `guru_research`
- `frontier_academic_research`
- `consumer_failure_patterns`
- `predictive_coaching`
- `simulation_models`

## Ingestion

Run:

```bash
./.venv/bin/python scripts/ingest_transformfit_training_domain.py
```

That script:

- ingests the editorial briefs
- scrapes the public web sources
- pulls the structured exercise catalogs
- ingests Reddit and App Store user research
- stores everything into Supabase under company `transformfit`
