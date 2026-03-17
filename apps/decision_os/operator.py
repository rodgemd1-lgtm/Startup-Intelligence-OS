"""Operator routing, graph assembly, and registry helpers."""
from __future__ import annotations

from pathlib import Path
import re

import yaml

from .maturity_surfaces import load_simulated_maturity_state
from .models import (
    ActionPacket,
    Decision,
    DecisionRequirement,
    DepartmentPack,
    DepartmentStep,
    GraphLink,
    GraphNode,
    SignalEvent,
    SignalSeverity,
)
from .store import Store

JOB_STUDIO_COMPANY_ID = "mike-job-studio"
JOB_ROUTING_SKIP_PHRASES = ("job to be done",)
JOB_NONTECHNICAL_TRACKS = {
    "training_factory",
    "ai_strategist_enablement",
    "ellen_enablement",
    "work_memory",
    "writing_intelligence",
    "resume_packets",
    "interview_prep",
    "opportunity_briefs",
}
TECHNICAL_ROUTING_TERMS = (
    "system",
    "architecture",
    "integration",
    "backend",
    "agent",
    "api",
    "pipeline",
    "sync",
    "graph",
    "dashboard",
    "implementation",
)

QUALITATIVE_SCORES = {
    "very_low": 25.0,
    "low": 40.0,
    "medium": 60.0,
    "high": 80.0,
    "very_high": 95.0,
    "fast": 85.0,
    "medium_fast": 70.0,
    "medium_slow": 55.0,
    "slow": 35.0,
}

SEVERITY_RANK = {
    SignalSeverity.critical.value: 0,
    SignalSeverity.warning.value: 1,
    SignalSeverity.info.value: 2,
}

DEPARTMENT_HINTS: dict[str, tuple[str, ...]] = {
    "founder-decision-room": (
        "decision",
        "strategy",
        "prioritize",
        "company",
        "project",
        "roadmap",
        "bet",
        "future-back",
    ),
    "consumer-user-studio": (
        "customer",
        "consumer",
        "user",
        "persona",
        "research",
        "interview",
        "segment",
        "job to be done",
    ),
    "product-experience-studio": (
        "product",
        "roadmap",
        "experience",
        "ux",
        "workflow",
        "feature",
        "prototype",
        "funnel",
    ),
    "marketing-narrative-studio": (
        "launch",
        "message",
        "marketing",
        "campaign",
        "narrative",
        "positioning",
        "brand",
        "go to market",
    ),
    "engineering-agent-systems-studio": (
        "build",
        "system",
        "engineering",
        "architecture",
        "backend",
        "agent",
        "implement",
        "integration",
    ),
    "job-studio": (
        "job studio",
        "training",
        "session",
        "slides",
        "handout",
        "activity",
        "strategist",
        "ellen",
        "gen chat",
        "resume",
        "interview",
    ),
    "data-decision-science-studio": (
        "data",
        "analytics",
        "metrics",
        "forecast",
        "simulation",
        "score",
        "evaluation",
    ),
    "revenue-growth-studio": (
        "revenue",
        "growth",
        "pipeline",
        "funnel",
        "pricing",
        "conversion",
    ),
    "finance-operating-cadence-studio": (
        "finance",
        "budget",
        "kpi",
        "cadence",
        "operating review",
        "variance",
    ),
    "talent-org-design-studio": (
        "team",
        "org",
        "role",
        "hiring",
        "recruiting",
        "onboarding",
    ),
    "trust-governance-studio": (
        "trust",
        "governance",
        "security",
        "privacy",
        "compliance",
        "accessibility",
        "audit",
    ),
}

MATERIALITY_HINTS = (
    "strategy",
    "strategic",
    "architecture",
    "build",
    "launch",
    "operating model",
    "future-back",
    "roadmap",
    "project",
    "decision",
)


def _qualitative_score(value: str, invert: bool = False) -> float:
    base = QUALITATIVE_SCORES.get(str(value or "").lower(), 55.0)
    return round(100.0 - base if invert else base, 1)


def normalize_decision_records(store: Store) -> list[dict]:
    decisions_dir = store.startup_os / "decisions"
    records = store.load_yaml_collection(decisions_dir)
    return [_normalize_decision_record(record) for record in records]


def get_decision_record(store: Store, decision_id: str) -> dict | None:
    for record in normalize_decision_records(store):
        if record["id"] == decision_id:
            return record
    return None


