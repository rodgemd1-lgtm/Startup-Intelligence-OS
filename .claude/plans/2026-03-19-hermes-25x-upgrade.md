# Hermes 25x Upgrade Plan — Jake-Level Intelligence

**Date**: 2026-03-19
**Project**: Hermes Agent Optimization
**Goal**: Transform Hermes from a basic chat agent into a Jake-caliber co-founder with context health monitoring, adaptive effort routing, self-improvement, and proactive intelligence
**Status**: PLAN — Awaiting approval

---

## Part 1: What Jake Has That Hermes Doesn't (The Gap)

### Category A: Context & Session Intelligence
| # | Jake Capability | Hermes Current State | Gap Severity |
|---|----------------|---------------------|-------------|
| A1 | Context health monitoring (6 signals: file scatter, arch drift, repeated reads, error accumulation, scope creep, silent work) | None — runs until it crashes or hits token limit | CRITICAL |
| A2 | Context budget estimation before tasks | None — blindly consumes tokens | CRITICAL |
| A3 | Alert levels (GREEN/YELLOW/ORANGE/RED) with escalating responses | Basic compression at 85% threshold | HIGH |
| A4 | Session boundary protocol (auto-handoff when ORANGE/RED) | Session reset after 24h idle or at 4 AM | MEDIUM |
| A5 | Boot sequence (5-step silent orient → informed greeting) | Loads SOUL.md + memories, generic start | HIGH |

### Category B: Reasoning & Effort Control
| # | Jake Capability | Hermes Current State | Gap Severity |
|---|----------------|---------------------|-------------|
| B1 | 4-tier effort routing (low/medium/high/max) with task classification | Fixed `reasoning_effort: medium` for everything | CRITICAL |
| B2 | `ultrathink` keyword for single-turn deep reasoning | Not supported | HIGH |
| B3 | Task classification before every task (announces effort level) | No classification — same effort for "what time is it" and "redesign the architecture" | CRITICAL |
| B4 | Smart model routing by TASK COMPLEXITY (not just message length) | Smart routing by character/word count only (≤160 chars → cheap model) | HIGH |

### Category C: Planning & Discipline
| # | Jake Capability | Hermes Current State | Gap Severity |
|---|----------------|---------------------|-------------|
| C1 | Plan-before-build enforcement (hard gate) | No planning gate — executes immediately | CRITICAL |
| C2 | Trigger phrase detection ("wouldn't it be great if...") | None | MEDIUM |
| C3 | Parking lot for ideas (captured, deferred, reviewed later) | None — ideas either executed or lost | HIGH |
| C4 | PRP workflow (INITIAL.md → research → blueprint → execute → validate) | None | HIGH |

### Category D: Quality & Debt Tracking
| # | Jake Capability | Hermes Current State | Gap Severity |
|---|----------------|---------------------|-------------|
| D1 | Technical debt circuit breaker (score tracking, auto-trips at 31+) | None | HIGH |
| D2 | Feature-to-Quality Ratio tracking (FQR) | None | MEDIUM |
| D3 | Quality gates at build milestones (10/25/50/75/90/100%) | None | HIGH |
| D4 | Confidence tiers on every output (AUTO/DRAFT/FLAG) | None | MEDIUM |

### Category E: Personality & Relationship
| # | Jake Capability | Hermes Current State | Gap Severity |
|---|----------------|---------------------|-------------|
| E1 | Four cognitive modes (Strategist/Challenger/Guardian/Executor) | Single mode — helpful assistant | HIGH |
| E2 | Hard pushback on bad ideas (Challenger mind) | Agrees with everything | CRITICAL |
| E3 | Proactive personal memory (Jacob, music, schedule, pet peeves) | Basic MEMORY.md + USER.md — reactive only | HIGH |
| E4 | Cross-project awareness (3 companies, pattern transfer) | Single-session, no cross-project | HIGH |
| E5 | Intent prediction (time of day, recent activity, project state) | None | MEDIUM |

### Category F: Multi-Agent & Research
| # | Jake Capability | Hermes Current State | Gap Severity |
|---|----------------|---------------------|-------------|
| F1 | 73 Susan agents + 112 wshobson agents available for dispatch | Delegation with MAX_DEPTH=2, MAX_CONCURRENT=3, limited toolsets | HIGH |
| F2 | 16 MCP servers (research, competitive intel, knowledge, dev tools) | Terminal + file + web + delegate | HIGH |
| F3 | Structured handoff protocol (machine-readable) | Session DB with compression | MEDIUM |

---

## Part 2: The 25x Upgrade Architecture

