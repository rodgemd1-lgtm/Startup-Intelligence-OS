# SOP-30: Product Development Sprint Planning

**Owner**: Mike Rodgers
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-24
**Category**: Startup / Venture Operations
**Priority**: P1 — Governs all product build cycles
**Maturity**: Documented (this SOP)
**Applies to**: TransformFit, Alex Recruiting App, any venture reaching the build phase

---

## 1. Purpose

Define and execute 2-week product development sprints that are strategically targeted (OKR-linked), technically scoped (user stories + acceptance criteria), and quality-gated (phase gate per SOP-20) — so that every sprint advances Product-Market Fit rather than generating technical debt and misdirected features.

**Constraint**: Mike is not a full-time product manager. Sprints must be lean enough to run with 1–2 engineers and produce shippable outcomes in 10 working days.

**Framework basis**: Shape Up (Basecamp / Ryan Singer) — appetite-first sizing and betting cycles; Agile/Scrum sprint mechanics; OKR linkage from Measure What Matters (John Doerr).

---

## 2. Scope

### 2.1 In Scope

- 2-week sprint planning and execution for all active ventures
- User story writing, story pointing, and sprint backlog management
- Sprint Demo and Retrospective protocols
- Technical debt tracking and sprint health metrics

### 2.2 Out of Scope

- Feature discovery (governed by SOP-29: Customer Discovery)
- Release and go-to-market planning (governed by SOP-33)
- Infrastructure and DevOps decisions (ad hoc technical decisions)

---

## 3. PHASE 1: Sprint Betting (Friday Before Sprint Starts)

**Duration**: 30–45 minutes

### 3.1 Input Checklist

Before any sprint starts, verify these inputs exist:

| Input | Source | Required? |
|-------|--------|----------|
| Active OKR for this venture | Jake goals tracking | REQUIRED |
| Customer discovery findings | SOP-29 output | REQUIRED (if building new feature) |
| Tech debt register | GitHub Issues | Review |
| Previous sprint's unfinished work | GitHub Projects | Flag for carry-over |
| Runway check | SOP-31 output | If < 6 months runway, constraint applies |

### 3.2 The Betting Table

Use Shape Up's concept of "betting" rather than backlog grooming. For each candidate feature or fix:

```
PITCH: [Feature name]
Problem it solves: [1 sentence — from customer discovery, not assumed]
Appetite: [S=1-3 days / M=4-6 days / L=7-10 days]
OKR link: [Which Key Result does this move?]
Expected outcome: [What changes for users after this ships?]
Risks: [What could block shipping?]
Bet or Skip: BET / SKIP / HOLD
```

**Sprint capacity rule**:
- 10-day sprint = 80% capacity target (assume 20% for bugs/interrupts)
- Max 3 items per sprint (focus beats breadth)
- At least 1 item must be shippable to real users (no unshippable "foundational" sprints)

### 3.3 The Appetite-First Constraint

Before scoping what goes in a feature, decide the maximum effort you're willing to spend — the **appetite**. Then scope to fit the appetite. This is the inverse of traditional estimation, and it prevents scope creep:

> "We have appetite for a [3-day / 5-day / 10-day] solution to this problem. What can we build in that time that actually solves it?"

---

## 4. PHASE 2: Story Writing (Sprint Day 1 Morning)

**Duration**: 60 minutes

### 4.1 User Story Format

Every accepted sprint item must have:

```
STORY: As a [specific user type], I want to [do something specific] so that [I get this outcome].

ACCEPTANCE CRITERIA:
- [ ] Given [context], when [action], then [result]
- [ ] Given [context], when [action], then [result]
- [ ] Edge case: [specific edge condition handled]

OUT OF SCOPE FOR THIS STORY:
- [What we are deliberately NOT building — prevents scope creep]

DESIGN NOTES:
- [Any UX decisions already settled]
- [UI mockup link if it exists]

DEFINITION OF DONE:
- [ ] Code written and reviewed
- [ ] Tests pass (unit + integration)
- [ ] Deployed to staging
- [ ] Mike manually tested the acceptance criteria
- [ ] No new lint errors introduced
```

### 4.2 Story Sizing (T-Shirt Sizing)

| Size | Days | Use When |
|------|------|----------|
| XS | < 1 day | Bug fix, copy change, config update |
| S | 1–2 days | Single-screen UI change, single API endpoint |
| M | 3–4 days | New feature with UI + backend + tests |
| L | 5–7 days | Multi-screen flow, third-party integration |
| XL | 8–10 days | Major feature — consider breaking into 2 stories |

**If a story is XL or larger**: Break it down. If it cannot be broken down, it is an Epic — scope one sprint's worth of the Epic and stop.

---

## 5. PHASE 3: Sprint Execution (Days 1–9)

