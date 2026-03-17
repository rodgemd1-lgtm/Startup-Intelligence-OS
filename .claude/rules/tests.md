---
paths:
  - "**/tests/**"
  - "**/test_*"
---

# Test Rules

## Framework
- pytest for all Python tests
- Tests mirror source structure in `tests/` directories

## Running Tests
```bash
# Decision OS tests
cd apps/decision_os && python -m pytest tests/ -v

# Susan backend tests
cd susan-team-architect/backend && source .venv/bin/activate && python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_models.py -v

# Specific test
python -m pytest tests/test_models.py::test_decision_record -v
```

## Import Patterns
```python
# Decision OS
from apps.decision_os.models import DecisionRecord
from apps.decision_os.store import DecisionStore

# Susan backend
from rag_engine.batch import BatchProcessor
from control_plane.catalog import AgentCatalog
```

## Conventions
- Test files: `test_<module>.py`
- Test functions: `test_<behavior>()`
- Use fixtures for shared setup
- Test both happy path and error cases
- Mock external services (Supabase, Voyage AI, web APIs)
- Keep tests fast — no real network calls in unit tests
