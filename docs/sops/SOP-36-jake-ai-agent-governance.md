# SOP-36: Jake AI Agent Governance & Capability Review

**Owner**: Mike Rodgers
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-24
**Category**: Jake System Operations
**Priority**: P1 — Jake is a critical business system; it must be governed like one
**Maturity**: Documented (this SOP)
**Applies to**: Jake AI system, Hermes agent framework, all recipes and SOPs

---

## 1. Purpose

Define the governance model for Jake — Mike's AI executive assistant — covering capability reviews, safety guardrails, cost oversight, version control, onboarding new capabilities, and deprecation of stale ones. This SOP treats Jake as a managed business system, not a black box.

**Core principle**: An AI agent without governance is a liability. Jake's outputs inform business decisions, generate communications, and trigger real-world actions. Every systemic failure in Jake is a failure in Mike's business operations. Governance must match the stakes.

**Framework basis**: NIST AI Risk Management Framework (AI RMF 1.0), Google's SRE Error Budget model, and standard software asset lifecycle management adapted for AI systems.

---

## 2. Scope

### 2.1 In Scope

- Weekly capability health checks (jake-daily-self-test recipe)
- Monthly capability audits (jake-capability-audit recipe)
- Recipe development lifecycle: draft → test → production → deprecate
- Brain memory hygiene: staleness, consolidation, privacy classification
- API cost monitoring and budget governance
- Error log review and systematic failure prevention
- New SOP and recipe commissioning process
- Jake's security and credential vault governance

### 2.2 Out of Scope

- Day-to-day Jake usage (individual task execution)
- Oracle Health data security (governed by Oracle IT/security)
- Personal data decisions (family context governed by family access controls)

---

## 3. PHASE 1: Weekly Health Check (jake-daily-self-test)

**Frequency**: Daily automated, full review on Sunday
**Trigger**: `jake run jake-daily-self-test`
**Duration**: 5–10 minutes automated, 5 minute human review

### 3.1 The 10-Layer Health Check

Jake tests against 10 capability layers on every run:

| Layer | What Is Tested | Healthy Signal |
|-------|---------------|----------------|
| **L1: Brain Memory** | Supabase pgvector connectivity, query latency | <300ms P95, 0 errors |
| **L2: Nervous System** | Email and calendar monitoring daemon status | Last check < 15 min ago |
| **L3: Telegram Delivery** | Bot token valid, delivery confirmed | Last delivery < 24h |
| **L4: Recipe Execution** | 3 random recipes parsed and validated | 100% parse success |
| **L5: API Costs** | Daily spend vs. daily budget | Under budget |
| **L6: Error Budget** | 30-day error rate | < 1% of interactions |
| **L7: Knowledge Freshness** | Oldest semantic memory age | No domain > 30 days stale |
| **L8: Goal Tracking** | Active goals have been checked in on | No goal unchecked for > 7 days |
| **L9: Vault Credentials** | All registered services have valid creds | No expired secrets |
| **L10: SOP Currency** | Any SOP flagged for review by review date | No overdue reviews |

### 3.2 Health Score Interpretation

```
Score = (layers passing / 10) × 100

90-100%: Green — normal operations
70-89%:  Yellow — investigate failing layers, fix within 48h
50-69%:  Orange — one or more critical systems degraded, fix within 24h
< 50%:   Red — major system failure, escalate immediately
```

### 3.3 Common Failure Modes and Remedies

| Failure Mode | Root Cause | Remedy |
|-------------|-----------|--------|
| Brain memory query timeout | Supabase cold start or indexing lag | Run `immune_health()` → restart source if needed |
| Telegram delivery failure | Bot token expired or rate limit | Rotate token in vault, check BotFather |
| Recipe parse error | YAML syntax issue | Run `python3 -c "import yaml; yaml.safe_load(open('FILE'))"` |
| API cost over budget | Large batch job ran | Review `~/.hermes/logs/cost.log`, adjust batch size |
| Stale semantic memory | Long gap since brain sync | Run `jake run jake-knowledge-refresh` |

---

## 4. PHASE 2: Monthly Capability Audit (jake-capability-audit)

**Frequency**: First Sunday of each month
**Trigger**: `jake run jake-capability-audit`
**Duration**: 15–30 minutes
**Framework**: Mike's 9-domain capability scorecard (see below)

