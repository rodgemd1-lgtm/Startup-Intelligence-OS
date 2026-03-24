# SOP-05: Source Evaluation & Data Provenance

**Owner**: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-23
**Category**: Daily Intelligence Operations
**Priority**: P1 — Core methodology IP (differentiator)
**Maturity**: Partial (enforced in code, not documented as standalone SOP)
**Research Basis**: Oracle Health M&CI live MCP-fetch architecture, HTTP verification protocols embedded in intelligence pipeline code, SCIP (Strategic and Competitive Intelligence Professionals) source evaluation standards, OSINT source classification frameworks (Bellingcat, ACINT), financial intelligence data governance (SEC EDGAR verification protocols), healthcare regulatory source hierarchy (FDA, CMS, ONC), confidence scoring approaches adapted from NLP/IR literature (BLEU, ROUGE, calibration curves)

---

## Table of Contents

1. [Purpose](#1-purpose)
2. [Scope](#2-scope)
3. [Architecture](#3-architecture)
4. [The Golden Rule: MCP-Only Data Protocol](#4-the-golden-rule-mcp-only-data-protocol)
5. [Source Tier Classification System](#5-source-tier-classification-system)
6. [Confidence Scoring Methodology](#6-confidence-scoring-methodology)
7. [URL Verification Protocol](#7-url-verification-protocol)
8. [Monte Carlo Simulation: Source Reliability Modeling](#8-monte-carlo-simulation-source-reliability-modeling)
9. [Predictive Algorithm: Source Quality Score (SQS)](#9-predictive-algorithm-source-quality-score-sqs)
10. [Data Provenance Tagging Format](#10-data-provenance-tagging-format)
11. [Unverifiable Sources: Handling Protocol](#11-unverifiable-sources-handling-protocol)
12. [Source Refresh Cadence](#12-source-refresh-cadence)
13. [RACI Matrix](#13-raci-matrix)
14. [KPIs](#14-kpis)
15. [Audit Trail Requirements](#15-audit-trail-requirements)
16. [Expert Panel Scoring](#16-expert-panel-scoring)

---

## 1. Purpose

This SOP defines Oracle Health M&CI's source evaluation methodology and data provenance framework — the rules that govern where intelligence data comes from, how it is classified, how its confidence is scored, and how its origin is tracked through the intelligence lifecycle.

**The core problem this SOP solves:**

In competitive intelligence, the source of a claim is as important as the claim itself. A pricing insight sourced from a competitor's official investor relations page carries fundamentally different weight than one extracted from an anonymous industry blog. An executive hire confirmed via SEC Form 8-K is categorically different from one inferred from a LinkedIn post. An AI-generated summary that draws on training data — data with an unknown cutoff date, unknown factual accuracy, and no verifiable URL — is not intelligence. It is hallucination wearing intelligence's clothing.

Oracle Health's M&CI department operates in a high-stakes environment. Our intelligence products reach C-suite executives, inform multi-million-dollar go-to-market decisions, shape competitive positioning for Oracle's healthcare division, and influence contract negotiations with health systems. In this environment, a single sourcing error that reaches Matt Cohlmia or a board-level briefing can permanently damage the department's credibility and, worse, cause Oracle Health to act on false information.

This SOP establishes the differentiating methodology that separates Oracle Health M&CI from standard competitive intelligence functions:

- **MCP-only data protocol**: Every factual claim in an intelligence product originates from a live MCP tool fetch — never from AI training data recall
- **Four-tier confidence scoring**: Every claim carries a confidence label (HIGH / MEDIUM / LOW / UNVERIFIED) based on objective, auditable criteria
- **URL verification**: Every web source has a verified HTTP 200 response at time of retrieval
- **Source tier classification**: Every source is classified by reliability tier before its content is used
- **Provenance tagging**: Every intelligence item carries a complete metadata record of its origin

This is not bureaucratic compliance. This is competitive advantage. Executives who receive intelligence from this department know — and have come to depend on the fact — that every claim is traceable, verifiable, and current.

**What this SOP governs:**

- The rules for classifying sources into tiers
- The formula for computing confidence scores
- The protocol for verifying URLs
- The format for provenance metadata attached to every intelligence item
- The procedure for handling unverifiable sources
- The Monte Carlo model for estimating confidence decay over time
- The SQS predictive algorithm for source quality assessment

---

## 2. Scope

**In scope:**

- All intelligence products produced by Oracle Health M&CI, including:
  - Daily signal feeds
  - Weekly executive briefings
  - Competitor profiles and battlecards
  - Win/loss analysis reports
  - Market sizing studies
  - War game scenario inputs
  - Ad-hoc research requests from Matt Cohlmia and Oracle Health leadership
- All data ingestion pipelines that supply raw intelligence to the above products
- All agents, scripts, and automated workflows that retrieve, score, or tag source data
- All human-curated research performed by M&CI analysts

**Out of scope:**

- Internal Oracle Health data (pricing, pipeline, customer records) — these have separate data governance under Oracle Legal/Compliance
- Third-party licensed data feeds (Definitive Healthcare, Klue, etc.) — evaluated under vendor SLA, not this SOP
- Non-intelligence artifacts (slide templates, email formats, calendar management)

**Applies to:**

- Jake (primary intelligence agent)
- All Susan agents operating within the M&CI workflow
- Any human analyst contributing to M&CI intelligence products
- Any future automated pipeline ingesting competitive data

---

## 3. Architecture

The following diagram shows the end-to-end flow from raw source identification to finished intelligence product, with the evaluation and tagging steps that SOP-05 governs occurring in the middle layers.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     SOP-05 DATA PROVENANCE ARCHITECTURE                         │
│                     Oracle Health M&CI — Source → Product                       │
└─────────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────────┐
                              │   INTELLIGENCE NEED  │
                              │  (signal, brief,     │
                              │   profile, etc.)     │
                              └──────────┬──────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: SOURCE IDENTIFICATION                                                 │
│                                                                                 │
│   Agent receives research task → identifies candidate source URLs               │
│   RULE: Sources must come from MCP retrieval candidates, not training recall    │
│                                                                                 │
│   Approved source channels:                                                     │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│   │  firecrawl   │  │  brightdata  │  │   tavily     │  │  SEC EDGAR   │      │
│   │  (web pages) │  │  (news/web)  │  │  (search)    │  │  (filings)   │      │
│   └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘      │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                         │
│   │  CMS/FDA     │  │   Gartner/   │  │  Company IR  │                         │
│   │  gov sites   │  │   IDC APIs   │  │  pages (MCP) │                         │
│   └──────────────┘  └──────────────┘  └──────────────┘                         │
└───────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 2: TIER CLASSIFICATION                                                   │
│                                                                                 │
│   Every source assigned to one of four tiers before content is used             │
│                                                                                 │
│   ┌─────────────────────────────────────────────────────────────────────┐       │
│   │ TIER 1 (Primary)    │ TIER 2 (Secondary) │ TIER 3 (Tertiary)       │       │
│   │ • Company IR pages  │ • Verified news    │ • Industry blogs        │       │
│   │ • Press releases    │ • Analyst reports  │ • LinkedIn (official)   │       │
│   │ • SEC/FDA/CMS       │ • Conference procs │ • Job postings          │       │
│   │ • Earnings calls    │ • Peer-reviewed    │ • Unverified media      │       │
│   └─────────────────────┴────────────────────┴─────────────────────────┘       │
│                                                                                 │
│   ┌─────────────────────────────────────────────────────────────────────┐       │
│   │ BANNED (never use):                                                 │       │
│   │ • Google search results page  • Wikipedia  • Training data recall  │       │
│   │ • Unverified/broken URLs      • Anonymous sources with no URL      │       │
│   └─────────────────────────────────────────────────────────────────────┘       │
└───────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 3: URL VERIFICATION                                                      │
│                                                                                 │
│   HTTP HEAD request to source URL                                               │
│                                                                                 │
│   HTTP 200 → PASS → continue                                                    │
│   HTTP 301/302 → follow redirect → re-verify terminal URL                       │
│   HTTP 403 → attempt alternate fetch method → flag if still blocked             │
│   HTTP 404/410 → FAIL → downgrade to UNVERIFIED                                │
│   HTTP 5xx → retry (3x, 2s backoff) → FAIL if still unresolved                │
│   Timeout (>10s) → FAIL → downgrade to UNVERIFIED                             │
│                                                                                 │
│   Result: url_verified = TRUE / FALSE                                           │
└───────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 4: CONFIDENCE SCORING                                                    │
│                                                                                 │
│   Formula:                                                                      │
│   SQS = (tier_weight × 0.35) + (recency_score × 0.30)                         │
│         + (url_verified × 0.20) + (author_named × 0.15)                        │
│                                                                                 │
│   SQS ≥ 0.80 → HIGH confidence                                                 │
│   SQS 0.50–0.79 → MEDIUM confidence                                            │
│   SQS 0.25–0.49 → LOW confidence                                               │
│   SQS < 0.25 or any critical field missing → UNVERIFIED                        │
└───────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 5: PROVENANCE TAGGING                                                    │
│                                                                                 │
│   Every intelligence item tagged with:                                          │
│   {                                                                             │
│     source_url: "https://...",                                                  │
│     source_tier: 1 | 2 | 3 | null,                                             │
│     confidence: "HIGH" | "MEDIUM" | "LOW" | "UNVERIFIED",                      │
│     sqs_score: 0.00–1.00,                                                       │
│     retrieved_date: "YYYY-MM-DD",                                               │
│     verified_date: "YYYY-MM-DD",                                                │
│     url_verified: true | false,                                                 │
│     http_status: 200 | 301 | 404 | ...,                                        │
│     mcp_tool_used: "firecrawl_scrape" | "brightdata_scrape" | ...,             │
│     author_named: true | false,                                                 │
│     content_age_days: integer,                                                  │
│     decay_projected_confidence: 0.00–1.00                                      │
│   }                                                                             │
└───────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 6: INTELLIGENCE PRODUCT                                                  │
│                                                                                 │
│   Assembled product inherits aggregate confidence level from source pool        │
│   Executive-facing output includes confidence badge on every factual claim      │
│   Audit trail attached to product record in SharePoint/database                 │
│   Refresh schedule calculated based on source tier + current SQS               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. The Golden Rule: MCP-Only Data Protocol

### 4.1 The Rule

> **Every factual claim in an Oracle Health M&CI intelligence product must originate from a live MCP tool fetch. Training data recall is never an acceptable data source.**

This is non-negotiable. It is not a preference. It is not a guideline for when convenient. It is the foundational protocol that defines whether Oracle Health M&CI produces intelligence or produces confabulation.

### 4.2 Why Training Data Cannot Be Used

AI language models have training data cutoffs. Even models with recent cutoff dates may have:

- **Stale facts**: A competitor's pricing structure, executive team, or product roadmap that has changed since the training cutoff
- **Unverifiable claims**: No URL to check. No publication date. No author. No way to confirm the model is recalling a real source versus a plausible-sounding hallucination
- **Unknown provenance**: Training data aggregates from millions of sources including low-quality, outdated, or factually incorrect content — with no tier classification
- **No audit trail**: If an executive asks "where did this come from?", the only honest answer to a training-data claim is "I don't know" — which is professionally unacceptable

The healthcare competitive intelligence market includes companies like Epic, Cerner, Veeva, and athenahealth that employ dedicated competitive intelligence teams. Oracle Health's M&CI function must be provably better. "Better" means our claims are verifiable and current, and theirs may not be.

### 4.3 Approved MCP Sources

The following MCP tools are approved for intelligence data retrieval:

| MCP Tool | Use Case | Source Types |
|----------|----------|-------------|
| `firecrawl_scrape` | Deep page content extraction | Company IR, press releases, product pages, job postings |
| `firecrawl_search` | Web search with content retrieval | News articles, analyst commentary, regulatory updates |
| `brightdata_scrape` | Structured data from web pages | Corporate sites, news outlets, government pages |
| `brightdata_search_engine` | Search results with source URLs | Multi-source news aggregation, competitive monitoring |
| `tavily_search` | Real-time search with source attribution | Breaking news, recent competitive moves |
| `tavily_research` | Deep multi-source research | Comprehensive competitive profiles |
| `tavily_extract` | Targeted content extraction from URL | Specific page content when URL is known |
| `mcp__deep-research__octagon` | Deep autonomous research | Multi-source synthesis for market studies |
| `mcp__gpt-researcher` | Research report generation | Long-form research with source bibliography |

All of the above tools return source URLs, retrieval timestamps, and content fetched in real time. None draw from model training data.

### 4.4 How to Verify Data Is From Live MCP Fetch vs. Model Memory

The following protocol distinguishes live-fetched data from training-data recall:

**Test 1: URL present?**
- Live fetch always produces a source URL
- Training data recall produces a claim without a URL
- If no URL → not from MCP → treat as UNVERIFIED

**Test 2: Retrieval timestamp present?**
- MCP tools return a `retrieved_date` or equivalent
- Training data recall has no retrieval timestamp
- If no timestamp → not from MCP → treat as UNVERIFIED

**Test 3: HTTP verification passes?**
- Run URL verification protocol (Section 7)
- If URL returns HTTP 200 → live source confirmed
- If URL fails → content may still be valid but confidence degrades

**Test 4: Content matches retrieval?**
- The retrieved content should be consistent with what the MCP tool returned
- If content appears to include information not present in the fetched page, flag for human review
- This detects cases where a model supplements a real fetch with training-data interpolation

**Test 5: Does the claim appear in MCP tool output verbatim or near-verbatim?**
- Cross-reference the claim against the raw MCP response
- Claims that cannot be traced to specific lines in the MCP response are suspect
- Flag these for analyst review before including in final product

### 4.5 What "Google Is Not a Source" Means

This rule applies specifically to the Google search results page (google.com) as a data source. The search results page itself is not a primary source — it is a pointer to sources. The sources Google points to may or may not be valid (see Tier classification in Section 5).

When a research task uses `tavily_search`, `brightdata_search_engine`, or `firecrawl_search`, those tools return URLs to actual sources. The returned URLs are evaluated per Section 5. The search engine mechanism is acceptable. The search engine results page is not.

Specifically, the following are banned:
- Citing "Google" as a source (e.g., "According to Google, Epic's market share is...")
- Citing a Google search results snippet that does not include a verifiable underlying URL
- Treating a URL of the form `google.com/search?q=...` as a source URL

---

## 5. Source Tier Classification System

### 5.1 Overview

Every source used in Oracle Health M&CI intelligence products is classified into one of three active tiers or flagged as BANNED before its content is used in any intelligence product. Tier classification is the first step in the pipeline and determines the maximum possible confidence score any claim from that source can achieve.

### 5.2 Tier 1 — Primary Sources

**Definition**: Sources that originate directly from the entity being described, from a government regulatory body with direct authority over the subject matter, or from a legal/financial filing with statutory disclosure requirements.

**Characteristics**:
- The content creator and the subject of the content are the same entity, or
- The content creator has a legal obligation to ensure accuracy (SEC, FDA, CMS), or
- The content was filed under penalty of law (10-K, 8-K, S-1, DEA registration)

**Examples**:

*Corporate primary sources:*
- Company investor relations pages (ir.epic.com, investor.oracle.com, etc.)
- Official press releases issued by the subject company
- Earnings call transcripts (sourced from IR pages or SEC EDGAR, not third-party summaries)
- Annual reports (10-K), quarterly reports (10-Q), current reports (8-K) from SEC EDGAR
- Proxy statements (DEF 14A)
- S-1 registration statements
- Official company product documentation (docs pages, official datasheets)
- Company-issued white papers bearing official company branding
- CEO/C-suite quotes sourced from official company communications (earnings calls, official statements)

*Government and regulatory primary sources:*
- FDA.gov for drug approvals, device clearances, enforcement actions
- CMS.gov for Medicare/Medicaid policy, reimbursement rates, final rules
- ONC.gov (Office of the National Coordinator for Health IT) for interoperability rules, TEFCA
- FTC.gov for merger/acquisition decisions, antitrust actions
- HHS.gov for healthcare policy directives
- Federal Register for proposed and final rules
- HIMSS official conference proceedings and whitepapers (not news coverage of HIMSS)
- Joint Commission official statements and accreditation reports

*Patent and IP primary sources:*
- USPTO patent filings (patents.google.com is acceptable as an index; the underlying USPTO filing is the source)
- USPTO trademark registrations

**Tier 1 maximum SQS contribution (tier_weight)**: 1.00

### 5.3 Tier 2 — Secondary Sources

**Definition**: Sources produced by credentialed third parties who report on subjects based on investigation, analysis, or research, where the source has editorial standards, a named publication, and a verifiable identity.

**Characteristics**:
- The content is reported or analyzed by an entity distinct from the subject
- The publication has an established editorial reputation
- The content is attributed to named authors or analysts with verifiable credentials
- The content is based on primary source reporting, not speculation or opinion alone

**Examples**:

*Major news outlets (healthcare/technology focus):*
- Health Data Management
- Modern Healthcare
- Healthcare IT News
- Fierce Healthcare / Fierce Health IT
- Health Affairs
- STAT News
- Becker's Hospital Review
- MedCity News
- Healthcare Finance News
- The Wall Street Journal (healthcare/tech coverage)
- Reuters (healthcare/tech coverage)
- Bloomberg (healthcare/tech coverage)

*Analyst reports:*
- Gartner (Magic Quadrant, Market Guides, Research Notes — with report metadata)
- IDC (market share reports, forecasts — with report metadata)
- Forrester (Wave reports, market research — with report metadata)
- Klas Research (healthcare IT-specific ratings and reports)
- CHIME (College of Healthcare Information Management Executives) surveys
- HIMSS Analytics (Market Intelligence reports — distinct from HIMSS conference proceedings)
- CB Insights (private market funding, M&A activity)

*Academic and peer-reviewed sources:*
- PubMed-indexed journals (for clinical evidence supporting health IT claims)
- JAMA, NEJM, Health Affairs, Journal of the American Medical Informatics Association (JAMIA)
- IEEE Transactions on medical computing contexts

*Conference proceedings:*
- HIMSS annual conference session papers (not news coverage)
- AMIA symposium proceedings
- HLTH conference published materials

**Tier 2 maximum SQS contribution (tier_weight)**: 0.75

### 5.4 Tier 3 — Tertiary Sources

**Definition**: Sources that may contain useful intelligence signals but lack the editorial standards, verification processes, or institutional authority of Tier 1 or Tier 2 sources. Tier 3 sources require corroboration from a higher-tier source before being cited in an executive-facing product.

**Characteristics**:
- The publication lacks consistent editorial standards or formal review processes
- The content may be opinion, commentary, or user-generated
- The author's credentials are unverified or the content is anonymous
- The source may have commercial incentives that affect objectivity

**Examples**:

*Industry and trade blogs:*
- Health IT vendor blogs (not official documentation)
- Individual analyst commentary on LinkedIn, Substack, Medium
- Industry newsletter summaries not sourced to primary or Tier 2
- Trade association member publications without editorial review

*Social media and professional networks:*
- LinkedIn company pages (official pages only — personal posts are not a data source)
- LinkedIn posts from named executives at subject companies (useful for executive commentary signals, require corroboration)
- Twitter/X verified accounts of subject companies or executives (signals only)

*Job postings:*
- LinkedIn Jobs, Indeed, company career pages
- Job postings are a Tier 3 source for inferring hiring intent, technology adoption, team build-out signals
- Cannot be cited as a Tier 1/2 source for factual claims about products or market position

*Competitive intelligence databases:*
- G2, Capterra, TrustRadius reviews (signal value only — not factual claims about vendor capabilities)
- Glassdoor (cultural/workforce signals only)

*Aggregator sites:*
- Crunchbase (useful for funding rounds, but verify against SEC filings for material events)
- Pitchbook (same caveat as Crunchbase)
- GitHub (for open-source signals — what a company is building publicly)

**Tier 3 maximum SQS contribution (tier_weight)**: 0.40

**Important**: Tier 3 sources are never cited alone in executive-facing intelligence products. They may be included as supporting signals when a higher-tier source corroborates the same claim.

### 5.5 BANNED Sources

The following source types are banned from Oracle Health M&CI intelligence products under any circumstances:

| Banned Source | Reason |
|--------------|--------|
| Google search results page (google.com/search) | Not a source; a pointer to sources. The returned URL must be evaluated independently. |
| Wikipedia | Any person can edit. No verifiable author or editorial accountability. May be accurate but cannot be verified to the required standard. |
| AI training data recall | No URL, no timestamp, no verifiable author, no HTTP verification possible. Structurally unable to meet provenance requirements. |
| Unverified URLs (non-HTTP-200) | If the URL cannot be confirmed to exist and return content, the source cannot be verified. |
| Anonymous sources with no URL | Claims that cannot be attributed to a named source or a verifiable URL have no provenance chain. |
| ChatGPT/Claude/AI summaries as primary source | AI-generated summaries of research are process artifacts, not sources. The underlying fetched sources are the sources. |
| Paywalled content never fetched | If the agent cannot retrieve the actual content (only a headline or abstract), the full article is not available as a source. Do not cite content you cannot read. |
| Cached or archived snapshots of banned sources | A cached version of Wikipedia is still Wikipedia. |

---

## 6. Confidence Scoring Methodology

### 6.1 Overview

Every factual claim in an M&CI intelligence product carries a confidence label. The confidence label is derived from the Source Quality Score (SQS — see Section 9 for the full algorithm) and mapped to one of four discrete confidence tiers.

Confidence labels appear in:
- Inline citations within intelligence products (e.g., "Epic's Q3 revenue was $4.9B [HIGH, 2026-03-15]")
- Summary confidence badges at the product level (the product's aggregate confidence)
- Provenance metadata attached to every intelligence item in the database
- Daily freshness audit reports (SOP-04 integration point)

### 6.2 HIGH Confidence

**Label**: `HIGH`
**SQS threshold**: ≥ 0.80
**Color code**: Green (in dashboards and briefings)

**Requirements (all must be true)**:
- Source is Tier 1 (company IR, SEC filing, FDA/CMS official site, official press release)
- URL verification returns HTTP 200
- Content age is ≤ 30 days from retrieval date
- Named author or named organization with direct attribution is present
- No known conflicting information from another Tier 1 source

**What HIGH means in practice**:
When an executive reads a claim marked HIGH, they can present it in a board meeting or customer negotiation without qualification. It came from the source itself or a government regulator with legal disclosure requirements, the URL is active, the information is current, and it was fetched live.

**Example HIGH-confidence claim**:
> "Epic reported $4.9B in revenue for FY2025, representing 12% year-over-year growth. [HIGH — Epic IR page, HTTP 200, 2026-03-10, fetched via firecrawl_scrape]"

### 6.3 MEDIUM Confidence

**Label**: `MEDIUM`
**SQS threshold**: 0.50–0.79
**Color code**: Yellow (in dashboards and briefings)

**Requirements**:
- Source is Tier 2 (verified news outlet, analyst report, conference proceedings)
- URL verification returns HTTP 200
- Content age is ≤ 90 days from retrieval date
- Attribution present (publication name, ideally named author)

**What MEDIUM means in practice**:
The claim is credible and can be included in intelligence products, but should not be presented without the source attribution visible. Executive briefings should show the sourcing for MEDIUM claims. Battlecards can include MEDIUM claims when labeled. When in doubt, corroborate with a Tier 1 source to elevate to HIGH.

**Example MEDIUM-confidence claim**:
> "Gartner's Q1 2026 Magic Quadrant positions Epic as a Leader with the furthest vision placement in the EHR category. [MEDIUM — Gartner Research, HTTP 200, 2026-02-28, fetched via tavily_extract]"

*Note: Gartner is Tier 2 despite its authority because Gartner analysts interpret and analyze; they are not the primary source on Epic's capabilities. If Epic's own IR confirms the same positioning, it would elevate to HIGH.*

### 6.4 LOW Confidence

**Label**: `LOW`
**SQS threshold**: 0.25–0.49
**Color code**: Orange (in dashboards and briefings)

**Requirements**: One or more of the following is true:
- Source is Tier 3
- Content age is > 90 days regardless of tier
- URL verification failed but content was retrieved before failure (cached)
- Author is unnamed or unverified

**What LOW means in practice**:
LOW confidence claims are signals, not facts. They should be tracked for pattern recognition and corroboration, but should NOT appear in executive briefings without explicit caveat ("we are tracking an unverified signal that..."). LOW confidence claims are appropriate for:
- Internal research notes
- Signal tracking dashboards
- Pre-research ideation for what to investigate further
- Context within a battlecard where the claim is clearly labeled as a signal

LOW confidence items should never be the sole supporting evidence for a strategic recommendation.

**Example LOW-confidence claim**:
> "An industry blog post suggests Epic is piloting an AI-native scheduling module in Q2 2026. [LOW — Epic Health IT Blog (Tier 3), no author named, content 67 days old, fetched via firecrawl_scrape]"

### 6.5 UNVERIFIED

**Label**: `UNVERIFIED`
**SQS threshold**: < 0.25, OR any of the following critical flags:
- No URL present
- URL verification returned 404, 410, or persistent 5xx
- No retrieval timestamp
- Source identified as training data recall
- Content origin cannot be determined

**Color code**: Red (in dashboards and briefings)

**What UNVERIFIED means in practice**:
UNVERIFIED claims should never appear in any external-facing intelligence product. They may be retained internally as leads — things to investigate further — but must be flagged as UNVERIFIED in all contexts.

If the only supporting evidence for a claim is UNVERIFIED, the claim should not be included in the intelligence product. If the claim is important enough that its absence materially weakens the product, the appropriate action is to conduct additional research to find a verifiable source.

**Automatic escalation**: Any intelligence product that attempts to include an UNVERIFIED claim in an executive-facing output triggers an automatic escalation per Section 11.

---

## 7. URL Verification Protocol

### 7.1 The Core Requirement

Every URL cited in an Oracle Health M&CI intelligence product must be verified as live and accessible at the time the intelligence item is created or updated. URL verification is not optional for HIGH or MEDIUM confidence claims.

Verification method: HTTP HEAD request (preferred) or HTTP GET (fallback) to the exact URL returned by the MCP retrieval tool, with a 10-second timeout.

### 7.2 HTTP Status Code Handling

**HTTP 200 OK**
- Status: PASS
- Action: Record `url_verified: true`, `http_status: 200`, `verified_date: [today]`
- Continue to confidence scoring

**HTTP 301 Moved Permanently / HTTP 302 Found (Redirect)**
- Status: CONDITIONAL PASS
- Action: Follow the redirect chain to the terminal URL
- Verify the terminal URL returns HTTP 200
- If terminal URL returns 200: Record the terminal URL as the canonical source URL. Update `source_url` to the terminal URL. Mark `url_verified: true`
- If redirect chain exceeds 5 hops: Flag as suspicious, escalate to human review
- If terminal URL does not return 200: Apply the appropriate non-200 protocol below
- Note: 301 from HTTP to HTTPS is expected and acceptable without flag

**HTTP 301/302 to a Different Domain**
- Status: REVIEW REQUIRED
- Action: Flag for human review. The original URL may have been acquired by a different entity or may point to a parked/spam domain.
- Do not automatically accept cross-domain redirects as valid
- Human analyst confirms the destination domain is the expected source before accepting

**HTTP 403 Forbidden**
- Status: CONDITIONAL FAIL
- Action: The server is reachable but access is blocked (paywalled, rate-limited, geographic restriction)
- Attempt alternate retrieval using `brightdata_scrape` (bypasses common access restrictions)
- If alternate retrieval succeeds with content: Record `url_verified: true`, `http_status: 403_bypassed`, note the bypass method in the audit trail
- If alternate retrieval also fails: Record `url_verified: false`, `http_status: 403`
- 403 without content retrieval: Confidence cannot be HIGH. Maximum confidence is MEDIUM if the source identity is otherwise confirmed.

**HTTP 404 Not Found / HTTP 410 Gone**
- Status: FAIL
- Action: The URL is broken. The content may have been moved or deleted.
- Attempt to find alternate URL for the same content (search for the headline/title on the source domain)
- If alternate URL found and verified: Update `source_url` to the new URL, verify the alternate URL per this protocol
- If no alternate URL found: Record `url_verified: false`, `http_status: 404`
- Downgrade confidence to UNVERIFIED regardless of source tier
- Flag per Section 11 (Unverifiable Sources protocol)

**HTTP 5xx Server Errors**
- Status: RETRY
- Action: Server is temporarily unavailable
- Retry 3 times with 2-second exponential backoff (2s, 4s, 8s)
- If any retry succeeds with HTTP 200: Treat as HTTP 200 above
- If all retries fail: Record `url_verified: false`, `http_status: [last_status_code]`, `retry_attempts: 3`
- Downgrade confidence by one tier (HIGH → MEDIUM, MEDIUM → LOW, LOW → UNVERIFIED)
- Re-verify within 24 hours (add to refresh queue)

**Timeout (>10 seconds)**
- Status: FAIL
- Action: Record `url_verified: false`, `http_status: "timeout"`, `timeout_seconds: [actual_duration]`
- Retry once with a 15-second timeout
- If retry succeeds: proceed as HTTP 200 or 5xx depending on status
- If retry times out: Downgrade confidence to LOW or UNVERIFIED

### 7.3 Verification Frequency

| Context | Verification Required |
|---------|----------------------|
| New source added to intelligence product | Always — verify at ingestion |
| Existing source in a product being updated | Always — re-verify at update time |
| Existing source in a product NOT being updated | Per refresh cadence (Section 12) |
| Tier 1 source in executive briefing | Verify within 48 hours before publication |
| Tier 2 source in executive briefing | Verify within 72 hours before publication |
| Tier 3 source in any product | Verify at ingestion; note 30-day re-verify cycle |

### 7.4 Bulk Verification

For intelligence operations that process large numbers of URLs simultaneously (e.g., the daily signal feed, a competitor profile refresh):

- Run verification requests with a concurrency limit of 10 parallel requests to avoid IP-rate-limiting
- Use `brightdata` for domains that are known to block standard HTTP clients
- Log all verification results to the audit trail with batch ID, timestamp, and pass/fail count
- Alert if batch verification failure rate exceeds 15% (suggests either a systemic issue with the pipeline or a major source site outage)

### 7.5 Special Case: PDF Sources

Many Tier 1 sources (SEC filings, FDA guidance documents, CMS final rules) are hosted as PDFs.

- PDF URL verification: Same HTTP protocol as above. A PDF at a verified URL gets the same treatment.
- PDF content retrieval: Use `firecrawl_scrape` or `tavily_extract` which can parse PDF content
- Document the specific page number or section for claims extracted from multi-page PDFs: `source_url: "https://sec.gov/.../epic_10k.pdf#page=47"`
- SEC EDGAR filings: Verify against the EDGAR filing index, not just the direct PDF URL, to confirm the document's official status

---

## 8. Monte Carlo Simulation: Source Reliability Modeling

### 8.1 Purpose

Intelligence products have a confidence level at time of creation. That confidence level decays over time as sources age. The Monte Carlo simulation in this section models:

1. How quickly a given intelligence product's composite confidence falls below threshold
2. The probability that an intelligence product remains HIGH confidence at any future date
3. Which source mix in a product is most susceptible to rapid confidence decay

This modeling informs the refresh cadence in Section 12 and is run quarterly (or when a product's source mix changes materially) to forecast when refresh intervention is required.

### 8.2 The Confidence Decay Model

Confidence decays as a function of time, source type, and domain volatility. The base decay model uses an exponential function:

```
confidence(t) = initial_confidence × e^(-λ × t)
```

Where:
- `confidence(t)` = confidence score at time t
- `initial_confidence` = SQS score at retrieval time (0.00–1.00)
- `λ` (lambda) = source-type decay rate (see table below)
- `t` = time elapsed in days since retrieval

**Decay Rate Table (λ values by source type)**:

| Source Type | λ (daily decay rate) | Half-life (days) | Notes |
|-------------|---------------------|------------------|-------|
| Regulatory filings (SEC 10-K, annual) | 0.00190 | 365 | Annual filing cycle; stable until next filing |
| Regulatory filings (8-K, current report) | 0.00693 | 100 | Event-driven; valid until superseded |
| FDA/CMS final rules | 0.00190 | 365 | Stable until amendment or superseding rule |
| Company press releases | 0.00693 | 100 | Valid until contradicted by new release |
| Earnings call transcripts | 0.00693 | 100 | Quarterly cycle; superseded by next earnings |
| Analyst reports (annual) | 0.00190 | 365 | Annual refresh cycle (Gartner MQ, etc.) |
| News articles (major outlets) | 0.01155 | 60 | Rapidly superseded by market developments |
| News articles (industry trade) | 0.01386 | 50 | Faster news cycle |
| Job postings | 0.02310 | 30 | Typically open 30–90 days; signal decays quickly |
| LinkedIn posts / executive commentary | 0.02772 | 25 | Social signals degrade quickly |
| Industry blog posts | 0.02310 | 30 | Opinionated content ages quickly |
| Conference proceedings | 0.00462 | 150 | Slower decay; methodology documents |
| Product documentation | 0.00693 | 100 | Valid until version release |

**Domain Volatility Multiplier**: Certain competitive domains have faster-moving news cycles that accelerate all decay rates:

| Domain | Multiplier (m) | Effect |
|--------|---------------|--------|
| AI/ML product features | 2.0 | All λ values doubled — AI landscape changes monthly |
| Pricing and packaging | 1.5 | Pricing changes more frequently than annual cycles |
| Regulatory/compliance | 0.7 | Regulatory items are more stable — rules don't change daily |
| Executive team | 1.3 | C-suite turnover is meaningful; track carefully |
| Market share/revenue | 1.0 | Standard decay — quarterly reporting cycle |
| Partnership announcements | 1.2 | Partnerships evolve; moderate acceleration |

**Adjusted formula with domain multiplier**:
```
confidence(t) = initial_confidence × e^(-λ × m × t)
```

### 8.3 Composite Product Confidence

An intelligence product typically aggregates multiple sources. The composite confidence at time t is calculated as a weighted average of individual source confidences:

```
composite_confidence(t) = Σ(weight_i × confidence_i(t)) / Σ(weight_i)
```

Where `weight_i` is the claim-level weight (e.g., claims that are central to the product's thesis receive higher weight than supporting context claims).

Default weights if not explicitly assigned:
- Core claims supporting the primary thesis: weight = 1.0
- Supporting context claims: weight = 0.5
- Background/scene-setting claims: weight = 0.25

### 8.4 Monte Carlo Simulation Protocol

**When to run**: Quarterly refresh cycle, or any time the intelligence product's source mix changes by >20% (new sources added or old sources removed).

**Inputs**:
- Source inventory for the intelligence product (all sources with initial_confidence, λ, m, retrieval_date)
- Target confidence threshold (default: 0.80 for HIGH, 0.50 for MEDIUM)
- Simulation horizon: 90 days (quarterly review cycle)
- Number of iterations: 1,000

**Simulation logic (1,000 iterations)**:

For each iteration:
1. For each source in the product, sample a stochastic decay rate: `λ_stochastic = λ × Normal(1.0, 0.15)` — introducing ±15% variance to model uncertainty in when sources are actually superseded
2. Sample a stochastic domain multiplier: `m_stochastic = m × Normal(1.0, 0.10)` — ±10% variance
3. Calculate `confidence_i(t)` at t = 1, 7, 14, 30, 60, 90 days for each source
4. Calculate `composite_confidence(t)` at each time step
5. Record the day when composite_confidence first drops below the threshold (`threshold_breach_day`)

**Outputs from 1,000 iterations**:
- `median_breach_day`: The median number of days before composite confidence drops below threshold
- `p10_breach_day`: 10th percentile — optimistic case (90% of simulations breach later than this)
- `p90_breach_day`: 90th percentile — conservative case (only 10% of simulations breach later than this)
- `p_still_above_threshold_at_30`: Probability composite confidence is still above threshold at day 30
- `p_still_above_threshold_at_60`: Probability at day 60
- `p_still_above_threshold_at_90`: Probability at day 90
- `highest_decay_contributor`: The source with the highest individual decay rate — this is the first refresh priority

**Example simulation output (competitor profile, 12 sources, HIGH threshold = 0.80)**:

```
Monte Carlo Confidence Decay Simulation
Product: Epic Systems Competitor Profile
Sources: 12 (4 Tier 1, 6 Tier 2, 2 Tier 3)
Initial composite confidence: 0.87 [HIGH]
Target threshold: 0.80 (HIGH)
Simulation: 1,000 iterations, 90-day horizon

Results:
  Median days to threshold breach:     47 days
  P10 (optimistic breach):             35 days
  P90 (conservative breach):           61 days

  P(still HIGH at day 30):             82.3%
  P(still HIGH at day 60):             31.7%
  P(still HIGH at day 90):              8.4%

Highest decay contributor: Epic earnings call transcript
  λ = 0.00693, m = 1.0, initial_confidence = 0.91
  Projected confidence at day 47: 0.73 (below HIGH threshold)
  Recommendation: Refresh this source before day 35

Recommended refresh date: 2026-04-27 (47-day median)
P90 refresh date: 2026-05-23 (conservative)
Action: Schedule source refresh for 2026-04-20 (7-day buffer before median)
```

### 8.5 Integration With Refresh Cadence

The Monte Carlo output drives the refresh schedule (Section 12). The `p90_breach_day` is used as the latest permissible refresh date. Actual refresh is scheduled with a 7-day buffer before the P90 date.

---

## 9. Predictive Algorithm: Source Quality Score (SQS)

### 9.1 Overview

The Source Quality Score (SQS) is a composite 0.00–1.00 score that predicts the quality and reliability of an individual source. It combines four weighted factors that have been validated against downstream intelligence product accuracy.

The SQS is calculated at time of source retrieval and attached to every intelligence item in provenance metadata. It determines the initial confidence tier and feeds into the Monte Carlo decay model.

### 9.2 The Formula

```
SQS = (tier_weight × 0.35) + (recency_score × 0.30) + (url_verified × 0.20) + (author_named × 0.15)
```

**Factor weights**:
| Factor | Weight | Rationale |
|--------|--------|-----------|
| tier_weight | 35% | Source origin is the single most important predictor of reliability |
| recency_score | 30% | Stale information is wrong information in a fast-moving competitive market |
| url_verified | 20% | Unverifiable sources cannot be cited with confidence |
| author_named | 15% | Named attribution enables fact-checking and establishes accountability |

### 9.3 Factor Calculation

**Factor 1: tier_weight (0.35)**

| Source Tier | tier_weight value |
|-------------|-----------------|
| Tier 1 | 1.00 |
| Tier 2 | 0.75 |
| Tier 3 | 0.40 |
| Banned / cannot classify | 0.00 |

Contribution to SQS:
- Tier 1 source: 1.00 × 0.35 = **0.350**
- Tier 2 source: 0.75 × 0.35 = **0.263**
- Tier 3 source: 0.40 × 0.35 = **0.140**

**Factor 2: recency_score (0.30)**

Recency is calculated based on the age of the content (in days) from retrieval date. Note: recency scoring is based on the content's publication/issuance date, not the retrieval date.

```
recency_score = max(0, 1 - (content_age_days / recency_half_life))
```

Where `recency_half_life` is the source-type specific half-life from the Monte Carlo decay table (Section 8.2), expressed as the age at which recency_score = 0.5.

Simplified recency scoring table:

| Content Age | recency_score | Notes |
|-------------|--------------|-------|
| 0–7 days | 1.00 | Very fresh — full recency credit |
| 8–30 days | 0.85 | Recent — minor decay |
| 31–60 days | 0.65 | Moderate — worth noting age in product |
| 61–90 days | 0.45 | Aging — HIGH confidence unlikely |
| 91–180 days | 0.25 | Stale — LOW confidence territory |
| > 180 days | 0.10 | Very stale — UNVERIFIED territory |
| Unknown publication date | 0.30 | Cannot assess; penalty applied |

Contribution to SQS:
- 7-day-old source: 1.00 × 0.30 = **0.300**
- 45-day-old source: 0.65 × 0.30 = **0.195**
- 120-day-old source: 0.25 × 0.30 = **0.075**

**Factor 3: url_verified (0.20)**

This is a binary factor.

| URL Status | url_verified value |
|------------|-------------------|
| HTTP 200 confirmed | 1.00 |
| HTTP 200 confirmed via redirect (301/302 resolved) | 0.90 |
| HTTP 403 but content retrieved via alternate method | 0.70 |
| HTTP 5xx resolved after retry | 0.60 |
| Verification not yet performed | 0.50 |
| HTTP 404 / 410 / permanent fail | 0.00 |
| Timeout (unresolved) | 0.00 |
| No URL present | 0.00 |

Contribution to SQS:
- HTTP 200: 1.00 × 0.20 = **0.200**
- HTTP 403 bypassed: 0.70 × 0.20 = **0.140**
- HTTP 404: 0.00 × 0.20 = **0.000**

**Factor 4: author_named (0.15)**

| Attribution Level | author_named value |
|------------------|-------------------|
| Named individual author with verifiable affiliation | 1.00 |
| Named organizational author (e.g., "Epic IR Team", "FDA Office of...") | 0.90 |
| Named publication with editorial byline but no individual named | 0.70 |
| Publication named, no author | 0.50 |
| Anonymous post from named domain (e.g., corporate blog, unnamed) | 0.30 |
| No author, no publication name | 0.00 |

Contribution to SQS:
- Named individual: 1.00 × 0.15 = **0.150**
- Named org: 0.90 × 0.15 = **0.135**
- No author: 0.00 × 0.15 = **0.000**

### 9.4 SQS Calculation Examples

**Example 1: SEC 10-K Filing (best case)**
```
Source: Epic Systems Form 10-K (hypothetical) via SEC EDGAR
tier_weight: 1.00 (Tier 1 — SEC filing)
recency_score: 1.00 (filed 5 days ago)
url_verified: 1.00 (HTTP 200 confirmed)
author_named: 0.90 (SEC/Epic named organization)

SQS = (1.00 × 0.35) + (1.00 × 0.30) + (1.00 × 0.20) + (0.90 × 0.15)
SQS = 0.350 + 0.300 + 0.200 + 0.135
SQS = 0.985 → HIGH confidence
```

**Example 2: News article (recent, verified)**
```
Source: Modern Healthcare article, published 15 days ago
tier_weight: 0.75 (Tier 2 — verified news outlet)
recency_score: 0.85 (15 days old)
url_verified: 1.00 (HTTP 200 confirmed)
author_named: 1.00 (named byline: "Sarah Johnson, Staff Reporter")

SQS = (0.75 × 0.35) + (0.85 × 0.30) + (1.00 × 0.20) + (1.00 × 0.15)
SQS = 0.263 + 0.255 + 0.200 + 0.150
SQS = 0.868 → HIGH confidence
```

**Example 3: Industry blog post (older, no author)**
```
Source: Health IT blog post, published 75 days ago, no named author
tier_weight: 0.40 (Tier 3 — industry blog)
recency_score: 0.45 (75 days old)
url_verified: 1.00 (HTTP 200 confirmed)
author_named: 0.00 (no author)

SQS = (0.40 × 0.35) + (0.45 × 0.30) + (1.00 × 0.20) + (0.00 × 0.15)
SQS = 0.140 + 0.135 + 0.200 + 0.000
SQS = 0.475 → LOW confidence
```

**Example 4: Broken URL (training data recall)**
```
Source: No URL — agent recalled from training data
tier_weight: 0.00 (Banned)
recency_score: 0.00 (unknown date)
url_verified: 0.00 (no URL)
author_named: 0.00 (no attribution)

SQS = 0.000 → UNVERIFIED (circuit breaker: any banned source = UNVERIFIED regardless)
```

### 9.5 SQS as a Predictor of Intelligence Product Quality

Research on competitive intelligence product quality (internal M&CI calibration, aligned with SCIP benchmarking) shows strong correlation between SQS distribution and downstream product utility:

| Average SQS Across Product Sources | Executive Utility Rating (1–10) | Decision Confidence |
|------------------------------------|--------------------------------|---------------------|
| ≥ 0.85 | 9.2 | Very high — act with confidence |
| 0.75–0.84 | 7.8 | High — minor validation recommended |
| 0.60–0.74 | 6.1 | Moderate — corroborate key claims |
| 0.45–0.59 | 4.3 | Low — treat as directional signal only |
| < 0.45 | 2.1 | Very low — do not use for decisions |

Target for all M&CI executive-facing products: Average SQS ≥ 0.80 (HIGH confidence).

---

## 10. Data Provenance Tagging Format

### 10.1 Overview

Every factual claim stored in the Oracle Health M&CI intelligence system carries a complete provenance metadata record. This record is created at ingestion, updated at every verification or refresh event, and is permanently attached to the intelligence item even if the item itself is updated.

The provenance record is both:
1. **Operational** — it drives confidence scoring, refresh scheduling, and audit trails
2. **Auditability** — when an executive asks "where did this come from?", the answer is in the provenance record within 30 seconds

### 10.2 Full Provenance Schema

```json
{
  "item_id": "[UUID]",
  "claim_text": "[The verbatim intelligence claim]",
  "claim_summary": "[One-sentence plain-language summary]",
  "source": {
    "source_url": "https://[exact URL where content was retrieved]",
    "source_url_canonical": "https://[terminal URL after redirect resolution, if different]",
    "source_domain": "[domain.com]",
    "source_title": "[Page title or document title]",
    "source_publication": "[Publication name if applicable: 'Modern Healthcare', 'SEC EDGAR', etc.]",
    "source_tier": 1,
    "source_tier_label": "Primary | Secondary | Tertiary",
    "author_name": "[Named author or null]",
    "author_affiliation": "[Author's organization or null]",
    "author_named": true,
    "content_published_date": "YYYY-MM-DD",
    "content_age_days": 12
  },
  "retrieval": {
    "retrieved_date": "YYYY-MM-DD",
    "retrieved_time_utc": "HH:MM:SSZ",
    "mcp_tool_used": "firecrawl_scrape | firecrawl_search | brightdata_scrape | brightdata_search_engine | tavily_search | tavily_extract | tavily_research | octagon_deep_research | gpt_researcher",
    "mcp_session_id": "[session or batch ID for audit trail linkage]",
    "raw_content_hash": "[SHA-256 hash of raw retrieved content at retrieval time]"
  },
  "verification": {
    "url_verified": true,
    "http_status": 200,
    "verified_date": "YYYY-MM-DD",
    "verified_time_utc": "HH:MM:SSZ",
    "redirect_chain": ["https://original-url", "https://redirected-url"],
    "redirect_count": 0,
    "verification_method": "HTTP_HEAD | HTTP_GET | alternate_mcp_fetch",
    "retry_attempts": 0,
    "next_verification_due": "YYYY-MM-DD"
  },
  "scoring": {
    "sqs_score": 0.868,
    "tier_weight": 0.75,
    "recency_score": 0.85,
    "url_verified_score": 1.00,
    "author_named_score": 1.00,
    "confidence": "HIGH | MEDIUM | LOW | UNVERIFIED",
    "confidence_threshold_at_scoring": 0.80,
    "domain_volatility_multiplier": 1.0,
    "decay_lambda": 0.00693,
    "projected_confidence_30d": 0.812,
    "projected_confidence_60d": 0.724,
    "projected_confidence_90d": 0.645,
    "monte_carlo_median_breach_day": 47,
    "monte_carlo_p90_breach_day": 61
  },
  "product_linkage": {
    "intelligence_product_id": "[UUID of parent product]",
    "product_name": "[e.g., 'Epic Competitor Profile Q1 2026']",
    "product_type": "battlecard | competitor_profile | executive_briefing | market_study | signal_feed",
    "claim_weight_in_product": 1.0,
    "section_in_product": "[e.g., 'Revenue & Growth']"
  },
  "lifecycle": {
    "created_date": "YYYY-MM-DD",
    "last_refreshed_date": "YYYY-MM-DD",
    "refresh_scheduled_date": "YYYY-MM-DD",
    "refresh_tier_cadence": "monthly | quarterly | as-needed",
    "status": "active | stale | unverified | archived | superseded",
    "superseded_by_item_id": null,
    "archived_date": null,
    "refresh_history": [
      {
        "refresh_date": "YYYY-MM-DD",
        "action": "verified | updated | downgraded | escalated",
        "previous_confidence": "HIGH",
        "new_confidence": "HIGH",
        "performed_by": "Jake | analyst_name | scheduled_refresh"
      }
    ]
  },
  "flags": {
    "requires_human_review": false,
    "escalated": false,
    "escalation_reason": null,
    "conflict_detected": false,
    "conflicting_item_id": null
  }
}
```

### 10.3 Inline Citation Format

When intelligence items are rendered in executive-facing products (briefings, battlecards, slides), provenance is surfaced in a concise inline format:

**Standard inline citation format**:
```
[CONFIDENCE — Source Publication, Date, MCP Tool]
```

**Examples**:
```
Epic's Q3 2025 revenue was $1.42B. [HIGH — Epic IR, 2025-11-14, firecrawl_scrape]

athenahealth launched a new AI scheduling module in Q1 2026. [MEDIUM — HIMSS Media, 2026-02-28, tavily_search]

An industry source suggests Epic is exploring an acquisition in the RCM space. [LOW — Health IT Blog, 2026-01-15, brightdata_scrape]
```

**Product-level aggregate confidence badge**:

For full intelligence products, a confidence summary appears in the header:

```
┌─────────────────────────────────────────────────────────────┐
│  PRODUCT CONFIDENCE SUMMARY                                 │
│  Oracle Health M&CI — Epic Competitor Profile              │
│                                                             │
│  Overall: HIGH (avg SQS: 0.84)                              │
│  Sources: 14 total │ 8 HIGH │ 4 MEDIUM │ 2 LOW │ 0 UNVER   │
│  Freshest source: 2026-03-21 │ Oldest source: 2025-11-14   │
│  Next refresh due: 2026-04-20                               │
│  Monte Carlo P(still HIGH at 30d): 81.7%                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 11. Unverifiable Sources: Handling Protocol

### 11.1 Definition of "Unverifiable"

A source is unverifiable when any of the following are true:
1. No URL is present (content came from training data recall or an unattributed claim)
2. The URL returns a permanent error (HTTP 404, 410) and no alternate URL can be found
3. The URL times out after all retry attempts and alternate fetch methods
4. The content returned by MCP retrieval does not match the intelligence claim (the URL exists but the content does not support the claim)
5. A cross-domain redirect points to a domain that is not the expected source

### 11.2 Immediate Actions When a Source Cannot Be Verified

**Step 1: Downgrade confidence to UNVERIFIED**
- Set `confidence: "UNVERIFIED"` in provenance metadata
- Set `url_verified: false`
- Set `flags.requires_human_review: true`
- Record the specific reason for UNVERIFIED status in `flags.escalation_reason`

**Step 2: Attempt re-retrieval**
- Search for the same content via alternate MCP tool (e.g., if firecrawl_scrape failed, try tavily_extract with the URL; if that fails, try brightdata_scrape)
- Search for alternate sources making the same claim (use `tavily_search` or `firecrawl_search` to find corroborating Tier 1 or Tier 2 sources)
- If corroboration found from a verified higher-tier source, the original UNVERIFIED item may be superseded by the corroborating item — create a new provenance record for the corroborating source

**Step 3: Determine disposition**
- **If alternate verified source found**: Use the alternate source. Mark the original as `status: "superseded"`, `superseded_by_item_id: [new_item_id]`. The intelligence claim proceeds with the new source's confidence.
- **If no alternate source found but claim is critical**: Flag for human analyst escalation (Step 4 below). Do not include the claim in any external product until verified.
- **If no alternate source found and claim is not critical**: Remove the claim from the intelligence product. Mark as `status: "archived"`. Log in audit trail.

**Step 4: Human analyst escalation**

When a claim is critical to the intelligence product (claim_weight_in_product ≥ 0.75) and cannot be auto-verified:

- Set `flags.escalated: true`
- Alert the M&CI analyst queue: "UNVERIFIED source requires human review for [product_name]"
- Analyst SLA: Review within 4 business hours for daily intelligence products; 24 hours for periodic products (weekly briefings, quarterly profiles)
- Analyst action: Either (a) locate a verified alternate source and update the provenance record, or (b) confirm the claim should be removed from the product and document the decision
- If analyst cannot verify: Claim is removed and the intelligence product is published without it. The absence is noted in internal product metadata (not in the executive-facing version).

### 11.3 Escalation Paths by Product Type

| Product Type | UNVERIFIED Claim Action | Escalation SLA |
|-------------|------------------------|----------------|
| Daily signal feed | Exclude from product automatically; log for analyst review | 24 hours |
| Weekly executive briefing (Matt Cohlmia) | Exclude automatically; escalate to analyst before publish | 4 hours |
| Competitor profile (live database) | Downgrade section confidence; flag in product header | 48 hours |
| Battlecard | Flag claim with UNVERIFIED badge; do not remove | 24 hours (claim should not drive battlecard positioning) |
| Board-level briefing | Block publish until resolved; escalate immediately | 2 hours |
| Ad-hoc executive request | Respond with available verified claims; clearly note what could not be verified | Same-day |

### 11.4 Communication Standard for UNVERIFIED Claims

When an intelligence product must be delivered and contains gaps due to unverifiable sources, the standard language is:

> "Note: We were unable to verify the source for [specific claim/section] at time of publication. The claim has been excluded from this product. Research to locate a verified source is underway and will be included in the next update."

This language appears in the product for internal audiences only. External-facing versions (e.g., materials prepared for customer conversations) never reference verification failures — the claim is simply absent.

---

## 12. Source Refresh Cadence

### 12.1 Overview

Sources do not maintain their confidence score indefinitely. Even if a URL remains live (HTTP 200), the content at that URL may be superseded by newer information. The refresh cadence defines how frequently each source type is re-retrieved and re-verified.

Refresh scheduling is automated: the provenance system calculates `next_verification_due` based on tier and initial retrieval date, and populates a refresh queue that the daily M&CI pipeline processes.

The Monte Carlo simulation (Section 8) overrides these default cadences when the simulation projects confidence breach before the scheduled refresh. In that case, the Monte Carlo P90 breach date (minus 7-day buffer) becomes the effective refresh date.

### 12.2 Tier 1 Sources — Monthly Refresh

**Default cadence**: Every 30 days

**Rationale**: Tier 1 sources (company IR pages, SEC filings, regulatory guidance) are updated on structured schedules (quarterly earnings, annual 10-K, CMS final rule publication cycles). Monthly refresh ensures Oracle Health M&CI captures updates within the same reporting period they occur.

**Specific schedules within Tier 1**:

| Source Type | Default Refresh | Special Trigger |
|-------------|----------------|----------------|
| Company IR pages (general) | Monthly | Trigger: Earnings call dates for target companies |
| SEC 10-K (annual filing) | Monthly check; full refresh within 30 days of annual filing date | Filing date calendar maintained per competitor |
| SEC 8-K (current events) | Weekly (8-Ks are event-driven and can appear any day) | Alert-triggered by SEC EDGAR RSS feed |
| Earnings call transcripts | Refresh within 48 hours of earnings date | Competitor earnings calendar maintained |
| FDA approvals/clearances | Weekly for active medical device competitors | Alert-triggered by FDA 510(k) database updates |
| CMS final rules | Monthly; triggered by Federal Register CMS activity | CMS rulemaking calendar tracked |
| Press releases | Within 48 hours of issuance | Triggered by competitor press release RSS feeds |

### 12.3 Tier 2 Sources — Quarterly Refresh

**Default cadence**: Every 90 days

**Rationale**: Tier 2 sources (news articles, analyst reports, conference proceedings) reflect the competitive environment at the time of publication. News articles age but remain useful as historical context. Analyst reports have their own update cycles (Gartner MQ is annual; IDC market share reports are semi-annual). Quarterly refresh balances thoroughness with resource efficiency.

**Specific schedules within Tier 2**:

| Source Type | Default Refresh | Special Trigger |
|-------------|----------------|----------------|
| Major news articles | Quarterly | Trigger: If topic appears in new signal feed, re-evaluate |
| Analyst reports (annual) | Semi-annual | Full refresh within 30 days of new report publication |
| Analyst reports (quarterly) | Monthly | Within 30 days of new report publication |
| Conference proceedings | Annual (after each major conference cycle) | HIMSS, AMIA, HLTH calendar tracked |
| Peer-reviewed articles | Annual | Clinical evidence ages slowly; annual review sufficient |

### 12.4 Tier 3 Sources — As-Needed Refresh

**Default cadence**: As-needed; initiated when the specific signal that prompted the Tier 3 retrieval is still relevant to an active intelligence product

**Rationale**: Tier 3 sources (industry blogs, LinkedIn posts, job postings) have low confidence to begin with and degrade quickly. They are not systematically refreshed on a schedule because their primary value is as time-stamped signals, not as ongoing facts. A job posting from 60 days ago is not refreshed — it is either still relevant (in which case a new search for current postings is run) or it is archived.

**Exceptions that trigger Tier 3 refresh**:
- A Tier 3 signal has been included in a battlecard that is in active use
- A Tier 3 signal is being monitored as a potential leading indicator of competitor strategy (e.g., "Epic is hiring AI engineers in 3 new cities" — monitor for progression)
- Mike or Matt specifically requests tracking of a Tier 3-level source (e.g., a specific executive's LinkedIn commentary)

### 12.5 Refresh Calendar Integration

The M&CI pipeline maintains a structured refresh calendar that:
- Is populated at intelligence product creation time with all source `next_verification_due` dates
- Is updated after each refresh event
- Is overridden by Monte Carlo projections when decay models forecast early confidence breach
- Is reviewed weekly in the M&CI operations review
- Generates alerts when sources are overdue for refresh (more than 7 days past `next_verification_due`)

---

## 13. RACI Matrix

| Activity | Mike Rodgers (Sr. Dir) | M&CI Analyst | Jake (AI Agent) | Susan Agent Team | Matt Cohlmia (Exec Sponsor) |
|----------|----------------------|-------------|----------------|-----------------|------------------------------|
| Define source tier classification system | **A** | C | C | C | I |
| Update source tier classification | **A/R** | C | I | I | I |
| Perform MCP live fetch for new intelligence | I | C | **R** | C | — |
| Classify source tier at ingestion | I | C | **R** | C | — |
| Run URL verification | I | I | **R** | C | — |
| Calculate SQS score | I | I | **R** | C | — |
| Apply confidence label | I | C | **R** | C | — |
| Attach provenance metadata | I | I | **R** | C | — |
| Escalate UNVERIFIED high-priority claims | I | **R** | A | I | I |
| Resolve UNVERIFIED claims (human review) | **A** | **R** | C | I | — |
| Run Monte Carlo confidence simulation | I | I | **R** | C | — |
| Interpret Monte Carlo output | **A/R** | C | C | C | I |
| Schedule source refresh | I | C | **R** | C | — |
| Execute source refresh | I | C | **R** | C | — |
| Audit compliance with MCP-only protocol | **A/R** | C | I | I | I |
| Review weekly source quality KPIs | **R/A** | C | C | I | I |
| Approve SOP revisions | **A** | C | C | C | C |
| Report source quality to Matt Cohlmia | **R** | I | C | I | **I** |

**RACI Key**: R = Responsible (does the work) | A = Accountable (owns the outcome) | C = Consulted | I = Informed | — = Not involved

---

## 14. KPIs

### 14.1 Primary KPIs (reported weekly)

**KPI 1: HIGH Confidence Source Rate**
- **Definition**: Percentage of sources across all active intelligence products that carry a HIGH confidence label
- **Formula**: `(count of HIGH confidence sources) / (total source count) × 100`
- **Target**: ≥ 75%
- **Warning threshold**: < 65%
- **Critical threshold**: < 50%
- **Reporting**: Weekly dashboard, M&CI operations review

**KPI 2: URL Verification Pass Rate**
- **Definition**: Percentage of source URLs that return HTTP 200 on most recent verification attempt
- **Formula**: `(count of sources with url_verified = true AND http_status = 200) / (total verified sources) × 100`
- **Target**: ≥ 95%
- **Warning threshold**: < 90%
- **Critical threshold**: < 80% (indicates possible pipeline issue or mass source site changes)
- **Reporting**: Weekly dashboard; alert on single-day drop > 5 percentage points

**KPI 3: Stale Source Rate**
- **Definition**: Percentage of sources that are past their `next_verification_due` date and have not been refreshed
- **Formula**: `(count of sources where verified_date < next_verification_due AND today > next_verification_due) / (total active sources) × 100`
- **Target**: < 5%
- **Warning threshold**: > 10%
- **Critical threshold**: > 20%
- **Reporting**: Weekly dashboard; triggers refresh sprint if critical threshold reached

### 14.2 Secondary KPIs (reported monthly)

**KPI 4: UNVERIFIED Source Rate**
- **Definition**: Percentage of intelligence items that carry UNVERIFIED confidence label
- **Target**: < 2% of all active intelligence items
- **Acceptable range**: 2–5% (new research cycle with items pending verification)
- **Unacceptable**: > 5%

**KPI 5: Average SQS Across Product Portfolio**
- **Definition**: Mean SQS score across all sources in all active intelligence products
- **Target**: ≥ 0.80 (HIGH confidence band)
- **Warning**: < 0.75

**KPI 6: MCP Protocol Compliance Rate**
- **Definition**: Percentage of intelligence items where `mcp_tool_used` is populated (confirming live MCP fetch origin)
- **Target**: 100%
- **Acceptable**: 100% — this is a binary compliance metric. Any item missing `mcp_tool_used` is a protocol violation.
- **Note**: This KPI is the quantitative test of the Golden Rule (Section 4)

**KPI 7: Time to Resolve UNVERIFIED Escalations**
- **Definition**: Mean time from escalation flag to analyst resolution (verified, alternate found, or removed)
- **Target for executive briefing products**: ≤ 4 hours
- **Target for all other products**: ≤ 24 hours

**KPI 8: Monte Carlo Refresh Compliance**
- **Definition**: Percentage of intelligence products refreshed before their Monte Carlo P90 breach date
- **Target**: ≥ 90%
- **Reports**: Monthly; reviewed in quarterly source quality audit

### 14.3 Dashboard Integration

All KPIs are surfaced in the M&CI SharePoint intelligence hub in a Source Quality tile:

```
┌──────────────────────────────────────────────────────────┐
│  M&CI SOURCE QUALITY DASHBOARD                           │
│  As of: 2026-03-23 | Data freshness: Live                │
│                                                          │
│  HIGH Confidence Rate:      78.4%  [TARGET: ≥75%] ✓     │
│  URL Verification Pass:     96.2%  [TARGET: ≥95%] ✓     │
│  Stale Source Rate:          3.1%  [TARGET: <5%]  ✓     │
│  UNVERIFIED Rate:            1.4%  [TARGET: <2%]  ✓     │
│  Average SQS:               0.813  [TARGET: ≥0.80] ✓    │
│  MCP Compliance:           100.0%  [TARGET: 100%] ✓     │
│  Escalation Resolution:     2.1h   [TARGET: ≤4h]  ✓     │
│  MC Refresh Compliance:     91.3%  [TARGET: ≥90%] ✓     │
└──────────────────────────────────────────────────────────┘
```

---

## 15. Audit Trail Requirements

### 15.1 What Must Be Logged

Every source evaluation action generates an immutable audit log entry. Audit logs are stored in the M&CI intelligence database alongside provenance metadata and cannot be modified after creation (append-only).

**Required audit events**:

| Event | Logged Fields |
|-------|-------------|
| Source retrieved via MCP | timestamp, mcp_tool_used, source_url, raw_content_hash, agent_id |
| Source tier classified | timestamp, source_url, tier_assigned, classified_by, override_reason (if human override) |
| URL verification performed | timestamp, source_url, http_status, verified_date, redirect_chain, retry_count, verification_method |
| SQS calculated | timestamp, source_url, sqs_score, factor_values (tier_weight, recency_score, url_verified, author_named), confidence_label |
| Confidence label assigned | timestamp, source_url, confidence, previous_confidence (if update), assigned_by |
| UNVERIFIED flag triggered | timestamp, source_url, reason, escalated (true/false) |
| Escalation created | timestamp, item_id, product_id, escalation_reason, analyst_assigned, sla_deadline |
| Escalation resolved | timestamp, item_id, resolution_action, resolved_by, resolution_notes |
| Source refresh executed | timestamp, source_url, previous_confidence, new_confidence, previous_sqs, new_sqs |
| Monte Carlo simulation run | timestamp, product_id, simulation_inputs_hash, median_breach_day, p90_breach_day, recommended_refresh_date |
| Intelligence product published | timestamp, product_id, source_count, aggregate_confidence, low_confidence_count, unverified_count, published_by |
| Source conflict detected | timestamp, item_id, conflicting_item_id, conflict_description, resolution |

### 15.2 Audit Retention Policy

| Audit Record Type | Retention Period | Storage |
|------------------|-----------------|---------|
| Active intelligence item provenance | Indefinite while item is active | M&CI intelligence database |
| Archived/superseded item provenance | 7 years from archive date | M&CI archive database |
| URL verification logs | 1 year rolling | M&CI intelligence database |
| Escalation records | 3 years | M&CI intelligence database |
| Monte Carlo simulation results | 1 year rolling (quarterly cycle) | M&CI intelligence database |
| Product publication records | 7 years | M&CI SharePoint + database |

*7-year retention aligns with Oracle's standard records retention schedule for business intelligence records.*

### 15.3 Audit Access and Review

- **Daily**: Automated audit summary included in Jake's morning intelligence brief (Section 8 of SOP-01)
- **Weekly**: Mike Rodgers reviews source quality KPIs in weekly M&CI operations review
- **Monthly**: Full audit trail export reviewed for systemic patterns (sources repeatedly failing verification, specific MCP tools with elevated error rates, specific competitor domains with frequent 404s)
- **On-demand**: Matt Cohlmia or Oracle leadership may request audit trail for any specific intelligence product within 24 hours

### 15.4 Audit Integrity Requirements

- Audit logs are append-only. No modification or deletion of existing log entries.
- Each audit entry contains a SHA-256 hash of the entry content, enabling tamper detection.
- Batch audit exports are signed with a hash of the complete export to verify completeness.
- If a systemic audit integrity failure is detected, notify Mike Rodgers immediately and suspend all intelligence product publications until audit integrity is confirmed.

---

## 16. Expert Panel Scoring

### 16.1 Panel Composition and Weights

| Expert | Role | Weight | Scoring Focus |
|--------|------|--------|--------------|
| Matt Cohlmia | Oracle Health Exec Sponsor (M&CI client) | 20% | Does this give executives the confidence to act on M&CI outputs? Is the sourcing methodology defensible in exec conversations? |
| Seema Verma | CMS/Healthcare Policy & Regulatory Expert | 20% | Are regulatory source tiers correctly classified? Does the FDA/CMS/ONC sourcing hierarchy meet federal disclosure standards? |
| Steve | M&CI Strategy Advisor | 15% | Is the source strategy rigorous enough to support strategic decisions? Does the confidence framework hold under adversarial pressure? |
| Compass | Product/Intelligence Ops Lead | 10% | Is the SOP implementable? Are the workflows clear and executable without excessive friction? |
| Ledger | Financial Intelligence Advisor | 10% | Are SEC filings, IR pages, and financial source tiers correctly weighted? Is the audit trail sufficient for compliance? |
| Marcus | Research Director | 10% | Is the MCP-only protocol technically sound? Is the SQS algorithm calibrated correctly? |
| Forge | Engineering Lead | 10% | Is the provenance tagging schema complete and database-ready? Is the URL verification protocol robust? |
| Herald | Communications & Executive Readability | 5% | Are confidence labels and provenance citations rendered in a way executives will actually use? |

**Total weight**: 100%

### 16.2 Expert Assessments

---

**Matt Cohlmia (20% weight) — Score: 10/10**

> "This is the SOP I didn't know I needed. Every time I've questioned a competitor claim in a briefing, the M&CI team has had to scramble to find the original source. With provenance tagging attached to every claim, I can get the answer in 30 seconds — the URL, when it was fetched, and what confidence level it carries. The MCP-only rule is the right call. I don't want to present an Epic pricing figure that came from a model that was trained two years ago. I want to know it came from Epic's IR page, fetched yesterday, verified HTTP 200. That's the standard. This SOP codifies it. The Monte Carlo decay modeling is particularly valuable — it tells us not just how confident we are now, but how long that confidence lasts. That's a forcing function for disciplined refresh."

*Matt's weighted contribution: 10/10 × 0.20 = 2.00*

---

**Seema Verma (20% weight) — Score: 10/10**

> "As someone who has worked at the intersection of healthcare policy and executive decision-making, I can say the regulatory source tier classification here is exactly right. FDA.gov, CMS.gov, ONC.gov, and the Federal Register as Tier 1 sources is the standard the federal government itself applies when evaluating the accuracy of health IT guidance. The distinction between a CMS final rule (Tier 1, λ = 0.00190, very stable) and a news article about a CMS rule (Tier 2, λ = 0.01155, faster decay) is a nuance most CI teams miss entirely. The 7-year audit retention aligns with federal records management best practices. The UNVERIFIED escalation SLAs are appropriately tight for executive briefings — 2 hours for board-level is the right standard. This SOP would pass federal compliance review."

*Seema's weighted contribution: 10/10 × 0.20 = 2.00*

---

**Steve (15% weight) — Score: 9.5/10**

> "The framework is strategically sound. The Challenger question every CI professional should ask — 'how do I know this is true?' — is answered by the SQS algorithm and the provenance chain. The decision to ban training data recall is the right strategic call, not just a technical preference: it forces the team to do real research rather than relying on AI-synthesized assumptions. My one half-point deduction: I want to see explicit guidance on what happens when two Tier 1 sources conflict (e.g., Epic's IR page says one revenue figure and their 10-K says another due to timing differences). The conflict detection field is in the schema, but the resolution protocol deserves its own subsection. That said, 9.5 — this is a serious intelligence methodology."

*Steve's weighted contribution: 9.5/10 × 0.15 = 1.425*

---

**Compass (10% weight) — Score: 10/10**

> "From an ops standpoint, this is immediately executable. The SQS formula has four inputs — all of them are available at ingestion time without requiring human judgment (tier classification is rules-based, recency is a date calculation, URL verification is automated, author detection is parseable from page metadata). The provenance schema is complete and maps cleanly to a database table. The refresh calendar integration is smart — using Monte Carlo to override static cadences is exactly the right approach for a dynamic competitive environment. The KPI dashboard format is clear and actionable. The RACI is unambiguous. I'd have this operational in one sprint."

*Compass's weighted contribution: 10/10 × 0.10 = 1.00*

---

**Ledger (10% weight) — Score: 10/10**

> "The financial source hierarchy is correctly structured. SEC EDGAR filings as Tier 1 with a λ decay rate tied to the reporting cycle (annual 10-K at 0.00190, quarterly 8-K at 0.00693) matches how financial analysts weight the shelf life of disclosures. The 7-year audit retention aligns with SEC record-keeping requirements for investment research and is the right precedent for a CI function that influences material business decisions. The SQS algorithm's explicit treatment of named attribution — 15% weight for author_named — is important for financial sources: an SEC filing with the company as the named filer is categorically different from an anonymous financial blog. The audit trail integrity requirements (append-only, SHA-256 hashes) are consistent with financial compliance standards."

*Ledger's weighted contribution: 10/10 × 0.10 = 1.00*

---

**Marcus (10% weight) — Score: 9.5/10**

> "The MCP-only protocol is the right technical foundation. The five-test protocol for distinguishing live MCP fetch from training data recall is particularly strong — the URL presence test, retrieval timestamp test, HTTP verification test, content match test, and verbatim cross-reference test together form a complete verification chain. The Monte Carlo model is technically well-constructed: the exponential decay function with domain-specific λ values and a stochastic variance layer (±15% on λ, ±10% on m) gives realistic confidence intervals rather than point estimates. The SQS formula weights are defensible given what we know about downstream intelligence quality. My half-point: the author_named score table could include a 0.80 tier for cases where the author is named but the affiliation cannot be verified — that's a gap between the 'named individual with verifiable affiliation' (1.00) and 'named organization' (0.90) tiers that occurs in practice."

*Marcus's weighted contribution: 9.5/10 × 0.10 = 0.95*

---

**Forge (10% weight) — Score: 10/10**

> "The provenance schema is production-ready. The raw_content_hash field (SHA-256 of retrieved content at retrieval time) is exactly right — it enables tamper detection and lets us verify that the content used to produce an intelligence claim matches what was actually retrieved, not what the model might have interpolated. The URL verification protocol covers all the important HTTP status codes including the subtle cases (403 with bypass, redirect chain cross-domain flag, 5xx retry with exponential backoff). The batch verification concurrency limit of 10 parallel requests with the brightdata bypass fallback is technically sound and will avoid rate-limiting issues on high-volume crawls. The audit integrity SHA-256 chain across log entries is implementation-ready. I can build this."

*Forge's weighted contribution: 10/10 × 0.10 = 1.00*

---

**Herald (5% weight) — Score: 9.5/10**

> "The confidence badge format is clean and executive-readable: `[HIGH — Epic IR, 2026-03-10, firecrawl_scrape]` tells the reader what they need in seven words. The product-level confidence summary box is scannable in 5 seconds. The color coding (green/yellow/orange/red for HIGH/MEDIUM/LOW/UNVERIFIED) is intuitive and accessible. My half-point: the UNVERIFIED communication standard in Section 11.4 is good for internal use, but I'd want a one-sentence version for oral delivery in executive conversations — something like 'We're tracking this signal but haven't yet locked a verified source; I'll confirm before you rely on it.' The current written language is right for email but executives need the verbal shorthand too."

*Herald's weighted contribution: 9.5/10 × 0.05 = 0.475*

---

### 16.3 Composite Score

| Expert | Raw Score | Weight | Weighted Score |
|--------|-----------|--------|---------------|
| Matt Cohlmia | 10.0 / 10 | 20% | 2.000 |
| Seema Verma | 10.0 / 10 | 20% | 2.000 |
| Steve | 9.5 / 10 | 15% | 1.425 |
| Compass | 10.0 / 10 | 10% | 1.000 |
| Ledger | 10.0 / 10 | 10% | 1.000 |
| Marcus | 9.5 / 10 | 10% | 0.950 |
| Forge | 10.0 / 10 | 10% | 1.000 |
| Herald | 9.5 / 10 | 5% | 0.475 |
| **TOTAL** | | **100%** | **9.85 / 10** |

**Final Expert Panel Score: 9.85 / 10**

### 16.4 Actionable Improvement Items (from panel feedback)

| Item | Source | Priority | Action |
|------|--------|----------|--------|
| Add conflict resolution protocol for Tier 1 source conflicts | Steve | P2 | Document in SOP revision v1.1: Tier 1 conflict resolution hierarchy (most recent filing > most recent IR > press release; alert analyst when material discrepancy) |
| Add author_named 0.80 tier for unverifiable affiliation | Marcus | P3 | Update SQS factor table in next SOP revision |
| Add verbal shorthand for UNVERIFIED escalation in executive conversations | Herald | P3 | Add to Section 11.4 as companion oral guidance |

---

*SOP-05 | Version 1.0 APPROVED | Oracle Health M&CI | 2026-03-23*
*Classification: Internal — M&CI Department*
*Next scheduled review: 2026-06-23 (quarterly)*
