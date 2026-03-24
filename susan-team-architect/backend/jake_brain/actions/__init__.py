"""Jake's Hands — action execution engine.

Phase 5 of the 9-phase Jake architecture.

Safety tiers:
  Tier 1 (AUTO):    Execute immediately. Read-only ops, Telegram, reminders.
  Tier 2 (CONFIRM): Show preview → Mike reacts ✅/❌ in Telegram before executing.
  Tier 3 (APPROVE): Require explicit written approval. Production / financial / external-facing.

Every executed action is logged to jake_episodic (source_type='action').
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
    message: str                        # Human-readable summary
    data: dict[str, Any] = field(default_factory=dict)  # Raw response payload
    error: str | None = None


class BaseAction:
    """Abstract base for all Jake actions.

    Subclasses must implement:
      - tier: SafetyTier
      - preview() → str   (what Jake *would* do, no side effects)
      - execute() → ActionResult  (the real thing)
    """

    tier: SafetyTier = SafetyTier.CONFIRM  # default; subclasses override
    name: str = "unnamed_action"
    description: str = ""

    def preview(self) -> str:
        """Return a human-readable description of what will happen."""
        raise NotImplementedError

    def execute(self) -> ActionResult:
        """Perform the action and return an ActionResult."""
        raise NotImplementedError

    def to_dict(self) -> dict:
        return {
            "action": self.name,
            "tier": int(self.tier),
            "tier_name": self.tier.name,
            "description": self.description,
            "preview": self.preview(),
        }


# ---------------------------------------------------------------------------
# Registry — maps action name → class
# ---------------------------------------------------------------------------

_registry: dict[str, type[BaseAction]] = {}


def register(cls: type[BaseAction]) -> type[BaseAction]:
    """Decorator to register an action class."""
    _registry[cls.name] = cls
    return cls


def get_action(name: str) -> type[BaseAction] | None:
    return _registry.get(name)


def list_actions() -> list[dict]:
    return [
        {"name": name, "tier": int(cls.tier), "description": cls.description}
        for name, cls in _registry.items()
    ]
