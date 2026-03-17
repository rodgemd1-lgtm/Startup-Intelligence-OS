"""
Main Research Daemon orchestrator.

Coordinates gap detection, prioritization, manifest generation, harvest
execution, digest creation, and status reporting in a single cycle.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path

import yaml

from research_daemon.schemas import DaemonStatus, ResearchGap, HarvestResult, _now_iso
from research_daemon.gap_detector import GapDetector
from research_daemon.auto_harvest import AutoHarvester
from research_daemon.quality_scorer import QualityScorer


class ResearchDaemon:
    """Orchestrate full research cycles: detect -> prioritize -> harvest -> report."""

    def __init__(self, workspace_root: Path, backend_root: Path) -> None:
        """
        Args:
            workspace_root: Path to .startup-os/ directory.
            backend_root: Path to susan-team-architect/backend/ directory.
        """
        self.workspace_root = Path(workspace_root)
        self.backend_root = Path(backend_root)
        self.data_dir = self.backend_root / "data"
        self.manifests_dir = self.data_dir / "scrape_manifests"
        self.memory_dir = self.data_dir / "memory"
        self.gaps_dir = self.memory_dir / "research_gaps"
        self.harvest_dir = self.memory_dir / "harvest_results"

        # Ensure output directories exist
        self.gaps_dir.mkdir(parents=True, exist_ok=True)
        self.harvest_dir.mkdir(parents=True, exist_ok=True)

        # Component instances
        self.gap_detector = GapDetector(
            workspace_root=self.workspace_root,
            rag_data_dir=self.data_dir,
        )
        self.harvester = AutoHarvester(
            data_dir=self.data_dir,
            manifests_dir=self.manifests_dir,
        )
        self.scorer = QualityScorer()

        # Internal state
        self._status = DaemonStatus()
        self._last_gaps: list[ResearchGap] = []
        self._last_results: list[HarvestResult] = []

    # ------------------------------------------------------------------
    # Full cycle
    # ------------------------------------------------------------------

    def run_cycle(self, top_n: int = 5) -> DaemonStatus:
        """
        Execute one full research cycle.

        Steps:
            1. Detect gaps via GapDetector
            2. Detect stale data
            3. Merge and prioritize all gaps
            4. For top-N gaps, generate manifests
            5. Run harvest for each manifest
            6. Score and filter results
            7. Generate digest report
            8. Persist results and status

        Args:
            top_n: Number of top-priority gaps to process per cycle.

        Returns:
            DaemonStatus snapshot after the cycle.
        """
        cycle_start = _now_iso()
        health = "healthy"
        all_results: list[HarvestResult] = []

        try:
            # Step 1: Detect coverage gaps
            coverage_gaps = self.gap_detector.detect_gaps()

            # Step 2: Detect stale data
            stale_gaps = self.gap_detector.detect_stale_data(max_age_days=30)

            # Step 3: Merge and prioritize
            all_gaps = coverage_gaps + stale_gaps
            prioritized = self.gap_detector.prioritize_gaps(all_gaps)

            # Save all detected gaps
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            self.gap_detector.save_gaps(
                prioritized,
                self.gaps_dir / f"gaps-{timestamp}.yaml",
            )

            # Step 4-5: Process top-N gaps
            top_gaps = prioritized[:top_n]
            for gap in top_gaps:
                # Generate manifest
                manifest = self.harvester.generate_manifest_from_gap(gap)

                # Save manifest
                manifest_slug = gap.domain.replace("-", "_")
                manifest_path = self.manifests_dir / f"auto_{manifest_slug}.yaml"
                self.harvester.save_manifest(manifest, manifest_path)

                # Run harvest
                results = self.harvester.harvest(manifest)

                # Step 6: Score and filter results
                scored_results: list[HarvestResult] = []
                for result in results:
                    quality = self.harvester.evaluate_quality(result)
                    result.quality_score = max(result.quality_score, quality)

                    # Keep results above minimum quality threshold
                    if result.quality_score >= 0.3:
                        scored_results.append(result)

                all_results.extend(scored_results)

                # Mark gap as researching
                gap.status = "researching"

            # Save harvest results
            if all_results:
                self.harvester.save_results(
                    all_results,
                    self.harvest_dir / f"harvest-{timestamp}.yaml",
                )

            # Step 7: Generate digest
            digest = self.harvester.generate_digest(all_results)
            digest_path = self.memory_dir / "latest_digest.md"
            digest_path.write_text(digest, encoding="utf-8")

            # Count filled gaps (gaps where we got high-quality results)
            gaps_with_good_results = set()
            for r in all_results:
                if r.gap_id and r.quality_score >= 0.6:
                    gaps_with_good_results.add(r.gap_id)

            # Step 8: Update status
            self._last_gaps = prioritized
            self._last_results = all_results

            self._status = DaemonStatus(
                last_run=cycle_start,
                next_run=self._calculate_next_run(),
                gaps_detected=len(prioritized),
                gaps_filled=len(gaps_with_good_results),
                items_harvested=len(all_results),
                programs_active=len(top_gaps),
                health=health,
            )

        except Exception as exc:
            health = "error"
            self._status = DaemonStatus(
                last_run=cycle_start,
                next_run=self._calculate_next_run(),
                gaps_detected=0,
                gaps_filled=0,
                items_harvested=0,
                programs_active=0,
                health="error",
            )
            # Re-raise so callers can inspect the error
            raise RuntimeError(
                f"Research daemon cycle failed: {exc}"
            ) from exc

        return self._status

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> DaemonStatus:
        """Return the current daemon status."""
        return self._status

    def save_status(self, path: Path) -> None:
        """
        Persist the current daemon status to YAML.

        Args:
            path: Output YAML file path.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "daemon_status": self._status.model_dump(),
            "summary": {
                "last_gaps_count": len(self._last_gaps),
                "last_results_count": len(self._last_results),
                "top_gaps": [
                    {"id": g.id, "domain": g.domain, "severity": g.severity}
                    for g in self._last_gaps[:10]
                ],
                "top_results": [
                    {
                        "id": r.id,
                        "title": r.title[:80],
                        "quality": r.quality_score,
                    }
                    for r in sorted(
                        self._last_results,
                        key=lambda r: r.quality_score,
                        reverse=True,
                    )[:10]
                ],
            },
        }

        with open(path, "w", encoding="utf-8") as fh:
            yaml.safe_dump(payload, fh, default_flow_style=False, sort_keys=False)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _calculate_next_run(self) -> str:
        """Calculate the next scheduled run (default: 24 hours from now)."""
        next_dt = datetime.now(timezone.utc) + timedelta(hours=24)
        return next_dt.isoformat()
