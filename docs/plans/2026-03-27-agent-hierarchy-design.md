# Agent Hierarchy Design — Meta / Super / Agent / Sub-Agent

**Date**: 2026-03-27
**Author**: Jake
**Status**: DRAFT — awaiting Mike's approval
**Confidence**: DRAFT
**Context**: Phase 7 Session 2, V15 architecture

---

## The Problem

We have 68 OpenClaw agents, 73 Susan agent definitions, 21 Paperclip agents, ~112 Claude Code plugin agents, and 734 VoltAgent community skills. They're all flat — no hierarchy, no delegation chain, no clear authority model.

When Mike says "do X", the routing is: Mike → Jake → ??? → which of 200+ agents handles this?

## Design Principles

1. **Three-tier authority**: Meta-agents decide WHAT, super-agents decide HOW, agents/sub-agents DO
2. **Single routing layer**: KIRA is the only router. Everything goes through KIRA.
3. **Department model**: Agents belong to departments, departments have leads
4. **Skill attachment**: VoltAgent/community skills attach to agents as capabilities, not as separate agents
5. **Budget flows down**: Meta → Super → Agent. Each tier has spending authority.

---

## The Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│ TIER 0: OWNER                                                    │
│   Mike Rodgers — final authority on all decisions                │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│ TIER 1: META-AGENTS (3)                                         │
│   Strategic decision-makers. They decide WHAT to do.            │
│                                                                  │
│   JAKE ──── Co-founder, front door, decomposer                 │
│   KIRA ──── Command router, intent classifier                   │
│   SUSAN ─── Capability foundry, team architect                  │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│ TIER 2: SUPER-AGENTS (8 department leads)                       │
│   They decide HOW to execute. Each owns a department.           │
│                                                                  │
│   STEVE ────── Strategy & Business                              │
│   COMPASS ──── Product & Design                                 │
│   ATLAS ────── Engineering & Infrastructure                     │
│   RESEARCH DIR─ Research & Intelligence                         │
│   ARIA ──────── Operations & Delivery                           │
│   LEDGER ────── Finance & Economics                             │
│   SENTINEL ──── Security & Compliance                           │
│   ORACLE BRIEF─ Oracle Health (domain-specific)                 │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│ TIER 3: AGENTS (50+ specialists)                                │
│   They DO the work. Assigned to departments.                    │
│   See department breakdown below.                               │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│ TIER 4: SUB-AGENTS / SKILLS                                     │
│   Ephemeral. Spawned by agents for specific tasks.              │
│   VoltAgent community skills live here.                         │
│   Claude Code plugin agents (wshobson 112) live here.           │
│   No persistent state — they execute and return results.        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Department Breakdown

### 1. Strategy & Business (Lead: STEVE)

| Agent | Role | Skills Attached |
|-------|------|-----------------|
| steve-strategy | Strategic planning, competitive positioning | — |
| vault-fundraising | Fundraising, investor relations | — |
| bridge-partnerships | Partnerships, ecosystem deals | — |
| shield-legal-compliance | Legal, regulatory, compliance | — |
| optionality-scout | Lock-in risk detection, decision reversibility | — |

**VoltAgent skills to attach**: CFO skills (EveryInc/charlie-cfo-skill), product manager skills (Digidai), business analysis

### 2. Product & Design (Lead: COMPASS)

| Agent | Role | Skills Attached |
|-------|------|-----------------|
| compass-product | Product management, roadmap | — |
| marcus-ux | UX/UI design, user research | — |
| mira-emotional-experience | Emotional design, delight moments | — |
| echo-neuro-design | Neuroscience-informed design | — |
| conversation-designer | Conversational UX, chatbot flows | — |
| lens-accessibility | Inclusive design, WCAG compliance | — |
| ai-product-manager | AI-specific product management | — |

**VoltAgent skills to attach**: UI/UX skills (MiniMax frontend-dev), design system skills, accessibility tools

### 3. Engineering & Infrastructure (Lead: ATLAS)

