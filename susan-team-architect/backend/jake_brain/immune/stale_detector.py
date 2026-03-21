"""Stale Data Detector — flag memories not reinforced in 30+ days.

A memory is "stale" if:
  - It was created more than N days ago, AND
  - It has not been accessed recently (low composite score)

Stale memories are NOT deleted — they're flagged for review.
Mike decides: reinforce (add more context), archive, or delete.

Promotion logic:
  - Episodic memories referenced 3+ times → candidate for semantic promotion
  - Semantic facts not referenced in 90 days → candidate for archival
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger("jake.immune.stale_detector")

_DEFAULT_STALE_DAYS = 30
_DEEP_STALE_DAYS = 90  # semantic facts this old with no access → archive candidate


class StaleDetector:
    """Identifies stale memories across all brain layers."""

    def __init__(self):
        self._supabase = None

    def _get_supabase(self):
        if self._supabase is None:
            try:
                from supabase import create_client
                from susan_core.config import config as susan_config
                self._supabase = create_client(
                    susan_config.supabase_url, susan_config.supabase_key
                )
            except Exception as exc:
                logger.warning("Supabase not available: %s", exc)
        return self._supabase

    def find_stale_episodic(self, days: int = _DEFAULT_STALE_DAYS) -> list[dict]:
        """Find episodic memories older than N days."""
        supabase = self._get_supabase()
        if supabase is None:
            return []

        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        try:
            result = (
                supabase.table("jake_episodic")
                .select("id, content, created_at, source, importance")
                .lt("created_at", cutoff)
                .eq("promoted", False)
                .order("created_at", desc=False)
                .limit(50)
                .execute()
            )
            rows = result.data or []
            logger.info("Found %d stale episodic memories (>%d days old)", len(rows), days)
            return rows
        except Exception as exc:
            logger.warning("Failed to fetch stale episodic: %s", exc)
            return []

    def find_stale_semantic(self, days: int = _DEEP_STALE_DAYS) -> list[dict]:
        """Find semantic facts older than N days (candidates for archival)."""
        supabase = self._get_supabase()
        if supabase is None:
            return []

        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        try:
            result = (
                supabase.table("jake_semantic")
                .select("id, content, created_at, confidence, category")
                .lt("created_at", cutoff)
                .order("confidence", desc=False)  # lowest confidence first
                .limit(30)
                .execute()
            )
            rows = result.data or []
            logger.info("Found %d stale semantic facts (>%d days old)", len(rows), days)
            return rows
        except Exception as exc:
            logger.warning("Failed to fetch stale semantic: %s", exc)
            return []

    def find_promotion_candidates(self) -> list[dict]:
        """Find episodic memories that are good candidates for semantic promotion.

        Criteria: imported or created >7 days ago, high importance (>0.6),
        not yet promoted.
        """
        supabase = self._get_supabase()
        if supabase is None:
            return []

        cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        try:
            result = (
                supabase.table("jake_episodic")
                .select("id, content, created_at, importance, source")
                .lt("created_at", cutoff)
                .eq("promoted", False)
                .gte("importance", 0.6)
                .order("importance", desc=True)
                .limit(20)
                .execute()
            )
            rows = result.data or []
            logger.info("Found %d episodic promotion candidates", len(rows))
            return rows
        except Exception as exc:
            logger.warning("Failed to fetch promotion candidates: %s", exc)
            return []

    def find_all_stale(self, episodic_days: int = _DEFAULT_STALE_DAYS) -> dict[str, Any]:
        """Run all stale detection queries and return a summary."""
        stale_episodic = self.find_stale_episodic(episodic_days)
        stale_semantic = self.find_stale_semantic(_DEEP_STALE_DAYS)
        promotion_candidates = self.find_promotion_candidates()

        return {
            "stale_episodic": stale_episodic,
            "stale_episodic_count": len(stale_episodic),
            "stale_semantic": stale_semantic,
            "stale_semantic_count": len(stale_semantic),
            "promotion_candidates": promotion_candidates,
            "promotion_candidates_count": len(promotion_candidates),
            "episodic_cutoff_days": episodic_days,
            "semantic_cutoff_days": _DEEP_STALE_DAYS,
        }

    def format_stale_report(self, days: int = _DEFAULT_STALE_DAYS) -> str:
        """Generate a human-readable stale data report."""
        data = self.find_all_stale(days)

        lines = ["**🗄️ Stale Memory Report**", ""]

        # Stale episodic
        count = data["stale_episodic_count"]
        lines.append(f"📖 Stale episodic memories (>{days} days old): **{count}**")
        for mem in data["stale_episodic"][:5]:
            age = _age_str(mem.get("created_at"))
            preview = mem.get("content", "")[:80].replace("\n", " ")
            lines.append(f"  • [{age}] {preview}...")

        lines.append("")

        # Stale semantic
        count = data["stale_semantic_count"]
        lines.append(f"💡 Stale semantic facts (>{_DEEP_STALE_DAYS} days old): **{count}**")
        for mem in data["stale_semantic"][:5]:
            age = _age_str(mem.get("created_at"))
            preview = mem.get("content", "")[:80].replace("\n", " ")
            lines.append(f"  • [{age}] {preview}...")

        lines.append("")

        # Promotion candidates
        count = data["promotion_candidates_count"]
        lines.append(f"⬆️ Promotion candidates (episodic → semantic): **{count}**")
        for mem in data["promotion_candidates"][:5]:
            importance = mem.get("importance", 0)
            preview = mem.get("content", "")[:80].replace("\n", " ")
            lines.append(f"  • [importance={importance:.2f}] {preview}...")

        return "\n".join(lines)


def _age_str(created_at: str | None) -> str:
    """Format a created_at timestamp as 'X days ago'."""
    if not created_at:
        return "unknown age"
    try:
        # Handle both with and without timezone
        if created_at.endswith("Z"):
            created_at = created_at[:-1] + "+00:00"
        dt = datetime.fromisoformat(created_at)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - dt
        days = delta.days
        if days == 0:
            return "today"
        elif days == 1:
            return "1 day ago"
        else:
            return f"{days} days ago"
    except Exception:
        return "unknown age"
