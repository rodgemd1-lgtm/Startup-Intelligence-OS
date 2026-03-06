"""App store review ingestion — scrapes competitor app reviews."""
from __future__ import annotations
import httpx
from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_text


class AppStoreIngestor(BaseIngestor):
    """Ingest app store reviews for competitor analysis."""

    # Apple App Store IDs for key competitors
    COMPETITOR_APPS = {
        "fitbod": "1041517543",
        "noom": "634598719",
        "myfitnesspal": "341232718",
        "strava": "426826309",
        "peloton": "792750948",
    }

    def ingest(
        self,
        source: str = "",
        company_id: str = "shared",
        data_type: str = "user_research",
        agent_id: str | None = None,
        apps: dict[str, str] | None = None,
        **kwargs,
    ) -> int:
        """Ingest app store reviews for competitor analysis.

        Args:
            source: Ignored (uses apps param or defaults)
            apps: Dict of {app_name: app_store_id}
        """
        target_apps = apps or self.COMPETITOR_APPS
        total = 0

        for app_name, app_id in target_apps.items():
            try:
                # Apple RSS feed for reviews
                url = f"https://itunes.apple.com/us/rss/customerreviews/id={app_id}/sortBy=mostRecent/json"
                response = httpx.get(url, timeout=15)
                data = response.json()

                entries = data.get("feed", {}).get("entry", [])
                if not entries:
                    continue

                for entry in entries:
                    if isinstance(entry, dict) and "content" in entry:
                        title = entry.get("title", {}).get("label", "")
                        content = entry.get("content", {}).get("label", "")
                        rating = entry.get("im:rating", {}).get("label", "")

                        if not content or len(content) < 50:
                            continue

                        review_text = f"**{app_name} Review ({rating}/5)**: {title}\n\n{content}"
                        chunks = self._make_chunks(
                            texts=[review_text],
                            data_type=data_type,
                            company_id=company_id,
                            agent_id=agent_id,
                            source=f"appstore:{app_name}",
                            metadata={
                                "app": app_name,
                                "rating": rating,
                                "app_id": app_id,
                            },
                        )
                        total += self.retriever.store_chunks(chunks)
            except Exception as e:
                print(f"  Warning: Failed to fetch reviews for {app_name}: {e}")

        return total
