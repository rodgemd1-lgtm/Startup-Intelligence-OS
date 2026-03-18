# V4a — Semi-Autonomous Foundation: Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build three standalone Python modules (`chains/`, `birch/`, `trust/`) with CLI interfaces, Pydantic schemas, and tests — all runnable independently before wiring in V4b.

**Architecture:** Three new sibling modules alongside existing `research_daemon/`, `self_improvement/`, `collective/` inside `susan-team-architect/backend/`. Each follows the same pattern: `schemas.py` (Pydantic models), core logic, `__main__.py` (CLI), tests. File-based communication via `.startup-os/signals/` and `.startup-os/runs/chains/`.

**Tech Stack:** Python 3.11+, Pydantic v2, aiohttp (Firehose SSE), argparse (CLI), pytest (tests). No new dependencies except `aiohttp` for SSE.

---

## Task 1: Chains Module — Schemas

**Files:**
- Create: `susan-team-architect/backend/chains/__init__.py`
- Create: `susan-team-architect/backend/chains/schemas.py`
- Test: `susan-team-architect/backend/tests/test_chains_schemas.py`

**Step 1: Write the failing test**

```python
# tests/test_chains_schemas.py
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
```

**Step 2: Run test to verify it fails**

Run: `cd susan-team-architect/backend && python -m pytest tests/test_chains_schemas.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'chains'`

**Step 3: Write the module**

```python
# chains/__init__.py
"""Chains — Sequential multi-agent workflow engine for Startup Intelligence OS."""

# chains/schemas.py
"""Pydantic V2 models for the Chains engine."""
from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_id() -> str:
    return f"run-{uuid.uuid4().hex[:12]}"


# --- Triggers ---

class ManualTrigger(BaseModel):
    kind: Literal["manual"] = "manual"


class SignalTrigger(BaseModel):
    kind: Literal["signal"] = "signal"
    min_score: int = Field(ge=0, le=100, default=80)
    signal_types: list[str] = Field(default_factory=list)


class ScheduledTrigger(BaseModel):
    kind: Literal["scheduled"] = "scheduled"
    cron: str = Field(..., description="Cron expression for scheduling")


class FileWatchTrigger(BaseModel):
    kind: Literal["file_watch"] = "file_watch"
    watch_path: str = Field(..., description="Path to watch for changes")


TriggerType = ManualTrigger | SignalTrigger | ScheduledTrigger | FileWatchTrigger


# --- Chain Definition ---

class ChainStep(BaseModel):
    agent: str = Field(..., description="Agent name to invoke (e.g., 'scout', 'herald')")
    input_key: Optional[str] = Field(default=None, description="Key to read from context bus")
    output_key: str = Field(..., description="Key to write result to context bus")
    gate: bool = Field(default=False, description="If True, step can halt the chain")
    timeout_seconds: int = Field(default=300, description="Max seconds for this step")


class ChainDef(BaseModel):
    name: str = Field(..., description="Unique chain identifier (kebab-case)")
    description: str = Field(default="", description="Human-readable description")
    trigger: TriggerType = Field(..., description="What triggers this chain")
    autonomy: Literal["MANUAL", "SUPERVISED", "AUTONOMOUS"] = Field(default="MANUAL")
    steps: list[ChainStep] = Field(..., min_length=1, description="Ordered steps to execute")


# --- Runtime Models ---

class GateResult(BaseModel):
    agent: str
    disposition: Literal["CLEAR", "REVIEW", "BLOCK"]
    reason: str = ""
    timestamp: str = Field(default_factory=_now_iso)


class StepResult(BaseModel):
    agent: str
    output_key: str
    status: Literal["completed", "failed", "blocked", "skipped"] = "completed"
    gate_result: Optional[GateResult] = None
    duration_ms: int = 0
    timestamp: str = Field(default_factory=_now_iso)


class ChainRun(BaseModel):
    id: str = Field(default_factory=_run_id)
    chain_name: str
    status: Literal["running", "completed", "failed", "blocked", "halted"] = "running"
    steps_completed: int = 0
    steps_total: int = 0
    step_results: list[StepResult] = Field(default_factory=list)
    trigger_source: str = ""
    started_at: str = Field(default_factory=_now_iso)
    finished_at: Optional[str] = None
    disposition: Literal["PUBLISH", "STAGE", "BLOCK", "PENDING"] = "PENDING"
```

**Step 4: Run test to verify it passes**

Run: `cd susan-team-architect/backend && python -m pytest tests/test_chains_schemas.py -v`
Expected: All 8 tests PASS

**Step 5: Commit**

```bash
git add susan-team-architect/backend/chains/ susan-team-architect/backend/tests/test_chains_schemas.py
git commit -m "feat(chains): add Pydantic schemas for chain engine — steps, triggers, runs"
```

---

## Task 2: Chains Module — Context Bus

**Files:**
- Create: `susan-team-architect/backend/chains/context.py`
- Test: `susan-team-architect/backend/tests/test_chains_context.py`

**Step 1: Write the failing test**

```python
# tests/test_chains_context.py
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
```

**Step 2: Run test to verify it fails**

Run: `cd susan-team-architect/backend && python -m pytest tests/test_chains_context.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# chains/context.py
"""Chain Context Bus — shared state passed between chain steps."""
from __future__ import annotations

from typing import Any


class ChainContext:
    """In-memory key-value store for passing data between chain steps.

    Each step writes its output under a named key. The next step reads
    the previous step's output by key. No file I/O between steps.
    """

    def __init__(self, chain_name: str = "", trigger_source: str = "") -> None:
        self.chain_name = chain_name
        self.trigger_source = trigger_source
        self._store: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def keys(self) -> list[str]:
        return list(self._store.keys())

    def to_dict(self) -> dict[str, Any]:
        return dict(self._store)
```

**Step 4: Run test to verify it passes**

Run: `cd susan-team-architect/backend && python -m pytest tests/test_chains_context.py -v`
Expected: All 6 tests PASS

**Step 5: Commit**

```bash
git add susan-team-architect/backend/chains/context.py susan-team-architect/backend/tests/test_chains_context.py
git commit -m "feat(chains): add context bus for inter-step data passing"
```

---

## Task 3: Chains Module — Engine + Registry

