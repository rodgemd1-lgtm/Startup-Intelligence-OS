# Revenue — SaaS Monetization & Pricing Playbook

> Pricing, billing, PLG monetization, and revenue optimization from 0 → $10M ARR.

---

## 1. Pricing Strategy Framework

### The 3 Pricing Models for AI SaaS

| Model | Best For | Example |
|-------|----------|---------|
| **Usage-Based** | API products, AI compute | OpenAI (per-token), Vercel (per-request) |
| **Seat-Based** | Collaboration tools | Figma, Slack, Notion |
| **Hybrid** | Most AI SaaS | Cursor ($20/seat + usage limits) |

### Pricing Psychology
1. **Anchor high, offer 3 tiers** — Good/Better/Best
2. **Highlight the middle tier** — most customers choose it
3. **Annual discount = 2 months free** (16.7% discount standard)
4. **Free tier or trial** — essential for PLG, but set clear limits

### AI SaaS Pricing Benchmarks (2026)
| Tier | Monthly Price | What's Included |
|------|--------------|-----------------|
| Free | $0 | 5-50 actions/day, watermark, limited features |
| Starter | $10-29/mo | 100-500 actions/mo, core features |
| Pro | $29-99/mo | 1,000-5,000 actions/mo, advanced features |
| Team | $49-199/seat/mo | Collaboration, admin, SSO |
| Enterprise | Custom | Unlimited, SLA, dedicated support |

---

## 2. Product-Led Growth (PLG) Revenue Engine

### The 7-Layer PLG Framework (Aakash Gupta, 2026)

**Source:** [news.aakashg.com — PLG in 2026](https://www.news.aakashg.com/p/plg-in-2026)

The old Slack/Dropbox playbook is dead. Modern PLG requires:

1. **Value Creation** — User gets value before paying
2. **Activation** — Time-to-value < 5 minutes
3. **Habit Formation** — Daily/weekly use patterns
4. **Viral Loops** — Built-in sharing mechanics
5. **Monetization Triggers** — Upgrade when value is proven
6. **Expansion Revenue** — Land and expand within orgs
7. **Community Moat** — Network effects + ecosystem

### PLG Metrics That Matter
| Metric | Good | Great |
|--------|------|-------|
| Free → Paid Conversion | 2-5% | 5-10% |
| Trial → Paid (14-day) | 15-25% | 25-40% |
| Net Revenue Retention | 110-120% | 120-140% |
| Expansion Revenue % | 20-30% | 30-50% |
| Time to Value | < 1 day | < 5 minutes |

---

## 3. Billing & Payments Infrastructure

### Recommended Stack
| Tool | Purpose | Pricing |
|------|---------|---------|
| **Stripe** | Payment processing | 2.9% + $0.30 per transaction |
| **Stripe Billing** | Subscription management | +0.5-0.8% |
| **Orb** | Usage-based billing | For complex metering |
| **Lago** | Open-source billing | Self-hosted alternative |
| **Stigg** | Pricing & packaging platform | Feature flags + billing |

### Implementation Checklist
- [ ] Stripe integration with webhooks
- [ ] Subscription lifecycle management (create, upgrade, downgrade, cancel)
- [ ] Usage metering and tracking
- [ ] Invoice generation
- [ ] Failed payment recovery (dunning)
- [ ] Proration for mid-cycle changes
- [ ] Tax calculation (Stripe Tax or Avalara)

---

## 4. Revenue Milestones: 0 → $10M ARR

### Phase 1: $0 → $100K ARR (Founder-Led Sales)
- **Focus**: Find 10 customers who love it
- **Pricing**: Charge from day 1 (validates willingness to pay)
- **Channel**: Direct outreach, communities, your network
- **Metric**: Weekly revenue growth rate

### Phase 2: $100K → $1M ARR (Repeatable Sales)
- **Focus**: Find repeatable acquisition channel
- **Pricing**: Test and iterate (raise prices until you get pushback)
- **Channel**: Content + SEO + PLG self-serve + outbound
- **Metric**: MRR growth, CAC payback period

### Phase 3: $1M → $5M ARR (Scale What Works)
- **Focus**: Double down on winning channels
- **Pricing**: Lock in packaging, add enterprise tier
- **Channel**: Paid acquisition, partnerships, sales team
- **Metric**: Net revenue retention, gross margin

### Phase 4: $5M → $10M ARR (Expansion Revenue)
- **Focus**: Land and expand, upsell, cross-sell
- **Pricing**: Usage-based expansion, enterprise contracts
- **Channel**: Account management, customer success
- **Metric**: NDR, LTV:CAC ratio, rule of 40

---

## 5. SaaS Metrics & Benchmarks (2026)

### Key Metrics
| Metric | Formula | Good Benchmark |
|--------|---------|---------------|
| **MRR** | Sum of monthly recurring revenue | Growing 15-20%+ MoM early stage |
| **ARR** | MRR × 12 | Revenue milestone tracker |
| **Gross Margin** | (Revenue - COGS) / Revenue | 70-80% for SaaS, 50-60% for AI SaaS |
| **CAC** | Sales & marketing spend / new customers | < 1/3 of first-year revenue |
| **LTV** | ARPU / monthly churn rate | LTV:CAC > 3:1 |
| **CAC Payback** | CAC / monthly gross profit per customer | < 12 months |
| **Net Revenue Retention** | (Start MRR + expansion - contraction - churn) / Start MRR | > 110% |
| **Burn Multiple** | Net burn / net new ARR | < 2x is efficient |
| **Rule of 40** | Revenue growth % + profit margin % | > 40% is healthy |

### Sources
| Source | URL |
|--------|-----|
| Eagle Rock CFO — SaaS Finance Metrics Benchmarks 2026 | [eaglerockcfo.com](https://www.eaglerockcfo.com/blog/research/saas-finance-metrics-benchmarks) |
| Visdum — SaaS Metrics 2026 | [visdum.com](https://www.visdum.com/blog/saas-metrics) |
| Baremetrics — SaaS Metrics Checklist: 15 KPIs | [baremetrics.com](https://baremetrics.com/blog/saas-metrics-checklist-kpis-founders-should-track) |
| GSquared CFO — SaaS Benchmarks 2026 | [gsquaredcfo.com](https://www.gsquaredcfo.com/blog/saas-benchmarks-2026) |
| re:cap — SaaS Metrics: 6 KPIs Founders Must Know | [re-cap.com](https://www.re-cap.com/blog/kpi-metric-saas) |
| FanRuan — 10 Essential SaaS Dashboard Metrics 2026 | [fanruan.com](https://www.fanruan.com/en/blog/saas-dashboard-essential-metrics-kpis) |

---

## 6. Revenue Tools & Platforms

| Tool | Purpose |
|------|---------|
| **Stripe** | Payments + billing |
| **Baremetrics** / **ChartMogul** | SaaS analytics dashboard |
| **ProfitWell** (Paddle) | Pricing optimization, churn analysis |
| **Close** / **Attio** | CRM for early-stage |
| **Vitally** | Customer health scoring |

---

*Compiled from live Exa AI + Firecrawl research, March 2026*
