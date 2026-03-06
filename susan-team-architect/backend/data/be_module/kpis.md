# Retention KPIs and Measurement Frameworks

This document provides retention benchmarks, measurement methodologies, and testing frameworks for behavioral economics interventions in fitness, health, and SaaS products. All benchmarks are grounded in industry data from AppsFlyer, Adjust, Mixpanel, Recurly, and published research.

---

## Retention Benchmarks by Category

### Fitness Apps

| Metric | Bottom Quartile | Median | Top Quartile | Elite (Top 10%) |
|--------|----------------|--------|-------------|-----------------|
| D1 Retention | 20% | 28% | 38% | 45%+ |
| D7 Retention | 10% | 16% | 24% | 32%+ |
| D14 Retention | 6% | 11% | 18% | 25%+ |
| D30 Retention | 4% | 8% | 14% | 20%+ |
| D90 Retention | 2% | 4% | 8% | 13%+ |
| Monthly Churn (Subscribed) | 15%+ | 10% | 6% | 3-4% |
| Annual Renewal Rate | 25% | 40% | 55% | 70%+ |

**Source:** Adjust Global App Trends 2024, AppsFlyer State of App Marketing 2024, supplemented by Liftoff Mobile App Trends.

**Key Insight:** The gap between median and elite D30 retention is 12 percentage points. For an app with 100,000 monthly installs, that gap represents 12,000 additional retained users per month — at typical fitness app ARPU of $15/month, that is $180,000/month in additional revenue.

### Health and Wellness Apps

| Metric | Bottom Quartile | Median | Top Quartile | Elite (Top 10%) |
|--------|----------------|--------|-------------|-----------------|
| D1 Retention | 18% | 25% | 35% | 42%+ |
| D7 Retention | 8% | 14% | 22% | 30%+ |
| D14 Retention | 5% | 9% | 16% | 22%+ |
| D30 Retention | 3% | 6% | 12% | 18%+ |
| D90 Retention | 1% | 3% | 7% | 11%+ |
| Monthly Churn (Subscribed) | 18%+ | 12% | 7% | 4% |

**Key Insight:** Health apps retain slightly worse than fitness apps at D1-D7 but show similar patterns at D30+. The initial activation hurdle is higher because the value proposition (mental health, meditation, sleep) is less tangible than visible fitness progress.

### SaaS Products

| Metric | SMB | Mid-Market | Enterprise |
|--------|-----|------------|-----------|
| Monthly Churn | 5-8% | 2-4% | 0.5-1.5% |
| Annual Churn | 30-50% | 15-25% | 5-10% |
| Net Revenue Retention | 80-95% | 100-115% | 110-135% |
| Time to First Value | 1-3 days | 1-2 weeks | 2-6 weeks |
| Feature Adoption Rate (90 days) | 15-25% | 25-40% | 35-55% |

**Source:** Recurly State of Subscriptions 2024, OpenView SaaS Benchmarks, KeyBanc Capital Markets Survey.

**Key Insight:** Enterprise SaaS achieves low churn primarily through Status Quo Bias and Sunk Cost — deep integrations, extensive customizations, and organizational dependency. SMB churn is high because these structural retention mechanisms are weak.

---

## Cohort Analysis Methodology

### Setting Up Retention Cohorts

Cohort analysis is the foundational tool for measuring retention. Every retention metric should be calculated by cohort, not in aggregate.

**Step 1: Define Cohort Boundaries**
- Standard: weekly or monthly sign-up cohorts
- Recommended: weekly cohorts for products with less than 10,000 MAU, monthly for larger
- Cohort start = first app open (not install date, not sign-up date)

**Step 2: Define Retention Events**
The retention event must be a meaningful engagement action, not just an app open.

