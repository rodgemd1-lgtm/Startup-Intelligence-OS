"""Decision execution pipeline for the Decision & Capability OS.

Implements the full decision lifecycle:
  1. Context assembly
  2. Option generation (rule-based)
  3. Weighted scoring (heuristic)
  4. Debate cycle (5 modes)
  5. Output contract synthesis
  6. Persistence via Store + RunTracer
"""
from __future__ import annotations

from .models import (
    Decision,
    DecisionStatus,
    ScoredOption,
    DebateEntry,
    OutputContract,
    _now,
    _uuid,
)
from .store import Store
from .telemetry import start_run, RunTracer


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEBATE_MODES = [
    "builder_pov",
    "skeptic_pov",
    "contrarian_pov",
    "operator_pov",
    "red_team_challenge",
]

DEFAULT_CRITERIA = ["feasibility", "impact", "risk", "speed"]

DEFAULT_WEIGHTS: dict[str, float] = {
    "feasibility": 0.25,
    "impact": 0.35,
    "risk": 0.20,
    "speed": 0.20,
}


# ---------------------------------------------------------------------------
# Helpers — option generation
# ---------------------------------------------------------------------------

def _generate_options(title: str, context: str) -> list[ScoredOption]:
    """Generate three rule-based options from the decision context."""
    context_summary = context[:120].rstrip(".") if context else title

    go_forward = ScoredOption(
        title=f"Go forward: {title}",
        description=(
            f"Commit to executing the proposed direction. {context_summary}. "
            "Allocate resources now, set a 2-week checkpoint, and drive "
            "toward the first measurable milestone."
        ),
    )

    alternative = ScoredOption(
        title=f"Alternative approach: scoped experiment for {title}",
        description=(
            f"Rather than a full commitment, run a time-boxed experiment. "
            f"{context_summary}. Limit scope to a single cohort or feature "
            "surface, measure leading indicators for 1 week, then decide "
            "whether to scale up, pivot, or stop."
        ),
    )

    do_nothing = ScoredOption(
        title="Do nothing / defer",
        description=(
            "Preserve the status quo and defer this decision. Revisit in "
            "the next planning cycle once more evidence is available. "
            "Accept the opportunity cost of delayed action in exchange for "
            "reduced execution risk and resource preservation."
        ),
    )

    return [go_forward, alternative, do_nothing]


# ---------------------------------------------------------------------------
# Helpers — scoring
# ---------------------------------------------------------------------------

def _score_options(
    options: list[ScoredOption],
    weights: dict[str, float],
) -> list[ScoredOption]:
    """Apply heuristic scores to each option across four criteria.

    Heuristics (deterministic, context-free):
    - feasibility: first option in list scores highest (0.8 descending by 0.15)
    - impact: longer description text scores higher (normalized across set)
    - risk: inverse of list position (first = lowest risk = highest score)
    - speed: "go forward" archetype scores highest; "do nothing" is fast too
    """
    n = len(options)
    if n == 0:
        return options

    # Feasibility — decreasing from first to last
    feasibility_scores = [round(max(0.3, 0.85 - i * 0.20), 2) for i in range(n)]

    # Impact — proportional to description length (longer = more thorough)
    lengths = [len(o.description) for o in options]
    max_len = max(lengths) if max(lengths) > 0 else 1
    impact_scores = [round(0.4 + 0.5 * (l / max_len), 2) for l in lengths]

    # Risk — first option is riskiest venture (lower score = more risky)
    # Invert: "do nothing" is safest, "go forward" is riskiest
    risk_scores = [round(0.3 + (i / max(n - 1, 1)) * 0.55, 2) for i in range(n)]

    # Speed — first option is fastest to value; last is slowest
    speed_scores = [round(max(0.3, 0.80 - i * 0.15), 2) for i in range(n)]

    for i, option in enumerate(options):
        scores = {
            "feasibility": feasibility_scores[i],
            "impact": impact_scores[i],
            "risk": risk_scores[i],
            "speed": speed_scores[i],
        }
        option.scores = scores
        option.total_score = round(
            sum(scores[c] * weights.get(c, 0.25) for c in scores), 3
        )

    return options


# ---------------------------------------------------------------------------
# Helpers — debate
# ---------------------------------------------------------------------------

