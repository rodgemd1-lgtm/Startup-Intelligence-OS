# Hermes Personal AI Assistant -- 10X Capability Assessment

**Assessor:** Susan (Capability Foundry)
**Date:** 2026-03-21
**Scope:** Full system audit of Hermes PA across 3 Telegram touchpoints, 4-layer brain, 11 ingestion scripts, 12 cron jobs, and 9-phase architecture (Phases 1-3 complete)
**Method:** Code-grounded analysis of jake_brain/ engine, ingestion scripts, retriever.py, consolidator.py, pipeline.py, 9-phase plan, and known issues
**Baseline Score:** 31/100 (Mani comparison, 2026-03-20)

---

## Executive Summary

Mike's Hermes system has built extraordinary infrastructure depth in 3 sessions: a 4-layer cognitive memory engine with 37,483 memories, 11 data ingestion scripts, a knowledge graph with 63 entities and 56 relationships, composite-scored brain search via RPC, and a consolidation pipeline with layer promotion logic. The brain architecture is genuinely sophisticated -- most personal AI projects never get past flat RAG.

The problem is the gap between infrastructure and experience. Mike has a Formula 1 engine bolted to a go-kart chassis. The brain stores everything but retrieves poorly (calendar events drown profiles). The 3 Telegram bots are disconnected (no shared routing, no unified identity). There is no priority engine, no proactive behavior, no action execution, and no learning from corrections. The system ingests Mike's life but does not run it.

The 10X target is not "more data in the brain." It is: Mike opens Telegram, asks "what should I focus on today," and gets a prioritized answer assembled from calendar, email, tasks, brain context, and cross-company signals -- then Jake executes the top items with minimal confirmation. That is the distance from 31/100 to 86/100.

**Current aggregate maturity:** 1.8 / 5.0 (Emerging)
**10X target maturity:** 4.0 / 5.0 (Optimizing)

---

## Maturity Scale

| Level | Score | Definition |
|-------|-------|------------|
| Nascent | 1 | Concept or spec exists, not operational |
| Emerging | 2 | Working prototype, used manually, obvious gaps |
| Scaling | 3 | Reliable, repeatable, measured, used daily |
| Optimizing | 4 | Self-improving, feedback loops closed, metrics-driven |
| Leading | 5 | Best-in-class, anticipatory, compounds automatically |

---

## CAPABILITY MAP: 15 Domains

### DOMAIN 1: Cognitive Memory (Brain)

| Attribute | Value |
|-----------|-------|
| Current Maturity | 2.8 / 5.0 (Emerging+) |
| Target Maturity | 4.5 / 5.0 |
| Delta | +1.7 |
| Owner | Atlas (architecture) + Knowledge Engineer |
| Human/Agent | 10% Mike / 90% agent |

**Current State (verified in code):**
- 4-layer architecture: Working -> Episodic -> Semantic -> Procedural (jake_brain/ — 7 modules)
- Knowledge graph: jake_entities (63) + jake_relationships (56)
- Composite search via `jake_brain_search` RPC: similarity x confidence x layer_weight x recency x access_boost
- Consolidation pipeline: Working->Episodic (auto), Episodic->Semantic (3+ refs), Patterns->Procedural (planned)
- 37,483 total memories: 33K episodic, 2K semantic, 2K procedural
- Voyage AI embeddings (1024 dim) via shared Embedder
- Content-hash deduplication on all ingestion scripts

**What is broken or weak:**
- **Signal-to-noise ratio is terrible.** 33K episodic memories with no quality scoring beyond `importance` field. Calendar events (low value per unit) vastly outnumber profile facts (high value per unit). A search for "Mike's family" returns 10 calendar entries before returning any actual family knowledge.
- **No memory decay.** Old calendar events from 2 months ago have the same weight as yesterday's. `access_count` bump exists but recency decay in the RPC is weak.
- **Consolidation runs manually.** The nightly cron was planned but the `promote_episodic_to_semantic` logic (consolidator.py line 50) scans batch_size=100 at a time and uses simple content similarity -- no clustering, no dedup of near-identical calendar blurbs.
- **Knowledge graph is static.** 63 entities seeded from contacts + knowledge dump. No entity resolution (same person mentioned different ways creates duplicates). No relationship inference. No graph queries at retrieval time (brain_search RPC ignores graph).
- **No contradiction detection.** If Mike says "meeting moved to Thursday" and the brain has it on Wednesday, both exist. The `contradiction_similarity_threshold` config exists but no code path uses it for resolution.

**Target State:**
- Memory quality scoring: every memory gets a `utility_score` based on access frequency, recency, uniqueness, and downstream usage (did Jake cite this in a response?)
- Aggressive consolidation: nightly job clusters related episodic memories, promotes high-utility clusters to semantic, archives low-utility stale memories (>30 days, 0 accesses)
- Source-type weighting: profile data and semantic facts get 3x boost over calendar events in search ranking
- Entity resolution: "Jacob," "Jacob Rodgers," "my son" resolve to one entity
- Graph-enhanced retrieval: brain_search RPC traverses 1-hop relationships when query mentions a person
- Contradiction resolution: when conflicting facts are detected, flag for Mike or auto-resolve by recency

**Gap:** The brain stores everything but treats all memories equally. The retriever needs source-type weighting, the consolidator needs real clustering, and the graph needs to participate in search.

**Success Criteria:**
- Search for "Mike's family" returns profile/semantic facts first, not calendar events
- Brain size stabilizes at <50K active memories (stale archived)
- Entity count reaches 200+ with <5% duplicate rate
- Contradiction detection catches at least 80% of schedule changes

---

