"""Susan Intelligence MCP Server.

Exposes Susan's RAG knowledge base, agent system, Monte Carlo simulator,
and competitive intelligence to Claude Desktop and Claude Code via MCP.

Usage:
    python3 -m mcp_server.server
"""
from __future__ import annotations

import json
import yaml
from mcp.server.fastmcp import FastMCP

from control_plane.protocols import (
    get_company_foundry_blueprint,
    get_company_status,
    get_team_manifest,
    get_visual_assets,
    maybe_model_route,
    refresh_company_data,
    route_company_task,
    search_company_knowledge,
    sync_project_protocols,
)
from susan_core.config import config
from rag_engine.retriever import Retriever
from rag_engine.ingestion.web import WebIngestor

mcp = FastMCP("Susan Intelligence")

# Lazy singletons
_retriever: Retriever | None = None
_registry: dict | None = None


def _get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


def _get_registry() -> dict:
    global _registry
    if _registry is None:
        registry_path = config.data_dir / "agent_registry.yaml"
        with open(registry_path) as f:
            _registry = yaml.safe_load(f)
    return _registry


# ── Tool 1: search_knowledge ────────────────────────────────

@mcp.tool()
def search_knowledge(
    query: str,
    data_types: list[str] | None = None,
    top_k: int = 5,
    company_id: str = "shared",
) -> str:
    """Search Susan's RAG knowledge base (6,693+ chunks across 22 data types).

    Returns the most relevant knowledge chunks with content, source, and similarity score.

    Data types include: user_research, behavioral_economics, market_research,
    sleep_recovery, exercise_science, nutrition, growth_marketing, legal_compliance,
    ai_ml_research, sports_psychology, gamification, content_strategy, security,
    business_strategy, ux_research, finance, technical_docs, community, partnerships,
    expert_knowledge, operational_protocols.

    Args:
        query: Natural language search query
        data_types: Optional filter by data type(s)
        top_k: Number of results to return (default 5, max 20)
        company_id: Company namespace (default "shared")
    """
    top_k = min(top_k, 20)
    results = search_company_knowledge(
        query=query,
        company_id=company_id,
        data_types=data_types,
        top_k=top_k,
    )
    return json.dumps({"results": results, "total": len(results)}, indent=2)


# ── Tool 2: list_agents ─────────────────────────────────────

@mcp.tool()
def list_agents(group: str | None = None) -> str:
    """List Susan's AI agent roster with roles and specializations.

    Groups: orchestration, strategy, product, engineering, science, psychology, growth

    Args:
        group: Optional filter by group name
    """
    registry = _get_registry()
    agents = registry.get("agents", {})
    groups = registry.get("groups", {})

    if group:
        group_info = groups.get(group)
        if not group_info:
            return json.dumps({"error": f"Unknown group: {group}. Available: {list(groups.keys())}"})
        agent_ids = group_info.get("agents", [])
        filtered = {k: v for k, v in agents.items() if k in agent_ids}
    else:
        filtered = agents

    result = []
    for agent_id, info in filtered.items():
        result.append({
            "id": agent_id,
            "name": info["name"],
            "role": info["role"],
            "model": info["model"],
            "group": info["group"],
            "rag_data_types": info.get("rag_data_types", []),
        })

    return json.dumps({"agents": result, "total": len(result)}, indent=2)


# ── Tool 3: run_agent ───────────────────────────────────────

@mcp.tool()
def run_agent(
    agent_id: str,
    prompt: str,
    company_id: str = "shared",
) -> str:
    """Execute a Susan agent with RAG context. Returns agent response with cost tracking.

    The agent queries the knowledge base for relevant context, then responds using
    Claude with its specialized system prompt and behavioral economics lens.

    Args:
        agent_id: Agent identifier (e.g., "steve", "freya", "coach")
        prompt: The question or task for the agent
        company_id: Company namespace for RAG scoping
    """
    registry = _get_registry()
    agents = registry.get("agents", {})

    if agent_id not in agents:
        return json.dumps({"error": f"Unknown agent: {agent_id}. Available: {list(agents.keys())}"})

    from agents.base_agent import BaseAgent

    agent_info = agents[agent_id]

    # Create agent instance with registry config
    agent = BaseAgent(company_id=company_id)
    agent.agent_id = agent_id
    agent.agent_name = agent_info["name"]
    agent.role = agent_info["role"]
    agent.model = agent_info["model"]
    agent.rag_data_types = agent_info.get("rag_data_types", [])
    agent.system_prompt = (
        f"You are {agent_info['name']}, {agent_info['role']} at Apex Ventures. "
        f"You provide expert analysis grounded in the knowledge base context provided. "
        f"Be specific, data-driven, and actionable."
    )

    result = agent.run(prompt)
    return json.dumps({
        "agent": agent_id,
        "name": agent_info["name"],
        "role": agent_info["role"],
        "response": result["text"],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "cost_usd": result["cost_usd"],
        "duration_ms": result["duration_ms"],
    }, indent=2)


