# Susan Scraper CLI -- Design Document

> Date: 2026-03-09
> Status: Design
> Location: Inside `susan-team-architect/backend`

---

## Problem

Susan has 7,367 chunks for TransformFit but the `dataset_requirements_master.md` shows massive gaps across 12+ data domains. The current ingestion infrastructure is Firecrawl-only (`rag_engine/ingestion/web.py`), one URL at a time, no semantic discovery, no dynamic page support, no clean text extraction. Building the TransformFit app requires a deep, referenceable data repository that agents can pull from during product design, workout programming, AI protocol development, and UX decisions.

What running the real scraper would add:

- **Exa semantic search** -- finds thematically related content that keyword search misses
- **Firecrawl deep crawl** -- extracts full article content, follows internal links, gets structured data from pages that return partial content to simple fetches
- **Playwright** -- can navigate dynamic pages (SPAs, paywalled previews, infinite scroll)
- **Jina AI reader mode** -- clean text extraction from cluttered pages

## Decision

Extend `susan_cli.py` with a `susan scrape` subcommand. New ingestor modules in `rag_engine/ingestion/`. Batch manifests in `data/scrape_manifests/`. All scraped data flows directly into Susan's pgvector knowledge base.

---

## 1. CLI Interface

```
susan scrape url <url>                     # Single URL
  --tool firecrawl|jina                    # Default: firecrawl
  --company transformfit
  --type exercise_science

susan scrape search "<query>"              # Exa semantic search -> scrape top N
  --num-results 10
  --company transformfit
  --type market_research
  --category autoprompt|keyword|neural     # Exa search type. Default: autoprompt

susan scrape crawl <url>                   # Firecrawl deep crawl (follows links)
  --max-pages 50
  --company transformfit
  --type exercise_science

susan scrape dynamic <url>                 # Playwright for JS-heavy pages
  --wait-for "selector"                    # CSS selector to wait for before extract
  --company transformfit
  --type competitive_intel

susan scrape batch <manifest.yaml>         # Batch execution from manifest file
  --dry-run                                # Preview: list URLs and tools, don't scrape
  --resume                                 # Skip already-ingested source_urls

susan scrape plan "<domain topic>"         # Exa discovery -> output manifest YAML
  --num-results 20
  --output data/scrape_manifests/topic.yaml
  --company transformfit
  --type exercise_science

susan scrape status                        # Report: chunks by data_type, last ingest
  --company transformfit
```

All commands share: `--company` (default from `SUSAN_DEFAULT_COMPANY`), `--type` (data_type taxonomy), `--agent` (optional agent_id tag).

### Shell variants

For MCP integration, shell variants follow existing pattern: `susan shell-scrape-url`, `susan shell-scrape-search`, etc.

---

## 2. New Ingestor Modules

All inherit from `BaseIngestor` and follow the existing pattern: scrape -> markdown -> chunk -> embed -> store.

### 2a. `rag_engine/ingestion/exa_search.py`

```python
class ExaSearchIngestor(BaseIngestor):
    """Semantic search via Exa, then extract content from top results."""

    def ingest(self, source: str, company_id="shared",
               data_type="market_research", num_results=10,
               search_type="autoprompt", **kwargs) -> int:
        # 1. Exa search(query=source, num_results, type=search_type,
        #              use_autoprompt=True, text=True)
        # 2. For each result: extract text content (Exa returns it inline)
        # 3. chunk_markdown -> _make_chunks -> retriever.store_chunks
        # 4. Return total chunks stored
```

**Exa provides content inline** with search results (when `text=True`), so we don't need a second fetch step for most results. For results where Exa returns only a snippet, fall back to Jina reader.

### 2b. `rag_engine/ingestion/jina_reader.py`

```python
class JinaReaderIngestor(BaseIngestor):
    """Clean text extraction via Jina AI reader mode."""

    JINA_READER_URL = "https://r.jina.ai/"

    def ingest(self, source: str, company_id="shared",
               data_type="market_research", **kwargs) -> int:
        # 1. GET https://r.jina.ai/{url}
        #    Headers: Accept: text/markdown, Authorization: Bearer {jina_api_key}
        # 2. Response is clean markdown
        # 3. chunk_markdown -> _make_chunks -> retriever.store_chunks
```

Jina reader is free for moderate volume (no API key needed for <100 req/day). For batch runs, use an API key to avoid rate limits.

### 2c. `rag_engine/ingestion/playwright_scraper.py`

```python
class PlaywrightIngestor(BaseIngestor):
    """Dynamic page scraping via Playwright for JS-heavy sites."""

    def ingest(self, source: str, company_id="shared",
               data_type="market_research",
               wait_for: str | None = None, **kwargs) -> int:
        # 1. Launch headless Chromium via playwright
        # 2. Navigate to URL, wait for wait_for selector (or networkidle)
        # 3. Extract page.content() -> HTML
        # 4. Convert HTML to markdown (html2text or markdownify)
        # 5. chunk_markdown -> _make_chunks -> retriever.store_chunks
```

