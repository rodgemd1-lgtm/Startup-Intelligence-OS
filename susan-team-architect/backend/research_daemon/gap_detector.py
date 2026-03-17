"""
Knowledge gap detection for the Research Daemon.

Scans capability records, department packs, scrape manifests, and RAG data
directories to identify domains with insufficient research coverage.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

import yaml

from research_daemon.schemas import ResearchGap, _now_iso


class GapDetector:
    """Detect knowledge gaps by comparing declared capabilities against actual data."""

    def __init__(self, workspace_root: Path, rag_data_dir: Path) -> None:
        """
        Args:
            workspace_root: Path to .startup-os/ directory.
            rag_data_dir: Path to susan-team-architect/backend/data/ directory.
        """
        self.workspace_root = Path(workspace_root)
        self.rag_data_dir = Path(rag_data_dir)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_yaml(self, path: Path) -> dict[str, Any]:
        """Safely load a YAML file, returning empty dict on failure."""
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
                return data if isinstance(data, dict) else {}
        except (FileNotFoundError, yaml.YAMLError, PermissionError):
            return {}

    def _list_yaml_files(self, directory: Path) -> list[Path]:
        """Return all .yaml/.yml files in a directory (non-recursive)."""
        if not directory.is_dir():
            return []
        return sorted(
            p for p in directory.iterdir()
            if p.suffix in (".yaml", ".yml") and p.is_file()
        )

    def _domain_slug(self, name: str) -> str:
        """Normalize a capability/department name to a filesystem-safe slug."""
        return name.lower().replace(" ", "-").replace("_", "-")

    def _check_domain_data_exists(self, domain_slug: str) -> float:
        """
        Score how much RAG data exists for a given domain.

        Returns:
            0.0 — no data found
            0.5 — partial data (scrape manifest exists but no domain dir, or few files)
            1.0 — comprehensive data (domain dir with substantial content)
        """
        score = 0.0

        # Check domain directories
        domains_dir = self.rag_data_dir / "domains"
        if domains_dir.is_dir():
            for entry in domains_dir.iterdir():
                if entry.is_dir() and domain_slug in entry.name.lower().replace("_", "-"):
                    file_count = sum(1 for _ in entry.rglob("*") if _.is_file())
                    if file_count >= 10:
                        score = max(score, 1.0)
                    elif file_count >= 3:
                        score = max(score, 0.7)
                    elif file_count >= 1:
                        score = max(score, 0.5)

        # Check scrape manifests
        manifests_dir = self.rag_data_dir / "scrape_manifests"
        if manifests_dir.is_dir():
            for manifest_path in manifests_dir.iterdir():
                if manifest_path.suffix in (".yaml", ".yml"):
                    slug_in_name = domain_slug.replace("-", "_")
                    if slug_in_name in manifest_path.stem or domain_slug in manifest_path.stem:
                        # Manifest exists — at least partial coverage
                        score = max(score, 0.5)

        # Check startup_os data directory
        startup_os_data = self.rag_data_dir / "startup_os"
        if startup_os_data.is_dir():
            for entry in startup_os_data.iterdir():
                if entry.is_dir() and domain_slug in entry.name.lower().replace("_", "-"):
                    file_count = sum(1 for _ in entry.rglob("*") if _.is_file())
                    if file_count >= 5:
                        score = max(score, 0.8)
                    elif file_count >= 1:
                        score = max(score, 0.5)

        # Check studio_assets
        studio_dir = self.rag_data_dir / "studio_assets"
        if studio_dir.is_dir():
            for entry in studio_dir.rglob("*"):
                if entry.is_dir() and domain_slug in entry.name.lower().replace("_", "-"):
                    file_count = sum(1 for _ in entry.rglob("*") if _.is_file())
                    if file_count >= 3:
                        score = max(score, 0.6)

        return score

    def _severity_from_coverage(self, coverage: float, has_gaps: bool) -> str:
        """Determine severity based on coverage and declared gaps."""
        if coverage == 0.0:
            return "critical"
        if coverage < 0.3:
            return "critical" if has_gaps else "high"
        if coverage < 0.5:
            return "high"
        if coverage < 0.7:
            return "medium"
        return "low"

    def _suggest_queries(self, domain: str, description: str) -> list[str]:
        """Generate search queries for a gap based on domain and description."""
        queries = []
        clean_domain = domain.replace("-", " ").replace("_", " ").strip()

        queries.append(f"{clean_domain} best practices official documentation")
        queries.append(f"{clean_domain} framework methodology guide")
        queries.append(f"{clean_domain} startup implementation playbook")

        # Add description-derived queries
        words = [w for w in description.split() if len(w) > 4]
        if len(words) >= 3:
            queries.append(" ".join(words[:5]) + " research")

        return queries

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect_gaps(self) -> list[ResearchGap]:
        """
        Analyze coverage gaps across capabilities, departments, and scrape manifests.

        Returns a list of ResearchGap objects for any domain below 0.7 coverage.
        """
        gaps: list[ResearchGap] = []
        seen_domains: set[str] = set()

        # 1. Scan capability records
        caps_dir = self.workspace_root / "capabilities"
        for cap_path in self._list_yaml_files(caps_dir):
            cap = self._load_yaml(cap_path)
            cap_id = cap.get("id", cap_path.stem)
            cap_name = cap.get("name", cap_id)
            domain_slug = self._domain_slug(cap_id)

            if domain_slug in seen_domains:
                continue
            seen_domains.add(domain_slug)

            coverage = self._check_domain_data_exists(domain_slug)

            # Also consider declared gaps in the capability record
            declared_gaps = cap.get("gaps", [])
            has_declared_gaps = bool(declared_gaps)

            if coverage < 0.7:
                gap_desc = (
                    f"Capability '{cap_name}' has coverage score {coverage:.1f}. "
                )
                if declared_gaps:
                    gap_desc += f"Declared gaps: {', '.join(str(g) for g in declared_gaps[:5])}."
                else:
                    gap_desc += "No matching RAG data or scrape manifests found."

                gap = ResearchGap(
                    domain=domain_slug,
                    description=gap_desc,
                    severity=self._severity_from_coverage(coverage, has_declared_gaps),
                    current_coverage=coverage,
                    target_coverage=min(1.0, max(0.7, cap.get("maturity_target", 3.5) / 5.0)),
                    suggested_queries=self._suggest_queries(domain_slug, gap_desc),
                    status="open",
                )
                gaps.append(gap)

        # 2. Scan department packs
        depts_dir = self.workspace_root / "departments"
        for dept_path in self._list_yaml_files(depts_dir):
            dept = self._load_yaml(dept_path)
            dept_id = dept.get("id", dept_path.stem)
            dept_name = dept.get("name", dept_id)
            domain_slug = self._domain_slug(dept_id)

            if domain_slug in seen_domains:
                continue
            seen_domains.add(domain_slug)

            coverage = self._check_domain_data_exists(domain_slug)

            # Check required_evidence fields
            required_evidence = dept.get("required_evidence", [])
            required_artifacts = dept.get("required_artifacts", [])
            has_requirements = bool(required_evidence or required_artifacts)

            if coverage < 0.7:
                gap_desc = (
                    f"Department '{dept_name}' has coverage score {coverage:.1f}."
                )
                if required_evidence:
                    gap_desc += (
                        f" Required evidence: {', '.join(str(e) for e in required_evidence[:5])}."
                    )

                gap = ResearchGap(
                    domain=domain_slug,
                    description=gap_desc,
                    severity=self._severity_from_coverage(coverage, has_requirements),
                    current_coverage=coverage,
                    target_coverage=0.8,
                    suggested_queries=self._suggest_queries(domain_slug, gap_desc),
                    status="open",
                )
                gaps.append(gap)

        # 3. Scan scrape manifests for domains that exist as manifests but have no data
        manifests_dir = self.rag_data_dir / "scrape_manifests"
        if manifests_dir.is_dir():
            for manifest_path in self._list_yaml_files(manifests_dir):
                manifest = self._load_yaml(manifest_path)
                manifest_meta = manifest.get("manifest", {})
                manifest_name = manifest_meta.get("name", manifest_path.stem)
                domain_slug = self._domain_slug(manifest_path.stem)

                if domain_slug in seen_domains:
                    continue
                seen_domains.add(domain_slug)

                # Check if the manifest's data has actually been ingested
                coverage = self._check_domain_data_exists(domain_slug)

                if coverage < 0.7:
                    gap_desc = (
                        f"Scrape manifest '{manifest_name}' exists but data coverage "
                        f"is {coverage:.1f}. Sources may not have been fully ingested."
                    )
                    gap = ResearchGap(
                        domain=domain_slug,
                        description=gap_desc,
                        severity="medium" if coverage > 0.3 else "high",
                        current_coverage=coverage,
                        target_coverage=0.8,
                        suggested_queries=self._suggest_queries(domain_slug, gap_desc),
                        status="open",
                    )
                    gaps.append(gap)

        return gaps

    def detect_stale_data(self, max_age_days: int = 30) -> list[ResearchGap]:
        """
        Find data directories where files are older than the given threshold.

        Args:
            max_age_days: Maximum acceptable age in days.

        Returns:
            List of ResearchGap objects for stale domains.
        """
        gaps: list[ResearchGap] = []
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)

        # Check domain data directories
        domains_dir = self.rag_data_dir / "domains"
        if not domains_dir.is_dir():
            return gaps

        for domain_dir in sorted(domains_dir.iterdir()):
            if not domain_dir.is_dir():
                continue

            domain_slug = self._domain_slug(domain_dir.name)
            files = list(domain_dir.rglob("*"))
            data_files = [f for f in files if f.is_file()]

            if not data_files:
                continue

            # Find the most recent file modification
            most_recent = max(
                (datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc) for f in data_files),
                default=cutoff,
            )

            if most_recent < cutoff:
                age_days = (datetime.now(timezone.utc) - most_recent).days
                coverage = self._check_domain_data_exists(domain_slug)

                gap = ResearchGap(
                    domain=domain_slug,
                    description=(
                        f"Domain '{domain_dir.name}' data is {age_days} days old "
                        f"(threshold: {max_age_days} days). Most recent file: "
                        f"{most_recent.strftime('%Y-%m-%d')}."
                    ),
                    severity="high" if age_days > max_age_days * 2 else "medium",
                    current_coverage=max(0.0, coverage - 0.2),  # Staleness penalty
                    target_coverage=0.8,
                    suggested_queries=self._suggest_queries(
                        domain_slug,
                        f"latest updates {domain_dir.name} 2025 2026",
                    ),
                    status="open",
                )
                gaps.append(gap)

        # Also check scrape manifests for staleness
        manifests_dir = self.rag_data_dir / "scrape_manifests"
        if manifests_dir.is_dir():
            for manifest_path in self._list_yaml_files(manifests_dir):
                mtime = datetime.fromtimestamp(
                    manifest_path.stat().st_mtime, tz=timezone.utc
                )
                if mtime < cutoff:
                    age_days = (datetime.now(timezone.utc) - mtime).days
                    domain_slug = self._domain_slug(manifest_path.stem)

                    gap = ResearchGap(
                        domain=domain_slug,
                        description=(
                            f"Scrape manifest '{manifest_path.name}' last modified "
                            f"{age_days} days ago. May contain outdated source URLs."
                        ),
                        severity="low",
                        current_coverage=0.5,
                        target_coverage=0.7,
                        suggested_queries=[
                            f"{domain_slug.replace('-', ' ')} latest documentation 2026",
                        ],
                        status="open",
                    )
                    gaps.append(gap)

        return gaps

    def prioritize_gaps(self, gaps: list[ResearchGap]) -> list[ResearchGap]:
        """
        Sort gaps by severity and impact (lowest coverage first within each severity).

        Severity order: critical > high > medium > low.
        Within the same severity, lower coverage is prioritized.
        """
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

        return sorted(
            gaps,
            key=lambda g: (
                severity_order.get(g.severity, 4),
                g.current_coverage,
                g.domain,
            ),
        )

    def save_gaps(self, gaps: list[ResearchGap], path: Path) -> None:
        """
        Persist detected gaps to a YAML file.

        Args:
            gaps: List of ResearchGap models.
            path: Output YAML file path.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        records = [gap.model_dump() for gap in gaps]
        payload = {
            "generated_at": _now_iso(),
            "total_gaps": len(records),
            "gaps": records,
        }

        with open(path, "w", encoding="utf-8") as fh:
            yaml.safe_dump(payload, fh, default_flow_style=False, sort_keys=False)
