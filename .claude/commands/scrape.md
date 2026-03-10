---
description: Intelligent multi-engine web scraping — discover, extract, and organize information from the web
argument-hint: '"topic or URL" [--depth shallow|deep|exhaustive] [--company company_id] [--data-type type] [--ingest] [--engines exa,firecrawl,brave,jina,apify]'
---

Use the `scrape` skill to handle this request.

**User input:** $ARGUMENTS

Follow the scrape skill workflow:
1. Parse the user's request (topic, depth, company, data type, URLs, ingest flag, engines)
2. Run Phase 1: Discovery (unless specific URLs were given)
3. Run Phase 2: Extraction (Firecrawl primary, Jina fallback)
4. Run Phase 3: Organization (folder structure + manifest + summary)
5. Run Phase 4: RAG Ingestion (only if --ingest flag or user requested)
6. Present the structured completion summary
