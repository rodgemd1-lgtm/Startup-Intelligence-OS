"""Domain models for the Decision & Capability OS."""
from __future__ import annotations

import datetime
import hashlib
import uuid
from enum import Enum
from typing import Any, Optional, List, Dict

from pydantic import BaseModel, Field


def _deterministic_id(prefix: str, seed: str) -> str:
    h = hashlib.sha256(seed.encode()).hexdigest()[:12]
    return f"{prefix}-{h}"


def _now() -> str:
    return datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _uuid() -> str:
    return uuid.uuid4().hex[:12]


# --- Enums ---

class DecisionStatus(str, Enum):
    draft = "draft"
    proposed = "proposed"
    approved = "approved"
    rejected = "rejected"
    superseded = "superseded"


class CapabilityMaturity(str, Enum):
    nascent = "nascent"
    emerging = "emerging"
    scaling = "scaling"
    optimizing = "optimizing"
    leading = "leading"


class ProjectStatus(str, Enum):
    planning = "planning"
    active = "active"
    paused = "paused"
    completed = "completed"
    cancelled = "cancelled"


class CompanyStage(str, Enum):
    concept = "concept"
    validation = "validation"
    mvp = "mvp"
    growth = "growth"
    scale = "scale"


class RunStatus(str, Enum):
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


# --- Option / Debate ---

class ScoredOption(BaseModel):
    id: str = Field(default_factory=_uuid)
    title: str
    description: str = ""
    scores: dict[str, float] = Field(default_factory=dict)
    total_score: float = 0.0


class DebateEntry(BaseModel):
    mode: str  # builder_pov, skeptic_pov, contrarian_pov, operator_pov, red_team_challenge
    argument: str
    confidence: float = 0.5
    timestamp: str = Field(default_factory=_now)


class OutputContract(BaseModel):
    recommendation: str = ""
    counter_recommendation: str = ""
    why_now: str = ""
    failure_modes: list[str] = Field(default_factory=list)
    next_experiment: str = ""


# --- Core domain objects ---

class Decision(BaseModel):
    id: str = ""
    title: str
    status: DecisionStatus = DecisionStatus.draft
    created_at: str = Field(default_factory=_now)
    updated_at: str = Field(default_factory=_now)
    owner: str = "mike"
    company: str = ""
    project: str = ""
    context: str = ""
    assumptions: list[str] = Field(default_factory=list)
    options: list[ScoredOption] = Field(default_factory=list)
    recommendation: str = ""
    risks: list[str] = Field(default_factory=list)
    reversal_criteria: str = ""
    debate_log: list[DebateEntry] = Field(default_factory=list)
    output: OutputContract = Field(default_factory=OutputContract)
    evidence_ids: list[str] = Field(default_factory=list)
    run_id: str = ""
    artifacts: list[str] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        if not self.id:
            self.id = _deterministic_id("dec", f"{self.title}-{self.created_at}")


class Capability(BaseModel):
    id: str = ""
    name: str
    owner: str = "mike"
    maturity: CapabilityMaturity = CapabilityMaturity.nascent
    outcome_metric: str = ""
    dependencies: list[str] = Field(default_factory=list)
    interfaces: list[str] = Field(default_factory=list)
    roles: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    linked_decisions: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=_now)
    updated_at: str = Field(default_factory=_now)

    def model_post_init(self, __context: Any) -> None:
        if not self.id:
            self.id = _deterministic_id("cap", f"{self.name}-{self.created_at}")


class LevelItem(BaseModel):
    text: str
    done: bool = False


class CapabilityLevel(BaseModel):
    name: str  # Nascent, Emerging, Scaling, Optimizing, Leading
    items: list[LevelItem] = Field(default_factory=list)


class CapabilityWithLevels(Capability):
    """Extended capability with per-level checklists."""
    wave: int = 1
    maturity_target: float = 4.0
    levels: dict[int, CapabilityLevel] = Field(default_factory=dict)


