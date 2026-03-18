# V2 Deep Workflows — The Five That Replace Forty

These 5 workflows are the core of V2. Each one is end-to-end, multi-agent, and produces a specific deliverable. They replace scattered shallow features with deep, reliable pipelines.

---

## Workflow 1: Morning Brief Synthesis

**Trigger:** Daily at 6:30 AM (scheduled), or on-demand via `/morning-brief`
**Agents:** ARIA (lead) + Susan (data) + Steve (strategy)
**Deliverable:** 3-bullet cross-project brief with "the one move today"

### Pipeline
```
1. ARIA gathers raw data:
   - Git status across 3 projects (commits, branches, uncommitted work)
   - HANDOFF.md files (session state)
   - Parking lot (parked ideas aging)
   - Decision audit trail (recent agent actions)
   - TrendRadar signals (if connected)

2. Susan enriches with intelligence:
   - RAG freshness status
   - Stale competitive intelligence
   - Knowledge gaps detected

3. Steve provides strategic filter:
   - Which of the 3 projects has highest strategic urgency?
   - Are there time-sensitive opportunities?
   - What decisions are pending?

4. ARIA synthesizes into brief format:
   - "The One Move Today" (single sentence)
   - 3 bullets (one per project or top 3 signals)
   - System health dashboard
   - Parking lot aging check
```

### Quality Gate
- Brief must answer "what should I do first?" in < 30 seconds of reading
- Every signal must cite a data source
- Confidence tier: AUTO if all data sources checked, DRAFT if any unavailable

---

## Workflow 2: Content Generation Pipeline

**Trigger:** `/content [topic]` or when SCOUT detects a content white space
**Agents:** Herald (content) + SCOUT (competitive intel) + Prism (brand)
**Deliverable:** Publishable content piece with strategic rationale

### Pipeline
```
1. SCOUT analyzes the competitive landscape:
   - What have competitors published recently?
   - Where are the content white spaces?
   - What topics are trending in this domain?
   - MCP tools: TrendRadar search_news, brave_web_search

2. Herald drafts content:
   - Informed by SCOUT's competitive analysis
   - Follows brand voice (Prism guidelines)
   - Includes strategic rationale: "why this content, why now"
   - Targets specific audience and platform

3. Prism reviews brand alignment:
   - Voice consistency check
   - Visual asset recommendations
   - Platform-specific formatting

4. Quality gate:
   - Content scored 1-10 on: relevance, originality, evidence basis, brand fit
   - Must score 7+ to ship
   - Below 7: specific improvement suggestions provided
```

### Output Format
```markdown
# Content Brief — {topic}

## Strategic Rationale
- Why this content: {competitive white space or trending signal}
- Target audience: {who}
- Target platform: {where}
- Timing: {why now}

## Content
{the actual content piece}

## Evidence Basis
- Sources: {list with URLs}
- Competitive context: {what competitors have/haven't covered}

## Quality Score: {1-10}
- Relevance: {score}
- Originality: {score}
- Evidence: {score}
- Brand fit: {score}

## Confidence: {AUTO|DRAFT|FLAG}
```

---

## Workflow 3: Strategic Memo Pipeline

**Trigger:** `/memo [topic]` or when Oracle Health intel requires stakeholder communication
**Agents:** Oracle-Brief agent (via Susan) + Memo Studio + SENTINEL-HEALTH
**Deliverable:** CMO-ready healthcare brief with evidence grades

### Pipeline
```
1. Oracle-Brief gathers intelligence:
   - Susan RAG search for relevant knowledge records
   - TrendRadar for recent healthcare news
   - SharePoint existing content (if accessible)
   - Competitive intelligence on Oracle Health competitors

2. Memo Studio structures the brief:
   - Executive summary (3 sentences max)
   - Key findings (each with evidence grade: HIGH/MEDIUM/LOW/UNVERIFIED)
   - Strategic implications
   - Recommended actions
   - Appendix: source list

3. SENTINEL-HEALTH reviews for compliance:
   - Healthcare regulatory considerations
   - Competitive sensitivity check
   - Data accuracy verification
   - Clearance: GREEN (safe to share) / YELLOW (internal only) / RED (needs legal review)

4. Final formatting:
   - CMO-ready presentation format
   - Evidence grades on every claim
   - Source attribution throughout
```