### DOMAIN 2: Data Ingestion (Eyes)

| Attribute | Value |
|-----------|-------|
| Current Maturity | 2.5 / 5.0 (Emerging+) |
| Target Maturity | 4.0 / 5.0 |
| Delta | +1.5 |
| Owner | Nova (data engineering) + Pulse (monitoring) |
| Human/Agent | 5% Mike / 95% agent |

**Current State (verified via file listing):**
- 11 ingestion scripts in `scripts/brain_*.py`: calendar, gcal, mail, reminders, contacts, github (19 repos), chatgpt (28 convos), claude_code, hermes, profile, knowledge_dump
- All scripts follow consistent pattern: extract -> normalize -> deduplicate -> store episodic + semantic + entities
- Content-hash dedup prevents duplicate ingestion on re-runs
- Wave 1 (life) and Wave 2 (work) complete per 9-phase plan

**What is broken or weak:**
- **No ingestion health monitoring.** If `brain_mail_ingest.py` fails because Mail.app timed out (known issue), nobody knows until Mike asks "why didn't you know about that email?"
- **ChatGPT export is broken.** Had to use Chrome scraping workaround. No reliable automated pipeline.
- **No incremental ingestion.** Scripts re-scan everything and rely on dedup to skip. For 19 GitHub repos, this is slow and wasteful.
- **Calendar events are over-ingested.** Every recurring standup creates an episodic memory. 52 weeks x 5 standups = 260 memories for "Oracle Health standup" alone.
- **No data freshness tracking.** No way to know when each source was last successfully ingested.

**Target State:**
- Ingestion health dashboard: last-run timestamp, success/fail, records ingested, error log per source
- Incremental ingestion: watermark tracking (last_ingested_at per source) so scripts only process new data
- Smart dedup for recurring events: one semantic memory "Mike has Oracle Health standup MWF 9am" instead of 260 episodic entries
- Source freshness alerts: if any source hasn't ingested in >24h, alert via Telegram
- Wave 3 (photos/media) metadata ingestion for location and timeline enrichment

**Success Criteria:**
- All 11 ingestion scripts tracked with last-run, status, and count
- Calendar ingestion produces <5 memories/week for recurring events (down from ~50)
- Failed ingestion triggers Telegram alert within 1 hour
- Incremental runs complete in <30 seconds (vs minutes for full scan)

---

### DOMAIN 3: Intent Understanding & Routing (Spine)

| Attribute | Value |
|-----------|-------|
| Current Maturity | 0.5 / 5.0 (Nascent) |
| Target Maturity | 4.0 / 5.0 |
| Delta | +3.5 |
| Owner | KIRA (intent classification) + Susan (orchestrator) |
| Human/Agent | 5% Mike / 95% agent |

**Current State:**
- No intent router exists. Hermes/Birch handles all requests through generic LLM + plugins.
- KIRA was built for the 25x system but not wired into Hermes.
- ClaudeBirchBot routes by project prefix (hardcoded) but has no intent understanding.
- No request classification, no complexity estimation, no agent delegation.

**What is broken or weak:**
- **Every request gets the same treatment.** "What's the weather?" and "analyze my Oracle Health strategy for Q3" both hit the same LLM path with the same context window.
- **No model routing.** Simple queries burn the same tokens as complex research. No Haiku/Sonnet/Opus tiering.
- **Brain context injection is blind.** The Hermes plugin injects brain results but doesn't select which memory layers are relevant to the specific request type.
- **No multi-step planning.** "Prepare for my 2pm meeting" requires: check calendar, find attendees, search brain for attendee context, check recent emails from them, compose brief. Currently impossible as a single request.

**Target State:**
- Intent classification layer: categorize every request into {question, action, research, planning, personal, meta}
- Complexity estimation: simple (Haiku), moderate (Sonnet), complex (Opus)
- Context-aware brain injection: questions about people get graph-enhanced results, calendar queries get time-filtered results, work queries get project-scoped results
- Multi-step decomposition: complex requests get broken into a chain of sub-tasks, each with appropriate brain context
- Request memory: learn from corrections ("no, I meant the OTHER Jacob meeting") to improve future classification

**Success Criteria:**
- 90% of requests classified correctly on first attempt
- Token cost per request drops 40% via model routing (simple queries on Haiku)
- Multi-step requests like "prepare for my meeting" work end-to-end
- Correction rate drops below 10% after 30 days of learning

---

### DOMAIN 4: Proactive Intelligence

| Attribute | Value |
|-----------|-------|
| Current Maturity | 1.0 / 5.0 (Nascent) |
| Target Maturity | 4.5 / 5.0 |
| Delta | +3.5 |
| Owner | ARIA (briefs) + Steve (strategy) |
| Human/Agent | 0% Mike / 100% agent |

**Current State:**
- ARIA daily brief emails at 6:39 AM (hardcoded template, not brain-assembled)
- Oracle Health morning brief at 6:02 AM weekdays
- Birthday check script exists (`scripts/birthday_check.py`)
- 12 cron jobs active

**What is broken or weak:**
- **Briefs are template-driven, not intelligence-driven.** The daily brief doesn't query the brain for today's priorities based on signals. It's a static format.
- **No anticipatory behavior.** Jake never says "heads up, you have a meeting with Matt in 2 hours and he emailed you about X yesterday." That requires cross-source correlation that doesn't exist.
- **No pattern detection.** The brain has 33K episodic memories but nobody is mining them for patterns ("you tend to get pulled into unplanned Oracle meetings on Thursdays").
- **No nudges.** If Mike hasn't responded to an important email in 48 hours, nobody flags it.