def department_registry(store: Store) -> list[DepartmentPack]:
    return sorted(store.departments.list_all(), key=lambda item: item.name.lower())


def list_action_packets(store: Store) -> list[ActionPacket]:
    packets = store.action_packets.list_all()
    return sorted(
        packets,
        key=lambda packet: (packet.status != "proposed", packet.created_at),
        reverse=True,
    )


def collect_signals(store: Store) -> list[SignalEvent]:
    persisted = store.signals.list_all()
    computed: list[SignalEvent] = []
    ctx = store.context()
    departments = department_registry(store)
    decisions = normalize_decision_records(store)
    capabilities = store.load_yaml_collection(store.startup_os / "capabilities")
    action_packets = list_action_packets(store)
    evidence_count = store.evidence.count()
    simulated_state = load_simulated_maturity_state(store.root)

    if not departments:
        computed.append(
            SignalEvent(
                signal_type="missing_department_registry",
                severity=SignalSeverity.critical,
                title="Department registry is empty",
                description="Wave 1 department packs are missing from .startup-os/departments.",
                source="operator",
                auto_generated=True,
                next_action="Create the Wave 1 department packs before routing asks.",
            )
        )

    if not simulated_state["available"]:
        computed.append(
            SignalEvent(
                signal_type="missing_simulated_maturity_surface",
                severity=SignalSeverity.warning,
                title="Simulated maturity surface is missing",
                description="The dashboard and operator console do not have a current simulated-maturity summary to attach.",
                source="operator",
                auto_generated=True,
                recommended_departments=[
                    "founder-decision-room",
                    "data-decision-science-studio",
                    "job-studio",
                ],
                next_action="Run `bin/refresh_maturity_surfaces.py` to regenerate the simulated-maturity summary and dashboard.",
            )
        )
    elif (simulated_state.get("age_hours") or 0) > 24:
        computed.append(
            SignalEvent(
                signal_type="stale_simulated_maturity_surface",
                severity=SignalSeverity.info,
                title="Simulated maturity surface is stale",
                description=(
                    f"The current simulated-maturity summary is {simulated_state['age_hours']} hours old."
                ),
                source="operator",
                auto_generated=True,
                recommended_departments=["data-decision-science-studio"],
                next_action="Refresh the maturity surfaces so simulated and operational maturity stay aligned.",
            )
        )

    active_decision_id = ctx.get("active_decision", "")
    if active_decision_id and not any(decision["id"] == active_decision_id for decision in decisions):
        computed.append(
            SignalEvent(
                signal_type="missing_active_decision",
                severity=SignalSeverity.warning,
                title="Workspace active decision is unresolved",
                description=(
                    f"`{active_decision_id}` is set in workspace context but no matching "
                    "decision record is available for routing."
                ),
                source="workspace",
                auto_generated=True,
                related_ids={"decision": active_decision_id},
                recommended_departments=["founder-decision-room"],
                next_action="Route a strategic ask through the Founder Decision Room and create a fresh decision packet.",
            )
        )

    if evidence_count < 3:
        computed.append(
            SignalEvent(
                signal_type="thin_evidence_coverage",
                severity=SignalSeverity.warning,
                title="Evidence coverage is thin",
                description="The operator graph has fewer than three evidence records backing current decisions.",
                source="operator",
                auto_generated=True,
                recommended_departments=["consumer-user-studio", "founder-decision-room"],
                next_action="Run a research or customer-intelligence ask to generate stronger evidence coverage.",
            )
        )

    if not action_packets:
        computed.append(
            SignalEvent(
                signal_type="no_action_packets",
                severity=SignalSeverity.info,
                title="No action packets in queue",
                description="The ask-driven routing layer has no queued or proposed action packets yet.",
                source="operator",
                auto_generated=True,
                recommended_departments=["founder-decision-room"],
                next_action="Use the ask composer to generate the first routed action packet.",
            )
        )

    for capability in capabilities:
        wave = capability.get("wave")
        maturity = capability.get("maturity_current")
        if wave == 1 and isinstance(maturity, (int, float)) and maturity < 2.0:
            computed.append(
                SignalEvent(
                    signal_type="wave_one_capability_drift",
                    severity=SignalSeverity.warning,
                    title=f"Wave 1 capability drift: {capability.get('name', capability.get('id', 'unknown'))}",
                    description="This Wave 1 capability remains below the Emerging threshold.",
                    source="capability-summary",
                    auto_generated=True,
                    related_ids={"capability": capability.get("id", "")},
                    next_action="Route an implementation ask that improves this capability's next incomplete checkpoint.",
                )
            )

    merged = persisted + computed
    merged.sort(key=lambda signal: (SEVERITY_RANK.get(signal.severity.value, 9), signal.created_at), reverse=False)
    return merged


