# Cross-Domain Pattern Registry

Transferable patterns detected across Mike's three companies. Jake references this registry when work in one project could benefit another.

**Last updated:** 2026-03-18

---

## Pattern Categories

### 1. Multi-Agent Orchestration
**Origin:** Startup Intelligence OS
**Applies to:** Alex Recruiting, Oracle Health

| Pattern | Description | Transfer Target |
|---------|-------------|-----------------|
| Research-first pipeline | 5-phase automated research before any build | All new projects |
| Team assembly from research | Susan picks agents based on research findings, not guesses | Alex Recruiting coach analysis |
| 6-dimension scorecard | Rate project readiness across Research, Team, Tech, Strategy, Capability, Governance | Oracle Health initiative assessment |
| Agent contradiction handling | Surface divergent outputs, never silently resolve | Any multi-agent workflow |

### 2. Outreach & Engagement Cadence
**Origin:** Alex Recruiting
**Applies to:** Oracle Health

| Pattern | Description | Transfer Target |
|---------|-------------|-----------------|
| Personalized outreach sequencing | Research target → personalized message → follow-up timing | Oracle Health strategist engagement |
| Engagement signal tracking | Track opens, replies, interest signals across touchpoints | Oracle Health stakeholder tracking |
| Relationship warmth scoring | Rate contact warmth (cold/warm/hot) based on interaction history | Cross-portfolio stakeholder management |

### 3. Knowledge Management & RAG
**Origin:** Startup Intelligence OS + Oracle Health
**Applies to:** All projects

| Pattern | Description | Transfer Target |
|---------|-------------|-----------------|
| Voyage AI embeddings (1024d) | Standardized embedding model across all RAG | Any new project with search |
| Domain tagging taxonomy | Structured tags for knowledge records | Alex Recruiting coach intelligence |
| Freshness lifecycle | DRAFT → REVIEW → PUBLISHED → AGING → STALE → REFRESH | All RAG-backed systems |
| Evidence grading | HIGH/MEDIUM/LOW/UNVERIFIED on every claim | Oracle Health briefs, strategy docs |

### 4. Content & Brief Generation
**Origin:** Oracle Health
**Applies to:** Startup Intelligence OS, Alex Recruiting

| Pattern | Description | Transfer Target |
|---------|-------------|-----------------|
| Stakeholder-specific formatting | Same data → different format per audience | Alex Recruiting (coach vs. parent view) |
| 7-pillar strategic framework | Organize intelligence around capability pillars | Startup Intelligence OS capability mapping |
| SharePoint-as-distribution | Use existing enterprise platforms for delivery | Any enterprise-facing output |

### 5. Session & Context Engineering
**Origin:** Startup Intelligence OS (WISC)
**Applies to:** All projects

| Pattern | Description | Transfer Target |
|---------|-------------|-----------------|
| 3-tier WISC context | CLAUDE.md → rules/ → docs/ | Every project gets this |
| Structured handoff protocol | Machine-readable HANDOFF.md for session continuity | All projects |
| Plan-before-build gate | No implementation without approved plan | All projects |
| Hook-based quality enforcement | Automated guardrails via Claude Code hooks | All projects |

---

## How to Use This Registry

1. **When starting work in any project:** Scan for applicable patterns from other domains
2. **When a pattern works well:** Add it here with origin and transfer targets
3. **When a pattern fails:** Note the failure and remove or update the entry
4. **Jake references this automatically** when cross-domain synergy is detected

## Adding New Patterns

```markdown
### N. Pattern Category Name
**Origin:** [source project]
**Applies to:** [target projects]

| Pattern | Description | Transfer Target |
|---------|-------------|-----------------|
| pattern_name | what it does | where it applies |
```
