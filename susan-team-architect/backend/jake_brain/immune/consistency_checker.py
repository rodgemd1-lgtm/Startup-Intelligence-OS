"""Consistency Checker — detect contradictory memories, flag for resolution.

How it works:
  1. When a new semantic fact is stored, search for similar existing facts.
  2. If two facts are semantically similar (>0.85 cosine) but contain
     opposing signal words or contradictory claims, flag the pair.
  3. Flags are logged to jake_episodic with source_type='contradiction'.
  4. Returns a list of flagged contradictions so Jake can surface them.

Examples of contradictions:
  - "Jacob plays OL" vs "Jacob plays QB"
  - "Mike's preferred tech is Drizzle" vs "Mike switched to Prisma"
  - "James's birthday is March 5" vs "James's birthday is April 5"
"""
from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("jake.immune.consistency_checker")

# Similarity threshold: two facts this similar are candidates for contradiction checking
SIMILARITY_THRESHOLD = 0.82

# Opposing word pairs that indicate a contradiction when present in similar facts
_OPPOSING_PAIRS = [
    (r"\byes\b", r"\bno\b"),
    (r"\btrue\b", r"\bfalse\b"),
    (r"\bactive\b", r"\binactive\b"),
    (r"\bmarried\b", r"\bdivorced\b"),
    (r"\benabled\b", r"\bdisabled\b"),
    (r"\bplays\s+(\w+)\b", r"\bplays\s+(\w+)\b"),  # "plays OL" vs "plays QB"
    (r"\bbirthday\s+is\b", r"\bbirthday\s+is\b"),   # same topic, different values
    (r"\bprefers?\s+(\w+)\b", r"\bprefers?\s+(\w+)\b"),
    (r"\bworks?\s+at\s+(\w+)\b", r"\bworks?\s+at\s+(\w+)\b"),
]


def _extract_key_claims(text: str) -> list[str]:
    """Extract simple subject-verb-object patterns for comparison."""
    text = text.lower().strip()
    # Simple approach: split on common delimiters and take clauses
    clauses = re.split(r"[.;,\n]", text)
    return [c.strip() for c in clauses if len(c.strip()) > 10]


def _might_contradict(text1: str, text2: str) -> bool:
    """Quick heuristic: do these two texts potentially contradict each other?

    Returns True if they share a subject but have conflicting claims.
    This is a lightweight pre-filter before semantic comparison.
    """
    claims1 = _extract_key_claims(text1)
    claims2 = _extract_key_claims(text2)

    for c1 in claims1:
        for c2 in claims2:
            # Skip if they're basically the same sentence
            if c1 == c2:
                continue
            # Check for opposing word patterns
            for pat1, pat2 in _OPPOSING_PAIRS:
                m1 = re.search(pat1, c1)
                m2 = re.search(pat2, c2)
                if m1 and m2:
                    # Same pattern found in both — check if values differ
                    if pat1 == pat2:
                        # Same pattern (like "plays X") — check if capture groups differ
                        if m1.groups() and m2.groups() and m1.group(1) != m2.group(1):
                            return True
                    else:
                        # Opposing patterns (like yes/no, true/false)
                        return True
    return False


class ConsistencyChecker:
    """Detects contradictions in Jake's semantic memory layer."""

    def __init__(self):
        self._supabase = None
        self._retriever = None

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

    def _get_retriever(self):
        if self._retriever is None:
            try:
                from jake_brain.retriever import BrainRetriever
                self._retriever = BrainRetriever()
            except Exception as exc:
                logger.warning("BrainRetriever not available: %s", exc)
        return self._retriever

    def check_new_fact(self, new_content: str, top_k: int = 5) -> list[dict]:
        """Check if a new semantic fact contradicts existing memories.

        Returns list of contradiction records (empty if none found).
        Each record: { existing_id, existing_content, new_content, reason }
        """
        retriever = self._get_retriever()
        if retriever is None:
            return []

        try:
            existing = retriever.search(
                query=new_content,
                top_k=top_k,
                layer_filter="semantic",
            )
        except Exception as exc:
            logger.warning("Consistency check search failed: %s", exc)
            return []

        contradictions = []
        for mem in existing:
            similarity = mem.get("composite_score", 0)
            if similarity < SIMILARITY_THRESHOLD:
                continue

            existing_content = mem.get("content", "")
            if _might_contradict(new_content, existing_content):
                contradiction = {
                    "existing_id": mem.get("id"),
                    "existing_content": existing_content,
                    "new_content": new_content,
                    "similarity": similarity,
                    "reason": f"Semantically similar (score={similarity:.3f}) but potentially contradictory claims",
                }
                contradictions.append(contradiction)
                self._flag_contradiction(contradiction)

        return contradictions

    def _flag_contradiction(self, record: dict):
        """Log a contradiction to jake_episodic for Mike's review."""
        supabase = self._get_supabase()
        if supabase is None:
            return

        content = (
            f"[CONTRADICTION DETECTED]\n"
            f"Existing: {record['existing_content'][:200]}\n"
            f"New claim: {record['new_content'][:200]}\n"
            f"Reason: {record['reason']}"
        )
        try:
            supabase.table("jake_episodic").insert({
                "content": content,
                "source": "immune-consistency-checker",
                "source_type": "contradiction",
                "importance": 0.8,
                "metadata": {
                    "existing_id": str(record.get("existing_id", "")),
                    "similarity": record.get("similarity", 0),
                    "flagged_at": datetime.now(timezone.utc).isoformat(),
                },
            }).execute()
            logger.info("Contradiction flagged: similarity=%.3f", record.get("similarity", 0))
        except Exception as exc:
            logger.warning("Failed to flag contradiction: %s", exc)

    def scan_all(self, limit: int = 100) -> list[dict]:
        """Scan recent semantic memories for internal contradictions.

        This is a heavier operation — run weekly, not on every write.
        Returns list of contradiction pairs found.
        """
        supabase = self._get_supabase()
        if supabase is None:
            return []

        try:
            result = (
                supabase.table("jake_semantic")
                .select("id, content, created_at")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            facts = result.data or []
        except Exception as exc:
            logger.warning("Failed to fetch semantic facts: %s", exc)
            return []

        contradictions = []
        checked = set()

        for i, fact_a in enumerate(facts):
            for fact_b in facts[i + 1:]:
                pair_key = tuple(sorted([str(fact_a.get("id")), str(fact_b.get("id"))]))
                if pair_key in checked:
                    continue
                checked.add(pair_key)

                if _might_contradict(fact_a.get("content", ""), fact_b.get("content", "")):
                    contradictions.append({
                        "id_a": fact_a.get("id"),
                        "content_a": fact_a.get("content", "")[:200],
                        "id_b": fact_b.get("id"),
                        "content_b": fact_b.get("content", "")[:200],
                        "reason": "Potential contradictory claims detected",
                    })

        logger.info(
            "Consistency scan complete: %d facts checked, %d contradictions found",
            len(facts), len(contradictions),
        )
        return contradictions
