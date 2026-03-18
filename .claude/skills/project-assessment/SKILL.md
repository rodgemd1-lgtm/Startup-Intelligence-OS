---
name: project-assessment
description: Run a 6-dimension project assessment scorecard for any company, initiative, or project. Rates readiness across Research, Team, Tech, Strategy, Capability, and Governance with evidence-backed scores.
---

# Project Assessment Scorecard

Evaluate any project across 6 dimensions with evidence-backed scores. Produces a rated scorecard that identifies strengths, gaps, and recommended next actions.

## When to Invoke
- New project or company being evaluated
- Periodic health check on existing project
- Before committing significant resources to an initiative
- User says "assess", "score", "evaluate", "rate this project"
- As part of the Research-First Pipeline (Phase 5)

## Assessment Dimensions

### 1. Research Depth (1-10)
**What it measures:** How well-researched is this space?

| Score | Meaning |
|-------|---------|
| 1-3 | No research. Operating on assumptions. |
| 4-6 | Basic research done. Some gaps remain. |
| 7-8 | Thorough research. Key questions answered. |
| 9-10 | Deep research with primary sources, competitor analysis, and market validation. |

**Evidence sources:** RAG chunk count, research docs, competitor profiles, market data

### 2. Team Readiness (1-10)
**What it measures:** Do we have the right agents/people to execute?

| Score | Meaning |
|-------|---------|
| 1-3 | No team assigned. Critical skill gaps. |
| 4-6 | Partial team. Some roles unfilled. |
| 7-8 | Full team with clear ownership. |
| 9-10 | World-class team with cross-domain expertise and proven track record. |

**Evidence sources:** Susan team manifest, agent coverage, skill gaps

### 3. Technical Foundation (1-10)
**What it measures:** Is the tech stack solid and maintainable?

| Score | Meaning |
|-------|---------|
| 1-3 | No codebase or prototype. Tech stack undefined. |
| 4-6 | Working prototype. Some technical debt. |
| 7-8 | Production-ready with tests, CI/CD, and monitoring. |
| 9-10 | Battle-tested, well-documented, with automated quality gates. |

**Evidence sources:** Git history, test coverage, CLAUDE.md presence, hook count, CI/CD

### 4. Strategy Clarity (1-10)
**What it measures:** Is the strategic direction clear and defensible?

| Score | Meaning |
|-------|---------|
| 1-3 | No strategy. Building features without direction. |
| 4-6 | Basic strategy exists but untested. |
| 7-8 | Clear strategy with competitive moat identified. |
| 9-10 | Strategy validated with evidence, user feedback, and market positioning. |

**Evidence sources:** Strategy docs, decision records, competitive analysis, user feedback

### 5. Capability Coverage (1-10)
**What it measures:** Are the right capabilities mapped and owned?

| Score | Meaning |
|-------|---------|
| 1-3 | No capability map. Unknown unknowns everywhere. |
| 4-6 | Partial map. Some capabilities owned. |
| 7-8 | Full map with ownership, maturity levels, and build sequence. |
| 9-10 | Capabilities mapped, owned, measured, and continuously improving. |

**Evidence sources:** Susan capability map, `.startup-os/capabilities/`, maturity scores

### 6. Governance & Quality (1-10)
**What it measures:** Are there guardrails preventing quality regression?

| Score | Meaning |
|-------|---------|
| 1-3 | No quality gates. Ship and pray. |
| 4-6 | Basic testing. Manual review only. |
| 7-8 | Automated hooks, audit trail, confidence tiers. |
| 9-10 | Full governance with autonomy graduation, decision audit, and trust calibration. |

**Evidence sources:** Hook count, test suite, audit trail, WISC tier completeness

## Output Format

```markdown
# Project Assessment Scorecard

**Project:** {name}
**Date:** {date}
**Assessor:** Jake + Susan
**Confidence:** {AUTO|DRAFT|FLAG}

## Scores

| Dimension | Score | Trend | Evidence |
|-----------|-------|-------|----------|
| Research Depth | {1-10} | {up/down/flat} | {one-line evidence} |
| Team Readiness | {1-10} | {up/down/flat} | {one-line evidence} |
| Technical Foundation | {1-10} | {up/down/flat} | {one-line evidence} |
| Strategy Clarity | {1-10} | {up/down/flat} | {one-line evidence} |
| Capability Coverage | {1-10} | {up/down/flat} | {one-line evidence} |
| Governance & Quality | {1-10} | {up/down/flat} | {one-line evidence} |
| **Overall** | **{avg}** | | |

## Strengths
1. {strongest dimension and why}
2. {second strongest}

## Critical Gaps
1. {weakest dimension and what to do about it}
2. {second weakest}

## Recommended Actions (Priority Order)
1. {action} — addresses {dimension} gap — estimated effort: {low/medium/high}
2. {action} — ...
3. {action} — ...

## Comparison (if prior assessment exists)
| Dimension | Previous | Current | Delta |
|-----------|----------|---------|-------|
| ... | ... | ... | +/- |
```

## Execution Protocol

1. **Gather evidence** — use Susan agents, git status, file checks, RAG search
2. **Score each dimension** — be honest, not optimistic. Evidence-backed scores only.
3. **Identify gaps** — the two lowest scores get "Critical Gap" treatment
4. **Recommend actions** — specific, actionable, prioritized by impact
5. **Tag confidence** — AUTO if all evidence is current, DRAFT if some is inferred
6. **Save the scorecard** — write to `.startup-os/artifacts/` or project docs

## Integration with Susan

For deeper assessment, dispatch Susan agents:
- **Susan** (capability mapping) for Capability Coverage
- **Steve** (strategy) for Strategy Clarity
- **Atlas** (engineering) for Technical Foundation
- **Forge** (QA) for Governance & Quality
- **Research Director** for Research Depth
- **Compass** (product) for Team Readiness
