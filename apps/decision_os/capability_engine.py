"""Capability lifecycle management for the Decision & Capability OS.

Provides maturity assessment, gap detection, wave planning, and
agent-readiness-index regeneration — all backed by the file store.
"""
from __future__ import annotations

import datetime
import os
from pathlib import Path
from typing import Any

import yaml

from .models import (
    Capability,
    CapabilityMaturity,
    Evidence,
    _now,
)
from .store import Store
from .telemetry import start_run


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_ROOT = Path(os.environ.get(
    "DECISION_OS_ROOT",
    Path(__file__).resolve().parents[2],
))
_STARTUP_OS = _ROOT / ".startup-os"
_AGENTS_DIR = _ROOT / "susan-team-architect" / "agents"
_READINESS_PATH = _STARTUP_OS / "capabilities" / "agent-readiness-index.yaml"

# ---------------------------------------------------------------------------
# Maturity ladder
# ---------------------------------------------------------------------------

_MATURITY_ORDER: list[CapabilityMaturity] = [
    CapabilityMaturity.nascent,
    CapabilityMaturity.emerging,
    CapabilityMaturity.scaling,
    CapabilityMaturity.optimizing,
    CapabilityMaturity.leading,
]

_MATURITY_INDEX: dict[CapabilityMaturity, int] = {
    m: i for i, m in enumerate(_MATURITY_ORDER)
}


def _maturity_numeric(m: CapabilityMaturity) -> float:
    """Convert maturity enum to a 0–1 numeric score."""
    return _MATURITY_INDEX.get(m, 0) / max(len(_MATURITY_ORDER) - 1, 1)


def _maturity_from_score(score: float) -> CapabilityMaturity:
    """Map a 0–1 score back to the nearest maturity level."""
    idx = round(score * (len(_MATURITY_ORDER) - 1))
    idx = max(0, min(idx, len(_MATURITY_ORDER) - 1))
    return _MATURITY_ORDER[idx]


# ---------------------------------------------------------------------------
# CapabilityEngine
# ---------------------------------------------------------------------------