| Product Type | Retention Event (Recommended) | Avoid Using |
|-------------|-------------------------------|-------------|
| Fitness app | Completed a workout (any length) | App open, screen view |
| Meditation app | Completed a session (any length) | App open, browsing content |
| Nutrition tracker | Logged at least one food item | App open, viewing dashboard |
| SaaS (productivity) | Created or edited a document | Login, dashboard view |
| SaaS (project mgmt) | Created or updated a task/ticket | Login, viewing a board |

**Step 3: Calculate Rolling Retention**
Use "unbounded" (rolling) retention, not "bounded" (exact day) retention.
- Bounded D7: Did the user perform the retention event on exactly Day 7?
- Unbounded D7: Did the user perform the retention event on Day 7 or any day after?

Unbounded retention is the correct metric for business decisions because it captures users who return on Day 8 or Day 10, which bounded retention misses. Bounded retention is useful for identifying exact timing patterns.

**Step 4: Segment Cohorts by Acquisition Source**
Retention varies dramatically by acquisition channel:
- Organic/word-of-mouth: typically 1.5-2x higher retention than paid
- Brand search: 1.3-1.5x higher than paid
- Paid social: baseline
- Incentivized installs: 0.3-0.5x of paid (these users often churn within D3)

Always segment retention by acquisition source before drawing conclusions about product changes.

---

## A/B Testing Framework for BE Interventions

### Test Design Principles

**Minimum Detectable Effect (MDE):**
For retention experiments, plan for MDEs of 2-5 percentage points. A test designed to detect a 1pp change in D30 retention requires sample sizes that most products cannot achieve in reasonable timeframes.

**Sample Size Calculation:**
```
n = (Z_alpha/2 + Z_beta)^2 * (p1(1-p1) + p2(1-p2)) / (p2 - p1)^2

For a typical fitness app D7 retention test:
- Baseline D7 retention (p1): 16%
- Expected improvement (p2): 20% (4pp MDE)
- Alpha: 0.05, Power: 0.80
- Required sample per variant: ~1,100 users
- Total (2 variants): ~2,200 users

For D30 retention tests:
- Baseline D30 retention (p1): 8%
- Expected improvement (p2): 11% (3pp MDE)
- Required sample per variant: ~2,400 users
- Total (2 variants): ~4,800 users
```

**Duration:** Run retention tests for at least 2x the retention window being measured. A D30 test should run for 60 days minimum to capture full cohort maturation.

### BE-Specific Testing Protocol

**Test 1: Loss-Framed vs Gain-Framed Notifications**
- Control: Current gain-framed notifications
- Variant: Loss-framed notifications (see copy_templates.md)
- Primary metric: D7 re-engagement rate among D3-dormant users
- Secondary metric: Session completion rate post-notification
- Expected lift: 15-30% improvement in re-engagement rate

**Test 2: MRA (Minimum Return Action) Effectiveness**
- Control: Standard "come back" notification with no specific action
- Variant: MRA notification with specific sub-2-minute action
- Primary metric: Notification-to-session conversion rate
- Secondary metric: MRA-to-full-session extension rate
- Expected lift: 20-40% improvement in notification conversion

**Test 3: Cumulative Investment Display**
- Control: Standard dashboard without investment summary
- Variant: Dashboard with "Your Investment" section (total workouts, hours, PRs)
- Primary metric: D30 retention rate for users with 10+ sessions
- Secondary metric: Cancellation flow completion rate (should decrease)
- Expected lift: 8-15% reduction in churn among established users

**Test 4: Social Cost Visibility**
- Control: Standard activity feed
- Variant: Feed with highlighted absence indicators ("Your group is 1 person short")
- Primary metric: D7 re-engagement rate among users with 3+ connections
- Secondary metric: Social interaction rate post-return
- Expected lift: 10-20% improvement in socially-connected user retention

### Statistical Rigor

