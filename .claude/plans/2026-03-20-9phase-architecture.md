# 9-Phase Jake Architecture — Full Roadmap

**Date**: 2026-03-20
**Status**: in-progress (Phase 1-2 complete, Phase 2.5 reliability hardening complete, Phase 3 Wave 1 complete)
**Origin**: Adapted from Mani Kanasani's ClawBuddy framework, scored Mike 31/100 vs Mani 86/100

---

## Phase 1: THE FOUNDATION ✅ (Complete)

**What**: Core infrastructure — multi-agent orchestration, Hermes config, MCP servers, personality

**Delivered**:
- Hermes config with SOUL.md personality
- 19 API keys in `~/.hermes/.env`
- Susan Intelligence + Notion MCP servers connected
- Approvals set to `off` (full autonomy)
- Telegram bot operational (`@mikerodgers_claw_bot`)
- 10 cognitive skills (jake-strategist, jake-challenger, jake-executor, etc.)
- jake-oracle-mail, jake-daily-intel skills

---

## Phase 2: THE BRAIN ✅ (Complete)

**What**: 4-layer cognitive memory + knowledge graph — Jake remembers everything across sessions and platforms

**Delivered**:
- 4 memory layers: Working → Episodic → Semantic → Procedural
- Knowledge graph: `jake_entities` + `jake_relationships` tables
- 6 Supabase tables with pgvector (Voyage AI 1024-dim embeddings)
- 2 RPC functions: `jake_brain_search` (composite ranking), `jake_entity_graph` (multi-hop traversal)
- Python engine: `jake_brain/` — 7 modules (config, store, extractor, graph, retriever, consolidator, pipeline)
- CLI: `scripts/jake_brain_cli.py` — seed, stats, search, person, ingest, consolidate, test
- Hermes plugin v2.0: 3 READ tools (brain_search, brain_person, brain_entities) + WRITE hooks
- Knowledge dump: 33 memory files → 34 episodic, 41 semantic, 19 entities, 29 relationships
- Apple Contacts ingestion: 43 contacts with birthdays + family relationships
- Shared brain: Claude Code Jake + Hermes Jake read/write same Supabase tables
- Auto-sync hook: `bin/hooks/brain-sync.sh` (Stop hook, async)

**Key files**:
- `susan-team-architect/backend/jake_brain/` (engine)
- `~/.hermes/plugins/jake-brain-ingest/__init__.py` (Hermes plugin)
- `scripts/brain_knowledge_dump.py`, `brain_contacts_ingest.py`, `jake_brain_cli.py`

---

## Phase 3: THE EYES 👁️ ✅ Wave 1 Complete (2026-03-21)

**What**: Sensors and data ingestion — Jake sees Mike's complete life, not just what's typed in chat

### Wave 1: Life Ingestion ✅ COMPLETE
| Source | Method | Status | Notes |
|--------|--------|--------|-------|
| Google Calendar | OAuth API | ✅ Working | 10 events found (flights, kids, Rush Friendly tonight) |
| Apple Reminders | osascript JXA | ✅ Working | 3 reminders (Matt Cohlmia call due today!) |
| Apple Mail (Exchange) | osascript JXA | ✅ Working | 26 emails (Matt Cohlmia, Oracle SharePoint) |
| Apple Calendar | osascript JXA (per-cal timeout) | ✅ Partial | Exchange hangs at 25s (skipped), other cals work |
| iMessage | sqlite3 chat.db | ⏳ Wave 1b | Deferred — needs Full Disk Access |

**Key fix**: `brain_calendar_ingest.py` rewritten to use per-calendar subprocess calls with
25s timeout each (replaces single slow `events.whose()` query that hung on Exchange).

**Daily cron**: `~/.hermes/scripts/brain_wave1_ingest.sh` → `com.jake.brain-wave1` launchd job
- Runs daily at 5:45 AM (15 min before morning brief)
- Loaded: `launchctl list | grep jake.brain-wave1` → confirmed

### Wave 2: Work Ingestion (scripts exist, not yet scheduled)
| Source | Script | Status |
|--------|--------|--------|
| GitHub activity | `brain_github_ingest.py` | ✅ Script exists |
| ChatGPT history | `brain_chatgpt_ingest.py` | ✅ Script exists |
| Claude transcripts | `brain_claude_ingest.py` | ✅ Script exists |
| Notion | TBD | ⏳ Not started |

