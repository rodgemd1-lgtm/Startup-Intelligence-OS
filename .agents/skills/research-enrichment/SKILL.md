---
name: research-enrichment
description: Run a live research enrichment sweep for one or more categories in the Startup Intelligence OS
disable-model-invocation: true
---

# Research Enrichment Skill

Run a structured research enrichment sweep to discover and curate the latest resources for one or more categories.

## Usage

```
/research-enrichment [category] [topic]
```

- `category` — One of the 23 category directories (e.g., `ai-approaches-frameworks`, `decentralized-ai`)
- `topic` — Optional focus area within the category

If no category is specified, ask which category to enrich.

## Workflow

### Step 1: Read Current State
1. Read the category's `README.md` to understand existing resources
2. Read `LIVE-RESEARCH-ENRICHMENT.md` for any existing enrichment in this category
3. Identify gaps, outdated entries, and areas needing fresh research

### Step 2: Research
Run web searches to discover new resources. For each category, search for:
1. **Latest rankings and comparisons** — "[topic] best tools 2026", "[topic] comparison 2026"
2. **GitHub repositories** — "[topic] awesome list github", "[topic] framework github stars"
3. **Industry articles** — "[topic] guide 2026", "[topic] trends 2026"
4. **New tools and platforms** — "[topic] new tools launched 2026"

Use at least 3-5 parallel searches per category.

### Step 3: Curate and Deduplicate
For each discovered resource:
1. Verify it is NOT already in the category README or LIVE-RESEARCH-ENRICHMENT.md
2. Verify the URL is live and accessible
3. Extract: name, description, URL, and key stats (stars, users, etc.)
4. Assess relevance and quality — only include best-in-class resources

### Step 4: Output
Present findings in two formats:

**For LIVE-RESEARCH-ENRICHMENT.md** (append to relevant section):
```markdown
## [Category Name] — [Month Year] Update

### [Subsection]

| Source | Title | URL |
|--------|-------|-----|
| Source Name | Article Title | [domain](url) |
```

**For category README.md** (suggest additions):
```markdown
### Suggested Additions to [category]/README.md

| Resource | Description | URL |
|----------|-------------|-----|
| Name | What it does | [link](url) |
```

### Step 5: Confirm Before Editing
Always present findings to the user BEFORE modifying any files. Let the user approve which resources to add and where.

## Quality Gates
- No duplicate URLs across the project
- All URLs verified as live
- Resources must be from 2025 or 2026 unless they are foundational/canonical
- Minimum 3 new resources per enrichment sweep, or explain why fewer were found
