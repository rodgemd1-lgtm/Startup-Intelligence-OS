# SOP-21: SharePoint Content Governance
**Owner**: Mike Rodgers, Sr. Director M&CI
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-23
**Category**: Quality & Governance
**Priority**: P2
**Maturity**: Partial → Documented

---

## 1. Purpose

This SOP establishes the complete governance framework for Oracle Health M&CI's SharePoint content environment: 21 active pages managed through an automated Playwright-based sync pipeline with SHA1 hash state tracking.

SharePoint is M&CI's primary internal knowledge distribution surface. Content quality and freshness directly affect deal outcomes, internal alignment, and M&CI credibility. Without documented governance, SharePoint environments accumulate five failure modes: content staleness, orphaned pages, permission sprawl, version confusion, and undetected automation failures.

This SOP prevents all five failure modes through structured ownership, publishing workflow, automated state tracking, content freshness scoring, and the Archive Never Delete protocol.

---

## 2. Page Inventory and Ownership

### 2.1 Inventory Principles

Every SharePoint page must have:
1. A unique **Page ID** (format: `SP-XXX`)
2. A designated **Content Owner** (named individual)
3. A designated **Backup Owner**
4. A **Page Type** classification
5. A **Review Cadence**
6. A **Sync Script** reference
7. A **Last Verified** date

### 2.2 Page Type Classification

| Type Code | Description | Review Cadence | Staleness Threshold |
|---|---|---|---|
| TYPE-CI | Competitive Intelligence (battlecards, briefs, win/loss) | Bi-weekly | 14 days |
| TYPE-ST | Strategic (positioning, messaging, GTM) | Monthly | 30 days |
| TYPE-REF | Reference (process docs, templates, SOPs) | Quarterly | 90 days |
| TYPE-EXEC | Executive (board decks, leadership summaries) | Monthly spot check | 30 days |
| TYPE-OPS | Operational (team resources, onboarding) | Quarterly | 90 days |
| TYPE-ARCH | Archive (superseded content, retained for record) | Annual audit | 365 days (soft) |

### 2.3 Master Page Inventory Register

Maintained at: `/oracle-health-ai-enablement/.sharepoint-state/page-inventory.yaml`

```yaml
pages:
  - id: SP-001
    title: "Oracle Health Competitive Battlecard — [Competitor]"
    url: "[SharePoint URL]"
    type: TYPE-CI
    owner: "Mike Rodgers"
    backup_owner: "[Backup Name]"
    sync_script: "sync_battlecard_[competitor].py"
    review_cadence: bi-weekly
    last_verified: "2026-03-23"
    last_sync: "2026-03-23T06:15:00Z"
    current_sha1: "[40-char SHA1]"
    status: active
```

### 2.4 Inventory Audit

The Page Inventory is audited quarterly. The audit verifies owner assignments, review cadence compliance, sync script accuracy, and absence of pages added outside governance. Results logged in `.sharepoint-state/audit-log.yaml`.

---

## 3. Publishing Workflow

### 3.1 Workflow Overview

```
[DRAFT] → [REVIEW] → [APPROVE] → [PUBLISH]
```

Minor updates (typos, formatting, metadata) use the expedited two-stage workflow:
```
[EDIT] → [PUBLISH]
```
Work Owner self-certifies the change is non-material. Self-certification logged.

### 3.2 Stage Definitions

**Stage 1 — Draft**
- **Who**: Content Owner
- **Gate criteria**: Draft complete against approved outline; all claims have source citations; self-reviewed against success criteria; committed to version history in staging (NOT live SharePoint)

**Stage 2 — Review**
- **Who**: At least one reviewer (Content Owner cannot be sole reviewer for TYPE-CI and TYPE-ST)
- **Gate criteria**: Reviewer signed off; all CRITICAL findings resolved; content factually accurate as of review date; for TYPE-CI: Expert Panel per SOP-18 (min 6 panelists)
- **SLA**: 48h standard; 24h Director-designated time-sensitive

**Stage 3 — Approve**
- **Who**: M&CI Director (or designated Senior Analyst for TYPE-REF and TYPE-OPS)
- **Gate criteria**: Director approved version for publication; version tagged (e.g., `v1.0-approved`); metadata complete; sync script identified

