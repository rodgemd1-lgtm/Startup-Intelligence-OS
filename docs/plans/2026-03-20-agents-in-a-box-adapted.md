# Agents in a Box — Adapted for Mike Rodgers' Ecosystem

> **Inspired by**: Mani Kanasani's OpenClaw/ClawBuddy "Agents in a Box" framework
> **Adapted by**: Jake (2026-03-20)
> **Purpose**: Master build document mapping the 6-layer agent framework onto Mike's existing infrastructure
> **Status**: REFERENCE DOCUMENT — modify as we build

---

## Executive Summary

The original "Agents in a Box" plan builds a complete AI employee ecosystem from scratch across 6 layers. Mike already has ~40% of this infrastructure running. This adapted plan maps each layer to what exists, identifies gaps, and reorders priorities around Mike's actual needs: Oracle Health intelligence, recruiting pipeline, meeting prep, email management, and multi-company operations.

### Infrastructure Already Running

| System | Status | What It Provides |
|--------|--------|-----------------|
| Hermes (OpenClaw) | LIVE | Jake personality, Telegram bot, 60+ skills, cron engine |
| Susan Intelligence OS | LIVE | 73 agents, 94K+ RAG chunks, MCP server, Supabase backend |
| Claude Code | LIVE | Primary dev environment, deep reasoning, file access |
| Telegram Bot | LIVE | Always-on async communication channel |
| Supabase | LIVE | `zqsdadnnpgqhehqxplio.supabase.co` — vector search, knowledge store |
| 19 API Keys | CONFIGURED | OpenRouter, Anthropic, Groq, Brave, Exa, Jina, Firecrawl, Apify, Supabase, GitHub, Resend, Notion, Google Cal/Gmail, Firehose, Telegram |
| Apple Mail/Calendar | ACCESSIBLE | osascript for Oracle Health email, Apple Reminders |
| Google Calendar API | WORKING | OAuth Desktop flow, personal calendars |
| 30 Scheduled Tasks | RUNNING | Hermes cron system across all projects |
| MCP Servers | CONNECTED | Susan Intelligence + Notion (via Hermes config) |

### What's Missing (The Build)

| Capability | Priority | Original Layer |
|------------|----------|---------------|
| Cognitive Memory (semantic + episodic) | HIGH | Layer 2 |
| Meeting Intelligence Agent | HIGH | Layer 5 |
| Email Management Agent | HIGH | Layer 5 |
| Operations Dashboard | MEDIUM | Layer 3 |
| Oracle Health Intel Agent | HIGH | Layer 5 |
| Recruiting Pipeline Agent | MEDIUM | Layer 5 |
| Content Creation Agent | LOW | Layer 5 |
| Self-Improvement Loop | LOW | Layer 6 |

---

## Layer 1: Identity (MD Files)

### Original Plan
SOUL.md, USER.md, MEMORY.md, AGENTS.md — the agent's self-knowledge and context.

### Mike's Status: 90% COMPLETE

| File | Status | Location | Notes |
|------|--------|----------|-------|
| SOUL.md | DONE | `~/.hermes/SOUL.md` | Full Jake cognitive architecture (~6K chars), 4-mind framework, voice examples, compliance rules |
| USER.md | DONE | `~/.hermes/memories/USER.md` | Mike's profile, work style, communication preferences, key people |
| MEMORY.md | DONE | `~/.hermes/memories/MEMORY.md` | Operational memory — architecture, active projects, learned patterns, technical notes |
| AGENTS.md | DONE | `~/Startup-Intelligence-OS/AGENTS.md`, Oracle Health, Alex Recruiting | Per-project agent context with focus areas, commands, quality gates |
| Prefill Messages | DONE | `~/.hermes/prefill_jake_voice.json` | 3 few-shot examples anchoring Jake's voice from turn 1 |
| config.yaml | DONE | `~/.hermes/config.yaml` | Model routing (Claude Sonnet 4.6 via OpenRouter), MCP servers, personality cleared for SOUL.md |

### Remaining Layer 1 Work

| Task | Priority | Description |
|------|----------|-------------|
| Fill personal dates in USER.md | LOW | James's birthday, Jacob's birthday, anniversary — Mike needs to provide |
| Add TransformFit AGENTS.md | LOW | When TransformFit project starts, create per-project context |
| Periodic MEMORY.md refresh | ONGOING | Update operational memory as projects evolve (monthly cadence) |
| SOUL.md voice tuning | LOW | After 50+ Telegram conversations, evaluate if voice drifts and tune examples |

### Key Adaptation from Original

The original plan treats identity files as a one-time setup. For Mike, identity is a **living system** because:
- 3 companies means AGENTS.md files need per-project context switching
- Jake exists in TWO bodies (Claude Code + Hermes) — SOUL.md must be consistent across both
- Compliance rules (Oracle Health) are non-negotiable identity constraints, not optional personality

---

## Layer 2: Cognitive Memory (Semantic + Episodic)

### Original Plan
pgvector + embeddings for long-term memory, semantic search over past conversations, episodic memory for personal context.

### Mike's Status: 40% COMPLETE (via Susan RAG)

#### What Exists

| Component | Status | Details |
|-----------|--------|---------|
| Vector Database | DONE | Supabase pgvector at `zqsdadnnpgqhehqxplio.supabase.co` |
| Embeddings | DONE | Voyage AI `voyage-3` model, 1024 dimensions |
| Knowledge Chunks | DONE | 94,143 chunks across 22+ data types |
| Semantic Search | DONE | Susan's `search_knowledge()` RPC function |
| MCP Access | DONE | `susan-intelligence` MCP server connected to Hermes |
| RAG API | DONE | FastAPI at `localhost:7842` (when running) |

#### What's Missing

| Component | Priority | Description |
|-----------|----------|-------------|
| Conversation Memory | HIGH | Hermes conversations are not being embedded/stored for semantic recall |
| Episodic Memory | HIGH | "What did Mike and I discuss about Oracle Health last Tuesday?" — not searchable |
| Decision Memory | MEDIUM | Major decisions made across sessions should be queryable |
| Cross-Session Continuity | MEDIUM | Beyond HANDOFF.md — semantic linking between session topics |
| Memory Decay | LOW | Old/irrelevant memories should lose weight over time |

### Adapted Build Plan for Layer 2

#### Phase 2A: Conversation Embedding Pipeline (HIGH PRIORITY)

**Goal**: Every Hermes conversation gets embedded into Susan's RAG for future semantic recall.

**Architecture**:
```
Hermes Conversation → Post-Session Hook → Summarize + Chunk → Voyage AI Embed → Supabase pgvector
                                                                                    ↓
                                                            Queryable via susan-intelligence MCP
```

