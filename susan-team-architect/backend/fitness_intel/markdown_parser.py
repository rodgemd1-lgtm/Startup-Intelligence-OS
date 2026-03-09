"""Markdown parsing and normalization."""

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import re
from typing import Optional

from .schemas import (
    AppRecord,
    ClaimRecord,
    CompanyRecord,
    DemographicSegment,
    EvidenceGrade,
    EvidenceRecord,
    FeatureRecord,
    MetricRecord,
    SourceRecord,
    SourceType,
    VerificationStatus,
)


@dataclass
class ParsedMarkdownProfile:
    path: Path
    title: str
    metadata: dict[str, str]
    sections: dict[str, str]
    tables: dict[str, list[dict[str, str]]]
    raw_text: str


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def parse_fuzzy_date(value: str) -> date:
    cleaned = value.strip()
    for fmt in ("%Y-%m-%d", "%B %Y", "%b %Y", "%B %d, %Y", "%b %d, %Y"):
        try:
            parsed = datetime.strptime(cleaned, fmt)
            if fmt in ("%B %Y", "%b %Y"):
                return date(parsed.year, parsed.month, 1)
            return parsed.date()
        except ValueError:
            continue
    return date(2026, 3, 3)


def infer_category_from_path(path: Path) -> str:
    parts = path.parts
    if "apps" in parts:
        idx = parts.index("apps")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    if "analysis" in parts:
        return "analysis"
    return "docs"