def build_graph(store: Store) -> dict:
    ctx = store.context()
    companies = store.load_yaml_collection(store.startup_os / "companies")
    projects = store.load_yaml_collection(store.startup_os / "projects")
    decisions = normalize_decision_records(store)
    capabilities = store.load_yaml_collection(store.startup_os / "capabilities")
    departments = department_registry(store)
    action_packets = list_action_packets(store)
    runs = store.runs.list_all()
    explicit_links = store.graph_links.list_all()

    nodes: dict[str, GraphNode] = {}
    links: dict[str, GraphLink] = {}

    def add_node(node: GraphNode) -> None:
        nodes[node.id] = node

    def add_link(source_id: str, target_id: str, relation: str, metadata: dict | None = None) -> None:
        if not source_id or not target_id:
            return
        link = GraphLink(
            source_id=source_id,
            target_id=target_id,
            relation=relation,
            metadata=metadata or {},
        )
        links[link.id] = link

    workspace_id = ctx.get("name", "workspace")
    add_node(
        GraphNode(
            id=workspace_id,
            type="workspace",
            label=ctx.get("name", "workspace"),
            status="active",
            path=".startup-os/workspace.yaml",
            metadata=ctx,
        )
    )

    for company in companies:
        company_id = company.get("id", company.get("_stem", "company"))
        add_node(
            GraphNode(
                id=company_id,
                type="company",
                label=company.get("name", company_id),
                status=str(company.get("stage", "")),
                path=company.get("_path", ""),
                metadata=company,
            )
        )
        add_link(workspace_id, company_id, "contains_company")
        for linked_project in company.get("linked_projects", []):
            add_link(company_id, linked_project, "owns_project")
        for linked_capability in company.get("linked_capabilities", []):
            add_link(company_id, linked_capability, "depends_on_capability")
        for linked_decision in company.get("linked_decisions", []):
            add_link(company_id, linked_decision, "governed_by_decision")

    for project in projects:
        project_id = project.get("id", project.get("_stem", "project"))
        add_node(
            GraphNode(
                id=project_id,
                type="project",
                label=project.get("name", project_id),
                status=str(project.get("status", "")),
                path=project.get("_path", ""),
                metadata=project,
            )
        )
        add_link(workspace_id, project_id, "contains_project")
        company_id = project.get("company_id") or ctx.get("active_company", "")
        if company_id:
            add_link(company_id, project_id, "owns_project")
        for linked_decision in project.get("linked_decisions", []):
            add_link(project_id, linked_decision, "tracks_decision")
        for linked_capability in project.get("linked_capabilities", []):
            add_link(project_id, linked_capability, "requires_capability")

    for decision in decisions:
        add_node(
            GraphNode(
                id=decision["id"],
                type="decision",
                label=decision["title"],
                status=decision["status"],
                path=decision["path"],
                metadata=decision,
            )
        )
        add_link(workspace_id, decision["id"], "contains_decision")
        if decision["company_id"]:
            add_link(decision["company_id"], decision["id"], "owns_decision")
        if decision["project_id"]:
            add_link(decision["project_id"], decision["id"], "tracks_decision")
        for capability_id in decision["linked_capabilities"]:
            add_link(decision["id"], capability_id, "depends_on_capability")
        for assumption in decision["assumptions"]:
            assumption_id = f"{decision['id']}:assumption:{_slug(assumption)[:24]}"
            add_node(
                GraphNode(
                    id=assumption_id,
                    type="assumption",
                    label=assumption[:80],
                    status="open",
                    metadata={"decision_id": decision["id"]},
                )
            )
            add_link(decision["id"], assumption_id, "tests_assumption")
        for next_action in decision["next_actions"]:
            experiment_id = f"{decision['id']}:experiment:{_slug(next_action)[:24]}"
            add_node(
                GraphNode(
                    id=experiment_id,
                    type="experiment",
                    label=next_action[:80],
                    status="proposed",
                    metadata={"decision_id": decision["id"]},
                )
            )
            add_link(decision["id"], experiment_id, "spawns_experiment")
        for artifact_path in decision["artifacts"]:
            artifact_id = artifact_path
            add_node(
                GraphNode(
                    id=artifact_id,
                    type="artifact",
                    label=Path(artifact_path).name,
                    path=artifact_path,
                    metadata={"source": "decision"},
                )
            )
            add_link(decision["id"], artifact_id, "produces_artifact")

    for capability in capabilities:
        capability_id = capability.get("id", capability.get("_stem", "capability"))
        add_node(
            GraphNode(
                id=capability_id,
                type="capability",
                label=capability.get("name", capability_id),
                status=str(capability.get("maturity_current", capability.get("maturity", ""))),
                path=capability.get("_path", ""),
                metadata=capability,
            )
        )
        add_link(workspace_id, capability_id, "contains_capability")

    for department in departments:
        add_node(
            GraphNode(
                id=department.id,
                type="department",
                label=department.name,
                status=str(department.current_maturity or ""),
                path=f".startup-os/departments/{department.id}.yaml",
                metadata=department.model_dump(mode="json"),
            )
        )
        add_link(workspace_id, department.id, "contains_department")
        for capability_id in department.linked_capabilities:
            add_link(department.id, capability_id, "owns_capability")

    for packet in action_packets:
        add_node(
            GraphNode(
                id=packet.id,
                type="action_packet",
                label=packet.request_text[:72],
                status=packet.status,
                path=f".startup-os/action-packets/{packet.id}.yaml",
                metadata=packet.model_dump(mode="json"),
            )
        )
        add_link(workspace_id, packet.id, "queues_action_packet")
        if packet.linked_decision_id:
            add_link(packet.id, packet.linked_decision_id, "linked_decision")
        for step in packet.department_sequence:
            add_link(packet.id, step.department_id, "routes_to_department", {"role": step.role})
        for artifact_path in packet.artifact_paths:
            add_node(
                GraphNode(
                    id=artifact_path,
                    type="artifact",
                    label=Path(artifact_path).name,
                    path=artifact_path,
                    metadata={"source": packet.id},
                )
            )
            add_link(packet.id, artifact_path, "produces_artifact")

    for run in runs:
        add_node(
            GraphNode(
                id=run.id,
                type="run",
                label=run.trigger or run.id,
                status=run.status.value,
                path=f"apps/decision_os/data/runs/{run.id}.yaml",
                metadata=run.model_dump(mode="json"),
            )
        )
        add_link(workspace_id, run.id, "contains_run")
        if run.decision:
            add_link(run.id, run.decision, "executes_decision")
        if run.project:
            add_link(run.project, run.id, "produces_run")

    for link in explicit_links:
        links[link.id] = link

    active_ids = {
        "company": ctx.get("active_company", ""),
        "project": ctx.get("active_project", ""),
        "decision": ctx.get("active_decision", ""),
    }
    for relation, target_id in active_ids.items():
        if target_id:
            add_link(workspace_id, target_id, f"active_{relation}")

    return {
        "nodes": [node.model_dump(mode="json") for node in nodes.values()],
        "links": [link.model_dump(mode="json") for link in links.values()],
        "summary": {
            "node_count": len(nodes),
            "link_count": len(links),
            "active": active_ids,
        },
    }