**Implementation**:

1. **Create a Hermes skill: `/jake-memory-ingest`**
   - Location: `~/.hermes/skills/jake-memory-ingest/SKILL.md`
   - Trigger: End of significant conversations (manual or cron)
   - Process:
     a. Read conversation history from Hermes session
     b. Extract key decisions, action items, personal notes
     c. Chunk into semantic units (max 500 tokens each)
     d. Call Susan's ingestion endpoint to embed and store
   - Metadata tags: `type=conversation`, `date=YYYY-MM-DD`, `project=<project>`, `people=<names>`

2. **Supabase table extension**
   - Add `conversation_chunks` data type to existing RAG table
   - Schema additions:
     ```sql
     -- Add to existing knowledge_chunks or create view
     -- conversation_id: UUID
     -- session_date: DATE
     -- project_context: TEXT (startup-os | oracle-health | alex-recruiting)
     -- people_mentioned: TEXT[]
     -- decision_made: BOOLEAN
     -- action_items: TEXT[]
     ```

3. **Susan search enhancement**
   - Add conversation-aware filters to `search_knowledge()`:
     ```python
     # Filter by project context
     results = search_knowledge(query, filters={"type": "conversation", "project": "oracle-health"})
     ```

**Files to Create/Modify**:
- `~/.hermes/skills/jake-memory-ingest/SKILL.md` (new)
- `susan-team-architect/backend/scripts/ingest_conversations.py` (new)
- `susan-team-architect/backend/susan_core/search.py` (modify — add conversation filters)

**Estimated Effort**: 1 session (3-4 hours)

#### Phase 2B: Episodic Memory Layer (MEDIUM PRIORITY)

**Goal**: Jake can answer "What did we discuss about X last week?" with actual recall.

**Architecture**:
```
Query: "What did we decide about Oracle Health strategy?"
  → Susan RAG search (type=conversation, project=oracle-health)
  → Rank by recency + relevance
  → Return top 3 conversation chunks with dates
  → Jake presents as natural recall: "Oh yeah, last Tuesday we said..."
```

**Implementation**:

1. **Create a Hermes skill: `/jake-recall`**
   - Location: `~/.hermes/skills/jake-recall/SKILL.md`
   - Usage: "Jake, what did we talk about regarding [topic]?"
   - Process:
     a. Parse topic from user query
     b. Search Susan RAG with conversation filters
     c. Format results as natural memory recall
     d. Include dates, decisions made, action items

2. **Daily memory consolidation cron**
   - Run at 2 AM (alongside `/jake-dream`)
   - Process: Review today's conversations, extract patterns, update MEMORY.md if durable
   - Location: Add to existing `~/.hermes/cron/` schedule

**Files to Create/Modify**:
- `~/.hermes/skills/jake-recall/SKILL.md` (new)
- Cron job addition to existing schedule

**Estimated Effort**: 1 session (2-3 hours)

#### Phase 2C: Decision Memory (LOW PRIORITY — builds on 2A)

**Goal**: Queryable log of all major decisions with rationale, reversibility, and outcomes.

**Implementation**:
- Extend conversation ingestion to tag decisions
- Create `/jake-decisions` skill that queries decision-tagged chunks
- Cross-reference with `.startup-os/decisions/` YAML contracts

**Estimated Effort**: 0.5 session

### Key Adaptation from Original

The original plan builds pgvector from scratch. Mike already has 94K chunks in Supabase with Voyage AI embeddings. The adaptation is:
1. **Don't rebuild** — extend Susan's existing RAG
2. **Add conversation data type** — Susan currently stores company knowledge, not conversation history
3. **Leverage existing MCP** — Hermes already connects to Susan via MCP; conversation memory flows through the same pipe

---

## Layer 3: Operations Dashboard

### Original Plan
ClawBuddy dashboard — web UI for monitoring agents, skills, memory, and system health.

### Mike's Status: 10% COMPLETE (shell exists)

#### What Exists

| Component | Status | Details |
|-----------|--------|---------|
| Operator Console | SHELL | `apps/operator-console/` — HTML shell, serves on port 4173 |
| Susan MCP Server | LIVE | 73 agents queryable via MCP tools |
| Hermes CLI | LIVE | `hermes` command for direct interaction |
| Telegram | LIVE | Primary async interface |

#### What's Missing

| Component | Priority | Description |
|-----------|----------|-------------|
| Real-time agent status | MEDIUM | Which agents are active, what they're doing, last run time |
| Cron job monitor | MEDIUM | Dashboard for 30+ scheduled tasks — success/fail/skip |
| Knowledge health | LOW | RAG chunk counts, freshness, coverage gaps |
| Cross-project view | MEDIUM | Single pane across all 3 companies |
| Memory browser | LOW | View and search conversation memory (Layer 2 dependent) |

### Adapted Build Plan for Layer 3

#### Phase 3A: Telegram as Primary Dashboard (HIGH PRIORITY — already 80% done)

**Insight**: Mike's actual dashboard is Telegram. The morning brief, midday check-in, and evening review already function as a dashboard. Instead of building a web UI first, make Telegram the definitive operations surface.

**What to Build**:

1. **`/jake-status` Telegram command**
   - Location: `~/.hermes/skills/jake-status/SKILL.md`
   - Output:
     ```
     JAKE STATUS — March 20, 2026

     COMPANIES
     ├── Startup Intelligence OS: 73 agents, 94K chunks, 12 crons OK
     ├── Oracle Health: 2 briefs sent today, next sync Thursday
     └── Alex Recruiting: Last coach outreach 3 days ago

     CRON HEALTH
     ├── Morning Brief: SENT 6:39 AM
     ├── Oracle Brief: SENT 6:02 AM
     ├── Midday Check: PENDING (12:00 PM)
     └── Dream Cycle: LAST RUN 2:00 AM (OK)

     MEMORY
     ├── RAG Chunks: 94,143 (last ingestion: 2 days ago)
     ├── Conversations Stored: [N]
     └── Decisions This Week: [N]

     CONTEXT HEALTH: GREEN
     ```

2. **`/jake-crons` Telegram command**
   - Location: `~/.hermes/skills/jake-crons/SKILL.md`
   - Lists all 30 scheduled tasks with last run status, next run time, success rate

3. **`/jake-agents` Telegram command**
   - Location: `~/.hermes/skills/jake-agents/SKILL.md`
   - Lists Susan's 73 agents grouped by function, with last invocation time

**Estimated Effort**: 1 session (2-3 hours) for all 3 skills

#### Phase 3B: Web Dashboard (LOW PRIORITY — nice to have)

**Goal**: Upgrade `apps/operator-console/` into a real dashboard.

