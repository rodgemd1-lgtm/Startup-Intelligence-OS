# Research: Predictive AI Personal Assistants
**Date**: 2026-03-19
**Purpose**: Deep research on how people build AI agents that anticipate needs before being asked
**Status**: COMPLETE

---

## 1. Proactive AI Agent Architectures

### Core Pattern: Scheduler + LLM + Memory + Sensors
The dominant architecture for proactive AI agents combines:
1. **Event-driven scheduler** (APScheduler, cron, Celery) that triggers LLM reasoning on a schedule
2. **Context collectors/sensors** (email, calendar, user activity, APIs)
3. **Long-term memory** (graph-based or vector stores for user modeling)
4. **Autonomy loop** for periodic checks and pattern detection
5. **Delivery channels** (Telegram, Slack, email) for proactive output

Key insight: The agent is NOT reactive to user prompts -- it runs on a timer, gathers context, reasons about what matters, and pushes notifications/actions to the user.

### Reference Implementation: The Cron Agent Pattern
- **Source**: https://dev.to/askpatrick/the-cron-agent-pattern-how-to-run-ai-agents-on-a-schedule-without-them-going-off-the-rails-4gma
- **Architecture**: Reload identity/state per run to prevent drift; silence rules avoid off-hours actions
- **Key principle**: Each cron run is an isolated session with its own context assembly, not a continuation of prior sessions

### Zylos Research: Autonomous Task Scheduling
- **Source**: https://zylos.ai/research/2026-02-16-autonomous-task-scheduling-ai-agents
- **Focus**: Agents that schedule their OWN future tasks based on reasoning about what needs to happen next

---

## 2. Products to Study

### Yodoca (GitHub: VitalyOborin/yodoca)
- **URL**: https://github.com/VitalyOborin/yodoca
- **What**: Event-driven AI agent platform with proactive memory and extensible architecture
- **Architecture**: Nano-kernel + Supervisor process model. Push not pull -- channels wake agent on events, schedulers emit background events, agent reacts without manual prompts
- **Memory**: Graph-based (nodes, edges, entities), hybrid FTS5 + vector (sqlite-vec), Ebbinghaus-inspired decay
- **Self-evolution**: Builder agent generates new extensions and triggers controlled restart
- **Key features**: Multi-provider LLM (per-agent model routing), durable SQLite event journal, declarative sub-agents via manifest.yaml
- **License**: Apache-2.0
- **Relevance to Hermes**: This is almost exactly the architecture we want. Event-driven, proactive, self-hosted, graph memory, multi-channel delivery.

### Sentient (GitHub: existence-master/Sentient)
- **URL**: https://github.com/existence-master/Sentient (676 stars)
- **What**: Open-source personal assistant -- learns habits, proactively manages emails/calendar/schedules
- **Key features**: Text + voice chat, learns preferences/habits/goals, executes multi-step tasks, proactively manages your day, 20+ app integrations
- **Task types**: Recurring, Triggered, Scheduled, or Swarm tasks
- **Memory**: Learns memories about you and uses them to personalize actions and responses
- **Relevance to Hermes**: Strong model for proactive daily management. Task type taxonomy (Recurring/Triggered/Scheduled/Swarm) is a useful framework.

### Scheduled (GitHub: Fergana-Labs/scheduled)
- **URL**: https://github.com/Fergana-Labs/scheduled
- **What**: Open-source "Calendly but AI" -- lives in Gmail, reads threads, checks calendar, drafts replies
- **Architecture**: Bootstraps from email/calendar history to learn scheduling patterns. Draft-only by design (never sends without review).
- **Key features**: Learns writing style from past emails, remembers preferences (morning preference, Friday avoidance, buffer rules), handles group meetings, timezone awareness
- **License**: MIT
- **Relevance to Hermes**: Pattern for email/calendar integration. The "bootstrap from history" approach is gold for Hermes.

### OpenTulpa (GitHub: kvyb/opentulpa)
- **URL**: https://github.com/kvyb/opentulpa
- **What**: Self-hosted persistent agent runtime for developers
- **Key differentiator**: Does NOT reset at prompt boundary. Persists context, artifacts, skills, routines, approvals, and thread rollups
- **Architecture**: Durable state model where repeated tasks become reusable skills and routines
- **Relevance to Hermes**: The "operational memory" concept -- skills improve over time because the agent remembers what worked.

