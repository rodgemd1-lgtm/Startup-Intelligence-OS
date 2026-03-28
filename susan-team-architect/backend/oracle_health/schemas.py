"""Pydantic schemas for Oracle Health department outputs."""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class Priority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class Freshness(str, Enum):
    FRESH = "FRESH"       # < 14 days
    AGING = "AGING"       # 14-30 days
    STALE = "STALE"       # > 30 days


class Competitor(str, Enum):
    EPIC = "epic"
    MICROSOFT = "microsoft"
    AWS = "aws"
    GOOGLE = "google"
    MEDITECH = "meditech"
    VEEVA = "veeva"


class Persona(str, Enum):
    CIO = "cio"
    CMIO = "cmio"
    VP_OPS = "vp_ops"
    CLINICAL_DIRECTOR = "clinical_director"
    IMPLEMENTATION_LEAD = "implementation_lead"


class SignalCategory(str, Enum):
    PRODUCT_LAUNCH = "product_launch"
    PRICING = "pricing"
    PARTNERSHIP = "partnership"
    ACQUISITION = "acquisition"
    CUSTOMER_WIN = "customer_win"
    CUSTOMER_LOSS = "customer_loss"
    ANALYST_REPORT = "analyst_report"
    EXECUTIVE_MOVE = "executive_move"


class ActionLevel(str, Enum):
    FLASH = "FLASH"         # UxR >= 20
    PRIORITY = "PRIORITY"   # UxR 12-19
    STANDARD = "STANDARD"   # UxR 6-11
    LOG = "LOG"             # UxR 1-5


# --- Signal ---

class CompetitiveSignal(BaseModel):
    id: str = ""
    competitor: Competitor
    priority: Priority
    urgency: int = Field(ge=1, le=5)
    relevance: int = Field(ge=1, le=5)
    category: SignalCategory
    headline: str
    detail: str
    source_url: str = ""
    source_type: str = ""
    affected_personas: list[Persona] = Field(default_factory=list)
    recommended_action: str = ""
    freshness_date: datetime = Field(default_factory=datetime.now)

    @property
    def score(self) -> int:
        return self.urgency * self.relevance

    @property
    def action_level(self) -> ActionLevel:
        s = self.score
        if s >= 20:
            return ActionLevel.FLASH
        elif s >= 12:
            return ActionLevel.PRIORITY
        elif s >= 6:
            return ActionLevel.STANDARD
        return ActionLevel.LOG


# --- Battlecard ---

class WinLossRecord(BaseModel):
    customer: str
    size: str = ""
    reason: str
    date: str
    source: str = ""


class TalkTrack(BaseModel):
    persona: Persona
    lead_with: str
    key_proof: str
    avoid: str = ""


class BattlecardSection(BaseModel):
    know_strategy: str = ""
    know_recent_wins: list[WinLossRecord] = Field(default_factory=list)
    know_recent_losses: list[WinLossRecord] = Field(default_factory=list)
    know_pricing: str = ""
    know_weaknesses: list[str] = Field(default_factory=list)
    say_positioning: str = ""
    say_talk_tracks: list[TalkTrack] = Field(default_factory=list)
    say_landmines: list[str] = Field(default_factory=list)
    say_traps: list[str] = Field(default_factory=list)
    show_evidence: list[str] = Field(default_factory=list)
    show_analyst_ratings: list[str] = Field(default_factory=list)


class Battlecard(BaseModel):
    competitor: Competitor
    priority: Priority
    freshness: Freshness = Freshness.FRESH
    updated: datetime = Field(default_factory=datetime.now)
    sections: BattlecardSection = Field(default_factory=BattlecardSection)


# --- Freshness Report ---

class CompetitorFreshness(BaseModel):
    competitor: Competitor
    latest_data: datetime | None = None
    chunk_count: int = 0
    freshness: Freshness = Freshness.STALE
    data_types_present: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)


class FreshnessReport(BaseModel):
    generated: datetime = Field(default_factory=datetime.now)
    competitors: list[CompetitorFreshness] = Field(default_factory=list)
    total_chunks: int = 0
    overall_health: str = ""


# --- Department Status ---

class DepartmentStatus(BaseModel):
    generated: datetime = Field(default_factory=datetime.now)
    total_agents: int = 12
    active_signals: int = 0
    battlecards_fresh: int = 0
    battlecards_aging: int = 0
    battlecards_stale: int = 0
    freshness_report: FreshnessReport | None = None
    last_sentinel_run: datetime | None = None
    next_actions: list[str] = Field(default_factory=list)
