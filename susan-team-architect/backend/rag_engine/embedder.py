"""Voyage AI embedding client."""
from __future__ import annotations
from susan_core.config import config
from susan_core.clients import get_voyage_client


class Embedder:
    """Wraps Voyage AI for text → vector conversion."""

    def __init__(self, api_key: str | None = None):
        self.client = get_voyage_client()
        self.model = config.embedding_model
        self.dim = config.embedding_dim

    def embed(
        self,
        texts: list[str],
        input_type: str = "document",
        batch_size: int = 128,
    ) -> list[list[float]]:
        """Embed a list of texts, returns list of 1024-dim vectors."""
        if not texts:
            raise ValueError("Cannot embed empty list")

        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            result = self.client.embed(
                batch,
                model=self.model,
                input_type=input_type,
            )
            all_embeddings.extend(result.embeddings)

        return all_embeddings

    def embed_query(self, query: str) -> list[float]:
        """Embed a single query for retrieval."""
        result = self.client.embed(
            [query],
            model=self.model,
            input_type="query",
        )
        return result.embeddings[0]