def route_request(store: Store, request_text: str) -> dict:
    packs = {pack.id: pack for pack in department_registry(store)}
    if not packs:
        raise ValueError("Department registry is empty.")

    company_context = _resolve_company_context(store, request_text)
    selected_ids = _select_departments(request_text, packs, company_context)
    ordered_ids = _order_departments(selected_ids, packs)
    primary_pack = packs[ordered_ids[0]]
    department_sequence = _build_department_sequence(ordered_ids, packs)
    required_evidence = _unique(
        [
            *company_context.get("required_evidence", []),
            *(
                item
        for pack_id in ordered_ids
        for item in packs[pack_id].required_evidence
            ),
        ]
    )
    required_artifacts = _unique(
        [
            *company_context.get("required_artifacts", []),
            *(
                item
        for pack_id in ordered_ids
        for item in packs[pack_id].required_artifacts
            ),
        ]
    )

    decision_requirement = _decision_requirement_for(
        request_text,
        [packs[pack_id] for pack_id in ordered_ids],
        company_context,
    )
    linked_decision_id = _link_or_create_decision(
        store,
        request_text,
        decision_requirement,
        company_context.get("company_id", ""),
    )

    packet = ActionPacket(
        request_text=request_text,
        inferred_intent=_infer_intent(request_text, ordered_ids, company_context),
        company_context_id=company_context.get("company_id", ""),
        company_context_name=company_context.get("company_name", ""),
        execution_track_id=company_context.get("track_id", ""),
        primary_department=primary_pack.id,
        supporting_departments=ordered_ids[1:],
        dependency_order=ordered_ids,
        department_sequence=department_sequence,
        recommended_susan_mode=company_context.get("default_mode", primary_pack.primary_mode),
        required_evidence=required_evidence,
        required_artifacts=required_artifacts,
        context_sources=company_context.get("context_sources", []),
        routing_notes=company_context.get("routing_notes", []),
        decision_requirement=decision_requirement,
        linked_decision_id=linked_decision_id,
        routing_quality=0.82,
        output_usefulness=0.7,
        follow_through=0.65,
        reuse_value=0.75,
    )
    artifact_path = _write_action_packet_summary(store, packet, ordered_ids, packs)
    packet.artifact_paths.append(artifact_path)
    store.action_packets.save(packet)

    link_specs = [
        GraphLink(source_id=packet.id, target_id=packet.primary_department, relation="primary_department"),
    ]
    for department_id in packet.supporting_departments:
        link_specs.append(
            GraphLink(source_id=packet.id, target_id=department_id, relation="supporting_department")
        )
    if packet.linked_decision_id:
        link_specs.append(
            GraphLink(source_id=packet.id, target_id=packet.linked_decision_id, relation="linked_decision")
        )
    if packet.company_context_id:
        link_specs.append(
            GraphLink(source_id=packet.id, target_id=packet.company_context_id, relation="company_context")
        )
    for link in link_specs:
        store.graph_links.save(link)

    return {
        "inferred_intent": packet.inferred_intent,
        "recommended_departments": [packs[department_id].model_dump(mode="json") for department_id in ordered_ids],
        "recommended_susan_mode": packet.recommended_susan_mode,
        "required_evidence": required_evidence,
        "required_artifacts": required_artifacts,
        "decision_requirement": packet.decision_requirement.value,
        "action_packet": packet.model_dump(mode="json"),
        "linked_decision_id": linked_decision_id,
        "company_context": company_context,
    }


