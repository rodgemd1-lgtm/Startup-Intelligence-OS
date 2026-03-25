# V3X + Susan Redesign — Master Plan

**Date**: 2026-03-25
**Status**: DRAFT — Awaiting Mike approval
**Depends On**: V1 (Memory Migration) COMPLETE
**Architecture**: VoltAgent-standard agents, department-based routing, Jake v5 as root supervisor

---

## Vision

Two parallel workstreams running simultaneously:

| Stream | Scope | Goal |
|--------|-------|------|
| **A: Jake + OpenClaw PAI** | V2 → V3X → V4-V10 | Wire 218 agents into OpenClaw, build the PAI stack to full autonomy |
| **B: Susan Redesign** | Department org + agent rebuild | Transform 218 agents from ad-hoc groups into a department-based organization with VoltAgent-standard definitions |

Both streams share the same agent roster. Stream B produces the agents; Stream A wires them into the runtime.

---

## Stream B: Susan Department Redesign

### Why Departments, Not Groups

The current 17 groups from the overlap analysis are a merge artifact — they map where agents came from, not how they should work together. Departments have:

- A **department head** (supervisor agent) who owns routing within the department
- A **mandate** (what the department is responsible for)
- **Internal delegation** (head routes to the right specialist)
- **External interfaces** (how departments collaborate)
- A **communication protocol** (JSON-structured handoffs)

### Department Architecture

