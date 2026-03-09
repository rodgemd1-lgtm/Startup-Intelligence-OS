"""Backfill visual_assets relational table from knowledge_chunks when the table exists."""
from __future__ import annotations

from pathlib import Path
import sys

from supabase import create_client

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from susan_core.config import config


def main() -> int:
    sb = create_client(config.supabase_url, config.supabase_key)
    rows = (
        sb.table("knowledge_chunks")
        .select("id,company_id,source_url,metadata")
        .eq("data_type", "visual_asset")
        .execute()
        .data
    )
    payload = []
    for row in rows:
        metadata = row.get("metadata") or {}
        payload.append(
            {
                "company_id": row.get("company_id"),
                "title": metadata.get("title") or "Visual asset",
                "asset_type": metadata.get("asset_type", "screenshot"),
                "bucket_name": metadata.get("storage_bucket"),
                "storage_path": metadata.get("storage_path"),
                "public_url": metadata.get("public_url"),
                "source_url": row.get("source_url"),
                "data_type": "visual_asset",
                "metadata": metadata,
            }
        )

    try:
        if payload:
            sb.table("visual_assets").upsert(payload).execute()
        print({"synced": len(payload)})
        return 0
    except Exception as exc:
        print({"synced": 0, "error": str(exc), "note": "Apply supabase migration 20260307010000_visual_assets.sql first."})
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
