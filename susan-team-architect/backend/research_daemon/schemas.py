"""
Pydantic V2 models for the Research Daemon.

All models use strict validation with sensible defaults. IDs are generated
via SHA-256 hashing (first 12 hex chars) to stay deterministic and
consistent with the Startup OS kernel convention.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field


def _generate_id(prefix: str, seed: str) -> str:
    """Deterministic ID: prefix + first 12 chars of SHA-256 hex digest."""
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def _now_iso() -> str:
    """Current UTC timestamp in ISO-8601."""
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# ResearchGap
# ---------------------------------------------------------------------------

class ResearchGap(BaseModel):
    """A detected gap in the knowledge base or research corpus."""

    id: str = Field(
        default="",
        description="Deterministic ID (gap-<sha256[:12]>).",
    )
    domain: str = Field(
        ...,
        description="Knowledge domain or capability area.",
    )
    description: str = Field(
        ...,
        description="Human-readable description of the gap.",
    )
    severity: Literal["critical", "high", "medium", "low"] = Field(
        default="medium",
        description="Impact severity of the gap.",
    )
    current_coverage: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Current coverage score (0 = none, 1 = comprehensive).",
    )
    target_coverage: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Desired coverage score.",
    )
    suggested_queries: list[str] = Field(
        default_factory=list,
        description="Search queries that could fill the gap.",
    )
    discovered_at: str = Field(
        default_factory=_now_iso,
        description="ISO-8601 timestamp of discovery.",
    )
    status: Literal["open", "researching", "filled", "dismissed"] = Field(
        default="open",
        description="Lifecycle status of the gap.",
    )

    def model_post_init(self, __context: object) -> None:
        if not self.id:
            seed = f"{self.domain}::{self.description}"
            self.id = _generate_id("gap", seed)


# ---------------------------------------------------------------------------
# HarvestResult
# ---------------------------------------------------------------------------

class HarvestResult(BaseModel):
    """A single piece of harvested research material."""

    id: str = Field(
        default="",
        description="Deterministic ID (harvest-<sha256[:12]>).",
    )
    gap_id: Optional[str] = Field(
        default=None,
        description="ID of the ResearchGap this result addresses.",
    )
    source_url: str = Field(
        ...,
        description="URL the content was harvested from.",
    )
    title: str = Field(
        ...,
        description="Title of the harvested content.",
    )
    content_summary: str = Field(
        ...,
        description="Summarized content of the source.",
    )
    quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall quality score.",
    )
    relevance_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Relevance to the target domain.",
    )
    source_authority: Literal["official", "practitioner", "community", "unknown"] = Field(
        default="unknown",
        description="Authority classification of the source.",
    )
    harvested_at: str = Field(
        default_factory=_now_iso,
        description="ISO-8601 timestamp of harvest.",
    )
    integrated: bool = Field(
        default=False,
        description="Whether the result has been ingested into the RAG corpus.",
    )
    chunk_ids: list[str] = Field(
        default_factory=list,
        description="RAG chunk IDs after ingestion.",
    )

    def model_post_init(self, __context: object) -> None:
        if not self.id:
            seed = f"{self.source_url}::{self.title}"
            self.id = _generate_id("harvest", seed)


# ---------------------------------------------------------------------------
# ChangelogEntry
# ---------------------------------------------------------------------------

class ChangelogEntry(BaseModel):
    """A changelog entry for a tracked dependency."""

    package: str = Field(
        ...,
        description="Package name.",
    )
    version: str = Field(
        ...,
        description="New version string.",
    )
    release_date: str = Field(
        default_factory=_now_iso,
        description="Release date (ISO-8601 or date string).",
    )
    changes_summary: str = Field(
        default="",
        description="Human-readable summary of changes.",
    )
    breaking_changes: list[str] = Field(
        default_factory=list,
        description="List of breaking changes.",
    )
    new_features: list[str] = Field(
        default_factory=list,
        description="List of new features.",
    )
    deprecations: list[str] = Field(
        default_factory=list,
        description="List of deprecations.",
    )
    url: str = Field(
        default="",
        description="URL to the changelog or release page.",
    )
    severity: Literal["breaking", "minor", "patch"] = Field(
        default="patch",
        description="Severity classification of the update.",
    )


# ---------------------------------------------------------------------------
# ResearchProgram
# ---------------------------------------------------------------------------

class ResearchProgram(BaseModel):
    """A planned or active research program spanning multiple gaps."""

    id: str = Field(
        default="",
        description="Deterministic ID (prog-<sha256[:12]>).",
    )
    name: str = Field(
        ...,
        description="Program name.",
    )
    description: str = Field(
        default="",
        description="What this research program aims to accomplish.",
    )
    gaps: list[str] = Field(
        default_factory=list,
        description="List of ResearchGap IDs covered by this program.",
    )
    status: Literal["planned", "active", "completed", "paused"] = Field(
        default="planned",
        description="Current program status.",
    )
    created_at: str = Field(
        default_factory=_now_iso,
        description="ISO-8601 creation timestamp.",
    )
    updated_at: str = Field(
        default_factory=_now_iso,
        description="ISO-8601 last-update timestamp.",
    )
    results: list[str] = Field(
        default_factory=list,
        description="List of HarvestResult IDs produced by this program.",
    )
    schedule: Literal["daily", "weekly", "monthly"] = Field(
        default="weekly",
        description="How often this program runs.",
    )

    def model_post_init(self, __context: object) -> None:
        if not self.id:
            seed = f"{self.name}::{self.description}"
            self.id = _generate_id("prog", seed)


# ---------------------------------------------------------------------------
# DaemonStatus
# ---------------------------------------------------------------------------

class DaemonStatus(BaseModel):
    """Snapshot of the research daemon's current state."""

    last_run: str = Field(
        default="",
        description="ISO-8601 timestamp of the last completed cycle.",
    )
    next_run: str = Field(
        default="",
        description="ISO-8601 timestamp of the next scheduled cycle.",
    )
    gaps_detected: int = Field(
        default=0,
        ge=0,
        description="Total gaps detected in the last cycle.",
    )
    gaps_filled: int = Field(
        default=0,
        ge=0,
        description="Total gaps marked as filled.",
    )
    items_harvested: int = Field(
        default=0,
        ge=0,
        description="Total items harvested in the last cycle.",
    )
    programs_active: int = Field(
        default=0,
        ge=0,
        description="Number of active research programs.",
    )
    health: Literal["healthy", "degraded", "error"] = Field(
        default="healthy",
        description="Overall daemon health.",
    )
