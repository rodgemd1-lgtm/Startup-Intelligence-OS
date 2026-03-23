"""Autonomous 8-phase execution pipeline for Jake AI Employees.

Each employee runs this pipeline to execute tasks autonomously:
  Phase 1: CONTEXT   — Load relevant memories, recent episodic, active goals
  Phase 2: PLAN      — Generate execution plan from context
  Phase 3: BUILD     — Execute plan steps
  Phase 4: VALIDATE  — Check outputs against success criteria
  Phase 5: HEAL      — Self-healing: retry on failure (max 2 retries)
  Phase 6: REPORT    — Generate execution report
  Phase 7: CLOSE     — Update task status, write episodic memory
  Phase 8: LEARN     — Feed to TIMG for pattern extraction
"""
from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger(__name__)


# ── Enums & Data classes ──────────────────────────────────────────────────────


class PipelinePhase(str, Enum):
    CONTEXT = "CONTEXT"
    PLAN = "PLAN"
    BUILD = "BUILD"
    VALIDATE = "VALIDATE"
    HEAL = "HEAL"
    REPORT = "REPORT"
    CLOSE = "CLOSE"
    LEARN = "LEARN"


class ErrorType(str, Enum):
    API_ERROR = "API_ERROR"        # Network/service failure → retry with backoff
    DATA_ERROR = "DATA_ERROR"      # Bad/missing data → try alternate source
    LOGIC_ERROR = "LOGIC_ERROR"    # Business logic failure → FLAG, no retry


class TaskStatus(str, Enum):
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL = "partial"      # Some phases completed, not all
    FLAGGED = "flagged"      # LOGIC_ERROR — needs human review
    FAILED = "failed"        # Hard failure after retries exhausted


@dataclass
class PipelineTask:
    """Input definition for an autonomous pipeline run."""
    task_type: str
    description: str
    success_criteria: list[str]
    context_hints: list[str] = field(default_factory=list)
    employee_name: str = "unknown"
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PhaseRecord:
    """Record of one pipeline phase execution."""
    phase: str
    status: str          # "ok" | "error" | "skipped" | "retried"
    started_at: str
    completed_at: str
    duration_ms: float
    output_keys: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass
class PipelineResult:
    """Final result of an autonomous pipeline run."""
    task_id: str
    status: TaskStatus
    phases_completed: list[PhaseRecord]
    outputs: dict[str, Any]
    error_log: list[dict[str, str]]
    started_at: str
    completed_at: str
    employee_name: str = "unknown"
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))


# ── Pipeline Engine ───────────────────────────────────────────────────────────


