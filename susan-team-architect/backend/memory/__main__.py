"""CLI entry point for the Layer 3 Graph-Native Memory Architecture.

Usage:
    python -m memory extract          Extract tips from all run trajectories
    python -m memory consolidate      Run memory consolidation cycle
    python -m memory query <text>     Query memory for relevant tips
    python -m memory stats            Print memory statistics
    python -m memory graph            Build and save knowledge graph

Must be invoked from the susan-team-architect/backend/ directory, or with
PYTHONPATH set so that the ``memory`` package is importable.
"""
from __future__ import annotations

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve standard paths relative to the backend directory
# ---------------------------------------------------------------------------

# This module lives at susan-team-architect/backend/memory/__main__.py
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_REPO_ROOT = _BACKEND_DIR.parent.parent

_RUNS_DIR = _REPO_ROOT / "apps" / "decision_os" / "data" / "runs"
_TIPS_DIR = _BACKEND_DIR / "data" / "memory" / "tips"
_GRAPH_DIR = _BACKEND_DIR / "data" / "memory" / "graph"
_WORKSPACE_ROOT = _REPO_ROOT / ".startup-os"


def cmd_extract() -> None:
    """Extract tips from all run trajectories."""
    from .trajectory_extractor import TrajectoryExtractor
    from .tip_store import TipStore

    extractor = TrajectoryExtractor(runs_dir=_RUNS_DIR)
    store = TipStore(store_path=_TIPS_DIR)

    print(f"Loading trajectories from {_RUNS_DIR} ...")
    trajectories = extractor.load_trajectories()
    print(f"  Found {len(trajectories)} trajectories.")

    all_tips = []
    for traj in trajectories:
        tips = extractor.extract_tips(traj)
        all_tips.extend(tips)

    print(f"  Extracted {len(all_tips)} tips.")

    saved = 0
    for tip in all_tips:
        store.save_tip(tip)
        saved += 1

    print(f"  Saved {saved} tips to {_TIPS_DIR}")


def cmd_consolidate() -> None:
    """Run memory consolidation cycle."""
    from .consolidator import MemoryConsolidator
    from .graph_builder import KnowledgeGraphBuilder
    from .tip_store import TipStore

    store = TipStore(store_path=_TIPS_DIR)
    graph = KnowledgeGraphBuilder(workspace_root=_WORKSPACE_ROOT)

    consolidator = MemoryConsolidator(tip_store=store, graph_builder=graph)

    print("Running consolidation ...")
    stats = consolidator.consolidate()

    for k, v in stats.items():
        print(f"  {k}: {v}")

    print()
    print(consolidator.generate_summary())


def cmd_query(text: str) -> None:
    """Query memory for relevant tips."""
    from .schemas import MemoryQuery
    from .tip_retriever import TipRetriever
    from .tip_store import TipStore

    store = TipStore(store_path=_TIPS_DIR)
    retriever = TipRetriever(store=store)

    query = MemoryQuery(query_text=text, max_results=5, min_confidence=0.3)
    tips = retriever.retrieve(query)

    if not tips:
        print("No relevant tips found.")
        return

    print(retriever.format_for_injection(tips))


def cmd_stats() -> None:
    """Print memory statistics."""
    from .tip_store import TipStore

    store = TipStore(store_path=_TIPS_DIR)
    stats = store.get_stats()

    print("Memory Stats")
    print(f"  Total tips:       {stats.total_tips}")
    print(f"  Avg confidence:   {stats.avg_confidence:.2f}")
    print(f"  Tips by type:")
    for t, c in sorted(stats.tips_by_type.items()):
        print(f"    {t}: {c}")
    print(f"  Tips by domain:")
    for d, c in sorted(stats.tips_by_domain.items()):
        print(f"    {d}: {c}")


def cmd_graph() -> None:
    """Build and save knowledge graph."""
    from .graph_builder import KnowledgeGraphBuilder
    from .trajectory_extractor import TrajectoryExtractor

    print(f"Building graph from workspace at {_WORKSPACE_ROOT} ...")
    builder = KnowledgeGraphBuilder(workspace_root=_WORKSPACE_ROOT)
    nodes, edges = builder.build_from_workspace()
    print(f"  Workspace: {len(nodes)} nodes, {len(edges)} edges")

    # Also add run trajectories
    extractor = TrajectoryExtractor(runs_dir=_RUNS_DIR)
    trajectories = extractor.load_trajectories()
    for traj in trajectories:
        new_nodes, new_edges = builder.add_run_to_graph(traj)
        nodes.extend(new_nodes)
        edges.extend(new_edges)

    print(f"  After trajectories: {len(builder.nodes)} nodes, {len(builder.edges)} edges")

    graph_path = _GRAPH_DIR / "knowledge_graph.json"
    builder.save_graph(graph_path)
    print(f"  Saved graph to {graph_path}")


def main() -> None:
    """Parse CLI arguments and dispatch to the appropriate command."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "extract":
        cmd_extract()
    elif command == "consolidate":
        cmd_consolidate()
    elif command == "query":
        if len(sys.argv) < 3:
            print("Usage: python -m memory query <text>")
            sys.exit(1)
        text = " ".join(sys.argv[2:])
        cmd_query(text)
    elif command == "stats":
        cmd_stats()
    elif command == "graph":
        cmd_graph()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
