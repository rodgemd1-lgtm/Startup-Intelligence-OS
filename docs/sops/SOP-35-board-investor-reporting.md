# SOP-35: Board & Investor Reporting

**Owner**: Mike Rodgers
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-24
**Category**: Startup / Venture Operations
**Priority**: P1 — Investor trust is built monthly, lost in one missed update
**Maturity**: Documented (this SOP)
**Applies to**: Any venture post-first investment (TransformFit seed, future raises)

---

## 1. Purpose

Standardize the format, cadence, and content of investor and board communications so that:
1. Mike never has to think about what to say — the structure is pre-built
2. Investors receive regular, honest updates that build trust even when results are mixed
3. Board meetings are productive strategy sessions, not surprise-and-defend exercises

**Core principle**: The investor update you dread sending is the most important one to send. Bad news delivered early with a plan is recoverable. Bad news discovered by investors on their own is not.

**Framework basis**: Fred Wilson's (Union Square Ventures) monthly update format, Sequoia's board meeting structure, Sam Altman's investor update guidelines, and David Skok's SaaS metrics reporting standards.

---

## 2. Scope

### 2.1 In Scope

- Monthly investor update emails (all ventures with investors)
- Quarterly board meeting preparation and facilitation
- Ad hoc investor communication (material events, pivots, fundraising)
- Cap table and equity management documentation

### 2.2 Out of Scope

- Oracle Health board/executive reporting (SOP-03: Weekly Executive Briefing, SOP-14: Executive Offsite)
- Personal financial reporting
- Pre-investor customer discovery updates (SOP-29)
- Fundraising pitch materials (investor-prep recipe)

---

## 3. PHASE 1: Monthly Investor Update (Due: First Monday of Each Month)

**Time required**: 45–60 minutes to write well
**Distribution**: Email, with PDF attachment for formal record

### 3.1 The Fred Wilson Monthly Update Format

This format, pioneered by USV, is the gold standard for early-stage investor updates. It takes 45 minutes to write and 5 minutes to read — that ratio is intentional.

```
SUBJECT LINE: [Venture] Investor Update — [Month Year]

---

Hi all,

[1 sentence on where we are. Be direct — not "exciting progress", just the fact.]

KEY METRICS:
| Metric | This Month | Last Month | MoM Change |
|--------|-----------|------------|------------|
| MRR | $X | $X | +/- % |
| Active Users | X | X | +/- % |
| Churn Rate | X% | X% | +/- pp |
| [Primary growth metric] | X | X | +/- % |
| Cash Balance | $X | $X | X months runway |

THE WINS:
1. [Specific win — what happened, why it matters, number if possible]
2. [Second win]
3. [Third win — can be small, but be specific]

THE CHALLENGES:
1. [Specific challenge — honest, with your hypothesis for why]
2. [Second challenge]
(Note: This section is what differentiates great founder communicators from the rest.
Investors who never hear about problems lose trust when problems become crises.)

WHAT WE'RE FOCUSED ON NEXT MONTH:
1. [Specific goal with measurable outcome]
2. [Specific goal]
3. [Specific goal]

ASKS — I NEED HELP WITH:
1. [Specific ask — intro to X, feedback on Y, a connection to Z]
(This is the most underused section. Investors want to help. Give them specific asks.)

[Mike]
```

### 3.2 Metrics to Track for SaaS Products

**Reference SOP-31 (Financial Modeling) for data sources.** Pull these metrics for each update:

| Category | Metrics |
|----------|---------|
| Revenue | MRR, ARR, MRR Growth Rate, New MRR, Expansion MRR, Churn MRR |
| Engagement | DAU, WAU, MAU, DAU/MAU ratio (stickiness), Core Action Rate |
| Economics | CAC, LTV, LTV:CAC, Payback Period |
| Health | Monthly Churn Rate, Net Revenue Retention |
| Cash | Cash balance, Monthly burn, Months of runway |

### 3.3 Communication Tone Standards

| Situation | How to Communicate It |
|-----------|----------------------|
| Strong month | Share the data, name what drove it, note what's still uncertain |
| Disappointing month | Lead with the number, give honest hypothesis, state the plan |
| Pivot or major change | Call investors individually before sending the written update |
| Crisis (legal, co-founder, technical) | Call immediately — not email first |
| Missing an update deadline | Send a short note the morning it's due: "Running 3 days late — update incoming Thursday." |

---

## 4. PHASE 2: Quarterly Board Meeting

**Duration**: 2–3 hours
**Frequency**: Quarterly (aligned with calendar quarters unless otherwise agreed)
**Attendees**: Investors, any advisors with board observer rights, potentially key team members for relevant sections

### 4.1 Board Meeting Preparation (1 Week Before)

| Action | Owner | Deadline |
|--------|-------|----------|
| Write board deck (see 4.2) | Mike | D-5 |
| Send deck to board members | Mike | D-3 |
| Send pre-read questions to board | Mike | D-3 |
| Confirm attendees and logistics | Mike | D-2 |
| Prepare financial model update | Mike | D-1 |
| Create action item list template | Mike | Day of |

### 4.2 Board Deck Structure (Sequoia Format, Adapted for Early Stage)

Each section: 1–2 slides. Total deck: 12–15 slides.