def _normalize_decision_record(raw: dict) -> dict:
    options = []
    for option in raw.get("options", []):
        if "scores" in option:
            scores = {
                key: round(value * 100, 1) if isinstance(value, (int, float)) and value <= 1 else float(value)
                for key, value in option.get("scores", {}).items()
            }
            total = float(option.get("total") or option.get("total_score") or round(sum(scores.values()) / max(len(scores), 1), 1))
            summary = option.get("summary", option.get("description", ""))
        else:
            scores = {
                "impact": _qualitative_score(option.get("impact", "medium")),
                "effort": _qualitative_score(option.get("effort", "medium"), invert=True),
                "risk": _qualitative_score(option.get("risk", "medium"), invert=True),
                "confidence": _qualitative_score(option.get("confidence", "medium")),
            }
            total = round(sum(scores.values()) / len(scores), 1)
            summary = option.get("summary", "")
        options.append(
            {
                "title": option.get("title", option.get("name", option.get("id", "Option"))),
                "scores": scores,
                "total": total,
                "summary": summary,
            }
        )

    if not options:
        recommendation = raw.get("recommendation", "Keep current direction")
        options.append(
            {
                "title": str(recommendation),
                "scores": {
                    "impact": 70.0,
                    "effort": 60.0,
                    "risk": 60.0,
                    "confidence": 70.0,
                },
                "total": 65.0,
                "summary": raw.get("decision_statement", ""),
            }
        )

    assumptions = [
        _normalize_text_item(item)
        for item in raw.get("assumptions", [])
        if _normalize_text_item(item)
    ]
    next_actions = [
        _normalize_text_item(item)
        for item in raw.get("next_actions", [])
        if _normalize_text_item(item)
    ]
    if not next_actions and raw.get("output", {}).get("next_experiment"):
        next_actions = [raw["output"]["next_experiment"]]

    return {
        "id": raw.get("id", raw.get("_stem", "")),
        "title": raw.get("title", raw.get("id", "Untitled decision")),
        "status": raw.get("status", "draft"),
        "context": raw.get("context") or raw.get("decision_statement") or raw.get("why_now", ""),
        "company_id": raw.get("company_id", raw.get("company", "")),
        "project_id": raw.get("project_id", raw.get("project", "")),
        "assumptions": assumptions,
        "next_actions": next_actions,
        "artifacts": raw.get("artifacts", []),
        "linked_capabilities": raw.get("linked_capabilities", []),
        "linked_projects": raw.get("linked_projects", []),
        "options": options,
        "recommendation": raw.get("recommendation", ""),
        "path": raw.get("_path", ""),
    }


