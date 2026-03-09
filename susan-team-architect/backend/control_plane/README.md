# Control Plane

Susan's orchestration control plane. Manages foundry operations, agent catalog, protocol execution, and artifact writeback.

## Runtime boundary

This directory is a protected runtime surface. Changes should be minimal, explicit, and validated. Do not rewrite behavior here without operator approval.

## Key modules

- `main.py` — control plane entry point
- `foundry.py` / `foundry_ops.py` — foundry orchestration
- `catalog.py` — agent and capability catalog
- `protocols.py` — operational protocols
- `audits.py` — validation and compliance audits
- `writeback.py` — artifact storage and persistence
- `schemas.py` — data validation schemas
- `prompts.py` — system prompt management
- `jobs.py` — background job scheduling
