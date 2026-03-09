from pathlib import Path

from susan_core.phase_runtime import load_cache, save_cache


def test_phase_cache_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr("susan_core.phase_runtime.config.phase_cache_dir", tmp_path)
    payload = {"company": "demo", "step": 1}
    save_cache("demo", "analysis", payload, {"value": 42})
    cached = load_cache("demo", "analysis", payload)
    assert cached == {"value": 42}