def _build_debate_argument(mode: str, title: str, context: str,
                           top_option: ScoredOption,
                           options: list[ScoredOption]) -> str:
    """Generate a substantive debate argument for a given mode."""

    ctx_short = context[:200] if context else title
    opt_title = top_option.title
    scores_summary = ", ".join(
        f"{k}={v:.2f}" for k, v in top_option.scores.items()
    ) if top_option.scores else "unscored"

    alt_names = [o.title for o in options if o.id != top_option.id]
    alt_list = "; ".join(alt_names[:2]) if alt_names else "none identified"

    templates: dict[str, str] = {
        "builder_pov": (
            f"This is achievable because the top-ranked option "
            f"({opt_title}) scores well on feasibility and speed "
            f"({scores_summary}). We should move fast on the first "
            f"milestone — the context ({ctx_short}) supports near-term "
            f"execution. Ship a minimal version within two weeks and "
            f"iterate from real signal."
        ),
        "skeptic_pov": (
            f"The main risk is over-committing before validating core "
            f"assumptions. The recommended option ({opt_title}) depends "
            f"on conditions we have not tested: {ctx_short}. We need to "
            f"validate the demand signal and technical feasibility with "
            f"a low-cost proof before allocating meaningful resources. "
            f"Alternatives worth exploring: {alt_list}."
        ),
        "contrarian_pov": (
            f"What if we instead pursued a fundamentally different path? "
            f"The conventional approach ({opt_title}) misses an important "
            f"angle: the context ({ctx_short}) could be reframed as an "
            f"opportunity to leapfrog rather than iterate. Consider "
            f"whether the alternatives ({alt_list}) reveal a higher-"
            f"leverage play that the default framing obscures."
        ),
        "operator_pov": (
            f"Operationally, the bottleneck is execution bandwidth and "
            f"sequencing. To ship '{opt_title}' we need clear ownership, "
            f"a defined interface with existing systems, and staging "
            f"criteria. The context ({ctx_short}) implies dependencies "
            f"that must be resolved before build starts. We need "
            f"resources for integration, testing, and rollback planning."
        ),
        "red_team_challenge": (
            f"This could fail because the top option ({opt_title}) "
            f"assumes conditions that may not hold: {ctx_short}. The "
            f"worst case scenario is sunk cost with no learning — we "
            f"invest two weeks and discover the premise was wrong. "
            f"Failure modes include: scope creep, blocked dependencies, "
            f"measurement gaps, and team context-switching overhead. "
            f"A kill switch and explicit reversal criteria are mandatory."
        ),
    }

    return templates.get(mode, f"[{mode}] No structured argument available for this mode.")


def _run_debate(
    title: str,
    context: str,
    options: list[ScoredOption],
) -> list[DebateEntry]:
    """Execute a full five-mode debate cycle, returning entries."""
    if not options:
        return []

    top = max(options, key=lambda o: o.total_score)
    entries: list[DebateEntry] = []

    confidence_by_mode = {
        "builder_pov": 0.75,
        "skeptic_pov": 0.60,
        "contrarian_pov": 0.45,
        "operator_pov": 0.70,
        "red_team_challenge": 0.55,
    }

    for mode in DEBATE_MODES:
        argument = _build_debate_argument(mode, title, context, top, options)
        entries.append(DebateEntry(
            mode=mode,
            argument=argument,
            confidence=confidence_by_mode.get(mode, 0.5),
        ))

    return entries


# ---------------------------------------------------------------------------
# Helpers — output contract synthesis
# ---------------------------------------------------------------------------

def _synthesize_output(
    title: str,
    context: str,
    options: list[ScoredOption],
    debate: list[DebateEntry],
    risks: list[str],
) -> OutputContract:
    """Produce the decision output contract from scored options and debate."""

    if not options:
        return OutputContract(
            recommendation="No options were generated.",
            counter_recommendation="",
            why_now="Insufficient context to determine urgency.",
            failure_modes=risks or [],
            next_experiment="Gather more context before re-running.",
        )

    ranked = sorted(options, key=lambda o: o.total_score, reverse=True)
    best = ranked[0]
    runner_up = ranked[1] if len(ranked) > 1 else None

    # Recommendation
    recommendation = (
        f"Proceed with '{best.title}' (score: {best.total_score:.3f}). "
        f"{best.description[:200]}"
    )

    # Counter-recommendation
    if runner_up:
        counter_recommendation = (
            f"If constraints block the primary path, fall back to "
            f"'{runner_up.title}' (score: {runner_up.total_score:.3f}). "
            f"{runner_up.description[:150]}"
        )
    else:
        counter_recommendation = "No viable counter-recommendation identified."

    # Why now — derive urgency from debate
    builder_arg = next((d.argument for d in debate if d.mode == "builder_pov"), "")
    why_now = (
        f"Acting now captures the current window described in the context. "
        f"{builder_arg[:120]}"
    )

    # Failure modes — merge explicit risks with red team output
    failure_modes = list(risks) if risks else []
    red_team = next((d.argument for d in debate if d.mode == "red_team_challenge"), "")
    if red_team:
        failure_modes.append(f"Red team: {red_team[:200]}")

    # Next experiment
    skeptic_arg = next((d.argument for d in debate if d.mode == "skeptic_pov"), "")
    next_experiment = (
        f"Run a 1-week scoped validation: {skeptic_arg[:180]}"
        if skeptic_arg
        else "Define a 1-week experiment to test the core assumption."
    )

    return OutputContract(
        recommendation=recommendation,
        counter_recommendation=counter_recommendation,
        why_now=why_now,
        failure_modes=failure_modes,
        next_experiment=next_experiment,
    )


