"""Signal Writer — appends scored signals to JSONL files."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from birch.schemas import ScoredSignal


class SignalWriter:
    def __init__(self, signals_dir: Path) -> None:
        self._dir = signals_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    def append(self, signal: ScoredSignal) -> None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        path = self._dir / f"scored-{date_str}.jsonl"
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(signal.model_dump_json() + "\n")

    def stats(self, days: int = 1) -> dict:
        total = 0
        tiers = {1: 0, 2: 0, 3: 0}
        for path in sorted(self._dir.glob("scored-*.jsonl"), reverse=True)[:days]:
            for line in path.read_text().strip().split("\n"):
                if not line:
                    continue
                record = json.loads(line)
                total += 1
                tier = record.get("tier", 3)
                tiers[tier] = tiers.get(tier, 0) + 1
        return {"total": total, "tier_1": tiers[1], "tier_2": tiers[2], "tier_3": tiers[3]}
