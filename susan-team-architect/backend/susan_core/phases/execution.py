"""Phase 5: Execution Plan — generate deployment roadmap."""
from __future__ import annotations
import json
from anthropic import Anthropic
from susan_core.config import config


async def run(company: str, context: dict) -> str:
    """Generate the execution plan as markdown."""
    client = Anthropic(api_key=config.anthropic_api_key)

    prompt = f"""You are Susan, the Team Architect. Generate a phased execution plan.

Company Profile:
{json.dumps(context.get('profile', {}), indent=2)}

Gap Analysis:
{json.dumps(context.get('analysis', {}), indent=2)}

Team Manifest:
{json.dumps(context.get('team', {}), indent=2, default=str)}

Dataset Requirements:
{json.dumps(context.get('datasets', {}), indent=2)}

Generate a detailed execution plan in markdown format with:
1. Phase 1: Foundation (Week 1-2) — Core infrastructure setup
2. Phase 2: Data Population (Week 2-3) — Seed knowledge bases
3. Phase 3: Agent Activation (Week 3-4) — Deploy and test agents
4. Phase 4: Integration (Week 4-5) — Cross-agent workflows
5. Phase 5: Optimization (Week 5-6) — Performance tuning

For each phase include: objectives, tasks, success criteria, risk mitigations.
Include a cost breakdown and timeline.
Output ONLY the markdown, no JSON wrapper."""

    response = client.messages.create(
        model=config.model_sonnet,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text
