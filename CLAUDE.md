# Startup Intelligence OS

Central intelligence repository for **Apex Ventures**. Powers **Susan**, an AI Team Architect that designs and deploys multi-agent workforces for startups. TransformFit (AI fitness app) is the first deployment target.

## Quick Start — Deploy Susan to Any Project

### Option 1: Run Susan from this repo
```bash
cd susan-team-architect/backend && source .venv/bin/activate

# Full 6-phase orchestration for a company
python3 -c "
from susan_core.orchestrator import run_susan
run_susan('TransformFit', mode='full')
"
```

### Option 2: Use slash commands in Claude Code
```
/susan-plan TransformFit     # Run full 6-phase orchestration
/susan-team TransformFit     # View designed agent team
/susan-status TransformFit   # Check orchestration status
/susan-ingest <URL>          # Add data to knowledge base
/susan-query "question"      # Search the RAG knowledge base
```

### Option 3: Use individual agents by name
Reference any of the 31 agents in conversation:
```
@steve-strategy     — Business Strategy & Revenue (Opus model)
@compass-product    — Product Management & Roadmap
@marcus-ux          — UX/UI Designer
@atlas-engineering  — Full-Stack Engineering
@freya-behavioral-economics — Retention & Behavioral Design
@vault-fundraising  — Pitch Decks & Investor Relations
@beacon-aso         — App Store Optimization & SEO
```

## Adding Susan to an Existing Project

### Step 1: Install the plugin
```bash
cd your-project/
claude plugin install /path/to/Startup-Intelligence-OS/susan-team-architect
```

### Step 2: Copy the .env file
```bash
cp /path/to/Startup-Intelligence-OS/susan-team-architect/backend/.env your-project/.env
```
Required keys: ANTHROPIC_API_KEY, VOYAGE_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY, FIRECRAWL_API_KEY

### Step 3: Use Susan
All slash commands and agents are now available in your project. The knowledge base (6,693 chunks in Supabase) is shared across all projects.

## Full Agent Roster (31 agents across 7 groups)

### Orchestration
- **Susan** — Team Architect / Orchestrator

### Strategy
- **Steve** — Business Strategy & Revenue (Opus)
- **Shield** — Legal, Compliance & Privacy
- **Bridge** — Partnerships & Ecosystem
- **Ledger** — Finance & Unit Economics
- **Vault** — Fundraising & Investor Relations

### Product
- **Marcus** — UX/UI Designer
- **Lens** — Accessibility & Inclusive Fitness
- **Echo** — Neuroscience-Informed Design
- **Compass** — Product Management & Roadmap
- **Prism** — Brand Strategy & Creative Direction

### Engineering
- **Atlas** — Full-Stack Engineering
- **Nova** — AI/ML Specialist
- **Pulse** — Data Science & Churn Prediction
- **Sentinel** — Security & Infrastructure
- **Forge** — QA & Testing

### Science
- **Coach** — Exercise Science & Biomechanics
- **Sage** — Nutrition Science
- **Drift** — Sleep & Recovery

### Psychology
- **Freya** — Behavioral Economics & Retention
- **Flow** — Sports Psychology & Motivation
- **Quest** — Gamification & Engagement

### Growth
- **Aria** — Growth & Content Marketing
- **Haven** — Community & Social
- **Guide** — Customer Success
- **Herald** — PR & Communications
- **Beacon** — ASO & SEO

### Research (auto-populate knowledge base)
- **researcher-web** — Scrape web sources via Firecrawl
- **researcher-arxiv** — Academic papers from arXiv
- **researcher-reddit** — Reddit community mining
- **researcher-appstore** — App Store review analysis

## Knowledge Base — 6,693 chunks across 22 data types

