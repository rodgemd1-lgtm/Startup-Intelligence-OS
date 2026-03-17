"""Repository-native control-plane catalog and audit services."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import cached_property
from pathlib import Path
import json
import os
import re

import yaml

from fitness_intel.markdown_parser import parse_fuzzy_date, parse_markdown_profile
from fitness_intel.pipeline import CorpusBuilder
from fitness_intel.retrieval import HybridRetriever
from susan_core.config import config

from .audits import extract_numeric_claim, file_exists_health, freshness_status, issue_to_backlog, make_issue
from .prompts import authoring_agent_id, compile_prompt_bundle, compile_prompt_bundle_for_agent, load_agent_characteristics
from .schemas import (
    AgentProfile,
    AgentCapability,
    BacklogItem,
    Claim,
    CoverageGap,
    EvidenceNode,
    KnowledgeAsset,
    KnowledgeSearchResponse,
    LaneStatus,
    LayerCoverage,
    MCPServer,
    MCPTool,
    PromptResearchSnapshot,
    PromptBundle,
    PromptResearchProviderStatus,
    ProtocolDefinition,
    ReconciliationIssue,
    ReconciliationReport,
    ResearchTopicStatus,
    RoutingPolicy,
    RunTrace,
    ScoreMetric,
    Tenant,
    TenantScorecard,
    VisualAsset,
)


@dataclass
class SearchDocument:
    id: str
    title: str
    content: str
    source_path: str
    asset_type: str
    lane: str
    freshness_date: datetime | None = None
    freshness_status: str = "unknown"
    metadata: dict | None = None


class ControlPlaneCatalog:
    """Aggregates repo state into stable cockpit contracts."""

    def __init__(self) -> None:
        self.backend_root = config.base_dir
        self.susan_root = self.backend_root.parent
        self.repo_root = self.susan_root.parent
        self.agent_authoring_dir = self.susan_root / "agents"
        self.commands_dir = self.susan_root / "commands"
        self.skills_dir = self.susan_root / "skills"
        self.company_registry_path = self.backend_root / "data" / "company_registry.yaml"
        self.agent_registry_path = self.backend_root / "data" / "agent_registry.yaml"
        self.dataset_requirements_path = self.backend_root / "data" / "dataset_requirements_master.md"
        self.domain_root = self.backend_root / "data" / "domains" / "fitness_app_intelligence"
        self.domain_contract_path = self.domain_root / "contracts" / "startup_os_domain_pack.yaml"
        self.freshness_policy_path = self.domain_root / "registry" / "freshness_policy.yaml"
        self.be_module_dir = self.backend_root / "data" / "be_module"
        self.experience_intelligence_dir = self.backend_root / "data" / "experience_intelligence"
        self.prompt_library_dir = self.backend_root / "data" / "prompt_library"
        self.prompt_source_manifest_path = self.prompt_library_dir / "source_manifest.yaml"
        self.prompt_research_artifacts_dir = self.backend_root / "artifacts" / "prompt_intelligence"
        self.prompt_research_results_path = self.prompt_research_artifacts_dir / "search_results.json"
        self.prompt_research_scrapes_path = self.prompt_research_artifacts_dir / "scraped_pages.jsonl"
        self.prompt_research_summary_path = self.prompt_research_artifacts_dir / "summary.md"
        self.mcp_config_path = self.repo_root / ".mcp.json"
        self.mcp_server_path = self.backend_root / "mcp_server" / "server.py"
        self.claude_md_path = self.repo_root / "CLAUDE.md"
        self.design_doc_path = self.repo_root / "docs" / "plans" / "2026-03-06-susan-team-architect-design.md"
        self.frontend_dir = self.repo_root / "apps" / "intelligence-cockpit"

    @cached_property
    def company_registry(self) -> dict:
        return yaml.safe_load(self.company_registry_path.read_text(encoding="utf-8")) or {}

    @cached_property
    def agent_registry(self) -> dict:
        return yaml.safe_load(self.agent_registry_path.read_text(encoding="utf-8")) or {}

    @cached_property
    def domain_contract(self) -> dict:
        return yaml.safe_load(self.domain_contract_path.read_text(encoding="utf-8")) or {}

    @cached_property
    def freshness_policy(self) -> dict:
        return yaml.safe_load(self.freshness_policy_path.read_text(encoding="utf-8")) or {}

    @cached_property
    def corpus_builder(self) -> CorpusBuilder:
        return CorpusBuilder(self.domain_root)

    @cached_property
    def inventory(self) -> dict:
        return self.corpus_builder.build_inventory()

    @cached_property
    def chunk_models(self) -> list:
        return self.corpus_builder.build_chunks()

    @cached_property
    def chunk_payload(self) -> list[dict]:
        return [chunk.model_dump(mode="json") for chunk in self.chunk_models]

    @cached_property
    def hybrid_retriever(self) -> HybridRetriever:
        return HybridRetriever(self.chunk_payload)

    @cached_property
    def app_records(self) -> list[dict]:
        return self.corpus_builder.build_app_records()

    @cached_property
    def authored_agent_files(self) -> list[Path]:
        return sorted(self.agent_authoring_dir.glob("*.md"))

    @cached_property
    def prompt_bundles(self) -> list[PromptBundle]:
        return [compile_prompt_bundle(path) for path in self.authored_agent_files]

    @cached_property
    def prompt_bundles_by_id(self) -> dict[str, PromptBundle]:
        return {bundle.id: bundle for bundle in self.prompt_bundles}

    @cached_property
    def prompt_source_manifest(self) -> dict:
        if not self.prompt_source_manifest_path.exists():
            return {}
        return yaml.safe_load(self.prompt_source_manifest_path.read_text(encoding="utf-8")) or {}

    @cached_property
    def prompt_research_hits(self) -> list[dict]:
        if not self.prompt_research_results_path.exists():
            return []
        return json.loads(self.prompt_research_results_path.read_text(encoding="utf-8"))

    @cached_property
    def prompt_research_scrapes(self) -> list[dict]:
        if not self.prompt_research_scrapes_path.exists():
            return []
        rows: list[dict] = []
        for line in self.prompt_research_scrapes_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows

    @cached_property
    def dataset_counts(self) -> dict[str, int]:
        text = self.dataset_requirements_path.read_text(encoding="utf-8")
        match = re.search(
            r"## Current RAG Knowledge Base Status.*?\n((?:\|.*\n)+)",
            text,
            flags=re.S,
        )
        counts: dict[str, int] = {}
        if not match:
            return counts
        for line in match.group(1).splitlines():
            if not line.startswith("|") or "data_type" in line or "---" in line:
                continue
            parts = [part.strip() for part in line.strip("|").split("|")]
            if len(parts) < 2:
                continue
            if parts[1].isdigit():
                counts[parts[0]] = int(parts[1])
        return counts

    @cached_property
    def protocol_definitions(self) -> list[ProtocolDefinition]:
        protocols: list[ProtocolDefinition] = []
        claude_text = self.claude_md_path.read_text(encoding="utf-8")
        in_protocols = False
        for line in claude_text.splitlines():
            if line.startswith("## 9 Operational Protocols"):
                in_protocols = True
                continue
            if in_protocols and line.startswith("## "):
                break
            if in_protocols and re.match(r"^\d+\.\s+\*\*(.+?)\*\*\s+—\s+(.+)$", line):
                match = re.match(r"^\d+\.\s+\*\*(.+?)\*\*\s+—\s+(.+)$", line)
                assert match is not None
                name, summary = match.groups()
                protocols.append(
                    ProtocolDefinition(
                        id=f"protocol-{len(protocols) + 1}",
                        name=name,
                        family="operational",
                        source_path=str(self.claude_md_path),
                        summary=summary,
                        owners=["susan"],
                    )
                )
        return protocols

    @cached_property
    def protocol_documents(self) -> list[SearchDocument]:
        documents: list[SearchDocument] = []
        for path in sorted(self.be_module_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            title = text.splitlines()[0].lstrip("# ").strip() if text else path.stem
            documents.append(
                SearchDocument(
                    id=f"protocol-{path.stem}",
                    title=title,
                    content=text,
                    source_path=str(path),
                    asset_type="protocol",
                    lane="protocol",
                    metadata={"family": "behavioral_economics"},
                )
            )
        if self.experience_intelligence_dir.exists():
            for path in sorted(self.experience_intelligence_dir.glob("*.md")):
                text = path.read_text(encoding="utf-8")
                title = text.splitlines()[0].lstrip("# ").strip() if text else path.stem
                documents.append(
                    SearchDocument(
                        id=f"experience-{path.stem}",
                        title=title,
                        content=text,
                        source_path=str(path),
                        asset_type="protocol",
                        lane="protocol",
                        metadata={"family": "experience_intelligence"},
                    )
                )
        if self.prompt_library_dir.exists():
            for path in sorted(self.prompt_library_dir.glob("*")):
                if path.suffix not in {".md", ".yaml", ".yml"}:
                    continue
                text = path.read_text(encoding="utf-8")
                title = text.splitlines()[0].lstrip("# ").strip() if text else path.stem
                documents.append(
                    SearchDocument(
                        id=f"prompt-library-{path.stem}",
                        title=title,
                        content=text,
                        source_path=str(path),
                        asset_type="prompt_library",
                        lane="protocol",
                        metadata={"family": "prompt_library"},
                    )
                )
        for path in sorted(self.commands_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            title = path.stem
            documents.append(
                SearchDocument(
                    id=f"command-{path.stem}",
                    title=title,
                    content=text,
                    source_path=str(path),
                    asset_type="workflow",
                    lane="protocol",
                    metadata={"family": "command"},
                )
            )
        for path in sorted(self.skills_dir.glob("*/SKILL.md")):
            text = path.read_text(encoding="utf-8")
            title = path.parent.name
            documents.append(
                SearchDocument(
                    id=f"skill-{path.parent.name}",
                    title=title,
                    content=text,
                    source_path=str(path),
                    asset_type="skill",
                    lane="protocol",
                    metadata={"family": "skill"},
                )
            )
        dataset_text = self.dataset_requirements_path.read_text(encoding="utf-8")
        documents.append(
            SearchDocument(
                id="dataset-requirements-master",
                title="Master Dataset Requirements",
                content=dataset_text,
                source_path=str(self.dataset_requirements_path),
                asset_type="protocol",
                lane="protocol",
                metadata={"family": "dataset"},
            )
        )
        return documents

    @cached_property
    def prompt_search_documents(self) -> list[SearchDocument]:
        documents: list[SearchDocument] = []
        for bundle in self.prompt_bundles:
            content = "\n\n".join(component.content for component in bundle.components)
            documents.append(
                SearchDocument(
                    id=f"prompt-{bundle.id}",
                    title=bundle.name,
                    content=content,
                    source_path=bundle.source_paths[0],
                    asset_type="prompt_bundle",
                    lane="protocol",
                    metadata={"status": bundle.status, "version": bundle.version},
                )
            )
        return documents

    @cached_property
    def prompt_research_snapshot(self) -> PromptResearchSnapshot:
        queries = self.prompt_source_manifest.get("queries", [])
        providers = self.prompt_source_manifest.get("providers", {})
        provider_statuses: list[PromptResearchProviderStatus] = []
        for provider_name, provider_config in providers.items():
            env_name = provider_config.get("enabled_env", "")
            configured = bool(os.getenv(env_name)) if env_name else False
            provider_statuses.append(
                PromptResearchProviderStatus(
                    provider=provider_name,
                    configured=configured,
                    status="ready" if configured else "missing_credentials",
                    formats=list(provider_config.get("formats", [])),
                )
            )

        search_hits = self.prompt_research_hits
        scrape_rows = self.prompt_research_scrapes
        scrape_counts = Counter(row.get("topic", "unknown") for row in scrape_rows)
        topic_statuses: list[ResearchTopicStatus] = []
        for entry in queries:
            topic = entry.get("topic", "unknown")
            hits = [hit for hit in search_hits if hit.get("topic") == topic]
            topic_statuses.append(
                ResearchTopicStatus(
                    topic=topic,
                    query=entry.get("query", ""),
                    why=entry.get("why", ""),
                    hits=len(hits),
                    scraped_pages=scrape_counts.get(topic, 0),
                    status="covered" if hits else "missing",
                    example_urls=[hit.get("url", "") for hit in hits[:3] if hit.get("url")],
                )
            )

        artifact_paths = [
            str(path)
            for path in [
                self.prompt_research_results_path,
                self.prompt_research_scrapes_path,
                self.prompt_research_summary_path,
            ]
            if path.exists()
        ]
        generated_at = None
        if artifact_paths:
            newest = max(Path(path).stat().st_mtime for path in artifact_paths)
            generated_at = datetime.fromtimestamp(newest, tz=UTC)

        return PromptResearchSnapshot(
            generated_at=generated_at,
            total_hits=len(search_hits),
            unique_urls=len({hit.get("url", "") for hit in search_hits if hit.get("url")}),
            total_scrapes=len(scrape_rows),
            providers=provider_statuses,
            topics=topic_statuses,
            artifact_paths=artifact_paths,
        )

    @cached_property
    def research_documents(self) -> list[SearchDocument]:
        documents: list[SearchDocument] = []
        for index, hit in enumerate(self.prompt_research_hits):
            content = "\n".join(
                part
                for part in [
                    hit.get("title", ""),
                    hit.get("snippet", ""),
                    hit.get("query", ""),
                    hit.get("topic", ""),
                ]
                if part
            )
            if not content.strip():
                continue
            documents.append(
                SearchDocument(
                    id=f"prompt-research-hit-{index}",
                    title=hit.get("title") or hit.get("url", "Prompt research hit"),
                    content=content,
                    source_path=hit.get("url", ""),
                    asset_type="research_hit",
                    lane="research",
                    metadata={"provider": hit.get("provider"), "topic": hit.get("topic")},
                )
            )

        for index, row in enumerate(self.prompt_research_scrapes):
            scrape = row.get("scrape") or {}
            markdown = self._scrape_markdown(scrape)
            branding = self._scrape_branding(scrape)
            content = "\n".join(
                part
                for part in [
                    row.get("title", ""),
                    row.get("query", ""),
                    row.get("topic", ""),
                    markdown,
                    branding,
                    row.get("error", ""),
                ]
                if part
            )
            if not content.strip():
                continue
            documents.append(
                SearchDocument(
                    id=f"prompt-research-scrape-{index}",
                    title=row.get("title") or row.get("url", "Scraped prompt research"),
                    content=content,
                    source_path=row.get("url", ""),
                    asset_type="research_scrape",
                    lane="research",
                    metadata={"provider": row.get("provider"), "topic": row.get("topic")},
                )
            )
        return documents

    @cached_property
    def structured_documents(self) -> list[SearchDocument]:
        documents: list[SearchDocument] = []
        for record in self.app_records:
            features = ", ".join(feature["name"] for feature in record.get("features", []))
            claims = ", ".join(claim["value"] for claim in record.get("claims", []))
            content = "\n".join(
                value
                for value in [
                    record.get("name", ""),
                    record.get("summary", ""),
                    features,
                    claims,
                ]
                if value
            )
            freshness = None
            sources = record.get("sources", [])
            if sources:
                source_date = sources[0].get("effective_date") or sources[0].get("captured_at")
                if source_date:
                    freshness = datetime.fromisoformat(f"{source_date}T00:00:00")
            documents.append(
                SearchDocument(
                    id=record["id"],
                    title=record["name"],
                    content=content,
                    source_path=record["editorial_markdown_path"],
                    asset_type="app_record",
                    lane="structured",
                    freshness_date=freshness,
                    freshness_status="current" if freshness else "unknown",
                    metadata={"category": record.get("category")},
                )
            )
        for tenant in self.tenants():
            profile = self.company_registry["companies"][tenant.id]
            content = "\n".join(
                str(profile.get(key, ""))
                for key in [
                    "product_description",
                    "target_market",
                    "current_challenges",
                    "constraints",
                ]
            )
            documents.append(
                SearchDocument(
                    id=f"tenant-{tenant.id}",
                    title=tenant.name,
                    content=content,
                    source_path=str(self.company_registry_path),
                    asset_type="company_profile",
                    lane="structured",
                    metadata={"domain": tenant.domain, "stage": tenant.stage},
                )
            )
        return documents

    def tenants(self) -> list[Tenant]:
        companies = self.company_registry.get("companies", {})
        return [
            Tenant(
                id=tenant_id,
                name=payload["name"],
                domain=payload["domain"],
                stage=payload["stage"],
                target_market=payload["target_market"],
                budget_per_month_usd=payload.get("budget_per_month_usd"),
                primary_domain_pack=(
                    "oracle_health_intelligence"
                    if payload.get("domain") == "healthcare_enterprise_ai"
                    else self.domain_contract.get("domain")
                ),
                health_score=self._health_score(tenant_id),
            )
            for tenant_id, payload in companies.items()
        ]

    def visual_assets(self, tenant_id: str, limit: int = 25) -> list[VisualAsset]:
        try:
            rows = self.hybrid_retriever  # ensure local retriever is initialized consistently
            _ = rows
            from supabase import create_client

            sb = create_client(config.supabase_url, config.supabase_key)
            data = (
                sb.table("knowledge_chunks")
                .select("id,content,company_id,source_url,metadata")
                .eq("company_id", tenant_id)
                .eq("data_type", "visual_asset")
                .limit(limit)
                .execute()
                .data
            )
        except Exception:
            data = []

        assets: list[VisualAsset] = []
        for row in data:
            metadata = row.get("metadata") or {}
            assets.append(
                VisualAsset(
                    id=str(row.get("id")),
                    tenant_id=row.get("company_id", tenant_id),
                    title=metadata.get("title") or "Visual asset",
                    source_url=row.get("source_url"),
                    public_url=metadata.get("public_url"),
                    bucket_name=metadata.get("storage_bucket"),
                    storage_path=metadata.get("storage_path"),
                    excerpt=(row.get("content") or "")[:280],
                    metadata=metadata,
                )
            )
        return assets

    def tenant_scorecard(self, tenant_id: str) -> TenantScorecard:
        tenant = next((candidate for candidate in self.tenants() if candidate.id == tenant_id), None)
        if tenant is None:
            raise KeyError(tenant_id)

        coverage_gaps = self.knowledge_gaps(tenant_id)
        capabilities = self.agent_capabilities()
        agent_profiles = self.agent_profiles()
        layer_coverage = self.layer_coverage()
        prompt_bundles = self.prompt_bundles
        mcp_servers = self.mcp_servers()
        backlog = self.reconciliation().backlog[:8]

        blocked_prompts = sum(1 for bundle in prompt_bundles if bundle.status != "ready")
        high_gap_count = sum(1 for gap in coverage_gaps if gap.severity in {"critical", "high"})
        weak_profiles = sum(1 for profile in agent_profiles if profile.registered and profile.humanization_score < 60)
        research_hits = self.prompt_research_snapshot.total_hits

        diagnosis = (
            f"{tenant.name} is strongest in curated knowledge coverage and executable agent surface area, "
            f"but it is currently dragged down by {high_gap_count} high-severity coverage gaps, "
            f"{blocked_prompts} blocked prompt bundles, {weak_profiles} under-humanized registered agents, "
            f"and a Layer 5 emotional-design corpus that is still thinner than the operating model requires."
        )

        metrics = [
            ScoreMetric(key="local_chunks", label="Local chunks", value=str(len(self.chunk_payload))),
            ScoreMetric(key="app_profiles", label="App profiles", value=str(self.inventory["total_app_profiles"])),
            ScoreMetric(key="registered_agents", label="Registered agents", value=str(len(self.agent_registry.get("agents", {})))),
            ScoreMetric(key="authored_agents", label="Authored agents", value=str(len(self.authored_agent_files))),
            ScoreMetric(key="humanized_agents", label="Humanized agents", value=str(sum(1 for profile in agent_profiles if profile.humanization_score >= 60))),
            ScoreMetric(key="blocked_prompts", label="Blocked prompts", value=str(blocked_prompts)),
            ScoreMetric(key="prompt_research_hits", label="Prompt research hits", value=str(research_hits)),
            ScoreMetric(key="configured_mcp", label="Configured MCP servers", value=str(sum(1 for server in mcp_servers if server.status == "configured"))),
        ]

        recommended_actions = [item.reason for item in backlog[:5]]

        return TenantScorecard(
            tenant=tenant,
            diagnosis=diagnosis,
            metrics=metrics,
            layer_coverage=layer_coverage,
            protocols=self.protocol_definitions,
            agent_capabilities=capabilities,
            agent_profiles=agent_profiles,
            coverage_gaps=coverage_gaps,
            prompt_bundles=prompt_bundles,
            mcp_servers=mcp_servers,
            recommended_actions=recommended_actions,
            backlog=backlog,
        )

    def layer_coverage(self) -> list[LayerCoverage]:
        authored_agents = len(self.authored_agent_files)
        registered_agents = len(self.agent_registry.get("agents", {}))
        prompt_ready = sum(1 for bundle in self.prompt_bundles if bundle.status == "ready")
        humanized_agents = sum(1 for profile in self.agent_profiles() if profile.humanization_score >= 60)
        research_topics = sum(1 for topic in self.prompt_research_snapshot.topics if topic.hits > 0)

        structured_assets = len(self.app_records) + sum(len(record.get("claims", [])) for record in self.app_records)
        protocol_assets = len(self.protocol_definitions) + len(self.prompt_bundles)
        executable_assets = authored_agents + len(self.mcp_tools()) + len(list((self.backend_root / "simulations").glob("*.py")))
        emotional_assets = (
            len(list(self.experience_intelligence_dir.glob("*.md")))
            + humanized_agents
            + research_topics
            + sum(1 for capability in self.agent_capabilities() if "emotional_design" in capability.required_data_types)
        )

        return [
            LayerCoverage(
                layer_id="layer_1",
                name="Layer 1",
                description="Raw sources and crawls",
                asset_count=self.inventory["total_markdown_files"],
                coverage_score=min(100, 35 + self.inventory["total_markdown_files"]),
                status="healthy" if self.inventory["total_markdown_files"] else "gap",
                notes=[
                    f"{self.inventory['total_app_profiles']} app profiles discovered",
                    f"{self.inventory['analysis_documents']} analysis docs and {self.inventory['docs_documents']} system docs indexed",
                ],
            ),
            LayerCoverage(
                layer_id="layer_2",
                name="Layer 2",
                description="Normalized entities, facts, metrics, and protocols",
                asset_count=structured_assets,
                coverage_score=min(100, 20 + structured_assets),
                status="partial",
                notes=[
                    f"{len(self.app_records)} normalized app records available",
                    "Evidence graph tables are planned but not persisted locally yet",
                ],
            ),
            LayerCoverage(
                layer_id="layer_3",
                name="Layer 3",
                description="Synthesized knowledge, prompt bundles, and domain packs",
                asset_count=len(self.chunk_payload) + protocol_assets + 1,
                coverage_score=min(100, 30 + (prompt_ready * 2) + int(len(self.chunk_payload) / 50)),
                status="partial" if prompt_ready != len(self.prompt_bundles) else "healthy",
                notes=[
                    f"{len(self.chunk_payload)} narrative knowledge chunks available",
                    f"{prompt_ready}/{len(self.prompt_bundles)} compiled prompt bundles are promotion-ready",
                ],
            ),
            LayerCoverage(
                layer_id="layer_4",
                name="Layer 4",
                description="Executable agents, MCP tools, simulations, and workflows",
                asset_count=executable_assets,
                coverage_score=max(0, min(100, 45 + executable_assets - max(0, authored_agents - registered_agents) * 8)),
                status="partial",
                notes=[
                    f"{authored_agents} authored agent files, {registered_agents} registered agents",
                    f"{len(self.mcp_tools())} MCP tools detected in the Susan server",
                ],
            ),
            LayerCoverage(
                layer_id="layer_5",
                name="Layer 5",
                description='Emotional connections, feeling data, and the "why" behind decisions',
                asset_count=emotional_assets,
                coverage_score=min(100, 15 + emotional_assets * 8),
                status="partial" if emotional_assets else "gap",
                notes=[
                    f"{len(list(self.experience_intelligence_dir.glob('*.md')))} experience-intelligence seed documents indexed",
                    f"{humanized_agents} agents have defined traits, habits, and debate protocols",
                    f"{research_topics}/{len(self.prompt_research_snapshot.topics)} prompt-research topics have harvested evidence",
                ],
            ),
        ]

    def agent_capabilities(self) -> list[AgentCapability]:
        registry_agents = self.agent_registry.get("agents", {})
        authored = {authoring_agent_id(path): path for path in self.authored_agent_files}
        capabilities: list[AgentCapability] = []
        seen_ids: set[str] = set()

        for agent_id, info in registry_agents.items():
            bundle = self.prompt_bundles_by_id.get(agent_id)
            required = info.get("rag_data_types", [])
            missing = [data_type for data_type in required if self.dataset_counts.get(data_type, 0) == 0]
            capabilities.append(
                AgentCapability(
                    id=agent_id,
                    name=info["name"],
                    role=info["role"],
                    group=info["group"],
                    authored=agent_id in authored,
                    registered=True,
                    prompt_status=bundle.status if bundle else "missing",
                    required_data_types=required,
                    missing_data_types=missing,
                    gap_count=len(missing) + (0 if bundle else 1),
                )
            )
            seen_ids.add(agent_id)

        for path in self.authored_agent_files:
            agent_id = authoring_agent_id(path)
            if agent_id in seen_ids:
                continue
            bundle = compile_prompt_bundle(path)
            capabilities.append(
                AgentCapability(
                    id=agent_id,
                    name=path.stem,
                    role="Unregistered research agent",
                    group="unregistered",
                    authored=True,
                    registered=False,
                    prompt_status=bundle.status,
                    required_data_types=[],
                    missing_data_types=[],
                    gap_count=1,
                )
            )

        return sorted(capabilities, key=lambda capability: (capability.gap_count, capability.id), reverse=True)

    def agent_profiles(self) -> list[AgentProfile]:
        registry_agents = self.agent_registry.get("agents", {})
        authored = {authoring_agent_id(path): path for path in self.authored_agent_files}
        profiles: list[AgentProfile] = []
        seen_ids: set[str] = set()

        for agent_id, info in registry_agents.items():
            characteristics = load_agent_characteristics(agent_id)
            required = info.get("rag_data_types", [])
            missing = [data_type for data_type in required if self.dataset_counts.get(data_type, 0) == 0]
            score = 25
            if characteristics.get("traits"):
                score += 20
            if characteristics.get("conversation_style"):
                score += 20
            if characteristics.get("debate_protocol"):
                score += 15
            if characteristics.get("uncertainty_protocol"):
                score += 10
            if characteristics.get("meeting_habits"):
                score += 10
            if "emotional_design" in required:
                score += 10
            if missing:
                score -= min(20, len(missing) * 5)
            profiles.append(
                AgentProfile(
                    id=agent_id,
                    name=info["name"],
                    role=info["role"],
                    group=info["group"],
                    authored=agent_id in authored,
                    registered=True,
                    traits=characteristics.get("traits", []),
                    conversation_style=characteristics.get("conversation_style"),
                    debate_protocol=characteristics.get("debate_protocol"),
                    uncertainty_protocol=characteristics.get("uncertainty_protocol"),
                    meeting_habits=characteristics.get("meeting_habits", []),
                    required_data_types=required,
                    missing_data_types=missing,
                    humanization_score=max(0, min(100, score)),
                )
            )
            seen_ids.add(agent_id)

        for path in self.authored_agent_files:
            agent_id = authoring_agent_id(path)
            if agent_id in seen_ids:
                continue
            characteristics = load_agent_characteristics(agent_id)
            profiles.append(
                AgentProfile(
                    id=agent_id,
                    name=path.stem,
                    role="Unregistered research agent",
                    group="unregistered",
                    authored=True,
                    registered=False,
                    traits=characteristics.get("traits", []),
                    conversation_style=characteristics.get("conversation_style"),
                    debate_protocol=characteristics.get("debate_protocol"),
                    uncertainty_protocol=characteristics.get("uncertainty_protocol"),
                    meeting_habits=characteristics.get("meeting_habits", []),
                    humanization_score=35 if characteristics else 10,
                )
            )
        return sorted(profiles, key=lambda profile: (profile.humanization_score, profile.id), reverse=True)

    def knowledge_gaps(self, tenant_id: str = "shared") -> list[CoverageGap]:
        gaps: list[CoverageGap] = []
        severity_for_zero = "critical"
        for capability in self.agent_capabilities():
            if capability.missing_data_types:
                gaps.append(
                    CoverageGap(
                        id=f"gap-{capability.id}-datasets",
                        gap_type="dataset",
                        severity=severity_for_zero,
                        title=f"{capability.name} lacks required data coverage",
                        detail=f"{capability.name} requires {', '.join(capability.missing_data_types)} but current dataset inventory has zero chunks for at least one required type.",
                        tenant_id=tenant_id,
                        owner=capability.id,
                        layer="layer_2",
                        evidence=[self.dataset_requirements_path.as_posix()],
                    )
                )
            if not capability.registered:
                gaps.append(
                    CoverageGap(
                        id=f"gap-{capability.id}-registration",
                        gap_type="registry",
                        severity="high",
                        title=f"{capability.id} exists in authoring but not in the registry",
                        detail="The authored agent file cannot be routed through the runtime registry until it is registered.",
                        tenant_id=tenant_id,
                        owner="susan",
                        layer="layer_4",
                        evidence=[str(self.agent_registry_path)],
                    )
                )

        stale_assets = self._stale_editorial_assets()
        if stale_assets:
            gaps.append(
                CoverageGap(
                    id="gap-stale-editorial-assets",
                    gap_type="freshness",
                    severity="warning",
                    title="Editorial corpus contains stale assets",
                    detail=f"{len(stale_assets)} editorial documents are outside their freshness window.",
                    tenant_id=tenant_id,
                    owner="researcher-web",
                    layer="layer_1",
                    evidence=stale_assets[:5],
                )
            )

        if self.dataset_counts.get("emotional_design", 0) == 0:
            gaps.append(
                CoverageGap(
                    id="gap-emotional-design-coverage",
                    gap_type="dataset",
                    severity="critical",
                    title="Emotional design layer has zero grounded knowledge chunks",
                    detail="The fifth layer is modeled, but the knowledge base currently has no indexed emotional-design chunks for motion narrative, moments of truth, organic layouts, or feeling-state signals.",
                    tenant_id=tenant_id,
                    owner="mira",
                    layer="layer_5",
                    evidence=[self.dataset_requirements_path.as_posix()],
                )
            )

        weak_profiles = [
            profile for profile in self.agent_profiles()
            if profile.registered and profile.humanization_score < 60
        ]
        if weak_profiles:
            gaps.append(
                CoverageGap(
                    id="gap-agent-humanization",
                    gap_type="agent_profile",
                    severity="high",
                    title="Some registered agents still read like tools instead of employees",
                    detail=f"{len(weak_profiles)} registered agents are missing traits, habits, or explicit debate and uncertainty protocols.",
                    tenant_id=tenant_id,
                    owner="susan",
                    layer="layer_5",
                    evidence=[str(self.backend_root / 'data' / 'agent_characteristics.yaml')],
                )
            )

        blocked_prompts = [bundle for bundle in self.prompt_bundles if bundle.status != "ready"]
        if blocked_prompts:
            gaps.append(
                CoverageGap(
                    id="gap-prompt-governance",
                    gap_type="prompt",
                    severity="high",
                    title="Prompt bundles are blocked from promotion",
                    detail=f"{len(blocked_prompts)} compiled prompt bundles fail schema, citation, or lint checks.",
                    tenant_id=tenant_id,
                    owner="nova",
                    layer="layer_3",
                    evidence=[bundle.source_paths[0] for bundle in blocked_prompts[:5]],
                )
            )

        if self.prompt_research_snapshot.total_hits == 0:
            gaps.append(
                CoverageGap(
                    id="gap-prompt-research-harvest",
                    gap_type="research",
                    severity="high",
                    title="Prompt and meta-prompt intelligence has not been harvested yet",
                    detail="The source manifest is defined, but there are no harvested Exa, Brave, or Firecrawl artifacts available for prompt trees, dialogue patterns, uncertainty handling, or emotional design.",
                    tenant_id=tenant_id,
                    owner="researcher-web",
                    layer="layer_3",
                    evidence=[str(self.prompt_source_manifest_path)],
                )
            )

        return sorted(gaps, key=self._gap_sort_key)

    def search_knowledge(
        self,
        query: str,
        tenant_id: str = "transformfit",
        top_k: int = 10,
        include_vector: bool = False,
    ) -> KnowledgeSearchResponse:
        lanes: list[LaneStatus] = []
        results: list[KnowledgeAsset] = []

        lexical_hits = self.hybrid_retriever.search(query, top_k=top_k)
        lexical_assets = [self._chunk_hit_to_asset(hit, lane="lexical") for hit in lexical_hits]
        lanes.append(LaneStatus(lane="lexical", enabled=True, detail="Local hybrid lexical retrieval over editorial chunks", result_count=len(lexical_assets)))
        results.extend(lexical_assets)

        structured_assets = self._search_documents(self.structured_documents, query, top_k, lane="structured")
        lanes.append(LaneStatus(lane="structured", enabled=True, detail="Normalized app and tenant records", result_count=len(structured_assets)))
        results.extend(structured_assets)

        protocol_assets = self._search_documents(self.protocol_documents + self.prompt_search_documents, query, top_k, lane="protocol")
        lanes.append(LaneStatus(lane="protocol", enabled=True, detail="Operational protocols, skills, and prompt bundles", result_count=len(protocol_assets)))
        results.extend(protocol_assets)

        research_assets = self._search_documents(self.research_documents, query, top_k, lane="research")
        lanes.append(
            LaneStatus(
                lane="research",
                enabled=bool(self.research_documents),
                detail="Harvested prompt, dialogue, and emotional-design research artifacts from Exa, Brave, and Firecrawl",
                result_count=len(research_assets),
            )
        )
        results.extend(research_assets)

        vector_assets: list[KnowledgeAsset] = []
        if include_vector and config.supabase_url and config.supabase_key and config.voyage_api_key:
            try:
                from rag_engine.retriever import Retriever

                retriever = Retriever()
                for hit in retriever.search(query=query, company_id="shared", top_k=min(top_k, 5)):
                    vector_assets.append(
                        KnowledgeAsset(
                            id=str(hit.get("id", "vector-hit")),
                            title=hit.get("data_type", "vector_hit"),
                            asset_type="knowledge_chunk",
                            lane="vector",
                            source=hit.get("source"),
                            source_path=hit.get("source_url"),
                            excerpt=hit.get("content", "")[:500],
                            freshness_status="unknown",
                            confidence=round(min(1.0, max(0.0, hit.get("similarity", 0.0))), 4),
                            metadata={"data_type": hit.get("data_type"), "similarity": hit.get("similarity")},
                        )
                    )
                lanes.append(LaneStatus(lane="vector", enabled=True, detail="Supabase pgvector semantic retrieval", result_count=len(vector_assets)))
                results.extend(vector_assets)
            except Exception as exc:
                lanes.append(LaneStatus(lane="vector", enabled=False, detail=f"Vector lane unavailable: {exc}", result_count=0))
        else:
            lanes.append(LaneStatus(lane="vector", enabled=False, detail="Enable with Supabase and Voyage credentials plus include_vector=true", result_count=0))

        deduped: dict[str, KnowledgeAsset] = {}
        for asset in sorted(results, key=lambda item: item.confidence, reverse=True):
            deduped.setdefault(asset.id, asset)

        ranked = list(deduped.values())[:top_k]
        return KnowledgeSearchResponse(query=query, tenant_id=tenant_id, lanes=lanes, results=ranked)

    def prompt_bundle(self, bundle_id: str) -> PromptBundle:
        bundle = self.prompt_bundles_by_id.get(bundle_id)
        if bundle is None:
            raise KeyError(bundle_id)
        return bundle

    def mcp_servers(self) -> list[MCPServer]:
        configured: dict = {}
        if self.mcp_config_path.exists():
            configured = json.loads(self.mcp_config_path.read_text(encoding="utf-8")).get("mcpServers", {})

        actual_tools = [tool for tool in self.mcp_tools() if tool.server_id == "susan-intelligence"]
        servers = [
            MCPServer(
                id="susan-intelligence",
                name="Susan Intelligence",
                transport="stdio",
                status="configured" if "susan-intelligence" in configured else "planned",
                health=file_exists_health(configured.get("susan-intelligence", {}).get("command")),
                scopes=["shared", "tenant"],
                tools_count=len(actual_tools),
                command=configured.get("susan-intelligence", {}).get("command"),
                dependent_workflows=["knowledge search", "simulation", "agent execution"],
            )
        ]

        planned_servers = [
            ("github", "GitHub", "planned", ["repo", "issues", "pull_requests"], ["backlog routing", "diff enrichment"]),
            ("supabase", "Supabase", "planned", ["tenant", "shared"], ["vector search", "run traces"]),
            ("filesystem", "Filesystem", "planned", ["workspace"], ["re-ingest source", "artifact inspection"]),
            ("web-research", "Web Research", "planned", ["shared"], ["freshness repair", "research ingestion"]),
            ("slack", "Slack", "planned", ["team"], ["incident alerts"]),
            ("linear", "Linear", "planned", ["team"], ["backlog sync"]),
            ("memory", "Memory", "planned", ["tenant"], ["long-running operator context"]),
        ]
        for server_id, name, status, scopes, workflows in planned_servers:
            servers.append(
                MCPServer(
                    id=server_id,
                    name=name,
                    transport="gateway",
                    status=status,
                    health="planned",
                    scopes=scopes,
                    tools_count=0,
                    dependent_workflows=workflows,
                )
            )
        return servers

    def mcp_tools(self) -> list[MCPTool]:
        tools: list[MCPTool] = []
        if self.mcp_server_path.exists():
            text = self.mcp_server_path.read_text(encoding="utf-8")
            pattern = re.compile(r"@mcp\.tool\(\)\s+def\s+(\w+)\(.*?\)\s*->\s*str:\s+\"\"\"([^\"]+?)\.\s", re.S)
            for name, description in pattern.findall(text):
                tools.append(
                    MCPTool(
                        id=f"mcp-tool-{name}",
                        server_id="susan-intelligence",
                        name=name,
                        description=description.strip(),
                        status="configured",
                        tenant_scoped="company_id" in text[text.find(f"def {name}"):text.find("\n\n", text.find(f"def {name}"))],
                    )
                )
        return tools

    def run_traces(self, tenant_id: str | None = None) -> list[RunTrace]:
        traces: list[RunTrace] = []
        companies_dir = self.backend_root / "companies"
        if companies_dir.exists():
            for output_dir in sorted(companies_dir.glob("*/susan-outputs")):
                company_id = output_dir.parent.name
                if tenant_id and company_id != tenant_id:
                    continue
                files = sorted(output_dir.glob("*"))
                if not files:
                    continue
                started = datetime.fromtimestamp(min(path.stat().st_mtime for path in files), tz=UTC)
                finished = datetime.fromtimestamp(max(path.stat().st_mtime for path in files), tz=UTC)
                traces.append(
                    RunTrace(
                        id=f"trace-{company_id}",
                        tenant_id=company_id,
                        kind="planning_session",
                        status="complete",
                        started_at=started,
                        finished_at=finished,
                        prompt_bundle_id="susan",
                        retrieval_lanes=["lexical", "structured", "protocol"],
                        model_route="claude-sonnet-4-6",
                        tool_names=["search_knowledge", "run_agent"],
                    )
                )
        return traces

    def routing_policies(self) -> list[RoutingPolicy]:
        return [
            RoutingPolicy(
                id="policy-central-default",
                name="Centralized default",
                mode="centralized",
                default_route="anthropic+supabase",
                allowed_workloads=["tenant analysis", "prompt compilation", "interactive operator queries"],
                provenance_required=False,
                description="Default policy for sensitive tenant intelligence and interactive work.",
            ),
            RoutingPolicy(
                id="policy-dai-offline",
                name="Pragmatic DAI offline",
                mode="hybrid",
                default_route="centralized",
                allowed_workloads=["public research backfills", "anonymous benchmarking", "offline eval workloads"],
                provenance_required=True,
                description="Use decentralized compute or storage only for approved, anonymized, offline workloads.",
            ),
        ]

    def reconciliation(self) -> ReconciliationReport:
        issues: list[ReconciliationIssue] = []

        authored_count = len(self.authored_agent_files)
        registered_count = len(self.agent_registry.get("agents", {}))
        if authored_count != registered_count:
            issues.append(
                make_issue(
                    issue_id="agent-registry-drift",
                    severity="high",
                    area="registry",
                    title="Agent registry does not match authored agents",
                    detail=f"{authored_count} authored agent files exist, but only {registered_count} agents are registered.",
                    recommendation="Register the missing researcher agents or remove stale authored files so runtime and docs agree.",
                    file_path=str(self.agent_registry_path),
                )
            )

        claude_text = self.claude_md_path.read_text(encoding="utf-8")
        claimed_agents = extract_numeric_claim(claude_text, r"Full Agent Roster \(([\d,]+) agents")
        if claimed_agents is None or claimed_agents != registered_count:
            detail = (
                "CLAUDE.md no longer publishes a machine-readable agent count."
                if claimed_agents is None
                else f"CLAUDE.md claims {claimed_agents} agents, but the runtime registry has {registered_count}."
            )
            issues.append(
                make_issue(
                    issue_id="claude-agent-count-stale",
                    severity="high",
                    area="documentation",
                    title="CLAUDE.md agent count is stale",
                    detail=detail,
                    recommendation="Update CLAUDE.md or align the runtime registry with the documented roster.",
                    file_path=str(self.claude_md_path),
                )
            )

        claimed_chunks = extract_numeric_claim(claude_text, r"Knowledge Base\s+—\s+([\d,]+) chunks")
        current_table_total = sum(self.dataset_counts.values())
        if claimed_chunks and current_table_total and claimed_chunks != current_table_total:
            issues.append(
                make_issue(
                    issue_id="knowledge-count-mismatch",
                    severity="warning",
                    area="documentation",
                    title="Knowledge base counts disagree across docs",
                    detail=f"CLAUDE.md claims {claimed_chunks} chunks, while dataset_requirements_master currently enumerates {current_table_total}.",
                    recommendation="Pick a single source of truth for chunk counts and update the stale doc.",
                    file_path=str(self.dataset_requirements_path),
                )
            )

        if self.inventory["total_markdown_files"] == 0:
            issues.append(
                make_issue(
                    issue_id="domain-ingestion-empty",
                    severity="critical",
                    area="ingestion",
                    title="Domain-pack ingestion resolved to zero markdown files",
                    detail="The merged domain pack is not being discovered by the corpus builder.",
                    recommendation="Point the corpus builder at the editorial subtree or auto-detect it from the domain root.",
                    file_path=str(self.domain_root),
                )
            )

        blocked_prompts = [bundle for bundle in self.prompt_bundles if bundle.status != "ready"]
        if blocked_prompts:
            issues.append(
                make_issue(
                    issue_id="prompt-governance-blocked",
                    severity="high",
                    area="prompts",
                    title="Compiled prompt bundles are blocked from promotion",
                    detail=f"{len(blocked_prompts)} prompt bundles currently fail schema, citation, or lint checks.",
                    recommendation="Add citations and richer eval coverage before using promotion as a runtime gate.",
                    file_path=blocked_prompts[0].source_paths[0],
                )
            )

        if self.dataset_counts.get("emotional_design", 0) == 0:
            issues.append(
                make_issue(
                    issue_id="emotional-design-empty",
                    severity="critical",
                    area="layer_5",
                    title="Emotional design dataset is still empty",
                    detail="The fifth-layer emotional-design category is tracked in the dataset requirements file, but there are zero grounded chunks in the current inventory.",
                    recommendation="Ingest experience-intelligence sources and harvest external emotional-design research before treating Layer 5 as production-ready.",
                    file_path=str(self.dataset_requirements_path),
                )
            )

        missing_profiles = [profile for profile in self.agent_profiles() if profile.registered and profile.humanization_score < 60]
        if missing_profiles:
            issues.append(
                make_issue(
                    issue_id="agent-humanization-gap",
                    severity="high",
                    area="agents",
                    title="Registered agent personas are incomplete",
                    detail=f"{len(missing_profiles)} registered agents are missing enough traits, conversation behaviors, or uncertainty protocols to feel like a real internal team.",
                    recommendation="Backfill agent characteristics and enforce debate and uncertainty sections for every core agent.",
                    file_path=str(self.backend_root / "data" / "agent_characteristics.yaml"),
                )
            )

        if self.prompt_research_snapshot.total_hits == 0:
            issues.append(
                make_issue(
                    issue_id="prompt-research-empty",
                    severity="high",
                    area="research",
                    title="Prompt-intelligence harvest has not produced artifacts yet",
                    detail="The research manifest exists, but there are no saved search hits or scraped pages for prompt trees, debate patterns, uncertainty handling, or emotional design.",
                    recommendation="Run the prompt-intelligence ingestion job and review gaps by topic in the cockpit before extending the prompt system further.",
                    file_path=str(self.prompt_source_manifest_path),
                )
            )

        stale_assets = self._stale_editorial_assets()
        if stale_assets:
            issues.append(
                make_issue(
                    issue_id="freshness-stale-assets",
                    severity="warning",
                    area="freshness",
                    title="Some editorial assets are stale",
                    detail=f"{len(stale_assets)} editorial files are outside their freshness window.",
                    recommendation="Prioritize a freshness sweep for pricing, app features, and market intelligence sources.",
                    file_path=stale_assets[0],
                )
            )

        backlog = sorted((issue_to_backlog(issue, tenant_id="transformfit") for issue in issues), key=lambda item: item.score, reverse=True)
        return ReconciliationReport(generated_at=datetime.now(UTC), issues=issues, backlog=backlog)

    def _gap_sort_key(self, gap: CoverageGap) -> tuple[int, str]:
        weights = {"critical": 0, "high": 1, "warning": 2, "info": 3}
        return (weights.get(gap.severity, 99), gap.title)

    def _health_score(self, tenant_id: str) -> int:
        gaps = self.knowledge_gaps(tenant_id)
        blocked_prompts = sum(1 for bundle in self.prompt_bundles if bundle.status != "ready")
        stale_assets = len(self._stale_editorial_assets())
        penalty = (
            sum({"critical": 12, "high": 8, "warning": 4, "info": 1}.get(gap.severity, 1) for gap in gaps)
            + blocked_prompts
            + int(stale_assets / 2)
        )
        return max(5, min(100, 100 - penalty))

    def _chunk_hit_to_asset(self, hit: dict, lane: str) -> KnowledgeAsset:
        freshness = None
        if hit.get("captured_at"):
            freshness = parse_fuzzy_date(hit["captured_at"])
        score = hit.get("score", 0.0)
        confidence = min(1.0, 0.2 + (score / 100.0))
        return KnowledgeAsset(
            id=hit["id"],
            title=hit.get("metadata", {}).get("title", hit["id"]),
            asset_type=hit.get("entity_type", "knowledge_chunk"),
            lane=lane,
            source=hit.get("source_type"),
            source_path=hit.get("source_path"),
            excerpt=hit["content"][:500],
            freshness_date=freshness,
            freshness_status="current" if freshness else "unknown",
            confidence=round(confidence, 4),
            metadata={"category": hit.get("category"), "entity_id": hit.get("entity_id")},
        )

    def _search_documents(self, documents: list[SearchDocument], query: str, top_k: int, lane: str) -> list[KnowledgeAsset]:
        terms = [term for term in re.findall(r"[a-z0-9]+", query.lower()) if len(term) > 1]
        scored: list[tuple[float, SearchDocument]] = []
        for document in documents:
            haystack = f"{document.title}\n{document.content}".lower()
            score = sum(haystack.count(term) for term in terms)
            if score <= 0:
                continue
            scored.append((float(score), document))
        results: list[KnowledgeAsset] = []
        for score, document in sorted(scored, key=lambda item: item[0], reverse=True)[:top_k]:
            confidence = min(1.0, 0.25 + score / 10.0)
            results.append(
                KnowledgeAsset(
                    id=document.id,
                    title=document.title,
                    asset_type=document.asset_type,
                    lane=lane,
                    source_path=document.source_path,
                    excerpt=document.content[:500],
                    freshness_date=document.freshness_date.date() if document.freshness_date else None,
                    freshness_status=document.freshness_status,
                    confidence=round(confidence, 4),
                    metadata=document.metadata or {},
                )
            )
        return results

    def _scrape_markdown(self, scrape_payload: dict) -> str:
        data = scrape_payload.get("data", scrape_payload)
        if isinstance(data, dict):
            markdown = data.get("markdown")
            if isinstance(markdown, str):
                return markdown
            if isinstance(markdown, dict):
                return json.dumps(markdown, ensure_ascii=True)
        return ""

    def _scrape_branding(self, scrape_payload: dict) -> str:
        data = scrape_payload.get("data", scrape_payload)
        branding = data.get("branding", {}) if isinstance(data, dict) else {}
        if not isinstance(branding, dict) or not branding:
            return ""
        parts: list[str] = []
        for key in ["brandName", "brandVoice", "tone", "summary"]:
            value = branding.get(key)
            if isinstance(value, str) and value.strip():
                parts.append(value.strip())
        if colors := branding.get("colors"):
            parts.append(json.dumps(colors, ensure_ascii=True))
        return "\n".join(parts)

    def _stale_editorial_assets(self) -> list[str]:
        stale_paths: list[str] = []
        for path in self.corpus_builder.markdown_files():
            profile = parse_markdown_profile(path)
            updated_at = parse_fuzzy_date(profile.metadata.get("Last Updated", "2026-03-03"))
            cadence = self._cadence_for_path(path)
            status = freshness_status(updated_at, cadence)
            if status == "stale":
                stale_paths.append(str(path))
        return stale_paths

    def _cadence_for_path(self, path: Path) -> str:
        normalized = path.name.lower()
        if "pricing" in normalized:
            return self.freshness_policy.get("pricing", "monthly")
        if "market" in normalized or "competitive" in normalized or "revenue" in normalized:
            return self.freshness_policy.get("market_reports", "semiannual")
        if "apps" in path.parts:
            return self.freshness_policy.get("app_features", "quarterly")
        return self.freshness_policy.get("market_reports", "semiannual")