```
SLIDE 1: COMPANY STATUS SNAPSHOT
  - One-line status: WHERE WE ARE TODAY
  - The 3 most important facts right now (metrics or events)
  - Energy: Are we winning? How?

SLIDES 2-3: QUARTER IN REVIEW
  - KPIs vs. last quarter and vs. plan
  - Wins (with data)
  - Misses (with honest analysis)

SLIDES 4-5: FINANCIAL SNAPSHOT
  - P&L summary (revenue, costs, net)
  - Cash position and runway
  - Financial model scenarios (base/bull/bear through 18 months)

SLIDES 6-7: PRODUCT UPDATE
  - What shipped (sprint demos reduced to 2-3 highlights)
  - What's next (roadmap, 1 quarter ahead only)
  - One key product metric trend (engagement, activation, retention)

SLIDE 8: MARKET / COMPETITIVE UPDATE
  - Any competitive threats or opportunities emerged this quarter?
  - Positioning changes?

SLIDES 9-10: THE BIG DECISIONS
  - 2-3 strategic decisions the board needs to weigh in on
  - For each: the situation, the options, Mike's recommendation
  - THIS IS THE MOST IMPORTANT PART OF THE MEETING

SLIDE 11: TEAM
  - Any hires, departures, structural changes
  - Open roles and priority

SLIDE 12: NEXT QUARTER OBJECTIVES
  - 3-5 explicit goals for the quarter
  - Metrics targets
  - What "success" looks like at the end of next quarter

SLIDE 13: ASKS
  - Specific help requests from each investor
  - Intros, expertise, network needed
```

### 4.3 Meeting Facilitation Protocol

The board meeting is a strategy conversation, not a status presentation. Handle status in the pre-read.

```
BOARD MEETING RUN-OF-SHOW
--------------------------
0:00 — 0:15: Quick financial and operational status (assume they read the deck)
0:15 — 0:45: The big decisions (this is 30 minutes minimum — the core value)
0:45 — 1:15: Strategic discussion (where should we be placing bets next?)
1:15 — 1:30: Asks and action items (capture who does what by when)
1:30 — 1:45: Any private conversations (Mike + investor 1:1 if needed)
```

**Action item capture format:**

```
BOARD MEETING ACTION ITEMS — [Date]
------------------------------------
Item: [What]
Owner: [Who — investor name or Mike]
Due: [Date]
Status: OPEN
```

---

## 5. PHASE 3: Material Event Communication (Ad Hoc)

### 5.1 What Constitutes a Material Event

Call investors (don't email first) for:
- Regulatory or legal action
- Loss of a major customer (>10% of revenue)
- Co-founder departure or serious team conflict
- Pivot decision (changing core product or market)
- Potential acquisition interest or LOI received
- Unexpected cash crisis (runway drops below 3 months suddenly)

### 5.2 Material Event Communication Template

```
Subject: [Venture] — Important Update Re: [Topic]

[Name],

I'm reaching out directly because [1 sentence on the event — factual].

What happened: [2-3 sentences. Just facts, no spin.]

My current assessment: [Your honest read of the situation]

What I'm doing about it: [Specific action plan with timeline]

Where I need your help: [1-2 specific asks]

I'll send a full written update to all investors [by DATE]. Wanted to call you first.

Mike
```

---

## 6. Output Artifacts

| Artifact | Location |
|----------|----------|
| Monthly investor updates | ~/Startup-Intelligence-OS/docs/ventures/[venture]/investors/updates/[YYYY-MM].md |
| Board decks | investors/board-meetings/[YYYY-QX]-deck.pdf |
| Board meeting notes | investors/board-meetings/[YYYY-QX]-notes.md |
| Action item tracker | investors/board-meetings/action-items.md |
| Cap table | investors/cap-table-[YYYY-MM-DD].md |

---

## 7. Tools and Systems

| Tool | Purpose |
|------|---------|
| Jake brain_search | Load prior investor context, board decisions, metric history |
| SOP-31 financial model | Data source for all financial metrics in updates |
| Claude Code | Draft investor update narrative, ensure no sugarcoating |
| Notion / Markdown | Store and version investor updates |
| Telegram (Jake) | Reminder to send update by first Monday of month |

---

## 8. Quality Checks

| Checkpoint | Standard | Owner |
|-----------|----------|-------|
| Monthly update sent by first Monday of each month | On file, distribution confirmed | Mike |
| Challenges section included (not just wins) | Present in every update | Mike |
| Board deck sent ≥ 3 days before meeting | File date-stamped | Mike |
| All board meeting action items captured and assigned | Action item doc exists | Mike |
| Material events communicated by call before email | No surprises by email | Mike |

---

## 9. Revision History

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-03-24 | 1.0 APPROVED | Initial SOP — WS3 Foundation Layer completion | Jake (Dust Star 25X) |

---

## 10. Source Attribution

1. **Fred Wilson** — Union Square Ventures blog — monthly investor update format (the gold standard since ~2012)
2. **Sequoia Capital** — Board meeting structure guidance and "company narrative" framework
3. **Sam Altman** — YC Startup School: investor update best practices (2019 lecture)
4. **David Skok** — SaaS metrics reporting for investors (ForEntrepreneurs.com)
5. **Ben Horowitz** — The Hard Thing About Hard Things (2014) — communication discipline in a company
6. **Brad Feld** — Startup Boards: A Field Guide (2013) — board meeting governance
