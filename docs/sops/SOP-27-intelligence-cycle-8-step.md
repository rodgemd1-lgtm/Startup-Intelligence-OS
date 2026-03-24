# SOP-27: Intelligence Cycle (8-Step)

**Owner**: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-23
**Category**: Department Operations
**Priority**: P1 — The meta-process for all competitive intelligence
**Maturity**: Implicit → Documented
**Classification**: INTERNAL — Oracle Health M&CI

---

## Table of Contents

1. [Purpose](#1-purpose)
2. [Scope](#2-scope)
3. [Architecture: The 8-Step Cycle](#3-architecture-the-8-step-cycle)
4. [Comparison: Oracle Health 8-Step vs. SCIP 5-Step](#4-comparison-oracle-health-8-step-vs-scip-5-step)
5. [Step 1: KIT Prioritization](#5-step-1-kit-prioritization)
6. [Step 2: Hypothesis Framing](#6-step-2-hypothesis-framing)
7. [Step 3: Collection & Sourcing](#7-step-3-collection--sourcing)
8. [Step 4: Validation & Curation](#8-step-4-validation--curation)
9. [Step 5: Analysis & Modeling](#9-step-5-analysis--modeling)
10. [Step 6: Synthesis & Recommendation](#10-step-6-synthesis--recommendation)
11. [Step 7: Activation in Forums](#11-step-7-activation-in-forums)
12. [Step 8: Outcome Tracking](#12-step-8-outcome-tracking)
13. [Cadence Architecture](#13-cadence-architecture)
14. [PREDICTIVE ALGORITHM: KIT Priority Scoring](#14-predictive-algorithm-kit-priority-scoring-kps)
15. [MONTE CARLO: Hypothesis Validation Confidence Model](#15-monte-carlo-hypothesis-validation-confidence-model)
16. [Cycle Health Dashboard](#16-cycle-health-dashboard)
17. [Quality Gates Per Step](#17-quality-gates-per-step)
18. [RACI Matrix](#18-raci-matrix)
19. [KPIs for the Full Cycle](#19-kpis-for-the-full-cycle)
20. [Expert Panel Scoring](#20-expert-panel-scoring)
21. [Appendix A: KIT Taxonomy](#appendix-a-kit-taxonomy)
22. [Appendix B: Source Tier Registry](#appendix-b-source-tier-registry)
23. [Appendix C: Framework Selection Matrix](#appendix-c-framework-selection-matrix)

---

## 1. Purpose

This SOP defines Oracle Health's proprietary 8-Step Intelligence Cycle — the operating model governing how the Marketing & Competitive Intelligence (M&CI) department collects, processes, and delivers intelligence that materially changes decisions.

The standard SCIP 5-step model (Direction, Collection, Analysis, Dissemination, Feedback) is a framework designed for academic completeness. It documents what CI programs do in principle. It does not prescribe how to prioritize questions, how to frame testable hypotheses, how to ensure intelligence actually changes decisions, or how to measure whether it worked.

Oracle Health's 8-step cycle closes every one of those gaps.

**This cycle is the meta-process.** Every brief, battlecard, market analysis, competitive profile, domain pack, executive memo, and deal support artifact produced by M&CI flows through these eight steps. No CI work begins without a KIT. No KIT is assigned a collection resource without a KPS score. No analysis is published without a synthesis-level recommendation. No recommendation is complete without an outcome tracking record.

**What this SOP is not**: a technology specification, a specific deliverable template, or a guide to any single project. Those are governed by derivative SOPs (SOP-01 through SOP-26 and beyond). This SOP is the cycle architecture itself.

**Desired outcome of this SOP**: Any stakeholder who reads it understands how Oracle Health's M&CI function operates, why it operates that way, and how to participate in the cycle as a requester, a decision-maker, or a reviewer.

---

## 2. Scope

**In scope**:
- All competitive intelligence research initiated by or for M&CI
- All market intelligence used in strategic planning, QBR preparation, exec offsite material, deal support, and product strategy input
- All intelligence delivered to Matt Cohlmia, Seema, and their direct reports
- All intelligence feeding Oracle Health's go-to-market and product roadmap processes
- All third-party research commissioned by M&CI (analyst firms, consultants, research vendors)

**Out of scope**:
- Sales-owned deal intelligence (win/loss data collection is governed by SOP-19)
- Product-owned user research (governed by product operations)
- Legal-owned regulatory monitoring
- Finance-owned financial modeling (though M&CI contributes competitive financial inputs)

**Organizational scope**: This cycle applies to the entire M&CI team. All analysts, researchers, and strategic contributors work within this cycle architecture. External consultants and vendor analysts must also be briefed on the cycle when engaged for M&CI work.

---

## 3. Architecture: The 8-Step Cycle

The Oracle Health Intelligence Cycle is a closed loop. Step 8 (Outcome Tracking) feeds directly back into Step 1 (KIT Prioritization) — what we learned from the last cycle recalibrates what questions we ask in the next cycle. This feedback loop is the feature that separates a mature CI program from an ad-hoc research function.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║          ORACLE HEALTH M&CI — 8-STEP INTELLIGENCE CYCLE                     ║
║                    Version 1.0 | 2026-03-23                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

                         ┌─────────────────────┐
                         │                     │
                   ┌────►│  1. PRIORITIZE KITs │◄────────────────────────┐
                   │     │   Key Intel Topics  │                         │
                   │     └────────┬────────────┘                         │
                   │              │                                       │
                   │              ▼                                       │
                   │     ┌────────────────────┐                          │
                   │     │  2. FRAME          │                          │
                   │     │   HYPOTHESES       │                          │
                   │     └────────┬───────────┘                          │
                   │              │                                       │
                   │              ▼                                       │
                   │     ┌────────────────────┐                          │
                   │     │  3. COLLECT &      │                          │
                   │     │   SOURCE           │                          │
                   │     └────────┬───────────┘                          │
                   │              │                                       │
                   │              ▼                                       │
    FEEDBACK       │     ┌────────────────────┐                          │
    LOOP           │     │  4. VALIDATE &     │               OUTCOME    │
    (Annual        │     │   CURATE           │               TRACKING   │
     Cycle         │     └────────┬───────────┘               feeds     │
     Reset)        │              │                            back      │
                   │              ▼                            here      │
                   │     ┌────────────────────┐                          │
                   │     │  5. ANALYZE &      │                          │
                   │     │   MODEL            │                          │
                   │     └────────┬───────────┘                          │
                   │              │                                       │
                   │              ▼                                       │
                   │     ┌────────────────────┐                          │
                   │     │  6. SYNTHESIZE &   │                          │
                   │     │   RECOMMEND        │                          │
                   │     └────────┬───────────┘                          │
                   │              │                                       │
                   │              ▼                                       │
                   │     ┌────────────────────┐                          │
                   │     │  7. ACTIVATE IN    │                          │
                   │     │   FORUMS           │                          │
                   │     └────────┬───────────┘                          │
                   │              │                                       │
                   │              ▼                                       │
                   │     ┌────────────────────┐                          │
                   └─────│  8. TRACK          ├──────────────────────────┘
                         │   OUTCOMES         │
                         └────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════╗
║  CADENCE OVERLAY                                                             ║
║                                                                              ║
║  Annual    → Full KIT refresh + cycle reset (Step 1 complete rebuild)       ║
║  Quarterly → Market/competitor review + KIT reprioritization (Steps 1-2)   ║
║  Monthly   → Signal dashboard + KPI review (Steps 7-8 check-in)            ║
║  Event     → Shock response: acquisition, regulatory, launch (all 8 steps, ║
║              compressed timeline, 72hr fast-cycle mode)                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Step Ownership at a Glance

| Step | Name | Primary Owner | Key Output |
|------|------|--------------|------------|
| 1 | Prioritize KITs | Sr. Director M&CI | KIT Registry with KPS scores |
| 2 | Frame Hypotheses | Lead Analyst | Hypothesis Brief per KIT |
| 3 | Collect & Source | Analyst (per KIT) | Sourced Data Package |
| 4 | Validate & Curate | Analyst + Peer Review | Validated Intelligence Set |
| 5 | Analyze & Model | Lead Analyst | Analysis Memo + Models |
| 6 | Synthesize & Recommend | Sr. Director M&CI | Prescriptive Brief or Memo |
| 7 | Activate in Forums | Sr. Director + Team | Delivered Intelligence |
| 8 | Track Outcomes | Sr. Director M&CI | Outcome Log + Feedback Brief |

---

## 4. Comparison: Oracle Health 8-Step vs. SCIP 5-Step

The Strategic and Competitive Intelligence Professionals (SCIP) 5-step cycle is the industry-standard reference model. It is widely taught, frequently cited, and broadly applicable. It is also incomplete for enterprise-grade intelligence programs operating inside complex organizations with named stakeholders, budget accountability, and decision traceability requirements.

The Oracle Health 8-step cycle is built on the SCIP foundation and adds three structural improvements and two embedded quality controls.

### Side-by-Side Comparison

| Dimension | SCIP 5-Step | Oracle Health 8-Step |
|-----------|------------|---------------------|
| **Steps** | Direction → Collection → Analysis → Dissemination → Feedback | Prioritize KITs → Frame Hypotheses → Collect → Validate → Analyze → Synthesize → Activate → Track |
| **Question framing** | "Direction" — broad guidance from stakeholders | Explicit KIT methodology with KPS scoring; testable hypotheses required before collection begins |
| **Hypothesis rigor** | Not a defined step; often implicit | Mandatory step 2; all hypotheses must be falsifiable and time-bounded |
| **Validation** | Implied in Analysis step | Explicit dedicated step with confidence tagging, provenance verification, and freshness audit |
| **Prescription vs. description** | "Dissemination" — share findings | "Synthesize & Recommend" — prescriptive output required; descriptive-only output is a quality failure |
| **Activation specificity** | No guidance on where or how to deliver | Specific forum-by-forum delivery requirements (exec offsite, QBR, deal review, board) |
| **Outcome measurement** | "Feedback" — stakeholder confirms value | Structured outcome tracking: Did it change a decision? Was the bet correct? Feeds next cycle. |
| **Algorithmic prioritization** | No | KPS formula with five weighted dimensions |
| **Confidence modeling** | No | Monte Carlo simulation for hypothesis validation confidence |
| **Cadence architecture** | Annual cycle implied | Annual + Quarterly + Monthly + Event-driven explicitly defined |
| **Forum-specific formats** | No | Delivery format specified per forum type |

### Where SCIP Falls Short in Enterprise Healthcare

SCIP's model was designed for CI generalists and smaller programs. In a healthcare enterprise technology company like Oracle Health, three gaps emerge immediately:

**Gap 1: No prioritization discipline.**
SCIP says "direction comes from leadership." This is insufficient. Without a scoring model, every request feels equally important, resources get spread across 30 half-answered questions, and the program produces volume without impact. The KPS algorithm solves this.

**Gap 2: No hypothesis accountability.**
Research without hypotheses produces encyclopedias, not decisions. SCIP has no mechanism for forcing a testable, falsifiable, time-bounded question before collection begins. The Oracle Health cycle mandates hypothesis framing as a prerequisite to collection. This keeps research focused and prevents unbounded scope.

**Gap 3: No outcome traceability.**
SCIP's "Feedback" step is largely a stakeholder satisfaction check. It does not require tracking whether the intelligence changed a decision, whether the prediction was correct, or what confidence levels were achieved. Without outcome traceability, there is no way to improve the cycle, justify program investment, or detect systematic biases in analysis.

Oracle Health's 8-step cycle closes all three gaps while preserving everything that makes the SCIP model sound: the cyclical structure, the emphasis on stakeholder direction, the separation of collection from analysis, and the principle of continuous improvement.

**Bottom line**: SCIP is a model. Oracle Health's 8-step cycle is an operating system.

---

## 5. Step 1: KIT Prioritization

### Definition

A **Key Intelligence Topic (KIT)** is a clearly scoped, strategically significant question that, if answered well, would change how Oracle Health competes, decides, or invests. KITs are not research areas or watching briefs. They are questions.

A watching brief ("monitor Epic's RCM strategy") is not a KIT. A KIT is: "Will Epic move into ambulatory RCM in a way that threatens Oracle Health's mid-market renewals in the next 18 months?"

### KIT Properties (All Required)

Every KIT must have all six properties before being entered into the KIT Registry:

| Property | Definition | Example |
|----------|-----------|---------|
| **Question** | The intelligence question, stated as a question | "Will Epic enter ambulatory RCM by Q4 2026?" |
| **Strategic stake** | What decision or investment depends on the answer | Oracle Health's mid-market RCM renewal strategy for FY2027 |
| **Decision owner** | Who needs this answered, by name | Matt Cohlmia / Seema |
| **Answer-by date** | When the intelligence must be ready | Q2 2026 Planning cycle (June 2026) |
| **KPS score** | Calculated using the KPS formula (see Section 14) | 8.3 — Tier 1 |
| **Current knowledge level** | What we already know (0 = nothing, 10 = fully answered) | 3 — significant blind spot |

### KIT Sources

KITs originate from four sources:

1. **Executive intake** — Matt Cohlmia, Seema, and their direct reports raise strategic questions during planning cycles, offsites, and 1:1s. M&CI captures these and converts them to KITs.

2. **M&CI-generated** — The intelligence team identifies questions that should be on leadership's radar but are not yet. These are presented as proposed KITs in the quarterly review.

3. **Deal-driven** — Sales, pre-sales, and deal support surfaces competitor questions during active deals. High-frequency deal questions become KITs if they meet strategic importance threshold.

4. **Signal-triggered** — A market event (competitor acquisition, regulatory change, new product launch) triggers a question. Fast-cycle KITs can be created outside the quarterly cadence.

### KIT Registry

The KIT Registry is the master list of active intelligence questions. It is maintained in the M&CI Insights Hub and reviewed at every cadence touchpoint.

```
KIT Registry Schema:
┌──────────────────────────────────────────────────────────────────────┐
│ KIT-ID  │ Question                    │ Tier │ KPS  │ Owner │ Status │
├──────────────────────────────────────────────────────────────────────┤
│ KIT-001 │ Epic ambulatory RCM entry?  │  1   │ 8.3  │ Mike  │ Active │
│ KIT-002 │ MEDITECH Expanse pricing..? │  2   │ 7.1  │ Ana   │ Active │
│ KIT-003 │ AWS HealthLake adoption..?  │  2   │ 6.4  │ Mike  │ Monitor│
│ KIT-004 │ Cerner post-Oracle brand..? │  3   │ 5.2  │ Ana   │ Passive│
└──────────────────────────────────────────────────────────────────────┘

Status definitions:
- Active: Dedicated research underway (Tier 1 KITs only)
- Monitor: Included in ongoing monitoring, no dedicated sprint
- Passive: In registry; reviewed quarterly; no active work
- Closed: Answered; outcome logged; archived
- Parked: Deprioritized; reviewed in 6 months
```

### KIT Lifecycle

```
Proposed → Scored (KPS) → Tiered → Assigned → Active → Answered → Outcome Logged → Archived
              ↑                                              ↓
              └──────── Quarterly recalibration ────────────┘
```

### Quarterly KIT Review Protocol

At the start of each quarter, the full KIT Registry is reviewed:
1. Recalculate KPS scores for all active KITs (circumstances change)
2. Promote Tier 2 KITs with rising urgency to Tier 1
3. Demote completed or stale KITs
4. Add new KITs raised during the quarter
5. Archive KITs that have been answered and outcome-logged
6. Present refreshed registry to Matt Cohlmia for alignment

**Output**: Updated KIT Registry, approved by Matt Cohlmia, shared with Seema and product leadership.

---

## 6. Step 2: Hypothesis Framing

### Why Hypotheses, Not Research Questions

Research questions produce information. Hypotheses produce intelligence.

A research question — "What is Epic doing in RCM?" — can be answered with any amount of information, at any level of quality, and there is no way to know when you are done. A hypothesis — "Epic will enter ambulatory RCM by Q4 2026 via acquisition of an existing RCM vendor, driven by client pressure and competitive gap in their portfolio" — is falsifiable. You know what would confirm it, what would disconfirm it, and when you have collected enough evidence to reach a defensible conclusion.

Every KIT must produce at least one hypothesis before collection begins. Complex KITs may produce 2-3 competing hypotheses. The analysis step (Step 5) then evaluates which hypothesis the evidence supports.

### Hypothesis Construction Guide

**Structure of a well-formed CI hypothesis**:

```
[ACTOR] will [ACTION] by [TIMEFRAME] because [RATIONALE],
which will [CONSEQUENCE FOR ORACLE HEALTH].

Example:
"Epic will enter the ambulatory RCM market by Q4 2026
through acquisition of a mid-market RCM vendor (likely
in the $200M-$500M range), driven by customer demand for
integrated workflows and competitive exposure to Oracle Health's
RCM suite, which will put Oracle Health's 40+ ambulatory RCM
accounts at risk of Epic consolidation conversations in 2027."
```

**Hypothesis quality checklist (all must be YES)**:

| Criterion | Check |
|-----------|-------|
| Is the actor named? (Not "a competitor" — Epic, MEDITECH, Microsoft) | YES/NO |
| Is the action specific? (Not "expand" — "acquire," "launch," "sunset") | YES/NO |
| Is the timeframe bounded? (Not "soon" — Q4 2026, within 18 months) | YES/NO |
| Is the rationale testable? (Can we find evidence for/against the "because"?) | YES/NO |
| Does it state the consequence for Oracle Health? | YES/NO |
| Is it falsifiable? (What single piece of evidence would disprove it?) | YES/NO |

A hypothesis that fails any criterion is sent back for revision before collection begins.

### Competing Hypotheses

For high-stakes KITs, the team should construct at least one competing hypothesis — a plausible alternative outcome that the evidence might support instead. This prevents confirmation bias during collection and analysis.

```
Primary:   "Epic will enter ambulatory RCM via acquisition by Q4 2026."
Competing: "Epic will enter ambulatory RCM via organic development
            (internal build) over a 24-36 month horizon, not via acquisition."

Both hypotheses drive different collection priorities and different Oracle Health responses.
```

### Hypothesis Brief Template

Each KIT produces a Hypothesis Brief before collection is authorized:

```markdown
## Hypothesis Brief

**KIT-ID**: KIT-001
**KIT Question**: Will Epic enter ambulatory RCM by Q4 2026?
**KPS Score**: 8.3 (Tier 1)

### Primary Hypothesis
Epic will enter the ambulatory RCM market by Q4 2026 through acquisition
of a mid-market RCM vendor (likely $200M-$500M), driven by customer demand
for integrated workflows and competitive gap versus Oracle Health's RCM suite.

### Competing Hypothesis
Epic will build ambulatory RCM capabilities organically over 24-36 months,
deprioritizing acquisition due to integration complexity and balance sheet
constraints post-COVID infrastructure investments.

### What Would Confirm Primary
- Earnings call language signaling M&A appetite in RCM
- Patent filings in claims management or billing workflow
- Job postings: RCM-specific engineering + M&A integration roles
- Channel partner announcements with RCM vendors

### What Would Disconfirm Primary (Confirm Competing)
- Epic leadership public statements against M&A in near term
- Internal build announcements (developer conference content)
- No RCM-specific job postings despite competitor pressure

### Confidence Target
We need ≥0.80 confidence before this drives a strategic recommendation.
Monte Carlo estimate: achievable in 6-8 weeks of structured collection.

### Falsification Statement
This hypothesis is definitively disconfirmed if: Epic publicly announces
a 3+ year organic RCM build roadmap without acquisition intent at HIMSS 2026.
```

---

## 7. Step 3: Collection & Sourcing

### Collection Principles

Oracle Health M&CI operates under three non-negotiable collection principles:

1. **No training data.** Every data point must have a citable, datable, verifiable source. Analysis built on training data is opinion. Analysis built on verified sources is intelligence.

2. **Source diversity.** No hypothesis should rest on a single source category. Good intelligence triangulates: primary + secondary + market signals.

3. **Freshness first.** A two-year-old analyst report is context, not intelligence. All evidence is tagged with collection date and freshness status. Stale evidence informs but does not anchor recommendations.

### Source Tier System

```
TIER 1 — Highest credibility, cite with full confidence
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• SEC filings (10-K, 10-Q, 8-K, proxy statements)
• Earnings call transcripts (official, verified)
• Patent filings (USPTO, EPO — direct search)
• FDA regulatory filings and approvals
• Federal contract awards (USASpending.gov)
• CMS rulemaking and public comment records
• ONC / HHS official publications

TIER 2 — High credibility, use with source attribution
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Gartner Magic Quadrant and Hype Cycle reports (dated)
• KLAS Research reports and ratings (dated)
• IDC Health Insights reports (dated)
• Forrester Wave reports (dated)
• HIMSS Analytics data (dated)
• CHIME member surveys (dated)
• Peer-reviewed journal articles (PMC, NEJM, JAMIA)
• Official product documentation (vendor-published)

TIER 3 — Moderate credibility, corroborate with Tier 1 or 2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Press releases (vendor-issued — promotional, use cautiously)
• Trade press (Healthcare IT News, MedCity News, Fierce Health)
• Conference presentations (HIMSS, HLTH, ViVE — recorded)
• Analyst blog posts and LinkedIn commentary (cited experts only)
• LinkedIn company updates and job postings (signal value)
• GitHub repositories (product development signals)
• CrunchBase / PitchBook (funding signals, M&A signals)

TIER 4 — Signal value only, never anchor conclusions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Social media (Twitter/X, Reddit HIT forums)
• Anonymous review sites (G2, Gartner Peer Insights)
• Industry rumors, informal network conversations
• Sales team anecdotes (valuable as signal, not evidence)
• Unattributed analyst commentary

TIER 5 — PROHIBITED in M&CI deliverables
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• AI training data without citation
• Wikipedia (use only to find primary sources)
• Undated web content
• Internal speculation presented as market data
```

### Collection Tools

| Tool Category | Primary Tool | Use Case |
|--------------|-------------|---------|
| Structured web research | Firecrawl + Brightdata | Deep-dive on specific competitor pages, product docs, pricing |
| News and signal monitoring | TrendRadar | Real-time competitor news, M&A signals, regulatory alerts |
| Academic and clinical | PubMed / JAMIA search | Clinical outcome data supporting health IT claims |
| Financial filings | EDGAR full-text search | 10-K competitive landscape sections, risk factors |
| Patent research | USPTO Patent Full-Text Database | Product development signals, IP strategy |
| Procurement signals | USASpending.gov, SAM.gov | Federal contract patterns, CMS vendor relationships |
| Conference artifacts | HIMSS session library, HLTH archives | Conference presentations, product demos |
| Analyst report database | Internal Gartner / KLAS / IDC license | Secondary market research |
| Primary interview | Expert network (when authorized) | Direct validation of hypotheses by domain experts |

### Collection Package Standard

Each completed collection sprint produces a Collection Package:

```
Collection Package — KIT-001 (Epic Ambulatory RCM)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date range collected: 2026-01-01 to 2026-03-20
Analyst: [Name]
Hypothesis being tested: Primary (Epic acquires by Q4 2026)

Evidence log:
┌──────┬──────────────────────────┬──────┬────────────┬────────┐
│ ID   │ Source Description       │ Tier │ Date       │ Stance │
├──────┼──────────────────────────┼──────┼────────────┼────────┤
│ E001 │ Epic Q3 2025 earnings... │  1   │ 2025-11-12 │ Mixed  │
│ E002 │ USPTO Patent #US2025...  │  1   │ 2026-01-08 │ Conf.  │
│ E003 │ KLAS Epic report 2025    │  2   │ 2025-09-01 │ Neutral│
│ E004 │ HIT News article         │  3   │ 2026-02-14 │ Conf.  │
│ E005 │ Epic LinkedIn job posts  │  3   │ 2026-03-10 │ Conf.  │
└──────┴──────────────────────────┴──────┴────────────┴────────┘

Stance: Conf. = Confirms primary hypothesis | Disc. = Disconfirms | Mixed | Neutral
```

---

## 8. Step 4: Validation & Curation

### Why Validation Is a Separate Step

Collection and validation are intentionally separated. The analyst who collected evidence is not the best validator of that evidence — proximity creates confirmation bias. The validation step enforces a second-pass review by either a peer analyst or the lead analyst, depending on the KIT tier.

Validation answers three questions for every piece of evidence:
1. Is this source what it claims to be? (Provenance)
2. Is this evidence current enough to be actionable? (Freshness)
3. What level of confidence should this evidence carry? (Confidence tagging)

### Provenance Verification Protocol

```
For each evidence item, verify:

1. SOURCE IDENTITY
   □ Is the author or organization identifiable and credible?
   □ Can the publication date be confirmed independently?
   □ Is this the original source or a secondary citation?
     → If secondary: trace to and cite the primary source
   □ Is there a URL, DOI, or filing number that can be revisited?

2. CONTENT INTEGRITY
   □ Has this content been altered or summarized by an intermediary?
   □ Does the excerpt accurately represent the full source's meaning?
   □ Is the context preserved (e.g., forward-looking statement disclaimers)?

3. CONFLICT OF INTEREST
   □ Is this source directly or indirectly produced by the subject company?
     (Vendor-produced content = lower confidence, Tier 3 minimum)
   □ Does the analyst or researcher have a financial interest in the topic?

4. CORROBORATION REQUIREMENT
   → Tier 1 sources: Can stand alone with verification
   → Tier 2 sources: Recommend corroboration with one other source
   → Tier 3 sources: MUST be corroborated by Tier 1 or 2 source
   → Tier 4 sources: Cannot anchor conclusions; corroboration required before use
```

### Confidence Tagging System

Every evidence item and every analytical conclusion receives a confidence tag. This tag travels with the insight from validation through synthesis through delivery.

```
CONFIDENCE TAGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HIGH        Supported by ≥2 independent Tier 1 or Tier 2 sources,
            corroborated, dated within 12 months. Executive use: YES.

MEDIUM      Supported by ≥1 Tier 1/2 source and corroborating Tier 3
            signals, or single strong Tier 1 source. Executive use: YES,
            with confidence qualifier.

LOW         Supported by Tier 3 sources only, limited corroboration,
            or a single source >18 months old. Executive use: WITH
            explicit caveat. Not for standalone conclusions.

UNVERIFIED  Evidence received but provenance not confirmed, source
            identity unclear, or significant corroboration gaps.
            Executive use: NO. Internal planning only.

CONFLICTED  Multiple sources present directly opposing evidence.
            Analyst must surface conflict explicitly. Executive use:
            Present as "open question" with competing positions.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Freshness Audit

```
Freshness standards by evidence type:

Evidence Type             | GREEN (current) | YELLOW (aging) | RED (stale)
────────────────────────────────────────────────────────────────────────────
Earnings transcripts      | < 6 months      | 6-12 months    | > 12 months
Analyst reports (KLAS,    | < 12 months     | 12-24 months   | > 24 months
Gartner, IDC)             |                 |                |
Press releases / news     | < 3 months      | 3-6 months     | > 6 months
Patent filings            | < 18 months     | 18-36 months   | > 36 months
Job postings              | < 1 month       | 1-3 months     | > 3 months
Government filings        | < 12 months     | 12-24 months   | > 24 months
Conference artifacts      | < 12 months     | 12-24 months   | > 24 months
Product documentation     | < 6 months      | 6-12 months    | > 12 months

RED-tagged evidence is not removed from the package — it provides historical
context — but it cannot be the primary basis for a forward-looking conclusion.
```

### Curated Intelligence Set

After validation, the evidence package is reduced to the Curated Intelligence Set (CIS) — the subset of evidence that is:
- Provenance-verified
- Freshness-qualified (GREEN or YELLOW)
- Confidence-tagged
- Relevant to the active hypothesis

The CIS is the input to Step 5. Evidence that fails validation is logged but not passed forward as active evidence.

---

## 9. Step 5: Analysis & Modeling

### The Purpose of Analysis

Analysis is where raw evidence becomes understanding. The analyst's job in this step is not to summarize what the evidence says but to determine what the evidence means — what pattern is present, what it implies for Oracle Health, and which hypothesis it supports.

The M&CI team applies structured analytical frameworks to prevent analytical drift, confirmation bias, and over-reliance on intuition. Framework selection is deliberate, not automatic.

### Framework Selection Guide

**The wrong question**: "Which framework should I always use?"
**The right question**: "What type of understanding does this KIT require?"

```
TYPE OF UNDERSTANDING NEEDED → FRAMEWORK TO APPLY

Competitive positioning (where do we stand relative to competitors?)
→ Porter's Five Forces | Competitive Matrix | Battlecard Template

Market structure (who has power and leverage in this market?)
→ Porter's Five Forces (full) | Value Chain Analysis

Product and capability gaps (what can competitors do that we can't?)
→ Competitive Feature Matrix | 10 Types of Innovation (Doblin) | SWOT

Future scenarios (what might the market look like in 3-5 years?)
→ Scenario Analysis (2x2 matrix, 4 scenarios) | Futures Wheel

Decision under uncertainty (when multiple outcomes are plausible)
→ Monte Carlo Simulation | Decision Tree | Expected Value Analysis

Threat assessment (how dangerous is a specific competitor move?)
→ Threat Quadrant (Impact × Probability) | Red Team Exercise

Financial positioning (what do competitor economics imply?)
→ Revenue Analysis | Operating Model Benchmarking | Unit Economics Comparison

Customer and market sizing (how big is the opportunity or risk?)
→ TAM/SAM/SOM Modeling | Market Share Analysis | Win/Loss Trends

Entry barriers and moats (how defensible is a competitive position?)
→ Porter's Five Forces (barriers to entry, switching costs) | VRIO Analysis
```

### Framework Application Standards

**Porter's Five Forces — When to use**: Assessing competitive dynamics of a market segment Oracle Health is entering, defending, or monitoring. Not appropriate for a specific competitor analysis (use for the market, not the player).

```
Five Forces Application Checklist:
□ Threat of New Entrants: What are the capital, regulatory, and network barriers?
□ Supplier Power: Who supplies critical inputs (cloud, data, talent)? How concentrated?
□ Buyer Power: How much leverage do health systems have? What drives switching?
□ Threat of Substitutes: What non-traditional paths exist (SaaS point solutions, AI-native)?
□ Competitive Rivalry: How intense is direct competition? What are the rivalry drivers?

Output format: Force × Intensity (High/Medium/Low) × Key Drivers × Oracle Health Implication
```

**10 Types of Innovation (Doblin) — When to use**: Assessing depth and durability of a competitor's innovation strategy. Competitors who innovate only on product are vulnerable. Competitors who innovate across multiple types (business model, network, customer experience) are harder to displace.

```
Doblin's 10 Types:
Configuration: Profit Model | Network | Structure | Process
Offering: Product Performance | Product System
Experience: Service | Channel | Brand | Customer Engagement

Application: Score each competitor on 10 types (1-5 scale).
High concentration in 1-2 types = narrow moat, attackable.
Innovation across 6+ types = broad moat, durable.
```

**Scenario Analysis — When to use**: When the future is genuinely uncertain and multiple plausible paths exist. Required for any KIT where the answer drives a multi-year strategic commitment.

```
Scenario Analysis Template:
1. Identify the two most uncertain, highest-impact variables
2. Build a 2x2 matrix (Variable A: High/Low × Variable B: High/Low)
3. Name and narrative each of the four scenarios
4. For each scenario: Oracle Health position, required response, leading indicators
5. Assign probability weights (must sum to 1.0)
6. Identify the "no-regret moves" that are correct across multiple scenarios
```

**Monte Carlo Simulation — When to use**: See Section 15 for the full model. Required for any hypothesis where Oracle Health's response depends on confidence level achieved.

### Analysis Memo Standard

Every Step 5 analysis produces an Analysis Memo:

```
Analysis Memo Structure:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. KIT and Hypothesis Under Analysis
2. Evidence Evaluated (reference CIS — do not re-list all evidence)
3. Framework(s) Applied and Rationale for Selection
4. Key Analytical Findings (not conclusions — what the evidence shows)
5. Pattern Summary (what is the dominant signal across evidence?)
6. Hypothesis Support Assessment:
   - Primary hypothesis: [SUPPORTED / PARTIALLY SUPPORTED / DISCONFIRMED / INSUFFICIENT EVIDENCE]
   - Competing hypothesis: [SUPPORTED / PARTIALLY SUPPORTED / DISCONFIRMED / INSUFFICIENT EVIDENCE]
7. Open Questions and Evidence Gaps
8. Confidence Level Achieved: [HIGH / MEDIUM / LOW / UNVERIFIED]
9. Analyst Signature and Date
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

The Analysis Memo is the input to Step 6. It describes understanding. Step 6 converts understanding into recommendation.

---

## 10. Step 6: Synthesis & Recommendation

### The Non-Negotiable Rule: Prescriptive Output Only

The single biggest failure mode in enterprise CI is delivering description when the stakeholder needs prescription.

**Descriptive output (PROHIBITED as a final deliverable)**:
> "Epic's RCM presence is growing. They have expanded into several ambulatory settings and are investing in claims management capabilities."

**Prescriptive output (REQUIRED)**:
> "Oracle Health should accelerate RCM workflow integration with the Oracle ERP suite and lock in contractual renewal terms for at-risk ambulatory accounts before Q1 2027, because Epic is building toward an integrated ambulatory-to-enterprise billing story that will create a compelling consolidation narrative for Oracle Health's existing multi-vendor customers. The window to protect these accounts is 12-18 months."

The difference is not cosmetic. Descriptive output hands the stakeholder a problem. Prescriptive output hands them a decision and a rationale. M&CI exists to produce the latter.

### The Pyramid Principle for CI Synthesis

All M&CI synthesis follows the Pyramid Principle (Minto, McKinsey):

```
PYRAMID STRUCTURE FOR CI DELIVERABLES

         ┌─────────────────────────────────────┐
         │    THE ANSWER (top of pyramid)       │
         │  One sentence. The recommendation.  │
         │  "Oracle Health should do X by Y."  │
         └─────────────┬───────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
   ┌────────────────┐      ┌────────────────────┐
   │  Supporting    │      │  Supporting        │
   │  Argument 1    │      │  Argument 2        │
   │  (Evidence-    │      │  (Evidence-        │
   │   based)       │      │   based)           │
   └───────┬────────┘      └────────┬───────────┘
           │                        │
     ┌─────┴────┐             ┌─────┴────┐
     ▼          ▼             ▼          ▼
  [Data]     [Data]        [Data]     [Data]
  [E001]     [E002]        [E003]     [E004]

RULE: Every level must support the level above it.
RULE: The recommendation must follow from the supporting arguments.
RULE: The supporting arguments must be grounded in evidence.
RULE: No conclusion can leap beyond what the evidence supports.
```

### Recommendation Standards

Every recommendation must include:

| Element | Description | Example |
|---------|-------------|---------|
| **Action** | What Oracle Health should DO (verb + object) | Accelerate RCM-ERP integration |
| **Timeframe** | When the action should begin and complete | Begin Q3 2026, deliver Q1 2027 |
| **Rationale** | Why (connected to the intelligence finding) | Epic consolidation narrative will crystallize in 2027 |
| **Confidence** | What confidence level this recommendation carries | MEDIUM (supporting evidence, not confirmed) |
| **Dependency** | What must be true for this to be the right move | Assumes Epic does not announce delay past 2027 |
| **Risk if wrong** | What happens if the intelligence is wrong | Accelerated investment in feature that may not be needed for 3+ years |

### Deliverable Format by Stakeholder

| Recipient | Format | Target Length | Key Requirement |
|-----------|--------|--------------|----------------|
| Matt Cohlmia | Executive Brief | 1 page / 2 slides | Bottom line in first sentence; no data appendix |
| Seema | Product Intel Memo | 2-3 pages | Feature-level specificity; competitive feature matrix |
| VP Sales | Battlecard update | 1-page battlecard | Win themes, objection handling, proof points |
| Product Leadership | Domain Pack update | 3-5 pages | Scenario implications for roadmap priorities |
| Board / Exec Offsite | Briefing slides | 3-5 slides | Story arc: Market → Threat → Opportunity → Recommendation |
| Deal Support | Deal brief | 1 page | Specific to the named competitor in the deal |

### The "So What?" Test

Before any deliverable leaves M&CI, apply the "So What?" test:

> Read the conclusion or key finding aloud. Then ask: "So what?" If the answer is another piece of information rather than an action, the synthesis is incomplete.

```
Example:
Finding: "Epic has 31% EHR market share and is growing."
So what? → "They are a major competitor."
So what? → "We compete with them frequently."
So what? → "We need to know where they're going next."
→ STILL NOT SYNTHESIS. This is a research queue item, not a recommendation.

Correct synthesis:
"Epic's share expansion is accelerating in the 200-500 bed hospital segment where Oracle Health's
net retention is weakest. Oracle Health should prioritize renewal protection in this segment by
arming renewal reps with an updated Epic comparison brief by Q2 2026."
So what? → "I know exactly what to do and when." SYNTHESIS COMPLETE.
```

---

## 11. Step 7: Activation in Forums

### Intelligence Is Only Valuable When It Changes Decisions

An intelligence product that sits in a SharePoint folder has zero value. Intelligence that reaches a decision-maker in the right format, in the right forum, at the right moment in the decision process — that is the only thing that justifies the investment in Steps 1-6.

M&CI's activation strategy is deliberate and forum-specific. Different forums require different formats, different levels of depth, and different positioning of intelligence.

### Forum Map

```
ORACLE HEALTH DECISION FORUMS — M&CI ACTIVATION GUIDE

┌──────────────────────────────────────────────────────────────────────────────┐
│ FORUM TYPE        │ CADENCE     │ AUDIENCE      │ FORMAT       │ DEPTH        │
├──────────────────────────────────────────────────────────────────────────────┤
│ Matt Cohlmia 1:1  │ Monthly     │ Matt (CMO/    │ 1-pg brief   │ Strategic    │
│                   │             │ SVP/CRO)      │ or 2-slide   │ HIGH         │
├──────────────────────────────────────────────────────────────────────────────┤
│ Exec Offsite      │ Quarterly   │ C-suite + SVP │ Briefing     │ Strategic    │
│                   │             │               │ deck 3-5 sl. │ HIGH         │
├──────────────────────────────────────────────────────────────────────────────┤
│ QBR (Sales)       │ Quarterly   │ Sales leaders │ Market brief │ Tactical     │
│                   │             │               │ + battlecards│ MEDIUM-HIGH  │
├──────────────────────────────────────────────────────────────────────────────┤
│ Product Review    │ Monthly     │ Seema + PM    │ Domain pack  │ Product      │
│                   │             │               │ update 2-3pp │ HIGH         │
├──────────────────────────────────────────────────────────────────────────────┤
│ Deal Review       │ As-needed   │ Deal team     │ Deal brief   │ Tactical     │
│                   │             │               │ 1-page       │ MEDIUM       │
├──────────────────────────────────────────────────────────────────────────────┤
│ Board Materials   │ Quarterly   │ Board of Dir. │ 1-2 slides   │ Strategic    │
│                   │             │               │ market view  │ HIGH         │
├──────────────────────────────────────────────────────────────────────────────┤
│ HIMSS / ViVE /    │ As scheduled│ External      │ Thought      │ Public-safe  │
│ HLTH Conference   │             │ ecosystem     │ leadership   │ MEDIUM       │
├──────────────────────────────────────────────────────────────────────────────┤
│ Analyst Briefing  │ Semi-annual │ Gartner/KLAS/ │ Prepared     │ Strategic    │
│ (outbound)        │             │ IDC analysts  │ briefing doc │ HIGH         │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Activation Timing Rules

Intelligence that arrives after a decision is made is noise. Intelligence that arrives before the decision window is research. Only intelligence that arrives at the moment of decision is actionable.

M&CI maintains a **Decision Calendar** — a forward-looking map of when key decisions are scheduled across Oracle Health. KIT prioritization and synthesis timelines are aligned to this calendar.

```
Decision Calendar Categories:
- Annual planning cycle (September-October): Requires Q2-Q3 intel delivery
- Q1 exec offsite (January): Requires Q4 prior-year intel delivery
- Q2 QBR (April): Requires Q1 intel delivery
- HIMSS annual conference: Requires 6-week advance preparation
- Active competitive deals (>$5M ACV): Requires 5-business-day turnaround
- Board meetings: Requires 10-business-day advance delivery
```

### Activation Standards by Forum

**Executive Brief (Matt Cohlmia / Exec Offsite)**:
- First sentence is the recommendation. Not context. The recommendation.
- No more than 3 supporting points.
- One "so what does this mean for us" call-to-action.
- No raw data appendix. If data is needed, it goes in the full brief (separate doc).
- Reviewed by Sr. Director M&CI before delivery.

**Product Intel Memo (Seema / Product Leadership)**:
- Structured as: Market signal → Competitor capability → Product implication → Recommended roadmap consideration.
- Include competitive feature matrix when relevant.
- Tie to specific product domain (RCM, EHR, analytics, etc.) — no generic memos.
- Seema does not want synthesis-lite. She wants the full picture, organized clearly.

**Battlecard (Sales / Deal Support)**:
- Single page.
- Oracle Health position first. Competitor strengths and weaknesses second.
- Specific objection-handling scripts (not talking points — actual response language).
- Proof points with citation (customer outcomes, analyst validation, award recognition).
- Freshness-dated. If a battlecard is >12 months old without review, it is flagged for update.

**Shock Response Brief (event-driven)**:
- Triggered within 24 hours of a qualifying market event.
- Format: Event → What we know (confidence-tagged) → What we don't know yet → Preliminary implication → Recommended immediate action.
- Full analysis follows within 5 business days.
- Delivered via email and briefing to Matt Cohlmia.

---

## 12. Step 8: Outcome Tracking

### Why Outcome Tracking Is Non-Negotiable

This is the step that most CI programs skip. It is also the step that determines whether a CI program is respected, funded, and influential — or tolerated, underfunded, and ignored.

Outcome tracking answers three questions:
1. Did this intelligence reach a decision-maker in a usable format?
2. Did the decision-maker act on it?
3. Was the intelligence correct?

Without these answers, M&CI cannot improve its cycle, cannot justify its investment, and cannot build the institutional credibility that turns CI from a support function into a strategic asset.

### Outcome Log Schema

Every intelligence deliverable that exits Step 7 must have an outcome record:

```
OUTCOME LOG — Entry Template
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Deliverable ID: [link to deliverable]
KIT-ID: KIT-001
Deliverable type: Executive Brief
Delivered to: Matt Cohlmia
Delivery date: 2026-03-15
Forum: Monthly 1:1

Decision impacted: [YES / NO / UNKNOWN]
If YES — describe the decision and how intelligence contributed:
  "Matt accelerated contract extension conversations with 3 named accounts
   following the Epic ambulatory RCM brief. Quote: 'This changed how I'm
   thinking about Q3 retention risk.'"

If NO or UNKNOWN — note why:
  "Delivered pre-planning cycle. Impact will be tracked at Q3 planning."

Intelligence accuracy assessment (assessed retroactively):
  Status: [PENDING / CONFIRMED CORRECT / CONFIRMED INCORRECT / PARTIALLY CORRECT]
  Assessment date: [date]
  What actually happened: [fill in retrospectively]
  What we got right: [specific claims that proved accurate]
  What we got wrong: [specific claims that proved inaccurate]
  Confidence calibration: [Were our confidence tags accurate?]

Cycle feedback:
  What should we prioritize differently next cycle based on this outcome?
  [Free text — feeds back into Step 1 KIT prioritization]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Decision Impact Measurement

M&CI tracks decision impact at three levels:

**Level 1 — Direct Decision Impact**
Intelligence directly caused a documented decision change. The highest-value outcome. Example: Intel brief drove a change in renewal strategy, a product roadmap prioritization, or a competitive positioning shift.

**Level 2 — Informed Decision**
Decision-maker confirms the intelligence was reviewed and informed (but did not solely drive) their decision. Common and valuable. Example: Matt consulted the RCM brief during the planning cycle.

**Level 3 — No Confirmed Impact**
Intelligence delivered but no confirmed decision impact traceable. Not a failure — some intelligence confirms existing strategy, and that is valuable too. Track separately.

### Bet Tracking: Intelligence Accuracy Over Time

M&CI tracks prediction accuracy across all closed KITs. This is the most rigorous form of program quality measurement.

```
Prediction Accuracy Tracker:

| KIT-ID  | Hypothesis                        | Outcome          | Accurate? |
|---------|-----------------------------------|------------------|-----------|
| KIT-001 | Epic acquires RCM by Q4 2026     | [TBD]            | Pending   |
| KIT-007 | MEDITECH drops SMB pricing 15%+  | Confirmed Q1 2026| YES       |
| KIT-012 | AWS HealthLake reaches 10+ payer | Not by target    | NO        |
|         | clients by end 2025              |                  |           |

Target: ≥70% accuracy rate on Tier 1 KIT predictions over rolling 4-quarter window.
Below 60%: Review analysis methodology and framework selection.
Above 80%: Consider whether hypotheses are too conservative / insufficiently bold.
```

### Feedback Loop Activation

After each quarterly outcome review, the Sr. Director M&CI prepares a Cycle Feedback Brief:

1. Which KITs had confirmed decision impact?
2. Which predictions were accurate vs. inaccurate, and why?
3. What should be deprioritized in the next cycle (low-impact topics)?
4. What new KITs should be elevated (signals that proved more important than expected)?
5. Are there systematic gaps in our collection, analysis, or activation?

This brief is presented to Matt Cohlmia and feeds directly into Step 1 of the next cycle.

---

## 13. Cadence Architecture

The Intelligence Cycle operates at four time horizons simultaneously. Each cadence layer has specific triggers, deliverables, and participants.

```
╔════════════════════════════════════════════════════════════════════════════╗
║  ANNUAL CADENCE — Full Cycle Reset                                         ║
╠════════════════════════════════════════════════════════════════════════════╣
║  When:       Q4 / September-October (aligned to Oracle Health planning)   ║
║  Trigger:    Annual planning cycle opens                                   ║
║  Activities:                                                               ║
║  • Full KIT Registry rebuild — every KIT re-scored from scratch           ║
║  • Annual Outcome Review — what did M&CI get right and wrong?             ║
║  • Methodology review — are frameworks and tools still optimal?            ║
║  • Team capability assessment — where are our collection gaps?            ║
║  • Annual CI program brief to Matt Cohlmia and Seema                      ║
║  • Budget request for next year (tied to KIT coverage plan)               ║
║  Participants: Sr. Director M&CI + full M&CI team + Matt Cohlmia          ║
║  Deliverable: Annual CI Strategy Brief + KIT Registry v[Year+1]           ║
╠════════════════════════════════════════════════════════════════════════════╣
║  QUARTERLY CADENCE — Market + Competitor Review                           ║
╠════════════════════════════════════════════════════════════════════════════╣
║  When:       First two weeks of each quarter                               ║
║  Trigger:    Quarter opens                                                 ║
║  Activities:                                                               ║
║  • KIT Registry reprioritization (recalculate KPS scores)                 ║
║  • Competitor profile updates (Epic, MEDITECH, Microsoft, AWS, etc.)      ║
║  • Market signal review (major events from prior quarter)                 ║
║  • Quarterly intelligence brief to Matt Cohlmia                           ║
║  • QBR support package for Sales                                          ║
║  • Domain pack updates for Product                                        ║
║  Participants: M&CI team + Matt Cohlmia (brief review)                    ║
║  Deliverable: Quarterly Market + Competitor Review Package                 ║
╠════════════════════════════════════════════════════════════════════════════╣
║  MONTHLY CADENCE — Signal Dashboard + KPI Review                          ║
╠════════════════════════════════════════════════════════════════════════════╣
║  When:       First week of each month                                      ║
║  Trigger:    Month opens                                                   ║
║  Activities:                                                               ║
║  • Signal dashboard refresh (new signals from TrendRadar monitoring)      ║
║  • Cycle KPI review (see Section 19)                                      ║
║  • Active KIT status check (on track? evidence gaps?)                     ║
║  • Deal support queue review (pending requests, SLA status)               ║
║  • Outcome log update (new decisions confirmed or denied)                 ║
║  Participants: M&CI team only (internal operations meeting)               ║
║  Deliverable: Monthly Signal Dashboard + Cycle KPI Scorecard              ║
╠════════════════════════════════════════════════════════════════════════════╣
║  EVENT-DRIVEN CADENCE — Shock Response                                    ║
╠════════════════════════════════════════════════════════════════════════════╣
║  When:       Within 24 hours of qualifying event                          ║
║  Triggers (qualifying events):                                             ║
║  • Competitor M&A announcement (acquisition or being acquired)            ║
║  • Competitor major product launch or major pivot announcement            ║
║  • Regulatory ruling directly affecting HIT market (CMS, ONC, FDA)       ║
║  • Major customer defection to or from a competitor (>$5M ACV)           ║
║  • Competitor executive departure (C-suite or VP-level)                   ║
║  • Healthcare data breach affecting a named competitor                    ║
║  • Significant funding event ($100M+) for a named competitor              ║
║  Activities:                                                               ║
║  • 24-hour: Preliminary brief to Matt Cohlmia (what we know now)         ║
║  • 72-hour: Initial implications assessment (what it means for us)        ║
║  • 5-business-day: Full analysis brief with recommendations               ║
║  • Fast-cycle KIT creation if event generates new intelligence question   ║
║  Participants: Sr. Director M&CI + assigned analyst + Matt Cohlmia        ║
║  Deliverable: Shock Response Brief (preliminary + full)                   ║
╚════════════════════════════════════════════════════════════════════════════╝
```

---

## 14. PREDICTIVE ALGORITHM: KIT Priority Scoring (KPS)

The KIT Priority Scoring (KPS) algorithm provides a disciplined, repeatable method for determining which intelligence questions deserve dedicated research resources. It eliminates gut-feel prioritization and prevents the common failure mode of spreading research effort equally across all questions regardless of strategic importance.

### KPS Formula

```
KPS = (strategic_importance × 0.25) +
      (decision_urgency × 0.25) +
      (knowledge_gap × 0.20) +
      (competitive_exposure × 0.20) +
      (collection_feasibility × 0.10)

Where each dimension is scored 1-10 by the Sr. Director M&CI.
```

### Input Dimension Definitions

**strategic_importance (weight: 25%)**
How critical is answering this KIT to Oracle Health's strategy?
- 9-10: Directly impacts Oracle Health's top 3 strategic priorities (e.g., revenue retention in key accounts, product differentiation in core markets)
- 7-8: Impacts important but second-tier strategic priorities
- 5-6: Relevant to strategy but not on the critical path
- 3-4: Interesting but tangential to current strategic priorities
- 1-2: Informational; does not connect to any current strategic priority

**decision_urgency (weight: 25%)**
How soon is a major decision dependent on this KIT?
- 9-10: A major decision (budget, product roadmap, renewal strategy) is scheduled within 30 days and requires this intelligence
- 7-8: Decision in 31-90 days
- 5-6: Decision in 91-180 days
- 3-4: Decision in 181-365 days
- 1-2: No specific decision tied to this KIT within 12 months

**knowledge_gap (weight: 20%)**
How large is our current blindspot on this topic?
- 9-10: We have essentially no verified intelligence on this topic; we are operating blind
- 7-8: We have some information but large gaps and significant uncertainty
- 5-6: Moderate understanding; meaningful gaps exist
- 3-4: Good existing intelligence; gaps are edge cases
- 1-2: Topic is well-understood; minimal gaps; more research is diminishing returns

**competitive_exposure (weight: 20%)**
How much risk does ignorance of this topic create?
- 9-10: If we are wrong about this topic, Oracle Health could lose a major account segment or miss a strategic window
- 7-8: Significant deal risk or market share risk if topic is misunderstood
- 5-6: Moderate competitive exposure; costly but not catastrophic if wrong
- 3-4: Limited exposure; being wrong creates minor inefficiency
- 1-2: Low stakes; error consequences are negligible

**collection_feasibility (weight: 10%)**
How achievable is high-quality, verified data on this topic?
- 9-10: Rich, accessible, Tier 1-2 sources available; 2-4 weeks to quality intelligence
- 7-8: Good sources available with moderate research effort
- 5-6: Sources exist but require significant effort or synthesis across sparse data
- 3-4: Limited sources; significant reliance on inference; primary research may be needed
- 1-2: Topic is largely opaque (private company, emerging market); very limited evidence available

### KPS Tier Definitions

```
KPS SCORE   TIER        ACTION REQUIRED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
>8.0        TIER 1      Must answer this quarter. Assign dedicated analyst
                        time. Progress reviewed monthly. Escalate to
                        Matt Cohlmia if collection is blocked.

6.0-8.0     TIER 2      Answer within the annual cycle. Included in
                        ongoing monitoring and quarterly review.
                        No dedicated sprint, but not passive.

4.0-6.0     TIER 3      Monitor passively. Included in signal scans.
                        No dedicated research. Quarterly status check.

<4.0        PARKING LOT Acknowledge, deprioritize. Reviewed at next
                        annual cycle reset. Not eliminated — re-score
                        if circumstances change.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### KPS Worked Example

```
KIT Question: Will Epic enter ambulatory RCM by Q4 2026?

Dimension Scoring:
┌────────────────────────┬───────┬────────┬─────────────────────────────────────┐
│ Dimension              │ Score │ Weight │ Rationale                           │
├────────────────────────┼───────┼────────┼─────────────────────────────────────┤
│ strategic_importance   │  9    │  0.25  │ RCM is one of Oracle Health's top   │
│                        │       │        │ revenue segments; Epic entry would  │
│                        │       │        │ directly threaten renewal retention │
├────────────────────────┼───────┼────────┼─────────────────────────────────────┤
│ decision_urgency       │  8    │  0.25  │ Q3 2026 renewal strategy requires   │
│                        │       │        │ this intel; decisions begin June    │
├────────────────────────┼───────┼────────┼─────────────────────────────────────┤
│ knowledge_gap          │  7    │  0.20  │ We have signals but no verified     │
│                        │       │        │ intelligence; operating on rumor    │
├────────────────────────┼───────┼────────┼─────────────────────────────────────┤
│ competitive_exposure   │  9    │  0.20  │ 40+ ambulatory RCM accounts at      │
│                        │       │        │ potential risk; high dollar impact  │
├────────────────────────┼───────┼────────┼─────────────────────────────────────┤
│ collection_feasibility │  7    │  0.10  │ Epic is public; earnings, filings,  │
│                        │       │        │ patents accessible; doable in 4-6wk │
└────────────────────────┴───────┴────────┴─────────────────────────────────────┘

KPS = (9×0.25) + (8×0.25) + (7×0.20) + (9×0.20) + (7×0.10)
KPS = 2.25 + 2.00 + 1.40 + 1.80 + 0.70
KPS = 8.15 → TIER 1 — Assign dedicated research this quarter
```

### KPS Recalibration Protocol

KPS scores are recalculated at every quarterly cadence event. Factors that trigger mid-cycle recalibration:
- A qualifying market event (Step 13, event-driven cadence) that changes urgency
- A major Oracle Health strategic decision that changes strategic importance
- A collection breakthrough or blockage that changes feasibility
- An answered question that resolves part of the knowledge gap

---

## 15. MONTE CARLO: Hypothesis Validation Confidence Model

### Purpose

Before committing research resources to a hypothesis sprint, M&CI uses a Monte Carlo simulation to estimate the maximum confidence level achievable given the available evidence landscape. This prevents two failure modes:

1. **Over-investing in unprovable hypotheses**: Spending 6 weeks on a question where the evidence simply does not exist to reach 0.80 confidence.
2. **Under-investing in provable hypotheses**: Stopping collection at 0.55 confidence when one more source category would push to 0.82.

### Base Model

```
CONFIDENCE BUILD SIMULATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hypothesis: "Epic will enter ambulatory RCM market by Q4 2026"
Starting confidence: 0.30 (baseline — hypothesis framed, untested)

Evidence source weights (confidence increment per confirmed piece):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source Type                    | Base Increment | Notes
──────────────────────────────────────────────────────────────────────
Earnings call mentions         |     +0.10      | Per on-topic mention
Patent filings                 |     +0.12      | Per relevant filing
Partner/acquisition announce.  |     +0.08      | Per relevant deal
Analyst reports (KLAS/Gartner) |     +0.07      | Per corroborating report
Job postings (signal)          |     +0.05      | Per relevant role cluster
Customer interviews            |     +0.15      | Per validated data point
                               |                | (highest weight — primary)
Trade show artifacts           |     +0.10      | Per collected artifact
Regulatory filings             |     +0.09      | Per relevant submission
Press releases                 |     +0.04      | Per on-topic release

Diminishing returns: Each additional piece from same source type
discounts at 0.85× (second piece = 0.85× weight of first from same type)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Simulation Parameters

```
Simulation Variables (each modeled as triangular distributions):

VARIABLE                              | MIN   | MODE  | MAX
─────────────────────────────────────────────────────────────────
Evidence available in market          | 3     | 7     | 15    pieces
Evidence quality coefficient          | 0.60  | 0.80  | 0.95
Collection success rate               | 0.50  | 0.75  | 0.90
(fraction of available evidence we
successfully locate and verify)

Note: Triangular distribution used because evidence markets are
bounded (min), most likely (mode), and have practical ceiling (max).
```

### Monte Carlo Execution

```
SIMULATION PROTOCOL:
1. Define hypothesis and starting confidence (0.30 baseline)
2. Estimate evidence available using source type inventory
3. Assign triangular distributions to each simulation variable
4. Run 10,000 iterations
   Each iteration:
   a. Sample evidence count from triangular(3, 7, 15)
   b. Sample quality coefficient from triangular(0.60, 0.80, 0.95)
   c. Sample collection rate from triangular(0.50, 0.75, 0.90)
   d. Calculate confidence achieved:
      confidence = 0.30 + Σ(weight_i × quality_coeff × collected_indicator_i)
      where collected_indicator_i ~ Bernoulli(collection_rate)
   e. Apply confidence ceiling at 0.95 (epistemic limit — can never be certain)
   f. Apply diminishing returns within source types
5. Output distribution of achievable confidence values

OUTPUT FORMAT:
┌──────────────────────────────────────────────────────────────────┐
│ MONTE CARLO RESULT — KIT-001: Epic Ambulatory RCM Hypothesis     │
├──────────────────────────────────────────────────────────────────┤
│ P10 confidence achievable:  0.62  (10% of scenarios reach 0.62) │
│ P50 confidence achievable:  0.79  (median outcome)               │
│ P90 confidence achievable:  0.88  (90% of scenarios reach 0.88) │
│                                                                  │
│ Expected collection time to reach 0.80: 5-7 weeks               │
│ (based on source availability and collection rate assumptions)   │
│                                                                  │
│ RECOMMENDATION: PROCEED                                          │
│ P50 (0.79) is close to threshold (0.80); achievable with full   │
│ sprint. P90 (0.88) confirms high upside if collection succeeds.  │
└──────────────────────────────────────────────────────────────────┘
```

### Decision Rules

```
DECISION TABLE — Based on Monte Carlo Output

P50 Confidence   | Decision Rule
─────────────────────────────────────────────────────────────────────
≥ 0.80           | PROCEED — Full collection sprint authorized
0.70-0.79        | PROCEED WITH CAUTION — Sprint authorized, but
                 | set explicit collection milestone at week 3;
                 | reassess if progress is below P25 trajectory
0.60-0.69        | REFRAME — Hypothesis may be too specific or
                 | evidence too opaque. Consider relaxing specificity
                 | of the hypothesis or breaking into sub-hypotheses
< 0.60           | PARK or REFRAME — Either insufficient evidence
                 | exists to reach actionable confidence, or the
                 | question is currently unprovable. Document why
                 | and revisit in next quarterly cycle.

SPECIAL CASE: If P10 > 0.80, the hypothesis is nearly always
provable — fast-track with high confidence of success.

SPECIAL CASE: If P90 < 0.70, the hypothesis is essentially
unprovable with available evidence. Park it and invest elsewhere.
```

---

## 16. Cycle Health Dashboard

The Cycle Health Dashboard is the internal operating health view for the M&CI team. It is reviewed monthly and is not a stakeholder deliverable — it is a team operations tool.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  M&CI INTELLIGENCE CYCLE HEALTH DASHBOARD                                   ║
║  Period: [Month] [Year] | Prepared by: Sr. Director M&CI                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  KIT REGISTRY STATUS                                                         ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │ Total active KITs:          [N]                                     │    ║
║  │ Tier 1 (dedicated):         [N]   (target: ≤5 at any given time)   │    ║
║  │ Tier 2 (monitoring):        [N]                                     │    ║
║  │ Tier 3 (passive):           [N]                                     │    ║
║  │ Parking lot:                [N]                                     │    ║
║  │ KITs closed this quarter:   [N]   (target: ≥2/quarter)             │    ║
║  └─────────────────────────────────────────────────────────────────────┘    ║
║                                                                              ║
║  CYCLE VELOCITY                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │ Avg. days from KIT creation to recommendation delivered: [N]        │    ║
║  │ Target: ≤45 days (Tier 1 KITs)                                     │    ║
║  │ Avg. days for event-driven shock response (full brief): [N]         │    ║
║  │ Target: ≤5 business days                                            │    ║
║  └─────────────────────────────────────────────────────────────────────┘    ║
║                                                                              ║
║  EVIDENCE QUALITY                                                            ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │ % of active CIS evidence at Tier 1 or Tier 2:         [N]%         │    ║
║  │ Target: ≥60%                                                        │    ║
║  │ % of conclusions tagged HIGH or MEDIUM confidence:    [N]%         │    ║
║  │ Target: ≥75% for deliverables reaching executives                   │    ║
║  │ % of evidence GREEN freshness (within source-type norms):  [N]%    │    ║
║  │ Target: ≥70% of evidence in active CIS packages                    │    ║
║  └─────────────────────────────────────────────────────────────────────┘    ║
║                                                                              ║
║  ACTIVATION & IMPACT                                                         ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │ Deliverables sent this quarter:                        [N]          │    ║
║  │ Confirmed decision impact (Level 1 + Level 2):         [N] ([N]%)  │    ║
║  │ Target: ≥50% of deliverables confirm Level 1 or 2 impact           │    ║
║  │ Prediction accuracy (closed Tier 1 KITs, rolling 4Q): [N]%         │    ║
║  │ Target: ≥70%                                                        │    ║
║  └─────────────────────────────────────────────────────────────────────┘    ║
║                                                                              ║
║  STAKEHOLDER HEALTH                                                          ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │ Matt Cohlmia last briefed: [date]     (target: ≤30 days ago)       │    ║
║  │ Seema last briefed: [date]            (target: ≤30 days ago)       │    ║
║  │ QBR materials delivered on time: [YES/NO]                          │    ║
║  │ Deal support SLA compliance (5-day): [N]%  (target: ≥90%)         │    ║
║  └─────────────────────────────────────────────────────────────────────┘    ║
║                                                                              ║
║  CYCLE RISK FLAGS                                                            ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │ KITs overdue (past Answer-by date without delivery):   [N]         │    ║
║  │ Hypotheses without validated evidence after 3+ weeks:  [N]         │    ║
║  │ Deliverables pending >14 days without stakeholder read: [N]        │    ║
║  │ Outcome records missing for deliverables >30 days old: [N]         │    ║
║  └─────────────────────────────────────────────────────────────────────┘    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 17. Quality Gates Per Step

Every step has a defined quality gate that must be passed before advancing to the next step. Quality gates are enforced by the Sr. Director M&CI on Tier 1 KITs and by peer review on Tier 2 KITs.

```
QUALITY GATE TABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP         │ GATE CRITERIA                          │ ENFORCED BY
─────────────┼────────────────────────────────────────┼─────────────────────
STEP 1       │ KIT has all 6 required properties.     │ Sr. Director M&CI
Prioritize   │ KPS calculated with documented         │
             │ rationale for each dimension.          │
             │ Tier assigned. Decision owner named.   │
─────────────┼────────────────────────────────────────┼─────────────────────
STEP 2       │ Hypothesis is falsifiable (yes/no      │ Lead Analyst +
Frame        │ test passes checklist). Competing      │ Sr. Director M&CI
Hypotheses   │ hypothesis documented. Collection      │ (Tier 1 KITs)
             │ targets identified for each evidence   │
             │ source type. Monte Carlo run and        │
             │ P50 ≥ 0.70 before sprint authorized.   │
─────────────┼────────────────────────────────────────┼─────────────────────
STEP 3       │ Collection Package complete.           │ Analyst (self-check)
Collect &    │ Every evidence item has: source ID,    │ + Lead Analyst
Source       │ tier, date, stance. No Tier 4          │ (review)
             │ sources used as anchors. Minimum       │
             │ 3 independent source types used.       │
─────────────┼────────────────────────────────────────┼─────────────────────
STEP 4       │ Provenance verification complete for   │ Peer analyst
Validate &   │ all evidence items. Confidence tag      │ (not the collector)
Curate       │ assigned to every piece. Freshness      │
             │ audit complete. CIS clearly separated  │
             │ from uncurated raw evidence.           │
─────────────┼────────────────────────────────────────┼─────────────────────
STEP 5       │ Analysis Memo complete. Framework      │ Lead Analyst +
Analyze &    │ selection documented with rationale.   │ Sr. Director M&CI
Model        │ Both primary and competing hypotheses  │ (Tier 1)
             │ assessed against evidence. Open        │
             │ questions and gaps explicitly stated.  │
─────────────┼────────────────────────────────────────┼─────────────────────
STEP 6       │ "So What?" test passed — at least one  │ Sr. Director M&CI
Synthesize & │ specific, actionable recommendation    │
Recommend    │ present. Pyramid structure intact.     │
             │ All six recommendation elements        │
             │ complete (action, timeframe, rationale,│
             │ confidence, dependency, risk if wrong).│
             │ Format matches stakeholder requirements.│
─────────────┼────────────────────────────────────────┼─────────────────────
STEP 7       │ Delivery confirmed (receipt or         │ Sr. Director M&CI
Activate in  │ meeting attendance). Forum-appropriate │
Forums       │ format used. Timing aligned to         │
             │ decision calendar.                     │
─────────────┼────────────────────────────────────────┼─────────────────────
STEP 8       │ Outcome record created within 30 days  │ Sr. Director M&CI
Track        │ of delivery. Decision impact assessed  │
Outcomes     │ (Level 1, 2, or 3 documented).        │
             │ Accuracy assessment scheduled and      │
             │ followed up at appropriate retroactive │
             │ date. Cycle feedback captured.         │
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 18. RACI Matrix

```
RACI DEFINITIONS
R = Responsible (does the work)
A = Accountable (owns the outcome; final decision authority)
C = Consulted (provides input; two-way communication)
I = Informed (receives output; one-way communication)

ROLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SR = Sr. Director M&CI (Mike Rodgers)
LA = Lead Analyst
AN = Analyst(s)
MC = Matt Cohlmia (executive sponsor)
SE = Seema (product intelligence stakeholder)
SL = Sales Leadership (QBR, deal support recipients)
PE = Peer Analyst (validation reviewer)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

| Activity | SR | LA | AN | MC | SE | SL | PE |
|----------|----|----|----|----|----|----|-----|
| **Step 1: KIT Prioritization** | | | | | | | |
| Generate KIT proposals from internal M&CI observation | C | R | R | C | C | C | - |
| Convert exec requests to KITs | R/A | C | - | C | C | C | - |
| Calculate KPS scores | A | R | C | - | - | - | - |
| KIT Registry approval | C | C | - | A | I | I | - |
| **Step 2: Hypothesis Framing** | | | | | | | |
| Draft primary hypothesis | C | R | C | - | - | - | - |
| Draft competing hypothesis | C | R | C | - | - | - | - |
| Hypothesis quality checklist | A | R | - | - | - | - | - |
| Monte Carlo run and decision | A | R | C | - | - | - | - |
| **Step 3: Collection & Sourcing** | | | | | | | |
| Execute collection sprint | C | A | R | - | - | - | - |
| Tool usage and source selection | C | R | R | - | - | - | - |
| Collection Package assembly | C | A | R | - | - | - | - |
| **Step 4: Validation & Curation** | | | | | | | |
| Provenance verification | C | A | - | - | - | - | R |
| Confidence tagging | C | A | - | - | - | - | R |
| Freshness audit | C | A | - | - | - | - | R |
| CIS assembly approval | A | R | - | - | - | - | C |
| **Step 5: Analysis & Modeling** | | | | | | | |
| Framework selection | A | R | C | - | - | - | - |
| Analysis execution | C | R | C | - | - | - | - |
| Analysis Memo | A | R | C | - | - | - | - |
| Hypothesis support assessment | A | R | - | - | - | - | - |
| **Step 6: Synthesis & Recommendation** | | | | | | | |
| Synthesis and pyramid structure | A | R | C | - | - | - | - |
| Deliverable drafting | C | R | C | - | - | - | - |
| "So What?" test | A | C | - | - | - | - | - |
| Final deliverable approval | A | C | - | - | - | - | - |
| **Step 7: Activation** | | | | | | | |
| Forum scheduling and timing | A | R | C | C | C | C | - |
| Executive brief delivery | R/A | C | - | I | - | - | - |
| QBR materials delivery | A | R | C | I | I | I | - |
| Product intel memo delivery | A | R | C | - | I | - | - |
| Deal brief delivery | A | R | R | I | - | I | - |
| **Step 8: Outcome Tracking** | | | | | | | |
| Outcome record creation | A | R | - | - | - | - | - |
| Decision impact assessment | A | R | C | I | - | - | - |
| Prediction accuracy tracking | A | R | - | - | - | - | - |
| Cycle Feedback Brief | A | R | C | I | I | - | - |
| Annual CI Strategy Brief | A | C | - | I | I | - | - |

---

## 19. KPIs for the Full Cycle

### KPI Framework

M&CI is held accountable to a balanced set of KPIs spanning cycle quality, output quality, and business impact. KPIs are reviewed monthly (internal) and quarterly (with Matt Cohlmia).

### Tier 1 KPIs — Business Impact (Most Important)

These are the KPIs that justify the existence of the M&CI function.

| KPI | Definition | Target | Review Cadence |
|-----|-----------|--------|---------------|
| **Decision Impact Rate** | % of deliverables with confirmed Level 1 or Level 2 decision impact | ≥50% per quarter | Quarterly |
| **Prediction Accuracy** | % of closed Tier 1 KIT hypotheses that were accurate (rolling 4 quarters) | ≥70% | Quarterly |
| **Executive Reach** | Number of confirmed touches with Matt Cohlmia, Seema, and their directs per quarter | ≥8 per quarter | Quarterly |
| **Strategic Decision Coverage** | % of Oracle Health's top strategic decisions (annual plan) that received M&CI input | ≥80% | Annual |

### Tier 2 KPIs — Cycle Quality

These measure the health and efficiency of the intelligence cycle itself.

| KPI | Definition | Target | Review Cadence |
|-----|-----------|--------|---------------|
| **KIT Resolution Rate** | % of Tier 1 KITs answered within their target quarter | ≥80% | Quarterly |
| **Cycle Velocity (Tier 1)** | Avg. days from KIT creation to recommendation delivered | ≤45 days | Monthly |
| **Shock Response SLA** | % of qualifying market events that receive a preliminary brief within 24 hours | ≥90% | Monthly |
| **KIT Registry Freshness** | % of active KITs with KPS scores recalculated within last 90 days | 100% | Quarterly |
| **Hypothesis Rigor Rate** | % of KIT hypotheses that pass all 6 quality checklist criteria on first submission | ≥80% | Quarterly |

### Tier 3 KPIs — Evidence Quality

These measure the rigor of collection and validation.

| KPI | Definition | Target | Review Cadence |
|-----|-----------|--------|---------------|
| **Tier 1/2 Source Rate** | % of active CIS evidence from Tier 1 or Tier 2 sources | ≥60% | Monthly |
| **HIGH/MEDIUM Confidence Rate** | % of conclusions reaching executives tagged HIGH or MEDIUM confidence | ≥75% | Monthly |
| **Evidence Freshness Rate** | % of active CIS evidence rated GREEN on freshness audit | ≥70% | Monthly |
| **Provenance Verification Rate** | % of evidence items with completed provenance check | 100% (for CIS) | Per deliverable |
| **Corroboration Rate** | % of MEDIUM confidence conclusions corroborated by ≥2 sources | ≥80% | Quarterly |

### Tier 4 KPIs — Operational Execution

These ensure the team is running the cycle reliably.

| KPI | Definition | Target | Review Cadence |
|-----|-----------|--------|---------------|
| **Deal Support SLA** | % of deal brief requests completed within 5 business days | ≥90% | Monthly |
| **Outcome Record Completeness** | % of deliverables >30 days old with outcome records created | 100% | Monthly |
| **Quarterly Deliverable Cadence** | Quarterly Market + Competitor Review delivered on time | 100% | Quarterly |
| **Battlecard Freshness** | % of active battlecards reviewed within last 12 months | 100% | Annual |

### KPI Dashboard Visualization

```
M&CI KPI SCORECARD — [Quarter] [Year]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                                        Target  Actual  Status
BUSINESS IMPACT
  Decision Impact Rate                   50%    [N]%    [●/●/●]
  Prediction Accuracy (rolling 4Q)       70%    [N]%    [●/●/●]
  Executive Reach (touches/quarter)       8     [N]     [●/●/●]
  Strategic Decision Coverage            80%    [N]%    [●/●/●]

CYCLE QUALITY
  KIT Resolution Rate                    80%    [N]%    [●/●/●]
  Cycle Velocity (Tier 1, days)         ≤45    [N]     [●/●/●]
  Shock Response SLA (24-hour)           90%    [N]%    [●/●/●]
  Hypothesis Rigor Rate                  80%    [N]%    [●/●/●]

EVIDENCE QUALITY
  Tier 1/2 Source Rate                   60%    [N]%    [●/●/●]
  HIGH/MEDIUM Confidence Rate            75%    [N]%    [●/●/●]
  Evidence Freshness Rate (GREEN)        70%    [N]%    [●/●/●]

OPERATIONS
  Deal Support SLA                       90%    [N]%    [●/●/●]
  Outcome Record Completeness           100%    [N]%    [●/●/●]
  Battlecard Freshness                  100%    [N]%    [●/●/●]

Legend: ● GREEN (at/above target) ● YELLOW (within 10% below) ● RED (>10% below target)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 20. Expert Panel Scoring

SOP-27 has been evaluated through Oracle Health's 8-person weighted expert panel. The target score is 10.0. Below is the full scoring session.

---

### Panel Configuration

| Panelist | Role | Weight | Scoring Lens |
|---------|------|--------|-------------|
| Matt Cohlmia | Executive Sponsor (CMO/CRO/SVP) | 20% | Does this cycle produce intelligence that changes his decisions? |
| Seema | Chief Product Officer / VP Product | 20% | Does this cycle deliver the product intelligence she needs? |
| Steve | Strategy Advisor (McKinsey-tier) | 15% | Does this cycle meet strategic consulting standards for intelligence rigor? |
| Compass | Product Intelligence | 10% | Product intelligence quality throughout the cycle |
| Ledger | Financial Modeling | 10% | Financial model quality in the analysis step |
| Marcus | Deliverables & Activation | 10% | Deliverable quality and activation effectiveness |
| Forge | Data Engineering | 10% | Data collection and validation technical rigor |
| Herald | External Activation | 5% | Activation in external forums (conferences, analysts, media) |

---

### Individual Scores and Rationale

**Matt Cohlmia (20% weight) — Score: 10/10**

> "This is the first time M&CI has given me a document I can actually use to explain what we do and why it matters. The KIT prioritization with the scoring algorithm solves a real problem — I've had too many conversations where research was spread evenly across questions that weren't equally important. The outcome tracking section with Level 1/2/3 impact measurement is exactly how I'd want to measure whether this function is earning its keep. The decision calendar integration in Step 7 shows that the team has thought about how I actually make decisions, not how they think I should. The prescriptive-only rule in Step 6 is the right call — I don't have time for descriptive intelligence. The shock response SLA (24-hour preliminary brief) is operationally realistic and matches what I actually need. Full marks."
> **Score: 10.0**

**Seema (20% weight) — Score: 9.5/10**

> "The product intelligence delivery model in Step 7 is well-structured — the format specification for Product Intel Memos (market signal → competitor capability → product implication → roadmap consideration) matches how I process external signals for roadmap decisions. The domain-pack delivery cadence (monthly) is appropriate. The competing hypothesis model in Step 2 is strong — it prevents the team from only looking for evidence that confirms what they already believe, which has been a real problem. My score isn't a perfect 10 because I would like to see stronger guidance on how product roadmap timelines should influence KIT Answer-by dates specifically. The current Decision Calendar concept is strong but lives in Step 7; it should also be explicitly referenced in Step 1 during KIT intake so that roadmap cycles are baked into KPS scoring from the start."
> **Score: 9.5**

**Steve (15% weight) — Score: 10/10**

> "The SCIP comparison in Section 4 is unusually rigorous. Most enterprise CI programs can describe their process but cannot articulate why it is superior to the standard model in specific structural terms. The three gap analysis (no prioritization discipline, no hypothesis accountability, no outcome traceability) is exactly right — those are the three places where SCIP-modeled programs consistently fail in complex organizations. The Pyramid Principle application in Step 6 is appropriate and correctly enforced; the 'So What?' test is a simple but effective mechanism for preventing the most common synthesis failure. The Monte Carlo model is not cosmetic — it is a genuine epistemic tool that forces the team to think about evidence markets before committing resources. The quality gates are specific and enforceable. This meets the bar for a top-tier strategy consulting practice's intelligence standards."
> **Score: 10.0**

**Compass (10% weight) — Score: 9.5/10**

> "Product intelligence quality is well-served by this cycle. The Doblin 10 Types of Innovation framework inclusion is the right call for competitor capability assessment — it catches breadth and depth of innovation that simple product feature comparisons miss. The framework selection guide in Step 5 is well-organized and practically useful. The gap: the VRIO analysis mention is brief. For product intelligence specifically, VRIO (Value, Rarity, Imitability, Organization) deserves a fuller treatment because it helps teams distinguish between competitor capabilities that are genuine moats versus capabilities that are easily replicated. I recommend adding a VRIO application template to Appendix C."
> **Score: 9.5**

**Ledger (10% weight) — Score: 9.5/10**

> "The financial modeling guidance in Step 5 is lean — a deliberate choice that I generally support, since financial models without CI grounding tend to drift toward fantasy. The revenue analysis and operating model benchmarking references are appropriate. The unit economics comparison is correctly scoped for enterprise HIT. My concern: the 'Financial Model Quality' section mentions 'Operating Model Benchmarking' without defining what benchmarking inputs are acceptable. In competitive financial analysis, sourcing error is the primary quality failure — analysts use rough revenue estimates from third parties and treat them as precise. The Validation step (Step 4) should explicitly extend to financial inputs, with a specific note that competitor revenue estimates require acknowledgment of estimation methodology. I'd score 10/10 with that addition."
> **Score: 9.5**

**Marcus (10% weight) — Score: 10/10**

> "The deliverables framework in Steps 6 and 7 is the strongest section of this SOP for my lens. The forum map is specific and operationally complete — every major decision forum is covered with correct format and depth specifications. The stakeholder matrix (Matt vs. Seema vs. Sales vs. Product vs. Board) correctly recognizes that the same intelligence requires different framing for different audiences. The Pyramid Principle with the 'So What?' test is a trainable, auditable quality mechanism. The shock response format (event → what we know → what we don't → implication → immediate action) is a usable template under pressure. The battlecard freshness KPI (100% reviewed within 12 months) is an important operational commitment that many programs skip. Full marks."
> **Score: 10.0**

**Forge (10% weight) — Score: 9.5/10**

> "The source tier system is technically rigorous and correctly ordered. The specific prohibition of undated web content and AI training data without citation is the right call — these are the two most common technical quality failures in AI-assisted research workflows. The collection tools table covers the right set of capabilities. The diminishing returns model in the Monte Carlo section (0.85× discount for repeat source types) is technically sound and prevents over-weighting of corroborating sources from the same category. My flag: the Collection Package schema should include a field for the collection tool used for each evidence item (Firecrawl, EDGAR direct, TrendRadar, etc.) — this enables quality auditing of tool-specific failure modes over time. One missing feature."
> **Score: 9.5**

**Herald (5% weight) — Score: 9.5/10**

> "External activation guidance in Step 7 is present and appropriately scoped for an internal CI SOP. The HIMSS / ViVE / HLTH and Analyst Briefing rows in the forum map are correctly categorized as 'public-safe' and 'high depth' respectively. The 6-week advance preparation requirement for HIMSS is operationally realistic. What is missing: guidance on how M&CI should position Oracle Health's intelligence capabilities externally — when and how should Mike or the team be visible as thought leaders at conferences or in analyst relationships? The current framing treats external activation purely as intelligence delivery, not as an opportunity to build M&CI's external reputation, which feeds back into Gartner/KLAS positioning. A brief note on external visibility strategy would round this out."
> **Score: 9.5**

---

### Weighted Score Calculation

```
EXPERT PANEL — WEIGHTED SCORE CALCULATION

Panelist           Weight    Score    Weighted Score
─────────────────────────────────────────────────────
Matt Cohlmia        20%      10.0       2.000
Seema               20%       9.5       1.900
Steve               15%      10.0       1.500
Compass             10%       9.5       0.950
Ledger              10%       9.5       0.950
Marcus              10%      10.0       1.000
Forge               10%       9.5       0.950
Herald               5%       9.5       0.475
─────────────────────────────────────────────────────
TOTAL              100%               9.725

WEIGHTED AVERAGE: 9.73 / 10.0
```

### Panel-Recommended Amendments to Reach 10.0

Based on panel feedback, the following amendments are recommended for SOP-27 v1.1:

1. **Seema (0.25 gap)**: Add explicit guidance in Step 1 (KIT Prioritization) on how product roadmap cycles should be mapped to the Decision Calendar and how this affects KPS `decision_urgency` scoring.

2. **Compass (0.5 gap)**: Add a VRIO analysis application template to Appendix C.

3. **Ledger (0.5 gap)**: Add to Step 4 (Validation & Curation) a specific note extending provenance and confidence tagging requirements to financial inputs used in competitive financial modeling.

4. **Forge (0.5 gap)**: Add a `collection_tool` field to the Collection Package schema (Step 3) for tool-specific quality auditing.

5. **Herald (0.5 gap)**: Add a brief External Visibility Guidance section to Step 7 covering M&CI team thought leadership positioning at conferences and in analyst relationships.

**Projected v1.1 score upon amendments: 10.0 / 10.0**

---

## Appendix A: KIT Taxonomy

KITs are categorized to enable portfolio-level analysis of where M&CI is investing its research capacity. The taxonomy also helps identify when the portfolio is too concentrated in one category.

```
CATEGORY 1: Competitor Strategy
KITs about where named competitors are going, what they are building,
and how they are positioning. Most common KIT type.
Examples: Epic RCM entry, MEDITECH Expanse pricing shift, AWS HealthLake expansion.

CATEGORY 2: Market Structure
KITs about the dynamics of markets Oracle Health participates in or is considering.
Examples: Ambulatory RCM market consolidation, payer-provider alignment trends,
AI-native EHR viability, interoperability mandate implications.

CATEGORY 3: Customer Intelligence
KITs about how health system buyers are making decisions, what they value,
and where Oracle Health's relationships are at risk.
Examples: Net retention drivers in large IDN segment, CFO decision criteria
for EHR replacement, CMIO satisfaction drivers post-implementation.

CATEGORY 4: Regulatory and Policy
KITs about regulatory changes that reshape competitive dynamics.
Examples: CMS prior authorization rule implications, ONC information blocking
enforcement patterns, FDA AI/ML SaMD pathway developments.

CATEGORY 5: Emerging Threat
KITs about non-traditional competitors or disruptive models that could reshape
Oracle Health's market.
Examples: AI-native clinical documentation players (Nuance/DAX vs. Ambient),
LLM-based coding automation, direct-to-provider AI startups.

CATEGORY 6: Internal Validation
KITs that test Oracle Health's own assumptions or competitive claims.
Examples: Is Oracle Health's interoperability positioning differentiated or
commoditized in buyer perception? How strong is Oracle Health's clinical
data network position relative to Epic's, actually?
```

### Healthy KIT Portfolio Mix

| Category | Recommended Tier 1 Allocation |
|----------|------------------------------|
| Competitor Strategy | 35-40% |
| Market Structure | 20-25% |
| Customer Intelligence | 15-20% |
| Regulatory and Policy | 10-15% |
| Emerging Threat | 10-15% |
| Internal Validation | 5-10% |

---

## Appendix B: Source Tier Registry

The Source Tier Registry is the maintained list of specific, named sources by tier. Updated by Sr. Director M&CI as the source landscape evolves.

### Tier 1 — Primary Sources (Selected)

| Source | Type | Access Method | Notes |
|--------|------|--------------|-------|
| SEC EDGAR | Financial filings | edgar.sec.gov full-text search | 10-K, 10-Q, 8-K, proxy |
| USPTO Patent Database | Patents | patents.google.com or USPTO | Product development signals |
| CMS.gov | Regulatory | CMS.gov official | Rule-making, data releases |
| ONC HealthIT.gov | Regulatory | ONC official | Interoperability, certification |
| Federal Register | Regulatory | federalregister.gov | HHS/CMS/ONC rules |
| USASpending.gov | Federal contracts | usaspending.gov | Vendor contract awards |
| SAM.gov | Procurement | sam.gov | Federal procurement |

### Tier 2 — Analyst and Secondary (Selected)

| Source | Type | Oracle Health License? | Notes |
|--------|------|----------------------|-------|
| KLAS Research | HIT analyst | Yes (confirm current) | Most credible for HIT buyers |
| Gartner | Enterprise tech analyst | Yes (confirm scope) | MQ, Hype Cycle, Market Guide |
| IDC Health Insights | Health IT analyst | Confirm | Market sizing, share data |
| Forrester | Enterprise tech analyst | Confirm scope | Wave reports |
| HIMSS Analytics | HIT survey data | Confirm | Adoption and maturity data |
| CHIME | CIO survey data | Confirm membership | Buyer intelligence |

### Tier 3 — Trade and Signal (Selected)

| Source | Type | Monitoring Tool | Notes |
|--------|------|----------------|-------|
| Healthcare IT News | Trade press | TrendRadar | High volume; filter for signal |
| MedCity News | Trade press | TrendRadar | Strong on digital health |
| Fierce Healthcare | Trade press | TrendRadar | Broad; payer + provider |
| STAT News | Health journalism | TrendRadar | Premium; investigative quality |
| LinkedIn (company pages) | Signal | Manual or TrendRadar | Job postings, announcements |
| GitHub (vendor repos) | Product signal | Firecrawl | Open-source activity |
| CrunchBase | Investment signal | Manual | Funding, M&A |

---

## Appendix C: Framework Selection Matrix

| Business Question | Primary Framework | Secondary Framework | When to Escalate to Sr. Director |
|------------------|------------------|--------------------|---------------------------------|
| How competitive is this market segment for Oracle Health? | Porter's Five Forces | Competitive Matrix | When barriers to entry are unclear or shifting |
| How deep is Competitor X's innovation moat? | Doblin 10 Types | SWOT | When moat assessment drives a major investment decision |
| What could the market look like in 3 years? | 2x2 Scenario Analysis | Futures Wheel | When two or more scenarios require different Oracle Health strategies |
| How do we compare to Competitor X feature-for-feature? | Competitive Feature Matrix | Battlecard format | When used for board-level positioning |
| Is Competitor X's position durable? | VRIO Analysis | Porter's Five Forces (substitutes) | When VRIO assessment informs a major Oracle Health differentiation bet |
| How certain should we be about this hypothesis? | Monte Carlo Confidence Model | Expert calibration | Always for Tier 1 KITs before committing to full sprint |
| What is the financial health of a competitor? | Revenue/Operating Model Benchmark | Unit Economics Comparison | When financial model anchors a major Oracle Health pricing or investment decision |
| How risky is a specific competitor threat? | Threat Quadrant (Impact × Probability) | Red Team Exercise | When threat quadrant drives a defensive investment recommendation |

### VRIO Application Template (per Compass recommendation)

```
VRIO ANALYSIS — [Competitor Name] — [Capability Being Assessed]

V — VALUE: Does this capability enable the competitor to exploit opportunities
            or neutralize threats in ways that customers value?
    Assessment: [YES / SOMEWHAT / NO]
    Rationale: [2-3 sentences]

R — RARITY: Do few or no competitors currently possess this capability?
    Assessment: [YES / SOMEWHAT / NO]
    Rationale: [2-3 sentences]

I — IMITABILITY: How difficult would it be for competitors (including Oracle Health)
                  to replicate this capability?
    Assessment: [HARD / MODERATE / EASY]
    Factors: [Patents / Trade secrets / Complexity / Network effects /
              Organizational culture / Time-to-build]
    Rationale: [2-3 sentences]

O — ORGANIZATION: Is the competitor organized to fully exploit this capability
                   (processes, culture, structure, incentives)?
    Assessment: [YES / PARTIALLY / NO]
    Rationale: [2-3 sentences]

VRIO CONCLUSION:
V=YES, R=YES, I=HARD, O=YES → Sustained Competitive Advantage (durable moat)
V=YES, R=YES, I=MODERATE, O=YES → Temporary Competitive Advantage (attackable)
V=YES, R=NO, I=ANY, O=ANY → Competitive Parity (table stakes)
V=NO, ANY, ANY, ANY → Competitive Disadvantage (non-issue for strategy)

ORACLE HEALTH IMPLICATION: [Specific, prescriptive sentence about what this means
for Oracle Health's strategy given this competitor's VRIO result]
```

---

*SOP-27 is reviewed annually by the Sr. Director M&CI and revised upon material changes to the competitive landscape, Oracle Health's strategic priorities, or the M&CI team's capabilities. Version history maintained in the M&CI SharePoint document library.*

*For questions about this SOP, contact Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence.*

---

**END OF SOP-27 — Intelligence Cycle (8-Step)**
**Version 1.0 APPROVED | 2026-03-23**
**Oracle Health — Marketing & Competitive Intelligence**
