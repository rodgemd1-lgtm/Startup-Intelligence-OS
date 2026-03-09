"""Tests for PlaywrightIngestor."""
from __future__ import annotations
from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def mock_retriever():
    r = MagicMock()
    r.store_chunks.return_value = 4
    return r


class TestPlaywrightIngestor:
    def test_ingest_launches_browser_and_extracts(self, mock_retriever):
        from rag_engine.ingestion.playwright_scraper import PlaywrightIngestor
        mock_page = MagicMock()
        mock_page.content.return_value = "<html><body><h1>Title</h1><p>Content here.</p></body></html>"
        mock_page.title.return_value = "Test Page"
        mock_context = MagicMock()
        mock_context.new_page.return_value = mock_page
        mock_browser = MagicMock()
        mock_browser.new_context.return_value = mock_context
        mock_chromium = MagicMock()
        mock_chromium.launch.return_value = mock_browser
        mock_pw = MagicMock()
        mock_pw.chromium = mock_chromium
        mock_pw.__enter__ = MagicMock(return_value=mock_pw)
        mock_pw.__exit__ = MagicMock(return_value=False)
        with patch("rag_engine.ingestion.playwright_scraper.sync_playwright", return_value=mock_pw):
            ingestor = PlaywrightIngestor(retriever=mock_retriever)
            count = ingestor.ingest(source="https://example.com/spa",
                                     company_id="transformfit", data_type="competitive_intel")
        mock_page.goto.assert_called_once_with("https://example.com/spa", wait_until="networkidle")
        assert count == 4

    def test_ingest_waits_for_selector(self, mock_retriever):
        from rag_engine.ingestion.playwright_scraper import PlaywrightIngestor
        mock_page = MagicMock()
        mock_page.content.return_value = "<html><body><div class='data'>Loaded</div></body></html>"
        mock_page.title.return_value = "Dynamic Page"
        mock_context = MagicMock()
        mock_context.new_page.return_value = mock_page
        mock_browser = MagicMock()
        mock_browser.new_context.return_value = mock_context
        mock_chromium = MagicMock()
        mock_chromium.launch.return_value = mock_browser
        mock_pw = MagicMock()
        mock_pw.chromium = mock_chromium
        mock_pw.__enter__ = MagicMock(return_value=mock_pw)
        mock_pw.__exit__ = MagicMock(return_value=False)
        with patch("rag_engine.ingestion.playwright_scraper.sync_playwright", return_value=mock_pw):
            ingestor = PlaywrightIngestor(retriever=mock_retriever)
            ingestor.ingest(source="https://example.com/dynamic",
                           company_id="transformfit", data_type="competitive_intel", wait_for=".data")
        mock_page.wait_for_selector.assert_called_once_with(".data", timeout=15000)

    def test_ingest_tags_source_as_playwright(self, mock_retriever):
        from rag_engine.ingestion.playwright_scraper import PlaywrightIngestor
        mock_page = MagicMock()
        mock_page.content.return_value = "<html><body><p>Test</p></body></html>"
        mock_page.title.return_value = "Test"
        mock_context = MagicMock()
        mock_context.new_page.return_value = mock_page
        mock_browser = MagicMock()
        mock_browser.new_context.return_value = mock_context
        mock_chromium = MagicMock()
        mock_chromium.launch.return_value = mock_browser
        mock_pw = MagicMock()
        mock_pw.chromium = mock_chromium
        mock_pw.__enter__ = MagicMock(return_value=mock_pw)
        mock_pw.__exit__ = MagicMock(return_value=False)
        with patch("rag_engine.ingestion.playwright_scraper.sync_playwright", return_value=mock_pw):
            ingestor = PlaywrightIngestor(retriever=mock_retriever)
            ingestor.ingest(source="https://example.com/pw", company_id="transformfit", data_type="test")
        stored_chunks = mock_retriever.store_chunks.call_args[0][0]
        assert stored_chunks[0].source == "playwright:https://example.com/pw"
        assert stored_chunks[0].metadata["tool"] == "playwright"

    def test_ingest_handles_browser_error(self, mock_retriever):
        from rag_engine.ingestion.playwright_scraper import PlaywrightIngestor
        mock_pw = MagicMock()
        mock_pw.chromium.launch.side_effect = Exception("Browser not installed")
        mock_pw.__enter__ = MagicMock(return_value=mock_pw)
        mock_pw.__exit__ = MagicMock(return_value=False)
        with patch("rag_engine.ingestion.playwright_scraper.sync_playwright", return_value=mock_pw):
            ingestor = PlaywrightIngestor(retriever=mock_retriever)
            count = ingestor.ingest(source="https://example.com/fail", company_id="transformfit", data_type="test")
        assert count == 0
