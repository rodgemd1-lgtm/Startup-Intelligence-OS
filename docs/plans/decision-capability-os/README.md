# Decision & Capability OS — Aggressive Pack

This pack is the aggressive version of Startup Intelligence OS reframed as a **Decision & Capability OS**.

It is designed around one core idea:

> Keep the **terminal** as the main execution surface, and make the **new interface** the control plane for context, visibility, decisions, artifacts, and handoffs.

## What is in this pack

- `docs/aggressive-plan.md` — full target-state architecture, operating model, phased build plan, and gap closure plan
- `docs/operating-model.md` — how terminal, interface, Codex, Claude Code, Jake, and Susan work together
- `docs/interface-spec.md` — screen-by-screen product spec for the interface
- `docs/capability-gap-map.md` — capability gaps and what to build to close them
- `docs/implementation-backlog.md` — build backlog and sequence
- `prototype/jake-console.html` — a static operator-console mockup
- `scaffold/` — starter files for Claude Code and Codex

## Core recommendation

Do **not** make the interface the place where the real work happens.

Make the interface the place where you:
- choose workspace
- choose company / project
- choose active decision
- see artifacts
- route work to Jake / Susan / research / build specialists
- review outputs
- hand off work to terminal or cloud task

Keep the terminal as the place where you:
- talk to Jake
- build
- inspect code
- run tests
- run company / project workflows
- launch or resume focused work

## Target mental model

- **Jake** = front door, co-founder, conductor, architect, strategist
- **Susan** = capabilities foundry, capability design, team design, operating system builder
- **Research specialists** = deep methods, definitions, protocols, benchmarks
- **Decision kernel** = the actual operating system
- **Terminal** = cockpit
- **Interface** = mission control
- **Git worktree / workspace** = unit of execution

## Where to start

1. Read `docs/operating-model.md`
2. Open `prototype/jake-console.html`
3. Drop the `scaffold/` files into your repo
4. Start with `CLAUDE.md`, `AGENTS.md`, and the `bin/jake` launcher
5. Build the workspace registry before building a heavy front-end
