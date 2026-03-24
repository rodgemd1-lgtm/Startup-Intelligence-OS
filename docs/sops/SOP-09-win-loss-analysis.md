# SOP-09: Win/Loss Analysis

**Owner**: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence
**Version**: 3.0 DRAFT — Awaiting Mike's approval
**Last Updated**: 2026-03-22
**Category**: Competitive Intelligence Production
**Priority**: P1 — #1 most impactful CI program per industry research; currently a gap
**Maturity**: Gap → Documented (this SOP)
**Research Basis**: 4 parallel MCP research scrapes, 80+ web sources, zero Claude training data

---

## Purpose

Systematically analyze why Oracle Health wins and loses competitive deals using behavioral science-informed interview methodology that penetrates beneath stated reasons to uncover actual decision drivers.

**Why this matters (sourced data):**
- Companies with comprehensive win/loss programs see **15-30% revenue increases** and **up to 50% improvement in win rates** (Gartner, via Clozd)
- Programs combining win/loss + CI are **3x more likely to report significant impact** (Klue 2025 Trends, 300+ leaders surveyed)
- **85% of CRM closed-lost data is fundamentally wrong** (Corporate Visions, 100K+ deals analyzed)
- Sales teams are incorrect about deal outcomes **more than 60% of the time** (Anova Consulting, 20+ years of research)

---

## THE BEHAVIORAL SCIENCE FOUNDATION

### Why Traditional Win/Loss Fails

Traditional win/loss asks "why did you choose/reject us?" and takes the answer at face value. This produces garbage data because of a fundamental misunderstanding of how B2B buying actually works.

**The 44-Point Price Gap** (User Intuition, 10,247 post-decision buyer conversations, Jan 2024 – Dec 2025):

| Loss Reason | Initially Cited by Buyers | Actual Primary Driver | Gap |
|-------------|--------------------------|----------------------|-----|
| **Price / Budget** | 62.3% | 18.1% | **-44.2 pp** |
| **Implementation Risk** | 4.1% | 23.8% | +19.7 pp |
| **Champion Confidence Failure** | 2.7% | 21.3% | +18.6 pp |
| **Time-to-Value Anxiety** | 7.2% | 16.9% | +9.7 pp |

**Stated reason matched actual decision driver only 36% of the time.**

Source: https://www.userintuition.ai/posts/win-loss-analysis-complete-guide/

### The Behavioral Forces Driving Every Deal

Every B2B purchase decision is shaped by these forces. Our interview methodology is designed to surface them:

| Force | What It Is | How It Shows Up | Source |
|-------|-----------|-----------------|--------|
| **Loss Aversion** | Losses feel ~2x more intense than equivalent gains | Buyers overweight implementation risk and career exposure over innovation value | Kahneman & Tversky, 1979 (*Econometrica*) |
| **Status Quo Bias** | Three forces — loss aversion, uncertainty costs, sunk costs — create inertia | "No decision" is the #1 competitor; kills 50-75% of modernization bids | Samuelson & Zeckhauser, 1988 (*Journal of Risk and Uncertainty*) |
| **Champion Risk** | Internal advocates are risk carriers who spend political capital | Champion-led deals close 2-3x more frequently; 51% of accounts churn within 12 months of champion departure | ChurnZero/Sturdy; UserGems |
| **FOMU > FOMO** | Fear of Messing Up outweighs Fear of Missing Out in enterprise sales | Urgency tactics backfire — buyers slow down, add stakeholders, extend timelines | Dixon, *The Jolt Effect* (2022) |
| **Social Proof** | Peer adoption is the primary trust mechanism | 90% of B2B buying decisions influenced by peer recommendations; 84% start with a referral | Forrester; HubSpot |
| **Choice Overload** | Too many vendor options → decision paralysis → no decision | 86% of B2B purchases stall at some point | Schwartz, *Paradox of Choice*; Gartner |
| **Anchoring** | First credible price/benchmark biases all subsequent evaluation | Order of vendor engagement shapes the entire evaluation frame | Tversky & Kahneman, 1974 (*Science*) |
| **DMU Conflict** | Buying committees fragment around competing objectives | 74% of B2B buying groups demonstrate "unhealthy conflict" during decisions | Gartner 2025 (press release, 05/07/2025) |

### The Meta-Insight

> **B2B buying is not a rational evaluation process with emotional noise. It is an emotional process with rational justification layered on after the fact.** Win/loss analysis that only captures rational reasons (price, features, timing) misses the 95% of the decision that happened subconsciously.
>
> — Synthesis from Gerald Zaltman (HBS), Kahneman & Tversky, CEB/Gartner research

---

## PROGRAM GOVERNANCE

### Ownership & RACI

| Role | Responsibility | Owner |
|------|---------------|-------|
| **Program Owner** | Designs methodology, conducts interviews, produces all reports | Mike Rodgers |
| **Deal Nominations** | Submits P1/P2 deals to interview pipeline within 7 days of close | Sales Ops (via Salesforce) |
| **Insight Recipients — Action SLA** | Product: 2 weeks / Sales Enablement: 2 weeks / Services: 1 week | Product, Sales Enablement, Services |
| **Executive Sponsor** | Quarterly review approval, program budget, escalation backstop | Matt Cohlmia |
| **Win/Loss Lead (Future)** | Will own interview execution as program scales past 20/quarter | David Okonkwo (nominated) |

### SLA Escalation Path

When an insight recipient misses their 2-week response SLA:
1. Mike sends a written reminder with the specific ask
2. If no response in 5 business days: Mike escalates to Matt Cohlmia cc'ing the recipient's VP
3. If 3 consecutive SLA misses by the same team: flagged in the Quarterly Executive Report as "Intelligence-to-Action Breakdown"

### Data Retention & Privacy Policy

| Data Type | Retention | Access | Destruction |
|-----------|-----------|--------|-------------|
| Interview recordings (audio/video) | 90 days | Mike only | Deleted after coding complete |
| Interview transcripts (raw) | 180 days | Mike + designated analyst | Deleted after themes extracted |
| Coded interview data (taxonomy) | Indefinite | Program team | Retained as longitudinal data |
| Anonymized quotes | Indefinite | Can be shared in reports | No destruction — anonymized |
| Buyer contact information | 2 years | Mike only | Purged on schedule |

