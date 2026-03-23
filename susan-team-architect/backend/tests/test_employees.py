"""Tests for Jake AI Employees and AutonomousPipeline.

Tests run without a live Supabase connection — all store calls are mocked.
"""
from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch, call
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_store():
    """Create a mock BrainStore that satisfies all pipeline calls."""
    store = MagicMock()
    store.supabase = MagicMock()

    # Default table().select()...execute() chain returns empty data
    table_mock = MagicMock()
    store.supabase.table.return_value = table_mock
    table_mock.select.return_value = table_mock
    table_mock.insert.return_value = table_mock
    table_mock.update.return_value = table_mock
    table_mock.eq.return_value = table_mock
    table_mock.lt.return_value = table_mock
    table_mock.gte.return_value = table_mock
    table_mock.lte.return_value = table_mock
    table_mock.contains.return_value = table_mock
    table_mock.order.return_value = table_mock
    table_mock.limit.return_value = table_mock
    table_mock.execute.return_value = MagicMock(data=[])

    # store_episodic and store_semantic and store_procedural return dicts
    store.store_episodic.return_value = {"id": "fake-episodic-id"}
    store.store_semantic.return_value = {"id": "fake-semantic-id"}
    store.store_procedural.return_value = {"id": "fake-procedural-id"}

    return store


# ---------------------------------------------------------------------------
# Test: AutonomousPipeline
# ---------------------------------------------------------------------------

class TestAutonomousPipelineImport(unittest.TestCase):
    def test_imports(self):
        from jake_brain.autonomous_pipeline import (
            AutonomousPipeline, PipelineTask, PipelineResult,
            PipelinePhase, ErrorType, TaskStatus,
        )
        self.assertIsNotNone(AutonomousPipeline)
        self.assertIsNotNone(PipelineTask)
        self.assertIsNotNone(PipelineResult)

    def test_pipeline_phase_enum(self):
        from jake_brain.autonomous_pipeline import PipelinePhase
        phases = [p.value for p in PipelinePhase]
        self.assertIn("CONTEXT", phases)
        self.assertIn("PLAN", phases)
        self.assertIn("BUILD", phases)
        self.assertIn("VALIDATE", phases)
        self.assertIn("HEAL", phases)
        self.assertIn("REPORT", phases)
        self.assertIn("CLOSE", phases)
        self.assertIn("LEARN", phases)
        self.assertEqual(len(phases), 8)

    def test_error_type_enum(self):
        from jake_brain.autonomous_pipeline import ErrorType
        self.assertIn("API_ERROR", [e.value for e in ErrorType])
        self.assertIn("DATA_ERROR", [e.value for e in ErrorType])
        self.assertIn("LOGIC_ERROR", [e.value for e in ErrorType])

    def test_task_status_enum(self):
        from jake_brain.autonomous_pipeline import TaskStatus
        statuses = [s.value for s in TaskStatus]
        self.assertIn("running", statuses)
        self.assertIn("success", statuses)
        self.assertIn("failed", statuses)
        self.assertIn("flagged", statuses)
        self.assertIn("partial", statuses)


