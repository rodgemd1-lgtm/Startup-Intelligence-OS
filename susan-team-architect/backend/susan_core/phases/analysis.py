"""Composite analysis wrapper for backward compatibility."""
from __future__ import annotations

from susan_core.phases import capability_diagnosis, decision_brief, evidence_gap_map, problem_framing


async def run(company: str, context: dict) -> dict:
    """Return a stable merged analysis payload for older consumers."""
    framing = context.get("problem_framing") or await problem_framing.run(company, context)
    context["problem_framing"] = framing
    diagnosis = context.get("capability_diagnosis") or await capability_diagnosis.run(company, context)
    context["capability_diagnosis"] = diagnosis
    evidence = context.get("evidence_gap_map") or await evidence_gap_map.run(company, context)
    context["evidence_gap_map"] = evidence
    brief = context.get("decision_brief") or await decision_brief.run(company, context)
    context["decision_brief"] = brief
    return {
        "company": company,
        "problem_framing": framing,
        "capability_gaps": diagnosis.get("capability_gaps", []),
        "domain_teams_needed": diagnosis.get("domain_teams_needed", []),
        "recommended_team_size": diagnosis.get("recommended_team_size"),
        "complexity_score": diagnosis.get("complexity_score"),
        "evidence_gap_map": evidence,
        "decision_brief": brief,
    }
