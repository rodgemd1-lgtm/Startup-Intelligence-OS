# SOP-29: Customer Discovery Process

**Owner**: Mike Rodgers
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-24
**Category**: Startup / Venture Operations
**Priority**: P0 — No product exists without customer truth
**Maturity**: Documented (this SOP)
**Applies to**: TransformFit, Alex Recruiting, any new venture concept under Mike's portfolio

---

## 1. Purpose

Systematically discover and validate the real problems, jobs-to-be-done, and willingness-to-pay signals from target customers before building product features. This SOP prevents the most common startup failure mode: building something nobody wants.

**Governing principle**: A startup's primary job before Product-Market Fit is to be a learning machine, not a building machine. Every week of discovery that prevents a month of wrong build is a positive ROI event.

**Framework basis**: Steve Blank's Customer Development methodology (Four Steps to the Epiphany), Osterwalder's Value Proposition Canvas, Bob Moesta's Jobs-to-Be-Done (JTBD) theory, and YC's "Do Things That Don't Scale" ethos.

---

## 2. Scope

### 2.1 In Scope

- Any new feature, product line, or business model hypothesis under active development
- Pre-launch customer interviews for new ventures
- Post-launch churn interviews and usage gap analysis
- Pivot decision support (is this a pivot situation or a persevere situation?)
- Pricing and packaging validation

### 2.2 Out of Scope

