# rag_engine/ingestion/__init__.py
"""Data ingestion pipelines for various sources."""
from rag_engine.ingestion.markdown import MarkdownIngestor
from rag_engine.ingestion.fitness_domain import FitnessDomainIngestor
from rag_engine.ingestion.books import BookIngestor
from rag_engine.ingestion.web import WebIngestor
from rag_engine.ingestion.arxiv_ingestor import ArxivIngestor
from rag_engine.ingestion.reddit import RedditIngestor
from rag_engine.ingestion.appstore import AppStoreIngestor
from rag_engine.ingestion.nhanes import NHANESIngestor
from rag_engine.ingestion.exa_search import ExaSearchIngestor
from rag_engine.ingestion.jina_reader import JinaReaderIngestor
from rag_engine.ingestion.playwright_scraper import PlaywrightIngestor

__all__ = [
    "MarkdownIngestor",
    "FitnessDomainIngestor",
    "BookIngestor",
    "WebIngestor",
    "ArxivIngestor",
    "RedditIngestor",
    "AppStoreIngestor",
    "NHANESIngestor",
    "ExaSearchIngestor",
    "JinaReaderIngestor",
    "PlaywrightIngestor",
]