# ── Tool 4: run_simulation ──────────────────────────────────

@mcp.tool()
def run_simulation(
    cohort_size: int = 10000,
    months: int = 12,
    num_trials: int = 50,
    ai_personalization: float = 1.0,
    social_features: float = 1.0,
    gamification: float = 1.0,
    onboarding_quality: float = 1.0,
    pricing_optimization: float = 1.0,
) -> str:
    """Run Monte Carlo simulation for user cohort lifecycle.

    Simulates users through: Download → Onboarding → Activation → Retention → Conversion → Revenue.
    Uses 7 user personas calibrated against RevenueCat, Sensor Tower, and industry benchmarks.

    Feature impact modifiers: 1.0 = baseline, 1.2 = 20% improvement, 1.3 = 30% improvement.

    Args:
        cohort_size: Number of users to simulate (default 10,000)
        months: Simulation duration in months (default 12)
        num_trials: Number of Monte Carlo trials (default 50, max 200)
        ai_personalization: Impact modifier for AI features
        social_features: Impact modifier for social features
        gamification: Impact modifier for gamification
        onboarding_quality: Impact modifier for onboarding
        pricing_optimization: Impact modifier for pricing
    """
    num_trials = min(num_trials, 200)

    from simulations.monte_carlo import run_simulation as mc_run

    results = mc_run(
        cohort_size=cohort_size,
        months=months,
        num_trials=num_trials,
        onboarding_quality=onboarding_quality,
        ai_personalization=ai_personalization,
        social_features=social_features,
        gamification=gamification,
        pricing_optimization=pricing_optimization,
    )

    funnel = results.funnel_summary()
    persona_data = results.persona_breakdown()

    summary = {
        "cohort_size": cohort_size,
        "months": months,
        "num_trials": num_trials,
        "feature_impacts": {
            "ai_personalization": ai_personalization,
            "social_features": social_features,
            "gamification": gamification,
            "onboarding_quality": onboarding_quality,
            "pricing_optimization": pricing_optimization,
        },
        "funnel": {
            "onboarding_completion": funnel["onboarding_rate"],
            "day1_activation": funnel["day1_activation_rate"],
            "day7_retention": funnel["day7_retention_rate"],
            "day30_retention": funnel["day30_retention_rate"],
            "day90_retention": funnel["day90_retention_rate"],
            "paid_conversion": funnel["conversion_rate"],
        },
        "revenue": funnel["revenue"],
        "active_users_at_end": funnel["active_at_end"],
        "persona_breakdown": persona_data,
    }

    return json.dumps(summary, indent=2)


# ── Tool 5: get_competitor ──────────────────────────────────

@mcp.tool()
def get_competitor(name: str) -> str:
    """Get competitive intelligence for a fitness app.

    Available competitors: Fitbod, Noom, Strava, Peloton, MyFitnessPal, Hevy, Future.

    Args:
        name: Competitor name (case-insensitive, partial match supported)
    """
    from simulations.competitive_intel import COMPETITORS

    name_lower = name.lower()
    matches = [c for c in COMPETITORS if name_lower in c.name.lower()]

    if not matches:
        available = [c.name for c in COMPETITORS]
        return json.dumps({"error": f"No competitor found matching '{name}'. Available: {available}"})

    competitor = matches[0]
    profile = {
        "name": competitor.name,
        "category": competitor.category,
        "app_store_rating": competitor.app_store_rating,
        "total_ratings": competitor.total_ratings,
        "pricing": competitor.pricing,
        "revenue_estimate": competitor.revenue_estimate,
        "user_count": competitor.user_count,
        "key_features": competitor.key_features,
        "strengths": competitor.strengths,
        "weaknesses": competitor.weaknesses,
        "target_persona": competitor.target_persona,
        "onboarding_type": competitor.onboarding_type,
        "monetization": competitor.monetization,
        "founded": competitor.founded,
        "funding": competitor.funding,
    }

    return json.dumps(profile, indent=2)


# ── Tool 6: ingest_url ──────────────────────────────────────

@mcp.tool()
def ingest_url(
    url: str,
    data_type: str = "market_research",
    company_id: str = "shared",
) -> str:
    """Add web content to Susan's knowledge base by scraping and chunking a URL.

    Uses Firecrawl to scrape, then chunks and embeds into pgvector.

    Args:
        url: The URL to scrape and ingest
        data_type: Knowledge taxonomy category for the content
        company_id: Company namespace
    """
    try:
        ingestor = WebIngestor()
        count = ingestor.ingest(
            source=url,
            company_id=company_id,
            data_type=data_type,
        )
        return json.dumps({
            "url": url,
            "chunks_stored": count,
            "data_type": data_type,
            "company_id": company_id,
        })
    except Exception as e:
        return json.dumps({"error": str(e), "url": url})


# ── Tool 7: count_knowledge ─────────────────────────────────

