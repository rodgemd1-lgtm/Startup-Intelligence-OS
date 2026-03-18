"""Pydantic V2 models for the Trust system."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TrustProfile(BaseModel):
    chain_name: str
    level: Literal["MANUAL", "SUPERVISED", "AUTONOMOUS"] = "MANUAL"
    total_runs: int = 0
    successful_runs: int = 0
    blocked_runs: int = 0
    rejected_runs: int = 0
    last_run_at: str = ""
    last_promotion_at: str = ""
    last_demotion_at: str = ""

    @property
    def accuracy(self) -> float:
        if self.total_runs == 0:
            return 0.0
        return (self.successful_runs / self.total_runs) * 100

    @property
    def escalation_rate(self) -> float:
        if self.total_runs == 0:
            return 0.0
        return ((self.blocked_runs + self.rejected_runs) / self.total_runs) * 100


class GraduationEvent(BaseModel):
    chain_name: str
    from_level: str
    to_level: str
    reason: str
    timestamp: str = Field(default_factory=_now_iso)
