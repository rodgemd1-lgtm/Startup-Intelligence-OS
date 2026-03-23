from __future__ import annotations

import concurrent.futures
import os
import queue
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))


def _load_env() -> None:
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        with open(env_path) as fh:
            for line in fh:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())


_load_env()


@dataclass
class PipelineStep:
    name: str
    fn: Callable  # callable that returns dict with status, result
    is_parallel: bool = False  # can run in parallel with other parallel steps
    depends_on: list[str] = field(default_factory=list)  # step names this depends on


@dataclass
class PipelineTask:
    description: str
    task_type: str  # research, content, maintenance, analysis
    priority: int = 3  # 1=highest, 5=lowest
    steps: list[PipelineStep] = field(default_factory=list)
    run_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])


class AutonomousPipeline:
    """8-phase autonomous execution engine with parallel BUILD and priority queuing."""

    def __init__(self):
        self._task_queue: queue.PriorityQueue = queue.PriorityQueue()
        self._run_id: str = ""
        self._pipeline_name: str = ""
        self._phases_completed: dict = {}

    def enqueue(self, task: PipelineTask) -> None:
        """Add task to priority queue. Lower priority number = processed first."""
        self._task_queue.put((task.priority, task))

    def process_next(self) -> dict:
        """Process highest-priority task from queue."""
        if self._task_queue.empty():
            return {"status": "empty", "message": "No tasks in queue"}
        _, task = self._task_queue.get_nowait()
        return self.execute(task)

    def process_all(self) -> list[dict]:
        """Process all queued tasks in priority order."""
        results = []
        while not self._task_queue.empty():
            results.append(self.process_next())
        return results

    def execute(self, task: PipelineTask) -> dict:
        """Run all 8 phases for a task."""
        self._run_id = task.run_id
        self._pipeline_name = task.description
        self._phases_completed = {}

        self._track_run("running", "CONTEXT")

        # Phase 1: CONTEXT
        ctx = self._phase_context(task)
        self._phases_completed["context"] = ctx

        # Phase 2: PLAN
        plan = self._phase_plan(task, ctx)
        self._phases_completed["plan"] = plan

        # Phase 3: BUILD (parallel for independent steps)
        build = self._phase_build(task, plan)
        self._phases_completed["build"] = build

        # Phase 4: VALIDATE
        validation = self._phase_validate(task, build)
        self._phases_completed["validate"] = validation

        # Phase 5: HEAL (if validation failed)
        if not validation.get("passed"):
            heal = self._phase_heal(task, validation, retries=0)
            self._phases_completed["heal"] = heal

        # Phase 6: REPORT
        report = self._phase_report(task)
        self._phases_completed["report"] = report

        # Phase 7: CLOSE
        close = self._phase_close(task)
        self._phases_completed["close"] = close

        # Phase 8: LEARN
        learn = self._phase_learn(task)
        self._phases_completed["learn"] = learn

        final_status = "completed" if validation.get("passed") else "completed_with_issues"
        self._track_run(final_status, "LEARN", completed=True)

        return {
            "status": final_status,
            "run_id": self._run_id,
            "task": task.description,
            "task_type": task.task_type,
            "phases": self._phases_completed,
        }

    def _phase_context(self, task: PipelineTask) -> dict:
        """Phase 1: Load relevant memories and context."""
        context: dict[str, Any] = {
            "task_description": task.description,
            "task_type": task.task_type,
            "memories": [],
            "goals": [],
        }
        try:
            from jake_brain.retriever import BrainRetriever
            from jake_brain.store import BrainStore
            store = BrainStore()
            retriever = BrainRetriever(store)
            recall = retriever.recall(task.description, top_k=3)
            context["memories"] = [recall] if recall else []
        except Exception as e:
            context["memory_error"] = str(e)

        try:
            from supabase import create_client
            url = os.environ.get("SUPABASE_URL", "")
            key = os.environ.get("SUPABASE_SERVICE_KEY", "")
            if url and key:
                client = create_client(url, key)
                goals = client.table("jake_goals").select("title,status").eq("status", "active").limit(5).execute()
                context["goals"] = [g["title"] for g in (goals.data or [])]
        except Exception:
            pass

        return {"status": "ok", "context": context}

    def _phase_plan(self, task: PipelineTask, context: dict) -> dict:
        """Phase 2: Generate execution plan."""
        # If task has explicit steps, use them; otherwise generate generic plan
        if task.steps:
            steps_plan = [{"name": s.name, "is_parallel": s.is_parallel} for s in task.steps]
        else:
            # Generic plan based on task_type
            type_plans: dict[str, list[dict]] = {
                "research": [
                    {"name": "search_rag", "is_parallel": True},
                    {"name": "search_web", "is_parallel": True},
                    {"name": "synthesize", "is_parallel": False},
                ],
                "content": [
                    {"name": "gather_context", "is_parallel": False},
                    {"name": "draft", "is_parallel": False},
                    {"name": "review", "is_parallel": False},
                ],
                "maintenance": [
                    {"name": "check_stale", "is_parallel": True},
                    {"name": "check_health", "is_parallel": True},
                    {"name": "report_issues", "is_parallel": False},
                ],
                "analysis": [
                    {"name": "load_data", "is_parallel": False},
                    {"name": "analyze_trends", "is_parallel": True},
                    {"name": "analyze_anomalies", "is_parallel": True},
                    {"name": "summarize", "is_parallel": False},
                ],
            }
            steps_plan = type_plans.get(task.task_type, [{"name": "execute", "is_parallel": False}])

        return {"status": "ok", "steps": steps_plan, "step_count": len(steps_plan)}

    def _phase_build(self, task: PipelineTask, plan: dict) -> dict:
        """Phase 3: Execute plan steps. Parallel steps run concurrently."""
        steps = plan.get("steps", [])
        results: dict[str, Any] = {}

        # Separate parallel and sequential steps
        parallel_steps = [s for s in steps if s.get("is_parallel")]
        sequential_steps = [s for s in steps if not s.get("is_parallel")]

        # Run parallel steps concurrently
        if parallel_steps:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(4, len(parallel_steps))
            ) as executor:
                future_to_step = {
                    executor.submit(self._execute_step, s["name"], task): s["name"]
                    for s in parallel_steps
                }
                for future in concurrent.futures.as_completed(future_to_step):
                    step_name = future_to_step[future]
                    try:
                        results[step_name] = future.result(timeout=30)
                    except Exception as e:
                        results[step_name] = {"status": "error", "error": str(e)}

        # Run sequential steps in order
        for step in sequential_steps:
            results[step["name"]] = self._execute_step(step["name"], task)

        errors = [k for k, v in results.items() if v.get("status") == "error"]
        return {
            "status": "ok" if not errors else "partial",
            "results": results,
            "errors": errors,
            "parallel_steps": len(parallel_steps),
            "sequential_steps": len(sequential_steps),
        }

    def _execute_step(self, step_name: str, task: PipelineTask) -> dict:
        """Execute a single named step. If task has step objects with fn, call them."""
        step_fn: Optional[Callable] = None
        for s in task.steps:
            if s.name == step_name and callable(s.fn):
                step_fn = s.fn
                break

        if step_fn:
            try:
                result = step_fn()
                return {"status": "ok", "result": result}
            except Exception as e:
                return {"status": "error", "error": str(e)}
        else:
            # No explicit fn — mark as simulated
            return {
                "status": "ok",
                "result": f"step '{step_name}' completed (simulated)",
                "simulated": True,
            }

    def _phase_validate(self, task: PipelineTask, build: dict) -> dict:
        """Phase 4: Validate build outputs."""
        errors = build.get("errors", [])
        passed = len(errors) == 0
        return {
            "passed": passed,
            "errors": errors,
            "steps_completed": len(build.get("results", {})),
        }

    def _phase_heal(self, task: PipelineTask, validation: dict, retries: int) -> dict:
        """Phase 5: Self-heal on validation failure. Max 2 retries."""
        if retries >= 2:
            return {
                "status": "blocked",
                "message": "Max retries exceeded",
                "errors": validation.get("errors"),
            }

        failed_steps = validation.get("errors", [])
        healed = []

        for step_name in failed_steps:
            retry_result = self._execute_step(step_name, task)
            if retry_result.get("status") == "ok":
                healed.append(step_name)

        return {
            "status": "healed" if healed else "blocked",
            "healed_steps": healed,
            "still_failing": [s for s in failed_steps if s not in healed],
            "retry_count": retries + 1,
        }

    def _phase_report(self, task: PipelineTask) -> dict:
        """Phase 6: Generate execution report."""
        completed_phases = list(self._phases_completed.keys())
        total_steps = self._phases_completed.get("plan", {}).get("step_count", 0)
        errors = self._phases_completed.get("build", {}).get("errors", [])

        return {
            "status": "ok",
            "summary": (
                f"Pipeline '{task.description}' completed "
                f"{len(completed_phases)} phases, {total_steps} steps"
            ),
            "phases_run": completed_phases,
            "errors": errors,
        }

    def _phase_close(self, task: PipelineTask) -> dict:
        """Phase 7: Update task status, write to episodic memory."""
        written = False
        try:
            from jake_brain.store import BrainStore
            store = BrainStore()
            store.store_episodic(
                content=f"Pipeline completed: {task.description} ({task.task_type})",
                memory_type="pipeline_run",
                importance=0.6,
                topics=["pipeline", task.task_type],
                metadata={"run_id": self._run_id, "task_type": task.task_type},
            )
            written = True
        except Exception:
            pass

        return {"status": "ok", "memory_written": written}

    def _phase_learn(self, task: PipelineTask) -> dict:
        """Phase 8: Feed to self_improvement TIMG pipeline."""
        extracted = False
        try:
            from self_improvement.timg_pipeline import TIMGPipeline
            timg = TIMGPipeline()
            timg.extract_from_run({
                "run_id": self._run_id,
                "task_type": task.task_type,
                "phases": self._phases_completed,
            })
            extracted = True
        except Exception:
            pass

        # Also try skill generator if run was successful
        if self._phases_completed.get("validate", {}).get("passed"):
            try:
                from self_improvement.skill_generator import SkillGenerator
                gen = SkillGenerator()
                gen.generate_from_pipeline(
                    pipeline_name=task.task_type,
                    task_description=task.description,
                    task_type=task.task_type,
                    phases_completed=self._phases_completed,
                    quality_score=0.9,
                    run_id=self._run_id,
                )
            except Exception:
                pass

        return {"status": "ok", "timg_extracted": extracted}

    def _track_run(self, status: str, current_phase: str, completed: bool = False) -> None:
        """Update jake_pipeline_runs table. Handles missing table gracefully."""
        try:
            from supabase import create_client
            url = os.environ.get("SUPABASE_URL", "")
            key = os.environ.get("SUPABASE_SERVICE_KEY", "")
            if not url or not key:
                return
            client = create_client(url, key)
            record: dict[str, Any] = {
                "pipeline_name": self._pipeline_name,
                "current_phase": current_phase,
                "status": status,
                "phases_completed": self._phases_completed,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            if status == "running":
                record["started_at"] = datetime.now(timezone.utc).isoformat()
            if completed:
                record["completed_at"] = datetime.now(timezone.utc).isoformat()

            # Insert new record — table may not exist, which is fine
            client.table("jake_pipeline_runs").insert(record).execute()
        except Exception:
            pass  # Table may not exist — that's fine


# CLI runner
if __name__ == "__main__":
    import argparse
    import json

    def _cli():
        parser = argparse.ArgumentParser(description="Run autonomous pipeline")
        parser.add_argument("--task", required=True, help="Task description")
        parser.add_argument(
            "--type",
            default="maintenance",
            help="Task type: research/content/maintenance/analysis",
        )
        parser.add_argument(
            "--priority", type=int, default=3, help="Priority 1-5 (1=highest)"
        )
        parser.add_argument("--json", action="store_true", help="JSON output")
        args = parser.parse_args()

        _load_env()
        pipeline = AutonomousPipeline()
        task = PipelineTask(
            description=args.task,
            task_type=args.type,
            priority=args.priority,
        )
        result = pipeline.execute(task)

        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            status = result.get("status", "unknown")
            icon = "+" if "completed" in status else "x"
            print(f"\n[{icon}] Pipeline: {result['task']}")
            print(f"  Status: {status}")
            print(f"  Run ID: {result['run_id']}")
            phases = result.get("phases", {})
            print(f"  Phases completed: {', '.join(phases.keys())}")
            build = phases.get("build", {})
            if build.get("parallel_steps"):
                print(f"  Parallel steps: {build['parallel_steps']}")

    _cli()
