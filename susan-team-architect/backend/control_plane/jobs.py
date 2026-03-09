"""Background Susan run manager for application-facing orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
import json
from pathlib import Path
import subprocess
import threading
import uuid

from susan_core.config import config
from .writeback import write_foundry_records_for_output_dir


OUTPUT_FILES = {
    "profile": "company-profile.json",
    "problem_framing": "problem-framing.json",
    "capability_diagnosis": "capability-diagnosis.json",
    "evidence_gap_map": "evidence-gap-map.json",
    "decision_brief": "decision-brief.json",
    "analysis": "analysis-report.json",
    "team": "team-manifest.json",
    "datasets": "dataset-requirements.json",
    "execution": "execution-plan.md",
    "execution_blueprint": "execution-blueprint.md",
    "behavioral_economics": "be-audit.json",
    "foundry_blueprint": "foundry-blueprint.json",
    "foundry_writeback": "foundry-writeback.json",
}


@dataclass
class SusanJobState:
    id: str
    company: str
    mode: str
    refresh: bool
    status: str
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    pid: int | None = None
    output_dir: str | None = None
    log_path: str | None = None
    cache_hit: bool = False
    result_files: dict[str, str] = field(default_factory=dict)
    dedupe_key: str | None = None
    error: str | None = None


class SusanRunManager:
    def __init__(self, autostart: bool = True) -> None:
        self.lock = threading.Lock()
        self.jobs: dict[str, SusanJobState] = {}
        self.processes: dict[str, subprocess.Popen] = {}
        self.autostart = autostart
        self.queue_dir = config.artifacts_dir / "run_queue"
        self.queue_dir.mkdir(parents=True, exist_ok=True)

    def _collect_result_files(self, output_dir: Path) -> dict[str, str]:
        files: dict[str, str] = {}
        for key, filename in OUTPUT_FILES.items():
            path = output_dir / filename
            if path.exists():
                files[key] = str(path)
        return files

    def _outputs_exist(self, state: SusanJobState) -> bool:
        if state.result_files:
            return True
        if not state.output_dir:
            return False
        return bool(self._collect_result_files(Path(state.output_dir)))

    def _completed_candidates(self, company: str, mode: str, max_age_minutes: int) -> list[SusanJobState]:
        cutoff = datetime.now(UTC) - timedelta(minutes=max_age_minutes)
        matches = [
            state for state in self.jobs.values()
            if state.company == company
            and state.mode == mode
            and state.status == "completed"
            and state.finished_at is not None
            and state.finished_at >= cutoff
            and self._outputs_exist(state)
        ]
        return sorted(matches, key=lambda item: item.finished_at or item.created_at, reverse=True)

    def submit(
        self,
        company: str,
        mode: str = "quick",
        refresh: bool = False,
        prefer_cached: bool = True,
        max_age_minutes: int = 240,
    ) -> SusanJobState:
        dedupe_key = f"{company}:{mode}:{int(refresh)}"
        with self.lock:
            if prefer_cached and not refresh:
                cached = self._completed_candidates(company, mode, max_age_minutes)
                if cached:
                    cached[0].cache_hit = True
                    cached[0].result_files = self._collect_result_files(Path(cached[0].output_dir or ""))
                    return cached[0]

            for state in self.jobs.values():
                if state.dedupe_key == dedupe_key and state.status in {"queued", "running"}:
                    state.cache_hit = False
                    return state

            job_id = f"susan-{uuid.uuid4().hex[:12]}"
            output_dir = config.companies_dir / company / "susan-outputs"
            log_path = self.queue_dir / f"{job_id}.log"
            state = SusanJobState(
                id=job_id,
                company=company,
                mode=mode,
                refresh=refresh,
                status="queued",
                created_at=datetime.now(UTC),
                output_dir=str(output_dir),
                log_path=str(log_path),
                cache_hit=False,
                dedupe_key=dedupe_key,
            )
            self.jobs[job_id] = state

        if self.autostart:
            thread = threading.Thread(target=self._run_job, args=(job_id,), daemon=True)
            thread.start()
        return state

    def _run_job(self, job_id: str) -> None:
        with self.lock:
            state = self.jobs[job_id]
            state.status = "running"
            state.started_at = datetime.now(UTC)

        output_dir = Path(state.output_dir or "")
        output_dir.mkdir(parents=True, exist_ok=True)
        log_path = Path(state.log_path or self.queue_dir / f"{job_id}.log")
        cmd = [
            str(config.base_dir / ".venv" / "bin" / "python"),
            "-m",
            "susan_core.orchestrator",
            "--company",
            state.company,
            "--mode",
            state.mode,
            "--output-dir",
            str(output_dir),
        ]
        if state.refresh:
            cmd.append("--refresh")

        with log_path.open("w", encoding="utf-8") as log_handle:
            process = subprocess.Popen(
                cmd,
                cwd=config.base_dir,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
            )
            with self.lock:
                self.processes[job_id] = process
                state.pid = process.pid
            return_code = process.wait()

        with self.lock:
            state.finished_at = datetime.now(UTC)
            self.processes.pop(job_id, None)
            if return_code == 0:
                state.status = "completed"
            else:
                state.status = "failed"
                state.error = f"Process exited with code {return_code}"

        if return_code == 0:
            try:
                writeback = write_foundry_records_for_output_dir(job_id, state.company, output_dir)
                (output_dir / "foundry-writeback.json").write_text(
                    json.dumps(writeback, indent=2),
                    encoding="utf-8",
                )
            except Exception as exc:
                state.error = f"Writeback failed: {exc}"

        with self.lock:
            state.result_files = self._collect_result_files(output_dir)

    def get(self, job_id: str) -> SusanJobState | None:
        with self.lock:
            return self.jobs.get(job_id)

    def list(self, company: str | None = None) -> list[SusanJobState]:
        with self.lock:
            states = list(self.jobs.values())
        if company:
            states = [state for state in states if state.company == company]
        return sorted(states, key=lambda item: item.created_at, reverse=True)

    def log_text(self, job_id: str) -> str:
        state = self.get(job_id)
        if not state or not state.log_path:
            return ""
        path = Path(state.log_path)
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    def outputs(self, job_id: str) -> dict[str, object]:
        state = self.get(job_id)
        if not state:
            return {}

        result_files = state.result_files or self._collect_result_files(Path(state.output_dir or ""))
        payload: dict[str, object] = {}
        for key, path_str in result_files.items():
            path = Path(path_str)
            if not path.exists():
                continue
            if path.suffix == ".json":
                payload[key] = json.loads(path.read_text(encoding="utf-8"))
            else:
                payload[key] = path.read_text(encoding="utf-8")
        return payload


manager = SusanRunManager()