**Target State:**
- Brain-assembled morning brief: pull today's calendar, overdue reminders, recent emails needing response, birthdays, cross-company priorities -> compose via LLM
- Meeting prep auto-delivery: 15 minutes before any meeting, deliver attendee context, recent email threads, relevant brain memories
- Stale commitment detector: if Mike said "I'll send that by Friday" and it's Friday morning with no action, nudge
- Pattern mining: weekly analysis of episodic memories for recurring themes, time-wasters, productivity patterns
- Anticipatory notifications: predict what Mike will need before he asks based on calendar + recent activity

**Success Criteria:**
- Morning brief includes at least 3 brain-sourced insights (not template filler)
- Meeting prep arrives for 100% of scheduled meetings with relevant context
- At least 1 proactive nudge per day that Mike finds useful (measured by response/action rate)
- Weekly pattern report identifies at least 1 actionable insight

---

### DOMAIN 5: Action Execution (Hands)

| Attribute | Value |
|-----------|-------|
| Current Maturity | 0.3 / 5.0 (Nascent) |
| Target Maturity | 3.5 / 5.0 |
| Delta | +3.2 |
| Owner | Forge (engineering) + Atlas (architecture) |
| Human/Agent | 15% Mike (approvals) / 85% agent |

**Current State:**
- Jake can read from: calendar, mail, contacts, reminders, GitHub, Notion, ChatGPT, Claude
- Jake can write to: Telegram (birthday_check.py pattern), Supabase brain tables
- Jake CANNOT: send email, create calendar events, set reminders, create GitHub issues, draft outreach, update Notion
- No action registry, no confirmation flow, no audit trail for actions

**What is broken or weak:**
- **Read-only assistant.** Jake can tell you what's on your calendar but cannot add to it. This is the #1 reason Mike can't say "this thing runs my life."
- **No action safety model.** No tiered approval system for different action types.
- **No undo/rollback.** If an action goes wrong, there's no reversal mechanism.

**Target State:**
- Action registry: Python classes with `preview()`, `execute()`, `undo()` methods
- 7 core actions: send_email, create_event, set_reminder, send_telegram, create_github_issue, update_notion, draft_outreach
- 3-tier safety: auto-execute (read-only, reminders), confirm (email, events), require approval (production, financial)
- Telegram confirmation flow: Tier 2 shows preview, Mike taps approve/reject
- Full audit trail: every action logged to jake_episodic with source_type="action"

**Success Criteria:**
- Mike can say "schedule a meeting with Matt tomorrow at 2pm" and it happens
- Mike can say "remind me to follow up with the recruiter Friday" and it's set
- Mike can say "draft an email to Ellen about the Q3 roadmap" and review/send from Telegram
- Zero unintended actions (100% confirmation rate on Tier 2+)

---

### DOMAIN 6: Bot Architecture & Unification

| Attribute | Value |
|-----------|-------|
| Current Maturity | 1.2 / 5.0 (Nascent) |
| Target Maturity | 3.5 / 5.0 |
| Delta | +2.3 |
| Owner | Atlas (architecture) + Sentinel (reliability) |
| Human/Agent | 20% Mike (design decisions) / 80% agent |

**Current State:**
- 3 disconnected Telegram bots:
  1. Hermes/Birch (OpenClaw): LLM + plugins, personality, brain access, 12 crons
  2. ClaudeBirchBot (NEW): `claude -p` CLI relay, project routing, launchd
  3. Genspark OpenClaw: GitHub PAT, channel posts
- No shared conversation state between bots
- No unified identity ("which bot do I talk to for what?")
- ClaudeBirchBot requires Mac to be on, has no session persistence

**What is broken or weak:**
- **Three bots is two too many for UX.** Mike has to remember which bot handles what. That's an assistant managing Mike, not the other way around.
- **No conversation continuity across bots.** If Mike talks to Hermes about a topic, then asks ClaudeBirchBot to execute, it has zero context.
- **ClaudeBirchBot is fragile.** Mac-dependent, no session persistence, new and untested.
- **Genspark bot serves a narrow purpose** (channel posts) that could be a cron job.

**Target State:**
- **Single Telegram entry point** with internal routing. Mike talks to "Jake" -- one bot, one identity.
- Behind the scenes: intent router decides whether to handle via Hermes (fast, personality, brain access) or Claude CLI (complex, multi-file, code tasks)
- Genspark channel posting becomes a cron job triggered by Jake, not a separate bot
- Conversation state persisted to brain so context carries across routing paths
- Fallback: if Mac is off, ClaudeBirchBot tasks queue and execute when Mac comes online (or route to cloud alternative)

**Success Criteria:**
- Mike interacts with exactly 1 bot ("Jake") for everything
- Routing is invisible -- Mike never has to think about which backend handles it
- Conversation from 10 minutes ago is available regardless of which path handled it
- System degrades gracefully when Mac is off (queues, not fails)

---

### DOMAIN 7: Conversation Quality

| Attribute | Value |
|-----------|-------|
| Current Maturity | 1.5 / 5.0 (Nascent-Emerging) |
| Target Maturity | 4.0 / 5.0 |
| Delta | +2.5 |
| Owner | Mira (product quality) + Conversation Designer |
| Human/Agent | 10% Mike (personality feedback) / 90% agent |

