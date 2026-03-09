"""Phase 5: Execution Plan — generate deployment roadmap."""
from __future__ import annotations
import json
from susan_core.config import config
from susan_core.phase_runtime import run_cached_text_phase


async def run(company: str, context: dict) -> str:
    """Generate the execution plan as markdown."""
    quick_mode = context.get("mode") == "quick"
    prompt = f"""You are Susan, the Team Architect. Generate a phased execution plan.

Company Profile:
{json.dumps(context.get('profile', {}), indent=2)}

Gap Analysis:
{json.dumps(context.get('analysis', {}), indent=2)}

Decision Brief:
{json.dumps(context.get('decision_brief', {}), indent=2)}

Team Manifest:
{json.dumps(context.get('team', {}), indent=2, default=str)}

Dataset Requirements:
{json.dumps(context.get('datasets', {}), indent=2)}

Generate a detailed execution plan in markdown format.
If mode is quick, compress the plan into 3 phases: Foundation, Validation, Activation.
If mode is full, use 5 phases: Foundation, Data Population, Agent Activation, Integration, Optimization.

For each phase include: objectives, tasks, success criteria, risk mitigations.
Include a cost breakdown and timeline.
Output ONLY the markdown, no JSON wrapper."""
    return run_cached_text_phase(
        company=company,
        phase="execution",
        cache_payload={
            "company": company,
            "profile": context.get("profile", {}),
            "analysis": context.get("analysis", {}),
            "team": context.get("team", {}),
            "datasets": context.get("datasets", {}),
        },
        prompt=prompt,
        model=config.model_sonnet,
        max_tokens=3072 if quick_mode else 4096,
        refresh=context.get("refresh", False),
    )