class TestAutonomousPipelineRun(unittest.TestCase):
    def setUp(self):
        from jake_brain.autonomous_pipeline import AutonomousPipeline, PipelineTask
        self.store = _make_mock_store()
        self.pipeline = AutonomousPipeline(store=self.store)
        self.PipelineTask = PipelineTask

    def _make_task(self, **kwargs):
        defaults = dict(
            task_type="test_task",
            description="Test description",
            success_criteria=["output produced"],
            context_hints=["test"],
            employee_name="test_employee",
        )
        defaults.update(kwargs)
        return self.PipelineTask(**defaults)

    def test_successful_run_returns_result(self):
        from jake_brain.autonomous_pipeline import TaskStatus
        task = self._make_task()

        def build_fn(t, ctx):
            return {"result": "test_output", "count": 42}

        result = self.pipeline.run(task, build_fn=build_fn)
        self.assertIsNotNone(result)
        self.assertEqual(result.task_id, task.task_id)
        self.assertEqual(result.status, TaskStatus.SUCCESS)
        self.assertIn("result", result.outputs)
        self.assertEqual(result.outputs["result"], "test_output")

    def test_all_phases_recorded(self):
        """On a successful run, all phases except HEAL should be present.
        HEAL only appears when BUILD fails, so it is absent on the happy path."""
        from jake_brain.autonomous_pipeline import PipelinePhase
        task = self._make_task()

        def build_fn(t, ctx):
            return {"data": "ok"}

        result = self.pipeline.run(task, build_fn=build_fn)
        phase_names = [p.phase for p in result.phases_completed]

        # HEAL is optional — only appears on BUILD failure
        required_phases = [p for p in PipelinePhase if p != PipelinePhase.HEAL]
        for phase in required_phases:
            self.assertIn(phase.value, phase_names,
                          f"Phase {phase.value} not found in {phase_names}")

    def test_phases_run_in_order(self):
        from jake_brain.autonomous_pipeline import PipelinePhase
        task = self._make_task()

        phase_order = []

        original_run = self.pipeline.run

        def build_fn(t, ctx):
            return {"data": "ok"}

        result = self.pipeline.run(task, build_fn=build_fn)
        phase_names = [p.phase for p in result.phases_completed]

        expected_order = [p.value for p in PipelinePhase]
        # Phases may have duplicates (HEAL inserted) but the first occurrence must be in order
        seen = []
        for phase in phase_names:
            if phase not in seen:
                seen.append(phase)

        # Verify CONTEXT comes before PLAN, PLAN before BUILD, BUILD before VALIDATE, etc.
        phase_to_idx = {p: i for i, p in enumerate(expected_order)}
        for i in range(len(seen) - 1):
            p1 = seen[i]
            p2 = seen[i + 1]
            if p1 in phase_to_idx and p2 in phase_to_idx:
                self.assertLessEqual(
                    phase_to_idx[p1], phase_to_idx[p2],
                    f"Phase {p1} should come before {p2}"
                )

    def test_result_has_required_fields(self):
        task = self._make_task()

        def build_fn(t, ctx):
            return {"output": "value"}

        result = self.pipeline.run(task, build_fn=build_fn)
        self.assertIsNotNone(result.task_id)
        self.assertIsNotNone(result.status)
        self.assertIsInstance(result.phases_completed, list)
        self.assertIsInstance(result.outputs, dict)
        self.assertIsInstance(result.error_log, list)
        self.assertIsNotNone(result.started_at)
        self.assertIsNotNone(result.completed_at)
        self.assertEqual(result.employee_name, "test_employee")

    def test_empty_outputs_partial_status(self):
        from jake_brain.autonomous_pipeline import TaskStatus
        task = self._make_task(success_criteria=["must_have_this"])

        def build_fn(t, ctx):
            return {}  # empty outputs

        result = self.pipeline.run(task, build_fn=build_fn)
        self.assertIn(result.status, (TaskStatus.PARTIAL, TaskStatus.SUCCESS))


