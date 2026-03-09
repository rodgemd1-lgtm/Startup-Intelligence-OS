"""Bootstrap Oracle Health records into Supabase relational tables."""
from __future__ import annotations

from pathlib import Path
import sys

import yaml
from supabase import create_client

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from susan_core.config import config


COMPANY_ID = "oracle-health-ai-enablement"


def main() -> int:
    registry = yaml.safe_load((BACKEND_ROOT / "data" / "company_registry.yaml").read_text(encoding="utf-8"))
    company = registry["companies"][COMPANY_ID]
    sb = create_client(config.supabase_url, config.supabase_key)
    sb.table("companies").upsert(
        {
            "id": COMPANY_ID,
            "name": company["name"],
            "domain": company["domain"],
            "stage": company["stage"],
            "profile": company,
        }
    ).execute()
    print({"bootstrapped_company": COMPANY_ID})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
