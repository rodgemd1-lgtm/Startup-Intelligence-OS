"""V4a Integration Test — Birch → Chains → Trust end-to-end flow."""
from pathlib import Path

import pytest


def test_birch_to_chains_to_trust(tmp_path: Path):
    """End-to-end: score a signal with Birch, run a chain, enforce trust."""
    from birch.scorer import BirchScorer
    from birch.schemas import RawSignal
    from birch.rubric import Rubric, CompanyRubric
    from birch.writer import SignalWriter
    from chains.engine import ChainEngine
    from chains.registry import ChainRegistry
    from chains.schemas import ChainDef, ChainStep, ManualTrigger
    from trust.tracker import TrustTracker
    from trust.enforcer import TrustEnforcer

    # --- Birch: score a signal ---
    rubric = Rubric(companies={
        "oracle-health": CompanyRubric(
            keywords=["epic", "ehr", "himss", "clinical ai"],
            competitors=["epic", "meditech"],
        ),
    })
    scorer = BirchScorer(rubric=rubric)
    signals_dir = tmp_path / "signals"
    writer = SignalWriter(signals_dir=signals_dir)

    raw = RawSignal(
        source="manual",
        title="Epic launches Agent Factory at HIMSS",
        content="Epic announces no-code AI agent builder with clinical outcomes data",
    )
    scored = scorer.score(raw)
    writer.append(scored)
    assert scored.tier in (1, 2)  # Should be high relevance

    # --- Chains: run competitive response ---
    reg = ChainRegistry()
    chain = ChainDef(
        name="competitive-response",
        trigger=ManualTrigger(),
        autonomy="SUPERVISED",
        steps=[
            ChainStep(agent="scout", output_key="signals"),
            ChainStep(agent="herald", input_key="signals", output_key="drafts"),
            ChainStep(agent="sentinel-health", input_key="drafts", output_key="cleared", gate=True),
        ],
    )
    reg.register(chain)

    def mock_executor(agent_name: str, input_data):
        if agent_name == "sentinel-health":
            return {"disposition": "CLEAR", "reason": "No issues"}
        return {"data": f"output from {agent_name}"}

    runs_dir = tmp_path / "runs"
    engine = ChainEngine(registry=reg, agent_executor=mock_executor, runs_dir=runs_dir)
    run = engine.run("competitive-response", trigger_source="birch-tier1")
    assert run.status == "completed"

    # --- Trust: enforce disposition ---
    trust_dir = tmp_path / "trust"
    tracker = TrustTracker(data_dir=trust_dir)
    enforcer = TrustEnforcer(tracker=tracker)
    disposition = enforcer.check("competitive-response")
    assert disposition == "STAGE"  # MANUAL level = stage for review

    # Record the outcome
    tracker.record_outcome("competitive-response", success=True)
    tracker.save()

    # Verify persistence
    tracker2 = TrustTracker(data_dir=trust_dir)
    tracker2.load()
    profile = tracker2.get_profile("competitive-response")
    assert profile.total_runs == 1
    assert profile.successful_runs == 1
