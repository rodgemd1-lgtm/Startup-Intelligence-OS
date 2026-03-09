"""Generate a current foundry assessment snapshot for key companies."""

from __future__ import annotations

import json
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from control_plane.foundry import build_foundry_assessment, render_foundry_assessment_markdown


COMPANIES = ["founder-intelligence-os", "transformfit", "alex-recruiting"]


def main() -> int:
    report = build_foundry_assessment(COMPANIES)
    output_dir = BACKEND_ROOT / "artifacts" / "foundry_assessment"
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "foundry_assessment.json"
    md_path = output_dir / "foundry_assessment.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(render_foundry_assessment_markdown(report), encoding="utf-8")

    print(
        json.dumps(
            {
                "json": str(json_path),
                "markdown": str(md_path),
                "companies": [company["company_id"] for company in report["companies"]],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
