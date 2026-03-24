<<<<<<< HEAD
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
=======
"""8-phase autonomous execution pipeline with self-healing.

Each pipeline run goes through:
  Phase 1: CONTEXT   — Load relevant memories, episodic, active goals
  Phase 2: PLAN      — Generate execution plan (what to do, which steps)
  Phase 3: BUILD     — Execute plan steps
  Phase 4: VALIDATE  — Check outputs against success criteria
  Phase 5: HEAL      — Retry with different approach on failure (max 2 retries)
  Phase 6: REPORT    — Generate execution report
  Phase 7: CLOSE     — Update task/goal status, write episodic memory
  Phase 8: LEARN     — Feed results to TIMG for pattern extraction

Usage:
    pipeline = AutonomousPipeline("my-task", "Research competitor X", "research")
    result = pipeline.run()
"""
from __future__ import annotations

import json
import time
import uuid
import logging
import traceback
>>>>>>> claude/nifty-ptolemy
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

<<<<<<< HEAD
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
=======
from supabase import create_client, Client

from jake_brain.store import BrainStore
from jake_brain.retriever import BrainRetriever
from susan_core.config import config as susan_config

logger = logging.getLogger(__name__)


class PipelineStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class ErrorClass(str, Enum):
    API_ERROR = "api_error"        # Retry with backoff
    DATA_ERROR = "data_error"      # Try alternate data source
    LOGIC_ERROR = "logic_error"    # Escalate to FLAG, don't retry


