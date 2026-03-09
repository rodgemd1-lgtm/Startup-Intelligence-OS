"""Tests for JinaReaderIngestor."""
from __future__ import annotations
from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def mock_retriever():
    r = MagicMock()
    r.store_chunks.return_value = 3
    return r


class TestJinaReaderIngestor:
    def test_ingest_fetches_via_jina_reader(self, mock_retriever):
        from rag_engine.ingestion.jina_reader import JinaReaderIngestor
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "# Article Title\n\nClean markdown content from Jina."
        mock_response.raise_for_status = MagicMock()
        with patch("rag_engine.ingestion.jina_reader.httpx.get", return_value=mock_response) as mock_get:
            ingestor = JinaReaderIngestor(retriever=mock_retriever)
            count = ingestor.ingest(source="https://example.com/article",
                                     company_id="transformfit", data_type="ux_research")
        mock_get.assert_called_once()
        call_url = mock_get.call_args[0][0]
        assert call_url == "https://r.jina.ai/https://example.com/article"
        assert count == 3

    def test_ingest_stores_chunks_with_correct_metadata(self, mock_retriever):
        from rag_engine.ingestion.jina_reader import JinaReaderIngestor
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Some clean content."
        mock_response.raise_for_status = MagicMock()
        with patch("rag_engine.ingestion.jina_reader.httpx.get", return_value=mock_response):
            ingestor = JinaReaderIngestor(retriever=mock_retriever)
            ingestor.ingest(source="https://example.com/test",
                           company_id="transformfit", data_type="exercise_science")
        stored_chunks = mock_retriever.store_chunks.call_args[0][0]
        chunk = stored_chunks[0]
        assert chunk.source == "jina:https://example.com/test"
        assert chunk.source_url == "https://example.com/test"
        assert chunk.metadata["tool"] == "jina"

    def test_ingest_handles_empty_response(self, mock_retriever):
        from rag_engine.ingestion.jina_reader import JinaReaderIngestor
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = ""
        mock_response.raise_for_status = MagicMock()
        with patch("rag_engine.ingestion.jina_reader.httpx.get", return_value=mock_response):
            ingestor = JinaReaderIngestor(retriever=mock_retriever)
            count = ingestor.ingest(source="https://example.com/empty", company_id="transformfit", data_type="test")
        assert count == 0

    def test_ingest_handles_http_error(self, mock_retriever):
        from rag_engine.ingestion.jina_reader import JinaReaderIngestor
        with patch("rag_engine.ingestion.jina_reader.httpx.get", side_effect=Exception("Connection refused")):
            ingestor = JinaReaderIngestor(retriever=mock_retriever)
            count = ingestor.ingest(source="https://example.com/fail", company_id="transformfit", data_type="test")
        assert count == 0

    def test_ingest_url_list_from_file(self, mock_retriever, tmp_path):
        from rag_engine.ingestion.jina_reader import JinaReaderIngestor
        url_file = tmp_path / "urls.txt"
        url_file.write_text("https://example.com/a\nhttps://example.com/b\n")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Content."
        mock_response.raise_for_status = MagicMock()
        with patch("rag_engine.ingestion.jina_reader.httpx.get", return_value=mock_response) as mock_get:
            ingestor = JinaReaderIngestor(retriever=mock_retriever)
            ingestor.ingest(source=str(url_file), company_id="transformfit", data_type="test")
        assert mock_get.call_count == 2