### 4.1 The 9-Domain Capability Scorecard (Mani Kanasani Framework)

Each domain scored 0–10 with evidence:

| Domain | What Is Assessed | Score | Evidence Required |
|--------|-----------------|-------|------------------|
| **1. Intelligence Gathering** | Signal collection quality, source coverage, freshness | /10 | Domains updated in last 14 days |
| **2. Analysis & Synthesis** | Output quality, framework application, insight density | /10 | Sample last 5 outputs scored |
| **3. Communication** | Brief clarity, exec-appropriate tone, format adherence | /10 | Mike's explicit feedback log |
| **4. Memory Architecture** | Episodic/semantic/procedural balance, retrieval accuracy | /10 | Brain test query pass rate |
| **5. Automation** | Recipe coverage, cron job health, reliability | /10 | Test pass rate + uptime |
| **6. Learning & Adaptation** | Corrections applied, feedback incorporated, skill growth | /10 | jake-correction-review output |
| **7. Strategic Framing** | Decision support quality, framework leverage, so-what generation | /10 | Sample 3 complex outputs |
| **8. Personal Context** | Family awareness, Mike's preferences, relationship context | /10 | Privacy check pass rate |
| **9. Startup / Ventures** | TransformFit, recruiting, financial modeling support quality | /10 | Output from venture tasks |

**Monthly audit output**: Scorecard with scores, evidence, and top 3 improvement actions.

### 4.2 Improvement Actions

For any domain scoring below 7:
1. Identify the root cause (missing recipe? stale memory? no SOP?)
2. Create a specific improvement action with a 30-day target
3. Log it in the DeathStar audit doc for tracking

---

## 5. PHASE 3: Recipe and SOP Lifecycle Governance

### 5.1 Recipe Development Lifecycle

```
STAGE 1: PROPOSAL
  - Trigger: Recurring task identified; >2 hours/month time value
  - Action: Write recipe hypothesis (name, trigger, expected output, tools needed)
  - Gate: Mike approves or rejects before building

STAGE 2: DRAFT
  - Build the YAML recipe with all steps
  - Validate YAML syntax: python3 -c "import yaml; yaml.safe_load(open('RECIPE.yaml'))"
  - Tag version as "0.1-draft"

STAGE 3: TEST
  - Run recipe manually with sample inputs
  - Verify: all steps execute, output is useful, Telegram delivery works
  - Fix any failures before promotion

STAGE 4: PRODUCTION
  - Update RECIPE_INDEX.md with new recipe entry
  - Set version to "1.0"
  - If scheduled: add to launchd plist

STAGE 5: DEPRECATE
  - Trigger: Recipe unused for 90 days OR replaced by better recipe
  - Action: Move to ~/.hermes/recipes/archive/
  - Remove from RECIPE_INDEX.md
  - Log in this SOP's revision history
```

### 5.2 SOP Lifecycle

```
NEW SOP:
  Criteria: Recurring process that would benefit from documentation
  Format: Match SOP-11 or SOP-26 format exactly
  Location: ~/Startup-Intelligence-OS/docs/sops/SOP-XX-description.md
  Review: Mike reviews within 14 days of creation
  
REVIEW CYCLE:
  P0/P1 SOPs: Quarterly review
  P2/P3 SOPs: Semi-annual review
  
DEPRECATE:
  Criteria: Process no longer applies to Mike's work
  Action: Add "DEPRECATED" header, move to docs/sops/archive/
```

---

## 6. PHASE 4: Cost and API Budget Governance

### 6.1 Monthly Cost Budget Structure

| API / Service | Monthly Budget | Alert Threshold | Hard Limit |
|--------------|---------------|-----------------|------------|
| Anthropic (Claude) | $150 | $120 | $200 |
| Voyage AI (embeddings) | $30 | $25 | $50 |
| Supabase | $25 | $20 | $40 |
| Bright Data (scraping) | $50 | $40 | $75 |
| Resend (email) | $20 | $15 | $30 |
| **Total** | **$275** | **$220** | **$395** |

**When alert threshold hit**: Jake sends Telegram notification, logs event.
**When hard limit hit**: Jake pauses non-critical batch jobs, alerts Mike.

### 6.2 Cost Attribution

Log all significant API spend against a project:
- `oracle-health`: Oracle M&CI work
- `startup-os`: TransformFit and ventures
- `alex-recruiting`: Jacob's recruiting
- `system`: Jake self-maintenance (brain sync, self-test, etc.)
- `personal`: Personal and family tasks