### Quality Gate
- Marcus Chen test: "Would Marcus present this to a CMO without rewriting?"
- Every claim must have an evidence grade
- SENTINEL clearance must be GREEN or YELLOW (RED = blocked)
- Confidence tier required on the full memo

---

## Workflow 4: Coach Outreach Pipeline (Alex Recruiting)

**Trigger:** `/outreach [coach-name]` or batch mode via LEDGER pipeline signals
**Agents:** Coach Outreach Studio + Research Director + Recruiting Strategy
**Deliverable:** Personalized outreach sequence with timing optimization

### Pipeline
```
1. Research Director profiles the coach:
   - School, conference, recent record
   - Recruiting track record and style
   - Social media presence and engagement patterns
   - Connection points to Jacob's profile
   - MCP tools: brave_web_search, scrape_as_markdown

2. Recruiting Strategy evaluates fit:
   - Position match (OL/DL for Jacob)
   - School academic fit
   - Geographic and conference preferences
   - Competition level assessment
   - Priority score: HOT / WARM / COOL

3. Coach Outreach Studio drafts sequence:
   - Initial contact (personalized to research findings)
   - Follow-up #1 (if no response after 5 days)
   - Follow-up #2 (different angle, 10 days)
   - Highlight reel delivery (if engaged)
   - Each message references specific research (not generic)

4. Timing optimization:
   - Best day/time for initial contact (Tuesday-Thursday, morning)
   - Avoid dead periods (in-season game weeks, signing day)
   - LEDGER tracks response rates by timing to improve recommendations
```

### Quality Gate
- Every outreach message references specific coach/school research
- No generic templates — if it could be sent to any coach, it fails
- Timing respects recruiting calendar
- LEDGER pipeline tracks: sent → opened → replied → engaged → committed

---

## Workflow 5: Project Assessment Pipeline

**Trigger:** `/project-assessment [project-name]` or via Research-First Pipeline Phase 5
**Agents:** Uses the `/project-assessment` skill + Susan + multiple assessors
**Deliverable:** 6-dimension scorecard with evidence and recommendations

### Pipeline
```
1. Data gathering (parallel dispatch):
   - Agent: Explore → Git history, test coverage, CLAUDE.md presence
   - Agent: Susan → RAG chunk count, team manifest, capability map
   - Agent: Research → Market research quality, competitor analysis depth
   - Agent: Steve → Strategy clarity, competitive positioning

2. Dimension scoring:
   Each dimension scored independently with evidence:
   - Research Depth: RAG chunks, source diversity, coverage
   - Team Readiness: Agent assignments, skill gaps, ownership clarity
   - Technical Foundation: Code quality, test coverage, CI/CD, hooks
   - Strategy Clarity: Strategy docs, decision records, market validation
   - Capability Coverage: Capability map completeness, maturity scores
   - Governance & Quality: Hook count, audit trail, confidence tier adoption

3. Synthesis:
   - Overall score (weighted average)
   - Top 2 strengths with evidence
   - Top 2 critical gaps with recommendations
   - Comparison to prior assessment (if exists)
   - Recommended sprint: what to build next to raise the lowest scores

4. Save and track:
   - Scorecard saved to .startup-os/artifacts/
   - LEDGER tracks score trajectory over time
   - If any dimension drops below 4, flag as critical
```

### Quality Gate
- Every score must have a cited evidence source
- No score inflation — if data is missing, score LOW and explain why
- Confidence tier: AUTO if all dimensions have evidence, DRAFT if any inferred
- Previous scorecard comparison required if one exists

---

## Workflow Selection Guide

| User Says | Workflow | Primary Agent |
|-----------|----------|---------------|
| "What should I work on?" | Morning Brief | ARIA |
| "Write a post about..." | Content Generation | Herald + SCOUT |
| "I need a brief for Oracle Health..." | Strategic Memo | Oracle-Brief |
| "Research Coach Smith at Alabama" | Coach Outreach | Coach Outreach Studio |
| "How's this project doing?" | Project Assessment | Project Assessment skill |
| "Set up a new project" | Research-First Pipeline → Assessment | Research Director → Assessment |

## Cross-Workflow Integration

The workflows compound:
- **Morning Brief** surfaces signals that trigger **Content Generation** or **Coach Outreach**
- **Research-First Pipeline** always ends with **Project Assessment**
- **Strategic Memo** pulls from the same RAG that **Morning Brief** monitors
- **LEDGER** tracks metrics across ALL workflows
- **KIRA** routes ambiguous requests to the right workflow
