"""Dashboard API Models — V7 Visual Command Center

Pydantic models for all dashboard API endpoints.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# --- System Status ---

class ServiceStatus(BaseModel):
    name: str
    status: str = "unknown"  # "healthy", "degraded", "down", "unknown"
    last_check: Optional[datetime] = None
    details: dict[str, Any] = Field(default_factory=dict)


class SystemStatus(BaseModel):
    overall: str = "unknown"
    services: list[ServiceStatus] = Field(default_factory=list)
    uptime_hours: float = 0
    last_morning_brief: Optional[datetime] = None
    active_channels: list[str] = Field(default_factory=list)


# --- Companies ---

class CompanySummary(BaseModel):
    id: str
    name: str
    agent_count: int = 0
    rag_chunks: int = 0
    active_signals: int = 0
    maturity_score: float = 0
    last_activity: Optional[datetime] = None


# --- Agents ---

class AgentStatus(BaseModel):
    name: str
    department: str = ""
    status: str = "idle"  # "idle", "active", "error", "disabled"
    last_invoked: Optional[datetime] = None
    invocation_count: int = 0
    success_rate: float = 0
    avg_rating: float = 0


# --- Memory ---

class MemoryTierStats(BaseModel):
    tier: str  # "episodic", "semantic", "wisdom"
    record_count: int = 0
    last_updated: Optional[datetime] = None
    health: str = "unknown"  # "healthy", "stale", "empty"


class MemoryHealth(BaseModel):
    tiers: list[MemoryTierStats] = Field(default_factory=list)
    consolidation_runs_30d: int = 0
    last_consolidation: Optional[datetime] = None
    corrections_30d: int = 0
    total_records: int = 0


# --- Goals ---

class GoalProgress(BaseModel):
    id: str
    name: str
    progress: str = ""  # "25%", "on track", etc.
    status: str = "active"  # "active", "blocked", "completed"
    blocker: str = ""
    deadline: Optional[datetime] = None


# --- Pipelines ---

class PipelineStatus(BaseModel):
    name: str
    status: str = "unknown"  # "running", "stopped", "error", "scheduled"
    last_run: Optional[datetime] = None
    last_result: str = ""  # "success", "failure", "timeout"
    schedule: str = ""  # Cron expression
    run_count_30d: int = 0
    failure_count_30d: int = 0


# --- Signals ---

class CompetitiveSignalSummary(BaseModel):
    title: str
    company: str
    competitor: str
    priority: str  # P0, P1, P2
    category: str
    detected_at: Optional[datetime] = None


# --- Ratings ---

class RatingsTrend(BaseModel):
    period: str  # "7d", "30d"
    count: int = 0
    average: float = 0
    trend: str = "stable"  # "improving", "declining", "stable"
    positive_count: int = 0
    negative_count: int = 0


# --- Brief ---

class TodayBrief(BaseModel):
    date: str
    one_thing: str = ""
    meeting_count: int = 0
    free_hours: float = 0
    urgent_email_count: int = 0
    signal_count: int = 0
    rendered_markdown: str = ""


# --- Actions ---

class PendingAction(BaseModel):
    id: str
    action_type: str  # "approve", "confirm"
    description: str
    proposed_by: str = "jake"
    created_at: Optional[datetime] = None
    details: dict[str, Any] = Field(default_factory=dict)


class ActionApproval(BaseModel):
    action_id: str
    approved: bool
    reason: str = ""
