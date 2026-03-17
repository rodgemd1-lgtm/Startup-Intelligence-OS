# Command, Skill, Agent & Hook Reference

**Startup Intelligence OS — Complete Inventory**
Last updated: 2026-03-16

This document catalogs every slash command, skill, agent, and hook available across the Startup Intelligence OS ecosystem. Items marked **(global)** are available in all Claude Code projects. Items marked **(project)** are specific to this repo.

---

## Session Management

Commands for preserving context, tracking progress, and resuming work across sessions.

| Command | Scope | Description |
|---------|-------|-------------|
| `/save-session` | global | Save current session state to a dated file — captures what worked, what failed, what's next — so the next session picks up exactly where this one left off |
| `/resume-session` | global | Load the most recent session file and present a structured briefing before resuming work |
| `/aside` | global | Answer a quick side question mid-task without losing context — freezes current task, answers, then resumes automatically |
| `/checkpoint` | global | Create or verify a named git checkpoint — snapshot state, compare before/after, track progress through a build |
| `/handoff` | global | Write a `HANDOFF.md` at repo root for session continuity — lighter than save-session, lives in the repo |

---

## Planning & Execution (WISC Workflow)

The core build cycle: plan a feature, execute the plan, commit the result.

| Command | Scope | Description |
|---------|-------|-------------|
| `/plan-feature` | global | Research via sub-agent, then generate a structured plan in `.claude/plans/` with architecture, steps, and verification criteria |
| `/execute` | global | Execute an approved plan step by step with protection zone checks and verification at each stage |
| `/commit` | global | Create a conventional commit with auto-detected type (feat/fix/refactor/docs/test/chore) and scope |

---

## V10 Intelligence Stack

The Seven-Layer Intelligence Stack — autonomous learning, evolution, prediction, and research.

| Command | Scope | Description |
|---------|-------|-------------|
| `/v10-status` | project | Show V10.0 system status across all seven layers — agents, memory, learning, evolution, prediction, research, orchestration |
| `/research-daemon` | project | Run the V10 autonomous research daemon — detect capability gaps, harvest knowledge from scrape manifests, generate research digest |
| `/evolve` | project | Run V10 evolution engine — propose new agents, capabilities, departments, and routing changes based on accumulated intelligence |
| `/learn` | project | Run the V10 learning cycle — extract tips from runs, consolidate memory, update routing rules |
| `/predict` | project | Run V10 predictive capability modeling — forecast maturity timelines and optimal build sequence |

---

## Project Bootstrap & Optimization

Set up any new project with best-practice context engineering, agents, and research.

| Command / Skill | Scope | Description |
|----------------|-------|-------------|
| `/optimize-startup` | global | **Level 7 agentic bootstrap** — detects project type, installs WISC three-tier context engineering (.claude/rules, .claude/docs, .claude/plans), recommends plugins, runs Susan capability analysis, dispatches auto-research, installs session management and hooks |

This skill performs a 6-step flow:
1. **Detect project type** — scan for package.json, requirements.txt, Cargo.toml, go.mod, etc.
2. **Set up WISC framework** — create rules, docs, plans directories with project-appropriate content
3. **Install session management** — copy /aside, /checkpoint, /save-session, /resume-session + PreCompact hook + cost tracker
4. **Recommend plugins** — map detected stack to optimal plugin subset (foundation + stack-specific + infrastructure)
5. **Susan capability analysis** — run lightweight capability gap analysis if Susan is available
6. **Auto-research** — dispatch sub-agent to scan dependencies, fetch latest best practices, write findings to `.claude/docs/project-research.md`

---

## Susan Foundry Commands

Interface to Susan, the capability foundry and specialist system.

