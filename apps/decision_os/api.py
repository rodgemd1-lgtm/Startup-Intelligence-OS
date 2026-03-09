"""FastAPI server for the Decision & Capability OS.

Provides REST endpoints for workspace context, decisions, runs,
capabilities, artifacts, intelligence ingestion, and operator debriefs.
"""
from __future__ import annotations

import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .store import Store
from .models import Decision, DecisionStatus

# ---------------------------------------------------------------------------
# Store instance
# ---------------------------------------------------------------------------
store = Store()

# ---------------------------------------------------------------------------
# Optional engine / ingestion imports (may not exist yet)
# ---------------------------------------------------------------------------
_engine_available = False
_ingestion_available = False

try:
    from .decision_engine import DecisionEngine  # type: ignore[import-untyped]
    engine = DecisionEngine(store)
    _engine_available = True
except ImportError:
    engine = None

try:
    from .ingestion import IntelligenceIngestion  # type: ignore[import-untyped]
    ingestion = IntelligenceIngestion(store)
    _ingestion_available = True
except ImportError:
    ingestion = None

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Decision & Capability OS",
    version="0.1.0",
    description="API surface for the Startup Intelligence OS decision runtime.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3500",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------

class IngestRequest(BaseModel):
    url: str
    domain: str = ""
    topic_tags: list[str] = Field(default_factory=list)


class DecisionRunRequest(BaseModel):
    title: str
    context: str = ""
    company: str = ""
    project: str = ""
    assumptions: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Context & status
# ---------------------------------------------------------------------------

@app.get("/api/context")
def get_context() -> dict:
    """Return the workspace contract from .startup-os/workspace.yaml."""
    ctx = store.context()
    if not ctx:
        return {"error": "workspace.yaml not found or empty"}
    return ctx


@app.get("/api/status")
def get_status() -> dict:
    """Return object counts across all repositories."""
    return store.status()


@app.get("/api/debrief")
def get_debrief(operator: str = Query(default="mike")) -> dict:
    """Generate a dynamic debrief payload for the given operator."""
    ctx = store.context()
    status = store.status()

    workspace_name = ctx.get("name", "startup-intelligence-os")
    active_company = ctx.get("active_company", "unknown")
    active_project = ctx.get("active_project", "unknown")
    active_decision = ctx.get("active_decision", "unknown")
    runtime = ctx.get("runtime_source_of_truth", "susan-team-architect/backend")

    total_objects = sum(status.values())

    greeting = f"Hello, {operator.capitalize()}"

    debrief_lines = [
        f"Workspace: {workspace_name}",
        f"Runtime source of truth: {runtime}",
        f"Active company: {active_company}",
        f"Active project: {active_project}",
        f"Active decision: {active_decision}",
        f"Total objects in store: {total_objects}",
    ]

    # Build per-operator action suggestions
    mike_actions: list[str] = []
    susan_actions: list[str] = []

    if status.get("decisions", 0) == 0:
        mike_actions.append("Create the first decision record via POST /api/decision/run")
    else:
        mike_actions.append(f"Review {status['decisions']} decision(s) for status updates")

    if status.get("capabilities", 0) == 0:
        mike_actions.append("Define initial capabilities for the active company")
    else:
        mike_actions.append(f"Audit {status['capabilities']} capability(s) for maturity progression")

    if status.get("evidence", 0) < 5:
        mike_actions.append("Ingest more evidence via POST /api/ingest to strengthen decisions")

    susan_actions.append("Run capability gap analysis on active company")
    susan_actions.append("Generate team design recommendations from capability map")
    if status.get("runs", 0) > 0:
        susan_actions.append(f"Review {status['runs']} run trace(s) for quality assurance")

    actions = {"mike": mike_actions, "susan": susan_actions}

    status_lines = [
        f"{k}: {v}" for k, v in status.items()
    ]

    return {
        "greeting": greeting,
        "debrief": debrief_lines,
        "actions": actions,
        "status": status_lines,
    }


# ---------------------------------------------------------------------------
# Intelligence ingestion
# ---------------------------------------------------------------------------

@app.post("/api/ingest")
def ingest_evidence(req: IngestRequest) -> dict:
    """Ingest a URL and return the resulting evidence record."""
    if _ingestion_available and ingestion is not None:
        result = ingestion.ingest(
            url=req.url,
            domain=req.domain,
            topic_tags=req.topic_tags,
        )
        return {"ok": True, "evidence": result}

    # Stub: create a minimal Evidence record directly
    from .models import Evidence
    ev = Evidence(
        source_url=req.url,
        source_type="web",
        title=f"Ingested from {req.url}",
        domain=req.domain,
        topic_tags=req.topic_tags,
        content="[stub] Ingestion engine not available. Install decision_engine dependencies.",
        confidence=0.0,
    )
    store.evidence.save(ev)
    return {
        "ok": True,
        "stub": True,
        "message": "Ingestion engine not available. Stub evidence created.",
        "evidence": ev.model_dump(mode="json"),
    }


