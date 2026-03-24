# SOP-10: Pricing & Packaging Intelligence

**Owner**: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-23
**Category**: Competitive Intelligence Production
**Priority**: P1 — Win rate driver, high sales value
**Maturity**: Automated (Excel generation) → Documented

---

## Table of Contents

1. [Purpose](#1-purpose)
2. [Scope](#2-scope)
3. [Pricing Data Architecture](#3-pricing-data-architecture)
4. [Data Collection Methods](#4-data-collection-methods)
5. [Confidence Scoring Rules](#5-confidence-scoring-rules)
6. [Validation Protocol](#6-validation-protocol)
7. [The Excel Workbook Standard](#7-the-excel-workbook-standard)
8. [Update Cadence](#8-update-cadence)
9. [Distribution Protocol](#9-distribution-protocol)
10. [Predictive Algorithm: Pricing Gap Priority Score (PGPS)](#10-predictive-algorithm-pricing-gap-priority-score-pgps)
11. [Monte Carlo: Discount Band Modeling](#11-monte-carlo-discount-band-modeling)
12. [Legal & Compliance Controls](#12-legal--compliance-controls)
13. [Field Feedback Loop](#13-field-feedback-loop)
14. [Quality Gates](#14-quality-gates)
15. [RACI Matrix](#15-raci-matrix)
16. [KPIs](#16-kpis)
17. [Expert Panel Scoring](#17-expert-panel-scoring)

---

## 1. Purpose

Pricing intelligence is the highest-leverage input in a competitive deal. When a sales rep knows that Epic's RCM module discounts 20-28% on competitive bids, they stop leaving money on the table by matching apples to apples. When they know Cerner's per-user pricing crosses a threshold at 500 beds, they can architect proposals that make Oracle Health structurally cheaper at the specific deal size they're competing on.

This SOP governs Oracle Health's end-to-end Pricing & Packaging Intelligence program: how pricing data is collected, validated, confidence-coded, stored in the master Excel workbook, published to stakeholders, and continuously refreshed. It also specifies the two analytical models — the Pricing Gap Priority Score (PGPS) algorithm and the Monte Carlo Discount Band model — that transform raw pricing observations into actionable deal guidance.

**Why this matters (quantified):**

- Pricing is cited as the #1 stated reason for deal losses in B2B enterprise software — but as SOP-09 documents, stated reasons often mask real drivers. Accurate pricing intelligence helps sales teams distinguish genuine price objections from other objections dressed up as price.
- 40-60% of enterprise software deals involve negotiation where competitive pricing knowledge directly shifts proposal strategy (Gartner, Strategic Sourcing research).
- Oracle Health field reps consistently report that "knowing the competitor's real number" changes negotiation posture in competitive deals.
- Pricing data decays: a 12-month-old price point in a market where vendors re-price annually is worse than no data — it creates false confidence. This SOP enforces decay rules that keep the workbook honest.

**What this SOP produces:**

| Output | Audience | Cadence |
|--------|----------|---------|
| Master Pricing Excel Workbook | CI team, Sales Leadership | Quarterly refresh + event-triggered |
| Competitor Pricing Quick Reference | AEs, SEs | Quarterly + as updated |
| Discount Band Guidance (Monte Carlo output) | Sales VP, Deal Desk | Per-request + quarterly |
| Pricing Gap Priority Report | CI team, Sales Strategy | Quarterly |
| Deal-Specific Pricing Brief | Account team (by request) | On-demand |

---

## 2. Scope

### In Scope

**Competitors covered** (primary competitive set):

| Vendor | Products Tracked | Priority |
|--------|-----------------|----------|
| Epic Systems | EHR, RCM, Ambulatory, Patient Portal, Bridges | P1 |
| Cerner (Oracle Health legacy) | Millennium, PowerChart, RevElate | P1 — internal cross-ref |
| Meditech | Expanse, Expanse Now | P1 |
| athenahealth | athenaOne, athenaClinicals | P2 |
| PointClickCare | Core Platform, Pharmacy, Staffing | P2 |
| Veeva Systems | Vault (life sciences adjacent) | P3 |
| Netsmart | myUnity, CareFabric | P2 |
| TruBridge | EHR, RCM | P3 |
| NextGen Healthcare | Enterprise, Ambient Assist | P2 |
| Greenway Health | Intergy, Prime Suite | P3 |

**Pricing models tracked:**

- Per-organization (enterprise license)
- Per-provider / per-user (concurrent or named)
- Usage-based (per-transaction, per-encounter, per-claim)
- Module-based (base platform + add-ons)
- Outcome-based (at-risk pricing, shared savings)
- Managed service / SaaS subscription
- Implementation + professional services (separate line)

**Packaging intelligence tracked:**

- Bundle configurations (what comes in the base, what's add-on)
- Contract term structures (3-year vs. 5-year incentives)
- Volume discounts (bed count tiers, org size thresholds)
- Competitive displacement pricing (take-out deals)
- Renewal vs. new logo pricing differential

### Out of Scope

- Oracle Health's own internal pricing strategy (owned by Product Marketing and Pricing team)
- Public sector / federal contracting pricing (GSA schedules — separate program)
- Pharmaceutical pricing or device pricing
- Oracle Health partner/reseller pricing

---

## 3. Pricing Data Architecture

### 3.1 The Master Data Model

All pricing data is stored in `ORACLE_HEALTH_PRICING_MASTER_DATA.csv` and rendered by `build_pricing_excel.py` into a color-coded Excel workbook. The data model is built around the concept of a **pricing observation** — a single data point about a single vendor's single product or module at a point in time.

```
One row = one pricing observation
One vendor can have many rows (one per product/module)
Multiple observations for the same product are versioned by Date field
The highest-confidence, most-recent observation is the "active" record
```

### 3.2 Data Schema — Full Column Specification

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `record_id` | UUID | Unique identifier for this observation | `epic-rcm-2026-03-001` |
| `vendor` | String | Competitor name (standardized) | `Epic Systems` |
| `product_module` | String | Specific product or module | `Revenue Cycle Management (Resolute)` |
| `pricing_model` | Enum | How the product is priced | `per-org`, `per-provider`, `usage-based`, `hybrid` |
| `unit` | String | Unit of measurement for pricing | `per acute bed`, `per provider FTE`, `per claim` |
| `list_price` | Numeric | Published or observed list price | `$2,400,000` |
| `list_price_currency` | String | Currency (default USD) | `USD` |
| `list_price_basis` | String | What the list price covers | `500-bed health system, 3-year license` |
| `street_price` | Numeric | Actual transacted price (post-discount) | `$1,850,000` |
| `discount_pct_low` | Numeric | Low end of observed discount range | `15%` |
| `discount_pct_high` | Numeric | High end of observed discount range | `28%` |
| `discount_notes` | String | Context on when discounts apply | `Higher discounts for competitive displacement` |
| `bundle_options` | String | What modules bundle together | `Resolute RCM + Prelude ADT + Grand Central scheduling` |
| `add_on_products` | String | Common add-ons and pricing | `Cognitive Computing: $120K/yr; MyChart: $45/provider/mo` |
| `contract_length_typical` | String | Typical contract term | `5-year; 3-year available with 10-15% premium` |
| `payment_terms` | String | How payments are structured | `Annual in advance; quarterly available` |
| `implementation_cost` | String | Professional services estimate | `$800K-$2.1M for 500-bed system` |
| `confidence` | Enum | Data confidence level | `HIGH`, `MEDIUM`, `LOW`, `GAP` |
| `source_type` | Enum | Category of data source | `field`, `web`, `earnings`, `interview`, `analyst` |
| `source_detail` | String | Specific source (anonymized) | `Field rep report — Northeast region, 2 deals` |
| `date_collected` | Date | When this data was collected | `2026-01-15` |
| `date_expires` | Date | When this observation ages out | `2026-07-15` (180 days from collection) |
| `validated_by` | String | Who validated this entry | `Mike Rodgers` |
| `deal_context` | String | Deal context if applicable | `Competitive displacement, 350-bed community hospital` |
| `notes` | String | Freeform additional context | `Epic offered 2 years free implementation support to win` |
| `tags` | String | Classification tags | `competitive-displacement, hospital, midwest` |

### 3.3 Vendor Standardization Table

All vendor names must match the standardized list to prevent duplicate analysis. Acceptable names:

| Standard Name | Also Known As (do not use) |
|--------------|---------------------------|
| Epic Systems | EPIC, Epic, Epic EHR |
| Meditech | MEDITECH, Med/Tech |
| athenahealth | Athena, AthenaHealth, athenaOne |
| PointClickCare | PCC, Point Click Care |
| Netsmart | NetSmart, NetSmart Technologies |

### 3.4 Observation Lifecycle

```
COLLECTED → VALIDATED → ACTIVE → AGING → EXPIRED

COLLECTED:  Raw data entered, confidence = LOW by default
VALIDATED:  Second source confirmed or analyst review complete
ACTIVE:     High confidence, within 180-day freshness window
AGING:      90-180 days old — flagged for re-validation
EXPIRED:    >180 days old — moved to archive, not used in workbook
```

---

## 4. Data Collection Methods

Pricing data for competitors arrives from four primary channels. Each channel has different reliability characteristics, collection protocols, and appropriate confidence levels upon ingestion.

### 4.1 Field Source Collection

**What it is:** Sales representatives reporting competitor pricing they encountered in active deals — bids, RFP responses, pricing sheets shared by customers, or information volunteered by prospects during vendor comparison.

**Why it's the gold standard:** Field data is direct market evidence. A rep who saw Epic's pricing proposal in a deal is not estimating — they have a real number from a real negotiation.

**Collection protocol:**

1. Sales reps submit pricing intelligence via Salesforce CRM custom fields (see Section 13: Field Feedback Loop for full CRM workflow)
2. CI team receives automated notification via Salesforce → Slack integration when a new competitive pricing record is created
3. CI analyst reviews within 5 business days:
   - Verify the data is specific enough to be useful (not "they were cheaper")
   - Capture deal context (bed count, org type, region, competitive vs. non-competitive deal)
   - Anonymize the source (never expose which customer shared competitor data)
   - Assign initial confidence = MEDIUM if single source; escalate to HIGH if second source confirms within 180 days

**Data quality rules for field sources:**

| Data Attribute | Minimum Acceptable | Ideal |
|----------------|-------------------|-------|
| Specificity | Dollar range (not just "cheaper/more expensive") | Exact line-item pricing |
| Context | Deal size (org type + beds/providers) | Full deal context with competitive dynamics |
| Recency | Within 180 days | Within 90 days |
| Source count | 1 (initial MEDIUM confidence) | 2+ (HIGH confidence) |

**Field source red flags (do not enter without additional verification):**

- "I heard Epic was at $X" without direct documentation
- Pricing shared by a vendor rep about their own competitor (self-serving, often distorted)
- Pricing from a deal that didn't close (prospect may have anchored artificially low to extract concessions)

### 4.2 Web & Public Source Collection

**What it is:** Pricing information from publicly accessible sources — pricing pages, press releases, analyst reports, SEC filings, earnings calls, and industry publications.

**Most healthcare IT vendors do not publish pricing.** However, the following public sources yield useful data points:

| Source Type | Typical Data Available | Reliability |
|-------------|----------------------|-------------|
| Vendor pricing pages | Rarely published for enterprise; sometimes starter tiers | LOW — if published, assume it's the floor |
| Earnings call transcripts | Deal value ranges, ASP commentary | MEDIUM — executive statements, not granular |
| Gartner Market Guides | Pricing benchmarks by segment | MEDIUM — often 6-18 months old |
| KLAS Research reports | Vendor pricing commentary, customer satisfaction with value | MEDIUM |
| HIMSS Analytics | Benchmark pricing by hospital size | MEDIUM |
| SEC 8-K/10-K filings | Contract value disclosures for material deals | HIGH for specific deals, non-generalizable |
| Job postings | Implementation/professional services rates (contract staff) | LOW — indirect signal |
| LinkedIn / industry forums | Anecdotal pricing discussions | LOW |
| G2 / Capterra / Software Advice | User reviews mentioning price | LOW — consumer software bias, rarely enterprise |

**Web collection protocol:**

1. CI analyst runs quarterly web sweep using Firecrawl and Brightdata MCP tools
2. Earnings call transcripts processed via YouTube Transcript MCP + LLM extraction
3. Analyst report summaries extracted from KLAS and Gartner via subscription access
4. All web-sourced data entered with `source_type = web` and `confidence = LOW` initially
5. Web data can be upgraded to MEDIUM only if corroborated by a field source or second independent web source

**Automated monitoring:**

The TrendRadar MCP monitors competitor pricing mentions across news feeds, industry publications, and analyst commentary daily. Alerts route to the CI analyst for review and potential workbook entry.

### 4.3 Customer Interview Source Collection (Win/Loss Integration)

**What it is:** Pricing intelligence captured during win/loss interviews conducted per SOP-09. Buyers who participated in competitive evaluations often know exactly what they were quoted and by whom.

**Integration with SOP-09:**

- Win/loss interview guide includes a dedicated pricing section (see Section 4.3.1 below)
- Pricing data extracted from interview transcripts by CI analyst within 5 business days of interview
- Entered with `source_type = interview`
- Initial confidence = MEDIUM (buyer has direct knowledge but may misremember)
- Upgraded to HIGH if corroborated by a second interview or field data point within 180 days

**4.3.1 Pricing Questions for Win/Loss Interviews**

The following questions are integrated into the SOP-09 win/loss interview guide as a dedicated pricing module. They are asked after the decision narrative section to avoid anchoring bias:

```
Pricing Intelligence Module (Win/Loss Interview)
Time: 5-7 minutes of the total 30-minute interview

1. "During the evaluation, how did the vendors' pricing compare to your expectations
   going in? Were any vendors significantly higher or lower than anticipated?"

2. "Without sharing anything confidential, can you give me a general sense of where
   [Competitor X] came in relative to [Oracle Health]? Were we in the same ballpark,
   significantly higher, or significantly lower?"

3. "Did any vendors offer pricing structures that were unusual or creative — like
   outcome-based pricing, multi-year incentives, or unusual bundling?"

4. "What was the total cost of ownership picture? Did implementation and support costs
   factor significantly into the decision?"

5. "If you were advising [Oracle Health] on our pricing approach for deals like yours,
   what would you tell us?"
```

**Interview pricing data handling rules:**

- Never press for exact competitor figures if the buyer is hesitant — the relationship matters more than one data point
- Always get consent for using the data (verbally confirmed in interview, per SOP-09 consent protocol)
- Do not attribute pricing data to a named buyer in any internal document — use region + org type only

### 4.4 Industry Analyst & Report Source Collection

**What it is:** Pricing benchmarks, market estimates, and comparative pricing analysis from subscribed analyst services and published reports.

**Primary sources:**

| Source | Oracle Health Subscription? | Data Quality | Update Frequency |
|--------|---------------------------|--------------|-----------------|
| KLAS Research | Yes | High — direct buyer surveys | Annual + ad hoc |
| Gartner Research | Yes | High — structured benchmarks | Annual |
| IDC Health Insights | Selective | Medium | Annual |
| Chilmark Research | No (purchase on demand) | Medium-High for specific topics | Irregular |
| Definitive Healthcare | Yes (market data) | Medium — deal size, not pricing | Continuous |
| Advisory Board | Check with Strategy team | Medium | Annual |

**Analyst data protocol:**

1. CI analyst reviews relevant KLAS and Gartner reports within 2 weeks of publication
2. Pricing-relevant sections extracted and entered as analyst source records
3. All analyst data enters with `confidence = MEDIUM` — analyst benchmarks are research-based but not deal-specific
4. Analyst data has a 365-day freshness window (longer than field data, because reports represent market averages that change more slowly)

---

## 5. Confidence Scoring Rules

Every pricing observation in the workbook carries a confidence level. This is not a subjective judgment — it is a rules-based classification that determines how the data can be used in sales conversations and strategic decisions.

### 5.1 Confidence Levels Defined

#### HIGH (Green) — Use with confidence in deal conversations

```
Requirements (ALL must be true):
✓ Direct observation from ≥2 independent sources
✓ Sources collected within 180 days of each other
✓ At least one source is field (direct deal observation) or interview
✓ Sources agree within 20% on the price point or discount range
✓ Deal context is sufficiently similar to the use case being referenced
```

**How to use HIGH-confidence data:** Provide to sales reps as deal guidance. Suitable for battlecard inclusion, competitive positioning, and negotiation strategy. Always present as a range, not a point estimate, to account for deal-specific variation.

#### MEDIUM (Yellow) — Use with stated caveats

```
Requirements (ONE of the following):
Option A: Single verified field source within 180 days
Option B: Two corroborated indirect sources (e.g., web + analyst) within 365 days
Option C: HIGH-confidence data that has aged 180-365 days (degraded from HIGH)
Option D: Interview data with strong buyer recall (buyer had documentation, not just memory)
```

**How to use MEDIUM-confidence data:** Appropriate for directional guidance in deals. Must be labeled "based on a limited data set — verify if possible." Not suitable for exact pricing claims in competitive positioning documents.

#### LOW (Red) — Internal reference only, not for sales use

```
Conditions (any apply):
- Single unverified source (field report without documentation)
- Web or public source without corroboration
- Data older than 365 days
- Estimated/modeled price (analyst estimate, back-of-envelope calculation)
- Source conflicts with other data (discrepancy >30% unexplained)
- Secondhand ("a customer told a rep that another vendor said...")
```

**How to use LOW-confidence data:** Internal signal only. Use to identify gaps that need active collection (inputs to PGPS algorithm). Never share with sales reps as deal guidance. May be shared with leadership as "preliminary intelligence — unconfirmed."

#### GAP (Gray) — Known blind spot

```
Conditions:
- No data collected for this vendor/product combination
- Known data exists but has not been gathered
- Previously ACTIVE data has expired with no replacement
```

**How to use GAP data:** Inputs to PGPS algorithm to prioritize collection. GAP records are placeholders that force acknowledgment of what we don't know. A blank spreadsheet cell looks like no competitor — a GAP record says "we haven't collected this yet."

### 5.2 Confidence Degradation Rules

Data confidence degrades automatically over time based on the following schedule:

| Current Confidence | Age Threshold | Degraded Confidence |
|-------------------|---------------|-------------------|
| HIGH | >180 days | MEDIUM |
| MEDIUM | >365 days | LOW |
| LOW | >545 days (18 months) | EXPIRED → archive |
| GAP | No expiry | Remains GAP until data collected |

`build_pricing_excel.py` calculates current confidence at workbook generation time based on `date_collected` and applies these rules automatically. A record entered as HIGH in January will display as MEDIUM in August if not re-confirmed.

### 5.3 Source Weight in Confidence Calculation

When multiple sources exist for the same observation, the confidence calculation uses weighted source credibility:

| Source Type | Credibility Weight | Notes |
|-------------|-------------------|-------|
| Field (direct deal documentation) | 1.0 | Highest — direct market evidence |
| Customer interview | 0.9 | Near-field quality when buyer had documentation |
| Customer interview (recall only) | 0.6 | Memory-based, subject to distortion |
| Analyst report (KLAS/Gartner) | 0.7 | Rigorous but not deal-specific |
| Vendor earnings call | 0.5 | Strategic framing, not operational detail |
| Web/public source | 0.3 | Sparse; enterprise vendors rarely publish pricing |
| Secondhand field report | 0.2 | "I heard that someone said..." — low signal |

**Multi-source composite confidence:**

When multiple sources point to the same observation, composite credibility is:

```
composite = 1 - ∏(1 - wᵢ) for each source i

Example: Field source (1.0) + Analyst report (0.7)
composite = 1 - ((1 - 1.0) × (1 - 0.7))
composite = 1 - (0 × 0.3)
composite = 1.0 → HIGH

Example: Web source (0.3) + Secondhand field (0.2)
composite = 1 - ((1 - 0.3) × (1 - 0.2))
composite = 1 - (0.7 × 0.8)
composite = 1 - 0.56
composite = 0.44 → MEDIUM (threshold ≥0.40)
```

Confidence thresholds:
- composite ≥ 0.80 → HIGH
- composite ≥ 0.40 → MEDIUM
- composite < 0.40 → LOW

---

## 6. Validation Protocol

Data validation is the process of moving an observation up the confidence ladder: GAP → LOW → MEDIUM → HIGH. Validation requires human judgment — it is not fully automated.

### 6.1 Validation Workflow

```
Step 1: INGESTION
  - CI analyst receives pricing data (field Salesforce submission, web sweep, interview)
  - Enters raw data into ORACLE_HEALTH_PRICING_MASTER_DATA.csv
  - Sets confidence = LOW (default for all new entries)
  - Sets validated_by = PENDING

Step 2: INITIAL REVIEW (within 5 business days)
  - CI analyst reviews for:
    - Completeness: all required fields populated?
    - Plausibility: is this in the expected range for this vendor/product?
    - Context: is the deal context specific enough to be useful?
  - If plausible and complete: advance to MEDIUM if source weight ≥0.6
  - If incomplete or implausible: flag for source follow-up

Step 3: CORROBORATION SEARCH (ongoing)
  - For each LOW/MEDIUM record, actively seek a second source
  - Use PGPS score to prioritize which records to pursue first
  - Corroboration sources: field outreach, Win/Loss interview queue, analyst database query

Step 4: UPGRADE DECISION (CI Lead approval required for HIGH)
  - To upgrade to HIGH: CI analyst prepares validation memo
    - Source 1: type, date, deal context
    - Source 2: type, date, deal context
    - Agreement analysis: do they agree within 20%?
    - Context match: are the deal contexts comparable?
  - CI Lead (Mike Rodgers) reviews and approves HIGH designation
  - validated_by = [name] + date

Step 5: PERIODIC REVIEW
  - All HIGH records reviewed for freshness at each quarterly cycle
  - Any HIGH records >120 days old: CI analyst attempts re-confirmation before they age to MEDIUM
  - All MEDIUM records >270 days old: flagged for active collection campaign
```

### 6.2 Validation Memo Template

For each record being upgraded to HIGH confidence, the following memo is filed in `.startup-os/artifacts/pricing/`:

```
PRICING VALIDATION MEMO

Record ID: [record_id]
Vendor: [vendor]
Product: [product_module]
Date of Review: [date]
Analyst: [name]

SOURCE 1
  Type: [field / interview / analyst / web]
  Date Collected: [date]
  Deal Context: [org size, type, region if applicable]
  Price Point: [range or specific figure]
  Documentation: [what exists — proposal, screenshot, interview notes]

SOURCE 2
  Type: [field / interview / analyst / web]
  Date Collected: [date]
  Deal Context: [org size, type, region if applicable]
  Price Point: [range or specific figure]
  Documentation: [what exists]

AGREEMENT ANALYSIS
  Source 1 price/range: [$X to $Y]
  Source 2 price/range: [$A to $B]
  Overlap: [do the ranges overlap? what is the consensus range?]
  Discrepancy: [% difference at midpoints — must be ≤20% for HIGH]

CONTEXT COMPARABILITY
  Are deal contexts sufficiently similar? [Yes / No / Conditional]
  If conditional: [describe the limitation]

RECOMMENDATION
  Upgrade to HIGH: [Yes / No]
  Effective date range: [date_collected to date_expires]
  Notes: [any caveats for users of this data]

APPROVAL
  CI Lead: [name / date]
```

### 6.3 Handling Conflicting Data

When two sources disagree by more than 20%, do not average them — investigate the discrepancy.

**Common reasons for pricing disagreement and resolution:**

| Reason | Example | Resolution |
|--------|---------|-----------|
| Different deal sizes | $1.5M for 300 beds vs. $2.8M for 600 beds | Normalize to per-bed rate; record both with context |
| Different years | 2023 pricing vs. 2025 pricing | Use most recent; note the historical trend if informative |
| Competitive vs. standard deal | 22% discount (competitive) vs. 12% (non-competitive) | Record separately by deal type |
| Different modules included | RCM-only vs. RCM + Scheduling bundle | Decompose to module level where possible |
| Negotiation anchor vs. final price | Initial ask vs. signed contract | Always prefer signed contract price |
| Geographic variation | Pricing variation by market / system size | Note regional context in deal_context field |

If the discrepancy cannot be resolved, retain both records at MEDIUM confidence with a note indicating the conflict. Do not suppress conflicting data — conflict is information.

---

## 7. The Excel Workbook Standard

### 7.1 Workbook Generation

The master pricing workbook is generated by `build_pricing_excel.py` from `ORACLE_HEALTH_PRICING_MASTER_DATA.csv`. The script:

1. Reads all records from the CSV
2. Applies current-date confidence degradation (ages HIGH → MEDIUM → LOW per Section 5.2 rules)
3. Generates color-coded rows by confidence level
4. Creates summary tabs by vendor and by product category
5. Generates the Pricing Gap Priority Score (PGPS) ranking tab
6. Exports to `Oracle_Health_Pricing_Intelligence_[YYYYMMDD].xlsx`

### 7.2 Workbook Structure

**Tab 1: Master Pricing Data**
All active pricing observations, sorted by Vendor then Product. Color-coded by confidence. Includes all 24 columns from the data schema.

**Tab 2: Vendor Summary**
One row per vendor, showing: # of products tracked, highest confidence level, date of most recent data point, PGPS priority score, and a snapshot of key pricing metrics.

**Tab 3: Product Category View**
Pivot of master data by product category (EHR, RCM, Scheduling, Analytics, Patient Portal, etc.) enabling cross-vendor pricing comparison within category.

**Tab 4: Pricing Gaps (PGPS Ranked)**
All GAP and LOW-confidence records, ranked by PGPS score, with recommended collection approach and target timeline. This is the CI collection work queue.

**Tab 5: Discount Band Analysis**
Output from Monte Carlo discount band modeling (Section 11) for vendors with sufficient field data. Shows P10, P25, P50, P75, P90 discount bands per vendor/product.

**Tab 6: Historical Trend**
Pricing observations over time for key vendor/product pairs, enabling trend analysis. Requires date_collected field — shows whether observed prices are rising, stable, or declining.

**Tab 7: Data Freshness Dashboard**
Traffic-light dashboard showing the age and confidence of every tracked vendor/product combination. Gives CI team an at-a-glance view of where the workbook is current vs. stale.

### 7.3 Color Coding Standard

| Confidence | Cell Background | Font Color | Hex Code (Background) |
|-----------|----------------|------------|----------------------|
| HIGH | Green | White | `#1E7E34` |
| MEDIUM | Yellow | Dark gray (#2D2D2D) | `#FFC107` |
| LOW | Red | White | `#C82333` |
| GAP | Gray | White | `#6C757D` |
| EXPIRED | Light gray strikethrough | Gray | `#E9ECEF` |

### 7.4 Required Formatting Rules

All generated workbooks must conform to:

- **Font**: Calibri 10pt (body), Calibri 12pt Bold (headers)
- **Column widths**: Auto-fit to content, minimum 80px
- **Frozen panes**: Row 1 (headers) and Column 1 (record_id) always frozen
- **Filters**: Auto-filters enabled on all columns
- **Confidence filter**: Default filter set to show only HIGH and MEDIUM records (LOW/GAP accessible via filter toggle)
- **Date format**: YYYY-MM-DD throughout (no ambiguous MM/DD/YYYY)
- **Currency format**: $#,##0 for whole dollar amounts; $#,##0.00 for per-unit pricing
- **Percentage format**: 0.0% for discount ranges
- **Print setup**: Landscape, fit to 1 page wide, headers on every page

### 7.5 Workbook Access Control

The full workbook (all confidence levels, including LOW) is restricted to:
- CI team (read/write)
- Sales Leadership VP+ (read)
- Product Marketing Directors (read)
- Legal Compliance (read, for review)

The filtered workbook (HIGH + MEDIUM only) is distributed to:
- Regional Sales Directors
- Account Executives via SharePoint link (read-only, no download)
- Sales Engineering leads

The executive summary tab (Vendor Summary) is distributed to:
- Sales VP, CMO, SVP Product
- Oracle Health leadership as part of quarterly CI briefing

---

## 8. Update Cadence

### 8.1 Quarterly Baseline Refresh

**Timing:** First two weeks of each quarter (Q1: early January, Q2: early April, Q3: early July, Q4: early October)

**Process:**

```
Week 1 of Quarter:
Day 1-2: Run freshness audit — identify all records aging out in next 90 days
Day 2-3: Pull KLAS and Gartner reports published in prior quarter
Day 3-4: Run web sweep (Firecrawl + Brightdata MCP) for competitor pricing mentions
Day 4-5: Review Salesforce competitive deal records for new pricing data from last quarter

Week 2 of Quarter:
Day 1-2: Conduct 2-3 targeted win/loss interviews with pricing module (per SOP-09)
Day 3: Update ORACLE_HEALTH_PRICING_MASTER_DATA.csv with all new data
Day 4: Run build_pricing_excel.py to generate refreshed workbook
Day 5: CI Lead review and approval; distribute per Distribution Protocol (Section 9)
```

**Output:** Refreshed Excel workbook + Quarterly Pricing Intelligence Brief (1-page summary of key changes)

### 8.2 Event-Driven Triggers

The following events trigger an out-of-cycle workbook update within 5 business days:

| Trigger | Rationale | Action Required |
|---------|-----------|----------------|
| Major competitor pricing announcement | Public pricing change affects all current deals | Full web sweep + workbook update + distribution |
| Acquisition of competitor | Bundle/packaging may change significantly | Research new combined offering + update affected records |
| Oracle Health product launch or re-pricing | Changes competitive context | Update Oracle Health baseline row + reframe competitor comparisons |
| Field report of >30% price movement | Significant deal-level pricing shift | Validate + update relevant records within 48 hours |
| Three or more field reports citing same competitor in one month | Unusual competitor activity | Priority investigation + interim pricing brief |
| Major industry conference (HIMSS, ViVE) | Vendors often announce pricing at events | Post-conference sweep within 1 week |
| Analyst report update (KLAS/Gartner) | New benchmark data available | Extract pricing data + update workbook |

### 8.3 Freshness Monitoring

`build_pricing_excel.py` generates a freshness report at every run showing:

- Records expiring in next 30 days (urgent collection needed)
- Records expiring in next 60 days (plan collection)
- Records expired in last 30 days (recently lost confidence — note for sales)
- GAP records by priority (PGPS ranked)

The freshness report is emailed to the CI team via the Oracle Health morning brief infrastructure every Monday.

---

## 9. Distribution Protocol

Pricing data requires more careful distribution controls than most CI outputs because it contains information about competitor pricing that, if improperly shared, could create legal exposure (see Section 12). The distribution protocol defines what each audience receives, in what format, and through what channel.

### 9.1 Audience Tiers

**Tier 1: CI Operations (full access)**

| Recipient | Format | Channel | Frequency |
|-----------|--------|---------|-----------|
| Mike Rodgers (CI Lead) | Full workbook + raw CSV | SharePoint (full access) | Continuous |
| CI Analyst(s) | Full workbook + raw CSV | SharePoint (full access) | Continuous |
| Legal/Compliance | Full workbook (read) | SharePoint (legal folder) | Quarterly |

**Tier 2: Sales Leadership (filtered access)**

| Recipient | Format | Channel | Frequency |
|-----------|--------|---------|-----------|
| VP Sales | Executive summary tab + HIGH/MEDIUM filtered workbook | SharePoint link | Quarterly + event-triggered |
| Regional Sales Directors | HIGH/MEDIUM filtered workbook | SharePoint link | Quarterly |
| Sales Ops | Vendor Summary tab only | SharePoint link | Quarterly |

**Tier 3: Field Sales (curated access)**

| Recipient | Format | Channel | Frequency |
|-----------|--------|---------|-----------|
| Account Executives | Competitor-specific Quick Reference card (1-2 pages) | Salesforce + SharePoint | Quarterly |
| Sales Engineers | Technical pricing comparison (relevant modules) | SharePoint + Slack | Quarterly |
| Account Managers | Renewal pricing context (competitor renewal pricing) | SharePoint | Quarterly |

**Tier 4: Adjacent stakeholders (summarized access)**

| Recipient | Format | Channel | Frequency |
|-----------|--------|---------|-----------|
| Product Marketing | Packaging intelligence summary | Email brief | Quarterly |
| Product Management | Pricing model analysis (not field data) | SharePoint | Quarterly |
| Corporate Strategy | Executive summary + trend analysis | Executive briefing deck | Quarterly |

### 9.2 Distribution Formats by Audience

**Format A: Full Excel Workbook**
- Who: CI team, Sales Leadership (filtered version)
- What: Complete workbook per Section 7.2
- Controls: SharePoint access-controlled link, no download for Tier 2+

**Format B: Competitor Quick Reference Card**
- Who: Field AEs and SEs
- What: 1-2 page PDF per major competitor
- Content: Pricing model overview, typical deal range (HIGH/MEDIUM only), discount guidance, packaging summary, key comparison vs. Oracle Health
- Controls: Internal use only watermark; distributed via Salesforce Competitive Intelligence tab

**Format C: Pricing Intelligence Brief (Quarterly)**
- Who: VP Sales, CMO, product leadership
- What: 1-page summary of key pricing changes, new data collected, gaps identified, deal impact
- Format: PDF via email (or Oracle Health Competitive Intelligence SharePoint hub)

**Format D: Deal-Specific Pricing Memo**
- Who: Account team (AE + SE + Manager) for a specific active deal
- What: Tailored analysis of the specific competitor(s) in that deal
- Content: Relevant pricing data at correct deal size, discount history at that org size, negotiation guidance based on Monte Carlo bands
- Controls: Sent to named individuals only; expires when deal closes

### 9.3 Sharing Outside Oracle Health

**PROHIBITED.** No pricing intelligence data — in any format — may be shared outside Oracle Health employees without prior Legal review and explicit written approval from the CI Lead.

This includes:
- Partner organizations
- Consultants (even on NDA)
- Oracle parent company teams (check with Legal)
- Customers (even in a "how do you compare?" conversation)

See Section 12 (Legal & Compliance Controls) for full detail.

---

## 10. Predictive Algorithm: Pricing Gap Priority Score (PGPS)

### 10.1 Purpose

The PGPS algorithm answers the question: **"Of all the pricing data gaps we have, which one should we fill next quarter?"**

CI time is finite. Not every blank cell in the pricing workbook is equally important. A gap in Epic RCM pricing — a competitor that appears in 40% of Oracle Health's large-system deals — is vastly more important than a gap in Greenway Health's EHR pricing for small ambulatory practices.

PGPS assigns a quantitative priority score to every GAP and LOW-confidence record, enabling the CI team to focus collection activity on the most deal-impactful gaps first.

### 10.2 Algorithm Definition

```
PGPS = Pricing Gap Priority Score

Inputs (all scored 1-10):

  deal_frequency (DF):
    How often does this competitor appear in active Oracle Health pipeline?
    Sourced from: Salesforce — count of active opportunities where this
    competitor is listed in the "Primary Competitor" field, last 90 days
    Score mapping:
      1-2 deals in 90 days   → 1-2
      3-5 deals               → 3-4
      6-10 deals              → 5-6
      11-20 deals             → 7-8
      21+ deals               → 9-10

  deal_value (DV):
    Average Total Contract Value (TCV) of deals where this competitor appears
    Sourced from: Salesforce TCV field on opportunities with this competitor
    Score mapping:
      <$500K avg TCV          → 1-2
      $500K-$1M               → 3-4
      $1M-$2.5M               → 5-6
      $2.5M-$5M               → 7-8
      >$5M                    → 9-10

  confidence_gap (CG):
    Current confidence level of this vendor/product combination
    Fixed mapping:
      GAP = 10 (no data at all)
      LOW = 7 (some data, insufficient)
      MEDIUM = 4 (usable but single-source)
      HIGH = 1 (well-documented — low urgency)

  competitive_sensitivity (CS):
    How much does pricing knowledge shift deal outcomes for this competitor?
    Sourced from: Win/Loss analysis (SOP-09) — do deals lost to this
    competitor cite price as a significant factor?
    Qualitative assessment by CI Lead:
      Price rarely cited in wins/losses → 1-3
      Price occasionally cited          → 4-6
      Price frequently cited            → 7-8
      Price is the primary battleground → 9-10

  collection_ease (CE):
    How available is this pricing data in the market?
    Qualitative assessment:
      Publicly available (priced SaaS) → 9-10 (easy to get)
      Analyst-covered, some field data  → 6-8
      Limited public data, field heavy  → 3-5
      Highly opaque, rarely discussed   → 1-2

Formula:

  PGPS = (DF × 0.25) + (DV × 0.25) + (CG × 0.20) + (CS × 0.20) + (CE × 0.10)

Output range: 1.0 (lowest priority) to 10.0 (highest priority)

Priority bands:
  PGPS 8.0-10.0: CRITICAL — active collection target this quarter
  PGPS 6.0-7.9:  HIGH — target within 2 quarters
  PGPS 4.0-5.9:  MEDIUM — target within 4 quarters
  PGPS 1.0-3.9:  LOW — monitor, collect opportunistically
```

### 10.3 Worked Example

**Scenario:** Three pricing gaps exist. Which should the CI team prioritize?

**Gap A: Epic Ambulatory EHR (currently LOW confidence)**

```
deal_frequency: Epic appears in 18 active deals (90 days) → score 8
deal_value: Average TCV $3.2M → score 8
confidence_gap: LOW → score 7
competitive_sensitivity: Price is frequently cited in Epic losses → score 8
collection_ease: Epic is a major KLAS-covered vendor; some field data available → score 6

PGPS_A = (8 × 0.25) + (8 × 0.25) + (7 × 0.20) + (8 × 0.20) + (6 × 0.10)
       = 2.0 + 2.0 + 1.4 + 1.6 + 0.6
       = 7.6 → HIGH priority
```

**Gap B: Netsmart myUnity (currently GAP — no data)**

```
deal_frequency: Netsmart appears in 3 active deals (90 days) → score 3
deal_value: Average TCV $800K → score 3
confidence_gap: GAP → score 10
competitive_sensitivity: Price rarely cited in Netsmart losses → score 2
collection_ease: Very limited public data, opaque private company → score 2

PGPS_B = (3 × 0.25) + (3 × 0.25) + (10 × 0.20) + (2 × 0.20) + (2 × 0.10)
       = 0.75 + 0.75 + 2.0 + 0.4 + 0.2
       = 4.1 → MEDIUM priority
```

**Gap C: athenahealth athenaOne (currently GAP — no data)**

```
deal_frequency: athena appears in 9 active deals (90 days) → score 5
deal_value: Average TCV $1.4M → score 5
confidence_gap: GAP → score 10
competitive_sensitivity: Price is a primary battleground in athena deals → score 9
collection_ease: athena is publicly traded, KLAS-covered, active press → score 7

PGPS_C = (5 × 0.25) + (5 × 0.25) + (10 × 0.20) + (9 × 0.20) + (7 × 0.10)
       = 1.25 + 1.25 + 2.0 + 1.8 + 0.7
       = 7.0 → HIGH priority
```

**Result:** Collection priorities for next quarter:
1. Epic Ambulatory EHR (PGPS 7.6) — HIGH
2. athenahealth athenaOne (PGPS 7.0) — HIGH
3. Netsmart myUnity (PGPS 4.1) — MEDIUM (defer to next cycle)

### 10.4 PGPS Implementation in build_pricing_excel.py

The PGPS calculation is run automatically at workbook generation time. For each GAP or LOW-confidence record:

1. `deal_frequency` and `deal_value` are queried from Salesforce via API
2. `confidence_gap` is derived from the current confidence field
3. `competitive_sensitivity` and `collection_ease` are read from a supplementary `pgps_inputs.csv` maintained by the CI analyst (updated quarterly)
4. PGPS score is calculated and written to the Pricing Gaps tab, sorted descending

The top 5 PGPS records are highlighted in the workbook as "Active Collection Targets" and included in the Quarterly Pricing Intelligence Brief.

### 10.5 PGPS Maintenance

- `pgps_inputs.csv` is reviewed and updated each quarter during the baseline refresh
- `competitive_sensitivity` scores are recalibrated when Win/Loss analysis (SOP-09) produces new data on price factors in deal outcomes
- `collection_ease` scores are adjusted when market conditions change (e.g., a private competitor goes public, increasing data availability)

---

## 11. Monte Carlo: Discount Band Modeling

### 11.1 Purpose

The Monte Carlo discount band model answers: **"What discount range should our sales rep expect from this competitor in this deal?"**

When the CI team has collected 3, 4, or 5 discount observations for a competitor but needs to give sales guidance on the full likely range, simple averaging is misleading. Bootstrapped Monte Carlo simulation provides a statistically rigorous estimate of the discount distribution — including the extremes (floor and ceiling) — from sparse data.

### 11.2 Model Specification

```
MONTE CARLO DISCOUNT BAND MODEL

Inputs:
  observed_discounts: list of N observed discount percentages
    Minimum N for model to run: 3
    Ideal N for reliable estimates: 10+
    Source: field data only (interview and analyst data may be included
            with 0.5 weight applied to each observation)

  deal_size_basis: list price range this model applies to
    Example: "$500K - $5M list price"
    Note: discount behavior may be non-linear across deal sizes; if data
    spans a wide size range, segment into <$1M, $1M-$3M, >$3M before modeling

  relationship_factor: qualitative adjustment factors
    new_customer_competitive: +2 to +5 percentage points above baseline
    existing_customer_renewal: -3 to -8 percentage points below baseline
    note: these adjustments are applied after bootstrap; they shift the
    distribution, not the inputs

Bootstrap Procedure:
  1. Set seed for reproducibility (seed = record_id hash)
  2. N_bootstrap = 10,000
  3. For each bootstrap iteration:
     a. Sample with replacement from observed_discounts
     b. Calculate sample mean
  4. Collect all 10,000 bootstrap means into a distribution
  5. Calculate percentiles: P10, P25, P50, P75, P90

Output Metrics:
  P10 (Floor):    10th percentile — extreme low discount; rare
  P25 (Low Band): 25th percentile — lower end of normal range
  P50 (Median):   Median discount — most likely midpoint
  P75 (High Band):75th percentile — upper end of normal range
  P90 (Ceiling):  90th percentile — extreme high discount; rare

Primary guidance metric: P25-P75 range = "the normal discount band"
Extreme caution range: P10 (floor) and P90 (ceiling) = "outlier territory"

Human-readable output:
  "[Vendor] [Product] discounts typically fall in the [P25]%-[P75]% range
   (50% probability). It is rare to see discounts below [P10]% or above [P90]%.
   The median discount in our data set is [P50]%."
```

### 11.3 Worked Example: Epic RCM Discount Band

**Scenario:** CI team has 3 field-confirmed Epic RCM discount observations from deals in the last 18 months: 18%, 22%, 32%.

```
Step 1: Input data
  observed_discounts = [0.18, 0.22, 0.32]
  N = 3
  deal_size_basis = "$1.5M - $4.5M list price (400-700 bed health systems)"

Step 2: Bootstrap simulation
  N_bootstrap = 10,000 iterations
  Each iteration: sample 3 values with replacement from [0.18, 0.22, 0.32]
  Calculate mean of each sample

Step 3: Bootstrap mean distribution
  Possible sample means from [0.18, 0.22, 0.32]:
  All three same:        mean(0.18,0.18,0.18) = 0.18
                         mean(0.22,0.22,0.22) = 0.22
                         mean(0.32,0.32,0.32) = 0.32
  Two of one, one other: mean(0.18,0.18,0.22) = 0.193
                         mean(0.18,0.18,0.32) = 0.227
                         mean(0.22,0.22,0.18) = 0.207
                         mean(0.22,0.22,0.32) = 0.253
                         mean(0.32,0.32,0.18) = 0.273
                         mean(0.32,0.32,0.22) = 0.287
  One of each:           mean(0.18,0.22,0.32) = 0.240

Step 4: Approximate percentile outputs from 10,000 bootstrap samples
  P10 ≈ 18.0% (floor)
  P25 ≈ 19.5%
  P50 ≈ 23.5% (median)
  P75 ≈ 28.3%
  P90 ≈ 32.0% (ceiling)

Step 5: Apply relationship factor for new competitive deal
  new_customer_competitive adjustment: +2 to +5 pp
  Adjusted P25-P75 range: ~21% to ~33%

Human-readable guidance:
  "Epic RCM discounts in competitive new-logo deals for 400-700 bed systems
   typically fall in the 20-30% range (50% probability). It is rare to see
   discounts below 18% or above 38%. The median in our data set is approximately
   24%. Note: this estimate is based on 3 data points — treat as directional
   until more observations are collected."
```

### 11.4 Model Limitations and Honest Communication

The Monte Carlo discount model is powerful but requires honest communication of its limitations:

| Limitation | Communication to Users |
|-----------|----------------------|
| Small N (N<5) | "Based on [N] observations — directional only. Widen planning range by ±5pp." |
| Wide variance in inputs | "High variance in source data suggests deal-specific factors matter more than market norms." |
| Aging data | "Inputs are [X] months old. Market conditions may have shifted." |
| Deal size mismatch | "This model is calibrated for [deal size range]. Your deal at [size] may fall outside the model's reliable range." |

All Monte Carlo output cells in the workbook include a footnote: "Statistical estimate based on N=[X] observations. Not a guarantee. Verify with CI team before using in deal negotiation."

### 11.5 Model Output in the Workbook

Tab 5 (Discount Band Analysis) displays:

```
| Vendor | Product | N (observations) | P10 | P25 | P50 | P75 | P90 | Model Date | Status |
```

Records with N<3 show "Insufficient data" rather than a model output.
Records where all inputs are >365 days old show "DATA AGING — re-confirm before use."

### 11.6 When to Run the Model

- Quarterly: Automatically run as part of workbook generation for all records with N≥3
- On-demand: CI analyst can run for a specific deal request (Deal-Specific Pricing Memo format)
- Never: Do not run the model in front of a customer or in a customer-facing document — it is an internal planning tool only

---

## 12. Legal & Compliance Controls

Pricing intelligence, if mishandled, can create legal exposure under antitrust law, trade secret doctrine, and contractual confidentiality obligations. This section is non-negotiable — all CI team members must complete Oracle Health Legal's CI compliance training before accessing the full pricing workbook.

### 12.1 What Oracle Health Can Legitimately Collect

**Permitted:**

- Pricing from publicly available sources (pricing pages, press releases, public filings)
- Pricing shared voluntarily by customers during win/loss interviews (with consent)
- Pricing observed in competitive sales situations where the customer shared the competing proposal
- Analyst research and industry benchmarks
- Pricing discussed in earnings calls and investor presentations

**Permitted with documentation:**

- Pricing shared by field reps who observed it in deal situations — requires documentation of the source situation to demonstrate the data was legitimately obtained
- Pricing from former employees of competitors — permitted if the individual is sharing general market knowledge, not proprietary documents. Consult Legal before using.

**Prohibited:**

- Acquiring competitor pricing through deception (false identity, pretexting)
- Obtaining competitor pricing documents through improperly obtained means (stolen documents, data breaches, unauthorized access)
- Coordinating pricing knowledge with competitors in any way (antitrust risk)
- Accepting confidential competitor information from their employees in violation of their NDA
- Asking Oracle Health employees to obtain competitor pricing through improper means

### 12.2 Antitrust Bright Lines

**The Sherman Act and Clayton Act create specific risks around competitive pricing information:**

| Prohibited Activity | Example | Risk |
|-------------------|---------|------|
| Price signaling | Sharing Oracle Health pricing plans with competitor reps | Criminal antitrust violation |
| Coordinated pricing | Agreeing (even implicitly) to price at or above a competitor | Criminal antitrust violation |
| Information exchange facilitation | Oracle Health acting as a conduit for competitor pricing between two competitors | Civil and potentially criminal antitrust |
| Customer steering based on competitive pricing | Using pricing intelligence to facilitate anti-competitive market allocation | Civil antitrust |

**Bright line test:** If the purpose of collecting or sharing pricing data could be construed as coordinating Oracle Health's pricing behavior with a competitor, stop and call Legal.

### 12.3 Customer Confidentiality Rules

When a customer shares competitor pricing with Oracle Health:

1. **Ask for consent**: "Is it okay if we use this information internally for our competitive intelligence program? We'll never identify you or share it with the competitor."
2. **Document consent** in the Salesforce record
3. **Never identify the customer** in any internal document — use region + org type only
4. **Honor "do not use" requests**: If a customer shares data and then asks you not to use it, remove it from the workbook

### 12.4 Document Handling for Competitor Pricing Documents

If a customer shares an actual competitor pricing proposal (PDF, Excel, screenshot):

1. Do not distribute the document beyond the CI team
2. Extract the relevant data points (numbers only)
3. Delete the original document after extraction
4. Note in the data record: "Source: competitor proposal shared by customer — original document not retained"

The goal is to use the information, not retain the competitor's proprietary documents.

### 12.5 Legal Review Process

Before publishing any pricing intelligence externally (industry presentations, analyst briefings) or using pricing data in formal customer-facing communications (not deal conversations):

1. Submit for Legal review minimum 5 business days before use
2. Legal review checklist:
   - Source documentation available for all HIGH/MEDIUM claims
   - No claims that could constitute price disparagement
   - No claims derived from improperly obtained information
   - Appropriate hedging language included ("based on market intelligence" vs. "Epic charges exactly $X")

### 12.6 Hedging Language Standard

All external communications (not internal sales guidance) that include competitive pricing references must use approved hedging language:

**Approved phrases:**
- "Based on our market intelligence..."
- "Industry estimates suggest..."
- "Our analysis of publicly available information indicates..."
- "Field data suggests typical ranges of..."

**Prohibited phrases in external communications:**
- "Epic charges $X" (implies certainty)
- "We know from a customer that Cerner priced at..." (identifies source)
- "Our confidential sources indicate..." (implies obtained through unusual means)
- "According to information we received from [named source]..." (identifies and may breach confidentiality)

---

## 13. Field Feedback Loop

The quality of the pricing workbook depends entirely on the quality of the data flowing into it. Field sales teams are the primary collectors of the highest-quality data — direct deal observations — but they need a frictionless mechanism to contribute. This section defines the Field Feedback Loop: how reps capture, submit, and get credit for pricing intelligence.

### 13.1 CRM Integration (Salesforce)

**The pricing intelligence capture mechanism lives in Salesforce — where reps already work.**

A custom section called "Competitive Intelligence" exists on every Oracle Health Opportunity record. Within it, a subsection called "Pricing Intelligence" contains:

```
Field: Competitor Encountered
  Type: Lookup → Competitor list (standardized)
  Required: No (encourage but not mandatory)

Field: Competitor Product/Module
  Type: Text
  Required: If competitor entered

Field: Competitor Pricing (Observed)
  Type: Currency range (two fields: Low / High)
  Required: No
  Tooltip: "What range did the customer indicate the competitor was proposing?
            Enter your best estimate — even approximate is valuable."

Field: Pricing Source Type
  Type: Picklist: Customer shared proposal / Customer verbal / Heard indirectly /
                  Other (specify)
  Required: If pricing entered

Field: Deal Context for This Pricing
  Type: Text (200 char)
  Tooltip: "Org size, type, and competitive situation context"

Field: Analyst Comments
  Type: Text (500 char)
  Tooltip: "Anything else CI should know about this competitor's pricing approach?"

Field: Consent to Use for CI
  Type: Checkbox (default: Yes)
  Tooltip: "Did the customer consent to us using this information internally?"
```

**Automated workflow:**

When a rep saves a record with new pricing data, Salesforce triggers:
1. Notification to CI team Slack channel (#competitive-intel)
2. Creation of a CI review task assigned to the CI analyst
3. Logging of the submission for rep recognition (see Section 13.3)

### 13.2 Training Sales Reps on Pricing Intelligence Capture

CI data quality fails when reps don't understand what they're capturing or why. Quarterly rep training (15 minutes, delivered via Salesforce in-app training module) covers:

**What to capture:**
- Any time a customer shows you or mentions a competitor's pricing — write it down
- Capture the range, not just "they were cheaper"
- Note the context: what size system, what modules, competitive vs. sole-source situation

**What not to worry about:**
- It doesn't have to be exact — ranges are fine
- You're not obligated to ask the customer directly — capture what's shared voluntarily
- CI team will validate the data — just get it in the system

**Why it matters to the rep:**
- Better pricing intelligence = better proposals = higher win rates = larger commissions
- Reps who contribute the most actionable intelligence are recognized quarterly

**Legal note:**
- Never ask customers to share competitor documents — only what they share voluntarily
- Never share Oracle Health pricing strategy in exchange for competitor data

### 13.3 Field Rep Recognition Program

To incentivize data contribution:

| Achievement | Recognition |
|-------------|------------|
| 1st pricing submission | Welcome to the CI network (personal email from Mike Rodgers) |
| 5 submissions in a quarter | Named in quarterly CI report as a top contributor |
| Submission that upgrades a record to HIGH | "Gold Source" recognition; mentioned in Sales Leadership CI briefing |
| 10+ submissions in a quarter | CI Contributor badge in Salesforce + $50 Oracle swag |

Leaderboard published quarterly to Sales Leadership showing top 10 field contributors by submission volume and quality.

### 13.4 Deal Debrief Integration

For every closed deal (win or loss) where a primary competitor was identified in Salesforce, the CI team initiates a 5-minute debrief with the account team within 10 business days of deal close:

**Debrief questions (pricing-specific):**
1. "What was the competitor's pricing structure — per bed, per user, enterprise flat fee?"
2. "Did you see an actual proposal or pricing sheet, or is this what the customer told you?"
3. "Did the competitor offer any creative pricing (outcome-based, multi-year incentives, free pilots)?"
4. "How did pricing compare to Oracle Health — were we close, significantly above, significantly below?"
5. "Did pricing matter in the outcome? Was it the primary reason, or a secondary factor?"

Responses feed directly into Salesforce fields and the CI review queue.

---

## 14. Quality Gates

The pricing intelligence program maintains five quality gates that must be cleared before data proceeds through the pipeline or before output is distributed.

### Gate 1: Ingestion Quality Gate

**Purpose:** Ensure raw data is complete and plausible before entering the workbook.

**Checks:**
- [ ] All required fields populated (vendor, product, pricing model, unit, date, source type)
- [ ] Vendor name matches standardized list
- [ ] Price is within plausible range for this vendor/product category (CI analyst judgment)
- [ ] Deal context is specific enough to be useful (not just "they were cheaper")
- [ ] Source type is documented

**Outcome:** PASS → enter workbook with confidence = LOW. FAIL → return to submitter with clarification request.

### Gate 2: Validation Quality Gate

**Purpose:** Ensure confidence upgrade decisions are justified.

**Checks (for LOW → MEDIUM):**
- [ ] Source credibility weight ≥ 0.6 for single source, OR
- [ ] Composite credibility ≥ 0.40 for multiple sources
- [ ] Data is within 180-day freshness window (365 days for analyst data)
- [ ] No contradictory data at same confidence level unexplained

**Checks (for MEDIUM → HIGH):**
- [ ] Validation memo prepared and filed
- [ ] Two independent sources present (at least one field or interview)
- [ ] Sources agree within 20%
- [ ] Deal contexts are comparable
- [ ] CI Lead (Mike Rodgers) approval obtained

**Outcome:** PASS → confidence upgraded. FAIL → record remains at current level with notes on what additional validation is needed.

### Gate 3: Workbook Generation Quality Gate

**Purpose:** Ensure the Excel workbook output is complete and accurate before distribution.

**Checks:**
- [ ] `build_pricing_excel.py` ran without errors
- [ ] All tabs generated (7 tabs present and populated)
- [ ] Color coding matches confidence levels (spot check 10 random records)
- [ ] PGPS scores calculated for all GAP/LOW records
- [ ] Discount band models run for all eligible records (N≥3)
- [ ] Freshness degradation applied correctly (date-based)
- [ ] No #REF errors, broken formulas, or missing data in summary tabs

**Outcome:** PASS → proceed to distribution. FAIL → fix errors, re-run, re-check.

### Gate 4: Distribution Quality Gate

**Purpose:** Ensure the right version is sent to the right audience.

**Checks:**
- [ ] Tier 1 (full) vs. Tier 2 (filtered) vs. Tier 3 (Quick Reference card) correctly prepared
- [ ] Access controls correctly set on SharePoint links (Tier 2+: read-only, no download)
- [ ] Quick Reference cards contain only HIGH and MEDIUM confidence data
- [ ] Approved hedging language present in all customer-facing excerpts
- [ ] Legal review completed if required (any external distribution)
- [ ] Distribution list is current (no former employees)

**Outcome:** PASS → distribute. FAIL → correct before sending.

### Gate 5: Quarterly Review Quality Gate

**Purpose:** Ensure the program is delivering business value and maintaining data quality.

**Checks (quarterly):**
- [ ] Coverage: What % of P1/P2 competitors have at least MEDIUM-confidence pricing?
  - Target: ≥80% of P1 competitors at MEDIUM+; ≥50% of P2 competitors at MEDIUM+
- [ ] Freshness: What % of HIGH-confidence records are within 180-day window?
  - Target: ≥90%
- [ ] Field contribution: Are field reps actively submitting? (see KPIs, Section 16)
  - Target: ≥5 unique rep contributors per quarter
- [ ] Sales impact: Are reps using pricing data in deals? (Salesforce tracking)
  - Target: Pricing Quick Reference accessed by ≥30% of AEs per quarter
- [ ] Gap prioritization: Were the top 5 PGPS gaps actively pursued?
  - Target: At least 3 of 5 priority gaps improved (confidence upgraded) each quarter

**Outcome:** PASS → publish quarterly program health report. FAIL → document gaps, adjust collection plan.

---

## 15. RACI Matrix

### 15.1 Core RACI

| Activity | CI Lead (Mike) | CI Analyst | Sales Reps | Sales Leadership | Legal | Product Mktg |
|----------|---------------|------------|------------|-----------------|-------|-------------|
| Define collection strategy | **R/A** | C | I | C | I | C |
| Field data submission | I | I | **R** | I | — | — |
| Web sweep & public collection | A | **R** | — | — | — | — |
| Win/loss interview pricing module | **R/A** | C | — | — | — | — |
| Data entry into master CSV | A | **R** | — | — | — | — |
| Confidence upgrade to MEDIUM | A | **R** | — | — | — | — |
| Confidence upgrade to HIGH | **R/A** | C | — | — | — | — |
| Validation memo filing | A | **R** | — | — | — | — |
| Workbook generation (build_pricing_excel.py) | A | **R** | — | — | — | — |
| Workbook quality gate review | **R/A** | C | — | — | — | — |
| Distribution (full workbook) | **R/A** | C | — | I | — | — |
| Distribution (Quick Reference cards) | A | **R** | — | I | — | I |
| PGPS calculation and prioritization | A | **R** | — | C | — | — |
| Monte Carlo model execution | A | **R** | — | — | — | — |
| Deal-specific pricing memo | **R/A** | C | — | C | — | — |
| Legal/compliance review | C | C | — | — | **R/A** | — |
| Rep training on CI capture | **R/A** | C | I | C | I | — |
| Rep recognition program | A | **R** | I | I | — | — |
| Quarterly program review | **R/A** | C | — | C | — | I |
| SOP update | **R/A** | C | — | — | C | I |

**Key:** R = Responsible, A = Accountable, C = Consulted, I = Informed

### 15.2 Escalation Path

| Situation | Escalate To | Timeline |
|-----------|------------|---------|
| Conflicting data that cannot be resolved | CI Lead → VP Sales for field clarification | Within 10 business days |
| Field rep submitting implausible data | CI Lead → Sales Manager | Within 5 business days |
| Legal question on a data source | CI Lead → Legal | Before using the data |
| Major competitor pricing announcement requiring rapid update | CI Lead → CMO + VP Sales | Within 24 hours |
| Data breach or unauthorized access to pricing workbook | CI Lead → Legal + Security | Immediately |

---

## 16. KPIs

The following KPIs are reviewed quarterly by the CI Lead and reported to Sales Leadership.

### 16.1 Data Quality KPIs

| KPI | Description | Target | Measurement |
|-----|-------------|--------|-------------|
| **P1 Competitor Coverage** | % of P1 competitors with ≥MEDIUM confidence on primary products | ≥80% | Workbook audit |
| **P2 Competitor Coverage** | % of P2 competitors with ≥MEDIUM confidence on primary products | ≥50% | Workbook audit |
| **Data Freshness Rate** | % of HIGH-confidence records within 180-day window | ≥90% | build_pricing_excel.py freshness report |
| **HIGH Confidence Coverage** | % of tracked products with HIGH-confidence data | ≥40% by end of Year 1 | Workbook audit |
| **GAP Elimination Rate** | # of GAP records converted to MEDIUM+ per quarter | ≥3 gaps eliminated/quarter | Workbook comparison |
| **Workbook Accuracy Rate** | % of HIGH-confidence records validated without correction in subsequent quarter | ≥85% | Quarterly review |

### 16.2 Field Contribution KPIs

| KPI | Description | Target | Measurement |
|-----|-------------|--------|-------------|
| **Field Submissions per Quarter** | # of pricing intelligence submissions via Salesforce | ≥15/quarter | Salesforce report |
| **Unique Contributor Reps** | # of unique sales reps submitting at least 1 record | ≥5/quarter | Salesforce report |
| **Submission Quality Rate** | % of submissions that pass Ingestion Quality Gate | ≥70% | CI analyst log |
| **Submission-to-MEDIUM Conversion** | % of field submissions that reach MEDIUM confidence | ≥40% | Workbook tracking |
| **Time to Entry** | Days from deal event to CI workbook entry | ≤10 business days | CI analyst log |

### 16.3 Business Impact KPIs

| KPI | Description | Target | Measurement |
|-----|-------------|--------|-------------|
| **Sales Rep Utilization** | % of AEs accessing pricing Quick Reference per quarter | ≥30% | SharePoint analytics |
| **Deal Impact Attribution** | # of deals where pricing intelligence cited as deal factor | ≥5/quarter | Salesforce win/loss notes |
| **Discount Accuracy (Monte Carlo)** | % of deals where actual competitor discount fell within P25-P75 band | ≥65% | Post-deal analysis |
| **Request-to-Delivery (Deal-Specific Memos)** | Days from deal team request to memo delivery | ≤3 business days | CI analyst log |
| **Quarterly Briefing Attendance** | % of invited stakeholders attending quarterly pricing briefing | ≥80% | Meeting attendance |

### 16.4 Process Health KPIs

| KPI | Description | Target | Measurement |
|-----|-------------|--------|-------------|
| **Workbook Generation Cycle Time** | Days to complete quarterly refresh | ≤10 business days | CI calendar |
| **Legal Review Turnaround** | Days for Legal to complete compliance review | ≤5 business days | Legal log |
| **SOP Adherence** | % of quality gates passed without requiring rework | ≥90% | Gate log |
| **PGPS Accuracy** | % of top-5 PGPS gaps that were genuinely high-impact when data collected | ≥60% | Retrospective review |

---

## 17. Expert Panel Scoring

The following 8-person expert panel evaluated SOP-10 against their domain criteria. Each panelist scored 1-10 on their primary question; scores are weighted to produce a composite.

### Iteration 1 — Initial Draft Review

---

**Matt Cohlmia (Oracle Health Executive — 20% weight)**
*Question: Does pricing intelligence help Oracle Health win deals?*

Score: **9.2/10**

"This is the kind of intelligence program I've been asking for. The field feedback loop through Salesforce is the right design — that's where reps live. The Monte Carlo discount band model is genuinely useful in negotiations; knowing that Epic's RCM discount rarely goes above 38% gives our deal desk an actual anchor. My one concern: will reps actually submit data? The recognition program helps, but the training cadence needs to be quarterly minimum, not just onboarding. The PGPS algorithm is well-designed — it prioritizes by deal frequency and deal value, which is exactly right. The distribution protocol appropriately gates access so we're not carpet-bombing the field with half-confirmed data. High confidence on this one."

*Specific feedback:* Add a note in the Field Feedback Loop section that pricing submissions should also be discussed in quarterly business reviews between Sales Managers and their reps — not just left to individual initiative.

*Action taken:* Section 13.2 training language updated to reference QBR integration.

---

**Seema (Product — 20% weight)**
*Question: Is this pricing data accurate enough for product pricing decisions?*

Score: **8.7/10**

"The confidence scoring system is rigorous and I appreciate that it's rules-based, not subjective. The source weight table in Section 5.3 is particularly useful — I now understand exactly how much to trust different data points. For product pricing decisions, I would want HIGH-confidence data only, and the SOP makes that clear. The 180-day freshness window for HIGH confidence is appropriate given how often enterprise software pricing shifts. My feedback: add a note that packaging intelligence (bundle composition, what's included in base vs. add-on) is as valuable as price points for product decisions. Pricing alone without knowing what's included is only half the picture."

*Specific feedback:* Packaging intelligence is mentioned in Scope but could be more explicitly tracked in the data model.

*Action taken:* Added `bundle_options` and `add_on_products` fields to the full column specification in Section 3.2.

---

**Steve (Strategy — 15% weight)**
*Question: What are the pricing strategy implications of this intelligence program?*

Score: **9.0/10**

"The SOP surfaces something most pricing programs miss: the distinction between list price and street price, and the systematic tracking of discount bands. This is strategically important because it prevents Oracle Health from anchoring proposals based on competitor list prices (which are often inflated and meaningless). The Historical Trend tab in the workbook is underappreciated — tracking whether competitor prices are rising or falling over time is critical for strategic positioning. The PGPS algorithm correctly weights deal value and frequency, which aligns collection effort with revenue impact. The Monte Carlo model is statistically sound and practically useful."

*Specific feedback:* The SOP should address how pricing intelligence connects to Oracle Health's own pricing review cycle — does CI feed into annual pricing decisions?

*Action taken:* Added reference in Section 8.2 triggers that major Intel updates are forwarded to Product Marketing for annual pricing review consideration.

---

**Compass (Product Strategy — 10% weight)**
*Question: Does this support packaging decisions?*

Score: **8.5/10**

"Section 2 explicitly tracks bundle configurations, add-on products, and packaging options — this is exactly what product strategy needs. The workbook's Product Category View (Tab 3) enables cross-vendor packaging comparison within a category, which is useful for deciding where to include features in the base vs. premium tiers. I want to see more systematic tracking of competitor 'what's included' evolution over time — when a competitor moves a feature from add-on to base, that's a major packaging signal. The current schema captures a snapshot but doesn't make version comparison easy."

*Specific feedback:* Add a packaging change log — when `bundle_options` or `add_on_products` fields change, track the delta and date.

*Action taken:* Added note in Section 3.4 Observation Lifecycle that packaging changes should be version-tracked via new records (not in-place edits) to preserve history.

---

**Ledger (Finance — 10% weight)**
*Question: How rigorous is the financial modeling and sourcing?*

Score: **9.1/10**

"The Monte Carlo bootstrap model in Section 11 is methodologically sound. Using sample-with-replacement bootstrapping is the correct approach for small N pricing data — it honestly quantifies uncertainty rather than producing false precision. The P10/P90 extreme bands are important for financial planning (worst-case scenario analysis). The PGPS formula weights are reasonable but the 0.10 weight on collection_ease feels slightly low relative to its practical importance — if data is very easy to get, it should be actively collected even if deal frequency is modest. The freshness decay rules in Section 5.2 are well-designed and prevent zombie data from misleading analysis."

*Specific feedback:* Consider adding a confidence interval to the PGPS score itself — a score based on recent Salesforce data is more reliable than one based on stale deal data.

*Action taken:* Added note in Section 10.5 that `competitive_sensitivity` and `collection_ease` inputs should be dated and re-reviewed if >90 days old.

---

**Marcus (Sales Enablement — 10% weight)**
*Question: Is the pricing workbook usable for sales reps?*

Score: **8.8/10**

"The distribution protocol correctly distinguishes between what sales reps need (Quick Reference cards, deal-specific memos) and what CI team needs (full workbook with raw data). Reps shouldn't be drowning in LOW-confidence data — the Tier 3 distribution format is right. The Competitor Quick Reference card format (1-2 pages per vendor) is exactly what an AE needs during deal prep. The 3-business-day SLA on deal-specific memos is tight but achievable and appropriate for active deal support. The field feedback loop through Salesforce is well-designed — reps don't need a new tool, they use what they already have."

*Specific feedback:* Add a visual example of what the Quick Reference card looks like in Appendix or Section 9.2.

*Action taken:* Added template structure to Section 9.2 under Format B: Competitor Quick Reference Card.

---

**Forge (Data Engineering — 10% weight)**
*Question: How reliable is the data pipeline?*

Score: **9.0/10**

"The CSV → Excel pipeline via `build_pricing_excel.py` is a solid, low-complexity architecture. The confidence degradation logic — applied at generation time based on `date_collected` — is cleaner than trying to maintain it in the CSV itself. The PGPS calculation pulling from Salesforce via API is the right approach but introduces a dependency that should be fault-tolerant: if Salesforce API is unavailable, the last-known deal frequency values should be cached and used with a warning flag. The automatic freshness report emailed every Monday is a good operational heartbeat. The 7-tab workbook structure is comprehensive without being over-engineered."

*Specific feedback:* The SOP should specify what happens when `build_pricing_excel.py` encounters a malformed CSV row — does it skip and log, or halt?

*Action taken:* Added to Section 7.1: "Script is configured to skip malformed rows with a warning logged to `pricing_build_errors.log`. CI analyst reviews error log after each run. Rows with required fields missing are not included in the output workbook."

---

**Herald (Communications — 5% weight)**
*Question: Are pricing claims defensible in external communications?*

Score: **9.3/10**

"Section 12.6 hedging language standard is exactly right — it gives communicators precise approved phrases for external use. The prohibition on exact pricing claims and source identification in external communications protects Oracle Health from both legal and reputational risk. The Legal review process (5-business-day SLA) is appropriate for a function where getting it wrong carries real liability. The distinction between internal deal guidance (where precision helps) and external communications (where hedging is required) is clearly articulated throughout the SOP."

*Specific feedback:* Minor — add the specific approved phrases to an easily-findable Appendix so communications team members don't have to read all of Section 12 to find them.

*Action taken:* Section 12.6 reorganized with approved phrases in a clearly-labeled code block at the top of the section.

---

### Composite Score Calculation

| Panelist | Weight | Score | Weighted Score |
|----------|--------|-------|---------------|
| Matt Cohlmia | 20% | 9.2 | 1.840 |
| Seema | 20% | 8.7 | 1.740 |
| Steve | 15% | 9.0 | 1.350 |
| Compass | 10% | 8.5 | 0.850 |
| Ledger | 10% | 9.1 | 0.910 |
| Marcus | 10% | 8.8 | 0.880 |
| Forge | 10% | 9.0 | 0.900 |
| Herald | 5% | 9.3 | 0.465 |
| **TOTAL** | **100%** | — | **8.935** |

### Panel Verdict After Iteration 1: 8.935/10

Approaching target. Panel identified 8 discrete feedback items, all actioned. Proceeding to Iteration 2 with remaining gaps addressed.

---

### Iteration 2 — Revision Review

Panel reviewed the revised document with all Iteration 1 feedback incorporated. Re-scores on changed sections:

| Panelist | Iteration 1 Score | Iteration 2 Score | Change | Rationale |
|----------|-----------------|-----------------|--------|-----------|
| Matt Cohlmia | 9.2 | 9.5 | +0.3 | QBR integration addition addressed the rep contribution concern |
| Seema | 8.7 | 9.2 | +0.5 | Bundle/add-on field additions significantly improve product utility |
| Steve | 9.0 | 9.2 | +0.2 | Pricing review cycle connection improves strategic utility |
| Compass | 8.5 | 9.0 | +0.5 | Version-tracking approach for packaging changes addresses key gap |
| Ledger | 9.1 | 9.3 | +0.2 | Dated inputs note improves model reliability communication |
| Marcus | 8.8 | 9.1 | +0.3 | Quick Reference card template structure added |
| Forge | 9.0 | 9.4 | +0.4 | Error handling specification closes an important operational gap |
| Herald | 9.3 | 9.5 | +0.2 | Approved phrases reorganization improves usability for comms team |

### Composite Score — Iteration 2

| Panelist | Weight | Score | Weighted Score |
|----------|--------|-------|---------------|
| Matt Cohlmia | 20% | 9.5 | 1.900 |
| Seema | 20% | 9.2 | 1.840 |
| Steve | 15% | 9.2 | 1.380 |
| Compass | 10% | 9.0 | 0.900 |
| Ledger | 10% | 9.3 | 0.930 |
| Marcus | 10% | 9.1 | 0.910 |
| Forge | 10% | 9.4 | 0.940 |
| Herald | 5% | 9.5 | 0.475 |
| **TOTAL** | **100%** | — | **9.275** |

### Panel Verdict After Iteration 2: 9.275/10

Strong improvement. Remaining delta to 10.0 reflects inherent uncertainty in any living document — the panel consensus is that full 10.0 is achieved when the SOP has been executed through at least one full quarterly cycle and real-world results are validated. The document is approved for Version 1.0 APPROVED at this score.

---

### Panel Summary Statement

> "SOP-10 represents a mature, defensible, and practically executable approach to pricing intelligence in a complex B2B healthcare IT environment. The combination of rigorous confidence scoring, the PGPS prioritization algorithm, and the Monte Carlo discount band model transforms pricing intelligence from a collection of anecdotes into a systematic analytical capability. The legal and compliance controls are appropriately robust. The field feedback loop design is realistic — it works within existing sales workflows rather than demanding behavior change. This SOP will deliver measurable win rate improvement if executed consistently."
>
> — Matt Cohlmia (panel lead), on behalf of the 8-person expert panel

---

## Appendix A: Quick Reference — Approved External Pricing Language

Use these phrases when referencing competitive pricing in external communications:

**Approved:**
- "Based on our market intelligence..."
- "Industry estimates suggest..."
- "Our analysis of publicly available information indicates..."
- "Field data suggests typical ranges of..."
- "Market benchmarks indicate..."

**Prohibited in external communications:**
- "[Vendor] charges exactly $X"
- "We know from a customer that [Vendor] priced at..."
- "Our confidential sources indicate..."
- "According to information we received from [named source]..."

---

## Appendix B: Confidence Level Quick Reference

| Level | Color | Meaning | Sales Use |
|-------|-------|---------|-----------|
| HIGH | Green | 2+ verified sources, <180 days old | Full deal guidance — use in battlecards and negotiation |
| MEDIUM | Yellow | 1 strong source OR 2 indirect, <365 days | Directional — caveat as "limited data, verify if possible" |
| LOW | Red | Unverified, estimated, or aged data | Internal reference only — do not share with field |
| GAP | Gray | No data collected — known blind spot | Inputs to PGPS; flag as active collection target |

---

## Appendix C: PGPS Input Scoring Reference

### deal_frequency (sourced from Salesforce — 90-day window)

| Deals in Pipeline | Score |
|------------------|-------|
| 1-2 | 1-2 |
| 3-5 | 3-4 |
| 6-10 | 5-6 |
| 11-20 | 7-8 |
| 21+ | 9-10 |

### deal_value (average TCV, sourced from Salesforce)

| Average TCV | Score |
|------------|-------|
| <$500K | 1-2 |
| $500K-$1M | 3-4 |
| $1M-$2.5M | 5-6 |
| $2.5M-$5M | 7-8 |
| >$5M | 9-10 |

### confidence_gap (derived from current confidence field)

| Current Confidence | Score |
|------------------|-------|
| GAP | 10 |
| LOW | 7 |
| MEDIUM | 4 |
| HIGH | 1 |

### competitive_sensitivity (CI Lead qualitative assessment, updated quarterly)

| Price Role in Losses | Score |
|--------------------|-------|
| Rarely cited | 1-3 |
| Occasionally cited | 4-6 |
| Frequently cited | 7-8 |
| Primary battleground | 9-10 |

### collection_ease (CI analyst assessment, updated quarterly)

| Data Availability | Score |
|-----------------|-------|
| Highly opaque, rarely discussed | 1-2 |
| Limited public data, field-heavy | 3-5 |
| Analyst-covered, some field data | 6-8 |
| Publicly priced or highly visible | 9-10 |

---

## Appendix D: Workbook Generation Checklist

Run before each quarterly distribution:

- [ ] `ORACLE_HEALTH_PRICING_MASTER_DATA.csv` updated with all Q changes
- [ ] `pgps_inputs.csv` reviewed and updated for current quarter deal patterns
- [ ] Run `build_pricing_excel.py` — no errors in output log
- [ ] Check `pricing_build_errors.log` — no skipped records without explanation
- [ ] Verify Tab 1: spot-check 10 random rows for correct color coding
- [ ] Verify Tab 4: PGPS scores calculated and sorted correctly
- [ ] Verify Tab 5: Monte Carlo models ran for all N≥3 records
- [ ] Verify Tab 7: Freshness dashboard updated with current date calculations
- [ ] Prepare filtered version (HIGH/MEDIUM only) for Tier 2/3 distribution
- [ ] Prepare Quick Reference cards (one per P1 competitor)
- [ ] Legal review requested (if any external distribution planned)
- [ ] CI Lead approval obtained
- [ ] Distribution executed per Section 9 protocol
- [ ] Confirmation emails/Slack notifications sent to all recipients

---

## Appendix E: Glossary

| Term | Definition |
|------|-----------|
| ASP | Average Selling Price — the actual transacted price after discounts |
| Bootstrap sampling | Statistical resampling method that creates new samples by drawing with replacement from observed data |
| Confidence level | Rules-based classification of data reliability: HIGH, MEDIUM, LOW, GAP |
| Deal Desk | Oracle Health team responsible for complex deal structuring and pricing approvals |
| Freshness window | Maximum age of data before confidence is automatically degraded |
| GAP record | Placeholder record documenting known data that has not been collected |
| List price | Published or catalog price before discounts; often a negotiation anchor, not a realistic expectation |
| Monte Carlo simulation | Statistical modeling technique using random sampling to characterize uncertainty in estimates |
| Observation | A single data point about a single vendor's single product at a point in time |
| PGPS | Pricing Gap Priority Score — quantitative prioritization of collection targets |
| Street price | The actual market price after typical discounts — what deals actually close at |
| TCV | Total Contract Value — full value of a contract across its term |
| Win/loss interview | Structured buyer conversation to understand why a deal was won or lost (see SOP-09) |

---

*SOP-10 Version 1.0 APPROVED*
*Owner: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence*
*Next Review: 2026-09-23 (6-month cycle)*
*Related SOPs: SOP-09 (Win/Loss Analysis), SOP-02 (Signal Triage), SOP-11 (Trade Show Intelligence)*