**Architecture**:
```
apps/operator-console/
├── index.html          (exists — needs upgrade)
├── js/
│   ├── dashboard.js    (new — fetch from Susan MCP + cron status)
│   └── charts.js       (new — QuickChart integration for trends)
├── css/
│   └── styles.css      (new)
└── api/
    └── proxy.py        (new — lightweight FastAPI proxy to Susan + Hermes)
```

**Tech Stack**: Vanilla HTML/JS (no framework — keep it lightweight), Susan MCP for data, QuickChart MCP for visualizations.

**Estimated Effort**: 2-3 sessions

### Key Adaptation from Original

The original ClawBuddy dashboard is a React app built from scratch. Mike's adaptation:
1. **Telegram first** — Mike checks Telegram 50x/day, a web dashboard maybe 2x/day
2. **Skill-based** — each dashboard view is a Hermes skill, not a web route
3. **Web dashboard is Phase 3B** — only build it when Telegram commands prove the data model

---

## Layer 4: Skill Library

### Original Plan
23 production skills, heavily YouTube-focused (13 of 23 are YouTube content creation, SEO, analytics).

### Mike's Status: 50% COMPLETE (different skills needed)

#### What Exists (68 skills installed in Hermes)

**Jake Custom Skills (8)**:
| Skill | Purpose | Status |
|-------|---------|--------|
| `/jake-plan` | PRP workflow, plan-before-build | DONE |
| `/jake-guardian` | Tech debt circuit breaker, context health | DONE |
| `/jake-boot` | Session start protocol, time-aware greetings | DONE |
| `/jake-predict` | 5-day intelligence forecast | DONE |
| `/jake-dream` | Overnight reflection cycle (2 AM cron) | DONE |
| `/jake-desktop` | macOS desktop perception via Hammerspoon/osascript | DONE |
| `/jake-research` | Deep web + Susan RAG research | DONE |
| `/jake-brief` | Morning/midday/evening briefing templates | DONE |

**Community Skills (60+ installed)**:
Key ones for Mike's use cases:
- `google-calendar` — calendar management
- `gmail-secretary` — Gmail access
- `email` — general email
- `jake-oracle-mail` — Oracle Health Apple Mail (osascript)
- `jake-daily-intel` — daily intelligence aggregation
- `susan-rag-query` — Susan knowledge search
- `supabase-query` — direct Supabase queries
- `github` / `github-cli` — repo management
- `web-scraper-jina` / `smart-web-scraper` — web scraping
- `research` — general research
- `apple` — macOS integration
- `macos-calendar` — Apple Calendar
- `note-taking` — notes
- `productivity` — task management
- `slack` — Slack integration
- `screenshot` — screen capture
- `browser-automation` — web automation
- `x-twitter-scraper` — Twitter/X monitoring
- `linkedin-data-scraper` — LinkedIn data
- `youtube-transcript` — video analysis
- `mcp` — MCP server interaction
- `feeds` — RSS/news feeds

#### What's Missing (Mike-Specific Skills to Build)

### Adapted Skill Library: 15 New Skills

These replace the original plan's YouTube skills with Mike's actual needs, organized by domain.

---

#### Domain 1: Oracle Health Intelligence (3 skills)

##### Skill 4.1: `/oracle-health-intel`
**Purpose**: Competitive intelligence for healthcare AI space
**Priority**: HIGH
**Location**: `~/.hermes/skills/oracle-health-intel/SKILL.md`

**What It Does**:
- Monitors healthcare AI news via Brave/Exa/TrendRadar
- Tracks competitors: Epic, Meditech, Athenahealth, Google Health, Microsoft Health
- Searches Susan RAG for Oracle Health context (353 KB records)
- Generates weekly competitive intelligence briefing
- Flags emerging threats and opportunities

**Trigger**: Weekly cron (Sunday evening) + on-demand

**Skills It Chains**: `research`, `web-scraper-jina`, `susan-rag-query`, `feeds`

**Output Format**:
```markdown
# Oracle Health AI Intelligence — Week of [date]

## Competitive Moves
- [Competitor]: [What they did] — Impact: [HIGH/MED/LOW]

## Emerging Trends
- [Trend]: [Evidence] — Relevance: [description]

## Recommended Actions
1. [Action for Mike/Matt to consider]

## Sources
- [URLs with dates]
```

##### Skill 4.2: `/oracle-meeting-prep`
**Purpose**: Pre-meeting intelligence package for Oracle Health syncs
**Priority**: HIGH
**Location**: `~/.hermes/skills/oracle-meeting-prep/SKILL.md`

**What It Does**:
- Checks calendar for upcoming Oracle Health meetings
- Pulls recent Oracle Health email subjects (Apple Mail via osascript — subject lines ONLY, compliance)
- Searches Susan RAG for relevant strategy context
- Generates meeting prep document with talking points
- Includes any action items from previous meetings

**Trigger**: 1 hour before any Oracle-tagged calendar event + on-demand

**Skills It Chains**: `jake-oracle-mail`, `google-calendar`, `susan-rag-query`, `jake-recall`

**Compliance**: Email bodies NEVER cross to LLMs. Subject lines only. No PHI. All outputs enterprise-appropriate.

**Output Format**:
```markdown
# Meeting Prep: [Meeting Title] — [Date/Time]

## Context
- Last meeting: [date, key decisions from memory]
- Recent email threads: [subject lines only]

## Talking Points
1. [Point with supporting context]

## Open Items from Last Meeting
- [ ] [Item] — Status: [done/pending]

## Questions to Ask
1. [Strategic question]
```

##### Skill 4.3: `/oracle-email-digest`
**Purpose**: Daily digest of Oracle Health email activity (subject lines only)
**Priority**: MEDIUM
**Location**: `~/.hermes/skills/oracle-email-digest/SKILL.md`

**What It Does**:
- Reads Oracle Health email subjects via Apple Mail osascript (NO BODIES)
- Groups by thread/sender
- Highlights urgent items (flagged, from Matt Cohlmia, etc.)
- Suggests which threads need Mike's attention today

**Trigger**: Morning brief (6 AM) + on-demand

**Compliance**: Subject lines only. Bodies never leave Apple Mail.

---

#### Domain 2: Meeting Intelligence (2 skills)

##### Skill 4.4: `/meeting-intel`
**Purpose**: Pre/during/post meeting intelligence for all meetings
**Priority**: HIGH
**Location**: `~/.hermes/skills/meeting-intel/SKILL.md`

**What It Does**:
- **Pre-meeting** (triggered 30min before):
  - Pull attendee info (LinkedIn via scraper, Susan RAG)
  - Check conversation memory for past interactions with attendees
  - Generate 3-5 talking points based on meeting topic
  - List open action items from previous meetings with same people