**Stage 4 — Publish**
- **Who**: Sync pipeline (automated) or Content Owner (manual emergency)
- **Actions**:
  1. Playwright-based upload executes
  2. SHA1 hash of published content computed and stored
  3. Page inventory record updated: `last_sync`, `current_sha1`, `last_verified`
  4. Post-publish SHA1 verification (Playwright re-fetches page, recomputes hash, compares)
  5. If mismatch: alert to Content Owner and M&CI Director

---

## 4. Content Standards

### 4.1 Naming Conventions

**Page title format**: `[Content Type] — [Subject] — [Qualifier if needed]`
- Examples: "Competitive Battlecard — Epic — Q1 2026"
- No unexplained abbreviations
- No dates unless material qualifier
- ≤ 80 characters
- Must be unique within M&CI SharePoint

**File/artifact names**: `[page-id]_[slug]_v[major].[minor]_[status].extension`
- Example: `SP-001_epic-battlecard_v2.1_approved.md`

### 4.2 Mandatory Metadata Block

Every SharePoint page must include at the top:
```
Owner:          [Name]
Last Updated:   [YYYY-MM-DD]
Version:        [X.Y]
Status:         [ACTIVE | UNDER REVIEW | ARCHIVED]
Review Due:     [YYYY-MM-DD]
Confidence:     [HIGH | MEDIUM | LOW]  (intelligence content only)
```

### 4.3 Formatting Standards

- H1: Page title (one per page)
- H2: Major sections; H3: Subsections (no deeper than H3)
- Tables preferred over bullet lists for comparative data
- Inline citations format: `[Source Name, Date]`
- No custom fonts; no embedded images without alt text
- Charts must have data source in caption

### 4.4 Content Quality Standards

**Accuracy**: All factual claims sourced; competitive claims current within staleness threshold; statistics cite original source; product features verified against Oracle Health product docs.

**Clarity**: Grade 10–12 reading level; paragraphs ≤ 5 sentences; sentences ≤ 25 words preferred.

**Completeness by type**:
- TYPE-CI: competitive context, Oracle Health differentiators, objection handlers, recommended talk tracks
- TYPE-ST: problem statement, audience, positioning statement, proof points
- TYPE-REF: purpose, scope, procedure steps, RACI or owner identification

### 4.5 Prohibited Content

- Confidential content not cleared for SharePoint distribution
- Unverified competitive claims presented as fact
- PII without explicit authorization
- Outdated content presented as current without explicit date labeling
- Draft/WIP content in the live environment (staging only)
- Competitor references in a defamatory or legally risky manner

---

## 5. Versioning Policy

### 5.1 Version Numbering

Semantic versioning: `v[MAJOR].[MINOR]`
- **MAJOR**: Substance, conclusions, or strategic guidance materially changes
- **MINOR**: Non-material updates (formatting, typos, source link refreshes)

### 5.2 Version History

Stored at: `.sharepoint-state/version-history/[page-id]-history.yaml`

```yaml
- version: "2.1"
  date: "2026-03-23"
  author: "Mike Rodgers"
  change_type: MINOR
  summary: "Updated Epic feature comparison table; Q1 2026 data"
  sha1: "[40-char SHA1]"
  approver: "Mike Rodgers"
  status: CURRENT
```

Version history files are never deleted.

### 5.3 Retention

| Status | Retention |
|---|---|
| CURRENT (latest approved) | Live in SharePoint |
| PREVIOUS (prior approved) | Retained in archive |
| DRAFT (unapproved working) | Staging for 90 days, then pruned |
| SUPERSEDED | Archived per Section 6; history retained permanently |

---

## 6. Archive Never Delete Protocol

### 6.1 Core Principle

No M&CI SharePoint content is ever permanently deleted. Content that is no longer current is archived — removed from the active content surface while all versions, metadata, and history are preserved. This policy is absolute.

### 6.2 Archival Triggers

