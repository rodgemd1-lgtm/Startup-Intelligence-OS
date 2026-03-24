"""SOUL.md Version Control — Track and rollback Jake's identity changes.

Every change to ~/.hermes/SOUL.md is versioned in a git-like append-only
log at ~/.hermes/logs/soul_versions.jsonl. Allows auditing identity drift
and rolling back to prior versions if behavior degrades.

Usage:
    versioner = SoulVersioner()
    versioner.checkpoint("before A/B test on personality tone")
    # ... modify SOUL.md ...
    versioner.checkpoint("after A/B test — more direct tone")
    diff = versioner.diff_versions("v1", "v2")
    versioner.rollback("v1")
"""

from __future__ import annotations

import difflib
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_SOUL_PATH = Path.home() / ".hermes" / "SOUL.md"
_VERSIONS_LOG = Path.home() / ".hermes" / "logs" / "soul_versions.jsonl"
_VERSIONS_DIR = Path.home() / ".hermes" / "logs" / "soul_archive"


class SoulVersioner:
    """Version control for SOUL.md — Jake's identity layer."""

    def __init__(self, soul_path: Path = _SOUL_PATH) -> None:
        self.soul_path = soul_path
        _VERSIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
        _VERSIONS_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def checkpoint(self, reason: str = "") -> str:
        """Save current SOUL.md as a named version. Returns version_id."""
        if not self.soul_path.exists():
            logger.warning("SOUL.md not found at %s", self.soul_path)
            return ""

        content = self.soul_path.read_text()
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:12]

        # Check if content changed since last checkpoint
        last = self._get_latest()
        if last and last.get("content_hash") == content_hash:
            logger.info("SOUL.md unchanged since last checkpoint (%s)", last["version_id"])
            return last["version_id"]

        version_id = f"v{self._count() + 1}"
        record = {
            "version_id": version_id,
            "content_hash": content_hash,
            "reason": reason,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "size_bytes": len(content.encode()),
            "line_count": content.count("\n") + 1,
        }

        # Archive the full content
        archive_path = _VERSIONS_DIR / f"soul_{version_id}_{content_hash}.md"
        archive_path.write_text(content)
        record["archive_path"] = str(archive_path)

        # Append to log
        with open(_VERSIONS_LOG, "a") as f:
            f.write(json.dumps(record) + "\n")

        logger.info("SOUL.md checkpoint: %s (hash=%s) — %s", version_id, content_hash, reason)
        return version_id

    def rollback(self, version_id: str) -> bool:
        """Restore SOUL.md to a specific version. Returns True on success."""
        record = self._find_version(version_id)
        if not record:
            logger.error("Version %s not found", version_id)
            return False

        archive_path = Path(record["archive_path"])
        if not archive_path.exists():
            logger.error("Archive file missing: %s", archive_path)
            return False

        # Checkpoint current state before rolling back
        self.checkpoint(reason=f"pre-rollback snapshot before restoring {version_id}")

        # Restore
        content = archive_path.read_text()
        self.soul_path.write_text(content)
        logger.info("SOUL.md rolled back to %s", version_id)
        return True

    def diff_versions(self, version_a: str, version_b: str) -> str:
        """Return unified diff between two versions."""
        rec_a = self._find_version(version_a)
        rec_b = self._find_version(version_b)
        if not rec_a or not rec_b:
            return f"Version not found: {version_a if not rec_a else version_b}"

        content_a = Path(rec_a["archive_path"]).read_text().splitlines(keepends=True)
        content_b = Path(rec_b["archive_path"]).read_text().splitlines(keepends=True)

        diff = list(difflib.unified_diff(
            content_a, content_b,
            fromfile=f"SOUL.md ({version_a})",
            tofile=f"SOUL.md ({version_b})",
        ))
        return "".join(diff) if diff else "No differences."

    def list_versions(self) -> list[dict]:
        """Return all checkpointed versions (newest first)."""
        return list(reversed(self._load_all()))

    def get_latest(self) -> Optional[dict]:
        """Return the most recent version record."""
        return self._get_latest()

    def drift_report(self) -> str:
        """Compare current SOUL.md against latest checkpoint. Shows what changed."""
        if not self.soul_path.exists():
            return "SOUL.md not found."
        latest = self._get_latest()
        if not latest:
            return "No checkpoints yet. Run checkpoint() first."
        current = self.soul_path.read_text()
        current_hash = hashlib.sha256(current.encode()).hexdigest()[:12]
        if current_hash == latest["content_hash"]:
            return f"SOUL.md unchanged since {latest['version_id']} ({latest['created_at'][:10]})."
        # Show diff vs latest
        archived = Path(latest["archive_path"]).read_text().splitlines(keepends=True)
        current_lines = current.splitlines(keepends=True)
        diff = list(difflib.unified_diff(
            archived, current_lines,
            fromfile=f"SOUL.md ({latest['version_id']})",
            tofile="SOUL.md (current)",
        ))
        lines_changed = sum(1 for d in diff if d.startswith(("+", "-")) and not d.startswith(("+++", "---")))
        return f"SOUL.md has drifted {lines_changed} lines from {latest['version_id']}:\n" + "".join(diff[:40])

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load_all(self) -> list[dict]:
        if not _VERSIONS_LOG.exists():
            return []
        records = []
        for line in _VERSIONS_LOG.read_text().splitlines():
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return records

    def _find_version(self, version_id: str) -> Optional[dict]:
        for r in self._load_all():
            if r["version_id"] == version_id:
                return r
        return None

    def _get_latest(self) -> Optional[dict]:
        records = self._load_all()
        return records[-1] if records else None

    def _count(self) -> int:
        return len(self._load_all())