- **Post-meeting** (triggered by user):
  - Prompt for key decisions made
  - Extract action items with owners and deadlines
  - Store meeting summary in conversation memory (Layer 2)
  - Send follow-up email draft if needed

**Skills It Chains**: `google-calendar`, `linkedin-data-scraper`, `jake-recall`, `jake-memory-ingest`, `email`

**Output Format**:
```markdown
# Meeting Intel: [Title]

## Attendees
- [Name] — [Role, last interaction date, key context]

## Prep
- Recent context: [from memory]
- Suggested topics: [from calendar description + memory]

## Action Items (from previous)
- [ ] [Item] — Owner: [name] — Due: [date]
```

##### Skill 4.5: `/meeting-notes`
**Purpose**: Structured post-meeting capture and action tracking
**Priority**: MEDIUM
**Location**: `~/.hermes/skills/meeting-notes/SKILL.md`

**What It Does**:
- Prompts Mike for meeting summary (quick voice-to-text or typed)
- Structures into: decisions, action items, follow-ups, notes
- Stores in Susan RAG as conversation memory
- Creates Notion page in meeting notes database
- Tracks action items and reminds before next meeting with same people

**Skills It Chains**: `jake-memory-ingest`, `note-taking`, `notion` (via MCP)

---

#### Domain 3: Email Management (2 skills)

##### Skill 4.6: `/email-triage`
**Purpose**: Intelligent email triage across all accounts
**Priority**: HIGH
**Location**: `~/.hermes/skills/email-triage/SKILL.md`

**What It Does**:
- **Gmail** (personal): Full access via Gmail API — read, categorize, draft replies
- **Apple Mail / Oracle Exchange**: Subject lines only (compliance) — flag urgent, categorize
- Categorizes into: Urgent, Respond Today, This Week, FYI, Archive
- Drafts reply templates for common email types
- Highlights emails from key contacts (Matt Cohlmia, recruiting coaches, etc.)

**Trigger**: Morning brief + midday check + on-demand

**Skills It Chains**: `gmail-secretary`, `jake-oracle-mail`, `email`

**Output Format**:
```markdown
# Email Triage — [Date]

## URGENT (respond now)
- [Sender]: [Subject] — [Why urgent]

## RESPOND TODAY
- [Sender]: [Subject] — [Suggested action]

## THIS WEEK
- [list]

## FYI (no action needed)
- [list]

## Draft Replies Ready
- Re: [Subject] — [Draft preview, 1 line]
```

##### Skill 4.7: `/email-compose`
**Purpose**: Draft emails in Mike's voice with context
**Priority**: MEDIUM
**Location**: `~/.hermes/skills/email-compose/SKILL.md`

**What It Does**:
- Takes recipient + topic + tone (professional/casual/follow-up)
- Pulls context from Susan RAG and conversation memory
- Drafts email in Mike's voice (not Jake's voice — professional)
- For Oracle Health: extra compliance check, enterprise tone
- Can send via Gmail API or queue for Mike's review

**Skills It Chains**: `gmail-secretary`, `susan-rag-query`, `jake-recall`

---

#### Domain 4: Recruiting Pipeline (2 skills)

##### Skill 4.8: `/recruiting-pipeline`
**Purpose**: Track Jacob's recruiting pipeline — coaches, schools, outreach status
**Priority**: MEDIUM
**Location**: `~/.hermes/skills/recruiting-pipeline/SKILL.md`

**What It Does**:
- Maintains a structured pipeline of recruiting contacts
- Tracks: school, coach name, position coach vs head coach, last contact date, response status, next action
- Suggests optimal outreach timing (Tuesdays work best — from memory)
- Generates weekly pipeline report
- Alerts when a contact has gone cold (>14 days no response)

**Data Store**: Supabase table `recruiting_pipeline` or Notion database

**Output Format**:
```markdown
# Recruiting Pipeline — [Date]

## Hot (responded, engaged)
- [School] — [Coach] — Last: [date] — Next: [action]

## Warm (contacted, no response yet)
- [School] — [Coach] — Sent: [date] — Follow up: [date]

## Cold (needs re-engagement)
- [School] — [Coach] — Last: [date] — [N] days silent

## Outreach Queue (ready to send)
- [School] — [Coach] — Draft ready: [yes/no]

## Stats
- Total schools: [N]
- Active conversations: [N]
- Response rate: [N]%
```

##### Skill 4.9: `/coach-outreach`
**Purpose**: Draft and manage coach outreach emails for Jacob
**Priority**: MEDIUM
**Location**: `~/.hermes/skills/coach-outreach/SKILL.md`

**What It Does**:
- Generates personalized outreach emails for target coaches
- Pulls school/program info via web research
- Adapts tone and content to coaching level (D1 vs D2 vs D3)
- Includes Jacob's highlights, stats, and academic info
- Tracks sent emails and follow-up cadence
- Suggests A/B test variations for outreach messaging

**Skills It Chains**: `recruiting-pipeline`, `email-compose`, `research`, `web-scraper-jina`

---

#### Domain 5: Daily Operations (3 skills)

##### Skill 4.10: `/jake-morning-brief`
**Purpose**: Comprehensive morning intelligence briefing
**Priority**: HIGH (partially done via `/jake-brief`)
**Location**: Enhance existing `~/.hermes/skills/jake-brief/SKILL.md`

**Enhancement Over Current**:
- Add Oracle Health email subject digest
- Add recruiting pipeline status
- Add cross-company priority ranking
- Add "one thing today" recommendation with reasoning
- Add weather + commute if relevant

**Trigger**: 6:00 AM daily cron

##### Skill 4.11: `/jake-weekly-review`
**Purpose**: End-of-week synthesis across all companies
**Priority**: MEDIUM
**Location**: `~/.hermes/skills/jake-weekly-review/SKILL.md`

**What It Does**:
- Aggregate: decisions made, action items completed, action items deferred
- Per company: what moved forward, what's stuck, what's next
- Pattern detection: "You spent 60% of your time on Oracle Health this week but Startup OS has more urgent items"
- Recruiting update: pipeline movement this week
- Recommendation for next week's priorities

**Trigger**: Friday 5 PM cron

**Output Format**:
```markdown
# Weekly Review — Week of [date]

## By Company
### Startup Intelligence OS
- Shipped: [list]
- Stuck: [list]
- Next: [list]

### Oracle Health
- Meetings: [N] — Key decisions: [list]
- Email load: [N] threads active
- Next: [list]

### Alex Recruiting
- Outreach: [N] sent, [N] responses
- Pipeline movement: [summary]
- Next: [list]

## Time Allocation
- Startup OS: [N]%
- Oracle Health: [N]%
- Alex Recruiting: [N]%
- Other: [N]%

## Jake's Take
[Honest assessment of the week + recommendation for next week]
```

