# V4 — Semi-Autonomous: Design Document

**Author:** Jake + Mike
**Date:** 2026-03-18
**Status:** APPROVED — Ready for implementation planning
**Parent:** V1-V5 Roadmap (`~/.claude/plans/2026-03-18-v1-v5-roadmap.md`)

---

## Goal

Multi-agent chains execute end-to-end. Human review only for external-facing / high-blast-radius outputs. Mike spends <30 min/day on routine operations.

## Design Decisions

| Decision | Choice | Rationale | Reversible? |
|----------|--------|-----------|-------------|
| Chain orchestration location | New `chains/` module (Option B) | Clean separation from existing orchestrator; chains are a new abstraction | Yes |
| Birch integration model | Standalone scorer, chains consume output (Option 2) | Loose coupling via signal files; Birch and chains evolve independently | Yes |
| Birch timing | Build in parallel with chains (not deferred) | Mike already has Firehose access; deferring means throwaway trigger code | Yes |
| Autonomy aggressiveness | Moderate — blast radius determines autonomy | AUTO for internal, HUMAN REVIEW for external-facing; protects stakeholder trust | Yes |
| Trust dashboard surface | CLI + daily markdown report (A+B) | Terminal-first; markdown feeds into ARIA brief; skip frontend until V5 | Yes |

## Architecture Overview

### New Modules

Three new Python modules inside `susan-team-architect/backend/`:

```
susan-team-architect/backend/
├── chains/          # NEW — Sequential multi-agent workflow engine
├── birch/           # NEW — Real-time signal scoring & routing
├── trust/           # NEW — Autonomy graduation + trust dashboard
├── susan_core/      # EXISTING — untouched
├── control_plane/   # EXISTING — untouched
├── research_daemon/ # EXISTING — untouched
├── self_improvement/ # EXISTING — untouched
└── collective/      # EXISTING — untouched
```

### Data Flow

```
Signal Sources (Firehose SSE, TrendRadar, morning intel, manual)
    ↓
Birch (score 0-100, classify tier)
    ↓
.startup-os/signals/scored-{date}.jsonl    ← interface file
    ↓
Chains Engine (reads scored signals, executes appropriate chain)
    ↓
Agent chain runs (SCOUT → HERALD → SENTINEL-HEALTH → output)
    ↓
Trust layer checks autonomy level:
    → AUTO: publish to .startup-os/briefs/
    → HUMAN REVIEW: stage to .startup-os/staging/ + notify in brief
    ↓
Trust Dashboard (CLI + daily markdown report)
```

Birch and chains communicate through files (`.startup-os/signals/`), not function calls. Birch can run as a background process, scheduled task, or SSE listener independently of when chains execute.

---

## Module 1: Chains Engine (`chains/`)

### Structure

```
chains/
├── __init__.py
├── __main__.py          # CLI: python -m chains run <chain-name>
├── engine.py            # Core chain executor — reads chain defs, runs steps
├── registry.py          # Chain definitions registry (which agents, what order)
├── schemas.py           # Pydantic models: ChainDef, ChainStep, ChainRun, ChainResult
├── triggers.py          # Trigger types: manual, scheduled, signal-scored, file-watch
├── context.py           # Shared context passed between chain steps (data bus)
└── chains/              # Individual chain definitions
    ├── competitive_response.py   # SCOUT → HERALD → SENTINEL-HEALTH → stage/publish
    ├── executive_brief.py        # SCOUT → ORACLE-BRIEF → SENTINEL-HEALTH → stage
    ├── research_refresh.py       # Gap Detector → Research Agents → Knowledge Engineer → ingest
    └── daily_cycle.py            # Morning: SCOUT → ARIA → digest assembly
```

### Chain Definition Model

```python
chain = ChainDef(
    name="competitive-response",
    trigger=SignalTrigger(min_score=80, signal_types=["competitor_move"]),
    autonomy="HUMAN_REVIEW",  # blast radius: external-facing
    steps=[
        ChainStep(agent="scout", output_key="signals"),
        ChainStep(agent="herald", input_key="signals", output_key="drafts"),
        ChainStep(agent="sentinel-health", input_key="drafts", output_key="cleared",
                  gate=True),  # gate=True means chain stops if this step fails
    ]
)
```

### Context Bus

Each step writes its output to a shared `ChainContext` dict. Next step reads the previous step's output by key. No file I/O between steps — only at chain start (read trigger) and chain end (write output).

### Gates

Any step marked `gate=True` can halt the chain. SENTINEL-HEALTH returns CLEAR/REVIEW/BLOCK:
- BLOCK → chain stops, escalates, trust demotion
- REVIEW → output staged for human approval
- CLEAR → chain continues

### CLI

```bash
python -m chains run competitive-response          # manual trigger
python -m chains run daily-cycle                   # run morning cycle
python -m chains list                              # show all registered chains
python -m chains status                            # show recent chain runs + outcomes
python -m chains history competitive-response      # audit trail for specific chain
python -m chains halt <chain-name>                 # emergency kill switch
```

