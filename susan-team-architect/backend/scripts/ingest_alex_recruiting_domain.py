"""Ingest Alex Recruiting editorial and open-source domain assets."""

from __future__ import annotations

from collections import defaultdict
import json
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


DOMAIN_ROOT = BACKEND_ROOT / "data" / "domains" / "alex_recruiting_intelligence"
MANIFEST_PATH = DOMAIN_ROOT / "datasets" / "open_sources.yaml"
EDITORIAL_PATHS = {
    "recruiting_intelligence": [
        DOMAIN_ROOT / "editorial" / "ALEX_RECRUITING_DOMAIN_BRIEF.md",
        Path("/Users/mikerodgers/Desktop/alex-recruiting-project/alex-recruiting/docs/plans/2026-03-06-rec-system-design.md"),
    ],
    "recruiting_film": [
        DOMAIN_ROOT / "editorial" / "ALEX_RECRUITING_HIGHLIGHT_REEL_STUDIO_BRIEF.md",
    ],
    "coach_outreach": [
        DOMAIN_ROOT / "editorial" / "ALEX_RECRUITING_COACH_OUTREACH_STUDIO_BRIEF.md",
    ],
    "social_growth": [
        DOMAIN_ROOT / "editorial" / "ALEX_RECRUITING_X_GROWTH_STUDIO_BRIEF.md",
    ],
    "dashboard_design": [
        DOMAIN_ROOT / "editorial" / "ALEX_RECRUITING_DASHBOARD_STUDIO_BRIEF.md",
    ],
}
RESET_TYPES = [
    "recruiting_intelligence",
    "recruiting_film",
    "coach_outreach",
    "social_growth",
    "dashboard_design",
]


def _delete_existing(company_id: str, data_type: str) -> None:
    supabase = create_client(config.supabase_url, config.supabase_key)
    supabase.table("knowledge_chunks").delete().eq("company_id", company_id).eq("data_type", data_type).execute()


def main() -> int:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8")) or {}
    company_id = manifest.get("company_id", "alex-recruiting")

    for data_type in RESET_TYPES:
        _delete_existing(company_id, data_type)

    totals: dict[str, int] = defaultdict(int)
    markdown_ingestor = MarkdownIngestor()
    web_ingestor = WebIngestor()

    for data_type, paths in EDITORIAL_PATHS.items():
        for path in paths:
            if path.exists():
                totals[data_type] += markdown_ingestor.ingest(str(path), company_id=company_id, data_type=data_type)

    for source in manifest.get("web_sources", []):
        totals[source["data_type"]] += web_ingestor.ingest(
            source["url"],
            company_id=company_id,
            data_type=source["data_type"],
        )

    print(
        json.dumps(
            {
                "company_id": company_id,
                "manifest": str(MANIFEST_PATH),
                "stored": dict(totals),
                "total": sum(totals.values()),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
