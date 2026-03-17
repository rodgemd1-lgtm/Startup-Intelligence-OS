"""Layer 3 Graph-Native Memory Architecture for Startup Intelligence OS V10.0.

This package implements the TIMG (Trajectory-Insight-Memory-Graph) pipeline:

  Phase 1: TrajectoryExtractor  -- analyse completed runs, extract tips
  Phase 2: TipStore             -- persist and manage tips as YAML files
  Phase 3: TipRetriever         -- runtime retrieval of relevant tips
  Graph:   KnowledgeGraphBuilder -- construct knowledge graph from workspace YAML
  Consolidation: MemoryConsolidator -- Mem0-style memory maintenance

Usage:
    from memory.schemas import MemoryTip, Trajectory, MemoryQuery
    from memory.trajectory_extractor import TrajectoryExtractor
    from memory.tip_store import TipStore
    from memory.tip_retriever import TipRetriever
    from memory.graph_builder import KnowledgeGraphBuilder
    from memory.consolidator import MemoryConsolidator

CLI:
    python -m memory extract
    python -m memory consolidate
    python -m memory query "revenue growth simulation"
    python -m memory stats
    python -m memory graph
"""
from __future__ import annotations

from .consolidator import MemoryConsolidator
from .graph_builder import KnowledgeGraphBuilder
from .schemas import (
    GraphEdge,
    GraphNode,
    MemoryQuery,
    MemoryStats,
    MemoryTip,
    Trajectory,
    TrajectoryStep,
)
from .tip_retriever import TipRetriever
from .tip_store import TipStore
from .trajectory_extractor import TrajectoryExtractor

__all__ = [
    "GraphEdge",
    "GraphNode",
    "KnowledgeGraphBuilder",
    "MemoryConsolidator",
    "MemoryQuery",
    "MemoryStats",
    "MemoryTip",
    "TipRetriever",
    "TipStore",
    "Trajectory",
    "TrajectoryExtractor",
    "TrajectoryStep",
]
