"""Reddit ingestion — pulls top posts from fitness subreddits via JSON API."""
from __future__ import annotations
import httpx
from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_text


class RedditIngestor(BaseIngestor):
    """Ingest Reddit posts into the knowledge base."""

    DEFAULT_SUBREDDITS = [
        "fitness", "loseit", "bodyweightfitness", "running",
        "flexibility", "nutrition", "sleep",
    ]

    def ingest(
        self,
        source: str = "",
        company_id: str = "shared",
        data_type: str = "user_research",
        agent_id: str | None = None,
        subreddits: list[str] | None = None,
        limit: int = 25,
        time_filter: str = "month",
        **kwargs,
    ) -> int:
        """Ingest top posts from fitness-related subreddits.

        Args:
            source: Ignored (uses subreddits param)
            subreddits: List of subreddit names
            limit: Posts per subreddit
            time_filter: top posts time filter (day/week/month/year/all)
        """
        subs = subreddits or self.DEFAULT_SUBREDDITS
        total = 0

        for sub in subs:
            try:
                url = f"https://www.reddit.com/r/{sub}/top.json?t={time_filter}&limit={limit}"
                response = httpx.get(url, headers={"User-Agent": "SusanBot/1.0"}, timeout=15)
                data = response.json()

                for post in data.get("data", {}).get("children", []):
                    post_data = post["data"]
                    title = post_data.get("title", "")
                    selftext = post_data.get("selftext", "")
                    if not selftext or len(selftext) < 100:
                        continue

                    content = f"**{title}**\n\n{selftext}"
                    text_chunks = chunk_text(content, max_tokens=500, overlap=50)
                    chunks = self._make_chunks(
                        texts=text_chunks,
                        data_type=data_type,
                        company_id=company_id,
                        agent_id=agent_id,
                        source=f"reddit:r/{sub}",
                        source_url=f"https://reddit.com{post_data.get('permalink', '')}",
                        metadata={
                            "subreddit": sub,
                            "score": post_data.get("score", 0),
                            "num_comments": post_data.get("num_comments", 0),
                        },
                    )
                    total += self.retriever.store_chunks(chunks)
            except Exception as e:
                print(f"  Warning: Failed to fetch r/{sub}: {e}")

        return total
