"""Sync Susan commands, protocol docs, and agent packs into target project repos."""
from __future__ import annotations

from pathlib import Path
import sys

import yaml

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from control_plane.protocols import sync_project_protocols


def main() -> int:
    config_path = BACKEND_ROOT / "data" / "project_protocol_targets.yaml"
    results = sync_project_protocols(config_path)
    print(yaml.safe_dump({"results": results}, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