| Command | Scope | Description |
|---------|-------|-------------|
| `/susan-status` | global | Check Susan status for a company — chunks, visual assets, latest outputs |
| `/susan-team` | global | View the current Susan team manifest for a company |
| `/susan-plan` | global | Run Susan's planning workflow for a company and summarize the outputs |
| `/susan-query` | global | Pull Susan research, examples, and database-backed retrieval results |
| `/susan-ingest` | global | Ingest data into Susan's RAG knowledge base |
| `/susan-bootstrap` | project | Install Susan protocols, commands, MCP config, and agent packs into active project repos |
| `/susan-foundry` | project | Show Susan's execution blueprint and foundry plan for a company |
| `/susan-route` | project | Ask Susan which agents, data types, and workflows should be used for a specific task |
| `/susan-design` | project | Run Susan in design-session mode for a company |
| `/susan-think` | project | Run Susan in deep-research mode for a company |
| `/susan-fast` | project | Ask Susan for a fast routed answer or compact plan |
| `/susan-refresh` | project | Refresh Susan data for a company, including Oracle Health research and screenshots |
| `/susan-assets` | project | Pull Susan visual assets and example materials for a company |

---

## Content Production

Create visual content, films, reels, images, and slide decks.

| Command / Skill | Scope | Description |
|----------------|-------|-------------|
| `/produce` | project | Start and manage film/image productions — orchestrate 18 AI agents across 6 formats (film, reel, photo, carousel, image, documentary) with quality gates, tool routing, and legal clearance |
| `/scrape` | project | Intelligent multi-engine web scraping — discover, extract, and organize information from the web using Exa, Firecrawl, Brave, Jina, and Apify engines |

---

## Skills (Multi-Step Workflows)

Skills are multi-step workflows triggered automatically by context or invoked directly.

### Decision & Strategy Skills

| Skill | Scope | Description |
|-------|-------|-------------|
| `decision-room` | project | Frame business/product decisions, generate alternatives, compare options, produce recommendations with assumptions and reversal criteria |
| `company-builder` | project | Build a new company — define the wedge, core problem, first operating artifacts |
| `capability-gap-map` | project | Map current vs target capabilities, identify gaps, assign ownership, create capability roadmaps |
| `research-packet` | project | Deep research packets with definitions, methods, protocols, benchmarks, source categories, and synthesis |

### Susan Specialist Skills

| Skill | Scope | Description |
|-------|-------|-------------|
| `susan-protocols` | project | Use Susan's backend, routed agents, research corpus, and studio assets for strategy, research, product, and marketing tasks |
| `team-architect` | global | Susan's core team design methodology — 6-phase workflow, agent selection criteria, cross-portfolio synergy patterns |
| `company-analysis` | global | Gap analysis framework — complexity scoring, risk assessment, cross-portfolio synergy matching |
| `behavioral-economics` | global | Behavioral economics integration — 12 mechanisms, LAAL protocol, loss framing, copy templates, retention architecture |

### Design & UX Skills

| Skill | Scope | Description |
|-------|-------|-------------|
| `ux-design-process` | global | 6-phase evidence-backed workflow: research, behavioral science, journey mapping, design specification, and implementation planning |
| `film-production` | project | Full film and image production lifecycle — orchestrate 18 AI agents across 6 formats with quality gates |
| `scrape` | project | Multi-engine web scraping: Exa, Firecrawl, Brave, Jina, Apify — with optional RAG ingestion |

### Training & Learning Skills

| Skill | Scope | Description |
|-------|-------|-------------|
| `training-factory` | project | Build or improve training systems — curriculum, session arcs, facilitator packets, decks, handouts, activity systems |
| `training-evaluation-panel` | project | Transcript review, facilitator critique, rubric scoring, post-session quality evaluation |
| `behavioral-learning-design` | project | Behavioral science for learning — motivation, confidence, transfer design, learning friction, learner emotional state |
| `ellen-oracle-enablement` | project | Training and implementing Ellen, Oracle Gen Chat workflows, slash-command systems, strategist enablement |
| `corpus-harvester` | project | Build or expand large local corpora from binary documents, repos, crawls, locators, or generated extraction outputs |

### Utility Skills

| Skill | Scope | Description |
|-------|-------|-------------|
| `link-checker` | project | Validate all URLs across category READMEs and flag dead or broken links |
| `research-enrichment` | project | Run a live research enrichment sweep for one or more categories |

---

## Agents

Specialized sub-agents that run in parallel or handle delegated tasks.