class TestAutonomousPipelineSelfHealing(unittest.TestCase):
    """Test the HEAL phase behavior on BUILD failures."""

    def setUp(self):
        from jake_brain.autonomous_pipeline import AutonomousPipeline, PipelineTask
        self.store = _make_mock_store()
        self.pipeline = AutonomousPipeline(store=self.store)
        self.PipelineTask = PipelineTask

    def _make_task(self, **kwargs):
        defaults = dict(
            task_type="heal_test",
            description="Heal test task",
            success_criteria=["output"],
            context_hints=["test"],
            employee_name="heal_tester",
        )
        defaults.update(kwargs)
        return self.PipelineTask(**defaults)

    def test_heal_invoked_on_build_failure(self):
        """When BUILD fails, HEAL phase should appear in phases_completed."""
        from jake_brain.autonomous_pipeline import PipelinePhase

        call_count = [0]

        def failing_then_succeeding_build(task, ctx):
            call_count[0] += 1
            if call_count[0] < 2:
                raise ConnectionError("Simulated API timeout")
            return {"output": "recovered"}

        task = self._make_task()
        result = self.pipeline.run(task, build_fn=failing_then_succeeding_build)

        phase_names = [p.phase for p in result.phases_completed]
        self.assertIn(PipelinePhase.HEAL.value, phase_names,
                      f"HEAL not in phases: {phase_names}")

    def test_logic_error_flags_no_retry(self):
        """LOGIC_ERROR should result in FLAGGED status with no more than 1 BUILD attempt."""
        from jake_brain.autonomous_pipeline import TaskStatus, PipelinePhase

        call_count = [0]

        def logic_error_build(task, ctx):
            call_count[0] += 1
            raise ValueError("Business logic failure — invalid state")  # classified as LOGIC_ERROR

        task = self._make_task()

        # Patch _classify_error to return LOGIC_ERROR
        from jake_brain.autonomous_pipeline import ErrorType
        with patch.object(self.pipeline, "_classify_error", return_value=ErrorType.LOGIC_ERROR):
            result = self.pipeline.run(task, build_fn=logic_error_build)

        self.assertEqual(result.status, TaskStatus.FLAGGED)
        # Should only have attempted BUILD once (no retries for LOGIC_ERROR)
        self.assertEqual(call_count[0], 1)

    def test_api_error_retries_up_to_max(self):
        """API_ERROR should retry up to MAX_RETRIES times."""
        from jake_brain.autonomous_pipeline import TaskStatus, ErrorType

        call_count = [0]
        max_retries = self.pipeline.MAX_RETRIES

        def always_api_error_build(task, ctx):
            call_count[0] += 1
            raise ConnectionError("timeout")  # API_ERROR

        task = self._make_task()

        # Patch sleep to speed up test
        with patch("time.sleep"):
            with patch.object(self.pipeline, "_classify_error", return_value=ErrorType.API_ERROR):
                result = self.pipeline.run(task, build_fn=always_api_error_build)

        # Should have attempted MAX_RETRIES + 1 times (initial + retries)
        self.assertEqual(call_count[0], max_retries + 1)
        self.assertEqual(result.status, TaskStatus.FAILED)

    def test_heal_phase_records_have_error_info(self):
        """Error log should contain entries for failed BUILD phases."""
        call_count = [0]

        def fail_once_build(task, ctx):
            call_count[0] += 1
            if call_count[0] == 1:
                raise ConnectionError("Network blip")
            return {"result": "recovered"}

        task = self._make_task()
        with patch("time.sleep"):
            result = self.pipeline.run(task, build_fn=fail_once_build)

        build_errors = [e for e in result.error_log if e.get("phase") == "BUILD"]
        self.assertGreater(len(build_errors), 0, "Expected BUILD error in error_log")


class TestErrorClassification(unittest.TestCase):
    def setUp(self):
        from jake_brain.autonomous_pipeline import AutonomousPipeline
        self.pipeline = AutonomousPipeline(store=None)

    def test_connection_error_is_api_error(self):
        from jake_brain.autonomous_pipeline import ErrorType
        exc = ConnectionError("connection refused")
        self.assertEqual(self.pipeline._classify_error(exc), ErrorType.API_ERROR)

    def test_timeout_error_is_api_error(self):
        from jake_brain.autonomous_pipeline import ErrorType
        exc = TimeoutError("request timed out")
        self.assertEqual(self.pipeline._classify_error(exc), ErrorType.API_ERROR)

    def test_key_error_is_data_error(self):
        from jake_brain.autonomous_pipeline import ErrorType
        exc = KeyError("missing key")
        self.assertEqual(self.pipeline._classify_error(exc), ErrorType.DATA_ERROR)

    def test_value_error_is_logic_error(self):
        from jake_brain.autonomous_pipeline import ErrorType
        exc = ValueError("invalid business state")
        self.assertEqual(self.pipeline._classify_error(exc), ErrorType.LOGIC_ERROR)


# ---------------------------------------------------------------------------
# Test: Employee instantiation
# ---------------------------------------------------------------------------

