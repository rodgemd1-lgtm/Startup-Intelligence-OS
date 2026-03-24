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

## Model Routing (V2)

Per-pattern model routing is defined in `pai/config/fabric-patterns-top50.json`.

| Tier | Model | Patterns |
|------|-------|----------|
| Cheap | gpt-5.4-mini | summarize, clean_text, extract_ideas, extract_main_idea, create_micro_summary |
| Mid | claude-sonnet-4-6 | analyze_claims, analyze_risk, improve_writing, rate_content, summarize_meeting |
| Expensive | claude-opus-4-6 | extract_wisdom, t_red_team_thinking, t_find_blindspots, t_first_principles, analyze_personality |

To run with a specific model:
```bash
echo "TEXT" | /Users/michaelrodgers/go/bin/fabric --pattern PATTERN --model MODEL
```

## Pipe Chains (V2)

Chain multiple patterns — output of one feeds into the next:
```bash
echo "TEXT" | fabric --pattern summarize | fabric --pattern extract_wisdom
```

For multi-step chains, run each pipe stage sequentially via Bash.

Example user request: "Pipe this through summarize then extract_wisdom"
→ Run: `echo "TEXT" | fabric --pattern summarize | fabric --pattern extract_wisdom`

## Fallback (no slash prefix)

If the user says "fabric summarize: ..." without the `/` prefix, call Bash with:
```
fabric-cmd PATTERN "TEXT_OR_URL"
```
NEVER paraphrase or answer yourself. ALWAYS use the Bash tool.
