# Wave 1 Skill Audit — obra/superpowers + muratcankoylan Context Engineering

**Date**: 2026-03-27
**Auditor**: Jake (Claude Code)
**Scope**: Wave 1 skills from voltagent-catalog.md — obra/superpowers (18 skills) + muratcankoylan/Agent-Skills-for-Context-Engineering (8 skills)

---

## Summary

| Category | Count | Already Covered | Missing | Duplicates |
|----------|-------|----------------|---------|------------|
| obra/superpowers | 18 | 12 (partial/full) | 6 | 0 |
| muratcankoylan context-engineering | 8 | 7 (partial/full) | 1 | 0 |
| **Total** | **26** | **19** | **7** | **0** |

---

## obra/superpowers — 18 Skills

### Operations / Planning Skills (mapped to jake, orchestrator)

| # | Skill | URL | Status | Existing Coverage | Action |
|---|-------|-----|--------|-------------------|--------|
| 1 | writing-plans | [SKILL.md](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md) | **COVERED** | `.claude/rules/process-doctrine.md` enforces plan-first development. `.claude/rules/session-protocol.md` Step 2 defines the plan format. Jake's Plan Gate in `jake.md` blocks coding without plans. | **SKIP** — deeply embedded in Jake's cognitive architecture already |
| 2 | executing-plans | [SKILL.md](https://github.com/obra/superpowers/blob/main/skills/executing-plans/SKILL.md) | **COVERED** | `.claude/rules/session-protocol.md` Steps 4-7 define execution with checkpoints, validation gates, and test-after-each-unit. Jake's Executor Mind handles this. | **SKIP** — already have execution protocol with quality gates |
| 3 | dispatching-parallel-agents | [SKILL.md](https://github.com/obra/superpowers/blob/main/skills/dispatching-parallel-agents/SKILL.md) | **PARTIAL** | `.claude/skills/research-pipeline/SKILL.md` Phase 2 dispatches parallel researchers. Jake's rules mention sub-agent dispatch. No *generic* parallel dispatch skill exists. | **INSTALL** — would add a reusable pattern beyond research-specific dispatch |
| 4 | subagent-driven-development | [SKILL.md](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md) | **PARTIAL** | Jake rules mention sub-agents for research. No formal dev-specific sub-agent orchestration skill. | **INSTALL** — fills gap for dev workflow sub-agent patterns |
| 5 | brainstorming | [SKILL.md](https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md) | **MISSING** | Nothing in current skills covers structured brainstorming with convergence. Jake's Strategist Mind thinks strategically but lacks a formal brainstorming protocol. | **INSTALL** — useful for ideation sessions |
| 6 | condition-based-waiting | [SKILL.md](https://github.com/obra/superpowers/blob/main/skills/condition-based-waiting/SKILL.md) | **MISSING** | No async polling/waiting pattern exists in current skills. | **INSTALL** — needed for agent coordination when dispatching parallel work |
| 7 | verification-before-completion | [SKILL.md](https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md) | **COVERED** | `.claude/skills/jake-review/SKILL.md` is a full review pipeline. `.claude/skills/jake-qa/SKILL.md` is a full QA pipeline. `.claude/skills/jake-ship/SKILL.md` enforces review+QA before shipping. Session protocol Steps 5-6 cover review and QA. | **SKIP** — our review/QA/ship pipeline is more comprehensive |
| 8 | sharing-skills | [SKILL.md](https://github.com/obra/superpowers/blob/main/skills/sharing-skills/SKILL.md) | **MISSING** | No skill for distributing/sharing skills across agents. | **INSTALL** — useful for the multi-agent roster (73 agents) |
| 9 | using-superpowers | [SKILL.md](https://github.com/obra/superpowers/blob/main/skills/using-superpowers/SKILL.md) | **MISSING** | No meta-skill for composing capabilities. | **INSTALL** — meta-skill for composing agent abilities, useful as orchestrator reference |
| 10 | superpowers-commands | [commands/](https://github.com/obra/superpowers/tree/main/skills/commands) | **COVERED** | `.claude/skills/` has 19 skills with CLI-style invocation. `bin/jake` provides CLI commands. Session protocol defines `/think`, `/plan`, `/build`, `/review`, `/qa`, `/ship`, `/reflect`. | **SKIP** — our command surface is already extensive |
| 11 | superpowers-lab | [repo](https://github.com/obra/superpowers-lab) | **N/A** | This is an experimental lab repo, not a single skill. | **SKIP** — reference only, not installable as a skill |
| 12 | writing-skills | [SKILL.md](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md) | **COVERED** | We already have 19 custom skills in `.claude/skills/`. The pattern is established. | **SKIP** — we know how to write skills |

### Engineering / QA Skills (mapped to forge-qa, atlas, sentinel)

| # | Skill | URL | Status | Existing Coverage | Action |
|---|-------|-----|--------|-------------------|--------|
| 13 | systematic-debugging | [SKILL.md](https://github.com/obra/superpowers/blob/main/skills/systematic-debugging/SKILL.md) | **PARTIAL** | `.claude/skills/jake-review/SKILL.md` does bug detection but not systematic debugging methodology. No dedicated debugging skill. | **INSTALL** as reference — useful for forge-qa agent |
| 14 | root-cause-tracing | [SKILL.md](https://github.com/obra/superpowers/blob/main/skills/root-cause-tracing/SKILL.md) | **MISSING** | No root cause analysis skill exists. Jake-review finds bugs but doesn't trace root causes. | **INSTALL** — fills a real gap |
| 15 | test-driven-development | [SKILL.md](https://github.com/obra/superpowers/blob/main/skills/test-driven-development/SKILL.md) | **COVERED** | `.claude/rules/tests.md` defines test patterns. Jake-ship runs tests before committing. Session protocol requires tests after each logical unit. | **SKIP** — TDD philosophy already embedded in process doctrine |
| 16 | testing-anti-patterns | [SKILL.md](https://github.com/obra/superpowers/blob/main/skills/testing-anti-patterns/SKILL.md) | **PARTIAL** | `.claude/rules/tests.md` exists but may not cover anti-patterns specifically. | **MERGE** — review and incorporate any missing anti-patterns into `tests.md` |
| 17 | testing-skills-with-subagents | [SKILL.md](https://github.com/obra/superpowers/blob/main/skills/testing-skills-with-subagents/SKILL.md) | **MISSING** | No skill for testing skills via sub-agents. | **SKIP** — low priority, niche use case |
| 18 | receiving-code-review / requesting-code-review / finishing-a-development-branch / using-git-worktrees / defense-in-depth | various | **COVERED** | `jake-review` handles code review. `jake-ship` handles branch completion. OpenClaw rules in `jake.md` Protocol 4 explicitly covers git worktrees. | **SKIP** — already have comprehensive git/review workflow |

---

## muratcankoylan/Agent-Skills-for-Context-Engineering — 8 Skills

| # | Skill | URL | Status | Existing Coverage | Action |
|---|-------|-----|--------|-------------------|--------|
| 1 | context-compression | [link](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/context-compression) | **COVERED** | `.claude/rules/context-health.md` monitors context usage. `.claude/rules/context-hygiene.md` defines conservation rules. `.claude/skills/structured-context/SKILL.md` handles handoffs to manage context. Jake's Guardian Mind tracks context budget with 60% hard limit. | **SKIP** — our context management is more comprehensive (3 files + guardian mind) |
| 2 | context-degradation | [link](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/context-degradation) | **COVERED** | `context-health.md` Signal 3 (repeated reads = context aging), Signal 4 (error accumulation = quality dropping). Jake announces context health levels (GREEN/YELLOW/ORANGE/RED). 60% hard limit doctrine. | **SKIP** — already have degradation detection with alert levels |
| 3 | context-fundamentals | [link](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/context-fundamentals) | **COVERED** | WISC three-tier system (CLAUDE.md → rules → docs) IS the context fundamentals implementation. Chain-of-Index protocol in `jake-context-engineering.md` defines the 3-level navigation. | **SKIP** — WISC IS our context fundamentals framework |
| 4 | context-optimization | [link](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/context-optimization) | **COVERED** | `context-hygiene.md` defines minimal context loading rules. `jake-context-engineering.md` Protocol 2 (Chain-of-Index) defines context budget tracking per task type. | **SKIP** — already optimized with budget tracking per task |
| 5 | memory-systems | [link](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/memory-systems) | **COVERED** | `jake-memory-ops.md` defines 3-tier memory (Session → Curated Long-Term → Deep Knowledge). Jake Brain has 4-layer cognitive memory (Working → Episodic → Semantic → Procedural). SuperMemory integration. This is one of our strongest areas. | **SKIP** — our memory architecture is significantly more advanced |
| 6 | multi-agent-patterns | [link](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/multi-agent-patterns) | **PARTIAL** | OpenClaw Protocol 4 covers multi-agent safety. Susan has 73-agent orchestration. But no formal *pattern library* for multi-agent coordination exists as a reference skill. | **INSTALL** — would serve as a reference pattern library |
| 7 | tool-design | [link](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/tool-design) | **COVERED** | `.claude/rules/agent-skill-definitions.md` defines how to create agents/skills/commands. 19 skills already demonstrate the pattern. MCP server design in `susan-runtime.md`. | **SKIP** — we have practical tool design experience across 19 skills |
| 8 | evaluation | [link](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/evaluation) | **PARTIAL** | `.claude/skills/project-assessment/SKILL.md` does project-level evaluation (6-dimension scorecard). Jake's quality gates at build milestones. But no generic *agent output evaluation* skill. | **MERGE** — review for agent-level evaluation patterns we might be missing |

---

## Action Summary

### INSTALL (7 skills — genuinely missing capabilities)

| Priority | Skill | Source | Why Install |
|----------|-------|--------|-------------|
| 1 | dispatching-parallel-agents | obra/superpowers | Reusable parallel dispatch pattern beyond research-specific use |
| 2 | subagent-driven-development | obra/superpowers | Dev workflow sub-agent patterns (not just research) |
| 3 | condition-based-waiting | obra/superpowers | Async polling needed for agent coordination |
| 4 | brainstorming | obra/superpowers | No structured ideation protocol exists |
| 5 | sharing-skills | obra/superpowers | Skill distribution across 73-agent roster |
| 6 | using-superpowers | obra/superpowers | Meta-skill for composing agent capabilities |
| 7 | multi-agent-patterns | muratcankoylan | Reference pattern library for multi-agent coordination |

### MERGE (2 skills — review and incorporate missing pieces into existing files)

| Skill | Source | Merge Into |
|-------|--------|-----------|
| testing-anti-patterns | obra/superpowers | `.claude/rules/tests.md` |
| evaluation | muratcankoylan | `.claude/skills/project-assessment/SKILL.md` or new `agent-evaluation` skill |

### SKIP (17 skills — already covered or not applicable)

| Skill | Reason |
|-------|--------|
| writing-plans | Plan-first development deeply embedded in jake.md + process-doctrine.md + session-protocol.md |
| executing-plans | Executor Mind + session protocol Steps 4-7 |
| verification-before-completion | jake-review + jake-qa + jake-ship pipeline is more comprehensive |
| superpowers-commands | 19 skills + bin/jake already provide extensive command surface |
| superpowers-lab | Reference repo, not an installable skill |
| writing-skills | Pattern established across 19 existing skills |
| test-driven-development | tests.md + jake-ship already enforce TDD |
| testing-skills-with-subagents | Niche, low priority |
| receiving-code-review | jake-review covers this |
| requesting-code-review | jake-review covers this |
| finishing-a-development-branch | jake-ship covers this |
| using-git-worktrees | OpenClaw Protocol 4 covers this |
| defense-in-depth | jake-review OWASP check covers security |
| context-compression | context-health.md + context-hygiene.md + 60% doctrine |
| context-degradation | Guardian Mind with GREEN/YELLOW/ORANGE/RED alerts |
| context-fundamentals | WISC three-tier system IS the implementation |
| context-optimization | Chain-of-Index + context budget tracking |
| memory-systems | Jake Brain 4-layer + jake-memory-ops 3-tier + SuperMemory |
| tool-design | 19 skills + agent-skill-definitions.md |

---

## Existing Coverage Map

### Where We Are Strong (No Action Needed)
- **Context engineering**: WISC + Chain-of-Index + Guardian Mind + 60% doctrine = best-in-class
- **Memory systems**: Jake Brain (4-layer cognitive) + jake-memory-ops (3-tier) + SuperMemory = exceeds muratcankoylan
- **Planning & execution**: Plan Gate + Session Protocol + Process Doctrine = comprehensive
- **Code review & QA**: jake-review + jake-qa + jake-ship = full pipeline
- **Tool/skill authoring**: 19 skills already demonstrate the pattern

### Where We Have Gaps (Action Needed)
- **Parallel agent dispatch**: Only research-pipeline does this; need a generic pattern
- **Sub-agent dev workflows**: No formal pattern for dev-specific sub-agent orchestration
- **Async coordination**: No condition-based waiting/polling pattern
- **Brainstorming protocol**: Jake challenges ideas but lacks structured ideation
- **Multi-agent pattern library**: We orchestrate 73 agents but lack a reference pattern catalog
- **Skill sharing across agents**: No mechanism to distribute skills to the full roster

---

## Next Steps

1. **Fetch the 7 INSTALL skills** from their GitHub URLs (use `mcp__github__get_file_contents` or web fetch)
2. **Adapt each skill** to Jake's architecture (add WISC references, Jake personality hooks, Susan agent mappings)
3. **Install to** `.claude/skills/` with proper SKILL.md format
4. **Review the 2 MERGE skills** and incorporate missing patterns into existing files
5. **Update CLAUDE.md** skill routing table if new skills add slash commands
