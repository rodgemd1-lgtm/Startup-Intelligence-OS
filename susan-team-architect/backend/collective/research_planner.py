"""Self-directed research program planner for the Collective Intelligence Framework.

Scans capability records from `.startup-os/capabilities/`, identifies maturity
gaps, determines knowledge needs at each maturity band, and generates full
research program specifications with questions, search strategies, and
acceptance criteria.
"""

from __future__ import annotations

import hashlib
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .schemas import ResearchProgramSpec


def _deterministic_id(prefix: str, *parts: str) -> str:
    """Generate a deterministic short hash ID from string parts."""
    raw = ":".join(parts)
    digest = hashlib.sha256(raw.encode()).hexdigest()[:12]
    return f"{prefix}-{digest}"


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Knowledge-need templates by maturity band
# ---------------------------------------------------------------------------

_BAND_NEEDS: dict[str, list[str]] = {
    "0-1": [
        "foundational definitions and vocabulary for {cap}",
        "basic concepts and mental models for {cap}",
        "minimum viable scope and boundary definition for {cap}",
    ],
    "1-2": [
        "documented processes and playbooks for {cap}",
        "real-world examples and case studies for {cap}",
        "common pitfalls and anti-patterns in early {cap} adoption",
        "starter toolkits and templates for {cap}",
    ],
    "2-3": [
        "metrics and KPIs for measuring {cap} effectiveness",
        "measurement frameworks and dashboards for {cap}",
        "scaling strategies for {cap} across teams",
        "integration patterns connecting {cap} to adjacent capabilities",
    ],
    "3-4": [
        "optimization techniques for advanced {cap} operations",
        "industry benchmarks and comparative analysis for {cap}",
        "automation opportunities within {cap} workflows",
        "advanced tooling and infrastructure for {cap}",
    ],
    "4-5": [
        "industry-leading practices and innovation research in {cap}",
        "emerging trends and frontier approaches for {cap}",
        "cross-industry transfer patterns applicable to {cap}",
        "thought leadership and original contribution opportunities in {cap}",
    ],
}

# ---------------------------------------------------------------------------
# Search strategy templates
# ---------------------------------------------------------------------------

_SEARCH_STRATEGIES: dict[str, list[str]] = {
    "0-1": [
        "academic: search for survey papers and textbook definitions on {cap}",
        "official_docs: review vendor and standards body documentation for {cap}",
    ],
    "1-2": [
        "practitioner: find blog posts, conference talks, and tutorials on {cap}",
        "official_docs: collect framework documentation and quickstart guides for {cap}",
        "case_studies: search for published case studies of {cap} adoption",
    ],
    "2-3": [
        "academic: find measurement and evaluation papers for {cap}",
        "practitioner: locate metrics dashboards and reporting templates for {cap}",
        "benchmarks: collect industry benchmark data for {cap}",
    ],
    "3-4": [
        "academic: search for optimization and performance research on {cap}",
        "benchmarks: gather competitive benchmarking data for {cap}",
        "practitioner: find advanced operational playbooks for {cap}",
        "tooling: evaluate automation and tooling ecosystem for {cap}",
    ],
    "4-5": [
        "academic: search for frontier research and innovation in {cap}",
        "practitioner: identify industry leaders and their published approaches for {cap}",
        "conferences: review recent conference proceedings for {cap} innovations",
        "patents: scan recent patent filings related to {cap}",
    ],
}


