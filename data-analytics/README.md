# Data & Analytics — Product Analytics, Dashboards & Data Stack

> Metrics, analytics tools, data pipelines, and KPI dashboards from 0 → $10M.

---

## 1. Analytics Stack by Stage

### Stage 1: Pre-PMF ($0-$100K ARR)
| Tool | Purpose |
|------|---------|
| **PostHog** (free tier) | Product analytics, feature flags, session replay |
| **Google Analytics 4** | Website traffic |
| **Stripe Dashboard** | Revenue metrics |
| **Google Sheets** | Ad hoc analysis |

### Stage 2: Growth ($100K-$1M ARR)
| Tool | Purpose |
|------|---------|
| **PostHog** or **Mixpanel** | Advanced product analytics |
| **Metabase** (self-hosted) | SQL dashboards, business reporting |
| **dbt** | Data transformations |
| **BigQuery** or **ClickHouse** | Data warehouse |

### Stage 3: Scale ($1M-$10M ARR)
| Tool | Purpose |
|------|---------|
| **Amplitude** or **Mixpanel** | Enterprise product analytics |
| **Looker** or **Preset** | BI dashboards |
| **Snowflake** or **BigQuery** | Enterprise data warehouse |
| **Fivetran** or **Airbyte** | Data ingestion |
| **Census** or **Hightouch** | Reverse ETL |

---

## 2. Critical Metrics Dashboard

### Executive Dashboard (Daily)
| Metric | Source | Visualization |
|--------|--------|--------------|
| **Daily Revenue** (MRR trend) | Stripe | Line chart |
| **New Signups** | PostHog/Mixpanel | Bar chart |
| **Active Users** (DAU/WAU/MAU) | PostHog | Line chart |
| **Activation Rate** | PostHog | Funnel |
| **Trial Conversions** | Custom | Gauge |
| **Support Tickets** | Intercom | Counter |
| **NPS Score** | Survey tool | Gauge |

### Product Dashboard (Weekly)
| Metric | What It Tells You |
|--------|------------------|
| **Feature adoption** | Which features drive retention |
| **Retention cohorts** | Are users coming back? |
| **Funnel drop-offs** | Where users get stuck |
| **Session duration** | Engagement depth |
| **Error rates** | Product reliability |
| **Page load times** | Performance |

### Financial Dashboard (Monthly)
| Metric | Formula |
|--------|---------|
| **MRR** | Sum of recurring revenue |
| **MRR Growth** | (Current - Previous) / Previous |
| **Gross Margin** | (Revenue - COGS) / Revenue |
| **Burn Rate** | Monthly cash outflow |
| **Runway** | Cash / Burn rate |
| **CAC** | Marketing + Sales spend / New customers |
| **LTV** | ARPU × (1 / Churn rate) |

---

## 3. Event Tracking Plan

### Core Events to Track
```
# Authentication
user_signed_up       {method, source, referrer}
user_logged_in       {method}
user_logged_out      {}

# Onboarding
onboarding_started   {step}
onboarding_completed {duration_seconds}
onboarding_skipped   {step}

# Core Product
feature_used         {feature_name, context}
item_created         {type, method}
item_updated         {type, field_changed}
item_deleted         {type}
search_performed     {query, results_count}
export_completed     {format, item_count}

# AI Features
ai_request_sent      {feature, model, prompt_length}
ai_response_received {feature, model, response_length, duration_ms}
ai_feedback_given    {feature, rating, type}

# Billing
trial_started        {plan}
subscription_created {plan, amount, interval}
subscription_upgraded {from_plan, to_plan}
subscription_cancelled {plan, reason}
payment_failed       {plan, error_type}

# Engagement
page_viewed          {path, referrer}
cta_clicked          {location, text}
help_article_viewed  {article_id}
feedback_submitted   {type, sentiment}
```

---

## 4. Retention Analysis

### Cohort Analysis
Track monthly cohorts: What % of users from Month X are still active in Month X+1, X+2, etc.

| | Month 0 | Month 1 | Month 2 | Month 3 | Month 6 | Month 12 |
|--|---------|---------|---------|---------|---------|----------|
| **Good** | 100% | 60% | 50% | 45% | 35% | 25% |
| **Great** | 100% | 70% | 60% | 55% | 45% | 35% |
| **World-class** | 100% | 80% | 70% | 65% | 55% | 45% |

### Retention Curve Shape
- **Flattening curve** = you have retention (good)
- **Declining curve** = leaky bucket (fix activation/value)
- **Smiling curve** = users coming back (resurrection, very good)

---

## 5. PostHog Setup Guide

### Why PostHog for Startups
- Free up to 1M events/month
- Product analytics + session replay + feature flags + A/B tests
- Self-hosted option (full data control)
- Open-source

### Key PostHog Features
| Feature | Use Case |
|---------|----------|
| **Events** | Track user actions |
| **Funnels** | Conversion analysis |
| **Retention** | Cohort retention charts |
| **Paths** | User flow visualization |
| **Session Replay** | Watch user sessions |
| **Feature Flags** | Gradual rollouts |
| **Experiments** | A/B testing |
| **Surveys** | In-app NPS, CSAT |

---

## 6. Data Tools Directory

| Tool | Category | Pricing |
|------|----------|---------|
| **PostHog** | Product analytics | Free - $450/mo |
| **Mixpanel** | Product analytics | Free - $28/mo+ |
| **Amplitude** | Product analytics | Free - custom |
| **Metabase** | BI dashboards | Free (self-hosted) |
| **dbt** | Data transformation | Free (open-source) |
| **BigQuery** | Data warehouse | Pay-per-query |
| **ClickHouse** | OLAP database | Free (self-hosted) |
| **Airbyte** | Data ingestion | Free (self-hosted) |
| **Fivetran** | Data ingestion | $1/MAR+ |
| **Census** | Reverse ETL | Free tier |

---

## Sources

| Source | URL |
|--------|-----|
| FanRuan — 10 Essential SaaS Dashboard Metrics 2026 | [fanruan.com](https://www.fanruan.com/en/blog/saas-dashboard-essential-metrics-kpis) |
| PostHog — Product Analytics for Startups | [posthog.com](https://posthog.com) |
| Baremetrics — 15 KPIs Every Founder Should Track | [baremetrics.com](https://baremetrics.com/blog/saas-metrics-checklist-kpis-founders-should-track) |
| NetSuite — 14 SaaS Metrics | [netsuite.com](https://www.netsuite.com/portal/resource/articles/erp/saas-metrics.shtml) |

---

*Compiled from live Exa AI + Firecrawl research, March 2026*
