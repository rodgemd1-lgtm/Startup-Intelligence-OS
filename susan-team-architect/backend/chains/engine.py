"""Chain Engine — executes multi-step agent workflows with gates and audit logging."""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional, Union

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
                    error=f"{type(exc).__name__}: {exc}",
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