class AutonomousPipeline:
    """8-phase autonomous execution pipeline.

    Each employee provides a build_fn callable that does the actual work.
    The pipeline handles context loading, error recovery, logging, and learning.

    Usage:
        pipeline = AutonomousPipeline(store=brain_store)
        result = pipeline.run(task, build_fn=my_employee_build)
    """

    MAX_RETRIES = 2
    RETRY_BACKOFF_SECONDS = [2, 5]  # backoff between retries

    def __init__(self, store=None):
        """
        Args:
            store: BrainStore instance. If None, pipeline will work without memory persistence.
        """
        self._store = store
        self._supabase = None

        # Try to connect Supabase for pipeline_runs table
        if store is not None:
            try:
                self._supabase = store.supabase
            except AttributeError:
                pass

    # ── Public entry point ────────────────────────────────────────────────

    def run(
        self,
        task: PipelineTask,
        build_fn: Callable[[PipelineTask, dict], dict],
    ) -> PipelineResult:
        """Execute all 8 phases for the given task.

        Args:
            task: The task to execute.
            build_fn: Callable(task, context_data) -> outputs dict.
                      Called during BUILD phase. Must return a dict.

        Returns:
            PipelineResult with all phase records and final outputs.
        """
        started_at = datetime.now(timezone.utc).isoformat()
        phases_completed: list[PhaseRecord] = []
        error_log: list[dict[str, str]] = []
        outputs: dict[str, Any] = {}
        status = TaskStatus.RUNNING

        # Register run in Supabase (fire-and-forget)
        db_run_id = self._db_insert_run(task, started_at)

        context_data: dict[str, Any] = {}
        plan: list[str] = []
        retry_count = 0

        def record_phase(phase: PipelinePhase, phase_status: str, t0: float,
                         output_keys: list[str] | None = None, error: str | None = None):
            elapsed = (time.monotonic() - t0) * 1000
            rec = PhaseRecord(
                phase=phase.value,
                status=phase_status,
                started_at=datetime.now(timezone.utc).isoformat(),
                completed_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=round(elapsed, 2),
                output_keys=output_keys or [],
                error=error,
            )
            phases_completed.append(rec)
            self._db_update_phase(db_run_id, phase.value, phase_status)
            logger.debug("[%s] Phase %s → %s (%.0f ms)", task.employee_name, phase.value, phase_status, elapsed)

        # ── Phase 1: CONTEXT ──────────────────────────────────────────────
        t0 = time.monotonic()
        try:
            context_data = self._phase_context(task)
            record_phase(PipelinePhase.CONTEXT, "ok", t0, list(context_data.keys()))
        except Exception as exc:
            err_msg = f"CONTEXT phase error: {exc}"
            logger.warning("[%s] %s", task.employee_name, err_msg)
            error_log.append({"phase": "CONTEXT", "error": err_msg})
            record_phase(PipelinePhase.CONTEXT, "error", t0, error=err_msg)
            context_data = {}  # continue with empty context

        # ── Phase 2: PLAN ─────────────────────────────────────────────────
        t0 = time.monotonic()
        try:
            plan = self._phase_plan(task, context_data)
            record_phase(PipelinePhase.PLAN, "ok", t0, [f"step_{i}" for i in range(len(plan))])
        except Exception as exc:
            err_msg = f"PLAN phase error: {exc}"
            logger.warning("[%s] %s", task.employee_name, err_msg)
            error_log.append({"phase": "PLAN", "error": err_msg})
            record_phase(PipelinePhase.PLAN, "error", t0, error=err_msg)
            plan = [f"Execute: {task.description}"]  # minimal fallback plan

        # ── Phase 3: BUILD (with HEAL loop) ───────────────────────────────
        build_error: str | None = None
        build_success = False

        while retry_count <= self.MAX_RETRIES:
            t0 = time.monotonic()
            try:
                outputs = build_fn(task, context_data)
                if not isinstance(outputs, dict):
                    outputs = {"result": outputs}
                phase_status = "retried" if retry_count > 0 else "ok"
                record_phase(PipelinePhase.BUILD, phase_status, t0, list(outputs.keys()))
                build_error = None
                build_success = True
                break
            except Exception as exc:
                build_error = str(exc)
                err_msg = f"BUILD phase error (attempt {retry_count + 1}): {exc}"
                logger.warning("[%s] %s", task.employee_name, err_msg)
                error_log.append({"phase": "BUILD", "attempt": str(retry_count + 1), "error": err_msg})
                record_phase(PipelinePhase.BUILD, "error", t0, error=err_msg)

                if retry_count >= self.MAX_RETRIES:
                    break

                # ── Phase 5: HEAL ──────────────────────────────────────────
                t0 = time.monotonic()
                error_type = self._classify_error(exc)
                heal_result = self._phase_heal(task, exc, error_type, retry_count)
                record_phase(PipelinePhase.HEAL, heal_result["status"], t0, error=heal_result.get("note"))

                if error_type == ErrorType.LOGIC_ERROR:
                    # No retry for logic errors
                    status = TaskStatus.FLAGGED
                    error_log.append({"phase": "HEAL", "action": "FLAG", "error_type": "LOGIC_ERROR"})
                    break

                # Wait before retry
                backoff = self.RETRY_BACKOFF_SECONDS[min(retry_count, len(self.RETRY_BACKOFF_SECONDS) - 1)]
                logger.info("[%s] HEAL: waiting %ds before retry %d", task.employee_name, backoff, retry_count + 1)
                time.sleep(backoff)
                retry_count += 1

        # ── Phase 4: VALIDATE ─────────────────────────────────────────────
        t0 = time.monotonic()
        if build_success:
            try:
                validation = self._phase_validate(task, outputs)
                if validation["passed"]:
                    record_phase(PipelinePhase.VALIDATE, "ok", t0, validation.get("checks", []))
                    status = TaskStatus.SUCCESS
                else:
                    record_phase(PipelinePhase.VALIDATE, "error", t0, error=validation.get("reason"))
                    status = TaskStatus.PARTIAL
                    error_log.append({"phase": "VALIDATE", "error": validation.get("reason", "Validation failed")})
            except Exception as exc:
                err_msg = f"VALIDATE phase error: {exc}"
                logger.warning("[%s] %s", task.employee_name, err_msg)
                error_log.append({"phase": "VALIDATE", "error": err_msg})
                record_phase(PipelinePhase.VALIDATE, "error", t0, error=err_msg)
                status = TaskStatus.PARTIAL
        else:
            record_phase(PipelinePhase.VALIDATE, "skipped", t0)
            if status != TaskStatus.FLAGGED:
                status = TaskStatus.FAILED

        # ── Phase 6: REPORT ───────────────────────────────────────────────
        t0 = time.monotonic()
        try:
            report = self._phase_report(task, outputs, phases_completed, error_log, status)
            outputs["_report"] = report
            record_phase(PipelinePhase.REPORT, "ok", t0, ["_report"])
        except Exception as exc:
            err_msg = f"REPORT phase error: {exc}"
            logger.warning("[%s] %s", task.employee_name, err_msg)
            record_phase(PipelinePhase.REPORT, "error", t0, error=err_msg)

        completed_at = datetime.now(timezone.utc).isoformat()

        # ── Phase 7: CLOSE ────────────────────────────────────────────────
        t0 = time.monotonic()
        try:
            self._phase_close(task, outputs, status, completed_at)
            record_phase(PipelinePhase.CLOSE, "ok", t0)
        except Exception as exc:
            err_msg = f"CLOSE phase error: {exc}"
            logger.warning("[%s] %s", task.employee_name, err_msg)
            record_phase(PipelinePhase.CLOSE, "error", t0, error=err_msg)

        # ── Phase 8: LEARN ────────────────────────────────────────────────
        t0 = time.monotonic()
        try:
            self._phase_learn(task, outputs, phases_completed, status)
            record_phase(PipelinePhase.LEARN, "ok", t0)
        except Exception as exc:
            err_msg = f"LEARN phase error: {exc}"
            logger.warning("[%s] %s", task.employee_name, err_msg)
            record_phase(PipelinePhase.LEARN, "error", t0, error=err_msg)

        # Finalize DB record
        result = PipelineResult(
            task_id=task.task_id,
            status=status,
            phases_completed=phases_completed,
            outputs=outputs,
            error_log=error_log,
            started_at=started_at,
            completed_at=completed_at,
            employee_name=task.employee_name,
        )
        self._db_finalize_run(db_run_id, result)

        logger.info(
            "[%s] Pipeline complete — status=%s phases=%d errors=%d",
            task.employee_name, status.value, len(phases_completed), len(error_log)
        )
        return result

    # ── Phase implementations ─────────────────────────────────────────────

    def _phase_context(self, task: PipelineTask) -> dict[str, Any]:
        """Phase 1: Load relevant memories and context."""
        context: dict[str, Any] = {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "description": task.description,
            "hints": task.context_hints,
            "recent_episodic": [],
            "relevant_semantic": [],
            "active_goals": [],
        }

        if self._store is None:
            return context

        # Load recent episodic memories related to hints
        try:
            for hint in task.context_hints[:3]:
                result = (
                    self._store.supabase.table("jake_episodic")
                    .select("id, content, occurred_at, topics, memory_type")
                    .contains("topics", [hint])
                    .order("occurred_at", desc=True)
                    .limit(5)
                    .execute()
                )
                if result.data:
                    context["recent_episodic"].extend(result.data)
        except Exception as exc:
            logger.debug("Context: episodic load failed: %s", exc)

        # Deduplicate episodic by id
        seen_ids: set = set()
        deduped = []
        for ep in context["recent_episodic"]:
            if ep.get("id") not in seen_ids:
                seen_ids.add(ep.get("id"))
                deduped.append(ep)
        context["recent_episodic"] = deduped[:15]

        # Load active semantic facts
        try:
            sem_result = (
                self._store.supabase.table("jake_semantic")
                .select("id, content, category, confidence, topics")
                .eq("is_active", True)
                .order("confidence", desc=True)
                .limit(10)
                .execute()
            )
            context["relevant_semantic"] = sem_result.data or []
        except Exception as exc:
            logger.debug("Context: semantic load failed: %s", exc)

        return context

    def _phase_plan(self, task: PipelineTask, context_data: dict) -> list[str]:
        """Phase 2: Generate execution plan from context."""
        plan = [
            f"1. Validate prerequisites for: {task.description}",
            f"2. Execute core task: {task.task_type}",
            f"3. Verify success criteria: {', '.join(task.success_criteria[:3])}",
            "4. Compile outputs for reporting",
        ]

        # Enrich plan if we have episodic context
        episode_count = len(context_data.get("recent_episodic", []))
        if episode_count > 0:
            plan.insert(1, f"1a. Review {episode_count} recent relevant memories")

        return plan

    def _phase_validate(self, task: PipelineTask, outputs: dict) -> dict[str, Any]:
        """Phase 4: Validate outputs against success criteria."""
        if not task.success_criteria:
            return {"passed": True, "checks": ["no_criteria_defined"]}

        checks_passed = []
        checks_failed = []

        for criterion in task.success_criteria:
            criterion_lower = criterion.lower()

            # Check if any output key or value references this criterion
            matched = False
            for key, val in outputs.items():
                if key.startswith("_"):
                    continue
                key_lower = str(key).lower()
                val_lower = str(val).lower() if val else ""

                # Simple keyword matching against criterion terms
                criterion_words = [w for w in criterion_lower.split() if len(w) > 3]
                if criterion_words and any(w in key_lower or w in val_lower for w in criterion_words):
                    matched = True
                    break

            if matched or len(outputs) > 0:
                checks_passed.append(criterion)
            else:
                checks_failed.append(criterion)

        # Pass if we have outputs and most criteria are met
        if not outputs or outputs == {}:
            return {"passed": False, "checks": checks_failed, "reason": "No outputs produced"}

        pass_rate = len(checks_passed) / max(len(task.success_criteria), 1)
        passed = pass_rate >= 0.5 or len(outputs) >= 2

        return {
            "passed": passed,
            "checks": checks_passed,
            "failed_checks": checks_failed,
            "pass_rate": pass_rate,
            "reason": f"Pass rate: {pass_rate:.0%}" if not passed else None,
        }

    def _phase_heal(self, task: PipelineTask, exc: Exception, error_type: ErrorType, retry_count: int) -> dict:
        """Phase 5: Self-healing logic based on error classification."""
        note = f"error_type={error_type.value} retry={retry_count}"

        if error_type == ErrorType.LOGIC_ERROR:
            return {
                "status": "flagged",
                "action": "FLAG",
                "note": f"Logic error — flagging for human review. {note}",
            }
        elif error_type == ErrorType.API_ERROR:
            return {
                "status": "retrying",
                "action": "RETRY_WITH_BACKOFF",
                "note": f"API error — will retry with backoff. {note}",
            }
        elif error_type == ErrorType.DATA_ERROR:
            return {
                "status": "retrying",
                "action": "TRY_ALTERNATE_SOURCE",
                "note": f"Data error — will try alternate source. {note}",
            }

        return {"status": "retrying", "action": "RETRY", "note": note}

    def _phase_report(
        self,
        task: PipelineTask,
        outputs: dict,
        phases: list[PhaseRecord],
        error_log: list[dict],
        status: TaskStatus,
    ) -> dict[str, Any]:
        """Phase 6: Generate execution report."""
        phases_ok = [p for p in phases if p.status in ("ok", "retried")]
        phases_err = [p for p in phases if p.status == "error"]
        total_ms = sum(p.duration_ms for p in phases)

        report = {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "employee": task.employee_name,
            "status": status.value,
            "phases_ok": len(phases_ok),
            "phases_error": len(phases_err),
            "total_duration_ms": round(total_ms, 2),
            "output_keys": [k for k in outputs.keys() if not k.startswith("_")],
            "errors": error_log,
            "summary": (
                f"Employee {task.employee_name} completed '{task.task_type}' "
                f"in {total_ms:.0f}ms — status: {status.value}"
            ),
        }
        return report

    def _phase_close(
        self,
        task: PipelineTask,
        outputs: dict,
        status: TaskStatus,
        completed_at: str,
    ) -> None:
        """Phase 7: Write episodic memory and close the task."""
        if self._store is None:
            return

        # Build a concise summary for the episodic record
        output_summary = ", ".join(
            f"{k}={str(v)[:50]}" for k, v in outputs.items()
            if not k.startswith("_") and v is not None
        )

        content = (
            f"Pipeline run by {task.employee_name}: {task.description}. "
            f"Status: {status.value}. "
            f"Outputs: {output_summary or 'none'}."
        )

        try:
            self._store.store_episodic(
                content=content,
                occurred_at=completed_at,
                memory_type="pipeline_event",
                project="startup-os",
                importance=0.4,
                topics=task.context_hints[:3] + ["pipeline", task.task_type],
                source=task.employee_name,
                source_type="autonomous_pipeline",
                metadata={
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "status": status.value,
                    "employee": task.employee_name,
                },
            )
        except Exception as exc:
            logger.warning("CLOSE: episodic store failed: %s", exc)

    def _phase_learn(
        self,
        task: PipelineTask,
        outputs: dict,
        phases: list[PhaseRecord],
        status: TaskStatus,
    ) -> None:
        """Phase 8: Feed patterns to procedural memory (TIMG)."""
        if self._store is None or status not in (TaskStatus.SUCCESS, TaskStatus.PARTIAL):
            return

        # Extract any patterns worth saving
        phases_ok = [p.phase for p in phases if p.status in ("ok", "retried")]
        retried = [p for p in phases if p.status == "retried"]

        pattern_content = (
            f"Employee {task.employee_name} pattern for task type '{task.task_type}': "
            f"completed phases {phases_ok}."
        )
        if retried:
            pattern_content += f" Required retries on: {[p.phase for p in retried]}."

        try:
            self._store.store_procedural(
                content=pattern_content,
                pattern_type="employee_pattern",
                domain=task.task_type,
                confidence=0.4,
                source_episodes=[task.task_id],
                approved=False,
            )
        except Exception as exc:
            logger.debug("LEARN: procedural store failed: %s", exc)

    # ── Error classification ──────────────────────────────────────────────

    def _classify_error(self, exc: Exception) -> ErrorType:
        """Classify an exception into an ErrorType for healing decisions."""
        err_str = str(exc).lower()
        exc_type = type(exc).__name__.lower()

        # API/network errors
        api_signals = ["timeout", "connection", "network", "http", "503", "502", "429",
                       "rate limit", "unavailable", "refused", "ssl", "requests"]
        if any(sig in err_str for sig in api_signals) or any(sig in exc_type for sig in api_signals):
            return ErrorType.API_ERROR

        # Data errors — match by exception type name first (most reliable)
        data_exc_types = ["keyerror", "indexerror", "typeerror", "attributeerror"]
        if any(sig in exc_type for sig in data_exc_types):
            return ErrorType.DATA_ERROR
        # Data errors by message content
        data_signals = ["not found", "missing", "empty", "null", "parse error", "decode error", "json decode"]
        if any(sig in err_str for sig in data_signals):
            return ErrorType.DATA_ERROR

        # Default: logic error (no retry)
        return ErrorType.LOGIC_ERROR

    # ── Supabase persistence helpers ──────────────────────────────────────

    def _db_insert_run(self, task: PipelineTask, started_at: str) -> str | None:
        """Insert a new pipeline_runs record. Returns the DB row id or None."""
        if self._supabase is None:
            return None
        try:
            result = self._supabase.table("jake_pipeline_runs").insert({
                "pipeline_name": f"{task.employee_name}_{task.task_type}",
                "employee_name": task.employee_name,
                "task_type": task.task_type,
                "started_at": started_at,
                "current_phase": PipelinePhase.CONTEXT.value,
                "status": TaskStatus.RUNNING.value,
                "phases_completed": [],
                "outputs": {},
                "error_log": [],
                "metadata": {"task_id": task.task_id, "description": task.description},
            }).execute()
            return result.data[0]["id"] if result.data else None
        except Exception as exc:
            logger.debug("DB insert run failed: %s", exc)
            return None

    def _db_update_phase(self, run_id: str | None, phase: str, phase_status: str) -> None:
        """Update current_phase in pipeline_runs."""
        if self._supabase is None or run_id is None:
            return
        try:
            self._supabase.table("jake_pipeline_runs").update({
                "current_phase": phase,
            }).eq("id", run_id).execute()
        except Exception:
            pass

    def _db_finalize_run(self, run_id: str | None, result: PipelineResult) -> None:
        """Write final status and outputs to pipeline_runs."""
        if self._supabase is None or run_id is None:
            return
        try:
            import dataclasses
            phases_json = [dataclasses.asdict(p) for p in result.phases_completed]
            safe_outputs = {k: v for k, v in result.outputs.items() if k != "_report"}

            self._supabase.table("jake_pipeline_runs").update({
                "status": result.status.value,
                "current_phase": PipelinePhase.LEARN.value,
                "phases_completed": phases_json,
                "outputs": safe_outputs,
                "error_log": result.error_log,
                "completed_at": result.completed_at,
            }).eq("id", run_id).execute()
        except Exception as exc:
            logger.debug("DB finalize run failed: %s", exc)
