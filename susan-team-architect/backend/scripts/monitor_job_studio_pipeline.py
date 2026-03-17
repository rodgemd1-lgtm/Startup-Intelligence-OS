"""Append Job Studio pipeline status updates every 15 minutes until completion."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
import time


BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parents[1]
SUMMARY_PATH = BACKEND_ROOT / "artifacts" / "job_studio_training_factory_corpus" / "summary.json"
LOG_PATH = REPO_ROOT / ".startup-os" / "artifacts" / "job-studio-pipeline-monitor-2026-03-12.md"
INTERVAL_SECONDS = 15 * 60


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def process_rows() -> list[str]:
    rows: list[str] = []
    patterns = [
        "scripts.build_job_studio_training_factory_corpus",
        "scripts.ingest_job_studio_training_factory",
    ]
    for pattern in patterns:
        result = subprocess.run(
            ["pgrep", "-fal", pattern],
            capture_output=True,
            text=True,
            check=False,
        )
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            if "monitor_job_studio_pipeline.py" in line:
                continue
            if line not in rows:
                rows.append(line)
    return rows


def read_summary() -> dict[str, object]:
    if not SUMMARY_PATH.exists():
        return {}
    try:
        return json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def append_update(status: str, rows: list[str], summary: dict[str, object]) -> None:
    if not LOG_PATH.exists():
        LOG_PATH.write_text(
            "# Job Studio Pipeline Monitor\n\n"
            "This file is updated automatically every 15 minutes while the corpus extraction and ingest jobs are active.\n\n",
            encoding="utf-8",
        )

    lines = [
        f"## Update {now_utc()}",
        f"- status: `{status}`",
        f"- active processes: `{len(rows)}`",
    ]
    if rows:
        lines.append("- process table:")
        for row in rows:
            lines.append(f"  - `{row}`")
    if summary:
        totals = summary.get("source_totals", {})
        lines.append(
            "- corpus summary:"
        )
        lines.append(
            "  - "
            f"seen={totals.get('documents_seen', 0)} "
            f"extracted={totals.get('documents_extracted', 0)} "
            f"cached={totals.get('documents_cached', 0)} "
            f"skipped={totals.get('documents_skipped', 0)} "
            f"failed={totals.get('documents_failed', 0)} "
            f"chars={totals.get('extracted_chars', 0)}"
        )
        lines.append(f"  - summary_generated_at: `{summary.get('generated_at', '')}`")
        lines.append(f"  - active_group: `{summary.get('active_group', '')}`")
    lines.append("")
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def main() -> int:
    while True:
        rows = process_rows()
        summary = read_summary()
        if rows:
            append_update("running", rows, summary)
            time.sleep(INTERVAL_SECONDS)
            continue
        append_update("completed", rows, summary)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
