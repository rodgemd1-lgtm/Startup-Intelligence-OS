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

    # All three filter keys should be present
    assert "company_id" in sql_parts
    assert "data_type" in sql_parts
    assert "keywords" in sql_parts

    # Each value is a (sql_template, params) tuple
    cid_sql, cid_params = sql_parts["company_id"]
    assert "%s" in cid_sql
    assert cid_params == ["transformfit"]
    assert "transformfit" not in cid_sql  # value must NOT be interpolated

    dt_sql, dt_params = sql_parts["data_type"]
    assert "%s" in dt_sql
    assert dt_params == [["exercise_science", "growth_marketing"]]

    kw_sql, kw_params = sql_parts["keywords"]
    assert kw_sql.count("%s") == 2  # one placeholder per keyword
    assert kw_params == ["%retention%", "%churn%"]


def test_prefilter_no_injection():
    """Malicious input must end up in the params list, never in the SQL string."""
    malicious = "'; DROP TABLE --"
    spec = PrefilterSpec(
        company_id=malicious,
        data_types=[malicious],
        keywords=[malicious],
    )
    sql_parts = apply_prefilter_sql(spec)

    for key, (sql_template, params) in sql_parts.items():
        # The raw malicious string must never appear in the SQL template
        assert malicious not in sql_template, (
            f"SQL injection possible in '{key}': malicious value found in SQL template"
        )
        # It must be safely captured in the params list
        if key == "company_id":
            assert params == [malicious]
        elif key == "data_type":
            assert params == [[malicious]]
        elif key == "keywords":
            assert params == [f"%{malicious}%"]


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
