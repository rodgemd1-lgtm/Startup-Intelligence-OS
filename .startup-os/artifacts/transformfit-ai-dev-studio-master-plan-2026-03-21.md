# TransformFit AI Dev Studio — Master Plan (2026-03-21)

## Objective
Build a full-company AI Dev Studio for TransformFit that can finish the product, operate the business, monetize the brand, and ship through a specialized multi-agent operating model led by Jake and powered by Susan.

## Framing
- **Planning control plane**: Startup Intelligence OS.
- **Execution repo**: Adapt-Evolve-Progress, as named by the user, once connected.
- **Brand to monetize**: TransformFit.
- **Operating stance**: company-grade, not feature-grade.
- **Decision**: design now, execute immediately after target repo audit.

## Recommendation
Use a Jake-led specialist studio with a 17-role operating model, an embedded markdown KB, Supabase-first infrastructure, an evidence-gated delivery cadence, and a 20-phase build plan that prioritizes repo audit, architecture lock, instrumented onboarding, memory, monetization, and launch readiness.

## Options considered
1. **Single-agent build mode** — faster to start, too brittle for this scope.
2. **Jake-led specialist studio** — best balance of fidelity, control, and sellable output. **Recommended.**
3. **Immediate code sprint without plan** — likely to create rework and mis-sequencing.

## Assumptions
- The execution repo contains the in-progress TransformFit app and website.
- Jake and Hermes should surface daily reporting and escalation.
- Susan remains the research and specialist foundry.
- A solo-founder-friendly stack and shipping cadence matter more than theoretical platform elegance.
- The company needs both a sellable product and a sellable operating system narrative.

## Risks
- No direct access yet to the Adapt-Evolve-Progress repo.
- Scope could sprawl beyond what can be responsibly shipped by end of next week.
- Revenue work may outrun validated retention improvements if sequencing slips.
- Too many agents without strong contracts could create orchestration theater.

## AI Dev Studio operating model

### Core departments
1. Executive orchestration
2. Product and program management
3. AI and memory systems
4. Backend/platform engineering
5. Frontend/app experience
6. Mobile and device experience
7. Research and intelligence
8. Growth and monetization
9. Brand/content and lifecycle messaging
10. Analytics and experimentation
11. Trust, security, and compliance
12. QA, evals, and release governance

### Agent roster and responsibilities
| Agent | Department | Primary output | Trigger |
|---|---|---|---|
| Jake | Executive orchestration | priorities, plans, escalations, daily brief | every major workstream |
| Susan | Foundry | specialist routing, research synthesis, capability maps | whenever domain depth is needed |
| Compass | Product | scope gates, ticket sequencing, dependency map | start of each phase |
| Atlas | Architecture | system diagrams, ADRs, integration constraints | architecture changes |
| Nova | AI | memory schema, model routing, prompt/eval strategy | AI feature or infra changes |
| Forge | Backend | APIs, DB, queues, integrations | backend task assigned |
| Spark | Frontend | web UI, design system, performance fixes | user-facing web task |
| Flux | Mobile | responsive/mobile workflows, PWA/app shell, sensors | mobile or workout UX task |
| Pulse | Analytics | event schema, dashboards, experiments | any funnel or feature launch |
| Mira | UX/Narrative | onboarding copy, coach voice, microcopy | any user-facing language |
| Freya | Retention | behavioral loops, nudges, habit mechanics | activation or retention project |
| Shield | Trust | policy checks, data minimization, safety and access review | auth, privacy, launch |
| Ledger | Finance | pricing, margin, AI cost guardrails | model or GTM changes |
| Steve | GTM | landing pages, offer stack, launch sequence | monetization phase |
| Scout | Research | competitor teardowns, user/problem briefs | new market or feature question |
| EVO | Process evolution | workflow upgrades, failure pattern analysis | daily review |
| Gatekeeper Panel | QA/Release | release readiness verdict, evidence and defect review | before deploy |

## Message-passing and control plane
- Each agent writes work artifacts, status updates, and blockers into structured run packets.
- Jake owns task assignment and executive synthesis.
- Compass enforces dependency sequencing.
- EVO reviews elapsed cycle time, defects, and rework sources daily.
- Gatekeeper Panel must approve launch-critical releases.
- Hermes receives daily summary output from Jake: completed, blocked, decision needed, tomorrow's move.

## Embedded KB design
### Required KB objects
- SOPs
- architecture decision records
- release gates
- incident notes
- design rules
- growth playbooks
- data definitions
- prompt/eval standards

### Reference convention
Use stable IDs in markdown, for example:
- `KB-ARCH-001`: Supabase multi-tenant schema rules
- `KB-REL-003`: pre-deploy release checklist
- `KB-GTM-002`: pricing experiment protocol

