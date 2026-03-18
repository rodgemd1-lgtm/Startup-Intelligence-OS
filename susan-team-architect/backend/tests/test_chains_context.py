"""Tests for the chain context bus (data passing between steps)."""
import pytest


def test_context_set_get():
    from chains.context import ChainContext

    ctx = ChainContext()
    ctx.set("signals", {"p0": ["Epic launched Agent Factory"]})
    assert ctx.get("signals") == {"p0": ["Epic launched Agent Factory"]}


def test_context_get_missing_returns_none():
    from chains.context import ChainContext

    ctx = ChainContext()
    assert ctx.get("nonexistent") is None


def test_context_get_missing_with_default():
    from chains.context import ChainContext

    ctx = ChainContext()
    assert ctx.get("nonexistent", "fallback") == "fallback"


def test_context_keys():
    from chains.context import ChainContext

    ctx = ChainContext()
    ctx.set("signals", [1, 2])
    ctx.set("drafts", [3, 4])
    assert set(ctx.keys()) == {"signals", "drafts"}


def test_context_to_dict():
    from chains.context import ChainContext

    ctx = ChainContext()
    ctx.set("signals", "data")
    snapshot = ctx.to_dict()
    assert snapshot == {"signals": "data"}
    # Snapshot should be a copy
    snapshot["signals"] = "modified"
    assert ctx.get("signals") == "data"


def test_context_metadata():
    from chains.context import ChainContext

    ctx = ChainContext(chain_name="competitive-response", trigger_source="birch-tier1")
    assert ctx.chain_name == "competitive-response"
    assert ctx.trigger_source == "birch-tier1"
