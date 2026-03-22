# Jake Intelligence Platform — Architecture & Integration Plan

**Date**: 2026-03-19
**Status**: Phase 1 Complete, Phase 2 In Progress
**Platform**: Hermes Agent v0.4.0 (migrated from OpenClaw)
**Model**: Claude Sonnet 4.6 via OpenRouter (300+ model access)

---

## What We Built Today

### Phase 1: Foundation (COMPLETE)

#### 1. OpenClaw Diagnosis & Fix
- **Root cause**: No API keys configured in any agent. Every request fell back to local 3B Llama model.
- **Fix**: Added Anthropic + Groq keys to all agent configs, fixed `api` type from `"anthropic"` to `"anthropic-messages"`, removed unsupported `fallbacks` keys.
- **Result**: OpenClaw working with Sonnet 4.6, 41 skills, 4 agents.

#### 2. Skill Expansion (41 skills installed on OpenClaw)
- 14 custom workspace skills (susan-rag-query, company-context, supabase-query, etc.)
- 17 ClawHub skills (browser-automation, google-calendar, gmail-secretary, linkedin-data-scraper, web scrapers, youtube-transcript, pdf, spreadsheet, etc.)
- 10 built-in skills (weather, github, imsg, apple-notes, etc.)

#### 3. OpenRouter Integration
- API key configured across all platforms
- Access to 300+ models (Claude, GPT, Gemini, Llama, Mistral, DeepSeek, etc.)
- One key, one invoice, auto-fallback between providers
- Credits loaded and working

#### 4. Migration to Hermes Agent
- **Decision**: Migrate from OpenClaw to Hermes Agent (Option A)
- **Why**: Self-improving skills, native OpenRouter, same platform support, better architecture
- **Result**: Hermes v0.4.0 running with 123 skills, 30 tools, Jake personality
- **Desktop app**: `/Applications/Jake.app` with Jacob's photo as icon
- **Gateway**: Running for Telegram (@BirchRodgersbot)

#### 5. Research Completed
- **697 API repo**: Full inventory of 22,000+ Apify APIs across 18 categories
- **OpenRouter**: 300+ models, 5.5% platform fee, auto-fallback, native OpenClaw/Hermes support
- **Firehose.com**: Real-time web monitoring by Ahrefs, free beta, 25 rules max, SSE streaming
- **Kilo Code**: VS Code extension, 500+ models, inline autocomplete, MIT open source — complement to Claude Code
- **Roo Code**: Same category as Kilo (fork chain: Cline → Roo → Kilo) — pick Kilo
- **Blackbox AI**: 300+ models, multi-agent, but proprietary and opaque — skip
- **Hermes Agent**: Self-improving agent by Nous Research, MIT, OpenRouter native — ADOPTED

---

## Current Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    MIKE'S INTERACTION LAYER                       │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│  Telegram    │  Desktop App │  CLI         │  Claude Code       │
│  @BirchBot   │  Jake.app    │  `hermes`    │  (development)     │
└──────┬───────┴──────┬───────┴──────┬───────┴────────┬───────────┘
       │              │              │                │
       ▼              ▼              ▼                ▼
┌──────────────────────────────────────┐  ┌────────────────────────┐
│         HERMES AGENT v0.4.0          │  │     CLAUDE CODE        │
│  ┌─────────────────────────────────┐ │  │  (Jake personality)    │
│  │  SOUL.md (Jake personality)     │ │  │  WISC context system   │
│  │  Smart Model Routing            │ │  │  Sub-agents + MCP      │
│  │  123 Skills / 30 Tools          │ │  │  Susan Integration     │
│  │  Self-improving learning loop   │ │  │  Hooks + Scheduled     │
│  └─────────────────────────────────┘ │  └────────────────────────┘
│                                      │
│  ┌─────────────┐ ┌────────────────┐  │
│  │ OpenRouter   │ │ Gemini Flash   │  │
│  │ (300+ models)│ │ (smart route)  │  │
│  │ Sonnet 4.6   │ │ (cheap queries)│  │
│  └──────┬──────┘ └───────┬────────┘  │
└─────────┼────────────────┼───────────┘
          │                │
          ▼                ▼