**Files:**
- Create: `susan-team-architect/backend/chains/registry.py`
- Create: `susan-team-architect/backend/chains/engine.py`
- Test: `susan-team-architect/backend/tests/test_chains_engine.py`

**Step 1: Write the failing test**

```python
# tests/test_chains_engine.py
"""Tests for chain engine and registry."""
import json
from pathlib import Path

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
```

**Step 2: Run test to verify it fails**

Run: `cd susan-team-architect/backend && python -m pytest tests/test_chains_engine.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# chains/registry.py
"""Chain Registry — stores and retrieves chain definitions."""
from __future__ import annotations

from chains.schemas import ChainDef


class ChainRegistry:
    def __init__(self) -> None:
        self._chains: dict[str, ChainDef] = {}

    def register(self, chain: ChainDef) -> None:
        self._chains[chain.name] = chain

    def get(self, name: str) -> ChainDef:
        if name not in self._chains:
            raise KeyError(f"Chain '{name}' not found. Available: {list(self._chains.keys())}")
        return self._chains[name]

    def list_names(self) -> list[str]:
        return list(self._chains.keys())
```

```python
# chains/engine.py
"""Chain Engine — executes multi-step agent workflows with gates and audit logging."""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

from chains.context import ChainContext
from chains.registry import ChainRegistry
from chains.schemas import ChainRun, GateResult, StepResult


AgentExecutor = Callable[[str, Optional[dict]], dict]


class ChainEngine:
    def __init__(
        self,
        registry: ChainRegistry,
        agent_executor: AgentExecutor,
        runs_dir: Path,
    ) -> None:
        self._registry = registry
        self._executor = agent_executor
        self._runs_dir = runs_dir

    def run(self, chain_name: str, trigger_source: str = "manual") -> ChainRun:
        chain_def = self._registry.get(chain_name)
        ctx = ChainContext(chain_name=chain_name, trigger_source=trigger_source)

        run = ChainRun(
            chain_name=chain_name,
            status="running",
            steps_total=len(chain_def.steps),
            trigger_source=trigger_source,
        )

        for step in chain_def.steps:
            start = time.monotonic()
            input_data = ctx.get(step.input_key) if step.input_key else None

            try:
                result = self._executor(step.agent, input_data)
            except Exception as exc:
                run.status = "failed"
                run.step_results.append(StepResult(
                    agent=step.agent,
                    output_key=step.output_key,
                    status="failed",
                    duration_ms=int((time.monotonic() - start) * 1000),
                ))
                break

            duration_ms = int((time.monotonic() - start) * 1000)
            ctx.set(step.output_key, result)
            run.steps_completed += 1

            # Check gate
            gate_result = None
            if step.gate and isinstance(result, dict) and "disposition" in result:
                gate_result = GateResult(
                    agent=step.agent,
                    disposition=result["disposition"],
                    reason=result.get("reason", ""),
                )
                if gate_result.disposition == "BLOCK":
                    run.status = "blocked"
                    run.step_results.append(StepResult(
                        agent=step.agent,
                        output_key=step.output_key,
                        status="blocked",
                        gate_result=gate_result,
                        duration_ms=duration_ms,
                    ))
                    break

            run.step_results.append(StepResult(
                agent=step.agent,
                output_key=step.output_key,
                status="completed",
                gate_result=gate_result,
                duration_ms=duration_ms,
            ))

        if run.status == "running":
            run.status = "completed"

        run.finished_at = datetime.now(timezone.utc).isoformat()
        self._save_audit(run)
        return run

    def _save_audit(self, run: ChainRun) -> None:
        self._runs_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_path = self._runs_dir / f"chains-{date_str}.jsonl"
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(run.model_dump_json() + "\n")
```

**Step 4: Run test to verify it passes**

Run: `cd susan-team-architect/backend && python -m pytest tests/test_chains_engine.py -v`
Expected: All 6 tests PASS

**Step 5: Commit**

```bash
git add susan-team-architect/backend/chains/registry.py susan-team-architect/backend/chains/engine.py susan-team-architect/backend/tests/test_chains_engine.py
git commit -m "feat(chains): add engine with gate support and JSONL audit logging"
```

---

## Task 4: Chains Module — CLI + Chain Definitions

**Files:**
- Create: `susan-team-architect/backend/chains/__main__.py`
- Create: `susan-team-architect/backend/chains/chains/` (chain defs directory)
- Create: `susan-team-architect/backend/chains/chains/__init__.py`
- Create: `susan-team-architect/backend/chains/chains/competitive_response.py`
- Create: `susan-team-architect/backend/chains/chains/daily_cycle.py`
- Test: `susan-team-architect/backend/tests/test_chains_cli.py`

**Step 1: Write the failing test**

```python
# tests/test_chains_cli.py
"""Tests for chains CLI entry point."""
import subprocess
import sys

import pytest


def test_chains_list():
    result = subprocess.run(
        [sys.executable, "-m", "chains", "--command", "list"],
        capture_output=True,
        text=True,
        cwd="susan-team-architect/backend" if __name__ != "__main__" else ".",
    )
    assert result.returncode == 0
    assert "competitive-response" in result.stdout
    assert "daily-cycle" in result.stdout


def test_chains_help():
    result = subprocess.run(
        [sys.executable, "-m", "chains", "--help"],
        capture_output=True,
        text=True,
        cwd="susan-team-architect/backend" if __name__ != "__main__" else ".",
    )
    assert result.returncode == 0
    assert "chains" in result.stdout.lower()
```

**Step 2: Run test to verify it fails**

