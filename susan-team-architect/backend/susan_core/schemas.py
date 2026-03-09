"""Pydantic schemas for all Susan outputs."""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field


# --- Phase 1: Company Profile ---

class Founder(BaseModel):
    name: str
    background: str

class CompanyProfile(BaseModel):
    company: str
    domain: str
    stage: str
    website: str | None = None
    founding_date: str | None = None
    founders: list[Founder] = Field(default_factory=list)
    product_description: str
    tech_stack: list[str] = Field(default_factory=list)
    target_market: str
    funding_status: str
    key_competitors: list[str] = Field(default_factory=list)
    current_challenges: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


# --- Phase 2: Gap Analysis ---

class CapabilityGap(BaseModel):
    area: str
    current_state: str
    ideal_state: str
    complexity: int = Field(ge=1, le=10)
    agent_needed: str
    risks: list[str] = Field(default_factory=list)
    cross_portfolio_synergy: str | None = None

class AnalysisReport(BaseModel):
    company: str
    capability_gaps: list[CapabilityGap]
    recommended_team_size: int
    complexity_score: float


# --- Phase 3: Team Design ---

class MemoryConfig(BaseModel):
    short_term: bool = True
    long_term: bool = False
    entity: bool = False

class AgentSpec(BaseModel):
    id: str = Field(description="snake_case identifier")
    name: str = Field(description="Display name (e.g., 'Susan', 'Steve')")
    role: str = Field(description="Job title")
    goal: str = Field(description="One-sentence objective")
    backstory: str = Field(description="Elite pedigree persona")
    tools: list[str] = Field(default_factory=list)
    llm: str = Field(default="claude-sonnet-4-6")
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    dependencies: list[str] = Field(default_factory=list)
    triggers: list[str] = Field(default_factory=list)
    rag_data_types: list[str] = Field(default_factory=list)
    estimated_cost_per_run: str = Field(default="$0.05")

class CrewSpec(BaseModel):
    name: str
    agents: list[str]
    process: str = Field(description="sequential | parallel | hierarchical")
    trigger: str

class TeamManifest(BaseModel):
    project: str
    designed_by: str = "susan"
    version: str = "1.0"
    timestamp: datetime = Field(default_factory=datetime.now)
    orchestration_pattern: str
    agents: list[AgentSpec]
    crews: list[CrewSpec] = Field(default_factory=list)
    total_agents: int
    estimated_monthly_cost: str


# --- Phase 4: Dataset Requirements ---

class DatasetRequirement(BaseModel):
    name: str
    type: str = Field(description="structured|vector|api|filesystem")
    status: str = Field(description="exists|needs_building|needs_acquisition")
    source: str
    format: str
    size_estimate: str
    priority: str = Field(description="P0|P1|P2")
    cost: str = Field(default="free")
    assigned_to: list[str] = Field(default_factory=list)

class DatasetManifest(BaseModel):
    datasets: list[DatasetRequirement]
    external_apis: list[dict] = Field(default_factory=list)
    total_estimated_cost: str


# --- Phase 6: Behavioral Economics Audit ---

class RetentionTarget(BaseModel):
    d1: float
    d7: float
    d30: float
    industry_baseline_d1: float
    industry_baseline_d7: float
    industry_baseline_d30: float

class LAALDesign(BaseModel):
    ownership_asset: str
    cost_of_leaving_progress: str
    cost_of_leaving_identity: str
    cost_of_leaving_social: str
    cost_of_leaving_asset: str
    minimum_return_action: str
    return_reward: str
    investment_flywheel: str

class RelationalArchitecture(BaseModel):
    love_map_strategy: str
    perceived_responsiveness_protocol: str
    therapeutic_alliance_design: dict = Field(default_factory=dict)
    personal_knowledge_map_policy: str
    uncanny_valley_risks: list[str] = Field(default_factory=list)
    staleness_decay_policy: str
    warm_handoff_protocol: str

class BEAudit(BaseModel):
    company: str
    retention_targets: RetentionTarget
    laal_design: LAALDesign
    relational_architecture: RelationalArchitecture | None = None
    copy_protocols: dict = Field(default_factory=dict)
    agent_be_map: dict = Field(default_factory=dict)
    measurement_plan: dict = Field(default_factory=dict)


# --- Knowledge Chunk ---

class KnowledgeChunk(BaseModel):
    content: str
    company_id: str = "shared"
    agent_id: str | None = None
    access_level: str = "public"
    data_type: str
    source: str | None = None
    source_url: str | None = None
    metadata: dict = Field(default_factory=dict)
