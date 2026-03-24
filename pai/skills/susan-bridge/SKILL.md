---
name: susan-bridge
description: Bridge to Susan's 73-agent capability foundry. Route tasks, search knowledge (6,693+ RAG chunks), get team manifests, and execute agents via Susan's control plane API.
---

# Susan Bridge — 73-Agent Capability Foundry

Susan is the capability foundry behind the Startup Intelligence OS. She orchestrates 73 specialized agents across strategy, product, engineering, science, psychology, growth, research, and studio domains.

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
curl -s -X POST http://127.0.0.1:8042/api/susan/route \
  -H "Content-Type: application/json" \
  -d '{"company_id": "COMPANY", "task": "TASK_DESCRIPTION", "top_k": 6}' | python3 -m json.tool
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
curl -s http://127.0.0.1:8042/api/susan/status/COMPANY | python3 -m json.tool
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
curl -s -X POST http://127.0.0.1:8042/api/susan/run \
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

## Agent Groups (73 total)

| Group | Count | Key Agents |
|-------|-------|------------|
| Orchestration | 6 | Susan, Steve, Shield, Bridge, Ledger, Vault |
| Strategy | 6 | Recruiting Strategy, Compass, AI PM |
| Product | 13 | Marcus, Mira, Echo, Lens, Prism, Conversation Designer |
| Engineering | 8 | Atlas, Nova, Pulse, Sentinel, Forge, Knowledge Engineer |
| Science | 5 | Coach, Sage, Drift, Workout Program |
| Psychology | 3 | Freya, Flow, Quest |
| Growth | 7 | Aria, Haven, Guide, Herald, Beacon |
| Research | 3 | Research Director, Research Ops, Training Research |
| Studio | 12 | Deck, Design Director, Landing Page, Marketing |
| Film Studio | 14 | Film Director, Screenwriter, Cinematography |

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
