# Susan Team Architect — Plugin Design Document

**Date**: 2026-03-06
**Author**: Claude (Opus 4.6) + Michael Rodgers
**Status**: Approved
**Company**: Apex Ventures — TransformFit as initial deployment

---

## 1. Overview

Susan is an AI Team Architect that designs and deploys optimal multi-agent workforces for startups. She analyzes a company's domain, stage, and gaps, then assembles a team of specialized AI agents — each with their own knowledge base, behavioral economics lens, and domain expertise.

**Packaging**: Claude Code plugin (`susan-team-architect`) with a Python backend.
**Architecture**: Hybrid — plugin shell provides slash commands, skills, and agent definitions; Python core handles orchestration, RAG queries, embeddings, and data ingestion.
**Portability**: Install the plugin in any Claude Code project to get Susan + her full agent roster.

### Key Requirements

- Build the entire team needed for a startup, including mid-session additions
- Analyze current status and trajectory to pull in necessary resources
- Create shared databases using Supabase pgvector with namespace isolation
- Incorporate "outside the box" skill sets (behavioral economics, exercise science, sports psychology, neuroscience-informed design) to create competitive moats
- Populate databases with real data, not scaffolding
- TransformFit is the initial deployment target

---

## 2. Architecture

### 2.1 Hybrid Plugin + Python Backend

```
User types /susan-plan "TransformFit" in Claude Code
  │
  ├── Plugin command (commands/susan-plan.md) invokes:
  │   python3 -m susan_core.orchestrator --company transformfit --mode full
  │
  ├── Python orchestrator runs 6-phase workflow:
  │   Phase 1: Company Intake → company-profile.json
  │   Phase 2: Gap Analysis → analysis-report.json
  │   Phase 3: Team Design → team-manifest.json (selects from 22 agents)
  │   Phase 4: Dataset Requirements → dataset-requirements.json
  │   Phase 5: Execution Plan → execution-plan.md
  │   Phase 6: Behavioral Economics Audit → be-audit.json
  │
  ├── Each phase queries Supabase pgvector for relevant context
  ├── Outputs written to ./companies/transformfit/susan-outputs/
  └── Claude Code reads and summarizes for Michael's review
```

### 2.2 Plugin Structure

```
susan-team-architect/
├── .claude-plugin/plugin.json
├── commands/
│   ├── susan-plan.md              # Full 6-phase planning session
│   ├── susan-team.md              # Add/modify team members mid-session
│   ├── susan-status.md            # Company dashboard
│   ├── susan-ingest.md            # Data ingestion pipeline
│   └── susan-query.md             # Direct RAG query
├── skills/
│   ├── team-architect/SKILL.md    # Susan's core methodology
│   ├── behavioral-economics/SKILL.md  # BE module for all agents
│   └── company-analysis/SKILL.md  # Gap analysis framework
├── agents/                        # 22 agent definitions (see Section 3)
│   ├── susan.md
│   ├── steve-strategy.md
│   └── ... (20 more)
├── hooks/hooks.json               # Schema validation, edit protection
├── backend/
│   ├── pyproject.toml
│   ├── .env.example
│   ├── susan_core/                # Orchestration + schemas
│   │   ├── orchestrator.py
│   │   ├── schemas.py
│   │   ├── config.py
│   │   └── phases/                # 6 phase modules
│   ├── rag_engine/                # Shared RAG infrastructure
│   │   ├── embedder.py            # Voyage AI voyage-4
│   │   ├── retriever.py           # Supabase pgvector queries
│   │   ├── chunker.py             # 500-token smart chunking
│   │   └── ingestion/             # 8 data source pipelines
│   ├── agents/                    # Agent-specific Python modules
│   │   ├── base_agent.py          # Base class: RAG + BE lens + cost tracking
│   │   └── ... (22 agent modules)
│   └── data/                      # Seed data + configs
│       ├── company_registry.yaml
│       ├── agent_registry.yaml
│       ├── be_module/             # Behavioral economics source docs
│       └── seed_data/             # Foundational texts, benchmarks, exercises
└── README.md
```

### 2.3 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Plugin shell | Claude Code Plugin SDK | Slash commands, skills, agents, hooks |
| Orchestrator | Python 3.11+ | 6-phase workflow execution |
| AI backbone | Claude Agent SDK (anthropic) | Agent spawning, structured output |
| Vector DB | Supabase pgvector | Knowledge storage + similarity search |
| Embeddings | Voyage AI voyage-4 (1024-dim) | Text → vector conversion |
| Schemas | Pydantic v2 | Output validation |
| Data ingestion | Firecrawl, Apify, arXiv API, Reddit API | Multi-source data pipelines |

---

## 3. Agent Roster — 22 Agents

