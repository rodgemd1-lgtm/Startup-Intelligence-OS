"""Autonomous agent creation factory for the Collective Intelligence Framework.

Scans run data for recurring task patterns, identifies unserved patterns that
lack a specialist agent, designs new agent blueprints with system prompts
and routing keywords, validates them against the existing agent roster, and
generates standard .md agent definition files.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .schemas import AgentBlueprint


def _deterministic_id(prefix: str, *parts: str) -> str:
    raw = ":".join(parts)
    digest = hashlib.sha256(raw.encode()).hexdigest()[:12]
    return f"{prefix}-{digest}"


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slugify(text: str) -> str:
    """Convert text into a lowercase kebab-case slug."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


# ---------------------------------------------------------------------------
# Model tier heuristics
# ---------------------------------------------------------------------------

_COMPLEXITY_KEYWORDS = {
    "high": [
        "architecture", "strategy", "design", "innovation", "debate",
        "synthesis", "complex", "novel", "creative",
    ],
    "low": [
        "format", "template", "convert", "copy", "list", "extract",
        "schedule", "simple", "routine", "standard",
    ],
}


def _assign_model_tier(pattern: dict[str, Any]) -> str:
    """Assign model tier based on task complexity.

    haiku  -- simple recurring patterns
    sonnet -- complex recurring patterns
    opus   -- novel patterns requiring deep reasoning
    """
    desc = (pattern.get("description", "") + " " + pattern.get("domain", "")).lower()
    occurrences = pattern.get("occurrences", 0)

    high_signals = sum(1 for kw in _COMPLEXITY_KEYWORDS["high"] if kw in desc)
    low_signals = sum(1 for kw in _COMPLEXITY_KEYWORDS["low"] if kw in desc)

    if occurrences <= 3 and high_signals > low_signals:
        return "opus"
    elif low_signals > high_signals:
        return "haiku"
    else:
        return "sonnet"


