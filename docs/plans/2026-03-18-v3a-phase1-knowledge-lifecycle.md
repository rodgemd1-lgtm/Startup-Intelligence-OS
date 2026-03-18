# V3a Phase 1: Knowledge Lifecycle + Output Hub

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extend the existing freshness audit into a full knowledge lifecycle system with auto-refresh triggers, and wire up the output hub so all agent briefs land in `.startup-os/briefs/`.

**Architecture:** Build on existing `control_plane/audits.py` (freshness_status), `research_daemon/gap_detector.py` (detect_stale_data), and the `mike-studio-stale-watchdog` scheduled task. Add lifecycle state definitions, transition rules, and standardized brief output. No new Python modules — this is docs + config + scheduled task updates.

**Tech Stack:** Markdown docs, YAML config, Claude scheduled tasks, existing Python backend (read-only reference)

---

### Task 1: Knowledge Lifecycle Documentation

**Files:**
- Create: `.claude/docs/knowledge-lifecycle.md`

**Step 1: Write the lifecycle state definitions**

Create `.claude/docs/knowledge-lifecycle.md` with:

```markdown
# Knowledge Lifecycle

## States

| State | Description | Entry Trigger | Exit Trigger |
|-------|-------------|---------------|--------------|
| DRAFT | New data ingested, not yet validated | Initial scrape or ingest | Manual review confirms accuracy |
| REVIEW | Flagged for quality check | Auto: first ingest of new domain; Manual: analyst flags | Reviewer marks PUBLISHED or rejects |
| PUBLISHED | Validated, actively used by agents | Review passes quality gate | Age exceeds domain freshness window |
| AGING | Approaching staleness threshold | Within 7 days of freshness window expiry | Reaches expiry OR manual refresh |
| STALE | Past freshness window, unreliable | Age exceeds domain freshness window | Refresh cycle completes |
| REFRESH | Active re-research in progress | Auto-refresh triggered on STALE record | New data ingested, returns to REVIEW |

## Freshness Windows (per domain)

| Domain | Window | Cadence | Source |
|--------|--------|---------|--------|
| market_intelligence | 30 days | Monthly | Oracle Health policy |
| clinical_operational | 90 days | Quarterly | Oracle Health policy |
| regulatory_enterprise | 45 days | ~6 weeks | Oracle Health policy |
| marketing_narrative | 30 days | Monthly | Oracle Health policy |
| firecrawl_screenshots | 21 days | ~3 weeks | Oracle Health policy |
| competitor_profiles | 30 days | Monthly | Stale watchdog |
| pricing | 30 days | Monthly | Fitness app policy |
| app_features | 90 days | Quarterly | Fitness app policy |
| company_metrics | 90 days | Quarterly | Fitness app policy |
| market_reports | 180 days | Semiannual | Fitness app policy |

## Transition Rules

### Automatic Transitions
1. **PUBLISHED → AGING**: When record age reaches `window - 7 days`
2. **AGING → STALE**: When record age exceeds `window`
3. **STALE → REFRESH**: When auto-refresh trigger fires (stale-watchdog)
4. **REFRESH → REVIEW**: When new data is ingested for the domain

### Manual Transitions
1. **DRAFT → REVIEW**: Analyst flags for review
2. **REVIEW → PUBLISHED**: Reviewer confirms quality
3. **REVIEW → DRAFT**: Reviewer rejects, needs rework
4. **Any → STALE**: Analyst manually marks unreliable

## Auto-Refresh Dispatch

When stale-watchdog detects STALE records:
1. Check domain against refresh task inventory (11 biweekly tasks exist)
2. If a scheduled refresh task exists → log "covered by scheduled task"
3. If NO scheduled task exists → flag as "needs manual research" in freshness report
4. Never auto-trigger expensive scrapes without a matching scheduled task

## Integration Points

- **Existing**: `control_plane/audits.py` → `freshness_status()` returns "stale" or "current"
- **Existing**: `research_daemon/gap_detector.py` → `detect_stale_data()` scores domain coverage
- **Existing**: `mike-studio-stale-watchdog` → weekly KB freshness audit (Sundays 3 AM)
- **Existing**: 11 biweekly domain refresh tasks → cover Oracle Health domains
- **New**: Freshness report output → `.startup-os/briefs/freshness-{date}.md`
```