Run: `cd susan-team-architect/backend && python -m pytest tests/test_chains_cli.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# chains/chains/__init__.py
"""Built-in chain definitions."""

# chains/chains/competitive_response.py
"""Competitive Response Chain: SCOUT → HERALD → SENTINEL-HEALTH."""
from chains.schemas import ChainDef, ChainStep, SignalTrigger

competitive_response = ChainDef(
    name="competitive-response",
    description="Detect competitive signals, draft response, compliance check",
    trigger=SignalTrigger(min_score=80, signal_types=["competitor_move"]),
    autonomy="SUPERVISED",
    steps=[
        ChainStep(agent="scout", output_key="signals"),
        ChainStep(agent="herald", input_key="signals", output_key="drafts"),
        ChainStep(
            agent="sentinel-health",
            input_key="drafts",
            output_key="cleared",
            gate=True,
        ),
    ],
)

# chains/chains/daily_cycle.py
"""Daily Cycle Chain: SCOUT → ARIA digest assembly."""
from chains.schemas import ChainDef, ChainStep, ScheduledTrigger

daily_cycle = ChainDef(
    name="daily-cycle",
    description="Morning intelligence cycle: scan signals, assemble daily brief",
    trigger=ScheduledTrigger(cron="0 6 * * *"),
    autonomy="MANUAL",  # starts MANUAL, graduates to AUTONOMOUS
    steps=[
        ChainStep(agent="scout", output_key="signals"),
        ChainStep(agent="aria", input_key="signals", output_key="brief"),
    ],
)
```

```python
# chains/__main__.py
"""CLI entry point for the Chains engine.

Usage:
    python -m chains --command list
    python -m chains --command run --chain competitive-response
    python -m chains --command status
    python -m chains --command history --chain competitive-response
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _find_repo_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / ".startup-os").is_dir():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return Path(__file__).resolve().parent.parent.parent.parent


def _build_registry():
    from chains.registry import ChainRegistry
    from chains.chains.competitive_response import competitive_response
    from chains.chains.daily_cycle import daily_cycle

    reg = ChainRegistry()
    reg.register(competitive_response)
    reg.register(daily_cycle)
    return reg


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="chains",
        description="V4 Chain Engine — Sequential multi-agent workflows",
    )
    parser.add_argument(
        "--command",
        choices=["list", "run", "status", "history", "halt"],
        required=True,
        help="Command to execute.",
    )
    parser.add_argument(
        "--chain",
        type=str,
        default="",
        help="Chain name (required for run/history/halt).",
    )

    args = parser.parse_args()
    repo_root = _find_repo_root()
    runs_dir = repo_root / ".startup-os" / "runs" / "chains"

    if args.command == "list":
        reg = _build_registry()
        print("Registered Chains")
        print("=" * 60)
        for name in sorted(reg.list_names()):
            chain = reg.get(name)
            print(f"  {name:<30s} [{chain.autonomy}] {chain.description}")

    elif args.command == "run":
        if not args.chain:
            print("Error: --chain required for run command", file=sys.stderr)
            sys.exit(1)

        reg = _build_registry()

        # Placeholder executor — V4b will wire real agent dispatch
        def placeholder_executor(agent_name: str, input_data: dict | None) -> dict:
            print(f"  [PLACEHOLDER] Would invoke agent: {agent_name}")
            return {"placeholder": True, "agent": agent_name}

        from chains.engine import ChainEngine

        engine = ChainEngine(registry=reg, agent_executor=placeholder_executor, runs_dir=runs_dir)
        print(f"Running chain: {args.chain}")
        run = engine.run(args.chain)
        print(f"  Status: {run.status}")
        print(f"  Steps: {run.steps_completed}/{run.steps_total}")
        print(f"  Run ID: {run.id}")
        print(f"  Audit log: {runs_dir}/")

    elif args.command == "status":
        runs_dir.mkdir(parents=True, exist_ok=True)
        log_files = sorted(runs_dir.glob("chains-*.jsonl"), reverse=True)
        if not log_files:
            print("No chain runs recorded yet.")
            return

        print("Recent Chain Runs")
        print("=" * 60)
        for log_file in log_files[:3]:
            lines = log_file.read_text().strip().split("\n")
            for line in lines[-5:]:
                record = json.loads(line)
                print(
                    f"  {record['id']:<20s} {record['chain_name']:<25s} "
                    f"{record['status']:<12s} {record.get('started_at', '')[:19]}"
                )

    elif args.command == "history":
        if not args.chain:
            print("Error: --chain required for history command", file=sys.stderr)
            sys.exit(1)

        runs_dir.mkdir(parents=True, exist_ok=True)
        log_files = sorted(runs_dir.glob("chains-*.jsonl"), reverse=True)
        print(f"History for: {args.chain}")
        print("=" * 60)
        found = 0
        for log_file in log_files:
            for line in log_file.read_text().strip().split("\n"):
                if not line:
                    continue
                record = json.loads(line)
                if record["chain_name"] == args.chain:
                    found += 1
                    print(
                        f"  {record['id']:<20s} {record['status']:<12s} "
                        f"steps={record['steps_completed']}/{record['steps_total']} "
                        f"{record.get('started_at', '')[:19]}"
                    )
        if not found:
            print(f"  No runs found for '{args.chain}'")

    elif args.command == "halt":
        if not args.chain:
            print("Error: --chain required for halt command", file=sys.stderr)
            sys.exit(1)
        # V4c will implement real halt — for now, write a halt marker
        halt_file = runs_dir / f"HALT-{args.chain}"
        halt_file.parent.mkdir(parents=True, exist_ok=True)
        halt_file.write_text(f"Halted at {__import__('datetime').datetime.now().isoformat()}\n")
        print(f"HALT marker written for chain: {args.chain}")
        print(f"  File: {halt_file}")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Step 4: Run test to verify it passes**

Run: `cd susan-team-architect/backend && python -m pytest tests/test_chains_cli.py -v`
Expected: All 2 tests PASS

**Step 5: Commit**

```bash
git add susan-team-architect/backend/chains/__main__.py susan-team-architect/backend/chains/chains/ susan-team-architect/backend/tests/test_chains_cli.py
git commit -m "feat(chains): add CLI and built-in chain definitions (competitive-response, daily-cycle)"
```

---

## Task 5: Birch Module — Schemas + Scorer

**Files:**
- Create: `susan-team-architect/backend/birch/__init__.py`
- Create: `susan-team-architect/backend/birch/schemas.py`
- Create: `susan-team-architect/backend/birch/rubric.py`
- Create: `susan-team-architect/backend/birch/scorer.py`
- Test: `susan-team-architect/backend/tests/test_birch_scorer.py`

**Step 1: Write the failing test**

```python
# tests/test_birch_scorer.py
"""Tests for Birch signal scoring engine."""
import pytest


