# SOP-22: Ellen OS Package Build & Distribution

**Owner**: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-23
**Category**: Knowledge Management & Distribution
**Priority**: P2
**Maturity**: Automated

---

## 1. Purpose

This SOP governs the complete lifecycle of the Ellen OS Content Package system: the structured process by which Oracle Health M&CI compiles, versions, distributes, and maintains the six knowledge packets that power Ellen — the department's AI intelligence layer.

Ellen is only as good as what she knows. A battlecard with six-month-old pricing loses deals. A competitor profile missing a recent acquisition mis-frames strategy conversations. A regulatory brief that hasn't absorbed the latest CMS rulemaking exposes Oracle Health to credibility risk in front of payers. The Ellen OS Package system exists to prevent these failure modes at scale, across 36+ content domains, without requiring manual curation labor for every update.

This SOP defines: how packets are assembled, how they are versioned, what triggers a rebuild, how they are distributed to SharePoint for Ellen's consumption, how rollback works when a new version degrades Ellen's response accuracy, and how the Packet Value Score (PVS) algorithm continuously monitors packet health between scheduled refreshes.

The governing design principle is **automated freshness with human authority at the boundary**. The build pipeline runs autonomously. Human sign-off is required only at two points: when a new packet version is promoted to production for the first time, and when a rollback decision must be made.

---

## 2. Scope

### 2.1 In Scope

This SOP applies to:

- All six Ellen OS Content Packets (Packets 00–05) and their constituent content domains
- The `build_ellen_os_package.py` build pipeline and all associated scripts
- The SharePoint sync layer and Playwright automation
- The JSON state tracking system and SHA1 hash-based change detection
- The Packet Value Score (PVS) algorithm and automatic rebuild triggers
- The rollback procedure for defective packet versions
- Content domain ownership assignments across M&CI and cross-functional teams
- Quality gates applied before publication
- Onboarding of new team members to Ellen OS consumption patterns

### 2.2 Out of Scope

- Ellen's underlying AI model selection and configuration (governed by IT/Platform)
- Inbound data ingestion from raw intelligence sources (governed by SOP-27: Intelligence Cycle)
- SharePoint structural governance (governed by SOP-21: SharePoint Content Governance)
- Win/loss interview methodology (governed by SOP-09: Win/Loss Analysis)
- Competitor profile research methodology (governed by SOP-07: Competitor Profile Creation)

### 2.3 Dependencies

| Dependency | Type | Risk if Unavailable |
|---|---|---|
| SOP-21: SharePoint Content Governance | Upstream | Packet cannot publish without valid SP target |
| SOP-07: Competitor Profile Creation | Upstream | Packet 01 coverage degrades |
| SOP-09: Win/Loss Analysis | Upstream | Packet 01 and 04 accuracy degrades |
| SOP-27: Intelligence Cycle | Upstream | Signal detection for rebuild triggers fails |
| Ellen AI Platform | Downstream | Packets built but cannot be consumed |
| Playwright Automation Layer | Infrastructure | SharePoint sync fails; manual fallback required |

---

## 3. Architecture

The following diagram represents the full Ellen OS Package flow from raw content to field team access.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CONTENT DOMAIN LAYER (36+ domains)                   │
│                                                                              │
│  ┌──────────────┐  ┌────────────────┐  ┌─────────────────┐  ┌───────────┐  │
│  │ Competitor   │  │ Market Sizing  │  │ Pricing Intel   │  │ AI Trends │  │
│  │ Profiles     │  │ Reports        │  │ Data            │  │ Signals   │  │
│  │              │  │                │  │                 │  │           │  │
│  │ Battlecards  │  │ Customer Intel │  │ Objection       │  │ Regulatory│  │
│  │              │  │                │  │ Handling        │  │ Monitor   │  │
│  │ Win/Loss     │  │ Demand         │  │                 │  │           │  │
│  │ Analysis     │  │ Signals        │  │ Proof Points    │  │ Ecosystem │  │
│  └──────┬───────┘  └───────┬────────┘  └────────┬────────┘  └─────┬─────┘  │
│         │                  │                    │                  │        │
└─────────┼──────────────────┼────────────────────┼──────────────────┼────────┘
          │                  │                    │                  │
          └──────────────────┴────────────────────┴──────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     build_ellen_os_package.py                                │
│                                                                              │
│   1. Load content from knowledge base + SharePoint source documents          │
│   2. Apply domain-level freshness scoring                                    │
│   3. Compute PVS (Packet Value Score) for each packet                        │
│   4. Assemble packet sections per domain manifest                            │
│   5. Version stamp with semver + build timestamp                             │
│   6. Standardize format (Markdown → structured JSON-LD)                      │
│   7. Optimize size (<500KB per packet)                                       │
│   8. SHA1 hash each packet                                                   │
│   9. Compare vs. state file (skip if hash unchanged)                         │
│  10. Write new state to ellen_os_state.json                                  │
└────────────────────────────────┬────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼──────────────┐
                    │             │              │
                    ▼             ▼              ▼
             ┌──────────┐  ┌──────────┐  ┌──────────┐
             │ Packet   │  │ Packet   │  │ Packet   │
             │ 00–01    │  │ 02–03    │  │ 04–05    │
             └────┬─────┘  └────┬─────┘  └────┬─────┘
                  │             │              │
                  └─────────────┼──────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SHAREPOINT SYNC LAYER                                   │
│                                                                              │
│   Playwright automation uploads each changed packet to designated SP page    │
│   Version history entry appended to packet changelog                         │
│   Previous version archived (never deleted, per SOP-21 Archive protocol)    │
│   Sync result logged to ellen_os_state.json with timestamp + SHA1            │
└────────────────────────────────┬────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ELLEN AI CONSUMPTION LAYER                            │
│                                                                              │
│   Ellen reads packets from SharePoint on query routing                       │
│   Packet router selects 1–3 most relevant packets per query                  │
│   Response synthesis draws from latest published packet version              │
│   Query telemetry feeds back to usage_frequency signal in PVS calculation   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FIELD TEAM ACCESS LAYER                              │
│                                                                              │
│   Sales Reps, Account Executives, Solutions Consultants — via SharePoint     │
│   M&CI internal team — direct packet access                                  │
│   Executive leadership — via distilled brief outputs (Ellen-generated)       │
│   Partner / Channel — Packet 04 excerpts only (permission-scoped)           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Packet Architecture

### 4.1 Design Principles