| Trigger | Required Action | Timeline |
|---|---|---|
| Superseded by newer version | Archive prior version | Within 24h of new version going live |
| Exceeds staleness threshold, Content Owner certifies no refresh | Archive page | Within 5 business days |
| Consolidated into another page | Archive source; link from destination | Within 24h |
| Error discovered, cannot immediately correct | Archive and replace with interim notice | Immediately |
| Page owner departs; no backup assigned within 30 days | Archive pending reassignment | 30 days post-departure |
| Annual audit finds page with no activity, no verified update, no clear purpose | Director-authorized archive | 10 business days post-finding |

### 6.3 Archive Process

1. Flag in page inventory: `status` → `archived`
2. Update metadata block: Status = ARCHIVED, Archive Date set
3. Remove from SharePoint navigation menus
4. Disable or remove sync script
5. Preserve version history (archive status logged as new entry, not modification)
6. Log archive action in `.sharepoint-state/archive-log.yaml`:

```yaml
- page_id: SP-012
  title: "[Page title]"
  archived_date: "2026-03-23"
  archived_by: "Mike Rodgers"
  reason: "Superseded by SP-019"
  replacement_page_id: SP-019
  final_sha1: "[SHA1 of last approved version]"
```

### 6.4 Legal Hold Override

Content under legal hold:
- Cannot be archived or modified
- Flagged in page inventory with `legal_hold: true` and case reference
- May only be changed after Legal confirms hold is lifted

---

## 7. Permission Model

### 7.1 Permission Tiers

| Tier | Name | Access Level | Who |
|---|---|---|---|
| T1 | Read | View published content | All Oracle Health employees (default) |
| T2 | Contribute | View + comment; cannot publish | Extended M&CI stakeholders, designated SMEs |
| T3 | Edit | View + edit + draft; cannot approve | M&CI Content Owners, designated authors |
| T4 | Manage | Full access including approve, publish, archive | M&CI Director, Senior Analysts |

### 7.2 Permission Assignment Rules

1. Principle of Least Privilege — minimum tier for each user's role
2. Named assignments only (no distribution lists for T3/T4)
3. Time-bound elevated access — T4 outside core M&CI team: max 90 days, Director authorization required
4. Contractor access — T3/T4 requires Director + InfoSec notification
5. Former employee revocation — T3/T4 revoked within 1 business day of departure

### 7.3 Permission Audit

Semi-annual audit. Enumerates T3/T4 users, verifies authorization, revokes unverifiable access. Results in `.sharepoint-state/permission-audit-log.yaml`.

---

## 8. Automation Sync Protocol (Playwright + SHA1)

### 8.1 Architecture Overview

```
[Source Content]
    → [Sync Script (Python + Playwright)]
    → [SharePoint Web Interface (browser automation)]
    → [SHA1 State File (.sharepoint-state/hashes.yaml)]
    → [Verification Pass (post-publish SHA1 check)]
    → [Alert System (mismatch detection)]
```

21 sync scripts reside in: `/oracle-health-ai-enablement/scripts/sharepoint-sync/`

### 8.2 Sync Script Standards

Every script must implement:
```python
class SharePointSyncScript:
    page_id: str          # e.g., "SP-001"
    page_url: str         # Full SharePoint URL
    source_path: str      # Path to approved source file
    state_file: str       # Path to SHA1 state file

    def compute_sha1(content: str) -> str: ...
    def has_changed(current_sha1: str, stored_sha1: str) -> bool: ...
    def sync(dry_run: bool = False) -> SyncResult: ...
    def verify(expected_sha1: str) -> VerificationResult: ...
    def rollback(previous_sha1: str) -> RollbackResult: ...
```

**Required error handling**:
- Authentication failure: retry 3× with 30s backoff; alert on 3rd failure
- Upload failure: retry 2×; alert and halt on 2nd; do not mark sync complete
- Verification mismatch: attempt one automatic rollback; if fails, alert immediately
- Timeout: 120s maximum per sync operation

### 8.3 SHA1 State File

```yaml
# .sharepoint-state/hashes.yaml
state_version: "1.0"
last_updated: "2026-03-23T06:15:00Z"
pages:
  SP-001:
    current_sha1: "[40-char hash]"
    previous_sha1: "[40-char hash of prior version]"
    last_sync: "2026-03-23T06:15:00Z"
    last_verified: "2026-03-23T06:15:00Z"
    sync_status: SUCCESS  # SUCCESS | FAILED | MISMATCH | PENDING
```

