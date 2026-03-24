---
name: susan-bridge
description: Bridge to Susan's 83-agent capability foundry. Route tasks, search knowledge (6,693+ RAG chunks), get team manifests, execute agents, and dispatch research pipelines via Susan's control plane API.
---

# Susan Bridge — 83-Agent Capability Foundry (V2)

Susan is the capability foundry behind the Startup Intelligence OS. She orchestrates 83 specialized agents across 12 groups: orchestration, strategy, product, engineering, science, psychology, growth, research, studio, film studio, slideworks, and oracle health.

## Agent Registry

Full registry with intent routing: `pai/agents/registry.json`
Model routing: `pai/config/inference.json`
Algorithm spec: `pai/algorithm/v1.0.0.md`

## When to Use This Skill

- User wants to route a task to the right agents ("who should work on this?")
- User wants to search the knowledge base ("what do we know about retention?")
- User wants a team manifest or company status
- User wants to execute a specific agent
- User mentions Susan, agents, RAG, knowledge base, or capability mapping

## Prerequisites

Susan's control plane must be running on port 8042. To start it:
```bash
cd /Users/michaelrodgers/Desktop/Startup-Intelligence-OS/susan-team-architect/backend && source .venv/bin/activate && python3 -m control_plane.__main__
```

To check if it's running:
```bash
curl -s http://127.0.0.1:8042/api/health | python3 -m json.tool
```

If the control plane is not running, use the CLI fallback instead.

## Commands

### Route a Task
Find the best agents for a task. Returns ranked agents with confidence scores.

**API:**
```bash
curl -s "http://127.0.0.1:8042/api/routing/susan?company=COMPANY&task=TASK_DESCRIPTION&top_k=6" | python3 -m json.tool
```

**CLI fallback:**
```bash
cd /Users/michaelrodgers/Desktop/Startup-Intelligence-OS/susan-team-architect/backend && \
  .venv/bin/python scripts/susan_cli.py route COMPANY "TASK_DESCRIPTION"
```

### Search Knowledge
Search the RAG knowledge base (6,693+ chunks across 22 data types).

**API:**
```bash
curl -s "http://127.0.0.1:8042/api/knowledge/search?q=QUERY&tenant_id=COMPANY&top_k=8" | python3 -m json.tool
```

**CLI fallback:**
```bash
cd /Users/michaelrodgers/Desktop/Startup-Intelligence-OS/susan-team-architect/backend && \
  .venv/bin/python scripts/susan_cli.py query "QUERY" --company COMPANY --top-k 8
```

### Company Status
Get corpus stats, asset counts, and output status for a company.

**API:**
```bash
curl -s http://127.0.0.1:8042/api/companies/COMPANY/status | python3 -m json.tool
```

**CLI fallback:**
```bash
cd /Users/michaelrodgers/Desktop/Startup-Intelligence-OS/susan-team-architect/backend && \
  .venv/bin/python scripts/susan_cli.py status COMPANY
```

### Team Manifest
Get the current team design for a company.

**CLI:**
```bash
cd /Users/michaelrodgers/Desktop/Startup-Intelligence-OS/susan-team-architect/backend && \
  .venv/bin/python scripts/susan_cli.py team COMPANY
```

### Run Susan Plan
Execute a full Susan planning cycle for a company.

**API:**
```bash
curl -s -X POST http://127.0.0.1:8042/api/runs/susan \
  -H "Content-Type: application/json" \
  -d '{"company_id": "COMPANY", "mode": "MODE"}' | python3 -m json.tool
```

Modes: `quick` (fast), `deep` (thorough), `design` (operating model), `foundry` (full execution plan)

## Companies

| ID | Name | Agents |
|----|------|--------|
| transformfit | TransformFit | 13 agents (coaching, design, AI, algorithm) |
| alex-recruiting | Alex Recruiting | 6 agents (recruiting, film, outreach) |
| oracle-health-ai-enablement | Oracle Health | 12 agents (research, design, HIPAA) |
| founder-intelligence-os | Founder Intelligence OS | 10 agents (research, design, strategy) |
| mike-job-studio | Mike Job Studio | 10 agents (research, design, strategy) |

## Agent Groups (83 total across 12 groups)

