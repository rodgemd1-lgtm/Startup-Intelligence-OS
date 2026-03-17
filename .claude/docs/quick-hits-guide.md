# Quick Hits Guide — Slash Commands & Plugins

## Daily Drivers (use these most)

| Command | What It Does | When to Use |
|---------|-------------|-------------|
| `/commit` | Auto-detects type/scope, conventional commit | After any code change |
| `/handoff` | Writes HANDOFF.md for session continuity | End of every session |
| `/plan-feature` | Research + plan in .claude/plans/ | Before building anything non-trivial |
| `/execute` | Step-by-step plan execution | After plan is approved |
| `/scrape` | Multi-engine web scraping | Need data from any URL |

## V10 Intelligence Commands

| Command | What It Does | When to Use |
|---------|-------------|-------------|
| `/v10-status` | Dashboard of all 7 layers | "What's the system state?" |
| `/learn` | TIMG extract + consolidate + routing | Weekly — makes the system smarter |
| `/research-daemon` | Detect gaps + harvest knowledge | Weekly — fills knowledge gaps |
| `/predict` | Forecast capability maturity timelines | Planning sprints or priorities |
| `/evolve` | Propose system evolution changes | Monthly — structural improvements |

## Susan Commands (the capability foundry)

| Command | What It Does | When to Use |
|---------|-------------|-------------|
| `/susan-status` | Company status in Susan | "What does Susan know about X?" |
| `/susan-team` | View current agent team | "Who's available?" |
| `/susan-route` | Route a question to best agent | "Who should handle this?" |
| `/susan-query` | Pull research/examples from RAG | "What do we know about X?" |
| `/susan-plan` | Planning workflow for a company | Strategic planning sessions |
| `/susan-think` | Deep research mode | Complex analysis needed |
| `/susan-design` | Design session mode | UX/product design work |
| `/susan-fast` | Quick routed answer | Simple questions |
| `/susan-foundry` | Show execution blueprint | "What's the build plan?" |
| `/susan-refresh` | Refresh data for a company | Data seems stale |
| `/susan-bootstrap` | Install Susan in a new project | Setting up a new repo |
| `/susan-assets` | Pull visual assets | Need images/diagrams |
| `/susan-ingest` | Ingest data into RAG | New data to add |

## Specialty Commands

| Command | What It Does | When to Use |
|---------|-------------|-------------|
| `/produce` | Film/image production pipeline | Creating visual content |
| `/optimize-startup` | Bootstrap WISC + agents in any repo | Opening a new/unoptimized project |

## Plugin Cheat Sheet (wshobson-agents)

### Always Active (every project)
- **comprehensive-review** — architecture + security + code quality reviews
- **tdd-workflows** — test-driven development enforcement
- **context-management** — context persistence across agents
- **agent-orchestration** — multi-agent cost optimization

### For This Repo (Startup Intelligence OS)
- **python-development** — Python 3.12+, async, pydantic
- **backend-development** — FastAPI, API design, microservices
- **startup-business-analyst** — market sizing, financial modeling
- **llm-application-dev** — RAG, embeddings, agent systems
- **full-stack-orchestration** — end-to-end feature delivery
- **security-scanning** — threat modeling, SAST

### For Frontend Projects (AEP, etc.)
- **frontend-mobile-development** — React, Next.js, mobile
- **ui-design** — accessibility, design systems, components
- **javascript-typescript** — JS/TS optimization

### For Research-Heavy Projects
- **data-engineering** — pipelines, data quality
- **machine-learning-ops** — ML pipelines, model serving

## Mental Model

```
Opening a session?     → HANDOFF.md is auto-read by hooks
Need to build?         → /plan-feature → /execute → /commit → /handoff
Need intelligence?     → /susan-query or /susan-think
Need system health?    → /v10-status
End of week?           → /learn + /research-daemon
End of month?          → /evolve + /predict
New project?           → /optimize-startup (auto-suggested if missing)
```
