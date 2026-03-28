"""Oracle Health Department — Intelligence, Content, and Sales Enablement.

This module implements the Oracle Health department orchestration:
- Director: routes work to super-agents
- Market Intelligence: competitive monitoring, signal triage
- Content & Positioning: messaging, persona banks, proof stacks
- Sales Enablement: battlecards, objections, assets
- Oracle Sentinel: autonomous daily monitoring

Usage:
    python -m oracle_health --command status
    python -m oracle_health --command signals
    python -m oracle_health --command battlecard --competitor epic
    python -m oracle_health --command brief
    python -m oracle_health --command freshness
"""

__all__ = [
    "director",
    "signals",
    "battlecards",
    "freshness",
]