def test_raw_signal_creation():
    from birch.schemas import RawSignal

    sig = RawSignal(
        source="firehose",
        title="Epic launches Agent Factory",
        content="Epic Systems announced...",
    )
    assert sig.source == "firehose"
    assert sig.id.startswith("sig-")


def test_scored_signal_tier_1():
    from birch.schemas import ScoredSignal

    sig = ScoredSignal(
        source="firehose",
        title="Epic Agent Factory",
        content="...",
        relevance=92,
        actionability=85,
        urgency=80,
        score=87,
        tier=1,
        company="oracle-health",
    )
    assert sig.tier == 1
    assert sig.score == 87


def test_scorer_high_relevance():
    from birch.scorer import BirchScorer
    from birch.schemas import RawSignal
    from birch.rubric import Rubric, CompanyRubric

    rubric = Rubric(companies={
        "oracle-health": CompanyRubric(
            keywords=["epic", "ehr", "himss", "clinical ai", "oracle health"],
            competitors=["epic", "meditech", "athenahealth", "cerner"],
        ),
    })
    scorer = BirchScorer(rubric=rubric)
    raw = RawSignal(
        source="firehose",
        title="Epic launches Agent Factory at HIMSS",
        content="Epic Systems announced Agent Factory, a no-code AI agent builder for healthcare",
    )
    scored = scorer.score(raw)
    assert scored.score >= 70  # High relevance to Oracle Health
    assert scored.tier in (1, 2)
    assert scored.company == "oracle-health"


def test_scorer_low_relevance():
    from birch.scorer import BirchScorer
    from birch.schemas import RawSignal
    from birch.rubric import Rubric, CompanyRubric

    rubric = Rubric(companies={
        "oracle-health": CompanyRubric(
            keywords=["epic", "ehr", "clinical ai"],
            competitors=["epic", "meditech"],
        ),
    })
    scorer = BirchScorer(rubric=rubric)
    raw = RawSignal(
        source="firehose",
        title="Tesla announces new factory in Austin",
        content="Tesla will build a new manufacturing facility...",
    )
    scored = scorer.score(raw)
    assert scored.score < 50
    assert scored.tier == 3


def test_scorer_tier_classification():
    from birch.scorer import BirchScorer

    assert BirchScorer.classify_tier(85) == 1
    assert BirchScorer.classify_tier(65) == 2
    assert BirchScorer.classify_tier(30) == 3
    assert BirchScorer.classify_tier(80) == 1
    assert BirchScorer.classify_tier(50) == 2
    assert BirchScorer.classify_tier(49) == 3
```

**Step 2: Run test to verify it fails**

Run: `cd susan-team-architect/backend && python -m pytest tests/test_birch_scorer.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# birch/__init__.py
"""Birch — Real-time signal scoring and routing for Startup Intelligence OS."""

# birch/schemas.py
"""Pydantic V2 models for Birch signal scoring."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sig_id() -> str:
    return f"sig-{uuid.uuid4().hex[:12]}"


class RawSignal(BaseModel):
    id: str = Field(default_factory=_sig_id)
    source: Literal["firehose", "trendradar", "morning_intel", "manual"] = "manual"
    title: str
    content: str = ""
    url: str = ""
    published_at: str = Field(default_factory=_now_iso)
    metadata: dict = Field(default_factory=dict)


class ScoredSignal(BaseModel):
    id: str = Field(default_factory=_sig_id)
    source: str
    title: str
    content: str = ""
    url: str = ""
    relevance: int = Field(ge=0, le=100, default=0)
    actionability: int = Field(ge=0, le=100, default=0)
    urgency: int = Field(ge=0, le=100, default=0)
    score: int = Field(ge=0, le=100, default=0)
    tier: Literal[1, 2, 3] = 3
    company: str = ""
    routed_to: str = ""
    scored_at: str = Field(default_factory=_now_iso)


# birch/rubric.py
"""Scoring rubric definitions — configurable per company/domain."""
from __future__ import annotations

from pydantic import BaseModel, Field


class CompanyRubric(BaseModel):
    keywords: list[str] = Field(default_factory=list)
    competitors: list[str] = Field(default_factory=list)
    action_patterns: list[str] = Field(
        default_factory=lambda: ["launch", "announce", "acquire", "partner", "hire", "raise"],
    )


class Rubric(BaseModel):
    companies: dict[str, CompanyRubric] = Field(default_factory=dict)


# birch/scorer.py
"""Birch scoring engine — 3-axis composite scoring."""
from __future__ import annotations

import re
from typing import Literal

from birch.schemas import RawSignal, ScoredSignal
from birch.rubric import Rubric


class BirchScorer:
    RELEVANCE_WEIGHT = 0.40
    ACTIONABILITY_WEIGHT = 0.35
    URGENCY_WEIGHT = 0.25

    def __init__(self, rubric: Rubric) -> None:
        self._rubric = rubric

    def score(self, raw: RawSignal) -> ScoredSignal:
        best_company = ""
        best_relevance = 0

        text = f"{raw.title} {raw.content}".lower()

        for company, company_rubric in self._rubric.companies.items():
            relevance = self._score_relevance(text, company_rubric)
            if relevance > best_relevance:
                best_relevance = relevance
                best_company = company

        actionability = self._score_actionability(text, best_company)
        urgency = self._score_urgency(raw)

        composite = int(
            best_relevance * self.RELEVANCE_WEIGHT
            + actionability * self.ACTIONABILITY_WEIGHT
            + urgency * self.URGENCY_WEIGHT
        )
        composite = max(0, min(100, composite))
        tier = self.classify_tier(composite)

        routed_to = ""
        if tier == 1 and best_company:
            routed_to = "competitive-response"

        return ScoredSignal(
            source=raw.source,
            title=raw.title,
            content=raw.content,
            url=raw.url,
            relevance=best_relevance,
            actionability=actionability,
            urgency=urgency,
            score=composite,
            tier=tier,
            company=best_company,
            routed_to=routed_to,
        )

    def _score_relevance(self, text: str, rubric) -> int:
        keyword_hits = sum(1 for kw in rubric.keywords if kw.lower() in text)
        competitor_hits = sum(1 for c in rubric.competitors if c.lower() in text)
        total_possible = len(rubric.keywords) + len(rubric.competitors)
        if total_possible == 0:
            return 0
        hit_ratio = (keyword_hits + competitor_hits * 2) / (total_possible + len(rubric.competitors))
        return max(0, min(100, int(hit_ratio * 100)))

    def _score_actionability(self, text: str, company: str) -> int:
        if not company:
            return 20
        rubric = self._rubric.companies.get(company)
        if not rubric:
            return 20
        action_hits = sum(1 for p in rubric.action_patterns if p.lower() in text)
        return max(20, min(100, 30 + action_hits * 15))

    def _score_urgency(self, raw: RawSignal) -> int:
        text = f"{raw.title} {raw.content}".lower()
        urgency_words = ["breaking", "just", "today", "announces", "launches", "immediate"]
        hits = sum(1 for w in urgency_words if w in text)
        return max(20, min(100, 30 + hits * 15))

    @staticmethod
    def classify_tier(score: int) -> Literal[1, 2, 3]:
        if score >= 80:
            return 1
        elif score >= 50:
            return 2
        return 3
```

**Step 4: Run test to verify it passes**

Run: `cd susan-team-architect/backend && python -m pytest tests/test_birch_scorer.py -v`
Expected: All 5 tests PASS

**Step 5: Commit**

```bash
git add susan-team-architect/backend/birch/ susan-team-architect/backend/tests/test_birch_scorer.py
git commit -m "feat(birch): add signal scoring engine with 3-axis rubric and tier classification"
```

---

## Task 6: Birch Module — Writer + CLI

**Files:**
- Create: `susan-team-architect/backend/birch/writer.py`
- Create: `susan-team-architect/backend/birch/__main__.py`
- Test: `susan-team-architect/backend/tests/test_birch_writer.py`

**Step 1: Write the failing test**

```python
# tests/test_birch_writer.py
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
```

**Step 2: Run test to verify it fails**

Run: `cd susan-team-architect/backend && python -m pytest tests/test_birch_writer.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# birch/writer.py
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
```

```python
# birch/__main__.py
"""CLI entry point for the Birch signal scorer.

