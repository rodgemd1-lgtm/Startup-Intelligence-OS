---
name: scrape
description: "Intelligent multi-engine web scraping that discovers, extracts, and organizes information into folders and optionally ingests into Susan's RAG. Use this skill whenever the user wants to scrape the web, research a topic from external sources, pull information from URLs, build a knowledge corpus, populate RAG data, gather competitive intelligence, or says anything like 'go find me information about X'. Triggers on: /scrape, web research, gather sources, pull articles, scrape URLs, build corpus, ingest knowledge, competitive research, find me everything about."
argument-hint: '"topic or URL" [--company company_id] [--data-type type] [--depth shallow|deep|exhaustive] [--ingest] [--engines exa,firecrawl,brave,jina,apify]'
---

# Intelligent Multi-Engine Scrape

Orchestrate 5 MCP scraping engines to discover, extract, and organize web content into structured folders. Optionally ingest into Susan's RAG knowledge base.

## Your 5 Engines

| Engine | Strength | When to use |
|--------|----------|-------------|
| **Exa** | Semantic discovery — finds content by meaning | Discovery phase: "what exists about X?" |
| **Brave** | Keyword search with independent index | Discovery phase: recent articles, news, niche sources |
| **Firecrawl** | Full-page extraction with JS rendering | Extraction phase: clean markdown from any URL |
| **Jina** | Reader fallback + academic content | Extraction phase: when Firecrawl hits limits |
| **Apify** | Platform-specific automation (social, app stores) | Platform data: reviews, social posts, forums |

## Parse the User's Request

Extract from the user's input:

1. **Topic** — What they want to research (required)
2. **Company** — Which company namespace, defaults to `founder-intelligence-os`
3. **Data type** — RAG category (exercise_science, market_research, ai_ml_research, etc.), infer from topic if not specified
4. **Depth** — How thorough:
   - `shallow` (default): 1 discovery engine + extraction of top 5 URLs
   - `deep`: 2 discovery engines + extraction of top 15 URLs
   - `exhaustive`: All engines + extraction of 25+ URLs + platform data
5. **Specific URLs** — If they gave URLs, skip discovery and go straight to extraction
6. **Ingest flag** — Whether to push results into Susan's RAG (if `--ingest` or user says "add to RAG / knowledge base")
7. **Engine preferences** — Specific engines to use, or auto-select based on depth

## Execution Workflow

### Phase 1: Discovery (skip if user provided specific URLs)

Run discovery engines in parallel based on depth:

**Shallow (1 engine):**
- Exa `web_search_exa` with the topic as a semantic query

**Deep (2 engines):**
- Exa `web_search_exa` — semantic discovery
- Brave `brave_web_search` — keyword search for recent content

**Exhaustive (all discovery + platform):**
- Exa `deep_search_exa` — deep multi-hop research
- Brave `brave_web_search` — broad keyword coverage
- Apify — platform-specific (app store reviews, Reddit, social media) if the topic warrants it

Collect all discovered URLs into a deduplicated list. Rank by relevance.

### Phase 2: Extraction

For each URL from discovery (or user-provided URLs):

1. **Primary:** Use Firecrawl to scrape the URL to clean markdown
2. **Fallback:** If Firecrawl fails or times out, use Jina reader
3. **Save** each extracted article as a markdown file in the output folder

Naming convention for files: `{domain}--{slug}.md` (e.g., `pubmed-gov--progressive-overload-meta-analysis.md`)

### Phase 3: Organization

Create this folder structure:

```
.claude/agent-memory/research/{topic-slug}/
  manifest.json        # Metadata: what was scraped, when, sources, engines used
  summary.md           # AI-generated synthesis of all findings
  sources/
    {domain}--{slug}.md   # Individual extracted articles
    {domain}--{slug}.md
    ...
```

**manifest.json structure:**
```json
{
  "topic": "the research topic",
  "created": "2026-03-10T14:30:00Z",
  "depth": "deep",
  "engines_used": ["exa", "brave", "firecrawl", "jina"],
  "company_id": "founder-intelligence-os",
  "data_type": "market_research",
  "ingested_to_rag": false,
  "sources": [
    {
      "url": "https://example.com/article",
      "title": "Article Title",
      "domain": "example.com",
      "discovered_by": "exa",
      "extracted_by": "firecrawl",
      "file": "sources/example-com--article.md",
      "word_count": 2450,
      "relevance": "high"
    }
  ],
  "stats": {
    "urls_discovered": 23,
    "urls_extracted": 15,
    "total_words": 45000,
    "extraction_failures": 2
  }
}
```

