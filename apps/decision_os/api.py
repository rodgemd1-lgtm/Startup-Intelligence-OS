"""FastAPI server for the Decision & Capability OS."""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import yaml

from .claw_control import ClawControlPlane
from .models import (
    Decision,
    DecisionStatus,
    SignalEvent,
    SignalSeverity,
)
from .maturity_surfaces import enrich_department_payload, load_simulated_maturity_state
from .operator import (
    build_graph,
    collect_signals,
    department_registry,
    get_decision_record,
    list_action_packets,
    normalize_decision_records,
    route_request,
)
from .store import Store


store = Store()

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


app = FastAPI(
    title="Decision & Capability OS",
    version="0.2.0",
    description="API surface for the Startup Intelligence OS operator runtime.",
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


class DebateRequest(BaseModel):
    mode: str


class RouteRequest(BaseModel):
    request_text: str


class SignalCreateRequest(BaseModel):
    signal_type: str
    title: str
    description: str = ""
    source: str = "operator"
    severity: SignalSeverity = SignalSeverity.warning
    related_ids: dict[str, Any] = Field(default_factory=dict)
    recommended_departments: list[str] = Field(default_factory=list)
    next_action: str = ""


class ClawRemoteCommandRequest(BaseModel):
    command: str
    args: list[str] = Field(default_factory=list)


DEBATE_STUBS: dict[str, dict] = {
    "builder": {
        "argument": "This approach maximizes value delivery and aligns with strategic goals. The technical foundation supports execution at the proposed pace.",
        "confidence": 0.82,
        "counter": "Speed of execution may introduce technical debt.",
    },
    "skeptic": {
        "argument": "Key assumptions remain untested. The projected outcomes lack supporting evidence within the proposed timeline.",
        "confidence": 0.65,
        "counter": "Perfect information is unavailable. Waiting has its own cost.",
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


@app.get("/api/context")
def get_context() -> dict:
    ctx = store.context()
    if not ctx:
        return {"error": "workspace.yaml not found or empty"}
    return ctx


@app.get("/api/status")
def get_status() -> dict:
    return store.status()


@app.get("/api/debrief")
def get_debrief(operator: str = Query(default="mike")) -> dict:
    ctx = store.context()
    status = store.status()
    signals = collect_signals(store)
    packets = list_action_packets(store)

    workspace_name = ctx.get("name", "startup-intelligence-os")
    active_company = ctx.get("active_company", "unknown")
    active_project = ctx.get("active_project", "unknown")
    active_decision = ctx.get("active_decision", "unknown")
    runtime = ctx.get("runtime_source_of_truth", "susan-team-architect/backend")

    debrief_lines = [
        f"Workspace: {workspace_name}",
        f"Runtime source of truth: {runtime}",
        f"Active company: {active_company}",
        f"Active project: {active_project}",
        f"Active decision: {active_decision}",
        f"Open signals: {len(signals)}",
        f"Queued action packets: {len(packets)}",
    ]

    mike_actions: list[str] = []
    susan_actions: list[str] = []

    if packets:
        mike_actions.append(f"Advance action packet: {packets[0].request_text[:72]}")
    else:
        mike_actions.append("Use the ask composer to generate the first action packet")

    if signals:
        top_signal = signals[0]
        mike_actions.append(top_signal.next_action or top_signal.title)
    else:
        mike_actions.append("Review department health and capability drift")

    if status.get("capabilities", 0) == 0:
        susan_actions.append("Define initial capabilities for the active company")
    else:
        susan_actions.append(f"Audit {status['capabilities']} capability records for maturity progression")

    susan_actions.append("Refresh the department registry and route map as new studios are added")

    return {
        "greeting": f"Hello, {operator.capitalize()}",
        "debrief": debrief_lines,
        "actions": {"mike": mike_actions, "susan": susan_actions},
        "status": [f"{key}: {value}" for key, value in status.items()],
    }


@app.post("/api/ingest")
def ingest_evidence(req: IngestRequest) -> dict:
    if _ingestion_available and ingestion is not None:
        result = ingestion.ingest(
            url=req.url,
            domain=req.domain,
            topic_tags=req.topic_tags,
        )
        return {"ok": True, "evidence": result}

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


@app.get("/api/decisions")
def list_decisions() -> list[dict]:
    return normalize_decision_records(store)


@app.post("/api/decision/run")
def run_decision(req: DecisionRunRequest) -> dict:
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
    record = get_decision_record(store, decision_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")
    return record


@app.post("/api/decision/{decision_id}/debate")
def run_debate(decision_id: str, req: DebateRequest) -> dict:
    valid_modes = {"builder", "skeptic", "contrarian", "operator", "red_team"}
    if req.mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Mode must be one of {valid_modes}")

    record = get_decision_record(store, decision_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")

    modeled_decision = store.decisions.get(decision_id)
    if _engine_available and engine is not None and modeled_decision is not None and hasattr(engine, "debate"):
        result = engine.debate(decision_id=decision_id)
        return {
            "mode": req.mode,
            "decision_id": result.id,
            "recommendation": result.recommendation,
            "confidence": 0.72,
        }

    stub = DEBATE_STUBS.get(req.mode, DEBATE_STUBS["builder"])
    stub_context = record.get("context", "")
    return {
        "mode": req.mode,
        "decision_id": decision_id,
        "context": stub_context[:180],
        **stub,
    }


@app.get("/api/runs")
def list_runs() -> list[dict]:
    return [run.model_dump(mode="json") for run in store.runs.list_all()]


@app.get("/api/run/{run_id}")
def get_run(run_id: str) -> dict:
    run = store.runs.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return run.model_dump(mode="json")


@app.get("/api/artifacts")
def list_artifacts() -> list[dict]:
    return [artifact.model_dump(mode="json") for artifact in store.artifacts.list_all()]


@app.get("/api/capabilities")
def list_capabilities() -> list[dict]:
    return store.load_yaml_collection(store.startup_os / "capabilities")


@app.get("/api/capabilities/summary")
def get_capabilities_summary() -> list[dict]:
    caps_dir = store.startup_os / "capabilities"
    results = []
    for path in sorted(caps_dir.glob("*.yaml")):
        if path.stem in (
            "README",
            "agent-readiness-index",
            "workspace-contract",
            "jake.profile",
            "susan.profile",
            "gen-chat-os.system",
            "decision-kernel-phase-a",
        ):
            continue
        data = yaml.safe_load(path.read_text())
        if not data or "levels" not in data:
            continue
        levels = data.get("levels", {})
        total_items = sum(len(level.get("items", [])) for level in levels.values())
        done_items = sum(
            sum(1 for item in level.get("items", []) if item.get("done"))
            for level in levels.values()
        )

        next_level = None
        next_item = None
        for level in sorted(levels.keys()):
            items = levels[level].get("items", [])
            for item in items:
                if not item.get("done"):
                    next_level = level
                    next_item = item.get("text")
                    break
            if next_level:
                break

        threshold = False
        for level in sorted(levels.keys()):
            items = levels[level].get("items", [])
            undone = [item for item in items if not item.get("done")]
            if len(undone) == 1:
                threshold = True
                break

        results.append(
            {
                "id": data.get("id", path.stem),
                "name": data.get("name", path.stem),
                "maturity_current": data.get("maturity_current", 0),
                "maturity_target": data.get("maturity_target", 4),
                "wave": data.get("wave", 1),
                "gaps": data.get("gaps", []),
                "total_items": total_items,
                "done_items": done_items,
                "progress_percent": round(done_items / total_items * 100) if total_items else 0,
                "next_level": next_level,
                "next_item": next_item,
                "threshold": threshold,
                "owner_agent": data.get("owner_agent", ""),
            }
        )
    results.sort(key=lambda item: (item["wave"], item["maturity_current"]))
    return results


@app.get("/api/capabilities/{capability_id}/levels")
def get_capability_levels(capability_id: str) -> dict:
    data = store.get_capability_levels(capability_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Capability {capability_id} not found")
    return data


@app.put("/api/capabilities/{capability_id}/levels/{level}/items/{index}")
def toggle_capability_item(capability_id: str, level: int, index: int) -> dict:
    data = store.toggle_capability_item(capability_id, level, index)
    if data is None:
        raise HTTPException(
            status_code=404,
            detail=f"Capability {capability_id} not found or invalid level/index",
        )
    return data


@app.get("/api/departments")
def list_departments() -> list[dict]:
    simulated_state = load_simulated_maturity_state(store.root)
    return [
        enrich_department_payload(department.model_dump(mode="json"), simulated_state)
        for department in department_registry(store)
    ]


@app.get("/api/departments/{department_id}")
def get_department(department_id: str) -> dict:
    department = store.departments.get(department_id)
    if department is None:
        raise HTTPException(status_code=404, detail=f"Department {department_id} not found")
    return enrich_department_payload(
        department.model_dump(mode="json"),
        load_simulated_maturity_state(store.root),
    )


@app.post("/api/route/request")
def route_operator_request(req: RouteRequest) -> dict:
    if not req.request_text.strip():
        raise HTTPException(status_code=400, detail="request_text is required")
    try:
        return route_request(store, req.request_text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/graph")
def get_graph() -> dict:
    return build_graph(store)


@app.get("/api/signals")
def list_signals() -> list[dict]:
    return [signal.model_dump(mode="json") for signal in collect_signals(store)]


@app.post("/api/signals")
def create_signal(req: SignalCreateRequest) -> dict:
    signal = SignalEvent(
        signal_type=req.signal_type,
        title=req.title,
        description=req.description,
        source=req.source,
        severity=req.severity,
        related_ids=req.related_ids,
        recommended_departments=req.recommended_departments,
        next_action=req.next_action,
    )
    store.signals.save(signal)
    return signal.model_dump(mode="json")


@app.get("/api/action-packets")
def get_action_packets() -> list[dict]:
    return [packet.model_dump(mode="json") for packet in list_action_packets(store)]


@app.get("/api/claw/remote-brief")
def get_claw_remote_brief(
    operator: str = Query(default="mike"),
    signal_limit: int = Query(default=5, ge=0, le=20),
    packet_limit: int = Query(default=5, ge=0, le=20),
) -> dict:
    control = ClawControlPlane()
    return control.remote_brief(
        operator=operator,
        signal_limit=signal_limit,
        packet_limit=packet_limit,
    )


@app.post("/api/claw/remote-command")
def post_claw_remote_command(req: ClawRemoteCommandRequest) -> dict:
    control = ClawControlPlane()
    return control.remote_command(req.command, req.args)


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8420)


if __name__ == "__main__":
    main()
