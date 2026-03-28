"""Oracle Health Director — Department orchestrator.

Routes work to the right super-agent, queries RAG for intelligence,
and produces department status reports.
"""
from __future__ import annotations
import json
from datetime import datetime, timedelta
from pathlib import Path

from oracle_health.schemas import (
    Competitor, Priority, Freshness, CompetitorFreshness,
    FreshnessReport, DepartmentStatus, CompetitiveSignal,
)

# Competitor metadata
COMPETITORS = {
    Competitor.EPIC: {"name": "Epic Systems", "priority": Priority.P0, "refresh_days": 7},
    Competitor.MICROSOFT: {"name": "Microsoft Health", "priority": Priority.P0, "refresh_days": 7},
    Competitor.AWS: {"name": "AWS HealthLake", "priority": Priority.P1, "refresh_days": 14},
    Competitor.GOOGLE: {"name": "Google Health", "priority": Priority.P1, "refresh_days": 14},
    Competitor.MEDITECH: {"name": "Meditech", "priority": Priority.P2, "refresh_days": 30},
    Competitor.VEEVA: {"name": "Veeva Systems", "priority": Priority.P2, "refresh_days": 30},
}

DATA_DIR = Path(__file__).parent.parent / "data" / "domains" / "oracle_health_intelligence"
BATTLECARD_DIR = DATA_DIR / "battlecards"
SIGNALS_DIR = DATA_DIR / "signals"


def _get_retriever():
    """Lazy import to avoid import errors when Supabase is unavailable."""
    try:
        from rag_engine.retriever import Retriever
        return Retriever()
    except Exception:
        return None


def freshness_check(days_old: int) -> Freshness:
    """Determine freshness status from age in days."""
    if days_old < 14:
        return Freshness.FRESH
    elif days_old < 30:
        return Freshness.AGING
    return Freshness.STALE


def get_competitor_freshness(competitor: Competitor) -> CompetitorFreshness:
    """Check RAG data freshness for a specific competitor."""
    retriever = _get_retriever()
    if not retriever:
        return CompetitorFreshness(
            competitor=competitor,
            freshness=Freshness.STALE,
            gaps=["RAG engine unavailable"],
        )

    # Query for competitor data — broad search, no type filter
    results = retriever.search(
        query=f"{COMPETITORS[competitor]['name']} competitive intelligence product strategy",
        company_id="oracle-health-ai-enablement",
        top_k=20,
    )

    if not results:
        return CompetitorFreshness(
            competitor=competitor,
            freshness=Freshness.STALE,
            gaps=[f"No RAG data found for {COMPETITORS[competitor]['name']}"],
        )

    # Analyze data types present
    data_types = set()
    for r in results:
        if r.get("data_type"):
            data_types.add(r["data_type"])

    # Get latest created_at via direct table query
    latest = None
    try:
        date_result = retriever.supabase.table("knowledge_chunks") \
            .select("created_at") \
            .eq("company_id", "oracle-health-ai-enablement") \
            .ilike("content", f"%{COMPETITORS[competitor]['name'].split()[0]}%") \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
        if date_result.data:
            latest_str = date_result.data[0].get("created_at", "")
            if latest_str:
                latest = datetime.fromisoformat(latest_str.replace("Z", "+00:00"))
    except Exception:
        pass

    days_old = (datetime.now(latest.tzinfo) - latest).days if latest else 999
    required_types = {"market_research", "competitive_signal", "studio_memory", "pricing_intel"}
    missing_types = required_types - data_types

    return CompetitorFreshness(
        competitor=competitor,
        latest_data=latest,
        chunk_count=len(results),
        freshness=freshness_check(days_old),
        data_types_present=sorted(data_types),
        gaps=[f"Missing data type: {t}" for t in sorted(missing_types)],
    )


def get_freshness_report() -> FreshnessReport:
    """Full freshness report across all competitors."""
    competitors = []
    total = 0
    for comp in Competitor:
        cf = get_competitor_freshness(comp)
        competitors.append(cf)
        total += cf.chunk_count

    fresh = sum(1 for c in competitors if c.freshness == Freshness.FRESH)
    aging = sum(1 for c in competitors if c.freshness == Freshness.AGING)
    stale = sum(1 for c in competitors if c.freshness == Freshness.STALE)

    if stale > 2:
        health = "CRITICAL — majority of competitor data is stale"
    elif aging > 2:
        health = "WARNING — multiple competitors aging"
    elif fresh >= 4:
        health = "HEALTHY — most competitor data is fresh"
    else:
        health = "FAIR — mixed freshness"

    return FreshnessReport(
        competitors=competitors,
        total_chunks=total,
        overall_health=health,
    )


def get_department_status() -> DepartmentStatus:
    """Get full Oracle Health department status."""
    report = get_freshness_report()

    fresh = sum(1 for c in report.competitors if c.freshness == Freshness.FRESH)
    aging = sum(1 for c in report.competitors if c.freshness == Freshness.AGING)
    stale = sum(1 for c in report.competitors if c.freshness == Freshness.STALE)

    # Check sentinel last run
    sentinel_status = DATA_DIR / "sentinel_status.yaml"
    last_sentinel = None
    if sentinel_status.exists():
        try:
            import yaml
            with open(sentinel_status) as f:
                data = yaml.safe_load(f)
                last_sentinel = data.get("last_run")
        except Exception:
            pass

    # Determine next actions
    actions = []
    for cf in report.competitors:
        if cf.freshness == Freshness.STALE:
            actions.append(f"URGENT: Refresh {COMPETITORS[cf.competitor]['name']} data — currently stale")
        elif cf.freshness == Freshness.AGING:
            actions.append(f"Schedule refresh for {COMPETITORS[cf.competitor]['name']} — data aging")
        for gap in cf.gaps:
            if "Missing data type" in gap:
                actions.append(f"Harvest {gap.split(': ')[1]} for {COMPETITORS[cf.competitor]['name']}")

    # Check battlecard directory
    BATTLECARD_DIR.mkdir(parents=True, exist_ok=True)
    battlecard_files = list(BATTLECARD_DIR.glob("*.md"))

    return DepartmentStatus(
        active_signals=0,  # TODO: count from signals dir
        battlecards_fresh=fresh,
        battlecards_aging=aging,
        battlecards_stale=stale,
        freshness_report=report,
        last_sentinel_run=last_sentinel,
        next_actions=actions[:10],  # Top 10 actions
    )


def search_competitor_intel(competitor: Competitor, query: str, top_k: int = 10) -> list[dict]:
    """Search RAG for competitor-specific intelligence."""
    retriever = _get_retriever()
    if not retriever:
        return []

    full_query = f"{COMPETITORS[competitor]['name']} {query}"
    return retriever.search(
        query=full_query,
        company_id="oracle-health-ai-enablement",
        top_k=top_k,
    )


def search_all_intel(query: str, top_k: int = 10) -> list[dict]:
    """Search RAG across all Oracle Health intelligence."""
    retriever = _get_retriever()
    if not retriever:
        return []

    return retriever.search(
        query=query,
        company_id="oracle-health-ai-enablement",
        top_k=top_k,
    )
