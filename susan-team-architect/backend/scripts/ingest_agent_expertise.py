"""Ingest agent expertise packs into Susan's shared RAG store."""
from __future__ import annotations

from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rag_engine.ingestion.markdown import MarkdownIngestor


TYPE_MAP = {
    "shared": "agent_expertise",
    "research": "research_expertise",
    "studio": "studio_expertise",
    "product": "product_expertise",
    "engineering": "engineering_expertise",
    "science": "science_expertise",
    "psychology": "psychology_expertise",
    "growth": "growth_expertise",
    "strategy": "strategy_expertise",
    "evals": "agent_eval_expertise",
}


def main() -> int:
    root = BACKEND_ROOT / "data" / "agent_expertise"
    ingestor = MarkdownIngestor()
    total = 0

    for folder, data_type in TYPE_MAP.items():
        path = root / folder
        if not path.exists():
            continue
        total += ingestor.ingest(str(path), company_id="shared", data_type=data_type)

    print({"stored": total, "root": str(root)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
