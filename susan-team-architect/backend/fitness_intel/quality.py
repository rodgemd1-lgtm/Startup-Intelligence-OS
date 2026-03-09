"""Data quality and freshness checks."""

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Union
import yaml

from .schemas import FreshnessCadence, QualityFinding, QualityReport


FRESHNESS_WINDOWS = {
    FreshnessCadence.monthly: 31,
    FreshnessCadence.quarterly: 92,
    FreshnessCadence.semiannual: 184,
}


def stale_after(cadence: FreshnessCadence, anchor: date) -> bool:
    return anchor < (date.today() - timedelta(days=FRESHNESS_WINDOWS[cadence]))


def audit_pilot_data(root: Union[str, Path]) -> QualityReport:
    root_path = Path(root)
    report = QualityReport()
    for yaml_file in sorted(root_path.glob("data/pilot/apps/*.yaml")):
        payload = yaml.safe_load(yaml_file.read_text(encoding="utf-8")) or {}
        app_id = payload.get("id", yaml_file.stem)
        if not payload.get("sources"):
            report.findings.append(
                QualityFinding(
                    severity="high",
                    code="missing_sources",
                    message="App record has no sources.",
                    entity_id=app_id,
                    entity_type="app",
                )
            )
        updated_at = payload.get("updated_at")
        if not updated_at:
            report.findings.append(
                QualityFinding(
                    severity="medium",
                    code="missing_updated_at",
                    message="App record is missing updated_at.",
                    entity_id=app_id,
                    entity_type="app",
                )
            )
        for metric in payload.get("metrics", []):
            if not metric.get("evidence"):
                report.findings.append(
                    QualityFinding(
                        severity="high",
                        code="metric_missing_evidence",
                        message=f"Metric '{metric.get('name')}' has no evidence.",
                        entity_id=app_id,
                        entity_type="app",
                    )
                )
    return report


def audit_chunks_for_citations(chunks: list[dict]) -> QualityReport:
    report = QualityReport()
    for chunk in chunks:
        if not chunk.get("source_path"):
            report.findings.append(
                QualityFinding(
                    severity="high",
                    code="chunk_missing_source_path",
                    message="Chunk is missing source_path.",
                    entity_id=chunk.get("id", "unknown"),
                    entity_type="chunk",
                )
            )
    return report
