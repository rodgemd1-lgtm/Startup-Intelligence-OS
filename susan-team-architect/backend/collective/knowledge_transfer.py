"""Cross-agent knowledge transfer engine for the Collective Intelligence Framework.

Maps agent domains, identifies transferable tips across domain boundaries,
generalizes entity-specific details, and executes knowledge transfers between
agents with full audit records.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .schemas import KnowledgeTransfer


def _deterministic_id(prefix: str, *parts: str) -> str:
    raw = ":".join(parts)
    digest = hashlib.sha256(raw.encode()).hexdigest()[:12]
    return f"{prefix}-{digest}"


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Generalization patterns for entity-specific details
# ---------------------------------------------------------------------------

_GENERALIZATION_PATTERNS: list[tuple[str, str]] = [
    # Company/product names -> placeholder
    (r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}(?:\s+(?:Inc|LLC|Corp|Ltd)\.?)\b", "<company>"),
    # URLs
    (r"https?://[^\s]+", "<url>"),
    # Email addresses
    (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "<email>"),
    # Specific dollar amounts
    (r"\$[\d,]+(?:\.\d{2})?", "<amount>"),
    # Dates in common formats
    (r"\b\d{4}-\d{2}-\d{2}\b", "<date>"),
    # Specific percentages with context
    (r"\b\d+(?:\.\d+)?%", "<percentage>"),
]


def _generalize_text(text: str, additional_entities: list[str] | None = None) -> str:
    """Replace entity-specific details with generic placeholders."""
    result = text

    # Apply regex patterns
    for pattern, replacement in _GENERALIZATION_PATTERNS:
        result = re.sub(pattern, replacement, result)

    # Replace additional known entities
    if additional_entities:
        for entity in additional_entities:
            if entity and len(entity) > 2:
                result = result.replace(entity, "<entity>")

    return result


class KnowledgeTransferEngine:
    """Manages cross-agent knowledge sharing via tip generalization and transfer.

    Reads agent definitions to map domains, scans tips for cross-domain
    insights, generalizes entity-specific details, and creates transfer
    records linking source agents to target agents.
    """

    def __init__(self, tips_dir: Path, agents_dir: Path) -> None:
        self.tips_dir = tips_dir
        self.agents_dir = agents_dir
        self._domain_map: dict[str, list[str]] | None = None

    # ------------------------------------------------------------------
    # Agent domain mapping
    # ------------------------------------------------------------------

    def map_agent_domains(self) -> dict[str, list[str]]:
        """Read all agent definitions, extract domains and routing keywords.

        Returns {domain: [agent_names]}.
        """
        if self._domain_map is not None:
            return self._domain_map

        domain_agents: dict[str, list[str]] = {}

        if not self.agents_dir.exists():
            self._domain_map = domain_agents
            return domain_agents

        for md_path in sorted(self.agents_dir.glob("*.md")):
            try:
                text = md_path.read_text()
            except Exception:
                continue

            agent_name = md_path.stem

            # Parse frontmatter
            domains: list[str] = []
            if text.startswith("---"):
                parts = text.split("---", 2)
                if len(parts) >= 3:
                    try:
                        frontmatter = yaml.safe_load(parts[1]) or {}
                    except Exception:
                        frontmatter = {}
                    name = frontmatter.get("name", agent_name)
                    description = frontmatter.get("description", "")

                    # Infer domains from name and description
                    domains = self._infer_domains(name, description)

            # Also scan the body for domain hints
            body_domains = self._infer_domains_from_body(text)
            for d in body_domains:
                if d not in domains:
                    domains.append(d)

            # If no domains detected, assign "general"
            if not domains:
                domains = ["general"]

            for domain in domains:
                if domain not in domain_agents:
                    domain_agents[domain] = []
                if agent_name not in domain_agents[domain]:
                    domain_agents[domain].append(agent_name)

        self._domain_map = domain_agents
        return domain_agents

    @staticmethod
    def _infer_domains(name: str, description: str) -> list[str]:
        """Infer domain labels from agent name and description."""
        combined = f"{name} {description}".lower()
        domain_keywords: dict[str, list[str]] = {
            "research": ["research", "analysis", "evidence", "study"],
            "strategy": ["strategy", "planning", "vision", "roadmap"],
            "engineering": ["engineering", "build", "architecture", "code", "system"],
            "marketing": ["marketing", "content", "brand", "narrative", "growth"],
            "product": ["product", "ux", "experience", "design", "user"],
            "finance": ["finance", "revenue", "fundraising", "ledger"],
            "data_science": ["data science", "analytics", "data", "metrics"],
            "customer": ["customer", "persona", "user research", "journey"],
            "film": ["film", "cinema", "video", "editing", "vfx"],
            "health": ["health", "fitness", "nutrition", "exercise", "workout"],
            "legal": ["legal", "compliance", "rights", "governance"],
            "security": ["security", "sentinel", "protection"],
            "recruiting": ["recruiting", "talent", "hiring"],
        }

        found: list[str] = []
        for domain, keywords in domain_keywords.items():
            if any(kw in combined for kw in keywords):
                found.append(domain)
        return found

    @staticmethod
    def _infer_domains_from_body(text: str) -> list[str]:
        """Scan agent body text for domain role declarations."""
        domains: list[str] = []
        text_lower = text.lower()

        # Look for "## Your Role" or "## Identity" sections
        role_patterns = {
            "research": ["research lead", "evidence synthesis", "research director"],
            "strategy": ["strategy lead", "strategic planning", "vision architect"],
            "engineering": ["engineering lead", "architecture", "implementation"],
            "marketing": ["marketing lead", "content strategy", "brand"],
            "product": ["product lead", "experience design", "ux"],
        }
        for domain, phrases in role_patterns.items():
            if any(phrase in text_lower for phrase in phrases):
                if domain not in domains:
                    domains.append(domain)

        return domains

    # ------------------------------------------------------------------
    # Tip loading
    # ------------------------------------------------------------------

    def _load_tips_for_agent(self, agent_name: str) -> list[dict[str, Any]]:
        """Load all tip YAML files that originated from a specific agent."""
        tips: list[dict[str, Any]] = []

        if not self.tips_dir.exists():
            return tips

        for yaml_path in sorted(self.tips_dir.glob("*.yaml")):
            try:
                data = yaml.safe_load(yaml_path.read_text())
                if data is None:
                    continue
            except Exception:
                continue

            # Handle both single tip and list-of-tips formats
            tip_list: list[dict[str, Any]] = []
            if isinstance(data, dict):
                if "tips" in data and isinstance(data["tips"], list):
                    tip_list = data["tips"]
                else:
                    tip_list = [data]
            elif isinstance(data, list):
                tip_list = data

            for tip in tip_list:
                if not isinstance(tip, dict):
                    continue
                source = tip.get("source_agent", "")
                if source == agent_name:
                    tips.append(tip)

        return tips

    def _load_all_tips(self) -> list[dict[str, Any]]:
        """Load all tips from all YAML files in the tips directory."""
        all_tips: list[dict[str, Any]] = []

        if not self.tips_dir.exists():
            return all_tips

        for yaml_path in sorted(self.tips_dir.glob("*.yaml")):
            try:
                data = yaml.safe_load(yaml_path.read_text())
                if data is None:
                    continue
            except Exception:
                continue

            if isinstance(data, dict):
                if "tips" in data and isinstance(data["tips"], list):
                    all_tips.extend(data["tips"])
                else:
                    all_tips.append(data)
            elif isinstance(data, list):
                all_tips.extend(t for t in data if isinstance(t, dict))

        return all_tips

    # ------------------------------------------------------------------
    # Transfer identification
    # ------------------------------------------------------------------

    def find_transferable_tips(
        self, source_agent: str, target_domain: str
    ) -> list[dict[str, Any]]:
        """Find tips from source_agent that could benefit agents in target_domain.

        Reads tips from the source agent, filters to those mentioning target
        domain concepts, and generalizes entity-specific details.
        """
        tips = self._load_tips_for_agent(source_agent)
        transferable: list[dict[str, Any]] = []

        # Build keyword set for the target domain
        domain_keywords: dict[str, list[str]] = {
            "research": ["research", "evidence", "source", "study", "finding"],
            "strategy": ["strategy", "plan", "vision", "roadmap", "scenario"],
            "engineering": ["build", "code", "architecture", "system", "implementation"],
            "marketing": ["marketing", "content", "brand", "audience", "growth"],
            "product": ["product", "ux", "experience", "design", "user"],
            "finance": ["finance", "revenue", "cost", "budget", "runway"],
            "data_science": ["data", "metric", "analytics", "dashboard", "measure"],
            "customer": ["customer", "persona", "journey", "feedback", "satisfaction"],
            "health": ["health", "fitness", "exercise", "nutrition", "recovery"],
        }
        target_kw = domain_keywords.get(target_domain, [target_domain])

        for tip in tips:
            content = tip.get("content", "").lower()
            # Check if the tip mentions concepts relevant to the target domain
            relevance_score = sum(1 for kw in target_kw if kw in content)
            if relevance_score > 0:
                # Generalize entity-specific details
                generalized = dict(tip)
                generalized["content"] = _generalize_text(tip.get("content", ""))
                generalized["_relevance_score"] = relevance_score
                generalized["_target_domain"] = target_domain
                transferable.append(generalized)

        # Sort by relevance
        transferable.sort(key=lambda t: t.get("_relevance_score", 0), reverse=True)
        return transferable

    def identify_transfer_opportunities(self) -> list[dict[str, Any]]:
        """Scan all tips and agents for cross-domain transfer opportunities.

        For each agent's tips, check if they contain insights relevant to
        other domains, and flag those as transfer opportunities.
        """
        domain_map = self.map_agent_domains()
        all_tips = self._load_all_tips()
        opportunities: list[dict[str, Any]] = []

        # Group tips by source agent
        tips_by_agent: dict[str, list[dict[str, Any]]] = {}
        for tip in all_tips:
            agent = tip.get("source_agent", "unknown")
            if agent not in tips_by_agent:
                tips_by_agent[agent] = []
            tips_by_agent[agent].append(tip)

        # Find the domains each agent belongs to
        agent_domains: dict[str, list[str]] = {}
        for domain, agents in domain_map.items():
            for agent in agents:
                if agent not in agent_domains:
                    agent_domains[agent] = []
                agent_domains[agent].append(domain)

        # For each agent's tips, check relevance to OTHER domains
        for agent, tips in tips_by_agent.items():
            own_domains = set(agent_domains.get(agent, ["general"]))

            for domain in domain_map:
                if domain in own_domains:
                    continue  # Skip own domain

                # Check each tip for cross-domain relevance
                transferable = self.find_transferable_tips(agent, domain)
                if transferable:
                    target_agents = domain_map.get(domain, [])
                    opportunities.append({
                        "source_agent": agent,
                        "source_domains": list(own_domains),
                        "target_domain": domain,
                        "target_agents": target_agents,
                        "transferable_tip_count": len(transferable),
                        "tip_ids": [
                            t.get("id", "unknown") for t in transferable[:10]
                        ],
                    })

        # Sort by number of transferable tips descending
        opportunities.sort(
            key=lambda o: o["transferable_tip_count"], reverse=True
        )
        return opportunities

    # ------------------------------------------------------------------
    # Transfer execution
    # ------------------------------------------------------------------

    def execute_transfer(
        self,
        source: str,
        targets: list[str],
        tip_ids: list[str],
    ) -> KnowledgeTransfer:
        """Create a transfer record and generalized copies of tips for targets.

        Reads the specified tips from the source agent, generalizes them,
        and writes transfer copies tagged for each target agent.
        """
        transfer_id = _deterministic_id("kt", source, ":".join(targets), _iso_now())

        # Load source tips and filter to requested IDs
        all_source_tips = self._load_tips_for_agent(source)
        selected_tips = [t for t in all_source_tips if t.get("id") in tip_ids]

        # Generalize and create copies for each target
        generalized_tips: list[dict[str, Any]] = []
        for tip in selected_tips:
            gen_tip = dict(tip)
            gen_tip["content"] = _generalize_text(tip.get("content", ""))
            gen_tip["id"] = _deterministic_id(
                "tip", tip.get("id", ""), "transfer", transfer_id
            )
            gen_tip["source_transfer_id"] = transfer_id
            gen_tip["original_source_agent"] = source
            gen_tip["transfer_targets"] = targets
            generalized_tips.append(gen_tip)

        # Persist generalized tips to transfers directory
        transfers_dir = self.tips_dir.parent / "transfers"
        transfers_dir.mkdir(parents=True, exist_ok=True)

        if generalized_tips:
            transfer_file = transfers_dir / f"transfer-{transfer_id}.yaml"
            payload = {
                "transfer_id": transfer_id,
                "source_agent": source,
                "target_agents": targets,
                "created_at": _iso_now(),
                "tips": generalized_tips,
            }
            transfer_file.write_text(
                yaml.dump(payload, default_flow_style=False, sort_keys=False)
            )

        # Infer domain from source agent domains
        domain_map = self.map_agent_domains()
        source_domains: list[str] = []
        for d, agents in domain_map.items():
            if source in agents:
                source_domains.append(d)
        domain = source_domains[0] if source_domains else "general"

        return KnowledgeTransfer(
            id=transfer_id,
            source_agent=source,
            target_agents=targets,
            tip_ids=[t.get("id", "") for t in generalized_tips],
            domain=domain,
            transfer_type="generalized",
            created_at=_iso_now(),
        )

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def generate_transfer_report(self) -> str:
        """Generate a markdown report of transfer activity and opportunities."""
        domain_map = self.map_agent_domains()
        opportunities = self.identify_transfer_opportunities()

        lines: list[str] = [
            "# Knowledge Transfer Report",
            "",
            f"**Generated:** {_iso_now()}",
            "",
            "## Agent Domain Map",
            "",
            f"| Domain | Agent Count | Agents |",
            f"|--------|-------------|--------|",
        ]

        for domain in sorted(domain_map.keys()):
            agents = domain_map[domain]
            agent_str = ", ".join(agents[:5])
            if len(agents) > 5:
                agent_str += f" (+{len(agents) - 5} more)"
            lines.append(f"| {domain} | {len(agents)} | {agent_str} |")

        lines.extend([
            "",
            "## Transfer Opportunities",
            "",
            f"**Total opportunities identified:** {len(opportunities)}",
            "",
        ])

        if opportunities:
            lines.append(
                "| Source Agent | Target Domain | Transferable Tips |"
            )
            lines.append(
                "|-------------|---------------|-------------------|"
            )
            for opp in opportunities[:20]:
                lines.append(
                    f"| {opp['source_agent']} "
                    f"| {opp['target_domain']} "
                    f"| {opp['transferable_tip_count']} |"
                )

        # Check for existing transfers
        transfers_dir = self.tips_dir.parent / "transfers"
        transfer_count = 0
        if transfers_dir.exists():
            transfer_count = len(list(transfers_dir.glob("transfer-*.yaml")))

        lines.extend([
            "",
            "## Transfer History",
            "",
            f"**Total transfers executed:** {transfer_count}",
            "",
        ])

        return "\n".join(lines)
