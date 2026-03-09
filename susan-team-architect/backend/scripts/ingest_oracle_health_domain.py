"""Ingest Oracle Health domain markdown assets into Susan's RAG store."""
from __future__ import annotations

from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rag_engine.ingestion.markdown import MarkdownIngestor


COMPANY_ID = "oracle-health-ai-enablement"

PATHS = {
    "market_research": [
        BACKEND_ROOT / "data" / "domains" / "oracle_health_intelligence" / "README.md",
        BACKEND_ROOT / "data" / "domains" / "oracle_health_intelligence" / "editorial" / "market",
        BACKEND_ROOT / "data" / "domains" / "oracle_health_intelligence" / "editorial" / "docs",
    ],
    "technical_docs": [
        BACKEND_ROOT / "data" / "domains" / "oracle_health_intelligence" / "editorial" / "clinical",
    ],
    "legal_compliance": [
        BACKEND_ROOT / "data" / "domains" / "oracle_health_intelligence" / "editorial" / "regulatory",
    ],
    "content_strategy": [
        BACKEND_ROOT / "data" / "domains" / "oracle_health_intelligence" / "editorial" / "marketing",
        BACKEND_ROOT / "data" / "domains" / "oracle_health_intelligence" / "studios" / "slide_studio",
        BACKEND_ROOT / "data" / "domains" / "oracle_health_intelligence" / "studios" / "marketing_studio",
    ],
}


def main() -> int:
    ingestor = MarkdownIngestor()
    total = 0
    for data_type, paths in PATHS.items():
        for path in paths:
            if path.exists():
                total += ingestor.ingest(str(path), company_id=COMPANY_ID, data_type=data_type)
    print({"stored": total, "domain": "oracle_health_intelligence", "company_id": COMPANY_ID})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
