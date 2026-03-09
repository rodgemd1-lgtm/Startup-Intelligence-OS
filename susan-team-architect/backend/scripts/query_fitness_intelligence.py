"""Query helper for the merged fitness intelligence domain."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rag_engine.retriever import Retriever


DEFAULT_TYPES = ["fitness_docs", "fitness_analysis", "fitness_app_profile"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Query the fitness intelligence domain.")
    parser.add_argument("query")
    parser.add_argument("--company-id", default="shared")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--types", default=",".join(DEFAULT_TYPES))
    args = parser.parse_args()

    data_types = [item.strip() for item in args.types.split(",") if item.strip()]
    retriever = Retriever()
    results = retriever.search(
        args.query,
        args.company_id,
        data_types=data_types,
        top_k=args.top_k,
    )
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
