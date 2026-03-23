"""A/B Testing Engine for Jake prompt variants.

Tracks prompt experiments, scores outcomes, and promotes winners.
Results stored in Supabase jake_semantic with category='ab_test'.

Usage:
    runner = ABTestRunner()
    test_id = runner.create_test("oracle_sentinel", "system_prompt",
                                 variant_a="You are an intelligence analyst...",
                                 variant_b="You are a strategic advisor...")
    runner.record_outcome(test_id, "a", score=0.82, notes="More specific intel")
    runner.record_outcome(test_id, "b", score=0.71, notes="Too broad")
    winner = runner.resolve_test(test_id)  # returns "a"
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_RESULTS_FILE = Path.home() / ".hermes" / "logs" / "ab_tests.jsonl"


class ABTestRunner:
    """Run and resolve A/B prompt experiments."""

    def __init__(self) -> None:
        _RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def create_test(
        self,
        agent_name: str,
        prompt_section: str,
        variant_a: str,
        variant_b: str,
        metric: str = "quality_score",
    ) -> str:
        """Register a new A/B test. Returns test_id."""
        test_id = str(uuid.uuid4())[:8]
        record = {
            "id": test_id,
            "agent_name": agent_name,
            "prompt_section": prompt_section,
            "variant_a": variant_a,
            "variant_b": variant_b,
            "metric": metric,
            "outcomes": [],
            "winner": None,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "resolved_at": None,
        }
        self._append(record)
        logger.info("AB test created: %s for %s/%s", test_id, agent_name, prompt_section)
        return test_id

    def record_outcome(
        self,
        test_id: str,
        variant: str,  # "a" or "b"
        score: float,
        notes: str = "",
    ) -> None:
        """Record a scored outcome for variant 'a' or 'b'."""
        record = self._find(test_id)
        if not record:
            logger.warning("AB test %s not found", test_id)
            return
        record["outcomes"].append({
            "variant": variant,
            "score": score,
            "notes": notes,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        })
        self._save(record)

    def resolve_test(self, test_id: str) -> Optional[str]:
        """Compare average scores and declare winner. Returns 'a', 'b', or None (tie)."""
        record = self._find(test_id)
        if not record:
            return None

        outcomes = record.get("outcomes", [])
        a_scores = [o["score"] for o in outcomes if o["variant"] == "a"]
        b_scores = [o["score"] for o in outcomes if o["variant"] == "b"]

        if not a_scores or not b_scores:
            logger.warning("AB test %s needs outcomes for both variants", test_id)
            return None

        avg_a = sum(a_scores) / len(a_scores)
        avg_b = sum(b_scores) / len(b_scores)

        if abs(avg_a - avg_b) < 0.05:
            winner = None  # statistical tie
        else:
            winner = "a" if avg_a > avg_b else "b"

        record["winner"] = winner
        record["a_score"] = round(avg_a, 4)
        record["b_score"] = round(avg_b, 4)
        record["status"] = "resolved"
        record["resolved_at"] = datetime.now(timezone.utc).isoformat()
        self._save(record)

        logger.info(
            "AB test %s resolved: winner=%s (a=%.3f, b=%.3f)",
            test_id, winner, avg_a, avg_b,
        )
        return winner

    def get_active_tests(self) -> list[dict]:
        """Return all active (unresolved) tests."""
        return [r for r in self._load_all() if r.get("status") == "active"]

    def get_winner_prompt(self, test_id: str) -> Optional[str]:
        """Return the winning prompt text, or None if unresolved."""
        record = self._find(test_id)
        if not record or not record.get("winner"):
            return None
        return record[f"variant_{record['winner']}"]

    def summary(self) -> dict:
        """Return summary stats across all tests."""
        all_tests = self._load_all()
        resolved = [t for t in all_tests if t.get("status") == "resolved"]
        return {
            "total": len(all_tests),
            "active": len([t for t in all_tests if t.get("status") == "active"]),
            "resolved": len(resolved),
            "winners": {
                "a": len([t for t in resolved if t.get("winner") == "a"]),
                "b": len([t for t in resolved if t.get("winner") == "b"]),
                "tie": len([t for t in resolved if t.get("winner") is None]),
            },
        }

    # ------------------------------------------------------------------
    # Persistence (JSONL — one record per test, rewritten on update)
    # ------------------------------------------------------------------

    def _load_all(self) -> list[dict]:
        if not _RESULTS_FILE.exists():
            return []
        records: dict[str, dict] = {}
        for line in _RESULTS_FILE.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                records[r["id"]] = r  # last write wins
            except (json.JSONDecodeError, KeyError):
                pass
        return list(records.values())

    def _find(self, test_id: str) -> Optional[dict]:
        for r in self._load_all():
            if r["id"] == test_id:
                return r
        return None

    def _append(self, record: dict) -> None:
        with open(_RESULTS_FILE, "a") as f:
            f.write(json.dumps(record) + "\n")

    def _save(self, record: dict) -> None:
        """Overwrite by appending (last-write-wins in _load_all)."""
        self._append(record)