### Audit

Every chain run logs to `.startup-os/runs/chains/` as JSONL with timestamps, step outcomes, gate results, and final disposition.

### Chain Definitions

| Chain | Steps | Trigger | Autonomy |
|-------|-------|---------|----------|
| `competitive-response` | SCOUT → HERALD → SENTINEL-HEALTH | Tier 1 signal (score 80+) | SUPERVISED (blast radius cap) |
| `executive-brief` | SCOUT → ORACLE-BRIEF → SENTINEL-HEALTH | Tier 1 signal + oracle-health domain | SUPERVISED (blast radius cap) |
| `research-refresh` | Gap Detector → Research Agents → Knowledge Engineer | Stale record threshold | AUTONOMOUS eligible |
| `daily-cycle` | SCOUT → ARIA → digest assembly | Scheduled (6:00 AM) | AUTONOMOUS eligible |

---

## Module 2: Birch Signal Scorer (`birch/`)

### Structure

```
birch/
├── __init__.py
├── __main__.py          # CLI: python -m birch listen / python -m birch score
├── scorer.py            # Core scoring engine — 3-axis rubric
├── sources/
│   ├── firehose.py      # SSE consumer for Firehose.com real-time stream
│   ├── trendradar.py    # Pull from TrendRadar MCP / local data
│   ├── morning_intel.py # Parse morning brief artifacts
│   └── manual.py        # Manual signal injection (CLI or file drop)
├── rubric.py            # Scoring rubric definitions per company/domain
├── schemas.py           # Pydantic: RawSignal, ScoredSignal, SignalTier
└── writer.py            # Writes scored signals to .startup-os/signals/
```

### Scoring Rubric (3-axis, 0-100 composite)

| Axis | Weight | What It Measures |
|------|--------|-----------------|
| Relevance | 40% | Does this signal relate to our companies/domains? |
| Actionability | 35% | Can we do something about this? Clear response path? |
| Urgency | 25% | Time-sensitivity — will this matter less tomorrow? |

### Tier Classification

| Tier | Score | Action |
|------|-------|--------|
| Tier 1 | 80-100 | Route to chain immediately |
| Tier 2 | 50-79 | Append to daily digest |
| Tier 3 | 0-49 | Log discard count, drop content |

### Firehose SSE Consumer

```python
async def listen(config: FirehoseConfig):
    """Connect to Firehose SSE stream, score each event, write to signals dir."""
    async with aiohttp.ClientSession() as session:
        async with session.get(config.sse_url, headers=config.headers) as resp:
            async for event in resp.content:
                raw = RawSignal.from_sse(event)
                scored = scorer.score(raw, rubric=config.rubric)
                writer.append(scored)
```

### Rubric Configuration

Per-company rubrics so Oracle Health, TransformFit, and Alex Recruiting each score signals against their own relevance keywords and competitive landscape.

### CLI

```bash
python -m birch listen                    # start SSE listener (foreground)
python -m birch listen --daemon           # background mode
python -m birch score --file signals.json # score a batch of manual signals
python -m birch stats                     # show score distribution, tier counts
python -m birch stats --days 7            # weekly scoring summary
```

### Output Format

`.startup-os/signals/scored-{date}.jsonl`:
```json
{"timestamp": "2026-03-18T14:30:00Z", "source": "firehose", "title": "Epic launches...", "score": 87, "tier": 1, "relevance": 92, "actionability": 85, "urgency": 80, "company": "oracle-health", "routed_to": "competitive-response"}
```

### Design Notes

- Discard logging (Tier 3 count without content) satisfies antifragility monitor
- Birch never calls agents directly — writes scored signals, chains pick them up
- Scoring rubric is configurable per company/domain

---

## Module 3: Trust System (`trust/`)

### Structure

```
trust/
├── __init__.py
├── __main__.py          # CLI: python -m trust dashboard / python -m trust promote
├── tracker.py           # Track chain run outcomes, accuracy, escalation rates
├── graduation.py        # Autonomy promotion/demotion logic
├── enforcer.py          # Called by chains engine — checks autonomy level before publishing
├── schemas.py           # Pydantic: TrustProfile, RunOutcome, GraduationEvent
├── dashboard.py         # CLI table output + markdown report generator
└── config.py            # Blast radius classifications, graduation thresholds
```

### Autonomy Levels

| Level | What Happens | Graduation Criteria |
|-------|-------------|-------------------|
| MANUAL | Human triggers chain, human approves output | Default for new chains |
| SUPERVISED | Chain auto-triggers, output staged for human review (30-min veto window) | 20+ runs, 90%+ accuracy, 0 BLOCK events |
| AUTONOMOUS | Chain auto-triggers, output auto-publishes, post-hoc audit only | 50+ runs at SUPERVISED, 95%+ accuracy, <5% escalation rate |

### Blast Radius Caps

