# SOP-02: Competitive Signal Triage & Urgency Classification

**Owner**: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence
**Version**: 2.0
**Last Updated**: 2026-03-22
**Category**: Daily Intelligence Operations
**Priority**: P1 — Core methodology IP
**Maturity**: Automated (in code) but undocumented as a process

---

## Strategic Context: Why Triage Quality Determines Competitive Win Rate

Signal triage is not an inbox management problem. It is a **competitive intelligence distribution problem** — and getting it wrong has a direct, measurable impact on Oracle Health's win rate.

**The connection:**

Oracle Health competes in a market where deals are won and lost on information asymmetry. The team that knows what Epic announced, what a competitor changed in their contract terms, or what a mutual prospect just said publicly — *before the sales team walks into a meeting* — wins. The team that finds out three days later loses.

**The math:**
- Competitive intelligence teams that achieve "high responsiveness" to signals close competitive deals at 18-22% higher rates than teams with low responsiveness (Dzreke & Dzreke, 2025, *IJRAR*, 200 enterprises)
- A signal that arrives in Mike's briefing 48 hours late has already lost half its value (recency decay half-life: 48 hours)
- Epic, Waystar, and Regard are resourced organizations that monitor Oracle Health signals continuously — the asymmetry compounds if Oracle's signal-to-action loop is slow

**What triage failure actually costs:**
- A missed P0 competitive signal before a finalist meeting can cost a $2M+ deal
- A delayed Matt briefing on a competitor announcement can cost an executive credibility in front of customers
- A stale competitive response (built on 2-week-old intel) can contradict what the buyer already knows

**Triage quality = competitive responsiveness = deal wins.** This SOP defines how that chain is maintained.

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

## CONSUMER INTERFACE — How Field Teams Access Intelligence

The triage system produces intelligence. This section defines how the two primary field consumers — **Sales Reps** and **Product/PMM** — receive and request it.

### Sales Rep Interface

| Need | How to Request | Turnaround | Delivery |
|------|---------------|-----------|---------|
| Pre-meeting competitive profile | Email Mike with deal ID + meeting date | < 48 hours | Email summary: competitor strengths/weaknesses relevant to this deal, recent signals |
| Urgent competitive intel (Tier 1 signal just broke) | Slack or Telegram message to Mike | < 4 hours during business hours | Direct message with briefing |
| Weekly competitive summary | Automatic — included in Sales Enablement weekly digest | Every Friday 3 PM | Email digest |
| Battlecard update request | Email Mike with competitor name + specific gap | < 5 business days | Updated battlecard section in SharePoint |

**What reps DON'T need to do:** Monitor raw feeds, interpret competitor announcements, or ask "did you see this?" The triage system is designed so that if a signal is Tier 1 or P0, Mike surfaces it to affected reps proactively — reps shouldn't need to ask.

### Product/PMM Interface

| Need | Source | Cadence | Format |
|------|--------|---------|--------|
| Competitive themes for messaging updates | Monthly Insight Report | Monthly | Section 3: Competitive Perception Shifts |
| Battlecard objection handling updates | Tier 1 signal routing | On-demand, <48 hours after signal | Mike emails PMM with specific battlecard section to update |
| Roadmap flag (competitor announced something relevant) | Tier 1 / immediate routing | Real-time | Telegram message to PMM + email |
| Win/loss-driven messaging trigger | Win/Loss SOP-09 integration | Per 3-interview threshold | Formal messaging review request from Mike |

**Messaging update trigger (from SOP-09):** When a competitive theme shifts by >10pp from baseline across 3+ win/loss interviews, Mike sends a formal messaging review request to PMM within 14 days.

---

## FAILURE MODE ANALYSIS

What happens when the triage system fails? These are the documented failure modes, their root causes, and the detection/recovery path for each.

### Failure Mode 1: Alert Fatigue — Too Many P0s