| Group | Count | Key Agents |
|-------|-------|------------|
| Orchestration | 1 | Susan |
| Strategy | 6 | Steve, Shield, Bridge, Ledger, Vault, Recruiting Strategy |
| Product | 9 | Marcus, Mira, Compass, AI PM, Conversation Designer, Echo, Lens, Prism, UX Design |
| Engineering | 8 | Atlas, Nova, Pulse, Sentinel, Forge, Knowledge Engineer, AI Eval, Algorithm Lab |
| Science | 7 | Coach, Sage, Drift, Workout Program, Coaching Architecture, Workout Session, Training Research |
| Psychology | 3 | Freya, Flow, Quest |
| Growth | 7 | Aria, Haven, Guide, Herald, Beacon, Coach Outreach, X Growth |
| Research | 6 | Research Director, Research Ops, Web, arXiv, Reddit, App Store |
| Studio | 12 | Deck, Design Director, Landing Page, App Experience, Marketing, Article, Memo, Social Media, Whitepaper, Instagram, Recruiting Dashboard, Photography |
| Film Studio | 17 | Film Director, Screenwriter, Cinematography, Editing, Color Grade, VFX, Sound Design, Music Score, Production Designer, Production Manager, Talent Cast, Distribution, Legal Rights, Highlight Reel, Audio Gen, Film Gen, Image Gen |
| Slideworks | 3 | Strategist, Creative Director, Builder |
| Oracle Health | 2 | Marketing Lead, Product Marketing |

## Intent Routing (Quick Reference)

| User Intent | Route To |
|-------------|----------|
| Strategy / GTM / positioning | steve-strategy, susan |
| Legal / compliance | shield-legal-compliance |
| UX / design / experience | marcus-ux, mira-emotional-experience |
| Product roadmap / features | compass-product, ai-product-manager |
| Engineering / architecture | atlas-engineering, nova-ai |
| Research / evidence / papers | research-director, researcher-web, researcher-arxiv |
| Growth / marketing / content | aria-growth, marketing-studio-director |
| Film / video / reels | film-studio-director, editing-studio |
| Presentations / decks | deck-studio, slideworks-strategist |
| Recruiting / hiring | recruiting-strategy-studio, coach-outreach-studio |
| Healthcare / Oracle | oracle-health-marketing-lead |

Full routing map: `pai/agents/registry.json`

## Cost Awareness

Agent execution costs real money (Claude API). Before executing an agent:
1. Tell the user which agent and model will be used
2. Estimate cost (~$0.01-0.05 for Sonnet, ~$0.10-0.50 for Opus)
3. Get confirmation before running expensive operations

## Output Formatting

For Telegram responses:
1. Bold the agent names and roles
2. Show confidence scores as percentages
3. Include suggested next commands
4. Keep responses concise — Telegram messages should be scannable

### Dispatch Research Pipeline
Run Susan's research pipeline across multiple sources.

**CLI:**
```bash
cd /Users/michaelrodgers/Desktop/Startup-Intelligence-OS/susan-team-architect/backend && \
  .venv/bin/python -m research_daemon --command harvest --topic "TOPIC" --sources web,arxiv
```

Sources: `web`, `arxiv`, `reddit`, `appstore`

### Execute Specific Agent
Run a named agent on a task for a company.

**CLI:**
```bash
cd /Users/michaelrodgers/Desktop/Startup-Intelligence-OS/susan-team-architect/backend && \
  .venv/bin/python scripts/susan_cli.py route COMPANY "TASK" --agent AGENT_NAME
```

## Examples

User: "who should work on our retention problem?"
→ Route: `POST /api/susan/route` with company=transformfit, task="improve user retention"
→ Return: Top 3-5 agents with roles and reasoning

User: "what do we know about exercise science?"
→ Search: `GET /api/knowledge/search?q=exercise science&tenant_id=transformfit`
→ Return: Top results with sources

User: "status on oracle health"
→ Status: `GET /api/susan/status/oracle-health-ai-enablement`
→ Return: Chunk count, asset count, last refresh

User: "run a deep plan for alex recruiting"
→ Plan: `POST /api/susan/run` with company=alex-recruiting, mode=deep
→ Return: Planning output with phases and recommendations
