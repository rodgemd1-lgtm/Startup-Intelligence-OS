---
name: enforce-build-doctrine-no-draft-before-research
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: docs/sops/.*\.md$
  - field: content
    operator: regex_match
    pattern: (DRAFT|Version.*1\.0|SOP-\d+)
action: warn
---

**BUILD DOCTRINE VIOLATION: You are writing an SOP draft before research is complete.**

Mike has corrected this behavior 6+ times. The rule is absolute:

```
RESEARCH --> DESIGN --> PLAN --> BUILD
```

**SERIES, NOT PARALLEL.**

Before writing ANY file to `docs/sops/`, you MUST verify:

1. All research agents have returned and their output is saved to `docs/research/sop-XX-*/`
2. Mike has reviewed and acknowledged the research findings
3. A design/synthesis plan exists and is approved

**What to do instead:**
- Wait for all research agents to complete
- Save all research files to `docs/research/`
- Present a research summary to Mike
- Get Mike's explicit "go" before drafting the SOP

**This block is non-negotiable. Do not bypass it.**
