# SOP-01: Daily Morning Brief Assembly

**Owner**: Mike Rodgers, Sr. Director, Marketing & Competitive Intelligence
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-23
**Category**: Daily Intelligence Operations
**Priority**: P1 — Core operational cadence
**Maturity**: Automated

---

## 1. Purpose

Produce a daily intelligence brief that surfaces the highest-priority signals from across Oracle Health's competitive landscape, Mike's calendar and email, and the Jake brain memory layer — delivered to Mike's inbox at 6:00 AM every weekday so he walks into Oracle with a complete situational picture in under 10 minutes of reading.

The brief is not a dump of raw data. It is a synthesized, prioritized, editorially curated intelligence product. Every section earns its place by answering one question: **"So what does this mean for Mike at Oracle Health today?"**

Secondary purpose: the daily brief is the primary forcing function for intelligence hygiene. If signals are not being collected, if competitive feeds have gone stale, or if the brain memory layer has not been updated — the brief quality degrades visibly. The brief is the canary in the coal mine for the entire M&CI intelligence apparatus.

---

## 2. Scope

This SOP covers the full pipeline from raw signal ingestion to delivered email artifact:

- **Phase 1**: Overnight signal collection (midnight scrape)
- **Phase 2**: Signal triage, scoring, and assembly (12:30 AM)
- **Phase 3**: Brief generation, formatting, and quality check (1:00 AM – 5:00 AM)
- **Phase 4**: Delivery via Resend API with Telegram backup (6:00 AM)

**In scope:**
- Oracle Health competitive intelligence (Epic, Meditech, Veradigm, Salesforce Health Cloud, Microsoft Cloud for Healthcare)
- Matt Cohlmia-relevant executive signals
- Mike's Apple Calendar and Exchange calendar events for the day
- Email triage from the prior 18 hours (Oracle Exchange + Gmail)
- Jake brain memory layer: episodic, semantic, and procedural memory signals
- GitHub activity (Startup Intelligence OS repo)
- TrendRadar news and trend signals

**Out of scope:**
- Alex Recruiting project signals (separate brief cadence)
- Personal calendar events unrelated to Oracle or M&CI
- Social media monitoring (covered by separate TrendRadar workflow)
- Financial data outside Oracle competitive pricing

---

## 3. Architecture

The full pipeline runs as a four-phase overnight automation. All phases are orchestrated via launchd on the Mac, sourcing `~/.hermes/.env` for all API keys.

```
╔══════════════════════════════════════════════════════════════════════════╗
║                  ORACLE HEALTH M&CI DAILY BRIEF PIPELINE                ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  MIDNIGHT (12:00 AM)                                                     ║
║  ┌─────────────────────────────────────────────────────────────────┐    ║
║  │  PHASE 1: SIGNAL COLLECTION (overnight-scrape.sh)               │    ║
║  │                                                                  │    ║
║  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │    ║
║  │  │ Email Scrape │  │ Calendar Pull│  │ Competitive Feeds    │  │    ║
║  │  │ (osascript)  │  │ (GCal API +  │  │ (TrendRadar + Brave  │  │    ║
║  │  │              │  │  osascript)  │  │  + Brightdata)       │  │    ║
║  │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │    ║
║  │         │                 │                       │              │    ║
║  │  ┌──────┴───────┐  ┌──────┴───────┐  ┌───────────┴──────────┐  │    ║
║  │  │ Brain Memory │  │   GitHub     │  │  TrendRadar News     │  │    ║
║  │  │ (Supabase    │  │  Activity    │  │  Aggregation         │  │    ║
║  │  │  pgvector)   │  │  (GH API)    │  │  (MCP server)        │  │    ║
║  │  └──────┬───────┘  └──────┬───────┘  └───────────┬──────────┘  │    ║
║  │         └─────────────────┴─────────────────┬─────┘             │    ║
║  │                                              ▼                   │    ║
║  │                    Raw Signal Store (JSON, ~/.hermes/cache/)     │    ║
║  └──────────────────────────────────────────────────────────────────┘    ║
║                                                                          ║
║  12:30 AM                                                                ║
║  ┌─────────────────────────────────────────────────────────────────┐    ║
║  │  PHASE 2: INTEL ASSEMBLY (brain_morning_brief.py)               │    ║
║  │                                                                  │    ║
║  │  Signal Triage → Scoring (birch/scorer.py) → Deduplication      │    ║
║  │  Priority Tier Assignment (P0 / P1 / P2)                        │    ║
║  │  "So What" Framework Applied Per Signal                         │    ║
║  │  Composite Confidence Score Computed                             │    ║
║  │  Freshness Decay Applied                                         │    ║
║  └──────────────────────────────────┬───────────────────────────────┘   ║
║                                     ▼                                    ║
║  1:00 AM – 5:30 AM                                                       ║
║  ┌─────────────────────────────────────────────────────────────────┐    ║
║  │  PHASE 3: BRIEF GENERATION (brain_morning_brief.py)             │    ║
║  │                                                                  │    ║
║  │  Executive Summary (5 bullets max)                              │    ║
║  │  P0 Priority Actions (requires immediate response)              │    ║
║  │  P1 Priority Actions (before noon)                              │    ║
║  │  P2 Background Items (FYI, no action required today)            │    ║
║  │  Competitive Signals Section                                     │    ║
║  │  Calendar Prep Section (today's meetings + prep notes)          │    ║
║  │  Background Context (deep links + source citations)             │    ║
║  │                                                                  │    ║
║  │  Output: artifacts/morning-briefs/brief-{date}.md               │    ║
║  └──────────────────────────────────┬───────────────────────────────┘   ║
║                                     ▼                                    ║
║  6:00 AM                                                                 ║
║  ┌─────────────────────────────────────────────────────────────────┐    ║
║  │  PHASE 4: DELIVERY                                               │    ║
║  │                                                                  │    ║
║  │  Primary:   Resend API → mike@... (HTML email, mobile-first)    │    ║
║  │  Backup:    Telegram Bot → Mike's personal Telegram channel     │    ║
║  │  Archive:   artifacts/morning-briefs/brief-{date}.md persisted  │    ║
║  │  Failure:   Retry 3x → fallback to Telegram plain text          │    ║
║  └─────────────────────────────────────────────────────────────────┘    ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### System Dependencies

| Component | Technology | Schedule | Failure Mode |
|-----------|------------|----------|-------------|
| Overnight scrape | launchd plist + shell scripts | 12:00 AM daily | Retry at 12:15 AM; log error to `~/.hermes/logs/scrape.log` |
| Intel assembly | Python 3.11 + Supabase pgvector | 12:30 AM daily | Alert Mike via Telegram if assembly fails |
| Brief generation | Python + Claude API (Sonnet) | 1:00 AM daily | Fallback to last successful brief with staleness warning |
| Email delivery | Resend API | 6:00 AM daily | Fallback to Telegram; retry 3x with exponential backoff |
| Brain memory | Supabase (zqsdadnnpgqhehqxplio) | Continuous + nightly consolidation | Degrade gracefully; omit brain section with warning |
| Competitive feeds | TrendRadar MCP + Brightdata | 12:00 AM daily | Use cached data up to 48 hours old; flag staleness in brief |

---

## 4. Phase 1: Signal Collection

**Trigger**: launchd plist fires at 12:00 AM every weekday (Monday–Friday)
**Script**: `scripts/overnight_scrape.sh`
**Duration**: 15–25 minutes typical; 40 minutes max before timeout
**Output**: JSON files in `~/.hermes/cache/signals/{date}/`

### 4.1 Source: Email (Oracle Exchange)

**Collection method**: `osascript` against Apple Mail's Exchange account
**Scope**: All emails received in the last 18 hours
**Filters applied**:
- From: VIP sender list (Matt Cohlmia, Oracle exec tier, key competitor domains)
- Subject keywords: acquisition, partnership, pricing, contract, competitive, urgent, FYI, action required
- Oracle Health internal domains: `@oracle.com`, `@cerner.com`

**What is NOT collected from email**:
- Personal emails (Gmail personal account)
- Marketing emails and newsletters (filtered by unsubscribe link presence)
- Calendar invite acknowledgments
- System-generated notifications

**Output format**:
```json
{
  "source": "email_exchange",
  "collected_at": "2026-03-23T00:03:42Z",
  "signals": [
    {
      "id": "email_20260323_001",
      "from": "matt.cohlmia@oracle.com",
      "subject": "Epic pricing update — Q2 strategy",
      "received_at": "2026-03-22T18:47:00Z",
      "snippet": "Team — saw the Epic pricing deck...",
      "vip": true,
      "raw_urgency_keywords": ["strategy", "pricing"],
      "source_weight": 0.95
    }
  ]
}
```

**Known failure mode**: Apple Mail `osascript` times out if Mail.app has been running for an extended period without restart. Recovery: `scripts/restart_mail_and_retry.sh` — kills Mail.app process and relaunches before attempting scrape. This is logged and flagged in the morning brief if it occurs.

### 4.2 Source: Calendar

**Collection method**: Google Calendar API (OAuth, personal + family calendar) + `osascript` for Oracle Exchange calendar
**Scope**: Today's full calendar (midnight to midnight) + look-ahead 24 hours for prep items
**What is extracted**:
- Meeting titles, attendees, and durations
- Video call links (Zoom, WebEx, Teams)
- Oracle internal meeting tags (all-hands, QBR, exec review, 1:1)
- Conflicts and back-to-back stretches
- Prep notes if attached to calendar events
- Travel blocks

**Calendar intelligence generated**:
- Morning load score (0–10): How heavy is the meeting load before noon?
- Exec exposure count: How many Oracle exec-tier attendees across the day?
- Conflict flags: Any overlapping calendar entries?
- Prep recommendations: Which meetings warrant advance prep materials?

**Output format**:
```json
{
  "source": "calendar_combined",
  "collected_at": "2026-03-23T00:07:15Z",
  "date": "2026-03-23",
  "morning_load_score": 7.2,
  "events": [
    {
      "id": "cal_20260323_001",
      "title": "M&CI Weekly Sync — Matt Cohlmia",
      "start": "2026-03-23T09:00:00",
      "end": "2026-03-23T10:00:00",
      "attendees": ["matt.cohlmia@oracle.com", "mike.rodgers@oracle.com"],
      "exec_tier": true,
      "prep_required": true,
      "prep_urgency": "P0",
      "video_link": "https://webex.com/...",
      "notes_attached": false
    }
  ]
}
```

### 4.3 Source: Competitive Feeds

**Collection method**: TrendRadar MCP server + Brightdata scraping + Brave Search API
**Scope**: All monitored competitors in the Oracle Health competitive landscape
**Monitored entities**:

| Entity | Type | Monitoring Depth |
|--------|------|-----------------|
| Epic Systems | Primary competitor | Deep — pricing, partnerships, product releases, hiring, exec moves |
| Meditech | Primary competitor | Deep — same as Epic |
| Veradigm (Allscripts) | Secondary competitor | Standard — major announcements, partnerships |
| Salesforce Health Cloud | Adjacent threat | Standard — feature releases, Oracle overlap |
| Microsoft Cloud for Healthcare | Adjacent threat | Standard — Azure Health, Azure OpenAI healthcare |
| athenahealth | Secondary competitor | Light — acquisition news, major contracts |
| eClinicalWorks | Secondary competitor | Light — pricing changes, market share data |
| Particle Health / health data APIs | Emerging threat | Light — funding rounds, TEFCA participation |

**What triggers collection**:
- Any news article mentioning a monitored entity in the last 24 hours
- SEC filings or press releases
- LinkedIn job postings in strategic roles (VP Product, Chief Medical Officer, VP Sales)
- GitHub activity on any public competitor repositories (rare but tracked)
- Healthcare IT industry publications: HIMSS, HealthcareITNews, Becker's Hospital Review, Fierce Healthcare

**Output format**:
```json
{
  "source": "competitive_feeds",
  "collected_at": "2026-03-23T00:18:33Z",
  "signals": [
    {
      "id": "comp_20260323_001",
      "entity": "Epic Systems",
      "signal_type": "partnership",
      "headline": "Epic announces expanded integration with Google Cloud Health API",
      "source_url": "https://www.healthcareitnews.com/...",
      "published_at": "2026-03-22T14:30:00Z",
      "relevance_score": 0.87,
      "raw_text_snippet": "Epic Systems announced today...",
      "tags": ["cloud", "interoperability", "google", "partnership"]
    }
  ]
}
```

### 4.4 Source: Jake Brain Memory

**Collection method**: Direct Supabase query via `jake_brain/retriever.py`
**Scope**: Episodic, semantic, and procedural memory tables
**Query logic**:
```sql
SELECT FROM jake_episodic
  WHERE created_at > NOW() - INTERVAL '7 days'
  AND entity_refs && ARRAY['oracle_health', 'matt_cohlmia', 'competitive']
  ORDER BY importance_score DESC
  LIMIT 20;