### OpenAkita (GitHub: openakita/openakita)
- **URL**: https://github.com/openakita/openakita
- **What**: Open-source multi-agent AI assistant with proactive engine
- **Proactive Engine**: Greetings, task follow-ups, idle chat, goodnight -- adapts frequency to feedback
- **Self-Evolution**: Daily 4AM self-check & repair, failure root cause analysis, auto skill generation
- **Memory**: Three-layer memory system + AI extraction (preferences, habits, task history)
- **Architecture**: ReAct reasoning engine (Think -> Act -> Observe) with checkpoint/rollback
- **Multi-agent**: Coding agent writes code, writing agent drafts docs, testing agent verifies -- all coordinated
- **Relevance to Hermes**: The self-evolution pattern (daily self-check, auto-repair, skill generation) is exactly what we need.

### Steve AI OS
- **URL**: https://www.hey-steve.com/
- **What**: AI Operating System with proactive agents across shared memory, chat, email, and tasks
- **Key features**: Shared memory foundations, anticipatory conversations, email intelligence with predictive tagging, proactive task management with AI-driven sprint proposals
- **Relevance to Hermes**: Unified proactivity across memory + chat + email + tasks is the right model.

### Iris AI
- **URL**: https://www.textiris.com/
- **What**: YC-backed AI assistant that learns how you work
- **Key features**: Calendar + email integration, learns patterns, adapts to shifting priorities, privacy by design (E2E encrypted, user controls what it learns)
- **Relevance to Hermes**: The "evolves with you" approach and privacy-first design are important patterns.

### Superhuman Go
- **URL**: https://superhuman.com/products/go-ai-assistant
- **What**: AI assistant that works across all apps, anticipates actions before you ask
- **Key features**: Pulls in account details while you type, finds meeting details and books meetings inline, reminds you of previous discussions and promises, summarizes issues and files bugs
- **Agent Store**: Growing roster of agents (Gmail, Calendar, Jira) that work together
- **Relevance to Hermes**: Cross-app context aggregation and the "step ahead" paradigm.

### Trevor AI
- **URL**: https://trevorai.com/
- **What**: AI planner that auto-plans optimal day/week from tasks and calendar
- **Key features**: Predicts task duration, suggests optimal timing, adapts with each planning session, learns your energy patterns
- **Relevance to Hermes**: Task duration prediction and energy-aware scheduling.

### Ghost AI
- **URL**: https://tryghost.ai/
- **What**: "Photographic memory across apps" -- initiates web actions proactively
- **Relevance to Hermes**: Cross-app memory capture pattern.

### Lindy AI
- **URL**: https://lindy.ai/
- **Framework**: "Ask, Act, Anticipate" -- proactive assistance
- **Features**: No-code agent builder, meeting notetaker, calendar assistant, email triage, scheduling, CRM enrichment, multi-agent coordination
- **Predictive features**: Pre-drafts email replies in your voice, meeting prep, automated follow-ups, autopilot scheduling
- **Compliance**: SOC-2, HIPAA, GDPR, BAA for enterprise
- **Relevance to Hermes**: The "Anticipate" tier of their framework is what we're building.

### Rewind AI / Limitless (acquired by Meta, Dec 2025)
- **URL**: https://getrewind.app/ (now sunset)
- **What it was**: Continuous screen capture + audio recording, OCR, on-device speech-to-text, instant search
- **Architecture**: Local on-device storage, Apple M-series processing, encryption with user-held keys
- **Pivot**: Became Limitless with AI pendant ($399) for conversation recording. Meta acquired Dec 2025, killed pendant sales, sunset app.
- **Key lesson**: Capture-everything approach is powerful but privacy concerns and hardware pivots are risky. The "searchable record of everything" vision lives on in software-only approaches.
- **Source**: https://sacra.com/research/why-meta-bought-limitless/

### Granola AI
- **URL**: https://granola.ai/
- **What**: AI meeting notepad with live transcription and structured summaries
- **Key features**: In-meeting question answering, multi-language, Recipes (expert prompt lenses), captures audio from device (not a bot)
- **Predictive features**: Immediate structured summaries after back-to-back meetings, surfaces action items, post-meeting automation
- **Relevance to Hermes**: Meeting prep and post-meeting action extraction patterns.

