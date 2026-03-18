---
name: project-dashboard
description: Side-by-side comparison dashboard of all active projects. Shows git activity, agent coverage, recent signals, health status, and next moves for each project.
---

# Project Comparison Dashboard

Produce a side-by-side health comparison of all active projects. Answers: **"How are all my projects doing right now?"**

## When to Invoke
- User says "project dashboard", "show me all projects", "how are my projects doing"
- Weekly review / planning sessions
- Before deciding where to focus next
- Invoked via `/project-dashboard`

## Step 1: Gather Data for Each Project

For each of the 3 active projects, collect:

### Projects to Check

| Project | Path | Type |
|---------|------|------|
| Startup Intelligence OS | `/Users/mikerodgers/Startup-Intelligence-OS/` | Platform |
| Oracle Health AI Enablement | `/Users/mikerodgers/Desktop/oracle-health-ai-enablement/` | Strategy Hub |
| Alex Recruiting | `/Users/mikerodgers/Desktop/alex-recruiting-project/alex-recruiting/` | App |

### Data Points per Project

1. **Git activity** — run `git log --oneline --since="7 days ago"` and count commits
2. **Last commit** — run `git log --oneline -1` for date and message
3. **Working tree** — run `git status --short` for uncommitted changes
4. **HANDOFF.md** — read if exists, extract status and next steps
5. **CLAUDE.md** — read first 20 lines for project identity
6. **Recent briefs** — check `.startup-os/briefs/` for any project-specific output (last 7 days)
7. **Agent coverage** — check `.claude/agents/` if directory exists
8. **Scheduled tasks** — note any active crons for this project

## Step 2: Assess Health

Score each project:

| Health | Criteria |
|--------|----------|
| **GREEN** | Active commits in last 7 days, no stale HANDOFF, tests passing |
| **YELLOW** | Some activity but slowing, or uncommitted changes > 3 days old |
| **ORANGE** | No commits in 14+ days, or known blockers unresolved |
| **RED** | No activity in 30+ days, or critical bugs/blockers |

## Step 3: Produce Dashboard

```markdown
# Project Dashboard — {date}

## Overview

| Dimension | Startup Intelligence OS | Oracle Health | Alex Recruiting |
|-----------|------------------------|---------------|-----------------|
| Health | {GREEN/YELLOW/ORANGE/RED} | {status} | {status} |
| Last commit | {date + message} | {date + message} | {date + message} |
| Commits (7d) | {count} | {count} | {count} |
| Uncommitted | {count files} | {count files} | {count files} |
| Agents | {count} | {count} | {count} |
| Scheduled tasks | {count} | {count} | {count} |
| Blockers | {any?} | {any?} | {any?} |

## Startup Intelligence OS
- **Status**: {1-2 sentence summary}
- **Recent wins**: {from git log}
- **Next move**: {from HANDOFF or briefs}
- **Risk**: {any concerns}

## Oracle Health AI Enablement
- **Status**: {1-2 sentence summary}
- **Recent wins**: {from git log}
- **Next move**: {from HANDOFF or briefs}
- **Risk**: {any concerns}

## Alex Recruiting
- **Status**: {1-2 sentence summary}
- **Recent wins**: {from git log}
- **Next move**: {from HANDOFF or briefs}
- **Risk**: {any concerns}

## Recommended Focus
**Where Mike should spend time today**: {project} — because {reasoning}

## Cross-Project Signals
- {Any patterns or connections between projects worth noting}
```

## Rules

1. **Real data only** — every field comes from git, files, or briefs. No guessing.
2. **Be honest about inactivity** — if a project hasn't been touched, say so plainly.
3. **One recommendation** — "Recommended Focus" picks ONE project, not three.
4. **Quick to read** — the overview table should answer "how are things?" in 10 seconds. Details below for those who want to dig in.
5. **No judgment** — a project being YELLOW isn't failure. It might just not be the priority right now.
