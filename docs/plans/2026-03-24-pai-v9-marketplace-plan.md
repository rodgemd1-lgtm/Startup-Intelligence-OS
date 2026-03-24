# PAI V9: Marketplace — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Share what works. Package custom patterns, skills, and frameworks for distribution via ClawHub and open source. Create revenue potential from the skill marketplace. Build a TELOS onboarding wizard for other founders.

**Depends On:** V0-V8 complete

**Score Target:** 93 → 95

---

## Pre-Flight Checklist

- [ ] V8 exit criteria all passed (cross-domain intelligence operational)
- [ ] 10+ custom Fabric patterns proven and battle-tested
- [ ] 5+ OpenClaw skills built and stable
- [ ] TELOS framework proven over 6+ months
- [ ] Jake personality framework documented
- [ ] ClawHub account created and accessible

---

## Phase 9A: Package Custom Patterns for ClawHub

### Task 1: Curate and Package Battle-Tested Patterns

**Files:**
- Create: `pai/marketplace/patterns/` (packageable patterns)
- Create: `pai/marketplace/patterns/package.json`

**What it does:**
Package the custom Fabric patterns auto-generated in V5 that have proven useful, plus any hand-crafted patterns.

**Patterns to package:**
- `jake_competitive_brief` — Structured competitive analysis format
- `jake_decision_frame` — Decision support with red team analysis
- `jake_meeting_summary` — Meeting summary in exec brief format
- `jake_morning_brief` — Morning brief compilation pattern
- `jake_research_synthesis` — Research findings synthesis
- Any other patterns with 10+ successful uses

**Implementation steps:**
1. Audit all custom patterns: usage count, satisfaction rating, failure rate
2. Select patterns with: 10+ uses, >4.0 avg rating, <5% failure rate
3. Clean up pattern prompts (remove personal context, generalize)
4. Add README, examples, and configuration docs per pattern
5. Package as ClawHub-compatible format:
   ```bash
   clawhub package create jake-patterns --patterns pai/marketplace/patterns/
   ```
6. Publish to ClawHub:
   ```bash
   clawhub publish jake-patterns
   ```
7. Track downloads, ratings, and feedback

**Commit:** `feat(pai): ClawHub pattern package — battle-tested custom Fabric patterns`

---

### Task 2: Package Susan Skills as OpenClaw Skills

**Files:**
- Create: `pai/marketplace/skills/` (packageable skills)

**Skills to package:**
| Skill | Description | Dependencies |
|-------|-------------|-------------|
| `jake-research-pipeline` | Multi-source research with synthesis | Fabric, Susan RAG |
| `jake-morning-brief` | Automated morning brief generation | Gmail, Calendar, Supabase |
| `jake-decision-support` | Structured decision framework | Fabric patterns |
| `jake-goal-tracker` | Goal tracking with git activity signals | Supabase, git |
| `jake-self-repair` | Service health monitoring and auto-restart | launchd |

**Implementation steps:**
1. Extract each skill from PAI codebase into standalone package
2. Remove hardcoded paths (use env vars and config)
3. Create installer that configures dependencies
4. Write documentation: setup, config, usage examples
5. Publish each to ClawHub as installable skill
6. Track installations and issues

**Commit:** `feat(pai): ClawHub skill packages — 5 standalone PAI skills`

---

## Phase 9B: TELOS Onboarding Wizard

### Task 3: Build TELOS Onboarding for Other Founders

**Files:**
- Create: `pai/marketplace/telos-wizard/`
- Create: `pai/marketplace/telos-wizard/wizard.py`
- Create: `pai/marketplace/telos-wizard/templates/`

**What it does:**
Interactive wizard that helps a new founder create their own TELOS identity files.

**Wizard flow:**
1. **Mission discovery:** "What do you want to build? Why does it matter?"
   → Generates MISSION.md
2. **Goals setting:** "What are your goals for the next 30 days? 6 months? 3 years?"
   → Generates GOALS.md
3. **Values mapping:** "What do you believe about AI? Business? Life?"
   → Generates BELIEFS.md
4. **Challenge identification:** "What's blocking you right now?"
   → Generates CHALLENGES.md, PROBLEMS.md
5. **Context gathering:** "Tell me about your projects, team, company"
   → Generates PROJECTS.md, NARRATIVES.md
6. **Mental models:** "How do you make decisions?"
   → Generates MODELS.md, FRAMES.md, STRATEGIES.md
7. **Review and refine:** Show all generated files, let user edit

**Implementation steps:**
1. Create wizard as Claude Code skill (interactive Q&A)
2. Create templates with placeholder prompts for each TELOS file
3. Use Fabric `improve_writing` to polish generated content
4. Output: complete TELOS directory ready to drop into any PAI setup
5. Publish as standalone tool + ClawHub skill
6. Create companion blog post / documentation

**Commit:** `feat(pai): TELOS onboarding wizard — interactive identity creation for new founders`

---

## Phase 9C: Jake Personality Framework

### Task 4: Create Personality Framework Template

**Files:**
- Create: `pai/marketplace/personality-framework/`
- Create: `pai/marketplace/personality-framework/README.md`
- Create: `pai/marketplace/personality-framework/templates/`

**What it does:**
Template system for creating custom AI personalities (not just Jake — any personality).

**Framework components:**
1. `SOUL.md` template — Voice, tone, boundaries, behaviors
2. `IDENTITY.md` template — Name, emoji, version, principal
3. `AISTEERINGRULES.md` template — Behavioral rules (universal + custom)
4. `personality-config.json` — Personality parameters
5. Channel adaptation rules — How personality shifts per channel
6. Example personalities: Professional, Casual, Coach, Analyst

**Implementation steps:**
1. Extract personality system from PAI into standalone framework
2. Create template system with variables: `{{name}}`, `{{voice}}`, `{{boundaries}}`
3. Create 4 example personalities showing range
4. Write documentation: how to create, customize, and deploy
5. Publish as ClawHub package + GitHub repo

**Commit:** `feat(pai): personality framework — template system for custom AI personalities`

---

## Phase 9D: Revenue and Distribution

### Task 5: Set Up Revenue Infrastructure

**Implementation steps:**
1. Create pricing tiers for ClawHub skills:
   - **Free:** TELOS wizard, personality templates, basic patterns
   - **Pro ($9/mo):** Full pattern pack, research pipeline, goal tracker
   - **Enterprise (contact):** Custom deployment, white-label, support
2. Set up Stripe integration for paid skills (if ClawHub supports it)
3. Create landing page: what Jake PAI is, demo video, install instructions
4. Write "Building a Personal AI" blog post series
5. Track: downloads, active users, revenue, support tickets

**Commit:** `feat(pai): marketplace revenue infrastructure — pricing, Stripe, landing page`

---

## V9 Exit Criteria (All Must Pass)

- [ ] 3+ patterns published to ClawHub with documentation
- [ ] 3+ skills published to ClawHub as installable packages
- [ ] TELOS onboarding wizard works end-to-end for a new user
- [ ] Personality framework published with 4 example personalities
- [ ] 1+ external user has installed and is running a skill Mike built
- [ ] Landing page deployed with install instructions
- [ ] Revenue infrastructure set up (even if revenue is $0 initially)

**Score target: 93 → 95**