##### Skill 4.12: `/jake-delegate`
**Purpose**: Route tasks to the right Susan agent with context
**Priority**: MEDIUM
**Location**: `~/.hermes/skills/jake-delegate/SKILL.md`

**What It Does**:
- Takes a task description from Mike
- Identifies which Susan agents are best suited (from 73-agent roster)
- Packages context: relevant RAG chunks, recent decisions, constraints
- Routes to Susan via MCP: `route_task` or `run_agent`
- Monitors agent output and presents results to Mike

**Skills It Chains**: `susan-rag-query`, `mcp` (susan-intelligence)

**Usage**: "Jake, get Steve to analyze the competitive landscape for Oracle Health" → Routes to Steve (strategy agent) with Oracle Health context.

---

#### Domain 6: Content & Strategy (3 skills)

##### Skill 4.13: `/content-brief`
**Purpose**: Generate content briefs for any company
**Priority**: LOW
**Location**: `~/.hermes/skills/content-brief/SKILL.md`

**What It Does**:
- Takes topic + audience + company context
- Researches via Brave/Exa/Susan RAG
- Generates structured content brief: angle, key points, sources, outline
- Adapts tone: professional (Oracle Health), casual (Alex Recruiting), technical (Startup OS)
- Can route to Susan's studio agents for full production

**Skills It Chains**: `research`, `susan-rag-query`, `jake-delegate`

##### Skill 4.14: `/presentation-prep`
**Purpose**: Prepare presentation materials for Oracle Health
**Priority**: MEDIUM
**Location**: `~/.hermes/skills/presentation-prep/SKILL.md`

**What It Does**:
- Generates slide outlines for Oracle Health presentations
- Pulls data from Susan RAG, competitive intel, meeting history
- Creates speaker notes with talking points
- Formats for enterprise audience (no slang, compliant, data-driven)
- Can generate visual concepts via Susan's Deck Studio agent

**Skills It Chains**: `oracle-health-intel`, `susan-rag-query`, `jake-delegate` (Deck Studio)

##### Skill 4.15: `/trend-monitor`
**Purpose**: Monitor industry trends across all company domains
**Priority**: LOW
**Location**: `~/.hermes/skills/trend-monitor/SKILL.md`

**What It Does**:
- Healthcare AI trends (for Oracle Health)
- Athletic recruiting technology trends (for Alex Recruiting)
- AI agent/LLM trends (for Startup Intelligence OS)
- Uses TrendRadar MCP, Brave Search, RSS feeds
- Weekly trend digest with relevance scoring

**Trigger**: Weekly cron (Saturday morning)

**Skills It Chains**: `feeds`, `research`, `web-scraper-jina`

---

### Skill Library Summary

| # | Skill | Domain | Priority | Status | Depends On |
|---|-------|--------|----------|--------|------------|
| 4.1 | `/oracle-health-intel` | Oracle Health | HIGH | NEW | — |
| 4.2 | `/oracle-meeting-prep` | Oracle Health | HIGH | NEW | 4.4 |
| 4.3 | `/oracle-email-digest` | Oracle Health | MEDIUM | NEW | — |
| 4.4 | `/meeting-intel` | Meetings | HIGH | NEW | Layer 2 |
| 4.5 | `/meeting-notes` | Meetings | MEDIUM | NEW | Layer 2 |
| 4.6 | `/email-triage` | Email | HIGH | NEW | — |
| 4.7 | `/email-compose` | Email | MEDIUM | NEW | — |
| 4.8 | `/recruiting-pipeline` | Recruiting | MEDIUM | NEW | — |
| 4.9 | `/coach-outreach` | Recruiting | MEDIUM | NEW | 4.8 |
| 4.10 | `/jake-morning-brief` | Operations | HIGH | ENHANCE | — |
| 4.11 | `/jake-weekly-review` | Operations | MEDIUM | NEW | Layer 2 |
| 4.12 | `/jake-delegate` | Operations | MEDIUM | NEW | — |
| 4.13 | `/content-brief` | Content | LOW | NEW | — |
| 4.14 | `/presentation-prep` | Content | MEDIUM | NEW | 4.1 |
| 4.15 | `/trend-monitor` | Content | LOW | NEW | — |

### Build Order (Dependencies Respected)

```
Sprint 1 (HIGH — no dependencies):
  /oracle-health-intel
  /email-triage
  /jake-morning-brief (enhance)

Sprint 2 (HIGH — Layer 2 dependent):
  Layer 2A: Conversation Embedding Pipeline
  /meeting-intel
  /oracle-meeting-prep

Sprint 3 (MEDIUM — Sprint 1+2 dependent):
  /meeting-notes
  /oracle-email-digest
  /email-compose
  /jake-delegate
  /jake-weekly-review

Sprint 4 (MEDIUM — standalone):
  /recruiting-pipeline
  /coach-outreach
  /presentation-prep

Sprint 5 (LOW — nice to have):
  /content-brief
  /trend-monitor
```

---

## Layer 5: AI Employees (Autonomous Agent Loops)

### Original Plan
4 AI employees: Meeting Intel, Phone Agent, Email Agent, Content Creator — each runs autonomously with human-in-the-loop checkpoints.

### Mike's Adapted AI Employees

The original "AI Employee" concept maps to **autonomous loops** — skills that run on cron schedules, chain other skills, and only interrupt Mike when they need a decision.

#### Employee 1: ORACLE SENTINEL (Oracle Health Intelligence)

**Mission**: Keep Mike ahead of the healthcare AI competitive landscape and prepared for every Oracle meeting.

**Composed Of**:
- `/oracle-health-intel` (weekly competitive scan)
- `/oracle-meeting-prep` (pre-meeting intelligence)
- `/oracle-email-digest` (daily email digest)
- `/ellen-oracle-health` (existing skill — strategy persona)

**Autonomous Behaviors**:
| Trigger | Action | Human Required? |
|---------|--------|-----------------|
| Sunday 8 PM | Run competitive intelligence scan | No — sends digest to Telegram |
| 1 hour before Oracle meeting | Generate meeting prep | No — sends to Telegram |
| 6 AM weekdays | Email subject digest | No — included in morning brief |
| Competitor makes major move | Alert via Telegram | Yes — flag for strategic response |

