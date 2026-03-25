"""Dashboard API Server — V7 Visual Command Center

FastAPI server exposing PAI system status, agent metrics, memory health,
goals, pipelines, signals, and ratings for the React dashboard.

Endpoints:
  GET  /api/status       — System health
  GET  /api/companies    — All 3 companies with metrics
  GET  /api/agents       — Agent status and invocation stats
  GET  /api/memory       — Memory tier stats and health
  GET  /api/goals        — Active goals with progress
  GET  /api/pipelines    — Pipeline status
  GET  /api/signals      — Recent competitive signals
  GET  /api/ratings      — Satisfaction trend
  GET  /api/brief/today  — Today's morning brief
  GET  /api/actions/pending — Pending APPROVE-tier actions
  POST /api/actions/approve — Approve a pending action

Run: uvicorn pai.dashboard.api.server:app --port 8043
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from pai.dashboard.api.models import (
    SystemStatus, ServiceStatus,
    CompanySummary,
    AgentStatus,
    MemoryHealth, MemoryTierStats,
    GoalProgress,
    PipelineStatus,
    CompetitiveSignalSummary,
    RatingsTrend,
    TodayBrief,
    PendingAction, ActionApproval,
)

PAI_ROOT = Path(__file__).parent.parent.parent
STATE_DIR = PAI_ROOT / "MEMORY" / "STATE"
INTELLIGENCE_LOGS = PAI_ROOT / "intelligence" / "logs"

if HAS_FASTAPI:
    app = FastAPI(
        title="Jake PAI Dashboard API",
        description="Visual Command Center for the Personal AI Infrastructure",
        version="7.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Mobile-first: allow all origins
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app = None


def _read_jsonl(path: Path, days: int | None = 30, limit: int = 100) -> list[dict]:
    """Read entries from a JSONL file."""
    if not path.exists():
        return []
    cutoff = None
    if days:
        cutoff = datetime.now(timezone.utc).timestamp() - (days * 86400)
    entries = []
    with open(path) as f:
        for line in f:
            try:
                entry = json.loads(line)
                if cutoff:
                    ts_str = entry.get("timestamp", entry.get("ts", entry.get("detected_at", "")))
                    if ts_str:
                        ts = datetime.fromisoformat(ts_str)
                        if ts.timestamp() < cutoff:
                            continue
                entries.append(entry)
            except (json.JSONDecodeError, ValueError):
                continue
    return entries[-limit:]


if HAS_FASTAPI:

    @app.get("/api/status", response_model=SystemStatus)
    async def get_status():
        """System health overview."""
        services = []

        # Check key services
        for name, check_file in [
            ("Morning Brief", STATE_DIR / "ratings.jsonl"),
            ("SCOUT", INTELLIGENCE_LOGS / "competitive-signals.jsonl"),
            ("Priority Engine", INTELLIGENCE_LOGS / "priority-engine.jsonl"),
            ("Consolidation", STATE_DIR / "consolidation.jsonl"),
        ]:
            if check_file.exists():
                services.append(ServiceStatus(name=name, status="healthy"))
            else:
                services.append(ServiceStatus(name=name, status="unknown"))

        channels = []
        context_file = PAI_ROOT / "MEMORY" / "STATE" / "cross-channel-context.jsonl"
        if context_file.exists():
            entries = _read_jsonl(context_file, days=1)
            channels = list(set(e.get("channel", "") for e in entries if e.get("channel")))

        healthy = sum(1 for s in services if s.status == "healthy")
        overall = "healthy" if healthy == len(services) else "degraded" if healthy > 0 else "down"

        return SystemStatus(
            overall=overall,
            services=services,
            active_channels=channels,
        )

    @app.get("/api/companies", response_model=list[CompanySummary])
    async def get_companies():
        """All 3 companies with key metrics."""
        return [
            CompanySummary(id="startup-intelligence-os", name="Startup Intelligence OS", agent_count=218, rag_chunks=6693),
            CompanySummary(id="oracle-health", name="Oracle Health", agent_count=15, rag_chunks=2100),
            CompanySummary(id="alex-recruiting", name="Alex Recruiting", agent_count=10, rag_chunks=500),
        ]

    @app.get("/api/agents", response_model=list[AgentStatus])
    async def get_agents():
        """Agent status from intent router logs."""
        log = _read_jsonl(INTELLIGENCE_LOGS / "intent-classifications.jsonl", days=30)
        agent_stats: dict[str, dict] = {}
        for entry in log:
            agent = entry.get("agent")
            if agent:
                if agent not in agent_stats:
                    agent_stats[agent] = {"count": 0, "name": agent}
                agent_stats[agent]["count"] += 1

        return [
            AgentStatus(name=s["name"], invocation_count=s["count"], status="active" if s["count"] > 0 else "idle")
            for s in sorted(agent_stats.values(), key=lambda x: x["count"], reverse=True)
        ]

    @app.get("/api/memory", response_model=MemoryHealth)
    async def get_memory():
        """Memory tier stats and health."""
        consolidation = _read_jsonl(STATE_DIR / "consolidation.jsonl", days=30)
        corrections = _read_jsonl(STATE_DIR / "corrections.jsonl", days=30)
        ratings = _read_jsonl(STATE_DIR / "ratings.jsonl", days=None)

        return MemoryHealth(
            tiers=[
                MemoryTierStats(tier="episodic", record_count=len(ratings), health="healthy" if ratings else "empty"),
                MemoryTierStats(tier="semantic", record_count=len(corrections), health="healthy" if corrections else "empty"),
                MemoryTierStats(tier="wisdom", record_count=0, health="building"),
            ],
            consolidation_runs_30d=len(consolidation),
            corrections_30d=len(corrections),
            total_records=len(ratings) + len(corrections),
        )

    @app.get("/api/pipelines", response_model=list[PipelineStatus])
    async def get_pipelines():
        """Pipeline status."""
        return [
            PipelineStatus(name="morning_brief", schedule="0 7 * * *", status="scheduled"),
            PipelineStatus(name="email_triage", schedule="0 7 * * *", status="scheduled"),
            PipelineStatus(name="scout_scan", schedule="0 5 * * *", status="scheduled"),
            PipelineStatus(name="nightly_consolidation", schedule="0 2 * * *", status="scheduled"),
            PipelineStatus(name="weekly_synthesis", schedule="0 10 * * 0", status="scheduled"),
        ]

    @app.get("/api/signals", response_model=list[CompetitiveSignalSummary])
    async def get_signals():
        """Recent competitive signals."""
        raw = _read_jsonl(INTELLIGENCE_LOGS / "competitive-signals.jsonl", days=7)
        return [
            CompetitiveSignalSummary(
                title=s.get("title", ""),
                company=s.get("company", ""),
                competitor=s.get("competitor", ""),
                priority=s.get("priority", "P2"),
                category=s.get("category", ""),
            )
            for s in raw
        ]

    @app.get("/api/ratings", response_model=RatingsTrend)
    async def get_ratings():
        """Satisfaction trend."""
        ratings = _read_jsonl(STATE_DIR / "ratings.jsonl", days=30)
        if not ratings:
            return RatingsTrend(period="30d")

        scores = [r.get("rating", 3) for r in ratings]
        avg = sum(scores) / len(scores)
        return RatingsTrend(
            period="30d",
            count=len(scores),
            average=round(avg, 2),
            positive_count=sum(1 for s in scores if s >= 4),
            negative_count=sum(1 for s in scores if s <= 2),
        )

    @app.get("/api/brief/today", response_model=TodayBrief)
    async def get_today_brief():
        """Today's morning brief."""
        return TodayBrief(
            date=datetime.now().strftime("%A, %B %d %Y"),
            one_thing="Run the V4-V10 build pipeline",
        )
