# Oracle Health M&CI — SOP Master List

**Date**: 2026-03-22
**Owner**: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence
**Sources**: GitHub repo (21 scripts), Claude Code sessions (18-agent studio), ChatGPT history (28 conversations), Web research (36 sources via MCP)
**Status**: RESEARCH COMPLETE — Ready for SOP capture interviews

---

## How To Read This Document

Each SOP below shows:
- **Source**: Where we found evidence this process exists (YOUR = your actual work, BEST PRACTICE = industry standard)
- **Maturity**: How documented/automated it is today
- **Priority**: How important it is to capture as a formal SOP

Maturity levels:
- **Automated** = Running in code, crons, or scripts
- **Implicit** = You do this but it's not documented
- **Partial** = Some documentation exists but incomplete
- **Gap** = Industry best practice you're not doing yet

---

## CATEGORY 1: DAILY INTELLIGENCE OPERATIONS (6 SOPs)

### SOP-01: Daily Morning Brief Assembly
**Source**: YOUR (mike-studio, sharepoint-updater.py, brain_morning_brief.py)
**Maturity**: Automated
**Priority**: P1 — Already running, needs documentation for continuity
**Current State**: Overnight scrape (midnight) → intel assembly (12:30 AM) → morning brief (6:00 AM) → email delivery via Resend API
**Artifacts**: `artifacts/morning-briefs/brief-{date}.md`
**What to Capture**: Signal selection criteria, urgency classification logic, brief format standards, delivery routing rules

### SOP-02: Competitive Signal Triage & Urgency Classification
**Source**: YOUR (sharepoint-updater.py → classify_urgency(), _classify_urgency_enhanced())
**Maturity**: Automated (in code) but undocumented as a process
**Priority**: P1 — This is your core methodology IP
**Current State**: raw_to_signal() → generate_signal_id() → classify_urgency() → match_domain() → match_competitor() → _score_positioning()
**What to Capture**: What makes a signal P0 vs P1 vs P2, VIP sender list, keyword urgency scoring, domain routing rules, the "So What" framework (What Happened → Why It Matters → What We Should Do)

### SOP-03: Weekly Executive Briefing (Matt Cohlmia)
**Source**: YOUR (mike-studio, Friday 3 PM scheduled task)
**Maturity**: Automated
**Priority**: P1
**Current State**: Weekly deep scrape (Mon 2 AM) → weekly digest → Friday Matt Brief (3 PM) → email via Resend
**What to Capture**: What Matt expects, format standards, what gets escalated vs parked, how to handle weeks with no major signals

### SOP-04: Data Freshness Audit
**Source**: YOUR (sharepoint-updater.py → audit_freshness()) + BEST PRACTICE (90-day max threshold)
**Maturity**: Automated
**Priority**: P2
**Current State**: `python sharepoint-updater.py --task freshness-audit`
**What to Capture**: Freshness thresholds by content type, what triggers a refresh, escalation when data goes stale

### SOP-05: Source Evaluation & Data Provenance
**Source**: YOUR (CLAUDE.md Gate 0, data provenance protocol)
**Maturity**: Partial (enforced in code, not documented as standalone SOP)
**Priority**: P1 — This is a differentiator
**Current State**: ALL data via MCP only (never training data), confidence tagging (HIGH/MEDIUM/LOW/UNVERIFIED), URL verification (HTTP 200), Google is NOT a source
**What to Capture**: Source tier classification, confidence scoring methodology, verification requirements, what happens when a source can't be verified

### SOP-06: Regulatory & Compliance Monitoring
**Source**: BEST PRACTICE (healthcare CI) + YOUR (Ellen OS Packet-06: Regulatory, International & Signals)
**Maturity**: Partial (content exists, process undocumented)
**Priority**: P2
**Industry Standard**: Automated scanning of CMS, FDA, ONC, HHS, Federal Register → impact assessment → stakeholder notification
**What to Capture**: Which regulatory bodies to monitor, impact assessment template, notification routing, compliance protocol

---

## CATEGORY 2: COMPETITIVE INTELLIGENCE PRODUCTION (6 SOPs)

### SOP-07: Competitor Profile Creation & Maintenance
**Source**: YOUR (knowledge-base/mci/products/rcm-platforms/) + BEST PRACTICE
**Maturity**: Partial (RCM profiles exist, process undocumented)
**Priority**: P1
**Current Profiles**: Waystar, R1 RCM, Ensemble, Epic, FinThrive, Conifer, CodaMetrix, Access Healthcare
**Industry Standard**: Semi-annual deep dives, event-driven updates within 48 hours, Six Strategic Lenses (Product, Financial, Market, GTM, Customer, Technology)
**What to Capture**: Profile template, update triggers, data sources per section, review cadence, archival policy

