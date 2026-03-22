# SOP-13: Market Sizing (R-01 Methodology)

**Owner**: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence
**Version**: 1.0 DRAFT — Awaiting Mike's approval
**Last Updated**: 2026-03-22
**Category**: Strategic Analysis & Deliverables
**Priority**: P1 — Proprietary methodology, used for real strategic deliverables
**Maturity**: Implicit → Documented (this SOP)
**Sources**: R-01 Market Sizing Shell v2.0, Matt Cohlmia's Market Sizing 101, live Public Health engagement (ChatGPT March 2026), 6 research files (1.93 MB, 150+ external sources)
**Research Basis**: HBS Note 510-081, Stanford Biodesign, Bass (1969), Wharton conjoint, McKinsey/BCG/Bain frameworks, Ipsos MDD, KLAS, Gartner, CMS/AHA/ONC government data

---

## Purpose

Size addressable markets for Oracle Health solutions using a structured, assumption-transparent, multi-method approach that produces executive-grade TAM/SAM/SOM analyses with full source provenance, sensitivity testing, and healthcare-specific structural adjustments.

**Why this matters:**
- Market sizing is the foundation for strategic investment decisions, white papers, and executive memos
- Matt Cohlmia's team uses this methodology across all domains — Payer, Provider, Life Sciences, RCM, ERP, Interoperability, Data Infrastructure
- Bad market sizing destroys credibility: Strategex documented a case where AI-generated sizing **overstated a market by $33 billion** (Strategex 2024)
- 85% of CRM closed-lost data is fundamentally wrong (Corporate Visions, 100K+ deals) — the same risk applies to market sizing that accepts surface-level data
- R-01 is the only Oracle Health methodology that enforces source tagging, assumption transparency, and mandatory vulnerability assessment

**What the research says:**
- Companies using structured market sizing with triangulation produce estimates within ±15% of actuals (Umbrex)
- Stanford Biodesign found 10:1 gaps between top-down and bottom-up estimates in healthcare — the gap is diagnostic, not a failure (Zenios et al., 2009)
- Bottom-up is mandatory for B2B enterprise with countable accounts (McKinsey, BCG, Bain consensus)
- Combining multiple forecasting methods reduces forecast error by >50% (Armstrong & Green, Wharton, 2017)

---

## THE R-01 FRAMEWORK

### Overview

R-01 is a 7-phase, guided market sizing engagement. It enforces:
- **No black boxes** — every number traces to a named source or flagged assumption
- **No false precision** — ranges, not point estimates
- **No unsourced statistics** — every data point carries a source tag
- **Three deliverables minimum** — data table, executive narrative, assumption audit trail
- **Mandatory vulnerability assessment** — critical thinking gate runs every time
- **Dual reconciliation** — top-down AND bottom-up, with gap analysis (Stanford Biodesign protocol)

### The Nine Methods

#### Matt Cohlmia's Original Six

| # | Method | Best When | How It Works |
|---|--------|-----------|-------------|
| 1 | **TAM/SAM/SOM** | A credible published total market number exists | Start with known total market → filter to serviceable → estimate capturable share |
| 2 | **Unit Economics** | You know the customer landscape and pricing model | Define segments → count entities per segment → apply pricing and share assumptions |
| 3 | **Funnel Model** | New markets or population-defined opportunities | Total population → progressive filters (geography, eligibility, adoption, conversion) |
| 4 | **Value Capture** | Opportunity is about solving an inefficiency | Size the waste/cost problem → estimate solvable portion → apply share and capture rates |
| 5 | **Competitor Benchmark** | Entering an established market with visible competitors | Start with competitors' known/estimated revenue → estimate Oracle's capturable share |
| 6 | **Wallet Share Expansion** | Cross-sell/upsell within installed base | Current customer count × expansion revenue opportunity × adoption rate |

#### Three Healthcare-Specific Additions (from research)