class CapabilityEngine:
    """Capability lifecycle: assess, detect gaps, plan waves, index agents."""

    def __init__(self, store: Store) -> None:
        self._store = store

    # ------------------------------------------------------------------
    # assess_maturity
    # ------------------------------------------------------------------

    def assess_maturity(self, capability_id: str) -> dict:
        """Score a capability's maturity based on evidence and decisions.

        Scoring heuristic:
        - Base score from current maturity enum (0–1)
        - +0.05 per linked evidence (max +0.25)
        - +0.05 per linked decision (max +0.15)
        - +0.10 if owner is set (non-default)
        - -0.10 per gap entry (min floor 0.0)

        Returns a dict with the numeric score, derived maturity level,
        and breakdown.
        """
        cap = self._store.capabilities.get(capability_id)
        if cap is None:
            return {
                "capability_id": capability_id,
                "error": "not_found",
                "score": 0.0,
                "maturity": CapabilityMaturity.nascent.value,
            }

        base = _maturity_numeric(cap.maturity)

        evidence_bonus = min(len(cap.evidence) * 0.05, 0.25)
        decision_bonus = min(len(cap.linked_decisions) * 0.05, 0.15)
        owner_bonus = 0.10 if cap.owner and cap.owner != "mike" else 0.0
        gap_penalty = min(len(cap.gaps) * 0.10, 0.50)

        raw_score = base + evidence_bonus + decision_bonus + owner_bonus - gap_penalty
        score = round(max(0.0, min(1.0, raw_score)), 3)
        derived_maturity = _maturity_from_score(score)

        return {
            "capability_id": capability_id,
            "name": cap.name,
            "current_maturity": cap.maturity.value,
            "score": score,
            "derived_maturity": derived_maturity.value,
            "breakdown": {
                "base": round(base, 3),
                "evidence_bonus": round(evidence_bonus, 3),
                "decision_bonus": round(decision_bonus, 3),
                "owner_bonus": round(owner_bonus, 3),
                "gap_penalty": round(gap_penalty, 3),
            },
            "evidence_count": len(cap.evidence),
            "decision_count": len(cap.linked_decisions),
            "gap_count": len(cap.gaps),
        }

    # ------------------------------------------------------------------
    # detect_gaps
    # ------------------------------------------------------------------

    def detect_gaps(self) -> list[dict]:
        """Scan all capabilities and identify those with gaps.

        Gap conditions (any triggers inclusion):
        - No linked evidence
        - Maturity is nascent
        - Owner is the default ("mike" or empty)
        - Explicit gaps list is non-empty
        - No linked decisions
        """
        capabilities = self._store.capabilities.list_all()
        gap_report: list[dict] = []

        for cap in capabilities:
            reasons: list[str] = []

            if not cap.evidence:
                reasons.append("no_evidence")
            if cap.maturity == CapabilityMaturity.nascent:
                reasons.append("nascent_maturity")
            if not cap.owner or cap.owner == "mike":
                reasons.append("default_or_missing_owner")
            if cap.gaps:
                reasons.append(f"explicit_gaps({len(cap.gaps)})")
            if not cap.linked_decisions:
                reasons.append("no_linked_decisions")

            if reasons:
                assessment = self.assess_maturity(cap.id)
                gap_report.append({
                    "capability_id": cap.id,
                    "name": cap.name,
                    "maturity": cap.maturity.value,
                    "maturity_score": assessment.get("score", 0.0),
                    "gap_reasons": reasons,
                    "explicit_gaps": cap.gaps,
                    "evidence_count": len(cap.evidence),
                    "decision_count": len(cap.linked_decisions),
                })

        # Sort by maturity score ascending — worst gaps first
        gap_report.sort(key=lambda g: g["maturity_score"])
        return gap_report

    # ------------------------------------------------------------------
    # plan_wave
    # ------------------------------------------------------------------

    def plan_wave(self, capability_ids: list[str]) -> dict:
        """Group capabilities into implementation waves.

        Wave assignment heuristic:
        - Wave 1: capabilities with no unresolved dependencies in the set
        - Wave 2: capabilities whose dependencies are all in Wave 1
        - Wave 3+: everything else, bucketed by remaining depth

        Within each wave, capabilities are sorted by maturity score
        (lowest first — build the weakest links first).
        """
        # Load all requested capabilities
        caps: dict[str, Capability] = {}
        for cid in capability_ids:
            cap = self._store.capabilities.get(cid)
            if cap is not None:
                caps[cid] = cap

        if not caps:
            return {"waves": [], "unresolved": capability_ids}

        id_set = set(caps.keys())

        # Build dependency graph (only internal to the requested set)
        deps: dict[str, set[str]] = {}
        for cid, cap in caps.items():
            internal_deps = set(d for d in cap.dependencies if d in id_set)
            deps[cid] = internal_deps

        waves: list[list[dict]] = []
        assigned: set[str] = set()
        remaining = set(id_set)
        max_iterations = len(id_set) + 1  # safety bound

        for _ in range(max_iterations):
            if not remaining:
                break

            # Find capabilities whose deps are all already assigned
            ready = {
                cid for cid in remaining
                if deps[cid].issubset(assigned)
            }

            if not ready:
                # Remaining caps have circular or external deps — dump into final wave
                ready = remaining.copy()

            wave_entries: list[dict] = []
            for cid in sorted(ready):
                assessment = self.assess_maturity(cid)
                wave_entries.append({
                    "capability_id": cid,
                    "name": caps[cid].name,
                    "maturity_score": assessment.get("score", 0.0),
                    "dependencies": sorted(deps[cid]),
                })
            wave_entries.sort(key=lambda e: e["maturity_score"])
            waves.append(wave_entries)

            assigned |= ready
            remaining -= ready

        # Identify capabilities that were requested but not found
        unresolved = [cid for cid in capability_ids if cid not in caps]

        return {
            "wave_count": len(waves),
            "waves": [
                {"wave": i + 1, "capabilities": w}
                for i, w in enumerate(waves)
            ],
            "total_capabilities": len(caps),
            "unresolved": unresolved,
        }

    # ------------------------------------------------------------------
    # regenerate_readiness_index
    # ------------------------------------------------------------------

    def regenerate_readiness_index(self) -> dict:
        """Regenerate ``agent-readiness-index.yaml`` from the local agent surface.

        Scans ``susan-team-architect/agents/*.md`` and writes a fresh
        index to ``.startup-os/capabilities/agent-readiness-index.yaml``.

        Returns the index data dict.
        """
        if not _AGENTS_DIR.is_dir():
            return {
                "error": f"Agent directory not found: {_AGENTS_DIR}",
                "agent_count": 0,
                "agents": [],
            }

        agent_files = sorted(_AGENTS_DIR.glob("*.md"))
        today = datetime.date.today().isoformat()
        now_iso = datetime.datetime.utcnow().isoformat(timespec="microseconds") + "Z"

        agents_list: list[dict[str, str]] = []
        for af in agent_files:
            name = af.stem  # e.g. "aria-growth"
            rel_path = str(af.relative_to(_ROOT))
            agents_list.append({
                "agent": name,
                "path": rel_path,
                "status": "synced",
                "last_synced": today,
                "sync_source": "local_runtime_and_os_docs",
            })

        index_data: dict[str, Any] = {
            "generated_at": now_iso,
            "agent_count": len(agents_list),
            "sync_policy": "all agents consume same Decision OS debrief package each launch",
            "agents": agents_list,
        }

        # Ensure output directory exists
        _READINESS_PATH.parent.mkdir(parents=True, exist_ok=True)
        _READINESS_PATH.write_text(
            yaml.safe_dump(index_data, sort_keys=False, allow_unicode=True)
        )

        return index_data