**Step 2: Verify the doc is well-formed**

Read the file back, confirm all tables render, no broken markdown.

**Step 3: Commit**

```bash
git add .claude/docs/knowledge-lifecycle.md
git commit -m "docs(v3a): knowledge lifecycle states and transition rules"
```

---

### Task 2: Update Freshness Command with Lifecycle States

**Files:**
- Modify: `.claude/commands/knowledge-freshness.md`

**Step 1: Read the current freshness command**

Read `.claude/commands/knowledge-freshness.md` to see current structure.

**Step 2: Add lifecycle state output to the command**

Update the command to include lifecycle state assignment in its output. After the existing audit steps, add:

```markdown
## Lifecycle Assessment

After counting chunks and checking staleness, assign lifecycle states:

3. **Assign lifecycle states** per domain:
   - Check each domain's last ingest date against its freshness window (see `.claude/docs/knowledge-lifecycle.md`)
   - Assign state: PUBLISHED (within window), AGING (within 7 days of expiry), STALE (past window)
   - For domains with no ingest date: assign DRAFT

4. **Generate lifecycle summary table**:

| Domain | Last Ingest | Window | State | Action Needed |
|--------|-------------|--------|-------|---------------|
| [domain] | [date] | [N days] | [STATE] | [none/aging-alert/needs-refresh/needs-research] |

5. **Save freshness report** to `.startup-os/briefs/freshness-{date}.md`
   - Include lifecycle summary table
   - Include domain coverage scores from gap detector
   - Include recommendations for STALE and AGING domains
```

**Step 3: Verify the command renders correctly**

Read it back, confirm markdown is valid.

**Step 4: Commit**

```bash
git add .claude/commands/knowledge-freshness.md
git commit -m "feat(v3a): add lifecycle states to freshness command"
```

---

### Task 3: Update Stale Watchdog with Auto-Refresh Logic

**Files:**
- Modify: scheduled task `mike-studio-stale-watchdog`

**Step 1: Read the current stale-watchdog task**

Read `~/.claude/scheduled-tasks/mike-studio-stale-watchdog/SKILL.md`.

**Step 2: Add lifecycle-aware output section**

Update the watchdog task prompt to:
1. Assign lifecycle states (not just "stale" binary)
2. Cross-reference STALE domains against the 11 biweekly refresh tasks
3. For covered domains: log "auto-refresh scheduled via [task-name]"
4. For uncovered domains: flag "NEEDS MANUAL RESEARCH" in output
5. Save a freshness report to `.startup-os/briefs/freshness-{date}.md` after each run

Add to the end of the task prompt:
```markdown
## Lifecycle Report Output

After completing the audit:

1. Assign lifecycle states per domain:
   - PUBLISHED: last updated within freshness window
   - AGING: within 7 days of window expiry
   - STALE: past freshness window
   - REFRESH: has a matching biweekly refresh task that will auto-update

2. Save report to the Startup Intelligence OS repo:
   - Path: `/Users/mikerodgers/Startup-Intelligence-OS/.startup-os/briefs/freshness-{YYYY-MM-DD}.md`
   - Format: lifecycle summary table + recommendations + coverage scores

3. If any domain is STALE with no matching refresh task, include a WARNING block:
   > **WARNING**: [domain] is STALE with no auto-refresh. Manual research needed.
```

**Step 3: Verify the updated task**

Read it back to confirm the additions are clean.

**Step 4: Commit**

```bash
cd /Users/mikerodgers/Startup-Intelligence-OS
git add -A .startup-os/briefs/
git commit -m "feat(v3a): lifecycle-aware stale watchdog with brief output"
```

Note: The scheduled task file lives outside the repo (`~/.claude/scheduled-tasks/`), so it won't be in git. The brief output location IS in the repo.

---

