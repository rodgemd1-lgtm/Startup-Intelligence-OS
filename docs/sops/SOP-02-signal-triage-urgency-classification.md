# SOP-02: Competitive Signal Triage & Urgency Classification

**Owner**: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-22
**Category**: Daily Intelligence Operations
**Priority**: P1 — Core methodology IP
**Maturity**: Automated (in code) but undocumented as a process

---

## Purpose

Classify, score, and route every incoming signal — from emails and calendar events to competitive intelligence and brain memories — through a unified triage system that ensures Mike sees the right thing at the right time with the right urgency level.

---

## Scope

This SOP covers the end-to-end signal triage pipeline:
- Raw signal intake from all sources
- Urgency and importance scoring
- Priority tier assignment (P0/P1/P2/P3)
- Routing to the appropriate output (real-time alert, daily brief, weekly summary, background log)
- Competitive signal scoring (3-axis: relevance × actionability × urgency)

---

## ARCHITECTURE: Three-Layer Signal Processing

The triage system operates as three complementary layers:

```
┌──────────────────────────────────────────────────────────────┐
│  Layer 1: PRIORITY ENGINE (jake_brain/priority.py)          │
│  Source-agnostic triage: email, calendar, reminders, brain  │
│  Formula: urgency × importance × recency × source_weight    │
│  Output: P0/P1/P2/P3 tier assignment                        │
├──────────────────────────────────────────────────────────────┤
│  Layer 2: BIRCH SCORER (birch/scorer.py)                    │
│  Competitive intelligence signals specifically              │
│  Formula: (relevance×0.40) + (actionability×0.35) +         │
│           (urgency×0.25)                                    │
│  Output: Tier 1/2/3 + routing to competitive-response       │
├──────────────────────────────────────────────────────────────┤
│  Layer 3: NERVOUS SYSTEM (jake_brain/nervous/email_alert.py)│
│  Real-time email scanning every 2 minutes                   │
│  VIP sender detection + urgent keyword matching             │
│  Output: Immediate Telegram alert for P0/P1 emails          │
└──────────────────────────────────────────────────────────────┘
```

---

## LAYER 1: PRIORITY ENGINE — General Signal Triage

### 1.1 Composite Scoring Formula

Every signal is scored using:

```
composite = urgency × importance × recency_factor × source_weight × vip_boost × imminence_boost
```

Score range: 0.0 – 1.0

### 1.2 Priority Tiers

| Tier | Score | Action | Description |
|------|-------|--------|-------------|
| **P0** | ≥ 0.75 | **Interrupt Mike immediately** | Real-time Telegram alert. Something needs attention RIGHT NOW. |
| **P1** | ≥ 0.50 | **Surface in next brief** | Include in morning brief or next check-in. Important but not interrupt-worthy. |
| **P2** | ≥ 0.25 | **Include in daily summary** | Goes into the daily digest. Good to know, not urgent. |
| **P3** | < 0.25 | **Background log only** | Stored in brain for context. No active surfacing. |

### 1.3 Source Weights

Not all sources are created equal. Source weight reflects how likely a signal from that channel is to be actionable:

| Source | Weight | Rationale |
|--------|--------|-----------|
| **Manual** | 1.00 | Mike explicitly flagged this — highest priority |
| **Phone Call** | 0.95 | Someone calling = high urgency by nature |
| **Text / iMessage** | 0.90 | Direct personal communication — high action rate |
| **Calendar** | 0.90 | Time-bound events almost always need action |
| **Email** | 0.85 | Work communications, high action rate |
| **Reminder** | 0.80 | Explicitly set by Mike, but may be stale |
| **Telegram** | 0.75 | Real-time but mixed signal quality |
| **Brain** | 0.70 | Memory recall — relevant but not urgent by nature |
| **GitHub** | 0.60 | Code changes — important but rarely interrupt-worthy |
| **System** | 0.50 | Automated system events — usually informational |