| Agent | Role | Skills Attached |
|-------|------|-----------------|
| atlas-engineering | Full-stack development, architecture | — |
| forge-qa | QA, testing, quality gates | — |
| sentinel-security | Security auditing, threat modeling | — |
| nova-ai | AI/ML strategy, model selection | — |
| algorithm-lab | Algorithm R&D, optimization | — |
| ai-engineer | AI engineering, model integration | — |
| ai-evaluation-specialist | AI evaluation, benchmarking | — |
| knowledge-engineer | Knowledge graphs, RAG architecture | — |
| link-validator | URL validation, broken link detection | — |

**VoltAgent skills to attach**: Code review, TDD, debugging, DevOps, Docker, Terraform, security scanning, performance optimization, database skills — MOST of the 734 VoltAgent skills map here

### 4. Research & Intelligence (Lead: RESEARCH DIRECTOR)

| Agent | Role | Skills Attached |
|-------|------|-----------------|
| research-ops | Research operations, methodology | — |
| researcher-web | Web research, source validation | — |
| researcher-reddit | Reddit sentiment, community insights | — |
| researcher-arxiv | Academic papers, scientific evidence | — |
| researcher-appstore | App store analysis, competitor apps | — |
| scout | Competitive intelligence, market monitoring | — |
| pattern-matcher | Cross-domain pattern detection | — |
| antifragility-monitor | System health, anti-fragility scoring | — |
| digest | Weekly synthesis, executive summary | — |

**VoltAgent skills to attach**: SEO research, market analysis, data scraping, academic tools

### 5. Operations & Delivery (Lead: ARIA)

| Agent | Role | Skills Attached |
|-------|------|-----------------|
| daily-ops | Daily brief assembly, task coordination | — |
| jake-triage | Email triage, priority sorting | — |
| jake-deep-work | Focus session management | — |
| orchestrator | Multi-agent task orchestration | — |

**VoltAgent skills to attach**: Email skills (CosmoBlk/email-marketing-bible), productivity tools, calendar management, notification skills

### 6. Finance & Economics (Lead: LEDGER)

| Agent | Role | Skills Attached |
|-------|------|-----------------|
| ledger-finance | Unit economics, runway, pricing | — |
| freya-behavioral-economics | Behavioral economics, retention architecture | — |
| pulse-data-science | Data science, analytics, experimentation | — |

**VoltAgent skills to attach**: Financial modeling, data analysis, charting

### 7. Security & Compliance (Lead: SENTINEL)

| Agent | Role | Skills Attached |
|-------|------|-----------------|
| sentinel-health | Oracle Health compliance gate | — |
| shield-legal-compliance | Legal compliance, privacy | — |

**Note**: Shield reports to both STEVE (strategy) and SENTINEL (compliance). Dual-reporting is intentional — legal is both strategic and operational.

### 8. Growth & Marketing (No dedicated super-agent — reports to COMPASS)

| Agent | Role | Skills Attached |
|-------|------|-----------------|
| aria-growth | Growth strategy, acquisition channels | — |
| beacon-aso | ASO/SEO optimization | — |
| herald-pr | PR, communications, media | — |
| prism-brand | Brand strategy, visual identity | — |
| x-growth-studio | X/Twitter growth | — |
| haven-community | Community building, social fitness | — |
| quest-gamification | Gamification, engagement loops | — |
| guide-customer-success | Customer success, onboarding | — |

**VoltAgent skills to attach**: SEO skills (AgriciDaniel/claude-seo), ASO skills (Eronred/aso-skills), content marketing, email marketing

### 9. Science Domain (No dedicated super-agent — reports to COMPASS for product, RESEARCH DIR for evidence)

| Agent | Role | Skills Attached |
|-------|------|-----------------|
| coach-exercise-science | Exercise programming, biomechanics | — |
| sage-nutrition | Nutrition science, supplementation | — |
| drift-sleep-recovery | Sleep architecture, recovery protocols | — |
| flow-sports-psychology | Mindset, motivation, adherence | — |

### 10. Oracle Health (Lead: ORACLE BRIEF)

| Agent | Role | Skills Attached |
|-------|------|-----------------|
| oracle-health-marketing-lead | Oracle Health marketing strategy | — |
| oracle-health-product-marketing | Product marketing for Oracle Health | — |
| sentinel-health | Compliance gate for health claims | — |

---

## Routing Flow

