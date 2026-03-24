"""Tests for Phase 2 cognitive memory polish: auto-promotion, contradiction, decay, access tracking."""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

# Ensure backend is importable
BACKEND = Path(__file__).resolve().parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


# ---------------------------------------------------------------------------
# 2a: Auto-promotion logic
# ---------------------------------------------------------------------------

class TestAutoPromotion:
    """Test that 3+ similar episodes within 14 days trigger semantic promotion."""

    def _make_episode(self, content: str, days_ago: int, eid: str) -> dict:
        occurred = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
        return {
            "id": eid,
            "content": content,
            "occurred_at": occurred,
            "project": None,
            "people": [],
            "topics": [],
            "metadata": {},
        }

    @patch("jake_brain.consolidator.BrainStore")
    def test_promotes_when_three_similar_episodes(self, MockStore):
        """3+ similar episodes within 14 days should auto-promote to semantic."""
        from jake_brain.consolidator import Consolidator

        store = MockStore.return_value
        store.find_similar_semantic.return_value = []  # no existing semantic match
        store.store_semantic.return_value = {"id": "sem-001"}
        store.supabase = MagicMock()
        store.supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = None

        consolidator = Consolidator(store=store)

        anchor = self._make_episode("Jacob plays football and trains hard", 1, "ep-01")
        similar_1 = self._make_episode("Jacob football training session", 3, "ep-02")
        similar_2 = self._make_episode("Jacob football practice and hard work", 7, "ep-03")
        unrelated = self._make_episode("Mike deployed the new Oracle feature", 2, "ep-04")

        candidates = [anchor, similar_1, similar_2, unrelated]
        promoted = consolidator._auto_promote_if_threshold_met(anchor, candidates)

        assert promoted is True
        store.store_semantic.assert_called_once()
        # Verify semantic content and metadata
        call_kwargs = store.store_semantic.call_args[1]
        assert call_kwargs["metadata"]["auto_promoted"] is True
        assert call_kwargs["metadata"]["cluster_size"] >= 3

    @patch("jake_brain.consolidator.BrainStore")
    def test_does_not_promote_below_threshold(self, MockStore):
        """Fewer than 3 similar episodes should NOT trigger promotion."""
        from jake_brain.consolidator import Consolidator

        store = MockStore.return_value
        store.find_similar_semantic.return_value = []
        store.store_semantic.return_value = {"id": "sem-002"}
        store.supabase = MagicMock()

        consolidator = Consolidator(store=store)

        anchor = self._make_episode("Jacob plays football", 1, "ep-01")
        similar_1 = self._make_episode("Jacob football training", 5, "ep-02")
        # Only 2 — below threshold of 3

        candidates = [anchor, similar_1]
        promoted = consolidator._auto_promote_if_threshold_met(anchor, candidates)

        assert promoted is False
        store.store_semantic.assert_not_called()

    @patch("jake_brain.consolidator.BrainStore")
    def test_excludes_episodes_outside_14_day_window(self, MockStore):
        """Episodes older than 14 days should not count toward promotion threshold."""
        from jake_brain.consolidator import Consolidator

        store = MockStore.return_value
        store.find_similar_semantic.return_value = []
        store.store_semantic.return_value = {"id": "sem-003"}
        store.supabase = MagicMock()

        consolidator = Consolidator(store=store)

        anchor = self._make_episode("Jacob plays football", 1, "ep-01")
        recent = self._make_episode("Jacob football training", 5, "ep-02")
        old_1 = self._make_episode("Jacob football hard work", 20, "ep-03")  # outside window
        old_2 = self._make_episode("Jacob football season", 30, "ep-04")  # outside window

        candidates = [anchor, recent, old_1, old_2]
        promoted = consolidator._auto_promote_if_threshold_met(anchor, candidates)

        # Only anchor + recent = 2, below threshold
        assert promoted is False

    def test_infer_category_relationship(self):
        """Category inference should detect relationship content."""
        from jake_brain.consolidator import Consolidator
        c = Consolidator.__new__(Consolidator)
        assert c._infer_category("Jacob plays football with James") == "relationship"

    def test_infer_category_work(self):
        from jake_brain.consolidator import Consolidator
        c = Consolidator.__new__(Consolidator)
        assert c._infer_category("Oracle health project with Cohlmia") == "work"

    def test_infer_category_preference(self):
        from jake_brain.consolidator import Consolidator
        c = Consolidator.__new__(Consolidator)
        assert c._infer_category("Mike always prefers Python over JS") == "preference"

    def test_infer_category_fallback(self):
        from jake_brain.consolidator import Consolidator
        c = Consolidator.__new__(Consolidator)
        assert c._infer_category("some random unclassifiable content") == "fact"


