"""Susan foundry helpers for company execution blueprints and mode protocols."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from supabase import create_client
import yaml

from susan_core.config import config

FOUNDY_ROOT = config.data_dir / "foundry"
MODE_PROTOCOLS_PATH = FOUNDY_ROOT / "susan_modes.yaml"
COMPANY_FOUNDRY_PATH = FOUNDY_ROOT / "company_foundry.yaml"
EXPERT_COUNCILS_PATH = FOUNDY_ROOT / "expert_councils.yaml"
STAGE_GATES_PATH = FOUNDY_ROOT / "stage_gates.yaml"
MATURITY_MODEL_PATH = FOUNDY_ROOT / "maturity_model.yaml"
PROJECT_TARGETS_PATH = config.data_dir / "project_protocol_targets.yaml"
AGENT_REGISTRY_PATH = config.data_dir / "agent_registry.yaml"
COMPANY_REGISTRY_PATH = config.data_dir / "company_registry.yaml"
DOMAINS_ROOT = config.data_dir / "domains"
SHARED_FALLBACK_TYPES = {
    "studio_case_library",
    "studio_antipatterns",
    "studio_memory",
    "studio_templates",
    "studio_evals",
    "studio_open_research",
    "technical_docs",
    "legal_compliance",
    "security",
    "ux_research",
    "operational_protocols",
    "expert_knowledge",
}


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _registry_agents() -> dict[str, Any]:
    return (_load_yaml(AGENT_REGISTRY_PATH).get("agents") or {})


def _companies() -> dict[str, Any]:
    return (_load_yaml(COMPANY_REGISTRY_PATH).get("companies") or {})


def _domain_root(company_id: str, company: dict[str, Any]) -> Path | None:
    domain_pack = company.get("primary_domain_pack")
    if domain_pack:
        root = DOMAINS_ROOT / domain_pack
        return root if root.exists() else None
    if company_id == "founder-intelligence-os":
        root = DOMAINS_ROOT / "founder_foundry_intelligence"
        return root if root.exists() else None
    return None


def suggest_mode(task: str) -> str:
    task_lower = task.lower()
    foundry_keywords = [
        "build out",
        "company",
        "domain",
        "studio",
        "foundry",
        "capability",
        "team",
        "protocol",
        "architecture",
        "operating system",
    ]
    design_keywords = [
        "design",
        "ux",
        "ui",
        "landing page",
        "experience",
        "wireframe",
        "motion",
        "journey",
        "prototype",
        "screen",
    ]
    deep_keywords = [
        "research",
        "benchmark",
        "compare",
        "evidence",
        "investigate",
        "unknown",
        "analyze",
        "analysis",
        "why",
        "review",
    ]

    if any(keyword in task_lower for keyword in foundry_keywords) and len(task.split()) >= 6:
        return "foundry"
    if any(keyword in task_lower for keyword in design_keywords):
        return "design"
    if any(keyword in task_lower for keyword in deep_keywords):
        return "deep"
    return "quick"


def mode_options_for_task(task: str | None = None) -> list[dict[str, Any]]:
    payload = _load_yaml(MODE_PROTOCOLS_PATH)
    modes = payload.get("modes", [])
    suggested = suggest_mode(task or "")
    rendered: list[dict[str, Any]] = []
    for mode in modes:
        rendered.append({**mode, "recommended": bool(task) and mode.get("id") == suggested})
    return rendered


def build_company_blueprint(company_id: str) -> dict[str, Any]:
    companies = _companies()
    company = companies.get(company_id, {})
    foundry = _load_yaml(COMPANY_FOUNDRY_PATH).get("companies", {}).get(company_id, {})
    councils_map = _load_yaml(EXPERT_COUNCILS_PATH).get("councils", {})
    stage_gates_map = _load_yaml(STAGE_GATES_PATH).get("gates", [])
    maturity_model = _load_yaml(MATURITY_MODEL_PATH).get("dimensions", [])
    targets = [
        target
        for target in (_load_yaml(PROJECT_TARGETS_PATH).get("targets") or [])
        if target.get("company_id") == company_id
    ]
    registry_agents = _registry_agents()
    supabase = create_client(config.supabase_url, config.supabase_key)

    def dataset_count(data_type: str) -> int:
        response = (
            supabase.table("knowledge_chunks")
            .select("id", count="exact")
            .eq("company_id", company_id)
            .eq("data_type", data_type)
            .execute()
        )
        total = int(response.count or 0)
        if company_id != "shared" and data_type in SHARED_FALLBACK_TYPES:
            shared = (
                supabase.table("knowledge_chunks")
                .select("id", count="exact")
                .eq("company_id", "shared")
                .eq("data_type", data_type)
                .execute()
            )
            total += int(shared.count or 0)
        return total

    artifact_inventory: list[dict[str, Any]] = []
    domain_root = _domain_root(company_id, company)
    if domain_root:
        artifact_manifest = _load_yaml(domain_root / "artifact_inventory.yaml").get("artifacts", [])
        for artifact in artifact_manifest:
            artifact_path = domain_root / artifact["path"]
            artifact_status = artifact.get("status", "active")
            if not artifact_path.exists():
                artifact_status = "missing"
            artifact_inventory.append(
                {
                    "id": artifact["id"],
                    "name": artifact["name"],
                    "data_type": artifact["data_type"],
                    "status": artifact_status,
                    "path": str(artifact_path),
                    "summary": artifact.get("summary", ""),
                    "stage_gates": artifact.get("stage_gates", []),
                    "exists": artifact_path.exists(),
                    "dataset_count": dataset_count(artifact["data_type"]),
                }
            )

    tracks: list[dict[str, Any]] = []
    for track in foundry.get("execution_tracks", []):
        agents = [agent for agent in track.get("agents", []) if agent in registry_agents]
        missing_agents = [agent for agent in track.get("agents", []) if agent not in registry_agents]
        dataset_summary = {data_type: dataset_count(data_type) for data_type in track.get("data_types", [])}
        missing_data = [data_type for data_type, count in dataset_summary.items() if count == 0]
        status = "ready"
        if missing_agents and agents:
            status = "partial"
        elif missing_agents and not agents:
            status = "planned"
        if missing_data and status == "ready":
            status = "partial"

        tracks.append(
            {
                "id": track["id"],
                "name": track["name"],
                "description": track["description"],
                "status": status,
                "agents": agents,
                "missing_agents": missing_agents,
                "data_types": track.get("data_types", []),
                "dataset_counts": dataset_summary,
                "outputs": track.get("outputs", []),
                "notes": track.get("notes", []),
            }
        )

    councils: list[dict[str, Any]] = []
    for council_id in foundry.get("expert_councils", []):
        council = councils_map.get(council_id)
        if not council:
            continue
        councils.append({"id": council_id, **council})

    gaps: list[dict[str, Any]] = []
    for track in tracks:
        if track["missing_agents"]:
            gaps.append(
                {
                    "id": f"gap-{track['id']}-agents",
                    "severity": "critical",
                    "title": f"{track['name']} is missing required agents",
                    "detail": f"Missing agents: {', '.join(track['missing_agents'])}",
                }
            )
        missing_data = [data_type for data_type, count in track["dataset_counts"].items() if count == 0]
        if missing_data:
            gaps.append(
                {
                    "id": f"gap-{track['id']}-datasets",
                    "severity": "warning",
                    "title": f"{track['name']} still lacks some dataset coverage",
                    "detail": f"Missing data types: {', '.join(missing_data)}",
                }
            )
    next_actions = list(foundry.get("next_actions", []))
    if not next_actions:
        next_actions = [gap["title"] for gap in gaps[:5]]

    all_data_types = sorted(
        {
            data_type
            for track in tracks
            for data_type in track.get("data_types", [])
        }
    )
    ready_tracks = sum(1 for track in tracks if track["status"] == "ready")
    genome = {
        "domain": company.get("domain"),
        "stage": company.get("stage"),
        "budget_per_month_usd": company.get("budget_per_month_usd"),
        "track_count": len(tracks),
        "ready_track_count": ready_tracks,
        "council_count": len(councils),
        "project_target_count": len(targets),
        "primary_workloads": [track["name"] for track in tracks],
        "accessible_data_types": all_data_types,
    }

    accessible_counts = {
        data_type: dataset_count(data_type)
        for data_type in all_data_types
    }
    maturity: list[dict[str, Any]] = []
    for dimension in maturity_model:
        required = dimension.get("required_data_types", [])
        present = [data_type for data_type in required if accessible_counts.get(data_type, 0) > 0]
        if not required:
            score = 100 if tracks and councils_map else 0
        else:
            score = round((len(present) / len(required)) * 100)
        status = "gap"
        if score >= 85:
            status = "ready"
        elif score >= 50:
            status = "partial"
        notes = []
        if not required:
            notes.append("Score inferred from company, tracks, and protocols.")
        else:
            missing = [data_type for data_type in required if data_type not in present]
            if missing:
                notes.append(f"Missing data types: {', '.join(missing)}")
        maturity.append(
            {
                "id": dimension["id"],
                "name": dimension["name"],
                "summary": dimension.get("summary", ""),
                "score": score,
                "status": status,
                "required_data_types": required,
                "present_data_types": present,
                "notes": notes,
            }
        )

    accessible = accessible_counts
    stage_gates: list[dict[str, Any]] = []
    for gate in stage_gates_map:
        gate_id = gate["id"]
        status = "gap"
        why = "Requirements not yet satisfied."
        blocking_gaps: list[str] = []
        gate_artifacts = [
            artifact
            for artifact in artifact_inventory
            if gate_id in artifact.get("stage_gates", [])
        ]
        missing_artifacts = [
            artifact["name"]
            for artifact in gate_artifacts
            if not artifact.get("exists") or artifact.get("status") == "missing"
        ]
        if gate_id == "thesis":
            thesis_ready = bool(company.get("product_description") and company.get("target_market") and company.get("current_challenges"))
            status = "ready" if thesis_ready else "partial"
            why = "Company definition is present." if thesis_ready else "Company context needs stronger definition."
        elif gate_id == "evidence":
            evidence_ready = any(accessible.get(data_type, 0) > 0 for data_type in all_data_types)
            status = "ready" if evidence_ready else "gap"
            why = "Track data coverage exists." if evidence_ready else "No accessible track evidence yet."
        elif gate_id == "blueprint":
            blueprint_ready = bool(tracks and councils and foundry.get("protocols"))
            status = "ready" if blueprint_ready else "partial"
            why = "Execution tracks, councils, and protocols are defined." if blueprint_ready else "Foundry definition is incomplete."
        elif gate_id == "build":
            required = ["technical_docs", "legal_compliance", "security"]
            blocking_gaps = [data_type for data_type in required if accessible.get(data_type, 0) == 0]
            status = "ready" if not blocking_gaps else "partial"
            why = "Build baselines exist." if not blocking_gaps else "Trust or technical baselines are still thin."
        elif gate_id == "launch":
            required = ["ux_research", "business_strategy"]
            blocking_gaps = [data_type for data_type in required if accessible.get(data_type, 0) == 0]
            status = "ready" if not blocking_gaps else "partial"
            why = "Launch and operating inputs exist." if not blocking_gaps else "Launch-facing inputs are incomplete."
        elif gate_id == "memory":
            required = ["studio_memory", "studio_evals"]
            blocking_gaps = [data_type for data_type in required if accessible.get(data_type, 0) == 0]
            status = "ready" if not blocking_gaps else "partial"
            why = "Memory and evaluation are available." if not blocking_gaps else "Memory writeback or evaluation needs seeding."
        if gate_artifacts:
            if missing_artifacts:
                status = "partial" if status == "ready" else status
                why = f"{why} Artifact coverage is still incomplete."
            if status == "gap" and not missing_artifacts:
                status = "partial"
        stage_gates.append(
            {
                "id": gate_id,
                "name": gate["name"],
                "summary": gate.get("summary", ""),
                "status": status,
                "why": why,
                "required_artifacts": gate.get("required_artifacts", []),
                "blocking_gaps": blocking_gaps,
                "artifact_count": len(gate_artifacts),
                "artifact_names": [artifact["name"] for artifact in gate_artifacts],
                "missing_artifacts": missing_artifacts,
            }
        )

    return {
        "company_id": company_id,
        "company_name": company.get("name", company_id),
        "description": foundry.get("description", company.get("product_description", "")),
        "default_mode": foundry.get("default_mode", "quick"),
        "genome": genome,
        "artifact_inventory": artifact_inventory,
        "mode_options": mode_options_for_task(),
        "stage_gates": stage_gates,
        "maturity": maturity,
        "key_protocols": foundry.get("protocols", []),
        "execution_tracks": tracks,
        "expert_councils": councils,
        "project_targets": targets,
        "coverage_gaps": gaps,
        "next_actions": next_actions,
    }


def build_foundry_assessment(company_ids: list[str] | None = None) -> dict[str, Any]:
    companies = _companies()
    selected = company_ids or list(companies.keys())
    return {
        "companies": [
            {
                "company_id": blueprint["company_id"],
                "company_name": blueprint["company_name"],
                "default_mode": blueprint["default_mode"],
                "genome": blueprint["genome"],
                "track_statuses": [
                    {
                        "id": track["id"],
                        "name": track["name"],
                        "status": track["status"],
                        "dataset_counts": track["dataset_counts"],
                    }
                    for track in blueprint["execution_tracks"]
                ],
                "maturity": blueprint["maturity"],
                "coverage_gaps": blueprint["coverage_gaps"],
                "stage_gates": blueprint["stage_gates"],
                "next_actions": blueprint["next_actions"],
            }
            for company_id in selected
            for blueprint in [build_company_blueprint(company_id)]
        ]
    }


def render_foundry_assessment_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Foundry Assessment Snapshot",
        "",
        "This report is generated from the live Susan foundry blueprints.",
        "",
    ]
    for company in report["companies"]:
        lines.append(f"## {company['company_name']}")
        lines.append(f"- Company ID: `{company['company_id']}`")
        lines.append(f"- Default mode: `{company['default_mode']}`")
        lines.append(
            f"- Ready tracks: `{company['genome'].get('ready_track_count', 0)}/{company['genome'].get('track_count', 0)}`"
        )
        lines.append("")
        lines.append("### Track Status")
        for track in company["track_statuses"]:
            dataset_counts = ", ".join(
                f"{name}={count}" for name, count in track["dataset_counts"].items()
            )
            lines.append(f"- `{track['id']}` [{track['status']}] {dataset_counts}")
        lines.append("")
        lines.append("### Maturity")
        for dimension in company["maturity"]:
            lines.append(
                f"- `{dimension['id']}` [{dimension['status']}] score={dimension['score']}"
            )
        lines.append("")
        if company["coverage_gaps"]:
            lines.append("### Coverage Gaps")
            for gap in company["coverage_gaps"]:
                lines.append(f"- [{gap['severity']}] {gap['title']} — {gap['detail']}")
            lines.append("")
        lines.append("### Next Actions")
        for action in company["next_actions"]:
            lines.append(f"- {action}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_company_blueprint_markdown(blueprint: dict[str, Any]) -> str:
    lines = [
        f"# {blueprint['company_name']} — Susan Execution Blueprint",
        "",
        blueprint.get("description") or "No company description available.",
        "",
        f"- Company ID: `{blueprint['company_id']}`",
        f"- Default mode: `{blueprint.get('default_mode', 'quick')}`",
        "",
        "## Genome",
        f"- Domain: `{blueprint.get('genome', {}).get('domain', 'unknown')}`",
        f"- Stage: `{blueprint.get('genome', {}).get('stage', 'unknown')}`",
        f"- Tracks ready: `{blueprint.get('genome', {}).get('ready_track_count', 0)}/{blueprint.get('genome', {}).get('track_count', 0)}`",
        f"- Councils: `{blueprint.get('genome', {}).get('council_count', 0)}`",
        "",
        "## Mode Options",
    ]

    for mode in blueprint.get("mode_options", []):
        lines.append(
            f"- `{mode['id']}`: {mode['name']} via `{mode['command']}` — {mode['use_when']}"
        )

    lines.extend(["", "## Execution Tracks"])
    for track in blueprint.get("execution_tracks", []):
        lines.append(f"### {track['name']} [{track['status']}]")
        lines.append(track["description"])
        if track.get("agents"):
            lines.append(f"- Agents: {', '.join(track['agents'])}")
        if track.get("data_types"):
            counts = ", ".join(
                f"{data_type}={track['dataset_counts'].get(data_type, 0)}"
                for data_type in track["data_types"]
            )
            lines.append(f"- Data types: {counts}")
        if track.get("outputs"):
            lines.append(f"- Outputs: {', '.join(track['outputs'])}")
        if track.get("notes"):
            lines.append(f"- Notes: {'; '.join(track['notes'])}")
        if track.get("missing_agents"):
            lines.append(f"- Missing agents: {', '.join(track['missing_agents'])}")
        lines.append("")

    if blueprint.get("artifact_inventory"):
        lines.append("## Artifact Inventory")
        for artifact in blueprint["artifact_inventory"]:
            lines.append(
                f"- `{artifact['id']}` [{artifact['status']}] {artifact['name']} — {artifact['data_type']}"
            )
        lines.append("")

    if blueprint.get("stage_gates"):
        lines.append("## Stage Gates")
        for gate in blueprint["stage_gates"]:
            lines.append(f"### {gate['name']} [{gate['status']}]")
            lines.append(gate.get("summary", ""))
            lines.append(f"- Why: {gate.get('why', '')}")
            if gate.get("artifact_names"):
                lines.append(f"- Artifacts: {', '.join(gate['artifact_names'])}")
            if gate.get("missing_artifacts"):
                lines.append(f"- Missing artifacts: {', '.join(gate['missing_artifacts'])}")
            if gate.get("blocking_gaps"):
                lines.append(f"- Blocking gaps: {', '.join(gate['blocking_gaps'])}")
            lines.append("")

    if blueprint.get("maturity"):
        lines.append("## Maturity")
        for dimension in blueprint["maturity"]:
            lines.append(f"- `{dimension['id']}` [{dimension['status']}] {dimension['score']}")
        lines.append("")

    lines.append("## Expert Councils")
    for council in blueprint.get("expert_councils", []):
        lines.append(f"### {council['name']}")
        lines.append(council["focus"])
        if council.get("disciplines"):
            lines.append(f"- Disciplines: {', '.join(council['disciplines'])}")
        if council.get("source_priorities"):
            lines.append(f"- Source priorities: {', '.join(council['source_priorities'])}")
        lines.append("")

    lines.append("## Key Protocols")
    for protocol in blueprint.get("key_protocols", []):
        lines.append(f"- {protocol}")

    lines.extend(["", "## Next Actions"])
    for action in blueprint.get("next_actions", []):
        lines.append(f"- {action}")

    if blueprint.get("coverage_gaps"):
        lines.extend(["", "## Coverage Gaps"])
        for gap in blueprint["coverage_gaps"]:
            lines.append(f"- [{gap.get('severity', 'info')}] {gap['title']}")

    return "\n".join(lines).strip() + "\n"