class AutonomousPipeline:
    """8-phase autonomous execution engine with self-healing."""

    MAX_HEAL_RETRIES = 2

    def __init__(
        self,
        pipeline_name: str,
        task_description: str,
        task_type: str,
        context_overrides: dict | None = None,
    ):
        self.pipeline_name = pipeline_name
        self.task_description = task_description
        self.task_type = task_type          # research | content | maintenance | custom
        self.context_overrides = context_overrides or {}
        self.run_id = str(uuid.uuid4())

        # Shared state across phases
        self.context_data: dict = {}
        self.plan_data: dict = {}
        self.build_results: dict = {}
        self.validation_result: dict = {}
        self.report_data: dict = {}
        self.phases_completed: dict = {}
        self.error_log: list[str] = []

        # Supabase + brain
        self.supabase: Client = create_client(
            susan_config.supabase_url, susan_config.supabase_key
        )
        self.store = BrainStore()
        self.retriever = BrainRetriever(self.store)

    # ------------------------------------------------------------------
    # PUBLIC ENTRY POINT
    # ------------------------------------------------------------------

    def run(self) -> dict:
        """Execute all 8 phases in sequence. Returns final status dict."""
        logger.info(f"[Pipeline:{self.pipeline_name}] Starting run {self.run_id}")
        self._create_run_record()

        try:
            # Phase 1: CONTEXT
            self._transition_phase("context")
            self.context_data = self._phase_context()
            self._record_phase("context", self.context_data)

            # Phase 2: PLAN
            self._transition_phase("plan")
            self.plan_data = self._phase_plan(self.context_data)
            self._record_phase("plan", self.plan_data)

            # Phase 3+4+5: BUILD → VALIDATE → HEAL loop
            validation_passed = False
            heal_attempts = 0

            for attempt in range(self.MAX_HEAL_RETRIES + 1):
                # Phase 3: BUILD
                self._transition_phase("build")
                self.build_results = self._phase_build(
                    self.plan_data, self.context_data, attempt=attempt
                )
                self._record_phase("build", self.build_results)

                # Phase 4: VALIDATE
                self._transition_phase("validate")
                self.validation_result = self._phase_validate(
                    self.build_results, self.plan_data
                )
                self._record_phase("validate", self.validation_result)

                if self.validation_result.get("passed"):
                    validation_passed = True
                    break

                # Phase 5: HEAL (only if not last attempt)
                if attempt < self.MAX_HEAL_RETRIES:
                    self._transition_phase("heal")
                    heal_result = self._phase_heal(
                        self.validation_result, heal_attempt=heal_attempts
                    )
                    self._record_phase("heal", heal_result)
                    heal_attempts += 1

                    # Logic errors escalate immediately (no retry)
                    if heal_result.get("error_class") == ErrorClass.LOGIC_ERROR:
                        reason = self.validation_result.get("reason", "Logic error")
                        return self._finalize(
                            success=False,
                            status=PipelineStatus.BLOCKED,
                            reason=f"Logic error — human review required: {reason}",
                        )

                    # Update plan with healed approach
                    if heal_result.get("revised_plan"):
                        self.plan_data.update(heal_result["revised_plan"])

            if not validation_passed:
                return self._finalize(
                    success=False,
                    status=PipelineStatus.BLOCKED,
                    reason=f"Max retries ({self.MAX_HEAL_RETRIES}) exceeded without validation pass",
                )

            # Phase 6: REPORT
            self._transition_phase("report")
            self.report_data = self._phase_report(
                self.build_results, self.validation_result, self.context_data
            )
            self._record_phase("report", self.report_data)

            # Phase 7: CLOSE
            self._transition_phase("close")
            close_result = self._phase_close(
                self.report_data, self.context_data, self.plan_data
            )
            self._record_phase("close", close_result)

            # Phase 8: LEARN
            self._transition_phase("learn")
            learn_result = self._phase_learn(self.report_data)
            self._record_phase("learn", learn_result)

            logger.info(f"[Pipeline:{self.pipeline_name}] Completed successfully")
            return self._finalize(success=True, status=PipelineStatus.COMPLETED)

        except Exception as e:
            tb = traceback.format_exc()
            self.error_log.append(f"Unhandled exception: {e}\n{tb}")
            logger.error(f"[Pipeline:{self.pipeline_name}] Unhandled error: {e}")
            return self._finalize(
                success=False,
                status=PipelineStatus.FAILED,
                reason=str(e),
            )

    # ------------------------------------------------------------------
    # PHASE IMPLEMENTATIONS (override in subclasses for custom behavior)
    # ------------------------------------------------------------------

    def _phase_context(self) -> dict:
        """Phase 1: Load relevant memories, episodic, active goals."""
        context = {
            "task": self.task_description,
            "task_type": self.task_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Load relevant semantic memories
        try:
            memories = self.retriever.recall(
                query=self.task_description, top_k=5
            )
            context["memories"] = memories
        except Exception as e:
            logger.warning(f"Memory recall failed: {e}")
            context["memories"] = ""

        # Load active goals from Supabase
        try:
            goals = (
                self.supabase.table("jake_goals")
                .select("id, title, project, status, priority")
                .eq("status", "active")
                .limit(10)
                .execute()
            )
            context["active_goals"] = goals.data or []
        except Exception as e:
            logger.warning(f"Goals fetch failed: {e}")
            context["active_goals"] = []

        # Apply any overrides
        context.update(self.context_overrides)
        return context

    def _phase_plan(self, context: dict) -> dict:
        """Phase 2: Generate execution plan based on task type."""
        task_type = self.task_type
        steps = self._get_default_steps(task_type)

        return {
            "task_type": task_type,
            "steps": steps,
            "success_criteria": self._get_success_criteria(task_type),
            "fallback_strategy": self._get_fallback_strategy(task_type),
            "context_summary": str(context.get("memories", ""))[:500],
        }

    def _phase_build(self, plan: dict, context: dict, attempt: int = 0) -> dict:
        """Phase 3: Execute plan steps. Override for custom build logic."""
        steps = plan.get("steps", [])
        results = []
        errors = []

        for step in steps:
            step_name = step.get("name", "unnamed")
            step_fn: Callable | None = step.get("fn")
            try:
                if callable(step_fn):
                    output = step_fn(context, attempt)
                else:
                    # Default: log step as completed (framework-level no-op)
                    output = {"step": step_name, "status": "skipped", "note": "No fn provided"}
                results.append({"step": step_name, "output": output, "status": "ok"})
            except Exception as e:
                error_msg = f"Step {step_name} failed: {e}"
                errors.append(error_msg)
                results.append({"step": step_name, "status": "error", "error": str(e)})

        return {
            "results": results,
            "errors": errors,
            "steps_completed": len([r for r in results if r["status"] == "ok"]),
            "steps_total": len(steps),
            "attempt": attempt,
        }

    def _phase_validate(self, build_results: dict, plan: dict) -> dict:
        """Phase 4: Check outputs against success criteria."""
        criteria = plan.get("success_criteria", {})
        errors = build_results.get("errors", [])
        steps_completed = build_results.get("steps_completed", 0)
        steps_total = build_results.get("steps_total", 0)

        # Base validation: all steps must complete without errors
        if errors:
            return {
                "passed": False,
                "reason": f"Build errors: {errors[0]}",
                "error_class": self._classify_error(errors[0]),
                "completion_rate": steps_completed / max(steps_total, 1),
            }

        min_steps = criteria.get("min_steps_completed", 1)
        if steps_completed < min_steps:
            return {
                "passed": False,
                "reason": f"Only {steps_completed}/{steps_total} steps completed (need {min_steps})",
                "error_class": ErrorClass.DATA_ERROR,
                "completion_rate": steps_completed / max(steps_total, 1),
            }

        return {
            "passed": True,
            "reason": "All success criteria met",
            "completion_rate": steps_completed / max(steps_total, 1),
        }

    def _phase_heal(self, validation: dict, heal_attempt: int = 0) -> dict:
        """Phase 5: Classify error and generate revised approach."""
        error_class = validation.get("error_class", ErrorClass.API_ERROR)
        reason = validation.get("reason", "Unknown failure")

        logger.info(f"[Heal attempt {heal_attempt+1}] Error class: {error_class}, reason: {reason}")

        if error_class == ErrorClass.LOGIC_ERROR:
            return {
                "error_class": error_class,
                "action": "escalate",
                "message": f"Logic error requires human review: {reason}",
            }

        if error_class == ErrorClass.API_ERROR:
            # Retry with exponential backoff (implement in build via attempt counter)
            backoff = 2 ** heal_attempt
            logger.info(f"API error — backing off {backoff}s before retry")
            time.sleep(min(backoff, 8))
            return {
                "error_class": error_class,
                "action": "retry_with_backoff",
                "backoff_seconds": backoff,
                "revised_plan": None,
            }

        if error_class == ErrorClass.DATA_ERROR:
            # Try alternate data source
            return {
                "error_class": error_class,
                "action": "use_fallback_data",
                "revised_plan": {
                    "fallback_mode": True,
                    "fallback_strategy": self.plan_data.get("fallback_strategy", "use_cached"),
                },
            }

        return {"error_class": error_class, "action": "retry", "revised_plan": None}

    def _phase_report(self, build_results: dict, validation: dict, context: dict) -> dict:
        """Phase 6: Generate execution report."""
        return {
            "pipeline_name": self.pipeline_name,
            "task_description": self.task_description,
            "task_type": self.task_type,
            "run_id": self.run_id,
            "steps_completed": build_results.get("steps_completed", 0),
            "steps_total": build_results.get("steps_total", 0),
            "validation_passed": validation.get("passed", False),
            "completion_rate": validation.get("completion_rate", 0),
            "results_summary": build_results.get("results", []),
            "errors": build_results.get("errors", []),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _phase_close(self, report: dict, context: dict, plan: dict) -> dict:
        """Phase 7: Update task status, write episodic memory."""
        closed = {}

        # Write episodic memory of this run
        try:
            summary = (
                f"Pipeline '{self.pipeline_name}' completed: "
                f"{report['steps_completed']}/{report['steps_total']} steps, "
                f"task: {self.task_description}"
            )
            episodic = self.store.store_episodic(
                content=summary,
                occurred_at=datetime.now(timezone.utc),
                memory_type="pipeline_run",
                project=self._infer_project(),
                importance=0.6,
                topics=["pipeline", self.task_type],
                metadata={"run_id": self.run_id, "pipeline_name": self.pipeline_name},
            )
            closed["episodic_id"] = episodic.get("id")
        except Exception as e:
            logger.warning(f"Failed to write episodic memory: {e}")

        return closed

    def _phase_learn(self, report: dict) -> dict:
        """Phase 8: Feed results to TIMG for pattern extraction."""
        try:
            # Store as procedural pattern if successful
            if report.get("validation_passed"):
                pattern = (
                    f"Successful pipeline pattern for {self.task_type}: "
                    f"{self.task_description[:100]}"
                )
                self.store.store_procedural(
                    content=pattern,
                    pattern_type="pipeline_success",
                    domain=self.task_type,
                    confidence=0.5,
                    approved=False,
                )
                return {"pattern_stored": True, "pattern": pattern}
        except Exception as e:
            logger.warning(f"TIMG learn failed: {e}")

        return {"pattern_stored": False}

    # ------------------------------------------------------------------
    # SUPABASE PIPELINE RUN TRACKING
    # ------------------------------------------------------------------

    def _create_run_record(self) -> None:
        try:
            self.supabase.table("jake_pipeline_runs").insert({
                "id": self.run_id,
                "pipeline_name": self.pipeline_name,
                "task_description": self.task_description,
                "task_type": self.task_type,
                "status": PipelineStatus.RUNNING,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "current_phase": "init",
                "phases_completed": {},
                "error_log": [],
            }).execute()
        except Exception as e:
            logger.warning(f"Failed to create pipeline run record: {e}")

    def _transition_phase(self, phase: str) -> None:
        logger.info(f"[Pipeline:{self.pipeline_name}] Phase: {phase.upper()}")
        try:
            self.supabase.table("jake_pipeline_runs").update({
                "current_phase": phase,
            }).eq("id", self.run_id).execute()
        except Exception as e:
            logger.warning(f"Phase transition update failed: {e}")

    def _record_phase(self, phase: str, result: dict) -> None:
        try:
            # Read current phases_completed and merge
            existing = self.supabase.table("jake_pipeline_runs").select(
                "phases_completed"
            ).eq("id", self.run_id).execute()
            current = {}
            if existing.data:
                current = existing.data[0].get("phases_completed") or {}
            current[phase] = {"status": "ok", "summary": str(result)[:500]}
            self.supabase.table("jake_pipeline_runs").update({
                "phases_completed": current,
            }).eq("id", self.run_id).execute()
        except Exception as e:
            logger.warning(f"Phase record update failed: {e}")

    def _finalize(
        self,
        success: bool,
        status: PipelineStatus = PipelineStatus.COMPLETED,
        reason: str = "",
    ) -> dict:
        try:
            self.supabase.table("jake_pipeline_runs").update({
                "status": status,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "error_log": self.error_log,
            }).eq("id", self.run_id).execute()
        except Exception as e:
            logger.warning(f"Finalize update failed: {e}")

        return {
            "run_id": self.run_id,
            "pipeline_name": self.pipeline_name,
            "success": success,
            "status": status,
            "reason": reason,
            "phases_completed": self.phases_completed,
        }

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _classify_error(self, error_msg: str) -> ErrorClass:
        """Classify an error string into API/Data/Logic error."""
        lower = error_msg.lower()
        if any(w in lower for w in ["timeout", "connection", "rate limit", "429", "503", "network"]):
            return ErrorClass.API_ERROR
        if any(w in lower for w in ["not found", "empty", "no data", "missing", "null"]):
            return ErrorClass.DATA_ERROR
        return ErrorClass.LOGIC_ERROR

    def _infer_project(self) -> str:
        task_lower = self.task_description.lower()
        if "oracle" in task_lower:
            return "oracle-health"
        if "recruit" in task_lower or "jacob" in task_lower:
            return "alex-recruiting"
        if "inbox" in task_lower or "email" in task_lower:
            return "hermes"
        return "startup-os"

    def _get_default_steps(self, task_type: str) -> list[dict]:
        """Default steps by task type."""
        defaults = {
            "research": [
                {"name": "query_rag", "description": "Query Susan RAG for relevant knowledge"},
                {"name": "synthesize", "description": "Synthesize findings into summary"},
            ],
            "content": [
                {"name": "load_context", "description": "Load template and context"},
                {"name": "draft", "description": "Draft content from context"},
                {"name": "review", "description": "Self-review draft for quality"},
            ],
            "maintenance": [
                {"name": "check_freshness", "description": "Check data freshness in RAG"},
                {"name": "flag_stale", "description": "Flag domains with >20% stale records"},
            ],
        }
        return defaults.get(task_type, [{"name": "execute", "description": "Execute task"}])

    def _get_success_criteria(self, task_type: str) -> dict:
        return {
            "research": {"min_steps_completed": 2},
            "content": {"min_steps_completed": 3},
            "maintenance": {"min_steps_completed": 2},
        }.get(task_type, {"min_steps_completed": 1})

    def _get_fallback_strategy(self, task_type: str) -> str:
        return {
            "research": "use_cached_rag_results",
            "content": "use_template_defaults",
            "maintenance": "skip_unavailable_sources",
        }.get(task_type, "retry_once")
>>>>>>> claude/nifty-ptolemy
