# Session Handoff

**Date**: 2026-03-24 (session 7 — V2 complete, V3 in progress)
**Project**: Startup Intelligence OS — PAI V3 Autonomous Execution
**Branch**: `claude/nice-shockley`
**Status**: V3 pipelines built and tested. Resume with runner + scheduling.

## What's Done

### V2 Complete (previous session)
- 81-agent registry (`pai/agents/registry.json`) — 12 groups, 16 routes
- Algorithm v1 execution loop (`pai/algorithm/v1.json`)
- Model router (Haiku/Sonnet/Opus)
- Apple ecosystem integration map
- 17/17 exit criteria PASS

### V3 In Progress (this session)

#### Pipelines Built & Tested (3/3)
1. **Morning Briefing** (`pai/pipelines/morning_briefing.py`)
   - Email: iCloud + Exchange via `mail-app-cli` (Go CLI, JSON output)
   - VIP detection + urgency scoring (1-5 scale)
   - Calendar: osascript fallback (slow), Orchard MCP preferred
   - Tested: 25 unread emails classified correctly

2. **Email Triage** (`pai/pipelines/email_triage.py`)
   - 5-level urgency: U5 critical → U1 noise
   - VIP domains (oracle.com) + named contacts
   - Actions: Reply needed, Review, Archive, Flag, FYI-only (CC detection)
   - Tested: 10 noise, 14 low, 1 medium — all correct

3. **Meeting Prep** (`pai/pipelines/meeting_prep.py`)
   - Attendee extraction from titles ("1:1 with Jordan Voss")
   - Email thread search for related context
   - Susan RAG context lookup
   - Format-aware prep notes (1:1, standup, review, demo)

#### Infrastructure
- **Orchard MCP wired** into `.claude/settings.json`
  - 48 Apple tools: Calendar, Mail, Notes, Reminders, Messages, Contacts, Music, Maps, Weather, Clock
  - Endpoint: `http://localhost:8086/mcp` (Streamable HTTP)
  - Next session has all 48 tools natively
- **mail-app-cli** working — both iCloud and Exchange
- **GCP credentials** in `pai/pipelines/.env` (gitignored)
  - Hermes OAuth (Calendar), Jake Gmail OAuth, Gemini API, YouTube API

## What's Left for V3

### Immediate (pick up here)
1. **Pipeline runner** — `pai/pipelines/run.py`
   - `python run.py briefing` / `triage` / `prep "Meeting Title"`
2. **OpenClaw skill** — `/briefing`, `/triage`, `/prep` commands
3. **Scheduled execution** — LaunchAgent for 7:00 AM morning briefing
4. **Orchard Calendar** — replace osascript with `calendar_info` MCP tool
5. **VIP contacts** — expand sender list with Mike's actual VIPs

### V3.1
- Google Calendar via Hermes OAuth
- Gmail VIP alerts via Jake Gmail OAuth
- Telegram notification output
- Auto-archive noise emails (with confirmation gate)

## Available Tools

| Tool | Transport | Scope |
|------|-----------|-------|
| mail-app-cli | CLI (JSON) | iCloud + Exchange email |
| Orchard MCP | HTTP localhost:8086 | 48 Apple app tools |
| iMessages MCP | In-session | Read/send iMessages |
| Apple Notes MCP | In-session | Read/write Apple Notes |
| osascript | CLI | Calendar (slow fallback) |

## GCP Credentials (Clawdbot Project)
- Project: `gen-lang-client-0499297227`
- Hermes OAuth: Calendar + general Google
- Jake Gmail OAuth: Email triage alerts
- Gemini API: CrewAI integration
- YouTube API: Content pipeline
- All stored in `pai/pipelines/.env` (gitignored)

## Key Files
```
pai/
├── agents/registry.json           # 81 agents, 12 groups, 16 routes
├── algorithm/v1.json              # TheAlgorithm execution loop
├── model_router.json              # Haiku/Sonnet/Opus routing
├── apple-integrations.json        # Apple ecosystem map
├── pipelines/
│   ├── .env                       # GCP creds (gitignored)
│   ├── morning_briefing.py        # Morning briefing
│   ├── email_triage.py            # Email triage + scoring
│   └── meeting_prep.py            # Meeting prep context
├── retrieval/
│   ├── retriever.py               # PAIRetriever (Supabase)
│   └── consolidator.py            # Session lifecycle
└── MEMORY/, TELOS/                # 3-tier memory architecture
```

## Context Health Protocol
Before ending any session:
1. Check context usage (< 60% hard limit)
2. Commit all working code
3. Update HANDOFF.md
4. Push to GitHub
5. Start new session: "Read HANDOFF.md. Continue V3."

## How to Resume
```
Read HANDOFF.md. Continue V3 — build pipeline runner, wire OpenClaw skills, set up scheduled execution.
Orchard MCP is now available (48 Apple tools). Use calendar_info for calendar instead of osascript.
```