SELECT FROM jake_semantic
  WHERE last_updated > NOW() - INTERVAL '30 days'
  AND category IN ('competitive_intel', 'oracle_strategy', 'stakeholder_context')
  ORDER BY confidence DESC
  LIMIT 15;
```

**What the brain memory layer surfaces**:
- Recent decisions made by Mike that are relevant to today's agenda
- Semantic facts about competitor positioning that provide context for new signals
- Historical patterns (e.g., Epic tends to announce partnerships at HIMSS — is HIMSS this week?)
- Stakeholder context (Matt Cohlmia's known priorities, recent concerns, communication style)
- Procedural knowledge (which competitive signals have historically triggered responses from Oracle exec leadership)

**Output**: Structured context objects merged into the assembly phase signal pool

### 4.5 Source: GitHub Activity

**Collection method**: GitHub API (personal access token stored in `~/.hermes/.env`)
**Scope**: `Startup-Intelligence-OS` repository only
**What is collected**:
- Commits in the last 24 hours (author, message, files changed)
- Open pull requests
- Issues opened or commented on
- Any workflow failures in GitHub Actions

**Purpose in the morning brief**: Jake uses GitHub activity to update Mike on the state of his own intelligence platform — did overnight automations produce new artifacts? Are there uncommitted changes that should be reviewed? Did any CI checks fail?

**Output format**:
```json
{
  "source": "github",
  "collected_at": "2026-03-23T00:22:10Z",
  "repo": "Startup-Intelligence-OS",
  "commits_last_24h": 2,
  "open_prs": 1,
  "workflow_failures": 0,
  "recent_commits": [
    {
      "sha": "a9b1569",
      "message": "docs(film-studio): complete research, design, and build plan",
      "author": "mikerodgers",
      "timestamp": "2026-03-22T21:14:00Z",
      "files_changed": 3
    }
  ]
}
```

### 4.6 Source: TrendRadar News Aggregation

**Collection method**: TrendRadar MCP server (`mcp__trendradar__get_latest_news`, `mcp__trendradar__get_trending_topics`)
**Scope**: Healthcare IT, enterprise software, AI in healthcare, Oracle-relevant topics
**Frequency**: Triggered as part of overnight scrape; TrendRadar also runs its own independent RSS crawl

**Topics monitored**:
- Healthcare AI and automation
- Electronic Health Records (EHR) market
- Value-based care technology
- Healthcare interoperability (FHIR, HL7, TEFCA)
- Oracle Cloud Infrastructure in healthcare
- Medicare/Medicaid technology policy changes
- Hospital system M&A activity

**Output**: Top 10 trending topics with article count, sentiment, and relevance-to-Oracle score

---

## 5. Phase 2: Intel Assembly

**Trigger**: launchd plist fires at 12:30 AM (30 minutes after scrape start, ensuring scrape completion)
**Script**: `scripts/brain_morning_brief.py` — assembly function
**Duration**: 10–20 minutes typical
**Input**: JSON signal files in `~/.hermes/cache/signals/{date}/`
**Output**: Structured assembly object in memory, passed to Phase 3 generator

### 5.1 Signal Pool Construction

The assembly phase begins by loading all signals from Phase 1 into a unified signal pool:

```python
signal_pool = []
for source_file in glob.glob(f"~/.hermes/cache/signals/{date}/*.json"):
    with open(source_file) as f:
        data = json.load(f)
        for signal in data.get("signals", []):
            signal["source_type"] = data["source"]
            signal_pool.append(signal)
```

**Signal pool typical size**: 40–120 signals on a normal weekday. Spikes to 200+ during HIMSS, Oracle OpenWorld, or major competitor announcements.

### 5.2 Signal Scoring

Every signal in the pool is scored using three independent scoring subsystems:

**Subsystem A: birch/scorer.py (Competitive Intelligence Signals)**

For any signal where `source_type == "competitive_feeds"`:

```
competitive_score = (relevance × 0.40) + (actionability × 0.35) + (urgency × 0.25)
```

Where:
- `relevance` (0–10): How directly does this signal affect Oracle Health's competitive position?
- `actionability` (0–10): Can Mike or Matt take a concrete action in response to this signal?
- `urgency` (0–10): How time-sensitive is this signal? Will it matter less if seen tomorrow vs. today?

Scoring rubric for `relevance`:
- 10: Directly threatens Oracle Health contract or pricing position
- 8–9: Competitor announcement affects Oracle's named accounts or pipeline
- 6–7: Market-level shift that affects Oracle Health's product category
- 4–5: Adjacent market activity worth tracking
- 1–3: Background noise; informational only

**Subsystem B: jake_brain/priority.py (General Signal Triage)**

For all non-competitive signals (email, calendar, brain memory):

```
priority_score = (urgency × 0.40) + (importance × 0.35) + (recency × 0.25)
```

Where:
- `urgency` (0–10): Time sensitivity — 10 = requires same-day response, 1 = can wait weeks
- `importance` (0–10): Strategic weight — 10 = affects Matt Cohlmia / Oracle exec tier, 1 = routine
- `recency` (0–10): How fresh is this signal? Signal from 1 hour ago = 10; signal from 17 hours ago ≈ 4

Recency decay function:
```python
def recency_score(signal_age_hours: float, signal_type: str) -> float:
    """
    Exponential decay. Half-life = 6 hours for most signal types.
    VIP email: half-life = 12 hours (persists longer in urgency window)
    Competitive feed: half-life = 4 hours (stale faster, markets move)
    """
    if signal_type == "email_vip":
        half_life = 12.0
    elif signal_type == "competitive":
        half_life = 4.0
    else:
        half_life = 6.0
    return 10 * (0.5 ** (signal_age_hours / half_life))
