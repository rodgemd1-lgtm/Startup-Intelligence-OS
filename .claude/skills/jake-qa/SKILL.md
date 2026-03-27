---
name: jake-qa
description: Run Jake's QA pipeline — browser testing via Playwright, console error detection, accessibility check, and screenshot verification. Use before shipping to verify the UI works.
---

# Jake QA Pipeline

Run a full browser-based QA sweep on a running or launchable web app using the Playwright MCP preview tools. Produces a structured PASS/FAIL report with screenshots.

## Usage

```
/jake-qa [url|path]
```

- `url` — A live URL to test (e.g., `http://localhost:4173`)
- `path` — Path to an app directory containing `package.json` (will auto-detect and start the dev server)
- No argument — scan the current repo for `package.json` and prompt the user

## Workflow

### Step 0: Detect and Start Dev Server

If the user provides a directory path (or no argument):

1. Look for `package.json` in the target directory (or repo root, then `apps/*/`)
2. Read `package.json` and detect the dev/start/preview command:
   - Check `scripts.dev`, `scripts.start`, `scripts.preview`, `scripts.serve` in that order
   - For Python apps, check for `manage.py` (Django), `app.py` / `main.py` (Flask/FastAPI), or a `Makefile`
   - For static sites, use `python3 -m http.server <port>` from the directory
3. Start the server using `mcp__Claude_Preview__preview_start` with the detected command and working directory
4. Wait for the server to be ready (check logs for "ready", "listening", or a URL)
5. Note the URL (usually `http://localhost:<port>`)

If the user provides a URL, skip to Step 1.

### Step 1: Initial Page Load and Screenshot

1. Use `mcp__Claude_Preview__preview_screenshot` to capture the landing page
2. Record load time if visible in logs
3. Save this as **Screenshot: Landing Page**
4. Use `mcp__Claude_Preview__preview_snapshot` to get the accessibility tree (DOM snapshot)
5. Verify the page is not blank, not a default error page, and has meaningful content

**Check: PAGE_LOADS** — PASS if the page renders with visible content, FAIL if blank/error/timeout

### Step 2: Console Error Detection

1. Use `mcp__Claude_Preview__preview_console_logs` to retrieve all browser console output
2. Categorize messages:
   - **Errors** (`error` level): JavaScript exceptions, failed imports, React/Vue errors, uncaught promises
   - **Warnings** (`warning` level): Deprecation notices, missing keys, accessibility warnings
   - **Info**: Ignore unless specifically relevant
3. Filter out known noise: browser extension messages, favicon 404s, HMR/dev-mode chatter

**Check: NO_CONSOLE_ERRORS** — PASS if zero errors, WARN if only warnings, FAIL if any errors found

### Step 3: Network Request Verification

1. Use `mcp__Claude_Preview__preview_network` to capture all network requests
2. Check each request:
   - **Failed requests** (status 4xx/5xx or network error): Flag with URL and status
   - **Slow requests** (>3 seconds): Flag as warnings
   - **CORS errors**: Flag as errors
   - **Mixed content** (HTTP on HTTPS page): Flag as errors
3. Categorize by type: document, script, stylesheet, image, API call, font, other

**Check: NETWORK_HEALTHY** — PASS if all requests succeed (2xx/3xx), WARN if only non-critical assets fail (fonts, analytics), FAIL if scripts/API/document requests fail

### Step 4: Page Navigation and Screenshot Tour

1. Use `mcp__Claude_Preview__preview_snapshot` to identify all navigable links and buttons
2. Select up to 5 key navigation targets:
   - Primary nav links (header/sidebar navigation)
   - Call-to-action buttons
   - Any route defined in the app's router (if detectable from snapshot)
3. For each target:
   a. Use `mcp__Claude_Preview__preview_click` to navigate
   b. Use `mcp__Claude_Preview__preview_screenshot` to capture the result
   c. Use `mcp__Claude_Preview__preview_console_logs` to check for new errors
   d. Record as **Screenshot: [Page Name]**
4. Verify no navigation leads to a blank page, 404, or crash

**Check: NAVIGATION_WORKS** — PASS if all navigations succeed without errors, FAIL if any page crashes or shows errors

### Step 5: Basic Interaction Testing

1. Use `mcp__Claude_Preview__preview_snapshot` to find interactive elements:
   - Text inputs / search bars
   - Buttons (non-navigation)
   - Dropdowns / selects
   - Toggles / checkboxes
   - Forms
2. For each found interactive element (up to 5):
   a. Use `mcp__Claude_Preview__preview_click` to focus/activate
   b. If it is a text input, use `mcp__Claude_Preview__preview_fill` to type test content (e.g., "test input")
   c. Use `mcp__Claude_Preview__preview_screenshot` to capture the interaction result
   d. Check console logs for errors triggered by the interaction
3. If a form exists, attempt a submission with test data and verify no crash

**Check: INTERACTIONS_WORK** — PASS if interactions respond without errors, WARN if some elements are unresponsive, FAIL if interactions cause crashes

### Step 6: Accessibility Basics