### Philosophy
Jake's power comes from **SOUL.md + skills + cron jobs**. We can't modify Hermes's core Python code (it's a third-party agent), but we CAN:
1. **Rewrite SOUL.md** with Jake's full cognitive architecture (personality, modes, rules)
2. **Create custom skills** that implement Jake's discipline systems
3. **Set up cron jobs** for proactive monitoring and self-improvement
4. **Optimize config.yaml** for intelligent model routing
5. **Build memory templates** that structure what Hermes learns

### The 25x Stack

```
┌─────────────────────────────────────────────────┐
│  L5: SELF-IMPROVEMENT LOOP                       │
│  Cron: learning extraction, memory consolidation │
│  Skills: /learn, /evolve                         │
├─────────────────────────────────────────────────┤
│  L4: MULTI-AGENT DISPATCH                        │
│  Skills: /research, /team, /audit                │
│  Config: delegation model routing                │
├─────────────────────────────────────────────────┤
│  L3: QUALITY & DISCIPLINE LAYER                  │
│  Skills: /plan, /gate, /debt-check               │
│  SOUL.md: plan enforcement, debt tracking        │
├─────────────────────────────────────────────────┤
│  L2: CONTEXT & EFFORT INTELLIGENCE               │
│  Config: smart routing by complexity             │
│  SOUL.md: effort classification, context health  │
├─────────────────────────────────────────────────┤
│  L1: IDENTITY & RELATIONSHIP                     │
│  SOUL.md: Jake personality, 4 minds, pushback    │
│  Memory: Mike profile, cross-project awareness   │
└─────────────────────────────────────────────────┘
```

---

## Part 3: Implementation Plan (5 Phases)

### Phase 1: Fix & Stabilize (Session 1 — NEXT SESSION)
**Goal**: Get Hermes working reliably before adding intelligence

- [x] **1.1** Force Anthropic provider routing (skip Azure) — `provider_routing.order: ["Anthropic"]` ✅ DONE
- [x] **1.2** Fix personality (was set to `kawaii`, changed to `helpful`) ✅ DONE
- [ ] **1.3** Test the fix — run Hermes, confirm no more 400 errors on multi-turn
- [ ] **1.4** Grant macOS permissions — Calendar, Mail, Contacts for python3/Terminal
- [ ] **1.5** Set up launchd plist for always-on Telegram gateway
- [ ] **1.6** Verify all 29 custom skills load and execute
- [ ] **1.7** Run the self-diagnostic prompt from the previous handoff

**Validation**: Hermes completes a 10+ turn conversation without API errors

### Phase 2: Rewrite SOUL.md — Jake's Full Brain (Session 1-2)
**Goal**: Transform Hermes from generic assistant to Jake

#### 2.1 — New SOUL.md Structure
```markdown
# Jake — Co-Founder Intelligence

## Identity (who you are)
## Four Minds (Strategist/Challenger/Guardian/Executor)
## Context Health Protocol (6 signals, 4 alert levels)
## Effort Classification (auto-classify every task)
## Plan Gate (NEVER code without a plan)
## Debt Tracking (running score, circuit breaker)
## Quality Gates (milestone-based checks)
## Confidence Tiers (tag every output)
## Memory Protocol (what to capture, what to skip)
## Cross-Project Awareness (3 companies)
## Session Protocol (boot → work → handoff)
## What Jake Never Does (anti-patterns)
```

Key additions to SOUL.md:
- **Effort classification rules** — Hermes can't change its own `reasoning_effort` mid-session, but it CAN:
  - Announce the effort level it WOULD use
  - Adjust response depth/thoroughness based on classification
  - Use delegation for heavy reasoning tasks (delegate to Opus via OpenRouter)
- **Context health as behavioral rules** — "If you've processed >15 messages without a summary, stop and summarize"
- **Challenger mind as hard rule** — "Before agreeing with ANY major decision, present the strongest counter-argument"
- **Plan gate as refusal** — "If the user asks you to build something with >3 steps, REFUSE until a plan exists"

#### 2.2 — Config Optimizations
```yaml
# Smarter model routing — classify by task, not just message length
smart_model_routing:
  enabled: true
  max_simple_chars: 200
  max_simple_words: 35
  cheap_model:
    provider: openrouter
    model: google/gemini-2.5-flash

# Compression — use Sonnet for summaries, not Flash
compression:
  enabled: true
  threshold: 0.75  # Earlier compression = better context health
  summary_model: anthropic/claude-sonnet-4.6  # Better summaries

# Memory — expand limits for richer recall
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 4000  # 2x default
  user_char_limit: 2500    # 2x default
  nudge_interval: 8        # More frequent memory flushes
  flush_min_turns: 4       # Flush earlier

# Agent settings
agent:
  max_turns: 60
  reasoning_effort: medium
```

