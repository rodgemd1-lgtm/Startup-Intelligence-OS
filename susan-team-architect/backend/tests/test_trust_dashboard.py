"""Tests for trust dashboard and enforcer."""
from pathlib import Path

import pytest

BACKEND_DIR = str(Path(__file__).resolve().parent.parent)


def test_enforcer_manual_chain(tmp_path: Path):
    from trust.enforcer import TrustEnforcer
    from trust.tracker import TrustTracker

    tracker = TrustTracker(data_dir=tmp_path)
    enforcer = TrustEnforcer(tracker=tracker)
    disposition = enforcer.check("daily-cycle")
    assert disposition == "STAGE"  # MANUAL = always stage


def test_enforcer_supervised_chain(tmp_path: Path):
    from trust.enforcer import TrustEnforcer
    from trust.tracker import TrustTracker

    tracker = TrustTracker(data_dir=tmp_path)
    profile = tracker.get_profile("daily-cycle")
    profile.level = "SUPERVISED"
    enforcer = TrustEnforcer(tracker=tracker)
    disposition = enforcer.check("daily-cycle")
    assert disposition == "STAGE"  # SUPERVISED = stage for review


def test_enforcer_autonomous_chain(tmp_path: Path):
    from trust.enforcer import TrustEnforcer
    from trust.tracker import TrustTracker

    tracker = TrustTracker(data_dir=tmp_path)
    profile = tracker.get_profile("daily-cycle")
    profile.level = "AUTONOMOUS"
    enforcer = TrustEnforcer(tracker=tracker)
    disposition = enforcer.check("daily-cycle")
    assert disposition == "PUBLISH"  # AUTONOMOUS = auto-publish


def test_dashboard_markdown(tmp_path: Path):
    from trust.dashboard import generate_markdown
    from trust.tracker import TrustTracker

    tracker = TrustTracker(data_dir=tmp_path)
    for _ in range(25):
        tracker.record_outcome("daily-cycle", success=True)
    for _ in range(10):
        tracker.record_outcome("competitive-response", success=True)
    tracker.record_outcome("competitive-response", success=False)

    md = generate_markdown(tracker)
    assert "daily-cycle" in md
    assert "competitive-response" in md
    assert "MANUAL" in md  # default level


def test_dashboard_cli_runs(tmp_path: Path):
    import subprocess, sys

    result = subprocess.run(
        [sys.executable, "-m", "trust", "--command", "dashboard"],
        capture_output=True,
        text=True,
        cwd=BACKEND_DIR,
    )
    assert result.returncode == 0
    assert "Trust Dashboard" in result.stdout
