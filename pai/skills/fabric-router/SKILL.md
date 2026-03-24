---
name: fabric
description: Run Fabric AI patterns. /fabric summarize TEXT or /fabric w URL
command-dispatch: tool
command-tool: exec
command-arg-mode: raw
metadata: {"openclaw": {}}
---

# Fabric Pattern Router — Deterministic Dispatch

This skill uses deterministic Bash dispatch. When a user types `/fabric PATTERN TEXT`,
the raw args are sent directly to Bash as a shell command.

Pattern names (summarize, extract_wisdom, w, s, etc.) are available as commands in PATH
via symlinks to fabric-dispatch, which routes to fabric-cmd.

Examples:
- `/fabric summarize The future is built` → Bash runs: `summarize The future is built`
- `/fabric w https://paulgraham.com/ds.html` → Bash runs: `w https://paulgraham.com/ds.html`
- `/fabric analyze_claims AI will replace all jobs` → Bash runs: `analyze_claims AI will replace all jobs`

## Available Patterns

Aliases: w(extract_wisdom) s(summarize) a(analyze_claims) i(extract_ideas) r(analyze_risk) p(create_prd) f(find_logical_fallacies) c(compare_and_contrast) q(extract_questions)

Full names: summarize, extract_wisdom, analyze_claims, analyze_risk, extract_ideas, extract_recommendations, extract_questions, extract_insights, extract_patterns, find_logical_fallacies, compare_and_contrast, create_prd, analyze_personality, create_better_frame, improve_prompt, write_essay, rate_content, clean_text, create_tags, and 230+ more.

## Fallback (no slash prefix)

If the user says "fabric summarize: ..." without the `/` prefix, call Bash with:
```
fabric-cmd PATTERN "TEXT_OR_URL"
```
NEVER paraphrase or answer yourself. ALWAYS use the Bash tool.