| Agent | Model | Description |
|-------|-------|-------------|
| `jake` | opus | Front-door co-founder agent — company building, project building, decision framing, architecture, decomposition, and routing |
| `susan` | opus | Capability foundry agent — capability mapping, current-vs-target state analysis, team design, operating model design, maturity scoring |
| `orchestrator` | opus | V10.0 lead orchestrator — decomposes complex tasks into parallel subtasks, delegates to specialist workers, synthesizes results |
| `research` | sonnet | Deep-research specialist — definitions, methods, protocols, techniques, benchmarks, source mapping, synthesis |
| `link-validator` | haiku | Validates all URLs in a markdown file and reports dead or broken links |
| `slideworks-strategist` | opus | McKinsey Senior Partner narrative architect — Minto Pyramid, Zelazny charts, Duarte storytelling |
| `slideworks-builder` | opus | Production engineer for consulting-quality PPTX — python-pptx assembly, Think-Cell matplotlib charts, QA pipeline |
| `slideworks-creative-director` | opus | Design studio lead — Tufte data-ink, Think-Cell visual grammar, McKinsey Firm Graphics, creative preview loop |

---

## Hooks (Automatic Lifecycle Scripts)

Hooks fire automatically at specific lifecycle events. No slash command needed.

### Session Lifecycle

| Hook | Event | Description |
|------|-------|-------------|
| `session-start.sh` | SessionStart | Auto-configures project context at session start — reads workspace.yaml, sets environment |
| `stop-gate.sh` | Stop | Fires when Claude finishes responding — checks for common incompleteness patterns |
| `session-end.sh` | Stop | Writes a minimal HANDOFF.md if significant work was done during the session |

### Context & Cost Management

| Hook | Event | Description |
|------|-------|-------------|
| `pre-compact.sh` | PreCompact | Logs compaction events to `~/.claude/sessions/compaction-log.txt` and annotates active session files with compaction timestamps |
| `cost-tracker.sh` | Stop (async) | Appends per-session token usage and cost metrics to `~/.claude/metrics/costs.jsonl` — passive, append-only |
| `hook-profile.sh` | (wrapper) | Profile gate — set `INTELLIGENCE_HOOK_PROFILE=minimal\|standard\|strict` to toggle which hooks run. Also supports `INTELLIGENCE_DISABLED_HOOKS=name1,name2` |

### Code Quality & Routing

| Hook | Event | Description |
|------|-------|-------------|
| `quality-gate.sh` | PostToolUse (Write/Edit) | Runs after every file write or edit — provides feedback on code quality |
| `model-router.sh` | PreToolUse (Agent) | Suggests model routing for cost optimization when spawning sub-agents |

### Protection Zones

| Hook | Event | Description |
|------|-------|-------------|
| (inline) | PreToolUse (Edit/Write) | Blocks edits to `claude-plugins/` — vendored plugin files are read-only |
| (inline) | PreToolUse (Edit/Write) | Blocks edits to `susan-outputs/` — generated by Susan, use `/susan-plan` to regenerate |

---

## Cross-Repo Availability

These commands and hooks are installed across all 5 repos in the ecosystem:

| Repo | Session Commands | Hooks | Susan Commands |
|------|-----------------|-------|----------------|
| **Startup Intelligence OS** | all 5 | all 8 | all 13 |
| **James OS** | all 5 | all 8 (incl. PreCompact + cost-tracker) | V10 subset |
| **Alex Recruiting** | all 5 | all 8 (incl. PreCompact + cost-tracker) | all 13 |
| **Oracle Health AI** | all 5 | all 8 (incl. PreCompact + cost-tracker) | V10 subset |
| **AEP (Adapt Evolve Progress)** | all 5 | all 8 (incl. PreCompact + cost-tracker) | all 13 |

---

## Quick Reference Card

```
SESSION           /save-session  /resume-session  /aside  /checkpoint  /handoff
PLANNING          /plan-feature  /execute  /commit
V10 INTELLIGENCE  /v10-status  /research-daemon  /evolve  /learn  /predict
BOOTSTRAP         /optimize-startup
SUSAN             /susan-status  /susan-team  /susan-plan  /susan-query
                  /susan-ingest  /susan-bootstrap  /susan-foundry  /susan-route
                  /susan-design  /susan-think  /susan-fast  /susan-refresh
                  /susan-assets
PRODUCTION        /produce  /scrape
```
