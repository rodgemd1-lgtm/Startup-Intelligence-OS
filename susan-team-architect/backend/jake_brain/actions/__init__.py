"""Jake's Hands — action execution engine.

DEPRECATED 2026-03-24: Hermes action engine replaced by OpenClaw gateway + PAI.
Action implementations archived to archive/hermes-actions/.
This stub preserves the base classes so existing imports don't break.

Migration: OpenClaw handles Telegram, tools, and skills natively.
"""

from __future__ import annotations

from enum import IntEnum
from dataclasses import dataclass, field
from typing import Any


class SafetyTier(IntEnum):
    AUTO = 1
    CONFIRM = 2
    APPROVE = 3


@dataclass
class ActionResult:
    """Result returned from any action's execute() call."""
    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class BaseAction:
    """Abstract base for all Jake actions. DEPRECATED — use OpenClaw skills."""

    tier: SafetyTier = SafetyTier.CONFIRM
    name: str = "unnamed_action"
    description: str = ""

    def preview(self) -> str:
        raise NotImplementedError

    def execute(self) -> ActionResult:
        raise NotImplementedError


_registry: dict[str, type[BaseAction]] = {}


def register(cls: type[BaseAction]) -> type[BaseAction]:
    _registry[cls.name] = cls
    return cls


def get_action(name: str) -> type[BaseAction] | None:
    return _registry.get(name)


def list_actions() -> list[dict]:
    return [
        {"name": name, "tier": int(cls.tier), "description": cls.description}
        for name, cls in _registry.items()
    ]
