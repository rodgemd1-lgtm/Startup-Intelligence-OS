"""Phase 3: Team Design — design the optimal agent team."""
from __future__ import annotations
import json
import yaml
from pathlib import Path
from anthropic import Anthropic
from susan_core.config import config


async def run(company: str, context: dict) -> dict:
    """Design the agent team based on gap analysis."""
    client = Anthropic(api_key=config.anthropic_api_key)

    registry_path = config.data_dir / "agent_registry.yaml"
    with open(registry_path) as f:
        agents = yaml.safe_load(f)

    prompt = f"""You are Susan, the Team Architect. Design the optimal agent team.

Company Profile:
{json.dumps(context.get('profile', {}), indent=2)}

Gap Analysis:
{json.dumps(context.get('analysis', {}), indent=2)}

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

Select agents based on the gaps identified. Include all agents that map to identified gaps.
Budget constraint: under $200/month total.
Return ONLY the JSON object."""

    response = client.messages.create(
        model=config.model_sonnet,
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text
    start = text.find('{')
    end = text.rfind('}') + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    return {"error": "Failed to parse", "raw": text}
