"""Smart Model Router — route tasks to the cheapest capable model.

Tiers: HAIKU (fast/cheap) → SONNET (balanced) → OPUS (deep reasoning).
Cost savings: use Haiku for classification/simple ops, Opus only for max-effort decisions.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ModelTier(str, Enum):
    HAIKU = "haiku"       # claude-haiku-4-5-20251001 — cheapest, fastest
    SONNET = "sonnet"     # claude-sonnet-4-6 — balanced (default)
    OPUS = "opus"         # claude-opus-4-6 — deepest reasoning, most expensive


# Current pricing per 1M tokens (USD, approximate as of 2025)
_MODEL_PRICING: dict[ModelTier, dict] = {
    ModelTier.HAIKU: {
        "model_id": "claude-haiku-4-5-20251001",
        "input_per_1m": 0.80,
        "output_per_1m": 4.00,
        "max_tokens": 8192,
        "description": "Fast classification, simple Q&A, formatting",
    },
    ModelTier.SONNET: {
        "model_id": "claude-sonnet-4-6",
        "input_per_1m": 3.00,
        "output_per_1m": 15.00,
        "max_tokens": 64000,
        "description": "Standard tasks, coding, analysis",
    },
    ModelTier.OPUS: {
        "model_id": "claude-opus-4-6",
        "input_per_1m": 15.00,
        "output_per_1m": 75.00,
        "max_tokens": 32000,
        "description": "Deep reasoning, security audits, irreversible decisions",
    },
}

# Task type → recommended tier
_TASK_ROUTING: dict[str, ModelTier] = {
    # Haiku tasks
    "classify": ModelTier.HAIKU,
    "categorize": ModelTier.HAIKU,
    "extract_fields": ModelTier.HAIKU,
    "format": ModelTier.HAIKU,
    "summarize_short": ModelTier.HAIKU,
    "triage": ModelTier.HAIKU,
    "tag": ModelTier.HAIKU,
    "embed_prep": ModelTier.HAIKU,

    # Sonnet tasks (default)
    "research": ModelTier.SONNET,
    "content_draft": ModelTier.SONNET,
    "code_review": ModelTier.SONNET,
    "analysis": ModelTier.SONNET,
    "pipeline": ModelTier.SONNET,
    "brief": ModelTier.SONNET,
    "email_triage": ModelTier.SONNET,
    "intel_summary": ModelTier.SONNET,
    "meeting_prep": ModelTier.SONNET,
    "employee_run": ModelTier.SONNET,

    # Opus tasks
    "architecture": ModelTier.OPUS,
    "security_audit": ModelTier.OPUS,
    "strategy": ModelTier.OPUS,
    "irreversible_decision": ModelTier.OPUS,
    "system_design": ModelTier.OPUS,
}


@dataclass
class RoutingDecision:
    task_type: str
    tier: ModelTier
    model_id: str
    rationale: str
    estimated_cost_per_1k_tokens: float

    def to_dict(self) -> dict:
        return {
            "task_type": self.task_type,
            "tier": self.tier.value,
            "model_id": self.model_id,
            "rationale": self.rationale,
            "estimated_cost_per_1k_tokens": round(self.estimated_cost_per_1k_tokens, 6),
        }


class ModelRouter:
    """Route tasks to the appropriate Claude model tier."""

    def __init__(self, default_tier: ModelTier = ModelTier.SONNET):
        self.default_tier = default_tier

    def route(self, task_type: str, complexity: str = "medium", force_tier: ModelTier | None = None) -> RoutingDecision:
        """Return routing decision for a task type.

        complexity: "low", "medium", "high" — can bump up the tier
        """
        if force_tier:
            tier = force_tier
            rationale = f"Forced tier override: {force_tier.value}"
        else:
            base_tier = _TASK_ROUTING.get(task_type.lower(), self.default_tier)
            # Complexity bump
            if complexity == "high" and base_tier == ModelTier.HAIKU:
                tier = ModelTier.SONNET
                rationale = f"Bumped from haiku→sonnet due to high complexity"
            elif complexity == "high" and base_tier == ModelTier.SONNET:
                tier = ModelTier.OPUS
                rationale = f"Bumped from sonnet→opus due to high complexity"
            else:
                tier = base_tier
                rationale = f"Standard routing for task_type='{task_type}'"

        pricing = _MODEL_PRICING[tier]
        avg_cost = (pricing["input_per_1m"] + pricing["output_per_1m"]) / 2 / 1000

        return RoutingDecision(
            task_type=task_type,
            tier=tier,
            model_id=pricing["model_id"],
            rationale=rationale,
            estimated_cost_per_1k_tokens=avg_cost,
        )

    def cheapest_capable(self, min_tier: ModelTier) -> ModelTier:
        """Return cheapest tier at or above the minimum."""
        tiers = [ModelTier.HAIKU, ModelTier.SONNET, ModelTier.OPUS]
        idx = tiers.index(min_tier)
        return tiers[idx]

    def cost_estimate(self, tier: ModelTier, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost in USD for a specific call."""
        pricing = _MODEL_PRICING[tier]
        input_cost = (input_tokens / 1_000_000) * pricing["input_per_1m"]
        output_cost = (output_tokens / 1_000_000) * pricing["output_per_1m"]
        return round(input_cost + output_cost, 8)

    def savings_report(self, actual_calls: list[dict]) -> dict:
        """Calculate savings from smart routing vs using Opus for everything.

        actual_calls: list of {tier, input_tokens, output_tokens}
        """
        actual_cost = 0.0
        opus_cost = 0.0
        for call in actual_calls:
            tier = ModelTier(call.get("tier", "sonnet"))
            in_tok = call.get("input_tokens", 0)
            out_tok = call.get("output_tokens", 0)
            actual_cost += self.cost_estimate(tier, in_tok, out_tok)
            opus_cost += self.cost_estimate(ModelTier.OPUS, in_tok, out_tok)

        savings = opus_cost - actual_cost
        pct = (savings / opus_cost * 100) if opus_cost > 0 else 0

        return {
            "actual_cost": round(actual_cost, 4),
            "opus_baseline_cost": round(opus_cost, 4),
            "savings_usd": round(savings, 4),
            "savings_pct": round(pct, 1),
            "call_count": len(actual_calls),
        }

    @staticmethod
    def pricing_table() -> str:
        lines = ["MODEL PRICING (per 1M tokens):", ""]
        for tier, info in _MODEL_PRICING.items():
            lines.append(f"  {tier.value.upper()} ({info['model_id']}):")
            lines.append(f"    Input:  ${info['input_per_1m']:.2f}/1M")
            lines.append(f"    Output: ${info['output_per_1m']:.2f}/1M")
            lines.append(f"    Use for: {info['description']}")
            lines.append("")
        return "\n".join(lines)


router = ModelRouter()