Usage:
    python -m birch --command score --file signals.json
    python -m birch --command stats
    python -m birch --command stats --days 7
    python -m birch --command listen          (V4b — Firehose SSE)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _find_repo_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / ".startup-os").is_dir():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return Path(__file__).resolve().parent.parent.parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="birch",
        description="V4 Birch Signal Scorer — Real-time signal scoring and routing",
    )
    parser.add_argument(
        "--command",
        choices=["score", "stats", "listen"],
        required=True,
        help="Command to execute.",
    )
    parser.add_argument("--file", type=str, default="", help="Input file for batch scoring.")
    parser.add_argument("--days", type=int, default=1, help="Days of history for stats.")

    args = parser.parse_args()
    repo_root = _find_repo_root()
    signals_dir = repo_root / ".startup-os" / "signals"

    if args.command == "score":
        if not args.file:
            print("Error: --file required for score command", file=sys.stderr)
            sys.exit(1)

        from birch.scorer import BirchScorer
        from birch.schemas import RawSignal
        from birch.rubric import Rubric, CompanyRubric
        from birch.writer import SignalWriter

        # Load default rubric — TODO: load from config file in V4b
        rubric = Rubric(companies={
            "oracle-health": CompanyRubric(
                keywords=["epic", "ehr", "himss", "clinical ai", "oracle health", "cerner",
                           "health it", "ehrs", "interoperability", "fhir"],
                competitors=["epic", "meditech", "athenahealth", "cerner", "microsoft nuance"],
            ),
            "transformfit": CompanyRubric(
                keywords=["fitness app", "ai coaching", "workout", "personal trainer",
                           "health tech", "wearable"],
                competitors=["peloton", "fitbod", "future", "caliber", "trainiac"],
            ),
            "alex-recruiting": CompanyRubric(
                keywords=["college recruiting", "athletic recruiting", "ncaa", "nil"],
                competitors=["fieldlevel", "ncsa", "berecruited"],
            ),
        })

        scorer = BirchScorer(rubric=rubric)
        writer = SignalWriter(signals_dir=signals_dir)

        input_path = Path(args.file)
        signals = json.loads(input_path.read_text())
        if isinstance(signals, dict):
            signals = [signals]

        print(f"Scoring {len(signals)} signals...")
        for raw_data in signals:
            raw = RawSignal(**raw_data)
            scored = scorer.score(raw)
            writer.append(scored)
            print(f"  [{scored.tier}] {scored.score:3d} — {scored.title[:60]}")

        print(f"\nResults written to: {signals_dir}/")

    elif args.command == "stats":
        from birch.writer import SignalWriter

        writer = SignalWriter(signals_dir=signals_dir)
        stats = writer.stats(days=args.days)
        print("Birch Signal Stats")
        print("=" * 40)
        print(f"  Total signals:  {stats['total']}")
        print(f"  Tier 1 (80+):   {stats['tier_1']}")
        print(f"  Tier 2 (50-79): {stats['tier_2']}")
        print(f"  Tier 3 (<50):   {stats['tier_3']}")

    elif args.command == "listen":
        print("Firehose SSE listener — will be implemented in V4b.")
        print("For now, use: python -m birch --command score --file <signals.json>")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

**Step 4: Run test to verify it passes**

Run: `cd susan-team-architect/backend && python -m pytest tests/test_birch_writer.py -v`
Expected: All 3 tests PASS

**Step 5: Commit**

```bash
git add susan-team-architect/backend/birch/writer.py susan-team-architect/backend/birch/__main__.py susan-team-architect/backend/tests/test_birch_writer.py
git commit -m "feat(birch): add signal writer with JSONL output and CLI"
```

---

## Task 7: Trust Module — Schemas + Tracker + Config

**Files:**
- Create: `susan-team-architect/backend/trust/__init__.py`
- Create: `susan-team-architect/backend/trust/schemas.py`
- Create: `susan-team-architect/backend/trust/config.py`
- Create: `susan-team-architect/backend/trust/tracker.py`
- Test: `susan-team-architect/backend/tests/test_trust_tracker.py`

**Step 1: Write the failing test**