# ---------------------------------------------------------------------------
# 2b: Contradiction detection
# ---------------------------------------------------------------------------

class TestContradictionDetection:
    """Test that store_semantic flags contradictions instead of silently overwriting."""

    @patch("jake_brain.store.Embedder")
    @patch("jake_brain.store.create_client")
    def test_contradiction_flagged_in_metadata(self, mock_create_client, mock_embedder_class):
        """When contradicting fact exists, new fact gets contradicted_by in metadata."""
        from jake_brain.store import BrainStore

        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        mock_embedder = MagicMock()
        mock_embedder.embed_query.return_value = [0.1] * 1024
        mock_embedder_class.return_value = mock_embedder

        store = BrainStore.__new__(BrainStore)
        store.supabase = mock_client
        store.embedder = mock_embedder

        # Mock find_similar_semantic to return a contradicting fact
        contradicting_fact = {
            "id": "fact-existing",
            "content": "Mike always uses Twilio for SMS",
            "category": "preference",
            "confidence": 0.9,
        }
        store.find_similar_semantic = MagicMock(return_value=[contradicting_fact])

        # Mock the insert
        mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "fact-new", "content": "Mike never uses Twilio", "metadata": {}}]
        )
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[])

        result = store.store_semantic(
            content="Mike never uses Twilio",
            category="preference",
        )

        # Verify contradiction was detected and flagged
        insert_call = mock_client.table.return_value.insert.call_args
        inserted_row = insert_call[0][0]
        assert "contradicted_by" in inserted_row["metadata"]
        assert "fact-existing" in inserted_row["metadata"]["contradicted_by"]

    @patch("jake_brain.store.Embedder")
    @patch("jake_brain.store.create_client")
    def test_no_contradiction_when_no_similar_facts(self, mock_create_client, mock_embedder_class):
        """No contradiction flags when no similar facts exist."""
        from jake_brain.store import BrainStore

        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        mock_embedder = MagicMock()
        mock_embedder.embed_query.return_value = [0.1] * 1024
        mock_embedder_class.return_value = mock_embedder

        store = BrainStore.__new__(BrainStore)
        store.supabase = mock_client
        store.embedder = mock_embedder
        store.find_similar_semantic = MagicMock(return_value=[])

        mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "fact-new", "metadata": {}}]
        )

        store.store_semantic(content="Mike prefers Python", category="preference")

        insert_call = mock_client.table.return_value.insert.call_args
        inserted_row = insert_call[0][0]
        assert "contradicted_by" not in inserted_row["metadata"]

    def test_check_contradiction_negation_detection(self):
        """check_contradiction detects negation asymmetry."""
        from jake_brain.store import BrainStore

        store = BrainStore.__new__(BrainStore)
        store.embedder = MagicMock()
        store.embedder.embed_query.return_value = [0.1] * 1024

        # Existing fact without negation
        existing_fact = {
            "id": "old-fact",
            "content": "Mike uses Vonage for SMS",
            "category": "preference",
            "confidence": 0.85,
            "similarity": 0.9,
        }
        store.find_similar_semantic = MagicMock(return_value=[existing_fact])

        # New fact with negation — should trigger contradiction
        contradictions = store.check_contradiction(
            "Mike doesn't use Vonage anymore",
            category="preference",
        )

        assert len(contradictions) == 1
        assert contradictions[0]["contradiction_type"] == "negation_asymmetry"


# ---------------------------------------------------------------------------
# 2c: Memory decay scoring
# ---------------------------------------------------------------------------