| # | Method | Best When | How It Works | Source |
|---|--------|-----------|-------------|--------|
| 7 | **Installed Base Analysis** | Market is saturated (>90% adoption) — sizing displacement, not greenfield | Map installed base → segment by contract vintage/satisfaction/switching propensity → size the replacement window | KLAS, Definitive HC |
| 8 | **Bass Diffusion Timing** | Forecasting WHEN adoption hits a threshold | Model innovators (coefficient p) + imitators (coefficient q) against market potential (m) → S-curve forecast | Bass 1969; Everson et al. 2018 (R²=0.91 for EHR) |
| 9 | **VBC Waste Sizing** | Value-based care / population health where the "market" is addressable waste | TAM = addressable waste pool × realistic capture rate × vendor's share of savings | JAMA ($760-935B waste); Health Affairs |

### Methodology Selection: Three Diagnostic Questions

**Q1**: "Do you have a known total market number from a credible source, or are we building from the ground up?"
- Known number exists → TAM/SAM/SOM or Competitor Benchmark
- Building from scratch → Unit Economics, Funnel Model, or Value Capture

**Q2**: "Is this about sizing a new market opportunity, or validating an existing estimate?"
- New opportunity → TAM/SAM/SOM, Value Capture, or Funnel Model
- Validating existing → Competitor Benchmark, Unit Economics, or Wallet Share Expansion

**Q3**: "Is this market greenfield or replacement?"
- Greenfield (<50% adoption) → Standard methods (1-6)
- Replacement (>90% adoption) → Installed Base Analysis (7) is mandatory as primary or triangulation partner
- Timing question → Bass Diffusion (8)
- Waste-reduction market → VBC Waste Sizing (9)

---

## SOURCE TIER HIERARCHY

Every data point carries both a **source tag** (who provided it) and a **source tier** (how reliable the source type is).

### Source Tags (R-01 Original — Matt's System)

| Tag | Definition | Executive Delivery Rule |
|-----|-----------|----------------------|
| **SOURCED** | Specific publication, report, filing, or dataset with date cited | Green light for all audiences |
| **USER-SOURCED** | Strategist provided this data; flagged for external verification | Include but flag: "Source: [name]. Not independently verified." |
| **AI-SOURCED** | Model found or synthesized; routes to U-01 audit automatically | Do NOT present to executive audiences without audit clearance |
| **ESTIMATED** | Not directly sourced but based on stated reasoning | Acceptable internally; verify before external delivery |
| **ASSUMED** | No direct basis; placeholder only | Label clearly as "[ASSUMPTION]" — must validate before executive use |

### Source Tier Hierarchy (New — from research)

| Tier | Description | Trust Level | Examples |
|------|-------------|-------------|---------|
| **Tier 1** | Primary research: customer interviews, surveys, transactional data, government admin data | Highest | CMS enrollment, AHA Annual Survey, KLAS interviews, HCRIS cost reports |
| **Tier 2** | Audited financials, SEC filings, peer-reviewed academic studies | High | IQVIA 10-K, R1 RCM revenue, Everson et al. (JMIR 2018) |
| **Tier 3** | Trade association data, analyst firms with disclosed methodology | Medium | CAQH Index, Gartner Market Guides, AHIP reports |
| **Tier 4** | General analyst reports without methodology disclosure, press releases | Low — directional only | Grand View Research, MarketsandMarkets (abstracts only) |
| **Tier 5** | AI-generated summaries, unattributed website statistics | Unreliable — never as key input | ChatGPT estimates, unattributed blog stats |

**Rule**: Every TAM/SAM/SOM number must trace to Tier 2-3 minimum. SOM must incorporate at least one Tier 1 input.

**The syndicated report warning**: RCM market estimates range from $51.6B to $343.78B across firms — a **6.5x spread**. This reflects market definition disagreement, not measurement error. **Never use a syndicated healthcare market number without reading the market definition and scope section.**

---

## PHASE 0: INTAKE

**Output artifact**: Problem Framing Card

### Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| **Market to size** | Product/solution + use case | "Active surveillance module for public health" |
| **Domain** | Payer / Provider / Life Sciences / RCM / ERP / HCM / Interop / Data Infra | "Public Health (cross-domain)" |
| **Decision this informs** | What decision this number unlocks | "Strategic white paper for market entry" |
| **Audience** | Who consumes this analysis | "Matt, Seema, Strategy & Product teams" |
| **Deliverable format** | White paper / deck / memo / briefing / internal planning | "White paper with embedded data table" |
| **Geographic scope** | US only / NA / Global / Specific regions | "US + UK + UAE + Malaysia + NZ" |
| **Time horizon** | Point-in-time / 5-year run-rate / cumulative 5-year | "5-year run-rate ARR" |
| **Existing data** | Published numbers or internal baselines | "$1.35B syndromic surveillance (2024)" |
| **Greenfield or replacement?** | Is adoption <50% or >90%? | "Greenfield for public health; replacement for EHR" |

**Gate**: Do not proceed to Phase 1 until all fields are populated.

---

## PHASE 1: METHODOLOGY SELECTION

**Output artifact**: Methodology Selection Card

Run the three diagnostic questions. Select 1-2 methods. Document reasoning.

### When to Triangulate (Use Two Methods)

- Decision is high-stakes (>$10M investment, exec-level visibility)
- Top-down and bottom-up estimates diverge by >15% (Umbrex standard)
- Primary research is limited and secondary sources vary widely
- Market is nascent or highly disrupted

### Method Pairing Guide

| Primary | Good Triangulation Partner | Why |
|---------|--------------------------|-----|
| TAM/SAM/SOM | Unit Economics | Top-down meets bottom-up — convergence = defensible |
| Unit Economics | Competitor Benchmark | Your build-up vs what competitors actually capture |
| Funnel Model | Value Capture | Population math vs economic opportunity math |
| Wallet Share | Unit Economics | Installed base vs total addressable |
| Installed Base (7) | Competitor Benchmark (5) | Displacement window vs competitor revenue floor |

### Formal Triangulation Protocol

1. Run both methods independently — do not let one inform the other's assumptions
2. Compare results: agreement within ~15-20% → use midpoint, document both
3. Divergence >20% → investigate which assumptions drive the gap before publishing
4. Report the range, not just the midpoint
5. Third-method options: competitor revenue benchmarking, customer survey, analogous market analysis

---

## PHASE 2: ASSUMPTION SCAFFOLDING + FILE INTAKE

**Output artifact**: Assumption Register

### Step 2A: Material Intake

Collect existing materials. For each, document:
1. What is this source?
2. What usable data does it contain?
3. Confidence level?
4. Source tag + source tier assignment

### Step 2B: Build Assumption Register

**Universal assumptions** (all methods): geographic scope, time horizon, Oracle Health's current position, key market dynamics.

**Method-specific assumptions**: Build only for the selected method(s) — see R-01 Shell v2.0 for full assumption templates per method.

### Assumption Register Template

| # | Assumption | Value | Source Tag | Source Tier | Source Detail | Confidence |
|---|-----------|-------|------------|------------|---------------|------------|
| 1 | [description] | [value] | SOURCED | Tier 1 | CMS MA enrollment, Feb 2026 | High |

**Gate**: If >50% of assumptions are ASSUMED (Tier 5), stop and gather more data before calculating.

---

## PHASE 3: CALCULATION ENGINE

**Output artifact**: Calculation Workbook

### Rules
- Show every step: input → operation → result → which assumption drives it
- Reference Assumption Register row numbers
- Never produce a single number — always a range or scenario set
- All math transparent

### Three-Scenario Modeling (Required)

| Scenario | Story | Pricing Posture |
|----------|-------|-----------------|
| **Conservative** | Most challenging plausible outcome | Low-end penetration, list price |
| **Base** | Most likely: current trajectory, management plan | Moderate penetration, mid-range pricing |
| **Aggressive** | Most favorable plausible: regulatory tailwinds, competitor exits | High penetration, platform bundling |

**Key discipline**: Aggressive is not fantasy. It must be a plausible scenario with internal consistency — not just inflated numbers (Phoenix Strategy Group).