```python
# tests/test_trust_tracker.py
"""Tests for trust tracker — autonomy levels, run tracking, graduation."""
import pytest
from pathlib import Path


def test_trust_profile_defaults():
    from trust.schemas import TrustProfile

    profile = TrustProfile(chain_name="daily-cycle")
    assert profile.level == "MANUAL"
    assert profile.total_runs == 0
    assert profile.successful_runs == 0


def test_tracker_record_success(tmp_path: Path):
    from trust.tracker import TrustTracker

    tracker = TrustTracker(data_dir=tmp_path)
    tracker.record_outcome("daily-cycle", success=True)
    tracker.record_outcome("daily-cycle", success=True)
    tracker.record_outcome("daily-cycle", success=False)

    profile = tracker.get_profile("daily-cycle")
    assert profile.total_runs == 3
    assert profile.successful_runs == 2
    assert profile.accuracy == pytest.approx(66.67, abs=0.1)


def test_tracker_blast_radius_cap():
    from trust.config import blast_radius_cap

    assert blast_radius_cap("competitive-response") == "SUPERVISED"
    assert blast_radius_cap("executive-brief") == "SUPERVISED"
    assert blast_radius_cap("daily-cycle") is None  # no cap


def test_tracker_autonomous_eligible():
    from trust.config import is_autonomous_eligible

    assert is_autonomous_eligible("daily-cycle") is True
    assert is_autonomous_eligible("research-refresh") is True
    assert is_autonomous_eligible("competitive-response") is False


def test_tracker_persist_and_reload(tmp_path: Path):
    from trust.tracker import TrustTracker

    tracker = TrustTracker(data_dir=tmp_path)
    for _ in range(5):
        tracker.record_outcome("daily-cycle", success=True)
    tracker.save()

    tracker2 = TrustTracker(data_dir=tmp_path)
    tracker2.load()
    profile = tracker2.get_profile("daily-cycle")
    assert profile.total_runs == 5
```

**Step 2: Run test to verify it fails**

Run: `cd susan-team-architect/backend && python -m pytest tests/test_trust_tracker.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# trust/__init__.py
"""Trust — Autonomy graduation and trust dashboard for Startup Intelligence OS."""

# trust/schemas.py
"""Pydantic V2 models for the Trust system."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TrustProfile(BaseModel):
    chain_name: str
    level: Literal["MANUAL", "SUPERVISED", "AUTONOMOUS"] = "MANUAL"
    total_runs: int = 0
    successful_runs: int = 0
    blocked_runs: int = 0
    rejected_runs: int = 0
    last_run_at: str = ""
    last_promotion_at: str = ""
    last_demotion_at: str = ""

    @property
    def accuracy(self) -> float:
        if self.total_runs == 0:
            return 0.0
        return (self.successful_runs / self.total_runs) * 100

    @property
    def escalation_rate(self) -> float:
        if self.total_runs == 0:
            return 0.0
        return ((self.blocked_runs + self.rejected_runs) / self.total_runs) * 100


class GraduationEvent(BaseModel):
    chain_name: str
    from_level: str
    to_level: str
    reason: str
    timestamp: str = Field(default_factory=_now_iso)


# trust/config.py
"""Blast radius caps and graduation thresholds."""
from __future__ import annotations

from typing import Optional

# These CANNOT graduate past SUPERVISED regardless of track record
_BLAST_RADIUS_CAPS: dict[str, str] = {
    "competitive-response": "SUPERVISED",
    "executive-brief": "SUPERVISED",
    "content-publish": "SUPERVISED",
}

# These CAN reach AUTONOMOUS
_AUTONOMOUS_ELIGIBLE: list[str] = [
    "daily-cycle",
    "research-refresh",
    "freshness-audit",
    "scout-signals",
]

# Graduation thresholds
SUPERVISED_MIN_RUNS = 20
SUPERVISED_MIN_ACCURACY = 90.0
AUTONOMOUS_MIN_RUNS = 50
AUTONOMOUS_MIN_ACCURACY = 95.0
AUTONOMOUS_MAX_ESCALATION = 5.0  # percent


def blast_radius_cap(chain_name: str) -> Optional[str]:
    return _BLAST_RADIUS_CAPS.get(chain_name)


def is_autonomous_eligible(chain_name: str) -> bool:
    if chain_name in _BLAST_RADIUS_CAPS:
        return False
    return chain_name in _AUTONOMOUS_ELIGIBLE


# trust/tracker.py
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
```

**Step 4: Run test to verify it passes**

Run: `cd susan-team-architect/backend && python -m pytest tests/test_trust_tracker.py -v`
Expected: All 5 tests PASS

**Step 5: Commit**

```bash
git add susan-team-architect/backend/trust/ susan-team-architect/backend/tests/test_trust_tracker.py
git commit -m "feat(trust): add trust tracker with profiles, blast radius caps, and persistence"
```

---

## Task 8: Trust Module — Dashboard + Enforcer + CLI

**Files:**
- Create: `susan-team-architect/backend/trust/dashboard.py`
- Create: `susan-team-architect/backend/trust/enforcer.py`
- Create: `susan-team-architect/backend/trust/__main__.py`
- Test: `susan-team-architect/backend/tests/test_trust_dashboard.py`

**Step 1: Write the failing test**

