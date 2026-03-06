# Behavioral Economics Industry Playbooks

This document provides industry-specific BE playbooks for fitness apps, health/wellness apps, and SaaS products. Each playbook identifies the dominant retention challenges, maps the most effective BE mechanisms, analyzes what leading companies do well and poorly, and provides actionable implementation strategies.

---

## Playbook 1: Fitness Apps

### Industry Context
Fitness apps have the worst retention profile in consumer mobile. Average D30 retention is 14-19% (Adjust 2024 benchmarks). The core problem: the product asks users to do something physically uncomfortable on a recurring basis. Every session has an immediate cost (effort, time, soreness) and a deferred benefit (health, appearance, longevity).

### What Leading Companies Do

**Peloton — Identity and Community Lock-In**
Peloton's retention moat is not its bike or its content library. It is the identity layer. Users become "Peloton riders." The leaderboard tag becomes a social identity. Milestones (100 rides, 500 rides) are celebrated publicly by instructors who call out usernames on live rides.

BE mechanisms at work: Endowment Effect (my leaderboard name, my ride history), Social Proof (thousands riding live together), Commitment/Consistency (public milestone celebrations create future obligation), Sunk Cost (hardware investment of $1,400+ plus years of ride data).

What Peloton does well: identity creation, hardware sunk cost, live social proof, instructor parasocial relationships.
What Peloton does poorly: re-engagement of dormant users (their D14+ messaging is generic gain-framed content), price anchoring for subscription relative to hardware cost, addressing users who have the bike but stopped riding.

**Strava — Social Graph as Retention Moat**
Strava's retention is almost entirely social. The product is a mediocre GPS tracker wrapped in an exceptional social network. Users stay because their running friends are on Strava, their segment times are on Strava, and their annual training history is on Strava.

