"""Trust Enforcer — checks autonomy level before publishing chain output."""
from __future__ import annotations

from typing import Literal

from trust.tracker import TrustTracker


class TrustEnforcer:
    def __init__(self, tracker: TrustTracker) -> None:
        self._tracker = tracker

    def check(self, chain_name: str) -> Literal["PUBLISH", "STAGE", "BLOCK"]:
        profile = self._tracker.get_profile(chain_name)
        if profile.level == "AUTONOMOUS":
            return "PUBLISH"
        return "STAGE"  # MANUAL and SUPERVISED both stage for human review