### SOP-08: Competitive Battlecard Creation & Maintenance
**Source**: BEST PRACTICE (Klue, Crayon, SCIP) + YOUR (implicit — field questions exist but no formal battlecard process)
**Maturity**: Gap → Implicit
**Priority**: P1 — High-value sales enablement artifact
**Industry Standard**: Quick Dismiss + Overview + Differentiators + Landmine Questions + Objection Handling + Pricing + Win/Loss Stories + Counter-FUD
**Maintenance**: Monthly forced review, 48-hour event-driven updates, 90-day max without review
**What to Capture**: Template, owner, update triggers, distribution (CRM integration?), sales feedback loop

### SOP-09: Win/Loss Analysis
**Source**: BEST PRACTICE (Klue, Pragmatic Institute, Clozd) + YOUR (ChatGPT — field questions for HIMSS)
**Maturity**: Gap → Implicit (you ask win/loss questions at HIMSS but no formal program)
**Priority**: P1 — Research says this is the #1 most impactful CI program
**Industry Standard**: 7-step process — scope → identify candidates → structured 30-min interviews → tag → trend analysis → report → action
**Best Practices**: Equal won/lost, within 30 days, separate collection from analysis, connect to revenue
**What to Capture**: Interview guide, candidate selection criteria, coding taxonomy, reporting cadence, action routing (Sales, Product, Marketing, Exec)

### SOP-10: Pricing & Packaging Intelligence
**Source**: YOUR (build_pricing_excel.py, ORACLE_HEALTH_PRICING_MASTER_DATA.csv, MCI scraper config)
**Maturity**: Automated (Excel generation) but process undocumented
**Priority**: P1
**Current State**: CSV master data → confidence-coded Excel workbook (HIGH green, MEDIUM yellow, LOW red, GAP gray)
**What to Capture**: How pricing data is collected (field, web, earnings), validation methodology, confidence scoring, update frequency, distribution list

### SOP-11: Trade Show / Conference Intelligence
**Source**: YOUR (ChatGPT — HIMSS 2026 two-pass booth sweep methodology)
**Maturity**: Implicit (methodology exists in your head + ChatGPT, not documented)
**Priority**: P1 — This is proprietary methodology
**Your Method**: Pass 1 (7-min hit, 3 questions max, artifact collection, initial score) → Pass 2 (targeted follow-up, triangulated with partners/speakers/Q&A)
**Team Split**: Pricing & Packaging Lead, AI Agents Lead, GTM Lead, Proof-Point Lead, Ecosystem/Partner Lead
**Capture Template**: Vendor, Offering, Buyer, Land Motion, Packaging, AI Maturity, Proof, GTM Angle, Risks, Confidence
**Three-Bucket**: What's sold now vs. what's piloted now vs. what's roadmap
**What to Capture**: Full methodology, team roles, booth capture template, post-event synthesis process, debrief format

### SOP-12: Competitive Response Playbook
**Source**: BEST PRACTICE + YOUR (implicit — you react to competitor moves but no formal playbook)
**Maturity**: Gap
**Priority**: P2
**Industry Standard**: Competitor makes a move → triage (24h) → impact assessment → stakeholder notification → response recommendation → battlecard update
**What to Capture**: Response timeline, RACI matrix, communication templates, escalation criteria

---

## CATEGORY 3: STRATEGIC ANALYSIS & DELIVERABLES (5 SOPs)

### SOP-13: Market Sizing (R-01 Methodology)
**Source**: YOUR (ChatGPT — R-01 Market Sizing Shell v1.1)
**Maturity**: Implicit (methodology exists, used for Public Health module)
**Priority**: P1
**Your Method**: Phase 0 Intake → Phase 1 Methodology Selection → Bottom-up (count × penetration × ASP) → 3 scenarios (Conservative/Base/Aggressive) → 5-year ARR modeling
**What to Capture**: Full R-01 template, data source requirements per segment, scenario assumption framework, output format standards

### SOP-14: Executive Offsite Strategy Prep
**Source**: YOUR (Claude — Seema offsite prep, 18 files across 5 categories)
**Maturity**: Implicit (done twice, process not formalized)
**Priority**: P1
**Your Method**: Intake → Data Assembly (6 foundation docs) → Framework Analysis (10 Types, Innosight, Design Thinking, Future-Back) → War Games (3 options × 3 scenarios) → Synthesis → Expert Panel → Deck
**Quality Bar**: 80+ panelist evaluations, average 2 passes to reach 9.0, worst case 3.35 → 9.0
**What to Capture**: Phase timeline, document template per phase, panel scoring methodology, iteration protocol, deck production process

