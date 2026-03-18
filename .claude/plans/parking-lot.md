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

---

*Reviewed during planning sessions (Strategist Mind). Ideas that survive 2+ reviews get promoted to plans.*
