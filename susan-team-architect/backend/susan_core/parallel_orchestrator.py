"""Phase DAG and parallel execution order for Susan orchestrator."""
from __future__ import annotations


# Phase dependency graph:
# 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> {8, 9} -> 10
PHASE_DEPS: dict[str, list[str]] = {
    "phase_1": [],
    "phase_2": ["phase_1"],
    "phase_3": ["phase_2"],
    "phase_4": ["phase_3"],
    "phase_5": ["phase_4"],
    "phase_6": ["phase_5"],
    "phase_7": ["phase_6"],
    "phase_8": ["phase_7"],
    "phase_9": ["phase_7"],
    "phase_10": ["phase_8", "phase_9"],
}


class PhaseDAG:
    """Directed acyclic graph of phase dependencies."""

    def __init__(self, deps: dict[str, list[str]] | None = None):
        self._deps = deps or PHASE_DEPS

    def dependencies(self, phase: str) -> list[str]:
        return self._deps.get(phase, [])

    def phases(self) -> list[str]:
        return list(self._deps.keys())

    def execution_order(self) -> list[str]:
        """Topological sort respecting dependencies."""
        visited: set[str] = set()
        order: list[str] = []

        def visit(phase: str) -> None:
            if phase in visited:
                return
            for dep in self.dependencies(phase):
                visit(dep)
            visited.add(phase)
            order.append(phase)

        for phase in self.phases():
            visit(phase)
        return order

    def parallel_groups(self) -> list[set[str]]:
        """Group phases into levels that can execute in parallel."""
        levels: dict[str, int] = {}

        def get_level(phase: str) -> int:
            if phase in levels:
                return levels[phase]
            deps = self.dependencies(phase)
            if not deps:
                levels[phase] = 0
                return 0
            level = max(get_level(d) for d in deps) + 1
            levels[phase] = level
            return level

        for phase in self.phases():
            get_level(phase)

        max_level = max(levels.values()) if levels else 0
        groups: list[set[str]] = [set() for _ in range(max_level + 1)]
        for phase, level in levels.items():
            groups[level].add(phase)
        return groups


def resolve_execution_order(dag: PhaseDAG) -> list[set[str]]:
    """Return phase groups in execution order, each group can run in parallel."""
    return dag.parallel_groups()
