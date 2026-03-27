# SOP-32: Hiring & Talent Acquisition (Startup)

**Owner**: Mike Rodgers
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-24
**Category**: Startup / Venture Operations
**Priority**: P1 — Every early hire is a co-founder-level decision
**Maturity**: Documented (this SOP)
**Applies to**: TransformFit, Alex Recruiting App, any venture hiring its first 10 employees/contractors

---

## 1. Purpose

Govern the full hiring lifecycle for early-stage ventures: role definition, sourcing, evaluation, offer, and onboarding — designed for a founder-CEO who is recruiting without a dedicated HR function.

**Core principle**: In early-stage startups, a single bad hire in the first 10 people can destroy the company. Conversely, one exceptional hire can 3x the trajectory. No SOP shortcut is worth compromising hiring standards.

**Framework basis**: Who: The A Method for Hiring (Geoff Smart & Randy Street), Lou Adler's Performance-Based Hiring, Ben Horowitz's "wartime CEO" talent bar standard, and first-principles engineering hiring frameworks from Stripe and Linear.

---

## 2. Scope

### 2.1 In Scope

- Contractor and part-time hire decisions (the primary early-stage mode)
- Full-time hire decisions (significant capital commitment — require fundraising trigger per SOP-31)
- Role definition, scorecard creation, and hiring rubric development
- Interview process design and evaluation
- Offer construction and compensation benchmarking
- 30-day onboarding checklist

### 2.2 Out of Scope

- Oracle Health hiring (different process, HR system, and compliance framework)
- Jacob's college recruiting (SOP: alex-recruiting-outreach recipe)
- Vendor selection (treated as procurement, not hiring)

---

## 3. PHASE 1: Define the Role Before You Post It

### 3.1 The Hiring Hypothesis

Before opening a role, complete this form:

```
HIRING HYPOTHESIS
------------------
Role title: [specific — not "Full Stack Dev", say what they'll actually do]
Venture: [which startup]
Employment type: Contractor / Part-time / Full-time
Start: [target date]
Budget: $[X]/hour OR $[X]/month OR $[X] total project

BUSINESS CASE:
1. What specific outcome will this person own?
   [1-2 sentences — not activities, outcomes]

2. What is the revenue/growth impact if we DON'T hire this role?
   [Be specific: "Growth is blocked by X" or "We ship 2x slower without Y"]

3. What is the 90-day success measure for this hire?
   [What does "great" look like in 90 days?]

4. Could this be automated instead of hired?
   [YES → build automation first. NO → proceed.]

5. Could this be a contractor first?
   [Default: YES unless the work requires deep context / full attention]
```

**Rule**: If you cannot answer questions 1–3 clearly, do not open the role.

### 3.2 The Role Scorecard

Adapted from Who (Smart & Street):

```
ROLE SCORECARD: [Title]
------------------------
MISSION: [Single sentence — what this role exists to accomplish]

OUTCOMES (what they must achieve in first 12 months):
1. [Specific, measurable outcome — not task]
2. [Specific, measurable outcome]
3. [Specific, measurable outcome]

COMPETENCIES (8 max — rank-ordered):
1. [Critical] [competency name] — [what it looks like in behavior]
2. [Critical] [competency name]
3. [Critical] [competency name]
... 
(mark top 3 as "Critical", rest as "Important")

CULTURE/OPERATING STYLE REQUIREMENTS:
- [Specific to your venture stage and style — e.g., "Thrives with ambiguity", "Ships fast over perfect first draft"]

DISQUALIFIERS (deal-breakers — 3 max):
- [Specific behavior or track record that = immediate no]
```

---

## 4. PHASE 2: Sourcing

### 4.1 Source Tier Priority

| Tier | Channel | Why |
|------|---------|-----|
| **Tier 1** | Warm referrals from trusted network | 3x lower time-to-hire, better fit signal |
| **Tier 2** | Communities (Discord, Slack groups) matching role | Pre-qualified interest + culture signal |
| **Tier 3** | LinkedIn (targeted outbound, not inbound posts) | Reach + specificity when Tier 1/2 exhausted |
| **Tier 4** | Job boards (Indeed, Wellfound for startups) | Volume play — lower signal quality |

**For technical roles**: Toptal, Arc.dev, and Lemon.io for vetted contractor pools. Worth the premium for early hires — bad technical hires are expensive to unwind.

**Warm network activation template**:

```
Hey [name],

I'm hiring a [role] for [venture name] — [one sentence on what the venture does].

Looking for someone who [1 key competency]. The work is [contractor/part-time/full-time],
roughly [time commitment], [remote/location], paying [range].

Do you know anyone who'd be great? Or is this something you'd want to hear more about?

[Mike]
```

### 4.2 Contractor First Principle

For every hire except co-founders:
1. Start with a paid 2-week project ($500–$1,500 typical)
2. Treat it as a full evaluation — does their work quality, communication, and initiative match the scorecard?
3. Convert to ongoing engagement only if the trial passes

**This is not exploitative** — frame it upfront: "We use paid trial projects for all early hires. It's a chance for both of us to evaluate fit before committing."

---

## 5. PHASE 3: Interview Process

### 5.1 Interview Structure (3-Step for Contractors, 4-Step for Full-Time)

**Step 1: Screen (30 min, async or video)**
- Goals: Does the candidate meet the basic scorecard? Is there a communication / personality disqualifier?
- Format: 5 questions covering background + 1 scenario question
- Decision: Advance or pass — this should take 30 min max

