"""
Automated research harvest pipeline for the Research Daemon.

Generates scrape manifests from detected gaps, orchestrates harvest
execution, evaluates quality, and produces digest reports.

Note: This module generates the query and manifest structures. Actual
HTTP requests are delegated to the existing scrape engine (rag_engine).
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from research_daemon.schemas import HarvestResult, ResearchGap, _now_iso
from research_daemon.quality_scorer import QualityScorer


# ---------------------------------------------------------------------------
# Source target templates for manifest generation
# ---------------------------------------------------------------------------

_SOURCE_TARGETS: dict[str, list[dict[str, Any]]] = {
    "official": [
        {"tool": "firecrawl-crawl", "max_pages": 20},
        {"tool": "jina"},
    ],
    "github": [
        {"tool": "jina"},
        {"tool": "exa", "num_results": 5},
    ],
    "stackoverflow": [
        {"tool": "exa", "num_results": 8},
    ],
    "general": [
        {"tool": "exa", "num_results": 10},
        {"tool": "jina"},
    ],
}

# Mapping from domain keywords to likely official doc URLs
_DOMAIN_DOC_URLS: dict[str, str] = {
    "react": "https://react.dev/learn",
    "nextjs": "https://nextjs.org/docs",
    "next": "https://nextjs.org/docs",
    "fastapi": "https://fastapi.tiangolo.com/",
    "pydantic": "https://docs.pydantic.dev/latest/",
    "anthropic": "https://docs.anthropic.com/en/docs/welcome",
    "python": "https://docs.python.org/3/",
    "supabase": "https://supabase.com/docs",
    "tailwind": "https://tailwindcss.com/docs",
    "typescript": "https://www.typescriptlang.org/docs/",
    "playwright": "https://playwright.dev/python/docs/intro",
    "agent": "https://docs.anthropic.com/en/docs/agents",
    "rag": "https://docs.voyageai.com/docs/embeddings",
    "fitness": "https://www.acsm.org/education-resources",
    "film": "https://www.masterclass.com/categories/film-tv",
}


class AutoHarvester:
    """End-to-end harvest pipeline: gap -> manifest -> harvest -> score -> digest."""

    def __init__(self, data_dir: Path, manifests_dir: Path) -> None:
        """
        Args:
            data_dir: Path to susan-team-architect/backend/data/.
            manifests_dir: Path to backend/data/scrape_manifests/.
        """
        self.data_dir = Path(data_dir)
        self.manifests_dir = Path(manifests_dir)
        self.scorer = QualityScorer()

    # ------------------------------------------------------------------
    # Manifest generation
    # ------------------------------------------------------------------

    def _generate_queries_from_gap(self, gap: ResearchGap) -> list[str]:
        """
        Generate search queries from a gap's domain and description.

        Uses the gap's suggested_queries plus generates additional
        domain-specific queries.
        """
        queries: list[str] = list(gap.suggested_queries)

        domain_clean = gap.domain.replace("-", " ").replace("_", " ").strip()

        # Add standard query patterns
        patterns = [
            f"{domain_clean} official documentation guide",
            f"{domain_clean} best practices 2025 2026",
            f"{domain_clean} tutorial getting started",
            f"site:github.com {domain_clean} awesome list",
        ]

        for pattern in patterns:
            if pattern not in queries:
                queries.append(pattern)

        return queries[:10]  # Cap at 10 queries

    def _find_doc_url(self, domain: str) -> str | None:
        """Find a known documentation URL for the domain."""
        domain_lower = domain.lower().replace("-", "").replace("_", "")
        for key, url in _DOMAIN_DOC_URLS.items():
            if key in domain_lower or domain_lower in key:
                return url
        return None

    def generate_manifest_from_gap(self, gap: ResearchGap) -> dict:
        """
        Create a scrape manifest YAML structure for a detected gap.

        The manifest follows the same schema as existing manifests in
        data/scrape_manifests/.

        Args:
            gap: The ResearchGap to generate a manifest for.

        Returns:
            Dict matching the scrape manifest YAML schema.
        """
        queries = self._generate_queries_from_gap(gap)
        domain_clean = gap.domain.replace("-", " ").replace("_", " ").strip()

        sources: list[dict[str, Any]] = []

        # Add official doc crawl if we know the URL
        doc_url = self._find_doc_url(gap.domain)
        if doc_url:
            sources.append({
                "tool": "firecrawl-crawl",
                "url": doc_url,
                "max_pages": 20,
            })
            sources.append({
                "tool": "jina",
                "url": doc_url,
            })

        # Add Exa search queries
        for query in queries[:5]:
            sources.append({
                "tool": "exa",
                "query": query,
                "num_results": 8,
            })

        # Add GitHub search
        sources.append({
            "tool": "exa",
            "query": f"site:github.com {domain_clean} README",
            "num_results": 5,
        })

        manifest = {
            "manifest": {
                "name": f"Auto-harvest: {domain_clean}",
                "company": "founder-intelligence-os",
                "data_type": "research_harvest",
                "priority": gap.severity,
                "description": (
                    f"Auto-generated manifest for gap '{gap.id}': "
                    f"{gap.description[:200]}"
                ),
                "generated_by": "research_daemon",
                "gap_id": gap.id,
                "generated_at": _now_iso(),
            },
            "sources": sources,
            "quality_thresholds": {
                "min_quality_score": 0.5,
                "min_relevance_score": 0.4,
                "preferred_authority": ["official", "practitioner"],
            },
        }

        return manifest

    # ------------------------------------------------------------------
    # Harvest execution
    # ------------------------------------------------------------------

    def harvest(self, manifest: dict) -> list[HarvestResult]:
        """
        Execute a harvest cycle from a manifest.

        This method generates HarvestResult structures from the manifest's
        source definitions. Actual web requests are delegated to the
        existing scrape engine (rag_engine/ingestion/).

        The results represent what the scrape engine should fetch and
        are scored for quality and relevance.

        Args:
            manifest: Scrape manifest dict (as produced by generate_manifest_from_gap).

        Returns:
            List of HarvestResult objects representing expected harvest targets.
        """
        results: list[HarvestResult] = []
        manifest_meta = manifest.get("manifest", {})
        gap_id = manifest_meta.get("gap_id")
        domain = manifest_meta.get("name", "").replace("Auto-harvest: ", "")
        thresholds = manifest.get("quality_thresholds", {})
        min_quality = thresholds.get("min_quality_score", 0.5)

        for source in manifest.get("sources", []):
            tool = source.get("tool", "unknown")

            if tool in ("firecrawl-crawl", "jina"):
                url = source.get("url", "")
                if not url:
                    continue

                # Score the source
                quality = self.evaluate_quality_from_url(url)
                relevance = self.scorer.score_relevance(
                    f"{url} {domain}", domain
                )

                if quality < min_quality:
                    continue

                authority = self._classify_authority(url)

                result = HarvestResult(
                    gap_id=gap_id,
                    source_url=url,
                    title=f"{tool} harvest: {url}",
                    content_summary=(
                        f"Pending harvest from {url} via {tool}. "
                        f"Expected content: {domain} documentation."
                    ),
                    quality_score=quality,
                    relevance_score=relevance,
                    source_authority=authority,
                    integrated=False,
                )
                results.append(result)

            elif tool == "exa":
                query = source.get("query", "")
                if not query:
                    continue

                num_results = source.get("num_results", 5)

                # Generate placeholder results for each expected search result
                for i in range(min(num_results, 5)):
                    seed = f"{query}::result::{i}"
                    result_id = hashlib.sha256(seed.encode()).hexdigest()[:12]

                    result = HarvestResult(
                        gap_id=gap_id,
                        source_url=f"exa://search/{result_id}",
                        title=f"Exa search result {i + 1}: {query[:80]}",
                        content_summary=(
                            f"Pending Exa search for: '{query}'. "
                            f"Result {i + 1} of {num_results}."
                        ),
                        quality_score=0.5,  # Baseline until actual content is fetched
                        relevance_score=0.6,
                        source_authority="unknown",
                        integrated=False,
                    )
                    results.append(result)

        return results

    def evaluate_quality(self, result: HarvestResult) -> float:
        """
        Score overall quality of a harvest result.

        Uses the composite scorer with the result's metadata.

        Args:
            result: HarvestResult to evaluate.

        Returns:
            Quality score between 0.0 and 1.0.
        """
        domain = result.gap_id or ""
        return self.scorer.composite_score(
            url=result.source_url,
            date_str=result.harvested_at,
            content=result.content_summary,
            domain=domain,
        )

    def evaluate_quality_from_url(self, url: str) -> float:
        """
        Quick quality evaluation based on URL alone.

        Scoring tiers:
        - Official docs = 0.9+
        - GitHub repos = 0.8
        - Stack Overflow accepted answers = 0.7
        - Blog posts from known domains = 0.6
        - Unknown = 0.4

        Args:
            url: Source URL.

        Returns:
            Quality score between 0.0 and 1.0.
        """
        return self.scorer.score_source(url)

    def _classify_authority(self, url: str) -> str:
        """Classify source authority based on URL."""
        url_lower = url.lower()

        official_markers = [
            "docs.", ".dev/docs", "/documentation", "/docs/",
            "docs.python.org", "react.dev", "nextjs.org",
            "fastapi.tiangolo.com", "docs.anthropic.com",
            "platform.openai.com", "supabase.com/docs",
        ]
        for marker in official_markers:
            if marker in url_lower:
                return "official"

        practitioner_markers = [
            "github.com", "stackoverflow.com", "arxiv.org",
            "martinfowler.com", "blog.", "medium.com/@",
        ]
        for marker in practitioner_markers:
            if marker in url_lower:
                return "practitioner"

        community_markers = [
            "reddit.com", "discord.com", "dev.to",
            "hackernews", "news.ycombinator",
        ]
        for marker in community_markers:
            if marker in url_lower:
                return "community"

        return "unknown"

    # ------------------------------------------------------------------
    # Digest generation
    # ------------------------------------------------------------------

    def generate_digest(self, results: list[HarvestResult]) -> str:
        """
        Generate a weekly digest markdown report of harvest results.

        Args:
            results: List of HarvestResult objects from recent harvests.

        Returns:
            Markdown-formatted digest string.
        """
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        lines: list[str] = [
            "# Research Harvest Digest",
            "",
            f"Generated: {now}",
            f"Total items: {len(results)}",
            "",
        ]

        if not results:
            lines.append("No new harvest results this period.")
            return "\n".join(lines)

        # Summary statistics
        integrated = [r for r in results if r.integrated]
        pending = [r for r in results if not r.integrated]
        avg_quality = (
            sum(r.quality_score for r in results) / len(results)
            if results
            else 0.0
        )
        avg_relevance = (
            sum(r.relevance_score for r in results) / len(results)
            if results
            else 0.0
        )

        lines.extend([
            "## Summary",
            "",
            f"- **Integrated**: {len(integrated)}",
            f"- **Pending integration**: {len(pending)}",
            f"- **Average quality**: {avg_quality:.2f}",
            f"- **Average relevance**: {avg_relevance:.2f}",
            "",
        ])

        # Group by authority
        by_authority: dict[str, list[HarvestResult]] = {}
        for r in results:
            by_authority.setdefault(r.source_authority, []).append(r)

        authority_order = ["official", "practitioner", "community", "unknown"]
        for authority in authority_order:
            items = by_authority.get(authority, [])
            if not items:
                continue

            lines.append(f"## {authority.title()} Sources ({len(items)})")
            lines.append("")

            # Sort by quality descending
            sorted_items = sorted(items, key=lambda r: r.quality_score, reverse=True)
            for item in sorted_items[:20]:  # Cap display at 20 per category
                quality_bar = self._quality_bar(item.quality_score)
                lines.append(
                    f"- {quality_bar} **{item.title[:80]}**"
                )
                lines.append(
                    f"  - Quality: {item.quality_score:.2f} | "
                    f"Relevance: {item.relevance_score:.2f} | "
                    f"{'Integrated' if item.integrated else 'Pending'}"
                )
                if item.source_url and not item.source_url.startswith("exa://"):
                    lines.append(f"  - Source: {item.source_url}")
                lines.append("")

        # Gap coverage
        gap_ids = set(r.gap_id for r in results if r.gap_id)
        if gap_ids:
            lines.append("## Gaps Addressed")
            lines.append("")
            for gap_id in sorted(gap_ids):
                gap_results = [r for r in results if r.gap_id == gap_id]
                avg_q = sum(r.quality_score for r in gap_results) / len(gap_results)
                lines.append(f"- `{gap_id}`: {len(gap_results)} results (avg quality: {avg_q:.2f})")
            lines.append("")

        lines.append("---")
        lines.append("*Generated by Research Daemon auto-harvester.*")

        return "\n".join(lines)

    def _quality_bar(self, score: float) -> str:
        """Render a text quality indicator."""
        if score >= 0.8:
            return "[HIGH]"
        if score >= 0.6:
            return "[MED]"
        if score >= 0.4:
            return "[LOW]"
        return "[MIN]"

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_manifest(self, manifest: dict, path: Path) -> None:
        """Write a manifest to YAML."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            yaml.safe_dump(manifest, fh, default_flow_style=False, sort_keys=False)

    def save_results(self, results: list[HarvestResult], path: Path) -> None:
        """Persist harvest results to YAML."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        records = [r.model_dump() for r in results]
        payload = {
            "generated_at": _now_iso(),
            "total_results": len(records),
            "results": records,
        }

        with open(path, "w", encoding="utf-8") as fh:
            yaml.safe_dump(payload, fh, default_flow_style=False, sort_keys=False)
