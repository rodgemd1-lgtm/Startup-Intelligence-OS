"""Canonical schemas for structured fitness intelligence."""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    editorial_profile = "editorial_profile"
    official_website = "official_website"
    app_store = "app_store"
    play_store = "play_store"
    press_release = "press_release"
    investor_filing = "investor_filing"
    paid_dataset = "paid_dataset"
    analyst_manual = "analyst_manual"
    third_party_report = "third_party_report"


class VerificationStatus(str, Enum):
    unverified = "unverified"
    analyst_reviewed = "analyst_reviewed"
    source_verified = "source_verified"
    stale = "stale"


class EvidenceGrade(str, Enum):
    primary = "primary"
    strong_secondary = "strong_secondary"
    weak_secondary = "weak_secondary"
    inferred_estimate = "inferred_estimate"


class FreshnessCadence(str, Enum):
    monthly = "monthly"
    quarterly = "quarterly"
    semiannual = "semiannual"


class SourceRecord(BaseModel):
    id: str
    title: str
    source_url: str
    source_type: SourceType
    captured_at: date
    effective_date: Optional[date] = None
    confidence: float = Field(ge=0, le=1)
    verification_status: VerificationStatus = VerificationStatus.unverified
    evidence_grade: EvidenceGrade
    notes: Optional[str] = None


class EvidenceRecord(BaseModel):
    source_id: str
    source_url: str
    source_type: SourceType
    captured_at: date
    effective_date: Optional[date] = None
    confidence: float = Field(ge=0, le=1)
    verification_status: VerificationStatus = VerificationStatus.unverified
    evidence_grade: EvidenceGrade
    excerpt: Optional[str] = None


class ClaimRecord(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    field_name: str
    value: str
    unit: Optional[str] = None
    as_of_date: Optional[date] = None
    evidence: list[EvidenceRecord] = Field(default_factory=list)


class PricingPlan(BaseModel):
    id: str
    name: str
    billing_interval: str
    amount: Optional[float] = None
    currency: str = "USD"
    trial_days: Optional[int] = None
    free_tier: bool = False
    notes: Optional[str] = None
    evidence: list[EvidenceRecord] = Field(default_factory=list)


class MetricRecord(BaseModel):
    id: str
    name: str
    value: str
    metric_type: str
    as_of_date: Optional[date] = None
    evidence: list[EvidenceRecord] = Field(default_factory=list)


class DemographicSegment(BaseModel):
    id: str
    label: str
    details: str
    evidence: list[EvidenceRecord] = Field(default_factory=list)


class IntegrationRecord(BaseModel):
    id: str
    name: str
    integration_type: str
    status: str
    notes: Optional[str] = None
    evidence: list[EvidenceRecord] = Field(default_factory=list)


class FeatureRecord(BaseModel):
    id: str
    name: str
    category: str
    summary: str
    evidence: list[EvidenceRecord] = Field(default_factory=list)


class CompanyRecord(BaseModel):
    id: str
    name: str
    headquarters: Optional[str] = None
    founded_year: Optional[int] = None
    status: Optional[str] = None
    aliases: list[str] = Field(default_factory=list)
    sources: list[SourceRecord] = Field(default_factory=list)


class AppRecord(BaseModel):
    id: str
    slug: str
    name: str
    category: str
    subcategory: Optional[str] = None
    company_id: Optional[str] = None
    platforms: list[str] = Field(default_factory=list)
    editorial_markdown_path: str
    summary: str
    aliases: list[str] = Field(default_factory=list)
    features: list[FeatureRecord] = Field(default_factory=list)
    pricing: list[PricingPlan] = Field(default_factory=list)
    metrics: list[MetricRecord] = Field(default_factory=list)
    demographics: list[DemographicSegment] = Field(default_factory=list)
    integrations: list[IntegrationRecord] = Field(default_factory=list)
    claims: list[ClaimRecord] = Field(default_factory=list)
    sources: list[SourceRecord] = Field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.unverified
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OpportunityRecord(BaseModel):
    id: str
    title: str
    summary: str
    opportunity_size: str
    execution_difficulty: str
    defensibility: str
    sources: list[SourceRecord] = Field(default_factory=list)


class DocumentChunk(BaseModel):
    id: str
    content: str
    source_path: str
    source_type: str
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    category: Optional[str] = None
    captured_at: date
    verification_status: VerificationStatus
    evidence_grade: EvidenceGrade
    metadata: dict = Field(default_factory=dict)


class QualityFinding(BaseModel):
    severity: str
    code: str
    message: str
    entity_id: str
    entity_type: str


class QualityReport(BaseModel):
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    findings: list[QualityFinding] = Field(default_factory=list)


class DomainPackManifest(BaseModel):
    domain: str
    version: str
    entity_types: list[str]
    ingestion_lanes: list[str]
    retrieval_capabilities: list[str]
    startup_os_boundary: dict