### 3.1 Orchestration

| Agent | Role | Model | Specialization |
|-------|------|-------|----------------|
| **Susan** | Team Architect / Orchestrator | Sonnet 4.5 | 6-phase planning, cross-portfolio synergy, agent spawning |

### 3.2 Strategy & Business (4 agents)

| Agent | Role | Model | Specialization |
|-------|------|-------|----------------|
| **Steve** | Business Strategy & Revenue | Opus 4.6 | Porter's Five Forces, SaaS metrics, fundraising, pricing, McKinsey 7S, BCG Matrix, Wardley Mapping |
| **Ledger** | Finance & Unit Economics | Haiku/Sonnet | MRR/ARR/churn, fitness seasonal economics, CAC/LTV modeling, burn rate, investor reporting |
| **Shield** | Legal, Compliance & Privacy | Sonnet 4.5 | HIPAA, GDPR, FTC Health Breach Notification Rule, BIPA, AI recommendation liability, health claims |
| **Bridge** | Partnerships & Ecosystem | Sonnet 4.5 | Wearable SDKs (HealthKit, Health Connect, Garmin, WHOOP, Oura), B2B wellness, insurance partnerships |

### 3.3 Product & Design (3 agents)

| Agent | Role | Model | Specialization |
|-------|------|-------|----------------|
| **Marcus** | UX/UI Designer | Sonnet 4.5 | Design systems, Baymard benchmarks, mobile-first fitness UX, one-hand operability |
| **Lens** | Accessibility & Inclusive Fitness | Sonnet 4.5 | WCAG 2.1/2.2, adaptive exercise modifications, assistive tech, $19.34B addressable market |
| **Echo** | Neuroscience-Informed Product Design | Sonnet 4.5 | Basal ganglia habit loops, dopamine reward prediction, Hook Model, cognitive load, body image harm prevention |

### 3.4 Engineering & Data (4 agents)

| Agent | Role | Model | Specialization |
|-------|------|-------|----------------|
| **Atlas** | Full-Stack Engineering | Sonnet 4.5 | React, FastAPI, Supabase, wearable SDKs, MLOps, biomechanics data modeling |
| **Nova** | AI/ML Specialist | Sonnet 4.5 | Model selection, RAG architecture, recommendation systems, arXiv monitoring, pose estimation |
| **Pulse** | Data Science & Churn Prediction | Sonnet 4.5 | Cohort analysis, Random Forest/XGBoost churn models, behavioral KPIs, A/B testing |
| **Sentinel** | Security & Infrastructure | Haiku/Sonnet | Supabase RLS, API security, encryption, SOC 2 prep, health data architecture |

### 3.5 Domain Science (3 agents)

| Agent | Role | Model | Specialization |
|-------|------|-------|----------------|
| **Coach** | Exercise Science & Biomechanics | Sonnet 4.5 | ACSM/NSCA guidelines, periodization, progressive overload, contraindications, injury prevention, MED research |
| **Sage** | Nutrition Science | Sonnet 4.5 | USDA FoodData, macronutrient periodization, chrononutrition, meal planning, glycemic response |
| **Drift** | Sleep & Recovery Optimization | Haiku/Sonnet | HRV analysis, sleep architecture, circadian biology, chronotype classification, recovery biomarkers |

### 3.6 Psychology & Behavior (3 agents)

| Agent | Role | Model | Specialization |
|-------|------|-------|----------------|
| **Freya** | Behavioral Economics & Retention | Sonnet 4.5 | 12 BE mechanisms, LAAL protocol, loss framing, "Cost of Not Returning" scripts, identity-based change |
| **Flow** | Sports Psychology & Motivation | Sonnet 4.5 | Self-determination theory, motivational interviewing (OARS), flow states, stages of change, CBT/ACT |
| **Quest** | Gamification & Engagement | Sonnet 4.5 | MDA framework, variable rewards, Bartle's player types, progression systems, intrinsic motivation balance |

### 3.7 Growth & Community (4 agents)

| Agent | Role | Model | Specialization |
|-------|------|-------|----------------|
| **Aria** | Growth & Content Marketing | Sonnet 4.5 | PLG, ASO, influencer strategy, YMYL/E-E-A-T compliance, creator ecosystem |
| **Haven** | Community & Social Fitness | Sonnet 4.5 | Social graph design, group accountability, challenge mechanics, UGC moderation, body image safety |
| **Guide** | Customer Success & Health Coaching | Sonnet 4.5 | Onboarding optimization, at-risk user intervention, NBC-HWC frameworks, Day-1/7/14 sequences |
| **Herald** | PR & Communications | Sonnet 4.5 | Press releases, transformation stories, scientific publication strategy, crisis comms |

