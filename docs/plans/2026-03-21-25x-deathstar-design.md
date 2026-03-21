# 25X DeathStar — System Design
**Date**: 2026-03-21
**Author**: Jake + Mike Rodgers
**Status**: APPROVED — building in sequence A → B → C
**Metaphor**: Foundation → Walls → Roof
**Destination**: $10M ARR, 3 companies running through Jake, PAI platform licensed externally

---

## The Core Insight (PAI Framework)

The bottleneck isn't AI capability. It's **knowledge articulation + infrastructure**.

The four components every Personal AI Infrastructure needs:

| # | Component | What It Does | Gap Today |
|---|-----------|-------------|-----------|
| 1 | Implicit Expertise Capture | Documents processes/SOPs that live in your head | Missing |
| 2 | Context Management (Memory Lake) | Links docs + tools + past work into a unified query surface | Partial |
| 3 | Agent Scaffolding | AI uses tools, accesses files, follows dynamic requirements | 80% done |
| 4 | Goal + Metric Tracking | Tracks intent → execution gap, budgets, KPIs | Missing |

Jake is the runtime. Susan is the intelligence layer. OpenClaw is the distribution platform. These three together ARE the PAI platform.

---

## Architecture: The House

```
┌─────────────────────────────────────────────────────┐
│  ROOF: Vertical Products                            │
│  TransformFit ($10M fitness PAI)                    │
│  Viral Architect (AI Social Media at scale)         │
│  Future verticals: 3+ more                          │
├─────────────────────────────────────────────────────┤
│  WALLS: Studio Empire                               │
│  AI Dev Studio (builds companies via Jake)          │
│  AI Social Media Studio (grows brands via Jake)     │
│  Each callable: "Jake, run studio session for X"    │
├─────────────────────────────────────────────────────┤
│  FOUNDATION: PAI Platform                           │
│  Jake 100/100 (Goal Tracking + Expertise Capture)   │
│  OpenClaw PAI Layer (installable for any founder)   │
│  Susan commercial intelligence layer               │
│  Universal: "Jake, [anything]" → workflow fires     │
└─────────────────────────────────────────────────────┘
```

---

## FOUNDATION — Option A: PAI Platform

### What Gets Built

**1. Goal + Metric Tracking Layer** (biggest gap, builds first)
- `jake_brain/goals/` module — Goals, Milestones, KPIs, OKRs
- Stored in new Supabase table: `jake_goals`
- Jake asks "what's your goal for this?" on every new project/task
- Weekly progress check via Telegram: "You said you wanted X by Y. Here's where you are."
- Connects to brain episodic layer — goal progress is a first-class memory type

**2. Implicit Expertise Capture**
- Hermes skill: `jake-sop-capture` — Jake interviews you to extract a process, generates a structured SOP
- "Jake, I keep doing X manually. Help me document it." → interview → structured doc → stored in brain
- Stored as `jake_procedural` with source_type='sop'
- Triggers: "Jake, capture this" or any time Mike solves a repeating problem

**3. Context Management Expansion (Memory Lake)**
- Document linker: Jake can ingest any file (PDF, markdown, Google Doc) into the brain with metadata
- Tool-to-memory connections: when Jake uses a tool, the result is linked to the relevant entity in the knowledge graph
- Unified search surface: one `brain_search` query hits docs + conversations + tools + SOPs

**4. OpenClaw PAI Integration**
- Jake's plugin stack becomes installable on OpenClaw
- Config-driven: each user gets their own memory lake (their Supabase project)
- Susan becomes the intelligence backend — `run_agent` API exposed
- Pricing: free tier (no brain), Pro tier ($49/mo — brain), Studio tier ($199/mo — full Susan team)

### Jake/Telegram Interface
Everything callable via Telegram. Zero-friction design.

```
Mike types:              Jake does:
"goal for TransformFit"  → opens goal session, tracks weekly
"capture this SOP"       → interviews, structures, stores
"what's my progress?"    → pulls all active goals, scores each
"search my docs"         → hits full memory lake
```

