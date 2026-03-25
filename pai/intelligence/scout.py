"""SCOUT Competitive Intelligence Pipeline — V4 Proactive Intelligence

Monitors competitive landscape across all 3 companies:
  - Startup Intelligence OS (PAI/OpenClaw space)
  - Oracle Health (health IT, EHR, AI clinical)
  - Alex Recruiting (sports recruiting tech)

Surfaces P0/P1 signals, content white space, and market moves.
Runs daily at 5 AM before the morning brief.

Sources:
  - RSS feeds (company blogs, product updates)
  - Hacker News / Product Hunt (new launches)
  - LinkedIn (hiring signals)
  - GitHub (feature releases)
  - Susan RAG (existing competitive data)
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class SignalPriority(str, Enum):
    P0 = "P0"  # Competitor launched something that directly threatens us
    P1 = "P1"  # Market shift worth tracking
    P2 = "P2"  # Interesting but not urgent


class SignalCategory(str, Enum):
    PRODUCT_LAUNCH = "product_launch"
    FUNDING = "funding"
    HIRING = "hiring"
    PARTNERSHIP = "partnership"
    MARKET_SHIFT = "market_shift"
    CONTENT_GAP = "content_gap"
    FEATURE_RELEASE = "feature_release"
    REGULATORY = "regulatory"
    PRICING = "pricing"


@dataclass
class CompetitiveSignal:
    """A single competitive intelligence signal."""
    title: str
    company: str  # which of our 3 companies this affects
    competitor: str
    category: SignalCategory
    priority: SignalPriority
    summary: str
    source_url: str = ""
    source_type: str = ""  # "rss", "hn", "github", "linkedin", "manual"
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "company": self.company,
            "competitor": self.competitor,
            "category": self.category.value,
            "priority": self.priority.value,
            "summary": self.summary,
            "source_url": self.source_url,
            "source_type": self.source_type,
            "detected_at": self.detected_at.isoformat(),
        }


# Competitive watchlist per company
WATCHLIST: dict[str, dict] = {
    "startup-intelligence-os": {
        "display_name": "Startup Intelligence OS",
        "competitors": [
            "lindy.ai", "relevance.ai", "crew.ai", "autogen",
            "langchain", "llamaindex", "fabric", "openclaw",
        ],
        "keywords": [
            "ai agent framework", "personal ai", "ai operating system",
            "ai assistant framework", "multi-agent orchestration",
            "ai co-pilot", "ai chief of staff",
        ],
        "rss_feeds": [],  # Populated from scout-sources.json
    },
    "oracle-health": {
        "display_name": "Oracle Health",
        "competitors": [
            "epic systems", "cerner", "meditech", "allscripts",
            "athenahealth", "veeva", "health catalyst",
            "nuance", "ambient clinical", "abridge", "nabla",
        ],
        "keywords": [
            "ehr ai", "clinical ai", "ambient documentation",
            "oracle health ai", "clinical decision support",
            "health it", "interoperability", "fhir",
        ],
        "rss_feeds": [],
    },
    "alex-recruiting": {
        "display_name": "Alex Recruiting",
        "competitors": [
            "ncsa", "berecruited", "captainu", "sportsrecruits",
            "fieldlevel", "hudl", "connectlax",
        ],
        "keywords": [
            "sports recruiting", "college recruiting platform",
            "athlete recruiting", "nil deals", "transfer portal",
            "recruiting highlights", "coach outreach",
        ],
        "rss_feeds": [],
    },
}


class Scout:
    """SCOUT competitive intelligence engine."""

    SIGNALS_DIR = Path(__file__).parent / "logs"
    CONFIG_DIR = Path(__file__).parent.parent / "config"

    def __init__(self):
        self.SIGNALS_DIR.mkdir(parents=True, exist_ok=True)
        self.watchlist = self._load_watchlist()
        self._signals: list[CompetitiveSignal] = []

    def scan_all(self) -> list[CompetitiveSignal]:
        """Run full scan across all companies. Returns new signals."""
        signals = []
        for company_key, config in self.watchlist.items():
            signals.extend(self._scan_company(company_key, config))
        self._signals = signals
        self._persist_signals(signals)
        return signals

    def get_signals(self, priority: SignalPriority | None = None) -> list[CompetitiveSignal]:
        """Get signals, optionally filtered by priority."""
        if priority is None:
            return self._signals
        return [s for s in self._signals if s.priority == priority]

    def get_p0_p1(self) -> list[CompetitiveSignal]:
        """Get only P0 and P1 signals for inclusion in morning brief."""
        return [s for s in self._signals if s.priority in (SignalPriority.P0, SignalPriority.P1)]

    def format_for_brief(self) -> str:
        """Format P0/P1 signals for inclusion in the morning brief."""
        signals = self.get_p0_p1()
        if not signals:
            return "No competitive signals detected."

        lines = []
        for s in signals:
            prefix = "!!!" if s.priority == SignalPriority.P0 else "!"
            lines.append(
                f"  [{prefix}] {s.competitor}: {s.title} "
                f"({s.category.value}, affects {s.company})"
            )
            if s.summary:
                lines.append(f"       {s.summary[:120]}")
        return "\n".join(lines)

    def weekly_digest(self) -> str:
        """Generate a weekly competitive digest summary."""
        signals_file = self.SIGNALS_DIR / "competitive-signals.jsonl"
        if not signals_file.exists():
            return "No competitive signals logged yet."

        # Read last 7 days of signals
        recent = []
        cutoff = datetime.now(timezone.utc).timestamp() - (7 * 86400)
        with open(signals_file) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    ts = datetime.fromisoformat(entry.get("detected_at", ""))
                    if ts.timestamp() > cutoff:
                        recent.append(entry)
                except (json.JSONDecodeError, ValueError):
                    continue

        if not recent:
            return "No competitive signals in the last 7 days."

        # Group by company
        by_company: dict[str, list] = {}
        for s in recent:
            co = s.get("company", "unknown")
            by_company.setdefault(co, []).append(s)

        lines = ["## SCOUT Weekly Competitive Digest", ""]
        for co, sigs in by_company.items():
            display = WATCHLIST.get(co, {}).get("display_name", co)
            p0_count = sum(1 for s in sigs if s.get("priority") == "P0")
            p1_count = sum(1 for s in sigs if s.get("priority") == "P1")
            lines.append(f"### {display} ({len(sigs)} signals: {p0_count} P0, {p1_count} P1)")
            for s in sorted(sigs, key=lambda x: x.get("priority", "P2")):
                lines.append(f"  - [{s.get('priority')}] {s.get('title', '?')} ({s.get('competitor', '?')})")
            lines.append("")

        return "\n".join(lines)

    def add_manual_signal(
        self,
        title: str,
        company: str,
        competitor: str,
        category: str,
        priority: str,
        summary: str = "",
        source_url: str = "",
    ) -> CompetitiveSignal:
        """Add a manually observed competitive signal."""
        signal = CompetitiveSignal(
            title=title,
            company=company,
            competitor=competitor,
            category=SignalCategory(category),
            priority=SignalPriority(priority),
            summary=summary,
            source_url=source_url,
            source_type="manual",
        )
        self._signals.append(signal)
        self._persist_signals([signal])
        return signal

    def _scan_company(self, company_key: str, config: dict) -> list[CompetitiveSignal]:
        """Scan for competitive signals for a single company."""
        signals = []

        # RSS feed scanning
        for feed_url in config.get("rss_feeds", []):
            signals.extend(self._scan_rss(company_key, config, feed_url))

        # Keyword-based web search (uses gws or web search if available)
        for keyword in config.get("keywords", [])[:3]:  # Limit to top 3 to avoid rate limits
            signals.extend(self._scan_keyword(company_key, config, keyword))

        return signals

    def _scan_rss(self, company_key: str, config: dict, feed_url: str) -> list[CompetitiveSignal]:
        """Scan an RSS feed for competitive signals."""
        # Placeholder — will wire to actual RSS parsing
        # For now, returns empty. Real implementation uses feedparser.
        return []

    def _scan_keyword(self, company_key: str, config: dict, keyword: str) -> list[CompetitiveSignal]:
        """Search for competitive signals using keyword search."""
        # Placeholder — will wire to web search or Susan RAG
        # For now, returns empty. Real implementation uses gws or Fabric.
        return []

    def _persist_signals(self, signals: list[CompetitiveSignal]):
        """Append signals to JSONL log."""
        log_file = self.SIGNALS_DIR / "competitive-signals.jsonl"
        try:
            with open(log_file, "a") as f:
                for s in signals:
                    f.write(json.dumps(s.to_dict()) + "\n")
        except OSError:
            pass

    def _load_watchlist(self) -> dict:
        """Load watchlist from config or use defaults."""
        config_file = self.CONFIG_DIR / "scout-sources.json"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    custom = json.load(f)
                # Merge custom sources into defaults
                for key, val in custom.items():
                    if key in WATCHLIST:
                        WATCHLIST[key].update(val)
                    else:
                        WATCHLIST[key] = val
            except (json.JSONDecodeError, OSError):
                pass
        return WATCHLIST