1. Use `mcp__Claude_Preview__preview_snapshot` to get the full accessibility tree
2. Check for these accessibility fundamentals:
   - **Page title**: Does the page have a `<title>`?
   - **Heading hierarchy**: Is there an `<h1>`? Do headings follow order (no skipping h1 to h3)?
   - **Image alt text**: Do images have `alt` attributes?
   - **Button labels**: Do buttons have accessible names (text content or aria-label)?
   - **Link text**: Are there links with vague text ("click here", "read more") without aria-labels?
   - **Form labels**: Do form inputs have associated labels?
   - **Color contrast**: Note if text appears very light on the screenshot (visual check only)
   - **Keyboard focus indicators**: Are there visible focus styles? (check via snapshot)
   - **ARIA landmarks**: Does the page use `<main>`, `<nav>`, `<header>`, `<footer>` or ARIA roles?
3. Use `mcp__Claude_Preview__preview_inspect` on any suspicious elements for detailed info

**Check: ACCESSIBILITY_BASICS** — PASS if all fundamentals met, WARN if minor issues (missing alt on decorative images, vague link text), FAIL if critical issues (no h1, unlabeled forms, no page title)

### Step 7: Responsive Check (Optional)

1. Use `mcp__Claude_Preview__preview_resize` to set viewport to mobile (375x812)
2. Use `mcp__Claude_Preview__preview_screenshot` — save as **Screenshot: Mobile View**
3. Check for:
   - Content overflow / horizontal scroll
   - Text readability (not too small)
   - Navigation accessibility (hamburger menu works?)
   - Touch target size (buttons not too small)
4. Use `mcp__Claude_Preview__preview_resize` to restore desktop (1280x720)

**Check: RESPONSIVE** — PASS if mobile layout is usable, WARN if minor layout issues, FAIL if content is inaccessible on mobile

### Step 8: Stop Server (if started)

If a dev server was started in Step 0:
1. Use `mcp__Claude_Preview__preview_stop` to shut down the server
2. Confirm the process exited cleanly

## QA Report Format

After all checks complete, produce the report in this exact format:

```
# QA Report — [App Name or URL]
**Date**: YYYY-MM-DD
**Tested URL**: [url]
**Server**: [auto-started / pre-running]

## Results Summary

| # | Check | Status | Details |
|---|-------|--------|---------|
| 1 | PAGE_LOADS | PASS/FAIL | [one-line summary] |
| 2 | NO_CONSOLE_ERRORS | PASS/WARN/FAIL | [count] errors, [count] warnings |
| 3 | NETWORK_HEALTHY | PASS/WARN/FAIL | [count] failed, [count] slow |
| 4 | NAVIGATION_WORKS | PASS/FAIL | [count] pages tested |
| 5 | INTERACTIONS_WORK | PASS/WARN/FAIL | [count] elements tested |
| 6 | ACCESSIBILITY_BASICS | PASS/WARN/FAIL | [issues found] |
| 7 | RESPONSIVE | PASS/WARN/FAIL/SKIP | [one-line summary] |

## Verdict: SHIP IT / NEEDS WORK / DO NOT SHIP

**SHIP IT** — All checks PASS (warnings acceptable)
**NEEDS WORK** — Any check is WARN with no FAIL
**DO NOT SHIP** — Any check is FAIL

## Screenshots
[All captured screenshots are shown inline above during the test run]

## Console Errors (if any)
[List each error with source file and line if available]

## Failed Network Requests (if any)
[List each with URL, method, status code]

## Accessibility Issues (if any)
[List each with element, issue, and recommended fix]

## Recommendations
[Prioritized list of fixes — critical first, then warnings]
```

## Tool Reference

These are the Playwright MCP preview tools used in this skill:

| Tool | Purpose |
|------|---------|
| `mcp__Claude_Preview__preview_start` | Start a dev server process |
| `mcp__Claude_Preview__preview_stop` | Stop the dev server |
| `mcp__Claude_Preview__preview_screenshot` | Capture page screenshot |
| `mcp__Claude_Preview__preview_console_logs` | Get browser console messages |
| `mcp__Claude_Preview__preview_network` | Get network request log |
| `mcp__Claude_Preview__preview_snapshot` | Get accessibility tree / DOM snapshot |
| `mcp__Claude_Preview__preview_click` | Click an element |
| `mcp__Claude_Preview__preview_fill` | Fill a text input |
| `mcp__Claude_Preview__preview_inspect` | Inspect a specific element |
| `mcp__Claude_Preview__preview_resize` | Change viewport dimensions |
| `mcp__Claude_Preview__preview_logs` | Get server-side logs |

## Notes

- This skill tests the VISIBLE, INTERACTIVE experience — not unit tests or API contracts
- Screenshots are the primary evidence — always capture before and after interactions
- The accessibility check is a baseline, not a full WCAG audit
- For SPAs (React, Vue, Svelte), pay extra attention to client-side routing and hydration errors
- If the app requires authentication, ask the user for test credentials before starting
- If the app needs environment variables or a database, flag this as a blocker rather than guessing
