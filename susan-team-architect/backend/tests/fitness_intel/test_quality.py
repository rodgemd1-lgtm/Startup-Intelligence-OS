from fitness_intel.pipeline import CorpusBuilder
from fitness_intel.quality import audit_chunks_for_citations, audit_pilot_data


def test_pilot_data_has_no_missing_sources():
    report = audit_pilot_data(".")
    assert not any(finding.code == "missing_sources" for finding in report.findings)


def test_chunk_audit_has_no_missing_source_path():
    builder = CorpusBuilder(".")
    chunks = [chunk.model_dump(mode="json") for chunk in builder.build_chunks(limit=5)]
    report = audit_chunks_for_citations(chunks)
    assert not report.findings

