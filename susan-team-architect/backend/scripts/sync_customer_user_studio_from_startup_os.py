"""Sync Customer User Studio artifacts from Startup OS into Susan backend data surface.

Usage:
  python scripts/sync_customer_user_studio_from_startup_os.py
"""

from __future__ import annotations

from pathlib import Path
import shutil
import yaml
from datetime import datetime, timezone


def main() -> int:
    backend_root = Path(__file__).resolve().parents[1]
    repo_root = backend_root.parents[1]

    src_root = repo_root / ".startup-os" / "artifacts" / "customer-user-studio"
    dst_root = backend_root / "data" / "startup_os" / "customer_user_studio"
    dst_root.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    for section in ("personas", "scenarios", "sessions", "reports"):
        src_dir = src_root / section
        dst_dir = dst_root / section
        dst_dir.mkdir(parents=True, exist_ok=True)
        for src in sorted(src_dir.glob("*.yaml")):
            dst = dst_dir / src.name
            shutil.copy2(src, dst)
            copied.append(str(dst.relative_to(repo_root)))

    index = {
        "id": "customer-user-studio-backend-sync",
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "source_root": str(src_root.relative_to(repo_root)),
        "target_root": str(dst_root.relative_to(repo_root)),
        "count": len(copied),
        "files_synced": copied,
    }
    idx_path = dst_root / "sync-index.yaml"
    idx_path.write_text(yaml.safe_dump(index, sort_keys=False))

    print("susan: customer user studio sync complete")
    print(f"  target: {dst_root.relative_to(repo_root)}")
    print(f"  files: {len(copied)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