- Oracle Health customer research (governed by Oracle's internal research protocols)
- Competitive intelligence (SOP-07 and SOP-12)
- Go-to-market execution (SOP-33)

### 2.3 When to Trigger This SOP

- Any new feature that would take more than 3 days to build
- Before committing to a new product domain
- When NPS drops more than 10 points quarter-over-quarter
- When churn rate exceeds 5% monthly
- When growth stalls for 3+ consecutive weeks

---

## 3. PHASE 1: Frame the Discovery Problem (Pre-Interview)

### 3.1 Define the Hypothesis

Before any call, write the falsifiable hypothesis in this format:

```
We believe [target customer segment] has [problem X].
The problem causes [pain / outcome / job-to-be-done].
They currently solve it by [current solution / workaround].
We believe they would pay [$X / switch behaviors] if we solved it [our way].
```

**Example (TransformFit):**
> We believe solo fitness coaches earning $3-8K/month have a client retention problem. The problem causes revenue volatility and burnout from manual check-ins. They currently solve it with WhatsApp groups and Google Sheets. We believe they would pay $97–$197/month if we automated personalized coaching touchpoints with AI while keeping their brand front-and-center.

### 3.2 Target Interview Profile

Define the exact profile of who to interview:

| Field | Definition |
|-------|-----------|
| **Role / Identity** | Who are they? (solo coach, gym owner, aspiring athlete) |
| **Current behavior** | What are they doing today around this problem? |
| **Motivation level** | Are they actively looking for a solution, or passively aware of the pain? |
| **Access channel** | Where do we find them? (Instagram, Reddit, LinkedIn, warm network) |
| **Disqualifiers** | Who should we NOT interview? (enterprise accounts, people with zero budget) |

**Target sample size**: 
- Discovery phase: 15–25 interviews minimum
- Validation phase: 30+ (looking for pattern saturation — when the last 5 interviews produce no new themes)

### 3.3 Build the Interview Guide

Use the Bob Moesta / JTBD structure. The goal is to find the "hiring and firing" story of solutions.

**Core questions:**
1. Walk me through the last time you tried to solve [this problem]. What happened?
2. What triggered you to look for a solution at that specific moment?
3. What did you try first? What made you stop using it?
4. Who else was involved in the decision?
5. What were you hoping for that you didn't get?
6. If [your solution] existed and worked perfectly, what would be different in your week?
7. What would make you NOT buy it, even if it worked?

**Forbidden questions (lead the witness):**
- "Would you use a product that...?" (hypothetical, not behavioral)
- "How much would you pay for X?" (abstract pricing, unreliable)
- "Is quality important to you?" (everyone says yes)

**Pricing signal questions (use instead):**
- "What are you currently paying for your workaround?"
- "If this saved you [X hours/month], how much is that worth?"
- "What would make you feel like you got a good deal vs. overpaid?"

---

## 4. PHASE 2: Conduct Interviews

### 4.1 Interview Protocol

| Step | Action | Duration |
|------|--------|----------|
| 1 | Open: introduce yourself, explain it's research not a sales call | 2 min |
| 2 | Permission: "Can I record this for my notes?" | 30 sec |
| 3 | Context: "Tell me about your [relevant role]" | 3 min |
| 4 | Core discovery: JTBD questions above | 20-30 min |
| 5 | Wrap: "What question didn't I ask that I should have?" | 2 min |
| 6 | Close: offer to share findings; ask for 2 referrals | 1 min |

### 4.2 Record and Log

For each interview, complete this log entry within 2 hours of the call (memory decay is real):

```
Interview Log Entry
-------------------
Date: YYYY-MM-DD
Interviewee: [first name + role, no last name needed for privacy]
Duration: X min
Channel: [Zoom, phone, in-person]

PROBLEM CONFIRMED: Yes / Partially / No
Top pain point stated: [verbatim quote]
Current workaround: [what they use today]
Willingness to pay signal: [$X / hour value / unclear]
Jobs-to-be-done: [1-sentence JTBD]

KEY INSIGHT:
[1-2 sentences on the most surprising thing said]

HYPOTHESIS STATUS: [Supports / Contradicts / Neutral] our hypothesis
REFERRALS: [Names, if given]
```

### 4.3 Avoid These Traps

- **Confirmation bias**: If you entered the call with a strong hypothesis, you will unconsciously steer toward confirming it. Have a devil's advocate reviewer read your notes.
- **Politeness bias**: People are nice. "That sounds interesting!" is not signal. "I would pay for this today" + followed by actually paying is signal.
- **Sample bias**: Only interviewing your warm network gives you the best-case customer. Add cold outreach to avoid survivor bias.

---

## 5. PHASE 3: Synthesize Findings

### 5.1 Theme Extraction (Affinity Mapping)

After every 5 interviews, do a synthesis pass:

1. List every distinct pain point mentioned across all interviews
2. Count frequency: how many interviewees mentioned it (n/total)?
3. Categorize by JTBD dimension: functional / emotional / social
4. Map to your hypothesis: confirms, contradicts, or introduces new direction?

### 5.2 Signal Quality Classification

| Signal Type | Description | Weight |
|-------------|-------------|--------|
| **Strong signal** | Interviewee described active behavior change or past money spent to solve this | 1.0x |
| **Medium signal** | Interviewee expressed strong frustration + described failed solutions | 0.6x |
| **Weak signal** | Interviewee agreed with your framing when prompted | 0.2x |
| **Noise** | Generic complaints without specificity or behavior change | 0.0x |

**Pivot threshold**: If strong signals support your hypothesis in fewer than 40% of interviews AND a different problem appears in 60%+ of interviews, you have a pivot signal — bring to decision framework (SOP-decision-framework).

### 5.3 The Demand Test (Beyond Interviews)

Interviews are necessary but not sufficient. Behavioral demand tests are more reliable:

| Test Type | Method | Pass Threshold |
|-----------|--------|----------------|
| **Landing page test** | Build a 1-page description, drive 200+ targeted visitors, measure email signup rate | >15% signup = strong signal |
| **Pre-order test** | Offer the product at a discount before it exists, accept payment | Any payment = real signal |
| **Concierge MVP** | Do the service manually for 5-10 users | They ask "when is the automated version ready?" |
| **Smoke test** | Run a $200 paid ad to a waitlist page | >$5 CPA on email = viable acquisition channel |

---

## 6. PHASE 4: Document and Route Findings

### 6.1 Output Artifacts

| Artifact | Template | Location |
|----------|----------|----------|
| Customer Discovery Report | [venture]-discovery-[YYYY-MM].md | ~/Startup-Intelligence-OS/docs/ventures/[venture]/discovery/ |
| Interview Log Master | [venture]-interview-log.csv | same directory |
| JTBD Map | [venture]-jtbd-map.md | same directory |
| Hypothesis Status | Updated in venture's OKR doc | goals tracking |

### 6.2 Routing Decision

After 15+ interviews with synthesis complete:

```
IF strong signals ≥ 60% AND demand test passes:
  → PROCEED to product build (trigger SOP-30)
  → Update pricing model (trigger SOP-31)
  → Flag GTM channel learnings (input to SOP-33)

IF strong signals 30-60% OR demand test inconclusive:
  → Run 10 more interviews with refined hypothesis
  → Test one demand signal (landing page or pre-order)

IF strong signals < 30%:
  → Pivot discussion: new customer segment OR new problem frame
  → Do NOT build features until hypothesis passes 40%+ threshold
```

---

## 7. Tools and Systems

| Tool | Purpose |
|------|---------|
| Jake brain_search | Load existing customer context before each call |
| Claude Code | Synthesize interview transcripts, extract themes, draft reports |
| Telegram (Jake) | Receive discovery alerts and milestone notifications |
| Apple Calendar | Schedule interview blocks |
| Notion / Markdown | Store interview logs and synthesis documents |
| Loom | Record and share call summaries |

---

## 8. Quality Checks

| Checkpoint | Standard | Owner |
|-----------|----------|-------|
| Hypothesis documented before first interview | Written, falsifiable statement exists | Mike |
| Interview guide uses behavioral questions (not leading) | No "would you" hypotheticals | Mike |
| Log completed within 2 hours of each call | Timestamp on file confirms | Mike |
| Synthesis after every 5 interviews | Pattern doc updated | Mike |
| Demand test run before product commitment | At least 1 behavioral test executed | Mike |
| Findings routed to SOP-30 / SOP-31 / SOP-33 | Cross-SOP triggers documented | Mike |

---

## 9. Revision History

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-03-24 | 1.0 APPROVED | Initial SOP — WS3 Foundation Layer completion | Jake (Dust Star 25X) |

---

## 10. Source Attribution

This SOP synthesizes methodology from:
1. **Steve Blank** — Customer Development methodology, Four Steps to the Epiphany (2005)
2. **Bob Moesta & Chris Spiek** — Jobs-to-Be-Done theory, Switch: How to Change Things When Change Is Hard framework
3. **Alexander Osterwalder** — Value Proposition Canvas, Testing Business Ideas (2019)
4. **Eric Ries** — The Lean Startup (2011) — Build-Measure-Learn loop, MVP methodology
5. **Paul Graham / YC** — "Do Things That Don't Scale" (2013); "Talk to Users" as YC's #1 advice
6. **Cindy Alvarez** — Lean Customer Development (2014) — interview protocol and sample size guidance