```python
# tests/test_trust_dashboard.py
"""Tests for trust dashboard and enforcer."""
from pathlib import Path

import pytest


def test_enforcer_manual_chain():
    from trust.enforcer import TrustEnforcer
    from trust.tracker import TrustTracker

    tracker = TrustTracker(data_dir=Path("/tmp/trust-test-enforcer"))
    enforcer = TrustEnforcer(tracker=tracker)
    disposition = enforcer.check("daily-cycle")
    assert disposition == "STAGE"  # MANUAL = always stage


def test_enforcer_supervised_chain(tmp_path: Path):
    from trust.enforcer import TrustEnforcer
    from trust.tracker import TrustTracker

    tracker = TrustTracker(data_dir=tmp_path)
    profile = tracker.get_profile("daily-cycle")
    profile.level = "SUPERVISED"
    enforcer = TrustEnforcer(tracker=tracker)
    disposition = enforcer.check("daily-cycle")
    assert disposition == "STAGE"  # SUPERVISED = stage for review


def test_enforcer_autonomous_chain(tmp_path: Path):
    from trust.enforcer import TrustEnforcer
    from trust.tracker import TrustTracker

    tracker = TrustTracker(data_dir=tmp_path)
    profile = tracker.get_profile("daily-cycle")
    profile.level = "AUTONOMOUS"
    enforcer = TrustEnforcer(tracker=tracker)
    disposition = enforcer.check("daily-cycle")
    assert disposition == "PUBLISH"  # AUTONOMOUS = auto-publish


def test_dashboard_markdown(tmp_path: Path):
    from trust.dashboard import generate_markdown
    from trust.tracker import TrustTracker

    tracker = TrustTracker(data_dir=tmp_path)
    for _ in range(25):
        tracker.record_outcome("daily-cycle", success=True)
    for _ in range(10):
        tracker.record_outcome("competitive-response", success=True)
    tracker.record_outcome("competitive-response", success=False)

    md = generate_markdown(tracker)
    assert "daily-cycle" in md
    assert "competitive-response" in md
    assert "MANUAL" in md  # default level


def test_dashboard_cli_runs(tmp_path: Path):
    import subprocess, sys

    result = subprocess.run(
        [sys.executable, "-m", "trust", "--command", "dashboard"],
        capture_output=True,
        text=True,
        cwd="susan-team-architect/backend" if __name__ != "__main__" else ".",
    )
    assert result.returncode == 0
    assert "Trust Dashboard" in result.stdout
```

**Step 2: Run test to verify it fails**

Run: `cd susan-team-architect/backend && python -m pytest tests/test_trust_dashboard.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# trust/enforcer.py
"""Trust Enforcer — checks autonomy level before publishing chain output."""
from __future__ import annotations

from typing import Literal

from trust.tracker import TrustTracker


class TrustEnforcer:
    def __init__(self, tracker: TrustTracker) -> None:
        self._tracker = tracker

    def check(self, chain_name: str) -> Literal["PUBLISH", "STAGE", "BLOCK"]:
        profile = self._tracker.get_profile(chain_name)
        if profile.level == "AUTONOMOUS":
            return "PUBLISH"
        return "STAGE"  # MANUAL and SUPERVISED both stage for human review


# trust/dashboard.py
"""Trust Dashboard — CLI table and markdown report."""
from __future__ import annotations

from datetime import datetime, timezone

from trust import config
from trust.tracker import TrustTracker


def generate_cli_table(tracker: TrustTracker) -> str:
    profiles = tracker.all_profiles()
    if not profiles:
        return "No chain trust profiles recorded yet."

    header = f"{'Chain':<25s} {'Level':<12s} {'Runs':<8s} {'Accuracy':<10s} {'Last Run':<20s}"
    sep = "=" * len(header)
    lines = [
        "Trust Dashboard",
        sep,
        header,
        "-" * len(header),
    ]
    for p in sorted(profiles, key=lambda x: x.chain_name):
        cap = config.blast_radius_cap(p.chain_name)
        runs_str = f"{p.total_runs}/∞" if cap else f"{p.total_runs}"
        accuracy_str = f"{p.accuracy:.1f}%" if p.total_runs > 0 else "—"
        last_run = p.last_run_at[:19] if p.last_run_at else "never"
        lines.append(f"{p.chain_name:<25s} {p.level:<12s} {runs_str:<8s} {accuracy_str:<10s} {last_run}")

    lines.append(sep)
    lines.append("  ∞ = blast radius cap, cannot graduate past SUPERVISED")
    return "\n".join(lines)


def generate_markdown(tracker: TrustTracker) -> str:
    profiles = tracker.all_profiles()
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        f"# Trust Dashboard — {date_str}",
        "",
        "| Chain | Level | Runs | Accuracy | Escalation Rate | Last Run |",
        "|-------|-------|------|----------|-----------------|----------|",
    ]
    for p in sorted(profiles, key=lambda x: x.chain_name):
        cap = config.blast_radius_cap(p.chain_name)
        runs_str = f"{p.total_runs}/∞" if cap else str(p.total_runs)
        accuracy_str = f"{p.accuracy:.1f}%" if p.total_runs > 0 else "—"
        escalation_str = f"{p.escalation_rate:.1f}%" if p.total_runs > 0 else "—"
        last_run = p.last_run_at[:19] if p.last_run_at else "never"
        lines.append(f"| {p.chain_name} | {p.level} | {runs_str} | {accuracy_str} | {escalation_str} | {last_run} |")

    lines.append("")
    lines.append("*∞ = blast radius cap, cannot graduate past SUPERVISED*")
    return "\n".join(lines)


# trust/__main__.py
"""CLI entry point for the Trust system.

Usage:
    python -m trust --command dashboard
    python -m trust --command report
    python -m trust --command promote --chain daily-cycle
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _find_repo_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / ".startup-os").is_dir():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return Path(__file__).resolve().parent.parent.parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="trust",
        description="V4 Trust System — Autonomy graduation and dashboard",
    )
    parser.add_argument(
        "--command",
        choices=["dashboard", "report", "promote", "demote"],
        required=True,
    )
    parser.add_argument("--chain", type=str, default="")

    args = parser.parse_args()
    repo_root = _find_repo_root()
    trust_dir = repo_root / ".startup-os" / "runs" / "trust"
    briefs_dir = repo_root / ".startup-os" / "briefs"

    from trust.tracker import TrustTracker
    from trust.dashboard import generate_cli_table, generate_markdown

    tracker = TrustTracker(data_dir=trust_dir)
    tracker.load()

    if args.command == "dashboard":
        print(generate_cli_table(tracker))

    elif args.command == "report":
        briefs_dir.mkdir(parents=True, exist_ok=True)
        from datetime import datetime, timezone
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        report_path = briefs_dir / f"trust-dashboard-{date_str}.md"
        md = generate_markdown(tracker)
        report_path.write_text(md, encoding="utf-8")
        print(f"Trust report saved to: {report_path}")

    elif args.command == "promote":
        if not args.chain:
            print("Error: --chain required", file=sys.stderr)
            sys.exit(1)
        from trust import config
        cap = config.blast_radius_cap(args.chain)
        profile = tracker.get_profile(args.chain)
        if profile.level == "MANUAL":
            if cap and cap == "SUPERVISED":
                profile.level = "SUPERVISED"
                print(f"Promoted {args.chain}: MANUAL → SUPERVISED (blast radius cap: cannot go higher)")
            else:
                profile.level = "SUPERVISED"
                print(f"Promoted {args.chain}: MANUAL → SUPERVISED")
        elif profile.level == "SUPERVISED":
            if cap:
                print(f"Cannot promote {args.chain} — blast radius cap at SUPERVISED")
            elif not config.is_autonomous_eligible(args.chain):
                print(f"Cannot promote {args.chain} — not in autonomous-eligible list")
            else:
                profile.level = "AUTONOMOUS"
                print(f"Promoted {args.chain}: SUPERVISED → AUTONOMOUS")
        else:
            print(f"{args.chain} is already AUTONOMOUS")
        tracker.save()

    elif args.command == "demote":
        if not args.chain:
            print("Error: --chain required", file=sys.stderr)
            sys.exit(1)
        profile = tracker.get_profile(args.chain)
        if profile.level == "AUTONOMOUS":
            profile.level = "SUPERVISED"
            print(f"Demoted {args.chain}: AUTONOMOUS → SUPERVISED")
        elif profile.level == "SUPERVISED":
            profile.level = "MANUAL"
            print(f"Demoted {args.chain}: SUPERVISED → MANUAL")
        else:
            print(f"{args.chain} is already MANUAL")
        tracker.save()


if __name__ == "__main__":
    main()
```