| Data Type | Chunks | Key Sources |
|-----------|--------|-------------|
| user_research | 3,305 | Reddit, App Store reviews, NHANES, academic studies |
| behavioral_economics | 600 | RevenueCat, behavioral science, decision theory |
| market_research | 321 | Sensor Tower, Business of Apps, Sacra, competitive intel |
| sleep_recovery | 319 | Sleep Foundation, Huberman, NCBI, WHOOP |
| exercise_science | 313 | ACSM, StrongerByScience, arXiv |
| nutrition | 235 | Examine, ISSN, Harvard, NCBI |
| growth_marketing | 187 | Reforge, Andrew Chen, Liftoff, CPI benchmarks |
| legal_compliance | 163 | HIPAA, FTC, GDPR, CCPA, Apple Guidelines |
| ai_ml_research | 148 | Lilian Weng, HuggingFace, arXiv (agents, RAG, LLMs) |
| sports_psychology | 145 | SDT, self-efficacy, intrinsic motivation |
| gamification | 133 | Octalysis, IxDF, health gamification studies |
| content_strategy | 124 | Backlinko, Buffer, Copyblogger |
| security | 120 | OWASP Mobile/API, auth cheat sheets, JWT |
| business_strategy | 93 | YC, a16z, pmarca, First Round |
| ux_research | 91 | Interaction design principles, behavioral design |
| finance | 82 | SaaS metrics, unit economics, fundraising guides |
| technical_docs | 80 | React Native, Supabase, Expo, HealthKit |
| community | 79 | Feverbee, Orbit, Strava community model |
| partnerships | 56 | HealthKit, Google Fit, Garmin, Fitbit, WHOOP APIs |
| ux_framework | 44 | Double Black Box method |
| agent_prompts | 39 | TransformFit Elite prompts |
| pr_communications | 16 | YC PR guide, crisis comms |

## Simulation Engine

```python
# Monte Carlo user cohort simulation
from simulations.monte_carlo import run_simulation, print_report, compare_scenarios

# Baseline vs TransformFit comparison
baseline = run_simulation(cohort_size=10_000, months=12)
enhanced = run_simulation(cohort_size=10_000, months=12,
    ai_personalization=1.30, social_features=1.20, gamification=1.25)
compare_scenarios(baseline, enhanced)

# Run all 8 pre-built scenarios
from simulations.scenario_runner import run_all_scenarios
run_all_scenarios()

# Generate competitive intelligence profiles
from simulations.competitive_intel import generate_competitive_chunks
generate_competitive_chunks()

# Download and process real CDC NHANES microdata
from simulations.nhanes_microdata import run
run()
```

## 9 Operational Protocols (stored in RAG)

1. **Product Development Lifecycle** — Discovery → Definition → Build → Test → Launch → Measure
2. **Go-to-Market Playbook** — Pre-launch → Launch Day → Post-launch → Scale
3. **Fundraising Process** — Preparation → Targeting → Outreach → Closing
4. **User Research Protocol** — Interviews, surveys, analytics, usability testing
5. **Experimentation Framework** — Hypothesis → A/B test → Analyze → Ship/Kill
6. **Content Calendar** — 4 pillars, weekly cadence, production pipeline
7. **Customer Feedback Loop** — Collect → Categorize → Route → Close the loop
8. **Incident Response** — SEV 1-4 classification, detection → resolution → postmortem
9. **Hiring Protocol** — Define → Source → Screen → Close → Onboard

## Architecture

```
├── susan-team-architect/           # Claude Code plugin
│   ├── agents/                     # 31 AI agent definitions
│   ├── commands/                   # 5 slash commands
│   ├── skills/                     # 3 skills
│   ├── hooks.json                  # Plugin hooks
│   └── backend/
│       ├── susan_core/             # Orchestrator, config, schemas
│       ├── rag_engine/             # Retriever, embedder, chunker
│       │   └── ingestion/          # 7 pipelines (web, arXiv, Reddit, AppStore, NHANES, markdown, books)
│       ├── simulations/            # Monte Carlo, personas, competitive intel, NHANES microdata
│       ├── data/                   # Agent registry, dataset inventory
│       └── scripts/                # Utility scripts
├── ux-ui-design/                   # UX research and frameworks
├── docs/plans/                     # Implementation plans
└── [23 category directories]       # Curated startup resources
```

## Backend Setup
```bash
cd susan-team-architect/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
# Verify: python3 -c "from susan_core.orchestrator import run_susan; print('OK')"
```

## API Keys
All in `susan-team-architect/backend/.env` (gitignored):
- ANTHROPIC_API_KEY, VOYAGE_API_KEY — Required for agents and embeddings
- SUPABASE_URL, SUPABASE_SERVICE_KEY — Required for knowledge base
- FIRECRAWL_API_KEY — Required for web scraping
- Optional: BRAVE_SEARCH_API_KEY, EXA_API_KEY, APIFY_API_KEY, JINA_API_KEY

## Connected Repositories
- **ios-intelligence-engine** — CrewAI competitive intel (7 flows, Supabase)
- **oracle-health-ai-enablement** — Strategy intel platform (180+ prompt pieces)
- **ux-design-scraper** — Chrome extension for UX design intelligence
