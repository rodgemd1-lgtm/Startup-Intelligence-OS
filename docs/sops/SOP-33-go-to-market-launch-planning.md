# SOP-33: Go-to-Market Launch Planning

**Owner**: Mike Rodgers
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-24
**Category**: Startup / Venture Operations
**Priority**: P0 — A great product without GTM is a hobby project
**Maturity**: Documented (this SOP)
**Applies to**: TransformFit launches, Alex Recruiting product updates, any venture public-facing release

---

## 1. Purpose

Govern the structured process for bringing a product or major feature to market: audience targeting, channel selection, messaging development, launch mechanics, and post-launch iteration. This SOP ensures that launch effort is preceded by strategy and followed by measurement.

**Core principle**: A GTM launch is not a marketing event — it is a hypothesis test. You are testing whether your message reaches the right people through the right channels and converts them into users at a sustainable CAC. Every launch produces data that improves the next launch.

**Framework basis**: Geoffrey Moore's Crossing the Chasm (beachhead market), April Dunford's Obviously Awesome (positioning), Dave Gerhardt's B2C/DTC launch playbooks, and Product Hunt launch methodology.

---

## 2. Scope

### 2.1 In Scope

- Initial product launch (v1.0 / alpha / beta)
- Major feature launches (new AI coach, new product tier, new market segment)
- Re-launches after pivots
- Seasonal campaign launches (e.g., New Year fitness campaign for TransformFit)

### 2.2 Out of Scope

