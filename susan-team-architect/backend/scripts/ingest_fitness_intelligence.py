"""Build structured records and chunks for the fitness intelligence domain."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import argparse

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fitness_intel.pipeline import CorpusBuilder
from fitness_intel.startup_os import to_startup_os_knowledge_chunk
from rag_engine.ingestion.fitness_domain import FitnessDomainIngestor


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and optionally ingest the fitness intelligence domain.")
    parser.add_argument("--store", action="store_true", help="Store chunks in Susan's retriever backend.")
    parser.add_argument("--company-id", default="shared")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    backend_root = BACKEND_ROOT
    domain_root = backend_root / "data" / "domains" / "fitness_app_intelligence"
    repo_root = domain_root / "editorial"
    artifacts_root = backend_root / "artifacts" / "fitness_intelligence"
    artifacts_root.mkdir(parents=True, exist_ok=True)

    builder = CorpusBuilder(repo_root)
    inventory = builder.build_inventory()
    app_records = builder.build_app_records(limit=args.limit)
    chunks = builder.build_chunks(limit=args.limit)
    startup_os_chunks = [to_startup_os_knowledge_chunk(chunk) for chunk in chunks]
    stored = None

    if args.store:
        ingestor = FitnessDomainIngestor()
        stored = ingestor.ingest(
            source=str(repo_root),
            company_id=args.company_id,
            limit=args.limit,
        )

    (artifacts_root / "inventory.json").write_text(
        json.dumps(inventory, indent=2),
        encoding="utf-8",
    )
    builder.export_jsonl(app_records, artifacts_root / "app_records.jsonl")
    builder.export_jsonl(
        [chunk.model_dump(mode="json") for chunk in chunks],
        artifacts_root / "chunks.jsonl",
    )
    builder.export_jsonl(startup_os_chunks, artifacts_root / "startup_os_chunks.jsonl")

    print(
        json.dumps(
            {
                "inventory": inventory,
                "domain_root": str(domain_root),
                "app_records": len(app_records),
                "chunks": len(chunks),
                "stored": stored,
                "artifacts_root": str(artifacts_root),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
