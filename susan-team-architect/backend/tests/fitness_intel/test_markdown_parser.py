from pathlib import Path

from fitness_intel.markdown_parser import build_app_record, parse_markdown_profile


def test_parse_markdown_profile_extracts_sections():
    profile = parse_markdown_profile(Path("apps/fitness/strava.md"))
    assert profile.title.startswith("Strava")
    assert "1. Overview" in profile.sections
    assert profile.metadata["Last Updated"] == "2026-03-03"


def test_build_app_record_from_markdown():
    profile = parse_markdown_profile(Path("apps/fitness/fitbod.md"))
    app = build_app_record(profile)
    assert app.name == "Fitbod"
    assert app.slug == "fitbod"
    assert app.editorial_markdown_path.endswith("apps/fitness/fitbod.md")
    assert app.sources