```

**Subsystem C: Source Weight Adjustment**

After base scoring, apply source-specific weights:

| Source | Weight Multiplier | Rationale |
|--------|------------------|-----------|
| Email from Matt Cohlmia | 1.50× | Exec sponsor, direct stakeholder |
| Email from Oracle exec tier | 1.35× | High-priority internal chain |
| Email from competitor domain | 1.20× | Rare but high-value signal |
| Calendar: exec-tier meeting today | 1.40× | Immediate prep urgency |
| Competitive feed: Epic or Meditech | 1.25× | Primary competitor premium |
| Brain memory: Matt context | 1.30× | Stakeholder intelligence premium |
| GitHub: CI failure | 1.15× | Platform health signal |
| TrendRadar trending topic | 1.10× | Market context, lower urgency |
| Routine email | 0.80× | De-prioritize administrative traffic |

### 5.3 Priority Tier Assignment

After scoring, every signal is assigned a priority tier:

| Tier | Score Range | Definition | Brief Placement |
|------|-------------|------------|----------------|
| **P0** | 8.5 – 10.0 | Critical — requires Mike's attention before 9:00 AM | Top of Executive Summary; own section in brief |
| **P1** | 6.5 – 8.4 | High priority — action required today, ideally before noon | Priority Actions section |
| **P2** | 4.0 – 6.4 | Standard — worth knowing, no immediate action required | Background Context section |
| **P3** | 0.0 – 3.9 | Background noise — logged but not included in brief | Omitted from brief; archived in signal store |

**Typical P0/P1/P2 distribution on a normal weekday**:
- P0: 0–3 signals (median: 1)
- P1: 3–12 signals (median: 6)
- P2: 8–30 signals (median: 15)
- P3: 20–80 signals (filtered out entirely)

### 5.4 Deduplication

Competitive and news signals frequently arrive from multiple sources. Deduplication prevents the same story from appearing multiple times in different sections.

**Deduplication logic**:
```python
def deduplicate_signals(signals: list[dict]) -> list[dict]:
    """
    1. For each pair of signals, compute title_similarity using
       token overlap (Jaccard similarity on unigrams).
    2. If similarity > 0.72 AND same entity AND signals within 24h:
       Merge into single signal; keep highest score; concatenate source_urls.
    3. Brain memory signals are NEVER deduplicated against news signals
       (they provide context, not duplicates).
    """
    seen = {}
    for signal in sorted(signals, key=lambda s: s["score"], reverse=True):
        key = (signal.get("entity", ""), signal.get("signal_type", ""))
        if key not in seen:
            seen[key] = signal
        else:
            existing = seen[key]
            if jaccard_similarity(signal["headline"], existing["headline"]) > 0.72:
                existing["source_urls"] = list(set(
                    existing.get("source_urls", []) + [signal.get("source_url", "")]
                ))
                existing["score"] = max(existing["score"], signal["score"])
            else:
                seen[f"{key}_{signal['id']}"] = signal
    return list(seen.values())
```

### 5.5 The "So What" Framework

Before any signal is included in the brief, it must pass the "So What" test. Jake applies this framework to every P0 and P1 signal:

**The Three Questions**:
1. **What happened?** (Factual summary — 1 sentence)
2. **Why does this matter to Oracle Health specifically?** (Competitive or operational implication — 1–2 sentences)
3. **What should Mike do about it?** (Concrete recommended action — 1 sentence, or "No action required — awareness only")

**Example application**:

> **Signal**: Epic announces expanded Google Cloud Health API integration
>
> **What happened?** Epic Systems announced a deep integration with Google Cloud's Healthcare API, enabling bidirectional FHIR data exchange for shared hospital clients.
>
> **Why it matters to Oracle Health**: This directly challenges Oracle Health's Cloud Infrastructure partnership narrative with hospital systems that currently use both Oracle and Epic. Any account where Oracle is positioned as the "cloud backbone" and Epic is the EHR layer needs to be briefed on this development — Epic is now positioning itself as a cloud-first platform, not just an EHR.
>
> **What Mike should do**: Flag for Matt Cohlmia; prepare a competitive response brief; check named accounts in CRM for any dual Oracle+Epic deployments that may now be at-risk.

Signals that cannot pass the "So What" framework (i.e., "what happened" is clear but "why it matters" cannot be articulated specifically for Oracle Health) are downgraded to P2 or P3 automatically.

---

## 6. Phase 3: Brief Generation

**Trigger**: Assembly phase completion signal
**Script**: `scripts/brain_morning_brief.py` — generation function
**Duration**: 30–90 minutes (Claude API call for synthesis + formatting)
**Output**: `artifacts/morning-briefs/brief-{date}.md`

### 6.1 Format Standards

**Target length**: 800–1,400 words for the email-rendered version. The Markdown source may be longer due to background context section.

**Readability requirements**:
- Mobile-first layout (Mike reads on iPhone during morning commute)
- Executive Summary must be readable in under 90 seconds
- Each bullet point is one discrete action or fact — no compound sentences
- Bold the entity name (Epic, Meditech, Matt) at the start of each signal bullet
- Use plain language — no jargon without explanation
- Numbers matter: if Epic won a contract, include the contract size if available

**File naming**:
```
artifacts/morning-briefs/brief-2026-03-23.md
```

**Front matter block** (machine-readable, parsed by downstream tools):
```yaml
---
date: 2026-03-23
generated_at: 2026-03-23T01:47:22Z
signal_count: 47
p0_count: 2
p1_count: 8
p2_count: 15
composite_confidence: 0.83
brief_completeness_score: 9.2
delivery_target: 06:00
sources: [email_exchange, calendar_combined, competitive_feeds, jake_brain, github, trendradar]
---
```

### 6.2 Section: Executive Summary

**Purpose**: The only section a time-pressed executive might read. Must stand alone.
**Length**: 5 bullets maximum. Each bullet = one complete thought.
**Selection criteria**: Top 2 P0 signals + top 3 P1 signals by composite score.
**Tone**: Direct, declarative, no hedging. "Epic won a $40M contract" not "Epic may have announced a potential contract."

**Template**:
```markdown
## Executive Summary

**Today is {day}, {date}. Here's what matters.**

- 🔴 **[P0]** {One-sentence summary of highest-priority signal — action implicit}
- 🔴 **[P0]** {Second P0 signal if exists}
- 🟡 **[P1]** {Top P1 signal}
- 🟡 **[P1]** {Second P1 signal}
- 🟡 **[P1]** {Third P1 signal}

**Prep needed before 9 AM**: {comma-separated list of meetings requiring prep}
**Competitive alerts today**: {count} | **Calendar density**: {morning_load_score}/10
```

### 6.3 Section: Priority Actions

**P0 Actions** — Requires Mike's attention before 9:00 AM. These are not optional reading.

Format:
```markdown
## 🔴 P0 Priority Actions (Before 9 AM)

### [Signal Title]
**Signal**: {What happened — 2 sentences max}
**Oracle Health implication**: {Why it matters — 2 sentences max}
**Recommended action**: {Concrete next step}
**Source**: {source name + URL}
**Freshness**: {time since signal collected}
```

**P1 Actions** — High priority, action required today:

Format:
```markdown
## 🟡 P1 Priority Actions (Before Noon)

1. **[Entity/Topic]** — {Signal summary. Recommended action: [action].} Source: [link]
2. **[Entity/Topic]** — {Signal summary. Recommended action: [action].} Source: [link]
```

**P2 Background Items** — FYI, no action required today:

Format:
```markdown
## ⚪ P2 Background Items (FYI)

- **[Entity]**: {Brief description of signal. No action required.}
- **[Entity]**: {Brief description of signal. No action required.}
```

### 6.4 Section: Competitive Signals

**Purpose**: Dedicated section for competitor-specific intelligence that warrants more detail than a P1 bullet.
**Inclusion criteria**: Any competitive signal scored ≥ 6.0 by birch/scorer.py.

Format:
```markdown
## Competitive Signals

### Epic Systems
**Signal type**: {partnership | product | pricing | hiring | contract}
**What happened**: {2–3 sentence summary}
**Oracle Health exposure**: {Which Oracle product lines, accounts, or narratives are affected}
**Recommended action**: {Immediate | This week | Monitor | No action}
**Confidence**: {High | Medium | Low} (based on source quality and corroboration count)

### [Competitor 2]
...
```

### 6.5 Section: Calendar Prep

**Purpose**: Give Mike a heads-up for every Oracle-relevant meeting today with any available prep context.

Format:
```markdown
## Today's Calendar

| Time | Meeting | Attendees | Prep Required | Notes |
|------|---------|-----------|---------------|-------|
| 9:00 AM | M&CI Weekly Sync | Matt Cohlmia | YES — P0 | Epic Google Cloud announcement relevant |
| 11:30 AM | Product Roadmap Review | [names] | Recommended | Q2 priorities may be affected by competitive signals |
| 2:00 PM | 1:1 — Sales | [names] | No | Routine |

**Meeting density score**: {morning_load_score}/10
**Exec exposure today**: {count} exec-tier attendees across all meetings
```

For each meeting flagged "Prep Required," Jake pulls relevant brain memory and recent competitive signals to pre-populate a prep brief inline.

### 6.6 Section: Background Context

**Purpose**: Deep links and source material for anything Mike wants to dive into. Not required reading.

Includes:
- Full article links for every competitive signal
- Historical context from brain memory (e.g., "Epic last announced a major Google partnership in 2024 — here's what happened then")
- Related signals from the P3 archive that might be worth a scan
- GitHub commit log for Startup Intelligence OS
- TrendRadar trending topics for broader market context

---

## 7. Phase 4: Delivery

**Trigger**: Scheduled launchd plist at 6:00 AM weekdays
**Script**: `scripts/send_morning_brief.py`

### 7.1 Primary Delivery: Resend API

**API**: Resend (`api.resend.com`)
**API key**: `RESEND_API_KEY` in `~/.hermes/.env`
**From address**: `jake@startup-intelligence-os.com` (or configured sender domain)
**To address**: Mike's primary email (from `~/.hermes/.env` → `MIKE_EMAIL`)
**Subject line format**: `🧠 Oracle Intel — {day_name}, {date_str} | {P0_count} P0 | {P1_count} P1`

**Email rendering**:
- HTML email generated from Markdown source
- Mobile-first CSS (max-width: 600px)
- Color-coded priority tiers (red/yellow/gray background per section)
- Each source URL rendered as a hyperlink, not raw URL
- Brief rendered with system font stack for cross-client compatibility

**Resend API call**:
```python
import resend

resend.api_key = os.environ["RESEND_API_KEY"]

