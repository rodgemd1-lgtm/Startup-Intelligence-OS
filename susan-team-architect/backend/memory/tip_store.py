"""TIMG Phase 2 -- Tip Storage and Management.

Provides file-backed YAML persistence for MemoryTip objects.  Each tip is
stored as an individual YAML file in the tips directory, following the same
pattern used by the Decision OS run store.

Supports listing with optional filters, deduplication via similarity-based
merging, low-confidence pruning, and access-count tracking for popularity
ranking.
"""
from __future__ import annotations

import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml

from .schemas import MemoryStats, MemoryTip


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _tokenize(text: str) -> set[str]:
    """Simple whitespace + punctuation tokenizer for keyword overlap scoring."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _jaccard_similarity(a: str, b: str) -> float:
    """Compute Jaccard similarity between two text strings."""
    tokens_a = _tokenize(a)
    tokens_b = _tokenize(b)
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


class TipStore:
    """File-backed YAML store for memory tips."""

    def __init__(self, store_path: Path) -> None:
        self.store_path = store_path
        self.store_path.mkdir(parents=True, exist_ok=True)

    def _tip_path(self, tip_id: str) -> Path:
        """Return the filesystem path for a given tip ID."""
        safe_id = tip_id.replace("/", "_")
        return self.store_path / f"{safe_id}.yaml"

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def save_tip(self, tip: MemoryTip) -> str:
        """Save a tip to a YAML file and return its ID."""
        path = self._tip_path(tip.id)
        data = tip.model_dump(exclude_none=True)
        # Exclude embeddings from YAML storage to keep files small
        data.pop("embedding", None)
        path.write_text(yaml.safe_dump(data, default_flow_style=False, sort_keys=False))
        return tip.id

    def load_tip(self, tip_id: str) -> MemoryTip:
        """Load a tip by its ID.  Raises FileNotFoundError if missing."""
        path = self._tip_path(tip_id)
        if not path.exists():
            raise FileNotFoundError(f"Tip not found: {tip_id}")
        data = yaml.safe_load(path.read_text())
        return MemoryTip(**data)

    def delete_tip(self, tip_id: str) -> bool:
        """Delete a tip file.  Returns True if it existed."""
        path = self._tip_path(tip_id)
        if path.exists():
            path.unlink()
            return True
        return False

    # ------------------------------------------------------------------
    # Listing & filtering
    # ------------------------------------------------------------------

    def list_tips(
        self,
        tip_type: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> list[MemoryTip]:
        """List all tips with optional type and domain filters."""
        tips: list[MemoryTip] = []
        for yaml_path in sorted(self.store_path.glob("*.yaml")):
            try:
                data = yaml.safe_load(yaml_path.read_text())
                if data is None:
                    continue
                tip = MemoryTip(**data)
                if tip_type and tip.tip_type != tip_type:
                    continue
                if domain and tip.task_domain != domain:
                    continue
                tips.append(tip)
            except Exception:
                continue
        return tips

    # ------------------------------------------------------------------
    # Merging similar tips
    # ------------------------------------------------------------------

    def merge_similar_tips(
        self,
        tips: list[MemoryTip],
        similarity_threshold: float = 0.85,
    ) -> list[MemoryTip]:
        """Cluster similar tips and merge them, keeping the highest-confidence version.

        Returns the deduplicated list.  Merged (lower-confidence) tips are
        removed from the store on disk.
        """
        if not tips:
            return []

        # Track which tips have been merged away
        merged_away: set[str] = set()
        result: list[MemoryTip] = []
        result_ids: set[str] = set()

        for i, tip_a in enumerate(tips):
            if tip_a.id in merged_away:
                continue

            best = tip_a
            for j in range(i + 1, len(tips)):
                tip_b = tips[j]
                if tip_b.id in merged_away:
                    continue
                if best.tip_type != tip_b.tip_type:
                    continue

                sim = _jaccard_similarity(best.content, tip_b.content)
                if sim >= similarity_threshold:
                    # Keep the one with higher confidence
                    if tip_b.confidence > best.confidence:
                        merged_away.add(best.id)
                        self.delete_tip(best.id)
                        best = tip_b
                    else:
                        merged_away.add(tip_b.id)
                        self.delete_tip(tip_b.id)

            # Only add the survivor if not already in result
            if best.id not in result_ids:
                result.append(best)
                result_ids.add(best.id)

        return result

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_stats(self) -> MemoryStats:
        """Compute current statistics across all stored tips."""
        tips = self.list_tips()
        if not tips:
            return MemoryStats()

        type_counter: Counter[str] = Counter()
        domain_counter: Counter[str] = Counter()
        total_conf = 0.0

        for tip in tips:
            type_counter[tip.tip_type] += 1
            domain_counter[tip.task_domain] += 1
            total_conf += tip.confidence

        return MemoryStats(
            total_tips=len(tips),
            tips_by_type=dict(type_counter),
            tips_by_domain=dict(domain_counter),
            avg_confidence=round(total_conf / len(tips), 4) if tips else 0.0,
        )

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    def prune_low_confidence(self, threshold: float = 0.2) -> int:
        """Remove tips below the confidence threshold.  Returns count removed."""
        tips = self.list_tips()
        removed = 0
        for tip in tips:
            if tip.confidence < threshold:
                self.delete_tip(tip.id)
                removed += 1
        return removed

    def increment_access(self, tip_id: str) -> None:
        """Increment the access_count and update last_accessed for a tip."""
        try:
            tip = self.load_tip(tip_id)
        except FileNotFoundError:
            return
        tip.access_count += 1
        tip.last_accessed = _iso_now()
        self.save_tip(tip)
