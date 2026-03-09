# 25X Capability Assessment -- Startup Intelligence OS

**Assessor:** Susan (Capability Foundry)
**Date:** 2026-03-09
**Scope:** Full system audit across 12 capability domains
**Method:** Code-grounded audit of every file, model, schema, engine, agent spec, and runtime path
**System version:** v4 (pre-v5 baseline)

---

## Executive Summary

The Startup Intelligence OS has built a remarkable breadth of capability surface area: 60 agents, 10 orchestration phases, a 5-mode debate engine, file-backed persistence, a RAG corpus of 10,788 chunks, a FastAPI control plane, an MCP server with 7 tools, and 5 domain packs across 5 companies. The maturity distribution is heavily weighted toward nascent and emerging, with very few capabilities at scaling or above. The system has strong *specification depth* (6,961 lines of agent specs) but weak *execution infrastructure* (no auth, no deployment, no real-time feedback, no multi-user access).

The 25X target is not "25 times more features." It is the system operating at 25 times current throughput, reliability, self-improvement rate, and value delivery. The gap is primarily in: execution automation, closed-loop learning, multi-tenant production infrastructure, and operator experience.

**Current aggregate maturity:** Emerging (1.6 / 5.0)
**25X target aggregate maturity:** Optimizing (4.0 / 5.0)

---

## Maturity Scale Reference

| Level | Score | Definition |
|-------|-------|------------|
| Nascent | 1 | Concept exists, maybe some code, not operational |
| Emerging | 2 | Working prototype, used manually, gaps everywhere |
| Scaling | 3 | Reliable, repeatable, measured, used in production |
| Optimizing | 4 | Self-improving, feedback loops closed, metrics-driven |
| Leading | 5 | Best-in-class, teaches others, compounds automatically |

---

## DOMAIN 1: Decision Intelligence

### Current Maturity: Emerging (2.0)

**Current Capabilities (verified in code):**
- Decision model with full lifecycle: draft, proposed, approved, rejected, superseded (`apps/decision_os/models.py`)
- 5-mode debate engine: builder_pov, skeptic_pov, contrarian_pov, operator_pov, red_team_challenge (`apps/decision_os/decision_engine.py`)
- Rule-based option generation: always produces 3 options (go forward, scoped experiment, do nothing)
- Heuristic scoring across 4 criteria (feasibility, impact, risk, speed) with configurable weights
- Output contract enforcement: recommendation, counter_recommendation, why_now, failure_modes, next_experiment
- Run tracing with step-level events, timestamps, evidence IDs, and confidence scores (`apps/decision_os/telemetry.py`)
- CLI access via `bin/jake run-decision` and `bin/jake debate`
- File-backed YAML persistence with generic Repository pattern
- Smoke test that validates end-to-end pipeline

**What is missing or weak:**
- Debate arguments are rule-generated strings, not LLM-powered reasoning
- Option generation is formulaic (always 3 archetypes), not context-sensitive
- No evidence linking in practice (evidence_ids field exists but unused in scoring)
- No decision dependency tracking
- No decision outcome tracking or reversal detection
- No multi-stakeholder input or voting
- No decision templates by type (investment, product, hiring, pivot)

### 25X Target:
- LLM-powered debate with each mode producing genuinely adversarial arguments grounded in RAG evidence
- Context-aware option generation that pulls from company state, competitive intelligence, and historical decisions
- Evidence-scored options where RAG results directly influence scoring weights
- Decision dependency graphs that show cascade effects
- Outcome tracking: decisions are revisited against actual results, with automatic reversal alerts
- Decision templates: different flows for investment vs product vs hiring vs pivot decisions
- Multi-stakeholder voting and dissent recording
- Decision replay: any decision can be re-run with updated evidence to test whether the recommendation would change

### Gap:
The engine has the right schema but runs on heuristics instead of intelligence. The debate modes are labels without genuine reasoning behind them. Evidence exists in the RAG but is not wired into scoring. There is no feedback loop from decision outcomes back to decision quality improvement.

### Wave: 1
### Required Agents: Steve (strategy), Freya (behavioral economics), Susan (orchestrator)
### Dependencies: Intelligence and Research domain (for evidence scoring), Data and Analytics domain (for outcome tracking)

---

## DOMAIN 2: Capability Management

### Current Maturity: Emerging (2.0)

**Current Capabilities (verified in code):**
- Capability model with maturity enum: nascent, emerging, scaling, optimizing, leading (`apps/decision_os/models.py`)
- CapabilityEngine with maturity assessment heuristic: base score + evidence count + decision count + owner status - gap count (`apps/decision_os/capability_engine.py`)
- Gap detection: capabilities with gaps field populated are flagged
- Wave planning: capabilities grouped by maturity delta into build waves
- Agent readiness index: auto-generated from agent spec files via `bin/jake sync-intel`
- 6 capability records in `.startup-os/capabilities/` including jake.profile, susan.profile, gen-chat-os.system, agent-readiness-index, workspace-contract, decision-kernel-phase-a
- Susan foundry maturity model with 6 dimensions: company_genome, evidence_graph, cognitive_studios, trust_governance, operator_console, memory_eval (`backend/data/foundry/maturity_model.yaml`)

**What is missing or weak:**
- Maturity scoring is purely heuristic (counts evidence and decisions), not outcome-based
- No capability health dashboards
- No automated capability discovery (must be manually created)
- No cross-company capability benchmarking
- No capability dependencies enforced at runtime
- Wave planning is a one-time analysis, not a continuously updated backlog
- No capability ownership transfer or escalation protocols

