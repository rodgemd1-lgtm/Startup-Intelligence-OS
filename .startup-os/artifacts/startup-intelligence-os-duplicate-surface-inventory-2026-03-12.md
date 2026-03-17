# Startup Intelligence OS Duplicate Surface Inventory

## Objective
Map duplicate agent, capability, and studio surfaces into one canonical Wave 1 department wrapper so the ask-driven OS routes through stable departments instead of a growing flat roster.

## Canonical Department Wrappers

### Founder Decision Room
- Canonical scope: company strategy, prioritization, operating model, future-back planning, decision governance
- Consolidates:
  - `decision-kernel`
  - `innovation-strategy`
  - Jake front-door orchestration
  - decision-room outputs in `.startup-os/decisions`

### Consumer User Studio
- Canonical scope: customer research, synthetic users, evidence synthesis, ranked opportunities, experiment design
- Consolidates:
  - `customer-user-studio`
  - `intelligence-research`
  - customer scenario, persona, session, and ranked opportunity artifacts
  - Susan research routing for user evidence

### Product & Experience Studio
- Canonical scope: product direction, workflow design, roadmap shaping, operator UX, implementation-ready experience briefs
- Consolidates:
  - `ux-design`
  - `operator-experience`
  - product and workflow shaping work currently scattered across app surfaces

### Marketing & Narrative Studio
- Canonical scope: positioning, message maps, launch sequences, proof spines, asset cascades
- Consolidates:
  - `content-marketing`
  - marketing studio director narrative work
  - launch and messaging artifacts that are currently distributed across notes and strategy docs

### Engineering & Agent Systems Studio
- Canonical scope: architecture, implementation, agent orchestration, platform quality, runtime-safe build execution
- Consolidates:
  - `agent-orchestration`
  - `platform-infrastructure`
  - `data-analytics` where it directly supports build and operator execution
  - implementation work in `apps/decision_os`, `apps/v5`, and runtime-safe integration with `susan-team-architect/backend`

## Duplicate Clusters To Reduce
- Product versus operator experience: converge into Product & Experience Studio with one implementation handoff path.
- Research versus customer simulation: converge into Consumer User Studio with shared evidence and writeback rules.
- Strategy versus decision documentation: converge into Founder Decision Room with one decision-record contract.
- Marketing notes versus launch execution: converge into Marketing & Narrative Studio with one message-map and proof-spine contract.
- Engineering, platform, and agent orchestration: converge into Engineering & Agent Systems Studio with one implementation packet and eval path.

## Cleanup Rule
When a new agent, studio, or capability is added, it must declare one canonical department wrapper first. If it cannot, it should attach to an existing department as a supporting surface rather than becoming a new top-level OS object.
