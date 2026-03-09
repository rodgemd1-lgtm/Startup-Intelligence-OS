# Decision & Capability OS — Capability Gap Map

## Goal

Close the gaps required to make the OS good at:
- building companies
- building projects
- improving capabilities over time
- using agents without losing quality

---

## 1. Intelligence to decision gaps

| Gap | Why it hurts | Build target | Definition of done |
|---|---|---|---|
| No decision object | conversations disappear into chat history | decision record schema | every major recommendation writes a decision record |
| Weak option comparison | default answer bias | options matrix | every decision has 3+ options unless impossible |
| Hidden assumptions | false confidence | assumptions ledger | every recommendation exposes assumptions |
| No reversal logic | sunk-cost behavior | reversal criteria field | every decision says what would change the call |
| Weak traceability | hard to learn | decision lineage | child decisions link to parent decisions |

---

## 2. Capability system gaps

| Gap | Why it hurts | Build target | Definition of done |
|---|---|---|---|
| No formal capability ontology | can’t compare or improve consistently | capability taxonomy | capabilities are named, scoped, and reusable |
| No current vs target state | no clear delta | maturity model | every capability can be scored current + target |
| No explicit owners | capability plans die | ownership model | each capability has human and/or agent owner |
| No build sequence | all gaps look equal | capability roadmap | each gap has sequence and prerequisites |
| No evidence links | opinions masquerade as facts | capability evidence links | each capability claim cites sources/artifacts |

---

## 3. Research quality gaps

| Gap | Why it hurts | Build target | Definition of done |
|---|---|---|---|
| No source grading | garbage can dominate | source grading system | every packet uses source quality labels |
| No benchmark library | no target standard | benchmark registry | common targets and comparisons are reusable |
| No protocol templates | methods drift | protocol pack | packets use standard protocols |
| No eval loop | quality stays anecdotal | workflow evals | failures feed back into skills and playbooks |

---

## 4. Execution gaps

| Gap | Why it hurts | Build target | Definition of done |
|---|---|---|---|
| Wrong-directory risk | agents load wrong context | workspace launcher | every session starts in known workspace |
| Weak handoff | terminal and UI drift | run/session registry | handoffs preserve state |
| Artifact sprawl | outputs get lost | artifact explorer | artifacts are indexed and searchable |
| Parallel task collisions | worktree conflict risk | worktree policy | every build task has a safe execution path |
| Poor completion checks | “done” is fuzzy | quality gates | runs stop only after checks or reviewer confirmation |

---

## 5. Conversational layer gaps

| Gap | Why it hurts | Build target | Definition of done |
|---|---|---|---|
| Persona-only system | charming but brittle | persona over kernel | Jake/Susan sit on structured workflows |
| No session greeting guarantee | inconsistent experience | launcher + instructions | Jake appears on every new session |
| Too many visible agents | cognitive overload | exposed vs hidden team split | only 3–4 agents shown at first |
| No routing rules | overlap and noise | role boundaries | Jake routes, Susan maps, build builds |

---

## 6. Interface gaps

| Gap | Why it hurts | Build target | Definition of done |
|---|---|---|---|
| No workspace home | no orientation | workspace dashboard | active repo/company/project always visible |
| No decision room | no core control surface | decision room page | decisions are created and updated there |
| No capability foundry | Susan has no home | foundry page | capability audits and roadmaps live there |
| No run visibility | execution hidden | run timeline | every build/research run is inspectable |
| No artifact browser | reuse is weak | artifact explorer | users can find and compare outputs |

---

## 7. Highest-priority closures

1. workspace contract  
2. Jake launcher  
3. decision record schema  
4. capability schema  
5. artifact index  
6. decision room workflow  
7. capability foundry workflow  
8. build routing to worktree/runtime  
9. research packet workflow  
10. interface home

---

## 8. World-class bar

This system is world-class when:
- the user rarely restates context
- a new company or project can be stood up quickly
- major decisions always have alternatives and assumptions
- capability gaps are explicit and sequenced
- outputs compound into reusable playbooks
- terminal and interface never disagree about where work is happening
