# SOP-31: Financial Modeling & Runway Analysis

**Owner**: Mike Rodgers
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-24
**Category**: Startup / Venture Operations
**Priority**: P0 — Runway = life. Never fly blind on cash.
**Maturity**: Documented (this SOP)
**Applies to**: TransformFit, any venture with revenue or expenses

---

## 1. Purpose

Maintain a living financial model for each active venture that tracks burn rate, runway, revenue trajectory, and milestone-to-funding nexus — so Mike is never surprised by a cash crisis and can make pricing, hiring, and pivot decisions with full financial context.

**Core principle**: A startup's financial model is not a prediction — it is a decision tool. The model is only as good as the assumptions it forces you to make explicit.

**Framework basis**: Dave McClure's Startup Metrics for Pirates (AARRR), YC's default alive/dead calculation, Bill Gurley's unit economics framework, and standard SaaS metrics (ARR, MRR, CAC, LTV, LTV:CAC).

---

## 2. Scope

### 2.1 In Scope

- Monthly financial model maintenance for all active ventures
- Burn rate, runway, and default alive/dead calculation
- Revenue model: pricing assumptions, conversion rates, churn assumptions
- Unit economics: CAC, LTV, LTV:CAC ratio, payback period
- Scenario modeling: base case, bull case, bear case
- Fundraising trigger criteria

### 2.2 Out of Scope

- Oracle Health financial analysis (governed by corporate finance)
- Personal finances (separate personal finance system)
- Detailed tax accounting (requires CPA)

---

## 3. PHASE 1: Build the Baseline Model (New Venture)

### 3.1 The 6-Block Financial Model Structure

Every venture gets a model with exactly 6 blocks:

```
BLOCK 1: REVENUE MODEL
- Pricing tiers (what you charge and to whom)
- Conversion assumptions (traffic → trial → paid → retained)
- MRR/ARR build: Month 1 through Month 24

BLOCK 2: COST STRUCTURE
- Fixed costs: infrastructure (hosting, APIs, tools), subscriptions
- Variable costs: support, payment processing fees, AI inference costs
- People costs: contractors, part-time, full-time hires (if any)
- Marketing spend: paid acquisition budget

BLOCK 3: UNIT ECONOMICS
- CAC (Customer Acquisition Cost) = Marketing Spend / New Customers
- LTV (Lifetime Value) = ARPU × (1 / Monthly Churn Rate)
- LTV:CAC ratio target: ≥ 3.0x for venture viability
- CAC Payback Period: LTV < payback months means unsustainable

BLOCK 4: CASH FLOW
- Starting cash balance
- Monthly burn rate = Fixed Costs + Variable Costs - Revenue
- Monthly net cash position
- Runway = Cash Balance / Monthly Burn Rate (months)

BLOCK 5: MILESTONE MAP
- Revenue milestone → next milestone → funding trigger
- Default Alive calc: current growth rate × current cost structure
- Break-even month projection

BLOCK 6: SCENARIO TABLE
- Bear case: 50% of revenue projections, costs stay fixed
- Base case: expected trajectory
- Bull case: 150% of revenue projections
```

### 3.2 Default Alive Calculation

From Paul Graham's "Default Alive or Default Dead" framework:

```
Default Alive threshold: 
  Monthly revenue growth rate needed to reach break-even 
  before current cash runs out, assuming costs stay constant.

Calculate:
  Months to break-even (current growth rate) vs. Months of runway
  
  IF months to break-even ≤ months of runway: DEFAULT ALIVE
  IF months to break-even > months of runway: DEFAULT DEAD

Review this calculation every month. The status can change.
```

---

## 4. PHASE 2: Monthly Model Update (First Monday of Each Month)

**Duration**: 30 minutes
**Trigger**: Monthly financial review calendar block

### 4.1 Data Collection

| Metric | Where to Pull It | Notes |
|--------|-----------------|-------|
| MRR | Stripe dashboard | New + expansion + contraction + churn |
| New customers | Stripe / app database | Count by cohort |
| Churned customers | Stripe / app database | Count + reason if known |
| Hosting costs | AWS / Vercel / Supabase dashboards | Export to CSV |
| AI inference costs | Anthropic / OpenAI dashboard | Critical variable for AI-native products |
| Marketing spend | Meta Ads / Google Ads / total | Actual spend, not budget |
| Support hours | Time log | If any paid support |

### 4.2 Update Protocol

1. Pull all metrics into the model spreadsheet
2. Recalculate MRR movement: New MRR + Expansion - Contraction - Churn
3. Recalculate burn rate with actual costs
4. Recalculate runway
5. Re-run default alive/dead calculation
6. Update the scenario table (are assumptions still valid?)
7. Flag any metric that moved outside expected range (±20%)

### 4.3 MRR Movement Accounting

```
MRR MOVEMENT WATERFALL
Starting MRR:         $____
+ New MRR:            $____  (new customers this month × ARPU)
+ Expansion MRR:      $____  (existing customers upgrading)
- Contraction MRR:    $____  (existing customers downgrading)
- Churn MRR:          $____  (lost customers × their ARPUs)
= Ending MRR:         $____

Net MRR Change:       $____  (Ending - Starting)
MRR Growth Rate:      ____%  (Net Change / Starting MRR)
```

