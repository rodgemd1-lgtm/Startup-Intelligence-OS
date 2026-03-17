"""
Research Daemon — Layer 5 Autonomous Research Engine for Startup Intelligence OS.

Detects knowledge gaps, monitors dependency changelogs, harvests research
material, scores quality, and orchestrates full research cycles.

Usage:
    python -m research_daemon --command detect-gaps
    python -m research_daemon --command check-updates
    python -m research_daemon --command harvest
    python -m research_daemon --command digest
    python -m research_daemon --command status
    python -m research_daemon --command cycle
"""

from research_daemon.schemas import (
    ResearchGap,
    HarvestResult,
    ChangelogEntry,
    ResearchProgram,
    DaemonStatus,
)
from research_daemon.gap_detector import GapDetector
from research_daemon.changelog_monitor import ChangelogMonitor
from research_daemon.auto_harvest import AutoHarvester
from research_daemon.quality_scorer import QualityScorer
from research_daemon.daemon import ResearchDaemon

__all__ = [
    "ResearchGap",
    "HarvestResult",
    "ChangelogEntry",
    "ResearchProgram",
    "DaemonStatus",
    "GapDetector",
    "ChangelogMonitor",
    "AutoHarvester",
    "QualityScorer",
    "ResearchDaemon",
]
