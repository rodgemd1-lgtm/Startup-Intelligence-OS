"""Pydantic V2 models for Birch signal scoring."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sig_id() -> str:
    return f"sig-{uuid.uuid4().hex[:12]}"


class RawSignal(BaseModel):
    id: str = Field(default_factory=_sig_id)
    source: Literal["firehose", "trendradar", "morning_intel", "manual"] = "manual"
    title: str
    content: str = ""
    url: str = ""
    published_at: str = Field(default_factory=_now_iso)
    metadata: dict = Field(default_factory=dict)


class ScoredSignal(BaseModel):
    id: str = Field(default_factory=_sig_id)
    source: str
    title: str
    content: str = ""
    url: str = ""
    relevance: int = Field(ge=0, le=100, default=0)
    actionability: int = Field(ge=0, le=100, default=0)
    urgency: int = Field(ge=0, le=100, default=0)
    score: int = Field(ge=0, le=100, default=0)
    tier: Literal[1, 2, 3] = 3
    company: str = ""
    routed_to: str = ""
    scored_at: str = Field(default_factory=_now_iso)
