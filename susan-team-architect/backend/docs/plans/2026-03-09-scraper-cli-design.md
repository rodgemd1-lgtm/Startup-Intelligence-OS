# Scraper CLI Design -- Susan Intelligence OS

**Date:** 2026-03-09
**Status:** Implemented
**Location:** Susan backend (`susan-team-architect/backend/`)

---

## Purpose

A unified scraper CLI (`susan scrape`) that builds a data-enriched knowledge repository for TransformFit. Uses four scraping tools (Exa, Firecrawl, Playwright, Jina) to systematically fill data gaps identified in `dataset_requirements_master.md`. All data flows into Susan's pgvector knowledge base for agent access via `search_knowledge`.

## CLI Interface

```
susan scrape url <url>              # Single URL (Firecrawl or Jina)
susan scrape search "<query>"       # Exa semantic search + ingest
susan scrape crawl <url>            # Firecrawl deep crawl (follow links)
susan scrape dynamic <url>          # Playwright for JS-heavy pages
susan scrape batch <manifest.yaml>  # Batch execute from manifest
susan scrape plan "<topic>"         # Exa discovery -> output manifest
susan scrape status                 # Chunk counts by data_type
```

## Architecture

### Ingestor Modules (rag_engine/ingestion/)

| Module | Tool | Use Case |
|--------|------|----------|
| `web.py` | Firecrawl | Standard web pages, deep crawls |
| `exa_search.py` | Exa | Semantic discovery of related content |
| `jina_reader.py` | Jina Reader API | Clean text from cluttered pages |
| `playwright_scraper.py` | Playwright | Dynamic/JS-heavy pages |

All extend `BaseIngestor`. Pattern: scrape -> markdown -> chunk (500 tokens) -> embed (Voyage) -> store (pgvector).

### Batch Manifest System (rag_engine/batch.py)

YAML manifests in `data/scrape_manifests/` define batch scraping jobs:

```yaml
manifest:
  name: "Exercise Science Core"
  company: transformfit
  data_type: exercise_science
sources:
  - tool: exa
    query: "progressive overload protocols"
    num_results: 10
  - tool: firecrawl
    url: https://example.com/article
```

Features: `--dry-run` preview, `--resume` skip duplicates.

### Domain Manifests (8 files)

1. `exercise_science.yaml` -- Movement patterns, periodization, form cues
2. `nutrition.yaml` -- Macros, supplements, meal timing
3. `sleep_recovery.yaml` -- Sleep, HRV, recovery modalities
4. `behavioral_economics.yaml` -- Gamification, loss aversion, habits
5. `competitive_intel.yaml` -- Fitbod, Noom, Peloton, Hevy, Future
6. `ai_fitness_tech.yaml` -- AI coaching, ML, wearables, NLP
7. `ux_patterns.yaml` -- Mobile UX, onboarding, dark mode, haptics
8. `sports_psychology.yaml` -- SDT, motivation, identity, mindset

## Configuration

API keys in `.env`: `EXA_API_KEY`, `JINA_API_KEY`, `FIRECRAWL_API_KEY`
Config class: `susan_core/config.py` (already has all fields)

## Dependencies

Added to `pyproject.toml`: `exa-py>=1.0.0`, `playwright>=1.49.0`, `markdownify>=0.14.0`

Post-install: `playwright install chromium`
