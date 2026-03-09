"""Phase 6: Behavioral Economics Audit — retention architecture and LAAL design."""
from __future__ import annotations
import json
from susan_core.config import config
from susan_core.phase_runtime import run_cached_json_phase


async def run(company: str, context: dict) -> dict:
    """Run the behavioral economics audit."""
    trigger_limit = 3 if context.get("mode") == "quick" else 5
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
- relational_architecture:
  - love_map_strategy (string): How the product remembers user context without crossing trust boundaries
  - perceived_responsiveness_protocol (string): How the product shows understanding, validation, and care
  - therapeutic_alliance_design (object): goals, tasks, and bond design principles
  - personal_knowledge_map_policy (string): What kinds of personal details are stored and how they are used
  - uncanny_valley_risks (array of strings): The top relational risks to avoid
  - staleness_decay_policy (string): How old details go dormant
  - warm_handoff_protocol (string): How Susan or coach agents should bring in specialists while preserving context
- copy_protocols (object): Keys are trigger types (dormant_d3, dormant_d7, etc.), values are objects with loss_frame and gain_frame versions. Limit to the top {trigger_limit} trigger types.
- agent_be_map (object): Maps agent IDs to their behavioral economics responsibilities
- measurement_plan (object): KPIs and measurement methodology

For fitness apps:
- Industry baseline D1 retention: ~25%
- Industry baseline D7: ~12%
- Industry baseline D30: ~3%
- World-class D30: ~30%

Apply all 12 BE mechanisms: loss aversion, endowment effect, sunk cost, status quo bias, IKEA effect, social proof, commitment/consistency, default effect, anchoring, framing effect, present bias, hyperbolic discounting.

Also incorporate these relational frameworks where relevant: Love Maps, therapeutic alliance, perceived responsiveness, social penetration, relatedness, and relational depth.

Return ONLY the JSON object."""
    return run_cached_json_phase(
        company=company,
        phase="behavioral_economics",
        cache_payload={"company": company, "profile": context.get("profile", {}), "team": context.get("team", {})},
        prompt=prompt,
        model=config.model_sonnet,
        max_tokens=4096,
        refresh=context.get("refresh", False),
    )