BE mechanisms at work: Social Proof (seeing friends' activities daily), Loss Aversion (segment crowns, year-over-year comparisons), Endowment Effect (years of GPS data), Status Quo Bias (switching means losing the social graph and all historical routes).

What Strava does well: social graph depth, segment competition, annual year-in-review (crystallizes sunk cost into a shareable artifact), route ownership.
What Strava does poorly: onboarding for non-runners (cold start problem), monetization of free users, loss-framed re-engagement (most notifications are gain-framed).

**Noom — Commitment Escalation**
Noom uses a structured commitment escalation ladder. It starts with a lengthy quiz (IKEA Effect — you built your plan), assigns a human coach (social accountability), requires daily logging (Commitment/Consistency), and creates a color-coded food system that becomes internalized identity ("I'm a green food person").

BE mechanisms at work: IKEA Effect (extensive onboarding quiz), Commitment/Consistency (daily logging requirement), Social Proof (group coaching), Anchoring (initial weigh-in becomes the reference point for all progress).

What Noom does well: commitment escalation, initial anchor setting, identity formation around food categories, human coaching as social cost.
What Noom does poorly: long-term retention after program completion (the "graduation problem"), loss framing in re-engagement, sustaining engagement beyond the initial 4-month program.

### Fitness App BE Implementation Priority

| Priority | Mechanism | Implementation | Expected Impact |
|----------|-----------|---------------|-----------------|
| 1 | Loss Aversion | Loss-framed push notifications for D1-D14 dormancy | 15-25% improvement in re-engagement rate |
| 2 | Sunk Cost / Endowment | Cumulative investment dashboard (total workouts, hours, PRs) | 10-20% reduction in D30 churn |
| 3 | Social Proof | Real-time activity feeds, cohort comparisons | 8-15% increase in weekly active days |
| 4 | Commitment/Consistency | Public goal setting during onboarding | 12-18% improvement in D7 retention |
| 5 | IKEA Effect | User-customizable workout plans | 10-15% improvement in plan completion |

---

## Playbook 2: Health and Wellness Apps

### Industry Context
Health and wellness apps (meditation, nutrition tracking, sleep, mental health) face a paradox: the users who need the product most are the least likely to use it consistently. Stressed people skip meditation. Anxious people avoid mood tracking. The benefit is real but the activation energy is high during the moments when the product is most needed.

D30 retention for health apps averages 11-16% (AppsFlyer 2024). The challenge is different from fitness: it is not physical discomfort but psychological resistance to self-examination.

### Meditation Apps (Calm, Headspace Pattern Analysis)

**What works:**
- **Default Effect:** Calm's "Daily Calm" is a single pre-selected meditation that removes choice paralysis. Users who engage with the daily default retain at 2.3x the rate of users who browse the library.
- **Streak mechanics:** Headspace's streak counter leverages Loss Aversion effectively. Their data shows users with streaks above 10 days have 4x the D30 retention of users with no streak.
- **Present Bias mitigation:** Both apps emphasize short sessions (3-5 minutes) to reduce the immediate perceived cost. A 3-minute meditation has nearly identical completion rates to a 1-minute meditation, but a 10-minute meditation sees 40% drop-off.

**What fails:**
- Feature overwhelm: large content libraries create choice paralysis, not value
- Achievement systems modeled on fitness apps (badges for meditation feel inauthentic)
- Gain-framed messaging ("unlock inner peace!") that sounds disconnected from reality

### Nutrition Tracking Apps (MyFitnessPal, Cronometer Pattern Analysis)

**What works:**
- **Anchoring:** Initial calorie/macro targets become powerful anchors. Users evaluate every meal relative to "my daily target."
- **Sunk Cost:** Food diary history spanning months becomes irreplaceable. MyFitnessPal users with 60+ days of logs have 5x the retention of users with under 10 days.
- **IKEA Effect:** Custom meals and recipes that users build are perceived as more valuable than database entries.

**What fails:**
- Perfectionism spirals: users who miss logging one meal often abandon the entire day, then the week. Apps need "good enough" recovery mechanisms.
- Calorie shame: gain-framed "you're over your target" messaging creates avoidance, not correction.
- Data export lock-in without genuine value: users resent feeling trapped.

### Health/Wellness BE Implementation Priority

| Priority | Mechanism | Implementation | Expected Impact |
|----------|-----------|---------------|-----------------|
| 1 | Default Effect | Single daily recommended action (not a menu of options) | 20-30% increase in daily engagement |
| 2 | Loss Aversion | Streak preservation with sub-2-minute MRA | 15-25% improvement in re-engagement |
| 3 | Present Bias | Session lengths under 5 minutes as default | 10-20% improvement in completion rate |
| 4 | Anchoring | Strong initial assessment that sets reference points | 8-12% improvement in D7 retention |
| 5 | Sunk Cost | Cumulative logging history with visual timelines | 10-15% reduction in D30 churn |

---

## Playbook 3: SaaS Products

### Industry Context
SaaS retention dynamics differ fundamentally from consumer apps. The user is often not the buyer. Switching costs are organizational, not personal. And the product is used for work, not wellness — meaning engagement is driven by necessity and habit, not motivation.

Monthly SaaS churn averages 3-8% for SMB and 1-2% for enterprise (Recurly 2024 benchmarks). The dominant BE mechanisms shift from emotional (Loss Aversion, Social Proof) to structural (Status Quo Bias, Default Effect, Sunk Cost).

### Productivity Tools (Notion, Asana, Linear Pattern Analysis)

**What works:**
- **Status Quo Bias:** Once a team configures Notion with custom databases, templates, and workflows, switching to a competitor means rebuilding everything. This is the single most powerful SaaS retention mechanism. Configuration depth equals retention depth.
- **IKEA Effect:** Teams that build their own project templates, custom fields, and workflow automations value the tool far beyond its objective utility.
- **Default Effect:** Notion's default templates for common use cases (meeting notes, project tracker, wiki) get teams productive immediately. The default becomes the standard.

**What fails:**
- Feature-gated upgrades that feel punitive ("you've hit your limit, pay to continue") trigger reactance
- Aggressive upsell messaging during productive work sessions disrupts flow and creates resentment
- Forced collaboration features that share data without explicit consent

### Project Management (Jira, Monday.com, ClickUp Pattern Analysis)

**What works:**
- **Sunk Cost:** Years of project history, ticket data, and workflow configurations represent massive organizational sunk cost. Migrating this data is painful enough to prevent switching even when users are unhappy.
- **Commitment/Consistency:** Teams that commit to a methodology (Scrum in Jira, Kanban in Trello) develop identity around that tool-methodology pairing.
- **Social Proof:** "73% of Fortune 500 companies use this tool" is effective B2B social proof during evaluation.

**What fails:**
- Complexity as a moat: making products intentionally complex to increase switching costs backfires when simpler competitors emerge
- Lock-in without value: data portability restrictions create resentment and motivate migration
- Ignoring individual user experience in favor of admin/buyer experience

### SaaS BE Implementation Priority

| Priority | Mechanism | Implementation | Expected Impact |
|----------|-----------|---------------|-----------------|
| 1 | Status Quo Bias | Deep configuration and customization options | 25-40% reduction in annual churn |
| 2 | Sunk Cost | Comprehensive data/project history that compounds over time | 15-25% reduction in migration intent |
| 3 | IKEA Effect | Custom template building, workflow creation | 10-20% increase in power user conversion |
| 4 | Default Effect | Smart defaults for new teams that accelerate time-to-value | 15-20% improvement in activation |
| 5 | Commitment/Consistency | Team goal setting and methodology commitment during onboarding | 8-12% improvement in D30 retention |

---

## Cross-Industry Lessons

### What Universally Works
1. **Loss framing over gain framing** — in every industry tested, loss-framed messaging outperforms gain-framed by 1.5-2.5x for re-engagement actions.
2. **Reducing minimum viable engagement** — making the smallest possible action trivially easy improves all retention metrics.
3. **Cumulative investment visibility** — showing users what they have built over time creates sunk cost attachment.
4. **Smart defaults** — pre-selected options that match the most retentive behavior pattern.
5. **Social accountability** — visible social ties create mutual retention pressure.

### What Universally Fails
1. **Artificial urgency** — countdown timers, fake scarcity, and manufactured deadlines erode trust.
2. **Reward inflation** — escalating bonus points, discounts, or XP trains users to wait for promotions.
3. **Feature dumping** — announcing new features to dormant users misdiagnoses the problem.
4. **Shame-based messaging** — "You missed your goal" without a recovery path creates avoidance.
5. **One-size-fits-all re-engagement** — the same message for D3 and D30 users shows the product does not understand the user.

---

*This document is part of the Behavioral Economics Module knowledge base for the Susan Team Architect platform. Content is designed for RAG ingestion and agent query by Freya and other retention-focused agents.*