**What it looks like:** Mike is getting P0 Telegram alerts multiple times per day, most of which don't require immediate action. He starts ignoring them.

**Root cause:** P0 threshold too low (currently 0.75), or VIP boost is over-triggering, or keyword list is too broad.

**Impact:** When real P0s arrive, they're ignored. A genuine crisis or competitive event gets missed. This is the CI equivalent of a car alarm nobody responds to.

**Detection:** Track P0 alert rate. If P0 > 3/day on average, the threshold needs adjustment.

**Recovery:**
1. Raise P0 threshold from 0.75 to 0.80
2. Review VIP_SENDERS list — remove anyone who shouldn't trigger interrupts
3. Prune URGENT_KEYWORDS list — remove words that appear frequently without being actionable
4. Consider splitting P0 into "interrupt" vs. "urgent-but-async" sub-tiers

---

### Failure Mode 2: Silent Priority Inversion — Important Signals Stuck at P2

**What it looks like:** A major Epic announcement or competitive move arrives as a P2 (morning brief inclusion), when it should have been surfaced immediately. Mike finds out at 6 AM the next day that a competitor announced something major the prior afternoon.

**Root cause:** Competitive signal keywords aren't matching. Either the announcement used phrasing not in the Birch rubric, or the signal came through a channel with low source weight (GitHub, system alert), or the competitor name isn't in the rubric.

**Impact:** Oracle Health's competitive response is delayed by 12-24 hours. The sales team walks into meetings without knowing about it.

**Detection:** Periodic audit — compare actual high-impact competitive events in the last 30 days with what tier they actually received. Any Tier 2/3 that should have been Tier 1 is a failure.

**Recovery:**
1. Update Birch rubric keyword list with missed terminology
2. Add missed competitor variants to the competitor name list
3. Consider adding a "competitive events" source with elevated source weight (0.90+)

---

### Failure Mode 3: False Champion — Wrong People on VIP List

**What it looks like:** Emails from people who aren't actually key to Mike's work keep triggering VIP boosts, crowding out genuine priority signals.

**Root cause:** VIP_SENDERS list hasn't been reviewed since it was set. Org changes have made some previous VIPs less relevant.

**Impact:** Noise in P0/P1 tier. Real priorities get buried.

**Detection:** Monthly review of VIP list. Ask: "When was the last time a message from [person] actually required immediate action?"

**Recovery:** Monthly VIP list review (per calibration cadence). Remove or downgrade anyone who hasn't triggered a genuine P0/P1 in 60+ days.

---

### Failure Mode 4: Recency Blind Spot — Stale Signal Accumulation

**What it looks like:** After a long weekend or holiday, the system has queued up dozens of signals. The half-life decay hasn't reduced them enough to prevent signal overload on Monday morning.

**Root cause:** 48-hour half-life is appropriate for normal operation but creates a Monday morning pile-up after weekend + holiday gaps.

**Impact:** Monday morning brief is overwhelming. Important signals from Friday are diluted by lower-priority signals that haven't decayed enough.

**Detection:** Monitor Monday brief length vs. Wednesday brief length. If Monday is consistently 3x longer, decay calibration may need adjustment for weekend periods.

**Recovery:** Consider time-of-week awareness in the decay function — accelerate decay over weekends for non-VIP signals. Or implement a "catch-up mode" that surfaces only genuine P0/P1 items for first 2 hours of Monday morning.

---

### Failure Mode 5: Competitive Response Disconnected from Triage

**What it looks like:** Tier 1 competitive signals are correctly identified but the `competitive-response` routing doesn't actually trigger a response — the signal goes into monitoring and nothing happens.

**Root cause:** The triage system routes correctly, but there's no human or agent who is accountable for acting on Tier 1 signals when Mike is unavailable.

**Impact:** The most important competitive intelligence in the system is effectively ignored when Mike is in meetings, traveling, or in a focus block.