### Wave 3: Media & Photos
| Source | Script | Status |
|--------|--------|--------|
| Apple Photos | `scripts/brain_photos_ingest.py` | ⏳ Not started |
| Google Photos | `scripts/brain_gphotos_ingest.py` | ⏳ Not started |

### Success Criteria
- [x] Jake can answer "What's on my calendar today?" — Google Calendar + Apple Calendar
- [x] Jake can answer "What did Oracle Health email me about?" — Mail ingest running
- [x] Jake can answer "When is Alex's next game?" — Google Calendar OAuth
- [x] Jake can answer "What reminders do I have?" — Reminders ingest running
- [x] All ingestion scripts are idempotent (dedup by event ID / content hash)

---

## Phase 4: THE SPINE 🦴 ✅ COMPLETE (2026-03-21)

**What**: Central routing + priority engine — Jake decides what matters and when to act

### Components Delivered
| Component | Purpose | Implementation |
|-----------|---------|---------------|
| Priority Engine | Rank incoming signals by urgency × importance × recency decay | `jake_brain/priority.py` |
| Intent Router | Route user requests to the right skill/agent | `jake_brain/intent_router.py` |
| Context Assembler | Build optimal context per task from brain layers | `jake_brain/context.py` |
| Morning Brief | Auto-assembled from brain (not hardcoded) | `scripts/brain_morning_brief.py` |

### Key Files
- `jake_brain/priority.py` — PriorityEngine, PrioritySignal, email_signal/calendar_signal/reminder_signal factories
- `jake_brain/context.py` — ContextAssembler, ContextBundle (token-budgeted, prompt-injectable)
- `jake_brain/intent_router.py` — IntentRouter (14 intent classes, keyword + regex routing → Hermes skill)
- `scripts/brain_morning_brief.py` — Full auto-assembly (pull → score → format → Telegram/email)
- `~/.hermes/scripts/brain_morning_brief.sh` — Shell wrapper for launchd
- `~/Library/LaunchAgents/com.jake.brain-morning-brief.plist` — daily at 6:00 AM

### Hermes Plugin Tools Added (3 new tools → 10 total)
- `brain_priority` — triage signals by P0/P1/P2/P3 tier
- `brain_context` — assemble context bundle for a task
- `brain_brief` — run morning brief from within Hermes

### Success Criteria
- [x] Jake's morning brief is auto-assembled from brain data (not hardcoded)
- [x] Jake can triage "what should I work on today?" via brain_priority tool
- [x] Intent router routes correctly (calendar, email, brief, oracle, family, recruiting, etc.)
- [x] Smoke test passed: 25 memories scored, 5 entities pulled, brief formatted and output

---

## Phase 5: THE HANDS ✋ ✅ COMPLETE (2026-03-21)

**What**: Action execution — Jake can DO things in the real world, not just read and report

### Capabilities Delivered
| Action | Method | Tier | File |
|--------|--------|------|------|
| Send email | Resend API | Tier 2 CONFIRM | `jake_brain/actions/send_email.py` |
| Create calendar event | Google Calendar API | Tier 2 CONFIRM | `jake_brain/actions/create_event.py` |
| Set reminder | osascript (Apple Reminders) | Tier 1 AUTO | `jake_brain/actions/set_reminder.py` |
| Send Telegram message | Bot API | Tier 1 AUTO | `jake_brain/actions/send_telegram.py` |
| Create GitHub issue | GitHub REST API | Tier 2 CONFIRM | `jake_brain/actions/create_github_issue.py` |
| Update Notion page | Notion REST API | Tier 2 CONFIRM | `jake_brain/actions/update_notion.py` |

### Architecture
- **Base class**: `jake_brain/actions/__init__.py` — `BaseAction`, `SafetyTier`, `ActionResult`, registry
- **Audit logger**: `jake_brain/actions/audit.py` — every execution logged to `jake_episodic` (source_type='action')
- **Safety model**: Tier 1 = auto, Tier 2 = preview → Telegram confirm → execute, Tier 3 = explicit approval
- **Action registry**: `@register` decorator → `get_action(name)` → `list_actions()`
- **CLI**: `scripts/jake_hands_cli.py` — list, preview, execute, smoke

### Hermes Plugin (v4.0.0)
- 3 new tools added: `action_preview`, `action_execute`, `action_list`
- Total: 13 tools (10 from Phase 4 + 3 new)
- `action_execute` sends Telegram confirmation for Tier 2 before executing
- All logged to jake_episodic with source_type='action'