### 1.4 VIP Detection

Any signal mentioning these people or entities gets a **1.3x multiplier**:

| VIP | Why |
|-----|-----|
| Matt Cohlmia / Cohlmia | Mike's VP — his requests are always P1+ |
| Seema Verma | SVP — executive stakeholder |
| Bharat Sutariya | SVP Clinical — key leadership |
| Elizabeth Krulish | Lead EA — scheduling and coordination gatekeeper |
| James Loehr / James | Mike's husband — personal priority |
| Jacob | Mike's son — personal priority |
| Jen | Mike's ex-wife — family coordination |
| Alex | Mike's younger son |
| Oracle Health / Oracle | Employer — work signals always elevated |

VIP detection scans both signal content and the people field.

### 1.5 Urgency Keyword Detection

Keywords in signal content automatically boost urgency scores:

**High Urgency → boosted to 0.85:**
`urgent`, `asap`, `today`, `due today`, `overdue`, `flight`, `deadline`, `critical`, `p0`, `immediate`, `alert`, `failure`, `error`, `down`, `birthday today`, `meeting in`

**Medium Urgency → boosted to 0.55:**
`tomorrow`, `this week`, `follow up`, `follow-up`, `reminder`, `review`, `draft`, `prepare`, `prep`, `schedule`

### 1.6 Recency Decay

Signals lose priority over time using exponential decay:

```
recency_factor = 0.5 ^ (hours_ago / 48.0)
```

- **Half-life: 48 hours** — a signal is worth half as much after 2 days
- A 1-hour-old email scores ~99% of original importance
- A 24-hour-old email scores ~71%
- A 48-hour-old email scores ~50%
- A 96-hour-old email scores ~25%

This prevents stale signals from competing with fresh ones.

### 1.7 Imminence Boost (Calendar Events)

Time-sensitive events get additional boosting based on proximity:

| Time Until Event | Multiplier | Logic |
|-----------------|------------|-------|
| < 1 hour | **1.8x** | Meeting is imminent — interrupt |
| < 2 hours | **1.4x** | Prep time — surface now |
| < 24 hours | **1.1x** | Today — mild boost |
| > 24 hours | 1.0x | No boost |
| Already past | 0.9x | Slight deprioritize |

### 1.8 Signal Factory Functions

The system provides pre-configured signal constructors for common source types:

| Factory | Source Type | Default Urgency | Default Importance |
|---------|------------ |-----------------|-------------------|
| `email_signal()` | EMAIL | 0.5 | 0.6 |
| `calendar_signal()` | CALENDAR | 0.6 | 0.7 |
| `reminder_signal()` | REMINDER | 0.5–0.95 (overdue = 0.95) | 0.65 |
| `brain_signal()` | BRAIN | 0.4 | varies |

---

## LAYER 2: BIRCH SCORER — Competitive Intelligence Signals

### 2.1 Three-Axis Scoring

Competitive signals are scored on three dimensions:

| Axis | Weight | What It Measures |
|------|--------|-----------------|
| **Relevance** | 40% | Does this signal mention our competitors or key topics? |
| **Actionability** | 35% | Can we do something with this intelligence? |
| **Urgency** | 25% | Is this time-sensitive? |

```
composite = (relevance × 0.40) + (actionability × 0.35) + (urgency × 0.25)
Score range: 0–100
```

### 2.2 Relevance Scoring

Relevance is keyword and competitor name matching against a rubric:

| Match Type | Points Per Hit |
|-----------|---------------|
| **Keyword hit** (e.g., "EHR", "RCM", "agentic AI") | +20 |
| **Competitor name hit** (e.g., "Epic", "Waystar", "Regard") | +30 |

If a term appears in BOTH keywords and competitors (e.g., "Epic" for Oracle Health), it scores both weights (20 + 30 = 50). This is intentional — overlap signals high relevance.

### 2.3 Actionability Scoring

