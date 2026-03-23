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
from susan_core.production_engine import ProductionEngine
from susan_core.production_store import ProductionStore
from rag_engine.retriever import Retriever
from rag_engine.ingestion.web import WebIngestor

mcp = FastMCP("Susan Intelligence")

# Lazy singletons
_retriever: Retriever | None = None
_registry: dict | None = None
_production_engine: ProductionEngine | None = None


def _get_production_engine() -> ProductionEngine:
    global _production_engine
    if _production_engine is None:
        store = None
        try:
            from susan_core.config import config as _cfg
            if _cfg.supabase_url and _cfg.supabase_key:
                from supabase import create_client
                _sb = create_client(_cfg.supabase_url, _cfg.supabase_key)
                store = ProductionStore(_sb)
        except Exception:
            pass  # Supabase unavailable — use in-memory only
        _production_engine = ProductionEngine(store=store)
    return _production_engine


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
    tool: str = "jina",
    data_type: str = "market_research",
    company_id: str = "transformfit",
) -> str:
    """Scrape a single URL and ingest into Susan's knowledge base.

    Args:
        url: The URL to scrape
        tool: Scraping tool to use -- "jina" (default, direct) or "firecrawl" (requires credits)
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


# ── Tool 19: start_production ──────────────────────────────────

@mcp.tool()
def start_production(
    brief: str,
    company_id: str,
    format: str,
    title: str | None = None,
) -> str:
    """Start a new film/image production.

    Initializes a production lifecycle (design → storyboard → generation → refinement → delivered).

    Args:
        brief: Description of what to produce
        company_id: Company namespace (e.g., "transformfit", "founder-intelligence-os")
        format: Production format — film, reel, photo, series, carousel, brand-film, documentary
        title: Optional production title
    """
    engine = _get_production_engine()
    prod = engine.start(brief=brief, company_id=company_id, format=format, title=title)
    return json.dumps({
        "production_id": prod.production_id,
        "brief": prod.brief,
        "company_id": prod.company_id,
        "format": prod.format,
        "phase": prod.status.value,
    }, indent=2)


# ── Tool 20: production_status ────────────────────────────────

@mcp.tool()
def production_status(production_id: str) -> str:
    """Get the current status of a production.

    Returns phase, assigned agents, and outputs.

    Args:
        production_id: The production ID returned by start_production
    """
    engine = _get_production_engine()
    try:
        status = engine.get_status(production_id)
        return json.dumps(status, indent=2)
    except KeyError:
        return json.dumps({"error": f"Production not found: {production_id}"})


# ── Tool 21: list_productions ─────────────────────────────────

@mcp.tool()
def list_productions(
    company_id: str,
    status_filter: str | None = None,
) -> str:
    """List all productions for a company.

    Args:
        company_id: Company namespace
        status_filter: Optional phase filter (design, storyboard, generation, refinement, delivered)
    """
    engine = _get_production_engine()
    prods = engine.list_productions(company_id)
    results = []
    for p in prods:
        if status_filter and p.status.value != status_filter:
            continue
        results.append({
            "production_id": p.production_id,
            "brief": p.brief,
            "format": p.format,
            "phase": p.status.value,
            "agents_count": len(p.agents_assigned),
            "outputs_count": len(p.outputs),
        })
    return json.dumps({"company_id": company_id, "productions": results, "total": len(results)}, indent=2)


# ── Tool 22: run_studio_agent ─────────────────────────────────

@mcp.tool()
def run_studio_agent(
    agent_id: str,
    prompt: str,
    production_id: str | None = None,
    company_id: str = "shared",
) -> str:
    """Execute a studio agent with RAG context and optional production binding.

    Routes to any of the 18 film studio agents (creative direction, generation engines).

    Args:
        agent_id: Studio agent ID (e.g., "film-studio-director", "image-gen-engine")
        prompt: The task or question for the agent
        production_id: Optional production ID to bind context
        company_id: Company namespace for RAG scoping
    """
    registry = _get_registry()
    agents = registry.get("agents", {})

    if agent_id not in agents:
        return json.dumps({"error": f"Unknown agent: {agent_id}. Available: {list(agents.keys())}"})

    from agents.base_agent import BaseAgent

    agent_info = agents[agent_id]
    agent = BaseAgent(company_id=company_id)
    agent.agent_id = agent_id
    agent.agent_name = agent_info["name"]
    agent.role = agent_info["role"]
    agent.model = agent_info["model"]
    agent.rag_data_types = agent_info.get("rag_data_types", [])

    # Enrich prompt with production context if bound
    enriched_prompt = prompt
    if production_id:
        engine = _get_production_engine()
        try:
            status = engine.get_status(production_id)
            enriched_prompt = (
                f"[Production Context: {status['brief']} | Phase: {status['phase']} | "
                f"Format: {status['format']} | Company: {status['company_id']}]\n\n{prompt}"
            )
        except KeyError:
            pass

    agent.system_prompt = (
        f"You are {agent_info['name']}, {agent_info['role']}. "
        f"You provide expert analysis grounded in the knowledge base context provided. "
        f"Be specific, data-driven, and actionable."
    )

    result = agent.run(enriched_prompt)
    return json.dumps({
        "agent": agent_id,
        "name": agent_info["name"],
        "production_id": production_id,
        "response": result["text"],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "cost_usd": result["cost_usd"],
    }, indent=2)


# ── Tool 23: generate_shot_list ───────────────────────────────

@mcp.tool()
def generate_shot_list(
    script_or_brief: str,
    format: str = "film",
    style_reference: str | None = None,
) -> str:
    """Generate a structured shot list from a script or brief.

    Uses cinematography and production management knowledge to create
    a detailed shot list with tool assignments per shot.

    Args:
        script_or_brief: The script text or production brief
        format: Production format (film, reel, photo, carousel)
        style_reference: Optional style/mood reference description
    """
    retriever = _get_retriever()

    # Gather relevant cinematography knowledge
    context_chunks = retriever.search(
        query=f"shot list cinematography {format} {style_reference or ''}",
        data_types=["cinematography", "film_production"],
        top_k=5,
    )
    context = "\n".join([c["content"] for c in context_chunks]) if context_chunks else ""

    return json.dumps({
        "format": format,
        "style_reference": style_reference,
        "brief": script_or_brief[:200],
        "rag_context_chunks": len(context_chunks) if context_chunks else 0,
        "instruction": (
            "Use film-studio-director and cinematography-studio agents to generate "
            "a full shot list. Route each shot to the optimal generation engine tool."
        ),
        "context_preview": context[:500] if context else "No RAG context found — run scrape manifests first.",
    }, indent=2)


# ── Tool 24: generate_content_calendar ────────────────────────

@mcp.tool()
def generate_content_calendar(
    company_id: str,
    month: str,
    content_pillars: list[str] | None = None,
    posts_per_week: int = 4,
) -> str:
    """Generate a monthly Instagram content calendar.

    Uses instagram-studio agent knowledge for hook optimization,
    content pillar mapping, and batch production scheduling.

    Args:
        company_id: Company namespace
        month: Target month (e.g., "2026-04")
        content_pillars: Optional content pillar categories
        posts_per_week: Target posts per week (default 4)
    """
    retriever = _get_retriever()

    context_chunks = retriever.search(
        query="Instagram content calendar planning content pillars Reels strategy",
        data_types=["instagram_production", "content_strategy"],
        top_k=5,
    )
    context = "\n".join([c["content"] for c in context_chunks]) if context_chunks else ""

    return json.dumps({
        "company_id": company_id,
        "month": month,
        "content_pillars": content_pillars or ["educational", "behind-the-scenes", "social-proof", "promotional"],
        "posts_per_week": posts_per_week,
        "rag_context_chunks": len(context_chunks) if context_chunks else 0,
        "instruction": (
            "Use instagram-studio agent to create a full monthly calendar with "
            "hook concepts, content types, and batch production schedule."
        ),
        "context_preview": context[:500] if context else "No RAG context found — run scrape manifests first.",
    }, indent=2)


# ── Tool 25: review_production ────────────────────────────────

@mcp.tool()
def review_production(
    production_id: str,
    review_type: str = "quality",
) -> str:
    """Run a review on a production.

    Review types: quality (technical quality gates), legal (rights clearance),
    technical (format specs and delivery requirements).

    Args:
        production_id: The production ID to review
        review_type: Type of review — quality, legal, or technical
    """
    engine = _get_production_engine()
    try:
        status = engine.get_status(production_id)
    except KeyError:
        return json.dumps({"error": f"Production not found: {production_id}"})

    review_agents = {
        "quality": "film-studio-director",
        "legal": "legal-rights-studio",
        "technical": "distribution-studio",
    }

    agent_id = review_agents.get(review_type, "film-studio-director")

    return json.dumps({
        "production_id": production_id,
        "review_type": review_type,
        "reviewing_agent": agent_id,
        "production_phase": status["phase"],
        "production_format": status["format"],
        "agents_assigned": status["agents_assigned"],
        "outputs_count": len(status["outputs"]),
        "instruction": (
            f"Use {agent_id} to run a {review_type} review on this production. "
            f"Check all relevant quality gates and compliance requirements."
        ),
    }, indent=2)


# ── Tool 26: route_to_engine ──────────────────────────────────

@mcp.tool()
def route_to_engine(
    task_description: str,
    format: str = "image",
    requirements: str | None = None,
) -> str:
    """Route a generation task to the optimal AI tool.

    Evaluates requirements against the image, film, and audio engine
    tool capability maps and recommends the best tool(s).

    Args:
        task_description: What needs to be generated
        format: Target format — image, video, audio, voice, music, sfx
        requirements: Specific requirements (resolution, duration, style, etc.)
    """
    engine_map = {
        "image": "image-gen-engine",
        "video": "film-gen-engine",
        "film": "film-gen-engine",
        "audio": "audio-gen-engine",
        "voice": "audio-gen-engine",
        "music": "audio-gen-engine",
        "sfx": "audio-gen-engine",
    }

    engine_id = engine_map.get(format, "image-gen-engine")

    retriever = _get_retriever()
    data_type_map = {
        "image-gen-engine": "ai_image_tools",
        "film-gen-engine": "ai_video_tools",
        "audio-gen-engine": "ai_audio_tools",
    }

    context_chunks = retriever.search(
        query=f"{task_description} {requirements or ''}",
        data_types=[data_type_map.get(engine_id, "ai_image_tools")],
        top_k=5,
    )
    context = "\n".join([c["content"] for c in context_chunks]) if context_chunks else ""

    return json.dumps({
        "task": task_description,
        "format": format,
        "requirements": requirements,
        "routed_engine": engine_id,
        "rag_context_chunks": len(context_chunks) if context_chunks else 0,
        "instruction": (
            f"Use {engine_id} agent to select the optimal tool for this task. "
            f"Apply routing logic and quality gates from the engine's capability map."
        ),
        "context_preview": context[:500] if context else "No RAG context found — run scrape manifests first.",
    }, indent=2)


# ── Tool 27: design_session ───────────────────────────────────

@mcp.tool()
def design_session(
    brief: str,
    company_id: str,
    style_preferences: str | None = None,
) -> str:
    """Start an interactive design session for a production.

    Phase 1 of the production process: explores look & feel with references,
    builds mood boards, and locks visual language.

    Args:
        brief: What the production is about
        company_id: Company namespace
        style_preferences: Optional style direction (e.g., "cinematic dark", "bright minimal")
    """
    retriever = _get_retriever()

    context_chunks = retriever.search(
        query=f"design session mood board visual language {style_preferences or ''} {brief}",
        data_types=["cinematography", "ai_image_tools", "photography"],
        top_k=5,
    )
    context = "\n".join([c["content"] for c in context_chunks]) if context_chunks else ""

    return json.dumps({
        "session_type": "design",
        "brief": brief,
        "company_id": company_id,
        "style_preferences": style_preferences,
        "rag_context_chunks": len(context_chunks) if context_chunks else 0,
        "workflow": [
            "1. Brief intake — purpose, audience, tone, references",
            "2. Reference gathering — Image Gen Engine generates 20-30 style references",
            "3. Look & feel lock — Cinematography Studio defines visual language",
            "4. Brand system generation — character refs, environment refs, typography",
        ],
        "agents_needed": [
            "film-studio-director",
            "cinematography-studio",
            "image-gen-engine",
            "production-designer-studio",
        ],
        "context_preview": context[:500] if context else "No RAG context found — run scrape manifests first.",
    }, indent=2)


# ── Tool 28: generate_storyboard ──────────────────────────────

@mcp.tool()
def generate_storyboard(
    script_or_brief: str,
    num_shots: int = 12,
    format: str = "film",
    style: str | None = None,
) -> str:
    """Generate a structured storyboard with shot descriptions and tool assignments.

    Phase 2 of the production process: creates visual storyboard from script/brief.

    Args:
        script_or_brief: Script text or production brief
        num_shots: Target number of shots (default 12)
        format: Production format (film, reel, carousel)
        style: Visual style reference
    """
    retriever = _get_retriever()

    context_chunks = retriever.search(
        query=f"storyboard creation shot description visual storytelling {format}",
        data_types=["screenwriting", "cinematography", "film_production"],
        top_k=5,
    )
    context = "\n".join([c["content"] for c in context_chunks]) if context_chunks else ""

    return json.dumps({
        "session_type": "storyboard",
        "brief": script_or_brief[:200],
        "num_shots": num_shots,
        "format": format,
        "style": style,
        "rag_context_chunks": len(context_chunks) if context_chunks else 0,
        "workflow": [
            "1. Script/narrative — Screenwriter Studio produces beat sheet + scene breakdown",
            "2. Visual storyboard — Image Gen Engine generates frame per shot",
            "3. Animatic (optional) — Film Gen Engine creates rough motion test",
            "4. Production plan — Production Manager generates shot list with tool assignments",
        ],
        "agents_needed": [
            "screenwriter-studio",
            "cinematography-studio",
            "image-gen-engine",
            "production-manager-studio",
        ],
        "context_preview": context[:500] if context else "No RAG context found — run scrape manifests first.",
    }, indent=2)


# ── Tool 29: orchestrate_production ──────────────────────────

@mcp.tool()
def orchestrate_production(production_id: str) -> str:
    """Auto-assign agents for the current production phase.

    Uses the AI-directed agent roster to assign the right specialists
    based on production format and current phase.

    Args:
        production_id: The production ID to orchestrate
    """
    engine = _get_production_engine()
    try:
        result = engine.orchestrate(production_id)
        return json.dumps(result, indent=2)
    except KeyError:
        return json.dumps({"error": f"Production not found: {production_id}"})


# ── Tool 30: auto_run_production ─────────────────────────────

@mcp.tool()
def auto_run_production(production_id: str) -> str:
    """Fully autonomous production run through all phases.

    Advances through design → storyboard → generation → refinement,
    auto-assigning agents at each phase. Stops at refinement
    (quality gates must be satisfied before delivery).

    Args:
        production_id: The production ID to auto-run
    """
    engine = _get_production_engine()
    try:
        steps = engine.auto_run(production_id)
        return json.dumps({"production_id": production_id, "steps": steps}, indent=2)
    except KeyError:
        return json.dumps({"error": f"Production not found: {production_id}"})


# ── Tool 31: advance_production ──────────────────────────────

@mcp.tool()
def advance_production(production_id: str, force: bool = False) -> str:
    """Advance production to the next phase.

    Quality gates are enforced on refinement → delivered transition.
    Use force=True to bypass quality gates (not recommended).

    Args:
        production_id: The production ID to advance
        force: Bypass quality gate enforcement (default False)
    """
    engine = _get_production_engine()
    try:
        new_status = engine.advance_phase(production_id, force=force)
        return json.dumps({
            "production_id": production_id,
            "new_phase": new_status.value,
        }, indent=2)
    except KeyError:
        return json.dumps({"error": f"Production not found: {production_id}"})
    except Exception as e:
        return json.dumps({"error": str(e), "production_id": production_id})


# ── Tool 32: run_quality_gate ────────────────────────────────

@mcp.tool()
def run_quality_gate(
    production_id: str,
    gate_name: str,
    score: float,
    details: str = "",
) -> str:
    """Record a quality gate result for a production.

    Score (0.0-1.0) is compared against the gate's threshold.
    All gates must pass before delivery.

    Args:
        production_id: The production ID
        gate_name: Gate name (e.g., physics_plausibility, hook_impact, resolution)
        score: Quality score between 0.0 and 1.0
        details: Optional details about the assessment
    """
    engine = _get_production_engine()
    try:
        result = engine.run_quality_gate(production_id, gate_name, score, details)
        return json.dumps({
            "gate_name": result.gate_name,
            "passed": result.passed,
            "score": result.score,
            "details": result.details,
        }, indent=2)
    except (KeyError, ValueError) as e:
        return json.dumps({"error": str(e)})


# ── Tool 33: route_generation_task ───────────────────────────

@mcp.tool()
def route_generation_task(task_type: str) -> str:
    """Route a generation task to the optimal AI tool.

    28 task types across image, video, and audio engines.
    Examples: photorealistic, dialogue_scene, music_orchestral.

    Args:
        task_type: Task type key (e.g., 'photorealistic', 'dialogue_scene', 'voice_dialogue')
    """
    engine = _get_production_engine()
    result = engine.route_to_tool(task_type)
    return json.dumps(result, indent=2)


# ── Tool 34: production_legal_clearance ──────────────────────

@mcp.tool()
def production_legal_clearance(
    production_id: str,
    asset_name: str,
    clearance_type: str,
    status: str = "pending",
    notes: str = "",
) -> str:
    """Add or update a legal clearance record for a production asset.

    7 clearance types: copyright, trademark, likeness, music_sync,
    music_master, talent_consent, ai_disclosure.
    4 statuses: pending, cleared, blocked, waived.

    Args:
        production_id: The production ID
        asset_name: Name of the asset requiring clearance
        clearance_type: Type of clearance needed
        status: Clearance status (default: pending)
        notes: Additional context
    """
    engine = _get_production_engine()
    try:
        result = engine.add_legal_clearance(
            production_id, asset_name, clearance_type, status, notes
        )
        return json.dumps(result, indent=2)
    except (KeyError, ValueError) as e:
        return json.dumps({"error": str(e)})


# ── Entry point ──────────────────────────────────────────────

def main():
    mcp.run()


if __name__ == "__main__":
    main()
