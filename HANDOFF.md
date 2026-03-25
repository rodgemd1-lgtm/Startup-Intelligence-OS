# Session Handoff — Susan Department Redesign + Jake v5

**Date**: 2026-03-25 (session 9 — full ecosystem research complete)
**Branch**: `claude/nice-shockley`
**Status**: All research done. Ready for overlap analysis + two parallel execution sessions.

---

## The Vision

Adopt **VoltAgent as the AI Agent Engineering Platform**. Merge all VoltAgent ecosystem assets (agents, skills, papers, presets) with Susan's existing 83 agents. Reorganize into **departments** that Jake routes to as root supervisor.

Two parallel workstreams:
- **Workstream A:** Jake v5 + OpenClaw runtime (deploy and connect)
- **Workstream B:** Susan department redesign (upgrade and reorganize)

---

## VoltAgent Ecosystem — COMPLETE Inventory

Clone ALL of these before starting:

```bash
cd /tmp
git clone https://github.com/VoltAgent/voltagent.git
git clone https://github.com/VoltAgent/awesome-claude-code-subagents.git
git clone https://github.com/VoltAgent/awesome-codex-subagents.git
git clone https://github.com/VoltAgent/awesome-agent-skills.git
git clone https://github.com/VoltAgent/awesome-openclaw-skills.git
git clone https://github.com/VoltAgent/awesome-ai-agent-papers.git
git clone https://github.com/VoltAgent/awesome-nemoclaw.git
git clone https://github.com/VoltAgent/ai-agent-platform.git
```

| Repo | What | Count |
|------|------|-------|
| **voltagent** | Core AI Agent Engineering Platform. 35 packages, 86 examples. TypeScript. | 35 packages |
| **awesome-claude-code-subagents** | Claude Code subagents (.md format, YAML frontmatter) | **134 agents** in 10 categories |
| **awesome-codex-subagents** | Codex subagents (.toml format) | **136 agents** in 10 categories |
| **awesome-agent-skills** | Official skills from Anthropic, Google, Vercel, Stripe, Cloudflare, etc. | **1,030+ skills** |
| **awesome-openclaw-skills** | Curated OpenClaw skills registry | **5,400+ skills** in 30 categories |
| **awesome-ai-agent-papers** | 2026 AI agent research papers from arXiv | **363 papers** in 5 topics |
| **awesome-nemoclaw** | Nvidia NemoClaw presets for sandboxed operations | **18 presets** (Stripe, AWS, GCP, etc.) |
| **ai-agent-platform** | Reference multi-agent platform (orchestration, memory, RAG) | 1 reference impl |

### Agent Format Details

**Claude Code subagents** (awesome-claude-code-subagents): Each is a `.md` file with YAML frontmatter (name, description, tools, model) + deep domain instructions. Categories: 01-core-development(10), 02-language-specialists(28), 03-infrastructure(16), 04-quality-security(14), 05-data-ai(13), 06-developer-experience(13), 07-specialized-domains(12), 08-business-product(11), 09-meta-orchestration(10), 10-research-analysis(7).

**Codex subagents** (awesome-codex-subagents): Same 10 categories but `.toml` format. 136 agents — mostly the same roles with Codex-specific adaptations plus a few unique ones (browser-debugger, reviewer).

**Agent Skills** (awesome-agent-skills): Official skills from 35+ dev teams (Anthropic, Google, Vercel, Stripe, Cloudflare, Netlify, Trail of Bits, Sentry, Expo, Hugging Face, Figma, etc.). These are production-tested, not mass-generated.

---

## Susan's Current State (from audit)

- **96 total agents** (81 Susan + 15 Claude Code operational)
- **Zero** tool definitions, supervisors, typed I/O, durable memory
- **77/81** agents are simple prompt-only (automatable migration)
- **10,409 lines** of domain knowledge prompts (the asset to preserve)
- **10,788+ RAG chunks** with Voyage AI embeddings
- Full audit: `.claude/docs/research-packet--susan-architecture-audit.md`

---

## Research Completed (all saved)

| Research | Location |
|----------|----------|
| VoltAgent deep research (1,150+ lines) | `docs/plans/2026-03-25-voltagent-deep-research.md` |
| Susan architecture audit | `.claude/docs/research-packet--susan-architecture-audit.md` |
| OpenClaw skills ecosystem | `.claude/docs/research-packet--openclaw-skills-ecosystem.md` |
| V3X plan (partially updated) | `docs/plans/2026-03-24-pai-v3x-ecosystem-supercharge-plan.md` |
| CF Workers research | In session memory (Hono router, deployment-ready code) |
| OpenClaw deployment research | In session memory (hybrid skill + group agents) |

---

## Decisions Made by Mike