```
Jake (CEO / Root Supervisor)
│
├── Susan (COO / Capability Foundry)
│   Coordinates cross-department work, capability mapping, maturity scoring
│
├── Kira (Chief of Staff / Intent Router)
│   Classifies incoming requests, routes to correct department head
│
└── 15 Departments:
    │
    ├── DEPT 01: Strategy & Business (13 agents)
    │   Head: steve-strategy
    │   Mandate: Business strategy, legal, finance, fundraising, partnerships, project management
    │   Agents: steve-strategy, shield-legal-compliance, bridge-partnerships,
    │           ledger-finance, vault-fundraising, recruiting-strategy-studio,
    │           guide-customer-success, business-analyst, project-manager,
    │           sales-engineer, scrum-master, content-marketer, seo-specialist
    │   Interfaces: Product (GTM), Growth (positioning), Research (market intel)
    │
    ├── DEPT 02: Product (10 agents)
    │   Head: compass-product
    │   Mandate: Product strategy, UX, design systems, accessibility, brand
    │   Agents: compass-product, ai-product-manager, marcus-ux,
    │           mira-emotional-experience, conversation-designer, echo-neuro-design,
    │           lens-accessibility, prism-brand, ux-design-process, ui-designer
    │   Interfaces: Engineering (specs), Strategy (roadmap), Research (user research)
    │
    ├── DEPT 03: Core Engineering (14 agents)
    │   Head: atlas-engineering
    │   Mandate: Architecture, full-stack development, APIs, real-time, mobile, desktop
    │   Agents: atlas-engineering, api-designer, backend-developer, frontend-developer,
    │           fullstack-developer, graphql-architect, microservices-architect,
    │           mobile-developer, mobile-app-developer, electron-pro,
    │           websocket-engineer, api-documenter, mcp-developer, cli-developer
    │   Interfaces: Language Specialists (implementation), Infrastructure (deployment), QA (testing)
    │
    ├── DEPT 04: Language & Framework Engineering (28 agents)
    │   Head: typescript-pro (primary) — routes by language/framework match
    │   Mandate: Language-specific and framework-specific deep expertise
    │   Agents: angular-architect, cpp-pro, csharp-developer, django-developer,
    │           dotnet-core-expert, dotnet-framework-4.8-expert, elixir-expert,
    │           expo-react-native-expert, fastapi-developer, flutter-expert,
    │           golang-pro, java-architect, javascript-pro, kotlin-specialist,
    │           laravel-specialist, nextjs-developer, php-pro, powershell-5.1-expert,
    │           powershell-7-expert, python-pro, rails-expert, react-specialist,
    │           rust-engineer, spring-boot-engineer, sql-pro, swift-expert,
    │           typescript-pro, vue-expert
    │   Routing: Auto-detected from file extension, import statements, or explicit request
    │   Interfaces: Core Engineering (architecture decisions), QA (language-specific testing)
    │
    ├── DEPT 05: Infrastructure & Platform (17 agents)
    │   Head: cloud-architect
    │   Mandate: Cloud, containers, networking, IaC, SRE, platform engineering
    │   Agents: cloud-architect, azure-infra-engineer, database-administrator,
    │           deployment-engineer, devops-engineer, devops-incident-responder,
    │           docker-expert, incident-responder, kubernetes-specialist,
    │           network-engineer, platform-engineer, sre-engineer,
    │           terraform-engineer, terragrunt-expert, windows-infra-admin,
    │           m365-admin, it-ops-orchestrator
    │   Interfaces: Engineering (deployment), QA (chaos engineering), Data (data infra)
    │
    ├── DEPT 06: Quality & Security (15 agents)
    │   Head: forge-qa (quality) + sentinel-security (security) — dual heads
    │   Mandate: QA, testing, security, compliance, code review, debugging
    │   Agents: forge-qa, sentinel-security, ai-evaluation-specialist,
    │           accessibility-tester, ad-security-reviewer, architect-reviewer,
    │           chaos-engineer, code-reviewer, compliance-auditor, debugger,
    │           error-detective, penetration-tester, performance-engineer,
    │           powershell-security-hardening, test-automator
    │   Interfaces: All engineering departments (review gates), Strategy (compliance)
    │
    ├── DEPT 07: Data & AI (14 agents)
    │   Head: nova-ai
    │   Mandate: Data science, ML/AI, LLM architecture, data engineering, prompt engineering
    │   Agents: nova-ai, pulse-data-science, algorithm-lab, knowledge-engineer,
    │           ai-engineer, data-analyst, data-engineer, database-optimizer,
    │           llm-architect, ml-engineer, mlops-engineer, nlp-engineer,
    │           postgres-pro, prompt-engineer
    │   Interfaces: Engineering (AI integration), Research (academic papers), Infrastructure (MLOps)
    │
    ├── DEPT 08: Developer Experience (12 agents)
    │   Head: dx-optimizer
    │   Mandate: Build systems, tooling, documentation, git workflows, refactoring, DX
    │   Agents: dx-optimizer, build-engineer, dependency-manager, documentation-engineer,
    │           git-workflow-manager, legacy-modernizer, powershell-module-architect,
    │           powershell-ui-architect, refactoring-specialist, slack-expert,
    │           tooling-engineer, wordpress-master
    │   Interfaces: All engineering departments (tooling), Infrastructure (CI/CD)
    │
    ├── DEPT 09: Research (14 agents)
    │   Head: research-director
    │   Mandate: Research coordination, source-specific research, competitive/market analysis
    │   Agents: research-director, research-ops, researcher-web, researcher-arxiv,
    │           researcher-reddit, researcher-appstore, competitive-analyst,
    │           data-researcher, market-researcher, research-analyst,
    │           search-specialist, trend-analyst, link-validator, research (CC)
    │   Interfaces: All departments (research requests), Strategy (market intel), Data (analysis)
    │
    ├── DEPT 10: Growth & Marketing (7 agents)
    │   Head: aria-growth
    │   Mandate: Growth strategy, community, PR, ASO, outreach, social
    │   Agents: aria-growth, haven-community, herald-pr, herald (CC),
    │           beacon-aso, coach-outreach-studio, x-growth-studio
    │   Interfaces: Strategy (positioning), Creative (assets), Product (adoption)
    │
    ├── DEPT 11: Content & Design Studio (15 agents)
    │   Head: design-studio-director
    │   Mandate: Visual design, content creation, presentations, landing pages, social media
    │   Agents: design-studio-director, marketing-studio-director, deck-studio,
    │           landing-page-studio, app-experience-studio, article-studio,
    │           memo-studio, social-media-studio, whitepaper-studio,
    │           instagram-studio, recruiting-dashboard-studio, photography-studio,
    │           slideworks-strategist, slideworks-creative-director, slideworks-builder
    │   Interfaces: Growth (campaign assets), Product (design systems), Strategy (pitch decks)
    │
    ├── DEPT 12: Film & Media Production (17 agents)
    │   Head: film-studio-director
    │   Mandate: Film production, video editing, VFX, audio, music, distribution
    │   Agents: film-studio-director, screenwriter-studio, cinematography-studio,
    │           editing-studio, color-grade-studio, vfx-studio, sound-design-studio,
    │           music-score-studio, production-designer-studio, production-manager-studio,
    │           talent-cast-studio, distribution-studio, legal-rights-studio,
    │           highlight-reel-studio, audio-gen-engine, film-gen-engine, image-gen-engine
    │   Interfaces: Creative (visual assets), Growth (video content), Product (demos)
    │
    ├── DEPT 13: Health & Fitness Science (7 agents)
    │   Head: coach-exercise-science
    │   Mandate: Exercise science, nutrition, sleep, workout programming, coaching architecture
    │   Agents: coach-exercise-science, sage-nutrition, drift-sleep-recovery,
    │           workout-program-studio, coaching-architecture-studio,
    │           workout-session-studio, training-research-studio
    │   Interfaces: Research (training science), Data (biometrics), Product (app features)
    │
    ├── DEPT 14: Behavioral Science (3 agents)
    │   Head: freya-behavioral-economics
    │   Mandate: Behavioral economics, sports psychology, gamification design
    │   Agents: freya-behavioral-economics, flow-sports-psychology, quest-gamification
    │   Interfaces: Product (engagement), Health Science (motivation), Growth (retention)
    │
    └── DEPT 15: Specialized Domains (8 agents)
        Head: fintech-engineer (rotates by active domain)
        Mandate: Blockchain, embedded systems, fintech, gaming, IoT, payments, risk
        Agents: blockchain-developer, embedded-systems, fintech-engineer,
                game-developer, iot-engineer, payment-integration,
                quant-analyst, risk-manager
        Interfaces: Engineering (integration), Strategy (domain analysis), Data (domain data)
```

