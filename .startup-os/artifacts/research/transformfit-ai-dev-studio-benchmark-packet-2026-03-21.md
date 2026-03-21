# TransformFit AI Dev Studio Benchmark Packet — 2026-03-21

## Research question
What architecture, operating model, and benchmark patterns should TransformFit use to build a monetizable AI Dev Studio that can finish the product, run the company, and ship through a specialized multi-agent team inside the Adapt-Evolve-Progress execution repo?

## Definitions
- **AI Dev Studio**: a company-grade operating system that combines product delivery, engineering execution, research, GTM, analytics, compliance, and lifecycle orchestration through specialized agents, explicit department ownership, and evidence-linked artifacts.
- **Embedded KB**: markdown SOPs, best practices, ADRs, and failure lessons stored in-repo and referenced from code comments or task contracts so agents can discover procedures in context.
- **Process evolution agent**: a constrained optimizer that inspects artifacts, failures, and cycle-time bottlenecks to recommend or apply workflow improvements.
- **AEP loop**: Adapt → Evolve → Progress — the closed loop in which runtime data informs process changes that improve the next shipping cycle.

## Methods
1. Review the root Startup Intelligence OS contract, current workspace state, and Jake/Susan operating model.
2. Audit local TransformFit intelligence already stored in Susan outputs and domain research.
3. Extract reusable patterns from local docs discussing AEP, OpenClaw, Jake, and TransformFit.
4. Benchmark the required studio against current market patterns from leading agent and orchestration ecosystems.
5. Convert findings into a company artifact, a decision record, capability records, and a 20-phase execution plan.

## Source stack
### Internal sources
- Root workspace contract and active workspace state.
- Susan TransformFit outputs: company profile, team manifest, and analysis report.
- Existing Startup Intelligence OS docs on AEP, Jake, and OpenClaw.
- Fitness domain research already ingested under Susan.

### External benchmark stack
- Anthropic's public guidance on building effective agents for practical decomposition, tool use, and bounded workflows.
- LangGraph patterns for stateful, durable agent workflows and orchestration graphs.
- Microsoft AutoGen patterns for agent-to-agent collaboration and task specialization.
- Supabase patterns for auth, Postgres, storage, edge functions, and vector-backed retrieval in one managed system.
- OpenHands as a benchmark for code-agent execution surfaces and repo-facing autonomy.

## Benchmark targets
### Product and company targets
- Personalized first workout generated in under 5 minutes for a new user.
- Day-1 abandonment reduced below 40%.
- Day-7 return rate improved via one evidence-backed retention mechanic.
- First paid offer live by end of next week with at least one checkout path and one lead-capture path.

### Studio operating targets
- 13+ specialized agents with explicit owners, inputs, outputs, and handoff rules.
- Every ship-critical workflow backed by an SOP or ADR in markdown.
- All major workflows produce evidence trails: source links, metrics, artifacts, and decision updates.
- Process-evolution agent reviews each daily build cycle and proposes at least one measurable improvement.

### Technical targets
- Single managed backend baseline using Supabase for auth, Postgres, storage, queue-adjacent tables, and vectors.
- Message bus abstraction built first as durable database-backed events before introducing heavier broker complexity.
- Shared memory model combining structured user profile, session summaries, and knowledge retrieval.
- Strong role boundaries across app runtime, agent runtime, and analytics runtime.

## Synthesis
### What the internal evidence already says
TransformFit already has a strong internal framing: the biggest constraints are Day-1 abandonment, lack of persistent memory, no behavioral retention loop, solo-founder bandwidth, and a strict AI-cost ceiling. Susan's existing TransformFit outputs already define an eight-agent nucleus centered on onboarding, memory, analytics, finance, narrative, and product gating. That nucleus is a useful starting point, but it is not yet a full company-grade dev studio.

### What should be added to reach the user's target
To become a full AI Dev Studio, the system needs four expansions:
1. **Execution expansion** — add software-delivery roles like tech lead, backend engineer, frontend engineer, DevOps/release, QA/evals, and security/compliance.
2. **Commercial expansion** — add growth, content/brand, sales funnel, and lifecycle/CRM ownership.
3. **Control-plane expansion** — define message passing, artifact schemas, run packets, reporting contracts, and Jake/Hermes summaries.
4. **Embedded-KB expansion** — formalize markdown SOPs and code-comment references so agents can discover the right procedures where they work.

### Recommended architecture shape
- **Jake**: conductor, planner, escalation point, executive reporter.
- **Susan**: specialist foundry, research router, capability mapping layer.
- **Hermes**: personal assistant OS and reporting relay, especially for summaries, reminders, and execution visibility.
- **Supabase**: starting system of record for users, content, agent messages, run logs, retrieval metadata, feature flags, and growth events.
- **App runtime**: Next.js web app + mobile-ready responsive shell, with API routes or FastAPI service for specialized workloads.
- **Agent runtime**: Python orchestration layer with durable work queues, evaluation gates, and repo-task adapters.
- **Knowledge runtime**: markdown KB + structured decisions/capabilities in Startup OS + Susan RAG.

### Recommended 13-plus-agent roster
1. Jake — executive conductor and phase owner.
2. Susan — capability foundry and specialist router.
3. Compass — PM/program manager.
4. Atlas — systems architect / tech lead.
5. Nova — AI engineer and memory architect.
6. Forge — backend engineer / data systems.
7. Spark — frontend + design systems engineer.
8. Flux — mobile/app shell engineer.
9. Pulse — analytics and experimentation.
10. Mira — persona, UX writing, and coach voice.
11. Freya — behavioral science and retention.
12. Shield — security, privacy, and policy.
13. Ledger — finance and unit economics.
14. Steve — GTM, positioning, and launches.
15. Scout — market and competitive research.
16. EVO — process evolution and QA-of-the-system.
17. Gatekeeper Panel — review board for release, evidence, and risk.

## Unknowns
- The actual structure and code state of the Adapt-Evolve-Progress repo is still unknown in this workspace.
- The current TransformFit production database, auth setup, and frontend maturity need direct audit.
- The user's preferred pricing model, launch package, and first sellable wedge are not yet confirmed.
- No direct video/reference package from the user has been ingested yet.

## Next research steps
1. Mount or clone the Adapt-Evolve-Progress repo into the workspace and run a full repo audit.
2. Ingest the user's reference videos, transcripts, and repos into Susan's research corpus.
3. Benchmark 3-5 comparable AI studio/app builder systems against the proposed architecture.
4. Produce executable tickets and run packets for phases 1-5.
5. Build the embedded KB spec and code-comment reference convention before feature work starts.
