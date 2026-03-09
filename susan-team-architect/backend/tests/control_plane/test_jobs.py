from control_plane.jobs import SusanRunManager


def test_susan_run_manager_dedupes_pending_job():
    manager = SusanRunManager(autostart=False)
    first = manager.submit("transformfit", "quick", False)
    second = manager.submit("transformfit", "quick", False)
    assert first.id == second.id


def test_susan_run_manager_reuses_recent_completed_job():
    manager = SusanRunManager(autostart=False)
    first = manager.submit("transformfit", "quick", False, prefer_cached=False)
    first.status = "completed"
    first.finished_at = first.created_at
    assert first.output_dir is not None
    profile_path = manager.queue_dir.parent / "test-profile.json"
    profile_path.write_text('{"company":"TransformFit"}', encoding="utf-8")
    first.result_files = {"profile": str(profile_path)}

    second = manager.submit("transformfit", "quick", False, prefer_cached=True, max_age_minutes=240)

    assert first.id == second.id
    assert second.cache_hit is True
