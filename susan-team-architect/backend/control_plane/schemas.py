"""Stable schemas for the Startup Intelligence Cockpit."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class ScoreMetric(BaseModel):
    key: str
    label: str
    value: str
    trend: str | None = None


class Tenant(BaseModel):
    id: str
    name: str
    domain: str
    stage: str
    target_market: str
    budget_per_month_usd: float | None = None
    status: str = "active"
    primary_domain_pack: str | None = None
    health_score: int = Field(default=0, ge=0, le=100)


class LayerCoverage(BaseModel):
    layer_id: str
    name: str
    description: str
    asset_count: int = 0
    coverage_score: int = Field(default=0, ge=0, le=100)
    status: str = "gap"
    notes: list[str] = Field(default_factory=list)


class EvidenceNode(BaseModel):
    id: str
    title: str
    source_url: str
    captured_at: date | None = None
    effective_date: date | None = None
    confidence: float = Field(default=0.0, ge=0, le=1)
    verification_status: str = "unverified"
    evidence_grade: str = "strong_secondary"
    excerpt: str | None = None


class Claim(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    field_name: str
    value: str
    as_of_date: date | None = None
    evidence: list[EvidenceNode] = Field(default_factory=list)


class KnowledgeAsset(BaseModel):
    id: str
    title: str
    asset_type: str
    lane: str
    tenant_id: str = "shared"
    source: str | None = None
    source_path: str | None = None
    excerpt: str
    freshness_date: date | None = None
    freshness_status: str = "unknown"
    confidence: float = Field(default=0.0, ge=0, le=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LaneStatus(BaseModel):
    lane: str
    enabled: bool
    detail: str
    result_count: int = 0


class KnowledgeSearchResponse(BaseModel):
    query: str
    tenant_id: str
    lanes: list[LaneStatus] = Field(default_factory=list)
    results: list[KnowledgeAsset] = Field(default_factory=list)


class VisualAsset(BaseModel):
    id: str
    tenant_id: str
    title: str
    asset_type: str = "screenshot"
    source_url: str | None = None
    public_url: str | None = None
    bucket_name: str | None = None
    storage_path: str | None = None
    excerpt: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProtocolDefinition(BaseModel):
    id: str
    name: str
    family: str
    source_path: str
    status: str = "active"
    summary: str
    owners: list[str] = Field(default_factory=list)
    freshness_status: str = "current"


class PromptComponent(BaseModel):
    name: str
    content: str


class PromptEvalResult(BaseModel):
    bundle_id: str
    version: str
    schema_valid: bool
    citations_present: bool
    eval_passed: bool
    ready_for_promotion: bool
    failures: list[str] = Field(default_factory=list)


class PromptBundle(BaseModel):
    id: str
    name: str
    source_agent: str
    version: str
    digest: str
    status: str
    compiled_at: datetime
    source_paths: list[str] = Field(default_factory=list)
    components: list[PromptComponent] = Field(default_factory=list)
    eval: PromptEvalResult


class AgentCapability(BaseModel):
    id: str
    name: str
    role: str
    group: str
    authored: bool
    registered: bool
    prompt_status: str
    required_data_types: list[str] = Field(default_factory=list)
    missing_data_types: list[str] = Field(default_factory=list)
    gap_count: int = 0


class AgentProfile(BaseModel):
    id: str
    name: str
    role: str
    group: str
    authored: bool
    registered: bool
    traits: list[str] = Field(default_factory=list)
    conversation_style: str | None = None
    debate_protocol: str | None = None
    uncertainty_protocol: str | None = None
    meeting_habits: list[str] = Field(default_factory=list)
    required_data_types: list[str] = Field(default_factory=list)
    missing_data_types: list[str] = Field(default_factory=list)
    humanization_score: int = Field(default=0, ge=0, le=100)


class CoverageGap(BaseModel):
    id: str
    gap_type: str
    severity: str
    title: str
    detail: str
    tenant_id: str = "shared"
    owner: str | None = None
    layer: str | None = None
    evidence: list[str] = Field(default_factory=list)


class MCPTool(BaseModel):
    id: str
    server_id: str
    name: str
    description: str
    status: str
    tenant_scoped: bool
    latency_ms: int | None = None
    failure_rate: float | None = None


class MCPServer(BaseModel):
    id: str
    name: str
    transport: str
    status: str
    health: str
    scopes: list[str] = Field(default_factory=list)
    tools_count: int = 0
    command: str | None = None
    endpoint: str | None = None
    dependent_workflows: list[str] = Field(default_factory=list)


class RunTrace(BaseModel):
    id: str
    tenant_id: str
    kind: str
    status: str
    started_at: datetime
    finished_at: datetime | None = None
    prompt_bundle_id: str | None = None
    retrieval_lanes: list[str] = Field(default_factory=list)
    model_route: str | None = None
    tool_names: list[str] = Field(default_factory=list)
    cost_usd: float | None = None
    quality_score: float | None = None


class SusanRunRequest(BaseModel):
    company: str
    mode: str = "quick"
    refresh: bool = False
    prefer_cached: bool = True
    max_age_minutes: int = Field(default=240, ge=1, le=10080)


class SusanRunJob(BaseModel):
    id: str
    company: str
    mode: str
    refresh: bool
    status: str
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    pid: int | None = None
    output_dir: str | None = None
    log_path: str | None = None
    cache_hit: bool = False
    result_files: dict[str, str] = Field(default_factory=dict)
    error: str | None = None


class CompanyStatus(BaseModel):
    company_id: str
    company: dict[str, Any] = Field(default_factory=dict)
    chunk_count: int = 0
    visual_asset_count: int = 0
    output_dir: str | None = None
    output_files: list[dict[str, Any]] = Field(default_factory=list)
    latest_output_at: str | None = None


class SusanRouteResponse(BaseModel):
    company_id: str
    task: str
    suggested_mode: str = "quick"
    mode_options: list[dict[str, Any]] = Field(default_factory=list)
    need_research_first: bool = False
    need_visual_assets: bool = False
    recommended_agents: list[str] = Field(default_factory=list)
    recommended_data_types: list[str] = Field(default_factory=list)
    next_commands: list[str] = Field(default_factory=list)
    rationale: list[str] = Field(default_factory=list)
    evidence_hits: list[dict[str, Any]] = Field(default_factory=list)


class FoundryBlueprint(BaseModel):
    company_id: str
    company_name: str
    description: str = ""
    default_mode: str = "quick"
    genome: dict[str, Any] = Field(default_factory=dict)
    artifact_inventory: list[dict[str, Any]] = Field(default_factory=list)
    mode_options: list[dict[str, Any]] = Field(default_factory=list)
    stage_gates: list[dict[str, Any]] = Field(default_factory=list)
    maturity: list[dict[str, Any]] = Field(default_factory=list)
    key_protocols: list[str] = Field(default_factory=list)
    execution_tracks: list[dict[str, Any]] = Field(default_factory=list)
    expert_councils: list[dict[str, Any]] = Field(default_factory=list)
    project_targets: list[dict[str, Any]] = Field(default_factory=list)
    coverage_gaps: list[dict[str, Any]] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)


class FoundryDecision(BaseModel):
    decision_id: str
    company_id: str
    owner: str
    summary: str
    context: str | None = None
    chosen_option: str
    why_this_won: str | None = None
    status: str = "active"
    review_date: date | None = None
    source_refs: list[str] = Field(default_factory=list)
    risks_accepted: list[str] = Field(default_factory=list)
    linked_experiments: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    decided_at: datetime | None = None


class FoundryExperiment(BaseModel):
    experiment_id: str
    company_id: str
    hypothesis: str
    owner: str
    status: str = "proposed"
    user_or_workflow: str | None = None
    metric_moved: str | None = None
    leading_signal: str | None = None
    disconfirming_signal: str | None = None
    intervention: str | None = None
    start_date: date | None = None
    stop_date: date | None = None
    result_summary: str | None = None
    linked_decisions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class FoundryMetric(BaseModel):
    metric_id: str
    company_id: str
    name: str
    category: str
    owner: str
    definition: str | None = None
    cadence: str | None = None
    leading_or_lagging: str | None = None
    threshold_green: str | None = None
    threshold_yellow: str | None = None
    threshold_red: str | None = None
    source_events: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class FoundryStageReview(BaseModel):
    company_id: str
    stage_gate_id: str
    reviewer: str
    status: str
    summary: str
    blocking_gaps: list[str] = Field(default_factory=list)
    artifact_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    reviewed_at: datetime | None = None


class FoundryAssessmentSnapshot(BaseModel):
    companies: list[dict[str, Any]] = Field(default_factory=list)


class RoutingPolicy(BaseModel):
    id: str
    name: str
    mode: str
    default_route: str
    allowed_workloads: list[str] = Field(default_factory=list)
    provenance_required: bool = False
    description: str


class BacklogItem(BaseModel):
    id: str
    title: str
    reason: str
    score: int = Field(default=0, ge=0)
    owner: str | None = None
    tenant_id: str = "shared"
    status: str = "proposed"


class PromptResearchProviderStatus(BaseModel):
    provider: str
    configured: bool
    status: str
    formats: list[str] = Field(default_factory=list)


class ResearchTopicStatus(BaseModel):
    topic: str
    query: str
    why: str
    hits: int = 0
    scraped_pages: int = 0
    status: str = "pending"
    example_urls: list[str] = Field(default_factory=list)


class PromptResearchSnapshot(BaseModel):
    generated_at: datetime | None = None
    total_hits: int = 0
    unique_urls: int = 0
    total_scrapes: int = 0
    providers: list[PromptResearchProviderStatus] = Field(default_factory=list)
    topics: list[ResearchTopicStatus] = Field(default_factory=list)
    artifact_paths: list[str] = Field(default_factory=list)


class ReconciliationIssue(BaseModel):
    id: str
    severity: str
    area: str
    title: str
    detail: str
    file_path: str | None = None
    recommendation: str


class ReconciliationReport(BaseModel):
    generated_at: datetime
    issues: list[ReconciliationIssue] = Field(default_factory=list)
    backlog: list[BacklogItem] = Field(default_factory=list)


class TenantScorecard(BaseModel):
    tenant: Tenant
    diagnosis: str
    metrics: list[ScoreMetric] = Field(default_factory=list)
    layer_coverage: list[LayerCoverage] = Field(default_factory=list)
    protocols: list[ProtocolDefinition] = Field(default_factory=list)
    agent_capabilities: list[AgentCapability] = Field(default_factory=list)
    agent_profiles: list[AgentProfile] = Field(default_factory=list)
    coverage_gaps: list[CoverageGap] = Field(default_factory=list)
    prompt_bundles: list[PromptBundle] = Field(default_factory=list)
    mcp_servers: list[MCPServer] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    backlog: list[BacklogItem] = Field(default_factory=list)
