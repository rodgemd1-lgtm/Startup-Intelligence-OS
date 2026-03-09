---
name: team-architect
description: Susan's core team design methodology — 6-phase workflow, agent selection criteria, cross-portfolio synergy patterns
---

# Team Architect Methodology

Susan follows a rigorous 6-phase workflow to design optimal agent teams for startups.

## 6-Phase Workflow

1. **Company Intake** — Extract and standardize company profile from registry or user input
2. **Gap Analysis** — Map current capabilities against ideal state, score complexity 1-10
3. **Team Design** — Select minimum viable agent team from 23 templates
4. **Dataset Requirements** — Enumerate data needs per agent, prioritize P0/P1/P2
5. **Execution Plan** — Generate phased deployment roadmap with success criteria
6. **Behavioral Economics Audit** — LAAL design, copy protocols, retention KPIs
7. **Emotional Experience Audit** — Moments of truth, motion narrative, organic layout fit, and feeling-state alignment

## Agent Selection Criteria

When selecting agents for a company:
- Map each capability gap to the most relevant agent
- Consider cross-agent dependencies (e.g., Coach needs Sage for nutrition context)
- Budget constraint: total monthly cost under company's budget
- Prefer fewer agents with broader coverage over many narrow specialists
- Always include Freya (BE) for any consumer product
- Include Mira or explicitly upgrade Marcus/Echo/Prism when landing-page conversion, trust transfer, or emotional resonance is a key driver

## Model Routing

- **Opus**: Strategic decisions with high stakes (Steve only)
- **Sonnet**: Most specialist work — analysis, design, recommendations
- **Haiku**: Data lookups, routine scans, cost-sensitive operations

## Cross-Portfolio Synergy

When a capability is portable across companies:
- Flag it as `cross_portfolio_synergy` in the gap analysis
- Store related knowledge as `company_id: "shared"` in pgvector
- Tag with `access_level: "public"` for cross-company visibility

## Priority Resolution

When agents or priorities conflict: **safety > retention > growth > features**
