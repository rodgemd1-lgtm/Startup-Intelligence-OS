"""Tests for batch manifest parser and executor."""
from __future__ import annotations
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
import yaml


@pytest.fixture
def mock_retriever():
    r = MagicMock()
    r.store_chunks.return_value = 5
    return r


@pytest.fixture
def sample_manifest(tmp_path):
    manifest = {
        "manifest": {
            "name": "Test Domain",
            "company": "transformfit",
            "data_type": "exercise_science",
            "created": "2026-03-09",
            "priority": "high",
        },
        "sources": [
            {"tool": "exa", "query": "progressive overload", "num_results": 5},
            {"tool": "jina", "url": "https://example.com/article"},
            {"tool": "firecrawl", "url": "https://example.com/site", "mode": "crawl", "max_pages": 10},
            {"tool": "firecrawl", "url": "https://example.com/single"},
        ],
    }
    path = tmp_path / "test_manifest.yaml"
    path.write_text(yaml.safe_dump(manifest, sort_keys=False))
    return path


class TestManifestParser:
    def test_parse_manifest(self, sample_manifest):
        from rag_engine.batch import parse_manifest
        result = parse_manifest(sample_manifest)
        assert result["manifest"]["name"] == "Test Domain"
        assert result["manifest"]["company"] == "transformfit"
        assert len(result["sources"]) == 4

    def test_parse_nonexistent_file(self):
        from rag_engine.batch import parse_manifest
        with pytest.raises(FileNotFoundError):
            parse_manifest(Path("/nonexistent/manifest.yaml"))


class TestBatchExecutor:
    def test_execute_dry_run(self, sample_manifest):
        from rag_engine.batch import execute_manifest
        result = execute_manifest(sample_manifest, dry_run=True)
        assert result["total_chunks"] == 0
        assert result["sources_processed"] == 0
        assert result["sources_total"] == 4

    def test_execute_dispatches_to_correct_ingestors(self, sample_manifest):
        from rag_engine.batch import execute_manifest
        with patch("rag_engine.batch.ExaSearchIngestor") as MockExa, \
             patch("rag_engine.batch.JinaReaderIngestor") as MockJina, \
             patch("rag_engine.batch.WebIngestor") as MockWeb, \
             patch("rag_engine.batch.PlaywrightIngestor"):
            MockExa.return_value.ingest.return_value = 10
            MockJina.return_value.ingest.return_value = 5
            MockWeb.return_value.ingest.return_value = 3
            MockWeb.return_value.crawl.return_value = 8
            result = execute_manifest(sample_manifest, dry_run=False)
        MockExa.return_value.ingest.assert_called_once()
        MockJina.return_value.ingest.assert_called_once()
        MockWeb.return_value.crawl.assert_called_once()
        MockWeb.return_value.ingest.assert_called_once()
        assert result["total_chunks"] == 26
        assert result["sources_processed"] == 4

    def test_execute_continues_on_error(self, tmp_path):
        manifest = {
            "manifest": {"name": "Error Test", "company": "transformfit", "data_type": "test"},
            "sources": [
                {"tool": "jina", "url": "https://example.com/fail"},
                {"tool": "jina", "url": "https://example.com/ok"},
            ],
        }
        path = tmp_path / "error_manifest.yaml"
        path.write_text(yaml.safe_dump(manifest, sort_keys=False))
        from rag_engine.batch import execute_manifest
        with patch("rag_engine.batch.ExaSearchIngestor"), \
             patch("rag_engine.batch.PlaywrightIngestor"), \
             patch("rag_engine.batch.WebIngestor"), \
             patch("rag_engine.batch.JinaReaderIngestor") as MockJina:
            MockJina.return_value.ingest.side_effect = [Exception("fail"), 5]
            result = execute_manifest(path, dry_run=False)
        assert result["total_chunks"] == 5
        assert result["errors"] == 1