### 25X Target:
- Automated capability discovery: system scans codebase, agent specs, and runtime logs to propose new capability records
- Outcome-based maturity scoring: capabilities advance when measurable outcomes improve, not when evidence count increases
- Live capability health dashboard showing maturity trends, gap counts, and ownership coverage
- Cross-company benchmarking: compare capability maturity across portfolio companies
- Enforced dependency graphs: capabilities cannot advance past a maturity threshold until dependencies meet theirs
- Continuous wave planning: backlog re-prioritizes automatically based on gap severity and strategic weight
- Capability ownership SLAs with escalation when progress stalls

### Gap:
The data model is sound but the engine runs on proxy metrics (file counts) instead of real outcomes. There is no continuous monitoring, no automated discovery, and no enforcement of capability dependencies. The foundry maturity model in Susan's backend is disconnected from the capability engine in the Decision OS.

### Wave: 1
### Required Agents: Susan (orchestrator), Compass (product), Pulse (data science)
### Dependencies: Data and Analytics domain (for outcome metrics), Platform Infrastructure (for dashboard hosting)

---

## DOMAIN 3: Innovation and Strategy

### Current Maturity: Emerging (1.8)

**Current Capabilities (verified in code):**
- Steve agent spec with business strategy and revenue focus
- Susan orchestrator with 10 phases including problem_framing, capability_diagnosis, evidence_gap_map, decision_brief
- Foundry modes: quick, deep, design, foundry (`backend/data/foundry/susan_modes.yaml`)
- Expert councils defined in `backend/data/foundry/expert_councils.yaml`
- Stage gates defined in `backend/data/foundry/stage_gates.yaml`
- Company-level strategy artifacts: company_foundry.yaml tracks per-company state
- Competitive intelligence via MCP tool: Fitbod, Noom, Strava, Peloton, MyFitnessPal, Hevy, Future
- Monte Carlo simulation for user cohort lifecycle with 7 personas and 6 feature modifiers

**What is missing or weak:**
- No Strategos-style future-back planning
- No scenario planning with branching timelines
- No option tree visualization
- No strategic assumption register with invalidation triggers
- No competitive response modeling (what competitors do if we do X)
- Strategy is generated per-session, not accumulated across sessions
- No innovation pipeline with stage gates tracked in the OS
- Monte Carlo simulation is fitness-domain-specific, not generalizable

### 25X Target:
- Future-back planning engine: define 3-year target state, decompose into quarterly capability milestones, work backward to current sprint
- Scenario planning with 3-5 branching futures, each with probability weights and leading indicators
- Option tree visualization: every strategic fork produces a tree of consequences, tracked over time
- Strategic assumption register: every strategy depends on explicit assumptions; each assumption has invalidation criteria and monitoring
- Competitive response modeling: given our move, simulate competitor reactions using their known patterns
- Cross-session strategy accumulation: strategic insights compound across runs, not restart each time
- Generalized Monte Carlo simulation engine: configurable for any business model, not just fitness cohorts
- Innovation pipeline with idea intake, stage gates, experiment tracking, and graduation criteria

### Gap:
The system has strong one-shot strategy generation through Susan's phases, but no persistent strategic state. Strategies are produced and forgotten. There is no future-back planning, no scenario branching, no assumption tracking with invalidation triggers. The competitive intelligence is static lookup, not dynamic modeling.

### Wave: 2
### Required Agents: Steve (strategy), Freya (behavioral economics), Pulse (data science), Algorithm Lab
### Dependencies: Decision Intelligence (for option tree tracking), Data and Analytics (for leading indicators)

---

## DOMAIN 4: UX and Design

### Current Maturity: Emerging (2.2)

**Current Capabilities (verified in code):**
- Design Studio Director agent with full cognitive architecture: diagnose, principles, critique, template cascade (136-line spec)
- Landing Page Studio with 6-beat emotional arc, trust-first conversion, moments-of-truth mapping
- App Experience Studio for onboarding, core loops, retention
- Marcus (UX/UI Designer) with ux_research and user_research RAG access
- Mira (Emotional Experience and Narrative Design) with emotional_design RAG access
- Echo (Neuro-Design) for cognitive load and perception
- Lens (Accessibility) agent
- 8-layer cognitive loop documented in studio specs: perception, diagnosis, concept, challenge, experiment, memory, writeback, evaluation
- Studio data types in RAG: studio_case_library, studio_antipatterns, studio_memory, studio_templates, studio_evals, studio_open_research
- Keyword-based studio routing in `backend/control_plane/protocols.py`

**What is missing or weak:**
- No design system or component library
- No Figma integration or export
- No design token management
- No visual asset generation (text-only outputs)
- No design review workflow (critique is conceptual, not operational)
- No A/B test integration
- No accessibility audit automation
- Studios generate text recommendations, not visual artifacts
- No design history or version control for design decisions

### 25X Target:
- Design system with tokenized components, documented patterns, and enforced usage
- Figma integration: studios output Figma-compatible specifications, studios can read Figma files for critique
- Visual asset generation pipeline: studios produce mockups, wireframes, and annotated screenshots
- Design review workflow: critique mode produces structured feedback, tracked to resolution
- A/B test integration: design variants are tracked, experiments are wired to analytics
- Accessibility audit automation: Lens agent runs automated WCAG checks on deployed surfaces
- Design decision history: every design choice is recorded with rationale, linked to user research
- Cross-surface consistency scoring: system detects when surfaces diverge from established principles

### Gap:
The studio specifications are genuinely excellent -- the cognitive architecture, doctrine, and contrarian beliefs represent leading-edge design thinking. But the output is text-only. There is no pipeline from studio recommendation to visual artifact to deployed surface to measured outcome. The studios are a brain without hands.

