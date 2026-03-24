# Process Doctrine — Non-Negotiable (DOCTRINE)

## The Process — Every Time, No Exceptions

Every task follows this exact sequence. Skipping a step is a CRITICAL FAILURE.

```
1. RESEARCH    → Complete ALL research before any design work begins
2. PLANNING    → Put a formal plan in place (written, approved by Mike)
3. EXECUTION   → Execute the plan (not before it's approved)
4. LESSONS     → Conduct a lessons learned session after execution
5. DOCUMENTATION → Write lessons into a permanent record
                   Include: what we learned + how we do it differently next time
```

### What This Means Concretely

**Research phase:**
- Dispatch research agents to cover every relevant source
- ALL agents must complete before moving to design
- No "I have enough to start" — research COMPLETES first
- Save research findings to `.claude/docs/` or reference docs

**Planning phase:**
- Write formal plan to `docs/plans/YYYY-MM-DD-<slug>.md`
- Plan includes bite-sized tasks, exact file paths, exact commands
- Mike must approve the plan before execution starts
- "Just build it" is not a valid plan

**Execution phase:**
- Follow the plan step by step
- If something unexpected comes up, STOP and revise the plan
- Do not improvise solutions that deviate from the approved plan
- Commit at each logical checkpoint

**Lessons learned phase:**
- After execution completes, conduct a formal review
- What went well? What went wrong? What was unexpected?
- What would we do differently next time?
- This is NOT optional — it happens every time

**Documentation phase:**
- Write lessons to `docs/lessons/YYYY-MM-DD-<slug>.md`
- Update relevant CLAUDE.md, rules, or TELOS files if lessons are durable
- These records are permanent — they make the next cycle better

## The Miessler Standard

Daniel Miessler is the reference implementation for everything we build.

**Before making any architectural decision:**
1. Check Miessler's repos first (PAI, TELOS, Fabric, Substrate, Daemon, Ladder, TheAlgorithm)
2. Ask: "How did Miessler solve this?"
3. Adapt his approach for our context (3 companies, Susan's 73 agents, OpenClaw)
4. Document where we diverge and WHY

**Key Miessler repos (reference):**
- `danielmiessler/Personal_AI_Infrastructure` — PAI v4.0.3 (the mothership)
- `danielmiessler/Telos` — Structured self-knowledge
- `danielmiessler/fabric` — 233 prompt patterns
- `danielmiessler/Substrate` — Collective intelligence framework
- `danielmiessler/Daemon` — Personal API (AI-to-AI communication)
- `danielmiessler/Ladder` — Autonomous optimization engine
- `danielmiessler/TheAlgorithm` — 7-phase execution loop + ISC methodology

**Key Miessler principles (internalize these):**
- "System Over Intelligence" — scaffolding matters more than the model
- "The model stays the same. The scaffolding evolves."
- "Without context, you have a tool. With context, you have an assistant that knows you."
- "90% of the power is in prompting."
- "Code Before Prompts" — write code to solve problems, use prompts to orchestrate code

## Context Health Doctrine

**Context must NEVER exceed 60%.** When approaching:
1. Stop work
2. Commit code
3. Write HANDOFF.md
4. Push to GitHub
5. Start new session

This is a first-class operation, not a failure. Fresh context = better decisions.