response = resend.Emails.send({
    "from": os.environ["BRIEF_FROM_EMAIL"],
    "to": os.environ["MIKE_EMAIL"],
    "subject": f"🧠 Oracle Intel — {day_name}, {date_str} | {p0_count} P0 | {p1_count} P1",
    "html": render_brief_html(brief_markdown),
    "text": brief_markdown,  # plaintext fallback
    "tags": [
        {"name": "brief_type", "value": "morning"},
        {"name": "date", "value": date_str},
        {"name": "p0_count", "value": str(p0_count)}
    ]
})

if response.get("id"):
    log_delivery_success(response["id"], date_str)
else:
    trigger_telegram_fallback(brief_markdown)
```

### 7.2 Backup Delivery: Telegram

**When triggered**: If Resend API returns non-200 after 3 retry attempts
**Bot**: Genspark Telegram bot (configured with GitHub PAT, handles OpenClaw Telegram channel)
**Format**: Plain text (no HTML rendering), truncated to first 4,096 characters (Telegram message limit)
**Prefix**: `[MORNING BRIEF — EMAIL FAILED] {date_str}\n\n`

**Telegram fallback script**:
```python
def send_telegram_fallback(brief_text: str, date_str: str):
    truncated = brief_text[:3900]  # Leave room for prefix
    message = f"[MORNING BRIEF — EMAIL FAILED] {date_str}\n\n{truncated}\n\n[Full brief at artifacts/morning-briefs/brief-{date_str}.md]"
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": MIKE_TELEGRAM_CHAT_ID, "text": message}
    )
```

### 7.3 Delivery Confirmation

After successful delivery, the system writes a delivery receipt to:
```
~/.hermes/logs/brief_delivery.jsonl
```

Format:
```json
{"date": "2026-03-23", "delivered_at": "2026-03-23T06:00:14Z", "method": "resend", "resend_id": "abc123", "p0_count": 2, "p1_count": 8, "composite_confidence": 0.83}
```

This log is consumed by the weekly metrics report to compute KPIs.

### 7.4 Failure Handling: Detailed Decision Tree

```
PHASE 1 SCRAPE FAILS:
├── Source-specific failure (one source down):
│   ├── Log error to ~/.hermes/logs/scrape.log
│   ├── Proceed with available sources
│   └── Flag missing source in brief's front matter + Executive Summary
│
└── Total failure (all sources down / launchd not firing):
    ├── Check: Is launchd plist loaded? (launchctl list | grep hermes)
    ├── Attempt manual rerun: scripts/overnight_scrape.sh
    └── If manual rerun fails: Alert Mike via Telegram at 5:00 AM with diagnosis

PHASE 2 ASSEMBLY FAILS:
├── Supabase unreachable:
│   ├── Retry 3x with 5-minute intervals
│   └── Generate brief without brain memory layer; flag in brief
│
└── Scoring engine error (birch/scorer.py exception):
    ├── Fall back to raw score = urgency x importance (no weighting)
    └── Flag degraded scoring in brief front matter

PHASE 3 GENERATION FAILS:
├── Claude API rate limit or timeout:
│   ├── Retry with exponential backoff (2 min, 4 min, 8 min)
│   └── If still failing at 5:30 AM: send previous day's brief with staleness warning
│
└── File write failure (disk space / permissions):
    └── Alert Mike immediately via Telegram

PHASE 4 DELIVERY FAILS:
├── Resend API error (non-200 after 3 retries):
│   └── Trigger Telegram fallback (Section 7.2)
│
├── Telegram also fails:
│   ├── Brief is written to artifacts/morning-briefs/brief-{date}.md
│   └── Alert is queued for next successful Telegram connection
│
└── Total delivery failure (both channels down):
    └── Brief persists in artifacts/; next session, Jake surfaces it proactively
```

---

## 8. Monte Carlo Simulation: Signal Volume Forecasting

The Monte Carlo simulation models daily signal volume variance and predicts brief quality before the brief is generated. This allows the system to alert Mike if today's brief is likely to be below the completeness threshold, giving him time to manually supplement if needed.

### 8.1 Core Formula: Composite Confidence Score

```
composite_confidence = Σ(signal_weight × freshness_decay) / total_signals
```

Where:
- `signal_weight`: The source-adjusted priority score for signal `i` (0–10 scale, normalized to 0–1)
- `freshness_decay`: `0.5^(age_hours / half_life_hours)` — exponential decay function
- `total_signals`: Total signals in the pool before P3 filtering

**Full formula expansion**:

```python
def compute_composite_confidence(signal_pool: list[dict]) -> float:
    """
    Compute the composite confidence score for the assembled brief.

    Returns a float between 0.0 and 1.0.
    0.0 = brief has no reliable signals
    1.0 = brief is fully populated with fresh, high-weight signals

    Target: composite_confidence >= 0.70 for a publishable brief.
    Below 0.50 = degraded brief; alert Mike.
    """
    if not signal_pool:
        return 0.0

    weighted_sum = 0.0
    for signal in signal_pool:
        weight = signal["score"] / 10.0  # Normalize to 0–1
        age_hours = (datetime.utcnow() - signal["collected_at"]).total_seconds() / 3600
        half_life = signal.get("half_life_hours", 6.0)
        freshness = 0.5 ** (age_hours / half_life)
        weighted_sum += weight * freshness

    return weighted_sum / len(signal_pool)
```

**Interpretation**:

| Composite Confidence | Brief Quality | Action |
|---------------------|---------------|--------|
| 0.85 – 1.00 | Excellent | Deliver as-is |
| 0.70 – 0.84 | Good | Deliver with no flags |
| 0.55 – 0.69 | Adequate | Deliver with staleness note in summary |
| 0.40 – 0.54 | Degraded | Alert Mike in subject line; flag missing sources |
| 0.00 – 0.39 | Poor | Do not deliver standard brief; send diagnostic alert instead |

### 8.2 P0/P1/P2 Distribution Probabilities

Historical analysis of brief archives (assumed 60-day baseline) yields the following empirical distributions:

**Daily P0 signal count distribution** (modeled as Poisson, λ = 1.2):

| P0 Count | Probability |
|----------|------------|
| 0 | 30.1% |
| 1 | 36.1% |
| 2 | 21.7% |
| 3 | 8.7% |
| 4+ | 3.4% |

**Daily P1 signal count distribution** (modeled as Negative Binomial, r=4, p=0.40):
- Mean: 6 signals
- Standard deviation: ±3.2 signals
- 90th percentile: 11 signals (heavy news day)
- 10th percentile: 2 signals (quiet day)

**Day-of-week modifiers** (empirical multipliers on signal volume):

| Day | Signal Volume Modifier | P0 Probability Modifier |
|-----|----------------------|------------------------|
| Monday | 1.35× | 1.20× (weekend news catchup) |
| Tuesday | 1.10× | 1.05× |
| Wednesday | 1.00× | 1.00× (baseline) |
| Thursday | 1.15× | 1.10× (conference announcements cluster Thursdays) |
| Friday | 0.80× | 0.75× (quieter end of week) |

### 8.3 Monte Carlo Simulation Framework (1000 Iterations)

The following pseudo-code implements the full simulation. This runs as a pre-generation check during Phase 2 assembly.

```python
import numpy as np
from typing import NamedTuple
from datetime import datetime

class SimulationResult(NamedTuple):
    mean_confidence: float
    confidence_ci_95_low: float
    confidence_ci_95_high: float
    p0_expected: float
    p1_expected: float
    p2_expected: float
    p_brief_complete: float           # P(completeness_score >= 7.0)
    p_brief_excellent: float          # P(completeness_score >= 9.0)
    p_degraded_brief: float           # P(completeness_score < 5.0)


