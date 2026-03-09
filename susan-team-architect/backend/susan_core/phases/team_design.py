"""Phase 3: Team Design — design the optimal agent team."""
from __future__ import annotations
import json
import yaml
from susan_core.config import config
from susan_core.phase_runtime import run_cached_json_phase


async def run(company: str, context: dict) -> dict:
    """Design the agent team based on gap analysis."""
    max_agents = 5 if context.get("mode") == "quick" else 8
    registry_path = config.data_dir / "agent_registry.yaml"
    with open(registry_path) as f:
        agents = yaml.safe_load(f)

    prompt = f"""You are Susan, the Team Architect. Design the optimal agent team.

Company Profile:
{json.dumps(context.get('profile', {}), indent=2)}

Capability Diagnosis / Analysis:
{json.dumps(context.get('analysis', {}), indent=2)}

Decision Brief:
{json.dumps(context.get('decision_brief', {}), indent=2)}

Agent Registry:
{json.dumps(agents, indent=2, default=str)}

Return a JSON object (TeamManifest) with:
- project (string): Company name
- designed_by: "susan"
- version: "1.0"
- orchestration_pattern (string): "hierarchical" or "parallel" or "sequential"
- agents (array): Each agent spec has:
  - id (string): snake_case identifier
  - name (string): Display name
  - role (string): Job title
  - goal (string): One-sentence objective for this company
  - backstory (string): Brief persona
  - llm (string): Model ID from registry
  - rag_data_types (array of strings): Knowledge types to query
  - estimated_cost_per_run (string): e.g. "$0.05"
- crews (array): Agent groupings with name, agents (list of IDs), process, trigger
- total_agents (int): Count of agents
- estimated_monthly_cost (string): Total monthly estimate

Select agents based on the diagnosed gaps, evidence needs, and decision brief. Include at most {max_agents} agents and prefer the leanest effective team.
If the company depends on emotional conversion, landing-page persuasion, trust, or brand feeling, include emotional-experience coverage via Mira and strengthened Marcus/Echo/Prism roles.
If the company needs heavy research or document-production capability, include the research and studio agents selectively rather than by default.
Budget constraint: under $200/month total.
Return ONLY the JSON object."""
    return run_cached_json_phase(
        company=company,
        phase="team_design",
        cache_payload={
            "company": company,
            "profile": context.get("profile", {}),
            "analysis": context.get("analysis", {}),
            "agents": agents,
        },
        prompt=prompt,
        model=config.model_sonnet,
        max_tokens=4096,
        refresh=context.get("refresh", False),
    )
