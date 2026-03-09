"""FastAPI control-plane service for the Startup Intelligence Cockpit."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .catalog import ControlPlaneCatalog
from .foundry import build_foundry_assessment
from .foundry_ops import (
    list_foundry_decisions,
    list_foundry_experiments,
    list_foundry_metrics,
    list_foundry_stage_reviews,
    save_foundry_decision,
    save_foundry_experiment,
    save_foundry_metric,
    save_foundry_stage_review,
)
from .jobs import manager as susan_run_manager
from .protocols import get_company_foundry_blueprint, get_company_status, route_company_task
from .schemas import (
    AgentProfile,
    CompanyStatus,
    FoundryAssessmentSnapshot,
    FoundryBlueprint,
    FoundryDecision,
    FoundryExperiment,
    FoundryMetric,
    FoundryStageReview,
    KnowledgeSearchResponse,
    PromptBundle,
    PromptResearchSnapshot,
    ReconciliationReport,
    RunTrace,
    SusanRouteResponse,
    SusanRunJob,
    SusanRunRequest,
    Tenant,
    TenantScorecard,
    VisualAsset,
)

catalog = ControlPlaneCatalog()

app = FastAPI(
    title="Startup Intelligence Cockpit",
    version="0.1.0",
    description="Repo-native control plane for startup intelligence, prompt governance, RAG audits, and MCP operations.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/tenants", response_model=list[Tenant])
def list_tenants() -> list[Tenant]:
    return catalog.tenants()


@app.get("/api/tenants/{tenant_id}/scorecard", response_model=TenantScorecard)
def get_tenant_scorecard(tenant_id: str) -> TenantScorecard:
    try:
        return catalog.tenant_scorecard(tenant_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown tenant: {tenant_id}") from exc


@app.get("/api/knowledge/search", response_model=KnowledgeSearchResponse)
def search_knowledge(
    q: str = Query(..., min_length=2),
    tenant_id: str = Query(default="transformfit"),
    top_k: int = Query(default=10, ge=1, le=25),
    include_vector: bool = Query(default=False),
) -> KnowledgeSearchResponse:
    return catalog.search_knowledge(query=q, tenant_id=tenant_id, top_k=top_k, include_vector=include_vector)


@app.get("/api/knowledge/gaps")
def knowledge_gaps(tenant_id: str = Query(default="transformfit")):
    return catalog.knowledge_gaps(tenant_id)


@app.get("/api/assets/visual", response_model=list[VisualAsset])
def visual_assets(
    tenant_id: str = Query(default="oracle-health-ai-enablement"),
    limit: int = Query(default=25, ge=1, le=100),
) -> list[VisualAsset]:
    return catalog.visual_assets(tenant_id, limit)


@app.get("/api/companies/{company_id}/status", response_model=CompanyStatus)
def company_status(company_id: str) -> CompanyStatus:
    return CompanyStatus(**get_company_status(company_id))


@app.get("/api/foundry/{company_id}/blueprint", response_model=FoundryBlueprint)
def company_foundry_blueprint(company_id: str) -> FoundryBlueprint:
    return FoundryBlueprint(**get_company_foundry_blueprint(company_id))


@app.get("/api/foundry/assessment", response_model=FoundryAssessmentSnapshot)
def foundry_assessment() -> FoundryAssessmentSnapshot:
    return FoundryAssessmentSnapshot(**build_foundry_assessment())


@app.get("/api/foundry/{company_id}/decisions", response_model=list[FoundryDecision])
def foundry_decisions(company_id: str, limit: int = Query(default=50, ge=1, le=200)) -> list[FoundryDecision]:
    return [FoundryDecision(**row) for row in list_foundry_decisions(company_id, limit)]


@app.post("/api/foundry/decisions", response_model=FoundryDecision)
def create_foundry_decision(payload: FoundryDecision) -> FoundryDecision:
    return FoundryDecision(**save_foundry_decision(payload.model_dump(mode="json")))


@app.get("/api/foundry/{company_id}/experiments", response_model=list[FoundryExperiment])
def foundry_experiments(company_id: str, limit: int = Query(default=50, ge=1, le=200)) -> list[FoundryExperiment]:
    return [FoundryExperiment(**row) for row in list_foundry_experiments(company_id, limit)]


@app.post("/api/foundry/experiments", response_model=FoundryExperiment)
def create_foundry_experiment(payload: FoundryExperiment) -> FoundryExperiment:
    return FoundryExperiment(**save_foundry_experiment(payload.model_dump(mode="json")))


@app.get("/api/foundry/{company_id}/metrics", response_model=list[FoundryMetric])
def foundry_metrics(company_id: str, limit: int = Query(default=50, ge=1, le=200)) -> list[FoundryMetric]:
    return [FoundryMetric(**row) for row in list_foundry_metrics(company_id, limit)]


@app.post("/api/foundry/metrics", response_model=FoundryMetric)
def create_foundry_metric(payload: FoundryMetric) -> FoundryMetric:
    return FoundryMetric(**save_foundry_metric(payload.model_dump(mode="json")))


@app.get("/api/foundry/{company_id}/stage-reviews", response_model=list[FoundryStageReview])
def foundry_stage_reviews(company_id: str, limit: int = Query(default=50, ge=1, le=200)) -> list[FoundryStageReview]:
    return [FoundryStageReview(**row) for row in list_foundry_stage_reviews(company_id, limit)]


@app.post("/api/foundry/stage-reviews", response_model=FoundryStageReview)
def create_foundry_stage_review(payload: FoundryStageReview) -> FoundryStageReview:
    return FoundryStageReview(**save_foundry_stage_review(payload.model_dump(mode="json")))


@app.get("/api/agents/profiles", response_model=list[AgentProfile])
def agent_profiles() -> list[AgentProfile]:
    return catalog.agent_profiles()


@app.get("/api/prompts/bundles", response_model=list[PromptBundle])
def prompt_bundles() -> list[PromptBundle]:
    return catalog.prompt_bundles


@app.get("/api/prompts/bundles/{bundle_id}", response_model=PromptBundle)
def prompt_bundle(bundle_id: str) -> PromptBundle:
    try:
        return catalog.prompt_bundle(bundle_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown prompt bundle: {bundle_id}") from exc


@app.get("/api/prompts/evals")
def prompt_evals():
    return [bundle.eval for bundle in catalog.prompt_bundles]


@app.get("/api/mcp/servers")
def mcp_servers():
    return catalog.mcp_servers()


@app.get("/api/mcp/tools")
def mcp_tools():
    return catalog.mcp_tools()


@app.get("/api/runs/traces", response_model=list[RunTrace])
def run_traces(tenant_id: str | None = Query(default=None)) -> list[RunTrace]:
    return catalog.run_traces(tenant_id)


@app.post("/api/runs/susan", response_model=SusanRunJob)
def submit_susan_run(request: SusanRunRequest) -> SusanRunJob:
    job = susan_run_manager.submit(
        request.company,
        request.mode,
        request.refresh,
        request.prefer_cached,
        request.max_age_minutes,
    )
    return SusanRunJob(**job.__dict__)


@app.get("/api/runs/susan", response_model=list[SusanRunJob])
def list_susan_runs(company: str | None = Query(default=None)) -> list[SusanRunJob]:
    return [SusanRunJob(**state.__dict__) for state in susan_run_manager.list(company)]


@app.get("/api/runs/susan/{job_id}", response_model=SusanRunJob)
def get_susan_run(job_id: str) -> SusanRunJob:
    state = susan_run_manager.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Unknown Susan job: {job_id}")
    return SusanRunJob(**state.__dict__)


@app.get("/api/runs/susan/{job_id}/log")
def get_susan_run_log(job_id: str) -> dict[str, str]:
    state = susan_run_manager.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Unknown Susan job: {job_id}")
    return {"job_id": job_id, "status": state.status, "log": susan_run_manager.log_text(job_id)}


@app.get("/api/runs/susan/{job_id}/outputs")
def get_susan_run_outputs(job_id: str) -> dict[str, object]:
    state = susan_run_manager.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Unknown Susan job: {job_id}")
    return {
        "job_id": job_id,
        "status": state.status,
        "cache_hit": state.cache_hit,
        "outputs": susan_run_manager.outputs(job_id),
    }


@app.get("/api/routing/susan", response_model=SusanRouteResponse)
def route_susan_task(
    company: str = Query(..., min_length=2),
    task: str = Query(..., min_length=3),
    top_k: int = Query(default=6, ge=1, le=12),
) -> SusanRouteResponse:
    return SusanRouteResponse(**route_company_task(company, task, top_k=top_k))


@app.get("/api/routing/policies")
def routing_policies():
    return catalog.routing_policies()


@app.get("/api/research/prompt-intelligence", response_model=PromptResearchSnapshot)
def prompt_intelligence() -> PromptResearchSnapshot:
    return catalog.prompt_research_snapshot


@app.get("/api/audits/reconcile", response_model=ReconciliationReport)
def reconcile() -> ReconciliationReport:
    return catalog.reconciliation()


frontend_dir = catalog.frontend_dir
if frontend_dir.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dir), name="assets")


@app.get("/")
def index() -> FileResponse:
    index_path = frontend_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Cockpit frontend has not been created yet.")
    return FileResponse(index_path)


@app.get("/{path_name:path}")
def spa_fallback(path_name: str) -> FileResponse:
    index_path = frontend_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail=f"Unknown path: {path_name}")
    return FileResponse(index_path)
