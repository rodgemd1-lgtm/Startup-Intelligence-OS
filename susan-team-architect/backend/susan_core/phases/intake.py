"""Phase 1: Company Intake — extract and standardize the company profile."""
from __future__ import annotations
import json
import yaml
from pathlib import Path
from anthropic import Anthropic
from susan_core.config import config


async def run(company: str, context: dict) -> dict:
    """Load and enrich company profile."""
    # Load from registry
    registry_path = config.data_dir / "company_registry.yaml"
    with open(registry_path) as f:
        registry = yaml.safe_load(f)

    company_data = registry.get("companies", {}).get(company)
    if not company_data:
        raise ValueError(f"Company '{company}' not found in registry")

    # Enrich with Claude
    client = Anthropic(api_key=config.anthropic_api_key)
    prompt = f"""Analyze this company profile and return an enriched, standardized version as JSON.

Company data:
{json.dumps(company_data, indent=2)}

Return a JSON object with these exact fields:
- company (string): Company name
- domain (string): Industry domain
- stage (string): Current stage
- website (string or null)
- founding_date (string or null)
- founders (array of {{name, background}})
- product_description (string): Detailed product description
- tech_stack (array of strings)
- target_market (string): Target market description
- funding_status (string)
- key_competitors (array of strings)
- current_challenges (array of strings)
- constraints (array of strings)

Preserve all existing data. Add detail where possible based on the domain.
Return ONLY the JSON object, no other text."""

    response = client.messages.create(
        model=config.model_sonnet,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text
    start = text.find('{')
    end = text.rfind('}') + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    return company_data
