"""Route a task to the right Susan agents, data types, and next commands."""
from __future__ import annotations

from pathlib import Path
import json
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from control_plane.protocols import maybe_model_route


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: route_susan_task.py <company_id> <task>")
        return 1

    company_id = sys.argv[1]
    task = " ".join(sys.argv[2:])
    print(json.dumps(maybe_model_route(company_id, task), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
