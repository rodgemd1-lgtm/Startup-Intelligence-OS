"""Pydantic V2 models for the Layer 3 Graph-Native Memory Architecture.

Defines the core data contracts for memory tips, trajectories, knowledge graph
nodes/edges, and query/stats structures used across the TIMG pipeline.
"""
from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Memory Tips
# ---------------------------------------------------------------------------

class MemoryTip(BaseModel):
    """A reusable insight extracted from agent trajectories."""

    id: str
    tip_type: Literal["strategy", "recovery", "optimization"]
    content: str
    source_run_id: str
    source_agent: str
    task_domain: str
    confidence: float = Field(ge=0.0, le=1.0)
    created_at: str
    access_count: int = 0
    last_accessed: Optional[str] = None
    embedding: Optional[list[float]] = None
    tags: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Trajectory models
# ---------------------------------------------------------------------------

class TrajectoryStep(BaseModel):
    """A single step in an agent execution."""

    step_index: int
    tool_name: str
    input_summary: str
    output_summary: str
    success: bool
    duration_ms: int
    token_count: int
    reasoning: Optional[str] = None


class Trajectory(BaseModel):
    """Complete agent run trace."""

    run_id: str
    agent_name: str
    task_description: str
    steps: list[TrajectoryStep] = Field(default_factory=list)
    outcome: Literal["success", "failure", "partial"]
    total_tokens: int
    total_duration_ms: int
    created_at: str
    quality_score: Optional[float] = None


# ---------------------------------------------------------------------------
# Knowledge graph
# ---------------------------------------------------------------------------

class GraphNode(BaseModel):
    """Knowledge graph node."""

    id: str
    node_type: Literal[
        "decision", "capability", "agent", "artifact",
        "research", "run", "company", "project",
    ]
    name: str
    properties: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str


class GraphEdge(BaseModel):
    """Knowledge graph edge."""

    source_id: str
    target_id: str
    relationship: Literal[
        "enables", "produced", "supports", "requires",
        "blocks", "supersedes", "learned_from",
    ]
    weight: float = Field(ge=0.0, le=1.0, default=1.0)
    evidence: Optional[str] = None
    created_at: str


# ---------------------------------------------------------------------------
# Query & stats
# ---------------------------------------------------------------------------

class MemoryQuery(BaseModel):
    """Query for memory retrieval."""

    query_text: str
    task_domain: Optional[str] = None
    tip_types: Optional[list[str]] = None
    max_results: int = 5
    min_confidence: float = 0.3


class MemoryStats(BaseModel):
    """Aggregate statistics for the memory system."""

    total_tips: int = 0
    tips_by_type: dict[str, int] = Field(default_factory=dict)
    tips_by_domain: dict[str, int] = Field(default_factory=dict)
    total_graph_nodes: int = 0
    total_graph_edges: int = 0
    avg_confidence: float = 0.0