# ---------------------------------------------------------------------------
# Decisions
# ---------------------------------------------------------------------------

@app.get("/api/decisions")
def list_decisions() -> list[dict]:
    """List all decisions."""
    return [d.model_dump(mode="json") for d in store.decisions.list_all()]


@app.post("/api/decision/run")
def run_decision(req: DecisionRunRequest) -> dict:
    """Run the decision pipeline and return the result."""
    if _engine_available and engine is not None:
        result = engine.run(
            title=req.title,
            context=req.context,
            company=req.company,
            project=req.project,
            assumptions=req.assumptions,
            risks=req.risks,
        )
        return {"ok": True, "decision": result}

    # Stub: create a draft decision directly
    dec = Decision(
        title=req.title,
        context=req.context,
        company=req.company or store.context().get("active_company", ""),
        project=req.project or store.context().get("active_project", ""),
        assumptions=req.assumptions,
        risks=req.risks,
        status=DecisionStatus.draft,
    )
    store.decisions.save(dec)
    return {
        "ok": True,
        "stub": True,
        "message": "Decision engine not available. Draft decision created.",
        "decision": dec.model_dump(mode="json"),
    }


@app.get("/api/decision/{decision_id}")
def get_decision(decision_id: str) -> dict:
    """Get a single decision by ID."""
    dec = store.decisions.get(decision_id)
    if dec is None:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")
    return dec.model_dump(mode="json")


# ---------------------------------------------------------------------------
# Debate
# ---------------------------------------------------------------------------

class DebateRequest(BaseModel):
    mode: str  # builder, skeptic, contrarian, operator, red_team


DEBATE_STUBS: dict[str, dict] = {
    "builder": {
        "argument": "This approach maximizes value delivery and aligns with strategic goals. The technical foundation supports execution at the proposed pace.",
        "confidence": 0.82,
        "counter": "Speed of execution may introduce technical debt.",
    },
    "skeptic": {
        "argument": "Key assumptions remain untested. The projected outcomes lack supporting evidence within the proposed timeline.",
        "confidence": 0.65,
        "counter": "Perfect information is unavailable — waiting has its own cost.",
    },
    "contrarian": {
        "argument": "The opposite approach may yield better results. Conventional framing could be anchoring us to a suboptimal path.",
        "confidence": 0.58,
        "counter": "Contrarian positions should pressure-test, not override strong evidence.",
    },
    "operator": {
        "argument": "Resource allocation and dependency sequencing need careful mapping before capacity commitment.",
        "confidence": 0.75,
        "counter": "Over-planning can be as costly as under-planning.",
    },
    "red_team": {
        "argument": "Failure modes need explicit enumeration. Blast radius analysis and mitigation strategies must be pre-positioned.",
        "confidence": 0.70,
        "counter": "Risk analysis should inform, not paralyze, decision-making.",
    },
}


@app.post("/api/decision/{decision_id}/debate")
def run_debate(decision_id: str, req: DebateRequest) -> dict:
    """Run a single-mode debate on a decision."""
    dec = store.decisions.get(decision_id)
    if dec is None:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")

    valid_modes = {"builder", "skeptic", "contrarian", "operator", "red_team"}
    if req.mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Mode must be one of {valid_modes}")

    # Use engine if available
    if _engine_available and engine is not None and hasattr(engine, "debate"):
        result = engine.debate(decision_id=decision_id, mode=req.mode)
        return {"mode": req.mode, **result}

    # Stub response
    stub = DEBATE_STUBS.get(req.mode, DEBATE_STUBS["builder"])
    return {"mode": req.mode, **stub}


# ---------------------------------------------------------------------------
# Runs
# ---------------------------------------------------------------------------

@app.get("/api/runs")
def list_runs() -> list[dict]:
    """List all runs."""
    return [r.model_dump(mode="json") for r in store.runs.list_all()]


@app.get("/api/run/{run_id}")
def get_run(run_id: str) -> dict:
    """Get a single run with its full event trace."""
    run = store.runs.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return run.model_dump(mode="json")


# ---------------------------------------------------------------------------
# Artifacts
# ---------------------------------------------------------------------------

@app.get("/api/artifacts")
def list_artifacts() -> list[dict]:
    """List all artifacts."""
    return [a.model_dump(mode="json") for a in store.artifacts.list_all()]


# ---------------------------------------------------------------------------
# Capabilities
# ---------------------------------------------------------------------------

@app.get("/api/capabilities")
def list_capabilities() -> list[dict]:
    """List all capabilities."""
    return [c.model_dump(mode="json") for c in store.capabilities.list_all()]


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8420,
    )


if __name__ == "__main__":
    main()
