"""Model routing engine -- classify tasks and route to fast/mid/deep lanes."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from susan_core.config import config


class TaskClass(Enum):
    FAST = "fast"      # Simple lookups, greetings, formatting
    MID = "mid"        # Analysis, summaries, moderate reasoning
    DEEP = "deep"      # Multi-step planning, team design, complex synthesis


LANE_DEFAULTS = {
    TaskClass.FAST: config.model_haiku,
    TaskClass.MID: config.model_sonnet,
    TaskClass.DEEP: config.model_sonnet,  # Sonnet is default deep; Opus only on explicit request
}

# Heuristic thresholds for classification
FAST_MAX_TOKENS = 500
MID_MAX_TOKENS = 4000


@dataclass
class RoutingDecision:
    task_class: TaskClass
    model: str
    max_tokens: int
    timeout_seconds: float
    fallback_model: str | None
    downgraded: bool = False
    estimated_cost: float = 0.0


class ModelRouter:
    """Classify tasks and route to appropriate model lane with cost enforcement."""

    def __init__(
        self,
        max_cost_per_call: float = 0.0,    # 0 = unlimited
        max_output_tokens: int = 0,         # 0 = unlimited
    ):
        self._max_cost = max_cost_per_call
        self._max_output = max_output_tokens

    def _classify(self, prompt: str, max_tokens: int) -> TaskClass:
        """Classify a task into fast/mid/deep based on max_tokens thresholds."""
        if max_tokens <= FAST_MAX_TOKENS:
            return TaskClass.FAST
        if max_tokens <= MID_MAX_TOKENS:
            return TaskClass.MID
        return TaskClass.DEEP

    def _estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate the cost of a call based on model pricing."""
        input_cost = input_tokens * config.cost_per_m_input.get(model, 3.0) / 1_000_000
        output_cost = output_tokens * config.cost_per_m_output.get(model, 15.0) / 1_000_000
        return input_cost + output_cost

    def _fallback_chain(self, model: str) -> list[str]:
        """Return the fallback chain for a given model (cheaper models only)."""
        chain = [config.model_opus, config.model_sonnet, config.model_haiku]
        try:
            idx = chain.index(model)
            return chain[idx + 1:]
        except ValueError:
            return [config.model_sonnet, config.model_haiku]

    def route(
        self,
        prompt: str,
        max_tokens: int,
        preferred_model: str | None = None,
        timeout_seconds: float = 30.0,
    ) -> RoutingDecision:
        """Route a task to the appropriate model lane.

        Args:
            prompt: The task prompt text.
            max_tokens: Requested maximum output tokens.
            preferred_model: Optional explicit model override.
            timeout_seconds: Timeout for the call.

        Returns:
            A RoutingDecision with model, token limits, cost estimate, and fallback info.
        """
        task_class = self._classify(prompt, max_tokens)
        model = preferred_model or LANE_DEFAULTS[task_class]
        effective_max = max_tokens
        downgraded = False

        # Apply output token ceiling
        if self._max_output > 0 and effective_max > self._max_output:
            effective_max = self._max_output

        # Estimate cost and enforce ceiling
        est_input = len(prompt) // 4  # rough token estimate
        est_cost = self._estimate_cost(model, est_input, effective_max)

        if self._max_cost > 0 and est_cost > self._max_cost:
            for fallback in self._fallback_chain(model):
                alt_cost = self._estimate_cost(fallback, est_input, effective_max)
                if alt_cost <= self._max_cost:
                    model = fallback
                    est_cost = alt_cost
                    downgraded = True
                    break
            else:
                # Even cheapest exceeds -- use cheapest anyway but flag
                model = config.model_haiku
                est_cost = self._estimate_cost(model, est_input, effective_max)
                downgraded = True

        fallback = self._fallback_chain(model)

        return RoutingDecision(
            task_class=task_class,
            model=model,
            max_tokens=effective_max,
            timeout_seconds=timeout_seconds,
            fallback_model=fallback[0] if fallback else None,
            downgraded=downgraded,
            estimated_cost=est_cost,
        )
