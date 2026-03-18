"""Trust Tracker — records chain outcomes and manages trust profiles."""
from __future__ import annotations

import json
from pathlib import Path

from trust.schemas import TrustProfile


class TrustTracker:
    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._profiles: dict[str, TrustProfile] = {}
        self._profiles_path = self._data_dir / "trust_profiles.json"

    def record_outcome(self, chain_name: str, success: bool, blocked: bool = False) -> None:
        if chain_name not in self._profiles:
            self._profiles[chain_name] = TrustProfile(chain_name=chain_name)
        profile = self._profiles[chain_name]
        profile.total_runs += 1
        if success:
            profile.successful_runs += 1
        if blocked:
            profile.blocked_runs += 1
        from datetime import datetime, timezone
        profile.last_run_at = datetime.now(timezone.utc).isoformat()

    def get_profile(self, chain_name: str) -> TrustProfile:
        if chain_name not in self._profiles:
            self._profiles[chain_name] = TrustProfile(chain_name=chain_name)
        return self._profiles[chain_name]

    def all_profiles(self) -> list[TrustProfile]:
        return list(self._profiles.values())

    def save(self) -> None:
        data = {name: p.model_dump() for name, p in self._profiles.items()}
        self._profiles_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load(self) -> None:
        if self._profiles_path.exists():
            data = json.loads(self._profiles_path.read_text(encoding="utf-8"))
            self._profiles = {name: TrustProfile(**d) for name, d in data.items()}
