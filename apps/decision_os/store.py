"""File-backed persistence for Decision OS domain objects.

Each object type is stored as individual YAML files in the .startup-os/ tree.
The store handles CRUD, schema validation via Pydantic, and cross-references.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TypeVar, Type

import yaml
from pydantic import BaseModel

from .models import (
    Decision, Capability, Project, Company, Run, Session, Artifact, Evidence,
    _now,
)

T = TypeVar("T", bound=BaseModel)

_ROOT = Path(os.environ.get("DECISION_OS_ROOT", Path(__file__).resolve().parents[2]))
_STARTUP_OS = _ROOT / ".startup-os"
_DATA = _ROOT / "apps" / "decision_os" / "data"


def _ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


# --- Generic file-backed repository ---

class Repository:
    """Generic YAML-file-backed repository for a Pydantic model."""

    def __init__(self, model_cls: Type[T], directory: Path, suffix: str = ".yaml"):
        self._model = model_cls
        self._dir = _ensure_dir(directory)
        self._suffix = suffix

    def _path(self, obj_id: str) -> Path:
        safe = obj_id.replace("/", "_")
        return self._dir / f"{safe}{self._suffix}"

    def save(self, obj: T) -> T:
        obj_id = getattr(obj, "id", None)
        if not obj_id:
            raise ValueError(f"Object has no id: {obj}")
        if hasattr(obj, "updated_at"):
            object.__setattr__(obj, "updated_at", _now())
        path = self._path(obj_id)
        data = obj.model_dump(mode="json")
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
        return obj

    def get(self, obj_id: str) -> T | None:
        path = self._path(obj_id)
        if not path.exists():
            return None
        raw = yaml.safe_load(path.read_text())
        return self._model.model_validate(raw)

    def delete(self, obj_id: str) -> bool:
        path = self._path(obj_id)
        if path.exists():
            path.unlink()
            return True
        return False

    def list_all(self) -> list[T]:
        results = []
        for p in sorted(self._dir.glob(f"*{self._suffix}")):
            if p.name.startswith("."):
                continue
            try:
                raw = yaml.safe_load(p.read_text())
                if raw:
                    results.append(self._model.model_validate(raw))
            except Exception:
                continue
        return results

    def count(self) -> int:
        return len([p for p in self._dir.glob(f"*{self._suffix}")
                     if not p.name.startswith(".")])


# --- Specialized stores ---

class DecisionStore(Repository):
    def __init__(self) -> None:
        super().__init__(Decision, _STARTUP_OS / "decisions")

    def _path(self, obj_id: str) -> Path:
        return self._dir / f"{obj_id}.yaml"


class CapabilityStore(Repository):
    def __init__(self) -> None:
        super().__init__(Capability, _STARTUP_OS / "capabilities")


class ProjectStore(Repository):
    def __init__(self) -> None:
        super().__init__(Project, _STARTUP_OS / "projects")


class CompanyStore(Repository):
    def __init__(self) -> None:
        super().__init__(Company, _STARTUP_OS / "companies")


class RunStore(Repository):
    def __init__(self) -> None:
        super().__init__(Run, _DATA / "runs")


class SessionStore(Repository):
    def __init__(self) -> None:
        super().__init__(Session, _DATA / "sessions")


class ArtifactStore(Repository):
    def __init__(self) -> None:
        super().__init__(Artifact, _DATA / "artifacts")


class EvidenceStore(Repository):
    def __init__(self) -> None:
        super().__init__(Evidence, _DATA / "evidence")


# --- Convenience singleton ---

class Store:
    """Unified access to all object repositories."""

    def __init__(self) -> None:
        self.decisions = DecisionStore()
        self.capabilities = CapabilityStore()
        self.projects = ProjectStore()
        self.companies = CompanyStore()
        self.runs = RunStore()
        self.sessions = SessionStore()
        self.artifacts = ArtifactStore()
        self.evidence = EvidenceStore()

    def status(self) -> dict:
        return {
            "decisions": self.decisions.count(),
            "capabilities": self.capabilities.count(),
            "projects": self.projects.count(),
            "companies": self.companies.count(),
            "runs": self.runs.count(),
            "sessions": self.sessions.count(),
            "artifacts": self.artifacts.count(),
            "evidence": self.evidence.count(),
        }

    def context(self) -> dict:
        workspace_path = _STARTUP_OS / "workspace.yaml"
        if workspace_path.exists():
            return yaml.safe_load(workspace_path.read_text()) or {}
        return {}

    def get_capability_levels(self, capability_id: str) -> dict | None:
        """Read capability YAML and return levels structure."""
        path = _STARTUP_OS / "capabilities" / f"{capability_id}.yaml"
        if not path.exists():
            return None
        data = yaml.safe_load(path.read_text())
        return data

    def toggle_capability_item(self, capability_id: str, level: int, index: int) -> dict | None:
        """Toggle a checklist item in a capability level."""
        path = _STARTUP_OS / "capabilities" / f"{capability_id}.yaml"
        if not path.exists():
            return None
        data = yaml.safe_load(path.read_text())
        levels = data.get("levels", {})
        level_data = levels.get(level)
        if not level_data or index < 0 or index >= len(level_data.get("items", [])):
            return None
        level_data["items"][index]["done"] = not level_data["items"][index]["done"]
        # Auto-compute checklist maturity: highest level where all items are done
        computed_maturity = 0
        for lvl in sorted(levels.keys()):
            items = levels[lvl].get("items", [])
            if items and all(item.get("done") for item in items):
                computed_maturity = lvl
            else:
                break
        # Only advance maturity_current when checklist maturity exceeds it
        # (preserves fractional human-assessed values until checklist proves higher)
        current = data.get("maturity_current", 0)
        if computed_maturity > current:
            data["maturity_current"] = computed_maturity
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
        return data
