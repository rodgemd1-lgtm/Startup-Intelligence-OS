"""Predictive Capability Modeling — V8 Cross-Domain Intelligence

Forecasts when capabilities will reach target maturity based on
historical progression rates. Uses linear projection from self-evaluation
scores over time.

Also predicts which capabilities should be built next based on
dependency graphs and impact scoring.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path


@dataclass
class MaturityForecast:
    """Predicted timeline for a capability to reach target maturity."""
    domain: str
    current_score: float
    target_score: float
    projected_date: datetime | None = None
    confidence: float = 0.5
    weekly_improvement_rate: float = 0.0
    bottleneck: str = ""

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "current_score": self.current_score,
            "target_score": self.target_score,
            "projected_date": self.projected_date.isoformat() if self.projected_date else None,
            "confidence": self.confidence,
            "weekly_improvement_rate": self.weekly_improvement_rate,
            "bottleneck": self.bottleneck,
        }


@dataclass
class BuildRecommendation:
    """What to build next, based on impact and dependencies."""
    capability: str
    reason: str
    impact_score: float  # 0-1
    effort: str  # "low", "medium", "high"
    unblocks: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)


class PredictiveModeling:
    """Forecast capability maturity and recommend build sequence."""

    WISDOM_DIR = Path(__file__).parent.parent / "MEMORY" / "WISDOM"

    def __init__(self):
        self._evaluations = self._load_evaluations()

    def forecast_all(self) -> list[MaturityForecast]:
        """Forecast all 9 PAI domains."""
        if len(self._evaluations) < 2:
            # Need at least 2 data points for projection
            return self._baseline_forecast()

        forecasts = []
        latest = self._evaluations[-1]
        previous = self._evaluations[-2]

        for domain_data in latest.get("domains", []):
            domain = domain_data["domain"]
            current = domain_data["score"]
            target = domain_data["target"]

            # Find previous score
            prev_score = current
            for pd in previous.get("domains", []):
                if pd["domain"] == domain:
                    prev_score = pd["score"]
                    break

            # Calculate improvement rate (per month, since evals are monthly)
            rate = current - prev_score
            weekly_rate = rate / 4  # Approximate monthly → weekly

            # Project when target will be reached
            if current >= target:
                projected = None  # Already at target
                confidence = 0.95
            elif weekly_rate > 0:
                weeks_needed = (target - current) / weekly_rate
                projected = datetime.now(timezone.utc) + timedelta(weeks=weeks_needed)
                confidence = min(0.8, 0.3 + weekly_rate * 2)
            else:
                projected = None  # Not improving
                confidence = 0.1

            forecasts.append(MaturityForecast(
                domain=domain,
                current_score=current,
                target_score=target,
                projected_date=projected,
                confidence=round(confidence, 2),
                weekly_improvement_rate=round(weekly_rate, 3),
                bottleneck=domain_data.get("gap", ""),
            ))

        return forecasts

    def recommend_build_sequence(self) -> list[BuildRecommendation]:
        """Recommend what to build next based on impact and dependencies."""
        forecasts = self.forecast_all()

        # Sort by: furthest from target → highest impact to fix
        behind = [f for f in forecasts if f.current_score < f.target_score]
        behind.sort(key=lambda f: f.target_score - f.current_score, reverse=True)

        recommendations = []
        for f in behind[:5]:
            recommendations.append(BuildRecommendation(
                capability=f.domain,
                reason=f"Currently {f.current_score}/10 (target: {f.target_score}). {f.bottleneck}",
                impact_score=round((f.target_score - f.current_score) / 10, 2),
                effort="medium",
                unblocks=[],
                depends_on=[],
            ))

        return recommendations

    def forecast_report(self) -> str:
        """Generate a formatted forecast report."""
        forecasts = self.forecast_all()
        lines = ["# Capability Maturity Forecast", ""]

        for f in forecasts:
            status = "AT TARGET" if f.current_score >= f.target_score else (
                f"→ {f.projected_date.strftime('%b %Y')}" if f.projected_date else "STALLED"
            )
            lines.append(
                f"  {f.domain}: {f.current_score}/10 → {f.target_score}/10 "
                f"[{status}] (rate: {f.weekly_improvement_rate:+.2f}/wk)"
            )

        return "\n".join(lines)

    def _baseline_forecast(self) -> list[MaturityForecast]:
        """Baseline forecast when insufficient data exists."""
        # Use V5 targets as reference
        from pai.learning.self_evaluation import V5_TARGETS
        return [
            MaturityForecast(
                domain=domain,
                current_score=5.0,  # Assumed baseline
                target_score=target,
                confidence=0.2,
                bottleneck="Insufficient historical data for projection",
            )
            for domain, target in V5_TARGETS.items()
        ]

    def _load_evaluations(self) -> list[dict]:
        """Load historical self-evaluation reports."""
        evals = []
        for json_file in sorted(self.WISDOM_DIR.glob("evaluation-*.json")):
            try:
                evals.append(json.loads(json_file.read_text()))
            except (json.JSONDecodeError, OSError):
                continue
        return evals