### Jake's Direct Reports (not departments)

| Agent | Role | Responsibility |
|-------|------|---------------|
| susan | COO / Capability Foundry | Cross-department coordination, capability mapping, maturity scoring |
| kira | Chief of Staff / Intent Router | Classify requests, route to department heads, confidence scoring |
| orchestrator | Multi-Agent Coordinator | Parallel task execution, team assembly from multiple departments |
| digest | Intelligence Digest | Cross-department pattern synthesis |
| oracle-brief | Executive Briefing | Stakeholder-ready summaries |
| sentinel-health | System Health | Monitor agent performance, error rates, context health |
| pattern-matcher | Cross-Domain Patterns | Detect patterns that transfer between companies/projects |
| antifragility-monitor | Antifragility Assessment | Track whether automation is helping or hurting |
| optionality-scout | Option Space Explorer | Flag lock-in risks and irreversible decisions |

### Vertical Divisions (company-specific, report to Susan)

| Division | Head | Agents |
|----------|------|--------|
| Oracle Health | oracle-health-marketing-lead | oracle-health-product-marketing, + temporary assignments from departments |
| (Future verticals get their own divisions when they have 2+ dedicated agents) |

---

### Agent Gold Standard Format

Every agent (new and rebuilt) follows this format:

```yaml
---
name: agent-name
description: One-line description
department: dept-name
role: specialist | supervisor | lead
supervisor: department-head-name
model: claude-sonnet-4-6 | claude-opus-4-6 | claude-haiku-4-5
tools:
  - tool_name_1
  - tool_name_2
guardrails:
  input: ["max_tokens: 8000", "required_fields: task, context"]
  output: ["no_pii", "json_valid"]
memory:
  type: session | persistent | shared
  scope: department | cross-department
hooks:
  on_start: validate_input
  on_complete: emit_trace
  on_error: escalate_to_supervisor
---

# {Agent Name}

## Identity
{Deep background, training, philosophy — 3-5 sentences establishing expertise and perspective}

## Mandate
{What this agent owns. Clear scope boundaries. What it does NOT do.}

## Workflow Phases

### Phase 1: Intake
- Validate request against mandate
- Check for required context
- Route to correct sub-specialty if needed

### Phase 2: Analysis
- {Domain-specific analysis steps}
- {Framework application}
- {Evidence gathering}

### Phase 3: Synthesis
- {Combine findings}
- {Apply judgment}
- {Generate recommendations}

### Phase 4: Delivery
- Format output per communication protocol
- Tag confidence level
- Flag handoff needs

## Communication Protocol

### Input Schema
```json
{
  "task": "string — what needs to be done",
  "context": "string — relevant background",
  "constraints": ["string — any limitations"],
  "priority": "P0 | P1 | P2 | P3",
  "requestor": "string — who's asking (agent or human)"
}
```

### Output Schema
```json
{
  "agent": "agent-name",
  "department": "dept-name",
  "result": "string — the deliverable",
  "confidence": "HIGH | MEDIUM | LOW",
  "evidence": ["string — supporting data points"],
  "handoffs": [{"to": "agent-name", "reason": "string"}],
  "trace_id": "string — for observability"
}
```

## Integration Points
- **Receives from**: {list agents/departments that send work here}
- **Sends to**: {list agents/departments this agent hands off to}
- **Escalates to**: {supervisor agent name}
- **Collaborates with**: {peer agents for joint work}

## Domain Expertise
{Detailed specialization areas, frameworks, methodologies, tools}

## Checklists

### Quality Gate
- [ ] Input validated against schema
- [ ] All required context present
- [ ] Output matches communication protocol
- [ ] Confidence level justified
- [ ] Handoffs identified and tagged

### Escalation Triggers
- Confidence < MEDIUM on P0/P1 tasks
- Request outside mandate scope
- Conflicting requirements detected
- 3+ failed attempts on same task
```

