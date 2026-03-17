---
paths:
  - "apps/operator-console/**"
---

# Operator Console Rules

## Architecture
- Static HTML/JS — no build tools, no framework
- Served via `python3 -m http.server 4173`
- URL: http://localhost:4173 or http://localhost:4173/?operator=susan

## Key Files
- `operator-debrief.json` — operator state and metrics

## Conventions
- Keep it simple: vanilla HTML, CSS, JS
- No npm dependencies
- Three-zone layout mirrors V5 but in static HTML
- Console reads from Decision OS API when available
