# rag_engine/ingestion/__init__.py
"""Data ingestion pipelines for various sources."""
from rag_engine.ingestion.markdown import MarkdownIngestor
from rag_engine.ingestion.books import BookIngestor

__all__ = ["MarkdownIngestor", "BookIngestor"]