### Task 4: Create Brief Output Templates

**Files:**
- Create: `.startup-os/briefs/README.md`

**Step 1: Write the briefs README**

Create `.startup-os/briefs/README.md`:

```markdown
# Agent Brief Output Hub

Standardized location for all agent-generated briefs. The Genspark bot reads this directory via GitHub API to relay content to Telegram.

## Brief Types

| Brief | Schedule | Agent | Filename Pattern |
|-------|----------|-------|-----------------|
| ARIA Daily Brief | Daily 6:39 AM | ARIA | `aria-brief-YYYY-MM-DD.md` |
| LEDGER Report | Weekly | LEDGER | `ledger-report-YYYY-MM-DD.md` |
| Freshness Report | Weekly (Sun 3 AM) | Stale Watchdog | `freshness-YYYY-MM-DD.md` |
| SCOUT Signals | TBD (V3a Phase 2) | SCOUT | `scout-signals-YYYY-MM-DD.md` |

## Format Requirements

All briefs must include:
1. H1 title with date
2. "The One Move Today" section (for actionable briefs)
3. Structured sections with H2/H3 headers
4. System Health section at bottom
5. No secrets, API keys, or sensitive data

## Retention

Briefs older than 30 days can be archived to `archive/briefs/`.
```

**Step 2: Commit**

```bash
git add .startup-os/briefs/README.md
git commit -m "docs(v3a): brief output hub README with format spec"
```

---

### Task 5: Wire LEDGER Report to Briefs Directory

**Files:**
- Modify: scheduled task `command-center-daily-brief` (or create a new weekly LEDGER task)

**Step 1: Check if LEDGER has a scheduled task**

Search for any existing LEDGER scheduled task in `~/.claude/scheduled-tasks/`.

**Step 2: Update ARIA daily brief task to also save to briefs/**

The ARIA daily brief task (`command-center-daily-brief`) already runs. Confirm it saves output to `.startup-os/briefs/aria-brief-{date}.md`. If not, add that instruction.

**Step 3: Create or update a LEDGER weekly task**

If no LEDGER task exists, note it for creation via `/schedule`. The task should:
- Run weekly (Mondays 7 AM)
- Generate a LEDGER funnel/conversion report across all projects
- Save to `.startup-os/briefs/ledger-report-{date}.md`
- Format: project status table, funnel metrics, 30-day trajectory, actionable signals

**Step 4: Commit any repo changes**

```bash
git add .startup-os/
git commit -m "feat(v3a): wire LEDGER report output to briefs hub"
```

---

### Task 6: Validation Gate

**Step 1: Run the freshness command**

Execute `/knowledge-freshness` and confirm:
- [ ] Lifecycle states are assigned per domain
- [ ] Output includes the lifecycle summary table
- [ ] A freshness report is saved to `.startup-os/briefs/freshness-{date}.md`

**Step 2: Verify briefs directory structure**

```bash
ls -la .startup-os/briefs/
```

Expected: `README.md`, `aria-brief-2026-03-18.md`, and `freshness-{date}.md`

**Step 3: Verify lifecycle doc is accessible**

Confirm `.claude/docs/knowledge-lifecycle.md` exists and is referenced by the freshness command.

**Step 4: Final commit — tag V3a Phase 1 complete**

```bash
git add -A
git commit -m "feat(v3a): Phase 1 complete — knowledge lifecycle + output hub"
```

---

## Summary

| Task | Type | Duration | Risk |
|------|------|----------|------|
| 1. Lifecycle doc | New doc | 5 min | Low |
| 2. Update freshness command | Edit | 5 min | Low |
| 3. Update stale watchdog | Edit scheduled task | 10 min | Low (outside git) |
| 4. Brief output templates | New doc | 3 min | Low |
| 5. Wire LEDGER to briefs | Edit/create scheduled task | 10 min | Medium (task scheduling) |
| 6. Validation gate | Verify | 5 min | Low |

**Total estimated: ~40 min**

No protection zone files touched. No Python code modified. All changes are docs, configs, and scheduled task prompts.
