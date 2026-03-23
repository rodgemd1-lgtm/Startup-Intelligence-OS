"""A/B Testing for Jake prompts — compare prompt variants and track which performs better.

Stores experiment definitions and results in Supabase (jake_ab_experiments).
Uses Bayesian success rates to determine winning variants.
"""
from __future__ import annotations

import hashlib
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class PromptVariant:
    name: str           # "control", "variant_a", "variant_b"
    template: str       # The prompt template with {placeholders}
    weight: float = 1.0 # Selection weight (higher = more likely to be selected)


@dataclass
class ExperimentResult:
    experiment_id: str
    variant_name: str
    success: bool
    quality_score: float   # 0-1 human/automated rating
    latency_ms: int
    token_count: int
    cost_usd: float
    notes: str = ""


class ABTestEngine:
    """Manage prompt A/B experiments and track results."""

    # In-memory experiments storage (no Supabase table required)
    _experiments: dict[str, dict] = {}
    _results: dict[str, list[dict]] = {}

    def register(self, experiment_name: str, variants: list[PromptVariant]) -> str:
        """Register an A/B experiment. Returns experiment_id."""
        exp_id = hashlib.md5(experiment_name.encode()).hexdigest()[:8]
        self._experiments[exp_id] = {
            "id": exp_id,
            "name": experiment_name,
            "variants": {v.name: {"template": v.template, "weight": v.weight} for v in variants},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "active": True,
        }
        if exp_id not in self._results:
            self._results[exp_id] = []
        return exp_id

    def select_variant(self, experiment_id: str) -> tuple[str, str]:
        """Select a variant using weighted random selection. Returns (variant_name, template)."""
        import random
        exp = self._experiments.get(experiment_id)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found")

        variants = exp["variants"]
        names = list(variants.keys())
        weights = [variants[n]["weight"] for n in names]

        # Use performance-weighted selection after 10+ results
        results = self._results.get(experiment_id, [])
        if len(results) >= 10:
            for i, name in enumerate(names):
                wins = sum(1 for r in results if r["variant"] == name and r["success"])
                total = sum(1 for r in results if r["variant"] == name) or 1
                weights[i] = (wins / total) * 2 + 0.1  # UCB-style boost

        chosen = random.choices(names, weights=weights, k=1)[0]
        return chosen, variants[chosen]["template"]

    def record_result(self, result: ExperimentResult) -> None:
        """Record an experiment result."""
        if result.experiment_id not in self._results:
            self._results[result.experiment_id] = []
        self._results[result.experiment_id].append({
            "variant": result.variant_name,
            "success": result.success,
            "quality": result.quality_score,
            "latency_ms": result.latency_ms,
            "cost_usd": result.cost_usd,
            "token_count": result.token_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def analyze(self, experiment_id: str) -> dict:
        """Analyze experiment results and determine the winner."""
        results = self._results.get(experiment_id, [])
        exp = self._experiments.get(experiment_id, {})
        if not results:
            return {"experiment_id": experiment_id, "status": "insufficient_data", "winner": None}

        by_variant: dict[str, dict] = {}
        for r in results:
            v = r["variant"]
            if v not in by_variant:
                by_variant[v] = {"successes": 0, "total": 0, "quality_sum": 0, "cost_sum": 0}
            by_variant[v]["total"] += 1
            if r["success"]:
                by_variant[v]["successes"] += 1
            by_variant[v]["quality_sum"] += r.get("quality", 0)
            by_variant[v]["cost_sum"] += r.get("cost_usd", 0)

        stats = {}
        for v, data in by_variant.items():
            total = data["total"] or 1
            stats[v] = {
                "success_rate": round(data["successes"] / total, 3),
                "avg_quality": round(data["quality_sum"] / total, 3),
                "avg_cost": round(data["cost_sum"] / total, 6),
                "sample_size": data["total"],
            }

        winner = max(stats.items(), key=lambda x: x[1]["success_rate"] * 0.6 + x[1]["avg_quality"] * 0.4)

        return {
            "experiment_id": experiment_id,
            "experiment_name": exp.get("name", ""),
            "total_samples": len(results),
            "stats": stats,
            "winner": winner[0],
            "winner_stats": winner[1],
            "status": "ready" if len(results) >= 30 else "collecting",
        }

    def report(self) -> str:
        """Plain-text report of all active experiments."""
        if not self._experiments:
            return "No A/B experiments registered."
        lines = ["═══ A/B TESTING REPORT ═══", ""]
        for exp_id, exp in self._experiments.items():
            analysis = self.analyze(exp_id)
            lines.append(f"  {exp['name']} (id={exp_id})")
            lines.append(f"    Status: {analysis['status']}, Samples: {analysis.get('total_samples', 0)}")
            if analysis.get("winner"):
                lines.append(f"    Winner: {analysis['winner']} ({analysis['winner_stats']['success_rate']*100:.0f}% success rate)")
            lines.append("")
        return "\n".join(lines)


ab_engine = ABTestEngine()


# ─── Pre-registered experiments for Jake's core prompts ───────────────────────

def register_default_experiments() -> None:
    """Register Jake's standard prompt A/B experiments."""
    ab_engine.register("daily_brief_format", [
        PromptVariant("control", "Generate a structured daily brief for Mike with sections: Focus, Alerts, Decisions, Jake's Take.", weight=1.0),
        PromptVariant("concise", "Generate a concise daily brief for Mike. Lead with the ONE most important thing, then 2-3 bullets. Max 150 words.", weight=1.0),
        PromptVariant("jake_voice", "Yo Mike — here's your daily rundown. Lead with what needs immediate attention, then what's cooking. Keep it real, under 200 words, Jake-style.", weight=1.0),
    ])

    ab_engine.register("meeting_brief_format", [
        PromptVariant("structured", "Generate a formal meeting brief with Purpose, Context, Talking Points, and Risks.", weight=1.0),
        PromptVariant("minimal", "3-bullet pre-meeting brief: What matters, What to watch, Jake's recommendation.", weight=1.0),
    ])

    ab_engine.register("research_synthesis", [
        PromptVariant("academic", "Synthesize research findings with executive summary, key findings, confidence levels, and recommendations.", weight=1.0),
        PromptVariant("operational", "What did we learn? What do we know for sure? What do we still need? What's the move?", weight=1.0),
    ])
