"""Corpus scanning, backfill, and export pipeline."""

from collections import Counter
from pathlib import Path
import json
from typing import Optional, Union

from susan_core.config import config

from .chunking import chunk_markdown
from .markdown_parser import build_app_record, infer_category_from_path, parse_fuzzy_date, parse_markdown_profile
from .schemas import DocumentChunk, DomainPackManifest, EvidenceGrade, VerificationStatus


class CorpusBuilder:
    def __init__(self, repo_root: Union[str, Path]):
        self.repo_root = self._resolve_repo_root(Path(repo_root).resolve())

    @staticmethod
    def _resolve_repo_root(repo_root: Path) -> Path:
        """Support both the legacy repo layout and merged domain-pack layout."""
        candidates = [
            repo_root,
            repo_root / "editorial",
            repo_root / "data" / "domains" / "fitness_app_intelligence" / "editorial",
            repo_root / "susan-team-architect" / "backend" / "data" / "domains" / "fitness_app_intelligence" / "editorial",
            config.fitness_domain_dir / "editorial",
        ]

        for candidate in candidates:
            if (candidate / "apps").is_dir():
                return candidate
            editorial_root = candidate / "editorial"
            if (editorial_root / "apps").is_dir():
                return editorial_root

        return repo_root

    def markdown_files(self) -> list[Path]:
        return sorted(self.repo_root.glob("apps/**/*.md")) + sorted(self.repo_root.glob("analysis/*.md")) + sorted(self.repo_root.glob("docs/*.md"))

    def app_markdown_files(self) -> list[Path]:
        return sorted(self.repo_root.glob("apps/**/*.md"))

    def build_inventory(self) -> dict:
        files = self.markdown_files()
        app_files = self.app_markdown_files()
        category_counts = Counter(infer_category_from_path(path) for path in app_files)
        return {
            "repo_root": str(self.repo_root),
            "total_markdown_files": len(files),
            "total_app_profiles": len(app_files),
            "category_counts": dict(category_counts),
            "analysis_documents": len(list(self.repo_root.glob("analysis/*.md"))),
            "docs_documents": len(list(self.repo_root.glob("docs/*.md"))),
        }

    def build_app_records(self, limit: Optional[int] = None) -> list[dict]:
        records = []
        for path in self.app_markdown_files()[:limit]:
            profile = parse_markdown_profile(path)
            app_record = build_app_record(profile)
            records.append(app_record.model_dump(mode="json"))
        return records

    def build_chunks(self, limit: Optional[int] = None) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        for path in self.markdown_files()[:limit]:
            profile = parse_markdown_profile(path)
            chunk_texts = chunk_markdown(profile.raw_text, max_tokens=500)
            source = parse_fuzzy_date(profile.metadata.get("Last Updated", "2026-03-03"))
            category = infer_category_from_path(path)
            for idx, text in enumerate(chunk_texts):
                chunks.append(
                    DocumentChunk(
                        id=f"chunk-{path.stem}-{idx}",
                        content=text,
                        source_path=str(path),
                        source_type="markdown",
                        entity_id=f"app-{path.stem}" if "apps" in path.parts else None,
                        entity_type="app" if "apps" in path.parts else "document",
                        category=category,
                        captured_at=source,
                        verification_status=VerificationStatus.analyst_reviewed,
                        evidence_grade=EvidenceGrade.strong_secondary,
                        metadata={"chunk_index": idx, "title": profile.title},
                    )
                )
        return chunks

    def build_domain_manifest(self) -> DomainPackManifest:
        return DomainPackManifest(
            domain="fitness_app_intelligence",
            version="0.1.0",
            entity_types=[
                "App",
                "Company",
                "Category",
                "Feature",
                "PricingPlan",
                "Metric",
                "DemographicSegment",
                "Integration",
                "Evidence",
                "Source",
                "Claim",
                "Opportunity",
            ],
            ingestion_lanes=["public_web", "paid_datasets", "manual_analyst"],
            retrieval_capabilities=[
                "competitive_lookup",
                "market_segment_analysis",
                "source_grounded_qna",
            ],
            startup_os_boundary={
                "shared_services": [
                    "ingestion_orchestration",
                    "storage",
                    "embeddings",
                    "retrieval",
                    "analyst_workflows",
                ],
                "fitness_domain_responsibilities": [
                    "fitness ontology",
                    "source adapters",
                    "prompts",
                    "quality rules",
                ],
            },
        )

    def export_jsonl(self, records: list[dict], output_path: Union[str, Path]) -> Path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=True) + "\n")
        return output