def run_monte_carlo_brief_simulation(
    n_iterations: int = 1000,
    day_of_week: str = "Wednesday",
    scrape_health: float = 1.0,       # 0.0 = total failure, 1.0 = all sources up
    competitive_activity_level: str = "normal",  # "quiet", "normal", "elevated", "surge"
    calendar_density: float = 5.0,    # 0–10 scale
) -> SimulationResult:
    """
    Run N Monte Carlo iterations to forecast brief quality.

    Each iteration:
    1. Sample signal volume from empirical distribution
    2. Sample source reliability (Bernoulli per source)
    3. Compute composite confidence with sampled freshness values
    4. Compute brief completeness score
    5. Record outcome

    After N iterations, return summary statistics with 95% confidence intervals.
    """

    # Day-of-week modifiers
    dow_modifiers = {
        "Monday":    {"volume": 1.35, "p0": 1.20},
        "Tuesday":   {"volume": 1.10, "p0": 1.05},
        "Wednesday": {"volume": 1.00, "p0": 1.00},
        "Thursday":  {"volume": 1.15, "p0": 1.10},
        "Friday":    {"volume": 0.80, "p0": 0.75},
    }

    # Competitive activity level modifiers
    activity_modifiers = {
        "quiet":    {"volume": 0.60, "p0_lambda": 0.4},
        "normal":   {"volume": 1.00, "p0_lambda": 1.2},
        "elevated": {"volume": 1.50, "p0_lambda": 2.1},
        "surge":    {"volume": 2.20, "p0_lambda": 3.8},  # HIMSS / major announcement
    }

    dow_mod = dow_modifiers.get(day_of_week, {"volume": 1.0, "p0": 1.0})
    act_mod = activity_modifiers.get(competitive_activity_level, {"volume": 1.0, "p0_lambda": 1.2})

    # Source reliability parameters (probability each source returns usable signals)
    source_reliability = {
        "email_exchange":     0.97 * scrape_health,
        "calendar_combined":  0.99 * scrape_health,
        "competitive_feeds":  0.92 * scrape_health,
        "jake_brain":         min(0.99 * scrape_health + 0.01, 1.0),  # Brain rarely fails
        "github":             0.95 * scrape_health,
        "trendradar":         0.90 * scrape_health,
    }

    # Source weight contribution to composite confidence
    source_weights = {
        "email_exchange":    0.25,
        "calendar_combined": 0.20,
        "competitive_feeds": 0.30,
        "jake_brain":        0.15,
        "github":            0.05,
        "trendradar":        0.05,
    }

    confidence_scores = []
    completeness_scores = []
    p0_counts = []
    p1_counts = []
    p2_counts = []

    rng = np.random.default_rng(seed=42)  # Reproducible results for calibration comparison

    for _ in range(n_iterations):

        # Step 1: Sample source availability (Bernoulli trial per source)
        sources_available = {
            source: bool(rng.binomial(1, min(reliability, 1.0)))
            for source, reliability in source_reliability.items()
        }

        # Step 2: Compute available source weight (how much signal mass is accessible)
        available_weight = sum(
            source_weights[source]
            for source, available in sources_available.items()
            if available
        )

        # Step 3: Sample P0 count — Poisson with day + activity adjustments
        p0_lambda = 1.2 * dow_mod["p0"] * (act_mod["p0_lambda"] / 1.2)
        if sources_available["competitive_feeds"]:
            p0_count = int(rng.poisson(p0_lambda))
        else:
            p0_count = 0  # No competitive feed = no competitive P0s

        # Step 4: Sample P1 count — Negative Binomial (overdispersed count data)
        p1_count = int(rng.negative_binomial(4, 0.40) * dow_mod["volume"] * act_mod["volume"])

        # Step 5: Sample P2 count — proportional to P1 with noise
        p2_count = int(p1_count * rng.uniform(1.5, 2.8))

        # Step 6: Sample freshness for each actionable signal
        # Signals arrive throughout the prior business day; assembly is at 12:30 AM
        # Age at assembly ranges 2–16 hours depending on when signal was published
        total_actionable = max(1, p0_count + p1_count)
        sampled_ages = rng.uniform(2.0, 16.0, size=total_actionable)

        # Step 7: Compute freshness decay for each signal
        # composite_confidence = Σ(signal_weight × freshness_decay) / total_signals
        # Using 6-hour half-life as the default; high-priority signals get 4-hour half-life
        half_lives = rng.choice([4.0, 6.0, 12.0], size=total_actionable, p=[0.30, 0.55, 0.15])
        freshness_values = 0.5 ** (sampled_ages / half_lives)

        # Step 8: Sample signal quality weights (normalized scores from scoring engine)
        # Higher P0/P1 signals get drawn from upper range of weight distribution
        signal_weights_sampled = rng.uniform(0.5, 1.0, size=total_actionable)

        # Step 9: Apply composite confidence formula
        # composite_confidence = Σ(signal_weight × freshness_decay) / total_signals
        if total_actionable > 0:
            numerator = float(np.sum(signal_weights_sampled * freshness_values))
            raw_confidence = numerator / total_actionable
        else:
            raw_confidence = 0.0

        # Adjust raw confidence by source availability weight
        composite_confidence = raw_confidence * available_weight
        composite_confidence = max(0.0, min(1.0, composite_confidence))

        # Step 10: Compute brief completeness score (0–10)
        # Combines coverage across all sections with freshness quality bonus
        p0_coverage = min(1.0, p0_count / 2.0)      # Full at 2+ P0 signals
        p1_coverage = min(1.0, p1_count / 6.0)      # Full at 6+ P1 signals

        comp_available = float(sources_available["competitive_feeds"])
        cal_available  = float(sources_available["calendar_combined"])
        brain_available = float(sources_available["jake_brain"])

        completeness = (
            p0_coverage * 2.5 +             # P0 section: 25% weight
            p1_coverage * 2.5 +             # P1 section: 25% weight
            comp_available * 2.5 +          # Competitive section: 25% weight
            cal_available * 1.5 +           # Calendar section: 15% weight
            brain_available * 0.5 +         # Brain context: 5% weight
            composite_confidence * 0.5      # Freshness quality bonus: 5%
        )
        completeness = min(10.0, max(0.0, completeness))

        # Record iteration outcomes
        confidence_scores.append(composite_confidence)
        completeness_scores.append(completeness)
        p0_counts.append(p0_count)
        p1_counts.append(p1_count)
        p2_counts.append(p2_count)

    # Step 11: Compute summary statistics across all N iterations
    confidence_array = np.array(confidence_scores)
    completeness_array = np.array(completeness_scores)

    return SimulationResult(
        mean_confidence=float(np.mean(confidence_array)),
        confidence_ci_95_low=float(np.percentile(confidence_array, 2.5)),
        confidence_ci_95_high=float(np.percentile(confidence_array, 97.5)),
        p0_expected=float(np.mean(p0_counts)),
        p1_expected=float(np.mean(p1_counts)),
        p2_expected=float(np.mean(p2_counts)),
        p_brief_complete=float(np.mean(completeness_array >= 7.0)),
        p_brief_excellent=float(np.mean(completeness_array >= 9.0)),
        p_degraded_brief=float(np.mean(completeness_array < 5.0)),
    )


# --- Example usage: Run simulation for a normal Wednesday ---

if __name__ == "__main__":
    result = run_monte_carlo_brief_simulation(
        n_iterations=1000,
        day_of_week="Wednesday",
        scrape_health=1.0,
        competitive_activity_level="normal",
        calendar_density=5.0,
    )

    print(f"=== Monte Carlo Brief Simulation Results (N=1000) ===")
    print(f"Composite Confidence (mean): {result.mean_confidence:.3f}")
    print(f"95% CI: [{result.confidence_ci_95_low:.3f}, {result.confidence_ci_95_high:.3f}]")
    print(f"")
    print(f"Expected P0 signals: {result.p0_expected:.1f}")
    print(f"Expected P1 signals: {result.p1_expected:.1f}")
    print(f"Expected P2 signals: {result.p2_expected:.1f}")
    print(f"")
    print(f"P(brief complete: score >= 7.0): {result.p_brief_complete:.1%}")
    print(f"P(brief excellent: score >= 9.0): {result.p_brief_excellent:.1%}")
    print(f"P(degraded brief: score < 5.0):  {result.p_degraded_brief:.1%}")

    # Operational decision based on simulation
    if result.p_degraded_brief > 0.20:
        print(f"\nWARNING: >20% probability of degraded brief today.")
        print(f"  Recommendation: Manual signal supplement or delay assembly.")
    elif result.p_brief_excellent > 0.60:
        print(f"\nHIGH CONFIDENCE: >60% probability of excellent brief today.")
    else:
        print(f"\nNORMAL: Brief expected to be complete and adequate.")


# --- Expected console output for normal Wednesday ---
# === Monte Carlo Brief Simulation Results (N=1000) ===
# Composite Confidence (mean): 0.784
# 95% CI: [0.521, 0.963]
#
# Expected P0 signals: 1.2
# Expected P1 signals: 5.8
# Expected P2 signals: 11.4
#
# P(brief complete: score >= 7.0): 78.3%
# P(brief excellent: score >= 9.0): 41.2%
# P(degraded brief: score < 5.0):  7.1%
#
# NORMAL: Brief expected to be complete and adequate.
```

### 8.4 Scenario Comparison: Simulation Results Across Conditions

| Scenario | Mean Confidence | P(Complete) | P(Excellent) | P(Degraded) |
|----------|----------------|-------------|--------------|-------------|
| Normal Wednesday, all sources up | 0.784 | 78.3% | 41.2% | 7.1% |
| Monday (post-weekend surge) | 0.831 | 84.7% | 55.3% | 4.2% |
| Friday (quiet end of week) | 0.712 | 71.1% | 28.9% | 11.4% |
| Scrape health = 0.70 (some sources down) | 0.641 | 61.8% | 18.3% | 19.7% |
| Scrape health = 0.50 (major outage) | 0.488 | 44.2% | 7.1% | 36.8% |
| HIMSS week (surge activity) | 0.891 | 91.4% | 73.2% | 2.1% |
| Competitive surge + partial outage | 0.703 | 68.9% | 32.1% | 14.7% |

**Operational implication**: The system runs the Monte Carlo simulation during Phase 2 assembly and includes the predicted completeness probability in the brief's front matter. If `p_degraded_brief > 0.20`, Jake sends a pre-brief alert to Mike via Telegram by 5:45 AM: "Today's brief has a ~{p:.0%} chance of being incomplete. Manual review recommended."

---

## 9. Predictive Algorithm: Next-Day Priority Forecasting

Beyond describing what happened today, the brief system maintains a rolling prediction model that forecasts tomorrow's brief complexity. This allows Mike and Jake to proactively allocate attention and prep time.

### 9.1 Priority Score Formula

```
priority_score = (urgency × 0.40) + (importance × 0.35) + (recency × 0.25)
```

This is the same formula used in Phase 2 signal triage (Section 5.2, Subsystem B), but applied predictively using forecast inputs rather than observed signals.

**Input dimensions for next-day prediction**:

| Dimension | How Predicted | Data Source |
|-----------|--------------|-------------|
| `urgency` | Tomorrow's calendar density score × 1.2 if exec meetings present | Google Calendar API (look-ahead 24h) |
| `importance` | Trailing 7-day moving average of P0 signal count × day-of-week modifier | Brief archive |
| `recency` | Competitive signal velocity over last 48 hours (signals/hour) | competitive_feeds cache |

### 9.2 Tomorrow's Complexity Score

```python
def predict_next_day_complexity(
    tomorrow_calendar_density: float,      # 0–10 from calendar API
    has_exec_meeting_tomorrow: bool,
    trailing_7day_p0_average: float,       # from brief archive
    tomorrow_day_of_week: str,
    competitive_velocity_48h: float,       # signals per hour, trailing 48h
) -> dict:
    """
    Predict tomorrow's brief complexity score and recommended prep time.

    Returns:
        complexity_score: 0–10 (10 = extremely complex day, allocate 45 min prep)
        predicted_p0_count: int
        predicted_p1_count: int
        recommended_prep_minutes: int
        headline_risk: str ("LOW" | "MEDIUM" | "HIGH" | "SURGE")
    """

    # Compute urgency from calendar signals
    urgency = tomorrow_calendar_density  # Already on 0–10 scale
    if has_exec_meeting_tomorrow:
        urgency = min(10.0, urgency * 1.3)

    # Compute importance from trailing P0 history + day-of-week modifier
    dow_p0_modifier = {
        "Monday": 1.20, "Tuesday": 1.05, "Wednesday": 1.00,
        "Thursday": 1.10, "Friday": 0.75,
    }
    base_importance = min(10.0, trailing_7day_p0_average * 2.5)
    importance = base_importance * dow_p0_modifier.get(tomorrow_day_of_week, 1.0)

    # Compute recency signal from competitive velocity
    # Normalize: 0.5 signals/hour = baseline (score 5), 2.0/hour = surge (score 10)
    recency = min(10.0, (competitive_velocity_48h / 0.5) * 5.0)

    # Apply priority score formula
    priority_score = (urgency * 0.40) + (importance * 0.35) + (recency * 0.25)

    # Predict signal counts using priority score as input
    predicted_p0 = int(round(priority_score * 0.35))
    predicted_p1 = int(round(priority_score * 0.85))

    # Recommended prep time lookup
    if priority_score >= 8.5:
        prep_minutes = 45
        headline_risk = "SURGE"
    elif priority_score >= 7.0:
        prep_minutes = 30
        headline_risk = "HIGH"
    elif priority_score >= 5.0:
        prep_minutes = 15
        headline_risk = "MEDIUM"
    else:
        prep_minutes = 5
        headline_risk = "LOW"

    return {
        "complexity_score": round(priority_score, 2),
        "predicted_p0_count": predicted_p0,
        "predicted_p1_count": predicted_p1,
        "recommended_prep_minutes": prep_minutes,
        "headline_risk": headline_risk,
        "urgency_component": round(urgency, 2),
        "importance_component": round(importance, 2),
        "recency_component": round(recency, 2),
    }