### SOP-15: Strategic Framing & Innovation Analysis
**Source**: YOUR (CLAUDE.md — every deliverable must be prescriptive, not descriptive)
**Maturity**: Partial (enforced in Claude sessions, not documented standalone)
**Priority**: P2
**Your Frameworks**: 10 Types of Innovation (Doblin), Innosight Dual Transformation, Frog Design Thinking, Future-Back (5-year horizon)
**What to Capture**: When to apply which framework, output format per framework, how to make leadership uncomfortable enough to act

### SOP-16: Monthly Strategic Intelligence Report
**Source**: YOUR (mike-studio — 1st of month leading indicators + content production)
**Maturity**: Automated
**Priority**: P2
**Current State**: Leading indicators analysis (1st of month 4 AM) → content production (1st of month 8 AM) — LinkedIn posts, conference proposals, blog concepts
**What to Capture**: Leading indicator sources, trend detection methodology, content production pipeline

### SOP-17: War Gaming & Scenario Planning
**Source**: YOUR (Seema offsite — 3 strategic options + cross-option synthesis) + BEST PRACTICE
**Maturity**: Implicit
**Priority**: P2
**What to Capture**: Scenario construction methodology, competitor move prediction, red team / blue team structure, synthesis format

---

## CATEGORY 4: QUALITY & GOVERNANCE (4 SOPs)

### SOP-18: 8-Person Weighted Expert Panel Review
**Source**: YOUR (CLAUDE.md, all deliverables)
**Maturity**: Automated (enforced in Claude Code)
**Priority**: P1 — Core quality methodology
**Panel**: Matt (20%), Seema (20%), Steve (15%), Compass (10%), Ledger (10%), Marcus (10%), Forge (10%), Herald (5%)
**Thresholds**: 7.0+ average, no single below 5, Matt and Seema both 7+
**8 Quality Gates**: Data Provenance → Structural Integrity → Strategic Altitude → Competitive Accuracy → Financial Integrity → Executive Readiness → Compliance → URL Verification
**What to Capture**: Full gate definitions, failure handling, iteration protocol, exemption criteria

### SOP-19: Executive Writing Pipeline (Matt/Seema)
**Source**: YOUR (.agents/skills/matt-the-writer.md, seema-the-reviewer.md)
**Maturity**: Automated
**Priority**: P2
**Pipeline**: Matt the Writer drafts (pyramid, 5th-8th grade, em-dashes, cross-industry analogies) → Seema the Reviewer (10-test, SEND/REVISE/RETHINK) → Mike final review
**What to Capture**: Matt's writing rules, Seema's 10 tests, when to bypass for speed

### SOP-20: Research → Define → Design → Build (Phase Gate)
**Source**: YOUR (CLAUDE.md lines 67-89)
**Maturity**: Automated (hard-stop enforced)
**Priority**: P2
**What to Capture**: Phase definitions, transition criteria, what's exempt, approval authority

### SOP-21: SharePoint Content Governance
**Source**: YOUR (sync scripts, upload scripts, capture scripts) + BEST PRACTICE
**Maturity**: Partial (scripts exist, governance policy undocumented)
**Priority**: P2
**Current State**: 21 SharePoint pages, automated sync via Playwright, state tracking via SHA1 hashes
**Industry Best Practice**: Archive never delete, versioning, team-level permissions, metadata columns for search
**What to Capture**: Publishing workflow, approval chain, naming conventions, archival policy, permissions model

---

## CATEGORY 5: KNOWLEDGE MANAGEMENT & DISTRIBUTION (4 SOPs)

### SOP-22: Ellen OS Package Build & Distribution
**Source**: YOUR (build_ellen_os_package.py — 6 packets, 36+ content domains)
**Maturity**: Automated
**Priority**: P2
**Current State**: 6 content packets (Operator Pack + 4 Core Packs) built via Python, synced to SharePoint, state tracked via JSON
**What to Capture**: Packet update triggers, content domain ownership, version management, participant onboarding

### SOP-23: Intelligence Distribution Matrix
**Source**: BEST PRACTICE (Crayon, CI Alliance) + YOUR (implicit)
**Maturity**: Gap → Implicit
**Priority**: P1
**Industry Standard**: Route by team × format × cadence × owner
**What to Capture**: Who gets what, when, in what format — formal RACI for all M&CI deliverables

### SOP-24: Knowledge Base Curation & Ingestion
**Source**: YOUR (scraper configs, MCP data pipeline, 2.1GB local KB)
**Maturity**: Automated (scraping) but curation undocumented
**Priority**: P2
**Current State**: 5 scraper configs (sales-enablement, pricing-intelligence, buyer-psychology, financial-modeling, thought-leadership), nightly + weekly + biweekly cycles
**What to Capture**: Source selection criteria, ingestion pipeline, dedup logic, quality thresholds, retirement policy