**summary.md** — After all extraction is complete, read through all extracted articles and write a synthesis:
- Key themes and findings across all sources
- Notable statistics or data points
- Gaps identified (what the research didn't cover)
- Recommended next steps or deeper dives
- Source quality assessment

### Phase 4: RAG Ingestion (optional, only if --ingest or user requests)

If the user wants results in Susan's RAG:

1. For each extracted source file, use `mcp__susan-intelligence__scrape_url` with the original URL
2. Or use `mcp__susan-intelligence__ingest_url` for direct ingestion
3. Set the `data_type` appropriately
4. Set the `company_id` to the specified company
5. Update manifest.json with `"ingested_to_rag": true` and chunk counts

## Data Type Reference

Common data types for the `--data-type` flag or auto-inference:

| Data Type | When to use |
|-----------|-------------|
| `exercise_science` | Fitness, training, biomechanics, programming |
| `nutrition` | Diet, macros, supplements, meal planning |
| `sports_psychology` | Motivation, mindset, adherence, identity |
| `sleep_recovery` | Sleep, recovery, fatigue, readiness |
| `behavioral_economics` | Nudges, loss aversion, framing, retention |
| `market_research` | Industry reports, trends, market sizing |
| `competitive_intel` | Competitor analysis, app reviews, feature comparison |
| `ai_ml_research` | AI tools, models, techniques, papers |
| `ux_research` | UX patterns, design systems, user research |
| `growth_marketing` | Acquisition, viral loops, content strategy |
| `legal_compliance` | Health tech regulation, privacy, disclaimers |
| `technical_docs` | APIs, architecture, engineering best practices |
| `user_research` | User interviews, surveys, personas |
| `community` | Social features, belonging, creator-led |
| `gamification` | Points, streaks, progression, rewards |
| `content_strategy` | Content marketing, SEO, editorial planning |
| `security` | App security, cloud architecture, threat modeling |
| `business_strategy` | Business models, pricing, fundraising |
| `finance` | Unit economics, budgets, runway |
| `partnerships` | Distribution deals, integrations, alliances |
| `expert_knowledge` | Domain expert insights, protocols |

## Output to User

After completion, present a structured summary:

```
Scrape complete: "{topic}"

Discovery: {N} URLs found via {engines}
Extraction: {N}/{M} articles saved ({total_words} words)
Failures: {N} URLs failed extraction
Folder: .claude/agent-memory/research/{topic-slug}/

Top sources:
1. {title} — {domain} ({word_count} words)
2. {title} — {domain} ({word_count} words)
3. {title} — {domain} ({word_count} words)

{If ingested}: Ingested {N} chunks into Susan RAG ({company_id}/{data_type})

Summary saved to: .claude/agent-memory/research/{topic-slug}/summary.md
```

## Examples

**Example 1: Quick topic research**
```
/scrape "AI video generation tools 2026"
```
Shallow depth. Exa semantic search. Extract top 5 articles. Save to research folder.

**Example 2: Deep competitive intelligence**
```
/scrape "Fitbod app features and user reviews" --depth deep --data-type competitive_intel --ingest
```
Deep depth. Exa + Brave discovery. Apify for App Store reviews. Extract 15+ sources. Ingest to RAG.

**Example 3: Specific URLs**
```
/scrape https://arxiv.org/abs/2401.12345 https://blog.example.com/ai-fitness --data-type ai_ml_research --ingest
```
Skip discovery. Extract both URLs via Firecrawl/Jina. Ingest into RAG.

**Example 4: Exhaustive domain research**
```
/scrape "behavioral nudges in fitness apps" --depth exhaustive --company transformfit --ingest
```
All engines. 25+ sources. Full synthesis. Ingest to RAG under transformfit namespace.

## Error Handling

- If an engine is unavailable, skip it and note in manifest
- If extraction fails for a URL, log it in manifest and try the fallback engine
- If all extraction fails for a URL, note it as a failure and move on
- Never block the entire scrape because one source failed
- If Exa returns 0 results (known issue with some queries), fall back to Brave automatically

## Engine Selection Logic

When the user doesn't specify engines, auto-select based on the topic:

- **Academic/research topics** → Exa (semantic) + Jina (academic papers)
- **Current events/news** → Brave (recent indexing) + Firecrawl
- **Competitor/app analysis** → Brave + Apify (app stores, social)
- **Technical documentation** → Exa (semantic) + Firecrawl (JS-rendered docs)
- **General knowledge building** → Exa + Brave + Firecrawl (full pipeline)
