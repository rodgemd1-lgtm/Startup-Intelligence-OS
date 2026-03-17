#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT / "apps"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from decision_os.simulated_maturity import run_simulated_maturity_harness  # noqa: E402


def main() -> int:
    simulated = run_simulated_maturity_harness()
    subprocess.run([sys.executable, str(ROOT / "bin" / "build_department_maturity_dashboard.py")], check=True)
    payload = {
        "simulated_summary_path": simulated["summary_path"],
        "dashboard_markdown_path": str(ROOT / ".startup-os" / "artifacts" / "department-maturity-dashboard-2026-03-12.md"),
        "dashboard_html_path": str(ROOT / ".startup-os" / "artifacts" / "department-maturity-dashboard-2026-03-12.html"),
        "dashboard_png_path": str(ROOT / ".startup-os" / "artifacts" / "department-maturity-dashboard-2026-03-12.png"),
        "results": simulated["results"],
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