**Probability weighting** (optional):
- Conservative: 20-30% / Base: 50-60% / Aggressive: 15-25%
- Expected value = Σ(Scenario × Probability)

### Year-5 ARR Table Format

| Segment | Anchor Count (source) | Conservative | Base | Aggressive |
|---------|----------------------|-------------|------|-----------|
| [segment] | [#] ([Tier 1 source]) | [pen%] × $[ASP] = $[X] | [pen%] × $[ASP] = $[X] | [pen%] × $[ASP] = $[X] |
| **Total Year-5 ARR** | | **$[X]** | **$[X]** | **$[X]** |

---

## PHASE 4: SENSITIVITY ANALYSIS

**Output artifact**: Sensitivity Table + Tornado Chart

### Protocol
1. Identify 3-5 key input variables
2. Define range for each: ±10%, ±25%, or bounds from primary research
3. Run single-variable sensitivity (tornado chart)
4. Top 3 assumptions should explain **≥70% of variance** (Umbrex standard)
5. State explicitly: "This estimate is most sensitive to X and Y"

---

## PHASE 5: OUTPUT ASSEMBLY

**Output artifact**: Three deliverables (always)

### Deliverable A — Data Table
Structured table matching Matt Cohlmia's format. Segmentation tiers labeled. Assumptions flagged by source tag + tier. Ready to paste into deck or memo.

### Deliverable B — Executive Narrative
2-3 paragraphs at Seema's executive altitude:
- Opens with bottom-line number and what it means for Oracle Health
- States methodology and why selected
- Names 2-3 most important assumptions and their basis
- Closes with sensitivity and recommended next steps

### Deliverable C — Assumption Audit Trail
Complete register updated with calculation results and sensitivity ratings.

---

## PHASE 6: CRITICAL THINKING GATE (NON-OPTIONAL)

**Output artifact**: Vulnerability Assessment

This phase runs every time. Not optional. Mirrors Matt Cohlmia's teaching framework and Stanford Biodesign's critical thinking protocol.

### Three Required Questions

**1. "What are the weak points in this analysis?"**
2-3 specific areas where the analysis is most vulnerable.

**2. "Where might this lead us astray?"**
The scenario where this sizing produces a misleading conclusion.

**3. "How would we validate?"**
2-3 specific validation steps.

### Healthcare-Specific Vulnerability Checks

| Check | Question | Why |
|-------|----------|-----|
| **Greenfield vs replacement** | Is this market >90% adopted? Did we use Installed Base Analysis? | 96% EHR adoption = displacement market |
| **GPO filter** | Did we account for GPO preferred vendor constraints on SAM? | 97% of hospitals in ≥1 GPO |
| **Deal cycle discount** | Did we apply 12-24 month sales cycle to SOM? | Healthcare procurement is structurally slow |
| **Network effects** | Did we account for platform lock-in (Epic at 42.3%)? | "Facilities × price" overestimates penetrability |
| **Regulatory timing** | Did we identify regulatory forcing functions? | CMS-0057-F, TEFCA create demand windows |
| **Contract vintage** | Did we check when installed base contracts expire? | Only renewal window is addressable |

---

## PHASE 7: BASS DIFFUSION FORECAST (OPTIONAL — TIMING QUESTIONS)

**Output artifact**: Adoption S-Curve with Timeline

When the question is "when will adoption reach X%?", apply Bass diffusion.

### Inputs
- **m**: Ultimate market potential (from TAM/SAM)
- **p**: Innovation coefficient (enterprise tech: 0.01-0.03)
- **q**: Imitation coefficient (enterprise: 0.2-0.5)

### Healthcare IT Benchmarks
- Everson et al. (2018, JMIR): Bass applied to HIMSS EMRAM, R² = 0.91
- Majority of hospitals will not reach EMRAM Stage 7 until 2035
- 71% of hospitals using EHR-integrated predictive AI in 2024 (ONC Data Brief 80)

---

## POST-R-01 ROUTING

| Condition | Route To |
|-----------|----------|
| AI-SOURCED or ESTIMATED claims present | U-01 Anti-Hallucination Protocol |
| USER-SOURCED claims for external use | U-02 Source Verification Protocol |
| White paper path | D-01 White Paper Shell, Phase 1 |
| Executive memo or deck | D-02 Executive Memo |
| Further stress-testing needed | U-05 Red Team Protocol |

---

## HARD ANCHOR TABLE — ORACLE HEALTH DOMAINS

### Government Data Sources (Tier 1 — Free, Verified)

| Entity / Metric | Hard Anchor | Source |
|---|---|---|
| Total US health spending | ~$5.0T (2024) | CMS NHE |
| US hospitals | 6,093 | AHA Fast Facts 2026 |
| US hospital beds | 913,136 | AHA Fast Facts 2026 |
| System-affiliated hospitals | 68% | AHA |
| MA enrollees | ~34.1M (54%+ of Medicare) | CMS/KFF |
| Medicaid + CHIP enrollees | ~76M | CMS Medicaid.gov |
| Medicaid MCO enrollees | ~61.7M (Dec 2024) | HMA |
| Hospital EHR adoption | 96%+ | ONC Dashboard |
| Avg hospital IT spend | $10.5M/year | Definitive HC |
| Local health departments | 3,300+ | NACCHO |
| State health agencies | 59 | ASTHO |
| Clinical trials registered | 500,000 | ClinicalTrials.gov |
| Admin costs | $83B/year; $258B avoided | CAQH Index 2024 |
| TEFCA organizations | 14,214 | HealthIT.gov |
| QHINs designated | 11 (Oracle Health is one) | Sequoia Project |
| Pharma R&D spend | ~$288B global (2024) | IQVIA |
| 340B drug purchases | $81.4B (2024) | Drug Channels |

### Competitor Revenue Anchors (Tier 2)

| Company | Revenue | Segment |
|---------|---------|---------|
| IQVIA | $15.4B (FY2024) | CRO/Life Sciences |
| R1 RCM | $2.46B (LTM 2024) | Outsourced RCM |
| Waystar | ~$900M run-rate | RCM Software |
| Workday | $7.3B (FY2024) | HCM/ERP |
| HCLS IT total | $265B → $309B | Gartner (market ceiling) |

### Domain TAM Ranges (Tier 3-4 — Triangulated)

| Domain | TAM 2024 | CAGR |
|--------|---------|------|
| Payer — Claims Mgmt Tech | $12-19B | 8-14% |
| Payer — PA Automation | $2.2-4.1B | 13-18% |
| RCM Technology | $58-65B | 12.4% |
| AI Medical Coding | $2.7B | 14.3% |
| EHR Global | $33-36B | 5.8% |
| Ambient AI/Scribes | $600M (+2.4x YoY) | ~140% |
| eClinical (CTMS+EDC+ePRO) | $10.3B | 14.4% |
| RWE Analytics | $2.3-4.7B | 14-16% |
| Healthcare ERP | $7.5-8.0B | 6.4% |
| Healthcare WFM/HCM | $1.7-1.9B | 10-13% |
| HIE Market | $1.7-4.2B | 9-10% |
| FHIR Platforms | $1.5B | 16.2% |
| Healthcare Analytics | $44.8-55.5B | 21-25% |
| US AI in Healthcare | $13.3B | 36.8% |
| GenAI in Healthcare | $2.2B | 30.1% |
| Healthcare Cloud Infra | $53.8-79.5B | 16-18% |

---

## COMMON PITFALLS

| Pitfall | How R-01 Prevents It | Source |
|---------|---------------------|--------|
| **TAM inflation** | SAM/SOM filters + MECE segmentation | McKinsey |
| **False precision** | Ranges required | Stanford Biodesign |
| **Unsourced numbers** | Source tagging + tier system | R-01 |
| **Double-counting** | MECE segmentation tree | BCG/Bain |
| **Ignoring procurement friction** | Deal cycle discount + GPO filter | Research |
| **AI overestimation** | $33B overstatement documented | Strategex 2024 |
| **Syndicated report confusion** | 6.5x RCM variance warning | Research |
| **Greenfield assumption in replacement market** | Installed Base Analysis mandatory at >90% adoption | KLAS/ONC |
| **Equating users with buyers** | Size by buying unit, not using unit | Research |

---

## KEY EXPERT AUTHORITIES

| Expert | Affiliation | Key Contribution |
|--------|-------------|-----------------|
| Frank Bass (1926-2006) | Purdue / UT Dallas | Diffusion model — 5,145 citations |
| Everett Rogers (1931-2004) | USC | Diffusion of Innovations — 5 adopter categories |
| Paul Green (1927-2012) | Wharton | Invented conjoint analysis |
| Clayton Christensen (1952-2020) | HBS | JTBD redefines market boundaries |
| Thomas Steenburgh | UVA Darden (formerly HBS) | HBS Note 510-081 |
| Paul Yock / Stefanos Zenios | Stanford Biodesign | Healthcare dual reconciliation |
| Jordan Everson | Johns Hopkins / ONC | Bass applied to EHR, R²=0.91 |
| J. Scott Armstrong | Wharton | Combining methods reduces error >50% |

---

## EXAMPLE: PUBLIC HEALTH MARKET SIZING (LIVE R-01 OUTPUT)

**Market**: Active surveillance and intervention module for public health
**Method**: Unit Economics | **Scope**: US + UK + UAE + Malaysia + NZ | **Horizon**: 5-year ARR

| Segment | Anchor Count (source) | Conservative | Base | Aggressive |
|---------|----------------------|-------------|------|-----------|
| US local health depts | 3,300 (NACCHO) | 3% × $150K = $14.9M | 8% × $250K = $66.0M | 15% × $350K = $173.3M |
| US state/territorial | 59 (ASTHO) | 20% × $750K = $8.9M | 40% × $1.25M = $29.5M | 60% × $2.0M = $70.8M |
| Provider systems (US) | ~800 (est.) | 1% × $200K = $1.6M | 5% × $400K = $16.0M | 12% × $650K = $62.4M |
| UK (UKHSA) | 1 | $5.0M | $8.0M | $12.0M |
| UAE | 1 | $3.0M | $5.0M | $8.0M |
| Malaysia | 1 | $2.0M | $3.5M | $6.0M |
| New Zealand | 1 | $1.5M | $2.5M | $4.0M |
| **Total Year-5 ARR** | | **$36.8M** | **$130.5M** | **$360.5M** |

---

## INTEGRATION WITH OTHER SOPs

| SOP | Relationship |
|-----|-------------|
| SOP-07 (Competitor Profiles) | Feeds Method 5 (Competitor Benchmark) |
| SOP-08 (Battlecards) | Market sizing informs competitive positioning |
| SOP-09 (Win/Loss) | Win rates feed SOM capture assumptions |
| SOP-10 (Pricing Intel) | ASP assumptions for Unit Economics |
| SOP-11 (Trade Show) | Captures pricing/packaging for triangulation |
| SOP-14 (Offsite Prep) | R-01 is a core input to white papers |
| SOP-18 (Expert Panel) | All R-01 outputs route through panel |

---

## RESEARCH CORPUS

All research in `docs/research/sop-13-market-sizing/`:

| File | Content | Size |
|------|---------|------|
| `01-enterprise-best-practices.md` | McKinsey/BCG/Bain frameworks, 19 sources | 166KB |
| `02-healthcare-specific-methods.md` | KLAS, Gartner, CMS NHEA, VBC waste | 266KB |
| `03-academic-papers.md` | HBS, Stanford Biodesign, Bass, Wharton, 12 experts | 464KB |
| `04-training-data-payer-rcm-provider.md` | MA enrollment, KLAS share, HFMA benchmarks | 329KB |
| `05-training-data-lifesci-erp-interop-data.md` | 7 domains, TEFCA, eClinical, GenAI | 393KB |
| `06-government-data-sources.md` | 40+ verified URLs, hard anchor table | 309KB |
| **Total** | **150+ external sources, zero training data** | **1.93 MB** |
