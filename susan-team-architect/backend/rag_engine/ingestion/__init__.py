# rag_engine/ingestion/__init__.py
"""Data ingestion pipelines for various sources."""
from rag_engine.ingestion.markdown import MarkdownIngestor

__all__ = ["MarkdownIngestor"]