### Smoke Test Results (2026-03-21)
- ✅ 6/6 actions registered and preview correctly
- ✅ set_reminder: Apple Reminder created in "Mike" list
- ✅ send_telegram: Message delivered (id: 252)
- Audit log: Non-blocking warning when Voyage AI key absent (works fine inside Hermes)

### Key Files
- `jake_brain/actions/__init__.py` — base class, registry, SafetyTier enum
- `jake_brain/actions/audit.py` — episodic audit logger
- `jake_brain/actions/send_email.py`, `create_event.py`, `set_reminder.py`
- `jake_brain/actions/send_telegram.py`, `create_github_issue.py`, `update_notion.py`
- `scripts/jake_hands_cli.py` — CLI runner + smoke test
- `~/.hermes/plugins/jake-brain-ingest/__init__.py` — updated with action handlers + schemas
- `~/.hermes/plugins/jake-brain-ingest/plugin.yaml` — bumped to v4.0.0

### Success Criteria
- [x] Jake can send an email on Mike's behalf (with confirmation)
- [x] Jake can add a calendar event (with confirmation)
- [x] Jake can set a reminder directly (auto-execute)
- [x] All actions are logged to jake_episodic and reversible where possible

---

## Phase 6: THE EMPLOYEES 👥 ✅ COMPLETE (2026-03-21)

**What**: Specialized sub-agents — Jake delegates to focused agents, each with their own brain context

### Agent Roster
| Agent | Domain | Runs On | Key Skills |
|-------|--------|---------|-----------|
| Oracle Jake | Oracle Health work | Hermes skill | Email triage, meeting prep, stakeholder intel, compliance |
| Family Jake | Family life | Hermes skill | Birthday tracking, schedule coordination, Jacob/Alex/Jen |
| Finance Jake | Money | Hermes skill | Budget tracking, subscription monitoring, API cost tracking |
| Health Jake | Fitness/wellness | Hermes skill | Workout tracking, sleep, nutrition, recovery |
| Recruiting Jake | Jacob's recruiting | Hermes skill | Coach outreach pipeline, school research, NCAA compliance |
| Research Jake | Deep research | Hermes skill | Competitive intel, market analysis, multi-source synthesis |

### Key Files
- `~/.hermes/skills/oracle-jake/SKILL.md` — Oracle Health work agent
- `~/.hermes/skills/family-jake/SKILL.md` — Family life agent
- `~/.hermes/skills/finance-jake/SKILL.md` — Finance/budget agent
- `~/.hermes/skills/health-jake/SKILL.md` — Health/wellness agent
- `~/.hermes/skills/recruiting-jake/SKILL.md` — Jacob's recruiting agent
- `~/.hermes/skills/research-jake/SKILL.md` — Deep research agent

### Delegation Tool
- `delegate_to_agent` tool added to `~/.hermes/plugins/jake-brain-ingest/__init__.py`
- Plugin bumped to v5.0.0 — 14 total tools
- Tool assembles domain-specific brain context per agent
- Routes to correct SKILL.md persona with relevant memories pre-loaded

### Architecture
- Each employee is a Hermes SKILL.md file (standalone skill that can be invoked by name)
- `delegate_to_agent(agent, query, context)` assembles domain brain context + loads persona
- Root Jake routes to employees via the Spine's intent router (already wired: oracle-jake, family-jake, recruiting-jake, research-jake)
- Employees can escalate back to root Jake for cross-domain work

### Success Criteria
- [x] All 6 employee skills exist and loaded (verified: 696 total lines across 6 skills)
- [x] `delegate_to_agent` tool registered in plugin (v5.0.0, 14 tools)
- [x] Brain context assembled per domain before delegation
- [x] Employees share brain but have domain-filtered context
- [x] Syntax valid, all 10 delegation checks pass

---

## Phase 7: THE IMMUNE SYSTEM 🛡️

**What**: Self-monitoring, error recovery, privacy guards — Jake protects himself and Mike

### Components
| Component | Purpose |
|-----------|---------|
| Error Recovery | Auto-retry failed API calls, escalate after 3 failures |
| Privacy Guard | Classify data sensitivity, enforce who sees what |
| Consistency Checker | Detect contradictory memories, flag for resolution |
| Health Monitor | Track brain stats, embedding costs, API usage, error rates |
| Stale Data Detector | Flag memories that haven't been reinforced in 30+ days |

