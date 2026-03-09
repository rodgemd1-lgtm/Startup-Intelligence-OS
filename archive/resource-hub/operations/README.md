# Operations — Startup Ops, SOPs & Workflow Management

> OKRs, project management, documentation, and operational excellence from 0 → $10M.

---

## 1. Operating System by Stage

### Solo / Co-Founder Stage (1-5 people)
- **Tools**: Notion (wiki + tasks), Linear (if engineering-heavy), Slack
- **Process**: Weekly standup, monthly goals, async by default
- **Docs**: Lightweight — CLAUDE.md, README, decision log

### Early Team (5-20 people)
- **Tools**: Linear + Notion + Slack + Loom
- **Process**: Bi-weekly sprints, quarterly OKRs, 1-on-1s
- **Docs**: SOPs for repeatable processes, runbooks for incidents

### Growth Team (20-50 people)
- **Tools**: Full project management, HR platform, knowledge base
- **Process**: Formal OKRs, sprint ceremonies, cross-functional meetings
- **Docs**: Comprehensive wiki, onboarding playbooks, role guides

---

## 2. OKR Framework

### OKR Structure
```
Objective: [Qualitative, inspiring goal]
  KR1: [Measurable result] — [Current] → [Target]
  KR2: [Measurable result] — [Current] → [Target]
  KR3: [Measurable result] — [Current] → [Target]
```

### Example: Q1 2026 OKRs for $0-$1M Startup
```
O1: Achieve product-market fit
  KR1: 100 daily active users → 500
  KR2: NPS score 20 → 50
  KR3: 40% 30-day retention → 60%

O2: Build repeatable revenue
  KR1: $5K MRR → $30K MRR
  KR2: CAC payback < 18 months → < 12 months
  KR3: 3 case studies → 10 case studies

O3: Ship core platform features
  KR1: Launch v2.0 with 5 key features
  KR2: API uptime 99.5% → 99.9%
  KR3: Median response time 500ms → 200ms
```

### OKR Cadence
| Frequency | Activity |
|-----------|----------|
| **Annual** | Set 3-5 company-level objectives |
| **Quarterly** | Set team OKRs aligned to company goals |
| **Monthly** | Score check-in, adjust tactics |
| **Weekly** | Team review of progress |

---

## 3. Standard Operating Procedures (SOPs)

### SOP Template
```markdown
# SOP: [Process Name]

## Purpose
Why this process exists and what it achieves.

## Owner
[Role/Person responsible]

## Trigger
When this process should be executed.

## Steps
1. Step 1 — [Description] (Tool: X)
2. Step 2 — [Description]
3. Step 3 — [Description]

## Expected Output
What the completed process should produce.

## Escalation
When and how to escalate issues.

## Review Schedule
[Quarterly / As needed]
```

### Critical SOPs to Build First
| SOP | Priority | Stage |
|-----|----------|-------|
| Incident response | P0 | Day 1 |
| Deploy process | P0 | Day 1 |
| Customer onboarding | P0 | First customer |
| Bug triage | P1 | First customer |
| New hire onboarding | P1 | First hire |
| Feature request intake | P1 | $100K ARR |
| Content publishing | P2 | $100K ARR |
| Security review | P2 | Pre-SOC2 |
| Sales demo process | P2 | First AE hire |
| Quarterly planning | P2 | $500K ARR |

---

## 4. Project Management Tools

| Tool | Best For | Pricing |
|------|----------|---------|
| **Linear** | Engineering teams | $8/user/mo |
| **Notion** | All-in-one wiki + PM | Free-$10/user/mo |
| **Shortcut** | Small-medium eng teams | Free-$8.50/user/mo |
| **Asana** | Cross-functional teams | Free-$10.99/user/mo |
| **Height** | AI-native project management | $6.99/user/mo |

### Recommended: Linear + Notion
- **Linear**: Engineering tasks, sprints, roadmap, bug tracking
- **Notion**: Wiki, docs, meeting notes, SOPs, OKRs

---

## 5. Meeting Framework

### Essential Meetings Only
| Meeting | Frequency | Duration | Who |
|---------|-----------|----------|-----|
| Daily standup | Daily | 15 min | Engineering |
| Sprint planning | Bi-weekly | 60 min | Eng + Product |
| Sprint retro | Bi-weekly | 30 min | Eng + Product |
| All-hands | Monthly | 30 min | Everyone |
| 1-on-1 | Weekly/Bi-weekly | 30 min | Manager + Report |
| OKR review | Monthly | 60 min | Leadership |

### Meeting Rules
1. No meeting without an agenda
2. Default to 25 min (not 30), 50 min (not 60)
3. Async first — meeting only if async fails
4. Record and share notes (Loom + Notion)
5. "No meeting" days (e.g., Tuesday + Thursday)

---

## 6. Startup Ops Tech Stack

| Category | Tool | Purpose |
|----------|------|---------|
| **Communication** | Slack | Team messaging |
| **Video** | Loom | Async video |
| **Meetings** | Google Meet / Zoom | Live calls |
| **Docs** | Notion | Wiki, docs, SOPs |
| **Engineering** | Linear | Task management |
| **Code** | GitHub | Version control |
| **Design** | Figma | UI/UX design |
| **Analytics** | PostHog | Product analytics |
| **Monitoring** | Sentry | Error tracking |
| **Hosting** | Vercel + Railway | Deployment |
| **Email** | Google Workspace | Team email |
| **HR** | Gusto / Rippling | Payroll, benefits |
| **Finance** | Mercury + Brex | Banking, cards |
| **Legal** | Clerky | Formation docs |

---

*Compiled from live Exa AI + Firecrawl research, March 2026*