**Current State:**
- SOUL.md personality (Jake's voice)
- Brain plugin injects search results into context
- `display.personality: ''` fix applied (was overriding SOUL.md)
- Approvals set to smart mode

**What is broken or weak:**
- **Brain context injection is dumb.** Every query gets brain_search results injected, even if irrelevant. No filtering by query type.
- **No conversation memory within session.** Hermes has some session state but it's not wired to brain working memory.
- **Responses fail at simple PA tasks.** Known issue: wrong tool usage, unnecessary retries, approval confusion. The UX of actual conversations is poor despite good infrastructure.
- **No personality consistency scoring.** Jake should sound like Jake 100% of the time. Sometimes plugins or tool outputs override personality.

**Target State:**
- Selective brain injection: only inject memories relevant to the detected intent
- Session working memory: current conversation tracked in jake_working, promoted at session end
- Response quality monitoring: track user satisfaction signals (message length as proxy, correction rate, abandon rate)
- Personality guard: post-response check that output maintains Jake's voice
- Error recovery: if a tool fails, Jake explains in character ("aight that didn't work, let me try another way") instead of showing raw errors

**Success Criteria:**
- Mike rates conversation quality 4+/5 in weekly self-assessment
- Tool failure rate drops below 5% per session
- Correction rate ("no, I meant...") drops below 10%
- Jake's personality is consistent across 95%+ of responses

---

### DOMAIN 8: Learning & Self-Improvement

| Attribute | Value |
|-----------|-------|
| Current Maturity | 0.5 / 5.0 (Nascent) |
| Target Maturity | 4.0 / 5.0 |
| Delta | +3.5 |
| Owner | AI Eval + Algorithm Lab |
| Human/Agent | 5% Mike / 95% agent |

**Current State:**
- Consolidation pipeline exists but runs manually
- access_count bumped on retrieved episodic memories
- No correction tracking, no preference learning, no feedback loops
- No routing quality measurement

**What is broken or weak:**
- **Jake doesn't learn from mistakes.** If Mike corrects a response, that correction is not stored as a procedural memory that changes future behavior.
- **No A/B testing.** No way to test whether a routing change or prompt change improves response quality.
- **No usage analytics.** Nobody knows which features Mike uses most, which fail most, which he ignores.
- **Consolidation is manual.** The nightly cron was planned but not confirmed running.

**Target State:**
- Correction capture: every "no, I meant X" gets stored as procedural memory with the failed attempt and correction
- Preference tracking: track which response formats, lengths, and styles Mike engages with most
- Nightly consolidation: automatic, with stats reported in morning brief ("consolidated 47 memories, promoted 3 to semantic, archived 12 stale")
- Weekly self-assessment: compare predicted vs actual utility of responses
- Routing telemetry: track which intent classifications led to satisfactory outcomes

**Success Criteria:**
- Same mistake never happens 3 times (correction capture prevents it)
- Consolidation runs automatically every night with zero human intervention
- Monthly learning report shows measurable improvement in at least 2 metrics
- Procedural memory library reaches 50+ entries within 60 days

---

### DOMAIN 9: Security & Privacy

| Attribute | Value |
|-----------|-------|
| Current Maturity | 0.8 / 5.0 (Nascent) |
| Target Maturity | 3.0 / 5.0 |
| Delta | +2.2 |
| Owner | Sentinel (security) + Shield (risk) |
| Human/Agent | 15% Mike / 85% agent |

**Current State:**
- 19 API keys in `~/.hermes/.env` (file-based, not vaulted)
- No PII classification on brain memories
- No access controls between work and personal contexts
- No audit log for who accessed what
- Mac must be on for ClaudeBirchBot (physical security dependency)

**What is broken or weak:**
- **No context boundaries.** If Jacob interacts with Jake (Phase 9 goal), he could theoretically see Mike's Oracle Health emails.
- **API keys in plaintext.** 19 keys in a dotfile. One compromised plugin exposes everything.
- **No data sensitivity tagging.** Brain stores Oracle Health emails and family texts in the same tables with the same access level.
- **No access logging.** Can't audit what data was accessed when.

**Target State:**
- Data sensitivity tagging: every memory gets a sensitivity level (public, personal, work-confidential, family-private)
- Context boundaries: brain queries filter by sensitivity level based on who's asking
- API key rotation schedule: quarterly rotation, monitored for staleness
- Access audit log: every brain query logged with requester, query, results returned
- Encryption at rest for high-sensitivity memories (beyond Supabase default)

**Success Criteria:**
- Family members can use Jake without seeing work data (tested)
- All API keys have rotation dates tracked
- Audit log captures 100% of brain queries
- No PII appears in non-matching context responses

---

### DOMAIN 10: Reliability & Observability

| Attribute | Value |
|-----------|-------|
| Current Maturity | 0.5 / 5.0 (Nascent) |
| Target Maturity | 3.5 / 5.0 |
| Delta | +3.0 |
| Owner | Pulse (monitoring) + Sentinel (reliability) |
| Human/Agent | 5% Mike / 95% agent |

**Current State:**
- No health monitoring for any component
- No error tracking beyond stdout logs
- No uptime monitoring for Telegram bots
- Known: Mail.app osascript times out if running long (killall workaround)
- No alerting on failures

**What is broken or weak:**
- **Silent failures everywhere.** If a cron job fails, Mike discovers it days later when data is missing.
- **No system health dashboard.** Brain stats, ingestion status, bot uptime, error rates -- all invisible.
- **No self-healing.** Known Mail.app timeout issue requires manual killall. Many such fixable failures exist.

**Target State:**
- Health check endpoint: ping all 3 bots, all 11 ingestion sources, brain connectivity, cron status
- Telegram health report: daily system status message (brain size, ingestion freshness, error count, uptime)
- Auto-recovery: common failure patterns get automatic retry with backoff
- Error budget: if any component exceeds 5 failures/day, auto-disable and alert Mike
- Cron monitoring: every scheduled task tracked with expected vs actual run time

**Success Criteria:**
- System health visible in one Telegram message daily
- Auto-recovery handles 80% of transient failures without Mike's intervention
- Mean time to detect failure < 15 minutes (down from days)
- Mean time to recover from common failures < 5 minutes

---

### DOMAIN 11: Cross-Company Intelligence

| Attribute | Value |
|-----------|-------|
| Current Maturity | 1.0 / 5.0 (Nascent) |
| Target Maturity | 3.5 / 5.0 |
| Delta | +2.5 |
| Owner | Steve (strategy) + Research Director |
| Human/Agent | 10% Mike / 90% agent |

**Current State:**
- Brain has memories tagged with projects (oracle-health, alex-recruiting, etc.)
- Susan's RAG has 94K chunks across companies
- No cross-company correlation or synergy detection
- No unified priority view across all companies

**What is broken or weak:**
- **No "what should I work on today" answer that spans all companies.** Mike has to check each project separately.
- **No pattern transfer.** When something works in one company, it's not surfaced as applicable to others.
- **TrendRadar competitive intel exists but isn't wired to brain or briefs.**

**Target State:**
- Unified priority engine: rank tasks/signals from all companies into one prioritized list
- Cross-company pattern matching: weekly scan for transferable patterns
- Competitive intel integration: TrendRadar signals feed into brain as semantic memories
- Portfolio health dashboard: one-glance view of all company statuses

**Success Criteria:**
- "What should I work on?" returns a prioritized list spanning all companies
- At least 1 cross-company insight surfaced per week
- Competitive alerts from TrendRadar appear in morning brief

---

### DOMAIN 12: Family & Personal Life

| Attribute | Value |
|-----------|-------|
| Current Maturity | 1.8 / 5.0 (Emerging) |
| Target Maturity | 4.0 / 5.0 |
| Delta | +2.2 |
| Owner | Family Jake (Phase 6 employee) |
| Human/Agent | 10% Mike / 90% agent |

**Current State:**
- 43 contacts with birthdays ingested
- Google Calendar has kids' events
- Knowledge graph has family entities (James, Jacob, Alex, Jen)
- Birthday check script exists

**What is broken or weak:**
- **No family coordination intelligence.** Jake knows Jacob has a game but doesn't know if it conflicts with Mike's meeting.
- **No proactive family reminders.** "Jacob's birthday is next week -- have you planned anything?"
- **No family-friendly interface.** Jacob can't ask Jake about his recruiting profile safely.

**Target State:**
- Conflict detection: flag when family events overlap with work events
- Proactive family alerts: birthdays 1 week out, school events day-of, pickup schedule
- Family member access: Jacob can interact with Jake (recruiting only), James can interact (shared calendar, home)
- Recruiting integration: Jacob's game schedule, highlight reel status, coach outreach tracking

**Success Criteria:**
- Zero missed family birthdays
- Schedule conflicts detected 24 hours in advance
- Jacob can ask "what's my recruiting status?" and get an answer
- Family events appear in morning brief alongside work events

---

### DOMAIN 13: Voice & Multi-Modal

| Attribute | Value |
|-----------|-------|
| Current Maturity | 0.0 / 5.0 (Not started) |
| Target Maturity | 2.5 / 5.0 |
| Delta | +2.5 |
| Owner | Atlas (architecture) + Nova (integration) |
| Human/Agent | 20% Mike / 80% agent |

**Current State:**
- Text-only interaction via Telegram
- No voice input or output
- No image/document understanding
- No screen/app context

**What is broken or weak:**
- **Text-only limits use cases.** Mike can't say "hey Jake" while driving to get a briefing.
- **No document understanding.** Mike can't forward a PDF and say "summarize this."
- **No visual context.** Jake can't see screenshots, photos, or documents.

**Target State:**
- Voice input via Telegram voice messages -> transcription -> intent router
- Document processing: PDF, image, screenshot analysis via multi-modal LLM
- Voice output: TTS for briefings (optional, Telegram voice notes)
- Smart reply suggestions based on email/message content

**Success Criteria:**
- Mike can send a voice note and get a text response
- Mike can forward a document and get a summary
- Voice briefing option available for morning brief

---

### DOMAIN 14: Smart Notifications & Interruption Management

| Attribute | Value |
|-----------|-------|
| Current Maturity | 0.3 / 5.0 (Nascent) |
| Target Maturity | 4.0 / 5.0 |
| Delta | +3.7 |
| Owner | Notification Manager (Phase 4 component) |
| Human/Agent | 5% Mike / 95% agent |

**Current State:**
- Cron-based briefs at fixed times
- Birthday check script
- No real-time event-driven notifications
- No interruption intelligence

**What is broken or weak:**
- **Dumb scheduling.** Briefs arrive at 6:02/6:39 AM regardless of whether Mike is awake, traveling, or in back-to-back meetings.
- **No urgency classification.** An email from the CEO and a newsletter arrive with the same (zero) notification priority.
- **No batching.** Each signal triggers independently. 10 emails in 5 minutes could mean 10 notifications.
- **No DND awareness.** Jake doesn't know when Mike is in a meeting, sleeping, or driving.

**Target State:**
- Urgency scoring: every incoming signal scored on urgency x importance x sender_weight
- Intelligent batching: low-urgency signals batch into hourly/daily digests
- DND awareness: check calendar before sending notifications; during meetings, queue non-urgent items
- Escalation: if an urgent signal isn't acknowledged in 30 minutes, re-notify or try alternate channel
- Notification learning: track which notifications Mike acts on vs ignores, adjust thresholds

**Success Criteria:**
- <5 push notifications per day (down from potential 50+)
- 90%+ of push notifications result in Mike taking action (relevance test)
- Zero notifications during scheduled meetings (DND respected)
- Urgent items reach Mike within 5 minutes regardless of DND

---

### DOMAIN 15: Delegation & Workflow Chains

| Attribute | Value |
|-----------|-------|
| Current Maturity | 0.0 / 5.0 (Not started) |
| Target Maturity | 3.0 / 5.0 |
| Delta | +3.0 |
| Owner | Susan (orchestrator) + Forge (engineering) |
| Human/Agent | 10% Mike / 90% agent |

**Current State:**
- No multi-step workflow execution
- No delegation to specialized agents from Telegram
- No workflow templates
- No progress tracking on delegated work

**What is broken or weak:**
- **Jake can't handle compound requests.** "Research competitor X, draft a brief, send it to Ellen" requires 3 manual interactions.
- **No workflow memory.** Jake can't track "I asked you to research this yesterday, where are we?"
- **No delegation chain.** Jake can't dispatch to Research Director, get results, pass to Aria for formatting, and deliver.

**Target State:**
- Workflow engine: define multi-step chains (research -> analyze -> draft -> review -> send)
- Delegation to Susan agents: Jake routes sub-tasks to appropriate agents
- Progress tracking: "status update on the research I asked for" returns current state
- Workflow templates: predefined chains for common requests (meeting prep, competitor brief, outreach draft)
- Background execution: long-running tasks execute in background, notify on completion

**Success Criteria:**
- "Research competitor X and send me a brief" executes end-to-end
- Background tasks report progress when asked
- At least 5 workflow templates available for common requests
- Multi-step workflows complete with <2 human interventions per chain

---

## AGGREGATE SCORING

| Domain | Current | Target | Delta | Priority |
|--------|---------|--------|-------|----------|
| 1. Cognitive Memory | 2.8 | 4.5 | +1.7 | HIGH |
| 2. Data Ingestion | 2.5 | 4.0 | +1.5 | MEDIUM |
| 3. Intent & Routing | 0.5 | 4.0 | +3.5 | CRITICAL |
| 4. Proactive Intelligence | 1.0 | 4.5 | +3.5 | CRITICAL |
| 5. Action Execution | 0.3 | 3.5 | +3.2 | HIGH |
| 6. Bot Unification | 1.2 | 3.5 | +2.3 | HIGH |
| 7. Conversation Quality | 1.5 | 4.0 | +2.5 | HIGH |
| 8. Learning & Self-Improvement | 0.5 | 4.0 | +3.5 | MEDIUM |
| 9. Security & Privacy | 0.8 | 3.0 | +2.2 | MEDIUM |
| 10. Reliability & Observability | 0.5 | 3.5 | +3.0 | HIGH |
| 11. Cross-Company Intelligence | 1.0 | 3.5 | +2.5 | MEDIUM |
| 12. Family & Personal | 1.8 | 4.0 | +2.2 | MEDIUM |
| 13. Voice & Multi-Modal | 0.0 | 2.5 | +2.5 | LOW |
| 14. Smart Notifications | 0.3 | 4.0 | +3.7 | CRITICAL |
| 15. Delegation Chains | 0.0 | 3.0 | +3.0 | LOW |
| **AGGREGATE** | **1.0** | **3.7** | **+2.7** | -- |

**Weighted score (by usage impact):** 1.8 / 5.0

---

## 10X HERMES IMPROVEMENT PLAN

### Guiding Principle

The 10X plan focuses on the **experience layer** -- making what already exists actually work for Mike. The brain is built. The data is ingested. The gap is: retrieval quality, proactive behavior, action execution, and unified UX. These 4 pillars will take Mike from "cool infrastructure" to "I can't live without this."

---

### PHASE 4A: THE SPINE (Priority Engine + Intent Router)
**Duration:** 1-2 sessions | **Impact:** Critical foundation for everything after

| Sub-Phase | Build | Owner | Effort | Success Test |
|-----------|-------|-------|--------|--------------|
| 4A.1 | Intent classifier (6 categories: question, action, research, planning, personal, meta) | KIRA + Atlas | 3h | 90% classification accuracy on 50 test prompts |
| 4A.2 | Brain context assembler — select memory layers by intent type | Knowledge Engineer | 2h | "Tell me about Jacob" returns profile facts, not calendar events |
| 4A.3 | Priority engine — rank signals from all sources by urgency x importance | Steve + Nova | 3h | "What should I work on?" returns cross-company prioritized list |
| 4A.4 | Source-type weighting in brain search (profile 3x, semantic 2x, episodic 1x, calendar 0.5x) | Atlas | 1h | Search quality validated on 20 test queries |

**Key files to create/modify:**
- `jake_brain/intent.py` — intent classification
- `jake_brain/context.py` — context assembly per intent
- `jake_brain/priority.py` — signal priority scoring
- Modify `jake_brain_search` RPC — add source_type weighting

---

### PHASE 4B: SMART NOTIFICATIONS
**Duration:** 1 session | **Impact:** Transforms passive assistant to proactive partner

| Sub-Phase | Build | Owner | Effort | Success Test |
|-----------|-------|-------|--------|--------------|
| 4B.1 | Notification manager with urgency scoring | Pulse + Nova | 2h | Email from CEO scores >0.8, newsletter scores <0.2 |
| 4B.2 | DND awareness — check calendar before push | Nova | 1h | Zero notifications during meetings |
| 4B.3 | Intelligent batching — hourly digest for low-priority | Pulse | 2h | <5 push notifications per day |
| 4B.4 | Meeting prep auto-delivery — 15 min before meetings | ARIA + Knowledge Engineer | 3h | Prep brief arrives for 100% of meetings |

**Key files to create:**
- `jake_brain/notifications.py` — notification manager
- `jake_brain/meeting_prep.py` — auto meeting prep pipeline

---

### PHASE 5A: BOT UNIFICATION + CONVERSATION QUALITY
**Duration:** 1-2 sessions | **Impact:** Mike talks to one Jake, not three bots

| Sub-Phase | Build | Owner | Effort | Success Test |
|-----------|-------|-------|--------|--------------|
| 5A.1 | Single Telegram bot with internal routing (Hermes for fast, Claude CLI for complex) | Atlas + Forge | 4h | Mike uses exactly 1 bot for everything |
| 5A.2 | Conversation state persistence — current chat to jake_working, promote at session end | Knowledge Engineer | 2h | "What did I ask you 10 minutes ago?" works |
| 5A.3 | Selective brain injection — only inject relevant memories per intent type | Atlas + KIRA | 2h | No irrelevant brain results in responses |
| 5A.4 | Error recovery in character — tool failures get Jake-voiced retries | Conversation Designer | 1h | Failed tools get "let me try another way" not raw errors |
| 5A.5 | Genspark channel posting becomes a Jake cron job | Nova | 1h | Genspark bot retired, channel still updated |

**Key changes:**
- Hermes config: unified entry point with router
- Retire Genspark bot as separate entity
- ClaudeBirchBot becomes a backend, not a user-facing bot

---

### PHASE 5B: ACTION EXECUTION (Hands)
**Duration:** 2 sessions | **Impact:** Jake goes from read-only to read-write

| Sub-Phase | Build | Owner | Effort | Success Test |
|-----------|-------|-------|--------|--------------|
| 5B.1 | Action registry pattern: `preview()`, `execute()`, `undo()` | Forge + Atlas | 2h | Registry loaded with 7 action types |
| 5B.2 | Core actions: send_email (Resend API), create_event (osascript), set_reminder (osascript) | Forge | 4h | Each action works standalone |
| 5B.3 | Telegram confirmation flow — preview -> approve/reject inline | Nova + Forge | 3h | Tier 2 actions show preview, respond to tap |
| 5B.4 | Audit trail — every action logged to jake_episodic | Knowledge Engineer | 1h | "What actions did you take today?" returns full list |
| 5B.5 | Action actions: create_github_issue, update_notion, draft_outreach | Forge | 3h | All 7 actions operational |

**Key files to create:**
- `jake_brain/actions/` directory with base class and 7 action implementations
- `jake_brain/actions/registry.py` — action discovery and routing

---

### PHASE 5C: BRAIN QUALITY (Memory Hardening)
**Duration:** 1 session | **Impact:** Fixes the "calendar drowns profile" problem

| Sub-Phase | Build | Owner | Effort | Success Test |
|-----------|-------|-------|--------|--------------|
| 5C.1 | Memory utility scoring: access_freq x recency x uniqueness x downstream_citation | Knowledge Engineer + AI Eval | 2h | Utility scores differentiate high vs low value memories |
| 5C.2 | Automatic nightly consolidation: cluster, promote, archive | Knowledge Engineer | 3h | Runs nightly, stats in morning brief |
| 5C.3 | Entity resolution: merge duplicates, infer relationships | Knowledge Engineer + Algorithm Lab | 2h | "Jacob" / "my son" / "Jacob Rodgers" resolve to 1 entity |
| 5C.4 | Graph-enhanced retrieval: 1-hop traversal on person queries | Atlas | 2h | "Tell me about Jacob" also returns his relationships |
| 5C.5 | Smart calendar dedup: recurring events -> 1 semantic memory | Nova | 1h | 260 standup memories become 1 semantic fact |

**Key changes:**
- Modify `jake_brain_search` RPC for utility-weighted ranking
- New `jake_brain/cluster.py` for memory clustering
- Modify `consolidator.py` for automated nightly runs
- Update `graph.py` for entity resolution

---

### PHASE 6A: PROACTIVE INTELLIGENCE
**Duration:** 1-2 sessions | **Impact:** Jake anticipates, not just responds

| Sub-Phase | Build | Owner | Effort | Success Test |
|-----------|-------|-------|--------|--------------|
| 6A.1 | Brain-assembled morning brief: LLM composes from brain data, not template | ARIA + Knowledge Engineer | 3h | Brief includes 3+ brain-sourced insights |
| 6A.2 | Stale commitment detector: scan episodic for promises, check completion | Steve + AI Eval | 2h | "You said you'd email Ellen by Friday" alert fires |
| 6A.3 | Pattern mining: weekly episodic analysis for recurring themes | Algorithm Lab + AI Eval | 3h | Weekly report identifies 1+ actionable pattern |
| 6A.4 | Cross-company priority sync: unified task ranking from all companies | Steve + Susan | 2h | Single prioritized list across all 3 companies |

---

### PHASE 6B: LEARNING ENGINE
**Duration:** 1 session | **Impact:** Jake stops making the same mistakes

| Sub-Phase | Build | Owner | Effort | Success Test |
|-----------|-------|-------|--------|--------------|
| 6B.1 | Correction capture: "no I meant X" -> procedural memory | AI Eval + Knowledge Engineer | 2h | Corrections stored, retrievable before similar requests |
| 6B.2 | Preference tracking: response format/length/style engagement signals | AI Eval | 2h | Jake adapts response style to what Mike engages with |
| 6B.3 | Routing telemetry: track intent classification -> outcome satisfaction | AI Eval + Pulse | 2h | Weekly routing accuracy report |
| 6B.4 | Consolidation dashboard: nightly stats, weekly learning report | Pulse + ARIA | 1h | Stats appear in morning brief |

---

### PHASE 7+: SECURITY, OBSERVABILITY, VOICE, DELEGATION
**Duration:** 3-5 sessions | **Impact:** Polish and expansion

| Phase | Focus | Duration | Key Deliverable |
|-------|-------|----------|-----------------|
| 7A | Reliability & Health | 1 session | Health check endpoint + daily Telegram report + auto-recovery |
| 7B | Security & Privacy | 1 session | Data sensitivity tags + context boundaries + access audit |
| 8A | Voice & Multi-Modal | 1 session | Voice message transcription + document analysis |
| 8B | Delegation Chains | 1-2 sessions | Multi-step workflow engine + Susan agent dispatch |
| 9 | Family & Network | 1 session | Family member access + cross-device sync |

---

## TEAM MANIFEST

| Susan Agent | Role in 10X Hermes | Phases |
|-------------|-------------------|--------|
| **Atlas** | Architecture decisions, brain search optimization, bot unification | 4A, 5A, 5C |
| **KIRA** | Intent classification, request routing | 4A, 5A |
| **ARIA** | Morning briefs, meeting prep, proactive alerts | 4B, 6A |
| **Steve** | Priority engine, cross-company ranking, stale commitments | 4A, 6A |
| **Nova** | Data engineering, notifications, integrations | 4A, 4B, 5A, 5B |
| **Forge** | Action registry, Telegram flows, engineering execution | 5A, 5B |
| **Knowledge Engineer** | Brain quality, consolidation, entity resolution, context assembly | 4A, 5A, 5B, 5C, 6A, 6B |
| **Pulse** | Monitoring, health checks, telemetry | 4B, 6B, 7A |
| **Sentinel** | Reliability, auto-recovery, error budgets | 7A, 7B |
| **Shield** | Security, PII classification, access controls | 7B |
| **AI Eval** | Correction capture, routing telemetry, quality scoring | 5C, 6A, 6B |
| **Algorithm Lab** | Pattern mining, memory clustering, entity resolution | 5C, 6A |
| **Conversation Designer** | Error recovery UX, personality consistency | 5A |
| **Research Director** | Competitive intel integration, deep research workflows | 8B |
| **Susan** | Orchestration, workflow chains, delegation | 8B |

---

## RISK REGISTER

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Brain quality never improves -- search returns noise | HIGH | CRITICAL | Phase 5C (memory hardening) is non-negotiable before more ingestion |
| Bot unification breaks existing Hermes functionality | MEDIUM | HIGH | Keep Hermes as-is during transition; router wraps, doesn't replace |
| Action execution sends wrong email / creates wrong event | LOW | CRITICAL | 3-tier safety model; all Tier 2+ require confirmation; audit trail |
| Mac dependency makes system fragile | HIGH | MEDIUM | Queue tasks when Mac offline; long-term: cloud Claude API fallback |
| Overbuilding infrastructure vs. fixing UX | HIGH | HIGH | Phase 4A-5A focus on experience first, infrastructure second |
| Memory costs grow unbounded (Voyage AI embeddings) | MEDIUM | MEDIUM | Consolidation + archival keep active memory under 50K |
| Scope creep -- building Phases 7-9 before 4-5 work | HIGH | HIGH | Strict phase gating; no Phase 6+ until Phase 5 success criteria pass |

---

## BUILD SEQUENCE (recommended session order)

```
Session N:   Phase 4A (Spine: intent + priority + brain weighting)     [CRITICAL PATH]
Session N+1: Phase 4B (Smart notifications + meeting prep)             [CRITICAL PATH]
Session N+2: Phase 5A (Bot unification + conversation quality)         [HIGH IMPACT]
Session N+3: Phase 5B (Action execution: email, calendar, reminders)   [HIGH IMPACT]
Session N+4: Phase 5C (Brain quality: consolidation, entity res, dedup)[HIGH IMPACT]
Session N+5: Phase 6A (Proactive intelligence: briefs, patterns)       [MEDIUM]
Session N+6: Phase 6B (Learning engine: corrections, preferences)      [MEDIUM]
Session N+7: Phase 7A (Reliability: health checks, auto-recovery)      [MEDIUM]
Session N+8: Phase 7B (Security: sensitivity tags, boundaries)         [MEDIUM]
Session N+9: Phase 8+ (Voice, delegation, family, network)             [LOW]
```

**Critical path:** Phases 4A -> 4B -> 5A. These three sessions transform Hermes from "cool tech" to "useful assistant." Everything else amplifies these.

---

## SCORING PROJECTION

| Milestone | Est. Score | What Changed |
|-----------|-----------|--------------|
| Current state | 31/100 | Infrastructure built, experience poor |
| After Phase 4 (Spine + Notifications) | 48/100 | Intent routing, priority engine, smart notifications |
| After Phase 5A-5B (Unification + Actions) | 62/100 | One bot, action execution, confirmation flows |
| After Phase 5C (Brain Quality) | 68/100 | Search returns useful results, memory maintained |
| After Phase 6 (Proactive + Learning) | 78/100 | Anticipatory behavior, self-improvement |
| After Phase 7 (Reliability + Security) | 85/100 | Production-grade, self-healing, access controls |
| After Phase 8-9 (Voice + Delegation + Network) | 92/100 | Multi-modal, workflow chains, family access |

**Parity with Mani's ClawBuddy (86/100):** Achievable after Phase 7 (approximately 8 sessions).
**10X from current (meaningful daily utility):** Achievable after Phase 5B (approximately 4 sessions).