### SOP-25: Stakeholder Request Intake & Tracking
**Source**: BEST PRACTICE (CI Alliance, UserIntuition)
**Maturity**: Gap
**Priority**: P2
**Industry Standard**: Formal intake form → triage → assign → track → deliver → feedback loop
**What to Capture**: Request form fields, SLA by request type, tracking system, completion criteria

---

## CATEGORY 6: DEPARTMENT OPERATIONS (3 SOPs)

### SOP-26: M&CI Department Operating Model
**Source**: YOUR (ChatGPT — 12-area department design, APQC/McKinsey/BCG/Bain benchmarking)
**Maturity**: Implicit (benchmarked but not formalized)
**Priority**: P1
**Your 12 Areas**: Strategic agenda, Market intelligence, Customer/demand, Competitive intelligence, Ecosystem/tech/regulatory, Foresight/scenario, Portfolio/growth, Strategy formulation, Strategy translation, Execution/performance, Benchmarking, Intelligence operations
**What to Capture**: Which areas you actively own vs aspirational, resource allocation, cadence per area

### SOP-27: Intelligence Cycle (8-Step)
**Source**: YOUR (ChatGPT — designed your own) + BEST PRACTICE (SCIP 5-step)
**Maturity**: Implicit
**Priority**: P1
**Your 8 Steps**: Prioritize KITs → Frame hypotheses → Collect/source → Validate/curate → Analyze/model → Synthesize/recommend → Activate in forums → Track outcomes
**Industry Cadence**: Annual (full refresh), Quarterly (market + competitor review), Monthly (signal dashboard + KPI), Event-driven (shock response)
**What to Capture**: Full cycle with handoff points, tool usage per step, quality checkpoints

### SOP-28: Program Effectiveness Measurement
**Source**: BEST PRACTICE (Crayon, Klue, CI Alliance)
**Maturity**: Gap
**Priority**: P2
**Industry KPIs**: Battlecard usage rate (70%+), competitive win rate (QoQ), deal flag rate, intelligence freshness (<90 days), stakeholder adoption, contributed won deals, time to intelligence, request volume
**What to Capture**: Which KPIs to track, measurement methodology, reporting cadence, target-setting process

---

## PRIORITY CAPTURE ORDER

Based on impact × documentation gap:

| Priority | SOP # | Name | Why First |
|----------|-------|------|-----------|
| 1 | SOP-11 | Trade Show Intelligence | Proprietary methodology, lives entirely in your head, HIMSS prep needed |
| 2 | SOP-02 | Signal Triage & Urgency | Core methodology IP, automated but undocumented |
| 3 | SOP-09 | Win/Loss Analysis | #1 most impactful CI program per research, currently a gap |
| 4 | SOP-13 | Market Sizing (R-01) | Proprietary methodology, used for real deliverables |
| 5 | SOP-08 | Battlecard Creation | High-value sales enablement, currently a gap |
| 6 | SOP-14 | Offsite Strategy Prep | Complex multi-phase process, done twice but not formalized |
| 7 | SOP-18 | Expert Panel Review | Core quality methodology, already automated |
| 8 | SOP-23 | Distribution Matrix | Who gets what — currently implicit |
| 9 | SOP-27 | Intelligence Cycle | Your 8-step version is unique, needs documentation |
| 10 | SOP-26 | Department Operating Model | The meta-SOP — defines everything else |

---

## AUTOMATION POTENTIAL

SOPs Jake can automate vs SOPs that require Mike's judgment:

| Automation Level | SOPs | What Jake Does |
|-----------------|------|----------------|
| **Fully Automated** | 01, 03, 04, 06, 16, 22 | Already running via crons + scripts |
| **Jake Drafts, Mike Reviews** | 07, 08, 10, 12, 17, 24 | Jake assembles from data, Mike validates |
| **Jake Assists Interview** | 02, 11, 13, 14, 26, 27 | SOP Capture skill interviews Mike, structures output |
| **Mike Owns, Jake Tracks** | 09, 15, 19, 20, 21, 23, 25, 28 | Mike executes, Jake logs and monitors |

---

## NEXT STEPS

1. **Capture SOPs via Jake's SOP Capture skill** — Start with Priority 1-3 (Trade Show, Signal Triage, Win/Loss)
2. **Store each SOP in Jake's Brain** as `jake_procedural` (source_type='sop')
3. **Create a goal** for "28 M&CI SOPs Documented" in the goal tracking system
4. **Publish to SharePoint** as the M&CI Program Operations section
5. **Set up quarterly SOP review** via Jake's weekly check-in system
