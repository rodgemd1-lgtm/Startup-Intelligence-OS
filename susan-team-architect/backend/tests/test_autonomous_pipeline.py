"""Tests for the autonomous pipeline engine."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Fixtures / Helpers
# ---------------------------------------------------------------------------

def make_pipeline(task="Test task", task_type="research", name="test-pipe"):
    """Create a pipeline instance with Supabase + brain mocked out."""
    from jake_brain.autonomous_pipeline import AutonomousPipeline, PipelineStatus

    with patch("jake_brain.autonomous_pipeline.create_client") as mock_sb, \
         patch("jake_brain.autonomous_pipeline.BrainStore") as mock_store_cls, \
         patch("jake_brain.autonomous_pipeline.BrainRetriever") as mock_retriever_cls:

        mock_client = MagicMock()
        mock_sb.return_value = mock_client
        # Make table().insert/update/select all chainable
        mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{"id": "run-1"}])
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"phases_completed": {}}])

        mock_store = MagicMock()
        mock_store_cls.return_value = mock_store

        mock_retriever = MagicMock()
        mock_retriever.recall.return_value = "Relevant context about the task."
        mock_retriever_cls.return_value = mock_retriever

        pipe = AutonomousPipeline(name, task, task_type)
        pipe._supabase_client = mock_client  # keep ref for assertions
        return pipe, mock_client, mock_store, mock_retriever


# ---------------------------------------------------------------------------
# Test: Happy path — all 8 phases complete
# ---------------------------------------------------------------------------

class TestHappyPath:
    def test_run_returns_success(self):
        """All phases complete without error → success=True."""
        from jake_brain.autonomous_pipeline import AutonomousPipeline, PipelineStatus

        with patch("jake_brain.autonomous_pipeline.create_client") as mock_sb, \
             patch("jake_brain.autonomous_pipeline.BrainStore") as mock_store_cls, \
             patch("jake_brain.autonomous_pipeline.BrainRetriever") as mock_retriever_cls:

            mock_client = MagicMock()
            mock_sb.return_value = mock_client
            mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])
            mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()
            mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"phases_completed": {}}])
            mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(data=[])

            mock_store = MagicMock()
            mock_store.store_episodic.return_value = {"id": "ep-1"}
            mock_store.store_procedural.return_value = {"id": "proc-1"}
            mock_store_cls.return_value = mock_store

            mock_retriever = MagicMock()
            mock_retriever.recall.return_value = "Some memory context"
            mock_retriever_cls.return_value = mock_retriever

            pipe = AutonomousPipeline("happy-test", "Test task", "research")
            result = pipe.run()

        assert result["success"] is True
        assert result["status"] == PipelineStatus.COMPLETED

    def test_phases_tracked_in_result(self):
        """Phase tracker updates as phases complete."""
        from jake_brain.autonomous_pipeline import AutonomousPipeline

        with patch("jake_brain.autonomous_pipeline.create_client") as mock_sb, \
             patch("jake_brain.autonomous_pipeline.BrainStore"), \
             patch("jake_brain.autonomous_pipeline.BrainRetriever") as mock_retriever_cls:

            mock_client = MagicMock()
            mock_sb.return_value = mock_client
            mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])
            mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()
            mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"phases_completed": {}}])
            mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(data=[])

            mock_retriever = MagicMock()
            mock_retriever.recall.return_value = ""
            mock_retriever_cls.return_value = mock_retriever

            pipe = AutonomousPipeline("phase-track-test", "Track phases", "maintenance")
            result = pipe.run()

        # The run_id and pipeline_name are set
        assert result["run_id"] is not None
        assert result["pipeline_name"] == "phase-track-test"


# ---------------------------------------------------------------------------
# Test: Self-healing on simulated failure
# ---------------------------------------------------------------------------

class TestSelfHealing:
    def test_heal_retries_on_api_error(self):
        """API errors trigger retry with backoff, then eventually pass."""
        from jake_brain.autonomous_pipeline import AutonomousPipeline, ErrorClass

        with patch("jake_brain.autonomous_pipeline.create_client") as mock_sb, \
             patch("jake_brain.autonomous_pipeline.BrainStore"), \
             patch("jake_brain.autonomous_pipeline.BrainRetriever") as mock_retriever_cls, \
             patch("jake_brain.autonomous_pipeline.time") as mock_time:

            mock_client = MagicMock()
            mock_sb.return_value = mock_client
            mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])
            mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()
            mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"phases_completed": {}}])
            mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(data=[])

            mock_retriever = MagicMock()
            mock_retriever.recall.return_value = ""
            mock_retriever_cls.return_value = mock_retriever

            pipe = AutonomousPipeline("heal-test", "Failing task", "research")

            # Override _phase_build to fail on attempt 0, pass on attempt 1
            attempt_counter = {"n": 0}

            def custom_build(plan, context, attempt=0):
                if attempt_counter["n"] == 0:
                    attempt_counter["n"] += 1
                    return {
                        "results": [],
                        "errors": ["Connection timeout"],
                        "steps_completed": 0,
                        "steps_total": 2,
                        "attempt": attempt,
                    }
                return {
                    "results": [
                        {"step": "query_rag", "status": "ok"},
                        {"step": "synthesize", "status": "ok"},
                    ],
                    "errors": [],
                    "steps_completed": 2,
                    "steps_total": 2,
                    "attempt": attempt,
                }

            pipe._phase_build = custom_build
            result = pipe.run()

        # Should eventually succeed after heal
        assert result["success"] is True

    def test_logic_error_blocks_immediately(self):
        """Logic errors escalate to BLOCKED without retrying."""
        from jake_brain.autonomous_pipeline import AutonomousPipeline, PipelineStatus

        with patch("jake_brain.autonomous_pipeline.create_client") as mock_sb, \
             patch("jake_brain.autonomous_pipeline.BrainStore"), \
             patch("jake_brain.autonomous_pipeline.BrainRetriever") as mock_retriever_cls:

            mock_client = MagicMock()
            mock_sb.return_value = mock_client
            mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])
            mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()
            mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"phases_completed": {}}])
            mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(data=[])

            mock_retriever = MagicMock()
            mock_retriever.recall.return_value = ""
            mock_retriever_cls.return_value = mock_retriever

            pipe = AutonomousPipeline("logic-error-test", "Logic failing task", "content")

            # Override _phase_build to always produce a logic error
            def logic_fail_build(plan, context, attempt=0):
                return {
                    "results": [],
                    "errors": ["Schema validation failed: unexpected field"],
                    "steps_completed": 0,
                    "steps_total": 3,
                    "attempt": attempt,
                }

            pipe._phase_build = logic_fail_build
            result = pipe.run()

        assert result["status"] == PipelineStatus.BLOCKED
        assert result["success"] is False

    def test_max_retry_limit_reached(self):
        """After MAX_HEAL_RETRIES exhausted, pipeline is BLOCKED."""
        from jake_brain.autonomous_pipeline import AutonomousPipeline, PipelineStatus

        with patch("jake_brain.autonomous_pipeline.create_client") as mock_sb, \
             patch("jake_brain.autonomous_pipeline.BrainStore"), \
             patch("jake_brain.autonomous_pipeline.BrainRetriever") as mock_retriever_cls, \
             patch("jake_brain.autonomous_pipeline.time") as mock_time:

            mock_client = MagicMock()
            mock_sb.return_value = mock_client
            mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])
            mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()
            mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"phases_completed": {}}])
            mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(data=[])

            mock_retriever = MagicMock()
            mock_retriever.recall.return_value = ""
            mock_retriever_cls.return_value = mock_retriever

            pipe = AutonomousPipeline("max-retry-test", "Always fails", "research")

            # Always fail with API error (retriable)
            def always_fail_build(plan, context, attempt=0):
                return {
                    "results": [],
                    "errors": ["Connection timeout — 503"],
                    "steps_completed": 0,
                    "steps_total": 2,
                    "attempt": attempt,
                }

            pipe._phase_build = always_fail_build
            result = pipe.run()

        assert result["status"] == PipelineStatus.BLOCKED
        assert result["success"] is False


# ---------------------------------------------------------------------------
# Test: Error classification
# ---------------------------------------------------------------------------

class TestErrorClassification:
    def test_api_error_classification(self):
        from jake_brain.autonomous_pipeline import AutonomousPipeline, ErrorClass
        with patch("jake_brain.autonomous_pipeline.create_client"), \
             patch("jake_brain.autonomous_pipeline.BrainStore"), \
             patch("jake_brain.autonomous_pipeline.BrainRetriever"):
            pipe = AutonomousPipeline("classify-test", "test", "research")
        assert pipe._classify_error("Connection timeout") == ErrorClass.API_ERROR
        assert pipe._classify_error("Rate limit 429") == ErrorClass.API_ERROR
        assert pipe._classify_error("503 service unavailable") == ErrorClass.API_ERROR

    def test_data_error_classification(self):
        from jake_brain.autonomous_pipeline import AutonomousPipeline, ErrorClass
        with patch("jake_brain.autonomous_pipeline.create_client"), \
             patch("jake_brain.autonomous_pipeline.BrainStore"), \
             patch("jake_brain.autonomous_pipeline.BrainRetriever"):
            pipe = AutonomousPipeline("classify-test", "test", "research")
        assert pipe._classify_error("Record not found") == ErrorClass.DATA_ERROR
        assert pipe._classify_error("Empty result set") == ErrorClass.DATA_ERROR

    def test_logic_error_classification(self):
        from jake_brain.autonomous_pipeline import AutonomousPipeline, ErrorClass
        with patch("jake_brain.autonomous_pipeline.create_client"), \
             patch("jake_brain.autonomous_pipeline.BrainStore"), \
             patch("jake_brain.autonomous_pipeline.BrainRetriever"):
            pipe = AutonomousPipeline("classify-test", "test", "research")
        assert pipe._classify_error("Schema validation failed") == ErrorClass.LOGIC_ERROR
        assert pipe._classify_error("AttributeError: 'NoneType'") == ErrorClass.LOGIC_ERROR