---

## Stream A: Jake + OpenClaw PAI (V2 → V10)

### V2: Agent Integration (8 tasks)

**Goal**: Wire all 218 agents into OpenClaw as callable skills.

| Task | Description | Depends On |
|------|-------------|------------|
| 2.1 | Susan OpenClaw Skill (skill.json + handler.ts) | V1 complete |
| 2.2 | mcporter MCP bridge (all MCP servers) | 2.1 |
| 2.3 | Fabric REST API sidecar (port 8080) | V1 complete |
| 2.4 | Claude Code bridge skill (openclaw-claude-code-skill) | 2.1 |
| 2.5 | Agent registry (218 agents, department-tagged) | Stream B dept design |
| 2.6 | Per-pattern model routing (Inference config) | 2.5 |
| 2.7 | Algorithm v1 (Miessler 7-phase reasoning loop) | 2.3, 2.6 |
| 2.8 | Exit criteria verification | All above |

**Exit Criteria**:
- All 218 agents callable from OpenClaw
- Department routing working (Jake → Kira → Head → Specialist)
- Algorithm v1 processing multi-step tasks
- MCP bridge passing all tools through

### V3X: Ecosystem Supercharge (8 tasks — CRITICAL PATH)

**Goal**: Inject external knowledge, observability, and multi-channel reach.

#### Phase 3X-A: External Knowledge (Tasks 1-3)

| Task | Description | Files |
|------|-------------|-------|
| 3X.1 | Add git submodules (fabric, papers-we-love, awesome-openclaw-agents, openclaw-multi-agent-kit, hermes-agent) | `.gitmodules` |
| 3X.2 | Build submodule indexes (fabric_index.json, papers_index.json, agents_index.json) | `pai/knowledge/` |
| 3X.3 | Create 4 knowledge agents (skill-scout, paper-harvester, codex-analyst, pattern-librarian) | `pai/agents/` |

#### Phase 3X-B: Observability (Tasks 4-7)

| Task | Description | Files |
|------|-------------|-------|
| 3X.4 | Supabase schema (agent_traces, pipeline_runs) | `pai/observability/schema.sql` |
| 3X.5 | OTLP bridge (Python, port 4318, batch writes) | `pai/observability/otlp_bridge.py` |
| 3X.6 | Claude Code hooks (trace emission on PostToolUse) | `.claude/settings.json` hooks |
| 3X.7 | Observability agents (trace_analyzer, voltagent_bridge) | `pai/agents/` |

#### Phase 3X-C: Multi-Channel (Task 8)

| Task | Description | Files |
|------|-------------|-------|
| 3X.8 | Cloudflare Workers webhook routing (Telegram/Discord/Slack) | `pai/channels/worker.ts` |

**Exit Criteria**:
- All submodules cloned and indexed
- agent_traces + pipeline_runs storing data in Supabase
- OTLP bridge running on port 4318
- All 218 agents deployed to OpenClaw channels
- Cloudflare Workers routing webhooks end-to-end

### V3: Autonomous Execution (after V3X)

**Goal**: Pipeline orchestration — multi-step tasks run autonomously.

| Task | Description |
|------|-------------|
| 3.1 | Pipeline engine (DAG-based task execution) |
| 3.2 | Approval gates (human-in-the-loop for risky steps) |
| 3.3 | Rollback mechanisms |
| 3.4 | Session persistence (resume interrupted pipelines) |

### V4: Proactive Intelligence

**Goal**: Agents suggest actions before being asked.

| Task | Description |
|------|-------------|
| 4.1 | Signal detection (new data → alert evaluation) |
| 4.2 | Priority scoring (P0-P3 classification) |
| 4.3 | Scheduled intelligence (daily/weekly agent runs) |
| 4.4 | Proactive briefing (morning brief, weekly digest) |

### V5: Learning Engine

**Goal**: System learns from every interaction.

