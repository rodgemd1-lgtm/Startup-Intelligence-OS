"""Ingest shared studio open-source research into Susan's RAG store."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import sys

from supabase import create_client
import yaml

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rag_engine.ingestion.markdown import MarkdownIngestor
from rag_engine.ingestion.web import WebIngestor
from susan_core.config import config


ROOT = BACKEND_ROOT / "data" / "studio_assets" / "open_sources"
MANIFEST_PATH = ROOT / "shared" / "studio_open_sources.yaml"
MARKDOWN_MAP = ROOT / "shared" / "STUDIO_OPEN_SOURCE_RESEARCH_MAP.md"


def _delete_existing(company_id: str, data_type: str) -> None:
    supabase = create_client(config.supabase_url, config.supabase_key)
    supabase.table("knowledge_chunks").delete().eq("company_id", company_id).eq("data_type", data_type).execute()


def main() -> int:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8")) or {}
    company_id = manifest.get("company_id", "shared")
    totals: dict[str, int] = defaultdict(int)

    _delete_existing(company_id, "studio_open_research")

    markdown_ingestor = MarkdownIngestor()
    web_ingestor = WebIngestor()

    if MARKDOWN_MAP.exists():
        totals["studio_open_research"] += markdown_ingestor.ingest(
            str(MARKDOWN_MAP),
            company_id=company_id,
            data_type="studio_open_research",
        )

    for source in manifest.get("web_sources", []):
        totals[source["data_type"]] += web_ingestor.ingest(
            source["url"],
            company_id=company_id,
            data_type=source["data_type"],
        )

    print(
        {
            "company_id": company_id,
            "manifest": str(MANIFEST_PATH),
            "stored": dict(totals),
            "total": sum(totals.values()),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
