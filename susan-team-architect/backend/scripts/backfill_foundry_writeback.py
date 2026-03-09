"""Backfill foundry writeback summaries from existing Susan output directories."""

from __future__ import annotations

import json
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from control_plane.writeback import write_foundry_records_for_output_dir
from susan_core.config import config


def main() -> int:
    summaries = []
    for company_dir in sorted(config.companies_dir.iterdir()):
        if not company_dir.is_dir():
            continue
        output_dir = company_dir / "susan-outputs"
        if not output_dir.exists():
            continue
        if not (output_dir / "problem-framing.json").exists() or not (output_dir / "decision-brief.json").exists():
            continue
        job_id = f"backfill-{company_dir.name}"
        summary = write_foundry_records_for_output_dir(job_id, company_dir.name, output_dir)
        (output_dir / "foundry-writeback.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        summaries.append(summary)
    print(json.dumps({"companies": len(summaries), "summaries": summaries}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