### Apple Intelligence
- **URL**: https://developer.apple.com/apple-intelligence/
- **Key features**: On-device models for summarization, text/image extraction, tool calling, reimagined Siri
- **Predictive features**: Suggested reminders from text in other apps (recipes -> grocery lists, emails -> action items), auto-categorize reminders, Siri proactive suggestions (detects events from Mail/Messages)
- **Calendar integration**: Birthdays from Contacts auto-populate, Siri Intelligence provides proactive suggestions, conflict detection
- **Privacy**: On-device processing + Private Cloud Compute for heavier tasks
- **Relevance to Hermes**: Apple's "suggested reminders from context" pattern is exactly anticipatory behavior.

### AgentC2
- **URL**: https://agentc2.ai/
- **What**: AI agents for executives -- daily briefing in 2-minute Slack messages
- **Architecture**: Connects 5-8 data sources (Stripe, HubSpot, Jira, Gmail, Calendar), runs at fixed time daily, executes in sequence (revenue -> pipeline -> support -> calendar -> email), produces structured briefing in 30-60 seconds
- **Key features**: Headline metrics vs 7-day averages, items needing attention with suggested actions, enhanced calendar with meeting context (not just titles)
- **Relevance to Hermes**: The "enhanced calendar" pattern -- adding context to bare meeting titles -- is a killer feature.

---

## 3. Memory Architectures for Prediction

