"""Tests for chain engine and registry."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import pytest


def test_registry_register_and_get():
    from chains.registry import ChainRegistry
    from chains.schemas import ChainDef, ChainStep, ManualTrigger

    reg = ChainRegistry()
    chain = ChainDef(
        name="test-chain",
        trigger=ManualTrigger(),
        steps=[ChainStep(agent="scout", output_key="signals")],
    )
    reg.register(chain)
    assert reg.get("test-chain") is chain


def test_registry_list_chains():
    from chains.registry import ChainRegistry
    from chains.schemas import ChainDef, ChainStep, ManualTrigger

    reg = ChainRegistry()
    for name in ["chain-a", "chain-b", "chain-c"]:
        reg.register(ChainDef(
            name=name,
            trigger=ManualTrigger(),
            steps=[ChainStep(agent="scout", output_key="out")],
        ))
    assert sorted(reg.list_names()) == ["chain-a", "chain-b", "chain-c"]


def test_registry_get_unknown_raises():
    from chains.registry import ChainRegistry

    reg = ChainRegistry()
    with pytest.raises(KeyError):
        reg.get("nonexistent")


def test_engine_run_simple_chain(tmp_path: Path):
    from chains.engine import ChainEngine
    from chains.registry import ChainRegistry
    from chains.schemas import ChainDef, ChainStep, ManualTrigger

    reg = ChainRegistry()
    chain = ChainDef(
        name="simple",
        trigger=ManualTrigger(),
        steps=[
            ChainStep(agent="echo", output_key="result"),
        ],
    )
    reg.register(chain)

    # Mock agent executor: just returns a dict
    def mock_executor(agent_name: str, input_data: dict | None) -> dict:
        return {"agent": agent_name, "echo": "hello"}

    engine = ChainEngine(
        registry=reg,
        agent_executor=mock_executor,
        runs_dir=tmp_path / "runs",
    )
    run = engine.run("simple")
    assert run.status == "completed"
    assert run.steps_completed == 1
    assert run.disposition == "PENDING"  # No trust enforcer wired yet


def test_engine_gate_blocks_chain(tmp_path: Path):
    from chains.engine import ChainEngine
    from chains.registry import ChainRegistry
    from chains.schemas import ChainDef, ChainStep, ManualTrigger

    reg = ChainRegistry()
    chain = ChainDef(
        name="gated",
        trigger=ManualTrigger(),
        steps=[
            ChainStep(agent="scout", output_key="signals"),
            ChainStep(agent="sentinel-health", input_key="signals", output_key="cleared", gate=True),
            ChainStep(agent="herald", input_key="cleared", output_key="drafts"),
        ],
    )
    reg.register(chain)

    call_count = 0

    def mock_executor(agent_name: str, input_data: dict | None) -> dict:
        nonlocal call_count
        call_count += 1
        if agent_name == "sentinel-health":
            return {"disposition": "BLOCK", "reason": "PHI detected"}
        return {"data": f"output from {agent_name}"}

    engine = ChainEngine(
        registry=reg,
        agent_executor=mock_executor,
        runs_dir=tmp_path / "runs",
    )
    run = engine.run("gated")
    assert run.status == "blocked"
    assert run.steps_completed == 2  # scout + sentinel ran, herald skipped
    assert call_count == 2  # herald was never called


def test_engine_saves_audit_log(tmp_path: Path):
    from chains.engine import ChainEngine
    from chains.registry import ChainRegistry
    from chains.schemas import ChainDef, ChainStep, ManualTrigger

    reg = ChainRegistry()
    chain = ChainDef(
        name="audited",
        trigger=ManualTrigger(),
        steps=[ChainStep(agent="scout", output_key="signals")],
    )
    reg.register(chain)

    def mock_executor(agent_name: str, input_data: dict | None) -> dict:
        return {"data": "test"}

    runs_dir = tmp_path / "runs"
    engine = ChainEngine(registry=reg, agent_executor=mock_executor, runs_dir=runs_dir)
    engine.run("audited")

    # Check audit log exists
    log_files = list(runs_dir.glob("*.jsonl"))
    assert len(log_files) == 1
    lines = log_files[0].read_text().strip().split("\n")
    record = json.loads(lines[0])
    assert record["chain_name"] == "audited"
    assert record["status"] == "completed"
