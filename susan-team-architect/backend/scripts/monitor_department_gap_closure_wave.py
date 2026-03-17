from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import dotenv_values
from supabase import create_client


BACKEND_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_ROOT.parent.parent
MONITOR_PATH = REPO_ROOT / ".startup-os" / "artifacts" / "department-gap-closure-wave-monitor-2026-03-12.md"
ARTIFACT_ROOT = BACKEND_ROOT / "artifacts" / "department_gap_closure_wave"
ENV_PATH = BACKEND_ROOT / ".env"
PROCESS_PATTERN = "scripts/run_department_gap_closure_wave.py"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def active_processes() -> list[str]:
    result = subprocess.run(
        ["pgrep", "-fal", PROCESS_PATTERN],
        capture_output=True,
        text=True,
        check=False,
    )
    lines = []
    for line in result.stdout.splitlines():
        if PROCESS_PATTERN in line and "monitor_department_gap_closure_wave.py" not in line:
            lines.append(line.strip())
    return lines


def latest_summary() -> dict | None:
    latest = ARTIFACT_ROOT / "latest_summary.json"
    if not latest.exists():
        return None
    return json.loads(latest.read_text(encoding="utf-8"))


def get_counts() -> dict[str, dict[str, int]]:
    env = dotenv_values(ENV_PATH)
    client = create_client(env["SUPABASE_URL"], env.get("SUPABASE_KEY") or env.get("SUPABASE_SERVICE_KEY"))
    targets = {
        "founder-intelligence-os": [
            "finance",
            "market_research",
            "legal_compliance",
            "technical_docs",
            "operational_protocols",
        ],
        "mike-job-studio": [
            "training_research",
            "operational_protocols",
            "studio_evals",
        ],
    }
    counts: dict[str, dict[str, int]] = {}
    for company, data_types in targets.items():
        counts[company] = {}
        for data_type in data_types:
            result = (
                client.table("knowledge_chunks")
                .select("id", count="exact")
                .eq("company_id", company)
                .eq("data_type", data_type)
                .execute()
            )
            counts[company][data_type] = result.count or 0
    return counts


def append_update() -> bool:
    processes = active_processes()
    summary = latest_summary()
    counts = get_counts()
    status = "running" if processes else "completed"
    lines = [
        f"## Update {now_utc()}",
        f"- status: `{status}`",
        f"- active processes: `{len(processes)}`",
    ]
    if processes:
        lines.append("- process table:")
        for line in processes:
            lines.append(f"  - `{line}`")
    if summary:
        lines.append(f"- latest summary timestamp: `{summary.get('finished_at', 'pending')}`")
        lines.append(f"- latest summary chunks: `{summary.get('total_chunks', 0)}`")
        lines.append(f"- latest summary errors: `{summary.get('total_errors', 0)}`")
    lines.append("- exact counts:")
    for company, data_types in counts.items():
        lines.append(f"  - `{company}`")
        for data_type, count in data_types.items():
            lines.append(f"    - `{data_type}`: `{count}`")
    MONITOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MONITOR_PATH.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n\n")
    return bool(processes)


def main() -> int:
    MONITOR_PATH.write_text(
        "# Department Gap Closure Wave Monitor\n\n"
        "This file is updated automatically every 15 minutes while the department gap closure wave is active.\n",
        encoding="utf-8",
    )
    keep_running = append_update()
    while keep_running:
        time.sleep(900)
        keep_running = append_update()
    return 0


if __name__ == "__main__":
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))
    raise SystemExit(main())
