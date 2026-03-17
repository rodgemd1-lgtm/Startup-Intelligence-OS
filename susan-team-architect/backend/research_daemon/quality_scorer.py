"""
Research quality scoring for the Research Daemon.

Provides composite scoring across source authority, recency, and relevance
dimensions. Used by the AutoHarvester and the Daemon to rank research
results before integration.
"""

from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# Authority domain registry
# ---------------------------------------------------------------------------

_AUTHORITY_DOMAINS: dict[str, float] = {
    # Official documentation (0.90 - 0.95)
    "docs.python.org": 0.95,
    "developer.mozilla.org": 0.95,
    "react.dev": 0.93,
    "nextjs.org": 0.93,
    "fastapi.tiangolo.com": 0.92,
    "docs.pydantic.dev": 0.92,
    "docs.anthropic.com": 0.94,
    "platform.openai.com": 0.93,
    "ai.google.dev": 0.92,
    "docs.voyageai.com": 0.91,
    "supabase.com": 0.91,
    "tailwindcss.com": 0.90,
    "typescriptlang.org": 0.92,
    "vercel.com": 0.90,
    "nodejs.org": 0.92,
    "postgresql.org": 0.93,
    "redis.io": 0.90,

    # Research and academic (0.85 - 0.92)
    "arxiv.org": 0.92,
    "scholar.google.com": 0.88,
    "nature.com": 0.90,
    "sciencedirect.com": 0.88,
    "acm.org": 0.88,
    "ieee.org": 0.88,
    "pubmed.ncbi.nlm.nih.gov": 0.90,

    # Major platforms and repos (0.80 - 0.88)
    "github.com": 0.85,
    "pypi.org": 0.82,
    "npmjs.com": 0.82,
    "hub.docker.com": 0.80,

    # Practitioner sources (0.65 - 0.80)
    "stackoverflow.com": 0.75,
    "dev.to": 0.65,
    "medium.com": 0.60,
    "hackernews.com": 0.68,
    "news.ycombinator.com": 0.68,
    "martinfowler.com": 0.80,
    "blog.pragmaticengineer.com": 0.78,
    "lethain.com": 0.76,
    "simonwillison.net": 0.78,

    # Community (0.50 - 0.65)
    "reddit.com": 0.55,
    "discord.com": 0.50,
    "twitter.com": 0.50,
    "x.com": 0.50,
}

# Keyword sets for domain relevance scoring
_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "agent": [
        "agent", "orchestrator", "autonomous", "agentic", "multi-agent",
        "tool use", "function calling", "chain of thought", "reasoning",
    ],
    "rag": [
        "rag", "retrieval", "embedding", "vector", "chunking", "ingestion",
        "semantic search", "knowledge base", "pgvector", "voyage",
    ],
    "research": [
        "research", "methodology", "evidence", "analysis", "systematic review",
        "literature", "survey", "benchmark", "evaluation",
    ],
    "startup": [
        "startup", "founder", "product-market fit", "growth", "fundraising",
        "operating model", "capability", "maturity", "lean",
    ],
    "frontend": [
        "react", "next.js", "nextjs", "tailwind", "typescript", "component",
        "server component", "app router", "hook", "state management",
    ],
    "training": [
        "training", "enablement", "learning", "onboarding", "curriculum",
        "workshop", "facilitation", "instructional design",
    ],
    "fitness": [
        "fitness", "exercise", "workout", "nutrition", "recovery", "sleep",
        "sports science", "periodization", "strength", "conditioning",
    ],
    "film": [
        "film", "cinema", "production", "editing", "screenplay", "vfx",
        "color grade", "sound design", "directing", "cinematography",
    ],
}


