---
name: jake-review
description: Run Jake's code review pipeline — checks for bugs, security issues, architectural drift, and plan consistency. Use after completing implementation before committing.
---

Run Jake's full code review pipeline on the current working tree changes. Accepts an optional argument: the path to a plan file for consistency checking.

## Arguments

- `$ARGUMENTS` — (optional) path to a plan file (e.g., `docs/plans/2026-03-27-feature-plan.md`). If provided, changes are checked against the plan for drift and completeness.

## Steps

### 1. Gather the Diff

Run git diff to capture all staged and unstaged changes:

```bash
git diff HEAD --stat
git diff HEAD
```

If there are no changes, stop and report: "Nothing to review — working tree is clean."

Also capture the list of new/untracked files:

```bash
git status --short
```

### 2. Production Bug Detection (code-reviewer)

Review every changed file for:

- **Logic errors**: off-by-one, null/undefined access, missing return values, unreachable code
- **Race conditions**: shared state without locks, async operations without proper awaiting
- **Error handling gaps**: bare except/catch blocks, swallowed errors, missing error propagation
- **Resource leaks**: unclosed files, connections, streams, missing cleanup in finally blocks
- **Type mismatches**: wrong argument types, implicit coercions that lose data
- **Data integrity**: mutations of shared objects, missing validation on inputs, SQL injection vectors
- **Edge cases**: empty arrays/strings, zero/negative values, Unicode handling, large inputs

For each issue found, report:
- File and line number
- Severity: CRITICAL / HIGH / MEDIUM / LOW
- What the bug is and why it matters
- Suggested fix (one-liner if possible)

### 3. OWASP Top 10 Security Audit (security-auditor)

Scan all changed files against the OWASP Top 10 (2021):

| ID | Category | What to Look For |
|----|----------|-----------------|
| A01 | Broken Access Control | Missing auth checks, IDOR, privilege escalation paths |
| A02 | Cryptographic Failures | Hardcoded secrets, weak hashing, plaintext sensitive data |
| A03 | Injection | SQL injection, command injection, XSS, template injection |
| A04 | Insecure Design | Missing rate limits, no input validation, trust boundary violations |
| A05 | Security Misconfiguration | Debug mode in prod, default credentials, overly permissive CORS |
| A06 | Vulnerable Components | Known-vulnerable dependencies, outdated packages |
| A07 | Auth Failures | Weak password rules, missing MFA hooks, session fixation |
| A08 | Data Integrity Failures | Unsigned updates, insecure deserialization, missing checksums |
| A09 | Logging Failures | Sensitive data in logs, missing audit trail, no alerting hooks |
| A10 | SSRF | Unvalidated URLs, internal network access from user input |

For each finding, report:
- OWASP ID (e.g., A03)
- File and line number
- Severity: CRITICAL / HIGH / MEDIUM / LOW
- Description and remediation

### 4. Plan Consistency Check

**If a plan file was provided (`$ARGUMENTS` is set):**

1. Read the plan file
2. Extract the list of files the plan says to create/modify
3. Compare against the actual diff:
   - **Missing work**: Files the plan mentions but the diff does not touch
   - **Unplanned changes**: Files the diff touches that the plan does not mention
   - **Incomplete tasks**: Plan tasks that are only partially implemented
4. Check that the architectural approach matches the plan (e.g., if the plan says "use factory pattern" but the code uses a different pattern)

**If no plan file was provided:**
- Skip this step
- Note in the report: "No plan file provided — skipping plan consistency check."

### 5. Architectural Drift Detection

Check the diff for signs of architectural drift:

- **Import violations**: Are files importing from layers they should not? (e.g., UI importing directly from database layer)
- **Pattern inconsistency**: Does the new code follow the same patterns as existing code in the same directory? (naming conventions, file structure, export patterns)
- **Boundary violations**: Are changes respecting module boundaries? Check for cross-cutting concerns that should be in shared utilities
- **Dependency direction**: Dependencies should flow inward (UI -> service -> data), not outward
- **Convention breaks**: Check against any conventions established in CLAUDE.md, `.claude/rules/`, or the codebase's existing patterns

Cross-reference with protection rules from CLAUDE.md — especially:
- Do NOT break or rewrite behavior under `susan-team-architect/backend/control_plane/`
- Do NOT break or rewrite behavior under `susan-team-architect/backend/mcp_server/`
- Do NOT break or rewrite behavior under `susan-team-architect/backend/susan_core/`

### 6. TODO/FIXME/HACK Audit

Search the diff for any newly introduced debt markers:

```bash
git diff HEAD | grep -n "^\+" | grep -iE "(TODO|FIXME|HACK|XXX|TEMP|WORKAROUND|KLUDGE)"
```

For each marker found:
- Report the file, line, and full comment text
- Classify: Is this acceptable (documented tech debt with a plan) or unacceptable (lazy shortcut)?
- If the marker references a ticket/issue, note it. If not, flag it as untracked debt.

### 7. Generate Review Report

Output a structured report in this exact format:

```
## Jake's Code Review Report

**Date**: [today]
**Files changed**: [count]
**Lines added/removed**: [+N / -N]
**Plan**: [plan file path or "None provided"]

### Bug Detection
Status: [PASS | WARN | FAIL]
- [list of findings, or "No bugs detected"]

### Security (OWASP Top 10)
Status: [PASS | WARN | FAIL]
- [list of findings, or "No security issues detected"]

### Plan Consistency
Status: [PASS | WARN | FAIL | SKIP]
- [list of findings, or "All changes match the plan" or "No plan provided"]

### Architectural Drift
Status: [PASS | WARN | FAIL]
- [list of findings, or "No drift detected"]

### Debt Markers (TODO/FIXME/HACK)
Status: [PASS | WARN | FAIL]
- [list of new markers, or "No new debt markers"]

---

### Final Verdict: [SHIP IT | NEEDS WORK | BLOCK]

[One-paragraph summary explaining the verdict and what needs to happen before shipping, if anything.]
```

**Verdict rules:**
- **SHIP IT**: All categories PASS, or only LOW-severity WARNs exist
- **NEEDS WORK**: Any category has MEDIUM WARNs, or minor plan deviations exist — fixable in <30 minutes
- **BLOCK**: Any category has CRITICAL/HIGH findings, or security issues exist, or major plan deviations — do NOT commit until resolved
