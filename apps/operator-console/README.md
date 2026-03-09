# Operator Console

Three-zone command center for the Decision & Capability OS.

## Layout

- **Left rail**: Workspaces, team console, navigation
- **Center**: Jake brief, decision room, primary terminal
- **Right rail**: Next actions, workspace summary, system status, design rule

## Operator modes

- Default: `Hello, Mike` (http://localhost:4173)
- Susan: `Hello, Susan` (http://localhost:4173/?operator=susan)

## Terminal commands

- `help` — Show available commands
- `bin/jake` — Validate OS contract
- `bin/jake status` — Print object counts
- `bin/jake sync-intel` — Sync agent readiness
- `bin/os-context` — Print OS context
- `clear` — Clear terminal

## Local development

```bash
python3 -m http.server 4173
```

## Vercel deployment

```bash
vercel
vercel --prod
```
