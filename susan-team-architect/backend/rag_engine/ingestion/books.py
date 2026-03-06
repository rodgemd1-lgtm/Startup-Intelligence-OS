"""Foundational text synthesis — generates and embeds book/framework summaries."""
from __future__ import annotations
import yaml
from pathlib import Path
from anthropic import Anthropic
from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_text
from susan_core.config import config


class BookIngestor(BaseIngestor):
    """Generate and ingest summaries of foundational texts."""

    def ingest(self, source: str, company_id: str = "shared", **kwargs) -> int:
        path = Path(source)
        with open(path) as f:
            books = yaml.safe_load(f)

        client = Anthropic(api_key=config.anthropic_api_key)
        total = 0

        for book in books.get("texts", []):
            prompt = f"""Summarize the key frameworks and actionable principles from:
Title: {book['title']}
Author: {book['author']}
Focus areas: {', '.join(book.get('focus', []))}

Write 5-8 detailed chunks (each 200-400 words) covering:
1. Core theory/model
2. Key mechanisms
3. Product design implications
4. Specific examples and applications
5. Common mistakes/anti-patterns

Format each chunk as a standalone paragraph that makes sense without context.
Separate chunks with ---"""

            response = client.messages.create(
                model=config.model_sonnet,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )

            text = response.content[0].text
            text_chunks = [c.strip() for c in text.split("---") if c.strip()]

            chunks = self._make_chunks(
                texts=text_chunks,
                data_type=book.get("data_type", "behavioral_economics"),
                company_id=company_id,
                source=f"book:{book['title']}",
                metadata={"author": book["author"], "category": book.get("category", "")},
            )
            total += self.retriever.store_chunks(chunks)

        return total