All interview data is anonymized before inclusion in any report shared beyond the immediate CI team. No buyer is identified by name, title, or health system without explicit written consent.

### Annual Program Review Gate

Each Q1, Mike conducts an annual review producing:
- YoY interview volume and mix vs. target
- Theme stability analysis (are the same drivers appearing, or shifting?)
- Win rate trend vs. the program's recommendations (did implementing our guidance move the needle?)
- Methodology update recommendation (are weights, scoring, or interview guides still calibrated?)

Review requires Matt's approval to continue at current funding level.

---

## PHASE 1: PROGRAM DESIGN

### 1.1 Program Parameters

| Parameter | Recommendation | Source |
|-----------|---------------|--------|
| **Volume** | 8-12 interviews/quarter to start; scale to 20-30 | Clozd: 20-30 for directional patterns; 50+ for stable themes |
| **Mix** | 40% wins, 60% losses | User Intuition: overweight losses — failure modes are more diverse |
| **Timing** | Within 30 days of decision (not contract signature) | Anova/Clozd: memory decay is severe beyond 30 days |
| **Interviewer** | Mike or designated analyst — NOT the sales rep | Anova: third-party/non-sales interviewers get 50-60% response rates vs. much lower for sales |
| **Duration** | 25-35 minutes, semi-structured | User Intuition: structured enough for coding, flexible enough for laddering |
| **Consent** | Verbal consent at start of call | Standard practice across all providers |

### 1.2 Deal Selection Criteria

**Must Interview (P1):**
- Any deal lost to a named competitor (Epic, Waystar, Regard, athenahealth, etc.)
- Any deal > $500K TCV won or lost
- Any deal where a new/unexpected competitor appeared
- Any deal won where a strong competitor was displaced