Then embed these references in code comments, tickets, scripts, and agent prompts:
```ts
// KB-REL-003: run smoke, eval, rollback checks before production deploy
```

## Technical architecture
### Application layer
- Next.js app for website, app shell, dashboards, and authenticated product flows.
- Component library built around TransformFit motion, coaching, and workout UX.
- API route or BFF layer for lightweight orchestration tasks.

### Service layer
- FastAPI or Python service for agent orchestration, evaluation jobs, content generation, and long-running pipelines.
- Worker processes for summarization, retrieval refresh, outbound lifecycle triggers, and research ingestion.

### Data layer
- Supabase Auth for identity.
- Postgres for product data, agent messages, run packets, phase logs, offers, experiments, and CRM events.
- Storage for assets and generated media.
- Vector support only where retrieval meaningfully beats structured memory.

### Analytics layer
- Product event schema beginning with signup, profile completion, first workout generated, workout started, workout completed, offer viewed, checkout started, and purchase completed.
- Daily dashboard for activation, retention, revenue, AI cost, and agent throughput.

## Monetization design for TransformFit
### Offer ladder
1. **Free personalized trial** — first workout + coach profile + progress preview.
2. **Core subscription** — adaptive workouts, coach memory, streaks, weekly plan refresh.
3. **Premium transformation plan** — deeper personalization, nutrition/recovery support, concierge AI planning.
4. **B2B/B2Coach toolkit** — white-label or coach-assist studio later, only after consumer proof.

### Monetization assets to ship by next week
- revised landing page
- clear offer comparison
- checkout path
- email/SMS waitlist and reactivation flow
- launch content calendar
- founder story / wedge narrative
- basic referral hook

## 20-phase plan through end of next week
### Phase 1 — Control-plane kickoff
- Confirm scope, success metrics, and execution repo access.
- Open decision, project, and capability records.

### Phase 2 — Repo audit
- Audit Adapt-Evolve-Progress structure, stack, environment, and current app state.
- Produce a gap map: design complete, partially built, missing, broken.

### Phase 3 — Brand and revenue lock
- Lock TransformFit brand story, ICP, wedge, pricing hypothesis, and CTA hierarchy.

### Phase 4 — Architecture lock
- Finalize target architecture: frontend, backend, agents, queues, data, auth, analytics, and deployment.

### Phase 5 — Embedded KB setup
- Create KB namespaces, ADR template, SOP template, code comment reference rules, and retrieval conventions.

### Phase 6 — Agent contracts
- Define 17 agent contracts: inputs, outputs, handoffs, tools, SLAs, escalation rules.

### Phase 7 — Department boards
- Create department backlogs for engineering, AI, marketing, research, trust, revenue, and panels.

### Phase 8 — UX and IA teardown
- Audit all live or designed screens; map missing states, broken flows, and copy inconsistencies.

### Phase 9 — Design system hardening
- Build tokens, component inventory, motion rules, accessibility rules, and coach persona presentation standards.

### Phase 10 — Supabase foundation
- Lock schema, auth, RLS, storage buckets, environment handling, and seed data.

### Phase 11 — Product analytics instrumentation
- Implement event taxonomy, dashboards, experiment flags, and cohort baselines before major redesign ships.

### Phase 12 — Onboarding compression
- Reduce onboarding to the minimum needed for first-value delivery and personalized first workout.

### Phase 13 — Persistent memory MVP
- Implement structured profile, session summaries, context injection, and memory retrieval.

### Phase 14 — Core workout and coach loop
- Finish workout generation, progress logging, adaptation logic, and coach-response surfaces.

### Phase 15 — Monetization funnel
- Ship pricing, paywall, checkout, lead capture, lifecycle messages, and purchase confirmation experiences.

### Phase 16 — Content and growth engine
- Launch landing pages, founder story assets, SEO program, social proof placeholders, and launch content pack.

### Phase 17 — QA, evals, and process evolution
- Run product QA, prompt evals, journey tests, and EVO review of bottlenecks.

### Phase 18 — Trust and launch readiness
- Verify policy pages, consent, safety language, rollback plans, access review, and incident response basics.

### Phase 19 — Beta launch and cohort review
- Release to a controlled cohort, review activation/retention/revenue signals, and prioritize fixes.

### Phase 20 — Sell-ready operating package
- Package the app, AI Dev Studio narrative, artifacts, launch deck, SOP bundle, and next-30-day roadmap.

## 100 discovery questions Jake wants answered

