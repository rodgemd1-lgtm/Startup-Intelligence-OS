from pathlib import Path

from fitness_intel.pipeline import CorpusBuilder
from fitness_intel.startup_os import to_susan_knowledge_chunk


def test_domain_editorial_inventory():
    root = Path("data/domains/fitness_app_intelligence/editorial")
    builder = CorpusBuilder(root)
    inventory = builder.build_inventory()
    assert inventory["total_app_profiles"] == 46
    assert inventory["analysis_documents"] == 5


def test_document_chunk_converts_to_susan_knowledge_chunk():
    root = Path("data/domains/fitness_app_intelligence/editorial")
    builder = CorpusBuilder(root)
    chunk = builder.build_chunks(limit=1)[0]
    knowledge_chunk = to_susan_knowledge_chunk(chunk)
    assert knowledge_chunk.company_id == "shared"
    assert knowledge_chunk.source_url