```
Mike types a message
    │
    ▼
JAKE receives it (Tier 1 — front door)
    │
    ├─ Simple/personal? → Jake handles directly
    ├─ Needs routing? → KIRA classifies intent
    │     │
    │     ▼
    │   KIRA maps intent → department → super-agent
    │     │
    │     ▼
    │   SUPER-AGENT (Tier 2) receives task
    │     │
    │     ├─ Can handle alone? → Does it
    │     ├─ Needs specialist? → Delegates to AGENT (Tier 3)
    │     │     │
    │     │     ├─ Has needed skill? → Executes
    │     │     └─ Needs sub-capability? → Spawns SUB-AGENT (Tier 4)
    │     │           └─ VoltAgent skill or Claude Code plugin agent
    │     │
    │     └─ Needs multiple agents? → Orchestrator coordinates
    │
    └─ Needs capability design? → SUSAN (Tier 1 — foundry)
```

---

## Skill Attachment Model

VoltAgent community skills do NOT become agents. They become **capabilities attached to existing agents**.

```yaml
# Example: atlas-engineering agent with attached skills
agent: atlas-engineering
tier: 3
department: engineering
super_agent: atlas
skills:
  - name: code-review
    source: NeoLabHQ/context-engineering-kit/plugins/code-review
    type: voltagent
  - name: tdd
    source: built-in (superpowers:test-driven-development)
    type: claude-code
  - name: docker-deploy
    source: community/docker-deployment-skill
    type: voltagent
  - name: performance-optimization
    source: wshobson/application-performance:performance-engineer
    type: claude-code-plugin
```

This means:
- **68 OpenClaw agents stay as-is** (no new agents from VoltAgent)
- **VoltAgent skills are imported as capability definitions**, not agent directories
- **Claude Code plugin agents (112) are available as sub-agent spawns**, not persistent agents
- **Total addressable capabilities**: 68 agents × N skills each, plus on-demand sub-agents

---

## Budget Authority

| Tier | Monthly Budget | Approval Authority |
|------|---------------|-------------------|
| Tier 0 (Mike) | Unlimited | — |
| Tier 1 (Meta) | $50/mo each ($150 total) | Can approve any Tier 2 spend |
| Tier 2 (Super) | $10-15/mo each (~$100 total) | Can approve Tier 3 agent tasks |
| Tier 3 (Agent) | $0-5/mo each | Must request from super-agent |
| Tier 4 (Sub) | $0 (ephemeral, counted against parent) | Auto-approved if parent has budget |

**Total system budget**: ~$250/mo maximum (currently ~$150/mo actual)

---

## Implementation Plan

### Phase 7.2a: Hierarchy Registration (this session)
- Write hierarchy YAML to `.startup-os/agent-hierarchy.yaml`
- Update Paperclip agent records with `reportsTo` field
- No code changes needed — this is metadata

### Phase 7.2b: Skill Attachment (next session)
- VoltAgent catalog completed (agent running now)
- Import Tier 1 + Tier 2 skills as capability YAML per agent
- Store in `~/.openclaw/agents/<name>/agent/skills/`

### Phase 7.2c: KIRA Routing Update (future session)
- Update KIRA's routing rules to use hierarchy
- Add department-based routing alongside current intent classification
- Test with 20 representative queries

---

## What This Changes

| Before | After |
|--------|-------|
| Flat list of 68 agents | 4-tier hierarchy with clear authority |
| No delegation chain | Meta → Super → Agent → Sub-agent |
| VoltAgent skills = new agents? | VoltAgent skills = capabilities on existing agents |
| Claude Code plugins = separate system | Claude Code plugins = Tier 4 sub-agents |
| No budget tracking | Budget flows down the hierarchy |
| KIRA routes to any agent directly | KIRA routes to department leads, they delegate |

---

## Open Questions (for Mike)

1. **Growth department lead**: Currently no super-agent for Growth. Should Aria-Growth be promoted, or should growth report to Compass (product)?
2. **Science department**: Same question — no super-agent. Reports to Compass? Or create a "Science Lead" super-agent?
3. **Oracle Health**: Is Oracle Brief the right super-agent, or should this be a sub-department under Research?
4. **Budget**: Is $250/mo the right ceiling? Current actual spend is ~$150/mo.
5. **Paperclip vs OpenClaw**: Should hierarchy live in Paperclip (has `reportsTo` field) or in OpenClaw SYSTEM.md files? Or both?
