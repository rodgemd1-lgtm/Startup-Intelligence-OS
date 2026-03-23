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
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

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