@mcp.tool()
def count_knowledge(company_id: str | None = None) -> str:
    """Count total knowledge chunks in Susan's RAG, optionally filtered by company.

    Args:
        company_id: Optional company filter
    """
    retriever = _get_retriever()
    count = retriever.count_chunks(company_id)
    return json.dumps({"total_chunks": count, "company_id": company_id or "all"})


# ── Tool 8: route_task ──────────────────────────────────────

@mcp.tool()
def route_task(company_id: str, task: str) -> str:
    """Route a company task to the right Susan agents, data types, and next commands."""
    return json.dumps(route_company_task(company_id, task), indent=2)


# ── Tool 9: route_task_with_model ───────────────────────────

@mcp.tool()
def route_task_with_model(company_id: str, task: str) -> str:
    """Route a company task and optionally refine the plan with a Claude model."""
    return json.dumps(maybe_model_route(company_id, task), indent=2)


# ── Tool 10: company_status ─────────────────────────────────

@mcp.tool()
def company_status(company_id: str) -> str:
    """Return Susan corpus, asset, and output status for a company."""
    return json.dumps(get_company_status(company_id), indent=2)


# ── Tool 11: visual_assets ──────────────────────────────────

@mcp.tool()
def visual_assets(company_id: str, limit: int = 10) -> str:
    """List searchable visual assets stored for a company."""
    return json.dumps({"company_id": company_id, "assets": get_visual_assets(company_id, limit)}, indent=2)


# ── Tool 12: team_manifest ──────────────────────────────────

@mcp.tool()
def team_manifest(company_id: str) -> str:
    """Return the latest Susan team manifest for a company, if present."""
    return json.dumps(get_team_manifest(company_id), indent=2)


# ── Tool 13: foundry_blueprint ──────────────────────────────

@mcp.tool()
def foundry_blueprint(company_id: str) -> str:
    """Return Susan's execution blueprint and company foundry plan for a company."""
    return json.dumps(get_company_foundry_blueprint(company_id), indent=2)


# ── Tool 13: refresh_company ────────────────────────────────

@mcp.tool()
def refresh_company(company_id: str) -> str:
    """Refresh Susan data for a company."""
    return json.dumps(refresh_company_data(company_id), indent=2)


# ── Tool 15: sync_project_protocols ─────────────────────────

@mcp.tool()
def sync_protocols() -> str:
    """Push Susan commands, MCP config, hooks, skills, and agents into mapped project repos."""
    return json.dumps({"results": sync_project_protocols()}, indent=2)


# ── Tool 16: scrape_url ──────────────────────────────────────

@mcp.tool()
def scrape_url(
    url: str,
    tool: str = "firecrawl",
    data_type: str = "market_research",
    company_id: str = "transformfit",
) -> str:
    """Scrape a single URL and ingest into Susan's knowledge base.

    Args:
        url: The URL to scrape
        tool: Scraping tool to use -- "firecrawl" or "jina"
        data_type: Knowledge category (exercise_science, ux_research, etc.)
        company_id: Company namespace
    """
    if tool == "jina":
        from rag_engine.ingestion.jina_reader import JinaReaderIngestor
        ingestor = JinaReaderIngestor()
    else:
        ingestor = WebIngestor()

    count = ingestor.ingest(source=url, company_id=company_id, data_type=data_type)
    return json.dumps({"url": url, "tool": tool, "chunks_ingested": count})


# ── Tool 17: scrape_search ───────────────────────────────────

@mcp.tool()
def scrape_search(
    query: str,
    num_results: int = 10,
    data_type: str = "market_research",
    company_id: str = "transformfit",
) -> str:
    """Run Exa semantic search and ingest results into Susan's knowledge base.

    Finds thematically related content that keyword search would miss.

    Args:
        query: Natural language search query
        num_results: Number of results to discover and ingest
        data_type: Knowledge category
        company_id: Company namespace
    """
    from rag_engine.ingestion.exa_search import ExaSearchIngestor

    ingestor = ExaSearchIngestor()
    count = ingestor.ingest(
        source=query,
        company_id=company_id,
        data_type=data_type,
        num_results=num_results,
    )
    return json.dumps({"query": query, "num_results": num_results, "chunks_ingested": count})


# ── Tool 18: scrape_batch ────────────────────────────────────

@mcp.tool()
def scrape_batch(
    manifest_name: str,
    dry_run: bool = False,
    company_id: str = "transformfit",
) -> str:
    """Execute a batch scraping manifest from data/scrape_manifests/.

    Args:
        manifest_name: Manifest filename (e.g., "exercise_science.yaml")
        dry_run: If True, list sources without executing
        company_id: Company namespace
    """
    from rag_engine.batch import execute_manifest

    manifest_path = config.scrape_manifests_dir / manifest_name
    if not manifest_path.exists():
        return json.dumps({"error": f"Manifest not found: {manifest_name}"})

    result = execute_manifest(manifest_path, dry_run=dry_run)
    return json.dumps(result)


# ── Entry point ──────────────────────────────────────────────

def main():
    mcp.run()


if __name__ == "__main__":
    main()
