"""Jake's Cognitive Memory Engine — 4-layer brain with knowledge graph.

Phase 2: Core engine (store, retriever, pipeline, extractor, graph, consolidator)
Phase 4: SPINE (priority, context, intent_router)
"""
from jake_brain.config import BrainConfig

__all__ = [
    # Phase 2 — Core
    "BrainConfig",
    # Phase 4 — SPINE (lazy import to avoid circular deps)
    # from jake_brain.priority import PriorityEngine, PrioritySignal
    # from jake_brain.context import ContextAssembler, ContextBundle
    # from jake_brain.intent_router import IntentRouter, RoutingDecision
]