```python
# These CANNOT graduate past SUPERVISED regardless of track record
BLAST_RADIUS_CAPS = {
    "oracle-brief": "SUPERVISED",
    "herald-response": "SUPERVISED",
    "content-publish": "SUPERVISED",
}

# These CAN reach AUTONOMOUS
AUTONOMOUS_ELIGIBLE = [
    "scout-signals",
    "daily-digest",
    "freshness-audit",
    "research-refresh",
]
```

### Demotion Triggers

- SENTINEL-HEALTH returns BLOCK → immediate demotion
- Mike manually rejects a staged output 3+ times in 30 days
- Antifragility monitor flags chain as FRAGILE

### Enforcer Integration

```python
# Inside chains/engine.py, after chain completes:
disposition = enforcer.check(chain_name, chain_result)
if disposition == "PUBLISH":
    write_to_briefs(chain_result)
elif disposition == "STAGE":
    write_to_staging(chain_result)  # .startup-os/staging/
    notify_in_brief(chain_name, "awaiting review")
elif disposition == "BLOCK":
    log_block(chain_name, chain_result)
    demote(chain_name)
```

### Trust Dashboard (CLI)

```
$ python -m trust dashboard

┌─────────────────────┬────────────┬───────┬──────────┬───────────┐
│ Chain               │ Level      │ Runs  │ Accuracy │ Last Run  │
├─────────────────────┼────────────┼───────┼──────────┼───────────┤
│ daily-cycle         │ AUTONOMOUS │ 47/50 │ 96.2%    │ 6:30 AM   │
│ research-refresh    │ SUPERVISED │ 23/20 │ 91.3%    │ yesterday │
│ competitive-response│ SUPERVISED │ 12/∞  │ 88.0%    │ 2 days    │
│ executive-brief     │ SUPERVISED │  8/∞  │ 100%     │ today     │
└─────────────────────┴────────────┴───────┴──────────┴───────────┘
  ∞ = blast radius cap, cannot graduate past SUPERVISED
```

Daily markdown report saved to `.startup-os/briefs/trust-dashboard-{date}.md`.

---

## Phasing

### V4a — Foundation (1-2 sessions)

Build the three modules in parallel. No wiring yet.

| Deliverable | Module | What |
|-------------|--------|------|
| Chain engine | `chains/` | Engine, registry, schemas, context bus, CLI |
| 2 chain definitions | `chains/chains/` | `competitive_response.py`, `daily_cycle.py` |
| Birch scorer | `birch/` | Scorer, rubric, schemas, writer, CLI |
| Firehose consumer | `birch/sources/` | SSE listener with Firehose.com |
| Trust tracker | `trust/` | Tracker, schemas, config with blast radius caps |
| Audit logging | `.startup-os/runs/chains/` | JSONL chain run logs |

**Validation:** Each module runs standalone via CLI.

### V4b — Wiring (1 session)

Connect the pieces.

| Deliverable | What |
|-------------|------|
| Signal → Chain trigger | Chains engine reads `.startup-os/signals/`, auto-triggers on Tier 1 |
| Chain → Trust enforcer | Chain output routed through `trust/enforcer.py` |
| Staging directory | `.startup-os/staging/` for SUPERVISED outputs |
| ARIA integration | Daily brief includes trust one-liner + staged items count |
| 2 more chain defs | `executive_brief.py`, `research_refresh.py` |

**Validation:** End-to-end — inject Tier 1 signal, watch it flow through Birch → chain → trust → staging.

### V4c — Autonomy (1 session)

Turn it on.

| Deliverable | What |
|-------------|------|
| Graduation logic | `trust/graduation.py` — promotion/demotion |
| Scheduled Birch listener | Background process for Firehose SSE |
| Scheduled chain runner | Check signals dir every 15 min |
| Trust dashboard report | Daily markdown to briefs dir |
| Kill switch | `python -m chains halt <chain-name>` |

**Validation:** 48-hour autonomous run. Daily digest auto-publishes. Competitive response stages for review. Trust dashboard reflects accurate data.

---

## What V4 Does NOT Include (V5)

- Operator console visual dashboard
- Multi-user access
- Agent self-improvement loops
- Always-on persistent runtime
- Cross-company inference without prompting

---

## Success Criteria (Lily Tanaka Test)

- [ ] New user identifies highest-priority action within 90 seconds (trust dashboard + daily brief)
- [ ] Mike spends <30 min/day on routine operations (AUTO chains handle intel + digest)
- [ ] System handles 50+ autonomous actions per week with <5% escalation rate
- [ ] Full audit trail for every chain run (JSONL logs in `.startup-os/runs/chains/`)
- [ ] Kill switch works instantly (`python -m chains halt`)

---

## New Directory Structure

```
.startup-os/
├── briefs/           # EXISTING — final published outputs
├── signals/          # NEW — scored signals from Birch (JSONL)
├── staging/          # NEW — SUPERVISED outputs awaiting human review
└── runs/
    └── chains/       # NEW — chain execution audit logs (JSONL)
```

---

*Approved by Mike on 2026-03-18. Ready for implementation planning.*
