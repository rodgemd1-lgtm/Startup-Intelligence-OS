from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rag_engine.batch import execute_manifest

MANIFEST_DIR = BACKEND_ROOT / "data" / "scrape_manifests"
ARTIFACT_ROOT = BACKEND_ROOT / "artifacts" / "stronger_dataset_benchmark_wave"

MANIFESTS = [
    "startup_os_stronger_benchmark_case_library.yaml",
    "startup_os_eval_and_synthetic_review_foundations.yaml",
    "job_studio_training_learning_science_stronger.yaml",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the stronger dataset and benchmark enrichment wave.")
    parser.add_argument("--resume", action="store_true", help="Skip sources already ingested when source_url matches.")
    return parser


def summarize(markdown_path: Path, payload: dict) -> None:
    lines = [
        "# Stronger Dataset Benchmark Wave Summary",
        "",
        f"- started_at: `{payload['started_at']}`",
        f"- finished_at: `{payload['finished_at']}`",
        f"- manifest_count: `{payload['manifest_count']}`",
        f"- total_chunks: `{payload['total_chunks']}`",
        f"- total_errors: `{payload['total_errors']}`",
        "",
        "## Manifest Results",
        "",
        "| Manifest | Company | Data type | Chunks | Errors | Sources |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for result in payload["results"]:
        lines.append(
            f"| {result['manifest']} | {result['company']} | {result['data_type']} | "
            f"{result['total_chunks']} | {result['errors']} | {result['sources_total']} |"
        )
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_manifest_meta(path: Path) -> dict:
    import yaml

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    meta = data.get("manifest", {})
    return {
        "name": meta.get("name", path.name),
        "company": meta.get("company", "shared"),
        "data_type": meta.get("data_type", "unknown"),
    }


def main() -> int:
    args = build_parser().parse_args()
    started_at = now_utc()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = ARTIFACT_ROOT / stamp
    run_dir.mkdir(parents=True, exist_ok=True)

    results = []
    total_chunks = 0
    total_errors = 0

    for manifest_name in MANIFESTS:
        manifest_path = MANIFEST_DIR / manifest_name
        meta = load_manifest_meta(manifest_path)
        result = execute_manifest(manifest_path, resume=args.resume)
        total_chunks += result.get("total_chunks", 0)
        total_errors += result.get("errors", 0)
        results.append(
            {
                "manifest_file": manifest_name,
                "manifest": meta["name"],
                "company": meta["company"],
                "data_type": meta["data_type"],
                "total_chunks": result.get("total_chunks", 0),
                "errors": result.get("errors", 0),
                "sources_total": result.get("sources_total", 0),
                "completed": result.get("completed", 0),
                "skipped": result.get("skipped", 0),
                "error_messages": result.get("error_messages", []),
            }
        )

    payload = {
        "started_at": started_at,
        "finished_at": now_utc(),
        "manifest_count": len(MANIFESTS),
        "resume": args.resume,
        "total_chunks": total_chunks,
        "total_errors": total_errors,
        "results": results,
    }

    json_path = run_dir / "summary.json"
    md_path = run_dir / "summary.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    summarize(md_path, payload)

    latest_json = ARTIFACT_ROOT / "latest_summary.json"
    latest_md = ARTIFACT_ROOT / "latest_summary.md"
    shutil.copyfile(json_path, latest_json)
    shutil.copyfile(md_path, latest_md)

    print(json.dumps({"run_dir": str(run_dir), **payload}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
