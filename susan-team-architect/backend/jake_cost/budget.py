"""Token Budget Enforcer — per-operation token limits to prevent runaway costs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class TokenBudget:
    name: str
    max_input_tokens: int
    max_output_tokens: int
    max_cost_usd: float
    description: str = ""

    @property
    def total_tokens(self) -> int:
        return self.max_input_tokens + self.max_output_tokens


# Default budgets per operation type
_DEFAULT_BUDGETS: dict[str, TokenBudget] = {
    "classify": TokenBudget("classify", 4_000, 256, 0.005, "Classification tasks"),
    "triage": TokenBudget("triage", 8_000, 512, 0.01, "Email/task triage"),
    "research_query": TokenBudget("research_query", 16_000, 2_000, 0.10, "Research queries"),
    "brief_generation": TokenBudget("brief_generation", 32_000, 4_000, 0.25, "Daily/weekly briefs"),
    "meeting_prep": TokenBudget("meeting_prep", 64_000, 8_000, 0.50, "Meeting preparation"),
    "pipeline_phase": TokenBudget("pipeline_phase", 32_000, 4_000, 0.20, "Pipeline execution phase"),
    "self_improvement": TokenBudget("self_improvement", 100_000, 16_000, 1.00, "TIMG self-improvement"),
    "employee_run": TokenBudget("employee_run", 48_000, 6_000, 0.35, "AI employee execution"),
    "content_draft": TokenBudget("content_draft", 16_000, 4_000, 0.15, "Content creation"),
    "security_audit": TokenBudget("security_audit", 64_000, 16_000, 2.00, "Security analysis"),
    "oracle_intel": TokenBudget("oracle_intel", 32_000, 4_000, 0.25, "Oracle Health intelligence"),
    "default": TokenBudget("default", 32_000, 4_000, 0.20, "Default budget"),
}

# Monthly spend cap (USD)
MONTHLY_BUDGET_USD = 150.0
MONTHLY_WARNING_THRESHOLD = 0.80  # warn at 80% of budget


class BudgetEnforcer:
    """Enforce token and cost budgets per operation."""

    def __init__(self, budgets: dict[str, TokenBudget] | None = None):
        self._budgets = dict(_DEFAULT_BUDGETS)
        if budgets:
            self._budgets.update(budgets)

    def get_budget(self, operation: str) -> TokenBudget:
        return self._budgets.get(operation, self._budgets["default"])

    def check_tokens(self, operation: str, input_tokens: int, output_tokens: int = 0) -> tuple[bool, str]:
        """Return (ok, reason). ok=False if budget exceeded."""
        budget = self.get_budget(operation)
        if input_tokens > budget.max_input_tokens:
            return False, (
                f"Input token budget exceeded for '{operation}': "
                f"{input_tokens:,} > {budget.max_input_tokens:,}"
            )
        if output_tokens > budget.max_output_tokens:
            return False, (
                f"Output token budget exceeded for '{operation}': "
                f"{output_tokens:,} > {budget.max_output_tokens:,}"
            )
        return True, "within budget"

    def check_cost(self, operation: str, estimated_cost: float) -> tuple[bool, str]:
        """Return (ok, reason) based on per-operation cost budget."""
        budget = self.get_budget(operation)
        if estimated_cost > budget.max_cost_usd:
            return False, (
                f"Cost budget exceeded for '{operation}': "
                f"${estimated_cost:.4f} > ${budget.max_cost_usd:.4f}"
            )
        return True, "within budget"

    def check_monthly(self, current_spend: float) -> tuple[bool, str]:
        """Check if monthly budget is approaching or exceeded."""
        if current_spend >= MONTHLY_BUDGET_USD:
            return False, f"Monthly budget EXCEEDED: ${current_spend:.2f} >= ${MONTHLY_BUDGET_USD:.2f}"
        pct = current_spend / MONTHLY_BUDGET_USD
        if pct >= MONTHLY_WARNING_THRESHOLD:
            return True, f"Monthly budget WARNING: ${current_spend:.2f} ({pct*100:.0f}% of ${MONTHLY_BUDGET_USD:.0f})"
        return True, f"Monthly spend: ${current_spend:.2f} ({pct*100:.0f}% of ${MONTHLY_BUDGET_USD:.0f})"

    def budget_summary(self) -> str:
        lines = ["═══ TOKEN BUDGET CONFIGURATION ═══", ""]
        for name, budget in sorted(self._budgets.items()):
            if name == "default":
                continue
            lines.append(
                f"  {name}: {budget.max_input_tokens//1000}K input / "
                f"{budget.max_output_tokens//1000}K output / "
                f"${budget.max_cost_usd:.2f} max"
            )
        lines.append(f"\n  Monthly cap: ${MONTHLY_BUDGET_USD:.0f}/month")
        return "\n".join(lines)


enforcer = BudgetEnforcer()
