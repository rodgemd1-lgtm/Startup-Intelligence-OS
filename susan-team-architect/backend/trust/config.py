"""Blast radius caps and graduation thresholds."""
from __future__ import annotations

from typing import Optional

# These CANNOT graduate past SUPERVISED regardless of track record
_BLAST_RADIUS_CAPS: dict[str, str] = {
    "competitive-response": "SUPERVISED",
    "executive-brief": "SUPERVISED",
    "content-publish": "SUPERVISED",
}

# These CAN reach AUTONOMOUS
_AUTONOMOUS_ELIGIBLE: list[str] = [
    "daily-cycle",
    "research-refresh",
    "freshness-audit",
    "scout-signals",
]

# Graduation thresholds
SUPERVISED_MIN_RUNS = 20
SUPERVISED_MIN_ACCURACY = 90.0
AUTONOMOUS_MIN_RUNS = 50
AUTONOMOUS_MIN_ACCURACY = 95.0
AUTONOMOUS_MAX_ESCALATION = 5.0  # percent


def blast_radius_cap(chain_name: str) -> Optional[str]:
    return _BLAST_RADIUS_CAPS.get(chain_name)


def is_autonomous_eligible(chain_name: str) -> bool:
    if chain_name in _BLAST_RADIUS_CAPS:
        return False
    return chain_name in _AUTONOMOUS_ELIGIBLE
