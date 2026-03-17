# V10.0 Architecture — Startup Intelligence OS

## Seven-Layer Stack

```
┌─────────────────────────────────────────────────────────┐
│  L7: COLLECTIVE INTELLIGENCE                             │
│  research_planner, agent_factory, knowledge_transfer,    │
│  capability_predictor, evolution_engine                   │
├─────────────────────────────────────────────────────────┤
│  L6: SELF-IMPROVEMENT                                    │
│  timg_pipeline, routing_feedback, performance_telemetry, │
│  debate_upgrade                                          │
├─────────────────────────────────────────────────────────┤
│  L5: AUTONOMOUS RESEARCH                                 │
│  gap_detector, changelog_monitor, auto_harvester,        │
│  quality_scorer, research_daemon                         │
├─────────────────────────────────────────────────────────┤
│  L4: MULTI-AGENT ORCHESTRATION                           │
│  orchestrator agent, team templates, model routing,      │
│  budget-aware scheduling                                 │
├─────────────────────────────────────────────────────────┤
│  L3: GRAPH-NATIVE MEMORY                                 │
│  trajectory_extractor, tip_store, tip_retriever,         │
│  graph_builder, memory_consolidator                      │
├─────────────────────────────────────────────────────────┤
│  L2: FULL LIFECYCLE HOOKS                                │
│  SessionStart, PreToolUse, PostToolUse, Stop,            │
│  quality gates, model routing advisor                    │
├─────────────────────────────────────────────────────────┤
│  L1: ZERO-TOUCH SESSION SETUP                            │
│  auto-detect, auto-configure, HANDOFF persistence,       │
│  context injection via hooks                             │
├─────────────────────────────────────────────────────────┤
│  EXISTING FOUNDATION                                     │
│  WISC 3-tier context, Susan runtime (81 agents, 34 MCP  │
│  tools, RAG engine), Decision OS, workspace contracts    │
└─────────────────────────────────────────────────────────┘
```

## Data Flow

### Learning Cycle
```
Agent Run → RunTracer (telemetry) → TIMG Pipeline (extract tips)
    → Tip Store (persist) → Tip Retriever (inject into next run)
    → Routing Feedback (adjust weights) → Better routing
```

### Research Cycle
```
Gap Detector (scan capabilities) → Research Gaps
    → Auto Harvester (generate manifests) → Scrape Engine
    → Quality Scorer (evaluate) → RAG Ingestion
    → Knowledge Graph (update) → Better research
```

### Evolution Cycle
```
Performance Telemetry → Agent Ranking → Pattern Detection
    → Agent Factory (propose new agents)
    → Research Planner (fill knowledge gaps)
    → Capability Predictor (forecast timelines)
    → Evolution Engine (propose structural changes)
    → Human Approval → System Update
```

## Module Map

| Module | Path | Depends On |
|--------|------|------------|
| memory | backend/memory/ | decision_os.data (runs), .startup-os/ (contracts) |
| research_daemon | backend/research_daemon/ | memory (gap data), rag_engine (ingestion) |
| self_improvement | backend/self_improvement/ | memory (tips, trajectories), decision_os (runs) |
| collective | backend/collective/ | memory, self_improvement, research_daemon |

## Slash Command Map

| Command | Layer | What It Does |
|---------|-------|-------------|
| `/v10-status` | All | Dashboard of all 7 layers |
| `/learn` | L6 | Run full learning cycle (TIMG + consolidation + routing) |
| `/research-daemon` | L5 | Run autonomous research cycle |
| `/predict` | L7 | Forecast capability maturity timelines |
| `/evolve` | L7 | Propose system evolution changes |
| `/plan-feature` | WISC | Plan with sub-agent research |
| `/execute` | WISC | Step-by-step plan execution |
| `/handoff` | L1 | Session continuity (also auto via hook) |
| `/commit` | WISC | Conventional commits |

## Hook Map

| Hook | Script | Layer | Effect |
|------|--------|-------|--------|
| SessionStart | session-start.sh | L1 | Auto-detect, inject context |
| PreToolUse (Agent) | model-router.sh | L2 | Cost optimization advisory |
| PreToolUse (Edit/Write) | inline blocks | L2 | Protection zone enforcement |
| PostToolUse (Write/Edit) | quality-gate.sh | L2 | Syntax/quality validation |
| Stop | stop-gate.sh | L2 | Completeness reminders |

## Token Economics Target

| Operation | Model | Est. Tokens | Frequency |
|-----------|-------|-------------|-----------|
| Session start hook | N/A (bash) | 0 | Every session |
| Quality gate | N/A (bash) | 0 | Every write |
| Learning cycle | Sonnet | ~50K | Weekly |
| Research daemon | Sonnet | ~100K | Weekly |
| Predictions | Sonnet | ~30K | On demand |
| Evolution analysis | Opus | ~80K | Monthly |
| Multi-agent research | Sonnet×5 + Opus | ~150K | On demand |
| Multi-agent build | Sonnet×3 + Haiku | ~100K | On demand |
