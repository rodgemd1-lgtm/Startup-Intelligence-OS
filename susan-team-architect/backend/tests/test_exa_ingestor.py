"""Tests for ExaSearchIngestor."""
from __future__ import annotations
from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def mock_retriever():
    r = MagicMock()
    r.store_chunks.return_value = 5
    return r


class TestExaSearchIngestor:
    def test_ingest_calls_exa_search(self, mock_retriever):
        from rag_engine.ingestion.exa_search import ExaSearchIngestor
        mock_exa = MagicMock()
        mock_exa.search_and_contents.return_value.results = [
            MagicMock(url="https://example.com/article", title="Test Article",
                      text="This is the full article content about progressive overload.")
        ]
        with patch("rag_engine.ingestion.exa_search.Exa", return_value=mock_exa):
            ingestor = ExaSearchIngestor(retriever=mock_retriever)
            count = ingestor.ingest(source="progressive overload protocols",
                                     company_id="transformfit", data_type="exercise_science", num_results=5)
        mock_exa.search_and_contents.assert_called_once()
        assert count == 5

    def test_ingest_chunks_multiple_results(self, mock_retriever):
        from rag_engine.ingestion.exa_search import ExaSearchIngestor
        mock_exa = MagicMock()
        mock_exa.search_and_contents.return_value.results = [
            MagicMock(url="https://example.com/1", title="Article 1", text="Short content."),
            MagicMock(url="https://example.com/2", title="Article 2", text="Another short piece."),
        ]
        with patch("rag_engine.ingestion.exa_search.Exa", return_value=mock_exa):
            ingestor = ExaSearchIngestor(retriever=mock_retriever)
            ingestor.ingest(source="test query", company_id="transformfit", data_type="exercise_science")
        assert mock_retriever.store_chunks.call_count == 2

    def test_ingest_skips_empty_text(self, mock_retriever):
        from rag_engine.ingestion.exa_search import ExaSearchIngestor
        mock_exa = MagicMock()
        mock_exa.search_and_contents.return_value.results = [
            MagicMock(url="https://example.com/empty", title="Empty", text=""),
            MagicMock(url="https://example.com/none", title="None", text=None),
        ]
        with patch("rag_engine.ingestion.exa_search.Exa", return_value=mock_exa):
            ingestor = ExaSearchIngestor(retriever=mock_retriever)
            count = ingestor.ingest(source="test", company_id="transformfit", data_type="test")
        assert count == 0

    def test_ingest_tags_source_correctly(self, mock_retriever):
        from rag_engine.ingestion.exa_search import ExaSearchIngestor
        mock_exa = MagicMock()
        mock_exa.search_and_contents.return_value.results = [
            MagicMock(url="https://example.com/tagged", title="Tagged Article", text="Content for tagging test."),
        ]
        with patch("rag_engine.ingestion.exa_search.Exa", return_value=mock_exa):
            ingestor = ExaSearchIngestor(retriever=mock_retriever)
            ingestor.ingest(source="tagging test", company_id="transformfit", data_type="exercise_science")
        stored_chunks = mock_retriever.store_chunks.call_args[0][0]
        chunk = stored_chunks[0]
        assert chunk.source.startswith("exa:")
        assert chunk.source_url == "https://example.com/tagged"
        assert chunk.company_id == "transformfit"
        assert chunk.data_type == "exercise_science"
        assert chunk.metadata["title"] == "Tagged Article"

    def test_ingest_handles_exa_error(self, mock_retriever):
        from rag_engine.ingestion.exa_search import ExaSearchIngestor
        mock_exa = MagicMock()
        mock_exa.search_and_contents.side_effect = Exception("API rate limit")
        with patch("rag_engine.ingestion.exa_search.Exa", return_value=mock_exa):
            ingestor = ExaSearchIngestor(retriever=mock_retriever)
            count = ingestor.ingest(source="test", company_id="transformfit", data_type="test")
        assert count == 0
