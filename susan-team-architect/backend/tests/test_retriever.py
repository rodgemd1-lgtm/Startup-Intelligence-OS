# tests/test_retriever.py
import os
import pytest
from rag_engine.retriever import Retriever
from susan_core.schemas import KnowledgeChunk

@pytest.fixture
def retriever():
    required = ["VOYAGE_API_KEY", "SUPABASE_URL", "SUPABASE_SERVICE_KEY"]
    for key in required:
        if not os.environ.get(key):
            pytest.skip(f"{key} not set")
    return Retriever()

def test_store_and_search(retriever):
    # Store a test chunk
    chunk = KnowledgeChunk(
        content="Loss aversion means losses feel 2x worse than equivalent gains.",
        company_id="test",
        data_type="behavioral_economics",
        source="test",
    )
    stored = retriever.store_chunks([chunk])
    assert stored == 1

    # Search for it
    results = retriever.search(
        query="What is loss aversion?",
        company_id="test",
        data_types=["behavioral_economics"],
    )
    assert len(results) >= 1
    assert "loss" in results[0]["content"].lower()

    # Cleanup
    retriever.delete_chunks("test")