┌──────────────────────────────────────────────────────────────────┐
│                     DATA & KNOWLEDGE LAYER                       │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│  Susan RAG   │  Supabase    │  Firehose    │  FastAPI Bridge    │
│  94K chunks  │  4 databases │  (real-time) │  localhost:7842    │
│  73 agents   │  31+ tables  │  web monitor │  44 endpoints      │
└──────────────┴──────────────┴──────────────┴────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                     macOS SYSTEM LAYER                            │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│  Calendar    │  Apple Mail  │  Spotlight   │  Hammerspoon       │
│  (osascript) │  (osascript) │  (mdfind)    │  localhost:7843    │
│  Contacts    │  Reminders   │  Finder      │  Window mgmt       │
└──────────────┴──────────────┴──────────────┴────────────────────┘
```

---

## Phase 2: Full Integration (TODO)

### Priority 1: Verify Full Capabilities

| Capability | How to Test | Tool Used | Status |
|-----------|-------------|-----------|--------|
| **Calendar access** | `hermes "what's on my calendar today"` | macos-calendar skill + osascript | NEEDS TEST |
| **Apple Mail** | `hermes "check my recent emails"` | osascript + Mail.app | NEEDS TEST |
| **Outlook** | `hermes "check Outlook inbox"` | osascript + Outlook | NEEDS TEST |
| **File system** | `hermes "list files on my Desktop"` | file tool (built-in) | TESTED OK |
| **Browser control** | `hermes "open Safari and search for X"` | browser tool (built-in) | NEEDS TEST |
| **App launching** | `hermes "open Spotify"` | terminal tool + `open` | NEEDS TEST |
| **Screenshots** | `hermes "take a screenshot"` | terminal tool + screencapture | NEEDS TEST |
| **Git operations** | `hermes "git status in my project"` | terminal tool + git | NEEDS TEST |
| **Telegram (remote)** | Message @BirchRodgersbot | gateway mode | NEEDS TEST |
| **Cron/scheduling** | `hermes "remind me at 5pm to..."` | cronjob tool | NEEDS TEST |
| **Web search** | `hermes "search for Oracle Health news"` | web tool (built-in) | NEEDS TEST |
| **Sub-agent delegation** | `hermes "research X in parallel"` | delegation tool | NEEDS TEST |

### Priority 2: Firehose.com Integration

**Goal**: Real-time web monitoring feeding into Jake's knowledge.

**Implementation Plan**:
1. Create `~/.hermes/skills/firehose/` skill directory
2. Build Python skill with 4 functions:
   - `create_rule(query, name)` — Lucene syntax monitoring rule
   - `list_rules()` — show active rules
   - `stream_matches(rule_id, limit)` — pull recent matches
   - `delete_rule(rule_id)` — remove a rule
3. Create initial monitoring rules:
   - `"oracle health" OR "oracle cerner"` — Oracle Health mentions
   - `"healthcare AI" AND page_category:"/News"` — industry news
   - `domain:competitor1.com OR domain:competitor2.com` — competitor changes
   - `"athletic recruiting" OR "college football recruiting"` — Alex Recruiting intel
4. Connect to ARIA daily brief pipeline — Firehose matches become morning brief items
5. **API**: REST at `https://api.firehose.com`, SSE for streaming
6. **Key**: `fhm_dmJQS4Hufk9MzKENZ8QAeIfUh4j6GDq3nTC21NMz`
7. **Limits**: 25 rules max, 60 req/min for rules, 30 connections/min for streams

### Priority 3: Telegram Bot Testing

**Goal**: Verify Jake responds via Telegram from anywhere.

1. Start Hermes gateway: `hermes --gateway`
2. Open Telegram, message @BirchRodgersbot
3. Test commands: "what's on my calendar", "search Susan for X", "take a screenshot"
4. Verify remote access works (from phone away from computer)
5. Set up gateway as a persistent background service (launchd plist)

### Priority 4: Kilo Code Installation

**Goal**: VS Code companion with inline autocomplete and cheap model routing.

