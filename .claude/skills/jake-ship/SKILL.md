---
name: jake-ship
description: Run Jake's shipping pipeline — sync, test, audit, commit, push, PR. The final step in Think→Plan→Build→Review→QA→Ship. Use when code is reviewed and QA'd.
---

Ship the current work through Jake's full shipping pipeline. This is the final gate before code goes live.

## Prerequisites

Before running this skill, the code MUST have passed through `/jake-review` and QA. Do NOT ship unreviewed code.

## Pipeline Steps

Execute these steps IN ORDER. If any step fails, STOP immediately, report the failure, and do NOT continue.

### Step 1: Sync with Remote

Pull latest changes and rebase local work on top:

```bash
git pull --rebase origin $(git branch --show-current)
```

- If there are merge conflicts, STOP and report them. Do NOT auto-resolve.
- If the pull fails because the branch has no upstream, skip this step (new branch).
- NEVER use `--force` or `--force-with-lease` during pull.

### Step 2: Detect and Run Tests

Detect the test runner and execute the full test suite:

```bash
# Check for test runners in priority order:
# 1. If pytest is available (look for pytest.ini, pyproject.toml [tool.pytest], or conftest.py):
cd susan-team-architect/backend && source .venv/bin/activate && python -m pytest --tb=short -q

# 2. If package.json exists with test script:
npm test

# 3. If neither exists, check for any test files:
# Look for *_test.py, test_*.py, *.test.js, *.test.ts, *.spec.js, *.spec.ts
```

- If tests FAIL, STOP the pipeline immediately.
- Report which tests failed and why.
- Say: "Tests failed. Fix these before shipping. Pipeline halted."
- Do NOT proceed to commit.

### Step 3: Security Audit

Run a quick security scan before committing:

```bash
# Check for .env files that might be staged
git diff --cached --name-only | grep -E '\.env|\.env\.' || true

# Check for hardcoded secrets in staged changes
git diff --cached | grep -iE '(api[_-]?key|secret|password|token|credential)\s*[:=]\s*["\x27][A-Za-z0-9]' || true

# Check for private keys
git diff --cached | grep -E '(BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY)' || true

# Verify .gitignore covers sensitive files
for pattern in ".env" ".env.local" "*.pem" "*.key" "credentials.json"; do
  grep -q "$pattern" .gitignore 2>/dev/null || echo "WARNING: $pattern not in .gitignore"
done
```

- If any .env files are staged, REMOVE them from staging and warn the user.
- If hardcoded secrets are detected, STOP and report. Do NOT commit.
- If .gitignore is missing patterns, warn but continue.

### Step 4: Stage and Commit

Stage changes and create a conventional commit:

1. Run `git status` to see all changes.
2. Run `git diff` and `git diff --cached` to understand what changed.
3. Stage the relevant files (prefer explicit file names over `git add -A`):
   - Do NOT stage `.env`, `credentials.json`, `*.pem`, `*.key`, or other sensitive files.
   - Do NOT stage large binary files unless they are intentional assets.

4. Determine the conventional commit type from the changes:
   - `feat` — new feature or capability
   - `fix` — bug fix
   - `refactor` — code restructuring without behavior change
   - `docs` — documentation only
   - `test` — adding or updating tests
   - `chore` — maintenance, dependencies, config
   - `style` — formatting, whitespace
   - `perf` — performance improvement

5. Determine the scope from the primary area of change:
   - `startup-os`, `decision-os`, `susan`, `v5`, `console`, `bin`, `agents`, `skills`, `memory`, `brain`

6. Write a concise commit message in imperative mood, lowercase, no period:
   ```
   type(scope): description

   Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
   ```

7. Create the commit using a HEREDOC for proper formatting.

### Step 5: Push to Remote

Push the committed changes:

```bash
git push origin $(git branch --show-current)
```

- If the branch has no upstream, use `git push -u origin $(git branch --show-current)`.
- NEVER use `--force` or `--force-with-lease`. If push is rejected, pull --rebase first and retry.
- If push fails after rebase retry, STOP and report the conflict.

### Step 6: Create PR (Feature Branches Only)

If the current branch is NOT `main` or `master`, create a pull request:

```bash
# Check if PR already exists
gh pr view $(git branch --show-current) 2>/dev/null

# If no PR exists, create one
gh pr create --title "type(scope): description" --body "$(cat <<'EOF'
## Summary
- [bullet points describing what changed and why]

## Test plan
- [ ] Tests pass locally
- [ ] Security audit clean
- [ ] No .env or secrets in diff

Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- PR title should match the commit message (without the co-author line).
- PR body uses the structured format: Summary, Test plan, Generated with Claude Code.
- If a PR already exists for this branch, skip creation and report the existing PR URL.

### Step 7: Update SuperMemory

Save a record of what was shipped to the SuperMemory shared container:

Use the `mcp__supermemory__supermemory_add` tool to save a memory with:
- **Container**: `shared`
- **Content**: A structured summary including:
  - Date shipped
  - Branch name
  - Commit hash (from `git rev-parse HEAD`)
  - What was shipped (summary of changes)
  - Files modified
  - PR URL (if created)
  - Test status (passed)

Example content format:
```
SHIPPED [date]: [commit type](scope) — [description]
Branch: [branch]
Commit: [hash]
Files: [count] modified
PR: [url or N/A]
Tests: PASSED
```

## Error Handling

| Error | Response |
|-------|----------|
| Merge conflicts on pull | STOP. Report conflicts. User must resolve manually. |
| Tests fail | STOP. Report failures. Do NOT commit. |
| Secrets detected in diff | STOP. Remove from staging. Warn user. |
| Push rejected | Pull --rebase and retry ONCE. If still rejected, STOP and report. |
| gh CLI not authenticated | Warn and skip PR creation. Still push. |
| No changes to commit | Report "nothing to ship" and exit cleanly. |

## Safety Rules

- NEVER force push. Ever. Under any circumstances.
- NEVER commit .env files, API keys, or credentials.
- NEVER skip tests. If tests fail, the pipeline halts.
- NEVER auto-resolve merge conflicts. Report them for human review.
- ALWAYS use conventional commit format.
- ALWAYS include the Co-Authored-By trailer.
- ALWAYS prefer explicit file staging over `git add -A`.

## Output

After successful completion, report:

```
Shipped successfully.
- Commit: [hash] — [message]
- Branch: [branch]
- PR: [url or N/A]
- Tests: PASSED
- Security: CLEAN
- SuperMemory: UPDATED
```
