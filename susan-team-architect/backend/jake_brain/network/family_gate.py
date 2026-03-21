"""
FamilyGate — context boundary control for family/guest access.

Mike is ADMIN — full access to everything.
James (husband) is FAMILY — home + personal, not Mike's work financials/Oracle.
Jacob (son, 15) is FAMILY — recruiting profile + family info, zero work data.
Alex (son, 12) is FAMILY — minimal, family events only.

Access model:
  ADMIN   → all domains
  FAMILY  → allowed_domains only, blocked_keywords stripped
  GUEST   → severely limited, no personal data

Usage:
    gate = FamilyGate()
    profile = gate.get_member("jacob")
    allowed, reason = gate.check(profile, "What are my recruiting stats?")
    context = gate.filter_context(profile, brain_results)
"""

from __future__ import annotations

import re
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


class AccessLevel(str, Enum):
    ADMIN = "admin"
    FAMILY = "family"
    GUEST = "guest"


@dataclass
class FamilyMember:
    name: str
    first_name: str
    access_level: AccessLevel
    telegram_username: Optional[str] = None   # for routing
    allowed_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=list)
    blocked_keywords: List[str] = field(default_factory=list)
    persona_hint: str = ""   # how Jake should talk to this person


# ── Member definitions ────────────────────────────────────────────────────────

FAMILY_ROSTER: List[FamilyMember] = [
    FamilyMember(
        name="mike_rodgers",
        first_name="Mike",
        access_level=AccessLevel.ADMIN,
        allowed_domains=["*"],
        persona_hint="co-founder, full context, sassy Jake",
    ),
    FamilyMember(
        name="james_loehr",
        first_name="James",
        access_level=AccessLevel.FAMILY,
        telegram_username=None,
        allowed_domains=[
            "family", "home", "schedule", "birthdays", "kids", "events",
            "reminders", "shopping", "travel", "general",
        ],
        blocked_domains=[
            "oracle_health", "work_email", "finance", "recruiting",
            "business", "investor", "revenue", "salary", "bank",
        ],
        blocked_keywords=[
            "oracle", "sharepoint", "quarterly", "p&l", "revenue",
            "invoice", "payroll", "raise", "termination",
        ],
        persona_hint=(
            "James is Mike's husband. Be warm and helpful. "
            "Focus on family, home, and schedule topics. "
            "Never reveal Mike's work finances, Oracle Health details, or business strategy."
        ),
    ),
    FamilyMember(
        name="jacob",
        first_name="Jacob",
        access_level=AccessLevel.FAMILY,
        telegram_username=None,
        allowed_domains=[
            "recruiting", "football", "schedule", "family", "birthdays",
            "school", "college_visits", "ncaa", "coaches", "workouts",
        ],
        blocked_domains=[
            "oracle_health", "work_email", "finance", "business",
            "personal_finance", "adult_content", "investor",
        ],
        blocked_keywords=[
            "oracle", "salary", "revenue", "p&l", "invoice", "bank",
            "alcohol", "mike's finances", "mortgage",
        ],
        persona_hint=(
            "Jacob is Mike's 15-year-old son who plays OL/DL football. "
            "He's being recruited by colleges. Be encouraging, direct, and age-appropriate. "
            "Focus on recruiting stats, school research, coach outreach, and football. "
            "Never reveal Mike's work or financial data. Keep it football-focused and motivating."
        ),
    ),
    FamilyMember(
        name="alex",
        first_name="Alex",
        access_level=AccessLevel.FAMILY,
        telegram_username=None,
        allowed_domains=["family", "schedule", "birthdays", "kids", "school", "general"],
        blocked_domains=["oracle_health", "finance", "business", "recruiting"],
        blocked_keywords=["oracle", "salary", "revenue", "recruiting", "bank"],
        persona_hint=(
            "Alex is Mike's 12-year-old son. Be friendly and age-appropriate. "
            "Only discuss family schedule, school, and general topics. "
            "Never reveal financial or work information."
        ),
    ),
]

_ROSTER_BY_NAME = {m.name: m for m in FAMILY_ROSTER}
_ROSTER_BY_FIRST = {m.first_name.lower(): m for m in FAMILY_ROSTER}


class FamilyGate:
    """Enforce context boundaries for family/guest access."""

    def get_member(self, identifier: str) -> Optional[FamilyMember]:
        """Look up by full name or first name (case-insensitive)."""
        key = identifier.lower().replace(" ", "_")
        if key in _ROSTER_BY_NAME:
            return _ROSTER_BY_NAME[key]
        first = identifier.lower()
        if first in _ROSTER_BY_FIRST:
            return _ROSTER_BY_FIRST[first]
        return None

    def check(self, member: FamilyMember, query: str) -> Tuple[bool, str]:
        """
        Check if a query is allowed for this member.
        Returns (allowed: bool, reason: str).
        """
        if member.access_level == AccessLevel.ADMIN:
            return True, "admin access"

        q_lower = query.lower()

        # Check blocked keywords
        for kw in member.blocked_keywords:
            if kw.lower() in q_lower:
                return False, f"topic '{kw}' is not accessible in this context"

        # Check blocked domains (heuristic keyword match)
        for domain in member.blocked_domains:
            domain_words = domain.replace("_", " ").split()
            if any(word in q_lower for word in domain_words if len(word) > 3):
                return False, f"domain '{domain}' is not accessible for {member.first_name}"

        return True, "allowed"

    def filter_context(
        self,
        member: FamilyMember,
        memories: List[dict],
    ) -> List[dict]:
        """
        Filter brain memories to only include content appropriate for this member.
        Memories with blocked keywords are stripped.
        """
        if member.access_level == AccessLevel.ADMIN:
            return memories

        filtered = []
        for mem in memories:
            content = str(mem.get("content", ""))
            blocked = False
            for kw in member.blocked_keywords:
                if kw.lower() in content.lower():
                    blocked = True
                    break
            if not blocked:
                filtered.append(mem)

        return filtered

    def build_system_prompt_addon(self, member: FamilyMember) -> str:
        """
        Return a persona hint + boundary reminder to prepend to Jake's system prompt
        when talking to this family member.
        """
        if member.access_level == AccessLevel.ADMIN:
            return ""

        blocked_str = ", ".join(member.blocked_domains[:6]) if member.blocked_domains else "none"
        return (
            f"\n\n---\n"
            f"FAMILY MODE — Speaking with: {member.first_name}\n"
            f"Persona: {member.persona_hint}\n"
            f"Blocked domains: {blocked_str}\n"
            f"CRITICAL: Never reveal Mike's work details, Oracle Health info, "
            f"business financials, or any blocked domain content to {member.first_name}.\n"
            f"---\n"
        )

    def list_members(self) -> List[dict]:
        return [
            {
                "name": m.name,
                "first_name": m.first_name,
                "access_level": m.access_level.value,
                "allowed_domains": m.allowed_domains,
                "blocked_domains": m.blocked_domains,
            }
            for m in FAMILY_ROSTER
        ]