def parse_markdown_table(table_text: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in table_text.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return []
    headers = [cell.strip(" *") for cell in lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in lines[2:]:
        values = [cell.strip() for cell in line.strip("|").split("|")]
        if len(values) != len(headers):
            continue
        rows.append(dict(zip(headers, values)))
    return rows


def parse_markdown_profile(path: Path) -> ParsedMarkdownProfile:
    raw = path.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.*)$", raw, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else path.stem

    metadata: dict[str, str] = {}
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("> **") and ":**" in stripped:
            cleaned = stripped.removeprefix("> ").strip("*")
            key, value = cleaned.split(":**", 1)
            metadata[key.strip("* ")] = value.strip()
        elif stripped.startswith("**") and ":**" in stripped:
            cleaned = stripped.strip("*")
            key, value = cleaned.split(":**", 1)
            metadata[key.strip("* ")] = value.strip()
        if stripped.startswith("## "):
            break

    sections: dict[str, str] = {}
    tables: dict[str, list[dict[str, str]]] = {}
    chunks = re.split(r"(?=^##\s+)", raw, flags=re.MULTILINE)
    for chunk in chunks:
        match = re.match(r"^##\s+(.*)$", chunk.strip(), re.MULTILINE)
        if not match:
            continue
        heading = match.group(1).strip()
        body = chunk.split("\n", 1)[1].strip() if "\n" in chunk else ""
        sections[heading] = body
        table_rows = parse_markdown_table(body)
        if table_rows:
            tables[heading] = table_rows

    return ParsedMarkdownProfile(
        path=path,
        title=title,
        metadata=metadata,
        sections=sections,
        tables=tables,
        raw_text=raw,
    )


def build_editorial_source(profile: ParsedMarkdownProfile) -> SourceRecord:
    captured = profile.metadata.get("Last Updated", "2026-03-03")
    return SourceRecord(
        id=f"source-{slugify(profile.path.stem)}-editorial",
        title=profile.title,
        source_url=str(profile.path),
        source_type=SourceType.editorial_profile,
        captured_at=parse_fuzzy_date(captured),
        effective_date=parse_fuzzy_date(captured),
        confidence=0.6,
        verification_status=VerificationStatus.analyst_reviewed,
        evidence_grade=EvidenceGrade.strong_secondary,
    )


def infer_summary(profile: ParsedMarkdownProfile) -> str:
    for key in ("Overview", "Company Overview", "What It Is", "Core Thesis"):
        body = profile.sections.get(key)
        if body:
            first_paragraph = body.split("\n\n")[0].strip()
            return re.sub(r"\s+", " ", first_paragraph)
    paragraphs = [line.strip() for line in profile.raw_text.splitlines() if line.strip() and not line.startswith("#")]
    return re.sub(r"\s+", " ", paragraphs[0]) if paragraphs else profile.title


def infer_company(profile: ParsedMarkdownProfile) -> Optional[CompanyRecord]:
    overview_tables = profile.tables.get("1. Overview") or profile.tables.get("1. Company Overview")
    if not overview_tables:
        return None

    field_map = {}
    for row in overview_tables:
        keys = list(row.keys())
        if len(keys) < 2:
            continue
        field_map[row[keys[0]].lower()] = row[keys[1]]

    company_name = field_map.get("full name") or profile.title.split(" -- ", 1)[0]
    return CompanyRecord(
        id=f"company-{slugify(company_name)}",
        name=company_name,
        headquarters=field_map.get("headquarters"),
        founded_year=_extract_year(field_map.get("founded")),
        status=field_map.get("parent company") or field_map.get("status"),
        aliases=[],
        sources=[build_editorial_source(profile)],
    )


def _extract_year(value: Optional[str]) -> Optional[int]:
    if not value:
        return None
    match = re.search(r"(19|20)\d{2}", value)
    return int(match.group(0)) if match else None


def build_app_record(profile: ParsedMarkdownProfile) -> AppRecord:
    name = profile.title.split(" -- ", 1)[0].split(" — ", 1)[0].strip()
    category = profile.metadata.get("Category", infer_category_from_path(profile.path))
    source = build_editorial_source(profile)
    evidence = EvidenceRecord(
        source_id=source.id,
        source_url=source.source_url,
        source_type=source.source_type,
        captured_at=source.captured_at,
        effective_date=source.effective_date,
        confidence=source.confidence,
        verification_status=source.verification_status,
        evidence_grade=source.evidence_grade,
    )
    features: list[FeatureRecord] = []
    core_features = profile.sections.get("3. Core Features") or profile.sections.get("4. Core Features & Product")
    if core_features:
        for line in core_features.splitlines():
            if line.strip().startswith("- "):
                feature_name = line.strip()[2:].split(":", 1)[0].strip("* ")
                if feature_name:
                    features.append(
                        FeatureRecord(
                            id=f"feature-{slugify(name)}-{slugify(feature_name)}",
                            name=feature_name,
                            category="core_feature",
                            summary=line.strip()[2:],
                            evidence=[evidence],
                        )
                    )

    demographics: list[DemographicSegment] = []
    if "2. User Demographics" in profile.sections or "2. Target Demographics" in profile.sections:
        label = "target-demographics"
        body = profile.sections.get("2. User Demographics") or profile.sections.get("2. Target Demographics") or ""
        demographics.append(
            DemographicSegment(
                id=f"demographic-{slugify(name)}-{label}",
                label=label,
                details=re.sub(r"\s+", " ", body.split("\n\n")[0]).strip(),
                evidence=[evidence],
            )
        )

    metrics: list[MetricRecord] = []
    metrics_body = profile.sections.get("3. Key Metrics & Business Performance") or profile.sections.get("2. User Demographics")
    if metrics_body:
        rows = parse_markdown_table(metrics_body)
        for row in rows[:5]:
            keys = list(row.keys())
            if len(keys) < 2:
                continue
            metrics.append(
                MetricRecord(
                    id=f"metric-{slugify(name)}-{slugify(row[keys[0]])}",
                    name=row[keys[0]],
                    value=row[keys[1]],
                    metric_type="editorial_metric",
                    as_of_date=source.effective_date,
                    evidence=[evidence],
                )
            )

    company = infer_company(profile)
    claims = [
        ClaimRecord(
            id=f"claim-{slugify(name)}-summary",
            entity_type="app",
            entity_id=f"app-{slugify(name)}",
            field_name="summary",
            value=infer_summary(profile),
            as_of_date=source.effective_date,
            evidence=[evidence],
        )
    ]

    return AppRecord(
        id=f"app-{slugify(name)}",
        slug=slugify(name),
        name=name,
        category=category,
        company_id=company.id if company else None,
        platforms=_extract_platforms(profile),
        editorial_markdown_path=str(profile.path),
        summary=infer_summary(profile),
        aliases=[],
        features=features,
        pricing=[],
        metrics=metrics,
        demographics=demographics,
        integrations=[],
        claims=claims,
        sources=[source],
        verification_status=VerificationStatus.analyst_reviewed,
    )


def _extract_platforms(profile: ParsedMarkdownProfile) -> list[str]:
    text = profile.raw_text
    platforms = []
    for label in ("iOS", "Android", "Web", "Apple Watch", "WearOS", "Wear OS"):
        if label.lower() in text.lower():
            platforms.append(label)
    return platforms
