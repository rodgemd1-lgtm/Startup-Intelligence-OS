"""Phase 3: Capability Diagnosis."""
from __future__ import annotations

import json
import yaml

from susan_core.config import config
from susan_core.phase_runtime import run_cached_json_phase


async def run(company: str, context: dict) -> dict:
    registry_path = config.data_dir / "agent_registry.yaml"
    agents = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    prompt = f"""You are Susan. Diagnose capability gaps and determine which expert resources are actually needed.

Company Profile:
{json.dumps(context.get('profile', {}), indent=2)}

Problem Framing:
{json.dumps(context.get('problem_framing', {}), indent=2)}

Agent Registry:
{json.dumps(agents, indent=2)}

Return ONLY a JSON object with:
- company (string)
- capability_gaps (array, max 8) of objects:
  - area
  - current_state
  - ideal_state
  - severity: P0 | P1 | P2
  - complexity: 1-10
  - recommended_agents (array of agent IDs)
  - risks (array of strings)
- domain_teams_needed (array of strings)
- recommended_team_size (int)
- routing_notes (array of strings)
- complexity_score (float 1-10)

Prefer the leanest effective staffing."""
    return run_cached_json_phase(
        company=company,
        phase="capability_diagnosis",
        cache_payload={
            "company": company,
            "profile": context.get("profile", {}),
            "problem_framing": context.get("problem_framing", {}),
            "agents": agents,
        },
        prompt=prompt,
        model=config.model_sonnet,
        max_tokens=3072 if context.get("mode") == "quick" else 4096,
        refresh=context.get("refresh", False),
    )
