# rag_engine/cache.py
"""Query result cache with TTL and invalidation."""
from __future__ import annotations

import hashlib
import json
import time
from threading import Lock
from typing import Any


class QueryCache:
    """In-memory query result cache with TTL.

    Avoids redundant vector searches by caching results keyed on
    (query, company_id, data_types).  Supports per-company invalidation
    and reports hit/miss statistics.
    """

    def __init__(self, ttl_seconds: float = 300.0, max_entries: int = 1000):
        self._lock = Lock()
        self._cache: dict[str, tuple[float, str, list[dict]]] = {}
        self._ttl = ttl_seconds
        self._max_entries = max_entries
        self._hits = 0
        self._misses = 0

    # ------------------------------------------------------------------
    # Key generation
    # ------------------------------------------------------------------

    def _key(self, query: str, company_id: str, data_types: list[str] | None) -> str:
        raw = json.dumps(
            {"q": query, "c": company_id, "t": sorted(data_types or [])},
            sort_keys=True,
        )
        return hashlib.sha256(raw.encode()).hexdigest()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, query: str, company_id: str, data_types: list[str] | None) -> list[dict] | None:
        """Return cached results or ``None`` on miss / expiry."""
        key = self._key(query, company_id, data_types)
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return None
            ts, _cid, results = entry
            if time.time() - ts > self._ttl:
                del self._cache[key]
                self._misses += 1
                return None
            self._hits += 1
            return results

    def put(
        self,
        query: str,
        company_id: str,
        data_types: list[str] | None,
        results: list[dict],
    ) -> None:
        """Store *results* under the composite key, evicting oldest if full."""
        key = self._key(query, company_id, data_types)
        with self._lock:
            if len(self._cache) >= self._max_entries:
                oldest_key = min(self._cache, key=lambda k: self._cache[k][0])
                del self._cache[oldest_key]
            self._cache[key] = (time.time(), company_id, results)

    def invalidate(self, company_id: str | None = None) -> int:
        """Drop cached entries.

        If *company_id* is given, only entries for that company are
        removed.  Passing ``None`` clears the entire cache.
        """
        with self._lock:
            if company_id is None:
                count = len(self._cache)
                self._cache.clear()
                return count
            keys_to_drop = [
                k for k, (_, cid, _) in self._cache.items() if cid == company_id
            ]
            for k in keys_to_drop:
                del self._cache[k]
            return len(keys_to_drop)

    def stats(self) -> dict:
        """Return cache statistics."""
        with self._lock:
            return {
                "size": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": self._hits / max(1, self._hits + self._misses),
            }