**Step 4: Run test to verify it passes**

Run: `cd susan-team-architect/backend && python -m pytest tests/test_trust_dashboard.py -v`
Expected: All 5 tests PASS

**Step 5: Commit**

```bash
git add susan-team-architect/backend/trust/dashboard.py susan-team-architect/backend/trust/enforcer.py susan-team-architect/backend/trust/__main__.py susan-team-architect/backend/tests/test_trust_dashboard.py
git commit -m "feat(trust): add dashboard, enforcer, and CLI with promote/demote commands"
```

---

## Task 9: Integration Test + Directory Setup

**Files:**
- Create: `.startup-os/signals/.gitkeep`
- Create: `.startup-os/staging/.gitkeep`
- Create: `.startup-os/runs/chains/.gitkeep`
- Create: `.startup-os/runs/trust/.gitkeep`
- Test: `susan-team-architect/backend/tests/test_v4a_integration.py`

**Step 1: Create directory structure**

```bash
mkdir -p .startup-os/signals .startup-os/staging .startup-os/runs/chains .startup-os/runs/trust
touch .startup-os/signals/.gitkeep .startup-os/staging/.gitkeep .startup-os/runs/chains/.gitkeep .startup-os/runs/trust/.gitkeep
```

**Step 2: Write the integration test**

```python
# tests/test_v4a_integration.py
"""Integration test — verifies all three V4a modules work together."""
import json
from pathlib import Path

import pytest


def test_full_pipeline_manual(tmp_path: Path):
    """Simulate: manual signal → Birch scores → Chain runs → Trust enforces."""
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
```

**Step 3: Run integration test**

Run: `cd susan-team-architect/backend && python -m pytest tests/test_v4a_integration.py -v`
Expected: PASS

**Step 4: Run ALL V4a tests**

Run: `cd susan-team-architect/backend && python -m pytest tests/test_chains_schemas.py tests/test_chains_context.py tests/test_chains_engine.py tests/test_chains_cli.py tests/test_birch_scorer.py tests/test_birch_writer.py tests/test_trust_tracker.py tests/test_trust_dashboard.py tests/test_v4a_integration.py -v`
Expected: All tests PASS (approximately 30+ tests)

**Step 5: Commit**

```bash
git add .startup-os/signals/ .startup-os/staging/ .startup-os/runs/ susan-team-architect/backend/tests/test_v4a_integration.py
git commit -m "feat(v4a): add integration test and directory structure for signals/staging/runs"
```

---

## Task 10: Update pyproject.toml + Final Validation

**Files:**
- Modify: `susan-team-architect/backend/pyproject.toml` (add `aiohttp` dependency)

**Step 1: Add aiohttp to dependencies**

Add `"aiohttp>=3.9.0"` to the `dependencies` list in `pyproject.toml` for the Firehose SSE consumer (used in V4b).

**Step 2: Run full test suite**

Run: `cd susan-team-architect/backend && python -m pytest tests/test_chains_schemas.py tests/test_chains_context.py tests/test_chains_engine.py tests/test_chains_cli.py tests/test_birch_scorer.py tests/test_birch_writer.py tests/test_trust_tracker.py tests/test_trust_dashboard.py tests/test_v4a_integration.py -v --tb=short`
Expected: All tests PASS

**Step 3: Verify all three CLIs work**

```bash
cd susan-team-architect/backend
python -m chains --command list
python -m birch --command stats
python -m trust --command dashboard
```

Expected: All three produce clean output without errors.

**Step 4: Commit**

```bash
git add susan-team-architect/backend/pyproject.toml
git commit -m "chore(v4a): add aiohttp dependency for Firehose SSE consumer"
```

**Step 5: Final commit — V4a complete**

```bash
git add -A
git commit -m "feat(v4a): V4a Semi-Autonomous foundation complete — chains, birch, trust modules"
```

---

## Summary

| Task | Module | What | Tests |
|------|--------|------|-------|
| 1 | chains | Pydantic schemas (triggers, steps, runs) | 8 |
| 2 | chains | Context bus (inter-step data passing) | 6 |
| 3 | chains | Engine + registry (execution, gates, audit) | 6 |
| 4 | chains | CLI + chain definitions (competitive-response, daily-cycle) | 2 |
| 5 | birch | Schemas + scorer (3-axis rubric, tier classification) | 5 |
| 6 | birch | Writer + CLI (JSONL output, stats) | 3 |
| 7 | trust | Schemas + tracker + config (profiles, blast radius caps) | 5 |
| 8 | trust | Dashboard + enforcer + CLI (table, markdown, promote/demote) | 5 |
| 9 | — | Integration test + directory setup | 1 |
| 10 | — | pyproject.toml update + full validation | 0 (validation only) |

**Total: 10 tasks, ~41 tests, 10 commits**

**New files: ~20** | **Modified files: 1** (pyproject.toml)

---

*Plan approved and ready for execution. Use superpowers:executing-plans or superpowers:subagent-driven-development.*
