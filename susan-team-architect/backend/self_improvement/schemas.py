"""Pydantic V2 models for the Layer 6 Self-Improvement System.

Defines data contracts for agent performance tracking, routing feedback,
prompt experimentation, performance dashboards, and debate grounding.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Agent performance
# ---------------------------------------------------------------------------

class AgentPerformanceRecord(BaseModel):
    """A single agent execution performance measurement."""

    agent_name: str
    run_id: str
    task_type: str
    tokens_used: int = Field(ge=0)
    duration_ms: int = Field(ge=0)
    success: bool
    quality_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    user_satisfaction: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    output_reuse: bool = False
    timestamp: str


# ---------------------------------------------------------------------------
# Routing feedback
# ---------------------------------------------------------------------------

class RoutingFeedback(BaseModel):
    """Feedback on how well a routed action packet performed."""

    action_packet_id: str
    routed_department: str
    routing_quality: float = Field(ge=0.0, le=1.0)
    output_usefulness: float = Field(ge=0.0, le=1.0)
    follow_through: float = Field(ge=0.0, le=1.0)
    reuse_value: float = Field(ge=0.0, le=1.0)
    timestamp: str


class RoutingWeight(BaseModel):
    """Learned routing weight for a department keyword pair."""

    department: str
    keyword: str
    base_weight: float
    learned_adjustment: float
    effective_weight: float
    sample_count: int = Field(ge=0)
    last_updated: str


# ---------------------------------------------------------------------------
# Prompt experimentation
# ---------------------------------------------------------------------------

class PromptVariant(BaseModel):
    """An A/B test between two prompt variants for an agent."""

    id: str
    agent_name: str
    prompt_section: str
    variant_a: str
    variant_b: str
    metric: str
    winner: Optional[str] = None
    a_score: Optional[float] = None
    b_score: Optional[float] = None
    created_at: str
    resolved_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Performance dashboard
# ---------------------------------------------------------------------------

class PerformanceDashboard(BaseModel):
    """Aggregate performance dashboard for a time period."""

    period: str
    agents_ranked: list[dict] = Field(default_factory=list)
    avg_quality: float = Field(ge=0.0, le=1.0)
    avg_tokens: int = Field(ge=0)
    improvement_trend: float = 0.0
    top_learnings: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Debate grounding
# ---------------------------------------------------------------------------

class DebateArgument(BaseModel):
    """A single argument in an evidence-grounded debate."""

    position: Literal["builder", "skeptic", "contrarian", "operator", "red_team"]
    argument: str
    evidence_ids: list[str] = Field(default_factory=list)
    evidence_summaries: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    source: Literal["template", "rag_grounded", "learned"] = "template"
