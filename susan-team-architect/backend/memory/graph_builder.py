"""Knowledge Graph Builder.

Constructs a typed knowledge graph from the .startup-os/ workspace YAML
contracts.  Nodes represent companies, projects, decisions, capabilities,
runs, and artifacts.  Edges capture relationships such as ``enables``,
``produced``, ``supports``, and ``requires``.

The graph supports BFS shortest-path queries, neighbour lookups, and
causal-chain tracing from any decision node back through its supporting
capabilities and upstream decisions.

Serialisation uses plain JSON so the graph can be consumed by downstream
tools without extra dependencies.
"""
from __future__ import annotations

import json
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml

from .schemas import GraphEdge, GraphNode, Trajectory


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe_load_yaml(path: Path) -> dict[str, Any] | None:
    """Load a YAML file, returning None on any error."""
    try:
        data = yaml.safe_load(path.read_text())
        return data if isinstance(data, dict) else None
    except Exception:
        return None


class KnowledgeGraphBuilder:
    """Builds and queries a knowledge graph from workspace YAML contracts."""

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self.nodes: list[GraphNode] = []
        self.edges: list[GraphEdge] = []
        # Lookup indices for fast queries
        self._node_index: dict[str, GraphNode] = {}
        self._adj: dict[str, list[tuple[str, GraphEdge]]] = {}  # node_id -> [(target_id, edge)]
        self._rev_adj: dict[str, list[tuple[str, GraphEdge]]] = {}  # node_id -> [(source_id, edge)]

    # ------------------------------------------------------------------
    # Index helpers
    # ------------------------------------------------------------------

    def _add_node(self, node: GraphNode) -> None:
        """Register a node in the graph and indices."""
        if node.id not in self._node_index:
            self.nodes.append(node)
            self._node_index[node.id] = node
            self._adj.setdefault(node.id, [])
            self._rev_adj.setdefault(node.id, [])

    def _add_edge(self, edge: GraphEdge) -> None:
        """Register an edge in the graph and indices."""
        self.edges.append(edge)
        self._adj.setdefault(edge.source_id, []).append((edge.target_id, edge))
        self._rev_adj.setdefault(edge.target_id, []).append((edge.source_id, edge))

    # ------------------------------------------------------------------
    # Build from workspace
    # ------------------------------------------------------------------

    def build_from_workspace(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        """Read all YAML contracts and construct the full knowledge graph.

        Returns (nodes, edges) tuple.
        """
        now = _iso_now()

        # --- Companies ---
        companies_dir = self.workspace_root / "companies"
        if companies_dir.exists():
            for p in sorted(companies_dir.glob("*.yaml")):
                data = _safe_load_yaml(p)
                if data is None or data.get("id") is None:
                    continue
                node = GraphNode(
                    id=data["id"],
                    node_type="company",
                    name=data.get("name", data["id"]),
                    properties={
                        k: v for k, v in data.items()
                        if k not in ("id", "name")
                    },
                    created_at=now,
                    updated_at=now,
                )
                self._add_node(node)

        # --- Projects ---
        projects_dir = self.workspace_root / "projects"
        if projects_dir.exists():
            for p in sorted(projects_dir.glob("*.yaml")):
                data = _safe_load_yaml(p)
                if data is None or data.get("id") is None:
                    continue
                node = GraphNode(
                    id=data["id"],
                    node_type="project",
                    name=data.get("name", data["id"]),
                    properties={
                        k: v for k, v in data.items()
                        if k not in ("id", "name")
                    },
                    created_at=now,
                    updated_at=now,
                )
                self._add_node(node)

                # Edge: project -> company
                company_id = data.get("company_id", "")
                if company_id and company_id in self._node_index:
                    self._add_edge(GraphEdge(
                        source_id=data["id"],
                        target_id=company_id,
                        relationship="supports",
                        weight=1.0,
                        evidence=f"project {data['id']} belongs to company {company_id}",
                        created_at=now,
                    ))

        # --- Decisions ---
        decisions_dir = self.workspace_root / "decisions"
        if decisions_dir.exists():
            for p in sorted(decisions_dir.glob("*.yaml")):
                data = _safe_load_yaml(p)
                if data is None or data.get("id") is None:
                    continue
                node = GraphNode(
                    id=data["id"],
                    node_type="decision",
                    name=data.get("title", data["id"]),
                    properties={
                        k: v for k, v in data.items()
                        if k not in ("id", "title")
                    },
                    created_at=data.get("created_at", now),
                    updated_at=data.get("updated_at", now),
                )
                self._add_node(node)

                # Edge: decision -> project
                project_id = data.get("project_id", "")
                if project_id and project_id in self._node_index:
                    self._add_edge(GraphEdge(
                        source_id=data["id"],
                        target_id=project_id,
                        relationship="supports",
                        weight=1.0,
                        evidence=f"decision {data['id']} under project {project_id}",
                        created_at=now,
                    ))

                # Edge: decision -> linked capabilities
                for cap_id in data.get("linked_capabilities") or []:
                    self._add_edge(GraphEdge(
                        source_id=data["id"],
                        target_id=cap_id,
                        relationship="enables",
                        weight=0.9,
                        evidence=f"decision {data['id']} enables capability {cap_id}",
                        created_at=now,
                    ))

                # Edge: decision -> run (if present)
                run_id = data.get("run_id", "")
                if run_id:
                    self._add_edge(GraphEdge(
                        source_id=data["id"],
                        target_id=run_id,
                        relationship="produced",
                        weight=0.8,
                        evidence=f"decision {data['id']} produced run {run_id}",
                        created_at=now,
                    ))

        # --- Capabilities ---
        capabilities_dir = self.workspace_root / "capabilities"
        if capabilities_dir.exists():
            for p in sorted(capabilities_dir.glob("*.yaml")):
                data = _safe_load_yaml(p)
                if data is None or data.get("id") is None:
                    continue
                # Skip profile files and README
                if data.get("id", "").endswith(".profile"):
                    continue
                node = GraphNode(
                    id=data["id"],
                    node_type="capability",
                    name=data.get("name", data["id"]),
                    properties={
                        k: v for k, v in data.items()
                        if k not in ("id", "name")
                    },
                    created_at=now,
                    updated_at=now,
                )
                self._add_node(node)

        # --- Artifacts (from index) ---
        artifacts_index = self.workspace_root / "artifacts" / "index.yaml"
        if artifacts_index.exists():
            data = _safe_load_yaml(artifacts_index)
            if data and "artifacts" in data:
                for art in data["artifacts"]:
                    art_id = art.get("id")
                    if not art_id:
                        continue
                    created_raw = art.get("created", now)
                    created_str = str(created_raw) if not isinstance(created_raw, str) else created_raw
                    node = GraphNode(
                        id=art_id,
                        node_type="artifact",
                        name=art_id,
                        properties={
                            k: str(v) if not isinstance(v, (str, int, float, bool, list, dict)) else v
                            for k, v in art.items()
                            if k != "id"
                        },
                        created_at=created_str,
                        updated_at=created_str,
                    )
                    self._add_node(node)

                    # Edge: artifact -> project
                    proj_id = art.get("project_id", "")
                    if proj_id and proj_id in self._node_index:
                        self._add_edge(GraphEdge(
                            source_id=art_id,
                            target_id=proj_id,
                            relationship="supports",
                            weight=0.7,
                            evidence=f"artifact {art_id} under project {proj_id}",
                            created_at=now,
                        ))

                    # Edge: artifact -> company
                    co_id = art.get("company_id", "")
                    if co_id and co_id in self._node_index:
                        self._add_edge(GraphEdge(
                            source_id=art_id,
                            target_id=co_id,
                            relationship="supports",
                            weight=0.5,
                            evidence=f"artifact {art_id} for company {co_id}",
                            created_at=now,
                        ))

        # --- Runs (from registry) ---
        runs_registry = self.workspace_root / "runs" / "registry.yaml"
        if runs_registry.exists():
            data = _safe_load_yaml(runs_registry)
            if data and "runs" in data:
                for run in data["runs"]:
                    run_id = run.get("id")
                    if not run_id:
                        continue
                    node = GraphNode(
                        id=run_id,
                        node_type="run",
                        name=run_id,
                        properties={
                            k: v for k, v in run.items()
                            if k != "id"
                        },
                        created_at=now,
                        updated_at=now,
                    )
                    self._add_node(node)

                    # Edge: run -> decision
                    dec_id = run.get("decision_id", "")
                    if dec_id and dec_id in self._node_index:
                        self._add_edge(GraphEdge(
                            source_id=run_id,
                            target_id=dec_id,
                            relationship="supports",
                            weight=0.8,
                            evidence=f"run {run_id} supports decision {dec_id}",
                            created_at=now,
                        ))

                    # Edge: run -> project
                    proj_id = run.get("project_id", "")
                    if proj_id and proj_id in self._node_index:
                        self._add_edge(GraphEdge(
                            source_id=run_id,
                            target_id=proj_id,
                            relationship="supports",
                            weight=0.6,
                            evidence=f"run {run_id} under project {proj_id}",
                            created_at=now,
                        ))

        return self.nodes, self.edges

    # ------------------------------------------------------------------
    # Add a run trajectory to the graph
    # ------------------------------------------------------------------

    def add_run_to_graph(
        self, trajectory: Trajectory,
    ) -> tuple[list[GraphNode], list[GraphEdge]]:
        """Add a completed run trajectory as a node with edges to its agent."""
        now = _iso_now()
        new_nodes: list[GraphNode] = []
        new_edges: list[GraphEdge] = []

        # Run node
        run_node = GraphNode(
            id=trajectory.run_id,
            node_type="run",
            name=f"run:{trajectory.agent_name}",
            properties={
                "outcome": trajectory.outcome,
                "total_tokens": trajectory.total_tokens,
                "total_duration_ms": trajectory.total_duration_ms,
                "quality_score": trajectory.quality_score,
                "step_count": len(trajectory.steps),
            },
            created_at=trajectory.created_at,
            updated_at=now,
        )
        self._add_node(run_node)
        new_nodes.append(run_node)

        # Agent node (idempotent)
        agent_id = f"agent-{trajectory.agent_name}"
        if agent_id not in self._node_index:
            agent_node = GraphNode(
                id=agent_id,
                node_type="agent",
                name=trajectory.agent_name,
                properties={},
                created_at=now,
                updated_at=now,
            )
            self._add_node(agent_node)
            new_nodes.append(agent_node)

        # Edge: run -> agent
        edge = GraphEdge(
            source_id=trajectory.run_id,
            target_id=agent_id,
            relationship="produced",
            weight=trajectory.quality_score or 0.5,
            evidence=f"run {trajectory.run_id} executed by agent {trajectory.agent_name}",
            created_at=now,
        )
        self._add_edge(edge)
        new_edges.append(edge)

        return new_nodes, new_edges

    # ------------------------------------------------------------------
    # Graph queries
    # ------------------------------------------------------------------

    def query_path(self, from_id: str, to_id: str) -> list[GraphEdge]:
        """BFS shortest path between two nodes.  Returns list of edges on the path."""
        if from_id not in self._node_index or to_id not in self._node_index:
            return []

        visited: set[str] = {from_id}
        queue: deque[tuple[str, list[GraphEdge]]] = deque([(from_id, [])])

        while queue:
            current, path = queue.popleft()
            if current == to_id:
                return path

            for neighbour_id, edge in self._adj.get(current, []):
                if neighbour_id not in visited:
                    visited.add(neighbour_id)
                    queue.append((neighbour_id, path + [edge]))

            # Also traverse reverse edges (undirected search)
            for neighbour_id, edge in self._rev_adj.get(current, []):
                if neighbour_id not in visited:
                    visited.add(neighbour_id)
                    queue.append((neighbour_id, path + [edge]))

        return []

    def query_neighbors(
        self,
        node_id: str,
        relationship: Optional[str] = None,
    ) -> list[GraphNode]:
        """Get nodes directly connected to the given node.

        Searches both outgoing and incoming edges.  Optionally filters by
        relationship type.
        """
        neighbour_ids: set[str] = set()

        for target_id, edge in self._adj.get(node_id, []):
            if relationship is None or edge.relationship == relationship:
                neighbour_ids.add(target_id)

        for source_id, edge in self._rev_adj.get(node_id, []):
            if relationship is None or edge.relationship == relationship:
                neighbour_ids.add(source_id)

        return [self._node_index[nid] for nid in neighbour_ids if nid in self._node_index]

    def get_causal_chain(
        self, decision_id: str,
    ) -> list[tuple[GraphNode, GraphEdge]]:
        """Trace the chain of decisions and capabilities that led to a decision.

        Walks backward through ``enables``, ``supports``, and ``requires``
        edges, collecting each (node, edge) pair in traversal order.
        """
        causal_rels = {"enables", "supports", "requires"}
        chain: list[tuple[GraphNode, GraphEdge]] = []
        visited: set[str] = set()
        queue: deque[str] = deque([decision_id])

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            for source_id, edge in self._rev_adj.get(current, []):
                if edge.relationship in causal_rels:
                    node = self._node_index.get(source_id)
                    if node:
                        chain.append((node, edge))
                        queue.append(source_id)

        return chain

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def save_graph(self, path: Path) -> None:
        """Serialize the full graph to a JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "nodes": [n.model_dump() for n in self.nodes],
            "edges": [e.model_dump() for e in self.edges],
        }
        path.write_text(json.dumps(payload, indent=2, default=str))

    def load_graph(self, path: Path) -> None:
        """Deserialize a graph from a JSON file, replacing current state."""
        if not path.exists():
            raise FileNotFoundError(f"Graph file not found: {path}")

        raw = json.loads(path.read_text())

        # Reset state
        self.nodes.clear()
        self.edges.clear()
        self._node_index.clear()
        self._adj.clear()
        self._rev_adj.clear()

        for nd in raw.get("nodes", []):
            node = GraphNode(**nd)
            self._add_node(node)

        for ed in raw.get("edges", []):
            edge = GraphEdge(**ed)
            self._add_edge(edge)