def _select_departments(
    request_text: str,
    packs: dict[str, DepartmentPack],
    company_context: dict | None = None,
) -> list[str]:
    lowered = request_text.lower()
    scores = {pack_id: 0.1 for pack_id in packs}

    company_context = company_context or {}
    for index, department_id in enumerate(company_context.get("default_departments", [])):
        if department_id in scores:
            scores[department_id] += 6.0 - index

    for pack_id, pack in packs.items():
        for keyword in pack.routing_keywords:
            if keyword.lower() in lowered:
                scores[pack_id] += 2.0

    for pack_id, hints in DEPARTMENT_HINTS.items():
        if pack_id not in scores:
            continue
        for hint in hints:
            if hint in lowered:
                scores[pack_id] += 1.5

    if "project" in lowered:
        scores["founder-decision-room"] = scores.get("founder-decision-room", 0) + 5.0
        scores["product-experience-studio"] = scores.get("product-experience-studio", 0) + 1.5
        scores["engineering-agent-systems-studio"] = scores.get("engineering-agent-systems-studio", 0) + 1.5

    if any(term in lowered for term in ("user", "customer", "consumer")):
        scores["consumer-user-studio"] = scores.get("consumer-user-studio", 0) + 3.5
        scores["product-experience-studio"] = scores.get("product-experience-studio", 0) + 1.0

    if any(term in lowered for term in ("launch", "message", "marketing", "campaign", "positioning")):
        scores["marketing-narrative-studio"] = scores.get("marketing-narrative-studio", 0) + 4.0
        scores["product-experience-studio"] = scores.get("product-experience-studio", 0) + 1.0
        scores["founder-decision-room"] = scores.get("founder-decision-room", 0) + 1.0

    if any(
        term in lowered
        for term in (
            "training",
            "session",
            "facilitation",
            "handout",
            "slides",
            "activity",
            "strategist",
            "ellen",
            "gen chat",
            "workshop",
        )
    ):
        scores["job-studio"] = scores.get("job-studio", 0) + 5.0
        scores["marketing-narrative-studio"] = scores.get("marketing-narrative-studio", 0) + 1.5
        scores["consumer-user-studio"] = scores.get("consumer-user-studio", 0) + 1.0

    if any(term in lowered for term in ("build", "architecture", "system", "engineering", "agent")):
        scores["engineering-agent-systems-studio"] = scores.get("engineering-agent-systems-studio", 0) + 4.0
        scores["product-experience-studio"] = scores.get("product-experience-studio", 0) + 1.5

    if any(term in lowered for term in ("metrics", "analytics", "data", "forecast", "simulation", "scorecard")):
        scores["data-decision-science-studio"] = scores.get("data-decision-science-studio", 0) + 4.0

    if any(term in lowered for term in ("revenue", "growth", "pipeline", "conversion", "pricing", "funnel")):
        scores["revenue-growth-studio"] = scores.get("revenue-growth-studio", 0) + 4.0

    if any(term in lowered for term in ("finance", "budget", "kpi", "cadence", "variance")):
        scores["finance-operating-cadence-studio"] = scores.get("finance-operating-cadence-studio", 0) + 4.0

    if any(term in lowered for term in ("team", "org", "role", "hiring", "recruiting", "onboarding")):
        scores["talent-org-design-studio"] = scores.get("talent-org-design-studio", 0) + 4.0

    if any(term in lowered for term in ("trust", "governance", "security", "privacy", "compliance", "accessibility")):
        scores["trust-governance-studio"] = scores.get("trust-governance-studio", 0) + 4.0

    if any(term in lowered for term in ("roadmap", "experience", "workflow", "feature", "product")):
        scores["product-experience-studio"] = scores.get("product-experience-studio", 0) + 3.0
        scores["founder-decision-room"] = scores.get("founder-decision-room", 0) + 1.0

    if "build" in lowered and "project" in lowered:
        scores["founder-decision-room"] = scores.get("founder-decision-room", 0) + 2.0

    if "roadmap" in lowered and any(term in lowered for term in ("user", "users", "customer", "consumer")):
        scores["consumer-user-studio"] = scores.get("consumer-user-studio", 0) + 2.5

    if _suppress_engineering_for_company_context(company_context, lowered):
        scores["engineering-agent-systems-studio"] = 0.1

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    selected = [pack_id for pack_id, score in ranked if score > 0.5][:3]
    if not selected:
        return ["founder-decision-room"]
    return selected


