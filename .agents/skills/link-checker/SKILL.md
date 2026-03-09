---
name: link-checker
description: Validate all URLs across category READMEs and flag dead or broken links
disable-model-invocation: true
---

# Link Checker Skill

Systematically validate URLs across the Startup Intelligence OS and report broken links.

## Usage

```
/link-checker [category|all]
```

- `category` — Check a specific category directory (e.g., `ai-product-development`)
- `all` — Check all category READMEs and LIVE-RESEARCH-ENRICHMENT.md

If no argument given, ask the user which category to check or offer to check all.

## Workflow

### Step 1: Extract URLs
1. Read the target markdown file(s)
2. Extract all URLs using markdown link pattern `[text](url)`
3. Deduplicate URLs (same URL may appear multiple times)
4. Count total unique URLs to check

### Step 2: Validate URLs
For each unique URL, use `WebFetch` or `curl` to check accessibility:
- **200-299**: Valid
- **301/302**: Redirect — note the destination
- **403**: Forbidden — may still be valid, flag for manual review
- **404**: Dead link — flag for removal
- **500+**: Server error — flag for recheck
- **Timeout**: Flag for manual review

Use parallel checking where possible (dispatch subagents per category for `all` mode).

### Step 3: Report
Output a structured report:

```markdown
## Link Check Report — [Category/All] — [Date]

**Total URLs checked**: X
**Valid**: X
**Broken (404)**: X
**Redirects**: X
**Needs review**: X

### Broken Links (Remove or Replace)

| File | Link Text | URL | Status |
|------|-----------|-----|--------|
| category/README.md | Resource Name | https://... | 404 |

### Redirects (Update URL)

| File | Link Text | Old URL | New URL |
|------|-----------|---------|---------|
| category/README.md | Resource Name | https://old... | https://new... |

### Needs Manual Review

| File | Link Text | URL | Issue |
|------|-----------|-----|-------|
| category/README.md | Resource Name | https://... | 403 Forbidden |
```

### Step 4: Fix (With Approval)
After presenting the report, offer to:
1. Remove broken links
2. Update redirected URLs
3. Search for replacement resources for removed links

Always confirm with the user before making edits.
