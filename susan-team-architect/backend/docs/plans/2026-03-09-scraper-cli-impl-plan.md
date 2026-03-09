# Susan Scraper CLI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a `susan scrape` CLI with Exa, Firecrawl crawl, Jina reader, and Playwright ingestors, plus a batch manifest system for systematic data collection across TransformFit's 14 data domains.

**Architecture:** Extends the existing `scripts/susan_cli.py` with a `scrape` subcommand. Four new ingestor modules in `rag_engine/ingestion/` follow the `BaseIngestor` pattern. Batch manifests in YAML define per-domain scraping jobs. All data flows into Susan's existing pgvector `knowledge_chunks` table.

**Tech Stack:** Python 3.11+, exa-py, playwright, markdownify, httpx (existing), firecrawl-py (existing), Supabase pgvector (existing), Voyage AI embeddings (existing)

**Design doc:** `docs/plans/2026-03-09-scraper-cli-design.md`

---

## Sprint 1: Dependencies and Configuration (Tasks 1-2)

### Task 1: Add new dependencies

**Files:**
- Modify: `pyproject.toml`
- Modify: `susan_core/config.py`
- Modify: `.env.example`

**Step 1: Add packages to pyproject.toml**

Open `pyproject.toml` and add to the `dependencies` list:

```toml
dependencies = [
    "anthropic>=0.1.40",
    "voyageai>=0.3.0",
    "supabase>=2.20.0",
    "psycopg[binary]>=3.3.3",
    "pydantic>=2.10.0",
    "fastapi>=0.115.0",
    "PyYAML>=6.0",
    "firecrawl-py>=4.0.0",
    "arxiv>=2.1.0",
    "httpx>=0.27.0",
    "tiktoken>=0.7.0",
    "exa-py>=1.0.0",
    "playwright>=1.49.0",
    "markdownify>=0.14.0",
]
```

**Step 2: Install dependencies**

Run:
```bash
cd /Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend
pip install -e ".[dev]"
playwright install chromium
```

Expected: All packages install. Chromium binary downloads (~150MB).

**Step 3: Add config fields to susan_core/config.py**

Add after `firecrawl_api_key` line:

```python
exa_api_key: str = os.environ.get("EXA_API_KEY", "")
jina_api_key: str = os.environ.get("JINA_API_KEY", "")
scrape_manifests_dir: Path = Path(__file__).parent.parent / "data" / "scrape_manifests"
```

**Step 4: Update .env.example**

Append:

```
EXA_API_KEY=exa-...           # Exa semantic search
JINA_API_KEY=jina_...         # Optional: Jina AI reader (free <100 req/day without key)
```

**Step 5: Commit**

```bash
git add pyproject.toml susan_core/config.py .env.example
git commit -m "chore: add exa-py, playwright, markdownify dependencies"
```

---

### Task 2: Create scrape_manifests directory structure

**Files:**
- Create: `data/scrape_manifests/.gitkeep`
- Create: `data/scrape_manifests/urls/.gitkeep`

**Step 1: Create directories**

```bash
mkdir -p data/scrape_manifests/urls
touch data/scrape_manifests/.gitkeep
touch data/scrape_manifests/urls/.gitkeep
```

**Step 2: Commit**

```bash
git add data/scrape_manifests/
git commit -m "chore: add scrape_manifests directory structure"
```

---

## Sprint 2: Exa Search Ingestor (Tasks 3-4)

### Task 3: Write ExaSearchIngestor

**Files:**
- Create: `rag_engine/ingestion/exa_search.py`
- Test: `tests/test_exa_ingestor.py`

**Step 1: Write the failing test**

Create `tests/test_exa_ingestor.py`:

```python
"""Tests for ExaSearchIngestor."""
from __future__ import annotations
from unittest.mock import MagicMock, patch
import pytest

# Mock the Retriever so we don't need a real DB connection
@pytest.fixture
def mock_retriever():
    r = MagicMock()
    r.store_chunks.return_value = 5
    return r


class TestExaSearchIngestor:
    def test_ingest_calls_exa_search(self, mock_retriever):
        """Exa client is called with the query string."""
        from rag_engine.ingestion.exa_search import ExaSearchIngestor

        mock_exa = MagicMock()
        mock_exa.search_and_contents.return_value.results = [
            MagicMock(
                url="https://example.com/article",
                title="Test Article",
                text="This is the full article content about progressive overload.",
            )
        ]

        with patch("rag_engine.ingestion.exa_search.Exa", return_value=mock_exa):
            ingestor = ExaSearchIngestor(retriever=mock_retriever)
            count = ingestor.ingest(
                source="progressive overload protocols",
                company_id="transformfit",
                data_type="exercise_science",
                num_results=5,
            )

        mock_exa.search_and_contents.assert_called_once()
        call_kwargs = mock_exa.search_and_contents.call_args
        assert call_kwargs[0][0] == "progressive overload protocols"
        assert count == 5

    def test_ingest_chunks_content(self, mock_retriever):
        """Content from results is chunked and stored."""
        from rag_engine.ingestion.exa_search import ExaSearchIngestor

        mock_exa = MagicMock()
        mock_exa.search_and_contents.return_value.results = [
            MagicMock(
                url="https://example.com/1",
                title="Article 1",
                text="Short content.",
            ),
            MagicMock(
                url="https://example.com/2",
                title="Article 2",
                text="Another short piece.",
            ),
        ]

        with patch("rag_engine.ingestion.exa_search.Exa", return_value=mock_exa):
            ingestor = ExaSearchIngestor(retriever=mock_retriever)
            ingestor.ingest(
                source="test query",
                company_id="transformfit",
                data_type="exercise_science",
            )

        # store_chunks called once per result
        assert mock_retriever.store_chunks.call_count == 2

    def test_ingest_skips_empty_text(self, mock_retriever):
        """Results with no text content are skipped."""
        from rag_engine.ingestion.exa_search import ExaSearchIngestor

        mock_exa = MagicMock()
        mock_exa.search_and_contents.return_value.results = [
            MagicMock(url="https://example.com/empty", title="Empty", text=""),
            MagicMock(url="https://example.com/none", title="None", text=None),
        ]

        with patch("rag_engine.ingestion.exa_search.Exa", return_value=mock_exa):
            ingestor = ExaSearchIngestor(retriever=mock_retriever)
            count = ingestor.ingest(source="test", company_id="transformfit", data_type="test")

        assert count == 0
        mock_retriever.store_chunks.assert_not_called()

    def test_ingest_tags_source_correctly(self, mock_retriever):
        """Chunks are tagged with exa source and correct metadata."""
        from rag_engine.ingestion.exa_search import ExaSearchIngestor

        mock_exa = MagicMock()
        mock_exa.search_and_contents.return_value.results = [
            MagicMock(
                url="https://example.com/tagged",
                title="Tagged Article",
                text="Content for tagging test.",
            ),
        ]

        with patch("rag_engine.ingestion.exa_search.Exa", return_value=mock_exa):
            ingestor = ExaSearchIngestor(retriever=mock_retriever)
            ingestor.ingest(
                source="tagging test",
                company_id="transformfit",
                data_type="exercise_science",
            )

        stored_chunks = mock_retriever.store_chunks.call_args[0][0]
        chunk = stored_chunks[0]
        assert chunk.source.startswith("exa:")
        assert chunk.source_url == "https://example.com/tagged"
        assert chunk.company_id == "transformfit"
        assert chunk.data_type == "exercise_science"
        assert chunk.metadata["title"] == "Tagged Article"

    def test_ingest_handles_exa_error(self, mock_retriever):
        """Exa API errors are caught and return 0."""
        from rag_engine.ingestion.exa_search import ExaSearchIngestor

        mock_exa = MagicMock()
        mock_exa.search_and_contents.side_effect = Exception("API rate limit")

        with patch("rag_engine.ingestion.exa_search.Exa", return_value=mock_exa):
            ingestor = ExaSearchIngestor(retriever=mock_retriever)
            count = ingestor.ingest(source="test", company_id="transformfit", data_type="test")

        assert count == 0
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend
python -m pytest tests/test_exa_ingestor.py -v
```

