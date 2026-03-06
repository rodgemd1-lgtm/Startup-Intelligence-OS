"""Phase 2: Gap Analysis — map capabilities to agent specialties."""
from __future__ import annotations
import json
import yaml
from pathlib import Path
from anthropic import Anthropic
from susan_core.config import config


async def run(company: str, context: dict) -> dict:
    """Analyze capability gaps and map to agents."""
    client = Anthropic(api_key=config.anthropic_api_key)

    # Load agent registry for available agents
    registry_path = config.data_dir / "agent_registry.yaml"
    with open(registry_path) as f:
        agents = yaml.safe_load(f)

    agent_list = []
    for agent_id, agent_info in agents.get("agents", {}).items():
        agent_list.append(f"- {agent_id}: {agent_info['name']} — {agent_info['role']}")

    prompt = f"""You are Susan, the Team Architect. Analyze this company and identify capability gaps.

Company Profile:
{json.dumps(context.get('profile', {}), indent=2)}

Available agents:
{chr(10).join(agent_list)}

Return a JSON object with:
- company (string): Company name
- capability_gaps (array): Each gap has:
  - area (string): Capability area
  - current_state (string): What exists now
  - ideal_state (string): What should exist
  - complexity (int 1-10): How hard to address
  - agent_needed (string): Agent ID from the list above
  - risks (array of strings): Key risks
  - cross_portfolio_synergy (string or null): Reusable across portfolio
- recommended_team_size (int): How many agents needed
- complexity_score (float): Overall complexity 1-10

Be thorough. Consider all dimensions: product, engineering, science, psychology, growth, legal, finance, security.
Return ONLY the JSON object."""

    response = client.messages.create(
        model=config.model_sonnet,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text
    start = text.find('{')
    end = text.rfind('}') + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    return {"error": "Failed to parse", "raw": text}