- **Base: 40 points** when the signal matches a tracked company
- **+20 points per action verb hit** (from company rubric action patterns)
- Range: 10–100

### 2.4 Urgency Scoring

Urgency words: `breaking`, `just`, `today`, `announces`, `launches`, `immediate`, `launch`, `announce`

- **Base: 20 points**
- **+20 points per urgency word**
- Range: 10–100

### 2.5 Competitive Signal Tiers

| Tier | Score | Routing | Action |
|------|-------|---------|--------|
| **Tier 1** | ≥ 80 | `competitive-response` | High relevance — route to competitive response workflow |
| **Tier 2** | ≥ 50 | monitoring | Medium — include in monitoring dashboard |
| **Tier 3** | < 50 | background | Low — log and archive |

---

## LAYER 3: NERVOUS SYSTEM — Real-Time Email Alerts

### 3.1 How It Works

The Nervous System daemon runs every 2 minutes and scans the last 2 hours of Oracle/Exchange email for urgent messages.

**Fetch Priority:**
1. **Microsoft Graph API** (preferred — fast, reliable, no Mail.app dependency)
2. **osascript fallback** (Apple Mail via JavaScript for Automation — unreliable if Mail.app has been running long)

### 3.2 Email Urgency Scoring

Each email is scored additively:

**Step 1 — VIP Sender Boost (one max):**

| Sender Fragment | Boost |
|----------------|-------|
| Matt Cohlmia / Cohlmia | +0.40 |
| CTO / CEO | +0.30 |
| VP / Vice President | +0.25 |
| Ellen | +0.25 |
| Director | +0.20 |
| Oracle | +0.20 |

**Step 2 — Keyword Boost (one max):**

| Keyword | Boost |
|---------|-------|
| P0 | +0.50 |
| Security alert | +0.45 |
| Urgent / Critical / Action required / Outage | +0.40 |
| ASAP / Overdue / Escalation / Incident / Approval needed / Action needed | +0.35 |
| By EOD / By end of day / Immediately | +0.30 |
| Deadline / Response needed | +0.25 |
| Please respond | +0.20 |

**Step 3 — Unread Boost:**
- Unread email: +0.10

**Threshold:** Score ≥ 0.50 triggers a real-time alert.

### 3.3 Alert Routing

| Score | Tier | Action |
|-------|------|--------|
| ≥ 0.75 | **P0 — Act now** | Immediate Telegram alert with full context |
| ≥ 0.50 | **P1 — Check soon** | Batched notification at next cycle |
| < 0.50 | No alert | Handled by daily brief (SOP-01) |

### 3.4 Deduplication

The Nervous System tracks `seen_events` by message ID to avoid re-alerting on the same email. State is maintained per-session in the EventBus.

---

## THE "SO WHAT" FRAMEWORK

Every signal surfaced to Mike must answer three questions:

| Question | Purpose |
|----------|---------|
| **What Happened?** | The raw signal — what was detected, from where |
| **Why It Matters** | Relevance to Oracle Health, competitive implications |
| **What Should We Do** | Recommended action — respond, monitor, park, or escalate |

This framework is embedded in:
- The daily morning brief (SOP-01)
- The weekly Matt briefing (SOP-03)
- Competitive response recommendations
- Conference capture templates (SOP-11, "So What" field)

Signals that can't answer "Why It Matters" should be downgraded to P3 regardless of urgency score.

---

## SIGNAL FLOW: END-TO-END