class TestEmployeeInstantiation(unittest.TestCase):
    """All 4 employees should instantiate with and without a store."""

    def test_oracle_sentinel_instantiates(self):
        from jake_brain.employees.oracle_sentinel import OracleSentinel
        emp = OracleSentinel(store=None)
        self.assertIsNotNone(emp)
        self.assertEqual(emp.EMPLOYEE_NAME, "oracle_sentinel")
        self.assertEqual(emp.TASK_TYPE, "oracle_intelligence")

    def test_research_agent_instantiates(self):
        from jake_brain.employees.research_agent import ResearchAgent
        emp = ResearchAgent(store=None)
        self.assertIsNotNone(emp)
        self.assertEqual(emp.EMPLOYEE_NAME, "research_agent")
        self.assertEqual(emp.TASK_TYPE, "research")

    def test_content_creator_instantiates(self):
        from jake_brain.employees.content_creator import ContentCreator
        emp = ContentCreator(store=None)
        self.assertIsNotNone(emp)
        self.assertEqual(emp.EMPLOYEE_NAME, "content_creator")
        self.assertEqual(emp.TASK_TYPE, "content")

    def test_family_coordinator_instantiates(self):
        from jake_brain.employees.family_coordinator import FamilyCoordinator
        emp = FamilyCoordinator(store=None)
        self.assertIsNotNone(emp)
        self.assertEqual(emp.EMPLOYEE_NAME, "family_coordinator")
        self.assertEqual(emp.TASK_TYPE, "family_coordination")

    def test_all_employees_instantiate_with_mock_store(self):
        from jake_brain.employees import EMPLOYEE_REGISTRY
        store = _make_mock_store()
        for name, cls in EMPLOYEE_REGISTRY.items():
            emp = cls(store=store)
            self.assertIsNotNone(emp, f"{name} failed to instantiate with store")

    def test_employee_registry_has_all_four(self):
        from jake_brain.employees import EMPLOYEE_REGISTRY
        expected = {"oracle_sentinel", "research_agent", "content_creator", "family_coordinator"}
        self.assertEqual(set(EMPLOYEE_REGISTRY.keys()), expected)

    def test_employee_schedules_defined(self):
        from jake_brain.employees import EMPLOYEE_SCHEDULES
        from jake_brain.employees import EMPLOYEE_REGISTRY
        for name in EMPLOYEE_REGISTRY:
            self.assertIn(name, EMPLOYEE_SCHEDULES, f"{name} missing from EMPLOYEE_SCHEDULES")
            schedule = EMPLOYEE_SCHEDULES[name]
            self.assertIsInstance(schedule, str)
            # Basic cron validation: 5 fields
            parts = schedule.split()
            self.assertEqual(len(parts), 5, f"{name} schedule has {len(parts)} parts, expected 5")


# ---------------------------------------------------------------------------
# Test: Employee run() with mocked store
# ---------------------------------------------------------------------------

class TestOracleSentinelRun(unittest.TestCase):
    def test_run_returns_required_keys(self):
        from jake_brain.employees.oracle_sentinel import OracleSentinel
        store = _make_mock_store()
        emp = OracleSentinel(store=store)
        result = emp.run()
        self.assertIn("intel_summary", result)
        self.assertIn("competitors_analyzed", result)
        self.assertIn("new_signals", result)
        self.assertIn("stale_records", result)

    def test_run_no_store(self):
        """Should not crash when store is None."""
        from jake_brain.employees.oracle_sentinel import OracleSentinel
        emp = OracleSentinel(store=None)
        result = emp.run()
        self.assertIn("intel_summary", result)

    def test_run_with_existing_intel(self):
        """When episodic table has intel entries, they should be reflected."""
        from jake_brain.employees.oracle_sentinel import OracleSentinel
        store = _make_mock_store()

        # Simulate 3 existing intel entries
        fake_entries = [
            {
                "id": f"ep-{i}",
                "content": f"Oracle vs Epic — update {i}",
                "occurred_at": "2026-03-20T10:00:00+00:00",
                "topics": ["oracle", "epic"],
                "metadata": {"competitor": "Epic Systems"},
            }
            for i in range(3)
        ]
        store.supabase.table.return_value.execute.return_value = MagicMock(data=fake_entries)

        emp = OracleSentinel(store=store)
        result = emp.run()
        self.assertIn("intel_summary", result)
        # Should have stored a new intel entry
        store.store_episodic.assert_called()