Playwright is for sites that require JS rendering (SPAs, dynamically loaded content, infinite scroll pages). Most fitness/research sites won't need this, but it's essential for competitor app pages and some data portals.

### 2d. Enhanced `rag_engine/ingestion/web.py` (Firecrawl)

Add `crawl` mode to existing WebIngestor:

```python
def crawl(self, source: str, company_id="shared",
          data_type="market_research", max_pages=50, **kwargs) -> int:
    # 1. app.crawl(url=source, limit=max_pages)
    # 2. For each page in results: extract markdown
    # 3. chunk_markdown -> _make_chunks -> retriever.store_chunks
```

Firecrawl's `crawl` follows internal links and returns structured content for entire sites. This is for deep-scraping documentation sites, research hubs, etc.

---

## 3. Batch Manifest System

Manifests are YAML files in `data/scrape_manifests/` that define batch scraping jobs.

### Manifest schema:

```yaml
# data/scrape_manifests/exercise_science.yaml
manifest:
  name: "Exercise Science & Biomechanics"
  company: transformfit
  data_type: exercise_science
  created: 2026-03-09
  priority: high

sources:
  # Exa semantic searches (discover URLs)
  - tool: exa
    query: "progressive overload protocols strength training evidence-based"
    num_results: 15
    search_type: autoprompt

  - tool: exa
    query: "exercise regression progression alternatives rehabilitation"
    num_results: 10

  # Direct URLs (Firecrawl)
  - tool: firecrawl
    url: "https://www.nsca.com/education/articles/"
    mode: crawl
    max_pages: 30

  # Jina for clean extraction from cluttered pages
  - tool: jina
    url: "https://www.acsm.org/education-resources/trending-topics-resources"

  # Playwright for dynamic content
  - tool: playwright
    url: "https://exrx.net/Lists/Directory"
    wait_for: ".exercise-list"

  # URL lists (file reference)
  - tool: firecrawl
    url_file: "data/scrape_manifests/urls/exercise_science_urls.txt"
```

### Execution behavior:

- `susan scrape batch exercise_science.yaml` processes all sources sequentially
- `--dry-run` lists what would be scraped without doing it
- `--resume` checks `source_url` in existing chunks and skips already-ingested URLs
- Progress logged to stdout: `[3/12] Exa search: "progressive overload..." -> 47 chunks`
- Errors logged but don't halt batch: `[WARN] Failed: https://... (403 Forbidden)`

---

## 4. TransformFit Data Domain Manifests

Based on `dataset_requirements_master.md`, create manifests for each domain. Priority order based on what informs the UI build first:

### Priority 1 (UI-informing -- scrape first)

| Manifest | data_type | Current chunks | Target | Why first |
|----------|-----------|---------------|--------|-----------|
| `exercise_science.yaml` | exercise_science | 118 | 500+ | Workout programming, exercise DB, form cues |
| `ux_research.yaml` | ux_research | 25 | 200+ | UI patterns, onboarding flows, interaction design |
| `emotional_design.yaml` | emotional_design | 0 | 150+ | Motion narrative, moments of truth, feeling states |
| `competitive_intel.yaml` | competitive_intel | 0 | 100+ | Competitor UX, features, pricing |
| `behavioral_economics.yaml` | behavioral_economics | 186 | 300+ | Gamification, retention, habit formation |

### Priority 2 (Product intelligence)

| Manifest | data_type | Current chunks | Target |
|----------|-----------|---------------|--------|
| `nutrition.yaml` | nutrition | 0 | 200+ |
| `sleep_recovery.yaml` | sleep_recovery | 9 | 100+ |
| `user_research.yaml` | user_research | 282 | 400+ |
| `ai_ml_research.yaml` | ai_ml_research | 35 | 150+ |

### Priority 3 (Business strategy)

| Manifest | data_type | Current chunks | Target |
|----------|-----------|---------------|--------|
| `market_research.yaml` | market_research | 12 | 100+ |
| `growth_marketing.yaml` | growth_marketing | 23 | 100+ |
| `legal_compliance.yaml` | legal_compliance | 0 | 80+ |
| `technical_docs.yaml` | technical_docs | 0 | 100+ |
| `security.yaml` | security | 0 | 50+ |

### Seed URL lists

Each manifest references specific sources from the dataset requirements doc. For example, `exercise_science.yaml` would include:
- Exa searches for progressive overload, movement patterns, injury prevention, form cues
- Firecrawl crawls of NSCA articles, ACE resources, ExRx.net
- Jina reads of ACSM guidelines, PubMed abstracts
- Playwright for dynamic exercise databases

The `plan` command generates initial manifests from Exa discovery:
```
susan scrape plan "exercise science progressive overload evidence-based protocols" \
  --num-results 20 --output data/scrape_manifests/exercise_science.yaml
```

---

## 5. Dependencies and Configuration

### New Python packages (add to `pyproject.toml`):

```toml
dependencies = [
    # ... existing ...
    "exa-py>=1.0.0",           # Exa semantic search
    "playwright>=1.49.0",       # Dynamic page scraping
    "markdownify>=0.14.0",      # HTML -> Markdown conversion (for Playwright)
]
```

