# tests/test_retrieval_upgrades.py
"""Tests for retrieval stack upgrades: cache, prefilter, async batch writer."""
import pytest
import time
from rag_engine.cache import QueryCache
from rag_engine.prefilter import PrefilterSpec, apply_prefilter_sql
from rag_engine.async_writer import AsyncBatchWriter


def test_cache_hit():
    cache = QueryCache(ttl_seconds=60)
    cache.put("query1", "company1", ["type1"], [{"content": "result"}])
    result = cache.get("query1", "company1", ["type1"])
    assert result is not None
    assert result[0]["content"] == "result"


def test_cache_miss():
    cache = QueryCache(ttl_seconds=60)
    assert cache.get("missing", "c", []) is None


def test_cache_ttl_expiry():
    cache = QueryCache(ttl_seconds=0.1)
    cache.put("q", "c", [], [{"content": "r"}])
    time.sleep(0.15)
    assert cache.get("q", "c", []) is None


def test_cache_invalidate():
    cache = QueryCache(ttl_seconds=60)
    cache.put("q", "c", ["t"], [{"content": "r"}])
    cache.invalidate(company_id="c")
    assert cache.get("q", "c", ["t"]) is None


def test_cache_invalidate_scoped():
    """Invalidating one company_id must not evict another company's entries."""
    cache = QueryCache(ttl_seconds=60)
    cache.put("q1", "alpha", ["t"], [{"content": "alpha-result"}])
    cache.put("q2", "beta", ["t"], [{"content": "beta-result"}])
    cache.put("q3", "alpha", ["t2"], [{"content": "alpha-result-2"}])

    evicted = cache.invalidate(company_id="alpha")
    assert evicted == 2  # only the two alpha entries

    # beta entry must survive
    result = cache.get("q2", "beta", ["t"])
    assert result is not None
    assert result[0]["content"] == "beta-result"

    # alpha entries must be gone
    assert cache.get("q1", "alpha", ["t"]) is None
    assert cache.get("q3", "alpha", ["t2"]) is None


def test_cache_invalidate_all():
    """Passing company_id=None must clear everything (backward compat)."""
    cache = QueryCache(ttl_seconds=60)
    cache.put("q1", "alpha", ["t"], [{"content": "a"}])
    cache.put("q2", "beta", ["t"], [{"content": "b"}])

    evicted = cache.invalidate(company_id=None)
    assert evicted == 2
    assert cache.get("q1", "alpha", ["t"]) is None
    assert cache.get("q2", "beta", ["t"]) is None


def test_cache_stats():
    cache = QueryCache(ttl_seconds=60)
    cache.put("q", "c", [], [{"content": "r"}])
    cache.get("q", "c", [])  # hit
    cache.get("miss", "c", [])  # miss
    stats = cache.stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1


def test_prefilter_spec():
    spec = PrefilterSpec(
        company_id="transformfit",
        data_types=["exercise_science", "growth_marketing"],
        keywords=["retention", "churn"],
    )
    sql_parts = apply_prefilter_sql(spec)
    assert "company_id" in sql_parts
    assert "data_type" in sql_parts


def test_async_writer_batching():
    """Test that the writer accumulates chunks and flushes at batch size."""
    written = []

    def mock_store(chunks):
        written.extend(chunks)
        return len(chunks)

    writer = AsyncBatchWriter(store_fn=mock_store, batch_size=3, flush_interval=10.0)
    writer.add({"content": "a"})
    writer.add({"content": "b"})
    assert len(written) == 0  # not yet flushed
    writer.add({"content": "c"})  # triggers batch
    writer.flush()  # ensure flush
    assert len(written) == 3


def test_async_writer_flush():
    written = []

    def mock_store(chunks):
        written.extend(chunks)
        return len(chunks)

    writer = AsyncBatchWriter(store_fn=mock_store, batch_size=100, flush_interval=10.0)
    writer.add({"content": "x"})
    writer.flush()
    assert len(written) == 1
