"""File-backed persistence for Decision OS domain objects.

Each object type is stored as individual YAML files in the .startup-os/ tree
or in app-local runtime data. The store handles CRUD, schema validation via
Pydantic, and lightweight workspace accessors.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Type, TypeVar

import yaml
from pydantic import BaseModel

from .models import (
    ActionPacket,
    Artifact,
    Capability,
    Company,
    Decision,
    DepartmentPack,
    Evidence,
    GraphLink,
    Run,
    Session,
    SignalEvent,
    Project,
    _now,
)

T = TypeVar("T", bound=BaseModel)


def root_dir() -> Path:
    return Path(os.environ.get("DECISION_OS_ROOT", Path(__file__).resolve().parents[2]))


def startup_os_dir() -> Path:
    return root_dir() / ".startup-os"


def data_dir() -> Path:
    return root_dir() / "apps" / "decision_os" / "data"


_ROOT = root_dir()
_STARTUP_OS = startup_os_dir()
_DATA = data_dir()


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


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
        if raw is None:
            return None
        return self._model.model_validate(raw)

    def delete(self, obj_id: str) -> bool:
        path = self._path(obj_id)
        if path.exists():
            path.unlink()
            return True
        return False

    def list_all(self) -> list[T]:
        results: list[T] = []
        for path in sorted(self._dir.glob(f"*{self._suffix}")):
            if path.name.startswith("."):
                continue
            try:
                raw = yaml.safe_load(path.read_text())
                if raw:
                    results.append(self._model.model_validate(raw))
            except Exception:
                continue
        return results

    def count(self) -> int:
        return len(
            [
                path
                for path in self._dir.glob(f"*{self._suffix}")
                if not path.name.startswith(".")
            ]
        )


class DecisionStore(Repository):
    def __init__(self) -> None:
        super().__init__(Decision, startup_os_dir() / "decisions")

    def _path(self, obj_id: str) -> Path:
        return self._dir / f"{obj_id}.yaml"


class CapabilityStore(Repository):
    def __init__(self) -> None:
        super().__init__(Capability, startup_os_dir() / "capabilities")


class ProjectStore(Repository):
    def __init__(self) -> None:
        super().__init__(Project, startup_os_dir() / "projects")


class CompanyStore(Repository):
    def __init__(self) -> None:
        super().__init__(Company, startup_os_dir() / "companies")


class DepartmentStore(Repository):
    def __init__(self) -> None:
        super().__init__(DepartmentPack, startup_os_dir() / "departments")


class SignalStore(Repository):
    def __init__(self) -> None:
        super().__init__(SignalEvent, startup_os_dir() / "signals")


class ActionPacketStore(Repository):
    def __init__(self) -> None:
        super().__init__(ActionPacket, startup_os_dir() / "action-packets")


class GraphLinkStore(Repository):
    def __init__(self) -> None:
        super().__init__(GraphLink, startup_os_dir() / "graph-links")


class RunStore(Repository):
    def __init__(self) -> None:
        super().__init__(Run, data_dir() / "runs")


class SessionStore(Repository):
    def __init__(self) -> None:
        super().__init__(Session, data_dir() / "sessions")


class ArtifactStore(Repository):
    def __init__(self) -> None:
        super().__init__(Artifact, data_dir() / "artifacts")


class EvidenceStore(Repository):
    def __init__(self) -> None:
        super().__init__(Evidence, data_dir() / "evidence")


class Store:
    """Unified access to all object repositories."""

    def __init__(self) -> None:
        self.root = root_dir()
        self.startup_os = startup_os_dir()
        self.data = data_dir()
        self.decisions = DecisionStore()
        self.capabilities = CapabilityStore()
        self.projects = ProjectStore()
        self.companies = CompanyStore()
        self.departments = DepartmentStore()
        self.signals = SignalStore()
        self.action_packets = ActionPacketStore()
        self.graph_links = GraphLinkStore()
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
            "departments": self.departments.count(),
            "signals": self.signals.count(),
            "action_packets": self.action_packets.count(),
            "graph_links": self.graph_links.count(),
            "runs": self.runs.count(),
            "sessions": self.sessions.count(),
            "artifacts": self.artifacts.count(),
            "evidence": self.evidence.count(),
        }

    def context(self) -> dict:
        workspace_path = self.startup_os / "workspace.yaml"
        if workspace_path.exists():
            return yaml.safe_load(workspace_path.read_text()) or {}
        return {}

    def load_yaml_collection(self, directory: Path, recursive: bool = False) -> list[dict]:
        pattern = "**/*.yaml" if recursive else "*.yaml"
        results: list[dict] = []
        for path in sorted(directory.glob(pattern)):
            if path.name.startswith(".") or path.name == "README.md":
                continue
            try:
                raw = yaml.safe_load(path.read_text())
            except Exception:
                continue
            if not raw:
                continue
            if isinstance(raw, dict):
                record = dict(raw)
                record.setdefault("_path", str(path.relative_to(self.root)))
                record.setdefault("_stem", path.stem)
                results.append(record)
        return results

    def get_capability_levels(self, capability_id: str) -> dict | None:
        path = self.startup_os / "capabilities" / f"{capability_id}.yaml"
        if not path.exists():
            return None
        return yaml.safe_load(path.read_text())

    def toggle_capability_item(self, capability_id: str, level: int, index: int) -> dict | None:
        path = self.startup_os / "capabilities" / f"{capability_id}.yaml"
        if not path.exists():
            return None
        data = yaml.safe_load(path.read_text())
        levels = data.get("levels", {})
        level_data = levels.get(level)
        if not level_data or index < 0 or index >= len(level_data.get("items", [])):
            return None
        level_data["items"][index]["done"] = not level_data["items"][index]["done"]

        computed_maturity = 0
        for current_level in sorted(levels.keys()):
            items = levels[current_level].get("items", [])
            if items and all(item.get("done") for item in items):
                computed_maturity = current_level
            else:
                break

        current = data.get("maturity_current", 0)
        if computed_maturity > current:
            data["maturity_current"] = computed_maturity
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
        return data