### Wave: 2
### Required Agents: Design Studio Director, Landing Page Studio, App Experience Studio, Marcus, Mira, Echo, Lens
### Dependencies: Platform Infrastructure (for design system hosting), Content and Marketing (for asset cascade)

---

## DOMAIN 5: Agent Orchestration

### Current Maturity: Emerging (2.0)

**Current Capabilities (verified in code):**
- 60 agents across 8 groups: orchestration, strategy, product, engineering, science, psychology, growth, research/studio
- Agent registry YAML with per-agent: name, role, model, rag_data_types, group, expertise_types (`backend/data/agent_registry.yaml`)
- Keyword-based routing in protocols.py: 30+ keyword sets mapped to agents
- MCP tool `run_agent`: dispatches any agent with RAG context injection
- MCP tool `list_agents`: returns roster filtered by group
- Susan orchestrator dispatches 10 sequential phases, each calling specific agents
- Route task with model: Claude-powered routing for ambiguous tasks
- Agent readiness index auto-generated from filesystem scan
- Per-agent expertise types and RAG data type scoping

**What is missing or weak:**
- No multi-agent reasoning (agents do not talk to each other)
- No agent memory persistence (each invocation starts fresh)
- No agent handoff protocol (one agent cannot delegate to another mid-task)
- No parallel agent execution (all phases are sequential)
- No agent performance tracking (which agents produce better outcomes)
- Keyword routing is brittle (exact string matching, no semantic fallback)
- No agent capability discovery (agents cannot introspect what they can do)
- No agent versioning or A/B testing of agent specs
- No agent conflict resolution (when two agents disagree)

### 25X Target:
- Multi-agent reasoning chains: agents can invoke other agents as tools, with structured handoff protocols
- Persistent agent memory: agents accumulate knowledge across invocations, scoped by company and project
- Parallel agent execution: independent agents run concurrently with result merging
- Semantic routing: task descriptions are embedded and matched against agent capability vectors, not keywords
- Agent performance tracking: every agent output is scored for quality, relevance, and user satisfaction
- Agent A/B testing: multiple agent spec versions run in parallel, best performer is promoted
- Agent conflict resolution protocol: when agents disagree, a structured resolution process produces a synthesis
- Agent capability discovery: each agent can declare what it can and cannot do, with confidence bounds
- Agent composition: complex tasks are decomposed into sub-tasks, each assigned to the best-fit agent

### Gap:
The agent roster is large and well-specified, but agents operate as isolated functions, not as a collaborating team. There is no memory, no handoff, no parallel execution, no performance measurement, and no learning from outcomes. Routing is keyword-based and brittle. This is the single highest-leverage domain for 25X improvement.

### Wave: 1
### Required Agents: Susan (orchestrator), Nova (AI/ML), Atlas (engineering), Knowledge Engineer
### Dependencies: Platform Infrastructure (for memory persistence), Data and Analytics (for performance tracking)

---

## DOMAIN 6: Studio Operations

### Current Maturity: Emerging (1.8)

**Current Capabilities (verified in code):**
- 18 cognitive studios, each with 8-layer cognitive loop spec
- Studios: Design Studio Director, Landing Page, App Experience, Marketing Studio Director, Social Media, Coaching Architecture, Conversation Designer, Workout Session, Workout Program, Training Research, Algorithm Lab, Knowledge Engineer, AI Evaluation Specialist, Deck, Whitepaper, Memo, Article, Highlight Reel
- Each studio has: identity, doctrine, canonical frameworks, contrarian beliefs, innovation heuristics, reasoning modes, value detection, experiment logic, 5 whys protocol, JTBD frame
- Studio data types in Supabase: studio_case_library, studio_antipatterns, studio_memory, studio_templates, studio_evals, studio_open_research
- Studio asset directories: `backend/data/studio_assets/` with companies/, generated/, open_sources/, shared/
- Studio routing keywords defined per-studio in protocols.py

