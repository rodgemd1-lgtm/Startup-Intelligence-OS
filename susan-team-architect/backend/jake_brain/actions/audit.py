"""Action audit logger — writes every executed action to jake_episodic."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("jake-actions")


def log_action(
    action_name: str,
    tier: int,
    preview_text: str,
    result_success: bool,
    result_message: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Log an action execution to jake_episodic. Non-blocking — errors are swallowed."""
    try:
        import sys, os
        SUSAN_BACKEND = "/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend"
        if SUSAN_BACKEND not in sys.path:
            sys.path.insert(0, SUSAN_BACKEND)

        from jake_brain.store import BrainStore

        store = BrainStore()
        status = "success" if result_success else "failed"
        content = (
            f"Action executed: {action_name} (tier {tier})\n"
            f"Preview: {preview_text}\n"
            f"Result: {status} — {result_message}"
        )
        store.store_episodic(
            content=content,
            occurred_at=datetime.now(timezone.utc),
            memory_type="action",
            importance=0.6,
            topics=["action", action_name, status],
            source=action_name,
            source_type="action",
            metadata={
                "action_name": action_name,
                "tier": tier,
                "status": status,
                "result_message": result_message,
                **(metadata or {}),
            },
        )
    except Exception as exc:
        # Never let audit failure break the action itself
        logger.warning("Audit log failed for %s: %s", action_name, exc)
