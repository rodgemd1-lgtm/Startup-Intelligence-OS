"""Phase 2: Problem Framing."""
from __future__ import annotations

import json

from susan_core.config import config
from susan_core.phase_runtime import run_cached_json_phase


async def run(company: str, context: dict) -> dict:
    prompt = f"""You are Susan. Frame the operating problem before proposing solutions.

Company Profile:
{json.dumps(context.get('profile', {}), indent=2)}

Return ONLY a JSON object with:
- company (string)
- primary_objective (string)
- decision_type (string): one of strategy | research | product | growth | engineering | mixed
- timeline_pressure (string): low | medium | high
- critical_constraints (array of strings)
- success_definition (array of strings)
- value_pools (array of objects with audience, value_type, description)
- core_questions (array of strings, max 6)
- domains_required (array of strings): strategy, research, product, growth, engineering, science, psychology, compliance, studio

Be decisive. Prefer crisp routing inputs over broad prose."""
    return run_cached_json_phase(
        company=company,
        phase="problem_framing",
        cache_payload={"company": company, "profile": context.get("profile", {})},
        prompt=prompt,
        model=config.model_sonnet,
        max_tokens=2048,
        refresh=context.get("refresh", False),
    )