| Task | Description |
|------|-------------|
| 5.1 | Trace-based learning (what worked, what didn't) |
| 5.2 | Routing feedback (improve Kira's department routing) |
| 5.3 | Agent performance scoring (accuracy, latency, satisfaction) |
| 5.4 | Prompt evolution (auto-improve agent prompts based on outcomes) |

### V6: Multi-Channel

**Goal**: Same intelligence, every surface.

| Task | Description |
|------|-------------|
| 6.1 | Telegram bot (persistent, multi-thread) |
| 6.2 | Discord bot (server + DM) |
| 6.3 | Slack integration |
| 6.4 | Web dashboard (real-time) |
| 6.5 | CLI (enhanced Jake) |

### V7: Visual Command Center

**Goal**: See the whole system at a glance.

| Task | Description |
|------|-------------|
| 7.1 | Department health dashboard |
| 7.2 | Agent trace explorer |
| 7.3 | Pipeline visualizer |
| 7.4 | Cost/performance analytics |

### V8: Cross-Domain Intelligence

**Goal**: Patterns from one domain applied to another.

| Task | Description |
|------|-------------|
| 8.1 | Cross-company pattern detection |
| 8.2 | Academic paper → practical application pipeline |
| 8.3 | Knowledge transfer between departments |

### V9: Marketplace

**Goal**: Agent and skill ecosystem.

| Task | Description |
|------|-------------|
| 9.1 | Skill catalog (searchable, versioned) |
| 9.2 | Agent templates (create new agents from patterns) |
| 9.3 | Community sharing (export/import agent definitions) |

### V10: Full Autonomy

**Goal**: <15 min/day human interaction, 90%+ automation.

| Task | Description |
|------|-------------|
| 10.1 | Self-evolving agents (auto-upgrade prompts and tools) |
| 10.2 | Capability prediction (forecast what's needed next) |
| 10.3 | Autonomous research cycles (detect gap → research → apply) |
| 10.4 | Human-in-the-loop governance (approval for high-risk only) |

---

## Execution Sequence

### Phase 1: Foundation (This Session)
1. **Stream B**: Define department structure (this plan) ✓
2. **Stream B**: Design gold standard agent format ✓
3. **Save**: Architectural decision as memory
4. **Commit**: Plan to repo

### Phase 2: Agent Rebuild (Next 2-3 Sessions)
1. **Stream B**: Rebuild department heads first (15 supervisor agents)
2. **Stream B**: Rebuild existing Susan agents (81) to gold standard
3. **Stream B**: Create new VoltAgent-sourced agents (89) in gold standard
4. **Stream B**: Wire supervisor routing within each department
5. **Stream A**: V2.1-2.4 (Susan OpenClaw skill, MCP bridge, Fabric API, CC bridge)

### Phase 3: Integration (Next 2-3 Sessions)
1. **Stream A**: V2.5-2.8 (Agent registry, model routing, Algorithm v1)
2. **Stream B**: Department integration testing
3. **Stream A**: V3X Phase A (submodules, indexes, knowledge agents)

### Phase 4: Observability + Channels (Next 2-3 Sessions)
1. **Stream A**: V3X Phase B (OTLP, Supabase, trace agents)
2. **Stream A**: V3X Phase C (Cloudflare Workers)
3. **Stream A**: V3 (Autonomous execution)

### Phase 5: Intelligence Layer (Ongoing)
1. **Stream A**: V4 (Proactive intelligence)
2. **Stream A**: V5 (Learning engine)
3. **Stream A**: V6-V10 (Multi-channel → full autonomy)

---

## Totals

| Metric | Count |
|--------|-------|
| Total agents | 218 |
| Departments | 15 |
| Department heads | 15 (+ 2 dual-head departments) |
| Jake's direct reports | 9 |
| Vertical divisions | 1 (Oracle Health) + future |
| PAI versions to build | V2-V10 (9 versions) |
| V3X tasks | 8 |
| Estimated sessions | 10-15 total |

---

## Risk Register

| Risk | Mitigation |
|------|-----------|
| 218 agents too many to rebuild at once | Priority: heads first, then high-use agents, then long-tail |
| Context budget (60% limit) | One department per session, commit + handoff discipline |
| Language specialist agents (28) may be low-value | Auto-route by file extension, no manual invocation needed |
| Department routing adds latency | Kira routes directly to specialist when confidence > 0.9 |
| Protection zones (susan_core, control_plane, mcp_server) | Stream B creates NEW agent files, doesn't modify runtime |

---

## Success Criteria

- [ ] Jake routes any request to the correct department in <2 hops
- [ ] Every agent has gold standard format (YAML + phases + JSON protocol)
- [ ] Department heads can delegate within their team
- [ ] All 218 agents callable from OpenClaw
- [ ] OTLP traces flowing to Supabase
- [ ] V10 target: <15 min/day human interaction