### Success Criteria (Foundation complete when)
- [ ] Jake tracks 5+ active goals with weekly Telegram check-ins
- [ ] SOP capture works: Mike describes process → structured doc in <5 min
- [ ] Memory lake: any doc ingested and searchable in <60 seconds
- [ ] OpenClaw plugin config exists with multi-user support
- [ ] Jake answers "what am I behind on?" correctly from goal tracking

---

## WALLS — Option B: Studio Empire

### AI Dev Studio

**What it is**: Jake-powered software development studio. Mike describes a product, Jake (with Susan's Atlas + Forge + Nova + Sentinel team) designs, specs, builds, and deploys it. First client: TransformFit.

**How it works via Jake/Telegram**:
```
Mike: "Jake, start a dev studio session for TransformFit onboarding flow"
Jake: loads TransformFit context from brain + PAI memory lake
      spins up Atlas (architect) + Forge (QA) + Nova (AI/ML) + Sentinel (security)
      runs design session → spec doc → implementation plan → execution
      checks in via Telegram at each milestone
```

**Hermes Skill**: `ai-dev-studio/SKILL.md`
- Loads company context from brain
- Assembles Susan team for the build type (web app / mobile / API / data pipeline)
- Creates milestone-based work breakdown
- Reports progress to Mike via Telegram
- Outputs: spec doc, implementation plan, committed code

**MCP Workflow** (like the Oracle onsite prep pattern):
- `/dev-studio start [company] [feature]` — kicks off a full build session
- `/dev-studio status` — where are we, what's next
- `/dev-studio ship` — final QA + deploy

**Revenue model**: $15K-50K per build. 10 builds/year = $150K-500K. Scales to team of AI agents.

### AI Social Media Studio

**What it is**: Viral Architect + Jake = full social media operation. Strategy, content creation, scheduling, analytics, growth — all callable via Telegram.

**How it works via Jake/Telegram**:
```
Mike: "Jake, run social studio for [brand]"
Jake: loads brand voice, past content, audience data from brain
      spins up Aria (growth) + Herald (PR) + Prism (brand) + Beacon (ASO/SEO) team
      generates content calendar → storyboard → shot list → captions → scheduling
      outputs ready-to-post content pack
```

**Hermes Skill**: `ai-social-studio/SKILL.md`
- Brand voice from brain (stored once, used forever)
- Content calendar generation (weekly, monthly)
- Viral hook framework (Viral Architect methodology)
- Platform-specific formatting (IG, TikTok, LinkedIn, X)
- Analytics ingestion → content strategy adaptation

**MCP Workflow**:
- `/social-studio brief [brand] [platform] [goal]` — generate content brief
- `/social-studio calendar [brand] [month]` — full monthly calendar
- `/social-studio post [brand]` — next post, ready to publish

**Revenue model**: $2K-5K/month retainer per brand. 20 brands = $40K-100K/month.

### Studio Coordination
Both studios run on top of the PAI Foundation:
- Goal tracking: each studio project tied to a client goal
- Memory lake: all project docs ingested automatically
- Expertise capture: every successful pattern stored as SOP

---

## ROOF — Option C: Vertical Dominator

### TransformFit → $10M

**What it is**: The PAI platform applied specifically to fitness businesses. Coaches + gym owners get a Jake instance trained on fitness SOPs, programmed with their client base, tracking every client goal.

**The PAI stack for fitness**:

| Component | Fitness Application |
|-----------|-------------------|
| Expertise Capture | Coach's programming philosophy, periodization models, injury protocols |
| Memory Lake | Every client's history, preferences, progress, injuries |
| Agent Scaffolding | Auto-generate programs, check-in messages, nutrition guidance |
| Goal Tracking | Client goals (strength, weight, performance) tracked by Jake weekly |

**Jake/Telegram for coaches**:
```
Coach types:             Jake does:
"program for [client]"   → pulls client history → generates 4-week block
"check-in [client]"      → pulls last session → sends personalized message
"business goals?"        → revenue, retention, new client pipeline
"what's working?"        → analyzes which programs have best outcomes
```

**Revenue model**: $99/mo per coach (individual) → $499/mo per gym (team). 10,000 coaches = $990K/mo = ~$12M ARR.

**Build via AI Dev Studio**: TransformFit's app is built by the AI Dev Studio. Meta — Jake builds the product that Jake then powers.

### Viral Architect → AI Social Media at Scale

**What it is**: The social media methodology productized. Founders pay for their own branded AI Social Media Studio powered by Viral Architect's frameworks.

**Revenue model**: $197/mo SaaS. 5,000 subscribers = $985K/mo = ~$12M ARR.

**Build via AI Social Media Studio**: Viral Architect's content IP becomes the training data + methodology layer for the studio.

---

## The Full Stack (Everything Callable via Jake)

```
Telegram command              → What fires
─────────────────────────────────────────────────────
/goal new [project]           → Goal session, tracked weekly
/sop capture                  → SOP interview + documentation
/dev-studio [company]         → Full AI Dev Studio session
/social-studio [brand]        → Full Social Media Studio session
/transformfit [coach/client]  → Fitness PAI session
/viral [brand]                → Viral Architect content session
/status                       → All goals, all studios, all companies
/brief                        → Morning brief (already working)
/oracle [context]             → Oracle Health work session (already working)
```

Every command fires a Hermes skill → assembles Susan team → reports back to Telegram.

---

## The 25X Timeline

```
TODAY → 30 days:     Foundation Phase 1
  - Goal tracking layer (jake_brain/goals/)
  - SOP capture skill
  - Complete Jake 100/100 (panelist audit)

30 → 60 days:        Foundation Phase 2
  - Memory lake expansion (document ingestion)
  - OpenClaw PAI plugin config
  - First external user on platform

60 → 90 days:        Walls Phase 1
  - AI Dev Studio skill + MCP workflow
  - AI Social Media Studio skill + MCP workflow
  - TransformFit dev studio session #1

90 → 180 days:       Walls Phase 2
  - First paying studio clients
  - TransformFit v1 live
  - Viral Architect integrated into social studio

180 → 365 days:      Roof Phase 1
  - TransformFit to 100 paying coaches
  - Viral Architect to 50 paying subscribers
  - OpenClaw PAI platform: 25 external users

Year 1 → Year 2:     Roof Phase 2
  - TransformFit: 1,000 coaches ($99K MRR)
  - Social Studio: 500 brands ($1M MRR)
  - Platform: 100 founders ($19.9K MRR)
  - Combined: ~$13M ARR

Year 3:              DeathStar Online
  - Jake is the operating system for 500+ founders
  - Susan is commercially licensed
  - 3 vertical products, 2 studios, 1 platform
  - $25M+ ARR
```

---

## Open Questions for Panel Review

1. **OpenClaw strategy**: Build ON OpenClaw (distribution) or build WITH OpenClaw patterns (inspired by) — or fork and own the distribution?
2. **TransformFit GTM**: Coach-led (bottom-up) or gym-led (top-down)? Different CAC/LTV profiles.
3. **Viral Architect positioning**: Methodology-first (sell the framework) or tool-first (sell the software)?
4. **Susan commercialization**: When does Susan become a standalone product vs. infrastructure-only?
5. **Jake for others**: How much of Jake's cognitive architecture is replicable without Mike's specific brain data?

---

## Panel Composition for Evaluation

Bringing in for Strategos Future-Back + Innosight 6-lens scoring:

| Panelist | Domain | What They'll Evaluate |
|----------|--------|-----------------------|
| Steve (Strategy) | Business strategy | Competitive moat, market timing, revenue model |
| Compass (Product) | Product management | PMF, sequencing, user journey |
| Atlas (Engineering) | Architecture | Build feasibility, technical risk, timeline |
| Vault (Fundraising) | Capital | Fundability, investor narrative, valuation |
| Ledger (Finance) | Unit economics | CAC, LTV, payback period, burn |
| Aria (Growth) | Acquisition | GTM, channel strategy, viral loops |
| Nova (AI/ML) | Intelligence layer | Susan scalability, AI architecture |
| Freya (Behavioral Econ) | Retention | Habit loops, retention architecture |

Each panelist scores A → B → C ordering on 6 Innosight lenses. Scores surface to Jake → Mike decides.
