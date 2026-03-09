"""CLI for backfill, chunk export, and quality reporting."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pipeline import CorpusBuilder
from .quality import audit_chunks_for_citations, audit_pilot_data
from .retrieval import HybridRetriever
from .startup_os import to_startup_os_knowledge_chunk


def main() -> int:
    parser = argparse.ArgumentParser(prog="fitness-intel")
    parser.add_argument("--repo-root", default=".")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("inventory")

    backfill = subparsers.add_parser("backfill")
    backfill.add_argument("--limit", type=int, default=None)
    backfill.add_argument("--output", default="artifacts/backfill/apps.jsonl")

    chunks = subparsers.add_parser("chunks")
    chunks.add_argument("--limit", type=int, default=None)
    chunks.add_argument("--output", default="artifacts/chunks/chunks.jsonl")
    chunks.add_argument("--startup-os-output", default="artifacts/chunks/startup_os_chunks.jsonl")

    audit = subparsers.add_parser("audit")
    audit.add_argument("--output", default="artifacts/reports/quality_report.json")

    query = subparsers.add_parser("query")
    query.add_argument("text")
    query.add_argument("--category", default=None)
    query.add_argument("--top-k", type=int, default=5)

    args = parser.parse_args()
    builder = CorpusBuilder(args.repo_root)

    if args.command == "inventory":
        print(json.dumps(builder.build_inventory(), indent=2))
        return 0

    if args.command == "backfill":
        records = builder.build_app_records(limit=args.limit)
        builder.export_jsonl(records, args.output)
        print(json.dumps({"records": len(records), "output": args.output}, indent=2))
        return 0

    if args.command == "chunks":
        chunks_payload = [chunk.model_dump(mode="json") for chunk in builder.build_chunks(limit=args.limit)]
        builder.export_jsonl(chunks_payload, args.output)
        startup_os_payload = [
            to_startup_os_knowledge_chunk(chunk)
            for chunk in builder.build_chunks(limit=args.limit)
        ]
        builder.export_jsonl(startup_os_payload, args.startup_os_output)
        print(json.dumps({"chunks": len(chunks_payload), "output": args.output}, indent=2))
        return 0

    if args.command == "audit":
        report = audit_pilot_data(args.repo_root)
        chunk_report = audit_chunks_for_citations([chunk.model_dump(mode="json") for chunk in builder.build_chunks(limit=10)])
        combined = {
            "generated_at": report.generated_at.isoformat(),
            "findings": [finding.model_dump(mode="json") for finding in report.findings + chunk_report.findings],
        }
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(combined, indent=2), encoding="utf-8")
        print(json.dumps({"findings": len(combined["findings"]), "output": args.output}, indent=2))
        return 0

    if args.command == "query":
        chunks_payload = [chunk.model_dump(mode="json") for chunk in builder.build_chunks()]
        retriever = HybridRetriever(chunks_payload)
        results = retriever.search(args.text, category=args.category, top_k=args.top_k)
        print(json.dumps(results, indent=2))
        return 0

    return 1

