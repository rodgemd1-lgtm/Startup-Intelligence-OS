"""Tests for WebIngestor.crawl (Firecrawl deep crawl)."""
from __future__ import annotations
from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def mock_retriever():
    r = MagicMock()
    r.store_chunks.return_value = 10
    return r


class TestWebIngestorCrawl:
    def test_crawl_calls_firecrawl_crawl(self, mock_retriever):
        from rag_engine.ingestion.web import WebIngestor
        mock_app = MagicMock()
        mock_app.crawl_url.return_value = MagicMock(data=[
            MagicMock(markdown="# Page 1\n\nContent of page 1.",
                      metadata=MagicMock(title="Page 1", sourceURL="https://example.com/page1")),
            MagicMock(markdown="# Page 2\n\nContent of page 2.",
                      metadata=MagicMock(title="Page 2", sourceURL="https://example.com/page2")),
        ])
        with patch("rag_engine.ingestion.web.FirecrawlApp", return_value=mock_app):
            ingestor = WebIngestor(retriever=mock_retriever)
            count = ingestor.crawl(source="https://example.com",
                                    company_id="transformfit", data_type="exercise_science", max_pages=20)
        mock_app.crawl_url.assert_called_once()
        assert count == 20  # 10 per call x 2 pages

    def test_crawl_skips_empty_pages(self, mock_retriever):
        from rag_engine.ingestion.web import WebIngestor
        mock_app = MagicMock()
        mock_app.crawl_url.return_value = MagicMock(data=[
            MagicMock(markdown="", metadata=MagicMock(title="Empty", sourceURL="https://example.com/empty")),
            MagicMock(markdown=None, metadata=MagicMock(title="None", sourceURL="https://example.com/none")),
        ])
        with patch("rag_engine.ingestion.web.FirecrawlApp", return_value=mock_app):
            ingestor = WebIngestor(retriever=mock_retriever)
            count = ingestor.crawl(source="https://example.com", company_id="transformfit", data_type="test")
        assert count == 0

    def test_crawl_handles_api_error(self, mock_retriever):
        from rag_engine.ingestion.web import WebIngestor
        mock_app = MagicMock()
        mock_app.crawl_url.side_effect = Exception("Rate limited")
        with patch("rag_engine.ingestion.web.FirecrawlApp", return_value=mock_app):
            ingestor = WebIngestor(retriever=mock_retriever)
            count = ingestor.crawl(source="https://example.com", company_id="transformfit", data_type="test")
        assert count == 0