---

## 5. PHASE 3: SaaS Health Scorecard

Run this scorecard monthly. Red flags require immediate action.

### 5.1 Core Metrics Table

| Metric | Formula | Healthy | Warning | Critical |
|--------|---------|---------|---------|---------|
| MRR Growth Rate | (This MRR - Last MRR) / Last MRR | >15%/mo | 5-15%/mo | <5%/mo |
| Monthly Churn Rate | Churned MRR / Starting MRR | <2% | 2-5% | >5% |
| LTV:CAC Ratio | LTV / CAC | >3x | 1-3x | <1x |
| CAC Payback Period | CAC / ARPU | <12 mo | 12-24 mo | >24 mo |
| Gross Margin | (Revenue - COGS) / Revenue | >70% | 50-70% | <50% |
| Runway | Cash / Monthly Burn | >18 mo | 9-18 mo | <9 mo |
| AI Cost as % of Revenue | AI Inference Cost / Revenue | <15% | 15-25% | >25% |

### 5.2 AI-Native Product Consideration

For AI-native products (TransformFit with IRON/PULSE/FUEL/GHOST/EDGE/SPARK coaches):

- Track inference cost per active user per month
- Track inference cost as % of ARPU — if this exceeds 40% of ARPU, pricing is underwater
- Tier AI usage by subscription tier to protect gross margin

```
AI Cost Management Formula:
  Affordable AI cost per user = ARPU × Target AI Cost % 
  Example: $97/mo ARPU × 20% = $19.40/mo AI budget per user
  
  If actual AI cost per user > budget: 
    → Optimize prompts, add rate limits, or raise pricing
```

---

## 6. PHASE 4: Fundraising Decision Framework

### 6.1 Fundraising Trigger Criteria

Do NOT raise money reactively out of desperation. Raise strategically:

| Trigger | Condition | Action |
|---------|-----------|--------|
| **Runway trigger** | Runway drops below 9 months | Begin investor conversations immediately |
| **Growth trigger** | MRR growing >20%/mo for 3+ consecutive months | Raise to pour fuel on fire |
| **Market trigger** | Competitor raises or market consolidates | Raise to defend position |
| **Hire trigger** | Growth blocked by specific missing team member | Raise to hire |

### 6.2 Round Sizing Formula

```
Round size = [18 months of target burn rate] + [product build budget] + [safety buffer (20%)]

Example:
  Target burn post-raise: $30K/month
  18 months = $540K
  Product build (hiring 1 engineer): $120K
  Safety buffer: $132K
  → Raise ~$800K seed round
```

### 6.3 Investor Update Cadence

Once investors are on board, monthly updates are non-negotiable (see SOP-35 for format). The update must include the financial model snapshot.

---

## 7. Output Artifacts

| Artifact | Location | Updated When |
|----------|----------|-------------|
| Financial model spreadsheet | ~/Startup-Intelligence-OS/docs/ventures/[venture]/finance/[venture]-model-[YYYY].xlsx | Monthly |
| Monthly financial summary (MD) | finance/monthly-[YYYY-MM].md | 1st Monday each month |
| Default alive/dead status | ventures/[venture]/STATUS.md | Monthly |
| SaaS health scorecard | finance/scorecard-[YYYY-MM].md | Monthly |
| Fundraising prep doc | finance/fundraising-[round]-[YYYY].md | When fundraising trigger fires |

---

## 8. Tools and Systems

| Tool | Purpose |
|------|---------|
| Stripe Dashboard | MRR, customer count, churn |
| Jake brain_search | Load prior financial decisions and model assumptions |
| Claude Code | Model scenario calculations, generate summary narrative |
| Telegram (Jake) | Monthly financial summary delivered automatically |
| Jake goal_checkin | Update revenue and runway KPIs |

---

## 9. Quality Checks

| Checkpoint | Standard | Owner |
|-----------|----------|-------|
| Financial model updated by first Monday of each month | Date on file | Mike |
| Default alive/dead calculation current | Recalculated with actual data | Mike |
| AI inference costs tracked separately | Line item in cost structure | Mike |
| Fundraising trigger criteria reviewed monthly | Checked against scorecard | Mike |
| LTV:CAC ratio tracked and above 1x | Below 1x = stop paid acquisition | Mike |

---

## 10. Revision History

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-03-24 | 1.0 APPROVED | Initial SOP — WS3 Foundation Layer completion | Jake (Dust Star 25X) |

---

## 11. Source Attribution

1. **Paul Graham** — "Default Alive or Default Dead" (2015) — YC essay, survival calculation framework
2. **Dave McClure** — AARRR Startup Metrics for Pirates — acquisition, activation, retention, referral, revenue
3. **Bill Gurley** — Unit economics framework for SaaS (Above the Crowd blog)
4. **David Skok** — SaaS Metrics 2.0 (ForEntrepreneurs.com) — CAC, LTV, churn math
5. **Jason Lemkin** — SaaStr — MRR movement waterfall, fundraising trigger criteria
6. **Brad Feld & Jason Mendelson** — Venture Deals (2019) — round sizing and term sheet mechanics
