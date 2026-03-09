"""Generate TransformFit Monte Carlo adherence and intervention datasets."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import random
from statistics import mean

import yaml


BACKEND_ROOT = Path(__file__).resolve().parents[1]
DOMAIN_ROOT = BACKEND_ROOT / "data" / "domains" / "transformfit_training_intelligence"
PROGRAM_DIR = DOMAIN_ROOT / "programs"
SIMULATION_DIR = DOMAIN_ROOT / "simulations"


@dataclass(frozen=True)
class Archetype:
    id: str
    label: str
    preferred_programs: tuple[str, ...]
    time_pressure: float
    life_stress: float
    recovery_capacity: float
    soreness_sensitivity: float
    confidence: float
    coach_bond: float
    equipment_match: float
    novelty_need: float
    plateau_tolerance: float


ARCHETYPES = (
    Archetype(
        id="beginner_restart",
        label="Beginner or returning lifter",
        preferred_programs=("full-body-foundations-12w", "efficient-hypertrophy-3day-12w"),
        time_pressure=0.42,
        life_stress=0.45,
        recovery_capacity=0.58,
        soreness_sensitivity=0.72,
        confidence=0.48,
        coach_bond=0.32,
        equipment_match=0.82,
        novelty_need=0.35,
        plateau_tolerance=0.36,
    ),
    Archetype(
        id="busy_parent_intermediate",
        label="Busy intermediate with schedule compression",
        preferred_programs=("efficient-hypertrophy-3day-12w", "upper-lower-power-hypertrophy-12w"),
        time_pressure=0.74,
        life_stress=0.70,
        recovery_capacity=0.54,
        soreness_sensitivity=0.50,
        confidence=0.61,
        coach_bond=0.28,
        equipment_match=0.80,
        novelty_need=0.31,
        plateau_tolerance=0.50,
    ),
    Archetype(
        id="ambitious_hypertrophy_user",
        label="Ambitious hypertrophy-focused intermediate",
        preferred_programs=("upper-lower-power-hypertrophy-12w", "scientific-push-pull-legs-12w"),
        time_pressure=0.46,
        life_stress=0.48,
        recovery_capacity=0.66,
        soreness_sensitivity=0.44,
        confidence=0.70,
        coach_bond=0.25,
        equipment_match=0.88,
        novelty_need=0.42,
        plateau_tolerance=0.56,
    ),
    Archetype(
        id="home_gym_time_crunched",
        label="Home gym user with limited equipment and time",
        preferred_programs=("dumbbell-momentum-3day-12w",),
        time_pressure=0.67,
        life_stress=0.53,
        recovery_capacity=0.57,
        soreness_sensitivity=0.52,
        confidence=0.59,
        coach_bond=0.30,
        equipment_match=0.64,
        novelty_need=0.38,
        plateau_tolerance=0.47,
    ),
    Archetype(
        id="confidence_fragile_returner",
        label="Detrained user with high shame risk",
        preferred_programs=("full-body-foundations-12w", "dumbbell-momentum-3day-12w"),
        time_pressure=0.51,
        life_stress=0.62,
        recovery_capacity=0.49,
        soreness_sensitivity=0.68,
        confidence=0.39,
        coach_bond=0.36,
        equipment_match=0.74,
        novelty_need=0.33,
        plateau_tolerance=0.29,
    ),
)

INTERVENTION_EFFECTS = {
    "first_completed_session": 0.04,
    "first_missed_session": 0.10,
    "second_miss_window": 0.14,
    "plateau_two_sessions": 0.10,
    "fatigue_spike": 0.08,
    "reentry_after_gap": 0.12,
    "deload_resistance": 0.07,
}


def _load_programs() -> dict[str, dict]:
    programs: dict[str, dict] = {}
    for path in sorted(PROGRAM_DIR.glob("*.yaml")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        programs[payload["id"]] = payload
    return programs


def _clamp(value: float, lower: float = 0.01, upper: float = 0.95) -> float:
    return max(lower, min(upper, value))


def _phase_deload_weeks(program: dict) -> set[int]:
    deload = program.get("deload", {})
    weeks = deload.get("weeks")
    if isinstance(weeks, list):
        return {int(x) for x in weeks}
    week = deload.get("week")
    if week:
        return {int(week)}
    return set()


def _pick_program(archetype: Archetype, programs: dict[str, dict], rng: random.Random) -> dict:
    program_id = rng.choice(archetype.preferred_programs)
    return programs[program_id]


def _session_risk(
    *,
    program: dict,
    archetype: Archetype,
    week: int,
    session_index: int,
    confidence: float,
    fatigue: float,
    missed_streak: int,
    plateau_streak: int,
    coach_enabled: bool,
    active_interventions: dict[str, int],
    rng: random.Random,
) -> tuple[float, list[str]]:
    frequency_days = int(program.get("frequency_days", 3))
    session_length = float(program.get("session_length_minutes", 60))
    deload_weeks = _phase_deload_weeks(program)

    reasons: list[str] = []
    risk = 0.05
    risk += archetype.time_pressure * 0.16
    risk += archetype.life_stress * 0.14
    risk += max(0.0, fatigue - archetype.recovery_capacity) * 0.20
    risk += max(0.0, archetype.soreness_sensitivity - 0.4) * 0.04 if session_index <= 2 else 0.0

    if session_index == 2:
        risk += 0.06
        reasons.append("session_2_friction")
    if week in (2, 3):
        risk += archetype.time_pressure * 0.05
        reasons.append("week_2_schedule_collision")
    if plateau_streak >= 2:
        risk += 0.08
        reasons.append("plateau_doubt")
    if missed_streak >= 1:
        risk += 0.11
        reasons.append("post_miss_shame_risk")
    if week in deload_weeks:
        risk += archetype.novelty_need * 0.06
        reasons.append("deload_resistance")
    if session_length > 65:
        risk += archetype.time_pressure * 0.04
    if program.get("equipment_profile") == "full_gym" and archetype.equipment_match < 0.72:
        risk += 0.07
        reasons.append("equipment_mismatch")
    if confidence < 0.45:
        risk += 0.05
        reasons.append("confidence_drop")
    if fatigue > 0.75:
        risk += 0.08
        reasons.append("fatigue_spike")

    for intervention_id, ttl in list(active_interventions.items()):
        if ttl <= 0:
            continue
        if coach_enabled:
            risk -= INTERVENTION_EFFECTS.get(intervention_id, 0.0)

    noise = rng.uniform(-0.03, 0.03)
    return _clamp(risk + noise), list(dict.fromkeys(reasons))


def _simulate_user(program: dict, archetype: Archetype, *, coach_enabled: bool, rng: random.Random) -> dict:
    total_sessions = int(program.get("frequency_days", 3)) * int(program.get("duration_weeks", 12))
    confidence = _clamp(archetype.confidence + rng.uniform(-0.08, 0.08))
    coach_bond = _clamp((archetype.coach_bond if coach_enabled else 0.05) + rng.uniform(-0.05, 0.05))
    fatigue = rng.uniform(0.18, 0.35)
    completed = 0
    misses = 0
    plateau_streak = 0
    missed_streak = 0
    recent_misses: list[int] = []
    active_interventions: dict[str, int] = {}
    trigger_counts: dict[str, int] = {}
    failure_reason_counts: dict[str, int] = {}
    dropped = False

    for session_index in range(1, total_sessions + 1):
        week = ((session_index - 1) // int(program.get("frequency_days", 3))) + 1
        risk, reasons = _session_risk(
            program=program,
            archetype=archetype,
            week=week,
            session_index=session_index,
            confidence=confidence,
            fatigue=fatigue,
            missed_streak=missed_streak,
            plateau_streak=plateau_streak,
            coach_enabled=coach_enabled,
            active_interventions=active_interventions,
            rng=rng,
        )

        missed = rng.random() < risk
        if missed:
            misses += 1
            missed_streak += 1
            recent_misses.append(session_index)
            recent_misses = [x for x in recent_misses if session_index - x <= 3]
            for reason in reasons:
                failure_reason_counts[reason] = failure_reason_counts.get(reason, 0) + 1
            confidence = _clamp(confidence - 0.05 - rng.uniform(0.0, 0.03))
            fatigue = _clamp(fatigue + 0.02, 0.0, 1.0)

            if misses == 1:
                trigger_counts["first_missed_session"] = trigger_counts.get("first_missed_session", 0) + 1
                active_interventions["first_missed_session"] = 2
            if len(recent_misses) >= 2:
                trigger_counts["second_miss_window"] = trigger_counts.get("second_miss_window", 0) + 1
                active_interventions["second_miss_window"] = 2
            if week in _phase_deload_weeks(program):
                trigger_counts["deload_resistance"] = trigger_counts.get("deload_resistance", 0) + 1
                active_interventions["deload_resistance"] = 1

            dropout_risk = 0.02 + (0.10 if len(recent_misses) >= 2 else 0.0) + (0.08 if confidence < 0.35 else 0.0)
            if coach_enabled:
                dropout_risk -= coach_bond * 0.06
            if rng.random() < _clamp(dropout_risk, 0.01, 0.50):
                dropped = True
                break
            continue

        completed += 1
        missed_streak = 0
        progress = rng.random() < _clamp(0.55 + confidence * 0.15 - fatigue * 0.12, 0.15, 0.85)
        if progress:
            plateau_streak = 0
            confidence = _clamp(confidence + 0.03 + rng.uniform(0.0, 0.02))
            if completed == 1:
                trigger_counts["first_completed_session"] = trigger_counts.get("first_completed_session", 0) + 1
                active_interventions["first_completed_session"] = 2
            if completed > 1 and rng.random() < 0.25:
                trigger_counts["first_load_jump"] = trigger_counts.get("first_load_jump", 0) + 1
        else:
            plateau_streak += 1
            confidence = _clamp(confidence - 0.02, 0.0, 1.0)
            if plateau_streak >= 2:
                trigger_counts["plateau_two_sessions"] = trigger_counts.get("plateau_two_sessions", 0) + 1
                active_interventions["plateau_two_sessions"] = 2

        if session_index > 1 and recent_misses and session_index - recent_misses[-1] >= 2:
            trigger_counts["reentry_after_gap"] = trigger_counts.get("reentry_after_gap", 0) + 1
            active_interventions["reentry_after_gap"] = 2
            recent_misses.clear()

        fatigue = _clamp(fatigue + 0.05 - (0.04 * archetype.recovery_capacity) - (0.03 if week in _phase_deload_weeks(program) else 0.0), 0.0, 1.0)
        if fatigue > 0.75:
            trigger_counts["fatigue_spike"] = trigger_counts.get("fatigue_spike", 0) + 1
            active_interventions["fatigue_spike"] = 1

        if coach_enabled:
            coach_bond = _clamp(coach_bond + 0.01)

        active_interventions = {key: ttl - 1 for key, ttl in active_interventions.items() if ttl - 1 > 0}

    completion_rate = completed / total_sessions
    return {
        "program_id": program["id"],
        "completed_sessions": completed,
        "total_sessions": total_sessions,
        "completion_rate": round(completion_rate, 4),
        "dropped": dropped,
        "trigger_counts": trigger_counts,
        "failure_reason_counts": failure_reason_counts,
    }


def _aggregate(results: list[dict]) -> dict:
    by_program: dict[str, list[dict]] = {}
    trigger_totals: dict[str, int] = {}
    reason_totals: dict[str, int] = {}
    for result in results:
        by_program.setdefault(result["program_id"], []).append(result)
        for key, value in result["trigger_counts"].items():
            trigger_totals[key] = trigger_totals.get(key, 0) + value
        for key, value in result["failure_reason_counts"].items():
            reason_totals[key] = reason_totals.get(key, 0) + value

    program_summary = []
    for program_id, rows in by_program.items():
        program_summary.append(
            {
                "program_id": program_id,
                "completion_rate": round(mean(row["completion_rate"] for row in rows), 4),
                "dropout_rate": round(sum(1 for row in rows if row["dropped"]) / len(rows), 4),
                "average_sessions_completed": round(mean(row["completed_sessions"] for row in rows), 2),
            }
        )

    return {
        "program_summary": sorted(program_summary, key=lambda row: row["program_id"]),
        "trigger_totals": dict(sorted(trigger_totals.items(), key=lambda item: item[1], reverse=True)),
        "failure_reason_totals": dict(sorted(reason_totals.items(), key=lambda item: item[1], reverse=True)),
        "overall_completion_rate": round(mean(row["completion_rate"] for row in results), 4),
        "overall_dropout_rate": round(sum(1 for row in results if row["dropped"]) / len(results), 4),
    }


def main() -> int:
    rng = random.Random(20260307)
    programs = _load_programs()
    users_per_archetype = 1500
    all_with_coach: list[dict] = []
    all_without_coach: list[dict] = []
    archetype_rows = []

    for archetype in ARCHETYPES:
        with_rows: list[dict] = []
        without_rows: list[dict] = []
        for _ in range(users_per_archetype):
            program = _pick_program(archetype, programs, rng)
            with_rows.append(_simulate_user(program, archetype, coach_enabled=True, rng=rng))
            without_rows.append(_simulate_user(program, archetype, coach_enabled=False, rng=rng))

        with_summary = _aggregate(with_rows)
        without_summary = _aggregate(without_rows)
        all_with_coach.extend(with_rows)
        all_without_coach.extend(without_rows)
        archetype_rows.append(
            {
                "archetype_id": archetype.id,
                "label": archetype.label,
                "completion_rate_with_coach": with_summary["overall_completion_rate"],
                "completion_rate_without_coach": without_summary["overall_completion_rate"],
                "dropout_rate_with_coach": with_summary["overall_dropout_rate"],
                "dropout_rate_without_coach": without_summary["overall_dropout_rate"],
                "completion_lift": round(with_summary["overall_completion_rate"] - without_summary["overall_completion_rate"], 4),
                "dropout_delta": round(without_summary["overall_dropout_rate"] - with_summary["overall_dropout_rate"], 4),
            }
        )

    with_summary = _aggregate(all_with_coach)
    without_summary = _aggregate(all_without_coach)

    risk_windows = []
    for trigger_id, with_count in with_summary["trigger_totals"].items():
        without_count = without_summary["trigger_totals"].get(trigger_id, 0)
        delta = with_count - without_count
        risk_windows.append(
            {
                "trigger_id": trigger_id,
                "occurrences_with_coach": with_count,
                "occurrences_without_coach": without_count,
                "delta_occurrences": delta,
                "recommended_priority": "high" if trigger_id in {"first_missed_session", "second_miss_window", "plateau_two_sessions", "reentry_after_gap"} else "medium",
            }
        )

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "users_per_archetype": users_per_archetype,
        "total_users_per_condition": users_per_archetype * len(ARCHETYPES),
        "with_coach": with_summary,
        "without_coach": without_summary,
        "archetype_summary": archetype_rows,
        "completion_rate_lift": round(with_summary["overall_completion_rate"] - without_summary["overall_completion_rate"], 4),
        "dropout_rate_reduction": round(without_summary["overall_dropout_rate"] - with_summary["overall_dropout_rate"], 4),
        "risk_windows": sorted(risk_windows, key=lambda row: row["occurrences_with_coach"], reverse=True),
        "recommended_top_cues": [
            "first_missed_session",
            "second_miss_window",
            "plateau_two_sessions",
            "reentry_after_gap",
            "fatigue_spike",
        ],
    }

    SIMULATION_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = SIMULATION_DIR / "transformfit_monte_carlo_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    heatmap_path = SIMULATION_DIR / "transformfit_program_heatmap.csv"
    with heatmap_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["condition", "program_id", "completion_rate", "dropout_rate", "average_sessions_completed"])
        writer.writeheader()
        for condition, payload in (("with_coach", with_summary), ("without_coach", without_summary)):
            for row in payload["program_summary"]:
                writer.writerow({"condition": condition, **row})

    risk_path = SIMULATION_DIR / "transformfit_risk_windows.csv"
    with risk_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["trigger_id", "occurrences_with_coach", "occurrences_without_coach", "delta_occurrences", "recommended_priority"])
        writer.writeheader()
        for row in summary["risk_windows"]:
            writer.writerow(row)

    print(json.dumps({"summary": str(summary_path), "heatmap": str(heatmap_path), "risk_windows": str(risk_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