### 3.8 Model Routing & Cost

| Tier | Agents | Model | Est. Monthly |
|------|--------|-------|-------------|
| Strategic | Steve | Opus 4.6 | ~$50 |
| Core | Susan + 16 others | Sonnet 4.5 | ~$120 |
| Lookup | Drift, Ledger, Sentinel | Haiku 4.5 | ~$15 |
| **Total** | 22 agents | Mixed | **~$185/mo** |

---

## 4. Database Schema

### 4.1 Supabase pgvector

**Tables:**
- `knowledge_chunks` — Core vector store with 1024-dim Voyage AI embeddings
- `companies` — Company profiles, team manifests, execution plans
- `agent_runs` — Cost tracking per agent per company

**20 data type taxonomies:**
`behavioral_economics`, `exercise_science`, `nutrition`, `sleep_recovery`, `sports_psychology`, `gamification`, `ux_research`, `growth_marketing`, `business_strategy`, `legal_compliance`, `technical_docs`, `market_research`, `user_research`, `ai_ml_research`, `community`, `finance`, `partnerships`, `content_strategy`, `pr_communications`, `security`

**Multi-tenancy:** Namespace isolation via `company_id` column. `shared` namespace accessible to all companies.

**Access control:** `access_level` column: `public` (all companies), `company` (single company), `agent_private` (single agent).

### 4.2 RAG Query Flow

```
Agent needs context
  → BaseAgent.query_rag(question, data_types=[...])
    → Voyage AI embeds question → 1024-dim vector
    → search_knowledge() against pgvector
      Filters: company_id + access_level + data_type + agent_id
    → Top-5 chunks returned with similarity scores
    → Chunks injected into agent's context window
```

Each agent has default data_type filters:
- **Freya**: `behavioral_economics`, `sports_psychology`, `user_research`
- **Coach**: `exercise_science`, `nutrition`, `sleep_recovery`
- **Steve**: `business_strategy`, `market_research`, `finance`
- **All agents**: Also receive `behavioral_economics` via BE lens injection

---

## 5. Data Population Plan

### 5.1 Tier 1 — Week 1 (~1,000 chunks)

| Source | Data Type | Chunks | Method |
|--------|-----------|--------|--------|
| Behavioral Economics Module (full doc) | behavioral_economics | ~200 | Markdown ingestion |
| 12 BE Mechanisms + examples | behavioral_economics | 48 | Chunk by mechanism |
| LAAL Protocol | behavioral_economics | 25 | Chunk by stage + channel |
| Cost of Not Returning Framework | behavioral_economics | 20 | Chunk by cost type |
| TransformFit Copy Library (D3/D7/D14/D21/D30) | behavioral_economics | 30 | Per trigger |
| Hooked + Indistractable (Nir Eyal) | behavioral_economics | 60 | AI synthesis |
| Tiny Habits / MAP (BJ Fogg) | behavioral_economics | 40 | AI synthesis |
| Atomic Habits (James Clear) | behavioral_economics | 50 | AI synthesis |
| Prospect Theory (Kahneman) | behavioral_economics | 30 | AI synthesis |
| 7 Influence Principles (Cialdini) | behavioral_economics | 35 | AI synthesis |
| ACSM Exercise Guidelines | exercise_science | 80 | Web scrape + synthesis |
| NSCA Strength & Conditioning | exercise_science | 60 | AI synthesis |
| Exercise Database (ExRx patterns) | exercise_science | 200 | Structured library |
| Retention Benchmarks by Industry | market_research | 30 | Research compilation |
| Reforge Growth Frameworks | growth_marketing | 50 | Essay synthesis |
| SaaS Metrics Models | business_strategy | 40 | Framework synthesis |

### 5.2 Tier 2 — Weeks 2-3 (~1,545 chunks)

| Source | Data Type | Chunks | Method |
|--------|-----------|--------|--------|
| NHANES Health Survey Data | user_research | 300 | CSV → synthetic profiles |
| App Store Reviews (5 competitors) | user_research | 200 | Apify scrape |
| Reddit fitness communities | user_research | 150 | Top posts by behavioral driver |
| Growth.design Case Studies | ux_research | 100 | Web scrape |
| AI Adoption Resistance Profiles | behavioral_economics | 25 | 5 persona profiles |
| Loss vs. Gain Copy Pairs (200) | behavioral_economics | 200 | AI-generated |
| HIPAA/GDPR/FTC Compliance | legal_compliance | 80 | Regulatory summaries |
| Wearable SDK Docs | technical_docs | 100 | HealthKit, Garmin, WHOOP APIs |
| USDA FoodData Central | nutrition | 150 | API download |
| Sleep Science (HRV/Circadian) | sleep_recovery | 60 | Research synthesis |
| Gamification Research | gamification | 80 | PMC papers + case studies |
| WCAG 2.1/2.2 Guidelines | ux_research | 40 | Actionable chunks |
| Strategy Frameworks | business_strategy | 60 | Porter's, BCG, McKinsey |

