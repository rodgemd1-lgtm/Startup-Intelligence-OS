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

## Phase 4: THE SPINE 🦴

**What**: Central routing + priority engine — Jake decides what matters and when to act

### Components
| Component | Purpose | Implementation |
|-----------|---------|---------------|
| Priority Engine | Rank incoming signals by urgency + importance | `jake_brain/priority.py` |
| Intent Router | Route user requests to the right agent/skill | Enhance KIRA agent |
| Context Assembler | Build optimal context for each task from brain layers | `jake_brain/context.py` |
| Notification Manager | Decide what's worth notifying Mike about, and when | `jake_brain/notifications.py` |

### Key Behaviors
- **Morning brief assembly**: Pull calendar, birthdays, tasks, recent emails → compose brief
- **Interrupt classification**: Is this worth a push notification or can it wait?
- **Agent routing**: Based on intent + context, pick the right Susan agent
- **Priority decay**: Things that aren't acted on gradually lose priority
- **Conflict detection**: Flag schedule conflicts, contradictory tasks, etc.

### Architecture Decisions
- Priority scoring: `urgency (0-1) × importance (0-1) × recency (decay function)`
- Notification channels: Telegram (push), daily brief (email), in-session (Claude Code)
- Context window: Spine assembles the MINIMUM context needed per request from brain layers

### Success Criteria
- [ ] Jake's morning brief is auto-assembled from brain data (not hardcoded)
- [ ] Jake can triage "what should I work on today?" from signals across all companies
- [ ] Notifications are smart — not every signal generates a ping

---

## Phase 5: THE HANDS ✋

**What**: Action execution — Jake can DO things in the real world, not just read and report

### Capabilities to Build
| Action | Method | Script/Tool |
|--------|--------|-------------|
| Send email | Apple Mail osascript OR Resend API | `jake_brain/actions/send_email.py` |
| Create calendar event | osascript / Google Calendar API | `jake_brain/actions/create_event.py` |
| Set reminder | osascript | `jake_brain/actions/set_reminder.py` |
| Send Telegram message | Bot API | Already exists (birthday_check.py pattern) |
| Create GitHub issue | gh CLI / API | `jake_brain/actions/create_issue.py` |
| Update Notion page | Notion API/MCP | `jake_brain/actions/update_notion.py` |
| Draft coach outreach email | Template + Resend | `jake_brain/actions/coach_outreach.py` |

### Safety Model
- **Tier 1 (Auto-execute)**: Read-only actions, Telegram messages, setting reminders
- **Tier 2 (Confirm)**: Sending emails, creating events, GitHub issues → Jake asks "Send this?"
- **Tier 3 (Require approval)**: Anything touching production, financial, or external-facing

### Architecture Decisions
- Action registry: Each action is a Python class with `preview()` and `execute()` methods
- Confirmation flow: Tier 2 actions show preview in Telegram, Mike reacts with ✅ or ❌
- Audit trail: Every action logged to `jake_episodic` with `source_type: "action"`

### Success Criteria
- [ ] Jake can send an email on Mike's behalf (with confirmation)
- [ ] Jake can add a calendar event (with confirmation)
- [ ] Jake can set a reminder directly
- [ ] All actions are logged and reversible where possible

---

## Phase 6: THE EMPLOYEES 👥

**What**: Specialized sub-agents — Jake delegates to focused agents, each with their own brain context

### Agent Roster
| Agent | Domain | Runs On | Key Skills |
|-------|--------|---------|-----------|
| Oracle Jake | Oracle Health work | Hermes + Claude Code | Email triage, meeting prep, stakeholder intel |
| Family Jake | Family life | Hermes | Birthday tracking, schedule coordination, school events |
| Finance Jake | Money | Hermes | Budget tracking, subscription monitoring, expense alerts |
| Health Jake | Fitness/wellness | Hermes | Workout tracking, nutrition, sleep patterns |
| Recruiting Jake | Jacob's recruiting | Claude Code | Coach outreach, highlight reel, school research |
| Research Jake | Deep research | Claude Code | Long-form research, competitive intel, market analysis |

### Architecture
- Each "employee" is a Hermes skill or Claude Code agent definition
- Employees access shared brain but have domain-specific prompts
- Jake (root) delegates to employees based on intent classification (Spine)
- Employees can escalate back to Jake when they need cross-domain context

### Success Criteria
- [ ] "Oracle Jake" handles all Oracle Health work without root Jake intervention
- [ ] "Family Jake" tracks school events, family birthdays, coordination with Jen
- [ ] Employees share brain but don't pollute each other's context

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
