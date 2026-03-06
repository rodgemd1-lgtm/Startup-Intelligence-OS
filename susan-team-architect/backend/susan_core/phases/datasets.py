"""Phase 4: Dataset Requirements — enumerate data needs per agent."""
from __future__ import annotations
import json
from anthropic import Anthropic
from susan_core.config import config


async def run(company: str, context: dict) -> dict:
    """Plan dataset requirements for the team."""
    client = Anthropic(api_key=config.anthropic_api_key)

    prompt = f"""You are Susan, the Team Architect. Plan the data requirements for this agent team.

Company Profile:
{json.dumps(context.get('profile', {}), indent=2)}

Team Manifest:
{json.dumps(context.get('team', {}), indent=2, default=str)}

Return a JSON object (DatasetManifest) with:
- datasets (array): Each dataset has:
  - name (string): Dataset name
  - type (string): "structured" | "vector" | "api" | "filesystem"
  - status (string): "exists" | "needs_building" | "needs_acquisition"
  - source (string): Where data comes from
  - format (string): Data format
  - size_estimate (string): Approximate size
  - priority (string): "P0" | "P1" | "P2"
  - cost (string): Estimated cost or "free"
  - assigned_to (array of strings): Agent IDs that need this data
- external_apis (array of objects): APIs needed with name, purpose, cost
- total_estimated_cost (string): Total data acquisition cost

Consider: behavioral economics data, exercise science databases, market research, user research templates, legal compliance docs, financial benchmarks, security standards.
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
