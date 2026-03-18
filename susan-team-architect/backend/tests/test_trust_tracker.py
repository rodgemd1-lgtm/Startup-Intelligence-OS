"""Tests for trust tracker — autonomy levels, run tracking, graduation."""
import pytest
from pathlib import Path


def test_trust_profile_defaults():
    from trust.schemas import TrustProfile

    profile = TrustProfile(chain_name="daily-cycle")
    assert profile.level == "MANUAL"
    assert profile.total_runs == 0
    assert profile.successful_runs == 0


def test_tracker_record_success(tmp_path: Path):
    from trust.tracker import TrustTracker

    tracker = TrustTracker(data_dir=tmp_path)
    tracker.record_outcome("daily-cycle", success=True)
    tracker.record_outcome("daily-cycle", success=True)
    tracker.record_outcome("daily-cycle", success=False)

    profile = tracker.get_profile("daily-cycle")
    assert profile.total_runs == 3
    assert profile.successful_runs == 2
    assert profile.accuracy == pytest.approx(66.67, abs=0.1)


def test_tracker_blast_radius_cap():
    from trust.config import blast_radius_cap

    assert blast_radius_cap("competitive-response") == "SUPERVISED"
    assert blast_radius_cap("executive-brief") == "SUPERVISED"
    assert blast_radius_cap("daily-cycle") is None  # no cap


def test_tracker_autonomous_eligible():
    from trust.config import is_autonomous_eligible

    assert is_autonomous_eligible("daily-cycle") is True
    assert is_autonomous_eligible("research-refresh") is True
    assert is_autonomous_eligible("competitive-response") is False


def test_tracker_persist_and_reload(tmp_path: Path):
    from trust.tracker import TrustTracker

    tracker = TrustTracker(data_dir=tmp_path)
    for _ in range(5):
        tracker.record_outcome("daily-cycle", success=True)
    tracker.save()

    tracker2 = TrustTracker(data_dir=tmp_path)
    tracker2.load()
    profile = tracker2.get_profile("daily-cycle")
    assert profile.total_runs == 5
