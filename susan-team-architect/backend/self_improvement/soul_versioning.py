"""SOUL.md Version Control — track changes to Jake's identity configuration.

Maintains a version history of ~/.hermes/SOUL.md changes, diffs between versions,
and allows rollback to previous identities.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


SOUL_PATH = Path.home() / ".hermes" / "SOUL.md"
SOUL_HISTORY_DIR = Path.home() / ".hermes" / ".soul_history"


@dataclass
class SoulVersion:
    version: int
    hash: str
    content: str
    created_at: str
    size_bytes: int
    change_summary: str = ""

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "hash": self.hash,
            "created_at": self.created_at,
            "size_bytes": self.size_bytes,
            "change_summary": self.change_summary,
        }


class SoulVersionControl:
    """Track and manage SOUL.md versions."""

    def __init__(self, soul_path: Path | None = None, history_dir: Path | None = None):
        self.soul_path = soul_path or SOUL_PATH
        self.history_dir = history_dir or SOUL_HISTORY_DIR
        self._index_path = self.history_dir / "index.json"

    def _ensure_dir(self) -> None:
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def _load_index(self) -> list[dict]:
        if not self._index_path.exists():
            return []
        try:
            return json.loads(self._index_path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save_index(self, index: list[dict]) -> None:
        self._ensure_dir()
        self._index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")

    def _hash(self, content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def snapshot(self, change_summary: str = "") -> SoulVersion | None:
        """Snapshot current SOUL.md. Returns version if content changed, None if unchanged."""
        if not self.soul_path.exists():
            return None

        content = self.soul_path.read_text(encoding="utf-8")
        content_hash = self._hash(content)

        index = self._load_index()

        # Check if content changed since last snapshot
        if index and index[-1]["hash"] == content_hash:
            return None  # Unchanged

        version_num = len(index) + 1
        self._ensure_dir()

        # Save versioned copy
        version_file = self.history_dir / f"soul_v{version_num:04d}_{content_hash}.md"
        version_file.write_text(content, encoding="utf-8")

        version = SoulVersion(
            version=version_num,
            hash=content_hash,
            content=content,
            created_at=datetime.now(timezone.utc).isoformat(),
            size_bytes=len(content.encode()),
            change_summary=change_summary or f"Auto-snapshot v{version_num}",
        )
        index.append(version.to_dict())
        self._save_index(index)
        return version

    def list_versions(self) -> list[dict]:
        """Return all version metadata."""
        return self._load_index()

    def get_version(self, version_num: int) -> str | None:
        """Retrieve content of a specific version."""
        index = self._load_index()
        for v in index:
            if v["version"] == version_num:
                # Find the file
                files = list(self.history_dir.glob(f"soul_v{version_num:04d}_*.md"))
                if files:
                    return files[0].read_text(encoding="utf-8")
        return None

    def diff(self, v1: int, v2: int) -> str:
        """Generate a simple diff between two versions."""
        content1 = self.get_version(v1)
        content2 = self.get_version(v2)
        if not content1 or not content2:
            return "One or both versions not found."

        import difflib
        diff = difflib.unified_diff(
            content1.splitlines(keepends=True),
            content2.splitlines(keepends=True),
            fromfile=f"soul_v{v1}",
            tofile=f"soul_v{v2}",
            n=2,
        )
        result = "".join(list(diff)[:50])  # Limit output
        return result if result else "No differences found."

    def rollback(self, version_num: int) -> bool:
        """Restore SOUL.md to a previous version. Creates backup of current first."""
        content = self.get_version(version_num)
        if not content:
            return False

        # Snapshot current before overwriting
        self.snapshot(change_summary=f"Pre-rollback snapshot before restoring v{version_num}")

        # Overwrite
        self.soul_path.write_text(content, encoding="utf-8")
        return True

    def current_version(self) -> int:
        """Return current version number (0 if no history)."""
        index = self._load_index()
        return len(index)

    def report(self) -> str:
        """Plain-text version history report."""
        index = self._load_index()
        if not index:
            return "No SOUL.md snapshots recorded yet. Run snapshot() to begin tracking."

        lines = [f"═══ SOUL.md VERSION HISTORY ({len(index)} versions) ═══", ""]
        for v in index[-5:]:  # Show last 5
            lines.append(
                f"  v{v['version']:04d} [{v['hash']}] "
                f"{v['created_at'][:19]} — {v['change_summary'][:60]}"
            )
        lines.append(f"\n  Current version: {self.current_version()}")
        if self.soul_path.exists():
            current_hash = self._hash(self.soul_path.read_text(encoding="utf-8"))
            last_hash = index[-1]["hash"] if index else ""
            status = "✓ Tracked" if current_hash == last_hash else "⚠ Untracked changes"
            lines.append(f"  Status: {status}")
        return "\n".join(lines)


soul_vc = SoulVersionControl()


def auto_snapshot_on_change() -> None:
    """Called at session start/end to auto-snapshot SOUL.md if changed."""
    version = soul_vc.snapshot(change_summary="Auto-snapshot")
    if version:
        print(f"[soul_vc] Snapshot created: v{version.version} ({version.hash})")
