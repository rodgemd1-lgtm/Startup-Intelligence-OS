from fitness_intel.pipeline import CorpusBuilder
from fitness_intel.retrieval import HybridRetriever


def test_retriever_finds_glp1_content():
    builder = CorpusBuilder(".")
    chunks = [chunk.model_dump(mode="json") for chunk in builder.build_chunks()]
    retriever = HybridRetriever(chunks)
    results = retriever.search("GLP-1 medication tracking", top_k=3)
    assert results
    assert any("GLP-1" in result["content"] for result in results)