1. Install: VS Code Extensions → search "Kilo Code" → Install
2. Configure with OpenRouter API key
3. Set up model routing: Gemini Flash for autocomplete, Sonnet for complex
4. Test inline completions in a real project
5. **Does NOT replace Claude Code** — use alongside for quick edits and model flexibility

### Priority 5: Persistent Gateway (Always-On Jake)

**Goal**: Jake is always reachable via Telegram, even when Terminal is closed.

1. Create launchd plist for Hermes gateway:
   ```
   ~/Library/LaunchAgents/com.jake.hermes-gateway.plist
   ```
2. Configure to start on login, restart on crash
3. Logs to `~/.hermes/logs/gateway.log`
4. Monitor with: `launchctl list | grep jake`

---

## API Keys Inventory

| Service | Key Location | Purpose |
|---------|-------------|---------|
| OpenRouter | `~/.hermes/.env`, `~/.zshrc` | 300+ model access |
| Anthropic | `~/.hermes/.env`, `susan/backend/.env` | Direct Claude access |
| Groq | `~/.hermes/.env`, `~/.zshrc` | Fast inference (Llama 70B) |
| Firehose | `~/.hermes/.env`, `susan/backend/.env` | Real-time web monitoring |
| Telegram | `~/.hermes/.env` | @BirchRodgersbot |
| OpenAI | `jake-assistant/.env` | GPT-4o access |
| Voyage AI | `susan/backend/.env` | Embeddings (1024d) |
| Resend | `susan/backend/.env` | Email delivery (ARIA briefs) |
| Supabase | `susan/backend/.env` | Database access |

---

## Cost Estimate (Monthly)

| Component | Estimated Cost |
|-----------|---------------|
| OpenRouter (Sonnet for complex, Flash for simple) | $30-60 |
| OpenRouter (sub-agents, research) | $15-30 |
| Groq (fallback, fast tasks) | $0-5 |
| Firehose.com | Free (beta) |
| Kilo Code | Free (BYOK via OpenRouter) |
| Ollama (local heartbeat) | $0 |
| **Total** | **$45-95/mo** |

Well under the $100-150/mo budget.

---

## File Map

```
~/.hermes/                          # Hermes Agent home
├── SOUL.md                         # Jake personality
├── config.yaml                     # Model, routing, tools config
├── .env                            # API keys
├── skills/                         # 123 skills (built-in + custom)
│   ├── susan-rag-query/            # Susan RAG search
│   ├── company-context/            # Company analysis
│   ├── supabase-query/             # Database queries
│   ├── google-calendar/            # Calendar management
│   ├── gmail-secretary/            # Gmail management
│   ├── browser-automation/         # Browser control
│   └── ... (120 more)
├── memories/                       # Hermes persistent memory
├── sessions/                       # Conversation history
├── cron/                           # Scheduled tasks
└── hermes-agent/                   # Source code + venv
    └── .venv/                      # Python 3.13 environment

/Applications/Jake.app              # Desktop launcher (Jacob's photo icon)
~/Desktop/Jake                      # Desktop shortcut

~/.openclaw/                        # Legacy (shut down, preserved for reference)
```

---

## Decision Log

| Decision | Rationale | Date |
|----------|-----------|------|
| Migrate OpenClaw → Hermes | Self-improving skills, better architecture, native OpenRouter | 2026-03-19 |
| Use OpenRouter as primary gateway | One key for 300+ models, auto-fallback, 5.5% fee worth it | 2026-03-19 |
| Smart model routing (Flash + Sonnet) | Cost optimization: cheap for simple, powerful for complex | 2026-03-19 |
| Skip Blackbox AI | Proprietary, opaque routing, credit-hungry | 2026-03-19 |
| Pick Kilo over Roo Code | Kilo is superset fork of Roo, more features, same base | 2026-03-19 |
| Keep Claude Code for development | WISC architecture, hooks, sub-agents, extended thinking irreplaceable | 2026-03-19 |
| Firehose.com for web monitoring | Free beta by Ahrefs, real-time push, content diffs, fills gap in stack | 2026-03-19 |
