# Auto-Research Dispatch Patterns

Reference for parallel research agent dispatch. Used by the Research-First Pipeline skill and any workflow that needs multi-source research.

## Core Pattern: Parallel MCP Research

```
# Launch 4 researchers in parallel using Agent tool with run_in_background: true
# Each gets a bounded question set and specific output format

Agent(
  subagent_type="researcher-web",
  description="Web research for {topic}",
  model="sonnet",
  run_in_background=true,
  prompt="Search for: {questions}. Use brave_web_search or tavily_search. Cite all sources with URLs. Return structured findings."
)

Agent(
  subagent_type="researcher-reddit",
  description="Reddit research for {topic}",
  model="haiku",
  run_in_background=true,
  prompt="Find Reddit discussions about: {questions}. Focus on lived experience, complaints, and use cases. Return themes with example quotes."
)

Agent(
  subagent_type="researcher-arxiv",
  description="Academic research for {topic}",
  model="sonnet",
  run_in_background=true,
  prompt="Search arXiv and academic sources for: {questions}. Focus on methods, benchmarks, and recent advances. Return structured findings."
)

Agent(
  subagent_type="researcher-appstore",
  description="App store research for {topic}",
  model="haiku",
  run_in_background=true,
  prompt="Analyze app store listings for: {questions}. Focus on reviews, ratings, feature gaps, and competitor positioning. Return structured findings."
)
```

## MCP Tool Routing

| Research Type | Primary MCP | Fallback MCP | Model |
|--------------|------------|-------------|-------|
| General web | `brave_web_search` | `tavily_search` | sonnet |
| Deep page read | `scrape_as_markdown` | `firecrawl_scrape` | sonnet |
| News/trends | `search_news` (TrendRadar) | `tavily_search` | haiku |
| Academic | `web_search_exa` (scholar filter) | `tavily_search` | sonnet |
| Reddit | `web_search_exa` (reddit filter) | `brave_web_search` | haiku |
| App reviews | `search_actors` (Apify) | `brave_web_search` | haiku |
| Video content | `get_transcript` | N/A | haiku |
| Competitive intel | `get_latest_news` (TrendRadar) | `company_research_exa` | sonnet |

## Cost Optimization

| Agent | Model | Why |
|-------|-------|-----|
| Research Director (scoping) | sonnet | Needs judgment to ask good questions |
| Web researcher | sonnet | Complex synthesis from multiple sources |
| Reddit researcher | haiku | Pattern matching, simpler task |
| arXiv researcher | sonnet | Academic content requires deeper understanding |
| App store researcher | haiku | Structured data extraction |
| Knowledge Engineer (grading) | sonnet | Quality judgment |
| Susan (team assembly) | opus | Strategic synthesis, most complex task |

## Dispatch Safety Rules

1. **Never dispatch more than 6 background agents simultaneously** — diminishing returns + cost
2. **Always set time budgets** — researchers will go forever if you let them
3. **Deduplicate before ingestion** — multiple researchers may find the same sources
4. **Grade before trusting** — Phase 3 quality grading is non-negotiable
5. **Log all dispatches** — decision audit trail captures every agent call