### Strategy and positioning
1. What exact outcome does TransformFit promise in one sentence?
2. Who is the first paying customer segment?
3. What segment do we explicitly exclude at launch?
4. What is the wedge versus Fitbod, Nike Training Club, and trainers?
5. Is the primary product for beginners, intermediates, or busy professionals?
6. What is the emotional promise beyond workout plans?
7. What is the fastest believable transformation claim?
8. What does “AI dev studio” mean externally versus internally?
9. Is the studio itself a future product or only internal leverage?
10. What is the pricing anchor for the first paid plan?

### Users, jobs, and behavior
11. What are the top 5 user jobs-to-be-done?
12. What event usually triggers a user to search for this product?
13. What does the user fear most about starting?
14. What does the user fear most about AI coaching?
15. What makes a first workout feel truly personalized?
16. What habits or routines already exist before they join?
17. How much time can they realistically commit per session?
18. What devices do they actually use during workouts?
19. What data will users willingly provide up front?
20. What data should be collected later via progressive profiling?

### Product scope
21. What are the non-negotiable MVP features?
22. Which features are nice-to-have but dangerous distractions?
23. What is the exact aha moment?
24. What should happen in the first 60 seconds after signup?
25. What should happen in the first 5 minutes?
26. What should happen in the first 24 hours?
27. What should happen by Day 7?
28. Which feature creates repeat use?
29. Which feature creates willingness to pay?
30. Which feature creates referrals?

### Experience and design
31. What UI already exists and what is only mockup-level?
32. Which screens feel premium today?
33. Which screens are broken or incomplete?
34. What design system is already in place?
35. What visual language should define TransformFit?
36. What tone should the coach use by user segment?
37. How should progress feel emotionally?
38. Which moments need motion or delight?
39. What accessibility standards must be met immediately?
40. What must the mobile experience optimize first?

### AI and agents
41. Which agents are runtime-facing versus internal-only?
42. Which agents need direct tool access?
43. What should Jake approve manually?
44. What should Susan route automatically?
45. What must EVO never change without approval?
46. What model providers are acceptable?
47. What tasks can use cheap models?
48. What tasks require high-intelligence models?
49. What evals define acceptable coach quality?
50. What evals define acceptable code-agent quality?

### Knowledge base and memory
51. Where should KB markdown live in the execution repo?
52. What naming convention should KB articles use?
53. Which code areas require KB references first?
54. What decisions must become ADRs immediately?
55. What runbooks are needed before launch?
56. What lessons from past mistakes already exist but are undocumented?
57. What should live in structured memory versus vector retrieval?
58. What summaries should be generated after each user session?
59. What summaries should be generated after each build run?
60. What data requires stricter access partitioning?

### Engineering and architecture
61. What stack is already implemented in Adapt-Evolve-Progress?
62. Is there a monorepo or split frontend/backend repos?
63. What is the deployment target today?
64. What environments already exist?
65. What auth system is active?
66. What database schema already exists?
67. Which integrations are already wired?
68. What CI/CD exists today?
69. What logging and observability exist?
70. What technical debt is blocking shipping?

### Analytics and experiments
71. Which events are already tracked correctly?
72. Which funnels are currently invisible?
73. What metrics should Jake report daily?
74. What metrics should Hermes summarize weekly?
75. Which experiments should run first?
76. What is the minimum sample size needed for each major decision?
77. What cohort definitions matter most?
78. How will attribution be handled?
79. How will AI cost per active user be measured?
80. What dashboard must exist before paid traffic starts?

### Monetization and GTM
81. Is the launch monetization subscription, one-time, coaching upsell, or hybrid?
82. What checkout provider is preferred?
83. Is there an annual plan at launch?
84. What free-to-paid conversion trigger should be used?
85. What proof assets exist today?
86. What founder story should power the launch narrative?
87. Which channels matter first: SEO, social, creator, paid, partnerships, outbound?
88. What lifecycle messages fire after signup, first workout, skipped day, and milestone?
89. What referral or community hook is viable by next week?
90. What market objections need direct rebuttal on the website?

### Trust, operations, and launch governance
91. What privacy and health disclaimers are legally required?
92. What user data is highest risk?
93. What safety boundaries should the AI coach enforce?
94. What rollback plan exists if launch breaks core flows?
95. Who approves launch-critical changes?
96. What is the support workflow for confused or frustrated users?
97. What incident classes should page Jake immediately?
98. What should trigger EVO to propose process changes?
99. What evidence is required before declaring launch success?
100. What is the next wedge after the first paid launch proves demand?

## Artifacts created or updated
- Company record
- Project record
- Decision record
- Three capability records
- Research benchmark packet
- This master plan

## Next actions
1. Connect or provide the Adapt-Evolve-Progress repo.
2. Provide the reference videos/repos/transcripts you want ingested.
3. Turn phases 1-5 into executable tickets.
4. Run the target repo audit immediately after it becomes available.
5. Start the KB and architecture lock before any major code sprint.