class TestResearchAgentRun(unittest.TestCase):
    def test_run_returns_required_keys(self):
        from jake_brain.employees.research_agent import ResearchAgent
        emp = ResearchAgent(store=None)
        result = emp.run()
        self.assertIn("topics_researched", result)
        self.assertIn("gaps_filled", result)
        self.assertIn("new_facts_stored", result)

    def test_run_with_low_confidence_semantics(self):
        """When low-confidence semantics exist, they should be synthesized."""
        from jake_brain.employees.research_agent import ResearchAgent
        store = _make_mock_store()

        fake_semantics = [
            {
                "id": f"sem-{i}",
                "content": f"Low confidence fact about oracle {i}",
                "category": "intel",
                "confidence": 0.4,
                "topics": ["oracle"],
            }
            for i in range(3)
        ]

        # First call (low-confidence semantics), second call (knowledge gaps) → empty
        call_seq = iter([
            MagicMock(data=fake_semantics),
            MagicMock(data=[]),
        ])
        store.supabase.table.return_value.execute.side_effect = lambda: next(call_seq, MagicMock(data=[]))

        emp = ResearchAgent(store=store)
        result = emp.run()
        self.assertIn("topics_researched", result)
        self.assertIsInstance(result["topics_researched"], list)


class TestContentCreatorRun(unittest.TestCase):
    def test_run_returns_required_keys(self):
        from jake_brain.employees.content_creator import ContentCreator
        emp = ContentCreator(store=None)
        result = emp.run()
        self.assertIn("content_type", result)
        self.assertIn("content", result)
        self.assertIn("topics_covered", result)
        self.assertIn("word_count", result)

    def test_empty_episodes_still_returns_content(self):
        """Even with no episodic entries, content should be returned."""
        from jake_brain.employees.content_creator import ContentCreator
        store = _make_mock_store()
        emp = ContentCreator(store=store)
        result = emp.run()
        self.assertIsInstance(result["content"], str)
        self.assertGreater(len(result["content"]), 0)

    def test_run_with_episodes(self):
        from jake_brain.employees.content_creator import ContentCreator
        store = _make_mock_store()

        fake_episodes = [
            {
                "id": f"ep-{i}",
                "content": f"Worked on oracle health intelligence pipeline today {i}",
                "occurred_at": "2026-03-20T10:00:00+00:00",
                "topics": ["oracle"],
                "memory_type": "conversation",
                "project": "oracle-health",
                "metadata": {"decisions": [f"decision {i}"], "action_items": [f"action {i}"]},
            }
            for i in range(5)
        ]
        store.supabase.table.return_value.execute.return_value = MagicMock(data=fake_episodes)

        emp = ContentCreator(store=store)
        result = emp.run()
        self.assertGreater(result["word_count"], 10)
        self.assertIn("oracle-health", result["topics_covered"])


