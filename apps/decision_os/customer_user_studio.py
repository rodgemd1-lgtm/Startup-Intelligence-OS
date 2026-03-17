from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import re
import shutil
import subprocess
import yaml


@dataclass
class ValidationResult:
    path: str
    valid: bool
    errors: list[str]


class CustomerUserStudio:
    """Operational helpers for Customer User Studio artifacts.

    This module intentionally uses simple file-backed contracts under `.startup-os/`
    so it remains compatible with the existing Susan runtime.
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.cwd()
        self.scenarios_dir = self.root / ".startup-os" / "artifacts" / "customer-user-studio" / "scenarios"
        self.personas_dir = self.root / ".startup-os" / "artifacts" / "customer-user-studio" / "personas"
        self.sessions_dir = self.root / ".startup-os" / "artifacts" / "customer-user-studio" / "sessions"
        self.reports_dir = self.root / ".startup-os" / "artifacts" / "customer-user-studio" / "reports"
        self.schema_dir = self.root / ".startup-os" / "schemas"

    def ensure_dirs(self) -> None:
        for d in (self.scenarios_dir, self.personas_dir, self.sessions_dir, self.reports_dir):
            d.mkdir(parents=True, exist_ok=True)

    def seed(self) -> dict[str, str]:
        """Create one runnable sample persona, scenario, and session evidence artifact."""
        self.ensure_dirs()
        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

        persona = {
            "id": f"customer-persona-founder-operator-{ts}",
            "name": "Founder Operator",
            "segment": "founder-operator",
            "applications": ["operator-console"],
            "goals": ["validate release readiness", "prioritize roadmap based on customer friction"],
            "constraints": ["limited time", "prefers clear next actions"],
            "preferences": {
                "likes": ["fast onboarding", "clear state visibility"],
                "dislikes": ["ambiguous errors", "hidden controls"],
                "future_wants": ["explainable recommendations", "release risk dashboard"],
            },
            "behavioral_profile": {
                "proficiency": "intermediate",
                "risk_tolerance": "medium",
                "patience_budget_minutes": 12,
            },
            "evidence_links": [],
        }

        scenario = {
            "id": f"customer-scenario-onboarding-health-check-{ts}",
            "app_id": "operator-console",
            "persona_id": persona["id"],
            "objective": "Complete onboarding-style release health check and collect recommendation output",
            "entry_state": {"logged_in": True, "workspace": "startup-intelligence-os"},
            "tasks": [
                {
                    "step_id": "step-1",
                    "action": "Open dashboard and confirm active workspace context",
                    "expected_outcome": "Workspace and project context visible",
                    "fallback_action": "Use context command fallback",
                },
                {
                    "step_id": "step-2",
                    "action": "Run status and sync intel workflows",
                    "expected_outcome": "Current counts and debrief generated",
                    "fallback_action": "Retry after refresh",
                },
            ],
            "success_criteria": [
                "Context visible",
                "Status command completes",
                "At least one actionable recommendation produced",
            ],
            "adaptation_rules": [
                {
                    "trigger": "If status command errors",
                    "adaptation": "Collect error trace and run alternate command path",
                }
            ],
            "instrumentation": {
                "capture_console_errors": True,
                "capture_network_failures": True,
                "capture_replay": True,
            },
        }

        session = {
            "id": f"customer-session-seed-{ts}",
            "app_id": "operator-console",
            "persona_id": persona["id"],
            "scenario_id": scenario["id"],
            "run_at": datetime.now(timezone.utc).isoformat(),
            "result": {
                "status": "warn",
                "completion_rate": 0.8,
                "critical_errors": 0,
                "frustration_index": 0.2,
            },
            "findings": [
                {
                    "type": "friction",
                    "summary": "Operator needed an extra step to find debrief command",
                    "severity": "medium",
                    "evidence": "session-replay://seed",
                },
                {
                    "type": "request",
                    "summary": "Add one-click daily summary in console",
                    "severity": "low",
                    "evidence": "interview://seed",
                },
            ],
            "preference_signals": {
                "likes": ["clear command list"],
                "dislikes": ["non-obvious command ordering"],
                "future_wants": ["priority-ranked next action card"],
            },
            "roadmap_candidates": [
                {
                    "theme": "operator-experience",
                    "candidate": "daily-summary-card",
                    "impact": "medium",
                    "confidence": "medium",
                }
            ],
            "evidence_links": ["session-replay://seed", "interview://seed"],
        }

        persona_path = self.personas_dir / f"{persona['id']}.yaml"
        scenario_path = self.scenarios_dir / f"{scenario['id']}.yaml"
        session_path = self.sessions_dir / f"{session['id']}.yaml"
        persona_path.write_text(yaml.safe_dump(persona, sort_keys=False))
        scenario_path.write_text(yaml.safe_dump(scenario, sort_keys=False))
        session_path.write_text(yaml.safe_dump(session, sort_keys=False))

        return {
            "persona": str(persona_path.relative_to(self.root)),
            "scenario": str(scenario_path.relative_to(self.root)),
            "session": str(session_path.relative_to(self.root)),
        }

    def _required(self, schema_name: str) -> list[str]:
        schema = yaml.safe_load((self.schema_dir / schema_name).read_text()) or {}
        return list(schema.get("required", []))

    def validate_file(self, path: Path) -> ValidationResult:
        data = yaml.safe_load(path.read_text()) or {}
        lower = path.name
        if lower.startswith("customer-persona"):
            req = self._required("customer-persona.schema.yaml")
        elif lower.startswith("customer-scenario"):
            req = self._required("customer-scenario.schema.yaml")
        elif lower.startswith("customer-session"):
            req = self._required("customer-session-evidence.schema.yaml")
        else:
            return ValidationResult(str(path), True, [])

        errs = [f"missing required field: {k}" for k in req if k not in data]
        if "id" in data and not re.match(r"^[a-z0-9-]+$", str(data["id"])):
            errs.append("id must be kebab-case")
        return ValidationResult(str(path), not errs, errs)

    def validate_all(self) -> list[ValidationResult]:
        self.ensure_dirs()
        results: list[ValidationResult] = []
        for d in (self.personas_dir, self.scenarios_dir, self.sessions_dir):
            for p in sorted(d.glob("*.yaml")):
                results.append(self.validate_file(p))
        return results

    def generate_ranked_opportunities(self) -> Path:
        self.ensure_dirs()
        priorities: list[dict[str, Any]] = []
        weight = {"low": 1, "medium": 2, "high": 3, "critical": 5}

        for p in sorted(self.sessions_dir.glob("*.yaml")):
            data = yaml.safe_load(p.read_text()) or {}
            for finding in data.get("findings", []):
                severity = str(finding.get("severity", "low"))
                score = weight.get(severity, 1)
                priorities.append(
                    {
                        "session_id": data.get("id"),
                        "app_id": data.get("app_id"),
                        "issue_type": finding.get("type"),
                        "summary": finding.get("summary"),
                        "severity": severity,
                        "priority_score": score,
                        "evidence": finding.get("evidence"),
                    }
                )

        priorities.sort(key=lambda x: x["priority_score"], reverse=True)
        output = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "count": len(priorities),
            "opportunities": priorities,
        }
        out_path = self.reports_dir / "ranked-opportunities.yaml"
        out_path.write_text(yaml.safe_dump(output, sort_keys=False))
        return out_path

    def push_to_susan_backend(self, backend_root: Path | None = None) -> dict[str, Any]:
        """Copy Customer User Studio artifacts into Susan backend data surface.

        Destination: `susan-team-architect/backend/data/startup_os/customer_user_studio/`
        """
        self.ensure_dirs()
        backend = backend_root or (self.root / "susan-team-architect" / "backend")
        target_root = backend / "data" / "startup_os" / "customer_user_studio"
        target_root.mkdir(parents=True, exist_ok=True)

        copied: list[str] = []
        for rel in [
            Path("personas"),
            Path("scenarios"),
            Path("sessions"),
            Path("reports"),
        ]:
            src_dir = self.root / ".startup-os" / "artifacts" / "customer-user-studio" / rel
            dst_dir = target_root / rel
            dst_dir.mkdir(parents=True, exist_ok=True)
            for src in sorted(src_dir.glob("*.yaml")):
                dst = dst_dir / src.name
                shutil.copy2(src, dst)
                copied.append(str(dst.relative_to(self.root)))

        index_payload = {
            "id": "customer-user-studio-backend-sync",
            "synced_at": datetime.now(timezone.utc).isoformat(),
            "source_root": ".startup-os/artifacts/customer-user-studio",
            "target_root": str(target_root.relative_to(self.root)),
            "files_synced": copied,
            "count": len(copied),
        }
        index_path = target_root / "sync-index.yaml"
        index_path.write_text(yaml.safe_dump(index_payload, sort_keys=False))

        return {
            "target_root": str(target_root.relative_to(self.root)),
            "index": str(index_path.relative_to(self.root)),
            "count": len(copied),
            "files": copied,
        }

    def publish_bundle(self, local_drive_root: Path | None = None) -> dict[str, Any]:
        """Publish Customer User Studio outputs to Susan backend and local-drive mirror."""
        self.ensure_dirs()

        # Always refresh ranked opportunities before publish
        report_path = self.generate_ranked_opportunities()
        backend_result = self.push_to_susan_backend()

        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        publish_root = self.root / ".startup-os" / "artifacts" / "customer-user-studio" / "publish" / ts
        publish_root.mkdir(parents=True, exist_ok=True)

        source_root = self.root / ".startup-os" / "artifacts" / "customer-user-studio"
        shutil.copy2(report_path, publish_root / "ranked-opportunities.yaml")

        git_commit = "unknown"
        try:
            git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip()
        except Exception:
            pass

        manifest = {
            "id": "customer-user-studio-publish",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "git_commit": git_commit,
            "source_root": str(source_root.relative_to(self.root)),
            "backend_sync": backend_result,
            "local_drive_path": None,
        }

        local_target = None
        if local_drive_root is not None:
            local_target = local_drive_root / "customer-user-studio"
            if local_target.exists():
                shutil.rmtree(local_target)
            shutil.copytree(source_root, local_target)
            manifest["local_drive_path"] = str(local_target)

        manifest_path = publish_root / "publish-manifest.yaml"
        manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False))

        return {
            "publish_root": str(publish_root.relative_to(self.root)),
            "manifest": str(manifest_path.relative_to(self.root)),
            "backend_index": backend_result["index"],
            "local_drive_path": str(local_target) if local_target else None,
        }