---

## 7. PHASE 5: Memory Hygiene (Monthly)

**Trigger**: Run monthly with `immune_stale_scan()`

### 7.1 Memory Decay Policy

| Memory Type | Staleness Window | Action |
|-------------|-----------------|--------|
| Episodic (events) | > 30 days without reinforcement | Flag for promotion to semantic or deletion |
| Semantic (facts) | > 90 days without verification | Re-verify before trusting in outputs |
| Procedural (SOPs/recipes) | > 180 days without execution | Mark as needing review |
| Working memory (context) | Session scope | Auto-cleared at session end |

### 7.2 Memory Promotion Criteria

Episodic → Semantic (facts that should be permanent):
- Decision made with documented rationale
- Relationship fact (person's role, preference, context)
- Strategic position (competitive insight, market fact)
- Any fact used in 3+ separate interactions

---

## 8. PHASE 6: Security and Credential Governance

### 8.1 Vault Management

All credentials must be stored in Jake's vault (`vault_store`), never in:
- Code files (GitHub repos)
- Chat logs
- `.env` files committed to version control
- Plaintext notes

### 8.2 Credential Rotation Schedule

| Credential Type | Rotation Frequency | Responsible Party |
|----------------|-------------------|-----------------|
| Anthropic API key | 90 days or on suspected compromise | Mike |
| Supabase keys | 180 days | Mike |
| Telegram bot token | 90 days | Mike |
| External service keys | Per service policy | Mike |

### 8.3 Credential Audit (Quarterly)

Run `vault_list()` and verify:
1. All listed credentials are still needed (remove unused)
2. No credentials have exceeded rotation window
3. All credentials have a known owner

---

## 9. Output Artifacts

| Artifact | Location |
|----------|----------|
| Daily self-test logs | ~/.hermes/logs/self-test-[YYYY-MM-DD].json |
| Monthly capability scorecard | ~/Startup-Intelligence-OS/docs/jake/audits/capability-[YYYY-MM].md |
| DeathStar audit log | docs/jake/deathstar-audit-[YYYY-MM].md |
| Recipe index | ~/.hermes/recipes/RECIPE_INDEX.md |
| Cost attribution logs | ~/.hermes/logs/cost-[YYYY-MM].log |

---

## 10. Quality Checks

| Checkpoint | Standard | Owner |
|-----------|----------|-------|
| Daily self-test passes ≥ 8/10 layers | Logged in test output | Jake (automated) |
| Monthly capability audit completed | Scorecard file exists | Mike |
| No YAML parse errors in recipe index | 0 errors on `jake validate` | Jake |
| API spend under monthly budget | Cost log reviewed monthly | Mike |
| No credential older than rotation window | Vault audit quarterly | Mike |
| Memory hygiene scan monthly | Stale scan results reviewed | Mike |
| All P0/P1 SOPs reviewed quarterly | Review dates current | Mike |

---

## 11. Jake System Principles (Non-Negotiable Guardrails)

1. **Privacy first**: Family context never leaks into work outputs. Work data never leaks into family context. Run `immune_privacy_check` before any cross-context delivery.
2. **Tier 2 actions require confirmation**: All send_email, create_event, create_github_issue, update_notion require Mike's explicit ✅ before execution.
3. **No hallucinated citations**: Every data point in an intelligence output must have a source. If no source exists, it is labeled as inference/estimate.
4. **Corrections are gold**: Every correction Mike makes is stored and analyzed. A corrected mistake that recurs is a system failure, not a one-time error.
5. **Degrade gracefully**: Jake never silently fails. If a data source is unavailable, Jake says so in the output.

---

## 12. Revision History

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-03-24 | 1.0 APPROVED | Initial SOP — WS3 Foundation Layer completion | Jake (Dust Star 25X) |

---

## 13. Source Attribution

1. **NIST AI Risk Management Framework 1.0** (2023) — AI system governance, risk classification, trustworthiness criteria
2. **Google SRE Book** — Error budget model, reliability targets, toil reduction principles
3. **OWASP Top 10 for LLM Applications** — Security risks specific to LLM-integrated systems
4. **Anthropic Usage Policies** — Responsible AI usage framework
5. **SOC 2 Type II Trust Principles** — Security, availability, processing integrity as governance model analogues
