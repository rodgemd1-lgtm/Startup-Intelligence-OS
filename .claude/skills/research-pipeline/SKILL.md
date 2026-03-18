---
name: research-pipeline
description: 5-phase automated research pipeline for new projects — scopes questions, dispatches parallel researchers, ingests findings, assembles team, and produces a 6-dimension scorecard. Trigger with /project-setup or when starting any new company/initiative.
---

# Research-First Pipeline

Automated 5-phase research pipeline that ensures every new project starts with evidence, not assumptions. This is the foundation of the "research-first" methodology across all of Mike's companies.

## When to Invoke
- Starting a new company or initiative
- Evaluating a new market or opportunity
- User says "/project-setup", "research this", "set up a new project"
- Before any significant resource commitment to a new idea
- When Jake's Strategist Mind asks "have we researched this?"

## The 5 Phases

### Phase 1: Question Scoping (Research Director)
**Agent:** Research Director (via Susan)
**Model tier:** sonnet
**Duration:** ~2 minutes

The Research Director defines what we need to know:

1. **Market questions**: How big is this market? Who are the incumbents? What's the growth rate?
2. **User questions**: Who is the target user? What problem are they solving today? What's broken?
3. **Technical questions**: What tech stack fits? What integrations are needed? What's the build complexity?
4. **Competitive questions**: Who else is doing this? What's their moat? Where are they weak?
5. **Strategic questions**: Why now? What's the wedge? How does this fit Mike's portfolio?

**Output:** Research brief with 15-25 specific questions organized by category.

### Phase 2: Parallel Research Dispatch
**Agents:** Multiple research agents dispatched in parallel
**Model tier:** sonnet for each
**Duration:** ~5-10 minutes (parallel)

Dispatch these researchers simultaneously:

```
Agent: researcher-web     → General web research (market size, trends, news)
Agent: researcher-reddit  → Lived-experience themes, complaints, use cases
Agent: researcher-arxiv   → Academic papers, technical approaches, benchmarks
Agent: researcher-appstore → Competitor apps, reviews, rating patterns
```

Each researcher gets:
- The Research Director's question brief (relevant subset)
- A specific output format requirement
- A 3-minute time budget
- Instructions to cite sources with URLs

**MCP tools to use:**
- `brave_web_search` or `tavily_search` for web research
- `scrape_as_markdown` for deep page reads
- `search_news` for recent developments
- `get_transcript` for relevant YouTube content

### Phase 3: Knowledge Ingestion (Knowledge Engineer)
**Agent:** Knowledge Engineer (via Susan)
**Model tier:** sonnet
**Duration:** ~3 minutes

The Knowledge Engineer:
1. Collects all Phase 2 outputs
2. Grades each finding: HIGH / MEDIUM / LOW / UNVERIFIED
3. Tags by domain and data type
4. Ingests into Susan's RAG via `susan-ingest`
5. Produces a **Research Quality Report**:
   - Total findings: {count}
   - HIGH confidence: {count}
   - Source diversity: {count of unique sources}
   - Coverage gaps: {questions from Phase 1 that weren't answered}

### Phase 4: Team Assembly (Susan)
**Agent:** Susan (capability foundry)
**Model tier:** opus
**Duration:** ~3 minutes

Susan reads the research and assembles the optimal team:
1. Maps required capabilities from research findings
2. Selects agents from the 73-agent roster based on actual needs (not guesses)
3. Identifies human roles needed (if any)
4. Produces a **Team Manifest**:
   - Agent assignments with rationale
   - Capability gaps (things no agent covers)
   - Cross-domain synergy opportunities (patterns from other projects)
   - Recommended first sprint

### Phase 5: Project Scorecard (AI Eval Specialist)
**Agent:** Uses the `/project-assessment` skill
**Model tier:** opus
**Duration:** ~2 minutes

Produces the 6-dimension scorecard:
- Research Depth (should be 7+ after this pipeline)
- Team Readiness (from Phase 4 team assembly)
- Technical Foundation (from Phase 2 technical research)
- Strategy Clarity (from Phase 1 strategic questions)
- Capability Coverage (from Phase 4 capability mapping)
- Governance & Quality (baseline score for new projects)

## Full Execution Template

```
1. Invoke Research Director:
   Agent(subagent_type="research", prompt="Phase 1: Scope research questions for: {project description}")

2. Dispatch parallel researchers (use run_in_background: true):
   Agent(subagent_type="researcher-web", prompt="Research: {web questions}")
   Agent(subagent_type="researcher-reddit", prompt="Research: {reddit questions}")
   Agent(subagent_type="researcher-arxiv", prompt="Research: {academic questions}")
   Agent(subagent_type="researcher-appstore", prompt="Research: {app questions}")

3. Wait for all researchers, then:
   Agent(subagent_type="general-purpose", prompt="Phase 3: Grade and ingest findings...")

4. Team assembly:
   Skill("susan-route", args="{company_id} 'Assemble team based on research'")

5. Scorecard:
   Skill("project-assessment", args="{project name}")
```

## Output Structure

```
.claude/plans/{date}-{project-slug}-research/
├── phase1-questions.md         # Research Director's question brief
├── phase2-web.md               # Web research findings
├── phase2-reddit.md            # Reddit research findings
├── phase2-arxiv.md             # Academic research findings
├── phase2-apps.md              # App store research findings
├── phase3-quality-report.md    # Knowledge Engineer's grading
├── phase4-team-manifest.md     # Susan's team assembly
└── phase5-scorecard.md         # 6-dimension project scorecard
```

## Success Criteria
- Pipeline completes in < 15 minutes
- Research quality: >60% HIGH confidence findings
- All Phase 1 questions addressed (even if answer is "no data found")
- Team manifest maps agents to specific capabilities with rationale
- Scorecard Research Depth dimension scores 7+

## Guardrails
- Never skip Phase 1 (scoping prevents wasted research)
- Never proceed to Phase 4 without Phase 3 quality grading
- If Research Quality Report shows >40% UNVERIFIED, re-run targeted research
- Flag coverage gaps prominently — unknown unknowns are the real risk
- Save all outputs to `.claude/plans/` for auditability