**Step 2: Work Sample / Technical Test (paid, 2–4 hours)**
- Goals: Can they actually do the work?
- Format: A realistic mini-project representing 10% of the actual job
- Payment: $75–$150 for their time (respect their investment)
- Evaluation: Score against scorecard outcomes, not vibes

**Step 3: Structured Behavioral Interview (45–60 min, video)**
- Goals: Evidence that they've hit the scorecard outcomes before
- Format: STAR method (Situation, Task, Action, Result) for each Critical competency
- Decision: Score each Critical competency 1–4 before making any offer

**Step 4 (Full-time only): Reference Checks (30 min × 2–3 refs)**
- Call the actual manager, not just someone who liked them
- Key question: "Would you hire [name] again? Tell me about a time they fell short."
- Red flag: Hesitation on "would you hire again" is a no regardless of words used

### 5.2 Structured Interview Question Bank

**For technical/product hires:**
- "Tell me about a product or feature you shipped from start to finish. What went wrong and how did you handle it?"
- "Describe the most complex technical decision you've made. How did you frame the tradeoffs?"
- "Tell me about a time you had to push back on a product requirement. What happened?"

**For growth/marketing hires:**
- "Walk me through a campaign you ran. What were the before/after metrics?"
- "Tell me about a growth channel that failed. What did you learn?"
- "How do you decide where to spend a $5K/month paid acquisition budget across channels?"

**Universal:**
- "Tell me about your biggest professional failure. What was your role and what did you change afterward?"
- "What are you working on that nobody asked you to?"
- "What would your last manager say is your biggest weakness?"

### 5.3 Scoring Rubric

| Score | Definition |
|-------|-----------|
| 4 — Exceptional | Specific, detailed evidence. Outcome achieved was exceptional. Would hire this person above most. |
| 3 — Strong | Clear evidence. Outcome was solid. Would hire into this role comfortably. |
| 2 — Adequate | Some evidence but thin or vague. Some doubt about ability to perform consistently. |
| 1 — Weak | No clear evidence. Candidate could not demonstrate this competency. |

**Hiring threshold**: Average score ≥ 3.0 on all Critical competencies AND no single Critical competency below 2.

---

## 6. PHASE 4: Offer and Onboarding

### 6.1 Offer Construction

| Component | Guidance |
|-----------|---------|
| **Cash comp** | Benchmark with Levels.fyi, Glassdoor, Radford (for full-time); market rate for contractors |
| **Equity (full-time)** | Standard YC guidance: 0.1–1.5% for early employees depending on role + stage. Use 4-year vest, 1-year cliff. |
| **Scope** | Write exactly what they own — prevents scope creep disputes |
| **Success criteria** | 30/60/90 day objectives tied to scorecard |
| **Communication** | How you communicate, meeting cadence, async expectations |

**Offer document format (contractor)**:

```
ENGAGEMENT AGREEMENT — [Name] x [Venture]
Start: [date]
Duration: [trial period / ongoing]
Rate: $[X]/hour OR $[X]/project
Scope: [specific deliverables and what's out of scope]
IP Assignment: All work product created for [Venture] is owned by [Venture]
Payment terms: Net-15 on invoice
Communications: [async first / X check-ins / Slack/Telegram]
```

### 6.2 30-Day Onboarding Checklist

| Day | Action | Owner |
|-----|--------|-------|
| Day 1 | Share access (GitHub, docs, Notion/Markdown, Telegram) | Mike |
| Day 1 | Walk through the venture: mission, current status, 90-day goals | Mike |
| Day 1 | Assign first small task with clear deliverable and deadline | Mike |
| Day 3 | First check-in: any blockers? Questions? | Mike |
| Day 7 | Review first deliverable — give specific feedback | Mike |
| Day 14 | "What do you wish you had known on Day 1?" debrief | both |
| Day 30 | 30-day review: score against scorecard, discuss going forward | both |

---

## 7. Output Artifacts

| Artifact | Location |
|----------|----------|
| Role scorecard | ~/Startup-Intelligence-OS/docs/ventures/[venture]/team/roles/[role]-scorecard.md |
| Interview scorecard (per candidate) | team/interviews/[name]-[date].md |
| Active roster | team/roster.md |
| 30-day onboarding doc | team/onboarding/[name]-onboarding.md |

---

## 8. Quality Checks

| Checkpoint | Standard | Owner |
|-----------|----------|-------|
| No role opened without completed scorecard | Scorecard exists before posting | Mike |
| Work sample included in every process | No hire based on interviews alone | Mike |
| Critical competencies all scored ≥ 2 | Explicit score sheet reviewed | Mike |
| References called for full-time hires | At least 2 direct manager references | Mike |
| 30-day onboarding checklist initiated Day 1 | Calendar items set before start date | Mike |

---

## 9. Revision History

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-03-24 | 1.0 APPROVED | Initial SOP — WS3 Foundation Layer completion | Jake (Dust Star 25X) |

---

## 10. Source Attribution

1. **Geoff Smart & Randy Street** — Who: The A Method for Hiring (2008) — scorecard, structured behavioral interview, reference check methodology
2. **Ben Horowitz** — The Hard Thing About Hard Things (2014) — hiring bar standards, "wartime CEO" talent philosophy
3. **Lou Adler** — Performance-Based Hiring (2004) — outcome-based role definition (SMART objectives)
4. **Gergely Orosz** — Engineering hiring practices (The Pragmatic Engineer newsletter) — technical work sample best practices
5. **YC Startup School** — Early-stage hiring advice, equity benchmarks, founder-as-recruiter frameworks
