"""Tests for chains module Pydantic schemas."""
from datetime import datetime

import pytest


def test_chain_step_basic():
    from chains.schemas import ChainStep

    step = ChainStep(agent="scout", output_key="signals")
    assert step.agent == "scout"
    assert step.output_key == "signals"
    assert step.input_key is None
    assert step.gate is False


def test_chain_step_with_gate():
    from chains.schemas import ChainStep

    step = ChainStep(
        agent="sentinel-health",
        input_key="drafts",
        output_key="cleared",
        gate=True,
    )
    assert step.gate is True
    assert step.input_key == "drafts"


def test_chain_def_basic():
    from chains.schemas import ChainDef, ChainStep, ManualTrigger

    chain = ChainDef(
        name="test-chain",
        trigger=ManualTrigger(),
        autonomy="MANUAL",
        steps=[
            ChainStep(agent="scout", output_key="signals"),
            ChainStep(agent="herald", input_key="signals", output_key="drafts"),
        ],
    )
    assert chain.name == "test-chain"
    assert len(chain.steps) == 2
    assert chain.autonomy == "MANUAL"


def test_signal_trigger():
    from chains.schemas import SignalTrigger

    trigger = SignalTrigger(min_score=80, signal_types=["competitor_move"])
    assert trigger.kind == "signal"
    assert trigger.min_score == 80


def test_scheduled_trigger():
    from chains.schemas import ScheduledTrigger

    trigger = ScheduledTrigger(cron="0 6 * * *")
    assert trigger.kind == "scheduled"
    assert trigger.cron == "0 6 * * *"


def test_chain_run_result():
    from chains.schemas import ChainRun

    run = ChainRun(
        chain_name="competitive-response",
        status="completed",
        steps_completed=3,
        steps_total=3,
    )
    assert run.chain_name == "competitive-response"
    assert run.status == "completed"
    assert run.id.startswith("run-")


def test_chain_run_auto_id():
    from chains.schemas import ChainRun

    run1 = ChainRun(chain_name="test", status="running", steps_completed=0, steps_total=2)
    run2 = ChainRun(chain_name="test", status="running", steps_completed=0, steps_total=2)
    # IDs should differ (timestamp-based)
    assert run1.id != run2.id


def test_gate_result():
    from chains.schemas import GateResult

    gate = GateResult(agent="sentinel-health", disposition="CLEAR")
    assert gate.disposition == "CLEAR"

    gate_block = GateResult(agent="sentinel-health", disposition="BLOCK", reason="PHI detected")
    assert gate_block.reason == "PHI detected"