Expected: FAIL -- `ModuleNotFoundError: No module named 'rag_engine.ingestion.exa_search'`

**Step 3: Write ExaSearchIngestor**

Create `rag_engine/ingestion/exa_search.py`:

```python
"""Exa semantic search ingestion -- discovers and extracts thematically related content."""
from __future__ import annotations
from exa_py import Exa
from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_markdown
from susan_core.config import config


class ExaSearchIngestor(BaseIngestor):
    """Semantic search via Exa, then ingest top results into knowledge base."""

    def ingest(
        self,
        source: str,
        company_id: str = "shared",
        data_type: str = "market_research",
        agent_id: str | None = None,
        num_results: int = 10,
        search_type: str = "autoprompt",
        **kwargs,
    ) -> int:
        """Run Exa semantic search and ingest result content.

        Args:
            source: The search query string.
            num_results: Number of results to fetch (default 10).
            search_type: Exa search type -- autoprompt, keyword, or neural.
        """
        client = Exa(api_key=config.exa_api_key)
        total = 0

        try:
            response = client.search_and_contents(
                source,
                num_results=num_results,
                type=search_type,
                text=True,
                use_autoprompt=(search_type == "autoprompt"),
            )
        except Exception as e:
            print(f"  Warning: Exa search failed: {e}")
            return 0

        for result in response.results:
            text = getattr(result, "text", "") or ""
            if not text.strip():
                continue

            title = getattr(result, "title", "") or ""
            url = getattr(result, "url", "") or ""

            text_chunks = chunk_markdown(text, max_tokens=500)
            chunks = self._make_chunks(
                texts=text_chunks,
                data_type=data_type,
                company_id=company_id,
                agent_id=agent_id,
                source=f"exa:{source[:80]}",
                source_url=url,
                metadata={"title": title, "tool": "exa", "query": source},
            )
            total += self.retriever.store_chunks(chunks)

        return total
```

**Step 4: Register in __init__.py**

Add to `rag_engine/ingestion/__init__.py`:

```python
from rag_engine.ingestion.exa_search import ExaSearchIngestor
```

And add `"ExaSearchIngestor"` to the `__all__` list.

**Step 5: Run tests to verify they pass**

```bash
python -m pytest tests/test_exa_ingestor.py -v
```

Expected: 5 passed.

**Step 6: Commit**

```bash
git add rag_engine/ingestion/exa_search.py rag_engine/ingestion/__init__.py tests/test_exa_ingestor.py
git commit -m "feat: add ExaSearchIngestor for semantic search ingestion"
```

---

### Task 4: Write JinaReaderIngestor

**Files:**
- Create: `rag_engine/ingestion/jina_reader.py`
- Test: `tests/test_jina_ingestor.py`

**Step 1: Write the failing test**

Create `tests/test_jina_ingestor.py`:

```python
"""Tests for JinaReaderIngestor."""
from __future__ import annotations
from unittest.mock import MagicMock, patch, AsyncMock
import pytest


@pytest.fixture
def mock_retriever():
    r = MagicMock()
    r.store_chunks.return_value = 3
    return r


class TestJinaReaderIngestor:
    def test_ingest_fetches_via_jina_reader(self, mock_retriever):
        """Jina reader URL is constructed correctly."""
        from rag_engine.ingestion.jina_reader import JinaReaderIngestor

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "# Article Title\n\nClean markdown content from Jina."
        mock_response.raise_for_status = MagicMock()

        with patch("rag_engine.ingestion.jina_reader.httpx.get", return_value=mock_response) as mock_get:
            ingestor = JinaReaderIngestor(retriever=mock_retriever)
            count = ingestor.ingest(
                source="https://example.com/article",
                company_id="transformfit",
                data_type="ux_research",
            )

        mock_get.assert_called_once()
        call_url = mock_get.call_args[0][0]
        assert call_url == "https://r.jina.ai/https://example.com/article"
        assert count == 3

    def test_ingest_stores_chunks_with_correct_metadata(self, mock_retriever):
        """Chunks are tagged with jina source and URL."""
        from rag_engine.ingestion.jina_reader import JinaReaderIngestor

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Some clean content."
        mock_response.raise_for_status = MagicMock()

        with patch("rag_engine.ingestion.jina_reader.httpx.get", return_value=mock_response):
            ingestor = JinaReaderIngestor(retriever=mock_retriever)
            ingestor.ingest(
                source="https://example.com/test",
                company_id="transformfit",
                data_type="exercise_science",
            )

        stored_chunks = mock_retriever.store_chunks.call_args[0][0]
        chunk = stored_chunks[0]
        assert chunk.source == "jina:https://example.com/test"
        assert chunk.source_url == "https://example.com/test"
        assert chunk.metadata["tool"] == "jina"

    def test_ingest_handles_empty_response(self, mock_retriever):
        """Empty response from Jina returns 0."""
        from rag_engine.ingestion.jina_reader import JinaReaderIngestor

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = ""
        mock_response.raise_for_status = MagicMock()

        with patch("rag_engine.ingestion.jina_reader.httpx.get", return_value=mock_response):
            ingestor = JinaReaderIngestor(retriever=mock_retriever)
            count = ingestor.ingest(source="https://example.com/empty", company_id="transformfit", data_type="test")

        assert count == 0

    def test_ingest_handles_http_error(self, mock_retriever):
        """HTTP errors are caught gracefully."""
        from rag_engine.ingestion.jina_reader import JinaReaderIngestor

        with patch("rag_engine.ingestion.jina_reader.httpx.get", side_effect=Exception("Connection refused")):
            ingestor = JinaReaderIngestor(retriever=mock_retriever)
            count = ingestor.ingest(source="https://example.com/fail", company_id="transformfit", data_type="test")

        assert count == 0

    def test_ingest_url_list_from_file(self, mock_retriever, tmp_path):
        """When source is a file path, read URLs from it."""
        from rag_engine.ingestion.jina_reader import JinaReaderIngestor

        url_file = tmp_path / "urls.txt"
        url_file.write_text("https://example.com/a\nhttps://example.com/b\n")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Content."
        mock_response.raise_for_status = MagicMock()

        with patch("rag_engine.ingestion.jina_reader.httpx.get", return_value=mock_response) as mock_get:
            ingestor = JinaReaderIngestor(retriever=mock_retriever)
            ingestor.ingest(source=str(url_file), company_id="transformfit", data_type="test")

        assert mock_get.call_count == 2
```

**Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_jina_ingestor.py -v
```

Expected: FAIL -- `ModuleNotFoundError`

**Step 3: Write JinaReaderIngestor**

Create `rag_engine/ingestion/jina_reader.py`:

```python
"""Jina AI reader mode -- clean text extraction from cluttered web pages."""
from __future__ import annotations
from pathlib import Path
import httpx
from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_markdown
from susan_core.config import config


class JinaReaderIngestor(BaseIngestor):
    """Extract clean markdown from URLs via Jina AI reader mode."""

    JINA_READER_URL = "https://r.jina.ai/"

    def ingest(
        self,
        source: str,
        company_id: str = "shared",
        data_type: str = "market_research",
        agent_id: str | None = None,
        **kwargs,
    ) -> int:
        """Ingest one URL or a file of URLs via Jina reader.

        Args:
            source: A URL string, or path to a file with one URL per line.
        """
        urls = self._resolve_urls(source)
        total = 0

        headers = {"Accept": "text/markdown"}
        if config.jina_api_key:
            headers["Authorization"] = f"Bearer {config.jina_api_key}"

        for url in urls:
            try:
                response = httpx.get(
                    f"{self.JINA_READER_URL}{url}",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                markdown = response.text.strip()
                if not markdown:
                    continue

                text_chunks = chunk_markdown(markdown, max_tokens=500)
                chunks = self._make_chunks(
                    texts=text_chunks,
                    data_type=data_type,
                    company_id=company_id,
                    agent_id=agent_id,
                    source=f"jina:{url}",
                    source_url=url,
                    metadata={"tool": "jina"},
                )
                total += self.retriever.store_chunks(chunks)
            except Exception as e:
                print(f"  Warning: Jina reader failed for {url}: {e}")

        return total

    def _resolve_urls(self, source: str) -> list[str]:
        """Resolve source to a list of URLs."""
        path = Path(source)
        if path.is_file():
            return [line.strip() for line in path.read_text().splitlines() if line.strip()]
        return [source]
```

**Step 4: Register in __init__.py**

Add to `rag_engine/ingestion/__init__.py`:

```python
from rag_engine.ingestion.jina_reader import JinaReaderIngestor
```

And add `"JinaReaderIngestor"` to `__all__`.

**Step 5: Run tests**

```bash
python -m pytest tests/test_jina_ingestor.py -v
```

Expected: 5 passed.

**Step 6: Commit**

```bash
git add rag_engine/ingestion/jina_reader.py rag_engine/ingestion/__init__.py tests/test_jina_ingestor.py
git commit -m "feat: add JinaReaderIngestor for clean text extraction"
```

---

## Sprint 3: Playwright and Firecrawl Crawl (Tasks 5-6)

### Task 5: Write PlaywrightIngestor

**Files:**
- Create: `rag_engine/ingestion/playwright_scraper.py`
- Test: `tests/test_playwright_ingestor.py`

**Step 1: Write the failing test**

Create `tests/test_playwright_ingestor.py`:

```python
"""Tests for PlaywrightIngestor."""
from __future__ import annotations
from unittest.mock import MagicMock, patch, PropertyMock
import pytest


@pytest.fixture
def mock_retriever():
    r = MagicMock()
    r.store_chunks.return_value = 4
    return r


class TestPlaywrightIngestor:
    def test_ingest_launches_browser_and_extracts(self, mock_retriever):
        """Playwright launches browser, navigates, and extracts content."""
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
            count = ingestor.ingest(
                source="https://example.com/spa",
                company_id="transformfit",
                data_type="competitive_intel",
            )

        mock_page.goto.assert_called_once_with("https://example.com/spa", wait_until="networkidle")
        assert count == 4

    def test_ingest_waits_for_selector(self, mock_retriever):
        """When wait_for is provided, page.wait_for_selector is called."""
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
            ingestor.ingest(
                source="https://example.com/dynamic",
                company_id="transformfit",
                data_type="competitive_intel",
                wait_for=".data",
            )

        mock_page.wait_for_selector.assert_called_once_with(".data", timeout=15000)

    def test_ingest_tags_source_as_playwright(self, mock_retriever):
        """Chunks are tagged with playwright source."""
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
            ingestor.ingest(
                source="https://example.com/pw",
                company_id="transformfit",
                data_type="test",
            )

        stored_chunks = mock_retriever.store_chunks.call_args[0][0]
        assert stored_chunks[0].source == "playwright:https://example.com/pw"
        assert stored_chunks[0].metadata["tool"] == "playwright"

    def test_ingest_handles_browser_error(self, mock_retriever):
        """Browser launch failure returns 0."""
        from rag_engine.ingestion.playwright_scraper import PlaywrightIngestor

        mock_pw = MagicMock()
        mock_pw.chromium.launch.side_effect = Exception("Browser not installed")
        mock_pw.__enter__ = MagicMock(return_value=mock_pw)
        mock_pw.__exit__ = MagicMock(return_value=False)

        with patch("rag_engine.ingestion.playwright_scraper.sync_playwright", return_value=mock_pw):
            ingestor = PlaywrightIngestor(retriever=mock_retriever)
            count = ingestor.ingest(source="https://example.com/fail", company_id="transformfit", data_type="test")

        assert count == 0
```

**Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_playwright_ingestor.py -v
```

Expected: FAIL -- `ModuleNotFoundError`

**Step 3: Write PlaywrightIngestor**

Create `rag_engine/ingestion/playwright_scraper.py`:

```python
"""Playwright scraper -- navigates dynamic/JS-heavy pages and extracts content."""
from __future__ import annotations
from playwright.sync_api import sync_playwright
from markdownify import markdownify as md
from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_markdown


class PlaywrightIngestor(BaseIngestor):
    """Scrape JS-rendered pages via headless Chromium."""

    def ingest(
        self,
        source: str,
        company_id: str = "shared",
        data_type: str = "market_research",
        agent_id: str | None = None,
        wait_for: str | None = None,
        **kwargs,
    ) -> int:
        """Navigate to URL with Playwright, extract content as markdown.

        Args:
            source: URL to scrape.
            wait_for: Optional CSS selector to wait for before extraction.
        """
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()

                page.goto(source, wait_until="networkidle")

                if wait_for:
                    page.wait_for_selector(wait_for, timeout=15000)

                html = page.content()
                title = page.title()

                browser.close()
        except Exception as e:
            print(f"  Warning: Playwright failed for {source}: {e}")
            return 0

        markdown = md(html, strip=["script", "style", "nav", "footer", "header"])
        markdown = markdown.strip()
        if not markdown:
            return 0

        text_chunks = chunk_markdown(markdown, max_tokens=500)
        chunks = self._make_chunks(
            texts=text_chunks,
            data_type=data_type,
            company_id=company_id,
            agent_id=agent_id,
            source=f"playwright:{source}",
            source_url=source,
            metadata={"title": title, "tool": "playwright"},
        )
        return self.retriever.store_chunks(chunks)
```

**Step 4: Register in __init__.py**

Add to `rag_engine/ingestion/__init__.py`:

```python
from rag_engine.ingestion.playwright_scraper import PlaywrightIngestor
```

And add `"PlaywrightIngestor"` to `__all__`.

**Step 5: Run tests**

```bash
python -m pytest tests/test_playwright_ingestor.py -v
```

Expected: 4 passed.

**Step 6: Commit**

```bash
git add rag_engine/ingestion/playwright_scraper.py rag_engine/ingestion/__init__.py tests/test_playwright_ingestor.py
git commit -m "feat: add PlaywrightIngestor for dynamic page scraping"
```

---

### Task 6: Add crawl method to WebIngestor

**Files:**
- Modify: `rag_engine/ingestion/web.py`
- Test: `tests/test_web_crawl.py`

**Step 1: Write the failing test**

Create `tests/test_web_crawl.py`:

```python
"""Tests for WebIngestor.crawl (Firecrawl deep crawl)."""
from __future__ import annotations
from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def mock_retriever():
    r = MagicMock()
    r.store_chunks.return_value = 10
    return r


class TestWebIngestorCrawl:
    def test_crawl_calls_firecrawl_crawl(self, mock_retriever):
        """Firecrawl crawl API is called with correct params."""
        from rag_engine.ingestion.web import WebIngestor

        mock_app = MagicMock()
        mock_app.crawl_url.return_value = MagicMock(data=[
            MagicMock(markdown="# Page 1\n\nContent of page 1.", metadata=MagicMock(title="Page 1", sourceURL="https://example.com/page1")),
            MagicMock(markdown="# Page 2\n\nContent of page 2.", metadata=MagicMock(title="Page 2", sourceURL="https://example.com/page2")),
        ])

        with patch("rag_engine.ingestion.web.FirecrawlApp", return_value=mock_app):
            ingestor = WebIngestor(retriever=mock_retriever)
            count = ingestor.crawl(
                source="https://example.com",
                company_id="transformfit",
                data_type="exercise_science",
                max_pages=20,
            )

        mock_app.crawl_url.assert_called_once()
        assert count == 20  # 10 per call x 2 pages

    def test_crawl_skips_empty_pages(self, mock_retriever):
        """Pages with no markdown content are skipped."""
        from rag_engine.ingestion.web import WebIngestor

        mock_app = MagicMock()
        mock_app.crawl_url.return_value = MagicMock(data=[
            MagicMock(markdown="", metadata=MagicMock(title="Empty", sourceURL="https://example.com/empty")),
            MagicMock(markdown=None, metadata=MagicMock(title="None", sourceURL="https://example.com/none")),
        ])

        with patch("rag_engine.ingestion.web.FirecrawlApp", return_value=mock_app):
            ingestor = WebIngestor(retriever=mock_retriever)
            count = ingestor.crawl(source="https://example.com", company_id="transformfit", data_type="test")

        assert count == 0

    def test_crawl_handles_api_error(self, mock_retriever):
        """API errors return 0."""
        from rag_engine.ingestion.web import WebIngestor

        mock_app = MagicMock()
        mock_app.crawl_url.side_effect = Exception("Rate limited")

        with patch("rag_engine.ingestion.web.FirecrawlApp", return_value=mock_app):
            ingestor = WebIngestor(retriever=mock_retriever)
            count = ingestor.crawl(source="https://example.com", company_id="transformfit", data_type="test")

        assert count == 0
```

**Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_web_crawl.py -v
```

Expected: FAIL -- `AttributeError: 'WebIngestor' object has no attribute 'crawl'`

**Step 3: Add crawl method to WebIngestor**

Add to `rag_engine/ingestion/web.py` after the `ingest` method:

```python
    def crawl(
        self,
        source: str,
        company_id: str = "shared",
        data_type: str = "market_research",
        agent_id: str | None = None,
        max_pages: int = 50,
        **kwargs,
    ) -> int:
        """Deep crawl a site via Firecrawl, following internal links.

        Args:
            source: Base URL to crawl.
            max_pages: Maximum number of pages to crawl.
        """
        app = FirecrawlApp(api_key=config.firecrawl_api_key)
        total = 0

        try:
            result = app.crawl_url(source, params={"limit": max_pages})
            pages = result.data if hasattr(result, "data") else []
        except Exception as e:
            print(f"  Warning: Firecrawl crawl failed for {source}: {e}")
            return 0

        for page in pages:
            markdown = getattr(page, "markdown", "") or ""
            if not markdown.strip():
                continue

            metadata = getattr(page, "metadata", None)
            title = getattr(metadata, "title", "") if metadata else ""
            page_url = getattr(metadata, "sourceURL", source) if metadata else source

            text_chunks = chunk_markdown(markdown, max_tokens=500)
            chunks = self._make_chunks(
                texts=text_chunks,
                data_type=data_type,
                company_id=company_id,
                agent_id=agent_id,
                source=f"firecrawl-crawl:{page_url}",
                source_url=page_url,
                metadata={"title": title, "tool": "firecrawl-crawl", "base_url": source},
            )
            total += self.retriever.store_chunks(chunks)

        return total
```

**Step 4: Run tests**

```bash
python -m pytest tests/test_web_crawl.py -v
```

Expected: 3 passed.

**Step 5: Commit**

```bash
git add rag_engine/ingestion/web.py tests/test_web_crawl.py
git commit -m "feat: add crawl method to WebIngestor for deep site crawling"
```

---

## Sprint 4: Batch Manifest System (Tasks 7-8)

### Task 7: Write manifest parser and executor

**Files:**
- Create: `rag_engine/batch.py`
- Test: `tests/test_batch.py`

**Step 1: Write the failing test**

Create `tests/test_batch.py`:

```python
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
        """Manifest YAML is parsed correctly."""
        from rag_engine.batch import parse_manifest

        result = parse_manifest(sample_manifest)
        assert result["manifest"]["name"] == "Test Domain"
        assert result["manifest"]["company"] == "transformfit"
        assert len(result["sources"]) == 4

    def test_parse_nonexistent_file(self):
        """Non-existent manifest raises FileNotFoundError."""
        from rag_engine.batch import parse_manifest

        with pytest.raises(FileNotFoundError):
            parse_manifest(Path("/nonexistent/manifest.yaml"))


class TestBatchExecutor:
    def test_execute_dry_run(self, sample_manifest, capsys):
        """Dry run prints sources without executing."""
        from rag_engine.batch import execute_manifest

        result = execute_manifest(sample_manifest, dry_run=True)
        assert result["total_chunks"] == 0
        assert result["sources_processed"] == 0
        assert result["sources_total"] == 4

    def test_execute_dispatches_to_correct_ingestors(self, sample_manifest, mock_retriever):
        """Each source is dispatched to the correct ingestor."""
        from rag_engine.batch import execute_manifest

        with patch("rag_engine.batch.ExaSearchIngestor") as MockExa, \
             patch("rag_engine.batch.JinaReaderIngestor") as MockJina, \
             patch("rag_engine.batch.WebIngestor") as MockWeb:

            MockExa.return_value.ingest.return_value = 10
            MockJina.return_value.ingest.return_value = 5
            MockWeb.return_value.ingest.return_value = 3
            MockWeb.return_value.crawl.return_value = 8

            result = execute_manifest(sample_manifest, dry_run=False)

        MockExa.return_value.ingest.assert_called_once()
        MockJina.return_value.ingest.assert_called_once()
        MockWeb.return_value.crawl.assert_called_once()  # mode=crawl
        MockWeb.return_value.ingest.assert_called_once()  # default single URL
        assert result["total_chunks"] == 26
        assert result["sources_processed"] == 4

    def test_execute_continues_on_error(self, tmp_path, mock_retriever):
        """Errors in one source don't halt the batch."""
        manifest = {
            "manifest": {"name": "Error Test", "company": "transformfit", "data_type": "test"},
            "sources": [
                {"tool": "jina", "url": "https://example.com/fail"},
                {"tool": "jina", "url": "https://example.com/ok"},
            ],
        }
        path = tmp_path / "error_manifest.yaml"
        path.write_text(yaml.safe_dump(manifest, sort_keys=False))

        with patch("rag_engine.batch.JinaReaderIngestor") as MockJina:
            MockJina.return_value.ingest.side_effect = [Exception("fail"), 5]
            result = execute_manifest(path, dry_run=False)

        assert result["total_chunks"] == 5
        assert result["errors"] == 1
```

**Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_batch.py -v
```

Expected: FAIL -- `ModuleNotFoundError: No module named 'rag_engine.batch'`

**Step 3: Write batch.py**

Create `rag_engine/batch.py`:

```python
"""Batch manifest parser and executor for systematic data scraping."""
from __future__ import annotations
from pathlib import Path
import yaml

from rag_engine.ingestion.exa_search import ExaSearchIngestor
from rag_engine.ingestion.jina_reader import JinaReaderIngestor
from rag_engine.ingestion.playwright_scraper import PlaywrightIngestor
from rag_engine.ingestion.web import WebIngestor


def parse_manifest(path: Path) -> dict:
    """Parse a scrape manifest YAML file."""
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")
    with open(path) as f:
        return yaml.safe_load(f)


def execute_manifest(
    manifest_path: Path,
    dry_run: bool = False,
    resume: bool = False,
) -> dict:
    """Execute all sources in a manifest.

    Args:
        manifest_path: Path to the YAML manifest file.
        dry_run: If True, list sources without executing.
        resume: If True, skip already-ingested source_urls (not yet implemented).

    Returns:
        Summary dict with total_chunks, sources_processed, errors.
    """
    data = parse_manifest(manifest_path)
    meta = data.get("manifest", {})
    sources = data.get("sources", [])
    company = meta.get("company", "shared")
    data_type = meta.get("data_type", "market_research")

    if dry_run:
        print(f"DRY RUN: {meta.get('name', 'Unnamed')} ({len(sources)} sources)")
        for i, src in enumerate(sources, 1):
            tool = src.get("tool", "unknown")
            target = src.get("query") or src.get("url") or src.get("url_file", "")
            print(f"  [{i}/{len(sources)}] {tool}: {target}")
        return {"total_chunks": 0, "sources_processed": 0, "sources_total": len(sources), "errors": 0}

    # Lazy-create ingestors (share retriever instance)
    exa = ExaSearchIngestor()
    jina = JinaReaderIngestor()
    playwright = PlaywrightIngestor()
    web = WebIngestor()

    total_chunks = 0
    processed = 0
    errors = 0

    for i, src in enumerate(sources, 1):
        tool = src.get("tool", "firecrawl")
        target = src.get("query") or src.get("url") or src.get("url_file", "")
        print(f"  [{i}/{len(sources)}] {tool}: {target[:80]}...")

        try:
            if tool == "exa":
                count = exa.ingest(
                    source=src["query"],
                    company_id=company,
                    data_type=data_type,
                    num_results=src.get("num_results", 10),
                    search_type=src.get("search_type", "autoprompt"),
                )
            elif tool == "jina":
                count = jina.ingest(
                    source=src.get("url") or src.get("url_file", ""),
                    company_id=company,
                    data_type=data_type,
                )
            elif tool == "playwright":
                count = playwright.ingest(
                    source=src["url"],
                    company_id=company,
                    data_type=data_type,
                    wait_for=src.get("wait_for"),
                )
            elif tool == "firecrawl":
                mode = src.get("mode", "single")
                if mode == "crawl":
                    count = web.crawl(
                        source=src["url"],
                        company_id=company,
                        data_type=data_type,
                        max_pages=src.get("max_pages", 50),
                    )
                else:
                    count = web.ingest(
                        source=src.get("url") or src.get("url_file", ""),
                        company_id=company,
                        data_type=data_type,
                    )
            else:
                print(f"    Unknown tool: {tool}")
                errors += 1
                continue

            total_chunks += count
            processed += 1
            print(f"    -> {count} chunks")

        except Exception as e:
            print(f"    ERROR: {e}")
            errors += 1

    return {
        "total_chunks": total_chunks,
        "sources_processed": processed,
        "sources_total": len(sources),
        "errors": errors,
    }
```

**Step 4: Run tests**

```bash
python -m pytest tests/test_batch.py -v
```

Expected: 5 passed.

**Step 5: Commit**

```bash
git add rag_engine/batch.py tests/test_batch.py
git commit -m "feat: add batch manifest parser and executor"
```

---

### Task 8: Add scrape subcommands to susan_cli.py

**Files:**
- Modify: `scripts/susan_cli.py`
- Test: `tests/test_scraper_cli.py`

**Step 1: Write the failing test**

Create `tests/test_scraper_cli.py`:

```python
"""Tests for susan scrape CLI subcommands."""
from __future__ import annotations
from unittest.mock import patch, MagicMock
import pytest


class TestScrapeCLIParsing:
    def test_scrape_url_parsed(self):
        """susan scrape url <url> parses correctly."""
        from scripts.susan_cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["scrape", "url", "https://example.com", "--type", "exercise_science"])
        assert args.command == "scrape"
        assert args.scrape_command == "url"
        assert args.target == "https://example.com"
        assert args.type == "exercise_science"

    def test_scrape_search_parsed(self):
        """susan scrape search <query> parses correctly."""
        from scripts.susan_cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["scrape", "search", "progressive overload", "--num-results", "15"])
        assert args.scrape_command == "search"
        assert args.target == "progressive overload"
        assert args.num_results == 15

    def test_scrape_crawl_parsed(self):
        """susan scrape crawl <url> parses correctly."""
        from scripts.susan_cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["scrape", "crawl", "https://example.com", "--max-pages", "30"])
        assert args.scrape_command == "crawl"
        assert args.target == "https://example.com"
        assert args.max_pages == 30

    def test_scrape_batch_parsed(self):
        """susan scrape batch <manifest> parses correctly."""
        from scripts.susan_cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["scrape", "batch", "data/scrape_manifests/test.yaml", "--dry-run"])
        assert args.scrape_command == "batch"
        assert args.target == "data/scrape_manifests/test.yaml"
        assert args.dry_run is True

    def test_scrape_dynamic_parsed(self):
        """susan scrape dynamic <url> parses correctly."""
        from scripts.susan_cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["scrape", "dynamic", "https://example.com", "--wait-for", ".content"])
        assert args.scrape_command == "dynamic"
        assert args.wait_for == ".content"

    def test_scrape_plan_parsed(self):
        """susan scrape plan <topic> parses correctly."""
        from scripts.susan_cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["scrape", "plan", "exercise science", "--output", "out.yaml"])
        assert args.scrape_command == "plan"
        assert args.target == "exercise science"
        assert args.output == "out.yaml"

    def test_scrape_status_parsed(self):
        """susan scrape status parses correctly."""
        from scripts.susan_cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["scrape", "status", "--company", "transformfit"])
        assert args.scrape_command == "status"
        assert args.company == "transformfit"
```

**Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_scraper_cli.py -v
```

Expected: FAIL -- `scrape` subparser doesn't exist yet.

**Step 3: Add scrape subcommands to susan_cli.py**

Add these imports at the top of `scripts/susan_cli.py`:

```python
from pathlib import Path as _Path
```

Add the scrape subparser inside `build_parser()`, after the existing `bootstrap` subparser block (before the shell variants loop):

```python
    # ── scrape subcommand with nested sub-subcommands ───────────
    scrape = subparsers.add_parser("scrape", help="Scraper CLI for data collection")
    scrape_sub = scrape.add_subparsers(dest="scrape_command", required=True)

    # scrape url
    s_url = scrape_sub.add_parser("url")
    s_url.add_argument("target", help="URL to scrape")
    s_url.add_argument("--tool", choices=["firecrawl", "jina"], default="firecrawl")
    s_url.add_argument("--company", default=_default_company())
    s_url.add_argument("--type", default="market_research")
    s_url.add_argument("--agent", default=None)

    # scrape search
    s_search = scrape_sub.add_parser("search")
    s_search.add_argument("target", help="Exa search query")
    s_search.add_argument("--num-results", type=int, default=10)
    s_search.add_argument("--search-type", choices=["autoprompt", "keyword", "neural"], default="autoprompt")
    s_search.add_argument("--company", default=_default_company())
    s_search.add_argument("--type", default="market_research")
    s_search.add_argument("--agent", default=None)

    # scrape crawl
    s_crawl = scrape_sub.add_parser("crawl")
    s_crawl.add_argument("target", help="Base URL to deep crawl")
    s_crawl.add_argument("--max-pages", type=int, default=50)
    s_crawl.add_argument("--company", default=_default_company())
    s_crawl.add_argument("--type", default="market_research")
    s_crawl.add_argument("--agent", default=None)

    # scrape dynamic
    s_dynamic = scrape_sub.add_parser("dynamic")
    s_dynamic.add_argument("target", help="URL to scrape with Playwright")
    s_dynamic.add_argument("--wait-for", default=None, help="CSS selector to wait for")
    s_dynamic.add_argument("--company", default=_default_company())
    s_dynamic.add_argument("--type", default="market_research")
    s_dynamic.add_argument("--agent", default=None)

    # scrape batch
    s_batch = scrape_sub.add_parser("batch")
    s_batch.add_argument("target", help="Path to manifest YAML")
    s_batch.add_argument("--dry-run", action="store_true")
    s_batch.add_argument("--resume", action="store_true")
    s_batch.add_argument("--company", default=_default_company())

    # scrape plan
    s_plan = scrape_sub.add_parser("plan")
    s_plan.add_argument("target", help="Domain topic for Exa discovery")
    s_plan.add_argument("--num-results", type=int, default=20)
    s_plan.add_argument("--output", default=None, help="Output manifest YAML path")
    s_plan.add_argument("--company", default=_default_company())
    s_plan.add_argument("--type", default="market_research")

    # scrape status
    s_status = scrape_sub.add_parser("status")
    s_status.add_argument("--company", default=_default_company())

    scrape.set_defaults(func=cmd_scrape)
```

Add the `cmd_scrape` handler function before `build_parser()`:

```python
def cmd_scrape(args: argparse.Namespace) -> int:
    """Dispatch scrape subcommands."""
    subcmd = args.scrape_command

    if subcmd == "url":
        from rag_engine.ingestion.web import WebIngestor
        from rag_engine.ingestion.jina_reader import JinaReaderIngestor

        if args.tool == "jina":
            ingestor = JinaReaderIngestor()
        else:
            ingestor = WebIngestor()
        count = ingestor.ingest(
            source=args.target,
            company_id=args.company,
            data_type=args.type,
            agent_id=args.agent,
        )
        print(f"Ingested {count} chunks from {args.target}")

    elif subcmd == "search":
        from rag_engine.ingestion.exa_search import ExaSearchIngestor

        ingestor = ExaSearchIngestor()
        count = ingestor.ingest(
            source=args.target,
            company_id=args.company,
            data_type=args.type,
            agent_id=args.agent,
            num_results=args.num_results,
            search_type=args.search_type,
        )
        print(f"Ingested {count} chunks from Exa search: {args.target}")

    elif subcmd == "crawl":
        from rag_engine.ingestion.web import WebIngestor

        ingestor = WebIngestor()
        count = ingestor.crawl(
            source=args.target,
            company_id=args.company,
            data_type=args.type,
            agent_id=args.agent,
            max_pages=args.max_pages,
        )
        print(f"Crawled {count} chunks from {args.target}")

    elif subcmd == "dynamic":
        from rag_engine.ingestion.playwright_scraper import PlaywrightIngestor

        ingestor = PlaywrightIngestor()
        count = ingestor.ingest(
            source=args.target,
            company_id=args.company,
            data_type=args.type,
            agent_id=args.agent,
            wait_for=args.wait_for,
        )
        print(f"Ingested {count} chunks via Playwright from {args.target}")

    elif subcmd == "batch":
        from rag_engine.batch import execute_manifest

        result = execute_manifest(
            _Path(args.target),
            dry_run=args.dry_run,
            resume=args.resume,
        )
        _dump(result)

    elif subcmd == "plan":
        from rag_engine.ingestion.exa_search import ExaSearchIngestor
        from exa_py import Exa
        from susan_core.config import config

        client = Exa(api_key=config.exa_api_key)
        response = client.search(
            args.target,
            num_results=args.num_results,
            type="autoprompt",
            use_autoprompt=True,
        )

        manifest = {
            "manifest": {
                "name": args.target,
                "company": args.company,
                "data_type": args.type,
                "created": "2026-03-09",
                "priority": "medium",
            },
            "sources": [],
        }
        for result in response.results:
            manifest["sources"].append({
                "tool": "firecrawl",
                "url": result.url,
            })

        output = args.output or f"data/scrape_manifests/{args.target.replace(' ', '_')[:40]}.yaml"
        _Path(output).parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w") as f:
            yaml.safe_dump(manifest, f, sort_keys=False, allow_unicode=True)
        print(f"Manifest written to {output} ({len(manifest['sources'])} URLs)")

    elif subcmd == "status":
        from rag_engine.retriever import Retriever

        retriever = Retriever()
        # Query chunk counts by data_type for the company
        result = retriever.supabase.table("knowledge_chunks") \
            .select("data_type", count="exact") \
            .eq("company_id", args.company) \
            .execute()
        # Group by data_type
        counts: dict[str, int] = {}
        if result.data:
            for row in result.data:
                dt = row.get("data_type", "unknown")
                counts[dt] = counts.get(dt, 0) + 1
        total = sum(counts.values())
        _dump({"company": args.company, "total_chunks": total, "by_data_type": counts})

    return 0
```

**Step 4: Run tests**

```bash
python -m pytest tests/test_scraper_cli.py -v
```

Expected: 7 passed.

**Step 5: Run existing CLI tests to verify no regressions**

```bash
python -m pytest tests/ -v -k "not test_import_ux_design"
```

Expected: All existing tests still pass.

**Step 6: Commit**

```bash
git add scripts/susan_cli.py tests/test_scraper_cli.py
git commit -m "feat: add susan scrape CLI subcommands"
```

---

## Sprint 5: MCP Server Integration (Task 9)

### Task 9: Add scrape tools to MCP server

**Files:**
- Modify: `mcp_server/server.py`

**Step 1: Add scrape_url tool**

Add to `mcp_server/server.py` after the existing tool definitions:

```python
@mcp.tool()
def scrape_url(
    url: str,
    tool: str = "firecrawl",
    data_type: str = "market_research",
    company_id: str = "transformfit",
) -> str:
    """Scrape a single URL and ingest into Susan's knowledge base.

    Args:
        url: The URL to scrape
        tool: Scraping tool to use -- "firecrawl" or "jina"
        data_type: Knowledge category (exercise_science, ux_research, etc.)
        company_id: Company namespace
    """
    if tool == "jina":
        from rag_engine.ingestion.jina_reader import JinaReaderIngestor
        ingestor = JinaReaderIngestor()
    else:
        ingestor = WebIngestor()

    count = ingestor.ingest(source=url, company_id=company_id, data_type=data_type)
    return json.dumps({"url": url, "tool": tool, "chunks_ingested": count})


@mcp.tool()
def scrape_search(
    query: str,
    num_results: int = 10,
    data_type: str = "market_research",
    company_id: str = "transformfit",
) -> str:
    """Run Exa semantic search and ingest results into Susan's knowledge base.

    Finds thematically related content that keyword search would miss.

    Args:
        query: Natural language search query
        num_results: Number of results to discover and ingest
        data_type: Knowledge category
        company_id: Company namespace
    """
    from rag_engine.ingestion.exa_search import ExaSearchIngestor

    ingestor = ExaSearchIngestor()
    count = ingestor.ingest(
        source=query,
        company_id=company_id,
        data_type=data_type,
        num_results=num_results,
    )
    return json.dumps({"query": query, "num_results": num_results, "chunks_ingested": count})


@mcp.tool()
def scrape_batch(
    manifest_name: str,
    dry_run: bool = False,
    company_id: str = "transformfit",
) -> str:
    """Execute a batch scraping manifest from data/scrape_manifests/.

    Args:
        manifest_name: Manifest filename (e.g., "exercise_science.yaml")
        dry_run: If True, list sources without executing
        company_id: Company namespace
    """
    from rag_engine.batch import execute_manifest

    manifest_path = config.scrape_manifests_dir / manifest_name
    if not manifest_path.exists():
        return json.dumps({"error": f"Manifest not found: {manifest_name}"})

    result = execute_manifest(manifest_path, dry_run=dry_run)
    return json.dumps(result)
```

**Step 2: Commit**

```bash
git add mcp_server/server.py
git commit -m "feat: add scrape_url, scrape_search, scrape_batch MCP tools"
```

---

## Sprint 6: Priority 1 Manifests (Tasks 10-14)

### Task 10: Create exercise_science.yaml manifest

**Files:**
- Create: `data/scrape_manifests/exercise_science.yaml`

**Step 1: Write the manifest**

```yaml
manifest:
  name: "Exercise Science & Biomechanics"
  company: transformfit
  data_type: exercise_science
  created: 2026-03-09
  priority: high

sources:
  - tool: exa
    query: "progressive overload training protocols evidence-based strength"
    num_results: 15

  - tool: exa
    query: "exercise regression progression alternatives for common lifts"
    num_results: 10

  - tool: exa
    query: "form cues and common errors barbell squat bench press deadlift"
    num_results: 10

  - tool: exa
    query: "periodization models for intermediate lifters hypertrophy strength"
    num_results: 10

  - tool: exa
    query: "injury prevention protocols strength training shoulders knees lower back"
    num_results: 10

  - tool: exa
    query: "warm up protocols dynamic stretching activation drills before lifting"
    num_results: 8

  - tool: exa
    query: "RPE RIR autoregulation strength training programming"
    num_results: 10

  - tool: exa
    query: "training volume landmarks per muscle group hypertrophy research"
    num_results: 10

  - tool: jina
    url: "https://www.strongerbyscience.com/hypertrophy-range-fact-fiction/"

  - tool: jina
    url: "https://www.strongerbyscience.com/the-new-approach-to-training-volume/"

  - tool: jina
    url: "https://rpstrength.com/blogs/articles/training-volume-landmarks-for-muscle-growth"
```

**Step 2: Commit**

```bash
git add data/scrape_manifests/exercise_science.yaml
git commit -m "feat: add exercise_science scrape manifest"
```

---

### Task 11: Create ux_research.yaml manifest

**Files:**
- Create: `data/scrape_manifests/ux_research.yaml`

```yaml
manifest:
  name: "UX/UI Research & Design Patterns"
  company: transformfit
  data_type: ux_research
  created: 2026-03-09
  priority: high

sources:
  - tool: exa
    query: "mobile fitness app UX design patterns best practices 2025 2026"
    num_results: 15

  - tool: exa
    query: "onboarding flow design patterns mobile health apps reduce abandonment"
    num_results: 10

  - tool: exa
    query: "interaction design principles dark mode mobile apps premium feel"
    num_results: 10

  - tool: exa
    query: "workout logging UX design patterns mobile gym apps"
    num_results: 10

  - tool: exa
    query: "WCAG 2.2 accessibility guidelines mobile fitness applications"
    num_results: 8

  - tool: exa
    query: "design system architecture component library best practices React"
    num_results: 8

  - tool: jina
    url: "https://lawsofux.com/"

  - tool: jina
    url: "https://www.nngroup.com/articles/ten-usability-heuristics/"

  - tool: jina
    url: "https://www.nngroup.com/articles/onboarding/"
```

**Step 2: Commit**

```bash
git add data/scrape_manifests/ux_research.yaml
git commit -m "feat: add ux_research scrape manifest"
```

---

### Task 12: Create emotional_design.yaml manifest

**Files:**
- Create: `data/scrape_manifests/emotional_design.yaml`

```yaml
manifest:
  name: "Emotional Design, Motion Narrative & Feeling Data"
  company: transformfit
  data_type: emotional_design
  created: 2026-03-09
  priority: high

sources:
  - tool: exa
    query: "emotional design principles health wellness apps user engagement"
    num_results: 15

  - tool: exa
    query: "motion design principles micro-interactions mobile apps trust building"
    num_results: 10

  - tool: exa
    query: "moments of truth customer journey health fitness app first experience"
    num_results: 10

  - tool: exa
    query: "behavioral design felt safety body image sensitive inclusive fitness"
    num_results: 10

  - tool: exa
    query: "premium brand design restraint luxury digital product dark mode"
    num_results: 8

  - tool: exa
    query: "copy tone voice health wellness app motivational not preachy"
    num_results: 8

  - tool: jina
    url: "https://www.nngroup.com/articles/emotional-design/"

  - tool: jina
    url: "https://material.io/design/motion/understanding-motion.html"
```

**Step 2: Commit**

```bash
git add data/scrape_manifests/emotional_design.yaml
git commit -m "feat: add emotional_design scrape manifest"
```

---

### Task 13: Create competitive_intel.yaml manifest

**Files:**
- Create: `data/scrape_manifests/competitive_intel.yaml`

```yaml
manifest:
  name: "Competitive Intelligence"
  company: transformfit
  data_type: competitive_intel
  created: 2026-03-09
  priority: high

sources:
  - tool: exa
    query: "Fitbod app review workout generation AI personalization features"
    num_results: 10

  - tool: exa
    query: "Hevy workout tracker app features pricing UX review"
    num_results: 8

  - tool: exa
    query: "Future fitness app personal training AI coaching review"
    num_results: 8

  - tool: exa
    query: "Noom weight loss app behavioral psychology design review"
    num_results: 8

  - tool: exa
    query: "AI fitness app market landscape 2025 2026 personalization"
    num_results: 10

  - tool: exa
    query: "Peloton app subscription fitness features engagement retention"
    num_results: 8

  - tool: exa
    query: "fitness app subscription pricing models freemium conversion"
    num_results: 8
```

**Step 2: Commit**

```bash
git add data/scrape_manifests/competitive_intel.yaml
git commit -m "feat: add competitive_intel scrape manifest"
```

---

### Task 14: Create behavioral_economics.yaml manifest

**Files:**
- Create: `data/scrape_manifests/behavioral_economics.yaml`

```yaml
manifest:
  name: "Behavioral Economics & Retention"
  company: transformfit
  data_type: behavioral_economics
  created: 2026-03-09
  priority: high

sources:
  - tool: exa
    query: "gamification health fitness apps evidence-based engagement mechanics"
    num_results: 15

  - tool: exa
    query: "loss aversion fitness app retention design churn prevention"
    num_results: 10

  - tool: exa
    query: "habit formation BJ Fogg tiny habits fitness exercise adherence"
    num_results: 10

  - tool: exa
    query: "variable reward schedules mobile app engagement ethical design"
    num_results: 10

  - tool: exa
    query: "streak reward system design Duolingo Strava engagement case study"
    num_results: 10

  - tool: exa
    query: "notification timing psychology mobile health app re-engagement"
    num_results: 8

  - tool: jina
    url: "https://www.behavioraleconomics.com/resources/mini-encyclopedia-of-be/loss-aversion/"

  - tool: jina
    url: "https://yukaichou.com/gamification-examples/octalysis-complete-gamification-framework/"
```

**Step 2: Commit**

```bash
git add data/scrape_manifests/behavioral_economics.yaml
git commit -m "feat: add behavioral_economics scrape manifest"
```

---

## Sprint 7: Execute Priority 1 Scrapes (Task 15)

### Task 15: Run Priority 1 batch scrapes

This task requires real API keys configured in `.env`. Run each manifest:

```bash
cd /Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend

# Dry run first to preview
python scripts/susan_cli.py scrape batch data/scrape_manifests/exercise_science.yaml --dry-run
python scripts/susan_cli.py scrape batch data/scrape_manifests/ux_research.yaml --dry-run
python scripts/susan_cli.py scrape batch data/scrape_manifests/emotional_design.yaml --dry-run
python scripts/susan_cli.py scrape batch data/scrape_manifests/competitive_intel.yaml --dry-run
python scripts/susan_cli.py scrape batch data/scrape_manifests/behavioral_economics.yaml --dry-run

# Execute (requires EXA_API_KEY and FIRECRAWL_API_KEY in .env)
python scripts/susan_cli.py scrape batch data/scrape_manifests/exercise_science.yaml
python scripts/susan_cli.py scrape batch data/scrape_manifests/ux_research.yaml
python scripts/susan_cli.py scrape batch data/scrape_manifests/emotional_design.yaml
python scripts/susan_cli.py scrape batch data/scrape_manifests/competitive_intel.yaml
python scripts/susan_cli.py scrape batch data/scrape_manifests/behavioral_economics.yaml

# Verify
python scripts/susan_cli.py scrape status --company transformfit
```

Expected: ~1,000+ new chunks across the 5 Priority 1 data domains.

---

## Sprint 8: Priority 2-3 Manifests (Tasks 16-17)

### Task 16: Create remaining Priority 2 manifests

Create manifests for: `nutrition.yaml`, `sleep_recovery.yaml`, `user_research.yaml`, `ai_ml_research.yaml`. Follow the same pattern as Priority 1 manifests with Exa queries and Jina URLs specific to each domain.

### Task 17: Create Priority 3 manifests

Create manifests for: `market_research.yaml`, `growth_marketing.yaml`, `legal_compliance.yaml`, `technical_docs.yaml`, `security.yaml`. Same pattern.

---

## Summary

| Sprint | Tasks | What it delivers |
|--------|-------|-----------------|
| 1 | 1-2 | Dependencies, config, directory structure |
| 2 | 3-4 | Exa + Jina ingestors with tests |
| 3 | 5-6 | Playwright ingestor + Firecrawl crawl with tests |
| 4 | 7-8 | Batch manifest system + CLI subcommands with tests |
| 5 | 9 | MCP server integration |
| 6 | 10-14 | Priority 1 scrape manifests (5 domains) |
| 7 | 15 | Execute Priority 1 scrapes (~1,000+ chunks) |
| 8 | 16-17 | Priority 2-3 manifests + execution |

Total: 17 tasks across 8 sprints. Sprints 1-5 are infrastructure (build once). Sprints 6-8 are data collection (run repeatedly as sources grow).