### Key Behaviors
- **Error budget**: Track failures per source. If a source fails >5x/day, disable and alert Mike
- **PII classification**: Tag entities with sensitivity levels. Don't leak personal data to work contexts
- **Memory hygiene**: Monthly consolidation — promote strong episodic → semantic, archive weak memories
- **Cost tracking**: Monitor Voyage AI embedding costs, Supabase usage, Telegram API calls
- **Self-test**: Daily smoke test of brain search, entity lookup, and Telegram delivery

### Success Criteria
- [ ] Jake auto-recovers from common failures (API timeout, rate limit, stale token)
- [ ] Sensitive personal data never appears in work-context outputs
- [ ] Brain doesn't grow unbounded — stale data is archived or pruned
- [ ] Mike gets a weekly "system health" report

---

## Phase 8: THE NERVOUS SYSTEM ⚡

**What**: Real-time event processing + push notifications — Jake reacts to events as they happen

### Event Sources
| Source | Trigger | Response |
|--------|---------|----------|
| New email (Oracle) | osascript poll or Mail.app rule | Triage → notify if urgent |
| Calendar event starting | 15-min lookahead | Send prep brief + join link |
| GitHub PR review requested | Webhook / poll | Notify + context summary |
| TrendRadar competitor alert | MCP signal | Competitive brief |
| Scheduled task failure | Cron monitoring | Alert + auto-retry |

### Architecture
- **Event bus**: Lightweight Python event queue (not Kafka — this is personal use)
- **Event handlers**: Each event type has a handler that decides action + notification
- **Polling vs webhooks**: Start with polling (simpler), migrate to webhooks for GitHub/Telegram
- **Debounce**: Don't send 10 notifications in 5 minutes. Batch and summarize.

### Success Criteria
- [ ] Jake notifies about urgent emails within 5 minutes
- [ ] Meeting prep briefs arrive 15 minutes before the meeting
- [ ] Notifications are batched intelligently (not spammy)

---

## Phase 9: THE NETWORK 🌐

**What**: Multi-device sync, cross-platform presence — Jake is everywhere Mike is

### Capabilities
| Capability | Implementation |
|-----------|---------------|
| Mac presence | Hammerspoon + FastAPI (Layer 2 — already scaffolded) |
| iPhone presence | Shortcuts + Telegram |
| iPad presence | Same as iPhone |
| Cross-company sync | Shared brain handles this (already working) |
| Multi-Jake sync | Claude Code Jake + Hermes Jake already share brain |
| Guest access | James/Jacob can interact with their own limited Jake instance |

### Architecture
- **Single brain, multiple interfaces**: All Jakes read/write same Supabase tables
- **Interface-appropriate responses**: Mac gets rich text, Telegram gets concise, email gets formal
- **Presence detection**: Know which device Mike is active on → route notifications there
- **Family mode**: Jake can interact with James (husband) and Jacob (son) with appropriate context boundaries

### Success Criteria
- [ ] Jake works identically whether accessed via Telegram, Claude Code, or Hammerspoon
- [ ] Notifications route to the device Mike is currently using
- [ ] Jacob can ask Jake about his recruiting profile without seeing Mike's work data

---

## Implementation Timeline

| Phase | Est. Duration | Dependencies | Priority |
|-------|--------------|-------------|----------|
| Phase 3: Eyes | 2-3 sessions | Brain complete ✅ | 🔴 HIGH — most value |
| Phase 4: Spine | 1-2 sessions | Eyes (needs data to route) | 🔴 HIGH |
| Phase 5: Hands | 2-3 sessions | Spine (needs routing to trigger) | 🟡 MEDIUM |
| Phase 6: Employees | 2-3 sessions | Hands (employees need actions) | 🟡 MEDIUM |
| Phase 7: Immune | 1-2 sessions | Employees (needs agents to monitor) | 🟡 MEDIUM |
| Phase 8: Nervous | 2-3 sessions | All above | 🟢 LOW (polish) |
| Phase 9: Network | 2-3 sessions | All above | 🟢 LOW (expansion) |

**Recommended next session**: Phase 3 Wave 1 — Calendar + Mail ingestion (highest immediate value for morning briefs)

---

## Scoring Target

Current: **31/100** (per Mani comparison)
Target after Phase 3-4: **55/100** (data ingestion + routing)
Target after Phase 5-6: **75/100** (actions + delegation)
Target after Phase 7-9: **86+/100** (parity with Mani's ClawBuddy)
