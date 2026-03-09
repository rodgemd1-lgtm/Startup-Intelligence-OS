"""Ingest shared studio assets and company-specific studio memory into Susan's RAG store."""
from __future__ import annotations

from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rag_engine.ingestion.markdown import MarkdownIngestor


ROOT = BACKEND_ROOT / "data" / "studio_assets"

SHARED_PATHS = {
    "studio_case_library": [
        ROOT / "shared" / "case_library",
    ],
    "studio_antipatterns": [
        ROOT / "shared" / "antipatterns",
    ],
    "studio_memory": [
        ROOT / "shared" / "memory",
    ],
    "studio_templates": [
        ROOT / "shared" / "templates",
    ],
    "studio_evals": [
        ROOT / "shared" / "evals",
    ],
}

COMPANY_PATHS = {
    "transformfit": {
        "studio_memory": [
            ROOT / "companies" / "transformfit",
        ],
    },
    "oracle-health-ai-enablement": {
        "studio_memory": [
            ROOT / "companies" / "oracle-health-ai-enablement",
        ],
    },
}


def _ingest_paths(ingestor: MarkdownIngestor, company_id: str, paths_by_type: dict[str, list[Path]]) -> int:
    total = 0
    for data_type, paths in paths_by_type.items():
        for path in paths:
            if path.exists():
                total += ingestor.ingest(str(path), company_id=company_id, data_type=data_type)
    return total


def main() -> int:
    ingestor = MarkdownIngestor()
    totals: dict[str, int] = {}
    totals["shared"] = _ingest_paths(ingestor, "shared", SHARED_PATHS)
    for company_id, paths_by_type in COMPANY_PATHS.items():
        totals[company_id] = _ingest_paths(ingestor, company_id, paths_by_type)
    print({"stored": totals, "root": str(ROOT)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