**Recovery:** Define explicit SLA for Tier 1 signal response: any Tier 1 competitive signal must produce a draft response recommendation within 4 business hours, even if Mike can't review it until later. The response is staged, not sent — but it exists and is ready.

---

## SUCCESS METRICS AND KPIs

### Operational Health Metrics (Jake monitors, reports weekly)

| Metric | Target | Warning Level | Critical Level |
|--------|--------|--------------|----------------|
| **P0 alert rate** | 0-2 / day | 3-4 / day | 5+ / day (alert fatigue risk) |
| **P0 false positive rate** | < 20% | 21-35% | > 35% (threshold recalibration needed) |
| **P1 signal capture rate** | > 90% of genuine P1s appear in brief | 80-90% | < 80% (systematic miss) |
| **Tier 1 competitive signal response time** | < 4 hours | 4-8 hours | > 8 hours (competitive exposure) |
| **Signal processing latency** | < 5 minutes from arrival to scored | < 15 min | > 15 min (daemon health check) |
| **Birch Tier 1 signal volume** | 1-5 / week | < 1 / week (keywords stale) | > 10 / week (over-triggering) |
| **Nervous System uptime** | 99%+ | 95-99% | < 95% (daemon restart needed) |

### Strategic Impact Metrics (Mike tracks quarterly)

| Metric | Definition | Target |
|--------|-----------|--------|
| **Matt brief accuracy rate** | % of Tier 1 signals that Matt acts on vs. discards | > 70% act-on rate |
| **Competitive response lead time** | Time from competitor announcement to Oracle Health response ready | < 24 hours for P0 events |
| **Pre-meeting intel delivery rate** | % of finalist meetings where competitive profile updated < 48 hours prior | > 85% |
| **Intelligence-to-action conversion** | % of surfaced Tier 1 signals that result in documented action | > 60% |
| **False urgency rate** | P0 signals flagged as "not actionable" on review | < 20% |

### External Benchmark Comparison

| Benchmark | Oracle Health Target | Industry Standard | Source |
|-----------|---------------------|-------------------|--------|
| CI team response time to breaking competitive events | < 4 hours | 24-48 hours (most teams) | Klue State of CI (2025) |
| % of deals with competitive profile updated before finalist meeting | 85%+ | ~45% (average CI team) | Crayon State of CI Report |
| Signal-to-insight cycle time | < 24 hours | 3-7 days (manual teams) | Crayon + Klue benchmarks |
| Battlecard utilization rate (sales team using materials) | 70%+ | ~40% (industry average) | Klue 2025 Trends |

**Competitive teams that achieve "high signal responsiveness" (sub-24-hour insight cycles) report 18-22% higher competitive win rates than teams with 3+ day cycles** (Dzreke & Dzreke, 2025). The triage system's primary KPI is not technical — it is whether it produces competitive wins.

---

## REVISION HISTORY

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-03-22 | 1.0 | Initial SOP documenting existing automated system | Jake + Mike |
| 2026-03-22 | 2.0 | Added strategic framing (revenue → win rate connection), failure mode analysis (5 modes), success metrics/KPIs, external benchmark comparison | Jake |

---

## SOURCE ATTRIBUTION

This SOP documents Mike's signal triage system as implemented in code:
1. **Priority Engine** (`jake_brain/priority.py`) — multi-factor urgency scoring with VIP detection, recency decay, and imminence boosting
2. **Birch Scorer** (`birch/scorer.py`) — 3-axis competitive intelligence signal scoring
3. **Nervous System** (`jake_brain/nervous/email_alert.py`) — real-time email monitoring with Graph API + osascript fallback
4. **Morning Brief Pipeline** (`scripts/brain_morning_brief.py`) — daily synthesis and delivery
5. **SCIP Intelligence Cycle** — industry standard for signal classification and routing
6. **Matt Cohlmia's "So What" framework** — every signal must answer What Happened / Why It Matters / What We Should Do
