"""Pydantic V2 models for the Layer 7 Collective Intelligence Framework.

Defines data contracts for research programs, agent blueprints, knowledge
transfers, capability predictions, and system evolution proposals.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Research programs
# ---------------------------------------------------------------------------

class ResearchProgramSpec(BaseModel):
    """A self-directed research program targeting a specific capability gap."""

    id: str
    name: str
    objective: str
    target_capabilities: list[str] = Field(default_factory=list)
    knowledge_gaps: list[str] = Field(default_factory=list)
    research_questions: list[str] = Field(default_factory=list)
    search_strategies: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    estimated_duration_weeks: int = Field(ge=1)
    priority: Literal["critical", "high", "medium", "low"] = "medium"
    status: Literal["proposed", "approved", "active", "completed", "cancelled"] = "proposed"
    created_at: str
    completed_at: Optional[str] = None
    findings_summary: Optional[str] = None


# ---------------------------------------------------------------------------
# Agent blueprints
# ---------------------------------------------------------------------------

class AgentBlueprint(BaseModel):
    """Blueprint for an autonomously proposed agent."""

    id: str
    name: str
    description: str
    model: Literal["opus", "sonnet", "haiku"] = "sonnet"
    system_prompt: str
    tools: list[str] = Field(default_factory=list)
    routing_keywords: list[str] = Field(default_factory=list)
    domain: str
    parent_agent: Optional[str] = None
    performance_baseline: Optional[dict] = None
    created_at: str
    status: Literal["proposed", "testing", "active", "deprecated"] = "proposed"
    test_results: Optional[dict] = None


# ---------------------------------------------------------------------------
# Knowledge transfer
# ---------------------------------------------------------------------------

class KnowledgeTransfer(BaseModel):
    """Record of a knowledge transfer between agents."""

    id: str
    source_agent: str
    target_agents: list[str] = Field(default_factory=list)
    tip_ids: list[str] = Field(default_factory=list)
    domain: str
    transfer_type: Literal["direct", "generalized"] = "generalized"
    created_at: str
    effectiveness_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)


# ---------------------------------------------------------------------------
# Capability predictions
# ---------------------------------------------------------------------------

class CapabilityPrediction(BaseModel):
    """Predictive maturity forecast for a single capability.

    Maturity scale supports both 0-5 (standard) and 0-10 (department/studio)
    ranges depending on the capability type.
    """

    capability_id: str
    capability_name: str
    current_maturity: float = Field(ge=0.0, le=10.0)
    target_maturity: float = Field(ge=0.0, le=10.0)
    predicted_weeks_to_target: int = Field(ge=0)
    confidence: float = Field(ge=0.0, le=1.0)
    blockers: list[str] = Field(default_factory=list)
    required_resources: list[str] = Field(default_factory=list)
    recommended_sequence: list[str] = Field(default_factory=list)
    predicted_at: str


# ---------------------------------------------------------------------------
# System evolution
# ---------------------------------------------------------------------------

class SystemEvolution(BaseModel):
    """A proposed evolution to the operating model."""

    id: str
    evolution_type: Literal[
        "new_agent",
        "new_capability",
        "new_department",
        "routing_change",
        "architecture_change",
    ]
    description: str
    rationale: str
    evidence: list[str] = Field(default_factory=list)
    status: Literal["proposed", "approved", "implemented", "rejected"] = "proposed"
    impact_assessment: str = ""
    created_at: str