State file is committed to project repo after every sync run. Never delete entries.

### 8.4 Sync Execution Cadence

| Page Type | Sync Frequency |
|---|---|
| TYPE-CI | Event-driven (SHA1 change on source) + daily verification pass |
| TYPE-ST, TYPE-REF, TYPE-OPS | Event-driven + weekly verification (Monday 06:00 UTC) |
| TYPE-EXEC | Event-driven + daily verification |
| TYPE-ARCH | Annual verification only |

**Event-driven trigger**: Source file watcher detects SHA1 change on source content, validates `approved` status tag, queues sync. Draft/unapproved files are never synced.

### 8.5 Sync Failure Protocol

**Severity 1 (MISMATCH)**: Alert within 5 min → attempt rollback → if rollback fails, InfoSec notified, manual restore.

**Severity 2 (FAILED)**: Alert to Content Owner → retry logic exhausted → Owner investigates within 4 business hours.

**Severity 3 (AUTH)**: Alert to Director + IT/InfoSec → no retry after 3rd failure → investigate within 2 business hours.

### 8.6 Sync Health Dashboard

Daily summary at: `.sharepoint-state/sync-health-[YYYY-MM-DD].yaml`
- Total pages: 21
- SUCCESS / FAILED / MISMATCH / not synced in >7 days counts
- M&CI Director reviews weekly (Monday ops review)

---

## 9. Predictive Algorithm: Content Freshness Score (CFS)

### 9.1 CFS Formula

```
CFS[page] = (w_a × A) + (w_v × V) + (w_c × C) + (w_s × S)

Where:
  A = Age Score              (how old vs staleness threshold)
  V = Velocity Score         (how fast is this domain changing)
  C = Citation Currency      (how current are cited sources)
  S = Source Volatility      (known rate of change for primary sources)

Weights:
  w_a = 0.40
  w_v = 0.25
  w_c = 0.20
  w_s = 0.15

CFS range: 0.0 (fully stale) – 1.0 (fully fresh)
```

### 9.2 Component Scoring

**A — Age Score**
```
A = max(0.0, 1.0 - (days_since_verified / staleness_threshold))

Example: TYPE-CI (14-day threshold), verified 3 days ago:
  A = 1.0 - (3/14) = 0.786

TYPE-CI verified 12 days ago:
  A = 1.0 - (12/14) = 0.143  ← approaching stale
```

**V — Velocity Score**
```
Domain velocity ceiling by type:
  HIGH (V_max = 0.3):  AI/ML competitive landscape, earnings-driven, active M&A
  MEDIUM (V_max = 0.6): General health IT competitive, product positioning, GTM
  LOW (V_max = 0.9):   Process documentation, templates, reference material

V = velocity_ceiling × (1.0 - decay_modifier)
  decay_modifier = age_score × (1 - velocity_ceiling)
```

**C — Citation Currency Score**
```
Per citation:
  citation_score = max(0.0, 1.0 - (citation_age / citation_threshold))
  threshold: CI=90 days, ST=180 days, REF=365 days

C = weighted mean (key claim citations weighted 2× over supporting)
```

**S — Source Volatility Score**
```
PRIMARY_SOURCE_VOLATILITY = {
  "competitor_website": 0.7,
  "press_release": 0.5,
  "analyst_report": 0.4,
  "oracle_internal_doc": 0.6,
  "regulatory_source": 0.3,
  "academic_paper": 0.2,
  "news_article": 0.5,
}

S = 1.0 - (mean_volatility × age_decay_factor)
  age_decay_factor = 1.0 - A
```

### 9.3 CFS Decision Rules

```
CFS ≥ 0.80     → FRESH. No action required.
CFS 0.60–0.79  → AGING. Proactive notice to Content Owner.
CFS 0.40–0.59  → STALE WARNING. Alert to Content Owner.
                  Review required within 48 hours.
CFS 0.20–0.39  → STALE. Alert to Content Owner AND M&CI Director.
                  24 hours to verify/refresh OR initiate archive.
CFS < 0.20     → CRITICALLY STALE. Immediate alert.
                  WARNING banner in SharePoint metadata.
                  Action required within 8 business hours.
                  If no action: Director auto-flags for archive.
```

