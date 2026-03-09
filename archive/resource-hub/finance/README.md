# Finance — Financial Modeling, Runway & Fundraising

> Financial models, cap table, fundraising strategy, and unit economics from 0 → $10M.

---

## 1. Financial Model Template

### Key Components
1. **Revenue model**: MRR projections by tier × expected customers
2. **Cost structure**: People, infrastructure, tools, marketing
3. **Unit economics**: CAC, LTV, gross margin, payback
4. **Cash flow**: Monthly burn, runway calculation
5. **Fundraising scenarios**: Dilution modeling

### Revenue Projection (Bottom-Up)
```
Month 1: 10 customers × $50 avg = $500 MRR
Month 6: 100 customers × $65 avg = $6,500 MRR
Month 12: 500 customers × $80 avg = $40,000 MRR
Month 18: 1,500 customers × $100 avg = $150,000 MRR
Month 24: 4,000 customers × $120 avg = $480,000 MRR → $5.76M ARR
```

### Cost Structure (Pre-Series A)
| Category | Monthly Range | Notes |
|----------|-------------|-------|
| **Founders** (2) | $0-$10K each | Low salary until funded |
| **Engineering** (2-3) | $8-15K each | First hires |
| **Infrastructure** | $500-$3,000 | Vercel, AWS, Supabase |
| **AI API costs** | $500-$5,000 | Claude API, OpenAI, etc. |
| **Tools** | $500-$2,000 | GitHub, Slack, Linear, etc. |
| **Marketing** | $1,000-$5,000 | Content, ads, tools |
| **Legal/Accounting** | $500-$2,000 | Ongoing compliance |
| **Total Burn** | $15K-$50K/mo | Pre-revenue estimate |

---

## 2. Runway Management

### Runway Formula
```
Runway (months) = Cash in bank / Monthly burn rate
```

### Runway Rules
- **Never let runway drop below 6 months** without fundraising
- **Start fundraising with 9-12 months runway** remaining
- **Fundraising takes 3-6 months** on average
- **Cut burn aggressively** if runway < 6 months

### Burn Multiple
```
Burn Multiple = Net Burn / Net New ARR
```
| Burn Multiple | Rating |
|--------------|--------|
| < 1x | Exceptional |
| 1-1.5x | Great |
| 1.5-2x | Good |
| 2-3x | Mediocre |
| > 3x | Concerning |

---

## 3. Fundraising Strategy

### Funding Rounds Overview
| Round | Amount | Valuation | What You Need |
|-------|--------|-----------|--------------|
| **Pre-seed** | $100K-$1M | $2-$8M | Team + idea + early traction |
| **Seed** | $1-$4M | $8-$20M | MVP + early revenue + 10-50 customers |
| **Series A** | $5-$20M | $25-$100M | $1M+ ARR + PMF + growth rate |
| **Series B** | $15-$50M | $80-$300M | $5M+ ARR + scalable GTM |

### SAFE Notes (Pre-Seed / Seed)
- **Post-money SAFE** is now standard (Y Combinator template)
- Typical pre-seed cap: $5-$12M
- Typical seed cap: $10-$25M
- MFN (Most Favored Nation) clause — optional but founder-friendly
- No interest, no maturity date, converts at next priced round

### Pitch Deck Structure (10-12 slides)
1. **Title** — Company name, one-line description, contact
2. **Problem** — What pain exists and for whom
3. **Solution** — Your product and how it solves the problem
4. **Demo** — Screenshots, video, or live product
5. **Market** — TAM/SAM/SOM with bottom-up analysis
6. **Business model** — How you make money, pricing
7. **Traction** — Revenue, users, growth rate, key metrics
8. **Team** — Founders' backgrounds, why you're uniquely suited
9. **Competition** — Positioning matrix, your unfair advantage
10. **Financials** — Projections, unit economics, burn
11. **Ask** — How much you're raising and what you'll do with it
12. **Appendix** — Product roadmap, technical architecture