class AgentFactory:
    """Analyses task patterns in run history and proposes new specialist agents.

    Pipeline: analyze_task_patterns -> design_agent -> validate_blueprint -> generate_agent_file
    """

    def __init__(self, agents_dir: Path, performance_data_dir: Path) -> None:
        self.agents_dir = agents_dir
        self.performance_data_dir = performance_data_dir
        self._existing_agents: dict[str, dict[str, Any]] | None = None
        self._existing_keywords: set[str] | None = None

    # ------------------------------------------------------------------
    # Existing agent inventory
    # ------------------------------------------------------------------

    def _load_existing_agents(self) -> dict[str, dict[str, Any]]:
        """Load all existing agent .md files and parse their frontmatter."""
        if self._existing_agents is not None:
            return self._existing_agents

        agents: dict[str, dict[str, Any]] = {}
        if not self.agents_dir.exists():
            self._existing_agents = agents
            return agents

        for md_path in sorted(self.agents_dir.glob("*.md")):
            try:
                text = md_path.read_text()
                # Parse YAML frontmatter between --- markers
                if text.startswith("---"):
                    parts = text.split("---", 2)
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1]) or {}
                        agents[md_path.stem] = {
                            "name": frontmatter.get("name", md_path.stem),
                            "description": frontmatter.get("description", ""),
                            "model": frontmatter.get("model", ""),
                            "path": str(md_path),
                            "body": parts[2].strip(),
                        }
            except Exception:
                continue

        self._existing_agents = agents
        return agents

    def _load_existing_keywords(self) -> set[str]:
        """Collect all routing keywords from existing agents."""
        if self._existing_keywords is not None:
            return self._existing_keywords

        agents = self._load_existing_agents()
        keywords: set[str] = set()
        for info in agents.values():
            desc = info.get("description", "").lower()
            name = info.get("name", "").lower()
            # Extract keywords from name and description
            words = set(re.findall(r"[a-z]{3,}", f"{name} {desc}"))
            keywords.update(words)

        self._existing_keywords = keywords
        return keywords

    # ------------------------------------------------------------------
    # Pattern analysis
    # ------------------------------------------------------------------

    def analyze_task_patterns(self, runs_dir: Path) -> list[dict[str, Any]]:
        """Scan run data for recurring task patterns.

        Groups runs by task_type/domain, identifies patterns with >3 occurrences,
        checks if a specialist agent exists, and returns unserved patterns.
        """
        if not runs_dir.exists():
            return []

        # Collect task info from all run files
        task_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for yaml_path in sorted(runs_dir.glob("run-*.yaml")):
            try:
                data = yaml.safe_load(yaml_path.read_text())
                if data is None or not isinstance(data, dict):
                    continue
            except Exception:
                continue

            # Derive task type from trigger and mode
            trigger = data.get("trigger", "")
            mode = data.get("mode", "general")
            output = data.get("output") or {}
            recommendation = output.get("recommendation", "")

            # Extract domain from trigger (format: "agent:task-description")
            if ":" in trigger:
                agent_part, task_part = trigger.split(":", 1)
            else:
                agent_part = trigger
                task_part = ""

            # Group key: domain derived from task description keywords
            domain = self._infer_domain_from_text(
                f"{task_part} {recommendation} {mode}"
            )
            group_key = f"{domain}:{mode}"

            task_groups[group_key].append({
                "run_id": data.get("id", ""),
                "trigger": trigger,
                "agent": agent_part,
                "task": task_part,
                "mode": mode,
                "status": data.get("status", ""),
                "recommendation": recommendation[:200],
            })

        # Filter to patterns with >3 occurrences
        existing_agents = self._load_existing_agents()
        agent_names_lower = {name.lower() for name in existing_agents}

        unserved: list[dict[str, Any]] = []
        for group_key, runs in task_groups.items():
            if len(runs) < 3:
                continue

            domain, mode = group_key.split(":", 1) if ":" in group_key else (group_key, "general")

            # Check if a specialist exists for this domain
            has_specialist = any(
                domain in agent_name or agent_name in domain
                for agent_name in agent_names_lower
            )

            if not has_specialist:
                # Gather representative descriptions
                descriptions = [r["recommendation"] for r in runs if r["recommendation"]]
                desc_summary = "; ".join(descriptions[:3])

                unserved.append({
                    "domain": domain,
                    "mode": mode,
                    "occurrences": len(runs),
                    "description": desc_summary,
                    "sample_run_ids": [r["run_id"] for r in runs[:5]],
                    "agents_used": list({r["agent"] for r in runs if r["agent"]}),
                })

        # Sort by occurrence count descending
        unserved.sort(key=lambda p: p["occurrences"], reverse=True)
        return unserved

    @staticmethod
    def _infer_domain_from_text(text: str) -> str:
        """Infer a domain label from free text."""
        text_lower = text.lower()
        domain_keywords = {
            "simulation": ["simulated", "monte carlo", "simulation", "scenario"],
            "decision": ["debate", "decision", "option", "recommend"],
            "finance": ["finance", "revenue", "burn", "runway", "ledger"],
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
    # Agent design
    # ------------------------------------------------------------------

    def design_agent(self, pattern: dict[str, Any]) -> AgentBlueprint:
        """Create a new agent blueprint from an observed task pattern.

        Generates name, system prompt, model tier, routing keywords, and
        performance baseline from the pattern data.
        """
        domain = pattern.get("domain", "general")
        description = pattern.get("description", "")
        mode = pattern.get("mode", "general")
        occurrences = pattern.get("occurrences", 0)

        # Generate agent name
        agent_name = f"{domain}-specialist"
        agent_slug = _slugify(agent_name)
        blueprint_id = _deterministic_id("ab", agent_slug, _iso_now())

        # Assign model tier
        model_tier = _assign_model_tier(pattern)

        # Derive routing keywords from domain and descriptions
        desc_words = re.findall(r"[a-z]{4,}", description.lower())
        word_freq = Counter(desc_words)
        top_keywords = [w for w, _ in word_freq.most_common(8)]
        routing_keywords = list(dict.fromkeys([domain] + top_keywords))[:10]

        # Determine tools from mode
        tool_map: dict[str, list[str]] = {
            "simulation": ["search_knowledge", "run_simulation", "analyze_results"],
            "research": ["search_knowledge", "ingest_url", "summarize"],
            "decision": ["search_knowledge", "run_debate", "score_options"],
            "general": ["search_knowledge"],
        }
        tools = tool_map.get(mode, tool_map["general"])

        # Generate system prompt
        system_prompt = self._generate_system_prompt(
            agent_name=agent_name,
            domain=domain,
            description=description,
            tools=tools,
        )

        # Performance baseline from pattern
        agents_used = pattern.get("agents_used", [])
        performance_baseline = {
            "source_pattern_occurrences": occurrences,
            "predecessor_agents": agents_used,
            "expected_task_frequency": f"{occurrences}+ runs observed",
        }

        # Determine parent agent from most common predecessor
        parent_agent = agents_used[0] if agents_used else None

        return AgentBlueprint(
            id=blueprint_id,
            name=agent_name,
            description=(
                f"Specialist agent for {domain} tasks. "
                f"Auto-proposed from {occurrences} observed task patterns. "
                f"{description[:200]}"
            ),
            model=model_tier,  # type: ignore[arg-type]
            system_prompt=system_prompt,
            tools=tools,
            routing_keywords=routing_keywords,
            domain=domain,
            parent_agent=parent_agent,
            performance_baseline=performance_baseline,
            created_at=_iso_now(),
            status="proposed",
        )

    @staticmethod
    def _generate_system_prompt(
        agent_name: str,
        domain: str,
        description: str,
        tools: list[str],
    ) -> str:
        """Generate a system prompt based on observed patterns."""
        tool_list = "\n".join(f"- {t}" for t in tools)
        desc_snippet = description[:300] if description else f"Tasks in the {domain} domain."

        return f"""You are {agent_name}, a specialist agent for the {domain} domain.

## Identity
You handle {domain}-related tasks with precision and domain expertise.
You were proposed because recurring {domain} task patterns were detected
that lacked a dedicated specialist.

## Core Responsibilities
{desc_snippet}

## Available Tools
{tool_list}

## Operating Principles
- Always ground recommendations in evidence from the knowledge base.
- Cite specific sources when making claims.
- Flag uncertainty explicitly rather than guessing.
- Produce structured, actionable outputs.
- Escalate to the appropriate department when a task exceeds your scope.

## Output Format
Produce structured outputs with:
1. Summary of findings
2. Evidence references
3. Recommended actions
4. Confidence assessment
5. Open questions or risks"""

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_blueprint(self, blueprint: AgentBlueprint) -> dict[str, Any]:
        """Validate a proposed agent blueprint.

        Checks:
        - Name does not conflict with existing agents
        - Routing keywords do not excessively overlap with existing agents
        - System prompt follows established patterns
        Returns a dict with: valid (bool), issues (list), warnings (list).
        """
        issues: list[str] = []
        warnings: list[str] = []

        existing = self._load_existing_agents()
        existing_kw = self._load_existing_keywords()

        # 1. Name conflict check
        slug = _slugify(blueprint.name)
        if slug in existing or blueprint.name.lower() in {
            n.lower() for n in existing
        }:
            issues.append(
                f"Name conflict: agent '{blueprint.name}' already exists."
            )

        # 2. Routing keyword overlap check
        blueprint_kw = set(kw.lower() for kw in blueprint.routing_keywords)
        overlap = blueprint_kw & existing_kw
        overlap_ratio = len(overlap) / max(len(blueprint_kw), 1)
        if overlap_ratio > 0.8:
            issues.append(
                f"Excessive keyword overlap ({overlap_ratio:.0%}): "
                f"keywords {sorted(overlap)} already covered by existing agents."
            )
        elif overlap_ratio > 0.5:
            warnings.append(
                f"Moderate keyword overlap ({overlap_ratio:.0%}): "
                f"keywords {sorted(overlap)} shared with existing agents."
            )

        # 3. System prompt structure check
        prompt = blueprint.system_prompt
        expected_sections = ["Identity", "Responsibilities", "Tools", "Principles"]
        missing_sections = [
            s for s in expected_sections
            if s.lower() not in prompt.lower()
        ]
        if missing_sections:
            warnings.append(
                f"System prompt missing recommended sections: {missing_sections}"
            )

        # 4. Minimum prompt length
        if len(prompt) < 100:
            issues.append("System prompt is too short (< 100 characters).")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "blueprint_id": blueprint.id,
        }

    # ------------------------------------------------------------------
    # File generation
    # ------------------------------------------------------------------

    def generate_agent_file(self, blueprint: AgentBlueprint) -> str:
        """Generate the .md file content in the standard agent format.

        Format:
        ---
        name: <name>
        model: <model>
        description: <description>
        ---
        <system_prompt>
        """
        model_map = {
            "opus": "claude-opus-4-6",
            "sonnet": "claude-sonnet-4-6",
            "haiku": "claude-haiku-4-5",
        }
        model_str = model_map.get(blueprint.model, "claude-sonnet-4-6")

        frontmatter = yaml.dump(
            {
                "name": blueprint.name,
                "model": model_str,
                "description": blueprint.description,
            },
            default_flow_style=False,
            sort_keys=False,
        ).strip()

        return f"---\n{frontmatter}\n---\n\n{blueprint.system_prompt}\n"

    # ------------------------------------------------------------------
    # Full pipeline
    # ------------------------------------------------------------------

    def propose_agents(self, runs_dir: Path) -> list[AgentBlueprint]:
        """Full pipeline: analyze task patterns, design agents, validate, return proposals."""
        patterns = self.analyze_task_patterns(runs_dir)
        proposals: list[AgentBlueprint] = []

        for pattern in patterns:
            blueprint = self.design_agent(pattern)
            validation = self.validate_blueprint(blueprint)

            # Include validation results in the blueprint
            blueprint.test_results = validation

            # Only include blueprints without blocking issues
            if validation["valid"]:
                proposals.append(blueprint)

        return proposals