def _order_departments(selected_ids: list[str], packs: dict[str, DepartmentPack]) -> list[str]:
    ordered: list[str] = []

    def visit(department_id: str) -> None:
        if department_id in ordered:
            return
        ordered.append(department_id)
        for handoff in packs[department_id].handoff_rules:
            if handoff.to_department in selected_ids and handoff.to_department not in ordered:
                ordered.append(handoff.to_department)

    visit(selected_ids[0])
    for department_id in selected_ids[1:]:
        visit(department_id)
    return ordered


def _build_department_sequence(selected_ids: list[str], packs: dict[str, DepartmentPack]) -> list[DepartmentStep]:
    sequence: list[DepartmentStep] = []
    for index, department_id in enumerate(selected_ids):
        pack = packs[department_id]
        depends_on = [selected_ids[index - 1]] if index > 0 else []
        sequence.append(
            DepartmentStep(
                department_id=department_id,
                department_name=pack.name,
                role="primary" if index == 0 else "supporting",
                depends_on=depends_on,
                expected_outputs=pack.default_outputs[:3],
            )
        )
    return sequence


def _decision_requirement_for(
    request_text: str,
    packs: list[DepartmentPack],
    company_context: dict | None = None,
) -> DecisionRequirement:
    lowered = request_text.lower()
    company_context = company_context or {}
    override = company_context.get("decision_requirement")
    if override:
        return DecisionRequirement(override)
    if any(pack.decision_requirement == DecisionRequirement.required for pack in packs):
        return DecisionRequirement.required
    if any(hint in lowered for hint in MATERIALITY_HINTS):
        return DecisionRequirement.required
    if len(packs) > 1:
        return DecisionRequirement.optional
    return DecisionRequirement.none


def _link_or_create_decision(
    store: Store,
    request_text: str,
    decision_requirement: DecisionRequirement,
    company_id: str = "",
) -> str:
    if decision_requirement == DecisionRequirement.none:
        return ""

    ctx = store.context()
    active_decision_id = ctx.get("active_decision", "")
    if active_decision_id and get_decision_record(store, active_decision_id):
        return active_decision_id

    decision = Decision(
        title=_request_title(request_text),
        context=request_text,
        company=company_id or ctx.get("active_company", ""),
        project=ctx.get("active_project", ""),
    )
    store.decisions.save(decision)
    return decision.id


def _write_action_packet_summary(
    store: Store,
    packet: ActionPacket,
    ordered_ids: list[str],
    packs: dict[str, DepartmentPack],
) -> str:
    target_dir = store.startup_os / "artifacts" / "action-packets"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{packet.id}.md"
    lines = [
        f"# Action Packet {packet.id}",
        "",
        f"- Request: {packet.request_text}",
        f"- Intent: {packet.inferred_intent}",
        f"- Company context: {packet.company_context_name or packet.company_context_id or 'workspace-default'}",
        f"- Execution track: {packet.execution_track_id or 'generic'}",
        f"- Susan mode: {packet.recommended_susan_mode}",
        f"- Decision requirement: {packet.decision_requirement.value}",
        f"- Linked decision: {packet.linked_decision_id or 'none'}",
        "",
        "## Department Sequence",
    ]
    for step in packet.department_sequence:
        outputs = ", ".join(step.expected_outputs) or "none specified"
        lines.append(
            f"- {step.department_name} ({step.role}) -> outputs: {outputs}"
        )
    evidence_lines = [f"- {item}" for item in packet.required_evidence] or ["- none"]
    artifact_lines = [f"- {item}" for item in packet.required_artifacts] or ["- none"]
    lines.extend(
        [
            "",
            "## Context Sources",
            *([f"- {item}" for item in packet.context_sources] or ["- none"]),
            "",
            "## Evidence Requirements",
            *evidence_lines,
            "",
            "## Artifact Requirements",
            *artifact_lines,
            "",
            "## Routing Notes",
            *([f"- {item}" for item in packet.routing_notes] or ["- none"]),
            "",
            "## Department Pack Notes",
        ]
    )
    for department_id in ordered_ids:
        pack = packs[department_id]
        lines.append(f"### {pack.name}")
        lines.append(f"- Mission: {pack.mission}")
        lines.append(f"- Writeback: {pack.memory_writeback_path}")
        lines.append(
            f"- Scorecard: {', '.join(pack.scorecard) if pack.scorecard else 'none specified'}"
        )
    target_path.write_text("\n".join(lines).strip() + "\n")
    return str(target_path.relative_to(store.root))


