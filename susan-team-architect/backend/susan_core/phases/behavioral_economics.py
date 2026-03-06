"""Phase 6: Behavioral Economics Audit — retention architecture and LAAL design."""
from __future__ import annotations
import json
from anthropic import Anthropic
from susan_core.config import config


async def run(company: str, context: dict) -> dict:
    """Run the behavioral economics audit."""
    client = Anthropic(api_key=config.anthropic_api_key)

    prompt = f"""You are Freya, the Behavioral Economics specialist. Conduct a comprehensive BE audit.

Company Profile:
{json.dumps(context.get('profile', {}), indent=2)}

Team Manifest:
{json.dumps(context.get('team', {}), indent=2, default=str)}

Conduct a full behavioral economics audit and return a JSON object (BEAudit) with:

- company (string): Company name
- retention_targets:
  - d1 (float): Day-1 retention target (0-1)
  - d7 (float): Day-7 retention target (0-1)
  - d30 (float): Day-30 retention target (0-1)
  - industry_baseline_d1 (float): Industry average
  - industry_baseline_d7 (float): Industry average
  - industry_baseline_d30 (float): Industry average
- laal_design:
  - ownership_asset (string): What user "owns" in the app
  - cost_of_leaving_progress (string): Progress they'd lose
  - cost_of_leaving_identity (string): Identity disruption
  - cost_of_leaving_social (string): Social connections lost
  - cost_of_leaving_asset (string): Digital asset lost
  - minimum_return_action (string): Lowest friction return (under 2 min)
  - return_reward (string): What they get for returning
  - investment_flywheel (string): How investment compounds
- copy_protocols (object): Keys are trigger types (dormant_d3, dormant_d7, etc.), values are objects with loss_frame and gain_frame versions
- agent_be_map (object): Maps agent IDs to their behavioral economics responsibilities
- measurement_plan (object): KPIs and measurement methodology

For fitness apps:
- Industry baseline D1 retention: ~25%
- Industry baseline D7: ~12%
- Industry baseline D30: ~3%
- World-class D30: ~30%

Apply all 12 BE mechanisms: loss aversion, endowment effect, sunk cost, status quo bias, IKEA effect, social proof, commitment/consistency, default effect, anchoring, framing effect, present bias, hyperbolic discounting.

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