1. **All-in on VoltAgent** — adopt as engineering platform, not just observability
2. **All-in on subagents** — all 134 Claude Code + 136 Codex agents into Susan's roster
3. **All-in on skills** — 1,030+ official skills + 5,400+ OpenClaw skills available
4. **Department-based organization** — not 12 ad-hoc groups, structured departments
5. **Jake v5** — rebuilt as root supervisor on VoltAgent gold standard
6. **Two parallel workstreams** — don't block each other
7. **Claude Code + Codex** as execution environments
8. **Supabase for observability** — hooks → Supabase (not VoltAgent Cloud)
9. **Cloudflare Workers** for multi-channel webhook routing

---

## FIRST THING TO DO: Overlap Analysis

Before writing execution plans, map VoltAgent's 134+136 agents against Susan's 83:
1. Read `pai/agents/registry.json` for Susan's roster
2. Read `/tmp/awesome-claude-code-subagents/categories/` for VoltAgent Claude agents
3. Read `/tmp/awesome-codex-subagents/categories/` for VoltAgent Codex agents
4. Produce: overlap mapping, gap analysis, merged department structure, total count

---

## Workstream A: Jake v5 + OpenClaw Runtime

| Task | Status |
|------|--------|
| Jake v5 agent definition (VoltAgent gold standard) | NOT STARTED |
| OpenClaw enhanced susan-bridge skill | NOT STARTED |
| CF Workers webhook router deployment | NOT STARTED |
| Morning briefing pipeline | EXISTS, needs testing |
| Email triage pipeline | EXISTS, needs testing |
| Meeting prep pipeline | EXISTS, needs testing |
| LaunchAgent for 7 AM briefing | NOT STARTED |

## Workstream B: Susan Department Redesign

| Phase | What | Status |
|-------|------|--------|
| Overlap analysis | Map VoltAgent vs Susan | NOT STARTED |
| Department design | ~15 departments with supervisors | NOT STARTED |
| Converter script | Parse .md/.toml → unified format | NOT STARTED |
| Batch import VoltAgent agents | Copy 134+136 agents | NOT STARTED |
| Build supervisor agents | ~15 department heads | NOT STARTED |
| VoltAgent runtime | Replace base_agent.py with TS runtime | NOT STARTED |
| Durable memory | Supabase adapter | NOT STARTED |
| Workflow engine | Port orchestrator to VoltAgent workflows | NOT STARTED |

---

## Proposed Department Structure

```
Jake v5 (Root Supervisor / CEO)
├── Engineering (core-dev + language specialists + Susan engineering)
├── Infrastructure (infra + devops + platform)
├── Quality & Security (QA + security + compliance)
├── Data & AI (data science + ML + AI)
├── Product (Susan product + UX + design)
├── Strategy (Susan strategy + business analysis)
├── Growth & Marketing (Susan growth + content + SEO)
├── Research (Susan research + VoltAgent research + 363 papers)
├── Creative Studio (Susan studio + film + slideworks)
├── Developer Experience (DX + tooling + documentation + MCP)
├── Operations (meta-orchestration + workflows)
├── Psychology & Behavioral Science (Susan unique)
├── Health & Fitness Science (Susan unique)
├── Oracle Health Division (company-specific)
└── Specialized Domains (fintech, blockchain, IoT, gaming)
```

---

## GCP Credentials (Clawdbot Project)

- Hermes Desktop Client: `28378277140-n3oroqgmedcuvt213ub0ltu9lucjrcur`
- Jake Gmail VIP: `28378277140-17cpsbejc7ud52vuhnr74m35nvi6jbcn`
- Gemini API: `AIzaSyDEfW7jXwnkGKMxesUE4zjD_C-_5lVshWM`
- YouTube Data: `AIzaSyDsCi8JTUn0zqXBYnUC6glYuI4J2KlfbXY`
- GCP Project: `gen-lang-client-0499297227`

## Tools Available

- `mail-app-cli` at `~/go/bin/mail-app-cli` (iCloud + Exchange)
- `icalBuddy` via Homebrew
- Orchard MCP (48 Apple tools)
- OpenClaw gateway on `ws://127.0.0.1:18789`

---

## Resume Prompts

### For Workstream A (Jake v5 + OpenClaw):
```
Read HANDOFF.md. Start Workstream A — Jake v5 + OpenClaw Runtime.
Clone the VoltAgent repos listed in the handoff.
Build Jake v5 as a VoltAgent gold-standard root supervisor agent.
Then wire the OpenClaw enhanced susan-bridge skill and deploy CF Workers.
```

### For Workstream B (Susan Department Redesign):
```
Read HANDOFF.md. Start Workstream B — Susan Department Redesign.
Clone the VoltAgent repos listed in the handoff.
First: run the overlap analysis (VoltAgent 134+136 agents vs Susan 83).
Then: design the department structure and build the converter script.
Research docs are at docs/plans/2026-03-25-voltagent-deep-research.md
and .claude/docs/research-packet--susan-architecture-audit.md
```
