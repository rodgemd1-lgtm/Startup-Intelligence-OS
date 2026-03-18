"""Tests for Birch signal writer and CLI."""
import json
from pathlib import Path

import pytest


def test_writer_append(tmp_path: Path):
    from birch.writer import SignalWriter
    from birch.schemas import ScoredSignal

    writer = SignalWriter(signals_dir=tmp_path)
    sig = ScoredSignal(
        source="firehose",
        title="Test Signal",
        score=85,
        tier=1,
        company="oracle-health",
    )
    writer.append(sig)

    files = list(tmp_path.glob("scored-*.jsonl"))
    assert len(files) == 1
    line = files[0].read_text().strip()
    record = json.loads(line)
    assert record["title"] == "Test Signal"
    assert record["tier"] == 1


def test_writer_multiple_signals(tmp_path: Path):
    from birch.writer import SignalWriter
    from birch.schemas import ScoredSignal

    writer = SignalWriter(signals_dir=tmp_path)
    for i in range(3):
        writer.append(ScoredSignal(
            source="manual", title=f"Signal {i}", score=50 + i * 20, tier=2,
        ))

    files = list(tmp_path.glob("scored-*.jsonl"))
    assert len(files) == 1
    lines = files[0].read_text().strip().split("\n")
    assert len(lines) == 3


def test_writer_stats(tmp_path: Path):
    from birch.writer import SignalWriter
    from birch.schemas import ScoredSignal

    writer = SignalWriter(signals_dir=tmp_path)
    writer.append(ScoredSignal(source="manual", title="A", score=90, tier=1))
    writer.append(ScoredSignal(source="manual", title="B", score=65, tier=2))
    writer.append(ScoredSignal(source="manual", title="C", score=30, tier=3))

    stats = writer.stats()
    assert stats["total"] == 3
    assert stats["tier_1"] == 1
    assert stats["tier_2"] == 1
    assert stats["tier_3"] == 1