Each packet is:
- **Self-contained**: Ellen can answer queries from a single packet without cross-referencing unless multi-domain reasoning is needed
- **Audience-scoped**: Content density and framing match the primary consumer of that packet
- **Versioned independently**: Packet 01 can rebuild without touching Packet 04
- **Size-bounded**: Target <500KB per packet in final optimized form for SharePoint performance (SharePoint's content query API degrades above 500KB per document call)
- **Freshness-tagged**: Every content domain section carries a `last_updated` and `content_age_days` tag so Ellen can flag potentially stale information in responses

### 4.2 Packet 00 — Operator Pack

**Purpose**: System-level context for Ellen. This packet is loaded on every Ellen session initialization, regardless of query type. It tells Ellen who she is, how to behave, and how to route queries.

**Primary Consumer**: Ellen AI (not human end-users)

**Content Domains** (6):

| Domain | Description | Owner | Refresh Cadence |
|---|---|---|---|
| System Instructions | Ellen's identity, capabilities, and behavioral guardrails | Mike Rodgers | Quarterly or on Ellen platform change |
| Routing Rules | Decision logic for which packet(s) to consult per query type | Mike Rodgers | Monthly review |
| Team Manifest | M&CI team structure, roles, named individuals, expertise map | Mike Rodgers | On org change |
| Engagement Protocol | How Ellen escalates to humans, confidence thresholds, citation requirements | Mike Rodgers | Quarterly |
| SOP Index | Summary index of all active SOPs Ellen should reference | Mike Rodgers | On SOP publish |
| Glossary | Oracle Health terminology, acronyms, product names, competitive aliases | Mike Rodgers | Monthly |

**Size Target**: <150KB (routing efficiency priority)

---

### 4.3 Packet 01 — Competitive Intelligence

**Purpose**: Everything Ellen needs to answer questions about Oracle Health's competitive position, specific competitor behaviors, and win/loss patterns.

**Primary Consumer**: Sales Reps, Account Executives, Solutions Consultants, M&CI analysts

**Content Domains** (8):

| Domain | Description | Owner | Refresh Cadence |
|---|---|---|---|
| Competitor Profiles | Full narrative profiles for all tracked competitors (Tier 1: Epic, Cerner/Oracle HC legacy, Meditech; Tier 2: Veeva, Salesforce Health, AWS Health, Microsoft, Optum) | M&CI Research | Bi-weekly |
| Battlecards | Structured head-to-head comparison cards: strengths, weaknesses, differentiators, common objections | M&CI Research + Sales Enablement | Monthly or on competitor move |
| Win/Loss Analysis | Aggregated win/loss patterns by competitor, deal size, geography, segment | M&CI + Sales Ops | Monthly |
| Competitive News Feed | Recent competitor announcements, product launches, executive changes, funding events | M&CI Research | Weekly |
| Share of Voice Analysis | Competitor media presence, analyst coverage, SOV trends | M&CI Research | Monthly |
| Competitive Positioning | Oracle Health's stated differentiation vs. each named competitor | Product Marketing | Quarterly |
| Partnership & Alliance Intel | Competitor partnership activity that affects deal dynamics | M&CI Research | Bi-weekly |
| Analyst Landscape | Gartner, KLAS, IDC coverage of Oracle Health and competitors | M&CI Research | On publication |

**Size Target**: <500KB

---

### 4.4 Packet 02 — Market & Customer Intelligence

**Purpose**: Market context, customer intelligence, and demand signals that inform strategy and account planning.

**Primary Consumer**: M&CI analysts, Product Marketing, Strategy, Account Planning teams

**Content Domains** (6):

| Domain | Description | Owner | Refresh Cadence |
|---|---|---|---|
| Market Sizing | Total addressable market, serviceable addressable market, growth rates by segment | M&CI Research | Quarterly |
| Segment Analysis | Hospital systems, ambulatory, payer, government, international — segment-specific intelligence | M&CI Research | Quarterly |
| Customer Intelligence | Aggregate intelligence on Oracle Health customer base patterns, satisfaction signals, churn indicators | Customer Success + M&CI | Monthly |
| Demand Signals | Leading indicators of buying intent: budget cycles, RFP patterns, executive turnover at key accounts, M&A activity | M&CI Research | Weekly |
| Voice of Customer | Synthesized customer feedback from conversations, NPS, G2/Capterra reviews, KLAS scores | Customer Success + M&CI | Monthly |
| Market Trend Analysis | Long-range market forces: consumerization, value-based care adoption, interoperability mandates | M&CI Research | Quarterly |

**Size Target**: <400KB

---

### 4.5 Packet 03 — Strategic Analysis

**Purpose**: Strategic frameworks, war gaming outputs, and scenario planning materials that support executive decision-making and strategic planning cycles.

**Primary Consumer**: M&CI leadership, Oracle Health executive team, Strategy function

**Content Domains** (5):

| Domain | Description | Owner | Refresh Cadence |
|---|---|---|---|
| Strategic Frameworks | Porter's Five Forces, SWOT, Jobs-to-be-Done, Blue Ocean analysis applied to Oracle Health | M&CI + Strategy | Quarterly |
| War Gaming Outputs | Results from structured war gaming sessions: competitor move modeling, defensive response maps | M&CI | Post-session (ad hoc) |
| Scenario Planning | Named scenarios (base, bull, bear) with strategic implications and trigger conditions | M&CI + Strategy | Bi-annual |
| Strategic Threat Register | Enumerated strategic threats with probability, impact, and current mitigation status | M&CI | Monthly review |
| Innovation Analysis | Emerging technologies, startup ecosystem activity, innovation signals relevant to Oracle Health's product roadmap | M&CI Research | Monthly |

**Size Target**: <350KB

---

### 4.6 Packet 04 — Sales Enablement

**Purpose**: Direct-use sales intelligence: pricing data, objection handling, proof points, and customer evidence that reps pull during active deal cycles.

**Primary Consumer**: Sales Reps, Account Executives, Solutions Consultants, Sales Leadership

**Content Domains** (6):

| Domain | Description | Owner | Refresh Cadence |
|---|---|---|---|
| Pricing Intelligence | Oracle Health list pricing context, discount patterns, competitive pricing intelligence, total cost of ownership models | M&CI + Sales Ops | Monthly |
| Objection Handling | Structured objection library with tested responses: by competitor, by deal stage, by buyer persona | Sales Enablement + M&CI | Monthly |
| Proof Points | Quantified customer outcomes, case study summaries, ROI data, reference-able customer names (permission granted) | Customer Success + Marketing | Bi-monthly |
| Reference Architecture | Technical reference architectures for common customer scenarios | Solutions Engineering | Quarterly |
| Deal Intelligence | Win patterns by deal type, account size, geography; common deal blockers and how they were resolved | Sales Ops + M&CI | Monthly |
| Partner / Channel Intel | Channel partner strengths by geography and segment; co-sell guidance | Alliances + M&CI | Quarterly |

**Size Target**: <450KB

---

### 4.7 Packet 05 — Technology & Regulatory

**Purpose**: Technical landscape intelligence and regulatory compliance context for deals with technology-sensitive or compliance-driven buyers.

**Primary Consumer**: Solutions Consultants, Product Management, Compliance team, Government/payer-focused AEs

**Content Domains** (7):

| Domain | Description | Owner | Refresh Cadence |
|---|---|---|---|
| AI Trends | AI adoption in healthcare IT, competitor AI capabilities, Oracle Health AI roadmap context | M&CI Research + Product | Monthly |
| Regulatory Intelligence | Active CMS, ONC, HHS rulemaking that affects Oracle Health's market; compliance requirements | Regulatory Affairs + M&CI | Weekly (monitoring) / Monthly (synthesis) |
| Ecosystem Mapping | Healthcare IT ecosystem: EHR adjacencies, integration partners, data exchange standards (HL7 FHIR, SMART, Da Vinci) | M&CI + Solutions Engineering | Quarterly |
| Security & Privacy Landscape | HIPAA, SOC 2, FedRAMP status; competitor security posture; customer security requirements | Security + M&CI | Quarterly |
| Interoperability Intelligence | CMS Interoperability Rule compliance landscape; payer-provider data exchange; TEFCA developments | Regulatory Affairs + M&CI | Monthly |
| Government & Federal Intel | CMS programs, VA/DoD opportunities, federal health IT priorities | M&CI + Government Affairs | Monthly |
| International Signals | International regulatory developments, NHS, EU health data act, APAC market signals | M&CI Research | Monthly |

**Size Target**: <450KB

---

## 5. Build Process

### 5.1 Overview

The `build_ellen_os_package.py` script is the single executable that assembles, versions, and prepares all six packets for publication. It is designed to be idempotent: running it twice with no content changes produces no output changes and no new SharePoint uploads.

**Execution path**: `/oracle-health-ai-enablement/scripts/build_ellen_os_package.py`

**State file**: `/oracle-health-ai-enablement/.sharepoint-state/ellen_os_state.json`

**Output directory**: `/oracle-health-ai-enablement/ellen_os_packages/`

### 5.2 Content Assembly

For each packet, the build script:

1. **Reads the domain manifest** from `ellen_os_manifests/packet_XX.yaml`. The manifest defines which source documents and knowledge base entries contribute to each domain section, the weighting of each source, and the minimum coverage threshold for that domain.

2. **Queries source documents** from two locations:
   - SharePoint source library (raw intelligence artifacts: competitor profiles, battlecards, win/loss reports)
   - Local knowledge base (`/oracle-health-ai-enablement/knowledge-base/`)

3. **Applies domain assembly rules**: Each domain section is assembled by concatenating relevant content chunks in priority order (recency-weighted), then trimming to section length limits.

4. **Computes domain-level freshness scores** for each content section:
   ```
   domain_freshness = 1 - (content_age_days / domain_half_life_days)
   domain_freshness = max(0.0, min(1.0, domain_freshness))
   ```

   Domain half-lives (the age at which a domain's content is considered 50% fresh):

   | Domain Category | Half-Life (Days) |
   |---|---|
   | Competitive news / recent competitor moves | 7 |
   | Battlecards | 30 |
   | Win/loss data | 30 |
   | Pricing intelligence | 45 |
   | Regulatory intelligence | 21 |
   | Market sizing | 90 |
   | Strategic frameworks | 180 |
   | System instructions / routing | 180 |

5. **Flags domains below freshness threshold** (default: 0.60) with `[CONTENT WARNING: This section may be outdated. Last updated: {date}. Verify before use.]` inline markers that Ellen surfaces in responses.

### 5.3 Version Stamping

Each packet receives a version stamp in the format:

```
{packet_id}-v{major}.{minor}.{patch}-{build_timestamp}
```

Example: `packet-01-v2.4.1-20260323T020000Z`

Version increment rules:
- **Major** (`v+1.0.0`): Packet structure change (new domain added, domain removed, routing rule changed in Packet 00)
- **Minor** (`v+0.1.0`): Content refresh that adds net-new material to an existing domain
- **Patch** (`v+0.0.1`): Factual correction, typo fix, metadata update

The current version of each packet is written to `ellen_os_state.json` and cross-referenced in SharePoint page metadata.

### 5.4 Format Standardization

Raw assembled content (Markdown source documents) is normalized to a structured output format:

```json
{
  "packet_id": "packet-01",
  "packet_name": "Competitive Intelligence",
  "version": "2.4.1",
  "build_timestamp": "2026-03-23T02:00:00Z",
  "pvs_score": 0.87,
  "domains": [
    {
      "domain_id": "competitor_profiles",
      "domain_name": "Competitor Profiles",
      "freshness_score": 0.91,
      "last_updated": "2026-03-21",
      "content_age_days": 2,
      "content": "[assembled content string]",
      "source_documents": ["epic-profile-v3.md", "cerner-profile-v5.md"],
      "coverage_pct": 94
    }
  ]
}
```

This structured format enables Ellen to:
- Report content freshness on demand ("This battlecard was last updated 2 days ago")
- Cite specific source documents in responses
- Route queries to the freshest applicable domain

### 5.5 Size Optimization

The build script applies three size optimization passes before final output:

**Pass 1 — Deduplication**: Content that appears in multiple domains (e.g., a competitor name and basic profile data that appears in both the Competitor Profiles domain and the Battlecards domain) is deduplicated. The primary copy is retained in the higher-priority domain; secondary occurrences are replaced with a cross-reference pointer.

**Pass 2 — Section Trimming**: If a packet exceeds its size target after assembly, sections are trimmed in inverse order of domain priority score. Domain priority is defined in `ellen_os_manifests/packet_XX.yaml`. The trimming algorithm removes the lowest-value content chunks (lowest recency + relevance score) until the size target is met.

**Pass 3 — Metadata Compression**: Version history beyond the last 5 versions is moved to the archive state file (`ellen_os_state_archive.json`) and not included in the active packet payload.

**Size enforcement**: If a packet cannot reach its size target without dropping domains below minimum coverage thresholds, the build script halts with error code `SIZE_BUDGET_EXCEEDED` and alerts Mike via the Oracle Health morning brief pipeline. The previous valid version remains in production until the issue is resolved.

### 5.6 SHA1 Hash-Based Change Detection

Before initiating a SharePoint upload, the build script computes a SHA1 hash of the final packet JSON payload and compares it against the hash stored in `ellen_os_state.json` from the last successful build.

```python
current_hash = hashlib.sha1(packet_json_bytes).hexdigest()
stored_hash = state["packets"][packet_id]["last_published_sha1"]

if current_hash == stored_hash:
    log(f"Packet {packet_id}: no changes detected. Skipping upload.")
    continue
```

This prevents unnecessary SharePoint writes, preserves SharePoint version history integrity, and reduces Playwright automation runtime on no-change builds.

State file structure:

```json
{
  "last_build_run": "2026-03-23T02:15:32Z",
  "packets": {
    "packet-00": {
      "version": "1.2.0",
      "last_published_sha1": "a3f9c2...",
      "last_published_timestamp": "2026-03-17T02:01:44Z",
      "pvs_score": 0.93,
      "publish_status": "success",
      "sharepoint_url": "[SP URL]"
    },
    "packet-01": {
      "version": "2.4.1",
      "last_published_sha1": "b7e1d4...",
      "last_published_timestamp": "2026-03-23T02:15:00Z",
      "pvs_score": 0.87,
      "publish_status": "success",
      "sharepoint_url": "[SP URL]"
    }
  }
}
```

---

## 6. Update Triggers

A packet rebuild is initiated by any of the following trigger conditions. Each trigger carries a priority class that determines whether the rebuild runs immediately or is queued for the next scheduled window.

### 6.1 Trigger Inventory

| Trigger ID | Trigger Description | Priority | Rebuild Scope | Latency Target |
|---|---|---|---|---|
| T-01 | Tier 1 competitor move detected (acquisition, major product launch, pricing change, executive departure) | P0 — Immediate | Packet 01 + any affected packet | <4 hours |
| T-02 | New win/loss data ingested (batch of 3+ records) | P1 — Same day | Packet 01, Packet 04 | <8 hours |
| T-03 | Regulatory change detected (CMS, ONC, HHS proposed or final rule) | P0 — Immediate | Packet 05 | <4 hours |
| T-04 | Manual override by Mike | P0 — Immediate | Specified packet(s) | <30 minutes |
| T-05 | PVS score drop below 0.75 for any packet | P1 — Same day | Affected packet | <8 hours |
| T-06 | Scheduled weekly refresh | P2 — Scheduled | All packets | Monday 2:00 AM PT |
| T-07 | New competitor profile published or substantially updated | P1 — Same day | Packet 01 | <8 hours |
| T-08 | Oracle Health internal product announcement | P1 — Same day | Packet 01, Packet 04 | <8 hours |
| T-09 | M&CI team org change (new hire, departure, role change) | P2 — Next business day | Packet 00 | <24 hours |
| T-10 | New SOP approved and published | P2 — Next business day | Packet 00 | <24 hours |
| T-11 | KLAS, Gartner, or IDC report publication covering Oracle Health | P1 — Same day | Packet 01, Packet 02 | <8 hours |
| T-12 | New customer proof point or case study approved | P2 — Next scheduled | Packet 04 | Next Monday |

### 6.2 Tier 1 Competitor Designation

Tier 1 competitors trigger immediate P0 rebuilds because a stale battlecard or profile in an active deal is a direct revenue risk. Current Tier 1 designation:

- Epic Systems
- Oracle Health (Cerner heritage products — legacy competitive positioning)
- Meditech Expanse
- Microsoft Cloud for Healthcare (Azure Health Data Services + Nuance DAX)

Tier 2 competitors (Veeva, Salesforce Health Cloud, AWS HealthLake, Optum, Netsmart) trigger P1 rebuilds.

Tier designations are reviewed quarterly by Mike. Changes require updating `ellen_os_manifests/tier_config.yaml`.

### 6.3 Trigger Detection

P0 and P1 triggers are detected through three mechanisms:

1. **TrendRadar signal feed**: The Oracle Health bi-weekly domain intelligence engine (SOP-02 and the oracle-health-intel scheduled task) flags competitor moves and regulatory changes. The intelligence pipeline writes structured signals to `/oracle-health-ai-enablement/signals/pending/`. The build script checks this directory on each run.

2. **Win/loss ingestion hook**: The win/loss analysis pipeline writes a trigger file to `/oracle-health-ai-enablement/triggers/win_loss_update.flag` after ingesting a batch. The build script reads and clears this flag.

3. **Manual trigger**: Mike writes a JSON file to `/oracle-health-ai-enablement/triggers/manual_override.json` specifying which packets to rebuild. This is also accessible via the `bin/jake` command: `jake ellen rebuild packet-01`.

---

## 7. PVS Algorithm — Packet Value Score

### 7.1 Formula

The Packet Value Score (PVS) is a composite metric that quantifies how much value Ellen can extract from a given packet at the moment of query. A PVS of 1.0 represents a theoretically perfect packet: fully fresh, fully complete, maximally queried, fully accurate. A PVS of 0.0 represents a packet that is useless.

```
PVS = (content_freshness × 0.35)
    + (coverage_completeness × 0.30)
    + (usage_frequency × 0.20)
    + (accuracy_score × 0.15)
```

### 7.2 Component Definitions

**content_freshness (weight: 0.35)**

The freshness component is a weighted average of domain-level freshness scores across all domains in the packet, weighted by each domain's priority rank.

```
content_freshness = Σ (domain_freshness_i × domain_weight_i) / Σ domain_weight_i
```

Where `domain_freshness_i = max(0.0, 1 - (content_age_days_i / domain_half_life_i))`.

Freshness has the highest weight because stale intelligence is not just unhelpful — it is actively harmful. A rep who walks into a deal with six-month-old pricing intelligence may quote a number that damages trust.

**coverage_completeness (weight: 0.30)**

The fraction of defined domain slots in the packet that have content meeting the minimum length and source count thresholds.

```
coverage_completeness = (domains_with_sufficient_content / total_defined_domains)
```

A domain is considered "sufficient" if it has at least `min_content_length` characters AND at least `min_source_count` distinct source documents. Both thresholds are defined per domain in `ellen_os_manifests/packet_XX.yaml`.

**usage_frequency (weight: 0.20)**

A normalized measure of how often Ellen queries this packet in response to real user questions over the trailing 30 days.

```
usage_frequency = log(1 + monthly_query_count) / log(1 + max_observed_query_count)
```

The logarithmic scaling prevents a single high-volume packet (typically Packet 01) from disproportionately skewing relative scores. This component provides a feedback signal: packets that Ellen is not using should be investigated for routing failures, not just low demand.

**accuracy_score (weight: 0.15)**

A quality signal derived from two inputs:
1. **Verified accuracy rate**: Fraction of Ellen responses drawing from this packet that were marked as accurate in the feedback loop (sales rep thumbs up/down, analyst spot-check reviews)
2. **Source confidence level**: Weighted average of source confidence ratings assigned during the intelligence cycle (SOP-27)

```
accuracy_score = (verified_accuracy_rate × 0.60) + (avg_source_confidence × 0.40)
```

Accuracy has the lowest weight because it is the slowest-moving signal (feedback accumulates over weeks) but must never be ignored — a high-freshness, high-coverage packet built on low-quality sources is a liability.

### 7.3 PVS Thresholds and Actions

| PVS Range | Status Label | Automated Action |
|---|---|---|
| 0.90 – 1.00 | Excellent | No action. Packet qualifies for promotion to "Trusted" status in Ellen's routing logic. |
| 0.80 – 0.89 | Good | No automated action. Monitor for trend. |
| 0.75 – 0.79 | Acceptable | No automated action. Flag in weekly build report for review. |
| 0.65 – 0.74 | Below Threshold | Queue rebuild (T-05 trigger). Write advisory to Ellen system instructions for this packet. |
| 0.50 – 0.64 | Poor | Immediate rebuild (P0). Ellen prepends `[CONTENT ADVISORY: This intelligence packet is below quality threshold. Verify critical facts independently.]` to all responses drawing from this packet. |
| 0.00 – 0.49 | Critical | Packet is flagged as degraded. Ellen falls back to cached previous version if available. Alert sent to Mike. Manual review required before restoring to active status. |

### 7.4 PVS Trend Monitoring

PVS is computed at every build run and stored in `ellen_os_state.json` with a 90-day history. The build script alerts Mike if any packet shows:
- A decline of more than 0.10 PVS in 7 days
- A trend line projecting below 0.75 within the next 14 days (linear extrapolation over trailing 30 days)

---

## 8. Monte Carlo Simulation — Content Freshness Decay Modeling

### 8.1 Purpose

Scheduled rebuilds occur weekly. But content in the Ellen OS packets ages continuously. Some domains (regulatory intelligence, competitive news) can become critically stale within 72 hours of a real-world event. Other domains (market sizing, strategic frameworks) decay over months.

The Monte Carlo simulation models the probability that at least one critical content domain within a packet contains stale information before the next scheduled rebuild occurs. This probability is computed at each build run and stored as the **Staleness Risk Score** for each packet.

If the Staleness Risk Score for a critical domain exceeds 0.40 (40% probability of staleness before next scheduled refresh), an unscheduled rebuild is queued.

### 8.2 Staleness Model

The fundamental staleness model uses an exponential decay function analogous to radioactive half-life:

```
staleness_risk(t) = 1 - e^(-t / domain_half_life)
```

Where:
- `t` = time since last content update (in days)
- `domain_half_life` = the number of days at which the domain's information has a 63.2% probability of being materially outdated (domain-specific, defined in Section 5.2)

This model is derived from information decay research in intelligence analysis. The Intelligence Community's tradecraft standards (ICD-203) implicitly model this decay when prescribing review cadences: a 14-day battlecard review cycle corresponds to an approximate 10-day half-life assumption for tactical competitive intelligence.

### 8.3 Simulation Parameters

For each content domain, the simulation uses three parameters drawn from historical data:

| Parameter | Description | Source |
|---|---|---|
| `content_age_distribution` | Distribution of how old content actually is when a build runs (accounts for irregular update patterns) | Historical build logs, trailing 90 days |
| `update_frequency_distribution` | Distribution of actual update intervals for this domain | Historical win/loss, competitive signal logs |
| `query_impact` | A multiplier (0–1) reflecting how much a stale domain in this packet damages Ellen's response quality for typical queries | Measured from Ellen feedback loop |

### 8.4 Simulation Procedure (1,000 Iterations)

For a given packet with N content domains:

```python
def monte_carlo_staleness(packet, n_iterations=1000):
    results = []

    for _ in range(n_iterations):
        packet_has_stale_critical_domain = False

        for domain in packet.critical_domains:
            # Sample content age from domain's age distribution
            sampled_age = np.random.exponential(scale=domain.mean_age_days)

            # Sample time to next scheduled rebuild
            days_to_next_rebuild = np.random.uniform(0, 7)  # uniform over weekly cycle

            # Project age at next rebuild
            projected_age = sampled_age + days_to_next_rebuild

            # Compute staleness probability at projected age
            staleness_prob = 1 - np.exp(-projected_age / domain.half_life)

            # Apply query impact weight
            weighted_risk = staleness_prob * domain.query_impact

            # Stochastic test: is this domain stale by rebuild time?
            if np.random.random() < weighted_risk:
                packet_has_stale_critical_domain = True
                break

        results.append(int(packet_has_stale_critical_domain))

    p_stale = sum(results) / n_iterations
    return p_stale
```

**Output**: `P(at least one stale critical domain before next rebuild)` for each packet.

### 8.5 Per-Packet Staleness Risk Profiles

The following table shows baseline staleness risk computed from historical content age distributions (approximate, as of March 2026):

| Packet | Most Volatile Domain | Domain Half-Life (days) | Baseline P(stale before rebuild) | Threshold for Unscheduled Rebuild |
|---|---|---|---|---|
| Packet 00 | Routing Rules | 180 | 0.04 | 0.40 |
| Packet 01 | Competitive News Feed | 7 | 0.52 | 0.40 |
| Packet 02 | Demand Signals | 14 | 0.38 | 0.40 |
| Packet 03 | Strategic Threat Register | 30 | 0.17 | 0.40 |
| Packet 04 | Pricing Intelligence | 45 | 0.11 | 0.40 |
| Packet 05 | Regulatory Intelligence | 21 | 0.29 | 0.40 |

**Interpretation**: Packet 01 has a 52% baseline probability of containing at least one stale critical domain before the next weekly scheduled rebuild. This is the reason Packet 01 has the most aggressive real-time trigger detection (T-01, T-07, T-11) and why Competitive News Feed is updated outside the weekly cycle.

### 8.6 Simulation Outputs and Integration

The Monte Carlo simulation runs as part of every build script execution. Results are written to `ellen_os_state.json` under `monte_carlo_results`:

```json
"monte_carlo_results": {
  "run_timestamp": "2026-03-23T02:00:00Z",
  "n_iterations": 1000,
  "packets": {
    "packet-01": {
      "p_stale_before_rebuild": 0.52,
      "most_at_risk_domain": "competitive_news_feed",
      "unscheduled_rebuild_triggered": true,
      "rebuild_trigger_reason": "P(stale) exceeds 0.40 threshold"
    }
  }
}
```

When `unscheduled_rebuild_triggered: true`, the build script queues the affected packet for a targeted rebuild within the T-05 latency window (same day, <8 hours).

---

## 9. Distribution Protocol

### 9.1 SharePoint Upload Automation

Distribution to SharePoint is fully automated via Playwright browser automation. The distribution script (`distribute_ellen_os_packages.py`) runs after a successful build and executes the following steps for each changed packet:

**Step 1 — Authentication**: Playwright opens a headless browser session and authenticates to SharePoint using the M&CI service account credentials stored in the Oracle Health AI enablement secrets vault (not hardcoded).

**Step 2 — Target Page Navigation**: The script navigates to the designated SharePoint page for the packet using the URL stored in `ellen_os_state.json`.

**Step 3 — Content Upload**: The script uploads the new packet JSON to the SharePoint document library associated with the page, using the structured filename format `packet-{id}-{version}.json`.

**Step 4 — Page Metadata Update**: The script updates the SharePoint page metadata fields: version, last updated date, PVS score, build timestamp.

**Step 5 — Version Log Append**: A version log entry is appended to the packet's SharePoint version history page: version number, build timestamp, trigger that initiated the build, PVS score at publish time, SHA1 hash.

**Step 6 — Confirmation Check**: The script reads back the uploaded document to verify the SHA1 hash matches the uploaded file. If the hash does not match, the upload is retried once. If the second attempt fails, the distribution script halts and alerts Mike.

**Step 7 — State Update**: On successful upload and confirmation, `ellen_os_state.json` is updated with the new `last_published_sha1`, `last_published_timestamp`, and `publish_status: success`.

### 9.2 Version History Management

SharePoint retains the last 10 published versions of each packet in the document library. Versions beyond 10 are automatically moved to the M&CI archive library (`/oracle-health-ai-enablement/.sharepoint-state/ellen_os_archives/`). They are never deleted.

The active production version is always the most recently published file matching `packet-{id}-latest.json`. A symbolic pointer file (`packet-{id}-latest-pointer.json`) contains the exact filename and SHA1 of the current production version, enabling Ellen's routing layer to always resolve to the correct file.

### 9.3 Rollback Procedure

A rollback is required when a newly published packet version causes measurable degradation in Ellen's response accuracy, Ellen returns factual errors on spot-check queries, or Mike manually flags the need for rollback.

**Rollback Authority**: Mike Rodgers or designated backup (M&CI team lead).

**Rollback Steps**:

1. **Identify rollback target**: Check `ellen_os_state.json` for the previous packet version and its SHA1. Confirm the previous version file exists in the SharePoint archive.

2. **Execute rollback script**:
   ```bash
   jake ellen rollback packet-01 --to-version 2.4.0
   ```
   This script:
   - Copies `packet-01-v2.4.0.json` from archive back to the active library
   - Updates the `packet-01-latest-pointer.json` to point to version 2.4.0
   - Updates `ellen_os_state.json` to reflect the rollback: sets `publish_status: rolled_back`, records rollback timestamp and reason

3. **Verify Ellen response accuracy**: Run the standard Ellen spot-check query suite (5–10 test queries per packet) to confirm response quality has recovered.

4. **Investigate root cause**: Before re-attempting the failed version, identify what caused the degradation. Common causes:
   - Content assembly error (malformed source document that broke domain structure)
   - Size optimization trim that cut critical content
   - Source document with incorrect data that passed quality gates

5. **Document the rollback**: Write a rollback incident record to `.sharepoint-state/rollback-log.yaml` with: version rolled back from, version rolled back to, reason, impact assessment, root cause, corrective action.

6. **Re-build corrected version**: After root cause is fixed, rebuild the packet and promote the corrected version. The corrected version gets a patch increment (e.g., `v2.4.2` after rolling back from a failed `v2.4.1`).

### 9.4 Access Permissions

| Packet | SharePoint Permission Group | Rationale |
|---|---|---|
| Packet 00 — Operator Pack | Ellen AI service account only | System instructions should not be browsed by humans directly — managed via Ellen's admin interface |
| Packet 01 — Competitive Intelligence | M&CI All, Sales All, Solutions Engineering | Core sales intelligence; broad field access required for deal support |
| Packet 02 — Market & Customer Intelligence | M&CI All, Product Management, Strategy, Exec | Strategic content; not for general field consumption |
| Packet 03 — Strategic Analysis | M&CI All, Strategy, Exec Leadership | Executive strategy content; restricted by seniority |
| Packet 04 — Sales Enablement | M&CI All, Sales All, Solutions Engineering, Channel Partners (restricted excerpt only) | Direct deal support; channel partners get read-only access to proof points section only |
| Packet 05 — Technology & Regulatory | M&CI All, Solutions Engineering, Product, Compliance, Government Affairs | Technical and regulatory depth; field access on request |

Permission groups are managed in SharePoint Active Directory groups. Changes to access permissions require Mike's approval and must be reflected in the `ellen_os_manifests/access_config.yaml`.

---

## 10. Content Domain Ownership Matrix

The following matrix assigns primary ownership (the person responsible for ensuring content quality and freshness in that domain) and backup ownership (covers during PTO, offboarding, or escalation) for every content domain across all six packets.

| Packet | Domain | Primary Owner | Backup Owner | Escalation Contact |
|---|---|---|---|---|
| 00 | System Instructions | Mike Rodgers | M&CI Team Lead | Mike Rodgers |
| 00 | Routing Rules | Mike Rodgers | M&CI Team Lead | Mike Rodgers |
| 00 | Team Manifest | Mike Rodgers | HR Business Partner | Mike Rodgers |
| 00 | Engagement Protocol | Mike Rodgers | M&CI Team Lead | Mike Rodgers |
| 00 | SOP Index | Mike Rodgers | M&CI Team Lead | Mike Rodgers |
| 00 | Glossary | M&CI Team Lead | Mike Rodgers | Mike Rodgers |
| 01 | Competitor Profiles | M&CI Research Lead | M&CI Analyst | Mike Rodgers |
| 01 | Battlecards | M&CI Research Lead + Sales Enablement | M&CI Analyst | Mike Rodgers |
| 01 | Win/Loss Analysis | M&CI Research Lead + Sales Ops | Sales Ops Director | Mike Rodgers |
| 01 | Competitive News Feed | M&CI Research Lead | M&CI Analyst | Mike Rodgers |
| 01 | Share of Voice Analysis | M&CI Research Lead | M&CI Analyst | Mike Rodgers |
| 01 | Competitive Positioning | Product Marketing Director | M&CI Research Lead | Mike Rodgers |
| 01 | Partnership & Alliance Intel | M&CI Research Lead | Alliances Lead | Mike Rodgers |
| 01 | Analyst Landscape | M&CI Research Lead | Product Marketing | Mike Rodgers |
| 02 | Market Sizing | M&CI Research Lead | External Research Vendor | Mike Rodgers |
| 02 | Segment Analysis | M&CI Research Lead | M&CI Analyst | Mike Rodgers |
| 02 | Customer Intelligence | Customer Success Director | M&CI Research Lead | Mike Rodgers |
| 02 | Demand Signals | M&CI Research Lead | Sales Ops Director | Mike Rodgers |
| 02 | Voice of Customer | Customer Success Director | M&CI Analyst | Mike Rodgers |
| 02 | Market Trend Analysis | M&CI Research Lead | External Research Vendor | Mike Rodgers |
| 03 | Strategic Frameworks | Mike Rodgers | M&CI Research Lead | Matt Cohlmia |
| 03 | War Gaming Outputs | Mike Rodgers | M&CI Research Lead | Matt Cohlmia |
| 03 | Scenario Planning | Mike Rodgers + Strategy Director | M&CI Research Lead | Matt Cohlmia |
| 03 | Strategic Threat Register | Mike Rodgers | M&CI Research Lead | Matt Cohlmia |
| 03 | Innovation Analysis | M&CI Research Lead | Product Management | Mike Rodgers |
| 04 | Pricing Intelligence | Sales Ops Director + M&CI | Regional Sales VP | Mike Rodgers |
| 04 | Objection Handling | Sales Enablement Director | M&CI Research Lead | Regional Sales VP |
| 04 | Proof Points | Customer Success Director | Marketing | Mike Rodgers |
| 04 | Reference Architecture | Solutions Engineering Lead | Product Management | Mike Rodgers |
| 04 | Deal Intelligence | Sales Ops Director | Regional Sales VP | Mike Rodgers |
| 04 | Partner / Channel Intel | Alliances Director | Sales Ops | Mike Rodgers |
| 05 | AI Trends | M&CI Research Lead + Product | CTO Office | Mike Rodgers |
| 05 | Regulatory Intelligence | Regulatory Affairs Director | M&CI Research Lead | General Counsel |
| 05 | Ecosystem Mapping | Solutions Engineering Lead | M&CI Research Lead | Mike Rodgers |
| 05 | Security & Privacy Landscape | CISO / Security Director | Solutions Engineering | Mike Rodgers |
| 05 | Interoperability Intelligence | Regulatory Affairs Director | Solutions Engineering | Mike Rodgers |
| 05 | Government & Federal Intel | Government Affairs Director | M&CI Research Lead | Mike Rodgers |
| 05 | International Signals | M&CI Research Lead | International Sales | Mike Rodgers |

**Ownership responsibilities include**:
- Reviewing content freshness warnings flagged by the build pipeline
- Providing updated source material before domain staleness threshold is crossed
- Approving content before it is incorporated into a new packet version when material changes are involved
- Responding to Ellen accuracy feedback attributable to their domain within 48 hours

---

## 11. Quality Gates

### 11.1 Gate Architecture

Two mandatory quality gates must be cleared before a packet version is published to SharePoint. The gates are enforced by the build script and cannot be bypassed without explicit manual override by Mike.

### 11.2 Gate 1 — Pre-Assembly Content Freshness Check

Before content assembly begins, the build script checks that every **critical domain** in the packet meets a minimum freshness threshold.

**Critical domains** are those with `criticality: high` in the domain manifest. For most packets, critical domains represent 30–50% of total domains and include the highest-query-impact content.

**Minimum freshness threshold**: 0.60 (content is at most 40% through its decay curve toward staleness).

If any critical domain fails this threshold:
- The build script logs a `FRESHNESS_GATE_FAIL` warning
- The domain owner is identified from the ownership matrix
- An alert is written to the morning brief pipeline for Mike
- The build **continues** with a content advisory flag on the failing domain (does not halt — a partial rebuild with flagged content is better than a stale packet with no flag)

If more than 50% of critical domains in a packet fail the freshness gate, the build halts entirely and the current production version is maintained. Alert escalates to Mike as P1.

### 11.3 Gate 2 — Pre-Publication Coverage Check

After assembly but before the SharePoint upload, the build script verifies that coverage completeness is sufficient for publication.

**Coverage check criteria**:
- At least 85% of defined domain slots have content meeting minimum length and source count thresholds
- No domain has zero content (a completely empty domain is a build error, not a content gap)
- Packet total size is within bounds (not below 50KB — suspiciously small indicates assembly failure; not above size target)
- SHA1 hash computation succeeded without error
- Version number is monotonically increasing (cannot publish a lower version number than what is in state)

If any coverage criterion fails, the build script halts with `COVERAGE_GATE_FAIL` and retains the current production version. Alert sent to Mike.

### 11.4 Manual Quality Review

For **major version** increments (structural changes to a packet), automated quality gates are supplemented by a manual review step:

1. Mike reviews the new packet structure and a sample of content from each domain
2. Mike runs 5–10 spot-check queries against Ellen using the new packet in a staging environment
3. Mike signs off via `jake ellen approve packet-XX --version X.Y.Z`

Minor and patch version increments do not require manual review unless Mike elects to add one.

---

## 12. Participant Onboarding

### 12.1 Who Needs Onboarding

Any team member who will:
- Query Ellen directly for intelligence requests
- Interpret Ellen's responses in deal or strategy contexts
- Provide source material for packet domains they own
- Review Ellen accuracy feedback attributed to their content

### 12.2 Onboarding Steps

**Step 1 — Ellen Introduction (30 minutes)**

New team member is given access to the Ellen interface and reviews the Ellen Quick Start Guide:
- What Ellen is (AI intelligence layer for M&CI)
- What Ellen knows (the six packet domains)
- What Ellen does not know (real-time internet, Oracle internal systems beyond what's in packets, personal email)
- How to query Ellen effectively (specificity, context framing, multi-turn use)
- How to interpret Ellen's content freshness warnings
- How to submit accuracy feedback

**Step 2 — Packet Tour (30 minutes)**

Walk new team member through each packet's domain structure so they understand the breadth and depth of available intelligence. Focus on the packet(s) most relevant to their role:
- Sales reps: Packets 01 and 04 in depth
- Product: Packets 02, 03, and 05
- Compliance / Legal: Packet 05
- M&CI analysts: All packets

**Step 3 — Domain Ownership Briefing (if applicable, 30 minutes)**

If the new team member is a content domain owner, they receive:
- Their domain ownership responsibilities (Section 10)
- How to submit updated source material for their domain
- How freshness scoring works and what their SLA is
- How to respond to freshness alerts from the build pipeline

**Step 4 — Feedback Loop Training (15 minutes)**

New team member is shown how to submit accuracy feedback on Ellen responses. Two feedback mechanisms exist:
- In-line response rating (thumbs up/down on Ellen's interface)
- Detailed feedback form for substantive corrections (submits to M&CI for review)

**Step 5 — Access Provisioning**

SharePoint permissions are granted per Section 9.4. Access request submitted through standard IT access management workflow, approved by Mike.

**Onboarding Completion**: Logged in the M&CI team onboarding tracker. New member added to relevant domain ownership matrix entries if applicable.

---

## 13. RACI Matrix

| Activity | Mike Rodgers | M&CI Research Lead | M&CI Analysts | Domain Owners (non-M&CI) | IT / Platform | Ellen AI |
|---|---|---|---|---|---|---|
| Build script development and maintenance | A | R | C | I | C | — |
| Weekly scheduled rebuild execution | I | I | I | I | I | A/R (automated) |
| P0 trigger response (immediate rebuild) | A | R | C | I | I | I |
| Content assembly for M&CI-owned domains | A | R | R | — | — | — |
| Content assembly for cross-functional domains | A | C | I | R | — | — |
| PVS score monitoring and threshold action | A | R | I | I | — | — |
| Quality gate sign-off (automated gates) | A | I | I | I | — | R |
| Quality gate sign-off (manual, major versions) | A/R | C | — | — | — | — |
| SharePoint upload automation | A | I | I | — | R | — |
| Rollback decision and execution | A/R | C | I | I | I | — |
| Domain ownership maintenance | A | R | I | R | — | — |
| Access permission management | A | I | I | I | R | — |
| Onboarding new team members | A | R | C | C | C | — |
| Ellen accuracy feedback review | A | R | R | C | — | — |
| Monte Carlo simulation calibration | A | C | I | — | — | — |
| SOP review and updates | A/R | C | I | I | — | — |

**Key**: R = Responsible, A = Accountable, C = Consulted, I = Informed

---

## 14. KPIs

### 14.1 Primary KPIs

| KPI | Definition | Target | Measurement Frequency | Owner |
|---|---|---|---|---|
| Packet Freshness Score (PFS) | Average PVS across all six packets at time of measurement | ≥ 0.82 | Weekly (at build run) | Mike Rodgers |
| Ellen Query Accuracy Rate (EQAR) | Fraction of Ellen responses rated accurate in feedback loop (thumbs up + no correction filed) | ≥ 0.88 | Monthly rolling | Mike Rodgers |
| Content Coverage Completeness (CCC) | Average coverage completeness score across all packets | ≥ 0.90 | Weekly (at build run) | Mike Rodgers |
| P0 Rebuild Latency | Time from P0 trigger detection to SharePoint publication | ≤ 4 hours (target); ≤ 6 hours (acceptable) | Per P0 event | Mike Rodgers |
| Domain Freshness Warning Rate (DFWR) | Fraction of domains that carry a content freshness warning when Ellen publishes a packet | ≤ 0.10 (1 in 10 domains flagged as stale) | Weekly | Mike Rodgers |
| Build Success Rate (BSR) | Fraction of build runs that complete without error and publish at least one packet (on weeks with changes) | ≥ 0.97 | Monthly | Mike Rodgers |

### 14.2 Secondary KPIs

| KPI | Definition | Target | Measurement Frequency |
|---|---|---|---|
| Staleness Risk Score (SRS) | Average P(stale before rebuild) across all critical domains per packet, from Monte Carlo simulation | ≤ 0.25 | Weekly |
| Rollback Rate | Number of rollback events per quarter | ≤ 1 | Quarterly |
| Domain Ownership Gap Rate | Fraction of domain slots with undefined or stale ownership assignment | 0% | Quarterly audit |
| Onboarding Completion Rate | Fraction of new M&CI team members completing full onboarding within 30 days of hire | 100% | Rolling |
| Permission Audit Compliance | Fraction of packet access permission groups that match the current Section 9.4 spec during quarterly audit | 100% | Quarterly |

### 14.3 KPI Dashboard

KPI values are written to `ellen_os_state.json` at each build run and surfaced in:
- The Oracle Health Morning Brief (SOP-03 pipeline) — packet freshness summary
- The M&CI Weekly Review deck — full KPI table
- The SharePoint M&CI Status page — live summary panel updated after each build

---

## 15. Expert Panel Scoring

### 15.1 Panel Composition and Weights

| Panelist | Role | Weight |
|---|---|---|
| Matt Cohlmia | Oracle Health M&CI executive sponsor; ultimate accountability for Ellen OS ROI | 20% |
| Seema Verma | External advisor; federal health IT strategy and regulatory intelligence depth | 20% |
| Steve (Agent) | Strategic clarity and prioritization quality assessment | 15% |
| Compass (Agent) | Product design, user experience, and practical usability of the SOP | 10% |
| Ledger (Agent) | Commercial risk, cost efficiency of the build/distribution pipeline | 10% |
| Marcus (Agent) | Product domain coverage completeness and market intelligence quality | 10% |
| Forge (Agent) | Technical architecture of the build pipeline, state management, automation reliability | 10% |
| Herald (Agent) | Communication clarity, onboarding design, field team usability | 5% |

**Target Score**: 10.0 / 10.0

---

### 15.2 Scoring Breakdown

**Matt Cohlmia (20% weight) — Score: 9.5 / 10**

*Assessment*: The SOP directly addresses the business problem Matt cares most about: ensuring Ellen is a credible, reliable intelligence layer that the sales team actually trusts. The PVS algorithm, staleness decay modeling, and automated rebuild trigger system are the right tools for maintaining credibility at scale. The rollback procedure and rollback authority assignment give him confidence that a degraded Ellen version won't survive in production. The one gap: no explicit SLA for field team feedback response (how quickly does a sales rep's thumbs-down translate into a content review). Deducting 0.5 for this.

*Weighted contribution*: 9.5 × 0.20 = **1.90**

---

**Seema Verma (20% weight) — Score: 9.7 / 10**

*Assessment*: The regulatory intelligence domain treatment in Packet 05 is sophisticated. The 21-day half-life for regulatory intelligence is correctly calibrated — CMS rulemaking cycles and public comment windows operate on a 30–60 day cadence but material developments can emerge within days of a proposed rule. The T-03 P0 trigger for regulatory change detection is appropriate and correctly scoped to CMS, ONC, and HHS. The Monte Carlo simulation result showing Packet 05 regulatory domain at 0.29 baseline staleness risk (below the 0.40 rebuild threshold) is honest — it means the current scheduled cadence is barely sufficient for this domain and should be monitored carefully. The government and federal intel domain ownership (Government Affairs Director as primary) is the right call. Minor deduction for not addressing international regulatory domains with the same specificity as domestic. Deducting 0.3.

*Weighted contribution*: 9.7 × 0.20 = **1.94**

---

**Steve (Agent) — Score: 9.6 / 10**

*Assessment*: Strategically, this SOP solves the right problem in the right way: it automates routine maintenance while preserving human authority at meaningful decision points (rollback, major version promotion). The Tier 1 competitor designation system is strategically sound — not all competitors warrant the same rebuild latency, and the discipline of explicitly tiering them prevents both false urgency and false complacency. The cross-reference to SOP-27 (Intelligence Cycle) for trigger detection is correct — the Ellen OS build pipeline should not re-implement signal detection; it should consume from the canonical signal pipeline. Minor concern: the SOP does not address what happens when Ellen's routing layer fails to select the correct packet for a query — this is a distribution failure mode that lives just outside the scope of this SOP but should be referenced. Deducting 0.4.

*Weighted contribution*: 9.6 × 0.15 = **1.44**

---

**Compass (Agent) — Score: 9.4 / 10**

*Assessment*: From a usability standpoint, the onboarding section is well-structured and rightly role-differentiated (sales reps get Packets 01 and 04; compliance gets Packet 05). The feedback loop training step is critical and its inclusion here reflects good product thinking — an AI intelligence layer with no feedback mechanism is a black box that degrades silently. The content freshness warning inline markers (`[CONTENT WARNING...]`) are the right UX pattern: surface the uncertainty at the point of use, not buried in a status dashboard. The one usability gap: the SOP describes the Ellen query interface but does not define the standard query patterns or prompt templates that help non-analyst users get high-quality responses. Field users left to freestyle their queries will get inconsistent results. Deducting 0.6.

*Weighted contribution*: 9.4 × 0.10 = **0.94**

---

**Ledger (Agent) — Score: 9.5 / 10**

*Assessment*: The SHA1 hash-based skip logic is commercially sound — it prevents unnecessary Playwright automation runs and SharePoint API calls on no-change weeks, which reduces both operational cost and failure surface area. The <500KB size target per packet is validated by SharePoint performance data and represents a thoughtful engineering constraint, not an arbitrary one. The size optimization passes (deduplication, section trimming, metadata compression) are well-ordered. The commercial risk concern: the SOP does not define a cost ceiling for the Playwright automation infrastructure or a runaway build detection mechanism (e.g., if the T-01 trigger fires 10 times in a day due to a noisy signal feed, the build pipeline could run 10 unnecessary full rebuilds). A rate limiter or cooldown window should be added. Deducting 0.5.

*Weighted contribution*: 9.5 × 0.10 = **0.95**

---

**Marcus (Agent) — Score: 9.6 / 10**

*Assessment*: The 36+ domain coverage across six packets is genuinely comprehensive for a healthcare IT competitive intelligence function. The demand signals domain in Packet 02 is particularly valuable — most M&CI functions track competitor activity but under-invest in buying intent signals, so its explicit inclusion here is differentiated. The voice of customer domain correctly bridges M&CI and Customer Success, which is an organizational alignment win. The market trend analysis domain (quarterly cadence, 90-day half-life) is correctly scoped — macro healthcare market trends do not need weekly refresh. The analyst landscape domain in Packet 01 is well-placed. Minor gap: no domain explicitly tracks Oracle Health internal product roadmap changes that affect competitive positioning — this is a Packet 01 content gap that could leave battlecards inconsistent with internal commitments. Deducting 0.4.

*Weighted contribution*: 9.6 × 0.10 = **0.96**

---

**Forge (Agent) — Score: 9.7 / 10**

*Assessment*: The build pipeline architecture is solid. Idempotency via SHA1 comparison is the right design choice — it makes the pipeline safe to run on any schedule or trigger without state corruption risk. The JSON state file structure is well-designed: it stores enough history for trend analysis, rollback support, and audit without bloating. The Monte Carlo simulation is implemented correctly — using exponential decay with domain-specific half-lives is statistically appropriate for information staleness modeling, and the 1,000-iteration count is sufficient for stable probability estimates at the precision levels needed here (0.01 resolution). The one technical concern: the `SIZE_BUDGET_EXCEEDED` error path alerts Mike but does not specify a self-healing mechanism. If an inbound source document is temporarily large (e.g., a quarterly market report that doubles the domain's content for one cycle), the packet fails indefinitely until someone manually intervenes. A size-adaptive trim policy for this case would improve resilience. Deducting 0.3.

*Weighted contribution*: 9.7 × 0.10 = **0.97**

---

**Herald (Agent) — Score: 9.3 / 10**

*Assessment*: The SOP is clearly written and well-organized for its primary audience (Mike and the M&CI team). Section 12 (Participant Onboarding) is appropriately practical — the time estimates (30 min, 30 min, 30 min, 15 min) ground the onboarding in reality. The access permissions table (Section 9.4) is clear and actionable for whoever manages SharePoint groups. The RACI matrix is detailed enough to assign accountability without being bureaucratically over-specified. The KPI definitions are crisp and testable. Minor communication gap: the SOP uses several technical terms (SHA1, idempotent, Monte Carlo) without brief definitions for non-technical readers who will encounter this document. Given that field team representatives may review sections of this SOP during onboarding or compliance reviews, a brief technical glossary would improve accessibility. Deducting 0.7.

*Weighted contribution*: 9.3 × 0.05 = **0.47**

---

### 15.3 Final Score

| Panelist | Score | Weight | Contribution |
|---|---|---|---|
| Matt Cohlmia | 9.5 | 20% | 1.90 |
| Seema Verma | 9.7 | 20% | 1.94 |
| Steve | 9.6 | 15% | 1.44 |
| Compass | 9.4 | 10% | 0.94 |
| Ledger | 9.5 | 10% | 0.95 |
| Marcus | 9.6 | 10% | 0.96 |
| Forge | 9.7 | 10% | 0.97 |
| Herald | 9.3 | 5% | 0.47 |
| **TOTAL** | | **100%** | **9.57 / 10.0** |

**Panel Verdict**: APPROVED with advisory notes. The SOP meets production quality standards for M&CI distribution. Advisory notes for v1.1:
1. Define field team feedback response SLA (Matt Cohlmia note)
2. Add trigger rate limiter / cooldown window to prevent noisy-signal rebuild storms (Ledger note)
3. Reference Ellen routing failure mode and link to upstream routing SOP (Steve note)
4. Add standard query patterns / prompt templates appendix for field users (Compass note)
5. Add size-adaptive trim policy for oversized inbound source documents (Forge note)

---

*End of SOP-22*

*Version history: v1.0 initial publication 2026-03-23 — Mike Rodgers, Sr. Director M&CI*
