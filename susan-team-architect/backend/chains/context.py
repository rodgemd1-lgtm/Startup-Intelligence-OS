"""Chain Context Bus — shared state passed between chain steps."""
from __future__ import annotations

from typing import Any


class ChainContext:
    """In-memory key-value store for passing data between chain steps.

    Each step writes its output under a named key. The next step reads
    the previous step's output by key. No file I/O between steps.
    """

    def __init__(self, chain_name: str = "", trigger_source: str = "") -> None:
        self.chain_name = chain_name
        self.trigger_source = trigger_source
        self._store: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def keys(self) -> list[str]:
        return list(self._store.keys())

    def to_dict(self) -> dict[str, Any]:
        return dict(self._store)