**What is missing or weak:**
- No case library population (the RAG type exists but studios do not write cases back)
- No experiment log (experiment logic is specified but no tracking system)
- No template management system (templates are mentioned but not stored or versioned)
- No studio memory writeback (8-layer loop describes writeback but it is not implemented)
- No cross-studio learning (studios cannot read each other's memories)
- No studio evaluation metrics (quality of studio outputs is not measured)
- No studio scheduling or cadence (studios run on demand only)
- No studio conflict detection (when two studios give contradictory advice)

### 25X Target:
- Case library writeback: every studio run produces a case entry with inputs, outputs, quality score, and lessons learned
- Experiment tracking: studios propose experiments, track them through execution, and record outcomes
- Template management: versioned templates per studio, with usage tracking and quality scoring
- Studio memory persistence: each studio writes back learnings that improve future runs
- Cross-studio knowledge sharing: insights from one studio are available to related studios
- Studio quality metrics: output quality scored by users and by downstream outcome correlation
- Studio scheduling: recurring studio runs on company cadence (weekly design critique, monthly strategy review)
- Studio conflict resolution: when studios disagree, a resolution protocol synthesizes the best of each

### Gap:
The 8-layer cognitive loop is well-designed in spec but only the first 3 layers (perception, diagnosis, concept) are operational. The back half (challenge, experiment, memory, writeback, evaluation) exists as spec text but has no runtime implementation. Studios produce outputs but do not learn, do not write cases, do not track experiments, and do not improve over time.

### Wave: 2
### Required Agents: All 18 studios, Knowledge Engineer, AI Evaluation Specialist, Research Ops
### Dependencies: Agent Orchestration (for memory persistence), Data and Analytics (for quality metrics)

---

## DOMAIN 7: Intelligence and Research

### Current Maturity: Scaling (2.8)

**Current Capabilities (verified in code):**
- RAG engine with Supabase pgvector: 10,788 chunks across 22+ data types
- Voyage AI embeddings (voyage-3 model, 1024 dimensions) via `backend/rag_engine/embedder.py`
- Retriever with similarity search, company scoping, data type filtering, agent scoping
- Web ingestion via Firecrawl: URL fetch, HTML strip, chunk, embed, store (`backend/rag_engine/ingestion/web.py`)
- SHA-256 content deduplication in ingestion pipeline
- Recency decay scoring for evidence freshness (`apps/decision_os/ingestion.py`)
- Confidence scoring by source type: web 0.8, doc 0.9, api 0.85, manual 0.95
- 5 domain packs: transformfit_training_intelligence, oracle_health_intelligence, fitness_app_intelligence, alex_recruiting_intelligence, founder_foundry_intelligence
- 4 research agents: researcher-appstore, researcher-arxiv, researcher-reddit, researcher-web
- Research Director and Research Ops agents for research management
- MCP tools: search_knowledge, ingest_url
- Evidence model with provenance: source, source_url, fetched_at, confidence, content_hash

**What is missing or weak:**
- No evidence quality scoring beyond source-type heuristic
- No cross-source triangulation (same claim from multiple sources)
- No contradiction detection
- No evidence expiry or staleness alerts
- No research scheduling (all ingestion is manual or on-demand)
- No research coverage maps (which topics are well-covered vs gaps)
- No citation management or bibliography generation
- No evidence graph (claims linked to sources linked to decisions)

### 25X Target:
- Evidence quality scoring: multi-signal scoring including source authority, recency, corroboration, and methodology
- Cross-source triangulation: when multiple sources support the same claim, confidence increases automatically
- Contradiction detection: system flags when new evidence contradicts existing beliefs, with alert to relevant decision owners
- Evidence expiry: time-based staleness with automatic refresh scheduling
- Research scheduling: automated crawl cadence per domain, per source type, with freshness targets
- Research coverage maps: visual maps showing topic coverage depth and identifying blind spots
- Citation management: every claim in the system links to its evidence chain
- Evidence graph: navigable graph connecting claims, sources, decisions, and outcomes

### Gap:
This is the most mature domain, with real infrastructure (pgvector, Voyage embeddings, Firecrawl, Supabase). The gap is in intelligence quality: no triangulation, no contradiction detection, no staleness management, no coverage mapping. The system ingests well but does not reason about what it knows vs what it does not know.

### Wave: 1
### Required Agents: Knowledge Engineer, Research Director, Research Ops, 4 researcher agents, Pulse (data science)
### Dependencies: Platform Infrastructure (for scheduled ingestion), Data and Analytics (for evidence graph)

---

## DOMAIN 8: Portfolio Management

### Current Maturity: Emerging (1.8)

**Current Capabilities (verified in code):**
- Company model with full lifecycle: concept, validation, mvp, growth, scale (`apps/decision_os/models.py`)
- Company registry with 8+ companies: transformfit, oracle-health, apex-social-studio, apex-fitness-studio, apex-design-studio, apex-template-studio, apex-innovation-studios, founder-intelligence-os, etc.
- Per-company configuration: domain, stage, tech_stack, target_market, funding_status, constraints, budget
- Company-scoped RAG: knowledge chunks tagged by company_id
- Company-scoped foundry blueprints via `control_plane/foundry.py`
- Tenant model in control plane with health_score
- Multi-tenant API endpoints: `/api/tenants`, `/api/tenants/{id}/scorecard`
- Domain packs per company for specialized knowledge

**What is missing or weak:**
- No cross-company dashboards
- No shared capability library (each company is siloed)
- No portfolio-level metrics or reporting
- No company onboarding automation (setup is manual)
- No resource allocation across portfolio
- No company comparison views
- No graduation criteria (when a company moves from one stage to the next)
- Health scores are placeholder values, not computed from real signals

### 25X Target:
- Cross-company capability dashboard: see all companies, their maturity levels, and gaps in one view
- Shared capability library: capabilities proven in one company are templated for reuse in others
- Portfolio metrics: aggregate revenue, burn rate, capability maturity, and strategic health across all companies
- Company onboarding automation: new company setup creates all required artifacts, seeds RAG, and assigns agent teams
- Resource allocation optimizer: given constraints, recommend where to invest effort across the portfolio
- Company comparison matrix: side-by-side capability maturity, strategy health, and execution velocity
- Stage graduation: explicit criteria for advancing from concept to validation to MVP to growth to scale
- Portfolio rebalancing alerts: when one company consumes disproportionate resources or stalls

### Gap:
The multi-company infrastructure exists (company registry, company-scoped RAG, tenant APIs) but operates as isolated silos. There is no cross-company view, no shared learning, no portfolio-level optimization. Company health scores are static, not computed. Onboarding is entirely manual.

### Wave: 3
### Required Agents: Susan (orchestrator), Steve (strategy), Ledger (finance), Vault (fundraising)
### Dependencies: Capability Management (for cross-company maturity), Platform Infrastructure (for dashboards)

---

## DOMAIN 9: Operator Experience

### Current Maturity: Emerging (1.5)

**Current Capabilities (verified in code):**
- CLI via `bin/jake` with 10 commands: check, status, sync-intel, context, new, run-decision, debate, ingest-intel, debrief, smoke
- Operator console: vanilla HTML/JS/CSS app (`apps/operator-console/`) with operator debrief JSON payload
- Intelligence cockpit: separate HTML/JS app (`apps/intelligence-cockpit/`) with FastAPI backend
- Operator debrief: structured JSON with debrief items, action items for mike and susan, status
- `bin/os-context` script for workspace state printing
- MCP server exposing 7 tools to Claude Desktop/Code
- Susan commands: 12 slash commands (susan-query, susan-fast, susan-think, susan-design, susan-foundry, susan-plan, susan-status, susan-team, susan-assets, susan-refresh, susan-route, susan-bootstrap)
- Claude skills: 7 skills (capability-gap-map, company-builder, decision-room, link-checker, research-enrichment, research-packet, susan-protocols)

**What is missing or weak:**
- No proactive notifications or alerts
- No task queue or inbox
- No progress tracking for long-running operations
- No mobile access
- No keyboard shortcuts or power-user workflows
- Console is read-only display, not interactive control surface
- No search across all OS objects
- No natural language query interface for the OS
- No onboarding for new operators
- No audit log viewer
- Debrief is static JSON, not real-time

### 25X Target:
- Proactive alert system: system pushes notifications when decisions need attention, evidence expires, capabilities stall, or experiments complete
- Task queue: operators see a prioritized inbox of actionable items
- Progress tracking: long-running Susan runs, ingestion jobs, and decision pipelines show real-time progress
- Interactive control surface: operator console allows clicking through to edit decisions, capabilities, and strategies
- Natural language query: ask the OS anything in plain language and get structured answers with citations
- Power-user keyboard shortcuts and command palette
- Mobile-responsive operator dashboard
- Unified search across all OS objects (decisions, capabilities, evidence, runs, companies)
- Audit log viewer: see every system action with timestamps and provenance
- Onboarding wizard: new operators are guided through the system with progressive disclosure

### Gap:
The operator experience is split across 3 surfaces (CLI, operator console, intelligence cockpit) with no cohesion. The CLI is functional but the web surfaces are display-only. There are no proactive features -- the system only acts when asked. There is no unified search, no task queue, and no progress tracking.

### Wave: 2
### Required Agents: Atlas (engineering), Marcus (UX), Guide (customer success)
### Dependencies: Platform Infrastructure (for real-time updates), Decision Intelligence (for task queue)

---

## DOMAIN 10: Platform Infrastructure

### Current Maturity: Nascent (1.3)

**Current Capabilities (verified in code):**
- Supabase for pgvector storage and RPC
- FastAPI control plane with CORS middleware (`backend/control_plane/main.py`)
- MCP server using FastMCP (`backend/mcp_server/server.py`)
- File-backed YAML persistence for Decision OS objects
- Python virtual environment with dependencies managed via pyproject.toml
- Vercel config for operator console static hosting
- Health check endpoint (`/api/health`)
- Run/job management in control plane (`backend/control_plane/jobs.py`)

**What is missing or weak:**
- No authentication or authorization
- No API rate limiting
- No deployment pipeline (CI/CD)
- No monitoring or alerting
- No error tracking (Sentry or equivalent)
- No real-time updates (WebSocket or SSE)
- No database migrations management
- No backup or disaster recovery
- No environment management (dev/staging/prod)
- No API documentation beyond FastAPI auto-docs
- No load testing
- No secrets management (env vars only)
- CORS is wide open (`allow_origins=["*"]`)

### 25X Target:
- Authentication: API keys for MCP, OAuth for dashboard, role-based access control
- Rate limiting and abuse prevention
- CI/CD pipeline: automated testing, linting, deployment on merge to main
- Monitoring stack: application metrics, error rates, latency tracking, uptime alerts
- Error tracking: structured error capture with Sentry or equivalent
- Real-time updates: WebSocket or SSE for live progress, alerts, and notifications
- Database migration management with version control
- Automated backups with point-in-time recovery
- Environment management: distinct dev, staging, and production configurations
- API documentation with versioning
- Load testing and performance benchmarks
- Secrets management via vault or managed service
- Secure CORS configuration with allowed origins list

### Gap:
This is the weakest domain. The system has no authentication, no deployment pipeline, no monitoring, no error tracking, no real-time updates, and wide-open CORS. It functions as a local development tool, not a production platform. Every other domain's 25X target depends on this domain reaching at least scaling maturity.

### Wave: 1
### Required Agents: Atlas (engineering), Sentinel (security), Nova (AI/ML for deployment automation)
### Dependencies: None -- this is a foundation domain that all others depend on

---

## DOMAIN 11: Content and Marketing

### Current Maturity: Emerging (1.8)

**Current Capabilities (verified in code):**
- Marketing Studio Director agent with messaging architecture, asset system, and campaign system capabilities
- Social Media Studio for instagram, tiktok, reels, short-form content
- Article Studio for blog posts, essays, and newsletters
- Whitepaper Studio for reports and thought leadership
- Memo Studio for internal briefs and decision memos
- Deck Studio for presentations and pitch decks
- Highlight Reel Studio for video clips (sports-specific)
- X Growth Studio for Twitter/X strategy
- Coach Outreach Studio for email sequences
- Oracle Health Marketing Lead and Product Marketing agents
- Prism (brand) and Herald (PR) agents
- Aria (growth marketing) and Beacon (ASO) agents
- Content strategy as a RAG data type with ingested knowledge

**What is missing or weak:**
- No asset pipeline (studios produce text, not published assets)
- No publishing workflow (draft, review, approve, publish)
- No content calendar
- No asset cascade (one research insight cascading to blog, social, deck, email)
- No SEO optimization or keyword tracking
- No analytics integration (which content performs)
- No brand consistency enforcement
- No image generation or visual asset creation
- No A/B testing for content variants
- No distribution automation

### 25X Target:
- Asset pipeline: studio outputs feed into a publishing workflow with draft, review, approve, publish stages
- Content calendar: scheduled content mapped to strategic themes and company milestones
- Asset cascade: one research insight or strategic decision automatically spawns content across blog, social, deck, email, and whitepaper formats
- SEO engine: keyword research, content optimization, ranking tracking
- Analytics integration: content performance feeds back into future content strategy
- Brand consistency scoring: automated checks that content adheres to brand guidelines
- Visual asset generation: studios produce images, diagrams, and social graphics alongside text
- A/B testing: content variants are tested with automatic winner promotion
- Distribution automation: content is automatically distributed to configured channels on schedule

### Gap:
The agent roster for content is extensive (10+ agents covering every format), but the output is disconnected from any publishing or distribution infrastructure. Studios produce text in conversation, but there is no pipeline to turn that text into published, tracked, measured assets. The asset cascade concept is documented but not implemented.

### Wave: 3
### Required Agents: Marketing Studio Director, all content studios, Aria (growth), Beacon (ASO), Prism (brand), Herald (PR)
### Dependencies: Platform Infrastructure (for publishing pipeline), Data and Analytics (for content performance)

---

## DOMAIN 12: Data and Analytics

### Current Maturity: Nascent (1.2)

**Current Capabilities (verified in code):**
- Run tracing: step-level events with timestamps, evidence IDs, confidence, and outputs (`apps/decision_os/telemetry.py`)
- RunTracer class with log(), complete(), fail(), and replay() methods
- Run model with events array, status tracking, and duration computation
- Evidence model with confidence scoring and content hashing
- Monte Carlo simulation for fitness cohort lifecycle (domain-specific)
- Pulse (data science) agent with general analytics capability
- Knowledge chunk metadata in Supabase with timestamps and source tracking

**What is missing or weak:**
- No analytics dashboard
- No telemetry aggregation (individual run traces but no rollups)
- No outcome tracking (did decisions produce expected results)
- No feedback loops (outcomes do not update agent quality or decision weights)
- No A/B testing infrastructure
- No user behavior tracking
- No system health metrics
- No cost tracking (API calls, compute, storage)
- No data export or reporting
- No anomaly detection
- Run traces exist but are never analyzed

### 25X Target:
- Analytics dashboard: system health, decision quality, agent performance, and evidence freshness in one view
- Telemetry aggregation: run traces rolled up into daily/weekly/monthly reports with trend analysis
- Outcome tracking: decisions are revisited against actual results, with quality scoring
- Closed-loop feedback: outcomes update agent quality scores, decision weight defaults, and evidence confidence
- A/B testing infrastructure: any system component can be A/B tested with automatic winner promotion
- Cost tracking: every API call, embedding, and compute operation tracked with cost attribution
- Data export: any OS object can be exported as CSV, JSON, or PDF
- Anomaly detection: system alerts when metrics deviate significantly from baseline
- System health metrics: uptime, latency, error rates, and throughput tracked and visualized

### Gap:
The telemetry model exists (RunTracer is well-designed) but the data it captures is never analyzed or acted upon. There are no dashboards, no rollups, no outcome correlation, and no feedback loops. The system generates traces but never learns from them. This is the critical missing piece for self-improvement.

### Wave: 1
### Required Agents: Pulse (data science), Nova (AI/ML), Atlas (engineering), Algorithm Lab
### Dependencies: Platform Infrastructure (for dashboard hosting and storage)

---

## NET-NEW CAPABILITIES REQUIRED FOR V5

These capabilities do not exist in any form today and must be built from scratch.

### N1: Semantic Agent Router
- Replace keyword-based routing with embedding-similarity routing
- Each agent declares capability vectors; incoming tasks are matched semantically
- Fallback to model-based routing for ambiguous tasks
- Wave: 1, Owner: Nova + Atlas

### N2: Agent Memory System
- Persistent, scoped memory per agent per company per project
- Memory types: factual (what is true), procedural (how to do things), episodic (what happened)
- Memory consolidation: periodic summarization of episodic memory into factual/procedural
- Wave: 1, Owner: Nova + Knowledge Engineer

### N3: Multi-Agent Reasoning Protocol
- Agents can invoke other agents as tools within a reasoning chain
- Structured handoff format: context summary, specific question, expected output format
- Parallel fan-out for independent sub-tasks with result merging
- Wave: 1, Owner: Susan + Nova + Atlas

### N4: Outcome Tracking and Feedback System
- Every decision, recommendation, and experiment is tracked to outcome
- Outcomes feed back into agent quality scores, decision weights, and evidence confidence
- Automatic reversal alerts when outcomes diverge from predictions
- Wave: 1, Owner: Pulse + Susan

### N5: Real-Time Event System
- WebSocket or SSE-based event bus for system-wide notifications
- Events: decision needs attention, evidence expired, capability stalled, experiment completed, agent conflict detected
- Subscriber model: operators and agents can subscribe to event types
- Wave: 2, Owner: Atlas + Sentinel

### N6: Design Artifact Pipeline
- Studios output structured design specifications (not just text)
- Specifications can be exported to Figma, HTML, or component library format
- Design decisions are version-controlled and linked to user research
- Wave: 2, Owner: Marcus + Design Studio Director + Atlas

### N7: Content Publishing Pipeline
- Studio text outputs feed into a publish workflow: draft, review, approve, publish
- Asset cascade: one insight spawns blog + social + deck + email automatically
- Distribution automation with channel configuration
- Wave: 3, Owner: Marketing Studio Director + Aria + Atlas

### N8: Cross-Company Intelligence Sharing
- Insights and capabilities proven in one company are flagged for portfolio reuse
- Privacy-preserving: company-specific data stays scoped, only patterns and capabilities are shared
- Wave: 3, Owner: Susan + Steve + Shield (legal)

---

## WAVE SEQUENCING

### Wave 1: Foundation (Weeks 1-8)
Build the infrastructure and intelligence backbone that every other capability depends on.

| Priority | Capability | Domain | Current | Target | Key Agent |
|----------|-----------|--------|---------|--------|-----------|
| 1.1 | Authentication and access control | Platform | Nascent | Scaling | Atlas, Sentinel |
| 1.2 | CI/CD and deployment pipeline | Platform | Nascent | Scaling | Atlas |
| 1.3 | Semantic agent routing | Agent Orchestration | Nascent | Emerging | Nova, Atlas |
| 1.4 | Agent memory persistence | Agent Orchestration | Nascent | Emerging | Nova, Knowledge Engineer |
| 1.5 | LLM-powered debate engine | Decision Intelligence | Nascent | Emerging | Steve, Freya |
| 1.6 | Evidence quality scoring | Intelligence | Emerging | Scaling | Knowledge Engineer, Research Ops |
| 1.7 | Outcome tracking system | Data & Analytics | Nascent | Emerging | Pulse, Susan |
| 1.8 | Telemetry aggregation dashboards | Data & Analytics | Nascent | Emerging | Pulse, Atlas |
| 1.9 | Monitoring and error tracking | Platform | Nascent | Emerging | Atlas, Sentinel |
| 1.10 | Automated capability discovery | Capability Management | Nascent | Emerging | Susan, Compass |

**Wave 1 success criteria:**
- System has authentication, deployment, and monitoring
- Agents route semantically and persist memory across invocations
- Decisions use LLM reasoning in debate, not string templates
- Evidence quality is scored beyond source-type heuristics
- Every run produces tracked outcomes
- Dashboards show system health and decision quality

### Wave 2: Intelligence Layer (Weeks 9-20)
Build the reasoning, learning, and creative capabilities that make the system genuinely intelligent.

| Priority | Capability | Domain | Current | Target | Key Agent |
|----------|-----------|--------|---------|--------|-----------|
| 2.1 | Multi-agent reasoning protocol | Agent Orchestration | Nascent | Scaling | Susan, Nova |
| 2.2 | Studio memory writeback | Studio Operations | Nascent | Emerging | All studios, Knowledge Engineer |
| 2.3 | Experiment tracking system | Studio Operations | Nascent | Emerging | AI Eval Specialist, Research Ops |
| 2.4 | Real-time event system | Platform | Nascent | Emerging | Atlas |
| 2.5 | Proactive operator alerts | Operator Experience | Nascent | Emerging | Atlas, Guide |
| 2.6 | Interactive operator dashboard | Operator Experience | Nascent | Emerging | Marcus, Atlas |
| 2.7 | Future-back planning engine | Innovation & Strategy | Nascent | Emerging | Steve, Susan |
| 2.8 | Design artifact pipeline | UX & Design | Nascent | Emerging | Marcus, Design Studio Dir |
| 2.9 | Contradiction detection | Intelligence | Nascent | Emerging | Knowledge Engineer |
| 2.10 | Closed-loop feedback | Data & Analytics | Nascent | Emerging | Pulse, Nova |

**Wave 2 success criteria:**
- Agents collaborate on multi-step reasoning chains
- Studios write back cases and learnings that improve future runs
- Experiments are proposed, tracked, and resolved systematically
- Operators receive proactive alerts and can interact with the dashboard
- Strategic planning works backward from target state
- Evidence contradictions are automatically detected and flagged
- Outcomes feed back into agent and decision quality

### Wave 3: Scale Layer (Weeks 21-36)
Build the multi-company, content, and portfolio capabilities that multiply impact.

| Priority | Capability | Domain | Current | Target | Key Agent |
|----------|-----------|--------|---------|--------|-----------|
| 3.1 | Content publishing pipeline | Content & Marketing | Nascent | Emerging | Marketing Studio Dir, Aria |
| 3.2 | Asset cascade system | Content & Marketing | Nascent | Emerging | All content studios |
| 3.3 | Cross-company dashboards | Portfolio Management | Nascent | Emerging | Susan, Steve, Ledger |
| 3.4 | Shared capability library | Portfolio Management | Nascent | Emerging | Susan, Compass |
| 3.5 | Company onboarding automation | Portfolio Management | Nascent | Emerging | Susan, Atlas |
| 3.6 | Cross-company intelligence sharing | Portfolio Management | Nascent | Emerging | Susan, Shield |
| 3.7 | Natural language OS query | Operator Experience | Nascent | Emerging | Nova, Atlas |
| 3.8 | Scenario planning engine | Innovation & Strategy | Nascent | Emerging | Steve, Pulse |
| 3.9 | Brand consistency scoring | Content & Marketing | Nascent | Emerging | Prism, AI Eval Specialist |
| 3.10 | A/B testing infrastructure | Data & Analytics | Nascent | Emerging | Pulse, Atlas |

**Wave 3 success criteria:**
- Content moves from studio output to published, tracked assets automatically
- Portfolio companies are visible in a single dashboard with cross-company metrics
- New companies can be onboarded with automated setup
- Proven capabilities in one company can be templated and reused
- Operators can query the OS in natural language
- Strategic scenarios are branched, tracked, and revisited

---

## RISK REGISTER

| Risk | Severity | Mitigation |
|------|----------|------------|
| Platform debt blocks all intelligence improvements | Critical | Wave 1 prioritizes platform before intelligence |
| Agent memory introduces stale or toxic context | High | Memory consolidation with periodic review and decay |
| Multi-agent reasoning creates circular dependencies | High | Strict handoff protocol with depth limits |
| LLM-powered debate costs explode | Medium | Token budgets per debate mode, caching for repeated queries |
| Portfolio management introduces privacy leaks | High | Company-scoped data isolation, shared pattern library only |
| Studio writeback produces low-quality cases | Medium | Quality gating on case entries, human review for first 50 |
| Outcome tracking requires human input that does not arrive | High | Default timeout with escalation, minimum-viable outcome signals |
| Design artifact pipeline scope creep | Medium | Start with wireframe-level output only, not pixel-perfect |

---

## MEASUREMENT FRAMEWORK

### Leading Indicators (check weekly)
- Agent routing accuracy (% of tasks routed to correct agent)
- Evidence freshness (% of corpus updated in last 30 days)
- Decision pipeline completion rate (% of decisions that reach output contract)
- Run trace completeness (% of runs with all events logged)

### Lagging Indicators (check monthly)
- Decision outcome accuracy (% of decisions whose predicted outcomes matched actual)
- Capability maturity velocity (average maturity increase per month across all capabilities)
- Studio output quality (human-rated quality of studio outputs on 1-5 scale)
- Operator engagement (frequency and depth of operator interactions per week)

### 25X Indicators (check quarterly)
- Throughput: decisions processed per week (current: ~2, target: 50)
- Self-improvement rate: % of system components that have auto-updated based on feedback (current: 0%, target: 30%)
- Time-to-insight: median time from question to evidence-backed answer (current: 15 min manual, target: 30 sec automated)
- Portfolio coverage: % of company capabilities tracked and scored (current: ~10%, target: 90%)

---

## AGENT ALLOCATION SUMMARY

| Agent | Primary Domains | Wave |
|-------|----------------|------|
| Susan | Capability Management, Portfolio Management, Studio Operations | 1, 2, 3 |
| Steve | Decision Intelligence, Innovation & Strategy | 1, 2 |
| Atlas | Platform Infrastructure, Operator Experience | 1, 2, 3 |
| Nova | Agent Orchestration, Data & Analytics | 1, 2 |
| Sentinel | Platform Infrastructure | 1 |
| Knowledge Engineer | Intelligence & Research, Agent Orchestration | 1, 2 |
| Research Ops | Intelligence & Research | 1 |
| Pulse | Data & Analytics, Innovation & Strategy | 1, 2, 3 |
| Marcus | Operator Experience, UX & Design | 2 |
| Freya | Decision Intelligence | 1 |
| Compass | Capability Management | 1 |
| Design Studio Director | UX & Design | 2 |
| Marketing Studio Director | Content & Marketing | 3 |
| Guide | Operator Experience | 2 |
| Ledger | Portfolio Management | 3 |
| AI Eval Specialist | Studio Operations | 2 |
| Aria | Content & Marketing | 3 |
| Shield | Portfolio Management | 3 |

---

## AGGREGATE MATURITY MAP

| Domain | Current | After Wave 1 | After Wave 2 | After Wave 3 | 25X Target |
|--------|---------|-------------|-------------|-------------|------------|
| Decision Intelligence | 2.0 | 2.8 | 3.5 | 4.0 | 4.0 |
| Capability Management | 2.0 | 2.5 | 3.2 | 4.0 | 4.0 |
| Innovation & Strategy | 1.8 | 2.0 | 3.0 | 3.8 | 4.0 |
| UX & Design | 2.2 | 2.2 | 3.0 | 3.5 | 4.0 |
| Agent Orchestration | 2.0 | 3.0 | 3.8 | 4.2 | 4.5 |
| Studio Operations | 1.8 | 1.8 | 3.0 | 3.5 | 4.0 |
| Intelligence & Research | 2.8 | 3.5 | 4.0 | 4.2 | 4.5 |
| Portfolio Management | 1.8 | 1.8 | 2.0 | 3.5 | 4.0 |
| Operator Experience | 1.5 | 1.5 | 3.0 | 3.8 | 4.0 |
| Platform Infrastructure | 1.3 | 2.8 | 3.5 | 4.0 | 4.0 |
| Content & Marketing | 1.8 | 1.8 | 2.0 | 3.5 | 4.0 |
| Data & Analytics | 1.2 | 2.5 | 3.5 | 4.0 | 4.0 |
| **Aggregate** | **1.85** | **2.35** | **3.13** | **3.83** | **4.08** |

---

## BOTTOM LINE

The Startup Intelligence OS has exceptional breadth -- 60 agents, 18 studios, a 10-phase orchestrator, a 5-mode debate engine, and a 10,788-chunk RAG corpus. Very few solo-founder systems have this kind of architectural surface area.

The gap to 25X is not more agents or more studios. It is:

1. **Infrastructure** (auth, deployment, monitoring, real-time) -- the system runs as a local dev tool, not a platform
2. **Closed loops** (outcome tracking, feedback, memory writeback) -- the system produces outputs but never learns from results
3. **Agent collaboration** (memory, handoff, multi-agent reasoning) -- 60 agents that cannot talk to each other are 60 isolated functions
4. **Evidence intelligence** (triangulation, contradiction detection, quality scoring) -- the RAG corpus is large but the system does not reason about what it knows

Wave 1 addresses all four. If Wave 1 succeeds, the system transitions from "impressive prototype" to "operational intelligence platform." If Wave 1 does not succeed, adding more agents, studios, or features will not change the fundamental ceiling.

The highest-leverage single investment is **Agent Orchestration** (Domain 5). Making 60 agents collaborate with shared memory, semantic routing, and multi-agent reasoning chains would multiply the value of every other domain without adding a single new agent.
