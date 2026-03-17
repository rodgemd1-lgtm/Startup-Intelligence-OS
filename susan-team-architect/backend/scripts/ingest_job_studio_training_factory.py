"""Ingest Job Studio Training Factory normalized outputs into Susan."""
from __future__ import annotations

import os
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rag_engine.ingestion.markdown import MarkdownIngestor


COMPANY_ID = "mike-job-studio"
GENERATED_ROOT = BACKEND_ROOT / "data" / "studio_assets" / "generated" / "job_studio_training_factory"

PATHS = {
    "market_research": [
        GENERATED_ROOT / "oracle_health_extracted",
        GENERATED_ROOT / "repo_harvest" / "oracle-health-vendor-intelligence",
    ],
    "training_research": [
        GENERATED_ROOT / "behavioral_science_seed",
    ],
    "operational_protocols": [
        GENERATED_ROOT / "repo_harvest" / "oracle-health-ai-enablement",
    ],
    "business_strategy": [
        GENERATED_ROOT / "repo_harvest" / "founder-intelligence-os",
    ],
    "ux_research": [
        GENERATED_ROOT / "repo_harvest" / "ux-design-scraper",
    ],
}


def main() -> int:
    supabase_key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")
    if not os.environ.get("SUPABASE_URL") or not supabase_key:
        print(
            {
                "company_id": COMPANY_ID,
                "stored": {},
                "root": str(GENERATED_ROOT),
                "status": "skipped",
                "reason": "SUPABASE_URL and SUPABASE_KEY or SUPABASE_SERVICE_KEY are required for ingestion",
            }
        )
        return 0

    os.environ.setdefault("SUPABASE_KEY", supabase_key)

    ingestor = MarkdownIngestor()
    totals: dict[str, int] = {}
    for data_type, paths in PATHS.items():
        stored = 0
        for path in paths:
            if path.exists():
                stored += ingestor.ingest(str(path), company_id=COMPANY_ID, data_type=data_type)
        totals[data_type] = stored
    print({"company_id": COMPANY_ID, "stored": totals, "root": str(GENERATED_ROOT)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
