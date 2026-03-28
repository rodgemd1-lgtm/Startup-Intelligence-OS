"""Susan Cloud Brain — FastAPI wrapper for the Susan backend.

Exposes Susan's orchestration, RAG, Oracle Health, memory, and research
capabilities over HTTP so Jake can reach Susan from any device.

Usage (local):
    uvicorn api:app --host 0.0.0.0 --port 8080

Usage (Fly.io):
    Deployed via Dockerfile — see fly.toml
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Ensure the backend directory is on sys.path so all modules can import
# ---------------------------------------------------------------------------
_BACKEND_DIR = Path(__file__).resolve().parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

# ---------------------------------------------------------------------------
# Version and metadata
# ---------------------------------------------------------------------------
VERSION = "0.1.0"
STARTED_AT = datetime.now().isoformat()

# ---------------------------------------------------------------------------
# Lazy / guarded imports — the app must start even if some deps are missing
# ---------------------------------------------------------------------------

# Susan config
try:
    from susan_core.config import config as susan_config
    _CONFIG_OK = True
except Exception:
    susan_config = None
    _CONFIG_OK = False

# Agent registry
try:
    from control_plane.foundry import _registry_agents, _companies
    _FOUNDRY_OK = True
except Exception:
    _FOUNDRY_OK = False

# RAG retriever
try:
    from rag_engine.retriever import Retriever
    _RAG_OK = True
except Exception:
    _RAG_OK = False

# Oracle Health
try:
    from oracle_health.director import (
        get_department_status,
        get_freshness_report,
        search_all_intel,
        COMPETITORS,
    )
    from oracle_health.battlecards import generate_battlecard
    from oracle_health.schemas import Competitor
    _ORACLE_OK = True
except Exception:
    _ORACLE_OK = False

# Memory system
try:
    from memory.tip_store import TipStore
    _MEMORY_TIPS_DIR = _BACKEND_DIR / "data" / "memory" / "tips"
    _MEMORY_OK = True
except Exception:
    _MEMORY_OK = False

# Research daemon
try:
    from research_daemon.gap_detector import GapDetector
    _RESEARCH_OK = True
except Exception:
    _RESEARCH_OK = False


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Susan Cloud Brain",
    description="Always-on API for Susan's agent orchestration, RAG, Oracle Health, memory, and research.",
    version=VERSION,
)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class RouteRequest(BaseModel):
    company: str
    task: str

class RAGQueryRequest(BaseModel):
    query: str
    company: str = "oracle-health-ai-enablement"
    top_k: int = Field(default=5, ge=1, le=50)

class GapDetectRequest(BaseModel):
    max_age_days: int = Field(default=30, ge=1, le=365)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _agent_groups() -> dict[str, list[dict[str, str]]]:
    """Build agent groups from the registry."""
    if not _FOUNDRY_OK:
        return {}
    agents = _registry_agents()
    groups: dict[str, list[dict[str, str]]] = {}
    for agent_id, meta in agents.items():
        group = meta.get("group", "ungrouped")
        groups.setdefault(group, []).append({
            "id": agent_id,
            "name": meta.get("name", agent_id),
            "role": meta.get("role", ""),
            "model": meta.get("model", ""),
        })
    return groups


def _agent_count() -> int:
    """Count total agents from the registry."""
    if not _FOUNDRY_OK:
        return 0
    return len(_registry_agents())


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    """Health check — returns status, version, module availability, agent count."""
    return {
        "status": "ok",
        "version": VERSION,
        "started_at": STARTED_AT,
        "agent_count": _agent_count(),
        "modules": {
            "config": _CONFIG_OK,
            "foundry": _FOUNDRY_OK,
            "rag": _RAG_OK,
            "oracle": _ORACLE_OK,
            "memory": _MEMORY_OK,
            "research": _RESEARCH_OK,
        },
    }


@app.get("/agents")
def list_agents():
    """List all agent groups and their agents."""
    if not _FOUNDRY_OK:
        raise HTTPException(status_code=503, detail="Agent registry unavailable — foundry module failed to load.")
    groups = _agent_groups()
    return {
        "total_agents": _agent_count(),
        "group_count": len(groups),
        "groups": groups,
    }


@app.post("/route")
def route_task(req: RouteRequest):
    """Route a task to Susan agents. Returns the suggested mode and relevant agents."""
    if not _FOUNDRY_OK:
        raise HTTPException(status_code=503, detail="Foundry module unavailable.")

    try:
        from control_plane.foundry import suggest_mode
        mode = suggest_mode(req.task)
    except Exception as e:
        mode = "full"

    # Find agents relevant to the task keywords
    agents = _registry_agents()
    task_lower = req.task.lower()
    relevant = []
    for agent_id, meta in agents.items():
        # Match on role, group, or data types
        role = (meta.get("role", "") or "").lower()
        group = (meta.get("group", "") or "").lower()
        data_types = " ".join(meta.get("rag_data_types", []))
        searchable = f"{role} {group} {data_types}"
        # Simple keyword overlap
        task_words = set(task_lower.split())
        match_count = sum(1 for w in task_words if w in searchable)
        if match_count > 0:
            relevant.append({
                "id": agent_id,
                "name": meta.get("name", agent_id),
                "role": meta.get("role", ""),
                "group": meta.get("group", ""),
                "match_score": match_count,
            })
    relevant.sort(key=lambda x: x["match_score"], reverse=True)

    # Check if company exists in registry
    companies = {}
    try:
        companies = _companies()
    except Exception:
        pass

    return {
        "company": req.company,
        "task": req.task,
        "suggested_mode": mode,
        "company_registered": req.company in companies,
        "relevant_agents": relevant[:10],
        "total_agents_available": len(agents),
    }


@app.post("/rag/query")
def rag_query(req: RAGQueryRequest):
    """Query the RAG knowledge base."""
    if not _RAG_OK:
        raise HTTPException(status_code=503, detail="RAG engine unavailable — check Supabase/Voyage credentials.")

    try:
        retriever = Retriever()
        results = retriever.search(
            query=req.query,
            company_id=req.company,
            top_k=req.top_k,
        )
        return {
            "query": req.query,
            "company": req.company,
            "result_count": len(results),
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")


@app.get("/oracle/status")
def oracle_status():
    """Get Oracle Health department status."""
    if not _ORACLE_OK:
        raise HTTPException(status_code=503, detail="Oracle Health module unavailable.")

    try:
        status = get_department_status()
        return status.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Oracle status failed: {str(e)}")


@app.get("/oracle/battlecard/{competitor}")
def oracle_battlecard(competitor: str):
    """Generate a battlecard for a specific competitor."""
    if not _ORACLE_OK:
        raise HTTPException(status_code=503, detail="Oracle Health module unavailable.")

    try:
        comp = Competitor(competitor.lower())
    except ValueError:
        valid = [c.value for c in Competitor]
        raise HTTPException(status_code=400, detail=f"Unknown competitor: {competitor}. Valid: {valid}")

    try:
        md = generate_battlecard(comp)
        return {
            "competitor": competitor,
            "format": "markdown",
            "battlecard": md,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Battlecard generation failed: {str(e)}")


@app.get("/oracle/freshness")
def oracle_freshness():
    """Get freshness report for all competitors."""
    if not _ORACLE_OK:
        raise HTTPException(status_code=503, detail="Oracle Health module unavailable.")

    try:
        report = get_freshness_report()
        return report.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Freshness report failed: {str(e)}")


@app.post("/research/gaps")
def detect_research_gaps(req: GapDetectRequest | None = None):
    """Detect knowledge gaps across capabilities and domains."""
    if not _RESEARCH_OK:
        raise HTTPException(status_code=503, detail="Research daemon module unavailable.")

    max_age = req.max_age_days if req else 30

    try:
        workspace_root = _BACKEND_DIR.parent.parent / ".startup-os"
        data_dir = _BACKEND_DIR / "data"
        detector = GapDetector(workspace_root=workspace_root, rag_data_dir=data_dir)

        coverage_gaps = detector.detect_gaps()
        stale_gaps = detector.detect_stale_data(max_age_days=max_age)

        all_gaps = coverage_gaps + stale_gaps
        prioritized = detector.prioritize_gaps(all_gaps)

        return {
            "total_gaps": len(prioritized),
            "coverage_gaps": len(coverage_gaps),
            "stale_gaps": len(stale_gaps),
            "gaps": [g.model_dump() for g in prioritized[:25]],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gap detection failed: {str(e)}")


@app.get("/memory/stats")
def memory_stats():
    """Get memory system statistics."""
    if not _MEMORY_OK:
        raise HTTPException(status_code=503, detail="Memory module unavailable.")

    try:
        store = TipStore(store_path=_MEMORY_TIPS_DIR)
        stats = store.get_stats()
        return stats.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory stats failed: {str(e)}")


@app.get("/cost/report")
def cost_report():
    """Cost tracking report — model pricing and configuration."""
    if not _CONFIG_OK:
        raise HTTPException(status_code=503, detail="Susan config unavailable.")

    return {
        "models": {
            "opus": {
                "model_id": susan_config.model_opus,
                "cost_per_m_input": susan_config.cost_per_m_input.get(susan_config.model_opus, 0),
                "cost_per_m_output": susan_config.cost_per_m_output.get(susan_config.model_opus, 0),
            },
            "sonnet": {
                "model_id": susan_config.model_sonnet,
                "cost_per_m_input": susan_config.cost_per_m_input.get(susan_config.model_sonnet, 0),
                "cost_per_m_output": susan_config.cost_per_m_output.get(susan_config.model_sonnet, 0),
            },
            "haiku": {
                "model_id": susan_config.model_haiku,
                "cost_per_m_input": susan_config.cost_per_m_input.get(susan_config.model_haiku, 0),
                "cost_per_m_output": susan_config.cost_per_m_output.get(susan_config.model_haiku, 0),
            },
        },
        "rag": {
            "embedding_model": susan_config.embedding_model,
            "embedding_dim": susan_config.embedding_dim,
            "chunk_size": susan_config.chunk_size,
            "top_k": susan_config.rag_top_k,
        },
        "generated_at": datetime.now().isoformat(),
    }