### 5.1 Daily Standup Protocol (Async)

Post in the venture's GitHub Issue or Telegram channel each morning:

```
STANDUP [venture] [date]
Done yesterday: [1-3 bullet points]
Doing today: [1-3 bullet points]
Blockers: [None / describe]
Sprint health: ON TRACK / AT RISK / BLOCKED
```

**If "AT RISK" appears**: Mike reviews same day. If a story cannot ship in this sprint, scope it down or cut it — never extend the sprint date.

### 5.2 Mid-Sprint Check (Day 5)

At the halfway point, run a 15-minute health check:

| Check | Question | Action if Failing |
|-------|---------|-------------------|
| Scope integrity | Have any stories grown since Day 1? | Cut scope to original appetite |
| Tech debt created | Any shortcuts taken that need logging? | Add to tech debt register |
| Blocker resolution | Any blocker unresolved for > 2 days? | Escalate or cut story |
| User shippability | Will anything reach real users this sprint? | If no — why? Address immediately |

### 5.3 Technical Standards (Non-Negotiable Per Sprint)

| Standard | Requirement |
|---------|------------|
| Test coverage | No net decrease from sprint start |
| Build passing | CI/CD pipeline must be green at all times |
| PR review | No self-merge without 24-hour cooling period |
| Deployment | Every completed story deployed to staging before Demo |
| Secrets | No API keys or secrets in code — vault only |

---

## 6. PHASE 4: Sprint Demo and Retro (Day 10)

### 6.1 Sprint Demo (30 minutes)

**Audience**: Mike (and any early users / stakeholders invited)

Format:
1. **What we bet on and why** (5 min) — review the sprint goals
2. **What shipped** — live demo of each completed story (15 min total)
3. **What didn't ship and why** (5 min)
4. **User reaction if available** (5 min) — any early user feedback on shipped items

**Demo rule**: Only demo working software against real acceptance criteria. No slides, no mockups as substitutes for working features.

### 6.2 Sprint Retrospective (20 minutes)

Answer three questions honestly:

```
WENT WELL (keep doing):
- [specific, actionable]

IMPROVE (change):
- [specific, one change to implement next sprint]

PUZZLED (needs discussion):
- [unresolved questions about process, tech, or product direction]

VELOCITY: [story points attempted] / [story points completed] = X% completion rate
```

**Target velocity**: >80% sprint completion rate. Below 70% two sprints in a row = revisit estimation process.

---

## 7. Output Artifacts

| Artifact | Location | Updated When |
|----------|----------|-------------|
| Sprint betting doc | ~/Startup-Intelligence-OS/docs/ventures/[venture]/sprints/YYYY-MM-DD-sprint-[N].md | Before sprint starts |
| User stories | GitHub Issues in venture repo | Sprint Day 1 |
| Daily standups | Telegram channel or GitHub comments | Each morning |
| Sprint demo notes | sprint doc addendum | Sprint Day 10 |
| Tech debt register | GitHub Issues (label: tech-debt) | Continuously |
| Velocity tracker | ventures/[venture]/velocity.md | After each sprint |

---

## 8. Tools and Systems

| Tool | Purpose |
|------|---------|
| GitHub Issues + Projects | Story tracking, tech debt register, velocity |
| Jake brain_search | Load venture context, prior decision history |
| Claude Code | Write and review user stories, check for scope creep |
| Telegram | Standup logging, sprint health alerts |
| Jake goal_checkin | Update OKR key results after sprint ships |

---

## 9. Quality Checks

| Checkpoint | Standard | Owner |
|-----------|----------|-------|
| OKR link documented for every sprint item | Present in betting doc | Mike |
| All stories have acceptance criteria before Day 1 | Verified in GitHub | Mike |
| No sprint item exceeds XL size | Break down or flag | Mike / engineer |
| Mid-sprint check completed on Day 5 | Calendar block exists | Mike |
| Demo shows working software (not slides) | Real demo, not mockup | Mike |
| Velocity tracked after every sprint | velocity.md updated | Mike |

---

## 10. Revision History

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-03-24 | 1.0 APPROVED | Initial SOP — WS3 Foundation Layer completion | Jake (Dust Star 25X) |

---

## 11. Source Attribution

1. **Ryan Singer** — Shape Up (Basecamp, 2019) — appetite-first sizing, betting table, 6-week cycles (adapted to 2-week for Mike's ventures)
2. **Jeff Sutherland & Ken Schwaber** — Scrum Guide (2020) — sprint events, definition of done, retrospective format
3. **John Doerr** — Measure What Matters (2018) — OKR linkage to sprint planning
4. **Marty Cagan** — Inspired (2018) — product discovery before delivery, user story format
5. **Martin Fowler** — Refactoring (2018) — technical standards, continuous integration principles