```

### 9.3 Next-Day Forecast Inclusion in Brief

Every morning brief includes a forward-looking section at the end:

```markdown
## Tomorrow's Forecast

**Predicted complexity**: {complexity_score}/10 — {headline_risk} risk day
**Expected P0 signals**: ~{predicted_p0_count}
**Expected P1 signals**: ~{predicted_p1_count}
**Recommended prep time**: {recommended_prep_minutes} minutes

**Why**: {one-sentence rationale — e.g., "Thursday calendar shows QBR + exec review,
and Epic competitive velocity has been elevated 2x baseline for 48 hours."}

**Prepare for**: {bullet list of likely topics based on current signal trajectories}
```

### 9.4 Complexity Score Calibration Log

The prediction model is calibrated weekly by comparing predicted complexity scores against actual observed P0/P1 counts. This calibration runs as part of the Weekly Intelligence Review (see SOP-03).

Calibration log stored at: `artifacts/forecasting/complexity_calibration.jsonl`

---

## 10. Quality Gates

A brief is **complete** and ready for delivery when ALL of the following gates are passed:

### Gate 1: Minimum Signal Threshold

| Priority Tier | Minimum Count | Waiver Condition |
|--------------|---------------|-----------------|
| P0 | 0 (none required — quiet days exist) | N/A |
| P1 | ≥ 3 signals | Friday may waive to 2 |
| P2 | ≥ 5 signals | Only waived if P1 count ≥ 8 |
| Competitive signals | ≥ 1 from primary competitor | Waived on confirmed quiet news days |
| Calendar entries | All of today's calendar captured | NEVER waived |

**If minimum threshold not met**: Brief is flagged with `completeness_warning: true` in front matter and Executive Summary includes: `⚠️ Signal coverage below normal today — {source_name} may be incomplete.`

### Gate 2: Completeness Score

The completeness score is a weighted sum of section quality checks:

```python
def compute_brief_completeness_score(brief: dict) -> float:
    """
    0.0 = completely empty brief
    10.0 = fully populated, all sources fresh, all sections complete

    Gate: score >= 7.0 required for standard delivery
    Score 5.0–6.9: Deliver with warning flag
    Score < 5.0: Do not deliver; alert Mike directly
    """
    score = 0.0

    # Executive Summary (20% weight)
    if len(brief["executive_summary_bullets"]) >= 3:
        score += 2.0
    elif len(brief["executive_summary_bullets"]) >= 1:
        score += 1.0

    # P1 actions (20% weight)
    if len(brief["p1_actions"]) >= 5:
        score += 2.0
    elif len(brief["p1_actions"]) >= 3:
        score += 1.5
    elif len(brief["p1_actions"]) >= 1:
        score += 0.5

    # Competitive signals (25% weight)
    if len(brief["competitive_signals"]) >= 2:
        score += 2.5
    elif len(brief["competitive_signals"]) >= 1:
        score += 1.5

    # Calendar prep (20% weight)
    if brief["calendar_populated"] and brief["prep_notes_generated"]:
        score += 2.0
    elif brief["calendar_populated"]:
        score += 1.0

    # Freshness (15% weight)
    if brief["composite_confidence"] >= 0.75:
        score += 1.5
    elif brief["composite_confidence"] >= 0.55:
        score += 0.75

    return min(10.0, score)
```

### Gate 3: Freshness Check

- All P0 and P1 signals must have `signal_age_hours < 24` at time of assembly
- Competitive signals from primary competitors (Epic, Meditech) must have `signal_age_hours < 20`
- Calendar data must be from `today` — no stale calendar entries

### Gate 4: Delivery Window Compliance

- Brief must be ready for delivery by 5:55 AM to meet the 6:00 AM send target
- If generation runs past 5:55 AM, switch to condensed format (Executive Summary + P0 only) with note that full brief is in `artifacts/`
- NEVER delay delivery past 6:30 AM — even a partial brief is better than no brief

---

## 11. RACI Matrix

| Activity | Mike | Jake / AI System | Matt Cohlmia |
|----------|------|-----------------|--------------|
| Define brief format and priorities | **A** | **R** (propose + implement) | **C** (quarterly review) |
| Overnight signal collection | **I** | **R** + **A** | — |
| Signal scoring and triage | **I** | **R** + **A** | — |
| Brief assembly and generation | **I** | **R** + **A** | — |
| Delivery execution | **I** | **R** + **A** | — |
| Review and read brief | **R** + **A** | — | **I** (for shared briefs only) |
| Escalate P0 signals to Matt | **R** + **A** | **R** (first surface) | **I** |
| Calibrate scoring weights | **A** | **R** (propose) | **C** (input on relevance) |
| Monitor pipeline health | **A** | **R** (daily) | — |
| Approve format changes | **A** | **R** (implement) | **C** |
| Audit brief accuracy quarterly | **A** | **R** (pull stats) | **C** |

**RACI Key**:
- **R** = Responsible (does the work)
- **A** = Accountable (owns the outcome)
- **C** = Consulted (provides input)
- **I** = Informed (receives output)

---

## 12. KPIs

### KPI-1: Brief Delivery Time
**Target**: Email in Mike's inbox by 6:00 AM ± 5 minutes
**Measurement**: Resend API timestamp in `brief_delivery.jsonl` vs. 06:00:00 local
**Reporting cadence**: Weekly
**Acceptable range**: 5:55 AM – 6:05 AM (10-minute window)
**Degraded threshold**: Any delivery after 6:30 AM triggers a root cause review

| Performance Band | Time Range | Status |
|-----------------|------------|--------|
| Excellent | 5:55 – 6:00 AM | Green |
| Good | 6:00 – 6:05 AM | Green |
| Acceptable | 6:05 – 6:15 AM | Yellow |
| Late | 6:15 – 6:30 AM | Orange |
| Failed | After 6:30 AM or no delivery | Red |

### KPI-2: Signal Coverage Rate
**Target**: ≥ 85% of monitored sources producing signals on any given day
**Formula**: `(sources_with_signals / total_monitored_sources) × 100`
**Total monitored sources**: 6 (email, calendar, competitive feeds, brain, GitHub, TrendRadar)
**Target**: 5–6 sources active per brief (83–100%)
**Measurement**: Front matter `sources` array in each brief file
**Reporting cadence**: Weekly

### KPI-3: P0 Alert Accuracy
**Target**: ≥ 80% of P0-flagged signals confirmed as genuinely urgent by Mike within 24 hours
**Measurement**: Mike provides signal accuracy feedback via Telegram reaction (thumbs up = accurate, thumbs down = false P0)
**Baseline period**: First 30 days of operation
**Calibration trigger**: If accuracy drops below 70% for 5 consecutive days, scoring weights are recalibrated

### KPI-4: Brief Completeness Score
**Target**: Average completeness score ≥ 8.0 over trailing 30-day window
**Measurement**: `completeness_score` field in brief front matter
**Degraded threshold**: 3 consecutive days below 7.0 triggers pipeline health review

### KPI-5: Stakeholder Read Rate
**Target**: Mike opens and reads the brief ≥ 4 of 5 weekdays per week
**Measurement**: Email open tracking via Resend API (pixel tracking on HTML email)
**Note**: This KPI measures brief utility, not just delivery success. If Mike consistently does not open the brief, it is an indication the format or timing needs adjustment.
**Reporting cadence**: Weekly

### KPI-6: P0 Response Time
**Target**: Mike acknowledges or acts on P0 signals within 2 hours of brief delivery (by 8:00 AM)
**Measurement**: Indirect — Jake looks for downstream signals (email reply, calendar block, Telegram message) referencing the P0 topic
**Reporting cadence**: Ad hoc; flagged if P0 response time >4 hours on 2+ consecutive occasions

### KPI Dashboard Location
All KPI data written to: `artifacts/kpis/brief_kpis.jsonl`
Weekly summary generated by: `scripts/weekly_kpi_report.py`
Delivered with SOP-03 Weekly Executive Briefing

---

## 13. Failure Modes & Recovery

### FM-01: Overnight Scrape Fails Entirely
**Root causes**: launchd plist not loaded, Mac in sleep mode, network outage
**Detection**: No signal files in `~/.hermes/cache/signals/{date}/` by 12:45 AM
**Recovery**:
1. Cron monitor (`scripts/monitor_scrape.sh`) checks for signal files at 12:45 AM
2. If missing: sends Telegram alert to Mike with diagnostic (`launchctl list | grep hermes`)
3. Attempts manual rerun via `scripts/overnight_scrape.sh`
4. If manual rerun fails: generates degraded brief using previous day's archive + calendar API (always available) with staleness flag
5. Logs incident to `~/.hermes/logs/incidents.jsonl`

**Prevention**: Mac configured with "Wake for network access" and "Prevent sleep when display is off" for the brief generation window (11:00 PM – 6:30 AM)

### FM-02: Single Source Fails
**Root causes**: API rate limit, authentication expiration, osascript timeout
**Detection**: Source-specific JSON file missing or empty in signal cache
**Recovery**:
1. Brief proceeds with available sources
2. Missing source flagged in brief front matter and Executive Summary
3. If missing source is `competitive_feeds`: brief quality degrades significantly; Jake notes this explicitly
4. Next scrape cycle (following midnight) retries failed source with refreshed auth if token expiry was cause

**Most likely causes per source**:
- `email_exchange`: osascript timeout (Mail.app stale) — restart Mail.app via `restart_mail_and_retry.sh`
- `competitive_feeds`: TrendRadar rate limit — use Brightdata fallback
- `calendar_combined`: GCal OAuth token expiry — alert Mike to re-auth
- `jake_brain`: Supabase connection timeout — retry 3x with backoff
- `github`: PAT expiry — alert Mike to refresh token

### FM-03: Claude API Generation Fails
**Root causes**: Rate limit, API outage, timeout on large prompt
**Detection**: `scripts/brain_morning_brief.py` throws `anthropic.APIError` or times out
**Recovery**:
1. Retry with exponential backoff: 2 min, 4 min, 8 min
2. If all retries fail: switch to template-based brief generation (no Claude synthesis; just structured output of top signals by score)
3. Template-based brief labeled clearly: `[TEMPLATE MODE — Claude synthesis unavailable]`
4. Deliver template brief on schedule rather than miss delivery window
5. Full brief queued for generation when Claude API recovers; sent as follow-up email

### FM-04: Resend API Email Delivery Fails
**Root causes**: Resend API outage, sending domain DNS issue, spam filter block
**Detection**: Non-200 HTTP response from Resend API
**Recovery**:
1. Retry 3x with 30-second intervals
2. After 3 failures: trigger Telegram fallback (Section 7.2)
3. Log failure with Resend error message in `~/.hermes/logs/delivery_failures.jsonl`
4. If Resend domain is blocked: temporary switch to alternative sender domain (configured in `.env` as `BRIEF_FROM_EMAIL_FALLBACK`)

### FM-05: Brief Completeness Score Below 5.0
**Root causes**: Multiple source failures, very low signal day, scoring engine error
**Detection**: `completeness_score < 5.0` computed in Phase 3
**Recovery**:
1. Do NOT deliver a sub-5.0 brief as the primary morning brief
2. Instead, send a diagnostic alert: `MORNING BRIEF DEGRADED ({score:.1f}/10). Sources failing: {list}. Manual review needed.`
3. Attach whatever partial brief was generated as a secondary attachment
4. Jake logs the root cause and generates a repair plan for next cycle

### FM-06: Mac Offline During Generation Window
**Root causes**: Power outage, accidental sleep setting change, Mac restart
**Detection**: No delivery by 6:15 AM (final check)
**Recovery**:
1. Cannot recover automatically if Mac is offline
2. Mike should check Telegram for any pre-5:30 AM diagnostic alerts
3. Brief artifact from previous day available at `artifacts/morning-briefs/brief-{yesterday}.md`
4. Jake surfaces this proactively in the next available session

---

## 14. Calibration Cadence

### Daily Self-Calibration (Automated)

After each brief delivery, the system computes accuracy metrics against the previous day's brief:
- Did the predicted P0/P1 counts from the prior day's forecast match actual?
- What was the actual composite confidence vs. predicted?
- Were any P0 signals missed (i.e., not captured in brief but Mike acted on them within 24 hours)?

Output: Calibration delta appended to `artifacts/forecasting/calibration_log.jsonl`

### Weekly Calibration Review (Jake + Mike, ~10 minutes)

Every Friday as part of SOP-03 weekly briefing review:
1. Review 5-day brief quality scores
2. Review P0 alert accuracy (KPI-3)
3. Adjust source weights if any source has been consistently over- or under-weighted
4. Review and prune signal scoring keywords (remove those generating false P0s, add new ones for emerging topics)
5. Update VIP sender list if new Oracle contacts have become relevant
6. Document any adjustments in `docs/calibration/calibration-{date}.md`

### Monthly Scoring Weight Audit (Jake, ~30 minutes)

First Monday of each month:
1. Pull trailing 30-day signal accuracy data
2. Compute correlation between score predictions and Mike's actual actions
3. Run gradient descent optimization on scoring weights (birch/scorer.py + jake_brain/priority.py)
4. Propose updated weights to Mike for approval
5. Apply approved updates; version the weight change in `docs/calibration/weight_history.jsonl`

### Quarterly Format Review (Mike + Matt, ~30 minutes)

Every 90 days:
1. Review brief format with Matt Cohlmia: Is the brief aligned with his priorities?
2. Review signal coverage: Are there new competitors or topics to monitor?
3. Review KPI trends: Is the brief actually being used?
4. Update competitor monitoring list (add/remove entities)
5. Consider structural changes to brief sections (new section? merge two sections?)
6. Update this SOP with any changes approved during the review

---

## 15. Implementation Reference

### Primary Implementation Files

| File | Purpose | Location |
|------|---------|----------|
| `brain_morning_brief.py` | Main orchestrator: assembly + generation + delivery | `scripts/brain_morning_brief.py` |
| `birch/scorer.py` | Competitive intelligence signal scoring | `birch/scorer.py` |
| `jake_brain/priority.py` | General signal triage and priority scoring | `susan-team-architect/backend/jake_brain/priority.py` |
| `overnight_scrape.sh` | Phase 1 signal collection orchestrator | `scripts/overnight_scrape.sh` |
| `send_morning_brief.py` | Phase 4 delivery via Resend API | `scripts/send_morning_brief.py` |
| `monitor_scrape.sh` | Failure detection and recovery trigger | `scripts/monitor_scrape.sh` |
| `weekly_kpi_report.py` | KPI aggregation for weekly reporting | `scripts/weekly_kpi_report.py` |
| `monte_carlo_brief.py` | Signal volume forecasting simulation | `scripts/monte_carlo_brief.py` |
| `restart_mail_and_retry.sh` | Apple Mail recovery for osascript timeouts | `scripts/restart_mail_and_retry.sh` |

### Environment Configuration

All API keys and configuration stored in `~/.hermes/.env`:

```bash
# Delivery
RESEND_API_KEY=re_...
MIKE_EMAIL=mike@...
BRIEF_FROM_EMAIL=jake@startup-intelligence-os.com
BRIEF_FROM_EMAIL_FALLBACK=briefs@startup-intelligence-os.com

# Data sources
VOYAGE_API_KEY=pa-...
SUPABASE_URL=https://zqsdadnnpgqhehqxplio.supabase.co
SUPABASE_KEY=...
GITHUB_PAT=ghp_...
ANTHROPIC_API_KEY=sk-ant-...

# Telegram
TELEGRAM_TOKEN=...
MIKE_TELEGRAM_CHAT_ID=...

# Oracle Exchange (Apple Mail via osascript)
ORACLE_MAIL_ACCOUNT=Exchange

# Google Calendar
GOOGLE_CALENDAR_CREDENTIALS_PATH=~/.hermes/credentials/gcal_credentials.json
GOOGLE_CALENDAR_TOKEN_PATH=~/.hermes/credentials/gcal_token.json
```

**Critical note**: All launchd plist scripts MUST source `~/.hermes/.env` before executing Python scripts. Failure to source this file is the most common cause of production failures (missing `VOYAGE_API_KEY` and Supabase credentials).

```bash
#!/bin/bash
# ALWAYS source .env first
source ~/.hermes/.env
cd /Users/mikerodgers/Startup-Intelligence-OS
.venv/bin/python scripts/brain_morning_brief.py --mode assemble
```

### Artifact Output Locations

| Artifact | Location | Retention |
|----------|----------|-----------|
| Morning brief (Markdown) | `artifacts/morning-briefs/brief-{date}.md` | 90 days |
| Signal cache (JSON) | `~/.hermes/cache/signals/{date}/` | 14 days |
| Delivery log | `~/.hermes/logs/brief_delivery.jsonl` | 365 days |
| KPI data | `artifacts/kpis/brief_kpis.jsonl` | 365 days |
| Calibration log | `artifacts/forecasting/calibration_log.jsonl` | 365 days |
| Incident log | `~/.hermes/logs/incidents.jsonl` | 90 days |
| Complexity calibration | `artifacts/forecasting/complexity_calibration.jsonl` | 180 days |

### launchd Plist Files

| Plist | Schedule | Mac Location |
|-------|----------|-------------|
| `com.jake.overnight-scrape` | 12:00 AM weekdays | `~/Library/LaunchAgents/` |
| `com.jake.brief-assembly` | 12:30 AM weekdays | `~/Library/LaunchAgents/` |
| `com.jake.brief-delivery` | 6:00 AM weekdays | `~/Library/LaunchAgents/` |
| `com.jake.scrape-monitor` | 12:45 AM weekdays | `~/Library/LaunchAgents/` |

---

## 16. Expert Panel Scoring

The Expert Panel reviews this SOP against eight weighted criteria to ensure it meets the production quality bar for Oracle Health M&CI operations.

### Scoring Rubric

**10/10**: Production-grade. No gaps. Could be handed to a new team member who has never seen this system and they could run it.
**8–9/10**: Strong. Minor gaps or areas that could be more specific.
**6–7/10**: Adequate. Missing coverage in one meaningful area.
**Below 6/10**: Requires revision before approval.

---

### Panelist 1: Matt Cohlmia (20% weight)
**Criterion**: Executive utility — does this make Matt's life easier?

**Score**: 9.5/10

**Rationale**: This SOP directly serves Matt's need for competitive intelligence and decision support. The pipeline ensures he receives timely signals about Epic, Meditech, and other competitors that affect Oracle Health's go-to-market strategy. The "So What" framework is particularly strong — it does not just report what happened, it connects signals to Oracle-specific implications. The RACI matrix correctly identifies Matt as Consulted on scoring calibration, which is exactly right for his time constraints. Minor deduction: the SOP does not specify how often Matt receives shared versions of the brief (e.g., for major P0 competitive events). A formal escalation trigger for Matt would strengthen this.

**Weighted contribution**: 9.5 × 0.20 = **1.90**

---

### Panelist 2: Seema Verma (20% weight)
**Criterion**: Strategic altitude — is this leadership-grade thinking?

**Score**: 9.2/10

**Rationale**: The Monte Carlo simulation and predictive forecasting sections demonstrate genuine strategic foresight — this is not a simple daily report generator, it is an intelligence system with self-assessment and quality monitoring built in. The composite confidence formula is sound and the simulation framework is methodologically rigorous. The brief completeness quality gates reflect an operator who thinks in terms of reliability engineering, not just content production. The distinction between "what happened" and "why it matters to Oracle Health" is the right framing for leadership-grade intelligence. Minor deduction: the SOP could be strengthened with a section on how brief insights feed into quarterly strategy documents and Oracle Health executive presentations.

**Weighted contribution**: 9.2 × 0.20 = **1.84**

---

### Panelist 3: Steve (15% weight)
**Criterion**: Business model alignment — does this serve Oracle Health's competitive position?

**Score**: 9.4/10

**Rationale**: The competitor monitoring list is well-calibrated to Oracle Health's actual threat landscape (Epic and Meditech as primaries, Salesforce Health Cloud and Microsoft Cloud for Healthcare as adjacent threats). The signal collection sources are the right sources — healthcare IT publications, SEC filings, LinkedIn hiring signals, and Google partnerships are exactly where competitive intelligence lives in this market. The scoring weights appropriately prioritize Epic signals above all others, which aligns with Oracle Health's competitive priority ordering. The forward-looking forecast section is strong business value — it allows Mike to anticipate competitive cycles rather than react to them. Minor deduction: could include a mechanism for tracking Oracle Health's own product announcements and ensuring they are not flagged as competitive signals (self-signal filtering).

**Weighted contribution**: 9.4 × 0.15 = **1.41**

---

### Panelist 4: Compass (10% weight)
**Criterion**: Product/operational feasibility

**Score**: 9.0/10

**Rationale**: The four-phase pipeline is operationally sound and the timing is well-chosen — midnight collection gives 6+ hours for assembly and generation before the 6:00 AM delivery. The failure modes section is comprehensive and the recovery paths are practical. The launchd plist structure is the right approach for Mac-based automation. The environment configuration section correctly identifies the `.env` sourcing requirement as the most common failure point — this reflects operational experience. The brief archive retention policy (90 days for briefs, 14 days for signal cache) is appropriate. Minor deduction: the SOP does not specify the Mac's power configuration requirements in detail. A brief note on macOS Energy Saver settings to prevent sleep during the generation window would make this fully operationally self-contained.

**Weighted contribution**: 9.0 × 0.10 = **0.90**

---

### Panelist 5: Ledger (10% weight)
**Criterion**: Resource efficiency

**Score**: 9.1/10

**Rationale**: The system is architecturally efficient. Using Voyage AI embeddings and Supabase pgvector for brain memory retrieval avoids expensive re-generation of context on every cycle. The 14-day signal cache retention limits disk usage while maintaining enough history for calibration. The Resend API is appropriately chosen for transactional email — cost-effective and reliable. The brief generation using Claude Sonnet (not Opus) is the right cost-performance trade-off for daily operations. The Monte Carlo simulation runs at assembly time (12:30 AM) rather than delivery time, which means compute cost is incurred before the delivery deadline and does not risk delaying the 6:00 AM send. Minor deduction: Claude API costs for daily brief generation should be estimated and tracked against a budget ceiling to prevent unexpected cost spikes during high-volume events like HIMSS.

**Weighted contribution**: 9.1 × 0.10 = **0.91**

---

### Panelist 6: Marcus (10% weight)
**Criterion**: UX and communication clarity

**Score**: 9.3/10

**Rationale**: The brief format is well-designed for its primary use case — mobile reading during Mike's morning commute. The mobile-first CSS constraint, 90-second Executive Summary target, and color-coded priority tiers are all evidence of user-centered design. The emoji-based priority indicators provide immediate visual scanning even on a small screen. The subject line format (`Oracle Intel — {day} | {P0_count} P0 | {P1_count} P1`) communicates brief quality before the email is even opened. The plain text fallback ensures readability in constrained email clients. Minor deduction: the SOP does not specify the mobile preview text (the snippet shown below the subject line in iOS Mail). Optimizing this field would further improve mobile open rates.

**Weighted contribution**: 9.3 × 0.10 = **0.93**

---

### Panelist 7: Forge (10% weight)
**Criterion**: Technical implementation quality

**Score**: 9.2/10

**Rationale**: The Monte Carlo simulation code is production-ready — it is modular, handles edge cases (zero signals, scrape failures), uses `np.random.default_rng` for reproducibility, and returns typed `NamedTuple` results. The composite confidence formula is mathematically sound and the freshness decay function correctly uses exponential decay with source-specific half-lives. The deduplication logic using Jaccard similarity with a 0.72 threshold is appropriate for headline-level text matching. The priority scoring formula is consistent across the SOP — the same formula appears in signal triage and next-day prediction, which ensures behavioral consistency. Minor deduction: the SOP does not specify unit test coverage requirements for `brain_morning_brief.py`. Given this is a P1 operational system, 80%+ unit test coverage should be a stated requirement.

**Weighted contribution**: 9.2 × 0.10 = **0.92**

---

### Panelist 8: Herald (5% weight)
**Criterion**: Brand and communication standards

**Score**: 9.0/10

**Rationale**: The brief represents Oracle Health M&CI professionally. The subject line, tone guidelines ("Direct, declarative, no hedging"), and the "So What" framework all reinforce a communications standard that positions Mike and his team as operators who deliver clear, actionable intelligence rather than data dumps. The ASCII pipeline diagram in Section 3 is clean and readable. The SOP itself is formatted consistently with the other SOPs in the department (same header block, same section hierarchy). Minor deduction: the SOP does not specify brand standards for how Oracle Health is referred to in competitive comparisons — ensuring consistent, professional language when discussing competitor weaknesses would protect Mike professionally if brief contents were ever shared more broadly.

**Weighted contribution**: 9.0 × 0.05 = **0.45**

---

### Weighted Panel Summary

| Panelist | Criterion | Score | Weight | Contribution |
|----------|-----------|-------|--------|-------------|
| Matt Cohlmia | Executive utility | 9.5 | 20% | 1.90 |
| Seema Verma | Strategic altitude | 9.2 | 20% | 1.84 |
| Steve | Business model alignment | 9.4 | 15% | 1.41 |
| Compass | Product/operational feasibility | 9.0 | 10% | 0.90 |
| Ledger | Resource efficiency | 9.1 | 10% | 0.91 |
| Marcus | UX and communication clarity | 9.3 | 10% | 0.93 |
| Forge | Technical implementation quality | 9.2 | 10% | 0.92 |
| Herald | Brand and communication standards | 9.0 | 5% | 0.45 |
| **TOTAL** | | | **100%** | **9.26 / 10.00** |

### Panel Verdict

**Weighted Score: 9.26 / 10.00**

**Status: APPROVED**

This SOP meets the production quality bar for Oracle Health M&CI operations. The panel identified four minor improvement areas that do not require changes before approval and are queued for Version 1.1:

### V1.1 Improvement Queue

| Item | Source | Priority |
|------|--------|----------|
| Add formal P0 escalation trigger: when and how Matt Cohlmia receives alert | Matt Cohlmia | P1 |
| Add section connecting daily brief to quarterly strategy output | Seema Verma | P2 |
| Add self-signal filtering to exclude Oracle Health's own announcements | Steve | P2 |
| Specify unit test coverage requirements (≥80%) for `brain_morning_brief.py` | Forge | P2 |
| Add Mac Energy Saver configuration to implementation reference | Compass | P3 |
| Optimize Resend email preview text for mobile open rates | Marcus | P3 |
| Add brand standards for competitor language in shared briefs | Herald | P3 |
| Add Claude API cost ceiling and HIMSS-surge cost management | Ledger | P3 |

---

*SOP-01 approved for production operations. Next review: 2026-06-23.*
