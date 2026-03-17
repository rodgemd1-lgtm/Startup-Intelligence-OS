#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT / "apps"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from decision_os.simulated_maturity import run_simulated_maturity_harness  # noqa: E402


def main() -> int:
    result = run_simulated_maturity_harness()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
