# tests/test_embedder.py
import os
import pytest
from rag_engine.embedder import Embedder

@pytest.fixture
def embedder():
    if not os.environ.get("VOYAGE_API_KEY"):
        pytest.skip("VOYAGE_API_KEY not set")
    return Embedder()

def test_embed_single_text(embedder):
    result = embedder.embed(["Hello world"])
    assert len(result) == 1
    assert len(result[0]) == 1024  # voyage-3 output dim

def test_embed_batch(embedder):
    texts = ["First text", "Second text", "Third text"]
    result = embedder.embed(texts)
    assert len(result) == 3
    assert all(len(v) == 1024 for v in result)

def test_embed_empty_raises():
    embedder = Embedder.__new__(Embedder)
    with pytest.raises(ValueError):
        embedder.embed([])
