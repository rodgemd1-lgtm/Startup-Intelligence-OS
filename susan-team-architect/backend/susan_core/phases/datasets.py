"""Phase 4: Dataset Requirements — enumerate data needs per agent."""
from __future__ import annotations
import json
from susan_core.config import config
from susan_core.phase_runtime import run_cached_json_phase


async def run(company: str, context: dict) -> dict:
    """Plan dataset requirements for the team."""
    max_datasets = 8 if context.get("mode") == "quick" else 12
    prompt = f"""You are Susan, the Team Architect. Plan the data requirements for this agent team.

Company Profile:
{json.dumps(context.get('profile', {}), indent=2)}

Team Manifest:
{json.dumps(context.get('team', {}), indent=2, default=str)}

Evidence Gap Map:
{json.dumps(context.get('evidence_gap_map', {}), indent=2)}

Return a JSON object (DatasetManifest) with:
- datasets (array, limit {max_datasets}): Each dataset has:
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

Prioritize only the most decision-critical datasets. Prefer datasets that directly answer unresolved evidence gaps or support the selected studio outputs.
Return ONLY the JSON object."""
    return run_cached_json_phase(
        company=company,
        phase="datasets",
        cache_payload={"company": company, "profile": context.get("profile", {}), "team": context.get("team", {})},
        prompt=prompt,
        model=config.model_sonnet,
        max_tokens=3072,
        refresh=context.get("refresh", False),
    )