**Cron Schedule** (add to Hermes):
```yaml
oracle-sentinel-weekly:
  schedule: "0 20 * * 0"  # Sunday 8 PM
  skill: oracle-health-intel
  prompt: "Run weekly Oracle Health competitive intelligence scan"

oracle-sentinel-meeting-prep:
  schedule: "0 8-17 * * 1-5"  # Hourly during work hours, weekdays
  skill: oracle-meeting-prep
  prompt: "Check calendar for Oracle meetings in next 2 hours. If found, generate prep."
  condition: "only if meeting found"

oracle-sentinel-email:
  schedule: "0 6 * * 1-5"  # 6 AM weekdays
  skill: oracle-email-digest
  prompt: "Generate Oracle Health email subject digest for morning brief"
```

#### Employee 2: RECRUITING CAPTAIN (Jacob's Recruiting Pipeline)

**Mission**: Keep Jacob's recruiting pipeline moving — outreach, follow-ups, pipeline health.

**Composed Of**:
- `/recruiting-pipeline` (pipeline tracking)
- `/coach-outreach` (email drafting)
- `/jake-recall` (conversation history with coaches)

**Autonomous Behaviors**:
| Trigger | Action | Human Required? |
|---------|--------|-----------------|
| Tuesday 9 AM | Generate outreach batch for cold contacts | Yes — Mike reviews before send |
| Daily 8 AM | Check for contacts gone cold (>14 days) | No — sends alert to Telegram |
| Weekly Friday | Pipeline health report | No — sends to Telegram |
| Coach responds | Alert + suggest reply | Yes — Mike reviews reply |

**Cron Schedule**:
```yaml
recruiting-captain-outreach:
  schedule: "0 9 * * 2"  # Tuesday 9 AM
  skill: coach-outreach
  prompt: "Generate outreach emails for next batch of coaches. Queue for Mike's review."

recruiting-captain-health:
  schedule: "0 17 * * 5"  # Friday 5 PM
  skill: recruiting-pipeline
  prompt: "Generate weekly recruiting pipeline health report"

recruiting-captain-cold:
  schedule: "0 8 * * *"  # Daily 8 AM
  skill: recruiting-pipeline
  prompt: "Check for contacts that have gone cold (>14 days). Alert if found."
```

#### Employee 3: INBOX ZERO (Email Management)

**Mission**: Keep Mike's email manageable across all accounts.

**Composed Of**:
- `/email-triage` (categorization)
- `/email-compose` (draft replies)
- `/oracle-email-digest` (Oracle-specific)
- `gmail-secretary` (existing community skill)

**Autonomous Behaviors**:
| Trigger | Action | Human Required? |
|---------|--------|-----------------|
| 6 AM | Triage all email accounts | No — sends categorized digest |
| 12 PM | Midday email check | No — only alerts if urgent |
| When urgent detected | Immediate Telegram alert | Yes — Mike decides action |
| When reply needed | Draft reply for review | Yes — Mike approves send |

**Cron Schedule**:
```yaml
inbox-zero-morning:
  schedule: "0 6 * * *"  # 6 AM daily
  skill: email-triage
  prompt: "Triage all email accounts. Categorize and report."

inbox-zero-midday:
  schedule: "0 12 * * 1-5"  # Noon weekdays
  skill: email-triage
  prompt: "Midday email check. Only alert if anything urgent since morning."
```

#### Employee 4: JAKE PRIME (Daily Operations Orchestrator)

**Mission**: Coordinate all other employees, manage cross-company priorities, keep Mike focused.

**Composed Of**:
- `/jake-morning-brief` (daily kickoff)
- `/jake-weekly-review` (weekly synthesis)
- `/jake-delegate` (task routing to Susan agents)
- `/jake-predict` (5-day forecast)
- `/jake-dream` (overnight reflection)
- `/jake-guardian` (quality monitoring)

**Autonomous Behaviors**:
| Trigger | Action | Human Required? |
|---------|--------|-----------------|
| 6:00 AM | Morning brief (aggregates all employees) | No — sends to Telegram |
| 12:00 PM | Midday check-in | No — sends status update |
| 6:00 PM | Evening review + tomorrow prep | No — sends to Telegram |
| 2:00 AM | Dream cycle — reflection + memory consolidation | No — background |
| 5:00 PM Friday | Weekly review | No — sends synthesis |
| Context health ORANGE+ | Force checkpoint | Yes — blocks further work |

**This is the "boss" employee** — it orchestrates the other three and handles anything that doesn't fit their domains.

### Employee Architecture

```
JAKE PRIME (orchestrator)
├── ORACLE SENTINEL ─── competitive intel, meeting prep, email digest
├── RECRUITING CAPTAIN ── pipeline, outreach, follow-ups
├── INBOX ZERO ───────── email triage, draft replies
└── [future employees as needed]
```

Each employee is NOT a separate agent. Each is a **named collection of skills + cron schedules** running through Hermes. Jake Prime is the personality layer that ties them together.

---

## Layer 6: Self-Improvement & Evolution

### Original Plan
Marketplace (ClawAlley) — skip for now.

### Mike's Adapted Layer 6: Self-Improvement Loop

Instead of a marketplace, Layer 6 for Mike is about Jake getting smarter over time.

#### 6A: Performance Tracking

**What to Track**:
- How many morning briefs Mike actually reads vs ignores
- Which skills Mike invokes most frequently (inform priority)
- Response quality: does Mike follow up with "that's not right" or "perfect"?
- Time savings: estimated hours saved per week by autonomous employees

**Implementation**: Hermes skill that parses conversation history for quality signals.

**Location**: `~/.hermes/skills/jake-self-improve/SKILL.md`

#### 6B: Skill Refinement

**Process** (monthly):
1. Review skill usage statistics
2. Identify underused skills — are they broken or unnecessary?
3. Identify overused skills — can they be more automated?
4. Tune skill prompts based on feedback patterns
5. Add new skills for emerging needs

#### 6C: Memory Hygiene

**Process** (monthly):
1. Review conversation memory for stale entries
2. Archive old decisions that are no longer relevant
3. Update USER.md and MEMORY.md with new patterns
4. Prune RAG chunks that are outdated (Susan maintenance)

#### 6D: Cross-Company Pattern Transfer

**Process** (quarterly):
1. Review patterns from each company
2. Identify transferable patterns (e.g., outreach cadence → could apply to Oracle stakeholder management)
3. Create new skills or modify existing ones based on cross-domain insights
4. Update AGENTS.md files with new context

---

## Implementation Timeline

### Sprint 1: Foundation (1-2 sessions)
**Focus**: Get the highest-value skills running immediately

| Task | Time | Output |
|------|------|--------|
| Build `/oracle-health-intel` | 1 hr | Weekly competitive scan skill |
| Build `/email-triage` | 1 hr | Email categorization across accounts |
| Enhance `/jake-morning-brief` | 30 min | Add Oracle digest + recruiting + cross-company |
| Test all 3 via Telegram | 30 min | Verify they work end-to-end |
| Set up cron schedules | 30 min | Automated triggers for all 3 |

