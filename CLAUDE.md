# Startup Intelligence OS

Central intelligence repository for **Apex Ventures**. Powers **Susan**, an AI Team Architect that designs and deploys multi-agent workforces for startups. Also serves as a curated resource hub across 23 categories.

## Susan — AI Team Architect

### Quick Start
```
/susan-plan <company-name>     # Run full 6-phase orchestration
/susan-team <company>          # View designed agent team
/susan-status <company>        # Check orchestration status
/susan-ingest <source>         # Add data to knowledge base (URL or file path)
/susan-query <question>        # Search the RAG knowledge base
```

### Use Specific Agents
Reference any of the 22 agents by name in conversation:
- **@susan** — Team Architect / Orchestrator
- **@steve-strategy** — Business Strategy & Revenue (Opus)
- **@marcus-ux** — UX/UI Designer
- **@aria-growth** — Growth & Content Marketing
- **@atlas-engineering** — Full-Stack Engineering
- **@coach-exercise-science** — Exercise Science & Biomechanics
- **@freya-behavioral-economics** — Behavioral Economics & Retention
- **@quest-gamification** — Gamification & Engagement

Full roster: `susan-team-architect/agents/` (22 agents across 7 groups)

### Research Agents (auto-populate knowledge base)
```
@researcher-web "topic"        # Scrape web sources via Firecrawl
@researcher-arxiv "topic"      # Pull academic papers from arXiv
@researcher-reddit "topic"     # Mine Reddit communities
@researcher-appstore "app"     # Scrape app store reviews
```

### RAG Knowledge Base
- **839+ chunks** in Supabase pgvector (Voyage AI voyage-3, 1024-dim)
- Critical data gaps: nutrition, legal_compliance, technical_docs, security, sports_psychology, gamification, community
- Full inventory: `susan-team-architect/backend/data/dataset_requirements_master.md`

## Architecture

```
├── susan-team-architect/        # Claude Code plugin (Susan)
│   ├── agents/                  # 22 AI agent definitions
│   ├── commands/                # 5 slash commands
│   ├── skills/                  # 3 skills
│   └── backend/                 # Python (orchestrator, RAG, ingestion)
├── ux-ui-design/                # UX/UI research and frameworks
├── docs/plans/                  # Implementation plans
└── [23 category directories]    # Curated startup resources
```

## Backend Setup
```bash
cd susan-team-architect/backend && source .venv/bin/activate
# Verify: python3 -c "from susan_core.orchestrator import run_susan; print('OK')"
```

## API Keys
All in `susan-team-architect/backend/.env` (gitignored). Required: ANTHROPIC_API_KEY, VOYAGE_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY, FIRECRAWL_API_KEY, BRAVE_SEARCH_API_KEY, EXA_API_KEY, APIFY_API_KEY, JINA_API_KEY.

## Connected Repositories
- **ios-intelligence-engine** — CrewAI competitive intel (7 flows, Supabase)
- **oracle-health-ai-enablement** — Strategy intel platform (180+ prompt pieces, Supabase)
- **ux-design-scraper** — Chrome extension for UX design intelligence (16 tables, Supabase)

## Key Files
- `backend/susan_core/config.py` — Configuration and model routing
- `backend/susan_core/orchestrator.py` — Main 6-phase pipeline
- `backend/data/agent_registry.yaml` — Agent configuration (22 agents)
- `backend/data/dataset_requirements_master.md` — 150+ dataset inventory

## Content Standards
- Resources include: name, description, URL, and discovery date
- Use markdown tables for resource listings
- Cross-reference `LIVE-RESEARCH-ENRICHMENT.md` to avoid duplicates
- URLs must be verified as live before adding
