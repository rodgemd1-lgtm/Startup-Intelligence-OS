"""
Jake Network Layer — Phase 9: THE NETWORK
Presence detection, interface-appropriate formatting, family access control.
"""

from .presence import PresenceManager, Interface, PresenceState
from .formatter import InterfaceFormatter
from .family_gate import FamilyGate, AccessLevel, FamilyMember

__all__ = [
    "PresenceManager", "Interface", "PresenceState",
    "InterfaceFormatter",
    "FamilyGate", "AccessLevel", "FamilyMember",
]
