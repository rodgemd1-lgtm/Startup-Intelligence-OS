"""Pydantic V2 models for the Chains engine."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_id() -> str:
    return f"run-{uuid.uuid4().hex[:12]}"


# --- Triggers ---

class ManualTrigger(BaseModel):
    kind: Literal["manual"] = "manual"


class SignalTrigger(BaseModel):
    kind: Literal["signal"] = "signal"
    min_score: int = Field(ge=0, le=100, default=80)
    signal_types: list[str] = Field(default_factory=list)


class ScheduledTrigger(BaseModel):
    kind: Literal["scheduled"] = "scheduled"
    cron: str = Field(..., description="Cron expression for scheduling")


class FileWatchTrigger(BaseModel):
    kind: Literal["file_watch"] = "file_watch"
    watch_path: str = Field(..., description="Path to watch for changes")


TriggerType = Union[ManualTrigger, SignalTrigger, ScheduledTrigger, FileWatchTrigger]


# --- Chain Definition ---

class ChainStep(BaseModel):
    agent: str = Field(..., description="Agent name to invoke (e.g., 'scout', 'herald')")
    input_key: Optional[str] = Field(default=None, description="Key to read from context bus")
    output_key: str = Field(..., description="Key to write result to context bus")
    gate: bool = Field(default=False, description="If True, step can halt the chain")
    timeout_seconds: int = Field(default=300, description="Max seconds for this step")


class ChainDef(BaseModel):
    name: str = Field(..., description="Unique chain identifier (kebab-case)")
    description: str = Field(default="", description="Human-readable description")
    trigger: TriggerType = Field(..., description="What triggers this chain")
    autonomy: Literal["MANUAL", "SUPERVISED", "AUTONOMOUS"] = Field(default="MANUAL")
    steps: list[ChainStep] = Field(..., min_length=1, description="Ordered steps to execute")


# --- Runtime Models ---

class GateResult(BaseModel):
    agent: str
    disposition: Literal["CLEAR", "REVIEW", "BLOCK"]
    reason: str = ""
    timestamp: str = Field(default_factory=_now_iso)


class StepResult(BaseModel):
    agent: str
    output_key: str
    status: Literal["completed", "failed", "blocked", "skipped"] = "completed"
    gate_result: Optional[GateResult] = None
    duration_ms: int = 0
    timestamp: str = Field(default_factory=_now_iso)


class ChainRun(BaseModel):
    id: str = Field(default_factory=_run_id)
    chain_name: str
    status: Literal["running", "completed", "failed", "blocked", "halted"] = "running"
    steps_completed: int = 0
    steps_total: int = 0
    step_results: list[StepResult] = Field(default_factory=list)
    trigger_source: str = ""
    started_at: str = Field(default_factory=_now_iso)
    finished_at: Optional[str] = None
    disposition: Literal["PUBLISH", "STAGE", "BLOCK", "PENDING"] = "PENDING"
