# rag_engine/ingestion/__init__.py
"""Data ingestion pipelines for various sources."""
from rag_engine.ingestion.markdown import MarkdownIngestor
from rag_engine.ingestion.books import BookIngestor
from rag_engine.ingestion.web import WebIngestor
from rag_engine.ingestion.arxiv_ingestor import ArxivIngestor
from rag_engine.ingestion.reddit import RedditIngestor
from rag_engine.ingestion.appstore import AppStoreIngestor
from rag_engine.ingestion.nhanes import NHANESIngestor

__all__ = [
    "MarkdownIngestor",
    "BookIngestor",
    "WebIngestor",
    "ArxivIngestor",
    "RedditIngestor",
    "AppStoreIngestor",
    "NHANESIngestor",
]