class TestMemoryDecay:
    """Test that memory decay formula reduces scores for old memories."""

    def _make_memory(self, mem_id: str, layer: str, score: float, days_since_access: int) -> dict:
        last_access = (datetime.now(timezone.utc) - timedelta(days=days_since_access)).isoformat()
        return {
            "id": mem_id,
            "layer": layer,
            "composite_score": score,
            "last_accessed_at": last_access,
        }

    @patch("jake_brain.retriever.BrainStore")
    @patch("jake_brain.retriever.Embedder")
    @patch("jake_brain.retriever.create_client")
    def test_fresh_memory_keeps_full_score(self, mock_client, mock_embedder, mock_store):
        """Memory accessed today should get close to full weight."""
        from jake_brain.retriever import BrainRetriever

        retriever = BrainRetriever.__new__(BrainRetriever)
        retriever.store = mock_store.return_value
        retriever.supabase = mock_client.return_value
        retriever.embedder = mock_embedder.return_value

        mem = self._make_memory("m1", "episodic", 0.8, days_since_access=0)
        result = retriever._apply_decay([mem])

        # 0 days: recency_factor = 1.0, multiplier = 1.0, score stays 0.8
        assert result[0]["composite_score"] == pytest.approx(0.8, abs=0.01)
        assert result[0]["decay_applied"] == pytest.approx(1.0, abs=0.01)

    @patch("jake_brain.retriever.BrainStore")
    @patch("jake_brain.retriever.Embedder")
    @patch("jake_brain.retriever.create_client")
    def test_old_memory_gets_70_percent_weight(self, mock_client, mock_embedder, mock_store):
        """Memory not accessed in 90+ days should get 0.7x weight."""
        from jake_brain.retriever import BrainRetriever

        retriever = BrainRetriever.__new__(BrainRetriever)
        retriever.store = mock_store.return_value
        retriever.supabase = mock_client.return_value
        retriever.embedder = mock_embedder.return_value

        mem = self._make_memory("m1", "episodic", 1.0, days_since_access=90)
        result = retriever._apply_decay([mem])

        # 90 days: recency_factor = 0.0, multiplier = 0.7
        assert result[0]["composite_score"] == pytest.approx(0.7, abs=0.02)

    @patch("jake_brain.retriever.BrainStore")
    @patch("jake_brain.retriever.Embedder")
    @patch("jake_brain.retriever.create_client")
    def test_45_day_memory_gets_partial_decay(self, mock_client, mock_embedder, mock_store):
        """Memory at 45 days should get halfway decay."""
        from jake_brain.retriever import BrainRetriever

        retriever = BrainRetriever.__new__(BrainRetriever)
        retriever.store = mock_store.return_value
        retriever.supabase = mock_client.return_value
        retriever.embedder = mock_embedder.return_value

        mem = self._make_memory("m1", "semantic", 1.0, days_since_access=45)
        result = retriever._apply_decay([mem])

        # 45 days: recency_factor = 0.5, multiplier = 0.7 + 0.3 * 0.5 = 0.85
        assert result[0]["composite_score"] == pytest.approx(0.85, abs=0.02)

    @patch("jake_brain.retriever.BrainStore")
    @patch("jake_brain.retriever.Embedder")
    @patch("jake_brain.retriever.create_client")
    def test_decay_re_sorts_memories(self, mock_client, mock_embedder, mock_store):
        """Decay should re-sort memories by adjusted score."""
        from jake_brain.retriever import BrainRetriever

        retriever = BrainRetriever.__new__(BrainRetriever)
        retriever.store = mock_store.return_value
        retriever.supabase = mock_client.return_value
        retriever.embedder = mock_embedder.return_value

        # Fresh memory with lower base score vs old memory with higher base score
        fresh = self._make_memory("fresh", "episodic", 0.7, days_since_access=1)
        old = self._make_memory("old", "episodic", 1.0, days_since_access=90)

        result = retriever._apply_decay([old, fresh])

        # After decay: fresh = 0.7 * ~1.0 = ~0.70, old = 1.0 * 0.7 = 0.70
        # Fresh should rank at least equal to old
        scores = [r["composite_score"] for r in result]
        assert scores == sorted(scores, reverse=True), "Results should be sorted by decayed score"


# ---------------------------------------------------------------------------
# 2d: Access tracking
# ---------------------------------------------------------------------------

class TestAccessTracking:
    """Test that access_count and last_accessed_at are updated on retrieval."""

    @patch("jake_brain.store.Embedder")
    @patch("jake_brain.store.create_client")
    def test_bump_episodic_access_increments_count(self, mock_create_client, mock_embedder_class):
        """bump_episodic_access should increment access_count and set last_accessed_at."""
        from jake_brain.store import BrainStore

        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        mock_embedder = MagicMock()
        mock_embedder_class.return_value = mock_embedder

        store = BrainStore.__new__(BrainStore)
        store.supabase = mock_client
        store.embedder = mock_embedder

        # Mock the select to return current count
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"access_count": 5}]
        )

        store.bump_episodic_access("ep-123")

        # Verify update was called with incremented count
        update_call = mock_client.table.return_value.update.call_args
        update_data = update_call[0][0]
        assert update_data["access_count"] == 6
        assert "last_accessed_at" in update_data

    @patch("jake_brain.store.Embedder")
    @patch("jake_brain.store.create_client")
    def test_bump_semantic_access_updates_timestamp(self, mock_create_client, mock_embedder_class):
        """bump_semantic_access should update last_accessed_at on semantic facts."""
        from jake_brain.store import BrainStore

        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        mock_embedder = MagicMock()
        mock_embedder_class.return_value = mock_embedder

        store = BrainStore.__new__(BrainStore)
        store.supabase = mock_client
        store.embedder = mock_embedder

        store.bump_semantic_access("sem-456")

        update_call = mock_client.table.return_value.update.call_args
        update_data = update_call[0][0]
        assert "last_accessed_at" in update_data
