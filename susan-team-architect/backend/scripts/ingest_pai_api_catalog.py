"""Ingest PAI (Personal AI Infrastructure) API catalog from openclaw-api-list into Susan's knowledge base."""

from __future__ import annotations

from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rag_engine.ingestion.markdown import MarkdownIngestor

REPO_ROOT = BACKEND_ROOT.parents[1]
WORKTREE_ROOT = REPO_ROOT / ".claude/worktrees/competent-lewin"

def _resolve(rel: str) -> Path:
    wt = WORKTREE_ROOT / rel
    if wt.exists():
        return wt
    return REPO_ROOT / rel

COMPANY_ID = "shared"

PATHS = {
    "framework": [
        _resolve("docs/research/openclaw-api-list-recommended-2026-03-22.md"),
        _resolve("docs/research/openclaw-api-list-focus-2026-03-22.md"),
    ],
}


def main() -> int:
    ingestor = MarkdownIngestor()
    total = 0
    for data_type, paths in PATHS.items():
        for path in paths:
            if path.exists():
                print(f"  Ingesting: {path.name}")
                count = ingestor.ingest(str(path), company_id=COMPANY_ID, data_type=data_type)
                print(f"    -> {count} chunks stored")
                total += count
            else:
                print(f"  SKIP (not found): {path}")
    print({"stored": total, "domain": "pai_api_catalog", "company_id": COMPANY_ID})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