class Project(BaseModel):
    id: str = ""
    name: str
    status: ProjectStatus = ProjectStatus.planning
    owner: str = "mike"
    company: str = ""
    objective: str = ""
    milestones: list[str] = Field(default_factory=list)
    linked_decisions: list[str] = Field(default_factory=list)
    linked_capabilities: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
    start_date: str = ""
    target_date: str = ""
    created_at: str = Field(default_factory=_now)
    updated_at: str = Field(default_factory=_now)

    def model_post_init(self, __context: Any) -> None:
        if not self.id:
            self.id = _deterministic_id("proj", f"{self.name}-{self.created_at}")


class Company(BaseModel):
    id: str = ""
    name: str
    domain: str = ""
    stage: CompanyStage = CompanyStage.concept
    owner: str = "mike"
    website: str = ""
    founding_date: str = ""
    product_description: str = ""
    tech_stack: list[str] = Field(default_factory=list)
    target_market: str = ""
    key_competitors: list[str] = Field(default_factory=list)
    current_challenges: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    linked_projects: list[str] = Field(default_factory=list)
    linked_capabilities: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=_now)
    updated_at: str = Field(default_factory=_now)

    def model_post_init(self, __context: Any) -> None:
        if not self.id:
            self.id = _deterministic_id("co", f"{self.name}-{self.created_at}")


class RunEvent(BaseModel):
    step: str
    timestamp: str = Field(default_factory=_now)
    data: dict[str, Any] = Field(default_factory=dict)
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = 0.5
    uncertainty: float = 0.5


class Run(BaseModel):
    id: str = ""
    trigger: str = ""
    started_at: str = Field(default_factory=_now)
    completed_at: str = ""
    status: RunStatus = RunStatus.running
    company: str = ""
    project: str = ""
    decision: str = ""
    capability: str = ""
    mode: str = ""
    events: list[RunEvent] = Field(default_factory=list)
    artifacts_produced: list[str] = Field(default_factory=list)
    notes: str = ""
    output: Optional[OutputContract] = None

    def model_post_init(self, __context: Any) -> None:
        if not self.id:
            self.id = _deterministic_id("run", f"{self.trigger}-{self.started_at}")

    def add_event(self, step: str, data: Optional[dict] = None, evidence_ids: Optional[list] = None,
                  confidence: float = 0.5) -> RunEvent:
        evt = RunEvent(
            step=step,
            data=data or {},
            evidence_ids=evidence_ids or [],
            confidence=confidence,
            uncertainty=1.0 - confidence,
        )
        self.events.append(evt)
        return evt

    def complete(self, output: Optional[OutputContract] = None) -> None:
        self.status = RunStatus.completed
        self.completed_at = _now()
        if output:
            self.output = output


class Session(BaseModel):
    id: str = Field(default_factory=lambda: f"sess-{_uuid()}")
    operator: str = "mike"
    started_at: str = Field(default_factory=_now)
    ended_at: str = ""
    runs: list[str] = Field(default_factory=list)
    notes: str = ""


class Artifact(BaseModel):
    id: str = Field(default_factory=lambda: f"art-{_uuid()}")
    name: str
    type: str = ""  # decision_packet, capability_map, evidence_bundle, etc.
    run_id: str = ""
    source_refs: list[str] = Field(default_factory=list)
    confidence: float = 0.5
    path: str = ""
    created_at: str = Field(default_factory=_now)


class Evidence(BaseModel):
    id: str = Field(default_factory=lambda: f"ev-{_uuid()}")
    source_url: str = ""
    source_type: str = ""  # web, doc, api, manual
    title: str = ""
    content: str = ""
    topic_tags: list[str] = Field(default_factory=list)
    domain: str = ""
    confidence: float = 0.5
    recency_score: float = 0.5
    fetched_at: str = Field(default_factory=_now)
    normalized: bool = False
    dedup_hash: str = ""