Jina reader uses raw HTTP (already have `httpx`). No additional package needed.

### New environment variables (add to `.env` and `.env.example`):

```
EXA_API_KEY=exa-...
JINA_API_KEY=jina_...    # Optional: only needed for >100 req/day
```

Playwright requires a one-time browser install: `playwright install chromium`

### Config additions (`susan_core/config.py`):

```python
exa_api_key: str = os.environ.get("EXA_API_KEY", "")
jina_api_key: str = os.environ.get("JINA_API_KEY", "")
scrape_manifests_dir: Path = base_dir / "data" / "scrape_manifests"
```

---

## 6. Integration with Susan Workflows

### How agents access scraped data:

Scraped content goes into the same pgvector `knowledge_chunks` table that all Susan agents query via `search_knowledge`. No special integration needed -- agents automatically get richer results as the repository grows.

### Tagging and traceability:

Every chunk gets:
- `company_id`: "transformfit" (or "shared" for cross-company data)
- `data_type`: taxonomized (exercise_science, ux_research, etc.)
- `source`: prefixed by tool (e.g., `exa:query:progressive overload`, `firecrawl:https://...`, `jina:https://...`, `playwright:https://...`)
- `source_url`: the original URL
- `metadata`: title, scraped_at timestamp, tool used, manifest name

### Deduplication:

Before storing, check if `source_url` already exists for the same `company_id` and `data_type`. The `--resume` flag on batch mode uses this to skip already-ingested URLs. For re-scraping (content updates), add a `--force` flag that deletes existing chunks for that source_url before re-ingesting.

### MCP server integration:

Add `scrape_url`, `scrape_search`, `scrape_batch` as MCP tools in `mcp_server/` so Claude Code agents can trigger scraping directly from conversations. This follows the existing `search_knowledge`, `company_status` MCP tool pattern.

---

## 7. File Structure

```
susan-team-architect/backend/
  rag_engine/
    ingestion/
      base.py            # (existing)
      web.py             # (enhance: add crawl method)
      exa_search.py      # NEW
      jina_reader.py     # NEW
      playwright_scraper.py  # NEW
      appstore.py        # (existing)
      arxiv_ingestor.py  # (existing)
      reddit.py          # (existing)
      ...

  scripts/
    susan_cli.py         # (enhance: add scrape subcommands)
    ...

  data/
    scrape_manifests/    # NEW directory
      exercise_science.yaml
      ux_research.yaml
      emotional_design.yaml
      competitive_intel.yaml
      behavioral_economics.yaml
      nutrition.yaml
      sleep_recovery.yaml
      user_research.yaml
      ai_ml_research.yaml
      market_research.yaml
      growth_marketing.yaml
      legal_compliance.yaml
      technical_docs.yaml
      security.yaml
      urls/              # URL list files referenced by manifests
        exercise_science_urls.txt
        ...

  mcp_server/
    ...                  # (enhance: add scrape tools)

  tests/
    test_scraper_cli.py      # NEW
    test_exa_ingestor.py     # NEW
    test_jina_ingestor.py    # NEW
    test_playwright_ingestor.py  # NEW
```

---

## 8. Execution Strategy

### Phase 1: Core infrastructure (build the CLI + ingestors)
1. Add dependencies (exa-py, playwright, markdownify)
2. Create `exa_search.py` ingestor
3. Create `jina_reader.py` ingestor
4. Create `playwright_scraper.py` ingestor
5. Enhance `web.py` with crawl method
6. Add `scrape` subcommands to `susan_cli.py`
7. Create batch manifest parser and executor
8. Add `scrape` MCP tools
9. Tests for each ingestor and the CLI

### Phase 2: Data collection (populate the repository)
10. Create Priority 1 manifests (exercise_science, ux_research, emotional_design, competitive_intel, behavioral_economics)
11. Run Priority 1 batch scrapes (target: 1,000+ new chunks)
12. Create Priority 2 manifests
13. Run Priority 2 batch scrapes (target: 800+ new chunks)
14. Create Priority 3 manifests
15. Run Priority 3 batch scrapes (target: 500+ new chunks)

### Phase 3: Continuous enrichment
16. Add `susan scrape status` reporting
17. Set up manifest refresh cadence (monthly re-scrape of key sources)
18. Document the scraper CLI in Susan's README

Target: ~2,300+ new chunks across 14 data domains, bringing TransformFit from 7,367 to ~9,700+ chunks.

---

## 9. Cost and Rate Limit Considerations

| Tool | Pricing | Rate limits | Notes |
|------|---------|-------------|-------|
| Exa | $1/1000 searches | 1000/month free tier | Autoprompt best for discovery |
| Firecrawl | $0.002/page (crawl) | 500 pages/month free | Already have API key |
| Playwright | Free (self-hosted) | None | Just needs `chromium` installed |
| Jina Reader | Free (<100/day) | 100 req/day free | API key lifts to 1000/day |
| Voyage embeddings | ~$0.06/1M tokens | n/a | Already paid, cost is marginal |

Estimated cost for full Priority 1-3 scraping: ~$15-30 total (well within $200/month budget).