### Pitch Deck Tools
| Tool | Purpose |
|------|---------|
| **Canva** | Quick, beautiful pitch decks |
| **Figma** | Custom design pitch decks |
| **Beautiful.ai** | AI-assisted presentation design |
| **Gamma** | AI-generated presentations |
| **DocSend** | Track deck views and engagement |

### Fundraising Resources
| Source | URL |
|--------|-----|
| Qubit Capital — AI Startup Pitch Deck Slides | [qubit.capital](https://qubit.capital/blog/essential-ai-startup-pitch-deck-fundraising-slides) |
| IdeaProof — Free Pitch Deck Templates 2026 | [ideaproof.io](https://ideaproof.io/tools/pitch-deck-templates) |
| InnMind — 2026 Pitch Deck Guide | [blog.innmind.com](https://blog.innmind.com/fundraising-pitch-deck-web3-ai-2026/) |
| Capwave AI — AI Fundraising Platform | [capwave.ai](https://capwave.ai/) |

---

## 4. Cap Table Management

### Cap Table Basics
```
Pre-seed example:
  Founder A: 45% (vesting 4yr/1yr cliff)
  Founder B: 35% (vesting 4yr/1yr cliff)
  Option Pool: 10% (for early hires)
  Angels/Pre-seed: 10% ($500K on $5M post-money SAFE)
```

### Cap Table Tools
| Tool | Pricing | Best For |
|------|---------|----------|
| **Carta** | $$$  | Standard, VC-friendly |
| **Pulley** | $$ | Modern, startup-friendly |
| **AngelList** | $ | If raising on AngelList |
| **LTSE Equity** | Free tier | Budget-conscious |

### Key Dilution Math
- Pre-seed: ~10-15% dilution
- Seed: ~15-25% dilution
- Series A: ~20-30% dilution
- By Series A, founders typically own ~40-55% combined

---

## 5. Unit Economics

### Key Formulas
```
CAC = Total sales & marketing spend / New customers acquired
LTV = Average revenue per account / Monthly churn rate
LTV:CAC Ratio = LTV / CAC (target: > 3:1)
Payback Period = CAC / Monthly gross profit per customer
Gross Margin = (Revenue - COGS) / Revenue
```

### SaaS Unit Economics Benchmarks (2026)
| Metric | Seed Stage | Series A | Series B |
|--------|-----------|----------|----------|
| Gross Margin | 60-70% | 70-80% | 75-85% |
| LTV:CAC | > 2:1 | > 3:1 | > 4:1 |
| CAC Payback | < 18 mo | < 12 mo | < 9 mo |
| Net Revenue Retention | > 100% | > 110% | > 120% |
| Monthly Logo Churn | < 8% | < 5% | < 3% |

---

## 6. Accounting & Bookkeeping

### Tools
| Tool | Purpose | Pricing |
|------|---------|---------|
| **Bench** | Full-service bookkeeping | $299/mo+ |
| **Pilot** | Startup bookkeeping + tax | $500/mo+ |
| **QuickBooks Online** | DIY accounting | $30/mo+ |
| **Xero** | DIY accounting (international) | $13/mo+ |
| **Finta** | Fundraising data room | Free tier |
| **Brex** | Corporate cards + expense management | Free |

---

## Sources

| Source | URL |
|--------|-----|
| Eagle Rock CFO — SaaS Finance Benchmarks 2026 | [eaglerockcfo.com](https://www.eaglerockcfo.com/blog/research/saas-finance-metrics-benchmarks) |
| GSquared CFO — SaaS Benchmarks 2026 | [gsquaredcfo.com](https://www.gsquaredcfo.com/blog/saas-benchmarks-2026) |
| 3L3C — Bootstrapping SaaS to $10M ARR with AI | [3l3c.ai](https://3l3c.ai/us/blog/how-ai-is-powering-technology-and-digital-services-in-the-united-states/bootstrapping-saas-ai) |
| We Are Founders — Bootstrap to $10M Playbook | [wearefounders.uk](https://www.wearefounders.uk/bootstrapped-to-10m-the-capital-efficient-playbook/) |

---

*Compiled from live Exa AI + Firecrawl research, March 2026*