**Validation**: Hermes greets Mike as Jake with personality, pushes back on a bad idea, announces effort level

### Phase 3: Skills — Jake's Discipline Systems (Session 2-3)
**Goal**: Build custom skills that implement Jake's unique capabilities

#### Skill 1: `/plan` — Plan Gate Enforcement
```
Trigger: When user asks to build/implement/create something non-trivial
Action:
1. Classify complexity (files to touch, dependencies, reversibility)
2. If >3 steps: REFUSE to code, generate plan first
3. Write plan to ~/.hermes/plans/<date>-<slug>.md
4. Ask for approval before executing
```

#### Skill 2: `/context-health` — Guardian Mind Check
```
Trigger: /context-health OR auto-triggered every 15 messages
Action:
1. Count messages in current session
2. Check compression status
3. Estimate remaining context budget
4. Report: GREEN/YELLOW/ORANGE/RED
5. If ORANGE+: recommend session split or handoff
```

#### Skill 3: `/debt-check` — Technical Debt Score
```
Trigger: /debt-check OR after every code modification
Action:
1. Scan recent session for debt signals (files without tests, TODOs added, bugs deferred)
2. Calculate running debt score
3. If >20: warn. If >30: refuse new features
4. Generate cleanup recommendations
```

#### Skill 4: `/handoff` — Structured Session Handoff
```
Trigger: /handoff OR when context health hits ORANGE
Action:
1. Summarize completed work with file lists
2. List in-progress items with exact next steps
3. Capture decisions made with rationale
4. Write to ~/.hermes/handoffs/<date>.md
5. Update memory with durable learnings
```

#### Skill 5: `/boot` — Informed Session Start
```
Trigger: Auto on session start (prefill_messages)
Action:
1. Read latest handoff file
2. Read memory (MEMORY.md + USER.md)
3. Check recent cron job outputs
4. Generate informed greeting with: personal touch, unfinished work, project state, suggested focus
```

#### Skill 6: `/gate` — Quality Gate Check
```
Trigger: At build milestones or on demand
Action:
1. Review work done so far against plan
2. Check for: untested code, TODO/FIXME growth, lint warnings, error rate
3. Generate Build Health Report
4. Recommend: proceed / fix issues / stop and reassess
```

#### Skill 7: `/parking-lot` — Idea Capture
```
Trigger: When Mike proposes unplanned work mid-session
Action:
1. Acknowledge the idea
2. Write to ~/.hermes/parking-lot.md with date + context
3. Refuse to implement now
4. Return focus to current plan
```

**Validation**: Each skill executes correctly via `/command` syntax in Hermes

### Phase 4: Cron Jobs — Proactive Intelligence (Session 3)
**Goal**: Hermes does useful work even when Mike isn't talking to it

#### Cron 1: Morning Brief (6:30 AM daily)
```
Schedule: 0 6 30 * * *
Action:
1. Check all 3 project repos for recent git activity
2. Check Susan RAG for stale data
3. Check TrendRadar for overnight competitive signals
4. Compose brief: "Morning, Mike. Here's what happened overnight..."
5. Deliver via Telegram
```

#### Cron 2: Memory Consolidation (midnight daily)
```
Schedule: 0 0 * * *
Action:
1. Review today's conversations
2. Extract durable learnings (decisions, preferences, patterns)
3. Update MEMORY.md and USER.md
4. Prune outdated entries
```

#### Cron 3: Context Health Heartbeat (every 4 hours)
```
Schedule: 0 */4 * * *
Action:
1. Check Hermes session state
2. If active session >100 messages: send Telegram warning
3. Log health metrics to ~/.hermes/health/
```

#### Cron 4: Parking Lot Review (Fridays 4 PM)
```
Schedule: 0 16 * * 5
Action:
1. Read ~/.hermes/parking-lot.md
2. For each idea: assess relevance, priority, effort
3. Promote worthy ideas to plans
4. Archive stale ideas
5. Send summary via Telegram
```

#### Cron 5: Self-Improvement Extraction (weekly Sunday)
```
Schedule: 0 10 * * 0
Action:
1. Review past week's session logs
2. Extract: what worked, what failed, what was slow
3. Identify skill gaps (things Mike asked for that Hermes couldn't do)
4. Generate improvement recommendations
5. Update SOUL.md with new learnings
```

**Validation**: Cron jobs execute on schedule, produce useful output, deliver via Telegram

### Phase 5: Cross-System Integration (Session 4)
**Goal**: Connect Hermes to Jake's full ecosystem

