---
name: fabric-router
description: Run Daniel Miessler's Fabric patterns on any text or URL. Pipe content through structured AI analysis patterns like extract_wisdom, summarize, analyze_claims, and 250+ more.
metadata: {"openclaw": {"requires": {"bins": ["fabric"]}}}
---

# Fabric Pattern Router

You have access to Daniel Miessler's Fabric — a library of 250+ structured AI analysis patterns. Use this skill when the user wants to run a specific pattern on text, a URL, or clipboard content.

## When to Use This Skill

- User says "fabric", "pattern", or names a specific pattern (e.g., "extract wisdom from this")
- User wants structured analysis of text, articles, videos, or URLs
- User asks to summarize, analyze, extract ideas/wisdom, rate content, or compare things
- User pastes a URL and wants insights

## How to Run Fabric

Execute fabric via shell. The binary is at `/Users/michaelrodgers/go/bin/fabric`.

**IMPORTANT**: Always use `env -i` to run fabric in a clean environment — this prevents conflicts with Claude Code's own env vars. Include HOME and PATH so fabric can find its config and binary.

### Text input
```bash
env -i HOME=$HOME PATH=$PATH echo "USER_TEXT_HERE" | env -i HOME=$HOME PATH=$PATH /Users/michaelrodgers/go/bin/fabric --pattern PATTERN_NAME
```

### URL input (fabric fetches and processes)
```bash
env -i HOME=$HOME PATH=$PATH /Users/michaelrodgers/go/bin/fabric -u "URL_HERE" --pattern PATTERN_NAME
```

### With specific model override
```bash
env -i HOME=$HOME PATH=$PATH /Users/michaelrodgers/go/bin/fabric --pattern PATTERN_NAME --model MODEL_NAME
```

## Pattern Tiers & Model Routing

Route patterns to the right model for cost/quality balance:

### Fast (use for quick transforms)
- `summarize` — Summarize any text
- `summarize_micro` — Ultra-short summary
- `create_5_sentence_summary` — 5-sentence summary
- `clean_text` — Clean up messy text
- `extract_ideas` — Pull out key ideas
- `extract_recommendations` — Actionable recommendations
- `extract_questions` — Pull out questions
- `create_tags` — Generate tags
- `convert_to_markdown` — Convert to markdown
- `create_flash_cards` — Flash cards from content

### Analysis (use for moderate reasoning)
- `analyze_claims` — Fact-check claims
- `analyze_risk` — Risk assessment
- `analyze_paper` — Academic paper analysis
- `analyze_presentation` — Presentation critique
- `analyze_product_feedback` — Product feedback synthesis
- `analyze_sales_call` — Sales call analysis
- `extract_article_wisdom` — Article wisdom
- `extract_insights` — Deep insights
- `extract_patterns` — Pattern recognition
- `find_logical_fallacies` — Logic errors
- `rate_content` — Content quality
- `compare_and_contrast` — A vs B analysis
- `create_prd` — Product requirements doc

### Strategic (use for deep reasoning — default to Opus)
- `extract_wisdom` — Miessler's flagship deep wisdom extraction
- `analyze_personality` — Personality analysis
- `analyze_military_strategy` — Strategy analysis
- `create_better_frame` — Reframe problems
- `improve_prompt` — Improve AI prompts
- `create_design_document` — Design documents
- `extract_business_ideas` — Business idea extraction
- `create_threat_scenarios` — Threat modeling
- `write_essay` — Long-form essay

## Aliases (for quick Telegram use)
- `w` → extract_wisdom
- `s` → summarize
- `a` → analyze_claims
- `i` → extract_ideas
- `r` → analyze_risk
- `p` → create_prd
- `f` → find_logical_fallacies
- `c` → compare_and_contrast
- `q` → extract_questions

## Output Formatting

1. Run the pattern
2. Return the FULL output to the user — do not summarize or truncate Fabric's output
3. If the output is very long (>4000 chars), split into multiple messages
4. Prefix with: **Pattern: `PATTERN_NAME`** and a separator line

## Error Handling

- If fabric binary not found: tell user to run `go install github.com/danielmiessler/fabric@latest`
- If pattern not found: suggest closest match from the lists above
- If URL fetch fails: ask user to paste the text directly
- If output is empty: the pattern may not match the input type — suggest an alternative

## List All Patterns

To show available patterns:
```bash
env -i HOME=$HOME PATH=$PATH /Users/michaelrodgers/go/bin/fabric -l
```

## Examples

User: "extract wisdom from https://example.com/article"
→ Run: `env -i HOME=$HOME PATH=$PATH /Users/michaelrodgers/go/bin/fabric -u "https://example.com/article" --pattern extract_wisdom`

User: "summarize this: [long text]"
→ Run: `echo "long text" | env -i HOME=$HOME PATH=$PATH /Users/michaelrodgers/go/bin/fabric --pattern summarize`

User: "fabric w https://paulgraham.com/ds.html"
→ Resolve alias w → extract_wisdom
→ Run: `env -i HOME=$HOME PATH=$PATH /Users/michaelrodgers/go/bin/fabric -u "https://paulgraham.com/ds.html" --pattern extract_wisdom`

User: "what patterns do you have?"
→ Show the tier lists above, grouped by Fast/Analysis/Strategic
