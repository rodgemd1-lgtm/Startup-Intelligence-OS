"""Correction Handler — when Mike corrects Jake, it sticks forever.

Detects correction signals in Mike's messages, extracts the claim being corrected,
stores in jake_semantic with highest confidence (1.0) and memory_type="correction".

Corrections beat every other memory type in retrieval priority.
They never decay. They never get overwritten except by newer corrections.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger("jake-brain-ingest")

# ---------------------------------------------------------------------------
# Correction signal patterns — these phrases from Mike = a correction
# ---------------------------------------------------------------------------

CORRECTION_PATTERNS = [
    # Direct corrections
    r"\bno[,.]?\s+(it'?s|that'?s|its)\b",
    r"\bactually[,.]?\s+",
    r"\bthat'?s wrong\b",
    r"\byou'?re wrong\b",
    r"\bwrong[,.]?\s+",
    r"\bnot\s+(that|this|it)\b",
    r"\byou said\b.{0,60}\bbut\b",
    r"\bthe correct\b",
    r"\bcorrect(ion)?\s+",
    r"\byou got that wrong\b",
    r"\bmy\s+\w+\s+is\s+\w+[,.]?\s+not\s+\w+",
    r"\bit'?s\s+\w+[,.]?\s+not\s+\w+",
    r"\b(should be|is actually|was actually)\b",
    r"\bI said\b.{0,60}\bnot\b",
    r"\bremember[,:]?\s+it'?s\b",
    r"\bI told you\b",
    r"\bstop saying\b",
    r"\bstop calling\b",
    r"\bdon'?t call\b",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in CORRECTION_PATTERNS]


def is_correction(message: str) -> bool:
    """Return True if this message from Mike looks like a correction."""
    if not message or len(message.strip()) < 5:
        return False
    for pattern in COMPILED_PATTERNS:
        if pattern.search(message):
            return True
    return False


def extract_correction(
    user_message: str,
    prior_response: str = "",
    context: str = "",
) -> Optional[dict]:
    """Extract the correction from Mike's message.

    Returns a dict with:
        wrong_claim: what Jake said that was wrong (best guess)
        correct_claim: what Mike says is correct
        raw_message: Mike's full correction message
        context: surrounding context
    """
    msg = user_message.strip()

    # Try to find "not X, it's Y" patterns
    # "it's X, not Y" → wrong=Y, correct=X
    m = re.search(r"it'?s\s+(.{3,60?})[,.]?\s+not\s+(.{3,60})", msg, re.IGNORECASE)
    if m:
        return {
            "wrong_claim": m.group(2).strip().rstrip(".,!?"),
            "correct_claim": m.group(1).strip().rstrip(".,!?"),
            "raw_message": msg,
            "context": context or prior_response[:200],
        }

    # "not X, it's Y" → wrong=X, correct=Y
    m = re.search(r"\bnot\s+(.{3,60?})[,.]?\s+it'?s\s+(.{3,60})", msg, re.IGNORECASE)
    if m:
        return {
            "wrong_claim": m.group(1).strip().rstrip(".,!?"),
            "correct_claim": m.group(2).strip().rstrip(".,!?"),
            "raw_message": msg,
            "context": context or prior_response[:200],
        }

    # "my X is Y, not Z"
    m = re.search(r"my\s+(\w+)\s+is\s+(.{3,60?})[,.]?\s+not\s+(.{3,60})", msg, re.IGNORECASE)
    if m:
        return {
            "wrong_claim": f"Mike's {m.group(1)} is {m.group(3).strip().rstrip('.,!?')}",
            "correct_claim": f"Mike's {m.group(1)} is {m.group(2).strip().rstrip('.,!?')}",
            "raw_message": msg,
            "context": context or prior_response[:200],
        }

    # Generic fallback — the whole message IS the correction
    return {
        "wrong_claim": prior_response[:200] if prior_response else "(see context)",
        "correct_claim": msg,
        "raw_message": msg,
        "context": context or prior_response[:200],
    }


def store_correction(
    wrong_claim: str,
    correct_claim: str,
    raw_message: str,
    context: str = "",
    supabase_client=None,
    embedder=None,
) -> bool:
    """Store a correction as a permanent jake_semantic memory.

    Uses confidence=1.0 (highest possible). Never decays. Always wins in retrieval.

    Returns True if stored successfully.
    """
    try:
        # Build the corrected fact as a clean statement
        fact = f"CORRECTION: {correct_claim}"
        if wrong_claim and wrong_claim != "(see context)":
            fact = f"CORRECTION: {correct_claim} (NOT: {wrong_claim})"

        now = datetime.now(timezone.utc)

        # jake_semantic schema: id, content, embedding, category, confidence,
        # source_episodes, evidence_count, last_reinforced_at, is_active,
        # project, topics, metadata, created_at, updated_at
        record = {
            "content": fact,
            "category": "rule",
            "confidence": 1.0,
            "topics": ["correction", "override", "permanent"],
            "is_active": True,
            "evidence_count": 1,
            "metadata": {
                "wrong_claim": wrong_claim,
                "correct_claim": correct_claim,
                "raw_message": raw_message,
                "context_snippet": context[:300] if context else "",
                "corrected_at": now.isoformat(),
                "source": "mike_explicit",
            },
            "created_at": now.isoformat(),
        }

        if supabase_client and embedder:
            # Embed and store
            try:
                embedding = embedder.embed_query(fact)
                record["embedding"] = embedding
            except Exception as e:
                logger.warning("Correction embedding failed: %s — storing without embedding", e)

            supabase_client.table("jake_semantic").insert(record).execute()
            logger.info("Correction stored in Supabase: %s → %s", wrong_claim[:50], correct_claim[:50])
        else:
            # Fallback: write to local correction index
            _write_correction_index(record)
            logger.info("Correction stored in local index (no Supabase client): %s", correct_claim[:60])

        return True

    except Exception as e:
        logger.error("Failed to store correction: %s", e)
        return False


def _write_correction_index(record: dict) -> None:
    """Fallback: append correction to local JSON file for later sync."""
    index_path = Path.home() / ".hermes" / "logs" / "correction_index.jsonl"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "a") as f:
        f.write(json.dumps(record) + "\n")


def build_correction_confirmation(wrong_claim: str, correct_claim: str) -> str:
    """Build the message Jake sends to Mike confirming the correction."""
    if wrong_claim and wrong_claim != "(see context)":
        return (
            f"Got it — updated my memory.\n"
            f"❌ Old: {wrong_claim[:100]}\n"
            f"✅ New: {correct_claim[:100]}\n"
            f"Stored permanently. Won't happen again."
        )
    return (
        f"Got it — stored that correction permanently.\n"
        f"✅ {correct_claim[:150]}"
    )