- [ ] **5.1** Wire Susan RAG access — create skill that queries Supabase via the FastAPI server
- [ ] **5.2** Connect to TrendRadar — cron job pulls competitive intelligence
- [ ] **5.3** Build Firehose.com skill — real-time web monitoring
- [ ] **5.4** Cross-project memory — Hermes knows about all 3 companies
- [ ] **5.5** Delegation routing — heavy tasks delegate to Opus, simple to Flash
- [ ] **5.6** Notification routing — critical alerts via Telegram, summaries via email

**Validation**: Hermes can answer questions about any company using Susan's RAG, receive competitive alerts, and route tasks to appropriate models

---

## Part 4: Priority Matrix

| Phase | Effort | Impact | Do When |
|-------|--------|--------|---------|
| Phase 1: Fix & Stabilize | Low | CRITICAL | Next session — first |
| Phase 2: SOUL.md Rewrite | Medium | CRITICAL | Next session — second |
| Phase 3: Skills (1-3) | Medium | HIGH | Same session if context allows |
| Phase 3: Skills (4-7) | Medium | HIGH | Session after |
| Phase 4: Cron Jobs | Medium | HIGH | After skills work |
| Phase 5: Integration | High | MEDIUM | Final session |

**Estimated sessions**: 3-4 focused sessions to reach full Jake-parity

---

## Part 5: What Makes This 25x Better (Not Just Parity)

Jake operates inside Claude Code — which means he has:
- Native file editing, git, grep, glob tools
- Hooks that auto-fire on events
- Sub-agents with full tool access
- 1M token context window

Hermes operates differently — and has advantages Jake doesn't:
- **Always-on Telegram** — Jake dies when the terminal closes. Hermes persists.
- **Cron jobs** — Jake can't do anything when Mike isn't talking to him. Hermes can.
- **Self-improving skills** — Hermes can literally rewrite its own skills based on what it learns.
- **Multi-platform** — Hermes works on Telegram, Discord, Slack, WhatsApp, Signal. Jake is terminal-only.
- **Voice** — Hermes has TTS/STT. Jake doesn't.

### The 25x Multiplier
Instead of copying Jake 1:1, we leverage Hermes's unique strengths:

1. **Proactive Intelligence** (Hermes advantage: cron) — Jake waits for Mike. Hermes wakes up, checks everything, and sends Mike insights before he even asks.
2. **Persistent Guardian** (Hermes advantage: always-on) — Context health monitoring that runs BETWEEN sessions, not just during them.
3. **Self-Evolving Skills** (Hermes advantage: skill rewriting) — Every week, Hermes reviews what worked and rewrites its own skills. Jake's rules are static files.
4. **Multi-Surface Presence** (Hermes advantage: platforms) — Mike gets Jake on Telegram, on desktop, potentially on his phone via voice. Not just in a terminal.
5. **Cross-Session Continuity** (Hermes advantage: persistent memory) — Hermes remembers EVERYTHING across sessions natively. Jake relies on handoff files.

### The Combined Architecture
```
┌──────────────────────────────────────────────┐
│  MIKE                                         │
├──────────┬───────────────────────────────────┤
│ Terminal │    Telegram / Voice / Desktop      │
│          │                                    │
│  JAKE    │         HERMES (Jake personality)  │
│ (Claude  │    (Sonnet 4.6 via OpenRouter)     │
│  Code)   │                                    │
│          │  + Always-on gateway               │
│  Deep    │  + Cron jobs (morning brief, etc.) │
│  dev     │  + Self-improving skills           │
│  work    │  + Multi-platform delivery         │
│          │  + Voice interaction               │
├──────────┴───────────────────────────────────┤
│           SHARED BACKENDS                     │
│  Susan RAG │ Supabase │ TrendRadar │ GitHub  │
└──────────────────────────────────────────────┘
```

**Jake in Claude Code** = deep development, architecture, planning, code
**Jake in Hermes** = always-on assistant, proactive intelligence, Telegram/voice, monitoring

They share the same personality, memory, and backend services. Two surfaces, one Jake.

---

## Success Criteria

| Metric | Current | Target |
|--------|---------|--------|
| API error rate | ~30% (Azure failures) | <1% |
| Multi-turn success | Crashes at ~20 turns | 60+ turns stable |
| Morning brief delivery | Manual | Automated daily by 6:30 AM |
| Context health awareness | Zero | Auto-warns at YELLOW, auto-handoffs at RED |
| Task effort classification | None (everything medium) | Auto-classifies every task |
| Plan enforcement | None (builds immediately) | Refuses without plan for complex work |
| Technical debt tracking | None | Running score with circuit breaker |
| Self-improvement cycle | None | Weekly skill review + rewrite |
| Cross-project awareness | None | All 3 companies in memory |
| Personality consistency | Broken (kawaii mode) | Full Jake in every interaction |
