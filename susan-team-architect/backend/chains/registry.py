"""Chain Registry — stores and retrieves chain definitions."""
from __future__ import annotations

from chains.schemas import ChainDef


class ChainRegistry:
    def __init__(self) -> None:
        self._chains: dict[str, ChainDef] = {}

    def register(self, chain: ChainDef) -> None:
        self._chains[chain.name] = chain

    def get(self, name: str) -> ChainDef:
        if name not in self._chains:
            raise KeyError(f"Chain '{name}' not found. Available: {list(self._chains.keys())}")
        return self._chains[name]

    def list_names(self) -> list[str]:
        return list(self._chains.keys())