### 9.4 CFS Execution

Runs daily at 05:30 UTC (30 min before morning sync). Implemented at:
```
/oracle-health-ai-enablement/scripts/sharepoint-sync/cfs_engine.py
```

Calibration reviewed quarterly; calibration log at `.sharepoint-state/cfs-calibration-log.yaml`.

---

## 10. Expert Panel Scoring

### 10.1 SharePoint-Specific Scoring Dimensions

| Dimension | Weight | Criteria |
|---|---|---|
| Content Accuracy | 25% | All facts current and correct; competitive data within staleness threshold |
| Structural Clarity | 20% | Follows formatting standards; H1/H2/H3 hierarchy clear; navigation intuitive |
| Completeness | 20% | Contains all required sections for its type; metadata block complete |
| Findability | 20% | Title follows naming convention; metadata keywords accurate; searchable |
| Governance Compliance | 15% | Owner identified; review date current; version correct; status accurate |

### 10.2 Thresholds (SharePoint)

| Panel Score | Decision |
|---|---|
| ≥ 9.0 | Deploy. Reference-quality — log as template example |
| 8.5–8.9 | Deploy. All CRITICAL and HIGH findings resolved |
| 8.0–8.4 | Conditional deploy. CRITICAL resolved; HIGH tracked for 5-day remediation |
| 7.0–7.9 | HOLD. Full revision required |
| < 7.0 | Do not publish. Return to Draft. Root cause required |

### 10.3 Review Cadence for Existing Pages

Expert Panel required for:
- New pages (always)
- MAJOR version increments
- Pages archived and being reinstated
- Pages with CRITICAL/HIGH finding in prior cycle
- Annual audit pass for all TYPE-CI and TYPE-ST pages

MINOR updates: Content Owner + one peer reviewer only.

---

## 11. RACI Matrix

| Activity | Content Owner | M&CI Director | Expert Panel | IT/InfoSec | Sync Auto | End Users |
|---|---|---|---|---|---|---|
| Draft new content | R/A | C | — | — | — | — |
| Stage 2 Review (TYPE-CI, TYPE-ST) | C | I | R | — | — | — |
| Stage 2 Review (TYPE-REF, TYPE-OPS) | R | C | — | — | — | — |
| Stage 3 Approval | C | R/A | I | — | — | — |
| Stage 4 Publish (automated) | I | I | — | — | R/A | — |
| Stage 4 Publish (manual override) | R | A | — | I | — | — |
| Post-publish SHA1 verification | I | I | — | — | R/A | — |
| Mismatch alert response | R | A | — | C | R | — |
| Severity 3 (auth failure) response | I | A | — | R | I | — |
| Archive trigger decision | R | A | — | — | — | — |
| Archive execution | R | A | — | — | — | I |
| Legal hold flagging | I | R | — | A | I | — |
| CFS alert response (AGING) | R | I | — | — | — | — |
| CFS alert response (STALE/CRITICAL) | R | A | — | — | — | — |
| Permission assignment (T3/T4) | C | R/A | — | I | — | — |
| Permission audit (semi-annual) | C | R/A | — | C | — | — |
| Page Inventory audit (quarterly) | C | R/A | — | — | — | — |
| Sync health dashboard review | C | R/A | — | — | — | — |

---

## 12. KPIs

| KPI | Target | Measurement |
|---|---|---|
| Pages with SUCCESS sync status | >95% at all times | Daily sync health dashboard |
| Average CFS across all pages | >0.70 | Daily CFS computation |
| Pages at STALE or worse | 0 | Daily CFS alert system |
| Stage 2 review SLA compliance | >90% | % reviewed within 48h window |
| Permission audit findings (T3/T4) | 0 unauthorized assignments | Semi-annual audit |
| Archive log completeness | 100% | Every archive action logged |
| SHA1 mismatch incidents | <2 per month | Sync health incident log |
| Version history completeness | 100% | All pages have history YAML |