# ---------------------------------------------------------------------------
# DecisionEngine
# ---------------------------------------------------------------------------

class DecisionEngine:
    """Full decision execution pipeline.

    Lifecycle:
        1. Context assembly
        2. Option generation
        3. Weighted scoring
        4. Debate cycle (5 modes)
        5. Output contract synthesis
        6. Persistence
    """

    def __init__(self, store: Store) -> None:
        self._store = store

    # -- public API --

    def run(
        self,
        title: str,
        context: str,
        company: str = "",
        project: str = "",
        assumptions: list[str] | None = None,
        risks: list[str] | None = None,
        criteria_weights: dict[str, float] | None = None,
    ) -> Decision:
        """Execute the full decision pipeline and return a persisted Decision."""

        assumptions = assumptions or []
        risks = risks or []
        weights = {**DEFAULT_WEIGHTS, **(criteria_weights or {})}

        # --- 0. Telemetry ---
        tracer = start_run(
            self._store,
            trigger=f"decision:{title}",
            company=company,
            project=project,
            mode="decision",
        )
        tracer.log("context_assembly", data={
            "title": title,
            "company": company,
            "project": project,
            "assumptions_count": len(assumptions),
            "risks_count": len(risks),
        }, confidence=0.9)

        # --- 1. Create decision ---
        decision = Decision(
            title=title,
            context=context,
            company=company,
            project=project,
            assumptions=assumptions,
            risks=risks,
            run_id=tracer.run.id,
        )
        tracer.log("decision_created", data={"decision_id": decision.id}, confidence=0.95)

        # --- 2. Option generation ---
        options = _generate_options(title, context)
        decision.options = options
        tracer.log("options_generated", data={
            "option_count": len(options),
            "option_titles": [o.title for o in options],
        }, confidence=0.85)

        # --- 3. Weighted scoring ---
        decision.options = _score_options(options, weights)
        ranked = sorted(decision.options, key=lambda o: o.total_score, reverse=True)
        tracer.log("options_scored", data={
            "weights": weights,
            "ranked": [(o.title, o.total_score) for o in ranked],
        }, confidence=0.80)

        # --- 4. Debate cycle ---
        debate_entries = _run_debate(title, context, decision.options)
        decision.debate_log = debate_entries
        tracer.log("debate_completed", data={
            "modes": [d.mode for d in debate_entries],
            "entry_count": len(debate_entries),
        }, confidence=0.70)

        # --- 5. Output contract ---
        output = _synthesize_output(title, context, decision.options, debate_entries, risks)
        decision.output = output
        decision.recommendation = output.recommendation
        decision.status = DecisionStatus.proposed
        tracer.log("output_synthesized", data={
            "recommendation_length": len(output.recommendation),
            "failure_mode_count": len(output.failure_modes),
        }, confidence=0.75)

        # --- 6. Persist ---
        self._store.decisions.save(decision)
        tracer.complete(output)

        return decision

    def debate(self, decision_id: str) -> Decision:
        """Run (or re-run) the debate cycle on an existing decision."""

        decision = self._store.decisions.get(decision_id)
        if decision is None:
            raise ValueError(f"Decision not found: {decision_id}")

        tracer = start_run(
            self._store,
            trigger=f"debate:{decision_id}",
            decision=decision_id,
            company=decision.company,
            project=decision.project,
            mode="debate",
        )

        tracer.log("debate_started", data={
            "decision_id": decision_id,
            "existing_debate_entries": len(decision.debate_log),
            "option_count": len(decision.options),
        }, confidence=0.8)

        debate_entries = _run_debate(decision.title, decision.context, decision.options)
        decision.debate_log = debate_entries

        # Re-synthesize output with fresh debate
        output = _synthesize_output(
            decision.title,
            decision.context,
            decision.options,
            debate_entries,
            decision.risks,
        )
        decision.output = output
        decision.recommendation = output.recommendation

        tracer.log("debate_completed", data={
            "entry_count": len(debate_entries),
        }, confidence=0.70)

        self._store.decisions.save(decision)
        decision.run_id = tracer.run.id
        self._store.decisions.save(decision)
        tracer.complete(output)

        return decision