### 5.3 Tier 3 — Month 2 (~1,450 chunks)

| Source | Data Type | Chunks | Method |
|--------|-----------|--------|--------|
| arXiv AI/ML Papers | ai_ml_research | 500 | RSS → abstract pipeline |
| Competitor Feature Matrices | market_research | 100 | Web research |
| Fundraising Benchmarks | business_strategy | 80 | Stage + vertical synthesis |
| Anti-patterns Library | behavioral_economics | 50 | Ethical flags |
| Community Management Patterns | community | 60 | Strava/Peloton/CrossFit |
| PR & Scientific Publication Playbook | pr_communications | 40 | Noom strategy |
| Insurance Partnership Guides | partnerships | 30 | B2B wellness research |
| SEO/YMYL Health Content | content_strategy | 40 | Google E-E-A-T |
| Supabase RLS + Security | security | 50 | Official docs |
| Synthetic User Journeys (1,000 users) | user_research | 500 | 90-day profile generation |

### 5.4 Totals

- **~4,000 chunks** across 20 data types
- **Embedding cost**: ~$0.12 (Voyage AI voyage-4)
- **Storage**: Free at this scale on Supabase

---

## 6. Behavioral Economics Integration

Every agent receives the BE lens injection in its system prompt:

```xml
<behavioral_economics_lens>
Before finalizing any output, apply these checks:

1. LOSS AUDIT: Does this help users feel the cost of NOT acting?
2. OWNERSHIP CHECK: Does the user own something that makes leaving feel like a loss?
3. IDENTITY ALIGNMENT: Does this reinforce who they're becoming?
4. FRICTION AUDIT: Is the return threshold under 2 minutes?
5. PROGRESS VISIBILITY: Is progress visible, named, and personalized?

Default to LOSS FRAMING for all re-engagement copy.
Reference the Apex Ventures BE Repository for scripts and benchmarks.
</behavioral_economics_lens>
```

Phase 6 (Behavioral Economics Audit) produces:
- Retention risk assessment (D1/D7/D30 targets)
- LAAL architecture (ownership, cost, threshold, reward, investment)
- Copy protocol (loss-framed scripts per day-trigger)
- Agent BE injection map (which mechanisms per agent)
- Measurement plan (behavioral KPIs + A/B test design)

---

## 7. Cross-Agent Coordination

### Priority Resolution
When agents disagree: **safety > retention > growth > features**

### Multi-Agent Queries
Questions spanning domains (e.g., "design the onboarding flow"):
1. Susan identifies relevant agents (Marcus + Freya + Coach + Quest)
2. Dispatches in parallel via Claude Code agent teams
3. Each agent queries its RAG namespace
4. Susan synthesizes into unified recommendation

### Mid-Session Team Addition
`/susan-team transformfit "behavioral economist"`:
1. Susan scans current team manifest for gaps
2. Matches against 22 agent templates
3. Runs mini Phase 3 (design) + Phase 4 (datasets) for new agent
4. Updates manifest + triggers data ingestion

---

## 8. Company Portability

To deploy Susan for a new company:
1. Install plugin: `claude plugin install susan-team-architect`
2. Run: `/susan-plan "NewCompany"`
3. Susan creates profile, runs gap analysis, designs team
4. Ingestion begins for company namespace
5. `shared` namespace (BE, frameworks, exercise science) available automatically

---

## 9. Services Setup

| Service | Purpose | Setup |
|---------|---------|-------|
| Anthropic API | Claude Agent SDK | Key exists |
| Voyage AI | Embeddings (voyage-4) | Sign up at voyageai.com (200M free tokens) |
| Supabase | pgvector + company data | Create project, run schema SQL |
| Firecrawl | Web scraping for data ingestion | API key for Tier 2+ data |
| Apify | App store review scraping | API key for Tier 2 data |

---

## 10. Success Criteria

- [ ] `/susan-plan transformfit` runs end-to-end, producing all 6 phase outputs
- [ ] All 22 agents have system prompts with BE lens injection
- [ ] Supabase contains ~1,000 Tier 1 chunks with working similarity search
- [ ] `/susan-team` can add agents mid-session and update the manifest
- [ ] `/susan-query` returns relevant chunks from the knowledge base
- [ ] Plugin is installable in a separate project and functions correctly
- [ ] Total monthly API cost stays under $200

---

*Design approved: 2026-03-06*
*Next step: Implementation plan via writing-plans skill*
