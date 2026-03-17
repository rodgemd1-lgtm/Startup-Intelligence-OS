# Decision OS Guide

## Overview
The Decision OS is a FastAPI application that manages the decision lifecycle: propose, debate, adopt/reject. It also handles maturity scoring, customer personas, and simulated maturity testing.

## API Endpoints (Port 8420)

### Core Decision Endpoints
- `GET /decisions` — List all decisions
- `GET /decisions/{id}` — Get decision by ID
- `POST /decisions` — Create new decision
- `PUT /decisions/{id}` — Update decision
- `POST /decisions/{id}/debate` — Add debate entry

### Maturity Endpoints
- `GET /maturity/surfaces` — List maturity surfaces
- `POST /maturity/score` — Score a capability
- `GET /maturity/dashboard` — Get maturity dashboard

### Customer User Studio
- `GET /customer/personas` — List personas
- `POST /customer/personas` — Create persona
- `GET /customer/scenarios` — List scenarios
- `POST /customer/scenarios` — Create scenario

## Pydantic Models (`models.py`)

### Key Models
```python
class DecisionRecord(BaseModel):
    id: str
    name: str
    description: str
    status: Literal["proposed", "adopted", "rejected", "superseded"]
    evidence: list[str]
    outcome: Optional[str]

class CapabilityScore(BaseModel):
    capability_id: str
    current: int  # 0-5
    target: int   # 0-5
    evidence: list[str]

class DebateEntry(BaseModel):
    position: Literal["for", "against", "neutral"]
    argument: str
    evidence: Optional[list[str]]
```

## Store Pattern (`store.py`)

The store is a file-backed YAML persistence layer:
```python
class DecisionStore:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def save_run(self, run: RunRecord) -> Path:
        # Writes to data/runs/run-<id>.yaml

    def load_run(self, run_id: str) -> RunRecord:
        # Reads from data/runs/run-<id>.yaml

    def list_runs(self) -> list[RunRecord]:
        # Lists all runs in data/runs/
```

## Debate Framework

Decisions flow through a structured debate:
1. **Propose** — Create decision with initial evidence
2. **Debate** — Add arguments for/against with evidence
3. **Decide** — Adopt or reject based on debate outcome
4. **Link** — Connect to capabilities and projects

## Running
```bash
cd apps/decision_os
uvicorn api:app --port 8420 --reload
```

## Testing
```bash
cd apps/decision_os
python -m pytest tests/ -v
```
