# Parking Lot — Ideas & Projects to Revisit

## Active Parking (2026-03-18)

### Alex Recruiting
- **What**: Building out Alex Recruiting project today
- **Context**: Mike mentioned this as a priority for today alongside V1/V2 work
- **Status**: Parked — separate session recommended
- **Next step**: Open Alex Recruiting repo, check HANDOFF.md, resume Phase 5 polish

### James OS — Fleet Management Dashboard
- **What**: Fleet management operating system with dashboard, built for James
- **Context**: Mike is building this out as a separate project
- **Status**: Parked — separate session recommended
- **Next step**: Scope requirements, tech stack, data sources. Likely needs own repo + WISC setup.

### Oracle Health Website
- **What**: Mike wants to build out a website for Oracle Health AI Enablement
- **Context**: Currently SharePoint-based strategy hub (353 KB records, 57 prompts, 7 pillars)
- **Status**: Parked — separate session recommended
- **Next step**: Define website scope, tech stack, and how it relates to existing SharePoint content

### Telegram → Claude Mobile Interface (V3 Feature)
- **What**: Use Telegram bot (@mikerodgers_claw_bot via Genspark OpenClaw) as mobile interface to Jake/Susan
- **Use case**: Mike needs answers while on the go, talking to boss, in meetings — query Oracle Health, Alex Recruiting, etc. from phone
- **Context**: Genspark bot is in pairing mode, needs /start sent to complete setup
- **Recommended approach**: Option B (custom Telegram Bot → Claude API with Jake context) or Option D (n8n bridge)
- **Status**: Parked as V3 scope — needs proper engineering project
- **Next step**: Complete Telegram pairing, then build bridge in V3
- **Reference**: See `~/.claude/projects/.../memory/reference_openclaw_telegram.md`

### CLI Tools Setup (2026-03-27)
- **OpenCut** (`opencut-app/opencut`): Open-source video editor — potential content production tool for Film Studio agents
- **Alexa ASK CLI** (`alexa/ask-cli`): Alexa Skills Kit CLI — voice interface for Jake (future multi-channel Phase 6)
- **Go Spotify CLI** (`Envoy49/go-spotify-cli`): Spotify control from terminal — integrate with Mike's music preferences, auto-DJ during work sessions
- **Status**: Parked — complete V15 Phase 4 first
- **Next step**: Research each, assess fit, install after Phase 4 is 100%

### Birch — Real-Time Signal Scoring & Autonomous Execution Engine (V4 Feature)
- **What**: Scoring + routing layer that ingests real-time web signals, scores them (Relevance/Actionability/Urgency 0-100), and auto-routes to existing agents
- **Data source**: Firehose.com — SSE streaming API for real-time web monitoring (free beta, no credit card). Delivers ML-classified content with article metadata, Lucene query syntax filtering.
- **Architecture**: NOT a monolithic agent. Birch is the scoring brain that orchestrates existing agents:
  - Firehose SSE stream → Birch scoring (0-100)
  - Tier 1 (80+): Route to HERALD for drafting → SENTINEL-HEALTH gate → staging queue
  - Tier 2 (50-79): Append to daily digest
  - Tier 3 (<50): Log discard count (anti-fragility compliant), discard content
- **Why V4**: Requires autonomous chain execution (SCOUT → scoring → HERALD → gate → publish). That's V4a territory.
- **Integration**: Firehose SSE → could wrap as MCP tool or Python consumer feeding into Susan RAG pipeline
- **Status**: Parked — V4a prerequisite. Park until autonomous research chains are proven.
- **Next step**: Sign up for Firehose beta, test SSE stream, define scoring rubric against real signals
- **Reference**: https://firehose.com/ — Mike found this, Jake validated the architecture

### OpenClaw API List — Unified API Registry for Agent Ecosystem (V7/V8 Feature)
- **What**: Kevjade's openclaw-api-list — a curated registry of APIs organized for AI agent consumption. Could serve as the universal API connector layer for Jake/Susan agents.
- **Source**: https://github.com/Kevjade/openclaw-api-list/
- **Potential use**: Give agents a catalog of available APIs they can self-select from based on task needs. Instead of hardcoding MCP integrations, agents discover and connect to APIs dynamically.
- **Why V7/V8**: Requires autonomous agent capability selection (V4), proven trust/governance (V5-V6), and dynamic tool discovery. This is late-stage autonomous cognition territory.
- **Status**: Parked — Mike's idea, noted for future roadmap review.
- **Next step**: Review the repo structure, assess API coverage, evaluate if it complements or replaces MCP-based tool discovery.

---

*Reviewed during planning sessions (Strategist Mind). Ideas that survive 2+ reviews get promoted to plans.*