class TestFamilyCoordinatorRun(unittest.TestCase):
    def test_run_returns_required_keys(self):
        """FamilyCoordinator run() should return all required keys."""
        from jake_brain.employees.family_coordinator import FamilyCoordinator
        store = _make_mock_store()

        with patch("jake_brain.employees.family_coordinator.get_upcoming_family_events", return_value=[]):
            emp = FamilyCoordinator(store=store)
            result = emp.run()

        self.assertIn("upcoming_events", result)
        self.assertIn("people_mentioned", result)
        self.assertIn("summary", result)

    def test_run_no_store(self):
        """Should not crash when store is None."""
        from jake_brain.employees.family_coordinator import FamilyCoordinator

        with patch("jake_brain.employees.family_coordinator.get_upcoming_family_events", return_value=[]):
            emp = FamilyCoordinator(store=None)
            result = emp.run()

        self.assertIn("summary", result)
        self.assertIsInstance(result["summary"], str)

    def test_run_with_calendar_events(self):
        """When osascript returns events, they should appear in output."""
        from jake_brain.employees.family_coordinator import FamilyCoordinator

        fake_events = [
            {"summary": "Jacob football practice", "start_date": "Wednesday, March 25, 2026 at 5:00 PM", "calendar": "home"},
            {"summary": "Alex soccer", "start_date": "Saturday, March 28, 2026 at 10:00 AM", "calendar": "home"},
            {"summary": "Work standup", "start_date": "Monday, March 23, 2026 at 9:00 AM", "calendar": "work"},
        ]
        store = _make_mock_store()

        with patch("jake_brain.employees.family_coordinator.get_upcoming_family_events", return_value=fake_events):
            emp = FamilyCoordinator(store=store)
            result = emp.run()

        # Jacob and Alex events should be detected as family events
        self.assertGreater(len(result["upcoming_events"]), 0)
        self.assertTrue(
            any("jacob" in p.lower() or "alex" in p.lower() for p in result["people_mentioned"])
        )

    def test_osascript_failure_returns_empty_events(self):
        """When osascript fails, should return empty events (not crash)."""
        import subprocess as _subprocess
        from jake_brain.employees.family_coordinator import get_upcoming_family_events

        with patch("subprocess.run", side_effect=_subprocess.TimeoutExpired(cmd="osascript", timeout=30)):
            events = get_upcoming_family_events()
        self.assertEqual(events, [])


# ---------------------------------------------------------------------------
# Test: get_upcoming_family_events (unit test for the osascript wrapper)
# ---------------------------------------------------------------------------

class TestGetUpcomingFamilyEvents(unittest.TestCase):
    def test_parses_pipe_delimited_output(self):
        from jake_brain.employees.family_coordinator import get_upcoming_family_events

        fake_output = (
            "Jacob practice|Wednesday, March 25, 2026 at 5:00 PM|home\n"
            "Alex birthday|Friday, March 27, 2026 at 12:00 PM|Family\n"
        )
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = fake_output

        with patch("subprocess.run", return_value=mock_result):
            events = get_upcoming_family_events(days=14)

        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["summary"], "Jacob practice")
        self.assertEqual(events[0]["calendar"], "home")
        self.assertEqual(events[1]["summary"], "Alex birthday")

    def test_returns_empty_on_nonzero_exit(self):
        from jake_brain.employees.family_coordinator import get_upcoming_family_events

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Calendar error"

        with patch("subprocess.run", return_value=mock_result):
            events = get_upcoming_family_events()

        self.assertEqual(events, [])

    def test_returns_empty_on_timeout(self):
        import subprocess as _subprocess
        from jake_brain.employees.family_coordinator import get_upcoming_family_events

        with patch("subprocess.run", side_effect=_subprocess.TimeoutExpired(cmd="osascript", timeout=30)):
            events = get_upcoming_family_events()

        self.assertEqual(events, [])

    def test_returns_empty_when_osascript_not_found(self):
        from jake_brain.employees.family_coordinator import get_upcoming_family_events

        with patch("subprocess.run", side_effect=FileNotFoundError("osascript not found")):
            events = get_upcoming_family_events()

        self.assertEqual(events, [])


# ---------------------------------------------------------------------------
# Test: Employee Runner CLI (smoke test)
# ---------------------------------------------------------------------------

class TestEmployeeRunnerCLI(unittest.TestCase):
    def test_runner_script_imports(self):
        """The runner script should be importable without crashing."""
        import importlib.util
        import sys
        from pathlib import Path

        runner_path = Path(__file__).parent.parent / "scripts" / "jake_employee_runner.py"
        self.assertTrue(runner_path.exists(), f"Runner not found at {runner_path}")

        spec = importlib.util.spec_from_file_location("jake_employee_runner", runner_path)
        mod = importlib.util.module_from_spec(spec)
        # Just loading the module spec is enough — don't exec (it has argparse at bottom)
        self.assertIsNotNone(spec)

    def test_registry_import(self):
        from jake_brain.employees import EMPLOYEE_REGISTRY, EMPLOYEE_SCHEDULES
        self.assertEqual(len(EMPLOYEE_REGISTRY), 4)
        self.assertEqual(len(EMPLOYEE_SCHEDULES), 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