def _infer_intent(request_text: str, ordered_ids: list[str], company_context: dict | None = None) -> str:
    lowered = request_text.lower()
    company_context = company_context or {}
    track_id = company_context.get("track_id", "")
    if track_id:
        return track_id.replace("_", "-")
    if "launch" in lowered or "message" in lowered:
        return "launch_and_message"
    if "user" in lowered or "customer" in lowered:
        return "customer_understanding"
    if "build" in lowered or "architecture" in lowered:
        return "build_and_operate"
    if ordered_ids and ordered_ids[0] == "founder-decision-room":
        return "strategic_direction"
    return "multi_department_execution"


def _request_title(text: str) -> str:
    words = re.sub(r"\s+", " ", text.strip()).split(" ")
    return "Action Packet Decision: " + " ".join(words[:10]).strip()


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _unique(items) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item and item not in seen:
            ordered.append(item)
            seen.add(item)
    return ordered


def _normalize_text_item(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return "; ".join(f"{key}: {item}" for key, item in value.items())
    return str(value) if value is not None else ""


def _resolve_company_context(store: Store, request_text: str) -> dict:
    lowered = request_text.lower()
    if any(phrase in lowered for phrase in JOB_ROUTING_SKIP_PHRASES):
        return {}

    company = _company_record(store, JOB_STUDIO_COMPANY_ID)
    if not company:
        return {}

    explicit_job_studio = "job studio" in lowered or JOB_STUDIO_COMPANY_ID in lowered
    matched_track = None
    best_score = 0
    for track in company.get("execution_tracks", []):
        keywords = [keyword.lower() for keyword in track.get("ask_keywords", [])]
        score = sum(1 for keyword in keywords if keyword and keyword in lowered)
        if score > best_score:
            best_score = score
            matched_track = track

    if not explicit_job_studio and best_score == 0:
        return {}

    if matched_track is None and explicit_job_studio:
        matched_track = next(
            (
                track
                for track in company.get("execution_tracks", [])
                if track.get("id") == "work_memory"
            ),
            None,
        )
    if matched_track is None:
        return {}

    data_assets = company.get("data_assets", [])
    source_types = matched_track.get("source_types", [])
    context_sources = []
    for asset in data_assets:
        asset_type = asset.get("type", "")
        if source_types and asset_type not in source_types:
            continue
        context_sources.append(f"{asset_type}: {asset.get('path', '')}")

    routing_notes = [
        f"Use Susan company_id `{company.get('susan_company_id', company.get('id', ''))}` for memory-grounded retrieval.",
        "Treat Job Studio memory as grounded recall support rather than a complete historical record.",
    ]
    if matched_track.get("id") in {"interview_prep", "opportunity_briefs", "linked_company_context"}:
        routing_notes.append("Bridge target-company research with Job Studio memory and keep namespaces explicit.")

    return {
        "company_id": company.get("id", ""),
        "company_name": company.get("name", ""),
        "track_id": matched_track.get("id", ""),
        "track_name": matched_track.get("name", ""),
        "default_departments": matched_track.get("default_departments", []),
        "required_evidence": matched_track.get("required_evidence", []),
        "required_artifacts": matched_track.get("required_artifacts", []),
        "decision_requirement": matched_track.get("decision_requirement", ""),
        "default_mode": matched_track.get("default_mode", ""),
        "context_sources": context_sources,
        "routing_notes": routing_notes,
    }


def _company_record(store: Store, company_id: str) -> dict | None:
    for record in store.load_yaml_collection(store.startup_os / "companies"):
        if record.get("id") == company_id:
            return record
    return None


def _suppress_engineering_for_company_context(company_context: dict, lowered_request: str) -> bool:
    if company_context.get("company_id") != JOB_STUDIO_COMPANY_ID:
        return False
    if company_context.get("track_id") not in JOB_NONTECHNICAL_TRACKS:
        return False
    return not any(term in lowered_request for term in TECHNICAL_ROUTING_TERMS)