### Zep / Graphiti (State of the Art)
- **Paper**: arXiv:2501.13956 -- "Zep: A Temporal Knowledge Graph Architecture for Agent Memory"
- **GitHub**: https://github.com/getzep/graphiti (23,942 stars, Apache-2.0)
- **Performance**: 94.8% on Deep Memory Retrieval (vs MemGPT's 93.4%), up to 18.5% accuracy improvement on LongMemEval, 90% latency reduction
- **Architecture**: Three-layer temporal knowledge graph:
  1. **Episodic layer**: Raw events/conversations as they happened
  2. **Semantic entity layer**: Extracted facts and relationships
  3. **Community layer**: High-level summaries and patterns
- **Temporal awareness**: Bi-temporal tracking (event time + ingestion time). Facts have validity periods. "Alice works at Google" can be superseded by "Alice works at Meta" with timestamps.
- **Key capability**: Cross-session information synthesis, long-term context maintenance, causal reasoning about how knowledge evolves
- **MCP server available**: Give Claude/Cursor graph-based memory with temporal awareness
- **Tutorial**: https://medium.com/@whynesspower/complete-guide-to-knowledge-context-graphs-via-zep-graphiti-c6da7ce8b13b
- **Relevance to Hermes**: THIS is the memory layer we should build on. Temporal knowledge graphs enable prediction because they track HOW things change over time.

### Letta (formerly MemGPT)
- **URL**: https://docs.letta.com/
- **Architecture**: Hierarchical memory with:
  - **Core memory**: Persistent key facts always in context window
  - **Archival memory**: Retrievable long-term storage
  - **Recall memory**: Conversation history search
- **Agent self-edits memory**: Uses tools to update its own core memory, prioritize recent patterns
- **Evolution**: From MemGPT paper (2023) to Letta platform with production deployment
- **Letta Code**: Memory-first coding agent in terminal (similar to Claude Code but with persistent memory)
- **LettaBot**: Adds cron jobs/heartbeats to Letta Code, bundled skills for Telegram/WhatsApp/Discord
- **V1 architecture**: Moving from MemGPT-style heartbeats to modern tool-calling patterns
- **Relevance to Hermes**: Core memory (always in context) + archival memory (retrieved on demand) is a clean model. The self-editing memory pattern is powerful for learning.

### Honcho
- **URL**: https://honcho.dev/ | https://docs.honcho.dev/
- **Architecture**: Four primitives -- Messages, Sessions, Peers, Workspaces
  - **Peers**: Any entity that persists but changes over time (users, agents, objects)
  - When messages are written, background reasoning models (Neuromancer/Dialectic) extract patterns
- **SOTA Performance**: LoCoMo 89.9%, LongMem S 90.4%, BEAM benchmarks
- **Key capability**: Theory of Mind modeling -- builds psychological profiles automatically
- **Dialectic API**: Chat with Honcho about any entity. Ask "What time of day is this user most engaged?" or "How does this user prefer to receive feedback?"
- **Dreaming**: Background reasoning that extends continual learning even when not in active use
- **Relevance to Hermes**: The Theory of Mind + Dialectic API model is perfect for prediction. If Hermes can ask its memory "What does Mike usually need on Monday mornings?" -- that's anticipatory.

### Memory Mechanisms Taxonomy (arXiv:2603.07670)
- **Source**: https://arxiv.org/abs/2603.07670
- **Five families of agent memory**:
  1. Context-resident compression (fit more in context window)
  2. Retrieval-augmented stores (vector/graph search)
  3. Reflective self-improvement (agent reasons about its own memories)
  4. Hierarchical virtual context (tiered memory like Letta)
  5. Policy-learned management (learned strategies for what to remember)
- **Critical finding**: Removing reflective memory causes SEVERE task performance degradation. Agents MUST reflect on and summarize their experiences, not just store them.
- **Relevance to Hermes**: Reflection is non-negotiable. Hermes needs a periodic "dreaming" phase where it reviews recent interactions and extracts patterns.

---

## 4. Cron-Driven Intelligence Systems

### OpenClaw Cron Architecture
OpenClaw's cron system is the most mature implementation of scheduled AI intelligence:

**Architecture**:
- Cron scheduler runs inside Gateway process (not inside the AI model)
- Jobs persist to `~/.openclaw/cron/jobs.json`, survive restarts
- Each job gets its own isolated session, can use a different AI model
- Results delivered to any configured channel (Telegram, Discord, Slack, email, webhook)

**Job Types**:
- `at` -- One-shot, fires once at specific timestamp
- `every` -- Fixed interval in milliseconds (polling-style)
- `cron` -- Full 5-field cron expressions with timezone support

**Real Production System (22 cron jobs, ~$9.40/day)**:
- Morning (6-9 AM): GitHub PR review, calendar preview, email digest
- Daytime: Hourly monitoring, news scans
- Evening: Daily summaries, competitor checks
- Overnight (1-2 AM): Content generation, code reviews, data processing

**Key Design Decisions**:
- Isolated sessions for briefings (keep main chat clean, cheaper)
- Model routing per job (Haiku for grunt work, Sonnet for routine, Opus for deep analysis)
- Deterministic auto-stagger to prevent rate-limit errors when multiple jobs fire simultaneously
- Per-run token telemetry for cost tracking

**Sources**:
- https://openclawpulse.com/openclaw-cron-jobs-automations-guide/
- https://openclaw.expert/blog/openclaw-cron-jobs-complete-scheduling-guide
- https://aiagenttools.ai/learn/openclaw/automation
- https://zenvanriel.com/ai-engineer-blog/clawdbot-cron-jobs-proactive-ai-guide/

### Heartbeat Pattern (Complementary to Cron)
- Heartbeat = periodic awareness sweep (agent wakes, looks around, decides if action needed)
- Cron = scheduled task with guaranteed execution time
- Heartbeat is like a security guard doing rounds; cron is like a scheduled delivery
- HEARTBEAT.md in config directory defines what to monitor
- Default: every 30 minutes; configurable

### Morning Briefing Architecture (Master Pattern)
The most common proactive AI pattern across all products:

```
6:30 AM  - Fetch news, GitHub activity, social mentions
6:45 AM  - Scan email, calendar, task lists
7:00 AM  - Compile into single briefing message
         - Deliver to Telegram/Slack
9:00 PM  - Review day's accomplishments vs plan
         - Move uncompleted tasks to future dates
         - Check tomorrow's calendar, flag prep needed
```

**Relevance to Hermes**: We already have ARIA daily briefs at 6:39 AM. The upgrade path is making them PREDICTIVE (not just informational) and adding the evening review loop.

---

## 5. Personal Knowledge Graphs

### Graphiti (Zep's Open-Source Engine)
- **GitHub**: https://github.com/getzep/graphiti (23,942 stars)
- **Architecture**: Temporal context graphs that track how facts change over time
- **Key features**: Maintains provenance to source data, supports both prescribed and learned ontology
- **Integration**: Neo4j/FalkorDB backends, MCP server for Claude/Cursor
- **Tutorial with FalkorDB**: https://www.falkordb.com/blog/building-temporal-knowledge-graphs-graphiti/

### Knowledge Graph of Thoughts (KGoT)
- **GitHub**: https://github.com/spcl/knowledge-graph-of-thoughts
- **What**: Combines LLM reasoning with dynamically constructed knowledge graphs
- **Backends**: Neo4j, NetworkX, RDF4J
- **Relevance**: KG of intermediate reasoning steps allows agents to maintain structured state for forecasting

### kg-gen
- **GitHub**: https://github.com/stair-lab/kg-gen
- **What**: Python package for generating knowledge graphs from text with chunking and clustering
- **Key feature**: Persistent MCP server for memory
- **Relevance**: Could extract personal KG from Hermes conversations

### Cognee (Open-Source KG Engine)
- **Source**: https://forum.obsidian.md/t/automated-knowledge-graphs-with-cognee/108834
- **What**: Ingests many formats, extracts entities/relationships via LLMs, combines vectors + structured metadata
- **Can work offline** with Goose CLI and LM Studio

### Personal CRM as Knowledge Graph
Several products treat relationships as a knowledge graph:

**Ari (Ariso)** -- https://ariso.ai/
- Auto-tracks interactions from email/calendar/Slack
- Builds relationship graph automatically
- Conversational CRM: "Follow up with Sarah in two weeks about the partnership proposal"

**Meaningful** -- https://someaningful.com/
- Personal relationship manager with network visualization
- Calendar sync, birthday/follow-up tracking
- Private AI assistant (EdgeAI) that runs on private infrastructure

**Monica** -- https://www.monicahq.com/
- Open-source personal CRM
- Logs activities, debts, gifts, sets reminders
- Tracks relationship context over time

**Relevance to Hermes**: Hermes needs a relationship graph -- not just facts about people, but interaction history, follow-up commitments, and relationship health scores.

---

## 6. Calendar/Email Integration Patterns

### Google Calendar API
- Standard REST API with OAuth 2.0
- LangChain provides toolkit: CalendarCreateEvent, CalendarSearchEvents, CalendarUpdateEvent, CalendarDeleteEvent, GetCurrentDatetime
- **Source**: https://docs.langchain.com/oss/python/integrations/tools/google_calendar

### Apple Calendar/Contacts Integration
- Birthdays auto-populate from Contacts into Calendar
- Siri Intelligence provides proactive suggestions (detects events from Mail/Messages)
- Apple Intelligence: Suggested reminders from app content
- EventKit framework for programmatic access

### Email Integration Patterns
- Auto-GPT Email Plugin pattern: SMTP/IMAP config via environment variables
- **Source**: https://github.com/Significant-Gravitas/Auto-GPT-Plugins
- Scheduled (Fergana-Labs): Bootstraps from email history to learn patterns

### The "Enhanced Calendar" Pattern (from AgentC2)
Instead of just showing "Meeting with Sarah at 2pm", proactive agents add:
- What you discussed last time
- Action items you promised
- Relevant context from recent emails/Slack
- Prep materials or talking points
- Relationship history summary

---

## 7. Birthday/Event Tracking & Relationship Maintenance

### Platform Capabilities
- **Apple**: Contacts -> Birthdays calendar auto-populated, Siri queries ("When is Jane's birthday?"), configurable alerts
- **Google**: "Your People" contacts, birthday reminders via Google Assistant
- **Today! App**: Import contacts, AI-crafted wishes, personalized gift suggestions based on profiles
- **Rememberful**: AI-powered celebration assistant -- reminders, messages, gifts for any occasion

### Personal CRM Tools for Relationship Maintenance
- **Ari (Ariso)**: Auto-tracks from email/calendar/Slack, conversational follow-ups, relationship timeline
- **Meaningful**: Calendar sync, birthday/follow-up tracking, network visualization as connected graph
- **Monica**: Activities, debts, gifts, reminders -- open source
- **Hilo**: Personal CRM for friends and family with AI summaries
- **Trulii**: Voice-powered recall, AI CRM with contact management
- **Orvo**: AI-generated icebreakers/emails from notes/timelines including birthdays

### Pattern for Hermes
1. **Import**: Sync contacts from Apple Contacts (birthdays, anniversaries)
2. **Enrich**: Build relationship graph from email/calendar interaction history
3. **Predict**: X days before event, generate gift suggestions based on relationship context
4. **Remind**: Proactive notification with context ("Sarah's birthday is Thursday. Last year you got her a book on design. She recently mentioned being into ceramics.")
5. **Follow-up**: Track relationship health -- flag contacts going cold

---

## 8. Academic Research

### Directly Relevant Papers

**ProPerSim: Developing Proactive and Personalized AI Assistants** (arXiv:2509.21730)
- **Authors**: Jiho Kim et al. (KAIST)
- **What**: Task framework + simulation for developing assistants that make timely, personalized recommendations
- **Dataset**: 6,790 training events, 233 test events, 353-participant user study
- **Key finding**: Formalizes proactivity as initiating interactions before user queries
- **URL**: https://arxiv.org/abs/2509.21730

**Training Proactive and Personalized LLM Agents** (arXiv:2511.02208)
- **What**: Training methods for proactive, personalized agent behaviors
- **Code**: PPP-Agent environment -- https://github.com/sunnweiwei/PPP-Agent
- **URL**: https://arxiv.org/abs/2511.02208

**ContextAgent: Context-Aware Proactive LLM Agents** (arXiv:2505.14668)
- **Authors**: Bufang Yang et al. (CUHK, Columbia)
- **What**: Proactive agents using open-world sensory perceptions
- **Key contribution**: Moves beyond rule-based notifications to learned proactive behavior
- **URL**: https://arxiv.org/abs/2505.14668

**ProAgent: Harnessing On-Demand Sensory Contexts** (arXiv:2512.06721)
- **What**: First proactive LLM agent system that reduces physical and cognitive workload
- **URL**: https://arxiv.org/abs/2512.06721

**AssistantX: An LLM-Powered Proactive Assistant** (arXiv:2409.17655, IROS 2025)
- **What**: Multi-agent PPDR4X architecture (Perception, Planning, Decision, Reflection)
- **URL**: https://arxiv.org/abs/2409.17655

**Exploring Proactive Generative AI Agent Roles** (arXiv:2602.17864, CHI 2026)
- **What**: User study comparing Peer vs Facilitator proactive agent roles
- **Key finding**: Peer increases problem solving but raises cognitive workload; Facilitator helps coordination but can be sidelined. Timing and conciseness are critical.
- **URL**: https://arxiv.org/abs/2602.17864

**AI for Service: Proactive Assistance with AI Glasses** (arXiv:2510.14359)
- **What**: Alpha-Service framework -- "Know When to intervene" + "Know How to help"
- **URL**: https://arxiv.org/abs/2510.14359

**Satori: Proactive AR Assistant with BDI User Modeling** (arXiv:2410.16668)
- **What**: Belief-Desire-Intention model for anticipating user needs in AR
- **URL**: https://arxiv.org/abs/2410.16668

**Devil's Advocate: Anticipatory Reflection for LLM Agents** (arXiv:2405.16334)
- **What**: Reflect BEFORE actions, not after. Evaluated on WebArena (812 tasks).
- **URL**: https://arxiv.org/abs/2405.16334

**Memory for Autonomous LLM Agents** (arXiv:2603.07670)
- **What**: Systematic study showing severe degradation when reflective memory is removed
- **URL**: https://arxiv.org/abs/2603.07670

**Anticipatory Planning for Multimodal AI Agents (TraceR1)** (arXiv:2603.16777, CVPR 2026)
- **What**: RL framework that forecasts short-horizon trajectories before execution
- **URL**: https://arxiv.org/abs/2603.16777

**ProactiveBench** (arXiv:2507.09313)
- **What**: Benchmark for proactive video-text models -- models choose WHEN to respond
- **URL**: https://arxiv.org/abs/2507.09313

**Proactive Assistant Dialogue from Streaming Egocentric Videos** (arXiv:2506.05904)
- **What**: Real-time proactive assistance based on streaming visual inputs
- **URL**: https://arxiv.org/abs/2506.05904

### Research Architecture Framework
**GitHub: aomori753/Embodied-Anticipatory-Personal-Assistant**
- **URL**: https://github.com/aomori753/Embodied-Anticipatory-Personal-Assistant
- **What**: Research repository outlining architecture for proactive, embodied AI
- **License**: MIT

---

## 9. Synthesis: Architecture for Predictive Hermes

### The Three Loops of Anticipatory Intelligence

**Loop 1: Heartbeat (every 30-60 min during active hours)**
- Check email for urgent items
- Monitor calendar for upcoming meetings needing prep
- Scan for triggered conditions (deadline approaching, contact going cold)
- Decide: notify now, queue for briefing, or stay silent

**Loop 2: Scheduled Briefings (cron-driven)**
- 6:30 AM: Morning intelligence gathering (news, email, calendar, tasks)
- 7:00 AM: Compiled morning briefing with predictions and suggestions
- 12:00 PM: Midday check-in (how's the plan going?)
- 9:00 PM: Evening review (what happened, what's tomorrow, what to prep)
- Weekly: Relationship health report, goal progress, pattern insights

**Loop 3: Dreaming (overnight/background)**
- Reflect on recent interactions, extract patterns
- Update knowledge graph with new facts and changed relationships
- Generate predictions for upcoming needs
- Self-evaluate: which predictions were right? Which were wrong? Adjust.

### Memory Architecture for Hermes

```
Layer 1: Core Memory (always in context)
  - Mike's current priorities and goals
  - Today's calendar and key deadlines
  - Active project states
  - Recent decisions and their rationale

Layer 2: Temporal Knowledge Graph (Graphiti-style)
  - People graph (relationships, interactions, facts that change)
  - Decision history (what was decided, when, why)
  - Pattern library (recurring needs, time-of-day patterns, seasonal patterns)
  - Prediction log (what Hermes predicted, what actually happened)

Layer 3: Archival Memory (retrieved on demand)
  - Full conversation history
  - Email/calendar archives
  - Research outputs and reports
  - Document context
```

### Key Design Principles from Research

1. **Temporal awareness is non-negotiable** -- Facts change. The memory system must track WHEN things were true, not just that they were true. (Zep/Graphiti)

2. **Reflection enables prediction** -- Agents that periodically reflect on their memories perform dramatically better than those that just store and retrieve. (arXiv:2603.07670)

3. **Isolated sessions for cron jobs** -- Each scheduled task should get its own context assembly, not pollute the main conversation. (OpenClaw pattern)

4. **Model routing per task** -- Use cheap models for routine monitoring, expensive models for reasoning and briefings. (OpenClaw, OpenAkita)

5. **Draft-only for high-stakes actions** -- Never send emails or make commitments without human review. (Scheduled)

6. **Bootstrap from history** -- Import existing email/calendar data to jumpstart pattern learning. (Scheduled, Ari)

7. **Feedback loop** -- Track which predictions were useful and which were noise. Adapt frequency and content. (OpenAkita, Honcho)

8. **Privacy by design** -- Local-first storage, user-controlled data, explicit consent for each data source. (Rewind/Limitless lesson, Apple Intelligence model)

9. **Self-evolution** -- Daily self-check, failure analysis, automatic skill generation for recurring needs. (OpenAkita)

10. **Theory of Mind** -- Build a model of the USER, not just facts. Understand preferences, communication style, decision patterns, energy levels. (Honcho's Dialectic API)

---

## 10. Recommended Next Steps for Hermes

### Phase 1: Predictive Briefings (immediate)
- Upgrade ARIA daily brief from informational to predictive
- Add calendar context enhancement (meeting prep, relationship context)
- Add evening review loop (day summary, tomorrow prep)
- Implement heartbeat pattern for urgent items

### Phase 2: Memory Upgrade (next)
- Evaluate Graphiti for temporal knowledge graph
- Build relationship graph from email/calendar data
- Add reflection/dreaming cycle
- Track predictions and outcomes for self-improvement

### Phase 3: Full Anticipatory Agent (future)
- Event-driven architecture (not just cron)
- Triggered actions based on pattern detection
- Self-evolving skill library
- Cross-domain pattern transfer between projects