class QualityScorer:
    """Score research materials across authority, recency, and relevance dimensions."""

    def score_source(self, url: str) -> float:
        """
        Score a URL by its domain authority.

        Known authoritative domains get higher scores. Unknown domains
        receive a baseline score of 0.40.

        Args:
            url: Full URL string.

        Returns:
            Score between 0.0 and 1.0.
        """
        if not url:
            return 0.3

        try:
            parsed = urlparse(url)
            hostname = (parsed.hostname or "").lower()
        except Exception:
            return 0.3

        if not hostname:
            return 0.3

        # Direct match
        if hostname in _AUTHORITY_DOMAINS:
            return _AUTHORITY_DOMAINS[hostname]

        # Strip www. prefix and try again
        bare = hostname.lstrip("www.")
        if bare in _AUTHORITY_DOMAINS:
            return _AUTHORITY_DOMAINS[bare]

        # Check if any known domain is a suffix of the hostname
        for domain, score in _AUTHORITY_DOMAINS.items():
            if hostname.endswith("." + domain) or hostname == domain:
                return score

        # Heuristics for unknown domains
        if hostname.endswith(".gov"):
            return 0.85
        if hostname.endswith(".edu"):
            return 0.80
        if hostname.endswith(".org"):
            return 0.60
        if hostname.endswith(".io"):
            return 0.50

        return 0.40

    def score_recency(self, date_str: str) -> float:
        """
        Score content recency with exponential decay.

        Content from today scores ~1.0. Content decays with a half-life
        of approximately 180 days (6 months).

        Args:
            date_str: ISO-8601 date or datetime string.

        Returns:
            Score between 0.0 and 1.0.
        """
        if not date_str:
            return 0.3

        try:
            # Handle both date-only and full datetime strings
            if "T" in date_str:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            else:
                dt = datetime.strptime(date_str[:10], "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
        except (ValueError, TypeError):
            return 0.3

        now = datetime.now(timezone.utc)
        age_days = max(0, (now - dt).days)

        # Exponential decay: half-life = 180 days
        half_life = 180.0
        decay = math.exp(-0.693 * age_days / half_life)

        # Floor at 0.1 — very old content still has some value
        return max(0.1, min(1.0, decay))

    def score_relevance(self, content: str, domain: str) -> float:
        """
        Score content relevance via keyword overlap with the target domain.

        Checks how many domain-specific keywords appear in the content.

        Args:
            content: Text content to evaluate.
            domain: Target domain key (e.g., 'agent', 'rag', 'startup').

        Returns:
            Score between 0.0 and 1.0.
        """
        if not content or not domain:
            return 0.3

        content_lower = content.lower()

        # Normalize domain name for keyword lookup
        domain_key = domain.lower().replace("-", "").replace("_", "").replace(" ", "")

        # Find matching keyword set
        keywords: list[str] = []
        for key, kw_list in _DOMAIN_KEYWORDS.items():
            normalized_key = key.replace("-", "").replace("_", "")
            if normalized_key == domain_key or domain_key.startswith(normalized_key):
                keywords = kw_list
                break

        # If no specific keyword set, try to match domain slug words
        if not keywords:
            # Collect keywords from all sets that have overlap with domain name
            domain_words = set(re.split(r"[-_\s]+", domain.lower()))
            for key, kw_list in _DOMAIN_KEYWORDS.items():
                key_words = set(re.split(r"[-_\s]+", key.lower()))
                if domain_words & key_words:
                    keywords.extend(kw_list)

        if not keywords:
            # Fall back: check if domain name itself appears in content
            domain_terms = re.split(r"[-_\s]+", domain.lower())
            hits = sum(1 for t in domain_terms if t in content_lower and len(t) > 2)
            return min(1.0, 0.3 + (hits * 0.15))

        # Count keyword hits
        hits = sum(1 for kw in keywords if kw.lower() in content_lower)
        total = len(keywords)

        if total == 0:
            return 0.3

        # Scale: hitting 60% of keywords = score 1.0
        ratio = hits / total
        score = min(1.0, ratio / 0.6)

        return max(0.1, score)

    def composite_score(
        self,
        url: str,
        date_str: str,
        content: str,
        domain: str,
    ) -> float:
        """
        Weighted composite quality score.

        Weights:
            - Source authority: 35%
            - Recency: 25%
            - Relevance: 40%

        Args:
            url: Source URL.
            date_str: Publication/harvest date.
            content: Text content.
            domain: Target domain.

        Returns:
            Weighted score between 0.0 and 1.0.
        """
        source = self.score_source(url)
        recency = self.score_recency(date_str)
        relevance = self.score_relevance(content, domain)

        composite = (
            0.35 * source
            + 0.25 * recency
            + 0.40 * relevance
        )

        return round(min(1.0, max(0.0, composite)), 4)