- Oracle Health go-to-market (enterprise GTM, governed by Oracle's field marketing)
- Ongoing content marketing (covered by viral-architect-content recipe)
- Paid acquisition optimization (ongoing, not launch-specific)

---

## 3. PHASE 1: GTM Strategy (3–4 Weeks Before Launch)

### 3.1 Positioning Document

Before writing any copy or building any campaign, write the positioning statement. Based on April Dunford's *Obviously Awesome* framework:

```
POSITIONING STATEMENT: [Venture] — [Product/Feature]
Last updated: [date]

1. BEST-FIT CUSTOMERS
   Who: [Specific segment — 1 sentence, as specific as possible]
   WHY they're our beachhead: [Why this segment is easiest to win AND
   positions us to expand later]

2. MARKET CATEGORY
   We belong in: [What market are we COMPETING in? This shapes buyer expectations.]
   Trend powering us: [What tailwind makes this the right time?]

3. UNIQUE VALUE (what we do better than alternatives for our best-fit customers)
   - [Specific, differentiated claim — not "easy to use", something defensible]
   - [Second differentiated claim]

4. COMPETITIVE ALTERNATIVES (what buyers use instead of doing nothing)
   - [Alternative 1] — our angle: [why we win against this]
   - [Alternative 2] — our angle: [why we win against this]

5. VALUE ATTRIBUTES (proof that our unique value is real)
   - [Specific evidence, result, or feature that proves claim 1]
   - [Specific evidence, result, or feature that proves claim 2]

6. THE HEADLINE TEST
   If a prospective customer read ONE sentence about us, what would make them say
   "I need to know more"?
   → [Write it]
```

### 3.2 Channel Plan

For each launch, select 2–3 primary channels max. Spreading across 6 channels is the most common early-stage GTM mistake.

| Channel | Best For | CAC Range (B2C) | Time to Results |
|---------|---------|-----------------|-----------------|
| Instagram Organic | Fitness, lifestyle, B2C with visual product | Near-zero (time cost) | 4–8 weeks |
| Instagram Paid | B2C, proven creative angle | $15–$60 | Days |
| TikTok Organic | Under-35 B2C, viral potential | Near-zero | Unpredictable |
| Email List | Existing warm audience | Near-zero | Immediate |
| Product Hunt | B2B, developer, tech-savvy consumers | Near-zero | Launch day spike |
| Referral/Word-of-mouth | Any — requires delightful product | Near-zero | Slow build |
| Community (Discord/Reddit/Facebook Group) | Niche audiences with existing gathering | Near-zero | Medium |
| LinkedIn | B2B, professional services | $40–$150 | Weeks |

**Channel selection criteria for TransformFit**: Instagram organic + paid (35K followers = owned asset), email list, referral program.

**Channel selection criteria for Alex Recruiting**: Direct outreach to families + LinkedIn + football coach networks.

### 3.3 Messaging Architecture

Build a 3-tier message hierarchy:

```
TIER 1 — THE CORE MESSAGE (one sentence, used everywhere)
[The single most important thing we want the market to know]

TIER 2 — PROOF POINTS (3 claims that support the core message)
- [Claim 1 + evidence]
- [Claim 2 + evidence]
- [Claim 3 + evidence]

TIER 3 — CHANNEL-SPECIFIC ADAPTATIONS
- Instagram caption version (150 words max, hook first)
- Email subject line options (5 variants for A/B testing)
- Short bio / profile description version (50 words)
- Spoken version for DMs and voice messages
```

---

## 4. PHASE 2: Pre-Launch Build (2 Weeks Before Launch)

### 4.1 Pre-Launch Checklist

| Asset | Status | Owner |
|-------|--------|-------|
| Landing page live and functional | ☐ | Mike / engineer |
| Onboarding flow tested (happy path + 3 edge cases) | ☐ | Mike |
| Pricing page live with CTAs tested | ☐ | Mike / engineer |
| Payment processing end-to-end tested | ☐ | Mike |
| Welcome email / onboarding email sequence live | ☐ | Mike |
| Mobile experience validation | ☐ | Mike |
| Analytics tracking (Posthog or Mixpanel) live | ☐ | engineer |
| Error monitoring (Sentry) live | ☐ | engineer |
| Support channel ready (email / Telegram / chat) | ☐ | Mike |
| Legal: Terms of Service and Privacy Policy live | ☐ | Mike |

### 4.2 Waitlist Warm-Up (for planned launches with a list)

1–2 weeks before launch, send a warm-up sequence to your waitlist:

```
Email 1 (D-14): "Something's coming — here's why we're building it"
  → Tell the origin story. Why does this product need to exist?
  → Ask: "What's your biggest challenge with [problem]?" (reply to this email)

Email 2 (D-7): "Here's a sneak peek — and we need your help"
  → Show a feature or screenshot. Ask for feedback.
  → "You're on the early access list. Launch is [DATE]."

Email 3 (D-1): "Tomorrow. You're in."
  → Clear instructions for what to do at launch.
  → Create urgency: early access pricing / beta cap / exclusive bonus.
```

---

## 5. PHASE 3: Launch Day Execution

### 5.1 Launch Day Run-of-Show

| Time | Action |
|------|--------|
| T-60 min | Final QA check: landing page, payment, onboarding, analytics |
| T-30 min | Prepare all social posts, emails, community messages (drafted, not sent) |
| T-0 | Flip the switch: post on all channels simultaneously |
| T+0 to T+4h | Monitor in real-time: signups, errors, support questions |
| T+4h | First metrics snapshot: conversion rate, error rate, support volume |
| T+24h | End-of-day analysis (see Phase 4) |

### 5.2 Launch Day Content Calendar

| Channel | Content | Type | Time |
|---------|---------|------|------|
| Email list | Launch email with CTA | Broadcast | T-0 |
| Instagram | Hero post with link in bio | Organic | T-0 |
| Instagram Story | Swipe-up to sign up / "We're live" | Story | T+1h |
| Telegram (personal) | Personal note to warm contacts | Direct | T+1h |
| Communities | Thoughtful post (not spam) | Community | T+2h |

### 5.3 Real-Time Monitoring (Launch Day)

Track these metrics hourly on launch day:

```
LAUNCH DAY METRICS DASHBOARD
-----------------------------
Hour 1:   Signups: ___ | Conversion rate: ___% | Errors reported: ___
Hour 4:   Signups: ___ | Conversion rate: ___% | Revenue: $___
Hour 8:   Signups: ___ | Conversion rate: ___% | Top traffic source: ___
Hour 24:  Signups: ___ | Conversion rate: ___% | DAU: ___ | Revenue: $___

FUNNEL:
Landing page visits:  ___
→ Trial starts:       ___ (conv: __%)
→ Onboarding complete: ___ (conv: __%)
→ Day-1 retained:     ___ (conv: __%)
```

---

## 6. PHASE 4: Post-Launch Analysis (Days 1–14)

### 6.1 Week 1 Analysis

Run 7 days post-launch:

```
LAUNCH PERFORMANCE ANALYSIS — [Venture] [date]

HYPOTHESIS: We expected [X users] at [Y% conversion] through [Z channels]
RESULT: [What actually happened]

WHAT WORKED:
- [Channel / message / anchor that outperformed]

WHAT DIDN'T WORK:
- [What underperformed and hypothesis for why]

USER BEHAVIOR SURPRISES:
- [Anything unexpected in the funnel or activation data]

NEXT ACTIONS:
1. [Double down on what worked]
2. [Kill or fix what didn't]
3. [Run next experiment: ...]
```

### 6.2 Activation Milestone (Day 7 → Day 30)

Track the path from signup to "I got value":

| Milestone | Metric | Target |
|-----------|--------|--------|
| Day 1 retention | % who come back on Day 1 | >40% |
| Core action completion | % who complete [key action] in Day 1 | >60% |
| Day 7 retention | % who are active on Day 7 | >20% |
| Day 30 retention | % who are active on Day 30 | >10% |
| First revenue event | % who start a trial or purchase | >8% |
| Referral action | % who share or invite someone | >5% |

**If Day 1 retention < 30%**: There is an activation problem. Do not spend on paid acquisition. Fix activation first.

---

## 7. Output Artifacts

| Artifact | Location |
|----------|----------|
| Positioning document | ~/Startup-Intelligence-OS/docs/ventures/[venture]/gtm/positioning-[version].md |
| Channel plan | gtm/channel-plan-[launch-name].md |
| Launch run-of-show | gtm/launch-[YYYY-MM-DD]-runsheet.md |
| Post-launch analysis | gtm/launch-[YYYY-MM-DD]-analysis.md |
| Messaging bank | gtm/messaging-[version].md |

---

## 8. Tools and Systems

| Tool | Purpose |
|------|---------|
| Jake brain_search | Load customer discovery findings, prior launch learnings |
| viral-architect-content recipe | Content generation for launch posts |
| Posthog / Mixpanel | Funnel analytics and launch day monitoring |
| Resend / Mailchimp | Email launch campaigns |
| Instagram | Primary organic distribution (TransformFit) |
| Claude Code | Draft positioning documents, email sequences, launch copy |
| Telegram (Jake) | Real-time launch day metric updates |

---

## 9. Quality Checks

| Checkpoint | Standard | Owner |
|-----------|----------|-------|
| Positioning document written before any copy | File exists and is dated | Mike |
| ≤ 3 channels selected for launch | Channel plan lists max 3 primary | Mike |
| Full pre-launch checklist complete 48h before launch | All items checked | Mike |
| Analytics and error monitoring live before launch | Verified in staging | Mike / engineer |
| Day-1 retention ≥ 30% before paid acquisition spend | Metric confirmed | Mike |
| Post-launch analysis completed within 7 days | File exists | Mike |

---

## 10. Revision History

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-03-24 | 1.0 APPROVED | Initial SOP — WS3 Foundation Layer completion | Jake (Dust Star 25X) |

---

## 11. Source Attribution

1. **April Dunford** — Obviously Awesome (2019) — positioning framework for category design
2. **Geoffrey Moore** — Crossing the Chasm (1991, revised 2014) — beachhead market strategy, technology adoption lifecycle
3. **Andrew Chen** — The Cold Start Problem (2021) — network effects, launch mechanics for products with network dynamics
4. **Sean Ellis** — Hacking Growth (2017) — activation, retention, and growth loop methodology
5. **Dave Gerhardt** — Founder-led marketing playbooks (DGMG community) — DTC/B2C launch frameworks
6. **Lenny Rachitsky** — Lenny's Newsletter — retention benchmarks, activation metrics, channel selection data