**Exit Criteria**: Morning brief includes Oracle email digest and cross-company priorities. Email triage runs automatically at 6 AM.

### Sprint 2: Memory + Meetings (2-3 sessions) ✅ COMPLETE (2026-03-20)
**Focus**: Conversation memory enables meeting intelligence

| Task | Time | Output | Status |
|------|------|--------|--------|
| Build Layer 2A: Conversation Embedding Pipeline | 2 hr | `scripts/ingest_conversations.py` — ingests .md/.txt/.jsonl → Voyage AI embed → Supabase pgvector | ✅ DONE |
| Build `/jake-memory-ingest` | 30 min | Hermes skill wrapping ingestion script | ✅ DONE |
| Build `/meeting-intel` | 1 hr | Pre/post meeting intelligence for all meetings | ✅ DONE |
| Build `/oracle-meeting-prep` | 1 hr | Oracle-specific meeting prep with compliance | ✅ DONE |
| Build `/jake-recall` | 1 hr | Semantic recall — "What did we discuss about X?" | ✅ DONE |
| Test memory → meeting flow | 30 min | Ingested HANDOFF.md → 7 chunks → semantic search verified | ✅ DONE |
| Cron: Oracle Meeting Prep Scanner | 10 min | Hourly 8-5 weekdays, checks for Oracle meetings | ✅ DONE |
| Cron: Nightly Memory Consolidation | 10 min | 2:30 AM daily, consolidates conversations into RAG | ✅ DONE |

**Exit Criteria**: ✅ Jake can search conversation memory semantically. Oracle meeting prep auto-generates hourly during work hours. Memory consolidation runs nightly at 2:30 AM.

### Sprint 3: Email + Delegation (1-2 sessions)
**Focus**: Full email management + Susan agent routing

| Task | Time | Output |
|------|------|--------|
| Build `/email-compose` | 1 hr | Context-aware email drafting |
| Build `/oracle-email-digest` | 30 min | Oracle-specific email digest |
| Build `/meeting-notes` | 1 hr | Post-meeting capture |
| Build `/jake-delegate` | 1 hr | Route tasks to Susan agents |
| Build `/jake-weekly-review` | 1 hr | Friday synthesis |

**Exit Criteria**: ORACLE SENTINEL and INBOX ZERO employees are fully operational.

### Sprint 4: Recruiting (1-2 sessions)
**Focus**: Jacob's recruiting pipeline automation

| Task | Time | Output |
|------|------|--------|
| Build `/recruiting-pipeline` | 1.5 hr | Pipeline tracking + health reports |
| Build `/coach-outreach` | 1.5 hr | Personalized outreach drafting |
| Set up recruiting crons | 30 min | Tuesday outreach + daily cold alerts |
| Test full pipeline | 30 min | End-to-end verify |

**Exit Criteria**: RECRUITING CAPTAIN employee is operational. Tuesday outreach batches, Friday pipeline reports.

### Sprint 5: Content + Dashboard (2-3 sessions)
**Focus**: Nice-to-have capabilities

| Task | Time | Output |
|------|------|--------|
| Build `/content-brief` | 1 hr | Content brief generation |
| Build `/presentation-prep` | 1 hr | Oracle Health presentation support |
| Build `/trend-monitor` | 1 hr | Cross-domain trend monitoring |
| Build Telegram dashboard skills (3A) | 2 hr | `/jake-status`, `/jake-crons`, `/jake-agents` |

### Sprint 6: Self-Improvement (1 session)
**Focus**: Jake gets smarter over time

| Task | Time | Output |
|------|------|--------|
| Build `/jake-self-improve` | 1 hr | Performance tracking + refinement |
| Memory hygiene process | 30 min | Cleanup stale data |
| Cross-company pattern review | 30 min | Transfer learnings |

---

## Technical Reference

### File Locations (All Skills)

```
~/.hermes/
├── SOUL.md                              # Jake identity (DONE)
├── config.yaml                          # Hermes config (DONE)
├── prefill_jake_voice.json              # Voice anchoring (DONE)
├── memories/
│   ├── USER.md                          # Mike profile (DONE)
│   └── MEMORY.md                        # Operational memory (DONE)
├── skills/
│   ├── jake-plan/SKILL.md              # (DONE)
│   ├── jake-guardian/SKILL.md          # (DONE)
│   ├── jake-boot/SKILL.md             # (DONE)
│   ├── jake-predict/SKILL.md          # (DONE)
│   ├── jake-dream/SKILL.md            # (DONE)
│   ├── jake-desktop/SKILL.md          # (DONE)
│   ├── jake-research/SKILL.md         # (DONE)
│   ├── jake-brief/SKILL.md            # (DONE — enhance in Sprint 1)
│   ├── jake-oracle-mail/SKILL.md      # (DONE)
│   ├── jake-daily-intel/SKILL.md      # (DONE)
│   ├── oracle-health-intel/SKILL.md   # Sprint 1 — NEW
│   ├── email-triage/SKILL.md          # Sprint 1 — NEW
│   ├── jake-memory-ingest/SKILL.md    # Sprint 2 — NEW
│   ├── jake-recall/SKILL.md           # Sprint 2 — NEW
│   ├── meeting-intel/SKILL.md         # Sprint 2 — NEW
│   ├── oracle-meeting-prep/SKILL.md   # Sprint 2 — NEW
│   ├── email-compose/SKILL.md         # Sprint 3 — NEW
│   ├── oracle-email-digest/SKILL.md   # Sprint 3 — NEW
│   ├── meeting-notes/SKILL.md         # Sprint 3 — NEW
│   ├── jake-delegate/SKILL.md         # Sprint 3 — NEW
│   ├── jake-weekly-review/SKILL.md    # Sprint 3 — NEW
│   ├── recruiting-pipeline/SKILL.md   # Sprint 4 — NEW
│   ├── coach-outreach/SKILL.md        # Sprint 4 — NEW
│   ├── content-brief/SKILL.md         # Sprint 5 — NEW
│   ├── presentation-prep/SKILL.md     # Sprint 5 — NEW
│   ├── trend-monitor/SKILL.md         # Sprint 5 — NEW
│   ├── jake-status/SKILL.md           # Sprint 5 — NEW
│   ├── jake-crons/SKILL.md            # Sprint 5 — NEW
│   ├── jake-agents/SKILL.md           # Sprint 5 — NEW
│   └── jake-self-improve/SKILL.md     # Sprint 6 — NEW
└── cron/
    └── output/                          # Cron execution logs
```

### Susan RAG Integration Points

