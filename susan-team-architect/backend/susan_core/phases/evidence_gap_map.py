"""Phase 4: Evidence Gap Map."""
from __future__ import annotations

import json

from susan_core.config import config
from susan_core.phase_runtime import run_cached_json_phase


async def run(company: str, context: dict) -> dict:
    prompt = f"""You are Susan. Determine what evidence is missing before deep execution planning.

Company Profile:
{json.dumps(context.get('profile', {}), indent=2)}

Problem Framing:
{json.dumps(context.get('problem_framing', {}), indent=2)}

Capability Diagnosis:
{json.dumps(context.get('capability_diagnosis', {}), indent=2)}

Return ONLY a JSON object with:
- company (string)
- knowns (array of strings)
- critical_unknowns (array of strings)
- research_tracks (array, max 8) of objects:
  - question
  - source_lane: web | appstore | community | scientific | enterprise_docs | internal_assets
  - freshness_requirement: immediate | current_quarter | durable
  - assigned_agents (array of agent IDs)
  - output_type: evidence_brief | teardown | contradiction_report | screenshot_pack | persona_language_pack
- data_layers_needed (array of strings)
- temporary_assumptions (array of strings)

Bias toward source-grounded research and explicit unknowns."""
    return run_cached_json_phase(
        company=company,
        phase="evidence_gap_map",
        cache_payload={
            "company": company,
            "profile": context.get("profile", {}),
            "problem_framing": context.get("problem_framing", {}),
            "capability_diagnosis": context.get("capability_diagnosis", {}),
        },
        prompt=prompt,
        model=config.model_sonnet,
        max_tokens=3072,
        refresh=context.get("refresh", False),
    )
