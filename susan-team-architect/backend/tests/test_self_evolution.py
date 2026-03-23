"""Tests for Self-Evolution components (A/B testing, auto-skill, SOUL versioner)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# AB Testing tests
# ---------------------------------------------------------------------------

class TestABTestRunner(unittest.TestCase):

    def setUp(self):
        """Use a temp file for test isolation."""
        self.tmp = tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False)
        self.tmp_path = Path(self.tmp.name)
        self.tmp.close()

    def _make_runner(self):
        from self_improvement.ab_testing import ABTestRunner
        runner = ABTestRunner()
        # Override the results file path to the temp file
        import self_improvement.ab_testing as mod
        self._orig_path = mod._RESULTS_FILE
        mod._RESULTS_FILE = self.tmp_path
        return runner

    def tearDown(self):
        import self_improvement.ab_testing as mod
        if hasattr(self, "_orig_path"):
            mod._RESULTS_FILE = self._orig_path
        self.tmp_path.unlink(missing_ok=True)

    def test_create_test_returns_id(self):
        runner = self._make_runner()
        test_id = runner.create_test("oracle_sentinel", "system_prompt", "Variant A", "Variant B")
        self.assertIsInstance(test_id, str)
        self.assertTrue(len(test_id) > 0)

    def test_record_and_resolve_winner_a(self):
        runner = self._make_runner()
        test_id = runner.create_test("agent_x", "tone", "Direct tone", "Verbose tone")
        runner.record_outcome(test_id, "a", score=0.90)
        runner.record_outcome(test_id, "a", score=0.85)
        runner.record_outcome(test_id, "b", score=0.70)
        runner.record_outcome(test_id, "b", score=0.65)
        winner = runner.resolve_test(test_id)
        self.assertEqual(winner, "a")

    def test_resolve_tie(self):
        runner = self._make_runner()
        test_id = runner.create_test("agent_y", "format", "Format A", "Format B")
        runner.record_outcome(test_id, "a", score=0.80)
        runner.record_outcome(test_id, "b", score=0.80)
        winner = runner.resolve_test(test_id)
        self.assertIsNone(winner)

    def test_get_active_tests(self):
        runner = self._make_runner()
        id1 = runner.create_test("a1", "s", "va", "vb")
        id2 = runner.create_test("a2", "s", "va", "vb")
        runner.record_outcome(id1, "a", 0.9)
        runner.record_outcome(id1, "b", 0.7)
        runner.resolve_test(id1)
        active = runner.get_active_tests()
        ids = [t["id"] for t in active]
        self.assertNotIn(id1, ids)
        self.assertIn(id2, ids)

    def test_get_winner_prompt(self):
        runner = self._make_runner()
        test_id = runner.create_test("agent", "section", "Winner text", "Loser text")
        runner.record_outcome(test_id, "a", 0.9)
        runner.record_outcome(test_id, "b", 0.5)
        runner.resolve_test(test_id)
        prompt = runner.get_winner_prompt(test_id)
        self.assertEqual(prompt, "Winner text")

    def test_summary(self):
        runner = self._make_runner()
        runner.create_test("a", "s", "v1", "v2")
        summary = runner.summary()
        self.assertIn("total", summary)
        self.assertIn("active", summary)
        self.assertEqual(summary["total"], 1)


# ---------------------------------------------------------------------------
# Auto-skill creator tests
# ---------------------------------------------------------------------------

class TestAutoSkillCreator(unittest.TestCase):

    def _make_creator(self, tmp_dir):
        from self_improvement.auto_skill_creator import AutoSkillCreator
        import self_improvement.auto_skill_creator as mod
        self._orig_dir = mod._SKILLS_DIR
        self._orig_reg = mod._REGISTRY_FILE
        mod._SKILLS_DIR = Path(tmp_dir) / "auto-generated"
        mod._REGISTRY_FILE = Path(tmp_dir) / "auto-generated" / "registry.json"
        creator = AutoSkillCreator()
        return creator

    def tearDown(self):
        from self_improvement import auto_skill_creator as mod
        if hasattr(self, "_orig_dir"):
            mod._SKILLS_DIR = self._orig_dir
            mod._REGISTRY_FILE = self._orig_reg

    def test_no_patterns_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            creator = self._make_creator(tmp)
            with patch.object(creator, "_load_procedural_patterns", return_value=[]):
                patterns = creator.detect_patterns(min_frequency=3)
                self.assertEqual(patterns, [])

    def test_detect_repeated_patterns(self):
        with tempfile.TemporaryDirectory() as tmp:
            creator = self._make_creator(tmp)
            mock_patterns = [
                {"task_type": "research", "actions": ["search", "store"], "success": True, "duration_ms": 500},
            ] * 4  # repeat 4 times
            with patch.object(creator, "_load_procedural_patterns", return_value=mock_patterns):
                patterns = creator.detect_patterns(min_frequency=3)
                self.assertEqual(len(patterns), 1)
                self.assertEqual(patterns[0]["frequency"], 4)
                self.assertEqual(patterns[0]["task_type"], "research")

    def test_create_skills_writes_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            creator = self._make_creator(tmp)
            patterns = [{
                "key": "research:search,store",
                "frequency": 5,
                "task_type": "research",
                "actions": ["search", "store"],
                "success_rate": 0.9,
                "avg_duration_ms": 400,
                "examples": [],
            }]
            created = creator.create_skills_from_patterns(patterns)
            self.assertEqual(len(created), 1)
            skill_name = created[0]
            skill_dir = Path(tmp) / "auto-generated" / skill_name
            self.assertTrue((skill_dir / "skill.yaml").exists())
            self.assertTrue((skill_dir / "handler.py").exists())

    def test_low_success_rate_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            creator = self._make_creator(tmp)
            patterns = [{
                "key": "broken:a,b",
                "frequency": 10,
                "task_type": "broken",
                "actions": ["a", "b"],
                "success_rate": 0.5,  # below 0.7 threshold
                "avg_duration_ms": 1000,
                "examples": [],
            }]
            created = creator.create_skills_from_patterns(patterns)
            self.assertEqual(created, [])

    def test_list_generated_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            creator = self._make_creator(tmp)
            skills = creator.list_generated_skills()
            self.assertIsInstance(skills, list)


# ---------------------------------------------------------------------------
# SOUL Versioner tests
# ---------------------------------------------------------------------------

class TestSoulVersioner(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.soul_path = Path(self.tmp_dir) / "SOUL.md"
        self.soul_path.write_text("# Jake\n\nI am a 15-year-old prodigy.\n")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _make_versioner(self):
        from self_improvement.soul_versioner import SoulVersioner, _VERSIONS_LOG, _VERSIONS_DIR
        import self_improvement.soul_versioner as mod
        self._orig_log = mod._VERSIONS_LOG
        self._orig_dir = mod._VERSIONS_DIR
        mod._VERSIONS_LOG = Path(self.tmp_dir) / "soul_versions.jsonl"
        mod._VERSIONS_DIR = Path(self.tmp_dir) / "soul_archive"
        return SoulVersioner(soul_path=self.soul_path)

    def tearDown(self):
        import self_improvement.soul_versioner as mod
        if hasattr(self, "_orig_log"):
            mod._VERSIONS_LOG = self._orig_log
            mod._VERSIONS_DIR = self._orig_dir
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_checkpoint_creates_version(self):
        versioner = self._make_versioner()
        version_id = versioner.checkpoint("initial")
        self.assertEqual(version_id, "v1")
        versions = versioner.list_versions()
        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0]["version_id"], "v1")

    def test_checkpoint_deduplicates_unchanged(self):
        versioner = self._make_versioner()
        v1 = versioner.checkpoint("first")
        v2 = versioner.checkpoint("same content")
        self.assertEqual(v1, v2)  # no new version if content unchanged
        self.assertEqual(len(versioner.list_versions()), 1)

    def test_rollback_restores_content(self):
        versioner = self._make_versioner()
        versioner.checkpoint("original")
        original = self.soul_path.read_text()

        # Modify SOUL.md
        self.soul_path.write_text("# Modified Jake\n\nDifferent content.\n")
        versioner.checkpoint("modified")

        # Rollback to v1
        result = versioner.rollback("v1")
        self.assertTrue(result)
        restored = self.soul_path.read_text()
        self.assertEqual(restored, original)

    def test_diff_versions(self):
        versioner = self._make_versioner()
        versioner.checkpoint("v1")
        self.soul_path.write_text("# Jake\n\nI am a brilliant 15-year-old prodigy.\n")
        versioner.checkpoint("v2 — added brilliant")
        diff = versioner.diff_versions("v1", "v2")
        self.assertIn("prodigy", diff)

    def test_drift_report_detects_change(self):
        versioner = self._make_versioner()
        versioner.checkpoint("baseline")
        self.soul_path.write_text("# Jake MODIFIED\n\nCompletely different.\n")
        report = versioner.drift_report()
        self.assertIn("drifted", report)

    def test_drift_report_no_change(self):
        versioner = self._make_versioner()
        versioner.checkpoint("baseline")
        report = versioner.drift_report()
        self.assertIn("unchanged", report)


if __name__ == "__main__":
    unittest.main()
