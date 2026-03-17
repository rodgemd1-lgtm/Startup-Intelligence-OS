"""Autonomous operating model evolution engine for the Collective Intelligence Framework.

Detects structural patterns in execution history -- misrouted tasks, emerging
domains without departments, agent performance clustering -- and proposes
concrete operating model changes (new agents, capabilities, departments,
routing changes, architecture changes) with full impact assessments.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .schemas import SystemEvolution


def _deterministic_id(prefix: str, *parts: str) -> str:
    raw = ":".join(parts)
    digest = hashlib.sha256(raw.encode()).hexdigest()[:12]
    return f"{prefix}-{digest}"


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Pattern types returned by detect_patterns
# ---------------------------------------------------------------------------
# Each pattern dict has: type, description, evidence, severity, data

_SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


class EvolutionEngine:
    """Detects structural patterns and proposes operating model evolutions.

    Analyses run history and memory tips to find:
    - Misrouted tasks (tasks repeatedly sent to the wrong department)
    - Emergent domains (task clusters without a dedicated department)
    - Performance clustering (agent groups that should be reorganised)
    - Structural bottlenecks (single agents overloaded across domains)
    """

    def __init__(
        self,
        workspace_root: Path,
        agents_dir: Path,
        departments_dir: Path,
    ) -> None:
        self.workspace_root = workspace_root
        self.agents_dir = agents_dir
        self.departments_dir = departments_dir
        self.capabilities_dir = workspace_root / ".startup-os" / "capabilities"

    # ------------------------------------------------------------------
    # Department loading
    # ------------------------------------------------------------------

    def _load_departments(self) -> dict[str, dict[str, Any]]:
        """Load all department YAML files."""
        departments: dict[str, dict[str, Any]] = {}
        if not self.departments_dir.exists():
            return departments

        for yaml_path in sorted(self.departments_dir.glob("*.yaml")):
            try:
                data = yaml.safe_load(yaml_path.read_text())
                if data and isinstance(data, dict):
                    dept_id = data.get("id", yaml_path.stem)
                    departments[dept_id] = data
            except Exception:
                continue

        return departments

    def _load_agent_names(self) -> set[str]:
        """Load all existing agent names."""
        names: set[str] = set()
        if not self.agents_dir.exists():
            return names
        for md_path in self.agents_dir.glob("*.md"):
            names.add(md_path.stem)
        return names

    # ------------------------------------------------------------------
    # Pattern detection
    # ------------------------------------------------------------------

    def detect_patterns(
        self, runs_dir: Path, tips_dir: Path
    ) -> list[dict[str, Any]]:
        """Analyse execution history for structural patterns.

        Returns a list of pattern dicts, each with:
          type: misrouted | emergent_domain | performance_cluster | bottleneck
          description: human-readable summary
          evidence: list of supporting evidence strings
          severity: critical | high | medium | low
          data: additional pattern-specific data
        """
        patterns: list[dict[str, Any]] = []

        # Run each detector
        patterns.extend(self._detect_misrouted_tasks(runs_dir))
        patterns.extend(self._detect_emergent_domains(runs_dir))
        patterns.extend(self._detect_performance_clusters(runs_dir, tips_dir))
        patterns.extend(self._detect_bottlenecks(runs_dir))
        patterns.extend(self._detect_maturity_tracking_gaps())

        # Sort by severity
        patterns.sort(key=lambda p: _SEVERITY_ORDER.get(p.get("severity", "low"), 4))
        return patterns

    def _detect_misrouted_tasks(self, runs_dir: Path) -> list[dict[str, Any]]:
        """Find tasks that appear to be repeatedly misrouted.

        A task is considered misrouted if:
        - The trigger agent differs from the expected department's agent
        - Multiple runs for the same domain route to different agents
        """
        patterns: list[dict[str, Any]] = []
        if not runs_dir.exists():
            return patterns

        # Collect routing data from runs
        route_map: dict[str, list[str]] = defaultdict(list)  # domain -> [agent_names]

        for yaml_path in sorted(runs_dir.glob("run-*.yaml")):
            try:
                data = yaml.safe_load(yaml_path.read_text())
                if data is None or not isinstance(data, dict):
                    continue
            except Exception:
                continue

            trigger = data.get("trigger", "")
            mode = data.get("mode", "")
            output = data.get("output") or {}
            recommendation = output.get("recommendation", "")

            # Extract agent from trigger
            agent = trigger.split(":")[0] if ":" in trigger else trigger

            # Infer domain
            domain = self._infer_domain(f"{trigger} {recommendation} {mode}")
            if agent and domain:
                route_map[domain].append(agent)

        # Look for domains routed to inconsistent agents
        departments = self._load_departments()
        dept_routing: dict[str, list[str]] = {}
        for dept_id, dept_data in departments.items():
            keywords = dept_data.get("routing_keywords", [])
            for kw in keywords:
                dept_routing[kw.lower()] = dept_routing.get(kw.lower(), [])
                dept_routing[kw.lower()].append(dept_id)

        for domain, agents in route_map.items():
            unique_agents = set(agents)
            if len(unique_agents) >= 3:
                # Many different agents handling the same domain
                agent_counts = Counter(agents)
                patterns.append({
                    "type": "misrouted",
                    "description": (
                        f"Domain '{domain}' is handled by {len(unique_agents)} "
                        f"different agents: {dict(agent_counts.most_common(5))}. "
                        f"This suggests unclear routing rules."
                    ),
                    "evidence": [
                        f"Agent '{a}' handled {c} {domain} tasks"
                        for a, c in agent_counts.most_common(5)
                    ],
                    "severity": "high" if len(unique_agents) >= 5 else "medium",
                    "data": {
                        "domain": domain,
                        "agents": dict(agent_counts),
                        "total_runs": len(agents),
                    },
                })

        return patterns

    def _detect_emergent_domains(self, runs_dir: Path) -> list[dict[str, Any]]:
        """Find task clusters that lack a dedicated department."""
        patterns: list[dict[str, Any]] = []
        if not runs_dir.exists():
            return patterns

        # Collect all task domains from runs
        domain_runs: dict[str, int] = Counter()

        for yaml_path in sorted(runs_dir.glob("run-*.yaml")):
            try:
                data = yaml.safe_load(yaml_path.read_text())
                if data is None or not isinstance(data, dict):
                    continue
            except Exception:
                continue

            trigger = data.get("trigger", "")
            output = data.get("output") or {}
            recommendation = output.get("recommendation", "")
            domain = self._infer_domain(f"{trigger} {recommendation}")
            domain_runs[domain] += 1

        # Load department domains
        departments = self._load_departments()
        covered_domains: set[str] = set()
        for dept_data in departments.values():
            keywords = dept_data.get("routing_keywords", [])
            for kw in keywords:
                covered_domains.add(kw.lower())
            # Also add the department name itself
            name = dept_data.get("name", "").lower()
            for word in name.split():
                if len(word) > 3:
                    covered_domains.add(word)

        # Find domains with significant activity but no department
        for domain, count in domain_runs.items():
            if count < 3:
                continue

            # Check if any department covers this domain
            is_covered = any(
                domain in kw or kw in domain for kw in covered_domains
            )

            if not is_covered:
                severity = "high" if count >= 8 else "medium"
                patterns.append({
                    "type": "emergent_domain",
                    "description": (
                        f"Domain '{domain}' has {count} runs but no dedicated "
                        f"department. Consider creating a department or expanding "
                        f"an existing one to cover this domain."
                    ),
                    "evidence": [
                        f"{count} runs in '{domain}' domain",
                        f"No department covers '{domain}' keywords",
                    ],
                    "severity": severity,
                    "data": {
                        "domain": domain,
                        "run_count": count,
                    },
                })

        return patterns

    def _detect_performance_clusters(
        self, runs_dir: Path, tips_dir: Path
    ) -> list[dict[str, Any]]:
        """Detect agent performance clustering suggesting team reorganisation.

        Looks for agents that consistently produce tips in domains outside their
        primary assignment, suggesting they should be reassigned or split.
        """
        patterns: list[dict[str, Any]] = []

        if not tips_dir.exists():
            return patterns

        # Collect tip domains by agent
        agent_tip_domains: dict[str, Counter] = defaultdict(Counter)

        for yaml_path in sorted(tips_dir.glob("*.yaml")):
            try:
                data = yaml.safe_load(yaml_path.read_text())
                if data is None:
                    continue
            except Exception:
                continue

            tip_list: list[dict[str, Any]] = []
            if isinstance(data, dict):
                if "tips" in data and isinstance(data["tips"], list):
                    tip_list = data["tips"]
                else:
                    tip_list = [data]
            elif isinstance(data, list):
                tip_list = [t for t in data if isinstance(t, dict)]

            for tip in tip_list:
                agent = tip.get("source_agent", "")
                domain = tip.get("task_domain", "")
                if agent and domain:
                    agent_tip_domains[agent][domain] += 1

        # Find agents whose tip production is spread across multiple domains
        for agent, domain_counts in agent_tip_domains.items():
            if len(domain_counts) < 2:
                continue

            total = sum(domain_counts.values())
            primary_domain, primary_count = domain_counts.most_common(1)[0]
            primary_ratio = primary_count / total

            # If less than 50% of tips are in the primary domain, flag it
            if primary_ratio < 0.5 and total >= 4:
                patterns.append({
                    "type": "performance_cluster",
                    "description": (
                        f"Agent '{agent}' produces tips across {len(domain_counts)} "
                        f"domains with only {primary_ratio:.0%} in primary domain "
                        f"'{primary_domain}'. Consider splitting into specialist agents."
                    ),
                    "evidence": [
                        f"Domain '{d}': {c} tips"
                        for d, c in domain_counts.most_common(5)
                    ],
                    "severity": "medium",
                    "data": {
                        "agent": agent,
                        "domain_distribution": dict(domain_counts),
                        "primary_domain": primary_domain,
                        "primary_ratio": round(primary_ratio, 2),
                    },
                })

        return patterns

    def _detect_bottlenecks(self, runs_dir: Path) -> list[dict[str, Any]]:
        """Detect structural bottlenecks where single agents are overloaded."""
        patterns: list[dict[str, Any]] = []
        if not runs_dir.exists():
            return patterns

        agent_load: Counter = Counter()

        for yaml_path in sorted(runs_dir.glob("run-*.yaml")):
            try:
                data = yaml.safe_load(yaml_path.read_text())
                if data is None or not isinstance(data, dict):
                    continue
            except Exception:
                continue

            trigger = data.get("trigger", "")
            agent = trigger.split(":")[0] if ":" in trigger else trigger
            if agent:
                agent_load[agent] += 1

        # Find agents handling disproportionate load
        total_runs = sum(agent_load.values())
        agent_count = len(agent_load)
        if agent_count == 0 or total_runs == 0:
            return patterns

        avg_load = total_runs / agent_count

        for agent, count in agent_load.most_common(5):
            if count > avg_load * 3 and count >= 5:
                patterns.append({
                    "type": "bottleneck",
                    "description": (
                        f"Agent '{agent}' handles {count} runs "
                        f"({count / total_runs:.0%} of total), which is "
                        f"{count / avg_load:.1f}x the average load. "
                        f"Consider distributing work or creating sub-specialists."
                    ),
                    "evidence": [
                        f"{count} runs handled by '{agent}'",
                        f"Average load per agent: {avg_load:.1f} runs",
                        f"Overload factor: {count / avg_load:.1f}x",
                    ],
                    "severity": "high" if count > avg_load * 5 else "medium",
                    "data": {
                        "agent": agent,
                        "run_count": count,
                        "overload_factor": round(count / avg_load, 1),
                    },
                })

        return patterns

    def _detect_maturity_tracking_gaps(self) -> list[dict[str, Any]]:
        """Detect capabilities that should be tracked but are not."""
        patterns: list[dict[str, Any]] = []

        departments = self._load_departments()
        if not self.capabilities_dir.exists():
            return patterns

        # Load existing capability IDs
        existing_caps: set[str] = set()
        for yaml_path in self.capabilities_dir.glob("*.yaml"):
            try:
                data = yaml.safe_load(yaml_path.read_text())
                if data and isinstance(data, dict) and "id" in data:
                    existing_caps.add(data["id"])
            except Exception:
                continue

        # Check department linked capabilities
        for dept_id, dept_data in departments.items():
            linked = dept_data.get("linked_capabilities", [])
            for cap_id in linked:
                if cap_id not in existing_caps:
                    patterns.append({
                        "type": "maturity_tracking_gap",
                        "description": (
                            f"Department '{dept_data.get('name', dept_id)}' links to "
                            f"capability '{cap_id}' which has no capability record. "
                            f"Create a capability record to enable maturity tracking."
                        ),
                        "evidence": [
                            f"Department '{dept_id}' references '{cap_id}'",
                            f"No file found in .startup-os/capabilities/ for '{cap_id}'",
                        ],
                        "severity": "medium",
                        "data": {
                            "department": dept_id,
                            "missing_capability": cap_id,
                        },
                    })

        return patterns

    @staticmethod
    def _infer_domain(text: str) -> str:
        """Infer a domain label from free text."""
        text_lower = text.lower()
        domain_keywords = {
            "simulation": ["simulated", "monte carlo", "simulation", "scenario"],
            "decision": ["debate", "decision", "option", "recommend"],
            "finance": ["finance", "revenue", "burn", "runway"],
            "maturity": ["maturity", "benchmark", "eval", "scoring"],
            "training": ["training", "job studio", "corpus", "learning"],
            "research": ["research", "analysis", "study", "evidence"],
            "marketing": ["marketing", "content", "brand", "narrative"],
            "product": ["product", "ux", "experience", "design"],
            "engineering": ["engineering", "build", "architecture", "system"],
            "customer": ["customer", "persona", "user", "journey"],
        }

        scores: dict[str, int] = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[domain] = score

        if scores:
            return max(scores, key=scores.get)  # type: ignore[arg-type]
        return "general"

    # ------------------------------------------------------------------
    # Evolution proposals
    # ------------------------------------------------------------------

    def propose_evolution(self, pattern: dict[str, Any]) -> SystemEvolution:
        """Generate a specific evolution proposal from a detected pattern."""
        pattern_type = pattern.get("type", "unknown")
        description = pattern.get("description", "")
        evidence = pattern.get("evidence", [])
        data = pattern.get("data", {})

        # Map pattern type to evolution type
        type_map: dict[str, str] = {
            "misrouted": "routing_change",
            "emergent_domain": "new_department",
            "performance_cluster": "new_agent",
            "bottleneck": "new_agent",
            "maturity_tracking_gap": "new_capability",
        }
        evolution_type = type_map.get(pattern_type, "architecture_change")

        # Generate rationale
        rationale = self._generate_rationale(pattern_type, data)

        # Generate impact assessment
        impact = self._assess_impact_from_pattern(pattern_type, data)

        evo_id = _deterministic_id("evo", pattern_type, description[:50])

        return SystemEvolution(
            id=evo_id,
            evolution_type=evolution_type,  # type: ignore[arg-type]
            description=description,
            rationale=rationale,
            evidence=evidence,
            status="proposed",
            impact_assessment=impact,
            created_at=_iso_now(),
        )

    @staticmethod
    def _generate_rationale(pattern_type: str, data: dict[str, Any]) -> str:
        """Generate a rationale for the evolution proposal."""
        if pattern_type == "misrouted":
            domain = data.get("domain", "unknown")
            total = data.get("total_runs", 0)
            return (
                f"The '{domain}' domain has {total} runs spread across multiple "
                f"agents with no clear routing. Establishing clear routing rules "
                f"will reduce confusion and improve task completion quality."
            )
        elif pattern_type == "emergent_domain":
            domain = data.get("domain", "unknown")
            count = data.get("run_count", 0)
            return (
                f"A new domain '{domain}' has emerged with {count} runs and no "
                f"department ownership. Creating a department ensures tasks are "
                f"routed correctly and knowledge accumulates systematically."
            )
        elif pattern_type == "performance_cluster":
            agent = data.get("agent", "unknown")
            domains = data.get("domain_distribution", {})
            return (
                f"Agent '{agent}' operates across {len(domains)} domains, "
                f"diluting its effectiveness. Splitting into specialist agents "
                f"will improve quality in each domain."
            )
        elif pattern_type == "bottleneck":
            agent = data.get("agent", "unknown")
            factor = data.get("overload_factor", 1)
            return (
                f"Agent '{agent}' handles {factor}x the average load. "
                f"Creating sub-specialist agents will distribute work more "
                f"evenly and reduce single-point-of-failure risk."
            )
        elif pattern_type == "maturity_tracking_gap":
            cap = data.get("missing_capability", "unknown")
            return (
                f"Capability '{cap}' is referenced by a department but has no "
                f"tracking record. Creating the record enables maturity monitoring "
                f"and gap analysis."
            )
        return "Pattern detected that warrants operating model adjustment."

    def assess_impact(self, evolution: SystemEvolution) -> str:
        """Generate an impact assessment for an evolution proposal.

        Returns a structured assessment covering:
        - What changes
        - What breaks
        - What improves
        - Reversibility
        """
        evo_type = evolution.evolution_type

        what_changes: str
        what_breaks: str
        what_improves: str
        reversibility: str

        if evo_type == "new_agent":
            what_changes = "A new specialist agent is added to the agent roster."
            what_breaks = "Routing rules may need updating. Existing agents may receive fewer tasks in the affected domain."
            what_improves = "Task quality in the domain improves. Load is better distributed."
            reversibility = "Fully reversible. Remove the agent file and revert routing."

        elif evo_type == "new_capability":
            what_changes = "A new capability record is created with maturity tracking."
            what_breaks = "Nothing breaks. New record is additive."
            what_improves = "Gap analysis and predictions now cover the new capability."
            reversibility = "Fully reversible. Remove the capability YAML file."

        elif evo_type == "new_department":
            what_changes = "A new department is created with routing keywords and agent assignments."
            what_breaks = "Tasks previously scattered across departments will be re-routed."
            what_improves = "Clear ownership for the emerging domain. Better knowledge accumulation."
            reversibility = "Reversible with routing adjustment. Move tasks back to original departments."

        elif evo_type == "routing_change":
            what_changes = "Routing rules are updated for one or more domains."
            what_breaks = "Agents previously receiving these tasks will see fewer. Operator workflows may need updating."
            what_improves = "Tasks reach the correct specialist faster. Fewer misrouted tasks."
            reversibility = "Fully reversible. Revert routing keyword changes."

        elif evo_type == "architecture_change":
            what_changes = "Structural change to the operating model."
            what_breaks = "May affect multiple departments and agents. Careful migration needed."
            what_improves = "Removes structural bottleneck or inefficiency."
            reversibility = "Partially reversible. Requires careful rollback plan."

        else:
            what_changes = "Operating model change."
            what_breaks = "Unknown -- requires analysis."
            what_improves = "Unknown -- requires analysis."
            reversibility = "Unknown."

        return (
            f"**What changes:** {what_changes}\n"
            f"**What breaks:** {what_breaks}\n"
            f"**What improves:** {what_improves}\n"
            f"**Reversibility:** {reversibility}"
        )

    @staticmethod
    def _assess_impact_from_pattern(pattern_type: str, data: dict[str, Any]) -> str:
        """Shortcut impact assessment from pattern data without a full SystemEvolution."""
        impact_templates: dict[str, str] = {
            "misrouted": (
                "Routing correction reduces task misdirection. "
                "Affected agents: {agents}. Reversible."
            ),
            "emergent_domain": (
                "New department creates clear ownership for '{domain}' domain. "
                "{count} existing runs will be retroactively covered. Additive change."
            ),
            "performance_cluster": (
                "Agent split improves specialist quality. "
                "Agent '{agent}' would be decomposed into domain specialists. "
                "Requires routing update."
            ),
            "bottleneck": (
                "Load redistribution from '{agent}' ({factor}x overloaded) "
                "to new sub-specialists. Improves throughput and resilience."
            ),
            "maturity_tracking_gap": (
                "New capability record enables maturity tracking for '{cap}'. "
                "Purely additive -- no breaking changes."
            ),
        }

        template = impact_templates.get(pattern_type, "Impact requires manual assessment.")

        # Fill in template variables safely
        try:
            agents_val = data.get("agents", {})
            agents_str = ", ".join(
                str(a) for a in (agents_val.keys() if isinstance(agents_val, dict) else [])
            )
            return template.format(
                agents=agents_str,
                domain=data.get("domain", "unknown"),
                count=data.get("run_count", 0),
                agent=data.get("agent", "unknown"),
                factor=data.get("overload_factor", 1),
                cap=data.get("missing_capability", "unknown"),
            )
        except (KeyError, TypeError):
            return template

    # ------------------------------------------------------------------
    # Full pipeline
    # ------------------------------------------------------------------

    def generate_proposals(
        self, runs_dir: Path, tips_dir: Path
    ) -> list[SystemEvolution]:
        """Full pipeline: detect patterns, generate evolution proposals."""
        patterns = self.detect_patterns(runs_dir, tips_dir)
        proposals: list[SystemEvolution] = []

        for pattern in patterns:
            evolution = self.propose_evolution(pattern)
            # Re-assess impact with full SystemEvolution context
            evolution.impact_assessment = self.assess_impact(evolution)
            proposals.append(evolution)

        return proposals

    def save_proposals(self, proposals: list[SystemEvolution], path: Path) -> None:
        """Save proposals to individual YAML files in a directory."""
        path.mkdir(parents=True, exist_ok=True)
        for proposal in proposals:
            file_path = path / f"{proposal.id}.yaml"
            file_path.write_text(
                yaml.dump(proposal.model_dump(), default_flow_style=False, sort_keys=False)
            )

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def format_proposals(self, proposals: list[SystemEvolution]) -> str:
        """Format proposals as a markdown document for human review."""
        lines: list[str] = [
            "# Operating Model Evolution Proposals",
            "",
            f"**Generated:** {_iso_now()}",
            f"**Proposals:** {len(proposals)}",
            "",
        ]

        if not proposals:
            lines.append("No evolution proposals detected at this time.")
            return "\n".join(lines)

        # Group by type
        by_type: dict[str, list[SystemEvolution]] = defaultdict(list)
        for p in proposals:
            by_type[p.evolution_type].append(p)

        type_labels = {
            "new_agent": "New Agent Proposals",
            "new_capability": "New Capability Proposals",
            "new_department": "New Department Proposals",
            "routing_change": "Routing Change Proposals",
            "architecture_change": "Architecture Change Proposals",
        }

        for evo_type, label in type_labels.items():
            group = by_type.get(evo_type, [])
            if not group:
                continue

            lines.extend([
                f"## {label}",
                "",
            ])

            for idx, proposal in enumerate(group, 1):
                lines.extend([
                    f"### {idx}. {proposal.description[:100]}",
                    "",
                    f"**ID:** `{proposal.id}`",
                    f"**Status:** {proposal.status}",
                    "",
                    f"**Rationale:** {proposal.rationale}",
                    "",
                    "**Evidence:**",
                ])
                for ev in proposal.evidence:
                    lines.append(f"- {ev}")
                lines.extend([
                    "",
                    "**Impact Assessment:**",
                    proposal.impact_assessment,
                    "",
                    "---",
                    "",
                ])

        return "\n".join(lines)