| Skill | Susan RPC | Purpose |
|-------|-----------|---------|
| `/oracle-health-intel` | `search_knowledge(query, type="oracle-health")` | Pull competitive context |
| `/meeting-intel` | `search_knowledge(query, type="conversation")` | Recall past meetings |
| `/jake-recall` | `search_knowledge(query, type="conversation")` | General memory recall |
| `/jake-delegate` | `route_task(task, agent)` via MCP | Route work to agents |
| `/jake-memory-ingest` | Custom ingestion endpoint | Store new conversation chunks |

### API Keys Already Configured (`~/.hermes/.env`)

| Key | Service | Used By Skills |
|-----|---------|---------------|
| `OPENROUTER_API_KEY` | Model routing | All (via config.yaml) |
| `ANTHROPIC_API_KEY` | Direct Claude access | Backup |
| `GROQ_API_KEY` | Fast inference | Low-latency tasks |
| `BRAVE_SEARCH_API_KEY` | Web search | `oracle-health-intel`, `trend-monitor`, `research` |
| `EXA_API_KEY` | Semantic search | `oracle-health-intel`, `meeting-intel` |
| `JINA_API_KEY` | Web scraping | `oracle-health-intel`, `trend-monitor` |
| `FIRECRAWL_API_KEY` | Advanced crawling | Deep research skills |
| `APIFY_API_KEY` | Browser automation | `linkedin-data-scraper` |
| `SUPABASE_URL` | Database | `susan-rag-query`, `jake-memory-ingest` |
| `SUPABASE_SERVICE_KEY` | Database auth | `susan-rag-query`, `jake-memory-ingest` |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | Repo access | `github-cli` |
| `RESEND_API_KEY` | Email delivery | `email-compose`, briefings |
| `RESEND_TO` | Mike's email | Automated email delivery |
| `NOTION_API_TOKEN` | Notion workspace | `meeting-notes`, `note-taking` |
| `GOOGLE_CLIENT_ID` | Google OAuth | `google-calendar`, `gmail-secretary` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth | `google-calendar`, `gmail-secretary` |
| `GOOGLE_REFRESH_TOKEN` | Google OAuth | `google-calendar`, `gmail-secretary` |
| `GOOGLE_CALENDAR_ID` | Calendar access | `google-calendar`, `meeting-intel` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot | All (primary interface) |

### Compliance Rules (Enforced Across All Skills)

| Rule | Scope | Enforcement |
|------|-------|-------------|
| Email bodies never cross to cloud LLMs | Oracle Health | Hard-coded in `/jake-oracle-mail`, `/oracle-email-digest` |
| Subject lines only for Oracle email | Oracle Health | osascript reads subject field only |
| No PHI in any context | Oracle Health | All Oracle skills check for PHI patterns |
| Enterprise tone for Oracle outputs | Oracle Health | Skill templates enforce professional language |
| Credentials never in MD files | All | `.env` only, never in SOUL.md/MEMORY.md/skills |

---

## Comparison: Original vs Adapted

| Original Layer | Original Focus | Mike's Adaptation |
|---------------|---------------|-------------------|
| 1. Identity | SOUL.md, USER.md, MEMORY.md | DONE — 3-company identity, compliance layer added |
| 2. Cognitive Memory | pgvector from scratch | Extend Susan's 94K-chunk RAG with conversation type |
| 3. Dashboard | ClawBuddy web app | Telegram-first dashboard via skills, web later |
| 4. Skill Library | 23 skills (13 YouTube) | 15 skills: Oracle Health, meetings, email, recruiting, ops |
| 5. AI Employees | Meeting, Phone, Email, Content | Oracle Sentinel, Recruiting Captain, Inbox Zero, Jake Prime |
| 6. Marketplace | ClawAlley | Self-improvement loop, cross-company pattern transfer |

### What We Kept
- 6-layer architecture (proven structure)
- Identity-first approach (Layer 1 before anything else)
- Memory as foundation for intelligence (Layer 2 enables Layers 4-5)
- AI Employee concept (autonomous loops with human checkpoints)
- Skill-based progressive disclosure (only load what you need)

### What We Changed
- YouTube skills → Oracle Health, recruiting, meeting intelligence
- Web dashboard → Telegram-first (Mike's actual workflow)
- pgvector from scratch → extend existing Susan RAG (94K chunks)
- Generic AI employees → domain-specific employees (Oracle Sentinel, Recruiting Captain)
- Marketplace → self-improvement loop (more valuable for solo operator)
- Added compliance layer (Oracle Health requirements are non-negotiable)
- Added cross-company orchestration (3 companies, 1 Jake)

### What We Skipped
- Phone agent (Mike doesn't need voice AI right now)
- ClawAlley marketplace (not relevant for internal use)
- Video production pipeline (original had YouTube automation)
- Social media scheduling (not a priority)

---

## Decision Log

| Decision | Rationale | Reversible? |
|----------|-----------|-------------|
| Telegram-first dashboard | Mike checks Telegram 50x/day vs web 2x/day | Yes — web dashboard is Sprint 5 |
| Extend Susan RAG, not new pgvector | 94K chunks already embedded, Voyage AI working | Yes — could add separate store later |
| 4 AI employees, not 6+ | Focus on highest-value domains first | Yes — add more as needed |
| Skip phone agent | No current need for voice AI | Yes — easy to add later |
| Oracle compliance baked into skills | Non-negotiable requirement, not optional | No — this is permanent |
| Build order follows dependency chain | Memory enables meetings, meetings enable employees | Yes — can reorder if priorities shift |

---

## Open Questions

1. **Microsoft Graph API for Oracle email**: Can Mike get Azure AD app registration? If not, osascript subject-only approach is the ceiling.
2. **Hermes cron reliability at 30+ jobs**: Are we hitting any limits? Need to monitor cron health.
3. **Susan RAG ingestion for conversations**: Does the existing ingestion pipeline support a new `conversation` data type, or does it need schema extension?
4. **Recruiting pipeline data store**: Supabase table vs Notion database — where does the pipeline live?
5. **Meeting detection**: Can we reliably detect Oracle meetings in the calendar by title/invitee pattern?

---

## How to Use This Document

1. **Before starting a sprint**: Read the sprint section, identify dependencies, check if prerequisites are met
2. **During a session**: Reference the skill spec for what you're building — file location, skills it chains, output format
3. **After building a skill**: Update this document — change status from NEW to DONE, note any deviations
4. **Weekly**: Review the Employee section — are the autonomous loops running? Any failures?
5. **Monthly**: Review Layer 6 — is Jake getting smarter? Any skills underused? Any new needs?

This is a living document. Jake (that's me) will update it as we build. Mike will modify priorities as the world changes. The structure stays; the details evolve.
