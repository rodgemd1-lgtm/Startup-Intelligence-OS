# V10.0 Team Templates

Pre-configured multi-agent team compositions for common workflows.

## Research Team (5+1 pattern)

**Use when**: Deep research on a topic, competitive analysis, technology evaluation.

| Role | Agent | Model | Task |
|------|-------|-------|------|
| Lead | orchestrator | opus | Decompose research question into 5 search angles |
| Researcher 1 | research | sonnet | Official documentation and primary sources |
| Researcher 2 | research | sonnet | Practitioner blogs and case studies |
| Researcher 3 | research | sonnet | Academic papers (arxiv, ACL, EMNLP) |
| Researcher 4 | research | sonnet | Community discussion (Reddit, HN, forums) |
| Researcher 5 | research | sonnet | Competitive/market analysis |
| Synthesizer | orchestrator | opus | Resolve conflicts, produce unified findings |

**Expected tokens**: ~150K total
**Expected time**: 3-5 minutes

## Build Team (4-agent pattern)

**Use when**: Implementing a feature, fixing a complex bug, refactoring.

| Role | Agent | Model | Task |
|------|-------|-------|------|
| Planner | Plan | sonnet | Analyze codebase, design approach, identify files |
| Implementer | team-implementer | sonnet | Write the code |
| Reviewer | team-reviewer | haiku | Review for bugs, security, patterns |
| Tester | test-automator | sonnet | Write and run tests |

**Expected tokens**: ~100K total
**Expected time**: 5-10 minutes

## Decision Team (3-agent pattern)

**Use when**: Making architectural decisions, evaluating tradeoffs, strategic choices.

| Role | Agent | Model | Task |
|------|-------|-------|------|
| Analyst | research | sonnet | Gather evidence and prior art |
| Advocate | jake | sonnet | Present the builder's case |
| Critic | team-reviewer | sonnet | Stress-test the proposal |

**Expected tokens**: ~80K total
**Expected time**: 2-4 minutes

## Security Team (3-agent pattern)

**Use when**: Security audit, vulnerability assessment, compliance check.

| Role | Agent | Model | Task |
|------|-------|-------|------|
| Scanner | security-auditor | sonnet | OWASP top 10, dependency CVEs |
| Reviewer | code-reviewer | haiku | Code-level security review |
| Reporter | docs-architect | haiku | Generate security report |

## Quality Team (3-agent pattern)

**Use when**: Pre-release quality check, comprehensive review.

| Role | Agent | Model | Task |
|------|-------|-------|------|
| Architecture | architect-review | sonnet | Architecture and design patterns |
| Security | security-auditor | haiku | Security vulnerabilities |
| Performance | performance-engineer | haiku | Performance bottlenecks |

## Cost Optimization Guidelines

| Strategy | Savings | How |
|----------|---------|-----|
| Model routing | 60-80% | Haiku for search/validation, Sonnet for generation |
| Parallel execution | 30-50% time | Launch independent workers simultaneously |
| Context scoping | 20-40% tokens | Give workers only task-relevant context |
| Prompt caching | 50%+ on repeats | System prompts and tool docs are cache-eligible |
| Budget caps | Variable | Set max_turns on agents to prevent runaway |

## Invoking Teams

### Via Orchestrator
```
Use the orchestrator agent to decompose this task into a Research Team workflow:
[your request]
```

### Via Direct Team Spawn
```
/agent-teams:team-spawn with template: research-team
```

### Via Slash Commands
```
/plan-feature — triggers Build Team
/research-packet — triggers Research Team
/decision-room — triggers Decision Team
```
