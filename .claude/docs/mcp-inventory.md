# MCP Server Inventory

Current state of all MCP servers connected to the Startup Intelligence OS.

**Last audited:** 2026-03-18

## Connected & Operational

| MCP Server | Tools Available | Primary Use | V-Level |
|-----------|----------------|-------------|---------|
| **susan-intelligence** | search_knowledge, run_agent, route_task, team_manifest, etc. | Susan's RAG, agents, planning | V1 |
| **github** | create_issue, create_pull_request, search_code, etc. | Repo operations, PR management | V1 |
| **context7** | resolve-library-id, query-docs | Up-to-date library documentation | V1 |
| **playwright** | browser_navigate, browser_snapshot, browser_click, etc. | Browser automation, E2E testing | V1 |
| **brave-search** | brave_web_search, brave_local_search | Web search, local business search | V1 |
| **exa** | web_search_exa, deep_search_exa, company_research_exa | Advanced web search, company research | V1 |
| **tavily** | tavily_search, tavily_extract, tavily_research | Search, extraction, deep research | V1 |
| **firecrawl** | firecrawl_scrape, firecrawl_crawl, firecrawl_search | Web scraping, crawling | V1 |
| **brightdata** | scrape_as_markdown, search_engine | Proxy-powered scraping | V1 |
| **trendradar** | get_latest_news, search_news, analyze_sentiment, etc. | Competitive intelligence, news monitoring | V1* |
| **gpt-researcher** | get_report | Autonomous deep research | V1 |
| **deep-research** | octagon-deep-research-agent | Multi-step research agent | V1 |
| **jina** | read_webpage, search_web, fact_check | Web reading, fact checking | V1 |
| **apify** | call-actor, search-actors | Web scraping actors | V1 |
| **gemini** | generate_text, analyze_media, generate_image | Multi-modal AI | V1 |
| **quickchart** | generate_chart, download_chart | Data visualization | V1 |
| **youtube-transcript** | get_transcript | Video content extraction | V1 |
| **notion-custom** | notion_pages, notion_database, notion_blocks | Notion integration | V1 |
| **xcode-build** | build_run_sim, test_sim, screenshot, etc. | iOS/macOS development | V1 |
| **google-drive** | google_drive_fetch, google_drive_search | Google Drive access | V1 |
| **scheduled-tasks** | create_scheduled_task, list_scheduled_tasks | Task scheduling | V1 |
| **promptx** | discover, recall, remember, action | Prompt management | V1 |
| **Claude Preview** | preview_start, preview_screenshot, etc. | Dev server preview | V1 |
| **Claude in Chrome** | navigate, read_page, computer, etc. | Browser control | V1 |
| **taskmaster** | get_tasks, parse_prd, expand_task | Task management | V1 |
| **mcp-registry** | search_mcp_registry, suggest_connectors | MCP discovery | V1 |

## V2 MCP Additions (When Needed)

| MCP Server | Purpose | Install When |
|-----------|---------|-------------|
| Qdrant | Custom vector embeddings | When RAG needs custom embedding search beyond Supabase |
| Kreuzberg | 88+ format document ingestion | When document pipeline is built |
| GenAI Toolbox | Database connector (BigQuery, Postgres) | When direct DB queries are needed |
| n8n | Visual workflow automation | When automated agent chains are proven |

## Notes
- TrendRadar (*) is connected and has tools available but needs workflow integration testing
- Susan Intelligence is the only project-local MCP (in `.mcp.json`); all others are global
- Total operational MCP servers: **25+**
- V1 target was 5 MCP servers — we have 25+. V1 criteria exceeded.