**Should Interview (P2):**
- Deals lost to "no decision" — these are often the most instructive (CEB: "no decision" is the #1 competitor)
- Deals won with no competition (validates positioning)
- Deals in new market segments

**Skip:**
- Renewals with no competitive threat
- Small deals with known incumbent advantages
- Deals where buyer is unresponsive after 3 contact attempts

### 1.3 Maturity Roadmap

Based on Clozd's 5-phase Win-Loss Maturity Curve:

| Phase | Description | Where Oracle M&CI Is Today |
|-------|-------------|---------------------------|
| **1. Guesswork** | General intuition about win/loss | Past this |
| **2. CRM Data** | Salesforce dropdown codes (85% wrong) | Partially here |
| **3. One-off Research** | Ad hoc buyer interviews, eye-opening but unsustainable | **Target: Q2 2026** |
| **4. Ongoing / Limited** | Continuous feedback on subset of pipeline | Target: Q3-Q4 2026 |
| **5. Full Coverage** | Complete pipeline analysis, third-party support | Target: 2027 |

---

## PHASE 2: INTERVIEW METHODOLOGY — THE LADDERING APPROACH

### 2.1 Why Laddering

Standard interviews capture **stated reasons**. Laddering — originated in clinical psychology, adapted for win/loss — uses 5-7 levels of probing to reach **actual decision drivers**.

| Level | What You Hear | What You Ask Next |
|-------|--------------|-------------------|
| **1. Surface** | "Your pricing was too high" | "Walk me through how you evaluated pricing" |
| **2. Context** | "We compared total cost across vendors" | "What costs beyond license were most concerning?" |
| **3. Comparison** | "Implementation services were 2x the software cost" | "How did you weigh implementation cost vs. other factors?" |
| **4. Decision** | "We were worried about the timeline and risk" | "What specifically felt risky about the implementation?" |
| **5. Root cause** | "Our last vendor switch took 18 months and we lost productivity" | "If we had guaranteed a 6-month go-live, would pricing still have been the issue?" |
| **6-7. True driver** | "Honestly, no. It was really about confidence in delivery" | ← **Implementation risk**, not price |

Source: User Intuition laddering methodology, https://www.userintuition.ai/posts/ai-moderated-win-loss-analysis/

### 2.2 Interview Guide — Lost Deals (30 minutes)

**Section 1: Context & Trigger (5 min)**

1. "Walk me through what was happening in your organization that made you start looking for a solution."
   - *Ladder:* "What specifically about that situation made it urgent enough to act on?"

2. "Had you tried to solve this before? What happened?"
   - *Ladder:* "What was different this time that made you commit to a formal evaluation?"

3. "Who else was involved in recognizing this was a problem worth solving?"
   - *Ladder:* "What role did they play in shaping what you looked for?"

**Section 2: Evaluation Process (10 min)**

4. "How did you decide which solutions to evaluate?"
   - *Ladder:* "What made those criteria the most important ones?"

5. "Walk me through how the evaluation unfolded — what happened first, second, third?"
   - *Ladder:* "At what point did your thinking change about what mattered most?"

6. "Who had the strongest opinion about which direction to go, and what shaped their view?"
   - *Ladder:* "What would have changed their mind?"

7. "Were there any concerns that almost stopped the process entirely?"
   - *Ladder:* "How were those concerns addressed — or were they?"

**Section 3: Decision Drivers (10 min)**

8. "When you made the final decision, what was the single most important factor?"
   - *Ladder:* "Help me understand why that specific factor outweighed everything else."

9. "What almost made you go in the other direction?"
   - *Ladder:* "What would have tipped the decision if that concern had been slightly bigger?"

10. "How did Oracle Health's pricing compare to the vendor you chose?"
    - *Ladder:* "If pricing had been identical, would you have chosen differently? Why or why not?"

11. "If you could change one thing about Oracle Health's offering, what would make you reconsider?"
    - *Ladder:* "Is that a fundamental limitation or something that could change?"

**Section 4: Internal Dynamics (3 min)**

12. "How did the internal conversation go when it came time to make a final decision?"
    - *Ladder:* "Were there disagreements? What drove them?"

13. "Did you feel you had what you needed to make the case internally for any vendor?"
    - *Ladder:* "What materials or proof would have made that easier?"

**Section 5: Reflection (2 min)**

14. "What advice would you give Oracle Health about how to win more deals like yours?"
    - *Ladder:* "What would be the single most impactful change?"

15. "Would you be open to re-evaluating Oracle Health in the future? Under what conditions?"

### 2.3 Interview Guide — Won Deals (30 minutes)

**Section 1: Context & Trigger (5 min)**

1. "What triggered the decision to evaluate new solutions?"
   - *Ladder:* "What was the breaking point with your previous approach?"

2. "Who were the key decision-makers and influencers?"
   - *Ladder:* "Who had the most influence on the final decision, and why?"

3. "What other vendors did you consider?"
   - *Ladder:* "What specifically put them on your shortlist?"

**Section 2: Why Oracle (10 min)**

4. "What specifically about Oracle Health made you choose us?"
   - *Ladder:* "Was there a single moment or proof point that tipped the decision?"

5. "Were there areas where competitors were stronger? What tipped the balance?"
   - *Ladder:* "How did you justify that trade-off internally?"

6. "How important was Oracle's broader ecosystem (cloud, database, ERP) vs. the specific product?"
   - *Ladder:* "Would you have chosen us without the platform story?"

7. "What role did references or case studies play?"
   - *Ladder:* "Which reference was most influential, and why?"

**Section 3: Risks & Concerns (10 min)**

8. "What was your biggest concern about choosing Oracle Health?"
   - *Ladder:* "How was that concern addressed — or is it still a concern?"

9. "Was there a moment during the evaluation where you almost went a different direction?"
   - *Ladder:* "What brought you back?"

10. "How did our sales team's approach compare to the competition?"
    - *Ladder:* "Did the sales experience help or hurt our chances?"

11. "What proof point or reference was most influential?"
    - *Ladder:* "What would have happened without that reference?"

**Section 4: Closing (5 min)**

12. "What would you tell another health system considering Oracle Health?"
13. "What's the #1 thing we should improve for future buyers?"
14. "Looking back, is there anything you wish you'd known earlier?"

### 2.4 Interview Best Practices

| Practice | Why | Source |
|----------|-----|--------|
| **Use laddering probes (5-7 levels)** | Surface answers match actual drivers only 36% of the time | User Intuition (10,247 conversations) |
| **Never defend Oracle** | This is listening mode, not selling mode | All providers |
| **Let silence work** | Pausing 3-5 seconds after an answer often surfaces deeper insight | Anova Consulting |
| **Interview the economic buyer** | Their perspective differs from end-users | Clozd methodology |
| **Equal+ losses** | 40/60 win/loss split avoids confirmation bias | User Intuition; Klue |
| **Third-party if possible** | 50-60% response rate vs. much lower for internal | Anova (20+ years data) |
| **Record if permitted** | Enables accurate coding; offer anonymized themes only | Standard practice |
| **Probe "no decision" separately** | Status quo bias is the #1 competitor, not a named vendor | CEB/Gartner research |

---

## PHASE 3: CODING TAXONOMY

### 3.1 The Five Real Loss Driver Categories

Based on User Intuition's analysis of 10,247 conversations — use these as primary categories, not CRM-style surface reasons:

| Code | Category | Actual Prevalence | What Buyers Say Instead |
|------|----------|-------------------|------------------------|
| **IMPL-RISK** | Implementation Risk | 23.8% | "Not the right fit" / "didn't meet requirements" |
| **CHAMP-FAIL** | Champion Confidence Failure | 21.3% | Rarely stated — surfaces through laddering |
| **PRICE** | Pricing / Value (actual) | 18.1% | Cited 62.3% of the time (massively overclaimed) |
| **TTV** | Time-to-Value Anxiety | 16.9% | "Budget constraints" / "timing" |
| **COMP-POS** | Competitive Positioning Failure | 11.4% | Almost never stated — requires 4+ levels of laddering |
| **TRUST** | Trust / Credibility Concerns | 8.5% | "Comfort level" / "confidence" |

### 3.2 Extended Coding (Secondary Tags)

Every interview also gets coded on:

| Dimension | Values |
|-----------|--------|
| **Competitor** | Primary competitor (who won), secondary competitors (also evaluated) |
| **Market Segment** | EHR, RCM, Portal, AI Agents, Life Sciences, etc. |
| **Customer Segment** | AMC, Regional, Community, Ambulatory, Public Sector |
| **Deal Size** | < $100K, $100K-$500K, $500K-$1M, > $1M |
| **Buying Committee** | Roles involved (clinical, IT, procurement, C-suite, compliance) |
| **Adoption Stage** | Visionary (early adopter) vs. Pragmatist (early majority) — per Moore's Crossing the Chasm |
| **Status Quo** | Lost to named competitor vs. lost to "no decision" vs. lost to incumbent |
| **Champion** | Had champion (Y/N), champion equipped (Y/N), champion survived internal scrutiny (Y/N) |
| **Behavioral Force** | Primary behavioral driver: loss aversion, status quo bias, FOMU, choice overload, social proof gap |

### 3.3 Win Reason Categories

| Code | Category |
|------|----------|
| **PROD-WIN** | Product strength / capability superiority |
| **PLAT-WIN** | Oracle ecosystem / platform value (cloud, DB, ERP) |
| **REF-WIN** | Reference customers / social proof was decisive |
| **REL-WIN** | Relationship / sales team quality |
| **IMPL-WIN** | Implementation approach / timeline confidence |
| **PRICE-WIN** | Pricing advantage or flexible packaging |
| **AI-WIN** | AI / automation capabilities |
| **STRAT-WIN** | Strategic alignment / long-term vision match |

---

## PHASE 4: REPORTING — THREE-TIER SYSTEM

### 4.1 Weekly Flash Report (1 page)

```
WEEKLY WIN-LOSS FLASH — [Date Range]
INTERVIEWS COMPLETED: [X] wins, [Y] losses, [Z] no-decision
TOP FINDING THIS WEEK: [One sentence]
BUYER QUOTE: "[Direct quote]" — [Role], [Segment], [Win/Loss]
PATTERN UPDATE:
  - [Theme 1]: [X] mentions this period ([trending up/down/stable])
  - [Theme 2]: [X] mentions this period
ACTIONS NEEDED:
  - [Specific insight] → [Owner] → [Due date]
```

### 4.2 Monthly Insight Report (7 sections)

1. Executive summary (3-4 sentences)
2. Volume and mix (interview count, win/loss split, competitor breakdown)
3. Driver distribution (5 actual-driver categories vs. prior month)
4. Top 3 actionable findings (with buyer quotes, revenue impact estimate, recommended action)
5. Competitive perception update (what buyers are actually saying about competitors)
6. Trend lines (month-over-month)
7. Action tracker status (what happened with last month's actions)

### 4.3 Quarterly Strategic Review (10 slides max)

| Slide | Content |
|-------|---------|
| 1 | Win rate trend by segment (with program start date marked) |
| 2 | Top 5 actual loss drivers this quarter vs. last quarter |
| 3 | Revenue at risk by driver category |
| 4 | The Price Gap: what buyers SAY vs. what actually drives decisions |
| 5 | Champion analysis: % of losses where champion lacked ammunition |
| 6 | Competitive perception shifts (what buyers say about competitors — from their mouth, not ours) |
| 7 | Product gaps costing deals (with estimated revenue impact) |
| 8 | Sales execution patterns (failure modes by deal stage) |
| 9 | Actions taken this quarter + measured impact |
| 10 | Recommended investments for next quarter (ranked by estimated revenue recovery) |

Source: User Intuition three-tier reporting system, adapted for Oracle Health

---

## PHASE 5: ACTION ROUTING & TRACKING

### 5.1 Insight-to-Action Log

| Field | Description |
|-------|-------------|
| **Insight ID** | WL-2026-001 |
| **Date identified** | When pattern confirmed (3+ interviews) |
| **Driver category** | Which of 5 actual-driver categories |
| **Specific finding** | What exactly was found |
| **Supporting evidence** | Interview count + anonymized quotes |
| **Routed to** | Named individual |
| **SLA** | Response deadline |
| **Recommended action** | Proposed fix |
| **Action taken** | What actually happened |
| **Outcome measurement** | How we'll know it worked |
| **Status** | Open / In progress / Completed / No action |

### 5.2 Routing Matrix

| Finding Type | Routed To | SLA |
|-------------|-----------|-----|
| Product gap cited by 3+ buyers | **Product** | 2 weeks response, next roadmap review |
| Pricing/packaging concern pattern | **Pricing / Commercial** | 2 weeks response, 4 weeks action |
| Sales approach feedback | **Sales Enablement** | 1 week response, 2 weeks action |
| Champion enablement gap | **Sales Enablement** | 1 week response, 2 weeks action |
| Competitive positioning shift | **M&CI (Mike)** | 1 week response, 2 weeks action |
| Implementation concerns | **Services / Consulting** | 2 weeks response, 4 weeks action |
| Reference/proof gap | **Customer Marketing** | 2 weeks response, 4 weeks action |

SLA framework adapted from User Intuition insight-to-action methodology.

### 5.3 Integration with M&CI SOPs

| SOP | How Win/Loss Feeds It |
|-----|----------------------|
| **SOP-02 (Signal Triage)** | Win/loss patterns become competitive signals in Priority Engine |
| **SOP-07 (Competitor Profiles)** | Buyer-sourced competitor strengths/weaknesses update profiles |
| **SOP-08 (Battlecards)** | Verbatim buyer language goes into objection handling |
| **SOP-11 (Trade Show Intel)** | Conference intel validates or contradicts win/loss themes |
| **SOP-03 (Matt Weekly Brief)** | Significant patterns surfaced in Friday brief |

### 5.4 Sales Rep Feedback Loop

**Rep Input Form** (submitted via Salesforce within 7 days of deal close):

| Field | What Rep Enters |
|-------|----------------|
| Deal ID | Salesforce opportunity ID |
| Decision date | Date customer made decision (not contract date) |
| Primary competitor | Vendor that won or most serious competitor |
| Buyer title | Economic buyer title (VP IT, CFO, CMO, etc.) |
| One-sentence loss reason (CRM) | Whatever they marked in Salesforce — even if wrong |

The CRM loss reason is intentionally included *because* it's likely wrong. The laddering interview will surface the real driver. Comparing CRM reason vs. interview finding is itself a data point about how accurately the team diagnoses deal outcomes.

**Rep Output Summary** (Mike sends back within 5 business days of interview):

- One-paragraph synthesis of what the buyer actually said
- 2-3 rep-specific takeaways ("for your next deal with this segment...")
- Anonymized — no buyer name, no organization name in what's shared to the rep

### 5.5 Messaging Update Trigger

Win/loss data must actively update messaging — not just sit in reports.

**Automatic trigger:** When a theme appears in **3+ interviews** AND shifts by **>10 percentage points** from the established baseline → mandatory messaging review within 14 days.

| Theme Type | Who Reviews | Artifact Updated |
|-----------|-------------|-----------------|
| Loss driver pattern (e.g., impl risk increasing) | PMM + Sales Enablement | Battlecard objection handling |
| Win driver pattern (e.g., AI story winning more) | PMM | Website copy, event messaging |
| Competitor perception shift (e.g., Epic getting weaker on pricing) | Competitive Intel | SOP-07 competitor profiles |
| Oracle transition sentiment trend | Mike → Matt | Executive narrative, sales talking points |

**Hard rule:** No quarterly report goes to Matt without a "Messaging Implications" section that names at least one messaging change triggered by the data.

---

## PHASE 6: PROGRAM METRICS

### 6.1 Operational KPIs

| KPI | Target | Source |
|-----|--------|--------|
| Interviews per quarter | 8-12 (scaling to 20+) | Clozd benchmark |
| Win/loss balance | 40-60% split | User Intuition |
| Time from decision to interview | < 30 days | Anova/Clozd |
| Buyer response rate | 40%+ (60%+ with third-party) | Anova: 50-60% with third-party |
| Insight-to-action rate | 80%+ of routed findings result in action | User Intuition |
| Recurrence rate | Declining (same loss drivers appearing less over time) | User Intuition |

### 6.2 Business Impact (Long-term)

| Metric | Baseline | Target (12 months) | Source |
|--------|----------|-------------------|--------|
| Competitive win rate | Establish Q1 | +5-10 points | Clozd: 10% improvement typical year 1 |
| Revenue impact | Establish baseline | +15-30% | Gartner/Challenger research |
| Battlecard usage | Unknown | 70%+ | Crayon: 71% report improved win rates with battlecards |
| Deal insights | 0 | 40% of closed deals analyzed | Klue 2025: 40% average |

### 6.3 ROI Calculator (Clozd Framework)

```
Current annual revenue:           $__M
Current win rate:                 ___%
Total opportunity value:          Revenue / Win Rate = $__M
Improved win rate (+10%):         ___% (multiply current by 1.10)
New revenue at improved rate:     Total Opportunity × New Rate = $__M
Incremental revenue:              New Revenue - Current Revenue = $__M
```

Example: $50M revenue / 25% win rate = $200M opportunity. At 27.5% = $55M. **$5M incremental.**

Source: https://www.clozd.com/revenue-calculator

---

## HEALTHCARE-SPECIFIC CONSIDERATIONS

### The Healthcare Buying Committee

Healthcare IT purchasing is uniquely complex — multiple veto-holders with different objectives:

| Role | What They Care About | Win/Loss Questions |
|------|---------------------|-------------------|
| **CMO / CMIO** | Clinical workflow, provider adoption, patient outcomes | "How will this affect physician workflows?" |
| **CIO / CISO** | Integration, security, compliance, HIPAA | "What's the interoperability and security story?" |
| **CFO** | TCO, ROI, budget cycle alignment | "What's the total cost including implementation?" |
| **VP Revenue Cycle** | Claims, denials, collections, automation | "How does this improve revenue capture?" |
| **Procurement** | Contract terms, vendor risk, switching costs | "What are the switching costs and risks?" |
| **End Users** | Usability, training burden, workflow disruption | "How long until this is easier than what we have?" |

Source: Stanford GSB Case Study E615; Webster & Wind (1972) buying center model; ASU healthcare procurement research (2025)

### Healthcare-Specific Findings

- **34% of hospitals switched EMR vendors** between 2003-2008 — switching does happen but is painful (Lammers & Zheng, 2011, AMIA Proceedings)
- **Demonstrations and site visits provide superior discriminatory value** over self-reported vendor specs (Priestman et al., 2019, BMJ Health & Care Informatics — Great Ormond Street Hospital case study)
- **Implementation risk is disproportionately important in healthcare** — 23.8% actual driver vs. 4.1% stated (User Intuition data, corroborated by healthcare procurement research)
- **Physician champions face unique career + clinical risk** — they're advocating for a system that will affect patient care, not just efficiency
- **KLAS Research** (klasresearch.com) is the gold standard for healthcare IT vendor evaluation — consider cross-referencing win/loss findings with KLAS data

### Healthcare Calibration Caveat

> **Important:** The behavioral driver percentages in this SOP (44-point price gap, 23.8% implementation risk, etc.) are sourced from User Intuition's general B2B SaaS dataset (10,247 conversations). Healthcare IT purchasing has structural differences — longer cycles (12-24 months vs. 3-9 months in SaaS), more veto-holders (clinical, compliance, IT, CFO, board), regulatory constraints (HIPAA, 21st Century Cures), and higher career risk for champions. The coefficients may not transfer directly.
>
> **Recommendation:** After 20 Oracle Health interviews, run a recalibration analysis using the protocol below.

**Recalibration Protocol (execute at 20-interview milestone):**

1. **Compare coded drivers vs. baseline:** For each of the 5 actual driver categories (IMPL-RISK, CHAMP-FAIL, PRICE, TTV, COMP-POS), compare Oracle Health's coded frequency against the User Intuition general B2B baseline (23.8%, 21.3%, 18.1%, 16.9%, 11.4%).
2. **Flag meaningful deviations:** Any category where Oracle Health's frequency differs by **>5 percentage points** from the baseline is flagged for review.
3. **Update simulation weights:** Revise the behavioral risk factor weights in `predictive_winloss.py` (the values in `compute_behavioral_risk_score()`) to reflect Oracle Health-specific frequencies.
4. **Approval gate:** Updated weights require Mike's sign-off and a note in the revision history. Matt Cohlmia is notified if any category shifts by >10pp (signals a strategic pattern, not just calibration noise).
5. **Cadence:** Re-run this recalibration at 20, 50, and 100 interviews. After 100 interviews, consider replacing hand-tuned weights with a logistic regression model trained on Oracle Health's own deal outcomes.

### IDN/Health System Consolidation — Distinct Deal Type

**A significant portion of Oracle Health pipeline involves IDN/health system consolidation events** — an acquired community hospital must standardize on the IDN's platform. This is a fundamentally different buying trigger than competitive greenfield evaluation.

| Dimension | Competitive Greenfield | IDN Consolidation |
|-----------|----------------------|-------------------|
| Primary driver | Best vendor wins | Standardization mandate (political) |
| Key decision-maker | Hospital CIO / CMO | IDN IT leadership / Board |
| Competitive dynamic | Oracle vs. Epic head-to-head | Oracle vs. "we already have [X]" |
| Status quo bias | Moderate | Very high (community hospital may resist) |
| Champion | Hospital IT leadership | IDN CIO as champion *and* buyer |
| Timeline | 6-18 months | Often 3-6 months (mandate-driven urgency) |

**Modified laddering questions for consolidation deals:**
- "How was the decision made to standardize platforms across the IDN, and who drove that decision?"
- "What was the biggest concern from the community hospital leadership about losing their current system?"
- "Was there any internal resistance? How was it handled?"
- "What would have made the transition feel more like a partnership and less like a mandate?"

**Flag consolidation deals separately in CRM and in the coding taxonomy** — their loss drivers are different (inertia/resistance to mandate, not competitive evaluation), and their insights should not be pooled with competitive deals without controlling for deal type.

---

## 90-DAY LAUNCH PLAN

| Week | Action | Owner |
|------|--------|-------|
| **1** | Mike reviews and approves this SOP | Mike |
| **2** | Finalize interview guides (customize laddering probes for Oracle Health context) | Mike |
| **3-4** | Identify first 8 deal candidates from CRM (3 wins, 5 losses) | Mike + Sales Ops |
| **5-8** | Conduct first 8 interviews using laddering methodology | Mike |
| **9-10** | Code interviews using 5-category actual-driver taxonomy | Mike |
| **11** | Produce first Weekly Flash + Monthly Insight Report | Mike |
| **12** | Present first Quarterly Strategic Review to Matt | Mike → Matt |
| **Ongoing** | Scale to 12-20 interviews/quarter, refine questions | Mike |

---

## PHASE 5: PREDICTIVE WIN/LOSS — MONTE CARLO SIMULATION ENGINE

### 5.1 Why Prediction, Not Just Retrospection

Traditional win/loss analysis is **retrospective** — it tells you why you lost after the deal is over. Phase 5 adds a **predictive layer** that estimates win probability *while the deal is still active*, enabling real-time resource allocation, intervention triggers, and pipeline prioritization.

**The shift:**
| Traditional Win/Loss | Predictive Win/Loss |
|---------------------|---------------------|
| Interviews post-decision | Probability scoring during active deal |
| Explains the past | Influences the future |
| Sample of closed deals | Applied to every deal in pipeline |
| Qualitative themes | Quantified risk factors + confidence intervals |
| Weekly/quarterly cadence | Real-time or on-demand |

### 5.2 Industry Calibration Reference: HP/Compaq → Oracle/Cerner

The simulation is calibrated against the **HP/Compaq acquisition (2002)** — the closest historical parallel to Oracle's acquisition of Cerner.

**The parallel:**

| Dimension | HP/Compaq (2002) | Oracle/Cerner (2022) |
|-----------|-----------------|----------------------|
| Acquisition type | Major tech consolidation ($25B) | Major health IT consolidation ($28B) |
| Brand confusion | Compaq → HP; customers unsure who to call | Cerner → Oracle Health; same confusion |
| Market leader response | IBM + Dell capitalized aggressively | Epic capitalized on transition uncertainty |
| Win rate degradation | ~18% market share loss in years 1-2 | Estimated 15-22% win rate degradation |
| Recovery timeline | 4 years to competitive parity | Expected 2026-2027 if reference wins execute |
| Key recovery driver | HP ProLiant reference wins + field engagement | Oracle Health reference wins + roadmap proof |

**Why this calibration matters:** HP/Compaq buyer surveys showed that customers with "very negative" transition perception had **2.3x lower close rates** compared to neutral baseline. This coefficient is embedded in the simulation as the `VERY_NEGATIVE` transition sentiment multiplier.

**Recovery pattern (HP/Compaq):** The recovery was driven NOT by messaging changes but by three specific actions:
1. **Reference wins in the same segment** — proof that real customers had a good experience post-acquisition
2. **Executive engagement** — HP CEO-level visits to at-risk accounts
3. **Roadmap transparency** — publishing a multi-year product roadmap that addressed "will HP kill Compaq products?"

All three have direct Oracle Health equivalents.

### 5.3 The Monte Carlo Algorithm

**File:** `susan-team-architect/backend/jake_brain/predictive_winloss.py`

#### How It Works

The simulation uses a **two-phase approach**:

**Phase A — Deterministic Base Probability:**
```
base = product_line_base_rate
     × sales_stage_probability (blended 40/60)
     × competitor_difficulty_multiplier
     × customer_segment_modifier
     × deal_size_modifier
     × transition_sentiment_modifier
     × relationship_strength_modifier
     × reference_customer_boost (if available)
     × oracle_ecosystem_boost (if active)
     × behavioral_risk_reduction (up to 60% penalty)
```

**Phase B — Monte Carlo Uncertainty Layer (10,000 runs):**

For each simulation run, five stochastic factors are independently sampled from normal distributions:

| Factor | Distribution | Variance | Why High/Low |
|--------|-------------|----------|--------------|
| Competitive response intensity | N(1.0, 0.15) | ±15% | Competitor behavior is partially unpredictable |
| Stakeholder alignment | N(1.0, 0.20) | ±20% | Committee dynamics shift during evaluation |
| Market timing / budget cycle | N(1.0, 0.10) | ±10% | Budget approval is relatively stable |
| Champion stability | N(strength, 0.25) | ±25% | **Highest variance** — HP/Compaq showed champion departure as dominant uncertainty |
| Implementation capacity | N(1.0, 0.12) | ±12% | Oracle implementation bandwidth varies |

The mean of 10,000 simulated win probabilities becomes the final prediction. The 5th/95th percentile spread is the 90% confidence interval.

#### Output Schema

```python
PredictionResult:
    win_probability_pct: float          # e.g., 34.2%
    confidence_interval_90: tuple       # e.g., (18.1%, 52.6%)
    confidence_interval_50: tuple       # e.g., (26.4%, 42.0%)
    probability_tier: str               # STRONG / MODERATE / CHALLENGING / LONGSHOT
    transition_calibration_note: str    # HP/Compaq context specific to this deal
    top_risk_factors: list[dict]        # Ranked risks with evidence + recommended actions
    recommended_actions: list[str]      # Prioritized interventions
    behavioral_risk_score: float        # 0.0-1.0 composite behavioral risk
```

### 5.4 Model Variables: Input Factors

Every deal is scored on 15+ factors:

**Deal Characteristics:**
| Variable | Values | Impact |
|----------|--------|--------|
| `product_line` | EHR, RCM, AI Agents, etc. | Base win rate: EHR (28%) to Life Sciences (50%) |
| `deal_size_usd` | Raw USD | Larger = more scrutiny = lower probability |
| `customer_segment` | AMC, Regional, Community, etc. | AMC hardest (Epic-dominant), Community easiest |
| `sales_stage` | Discovery → Verbal Win | Discovery (12%) to Verbal Win (82%) |
| `num_competitors` | Integer | >3 vendors = choice overload penalty |

**Competitive & Transition Factors:**
| Variable | Values | Impact |
|----------|--------|--------|
| `primary_competitor` | Epic, Meditech, No Decision, etc. | Epic: -45% multiplier; No Decision: -55% |
| `transition_sentiment` | Very Positive → Very Negative | Very Negative: -57% (2.3x HP/Compaq penalty) |
| `is_existing_oracle_customer` | bool | +22% land-and-expand advantage |
| `oracle_ecosystem_value` | bool | +18% platform story boost |

**Behavioral Risk Factors (0.0-1.0):**
| Variable | Driver It Measures | Weight in Model |
|----------|-------------------|-----------------|
| `champion_strength` | Champion confidence failure (21.3% of losses) | 0.213 |
| `implementation_risk_concern` | Implementation risk (23.8% of losses) | 0.238 |
| `time_to_value_anxiety` | TTV anxiety (16.9% of losses) | 0.169 |
| `price_sensitivity` | Price (18.1% ACTUAL, not 62.3% stated) | 0.181 |
| `status_quo_bias` | Inertia / "no decision" pressure | 0.100 |

**Weights sourced from User Intuition's 10,247-conversation dataset (SOP-09 behavioral science foundation).**

### 5.5 Base Win Rates by Product Line

Calibrated to Oracle Health competitive landscape (2024-2025 estimates):

| Product Line | Base Win Rate | Key Competitor | Primary Risk |
|-------------|---------------|---------------|--------------|
| EHR | 28% | Epic (70%+ market share in AMC/Regional) | Transition sentiment + Epic dominance |
| RCM | 38% | Waystar | Platform story advantage |
| Patient Portal | 42% | Various | Oracle ecosystem advantage |
| AI Agents | 45% | Regard, Epic AI | New category — less entrenched |
| Population Health | 35% | Health Catalyst | Reference customer gap |
| Analytics / BI | 40% | Various | Oracle platform story |
| Life Sciences | 50% | Less competitive | Oracle brand strength |

### 5.6 Usage — Running Predictions

**Demo (3 pre-built Oracle Health scenarios):**
```bash
cd /Users/mikerodgers/Startup-Intelligence-OS
python3 susan-team-architect/backend/jake_brain/predictive_winloss.py --demo
```

**Programmatic use:**
```python
from jake_brain.predictive_winloss import DealInput, predict, Competitor, CustomerSegment
from jake_brain.predictive_winloss import ProductLine, SalesStage, TransitionSentiment, RelationshipStrength

deal = DealInput(
    deal_id="OH-2025-042",
    deal_name="St. Mary's Health System — EHR Replacement",
    deal_size_usd=1_200_000,
    product_line=ProductLine.EHR,
    customer_segment=CustomerSegment.REGIONAL,
    primary_competitor=Competitor.EPIC,
    sales_stage=SalesStage.RFP,
    transition_sentiment=TransitionSentiment.SOMEWHAT_NEGATIVE,
    relationship_strength=RelationshipStrength.STRONG,
    champion_strength=0.65,
    implementation_risk_concern=0.55,
    reference_customer_available=True,
    oracle_ecosystem_value=True,
)

result = predict(deal)
print(f"Win probability: {result.win_probability_pct}%")
print(f"Tier: {result.probability_tier}")
```

### 5.7 Interpretation Guide

| Win Probability | Tier | Recommended Response |
|----------------|------|---------------------|
| ≥ 60% | STRONG | Protect. Confirm budget/timeline. Map new stakeholders. Don't get complacent. |
| 40-59% | MODERATE | Execute. Differentiate on Oracle platform story. Build champion confidence. |
| 25-39% | CHALLENGING | Intervene. Escalate to executive engagement. Deploy targeted reference. |
| < 25% | LONGSHOT | Triage. Ask champion "what would have to be true to win?" If no answer, de-prioritize. |

### 5.8 Confidence Interval Interpretation

The 90% confidence interval reflects **uncertainty in the simulation**, driven primarily by:
- Champion stability variance (±25% — highest uncertainty factor)
- Stakeholder alignment unpredictability (±20%)

**Narrow interval** (e.g., 32-38%) = High certainty. The deal's outcome is fairly predictable given current inputs.

**Wide interval** (e.g., 15-65%) = High uncertainty. Small changes in champion or stakeholder dynamics could swing the deal. This is a signal to gather more information, not a reason to give up.

### 5.9 When to Re-Run the Prediction

Trigger a new prediction when any of these events occur:

| Trigger | Why It Matters |
|---------|---------------|
| Sales stage advances | Stage is the strongest single predictor |
| Champion changes or goes dark | Champion stability is highest-variance factor |
| Customer mentions Oracle/Cerner transition explicitly | Transition sentiment should be re-scored |
| Competitor changes (new entrant or dropout) | Difficulty multiplier changes |
| Executive engagement occurs | Relationship strength can upgrade 1-2 levels |
| Deal goes quiet (>14 days no activity) | Staleness penalty kicks in |
| Budget cycle event (approval, deferral) | Timing and deal size impact changes |

### 5.10 Integration Roadmap

| Phase | Capability | Timeline |
|-------|-----------|----------|
| **Current** | CLI prediction engine, manual deal input | Available now |
| **Q2 2026** | Salesforce CRM connector — auto-pull deal fields | 2026 Q2 |
| **Q2 2026** | Batch scoring for full pipeline (50+ deals) | 2026 Q2 |
| **Q3 2026** | Bayesian updating — model learns from actual outcomes | 2026 Q3 |
| **Q4 2026** | Dashboard integration with Ellen's GenChat KB | 2026 Q4 |
| **2027** | ML model replaces hand-tuned weights — trained on 100+ oracle deals | 2027 |

---

## ETHICAL & LEGAL

- Anonymize all data before sharing internally
- Obtain verbal consent before recording
- Never attribute quotes to specific buyers without explicit permission
- Frame as "your feedback helps us improve" — never promise action
- Comply with Oracle data handling policies
- Align with SCIP Code of Ethics for primary intelligence collection

### Handling Inadvertent Competitor Disclosures

During laddering interviews, buyers occasionally share information about competitor roadmaps, pricing structures, or contractual terms that they may have received in confidence. This requires a specific handling protocol:

| Situation | Action |
|-----------|--------|
| Buyer shares competitor pricing | Note in restricted log only. Do NOT include in standard reports. Consult Oracle legal before any use. |
| Buyer shares competitor roadmap details | Same — restricted log, legal review required. Buyer may be under NDA with competitor. |
| Buyer shares details of their own Oracle contract | Permitted — this is Oracle's own data. Use with standard anonymization. |
| Buyer shares employee names at competitor | Acceptable as competitive intelligence. Handle per SCIP Code of Ethics. |

**Restricted log:** Mike maintains a separate `win-loss-restricted-intel.md` (not shared with team) for inadvertent disclosures pending legal review. This is distinct from the standard interview coding file.

**The rule:** If you wouldn't want to explain in a deposition how you used a piece of information, document it in the restricted log instead of the main intel system.

---

## SOURCE ATTRIBUTION — ALL SCRAPED, ZERO TRAINING DATA

### Practitioner Platforms (Scraped via Brave, Tavily, Exa)
1. **Klue** — 31-question framework, 7-step methodology, 4 maturity stages, 2025 Trends Report (300+ leaders). https://klue.com/blog/win-loss-analysis-guide
2. **Clozd** — 6-step program, 4 pillars, 5-phase maturity curve, ROI calculator. https://www.clozd.com/blog/kicking-off-your-first-win-loss-analysis-project
3. **Anova Consulting** — 7-step implementation, 60% truth-telling gap, third-party recommendation. https://www.theanovagroup.com/win-loss-analysis-insights/
4. **User Intuition** — 44-point price gap (10,247 conversations), laddering methodology, 5 actual-driver categories, three-tier reporting. https://www.userintuition.ai/posts/win-loss-analysis-complete-guide/
5. **Corporate Visions / Primary Intelligence** — 100K+ deals analyzed, 85% CRM data wrong, TruVoice platform. https://corporatevisions.com/blog/win-loss-analysis-competitive-intelligence/
6. **Crayon** — CI + win/loss integration, battlecard impact (71% report improved win rates), State of CI reports. https://www.crayon.co/state-of-competitive-intelligence
7. **Pragmatic Institute** — 7-step implementation guide, program coordinator role. https://www.pragmaticinstitute.com/resources/articles/product/how-to-implement-a-winloss-program/

### Behavioral Science (Scraped via Brave, Tavily, Exa)
8. **Kahneman & Tversky (1979)** — Prospect Theory, loss aversion ~2x. *Econometrica*, 47(2), 263-292. https://web.mit.edu/curhan/www/docs/Articles/15341_Readings/Behavioral_Decision_Theory/Kahneman_Tversky_1979_Prospect_theory.pdf
9. **Samuelson & Zeckhauser (1988)** — Status quo bias. *Journal of Risk and Uncertainty*, 1, 7-59.
10. **Webster & Wind (1972)** — Organizational Buying Behavior model (1,810 citations). *Journal of Marketing*, 36(2). https://faculty.wharton.upenn.edu/wp-content/uploads/2012/04/7215_A_General_Model_for_Understanding.pdf
11. **Robinson, Faris & Wind (1967)** — BuyGrid framework. https://faculty.wharton.upenn.edu/wp-content/uploads/2012/04/9802_The_BuyGrid_Model_30_Years.pdf
12. **Dixon & Adamson (2011)** — *The Challenger Sale*, 6,000 reps surveyed. CEB/Gartner.
13. **Dixon (2022)** — *The Jolt Effect*, FOMO vs. FOMU distinction.
14. **Moore (1991/2014)** — *Crossing the Chasm*, technology adoption lifecycle.
15. **Christensen et al. (2016)** — JTBD framework, *Competing Against Luck*. https://hbr.org/2016/09/know-your-customers-jobs-to-be-done
16. **Thaler & Sunstein (2008)** — *Nudge*, choice architecture. Nobel Prize 2017.
17. **Cialdini (1984)** — *Influence*, social proof in B2B.

### Academic Research (Scraped via Brave, Tavily, Exa)
18. **Ahearne et al. (2013)** — CI quality → sales performance. *Journal of Marketing*, 77(5), 37-56. DOI: 10.1509/jm.11.0217
19. **Dickson (1966)** — 23 vendor selection criteria (1,782 citations). *Journal of Purchasing*, 2(1).
20. **Lammers & Zheng (2011)** — Hospital vendor switching: 34% switched EMR 2003-2008. AMIA Proceedings. https://pmc.ncbi.nlm.nih.gov/articles/PMC3243192/
21. **Priestman et al. (2019)** — Demos > self-reported specs. *BMJ Health & Care Informatics*, 26(1). https://informatics.bmj.com/content/bmjhci/26/1/e000020.full.pdf
22. **Polites & Karahanna (2012)** — Incumbent habit as resistance to new systems. *MIS Quarterly*.
23. **Gartner 2025** — 74% buying groups show unhealthy conflict; 61% prefer rep-free. Press releases.
24. **Dzreke & Dzreke (2025)** — AI-enhanced CI = 18-22% higher profitability (200 enterprises). *IJRAR*.

### Healthcare-Specific (Scraped via Brave, Tavily, Exa)
25. **Stanford GSB Case E615** — Stanford Medicine health IT purchasing decisions. https://www.gsb.stanford.edu/faculty-research/case-studies/stanford-medicine-health-it-purchasing-decisions-complex-medical
26. **Eliciting Insights** — Healthcare-specific win/loss firm. https://elicitinginsights.com/blog/win-loss-analysis/
27. **KLAS Research** — Healthcare IT vendor evaluation gold standard. https://klasresearch.com
28. **ASU W.P. Carey (2025)** — Hospital procurement: physician preferences + supplier services + outcomes. https://news.asu.edu/20251003-business-and-entrepreneurship-new-study-shows-how-hospitals-buy-supplies-could-make-or

### Oracle Health Internal
29. **Mike's HIMSS field questions** — Informal win/loss questioning at conferences
30. **Matt's KPI framework** — Competitive landscape as tracked function
31. **Ellen KB catalog** — `genchat-kb-mci-win-loss-intelligence.md` (planned, not yet built; David Okonkwo as Win/Loss Lead)
32. **ChatGPT department design** — 8-step intelligence cycle with "Track outcomes and learn back"