class ResearchPlanner:
    """Plans self-directed research programs based on capability maturity gaps.

    Reads capability YAML files from the workspace, identifies where current
    maturity falls short of target, determines what knowledge is needed at each
    band, and generates full research program specifications.
    """

    def __init__(self, workspace_root: Path, memory_data_dir: Path) -> None:
        self.workspace_root = workspace_root
        self.capabilities_dir = workspace_root / ".startup-os" / "capabilities"
        self.memory_data_dir = memory_data_dir

    # ------------------------------------------------------------------
    # Gap analysis
    # ------------------------------------------------------------------

    def analyze_maturity_gaps(self) -> list[dict[str, Any]]:
        """Read capability records, find those with maturity < target, rank by gap size.

        Returns a list of dicts with keys: id, name, current, target, gap, gaps_list,
        owner_agent, wave.
        """
        results: list[dict[str, Any]] = []

        if not self.capabilities_dir.exists():
            return results

        for yaml_path in sorted(self.capabilities_dir.glob("*.yaml")):
            # Skip non-capability files (profiles, README-like, system files)
            if yaml_path.stem.endswith(".profile") or yaml_path.stem == "README":
                continue
            try:
                data = yaml.safe_load(yaml_path.read_text())
                if data is None or not isinstance(data, dict):
                    continue
            except Exception:
                continue

            cap_id = data.get("id", yaml_path.stem)
            name = data.get("name", cap_id)
            current = float(data.get("maturity_current", 0))
            target = float(data.get("maturity_target", 0))
            gap = target - current

            if gap <= 0:
                continue

            results.append({
                "id": cap_id,
                "name": name,
                "current": current,
                "target": target,
                "gap": round(gap, 2),
                "gaps_list": data.get("gaps", []),
                "owner_agent": data.get("owner_agent", ""),
                "wave": data.get("wave", 99),
            })

        # Rank by gap size descending
        results.sort(key=lambda r: r["gap"], reverse=True)
        return results

    # ------------------------------------------------------------------
    # Knowledge needs
    # ------------------------------------------------------------------

    def identify_knowledge_needs(self, gaps: list[dict[str, Any]]) -> list[str]:
        """For each maturity gap, determine what knowledge is needed to close it.

        Uses maturity band templates:
          0->1: definitions, basic concepts
          1->2: documented processes, examples
          2->3: metrics, measurement frameworks
          3->4: optimization techniques, benchmarks
          4->5: industry-leading practices, innovation research
        """
        all_needs: list[str] = []

        for gap_rec in gaps:
            cap_name = gap_rec["name"]
            current = gap_rec["current"]
            target = gap_rec["target"]

            # Walk through each maturity band the capability must cross
            band_floor = int(math.floor(current))
            band_ceil = int(math.ceil(target))

            for low in range(band_floor, min(band_ceil, 5)):
                high = low + 1
                band_key = f"{low}-{high}"
                templates = _BAND_NEEDS.get(band_key, [])
                for tmpl in templates:
                    need = tmpl.format(cap=cap_name)
                    if need not in all_needs:
                        all_needs.append(need)

        return all_needs

    # ------------------------------------------------------------------
    # Single program generation
    # ------------------------------------------------------------------

    def generate_research_program(
        self,
        capability_name: str,
        current: float,
        target: float,
        knowledge_needs: list[str],
    ) -> ResearchProgramSpec:
        """Create a full research program for a capability gap.

        Generates research questions from knowledge needs, designs search
        strategies, sets acceptance criteria, and estimates duration.
        """
        cap_slug = capability_name.lower().replace(" ", "-").replace("&", "and")
        program_id = _deterministic_id("rp", cap_slug, str(current), str(target))

        # Generate research questions from knowledge needs
        research_questions: list[str] = []
        for need in knowledge_needs:
            research_questions.append(f"What is the current state of {need}?")
            research_questions.append(
                f"What evidence exists that {need} improves outcomes?"
            )
        # Add gap-specific questions
        if current < 1:
            research_questions.append(
                f"What is the minimum viable definition of {capability_name}?"
            )
        if target >= 4:
            research_questions.append(
                f"What do industry leaders consider best practice for {capability_name}?"
            )

        # Design search strategies based on bands to cross
        search_strategies: list[str] = []
        band_floor = int(math.floor(current))
        band_ceil = int(math.ceil(target))
        for low in range(band_floor, min(band_ceil, 5)):
            high = low + 1
            band_key = f"{low}-{high}"
            templates = _SEARCH_STRATEGIES.get(band_key, [])
            for tmpl in templates:
                strategy = tmpl.format(cap=capability_name)
                if strategy not in search_strategies:
                    search_strategies.append(strategy)

        # Set acceptance criteria
        gap_size = target - current
        min_sources = max(3, int(gap_size * 3))
        acceptance_criteria = [
            f"Minimum {min_sources} distinct sources per research question",
            f"Coverage of all maturity bands from {current:.1f} to {target:.1f}",
            "At least one academic/official source per band",
            "At least one practitioner source per band",
            "Findings validated against at least two independent sources",
        ]
        if target >= 4:
            acceptance_criteria.append(
                "At least one benchmark dataset or comparative study"
            )

        # Estimate duration: 1 week per maturity point of gap, minimum 1 week
        estimated_weeks = max(1, int(math.ceil(gap_size * 1.5)))

        # Determine priority from gap size
        if gap_size >= 3:
            priority = "critical"
        elif gap_size >= 2:
            priority = "high"
        elif gap_size >= 1:
            priority = "medium"
        else:
            priority = "low"

        return ResearchProgramSpec(
            id=program_id,
            name=f"Research: {capability_name} ({current:.1f} -> {target:.1f})",
            objective=(
                f"Close the maturity gap for {capability_name} from {current:.1f} "
                f"to {target:.1f} by acquiring targeted knowledge across "
                f"{len(knowledge_needs)} identified knowledge needs."
            ),
            target_capabilities=[cap_slug],
            knowledge_gaps=knowledge_needs,
            research_questions=research_questions,
            search_strategies=search_strategies,
            acceptance_criteria=acceptance_criteria,
            estimated_duration_weeks=estimated_weeks,
            priority=priority,
            status="proposed",
            created_at=_iso_now(),
        )

    # ------------------------------------------------------------------
    # Batch operations
    # ------------------------------------------------------------------

    def plan_all(self) -> list[ResearchProgramSpec]:
        """Generate research programs for all capability gaps."""
        gaps = self.analyze_maturity_gaps()
        programs: list[ResearchProgramSpec] = []

        for gap_rec in gaps:
            # Compute knowledge needs for this single capability
            needs = self.identify_knowledge_needs([gap_rec])
            if not needs:
                continue

            program = self.generate_research_program(
                capability_name=gap_rec["name"],
                current=gap_rec["current"],
                target=gap_rec["target"],
                knowledge_needs=needs,
            )
            programs.append(program)

        return programs

    def prioritize(
        self, programs: list[ResearchProgramSpec]
    ) -> list[ResearchProgramSpec]:
        """Sort programs by priority: critical first, then by impact/effort ratio.

        Impact is approximated by the number of knowledge gaps.
        Effort is approximated by estimated duration.
        """
        priority_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}

        def sort_key(p: ResearchProgramSpec) -> tuple[int, float]:
            rank = priority_rank.get(p.priority, 4)
            # Higher impact-to-effort is better; negate for ascending sort
            impact = len(p.knowledge_gaps)
            effort = max(p.estimated_duration_weeks, 1)
            ratio = -(impact / effort)
            return (rank, ratio)

        return sorted(programs, key=sort_key)

    def save_programs(self, programs: list[ResearchProgramSpec], path: Path) -> None:
        """Persist research programs to a YAML file."""
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "generated_at": _iso_now(),
            "program_count": len(programs),
            "programs": [p.model_dump() for p in programs],
        }
        path.write_text(yaml.dump(payload, default_flow_style=False, sort_keys=False))
