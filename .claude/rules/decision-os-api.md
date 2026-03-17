---
paths:
  - "apps/decision_os/**"
---

# Decision OS API Rules

## Stack
- FastAPI with Pydantic v2 models
- Port: 8420
- CORS enabled for local development

## Architecture Pattern
- **Models** (`models.py`): Pydantic BaseModel classes for all data structures
- **Store** (`store.py`): File-backed YAML persistence layer
- **API** (`api.py`): FastAPI router with typed endpoints
- **Operator** (`operator.py`): High-level orchestration logic

## Key Modules
- `customer_user_studio.py` — Customer persona and scenario management
- `maturity_surfaces.py` — Maturity scoring and surface tracking
- `simulated_maturity.py` — Simulated maturity harness

## Data Storage
- All data in `apps/decision_os/data/`
- Runs: `data/runs/run-<id>.yaml`
- Artifacts: `data/artifacts/`
- Evidence: `data/evidence/`
- Store reads/writes YAML files — no database

## Debate Framework
- Decisions go through propose → debate → adopt/reject flow
- Each decision has evidence, arguments for/against, and outcome
- Link decisions to capabilities and projects

## Testing
```bash
cd apps/decision_os
python -m pytest tests/ -v
```
- Test models: `tests/test_models.py`
- Test store: `tests/test_store.py`
- Test API: `tests/test_api_operator.py`
- Test modules: `tests/test_customer_user_studio.py`, `tests/test_simulated_maturity.py`

## Import Pattern
```python
from apps.decision_os.models import DecisionRecord, CapabilityScore
from apps.decision_os.store import DecisionStore
```

## API Conventions
- All endpoints return Pydantic models
- Use `HTTPException` for errors with appropriate status codes
- Validate input with Pydantic, not manual checks