```
              ┌─────────────┐
              │  RAW INPUT   │
              │              │
              │  Email       │
              │  Calendar    │
              │  Reminders   │
              │  Brain       │
              │  GitHub      │
              │  CI feeds    │
              │  Telegram    │
              └──────┬───────┘
                     │
           ┌─────────┴──────────┐
           │                    │
     ┌─────▼──────┐     ┌──────▼──────┐
     │  PRIORITY   │     │   BIRCH     │
     │  ENGINE     │     │   SCORER    │
     │             │     │             │
     │  Personal   │     │ Competitive │
     │  + Work     │     │ Intelligence│
     │  signals    │     │ signals     │
     └─────┬───────┘     └──────┬──────┘
           │                    │
     ┌─────▼──────────────┐     │
     │ P0: Telegram alert ├─────┤
     │ P1: Morning brief  │     │
     │ P2: Daily summary  │     │
     │ P3: Background log │     │
     └────────────────────┘     │
                          ┌─────▼──────┐
                          │ Tier 1:    │
                          │ Competitive│
                          │ Response   │
                          │            │
                          │ Tier 2:    │
                          │ Monitor    │
                          │            │
                          │ Tier 3:    │
                          │ Archive    │
                          └────────────┘
```

---

## TUNING & CALIBRATION

### When to Adjust Weights

| Symptom | Likely Fix |
|---------|-----------|
| Too many P0 alerts | Raise P0 threshold from 0.75 to 0.80, or reduce VIP boost from 1.3x to 1.2x |
| Missing important emails | Add sender to VIP_SENDERS list, or add keyword to URGENT_KEYWORDS |
| Stale signals crowding fresh ones | Reduce HALF_LIFE_HOURS from 48 to 24 |
| Competitive signals all scoring Tier 2 | Review Birch rubric — keywords/competitors may need updating |
| Calendar events not surfacing | Check imminence_factor thresholds |

### Calibration Cadence

| Review | Frequency | What to Check |
|--------|-----------|---------------|
| VIP list | Monthly | Any new stakeholders? (new VP, new direct report) |
| Keyword lists | Monthly | Any new urgency patterns in email? |
| Source weights | Quarterly | Has signal quality changed by channel? |
| Tier thresholds | Quarterly | Are P0/P1/P2 distributions balanced? |
| Birch rubric | Per competitor change | New competitors? New keywords? |

---

## IMPLEMENTATION REFERENCE

### Source Files

| Component | File | Purpose |
|-----------|------|---------|
| Priority Engine | `jake_brain/priority.py` | General triage scoring |
| Email Alert Scanner | `jake_brain/nervous/email_alert.py` | Real-time email urgency |
| Birch Scorer | `birch/scorer.py` | Competitive intelligence scoring |
| Birch Schemas | `birch/schemas.py` | RawSignal / ScoredSignal data models |
| Morning Brief | `scripts/brain_morning_brief.py` | Daily synthesis + delivery |
| Nervous Daemon | `scripts/jake_nervous_daemon.py` | 2-minute scan cycle |

### Cron Schedule

| Cron | What | Frequency |
|------|------|-----------|
| `jake_nervous_daemon` | Email + meeting alerts | Every 2 minutes |
| `brain_morning_brief` | Morning brief assembly + delivery | Daily 6:00 AM |
| Weekly Matt Brief | Executive briefing for Matt | Friday 3:00 PM |

---

## REVISION HISTORY

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-03-22 | 1.0 DRAFT | Initial SOP documenting existing automated system | Jake + Mike |

---

## SOURCE ATTRIBUTION

This SOP documents Mike's signal triage system as implemented in code:
1. **Priority Engine** (`jake_brain/priority.py`) — multi-factor urgency scoring with VIP detection, recency decay, and imminence boosting
2. **Birch Scorer** (`birch/scorer.py`) — 3-axis competitive intelligence signal scoring
3. **Nervous System** (`jake_brain/nervous/email_alert.py`) — real-time email monitoring with Graph API + osascript fallback
4. **Morning Brief Pipeline** (`scripts/brain_morning_brief.py`) — daily synthesis and delivery
5. **SCIP Intelligence Cycle** — industry standard for signal classification and routing
6. **Matt Cohlmia's "So What" framework** — every signal must answer What Happened / Why It Matters / What We Should Do
