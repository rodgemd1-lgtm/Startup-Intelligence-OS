"""Smart Model Router — route tasks to the cheapest capable model.

V1.5 Cost Optimization: Routes through OpenRouter for GLM-5, MiniMax M2.7,
GLM-4.7-Flash. Anthropic direct reserved for Claude Code only.

Provider priority: OpenRouter (GLM-5/MiniMax/Flash) → Anthropic (fallback)
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ModelTier(str, Enum):
    LOCAL = "local"             # Ollama on M5 Max 48GB — $0, offline capable
    FREE_BULK = "free_bulk"     # GLM-4.7-Flash via OpenRouter — FREE
    VOLUME_OPS = "volume_ops"   # MiniMax M2.7 via OpenRouter — cheapest paid
    SMART_OPS = "smart_ops"     # GLM-5 via OpenRouter — research/briefs
    FALLBACK = "fallback"       # GPT-4o via OpenRouter — Jake/OpenClaw fallback
    # Legacy Anthropic tiers (kept for backward compat + Claude Code)
    HAIKU = "haiku"
    SONNET = "sonnet"
    OPUS = "opus"


class Provider(str, Enum):
    OPENROUTER = "openrouter"
    ANTHROPIC = "anthropic"
    LOCAL = "local"  # Ollama on M5 Max — zero cost


# Pricing per 1M tokens (USD)
_MODEL_PRICING: dict[ModelTier, dict] = {
    # === Local tier (M5 Max 48GB — zero cost, offline) ===
    ModelTier.LOCAL: {
        "model_id": "qwen2.5-coder:14b",  # override via OLLAMA_MODEL env var
        "provider": Provider.LOCAL,
        "input_per_1m": 0.00,
        "output_per_1m": 0.00,
        "max_tokens": 8192,
        "context_window": 32768,
        "description": "Ollama local — zero cost, offline (14b on M4 Pro, 32b on M5 Max)",
    },
    # === OpenRouter tiers (primary) ===
    ModelTier.FREE_BULK: {
        "model_id": "z-ai/glm-4.5-air:free",
        "provider": Provider.OPENROUTER,
        "input_per_1m": 0.00,
        "output_per_1m": 0.00,
        "max_tokens": 8192,
        "context_window": 131_072,
        "description": "Classification, extraction, formatting, tagging — FREE",
    },
    ModelTier.VOLUME_OPS: {
        "model_id": "google/gemini-2.0-flash-001",
        "provider": Provider.OPENROUTER,
        "input_per_1m": 0.10,
        "output_per_1m": 0.40,
        "max_tokens": 8192,
        "context_window": 1_048_576,
        "description": "Default for all 73 agents — fast, cheap, 1M context",
    },
    ModelTier.SMART_OPS: {
        "model_id": "deepseek/deepseek-v3.2",
        "provider": Provider.OPENROUTER,
        "input_per_1m": 0.26,
        "output_per_1m": 0.38,
        "max_tokens": 16384,
        "context_window": 163_840,
        "description": "Deep reasoning — strategy, competitive analysis, complex research",
    },
    ModelTier.FALLBACK: {
        "model_id": "openai/gpt-4o",
        "provider": Provider.OPENROUTER,
        "input_per_1m": 2.50,
        "output_per_1m": 10.00,
        "max_tokens": 16384,
        "context_window": 128_000,
        "description": "Escalation only — when T1/T2 quality is provably insufficient",
    },
    # === Anthropic tiers (legacy / Claude Code only) ===
    ModelTier.HAIKU: {
        "model_id": "claude-haiku-4-5-20251001",
        "provider": Provider.ANTHROPIC,
        "input_per_1m": 0.80,
        "output_per_1m": 4.00,
        "max_tokens": 8192,
        "context_window": 200_000,
        "description": "[LEGACY] Fast classification — prefer FREE_BULK instead",
    },
    ModelTier.SONNET: {
        "model_id": "claude-sonnet-4-6",
        "provider": Provider.ANTHROPIC,
        "input_per_1m": 3.00,
        "output_per_1m": 15.00,
        "max_tokens": 64000,
        "context_window": 200_000,
        "description": "[LEGACY] Standard tasks — prefer SMART_OPS instead",
    },
    ModelTier.OPUS: {
        "model_id": "claude-opus-4-6",
        "provider": Provider.ANTHROPIC,
        "input_per_1m": 5.00,
        "output_per_1m": 25.00,
        "max_tokens": 32000,
        "context_window": 200_000,
        "description": "Claude Code dev sessions ONLY — not for agent ops",
    },
}

# Task type → recommended tier (V1.5 optimized)
_TASK_ROUTING: dict[str, ModelTier] = {
    # LOCAL (Ollama on M5 Max) — zero cost, offline capable
    # These tasks run locally when Ollama is available, fall back to FREE_BULK
    "format": ModelTier.LOCAL,
    "embed_prep": ModelTier.LOCAL,
    "background_process": ModelTier.LOCAL,
    "summarize_short": ModelTier.LOCAL,

    # FREE BULK (GLM-4.7-Flash) — zero cost
    "classify": ModelTier.FREE_BULK,
    "categorize": ModelTier.FREE_BULK,
    "extract_fields": ModelTier.FREE_BULK,
    "tag": ModelTier.FREE_BULK,

    # VOLUME OPS (MiniMax M2.7) — $0.30/$1.20 per MTok
    "triage": ModelTier.VOLUME_OPS,
    "email_triage": ModelTier.VOLUME_OPS,
    "rag_query": ModelTier.VOLUME_OPS,
    "summarize": ModelTier.VOLUME_OPS,
    "content_draft": ModelTier.VOLUME_OPS,
    "content_generation": ModelTier.VOLUME_OPS,
    "employee_run": ModelTier.VOLUME_OPS,
    "susan_agent_ops": ModelTier.VOLUME_OPS,
    "bulk_agent_tasks": ModelTier.VOLUME_OPS,
    "pipeline": ModelTier.VOLUME_OPS,

    # SMART OPS (GLM-5) — $1.00/$3.20 per MTok
    "research": ModelTier.SMART_OPS,
    "brief": ModelTier.SMART_OPS,
    "meeting_prep": ModelTier.SMART_OPS,
    "intel_summary": ModelTier.SMART_OPS,
    "competitive_analysis": ModelTier.SMART_OPS,
    "code_review": ModelTier.SMART_OPS,
    "analysis": ModelTier.SMART_OPS,
    "strategy": ModelTier.SMART_OPS,

    # FALLBACK (GPT-4o) — only when GLM-5/MiniMax quality is insufficient
    "jake_fallback": ModelTier.FALLBACK,
    "openclaw_fallback": ModelTier.FALLBACK,

    # ANTHROPIC (Claude Code sessions only — not used by agent runtime)
    "architecture": ModelTier.OPUS,
    "security_audit": ModelTier.OPUS,
    "irreversible_decision": ModelTier.OPUS,
    "system_design": ModelTier.OPUS,
}

# Map legacy tier names to new tiers for backward compatibility
_LEGACY_TIER_MAP: dict[ModelTier, ModelTier] = {
    ModelTier.HAIKU: ModelTier.FREE_BULK,
    ModelTier.SONNET: ModelTier.SMART_OPS,
    # OPUS stays as OPUS — only used in Claude Code
}

# Fallback chain: LOCAL → FREE_BULK (when Ollama is not running)
_LOCAL_FALLBACK = ModelTier.FREE_BULK


@dataclass
class RoutingDecision:
    task_type: str
    tier: ModelTier
    model_id: str
    provider: Provider
    rationale: str
    estimated_cost_per_1k_tokens: float

    def to_dict(self) -> dict:
        return {
            "task_type": self.task_type,
            "tier": self.tier.value,
            "model_id": self.model_id,
            "provider": self.provider.value,
            "rationale": self.rationale,
            "estimated_cost_per_1k_tokens": round(self.estimated_cost_per_1k_tokens, 6),
        }


class ModelRouter:
    """Route tasks to the cheapest capable model across providers."""

    def __init__(self, default_tier: ModelTier = ModelTier.VOLUME_OPS,
                 force_anthropic: bool = False):
        """
        default_tier: tier used when task_type isn't in the routing table.
        force_anthropic: if True, use legacy Anthropic tiers (for backward compat).
        """
        self.default_tier = default_tier
        self.force_anthropic = force_anthropic

    def route(self, task_type: str, complexity: str = "medium",
              force_tier: ModelTier | None = None) -> RoutingDecision:
        """Return routing decision for a task type."""
        if force_tier:
            tier = force_tier
            rationale = f"Forced tier override: {force_tier.value}"
        else:
            base_tier = _TASK_ROUTING.get(task_type.lower(), self.default_tier)

            # If force_anthropic, map OpenRouter tiers back to Anthropic
            if self.force_anthropic and base_tier in (
                ModelTier.FREE_BULK, ModelTier.VOLUME_OPS,
                ModelTier.SMART_OPS, ModelTier.FALLBACK,
            ):
                base_tier = ModelTier.SONNET

            # Complexity bump
            openrouter_tiers = [ModelTier.FREE_BULK, ModelTier.VOLUME_OPS,
                                ModelTier.SMART_OPS, ModelTier.FALLBACK]
            if complexity == "high":
                if base_tier == ModelTier.FREE_BULK:
                    tier = ModelTier.VOLUME_OPS
                    rationale = "Bumped from free_bulk→volume_ops due to high complexity"
                elif base_tier == ModelTier.VOLUME_OPS:
                    tier = ModelTier.SMART_OPS
                    rationale = "Bumped from volume_ops→smart_ops due to high complexity"
                elif base_tier == ModelTier.SMART_OPS:
                    tier = ModelTier.FALLBACK
                    rationale = "Bumped from smart_ops→fallback due to high complexity"
                elif base_tier == ModelTier.HAIKU:
                    tier = ModelTier.SONNET
                    rationale = "Bumped from haiku→sonnet due to high complexity"
                elif base_tier == ModelTier.SONNET:
                    tier = ModelTier.OPUS
                    rationale = "Bumped from sonnet→opus due to high complexity"
                else:
                    tier = base_tier
                    rationale = f"Standard routing for task_type='{task_type}'"
            else:
                tier = base_tier
                rationale = f"Standard routing for task_type='{task_type}'"

        pricing = _MODEL_PRICING[tier]
        avg_cost = (pricing["input_per_1m"] + pricing["output_per_1m"]) / 2 / 1000

        return RoutingDecision(
            task_type=task_type,
            tier=tier,
            model_id=pricing["model_id"],
            provider=Provider(pricing["provider"]),
            rationale=rationale,
            estimated_cost_per_1k_tokens=avg_cost,
        )

    def get_model_info(self, tier: ModelTier) -> dict:
        """Return pricing and config for a model tier."""
        return _MODEL_PRICING[tier]

    def cost_estimate(self, tier: ModelTier, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost in USD for a specific call."""
        pricing = _MODEL_PRICING[tier]
        input_cost = (input_tokens / 1_000_000) * pricing["input_per_1m"]
        output_cost = (output_tokens / 1_000_000) * pricing["output_per_1m"]
        return round(input_cost + output_cost, 8)

    def savings_report(self, actual_calls: list[dict]) -> dict:
        """Calculate savings from smart routing vs using Sonnet for everything."""
        actual_cost = 0.0
        sonnet_cost = 0.0
        for call in actual_calls:
            tier = ModelTier(call.get("tier", "volume_ops"))
            in_tok = call.get("input_tokens", 0)
            out_tok = call.get("output_tokens", 0)
            actual_cost += self.cost_estimate(tier, in_tok, out_tok)
            sonnet_cost += self.cost_estimate(ModelTier.SONNET, in_tok, out_tok)

        savings = sonnet_cost - actual_cost
        pct = (savings / sonnet_cost * 100) if sonnet_cost > 0 else 0

        return {
            "actual_cost": round(actual_cost, 4),
            "sonnet_baseline_cost": round(sonnet_cost, 4),
            "savings_usd": round(savings, 4),
            "savings_pct": round(pct, 1),
            "call_count": len(actual_calls),
        }

    @staticmethod
    def pricing_table() -> str:
        lines = ["MODEL PRICING (per 1M tokens):", ""]
        for tier, info in _MODEL_PRICING.items():
            provider_tag = f"[{info['provider'].value}]"
            lines.append(f"  {tier.value.upper()} ({info['model_id']}) {provider_tag}:")
            lines.append(f"    Input:  ${info['input_per_1m']:.2f}/1M")
            lines.append(f"    Output: ${info['output_per_1m']:.2f}/1M")
            lines.append(f"    Use for: {info['description']}")
            lines.append("")
        return "\n".join(lines)


# Default router — routes to OpenRouter models
router = ModelRouter()

# Legacy router — forces Anthropic models (for backward compat during transition)
anthropic_router = ModelRouter(default_tier=ModelTier.SONNET, force_anthropic=True)
