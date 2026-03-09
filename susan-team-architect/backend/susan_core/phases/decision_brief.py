"""Phase 5: Decision Brief."""
from __future__ import annotations

import json

from susan_core.config import config
from susan_core.phase_runtime import run_cached_json_phase


async def run(company: str, context: dict) -> dict:
    prompt = f"""You are Susan. Produce the routing and decision brief that determines what happens next.

Company Profile:
{json.dumps(context.get('profile', {}), indent=2)}

Problem Framing:
{json.dumps(context.get('problem_framing', {}), indent=2)}

Capability Diagnosis:
{json.dumps(context.get('capability_diagnosis', {}), indent=2)}

Evidence Gap Map:
{json.dumps(context.get('evidence_gap_map', {}), indent=2)}

Return ONLY a JSON object with:
- company (string)
- recommended_path (string)
- options (array of objects with name, tradeoff, when_to_choose)
- prioritized_workstreams (array of strings)
- immediate_agent_team (array of agent IDs)
- research_first (boolean)
- studio_needed (boolean)
- execution_risks (array of strings)
- first_30_day_focus (array of strings)

Optimize for momentum, evidence quality, and practical sequencing."""
    return run_cached_json_phase(
        company=company,
        phase="decision_brief",
        cache_payload={
            "company": company,
            "profile": context.get("profile", {}),
            "problem_framing": context.get("problem_framing", {}),
            "capability_diagnosis": context.get("capability_diagnosis", {}),
            "evidence_gap_map": context.get("evidence_gap_map", {}),
        },
        prompt=prompt,
        model=config.model_sonnet,
        max_tokens=3072,
        refresh=context.get("refresh", False),
    )