- Use sequential testing (not fixed-horizon) if sample sizes are limited. Recommended: always-valid confidence sequences (Howard et al., 2021).
- Correct for multiple comparisons if running multiple secondary metrics.
- Report confidence intervals, not just p-values.
- Pre-register the primary metric and analysis plan before launching the test.
- Watch for novelty effects: new notification copy often shows an initial spike that decays. Run tests long enough (4+ weeks) to measure steady-state impact.

---

## North Star Metrics for Behavioral Engagement

### Defining the North Star

The North Star Metric (NSM) should capture the core behavior that predicts long-term retention. It is not a vanity metric (total users) or a revenue metric (MRR). It is the behavioral leading indicator.

| Product Type | Recommended NSM | Why |
|-------------|----------------|-----|
| Fitness app | Weekly sessions completed per active user | Directly predicts D30 and D90 retention; 3+ sessions/week is the inflection point |
| Meditation app | Weekly minutes of completed meditation | Duration matters more than session count; 20+ min/week predicts retention |
| Nutrition tracker | Days with complete food logging per week | Completeness predicts long-term adherence; 5+ days/week is the threshold |
| SaaS (productivity) | Weekly active documents created/edited per team | Team-level engagement predicts account retention |
| SaaS (project mgmt) | Weekly tasks created or moved per user | Workflow activity predicts both user and account retention |

### Supporting Metrics Dashboard

Build a metrics dashboard with these tiers:

**Tier 1: Health Metrics (check daily)**
- DAU/MAU ratio (target: 25%+ for fitness, 20%+ for health, 40%+ for SaaS)
- D1 retention for latest cohort
- MRA completion rate
- Push notification opt-in rate

**Tier 2: Retention Metrics (check weekly)**
- D7 and D30 retention by cohort
- Churn rate by user segment (new, established, power)
- Re-engagement rate for D3 and D7 dormant users
- Loss-framed vs gain-framed notification performance

**Tier 3: Business Metrics (check monthly)**
- Net Revenue Retention
- LTV by acquisition cohort
- Payback period by channel
- Subscription conversion rate (trial to paid)

---

## Industry Baselines and Sources

### AppsFlyer State of App Marketing (2024)
- Median D30 retention across all app categories: 6%
- Health & Fitness D30: 8%
- Retention improves by 1.3x when using re-engagement campaigns vs no campaigns
- iOS retains 1.2x better than Android across all categories

### Adjust Global App Trends (2024)
- Health & Fitness D1: 25%, D7: 14%, D30: 7%
- Session length average for Health & Fitness: 7.2 minutes
- Push notification opt-in rate for Health & Fitness: 44%
- Users who opt in to notifications retain at 1.8x the rate of those who opt out

### Mixpanel Product Benchmarks (2024)
- Median weekly retention for mobile apps: 25%
- Top quartile weekly retention: 42%
- Feature adoption rate (users who try a new feature within 7 days of release): 12% median
- Power user concentration: typically 8-12% of MAU generates 40-60% of sessions

### Recurly State of Subscriptions (2024)
- Voluntary churn (user cancels): 4.1% average across all subscription businesses
- Involuntary churn (payment failure): 1.7% average
- Annual subscribers churn at 0.4x the rate of monthly subscribers
- Dunning recovery rate (recovering failed payments): 58-73% with proper retry logic

---

## Measurement Cadence

| Activity | Frequency | Owner |
|----------|-----------|-------|
| Cohort retention review | Weekly | Product/Growth |
| A/B test check-in (sequential analysis) | Twice weekly | Growth/Data Science |
| North Star Metric review | Weekly | Leadership |
| BE intervention performance review | Bi-weekly | Product/Growth |
| Churn analysis (exit survey + behavioral) | Monthly | Product/CX |
| Benchmark comparison vs industry | Quarterly | Strategy |
| Full retention audit | Quarterly | Product/Data Science |

---

*This document is part of the Behavioral Economics Module knowledge base for the Susan Team Architect platform. Content is designed for RAG ingestion and agent query by Freya and other retention-focused agents.*
